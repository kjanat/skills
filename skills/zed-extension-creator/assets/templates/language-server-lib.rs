//! Complete, working language-server extension for Zed.
//!
//! This is the best starting point for ANY Rust-based Zed extension. It:
//!   1. lets a user point at their own server binary via settings,
//!   2. falls back to a binary already on PATH,
//!   3. otherwise downloads the right asset from GitHub releases, caches it in a
//!      versioned dir, marks it executable, and prunes old versions,
//!   4. drives the installation-status UI throughout,
//!   5. forwards user config as LSP init options + workspace configuration.
//!
//! To adapt for an MCP server, replace `language_server_command` with
//! `context_server_command`; for a debug adapter, implement `get_dap_binary` +
//! `dap_request_kind`. The binary-acquisition helper below is reusable as-is.
//!
//! Search-and-replace before using:
//!   my-language-server  -> the binary / executable name
//!   org/my-language-server -> the GitHub "owner/repo"
//!   my-lsp              -> the language_servers.<id> from extension.toml
//!   (and fix the asset_name format! to match the project's real release names)
//!
//! Reference: references/language-servers.md and references/rust-api.md

use zed_extension_api::{self as zed, settings::LspSettings, LanguageServerId, Result};

const SERVER_BINARY_NAME: &str = "my-language-server";
const GITHUB_REPO: &str = "org/my-language-server";
const LSP_SETTINGS_KEY: &str = "my-lsp";

struct MyExtension {
    /// Resolved path to a downloaded binary, cached so repeat starts skip the
    /// network. Invalidated automatically if the file disappears.
    cached_binary_path: Option<String>,
}

impl MyExtension {
    /// Returns a path to a runnable server binary, acquiring it if necessary.
    fn server_binary_path(
        &mut self,
        language_server_id: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<String> {
        // (1) User override: "lsp": { "my-lsp": { "binary": { "path": "..." } } }
        if let Ok(settings) = LspSettings::for_worktree(LSP_SETTINGS_KEY, worktree) {
            if let Some(binary) = settings.binary {
                if let Some(path) = binary.path {
                    return Ok(path);
                }
            }
        }

        // (2) Already on PATH — respect an existing user install.
        if let Some(path) = worktree.which(SERVER_BINARY_NAME) {
            return Ok(path);
        }

        // (3) Reuse a previous download if the file is still present.
        if let Some(path) = &self.cached_binary_path {
            if std::fs::metadata(path).map_or(false, |stat| stat.is_file()) {
                return Ok(path.clone());
            }
        }

        // (4) Resolve the latest GitHub release for this platform.
        zed::set_language_server_installation_status(
            language_server_id,
            &zed::LanguageServerInstallationStatus::CheckingForUpdate,
        );

        let release = zed::latest_github_release(
            GITHUB_REPO,
            zed::GithubReleaseOptions {
                require_assets: true,
                pre_release: false,
            },
        )?;

        let (os, arch) = zed::current_platform();
        let arch_str = match arch {
            zed::Architecture::Aarch64 => "aarch64",
            zed::Architecture::X8664 => "x86_64",
            zed::Architecture::X86 => "x86",
        };
        let os_str = match os {
            zed::Os::Mac => "apple-darwin",
            zed::Os::Linux => "unknown-linux-gnu",
            zed::Os::Windows => "pc-windows-msvc",
        };
        let (archive_ext, file_type) = match os {
            zed::Os::Windows => ("zip", zed::DownloadedFileType::Zip),
            _ => ("tar.gz", zed::DownloadedFileType::GzipTar),
        };

        // IMPORTANT: this must match the project's actual release asset naming.
        let asset_name = format!(
            "{SERVER_BINARY_NAME}-{version}-{arch_str}-{os_str}.{archive_ext}",
            version = release.version,
        );

        let asset = release
            .assets
            .iter()
            .find(|asset| asset.name == asset_name)
            .ok_or_else(|| format!("no release asset found matching `{asset_name}`"))?;

        // (5) Download into a per-version directory so updates never clobber a
        //     server that's currently running.
        let version_dir = format!("{SERVER_BINARY_NAME}-{}", release.version);
        let executable = if matches!(os, zed::Os::Windows) {
            format!("{version_dir}/{SERVER_BINARY_NAME}.exe")
        } else {
            format!("{version_dir}/{SERVER_BINARY_NAME}")
        };

        if !std::fs::metadata(&executable).map_or(false, |stat| stat.is_file()) {
            zed::set_language_server_installation_status(
                language_server_id,
                &zed::LanguageServerInstallationStatus::Downloading,
            );

            zed::download_file(&asset.download_url, &version_dir, file_type)
                .map_err(|err| format!("failed to download {asset_name}: {err}"))?;

            zed::make_file_executable(&executable)?;

            // (6) Prune older version directories.
            if let Ok(entries) = std::fs::read_dir(".") {
                for entry in entries.flatten() {
                    let name = entry.file_name().into_string().unwrap_or_default();
                    if name.starts_with(&format!("{SERVER_BINARY_NAME}-")) && name != version_dir {
                        let _ = std::fs::remove_dir_all(entry.path());
                    }
                }
            }
        }

        self.cached_binary_path = Some(executable.clone());
        Ok(executable)
    }
}

impl zed::Extension for MyExtension {
    fn new() -> Self {
        Self {
            cached_binary_path: None,
        }
    }

    fn language_server_command(
        &mut self,
        language_server_id: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<zed::Command> {
        let path = self.server_binary_path(language_server_id, worktree)?;
        Ok(zed::Command {
            command: path,
            // Most stdio LSP servers take a flag like this; adjust per server.
            args: vec!["--stdio".into()],
            env: Default::default(),
        })
    }

    /// Forward `"initialization_options"` from the user's LSP settings.
    fn language_server_initialization_options(
        &mut self,
        _language_server_id: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<Option<zed::serde_json::Value>> {
        let options = LspSettings::for_worktree(LSP_SETTINGS_KEY, worktree)
            .ok()
            .and_then(|settings| settings.initialization_options);
        Ok(options)
    }

    /// Forward `"settings"` from the user's LSP settings as workspace config.
    fn language_server_workspace_configuration(
        &mut self,
        _language_server_id: &LanguageServerId,
        worktree: &zed::Worktree,
    ) -> Result<Option<zed::serde_json::Value>> {
        let settings = LspSettings::for_worktree(LSP_SETTINGS_KEY, worktree)
            .ok()
            .and_then(|settings| settings.settings);
        Ok(settings)
    }
}

zed::register_extension!(MyExtension);
