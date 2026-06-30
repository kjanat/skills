# Debug Adapter (DAP) Extensions Reference

An extension can provide [Debug Adapter Protocol](https://microsoft.github.io/debug-adapter-protocol) servers for Zed's debugger, and/or **locators** that turn ordinary tasks (like `cargo run`) into debug sessions. Both are Rust. As always, **don't bundle the adapter binary** — download or locate it.

Trait surface and types: `references/rust-api.md`. The DAP types (`DebugAdapterBinary`, `DebugConfig`, `DebugScenario`, `DebugTaskDefinition`, `StartDebuggingRequestArgumentsRequest`, `TaskTemplate`, `DebugRequest`, `TcpArguments…`) are re-exported from `zed::extension::dap`.

## Manifest

```toml
[debug_adapters.my-debug-adapter]
# A schema is mandatory. schema_path is optional; defaults to
# debug_adapter_schemas/my-debug-adapter.json
schema_path = "relative/path/to/schema.json"

# optional: locators (can exist without an adapter)
[debug_locators.my-locator]

# capabilities for acquiring the adapter
[[capabilities]]
kind = "download_file"
host = "github.com"
path = ["**"]
```

The JSON schema describes the adapter's configuration object (what users put in `debug.json`). It's required even though `schema_path` is optional (a default path is used).

## Minimum viable adapter: two methods

### 1. `get_dap_binary`

```rust
fn get_dap_binary(
    &mut self,
    adapter_name: String,
    config: zed::DebugTaskDefinition,
    user_provided_debug_adapter_path: Option<String>,
    worktree: &zed::Worktree,
) -> zed::Result<zed::DebugAdapterBinary>
```

Return the command (binary + args + env, or TCP connection info) to start the DAP server. Acquire the binary here — download from GitHub/npm or use `user_provided_debug_adapter_path` / `worktree.which(...)`. **Check for updates only periodically**: this is called on every new debug session.

`DebugAdapterBinary` describes how to start the adapter — the executable and arguments, environment, optional `cwd`, and optionally TCP connection details (use `resolve_tcp_template`/`TcpArguments` for adapters that listen on a socket rather than stdio).

### 2. `dap_request_kind`

```rust
fn dap_request_kind(
    &mut self,
    adapter_name: String,
    config: zed::serde_json::Value,
) -> zed::Result<zed::StartDebuggingRequestArgumentsRequest>
```

Given a config, decide whether the session **launches** a new debuggee or **attaches** to a running one (`StartDebuggingRequestArgumentsRequest::Launch | Attach`). Do *only* this classification — no other validation. Return an error if the kind can't be determined (don't guess a default).

These two are enough to make the adapter usable in `debug.json`-based workflows.

## Strongly recommended: `dap_config_to_scenario`

```rust
fn dap_config_to_scenario(
    &mut self,
    config: zed::DebugConfig,
) -> zed::Result<zed::DebugScenario>
```

Used when the user spawns a session from the **New Process modal** (the GUI, not hand-written `debug.json`). It takes a generic, adapter-agnostic `DebugConfig` (program, args, cwd, env) and produces a concrete `DebugScenario` for your adapter. In plain terms: *"given a program + args + cwd + env, what does my adapter's config look like?"* Implement this so users get a GUI path, not just manual JSON.

The type distinction matters:

- **`DebugConfig`** — highest level, from the New Process modal, adapter-agnostic.
- **`DebugScenario`** — user-facing config used in `debug.json`; concerned with *what* to debug, mostly adapter-agnostic except adapter-specific options.
- **`DebugAdapterBinary`** — lowest level; how to actually start the adapter.

## Locators (turn tasks into debug sessions)

A locator converts a Zed task into a debug scenario — e.g. it sees a `cargo run` task and produces a scenario that runs `cargo build` then debugs `target/debug/<bin>`. **An extension can ship locators even without its own adapter**, and you should when your extension already provides language tasks: it lets users start debugging without manually configuring an adapter. Locators can be adapter-agnostic, so logic is shareable.

Two phases:

### Phase 1 — `dap_locator_create_scenario`

```rust
fn dap_locator_create_scenario(
    &mut self,
    locator_name: String,
    build_task: zed::TaskTemplate,
    resolved_label: String,
    debug_adapter_name: String,
) -> Option<zed::DebugScenario>
```

Run against each available task. Return `Some(scenario)` if this locator can provide a debugging counterpart for the task, else `None`. **Return `None` early and cheaply** — your locator will be offered tasks it shouldn't accept; bail before any expensive work.

A returned `DebugScenario` may include a **build task**. If it does, Zed runs the build, then calls phase 2 (`run_dap_locator`) to find the artifact. If you can determine the full configuration up front (common for interpreted languages), omit the `build` field and skip phase 2 entirely.

### Phase 2 — `run_dap_locator`

```rust
fn run_dap_locator(
    &mut self,
    locator_name: String,
    build_task: zed::TaskTemplate,
) -> zed::Result<zed::DebugRequest>
```

Runs after a build task succeeds. Use it when the build artifact's path isn't known up front (some build systems produce names you can't predict). It returns the adapter-agnostic launch request (which Zed then resolves via `dap_config_to_scenario`). It's "as if the user found the artifact path themselves."

## Acquisition

Same download/cache discipline as `references/language-servers.md` (Pattern A / B). Resolve the platform with `current_platform()`, fetch the right asset, cache under a versioned dir, and gate update checks.

## Testing

Install as a dev extension, then exercise it three ways: a hand-written `debug.json` (exercises `get_dap_binary` + `dap_request_kind`), the New Process modal (exercises `dap_config_to_scenario`), and a runnable task in a buffer (exercises your locator). `zed --foreground` shows adapter stdout/stderr. See `references/publishing.md`.

## Real examples

Filter the extensions site by debug adapters and read their repos for concrete `DebugAdapterBinary` construction and locator logic. Build-task and scenario docs: <https://zed.dev/docs/debugger.html>.
