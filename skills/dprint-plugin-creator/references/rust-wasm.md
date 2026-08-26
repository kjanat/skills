# Rust → Wasm plugin (`SyncPluginHandler`)

The default and preferred path. The wrapped formatter is a Rust crate; the plugin compiles to
`wasm32-unknown-unknown` and runs in dprint's Wasm host. These are architecture examples, not substitutes
for the strict lint gate in [rust-wasm-build.md](rust-wasm-build.md):
[`dprint-plugin-tex-fmt`](https://github.com/kjanat/dprint-plugin-tex-fmt),
[`dprint-plugin-svg`](https://github.com/kjanat/dprint-plugin-svg),
[`dprint-plugin-json-schema-sort`](https://github.com/kjanat/dprint-plugin-json-schema-sort).

## File layout

```
dprint-plugin-<NAME>/
├── Cargo.toml
├── Cargo.lock               # commit it; CI and cargo lint use --locked
├── rust-toolchain.toml
├── .cargo/config.toml
├── build.rs                 # (optional) inline schema + release-fragment generation
├── src/
│   ├── lib.rs               # SyncPluginHandler impl + generate_plugin_code!
│   ├── config.rs            # resolve_config (optional split; tex-fmt does this)
│   └── schema.rs            # schema model when using a generate-schema bin (svg does this)
├── tests/
│   ├── format.rs            # behavior + idempotence + diagnostics
│   └── fixtures/<case>/{source,target}/...
└── .github/workflows/{ci.yml,release.yml}
```

Two viable schema strategies — pick one:

- **Inline in `build.rs`** (tex-fmt): a `schema_types.rs` is `include!`d by both `build.rs` and the lib;
  `build.rs` runs `schemars::schema_for!` and writes `schema.json` + `release-fragment.md`. Simplest.
- **Feature-gated bin** (svg): a `schema` feature gates `src/schema.rs`; `src/bin/generate-schema.rs`
  writes the schema. Use when you also generate docs from the same model.

## Cargo.toml

```toml
[package]
name         = "dprint-plugin-<NAME>"
version      = "0.1.0"
edition      = "2024"
rust-version = "1.85"
description  = "dprint Wasm plugin that formats <NAME>"
readme       = "README.md"
repository   = "https://github.com/<USER>/dprint-plugin-<NAME>"
license      = "MIT"   # house default; Apache-2.0 or "Apache-2.0 OR MIT" also fine. Inherit upstream's for a fork.
keywords     = ["dprint", "formatter", "<NAME>", "wasm"]
categories   = ["development-tools", "text-editors"]
publish      = false
autobins     = false

[lib]
crate-type = ["cdylib", "lib"]
name       = "dprint_plugin_<NAME>"
path       = "src/lib.rs"

[dependencies]
anyhow      = "1"
dprint-core = { version = "0.68", features = ["formatting", "wasm"] }
dprint-core-macros = "0.1"
serde       = { version = "1", features = ["derive"] }
serde_json  = "1"
schemars    = "1"            # if generating schema from types
# the wrapped formatter crate:
<formatter> = "x"

# Size-optimized profile: cold-load cost dominates a dprint plugin, so trade
# compile time / steady-state speed for a smaller binary.
[profile.wasm-release]
inherits      = "release"
opt-level     = "z"
strip         = true
lto           = "fat"
panic         = "abort"
codegen-units = 1
```

`dprint-core` 0.68.3 was released in [dprint/dprint#1212]. Re-check the current compatible release when
scaffolding rather than copying that patch version.

[dprint/dprint#1212]: https://github.com/dprint/dprint/pull/1212

## rust-toolchain.toml & .cargo/config.toml

```toml
# rust-toolchain.toml
[toolchain]
channel    = "stable"
components = ["clippy", "rustfmt"]
targets    = ["wasm32-unknown-unknown"]
```

```toml
# .cargo/config.toml — bump the wasm stack if the formatter recurses deeply.
[target.wasm32-unknown-unknown]
rustflags = ["-Clink-args=-z stack-size=10485760"]

[alias]
wasm       = "build --profile wasm-release --target wasm32-unknown-unknown"
check-wasm = "check --lib --target wasm32-unknown-unknown"
lint       = "clippy --locked --workspace --all-targets --all-features"
lint-wasm  = "clippy --locked --lib --target wasm32-unknown-unknown --all-features"
```

## src/lib.rs (the core)

Implement `SyncPluginHandler<Configuration>` with five methods. Skeleton (adapt from tex-fmt's lib.rs):

```rust
use dprint_core::configuration::{ConfigKeyMap, GlobalConfiguration};
use dprint_core::plugins::{
    CheckConfigUpdatesMessage, ConfigChange, PluginInfo, PluginResolveConfigurationResult,
    SyncFormatRequest, SyncHostFormatRequest, SyncPluginHandler,
};

pub struct PluginHandler;

impl SyncPluginHandler<Configuration> for PluginHandler {
    fn plugin_info(&mut self) -> PluginInfo {
        PluginInfo {
            name: env!("CARGO_PKG_NAME").to_string(),
            version: env!("CARGO_PKG_VERSION").to_string(),
            config_key: "<configKey>".to_string(),           // short camelCase
            help_url: env!("CARGO_PKG_REPOSITORY").to_string(), // or a docs/website URL if you have one
            config_schema_url: format!(
                "https://plugins.dprint.dev/<USER>/<short>/{}/schema.json",
                env!("CARGO_PKG_VERSION")
            ),
            update_url: Some("https://plugins.dprint.dev/<USER>/<short>/latest.json".to_string()), // required — don't drop this
        }
    }

    fn license_text(&mut self) -> String { include_str!("../LICENSE-MIT").to_string() }

    fn resolve_config(
        &mut self,
        config: ConfigKeyMap,
        global_config: &GlobalConfiguration,
    ) -> PluginResolveConfigurationResult<Configuration> {
        resolve_config(config, global_config) // see below
    }

    fn check_config_updates(
        &self,
        _message: CheckConfigUpdatesMessage,
    ) -> anyhow::Result<Vec<ConfigChange>> {
        Ok(Vec::new()) // no deprecated keys to migrate
    }

    fn format(
        &mut self,
        request: SyncFormatRequest<Configuration>,
        _format_with_host: impl FnMut(SyncHostFormatRequest) -> dprint_core::plugins::FormatResult,
    ) -> dprint_core::plugins::FormatResult {
        let source = std::str::from_utf8(&request.file_bytes)?;

        let formatted = run_wrapped_formatter(source, &request.config); // build the lib's options here

        if formatted == source {
            Ok(None)                       // already canonical → enables `dprint check`
        } else {
            Ok(Some(formatted.into_bytes()))
        }
    }
}

// Emits the wasm exports. Only compiled for the wasm target.
#[cfg(all(target_arch = "wasm32", target_os = "unknown"))]
use dprint_core::generate_plugin_code;
#[cfg(all(target_arch = "wasm32", target_os = "unknown"))]
generate_plugin_code!(PluginHandler, PluginHandler);
```

`Utf8Error` converts directly into `FormatError` on the current core line, so `?` preserves the original
error without an `anyhow!` wrapper ([dprint/dprint#1202]).

[dprint/dprint#1202]: https://github.com/dprint/dprint/pull/1202

`FileMatchingInfo` (returned from `resolve_config`) decides which files the plugin claims:

- `file_extensions: vec!["tex", "sty", ...]` for extension-based matching.
- `file_names: vec!["schema.json"]` to claim specific filenames (json-schema-sort does this so it doesn't
  collide with the generic JSON plugin on every `.json`).

User-supplied `associations` add to these defaults, and negated associations remove defaults
([dprint/dprint#1172]); glob matching is case-sensitive ([dprint/dprint#1089]). Per-file `overrides` are
resolved by dprint before `resolve_config`, so do not implement a second override system in the plugin
([dprint/dprint#1136]).

[dprint/dprint#1089]: https://github.com/dprint/dprint/pull/1089
[dprint/dprint#1136]: https://github.com/dprint/dprint/pull/1136
[dprint/dprint#1172]: https://github.com/dprint/dprint/pull/1172

Continue with [rust-wasm-build.md](rust-wasm-build.md) for config resolution, dependency stubbing, schema
generation, tests, CI, and release verification.
