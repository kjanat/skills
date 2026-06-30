# Testing & Publishing Reference

This covers the inner dev loop and the path to the Zed extension registry.

## Dev extension loop (test before you publish)

1. **Install Rust via rustup** (not Homebrew/apt/nix). A non-rustup toolchain cannot build dev extensions and fails opaquely. `rustup --version` to verify. You do **not** add a wasm target or run `cargo build` yourself — Zed cross-compiles to `wasm32-wasip2` on install.
2. In Zed: command palette → `zed: install dev extension` (or the **Install Dev Extension** button on the Extensions page). Select the extension's **root directory** (the folder containing `extension.toml`). Zed compiles and installs it; a "dev" badge appears.
3. After edits: use the **Rebuild** action on the Extensions page (Rust changes recompile; grammar/query/theme/snippet changes load on reload).
4. If the published version of the same `id` is installed, it's uninstalled/overridden — the page shows "Overridden by dev extension." (On some setups a pre-installed extension with the same name must be uninstalled first.)

### Debugging
- `stdout`/`stderr` from your extension forwards to Zed. To see `println!`/`dbg!` and INFO logs, launch Zed from a terminal: **`zed --foreground`**.
- Errors and general logs: `zed: open log` (`Zed.log`).
- If a Rust extension "does nothing," re-read the WASM constraints in `references/rust-api.md` §6 — `std::env::var`, `#[cfg]`, and `chdir` are the usual culprits.

## License requirement (mandatory to publish)

Since **2025‑10‑01**, the extension repo must contain a license file or CI rejects the PR. Accepted licenses:

`Apache-2.0` · `BSD-2-Clause` · `BSD-3-Clause` · `CC-BY-4.0` · `GPLv3` · `LGPLv3` · `MIT` · `Unlicense` · `zlib`

- Put it at the **repo root** (or, if your extension is in a subdirectory referenced by `path`, at that path — a root license won't count; you may symlink).
- Any filename prefixed `LICENSE`/`LICENCE` (case-insensitive) is inspected.
- This applies **only to your extension's own code** — not to language servers, DAP servers, or other tools the extension downloads. A repo can hold both extension code (must be an accepted license) and an unrelated-licensed tool.

## Pre-publish checklist

- `id` is unique, immutable-worthy, and contains no `zed`/`Zed`/`extension`; follows the suffix convention (`-theme`, `-snippets`, etc. — language/tooling extensions may use the tool name).
- All required manifest fields are filled.
- The extension ships **only** what it needs — no bundled language servers/DAP/MCP binaries (download or locate them instead).
- Themes / icon themes are **standalone** extensions (not combined with languages or each other).
- `[[capabilities]]` are declared and scoped narrowly to what the code uses.
- It's been installed and **tested as a dev extension** and actually works. Non-functional submissions get closed without detailed feedback.
- It provides something not already in the registry. If you're fixing a gap in an *existing* extension, prefer contributing a fix upstream first; only submit a new/competing extension if upstream is unresponsive, and document your prior efforts in the PR.

## Publishing (PR to `zed-industries/extensions`)

The registry is the [`zed-industries/extensions`](https://github.com/zed-industries/extensions) repo; extensions are Git submodules listed in `extensions.toml`.

1. **Fork `zed-industries/extensions`** — to a **personal** GitHub account, not an org. (This lets Zed staff push fixes to your PR to speed up review.)
2. Clone and init submodules:
   ```sh
   git clone https://github.com/<you>/extensions
   cd extensions
   git submodule init
   git submodule update
   ```
3. Add your extension repo as a submodule under `extensions/<id>`:
   ```sh
   git submodule add https://github.com/<you>/<your-extension>.git extensions/<id>
   git add extensions/<id>
   ```
   - Submodule URLs must be **HTTPS**, not SSH (`git@github.com:` is rejected).
   - Your extension repo must be **public**, and the checked-out submodule commit must be **on a branch** (not a detached commit).
4. Add an entry to the top-level `extensions.toml`:
   ```toml
   [<id>]
   submodule = "extensions/<id>"
   version = "0.0.1"
   # path = "subdir"   # if the extension.toml is in a subdirectory of the submodule
   ```
   If you use `path`, the required license must reside **at that path** (a root license won't satisfy CI; symlinking is allowed).
5. Sort the metadata:
   ```sh
   pnpm sort-extensions      # sorts extensions.toml and .gitmodules
   ```
6. Open the PR. On merge, Zed packages and publishes the extension to the registry.

## Updating a published extension

1. Push the new version to your extension repo (bump `version` in its `extension.toml`).
2. In a fork of `zed-industries/extensions`:
   ```sh
   git submodule update --remote extensions/<id>
   ```
3. Bump the matching `version` in `extensions.toml` so it equals the `extension.toml` version at that commit.
4. PR it.

To automate updates, the community [`huacnlee/zed-extension-action`](https://github.com/huacnlee/zed-extension-action) GitHub Action opens the bump PR for you on each release. (If your repo's license changes, update it to an accepted one before publishing an update.)

## What lives where (canonical sources)

When you need ground truth beyond the docs:
- `zed_extension_api` crate (trait, types, helpers): <https://docs.rs/zed_extension_api> and <https://crates.io/crates/zed_extension_api>.
- The WIT contract per API version: `crates/extension_api/wit/since_v0.X.0/` in `zed-industries/zed`.
- Real built-in languages (config + queries): `crates/languages/src/` in `zed-industries/zed`.
- The registry and its CI (incl. license validation): `zed-industries/extensions`.
