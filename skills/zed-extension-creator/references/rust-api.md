# Rust API Reference (`zed_extension_api`)

Procedural extensions are a Rust crate compiled to `wasm32-wasip2` (Zed does the cross-compile). You implement the `Extension` trait and register it. This reference covers the trait, the helper functions, the key types, and the sandbox rules — accurate to crate line **0.7.x** (WIT `since_v0.6.0`). Always confirm against the version you pin: <https://docs.rs/zed_extension_api>.

## Table of contents

1. Crate setup and entry point
2. The `Extension` trait — every method
3. Helper functions (downloads, GitHub, npm, platform, install status)
4. Key types (`Command`, `Worktree`, `CodeLabel`, ids, enums)
5. Modules (`process`, `http_client`, `settings`, `lsp`)
6. WASM sandbox constraints (read this)

---

## 1. Crate setup and entry point

`Cargo.toml`:

```toml
[package]
name    = "my-extension"
version = "0.0.1"
edition = "2024"

[lib]
crate-type = ["cdylib"]

[dependencies]
zed_extension_api = "0.7"  # pin to the version you mean; check crates.io for newest
```

`src/lib.rs`:

```rust
use zed_extension_api::{self as zed, Result};

struct MyExtension {
    // cache handles, resolved binary paths, etc.
}

impl zed::Extension for MyExtension {
    fn new() -> Self {
        Self { /* ... */ }
    }

    // implement only the methods your extension needs; the rest have defaults
}

zed::register_extension!(MyExtension);
```

`new()` is the only required method. `register_extension!` wires up the wasm entry point. Note: the macro deliberately stubs out `chdir` so the extension cannot change its working directory — a sandbox guarantee, not a bug.

---

## 2. The `Extension` trait

Every method except `new()` has a default implementation, so implement only what applies. Signatures below are exact for 0.7.x. `Result<T>` is `zed_extension_api::Result<T>` = `core::result::Result<T, String>` — errors are plain strings.

### Always

```rust
fn new() -> Self where Self: Sized;
```

Constructs the extension. Initialize caches here; keep it cheap (no network).

### Language servers

```rust
fn language_server_command(
    &mut self,
    language_server_id: &LanguageServerId,
    worktree: &Worktree,
) -> Result<Command>;
```

**The core LSP method.** Return the `Command` (binary path + args + env) that launches the server. Acquire the binary here — download from GitHub/npm or locate it via `worktree.which(...)`. Called on every server start, so cache and rate-limit any network work. Default returns an error (so declaring a server without implementing this fails).

```rust
fn language_server_initialization_options(
    &mut self, _id: &LanguageServerId, _worktree: &Worktree,
) -> Result<Option<serde_json::Value>>;            // default: Ok(None)

fn language_server_workspace_configuration(
    &mut self, _id: &LanguageServerId, _worktree: &Worktree,
) -> Result<Option<serde_json::Value>>;            // default: Ok(None)
```

Return JSON passed to the server as LSP `initializationOptions` / `workspace/configuration`. Read user settings via the `settings` module (see §5) and merge.

```rust
fn language_server_additional_initialization_options(
    &mut self, _id: &LanguageServerId, _target_id: &LanguageServerId, _worktree: &Worktree,
) -> Result<Option<serde_json::Value>>;            // default: Ok(None)

fn language_server_additional_workspace_configuration(
    &mut self, _id: &LanguageServerId, _target_id: &LanguageServerId, _worktree: &Worktree,
) -> Result<Option<serde_json::Value>>;            // default: Ok(None)
```

For options/config that one server needs to send *to another* server (`_target_id`). Niche; used by stacked servers (e.g. a framework server configuring a base server).

```rust
fn label_for_completion(
    &self, _id: &LanguageServerId, _completion: lsp::Completion,
) -> Option<CodeLabel>;                             // default: None

fn label_for_symbol(
    &self, _id: &LanguageServerId, _symbol: lsp::Symbol,
) -> Option<CodeLabel>;                             // default: None
```

Style how completions/symbols render (e.g. show a function signature with the return type dimmed). Return a `CodeLabel` (see §4) or `None` to use Zed's default. Worth implementing for a polished feel; see `references/language-servers.md`.

### Context servers (MCP)

```rust
fn context_server_command(
    &mut self, _context_server_id: &ContextServerId, _project: &Project,
) -> Result<Command>;                              // default: error
```

Return the `Command` that launches the MCP server (stdio transport). Same acquire-and-cache discipline as LSP.

```rust
fn context_server_configuration(
    &mut self, _context_server_id: &ContextServerId, _project: &Project,
) -> Result<Option<ContextServerConfiguration>>;   // default: Ok(None)
```

Surface setup info to the user. `ContextServerConfiguration { installation_instructions: String (Markdown), settings_schema: String (JSON Schema), default_settings: String }`. See `references/context-servers.md`.

### Slash commands (legacy Assistant)

```rust
fn complete_slash_command_argument(
    &self, _command: SlashCommand, _args: Vec<String>,
) -> Result<Vec<SlashCommandArgumentCompletion>>;  // default: Ok(vec![])

fn run_slash_command(
    &self, _command: SlashCommand, _args: Vec<String>, _worktree: Option<&Worktree>,
) -> Result<SlashCommandOutput>;                    // default: error
```

`run_slash_command` returns `SlashCommandOutput { text: String, sections: Vec<SlashCommandOutputSection> }`. Legacy; prefer MCP for new work.

### Docs indexing (the `/docs` slash command)

```rust
fn suggest_docs_packages(&self, _provider: String) -> Result<Vec<String>>;  // default: Ok(vec![])

fn index_docs(
    &self, _provider: String, _package: String, _database: &KeyValueStore,
) -> Result<()>;                                    // default: error
```

Lets an extension provide package docs to the `/docs` command, writing indexed content into the provided `KeyValueStore`. Niche.

### Debug adapters (DAP)

```rust
fn get_dap_binary(
    &mut self,
    _adapter_name: String,
    _config: DebugTaskDefinition,
    _user_provided_debug_adapter_path: Option<String>,
    _worktree: &Worktree,
) -> Result<DebugAdapterBinary>;                    // default: error

fn dap_request_kind(
    &mut self, _adapter_name: String, _config: serde_json::Value,
) -> Result<StartDebuggingRequestArgumentsRequest>;// default: error

fn dap_config_to_scenario(
    &mut self, _config: DebugConfig,
) -> Result<DebugScenario>;                         // default: error

fn dap_locator_create_scenario(
    &mut self,
    _locator_name: String,
    _build_task: TaskTemplate,
    _resolved_label: String,
    _debug_adapter_name: String,
) -> Option<DebugScenario>;                         // default: None

fn run_dap_locator(
    &mut self, _locator_name: String, _build_task: TaskTemplate,
) -> Result<DebugRequest>;                          // default: error
```

Full treatment, including the two-phase locator flow, in `references/debug-adapters.md`.

---

## 3. Helper functions

Free functions in `zed_extension_api`. These are how you acquire binaries and learn about the environment.

```rust
// Platform — branch at runtime instead of with #[cfg]
fn current_platform() -> (Os, Architecture);
// Os: Mac | Linux | Windows ; Architecture: Aarch64 | X86 | X8664

// GitHub releases
fn latest_github_release(repo: &str, options: GithubReleaseOptions) -> Result<GithubRelease>;
fn github_release_by_tag_name(repo: &str, tag: &str) -> Result<GithubRelease>;
// repo is "owner/name". GithubReleaseOptions { require_assets: bool, pre_release: bool }.
// GithubRelease { version: String, assets: Vec<GithubReleaseAsset> };
// GithubReleaseAsset { name: String, download_url: String }.

// Downloading + making executable
fn download_file(url: &str, path: &str, file_type: DownloadedFileType) -> Result<()>;
// DownloadedFileType: Uncompressed | Gzip | GzipTar | Zip | Zip (and tar variants).
// `path` is relative to the extension's working directory.
fn make_file_executable(path: &str) -> Result<()>;

// npm-based servers
fn node_binary_path() -> Result<String>;
fn npm_install_package(package: &str, version: &str) -> Result<()>;
fn npm_package_installed_version(package: &str) -> Result<Option<String>>;
fn npm_package_latest_version(package: &str) -> Result<String>;

// Language-server install status (drives the UI spinner/errors)
fn set_language_server_installation_status(
    id: &LanguageServerId, status: &LanguageServerInstallationStatus,
);
// LanguageServerInstallationStatus: None | Downloading | CheckingForUpdate | Failed(String)
```

`resolve_tcp_template(...)` exists for DAP servers that communicate over TCP rather than stdio.

Each of `download_file`, `npm_install_package`, and `process::Command` requires a matching `[[capabilities]]` entry in `extension.toml` (see `references/manifest.md`).

---

## 4. Key types

### `Command` (`type Command`)

```rust
struct Command {
    command: String,          // path to the executable
    args: Vec<String>,
    env: Vec<(String, String)>,   // EnvVars
}
```

Returned by `language_server_command`, `context_server_command`. Build the env from `worktree.shell_env()` if the server needs the user's environment.

### `Worktree`

Represents an open project folder. Methods you'll actually use:

```rust
worktree.root_path() -> String
worktree.read_text_file(path: &str) -> Result<String>   // read a project file (e.g. detect config)
worktree.which(binary_name: &str) -> Option<String>     // find a binary in the user's PATH
worktree.shell_env() -> Vec<(String, String)>           // the user's environment (NOT std::env)
```

`which` + `shell_env` are the **sandbox-correct** replacements for std environment access.

### `CodeLabel` (completion/symbol styling)

```rust
struct CodeLabel {
    code: String,                 // the text to display
    spans: Vec<CodeLabelSpan>,    // how to highlight ranges
    filter_range: Range,          // which part is matched during filtering
}
enum CodeLabelSpan {
    CodeRange(Range),                                  // highlight using grammar of the language
    Literal(CodeLabelSpanLiteral { text, highlight_name }),
}
// Constructors: CodeLabelSpan::code_range(range), CodeLabelSpan::literal(text, Some("type"))
```

See the worked example in `references/language-servers.md`.

### IDs

`LanguageServerId` and `ContextServerId` are opaque newtypes over `String` with `AsRef<str>` and `Display`. Match on `id.as_ref()` when one extension provides several servers.

### `KeyValueStore`

A persistent key/value store handed to `index_docs` for caching indexed documentation.

### Module `lsp` types

`Completion`, `CompletionKind`, `Symbol`, `SymbolKind`, `InsertTextFormat` — the LSP payloads passed to `label_for_completion`/`label_for_symbol`.

---

## 5. Modules

- **`zed_extension_api::process`** — `process::Command` for executing subprocesses from the extension (gated by `process:exec` capability). Use for running a tool to discover a version, etc.
- **`zed_extension_api::http_client`** — an HTTP client for requests beyond `download_file`/GitHub helpers.
- **`zed_extension_api::settings`** — read Zed settings relevant to your server (e.g. `settings::LspSettings::for_worktree("server-name", worktree)` to get the user's `lsp.<server>.{binary,initialization_options,settings}`). This is how you let users point at a custom binary path or pass server settings.
- **`zed_extension_api::lsp`** — the LSP payload types listed in §4.
- The crate also re-exports `serde_json` so you don't need a separate dependency for building JSON values.

---

## 6. WASM sandbox constraints (the silent-failure causes)

The extension runs as a sandboxed wasm component. Standard Rust assumptions break:

- **`std::env::var` does not see the user's environment.** Use `worktree.shell_env()` / `worktree.which()`. This is the most common cause of "the server won't start — it works in my terminal."
- **`#[cfg(target_os = ...)]` is unreliable.** The crate is compiled once for wasm, not per host OS. Use `zed::current_platform()` and branch at runtime to pick the right release asset / binary name.
- **No `chdir`.** The working directory is fixed (the macro enforces this). Use absolute/relative paths from the working dir.
- **No reading/writing outside the granted environment.** Filesystem and process access is mediated by Zed and the declared capabilities. Don't reach for arbitrary paths.
- **`println!`/`dbg!` go to Zed's stdout** — only visible when Zed is launched with `zed --foreground`. Logs otherwise land in `Zed.log` (`zed: open log`).
- **Keep `new()` and hot methods cheap.** `language_server_command`/`context_server_command` run on every (re)start; do expensive downloads once and cache, checking for updates only periodically.
