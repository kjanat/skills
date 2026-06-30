# MCP / Context Server Extensions Reference

An extension can expose a [Model Context Protocol](https://modelcontextprotocol.io) server to Zed's Agent Panel. The extension's job is to **launch the MCP server process** (stdio transport) and optionally surface setup/configuration to the user. It does not implement MCP itself — it starts a server that does. As with language servers, **don't bundle the server binary**; download it, install via npm, run via `npx`/`uvx`, or locate it on the user's machine.

Trait surface: `references/rust-api.md`. WASM constraints (especially `worktree`/`project` env access vs `std::env`): same file, §6.

## Manifest

```toml
[context_servers.my-mcp-server]
# no required fields; behavior is in Rust

# capabilities, tuned to how you launch the server:
[[capabilities]]
kind    = "process:exec"
command = "npx"
args    = ["**"]
```

Multiple servers → multiple `[context_servers.X]` tables. The table key is the `ContextServerId`.

## The core method

```rust
fn context_server_command(
    &mut self,
    context_server_id: &zed::ContextServerId,
    project: &zed::Project,
) -> zed::Result<zed::Command>
```

Return the `Command` that launches the MCP server speaking MCP over **stdio**. Like the LSP method, this can run repeatedly — do any download/install once and cache.

### Pattern — run an npm-published MCP server via npx

```rust
use zed_extension_api::{self as zed, Result};

struct MyMcpExtension;

impl zed::Extension for MyMcpExtension {
    fn new() -> Self { Self }

    fn context_server_command(
        &mut self,
        _id: &zed::ContextServerId,
        _project: &zed::Project,
    ) -> Result<zed::Command> {
        Ok(zed::Command {
            command: "npx".into(),
            args: vec!["-y".into(), "@org/my-mcp-server".into()],
            env: vec![
                // pull a secret from the user's settings (see context_server_configuration)
                ("MY_API_KEY".into(), get_api_key_from_settings()?),
            ],
        })
    }
}

zed::register_extension!(MyMcpExtension);
```

### Pattern — download a compiled MCP server

Identical to the GitHub-release flow in `references/language-servers.md` (Pattern A): resolve `latest_github_release`, pick the asset for `current_platform()`, `download_file` into a versioned dir, `make_file_executable`, cache the path on `self`, then return it as the command.

### Reading the environment / project

The server often needs env vars (API keys, project paths). Get them the sandbox-correct way:

- From the `project`/worktree, not `std::env`.
- From user settings via `context_server_configuration` (below), which exposes a settings schema and the user's filled-in values.

## Surfacing configuration to the user

Most MCP servers need credentials or options. Implement `context_server_configuration` to give the user a guided setup: Markdown instructions, a JSON Schema for the settings (so Zed can validate/auto-complete them), and a default settings template.

```rust
fn context_server_configuration(
    &mut self,
    _id: &zed::ContextServerId,
    _project: &zed::Project,
) -> zed::Result<Option<zed::ContextServerConfiguration>> {
    let installation_instructions =
        include_str!("../configuration/instructions.md").to_string();
    let default_settings = include_str!("../configuration/default_settings.jsonc").to_string();
    let settings_schema = zed::serde_json::to_string(&zed::serde_json::json!({
        "type": "object",
        "properties": {
            "api_key": { "type": "string", "description": "Your API key" }
        },
        "required": ["api_key"]
    })).unwrap();

    Ok(Some(zed::ContextServerConfiguration {
        installation_instructions,
        settings_schema,
        default_settings,
    }))
}
```

`ContextServerConfiguration` fields (all `String`):

- `installation_instructions` — Markdown shown to the user for setup.
- `settings_schema` — a JSON Schema string used to validate the user's settings and drive completion.
- `default_settings` — a settings template the user starts from.

The user fills these in via Zed settings; you then read the values (e.g. in `context_server_command`) to build the launch env. **Per Zed's extension policy, an extension must not modify the user's real environment** — instead it requests configuration from the user through this mechanism.

## Testing

Install as a dev extension, open the Agent Panel, and confirm the server connects and its tools appear. Run Zed with `zed --foreground` to see the server's stdout/stderr and any launch errors. See `references/publishing.md`.

## Real examples

Published MCP extensions (Context7, code-runner, various docs servers) in the registry show common launch strategies; filter the extensions site by MCP servers and read their repos.
