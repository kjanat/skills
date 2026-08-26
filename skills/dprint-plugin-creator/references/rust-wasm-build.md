# Rust/Wasm configuration, schema, tests, and release

Read after [rust-wasm.md](rust-wasm.md) when implementing and shipping the Rust/Wasm path.

## Config resolution

Resolve plugin keys diagnostically, inherit appropriate global values, and source defaults from the
wrapped formatter:

```rust
use dprint_core::configuration::{
    ConfigurationDiagnostic, get_unknown_property_diagnostics, get_value,
};

#[must_use]
pub fn resolve_config(
    mut config: ConfigKeyMap,
    global_config: &GlobalConfiguration,
) -> PluginResolveConfigurationResult<Configuration> {
    let mut diagnostics = Vec::<ConfigurationDiagnostic>::new();
    let default_wraplen = usize::try_from(global_config.line_width.unwrap_or(80))
        .unwrap_or(usize::MAX);
    let wraplen = get_value(&mut config, "wraplen", default_wraplen, &mut diagnostics);

    let formatter_defaults = <formatter>::FormatOptions::default();
    let attribute_sort = get_value(
        &mut config,
        "attributeSort",
        unmap_attribute_sort(formatter_defaults.attribute_sort),
        &mut diagnostics,
    );

    if attributes_per_line == 0 {
        diagnostics.push(ConfigurationDiagnostic {
            property_name: "attributesPerLine".into(),
            message: "Expected a value greater than 0.".into(),
        });
        attributes_per_line = 1;
    }

    diagnostics.extend(get_unknown_property_diagnostics(config));
    PluginResolveConfigurationResult {
        file_matching: FileMatchingInfo {
            file_extensions: vec!["<ext>".into()],
            file_names: vec![],
        },
        diagnostics,
        config: Configuration { /* ... */ },
    }
}
```

For every wrapped-formatter enum, pair `map_x` (config → formatter) with `unmap_x` (formatter → config),
then derive the config default with `unmap_x(FormatterOptions::default().x)`. This prevents silent default
drift across dependency upgrades. Make pure `map_*`, `unmap_*`, and scalar default helpers `const fn` when
their operations permit it.

## Strict lint policy

Put the lint policy in `Cargo.toml` so every Clippy invocation uses the same contract. This includes local
editors when their Rust analyzer is configured to run Clippy instead of its default `cargo check`:

```toml
[lints.rust]
warnings = "deny"

[lints.clippy]
all      = { level = "deny", priority = -1 }
pedantic = { level = "deny", priority = -1 }
nursery  = { level = "deny", priority = -1 }
cargo    = { level = "deny", priority = -1 }

# Transitive dependencies may legitimately require two semver-incompatible versions.
multiple_crate_versions = "allow"
```

For a workspace, put these under `[workspace.lints.rust]` and `[workspace.lints.clippy]`, then add
`[lints] workspace = true` to every member. Do not enable `clippy::restriction` as a group: it contains
deliberately incompatible and context-specific lints. Enable an individual restriction lint only when it
expresses a project rule.

Run both `cargo lint` and `cargo lint-wasm`. The aliases in [rust-wasm.md](rust-wasm.md) cover every Cargo
target kind and feature on the host plus the plugin library on `wasm32-unknown-unknown`. Fix first-party
findings instead of adding a crate-wide allow. In particular:

- document public fallible functions with `# Errors`, public panicking functions with `# Panics`, and add
  `#[must_use]` where ignoring the result is almost certainly a bug;
- use checked or lossless conversions instead of `as`, merge identical match arms, avoid wildcard
  imports, prefer `Self` for the current type inside an `impl`, and keep functions below Clippy's
  complexity/length thresholds;
- make eligible helpers `const fn` and use method pointers such as `map(ToString::to_string)` instead of
  redundant closures;
- when an external derive contract forces a shape Clippy rejects, place a narrow, reasoned `#[allow]` on
  that item. A Schemars default provider that must return `Option<T>` may need
  `#[allow(clippy::unnecessary_wraps, reason = "Schemars requires the field type")]`.

The gate applies to library code, tests, examples, bins, and `build.rs`. A Cargo future-incompatibility
notice from a transitive dependency is not a first-party Clippy finding; inspect it with
`cargo report future-incompatibilities` and update the dependency when possible.

## Wasm dependency stubbing

Bare `wasm32-unknown-unknown` has no browser/JS host. If a transitive dependency imports unavailable APIs,
patch it with a local stub crate. tex-fmt does this for `web-time`:

```toml
[patch.crates-io]
web-time = { path = "crates/web-time" }
```

Copy the proven stub from tex-fmt and retain native behavior; do not invent broad fake APIs merely to make
the linker pass.

## Schema generation

Have `build.rs` include the config type, run `schemars`, inject the versioned `$id`, sort the schema, and
write `schema.json`. Also generate `release-fragment.md` there when using the tex-fmt pattern.

```rust
let sorted = json_schema_sort::sorted_schema(value);
let out = serde_json::to_string_pretty(&sorted).unwrap() + "\n";
std::fs::write("schema.json", out).unwrap();
```

```toml
[build-dependencies]
json-schema-sort = { version = "0.1", default-features = false }
```

CI must regenerate the schema and run `git diff --exit-code schema.json`. Descriptions, enum/const
descriptions, and defaults are user-facing because `dprint lsp` downloads the resolved plugin schema for
config completion and hover ([dprint/dprint#1177]).

[dprint/dprint#1177]: https://github.com/dprint/dprint/pull/1177

## Tests

Cover at least:

1. A committed input/expected-output fixture.
2. A second formatting pass returning `None`.
3. An unknown-key diagnostic naming the property.
4. Invalid UTF-8 returning `Err` rather than panicking.
5. `plugin_info` schema/update URL sanity.
6. A real CLI configuration covering additive/negated associations and a per-file override when relevant.

Drive `resolve_config` and `format` directly for unit tests, then build the Wasm and run the real dprint CLI
over fixtures for the end-to-end gate.

## CI and release

- Run `cargo fmt --all --check`, `cargo lint`, and `cargo lint-wasm`, then check schema drift.
- Test native handler behavior and `cargo check --lib --target wasm32-unknown-unknown`.
- Build the size-optimized Wasm and exercise the downloaded CI artifact end to end.
- On a bare-semver tag, regenerate schema/release notes and publish `plugin.wasm` plus `schema.json`.

Treat a published version as immutable. Use [release-notes.md](release-notes.md) for release bodies and
[distribution.md](distribution.md) for npm, registry metadata, checksums, and published-artifact checks.
