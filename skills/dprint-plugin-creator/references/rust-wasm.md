# Rust → Wasm plugin (`SyncPluginHandler`)

The default and preferred path. The wrapped formatter is a Rust crate; the plugin compiles to
`wasm32-unknown-unknown` and runs in dprint's Wasm host. Canonical templates:
[`dprint-plugin-tex-fmt`](https://github.com/kjanat/dprint-plugin-tex-fmt),
[`dprint-plugin-svg`](https://github.com/kjanat/dprint-plugin-svg),
[`dprint-plugin-json-schema-sort`](https://github.com/kjanat/dprint-plugin-json-schema-sort).

## File layout

```
dprint-plugin-<NAME>/
├── Cargo.toml
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
dprint-core = { version = "0.67", features = ["formatting", "wasm"] }
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
lint       = "clippy --all-targets -- -D warnings"
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
        let source = std::str::from_utf8(&request.file_bytes)
            .map_err(|e| anyhow::anyhow!("file is not valid UTF-8: {e}"))?;

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
generate_plugin_code!(PluginHandler, PluginHandler::new());
```

`FileMatchingInfo` (returned from `resolve_config`) decides which files the plugin claims:

- `file_extensions: vec!["tex", "sty", ...]` for extension-based matching.
- `file_names: vec!["schema.json"]` to claim specific filenames (json-schema-sort does this so it doesn't
  collide with the generic JSON plugin on every `.json`).

## Config resolution (diagnostic-first, defaults from upstream)

Pattern from `src/config.rs` (tex-fmt) and `resolve_config` in svg's lib.rs:

```rust
use dprint_core::configuration::{
    ConfigurationDiagnostic, get_nullable_value, get_unknown_property_diagnostics, get_value,
};

pub fn resolve_config(
    mut config: ConfigKeyMap,
    global_config: &GlobalConfiguration,
) -> PluginResolveConfigurationResult<Configuration> {
    let mut diagnostics = Vec::<ConfigurationDiagnostic>::new();

    // Inherit from dprint global config; plugin key overrides it.
    let default_wraplen = global_config.line_width.unwrap_or(80) as usize;
    let wraplen = get_value(&mut config, "wraplen", default_wraplen, &mut diagnostics);

    // Source enum/struct defaults from the wrapped lib so they never drift:
    let svg_defaults = <formatter>::FormatOptions::default();
    let attribute_sort = get_value(
        &mut config, "attributeSort",
        unmap_attribute_sort(svg_defaults.attribute_sort),  // upstream → config enum
        &mut diagnostics,
    );

    // Validate domain constraints, push diagnostics, fall back to a safe value:
    if attributes_per_line == 0 {
        diagnostics.push(ConfigurationDiagnostic {
            property_name: "attributesPerLine".into(),
            message: "Expected a value greater than 0.".into(),
        });
        attributes_per_line = 1;
    }

    diagnostics.extend(get_unknown_property_diagnostics(config));   // ALWAYS last

    PluginResolveConfigurationResult {
        file_matching: FileMatchingInfo { file_extensions: vec!["<ext>".into()], file_names: vec![] },
        diagnostics,
        config: Configuration { /* ... */ },
    }
}
```

The **`unmap_*` pattern** is the key idea: for every option that maps to a wrapped-lib enum, write a pair
`map_x` (config → lib) and `unmap_x` (lib → config). Use `unmap_x(Lib::default().x)` as the config
default. This guarantees the plugin's defaults track the library's defaults across version bumps. See the
full set of `map_*`/`unmap_*` fns at the bottom of svg's `src/lib.rs`.

## Wasm dependency stubbing

Some transitive deps call browser/JS APIs that don't exist on bare `wasm32-unknown-unknown` (no JS host
in dprint). Symptom: unresolved imports at load time. Fix with a local stub crate + `[patch.crates-io]`.

tex-fmt does this for `web-time` (tex-fmt only uses `Instant` for discarded log timestamps):

```toml
# Cargo.toml
[patch.crates-io]
web-time = { path = "crates/web-time" }
```

The stub mirrors `std::time` on native and provides a counter-based `Instant`/`SystemTime` on wasm. See
`crates/web-time/src/wasm.rs` in tex-fmt for a complete, copyable implementation.

## Schema generation (inline build.rs variant)

`build.rs` `include!`s the config struct file, runs schemars, injects `$id` + any `x-*` extensions, sorts
keys for stable diffs, writes `schema.json`, and synthesizes `release-fragment.md` from the schema
defaults. Copy tex-fmt's `build.rs` wholesale and swap the type name / file-extension list. Add a CI step:

```yaml
- run: cargo build # regenerates schema.json via build.rs
- run: git diff --exit-code schema.json
```

**Sort the schema deterministically before writing it.** schemars' key order isn't guaranteed stable
across versions, which makes drift checks (`git diff --exit-code schema.json`) flaky and produces noisy
diffs. Use the [`json-schema-sort`](https://crates.io/crates/json-schema-sort) crate to canonicalize into
a stable, schema-aware key order — exactly what tex-fmt's `build.rs` does:

```rust
// in build.rs, after building the schema Value and injecting $id:
let sorted = json_schema_sort::sorted_schema(value);
let out = serde_json::to_string_pretty(&sorted).unwrap() + "\n";
std::fs::write("schema.json", out).unwrap();
```

```toml
# Cargo.toml
[build-dependencies]
json-schema-sort = { version = "0.1", default-features = false }
```

The same library also ships as a dprint plugin (`dprint add kjanat/json-schema-sort`), which keeps any
committed `schema.json` (and other `schema.json`-named files) sorted via `dprint fmt` — handy alongside
the build-time sort if you want the repo's schemas kept canonical without rebuilding. It claims only files
named `schema.json` by default (so it won't fight `dprint-plugin-json` over `package.json`); widen with an
`associations` glob if needed.

## Tests (`tests/format.rs` + fixtures)

Cover, at minimum (mirror tex-fmt's `tests/fixtures.rs` and svg's `tests/plugin_settings.rs`):

1. **Behavior** — a fixture `source/x.<ext>` formats to the committed `target/x.<ext>`.
2. **Idempotence** — formatting the output again returns `None` (no change). Non-negotiable.
3. **Unknown-key diagnostic** — an unknown config key yields a diagnostic with that `property_name`.
4. **Invalid UTF-8** — `format` returns `Err`, not a panic.
5. **plugin_info sanity** — `config_schema_url` ends with `/schema.json`, `update_url` is `Some`.

Drive `resolve_config` + `format` directly via `PluginHandler` against a `GlobalConfiguration::default()`;
no wasm needed for unit tests. Add an `e2e.sh` that builds the wasm and runs the real `dprint` binary over
the fixtures for a true end-to-end check (tex-fmt's `scripts/e2e.sh`).

## CI & release

- **ci.yml**: jobs for lint (`cargo clippy --all-targets -- -D warnings` + schema drift), test, a
  `cargo check --lib --target wasm32-unknown-unknown`, and a `wasm-release` build that uploads the
  `.wasm` artifact. Optionally an e2e job that downloads the artifact and runs `dprint fmt`.
- **release.yml**: trigger on a semver tag (`tags: ["[0-9]+.[0-9]+.[0-9]+"]` — **bare semver, no `v`
  prefix**), build `cargo wasm`, regenerate the schema, then `softprops/action-gh-release` uploading
  `plugin.wasm` + `schema.json` with `body_path: release-fragment.md` and `generate_release_notes: true`.
  Copy the built wasm to `plugin.wasm` (build.rs can do this, or do it in the workflow) — **that exact
  filename is what the proxy serves.**

Remember the immutability rule: a published version is frozen on the CDN. To fix a bad release, **bump the
version** — never re-upload over an existing one. See `references/release-notes.md` for the
`release-fragment.md` template and the optional GitHub hardening (immutable releases + blocking `v*` tags).
