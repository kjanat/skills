# Language Server Extensions Reference

A language-server extension provides IDE features (completions, diagnostics, go-to-definition, formatting) by launching an LSP server and adapting it to Zed. This is the Rust half. The language-definition half (grammar + queries) is in `references/languages.md`; use it only when adding a new language or replacing language syntax behavior.

The trait method surface is in `references/rust-api.md`. This file is about the **patterns that make a server extension actually work**: acquiring the binary, caching it, reporting status, and styling output.

## Manifest

```toml
[language_servers.my-lsp]
name      = "My Language LSP"
languages = ["My Language"]    # must match Zed language names

# capabilities you'll need (tune to your acquisition strategy):
[[capabilities]]
kind = "download_file"
host = "github.com"
path = ["**"]

[[capabilities]]
kind    = "process:exec"
command = "*"
args    = ["**"]
```

`languages` entries attach the server to existing Zed language names. They may refer to a `name` from this extension's `languages/<lang>/config.toml` or to a built-in/installed language. If the language already exists, skip `languages/<lang>/` and skip `[grammars.*]`:

```toml
[language_servers.tombi]
name      = "Tombi"
languages = ["TOML"]
```

This avoids global grammar-key collisions. Do not create a fake/scoped language that reuses a common grammar key just to narrow an LSP to certain files.

## The core method

```rust
fn language_server_command(
    &mut self,
    language_server_id: &zed::LanguageServerId,
    worktree: &zed::Worktree,
) -> zed::Result<zed::Command>
```

This runs **every time a server starts** (including restarts and reopening projects). The job: return the path to a runnable server binary plus args/env. The challenge is that you must not ship the binary — you download it or find it on the user's machine. So this method has to be idempotent and cheap on the common path (binary already present).

### Acquisition strategy — in priority order

A robust server extension tries these in order:

1. **User-specified binary.** Let power users point at their own install via settings. Read `lsp.<server>.binary.path`:
   ```rust
   use zed_extension_api::settings::LspSettings;
   if let Ok(settings) = LspSettings::for_worktree("my-lsp", worktree)
       && let Some(binary) = settings.binary
       && let Some(path) = binary.path
   {
       return Ok(zed::Command { command: path, args: binary.arguments.unwrap_or_default(), env: vec![] });
   }
   ```
2. **Binary on `PATH`.** Many users already have the server installed:
   ```rust
   if let Some(path) = worktree.which("my-language-server") {
       return Ok(zed::Command { command: path, args: vec![], env: worktree.shell_env() });
   }
   ```
3. **Download + cache** (below).

### Pattern A — download from GitHub releases

The most common pattern for compiled servers. Cache the resolved path on `self` so repeat calls skip the network; check GitHub only when the cached binary is missing.

```rust
use zed_extension_api::{self as zed, Result};

struct MyExtension { cached_binary_path: Option<String> }

impl MyExtension {
    fn language_server_binary_path(
        &mut self,
        language_server_id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<String> {
        // 1. user override / PATH first (omitted here for brevity)
        if let Some(path) = worktree.which("my-language-server") {
            return Ok(path);
        }
        // 2. reuse cached download if it's still on disk
        if let Some(path) = &self.cached_binary_path
            && std::fs::metadata(path).is_ok_and(|s| s.is_file())
        {
            return Ok(path.clone());
        }

        // 3. resolve the latest release for the current platform
        zed::set_language_server_installation_status(
            language_server_id, &zed::LanguageServerInstallationStatus::CheckingForUpdate);

        let release = zed::latest_github_release(
            "org/my-language-server",
            zed::GithubReleaseOptions { require_assets: true, pre_release: false },
        )?;

        let (os, arch) = zed::current_platform();
        let asset_name = format!(
            "my-language-server-{version}-{arch}-{os}.{ext}",
            version = release.version,
            arch = match arch { zed::Architecture::Aarch64 => "aarch64",
                                zed::Architecture::X8664 => "x86_64",
                                zed::Architecture::X86 => "x86" },
            os = match os { zed::Os::Mac => "apple-darwin",
                            zed::Os::Linux => "unknown-linux-gnu",
                            zed::Os::Windows => "pc-windows-msvc" },
            ext = match os { zed::Os::Windows => "zip", _ => "tar.gz" },
        );

        let asset = release.assets.iter()
            .find(|a| a.name == asset_name)
            .ok_or_else(|| format!("no asset matching {asset_name}"))?;

        // 4. download into a versioned dir (so updates don't clobber a running server)
        let version_dir = format!("my-language-server-{}", release.version);
        let binary_path = format!("{version_dir}/my-language-server");

        if !std::fs::metadata(&binary_path).is_ok_and(|s| s.is_file()) {
            zed::set_language_server_installation_status(
                language_server_id, &zed::LanguageServerInstallationStatus::Downloading);
            zed::download_file(
                &asset.download_url,
                &version_dir,
                match os { zed::Os::Windows => zed::DownloadedFileType::Zip,
                           _ => zed::DownloadedFileType::GzipTar },
            ).map_err(|e| format!("download failed: {e}"))?;
            zed::make_file_executable(&binary_path)?;

            // 5. tidy: remove older version dirs
            if let Ok(entries) = std::fs::read_dir(".") {
                for entry in entries.flatten() {
                    let name = entry.file_name().into_string().unwrap_or_default();
                    if name.starts_with("my-language-server-") && name != version_dir {
                        let _ = std::fs::remove_dir_all(entry.path());
                    }
                }
            }
        }

        self.cached_binary_path = Some(binary_path.clone());
        Ok(binary_path)
    }
}

impl zed::Extension for MyExtension {
    fn new() -> Self { Self { cached_binary_path: None } }

    fn language_server_command(
        &mut self,
        id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<zed::Command> {
        let path = self.language_server_binary_path(id, worktree)?;
        Ok(zed::Command { command: path, args: vec!["--stdio".into()], env: vec![] })
    }
}

zed::register_extension!(MyExtension);
```

This is essentially the contents of `assets/templates/language-server-lib.rs` — start from that file.

### Pattern B — npm-distributed server

For servers shipped on npm (many JS/TS-ecosystem servers), use the npm helpers and launch via Node.

```rust
const PACKAGE: &str = "my-language-server";
const SERVER_PATH: &str = "node_modules/my-language-server/bin/server.js";

fn language_server_command(&mut self, id: &zed::LanguageServerId, worktree: &zed::Worktree)
    -> Result<zed::Command>
{
    let installed = zed::npm_package_installed_version(PACKAGE)?;
    let latest = zed::npm_package_latest_version(PACKAGE)?;
    if installed.as_deref() != Some(latest.as_str()) {
        zed::set_language_server_installation_status(
            id, &zed::LanguageServerInstallationStatus::Downloading);
        zed::npm_install_package(PACKAGE, &latest)?;
    }
    Ok(zed::Command {
        command: zed::node_binary_path()?,
        args: vec![
            std::env::current_dir().unwrap().join(SERVER_PATH).to_string_lossy().into(),
            "--stdio".into(),
        ],
        env: vec![],
    })
}
```

Requires `[[capabilities]] kind = "npm:install"` (and `process:exec` for node).

## Installation status

Always drive `set_language_server_installation_status` so the user sees progress and errors:

- `CheckingForUpdate` while resolving a release/version,
- `Downloading` during fetch/install,
- `Failed(msg)` on error (the message surfaces in the UI),
- `None` once ready.

Without this, a slow download looks like a hang.

## Init options & workspace configuration

Pass server config from user settings:

```rust
fn language_server_initialization_options(
    &mut self, _id: &zed::LanguageServerId, worktree: &zed::Worktree,
) -> Result<Option<zed::serde_json::Value>> {
    let opts = zed::settings::LspSettings::for_worktree("my-lsp", worktree)
        .ok()
        .and_then(|s| s.initialization_options)
        .unwrap_or_default();
    Ok(Some(opts))
}

fn language_server_workspace_configuration(
    &mut self, _id: &zed::LanguageServerId, worktree: &zed::Worktree,
) -> Result<Option<zed::serde_json::Value>> {
    let settings = zed::settings::LspSettings::for_worktree("my-lsp", worktree)
        .ok().and_then(|s| s.settings).unwrap_or_default();
    Ok(Some(settings))
}
```

This is the bridge that lets users configure the server via `"lsp": { "my-lsp": { "initialization_options": {...}, "settings": {...} } }`.

## Completion & symbol labels

Style how completions/symbols render. Return a `CodeLabel` mixing literal text and grammar-highlighted ranges. Example: render a function completion as `name(…) -> ReturnType` with the signature styled:

```rust
fn label_for_completion(
    &self, _id: &zed::LanguageServerId, completion: zed::lsp::Completion,
) -> Option<zed::CodeLabel> {
    use zed::lsp::CompletionKind;
    match completion.kind? {
        CompletionKind::Function | CompletionKind::Method => {
            let detail = completion.detail.unwrap_or_default();   // e.g. "(a: Int) -> Bool"
            let code = format!("{}{}", completion.label, detail);
            Some(zed::CodeLabel {
                spans: vec![
                    zed::CodeLabelSpan::literal(completion.label.clone(), Some("function".into())),
                    zed::CodeLabelSpan::literal(detail, None),
                ],
                filter_range: (0..completion.label.len()).into(),
                code,
            })
        }
        _ => None,   // fall back to Zed default
    }
}
```

`CodeLabelSpan::code_range(range)` highlights a slice of `code` using the language grammar; `CodeLabelSpan::literal(text, Some("highlight_name"))` applies a named highlight directly. `filter_range` is the portion used when matching the user's typed query.

## Multi-language servers

If one server handles several languages, list them all and map Zed names to LSP `languageId`s in the manifest:

```toml
[language_servers.my-lsp]
name      = "My LSP"
languages = ["JavaScript", "TSX", "CSS"]

[language_servers.my-lsp.language_ids]
"JavaScript" = "javascript"
"TSX"        = "typescriptreact"
"CSS"        = "css"
```

## Real examples

Browse published LSP extensions for proven structures: language servers in the registry (e.g. for Gleam, Lua, Zig) and Zed's built-in language adapters in `crates/languages/src/` of `zed-industries/zed`.
