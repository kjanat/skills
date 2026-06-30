# `extension.toml` — Manifest Reference

The manifest at the repo root is the source of truth for an extension's identity and capabilities. It is TOML. Every extension has one; capability sections are added only for the features the extension provides.

## Identity fields (required)

```toml
id             = "my-extension"                         # Primary identifier. IMMUTABLE after publishing.
name           = "My Extension"                         # Human-readable, shown in the Extensions UI.
version        = "0.0.1"                                # SemVer. Must match the version entry in extensions.toml when publishing.
schema_version = 1                                      # Manifest schema version. Currently 1.
authors        = ["Your Name <you@example.com>"]
description    = "What the extension does"
repository     = "https://github.com/you/my-extension"
```

Naming rules (enforced at publish time):

- `id` must **not** contain `zed`, `Zed`, or `extension` — every extension is a Zed extension, so it's redundant.
- `id` should describe the purpose. Convention: themes end in `-theme`, icon themes in `-icon-theme` (or similar), snippet packs in `-snippets`. Language/tooling extensions may use the tool's name directly (e.g. `gleam`, `ruby`) when users would expect to find it under that id.
- `id` cannot be changed after the extension is published — choose carefully.

## Capability sections

An extension declares each capability it provides. Mix and match, with the caveat that **themes/icon themes must be their own extension** and cannot be combined with other capabilities.

### Grammars (language extensions)

Register each tree-sitter grammar the extension uses. Grammars are compiled from their source repo to wasm by Zed's builder.

```toml
[grammars.my-language]
repository = "https://github.com/org/tree-sitter-my-language"
rev        = "58b7cac8fc14c92b0677c542610d8738c373fa81"        # a commit SHA (or tag)
# path = "subdir"   # optional: if the grammar lives in a subdirectory of the repo
```

- `repository` — where to fetch the grammar from. For **local development** you may use a `file://` URL.
- `rev` — a Git revision (commit SHA strongly preferred for reproducibility; a tag works).
- `path` — optional subdirectory, for monorepos that contain the grammar under a subfolder.
- One extension can register multiple grammars (multiple `[grammars.X]` tables).

The grammar `name` (the table key) is what `languages/<lang>/config.toml`'s `grammar = "..."` field references. See `references/languages.md`.

### Language servers

Declares that the extension provides an LSP adapter. The Rust code implements the actual launch (`language_server_command`).

```toml
[language_servers.my-language-lsp]
name      = "My Language LSP"  # display name
languages = ["My Language"]    # must match the `name` in the language's config.toml

# language_ids maps Zed language names -> the LSP's own languageId strings, for multi-language servers:
[language_servers.my-language-lsp.language_ids]
"JavaScript" = "javascript"
"TSX"        = "typescriptreact"
```

- `languages` — the Zed language names this server attaches to. Each must equal a `name` from some `languages/<lang>/config.toml` (in this extension or built into Zed).
- `language_ids` — optional. Use when one server handles several languages and needs the LSP-spec `languageId` per language.
- Multiple servers: add multiple `[language_servers.X]` tables. Users can order/disable them via the `language_servers` setting.

### Context servers (MCP)

```toml
[context_servers.my-mcp-server]
# No required fields here; behavior is defined in Rust (context_server_command).
```

The Rust `context_server_command` returns the launch `Command`; `context_server_configuration` can surface install instructions + a settings schema. See `references/context-servers.md`.

### Debug adapters (DAP)

```toml
[debug_adapters.my-debug-adapter]
# schema_path is optional but a schema is mandatory.
# Defaults to debug_adapter_schemas/<adapter-id>.json if omitted.
schema_path = "relative/path/to/schema.json"
```

### Debug locators

A locator turns an ordinary task (e.g. `cargo run`) into a debug scenario. An extension can ship locators even without a debug adapter.

```toml
[debug_locators.my-locator]
```

See `references/debug-adapters.md` for both.

### Themes

```toml
themes = ["themes/my-theme.json"]
```

An array of paths (relative to `extension.toml`) to theme-family JSON files. **Must be a theme-only extension.** See `references/themes.md`.

### Icon themes

```toml
icon_themes = ["icon_themes/my-icon-theme.json"]
```

An array of paths to icon-theme JSON files. Icons referenced inside are resolved relative to the extension root. **Must be an icon-theme-only extension.**

### Snippets

```toml
snippets = ["./snippets/rust.json", "./snippets/typescript.json"]
```

An array of paths to snippet JSON files. File naming controls scope: `rust.json` applies to Rust (lowercase language name); `snippets.json` applies to all languages. See `references/snippets.md`.

### Slash commands (legacy)

Slash commands target the older Assistant flow. They still exist in the API but are de-emphasized in current Zed (the Agent Panel favors MCP/context servers). Include only if you specifically need them.

```toml
[slash_commands.my-command]
description       = "What the command does"
requires_argument = false
# tooltip_text = "..."   # optional
```

The Rust side implements `run_slash_command` and optionally `complete_slash_command_argument`. See `references/rust-api.md`.

## Declared capabilities (`[[capabilities]]`)

Separately from *what features it provides*, an extension declares the **host operations it needs permission to perform**: executing processes, downloading files, installing npm packages. Zed's capability system gates these, and users can further restrict them via the `granted_extension_capabilities` setting. Declare exactly what you use.

```toml
# Allow running a specific command (here: any args to `git`)
[[capabilities]]
kind    = "process:exec"
command = "git"
args    = ["**"]

# Allow downloading from a host (here: anything on github.com)
[[capabilities]]
kind = "download_file"
host = "github.com"
path = ["**"]

# Allow installing a specific npm package
[[capabilities]]
kind    = "npm:install"
package = "typescript"
```

The three capability kinds:

| `kind`          | Grants                            | Fields                                                        |
| --------------- | --------------------------------- | ------------------------------------------------------------- |
| `process:exec`  | `zed::process::Command` execution | `command` (name or `*`), `args` (glob array, `**` = anything) |
| `download_file` | `zed::download_file`              | `host` (or `*`), `path` (glob array)                          |
| `npm:install`   | `zed::npm_install_package`        | `package` (name or `*`)                                       |

Globs: `*` matches one segment, `**` matches any number. Narrow these to what you actually need — broad capabilities draw reviewer scrutiny and reduce user trust. A language-server extension that downloads from GitHub typically needs `download_file` for `github.com` plus maybe `process:exec` for the server binary; an npm-based server needs `npm:install` and a `process:exec` for `node`.

## Directory structure (all capabilities)

```
my-extension/
  extension.toml
  LICENSE                         # required to publish
  Cargo.toml                      # if Rust
  src/
    lib.rs                        # if Rust
  languages/
    my-language/
      config.toml
      highlights.scm
      injections.scm              # + brackets/indents/outline/textobjects/runnables/overrides/redactions as needed
      semantic_token_rules.json   # optional, for custom LSP token types
  themes/
    my-theme.json
  icon_themes/
    my-icon-theme.json
    icons/*.svg
  snippets/
    rust.json
  debug_adapter_schemas/
    my-debug-adapter.json
```

## API version compatibility

The Rust crate version (`zed_extension_api` in `Cargo.toml`) determines which WIT interface the compiled wasm binds to, which in turn determines the minimum Zed version that can run it. Zed embeds the API version in the built artifact and instantiates the extension against the matching interface.

- Use the latest `zed_extension_api` on crates.io unless you must support older Zed.
- Newer API versions can change trait signatures; bumping may require code edits.
- Compatibility table: <https://github.com/zed-industries/zed/blob/main/crates/extension_api#compatible-zed-versions>.
- The WIT definitions themselves live at `crates/extension_api/wit/since_v0.X.0/` in `zed-industries/zed` — the authoritative contract if you need to verify a signature.
