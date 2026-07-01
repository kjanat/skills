---
name: zed-extension-creator
description: >-
  Scaffolds, implements, and ships extensions for the Zed editor. Use whenever someone wants to build,
  scaffold, or set up a Zed extension; add a language, grammar, or tree-sitter queries to Zed; wrap a
  language server (LSP) as a Zed extension; add a color theme or icon theme; expose an MCP / context
  server, a debug adapter (DAP), or snippets to Zed; or asks about the `extension.toml` manifest, the
  `zed_extension_api` Rust crate, the `Extension` trait, tree-sitter `.scm` query files, the WASM sandbox
  constraints, or the `zed-industries/extensions` publishing flow — even without the word "skill". Also
  triggers on a `.scm` highlights/injections/outline file in a Zed context, a per-language `config.toml`,
  or publishing/updating an extension in the Zed registry. Picks the right extension type and routes to
  the matching reference and template.
---

# Zed Extension Creator

A Zed extension is a **Git repository with an `extension.toml` manifest** that adds capability to the editor. Any procedural logic (a language server adapter, MCP server launcher, or debug adapter) is written in **Rust, compiled to WebAssembly** against the [`zed_extension_api`](https://crates.io/crates/zed_extension_api) crate. Many extensions (languages defined purely by a grammar + queries, themes, icon themes, snippets) need **no Rust at all** — just data files.

This skill takes someone from "I want to add X to Zed" to a tested, dev-installed, publish-ready extension. Work through the steps below in order; jump into the matching reference file for the deep detail on the specific type being built.

## Step 0 — Establish what's being built

Zed extensions come in distinct flavors, and the flavor decides almost everything (whether you need Rust, what files go where, what the manifest declares). Pin this down first, because building a "language extension" and a "language server extension" are different jobs that happen to live in the same repo.

| Goal                                                                             | Needs Rust? | Read this reference                                                                  |
| -------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------ |
| Syntax highlighting / indentation / outline for a language (grammar + queries)   | No          | `references/languages.md`                                                            |
| Run a language server (LSP) for a language — completions, diagnostics, go-to-def | **Yes**     | `references/language-servers.md` (+ `references/languages.md` for the language half) |
| A color theme                                                                    | No          | `references/themes.md`                                                               |
| An icon theme (file/folder icons)                                                | No          | `references/themes.md` (icon section)                                                |
| Expose an MCP / context server to the Agent Panel                                | **Yes**     | `references/context-servers.md`                                                      |
| A debug adapter (DAP) and/or debug locator                                       | **Yes**     | `references/debug-adapters.md`                                                       |
| Code snippets                                                                    | No          | `references/snippets.md`                                                             |

Two flavors often combine: a real new-language extension usually ships **both** the grammar+queries (the `languages/` half) **and** a language server adapter (the Rust half). But if the language already exists in Zed and you only need IDE features, attach the server to that existing language name; do **not** declare a new language or grammar just to scope the server.

Cross-cutting references, useful for almost every build:

- `references/manifest.md` — the complete `extension.toml` schema: every field, every capability section, the `[[capabilities]]` permission declarations, `schema_version`, and API-version compatibility.
- `references/rust-api.md` — the full `Extension` trait (every method, when to implement it), the helper functions (`latest_github_release`, `npm_install_package`, `download_file`, `current_platform`, …), the `Worktree`/`Command`/`CodeLabel` types, and the **WASM sandbox constraints that trip everyone up**.
- `references/publishing.md` — installing as a dev extension, testing, the mandatory license, and the `zed-industries/extensions` PR flow.

If the goal is ambiguous, ask the one question that resolves it: *"highlighting only, or full IDE features (completions/diagnostics) via a language server?"* — that single fork determines whether Rust is involved.

## Step 1 — Prerequisites (state these, don't assume them)

- **Rust must be installed via [rustup](https://rustup.rs)**, not Homebrew/apt/nix. This is the single most common setup failure: a Homebrew Rust cannot build dev extensions, and the error is opaque. Verify with `rustup --version`.
- You do **not** manually add a wasm target or run `cargo build` for a dev extension. Zed bundles its own wasi-sdk and cross-compiles your crate to `wasm32-wasip2` when you install the dev extension. (rustup just has to be the active toolchain.)
- Pin a specific `zed_extension_api` version in `Cargo.toml`. The latest published version is on [crates.io](https://crates.io/crates/zed_extension_api) — as of this writing the current line is **`0.7.x`**, which binds the `since_v0.6.0` WIT interface. Always check crates.io for the newest, and confirm it's [compatible with the Zed versions](https://github.com/zed-industries/zed/blob/main/crates/extension_api#compatible-zed-versions) you want to support. Bumping the API version can require code changes, so do it deliberately.

## Step 2 — Scaffold the repository

Every extension, regardless of type, starts the same way. Create a Git repo with this skeleton (omit the parts the chosen type doesn't use):

```
my-extension/
  extension.toml          # required: identity + declared capabilities
  LICENSE                 # required to publish (see Step 5)
  Cargo.toml              # only if the extension has Rust code
  src/lib.rs              # only if the extension has Rust code
  languages/<lang>/       # language extensions: config.toml + *.scm queries
  themes/*.json           # color themes
  icon_themes/*.json      # icon themes (+ icons/*.svg)
  snippets/*.json         # snippets
```

Use the annotated templates in `assets/templates/` as starting points:

- `extension.toml` — every manifest section, commented, so you delete what you don't need rather than remember what to add.
- `Cargo.toml` — the correct `crate-type = ["cdylib"]` + dependency.
- `language-server-lib.rs` — a **complete, working** language-server extension (downloads the server from GitHub releases, caches it, reports install status). The best starting point for any Rust extension; adapt it for MCP/DAP by swapping the trait method.
- `language-config.toml` — a filled-in `languages/<lang>/config.toml`.

The minimal manifest is just identity:

```toml
id             = "my-extension"                         # immutable after publishing; lowercase, no "zed"/"extension"
name           = "My Extension"
version        = "0.0.1"
schema_version = 1
authors        = ["Your Name <you@example.com>"]
description    = "What it does"
repository     = "https://github.com/you/my-extension"
```

Then add the capability sections for the chosen type — see `references/manifest.md` and the type-specific reference for exactly which keys.

## Step 3 — Implement

Follow the matching reference. The shape of the work per type:

- **Language (no Rust):** register the grammar in `extension.toml` (`[grammars.<name>]` with `repository` + `rev`), write `languages/<lang>/config.toml`, then author the tree-sitter `.scm` queries (`highlights.scm` at minimum; add `injections`, `brackets`, `indents`, `outline`, `textobjects`, `runnables`, `overrides`, `redactions` as needed). Grammar names are global in Zed; reusing a common key like `toml` replaces the existing grammar by that name. The single best reference for real queries is Zed's own built-in languages at [`crates/languages/src/`](https://github.com/zed-industries/zed/tree/main/crates/languages/src). Details + every capture name: `references/languages.md`.

- **Language server (Rust):** implement `language_server_command` to return the `Command` that launches the server. If the server targets an existing Zed language, declare `[language_servers.<id>] languages = ["TOML"]` (or the relevant built-in name) and skip `languages/<lang>/` plus `[grammars.*]`. The hard part is *acquiring* the binary — download from GitHub releases or install via npm, cache it under the extension's working dir, and only check for updates periodically (the method is called on every server start). Optionally implement `label_for_completion`/`label_for_symbol` for nicer completion styling and `language_server_initialization_options`/`language_server_workspace_configuration` for config. Details + the download/caching patterns: `references/language-servers.md`.

- **Theme / icon theme (no Rust):** author the JSON against the published schema (`https://zed.dev/schema/themes/v0.2.0.json` for color, `https://zed.dev/schema/icon_themes/v0.3.0.json` for icons), declare it with `themes = [...]` / `icon_themes = [...]`. Themes and icon themes **must be their own extension** — they can't be bundled with language support. Details + the full style-key catalog: `references/themes.md`.

- **MCP / context server (Rust):** implement `context_server_command` to launch the MCP server (stdio transport), register it with `[context_servers.<id>]`, and optionally `context_server_configuration` to surface install instructions + a settings JSON schema to the user. Details: `references/context-servers.md`.

- **Debug adapter (Rust):** implement `get_dap_binary` + `dap_request_kind` (and strongly prefer `dap_config_to_scenario`), register with `[debug_adapters.<name>]` and a JSON schema. Optionally add locators (`[debug_locators.<name>]`) to turn ordinary tasks like `cargo run` into debug sessions. Details: `references/debug-adapters.md`.

- **Snippets (no Rust):** write VS Code-style snippet JSON, reference the files with `snippets = ["./snippets/<lang>.json"]`. Details: `references/snippets.md`.

## Step 4 — Test as a dev extension (the inner loop)

This is the feedback loop; show it early.

1. In Zed, open the command palette and run `zed: install dev extension` (or the **Install Dev Extension** button on the Extensions page). Select the extension's root directory (the folder with `extension.toml`). Zed compiles the Rust (if any) and installs it. A "dev" badge appears.
2. After editing source, rebuild via the **Rebuild** affordance on the Extensions page (or reinstall). Grammar/query/theme/snippet changes are picked up on reload.
3. **Debug output:** `stdout`/`stderr` from your extension forwards to Zed. To see `println!`/`dbg!` and INFO logs, **launch Zed from a terminal with `zed --foreground`**. For errors, check `zed: open log` (`Zed.log`).
4. If a published extension with the same id is installed, the dev version overrides it ("Overridden by dev extension").

The full testing notes (including the wasm constraints that cause silent failures) are in `references/publishing.md` and `references/rust-api.md`.

## Step 5 — Publish (when ready)

Publishing is a PR to [`zed-industries/extensions`](https://github.com/zed-industries/extensions). Before that:

- **License is mandatory** (since 2025‑10‑01). A `LICENSE*` file at the repo root must be one of: Apache-2.0, BSD-2/3-Clause, CC-BY-4.0, GPLv3, LGPLv3, MIT, Unlicense, zlib. CI fails without it. This applies only to your extension code, not to tools it downloads.
- Test it thoroughly as a dev extension first — untested, non-functional submissions get closed.
- The PR adds your repo as a **Git submodule** under `extensions/<id>` and an entry to `extensions.toml`, then `pnpm sort-extensions`.

The complete flow, naming rules, capability-declaration requirements, and the update process are in `references/publishing.md`.

## Gotchas that bite everyone (internalize these)

These come from the WASM sandbox and Zed's distribution model. Most "my extension does nothing / crashes silently" reports trace to one of these:

- **`std::env::var` does not read the user's environment.** The extension runs in a wasm sandbox. To read env vars or find binaries in `PATH`, use the `Worktree` methods (`worktree.shell_env()`, `worktree.which(...)`), not std. See `references/rust-api.md`.
- **`#[cfg(...)]` platform directives don't work** the way you expect. Use `zed::current_platform()` to branch on OS/arch at runtime.
- **The extension cannot change its working directory** (`chdir` is deliberately blocked) and must not read or modify anything outside the environment Zed grants it.
- **Don't bundle a language server / DAP / MCP binary in the extension.** Download it at runtime or locate it in the user's `PATH`. Shipping the binary will get a publish rejected.
- **Themes and icon themes can't ride along with other features.** Ship them as separate extensions, even if developed in the same repo.
- **Grammar keys are global, not extension-local.** Registering `[grammars.toml]` overwrites the editor-wide `toml` grammar entry. Do not reuse a built-in/common grammar key to create a scoped variant. If you only need an LSP for an existing language, attach to the existing language name instead.
- **`id` is immutable once published** and must not contain `zed`, `Zed`, or `extension`. Theme ids conventionally end in `-theme`, snippet ids in `-snippets`.
- **`rustup`, not Homebrew.** (Worth repeating — it's the #1 setup failure.)

## Reference map

| File                             | Covers                                                                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `references/manifest.md`         | Full `extension.toml` schema, every capability section, `[[capabilities]]`, version compatibility                                    |
| `references/rust-api.md`         | `Extension` trait (all methods), helper functions, `Worktree`/`Command`/`CodeLabel`, WASM constraints, slash commands, docs indexing |
| `references/languages.md`        | `config.toml`, grammar registration, all tree-sitter query files + every capture, semantic tokens                                    |
| `references/language-servers.md` | LSP extensions: download/cache patterns (GitHub, npm), install status, completion/symbol labels, init/workspace config               |
| `references/themes.md`           | Color theme v0.2.0 + icon theme v0.3.0 schemas, style keys, syntax keys, players, SVG guidance                                       |
| `references/context-servers.md`  | MCP servers: `context_server_command`, `ContextServerConfiguration`, transport, settings                                             |
| `references/debug-adapters.md`   | DAP servers + locators: `get_dap_binary`, `dap_request_kind`, `dap_config_to_scenario`, scenarios                                    |
| `references/snippets.md`         | Snippet JSON format, manifest `snippets` field, placeholders, language scoping                                                       |
| `references/publishing.md`       | Dev install + testing, license requirement, the extensions-repo PR flow, versioning, naming                                          |
