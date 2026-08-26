---
name: dprint-plugin-creator
description: >-
  Scaffolds a new dprint formatter plugin that wraps an existing formatter library and bridges it to the
  dprint plugin protocol. Use when building or scaffolding a dprint plugin, wrapping a Rust, Go, or
  JavaScript formatter, or working on dprint plugin config resolution, schema generation, handler traits,
  registry metadata, npm distribution, or release flow. Selects Rust/Wasm, Go/TinyGo Wasm, or a
  V8-backed JavaScript process plugin.
metadata:
  version: "2026-08-26"
---

# dprint plugin creator

Bridge an existing formatter to dprint; do not reimplement its formatting algorithm. The plugin adapts
the formatter's options, input, and output to the dprint protocol.

## Core mental model

A dprint plugin is a small adapter implementing four responsibilities:

1. **Identity** — name, version, config key, schema URL, update URL (`plugin_info`).
2. **Config resolution** — read the user's `dprint.json` slice + global config, produce a typed config
   and a list of diagnostics for bad/unknown keys. Never hard-fail; diagnose.
3. **Format** — decode bytes (UTF-8), run the wrapped formatter, return `None` when the input is already
   canonical (this is what makes `dprint check` work) or the new bytes otherwise.
4. **Schema** — a JSON Schema describing the config, published alongside the artifact.

- **Idempotence** — formatting already-formatted output must produce no further change. Always add a test
  that formats twice and asserts the second pass is a no-op.
- **Diagnostic-first config** — invalid or unknown config keys produce `ConfigurationDiagnostic`s, not
  panics or errors.

## Step 0 — Before you build: does it already exist?

Before writing code:

- Search GitHub for `dprint-plugin-<TOOL>` across all owners, then check dprint's own organization,
  [dprint.dev/plugins](https://dprint.dev/plugins/), crates.io, and npm.
- Prefer an acceptable Rust- or Go-native formatter over a JavaScript process plugin; for JS/TS, check
  dprint's TypeScript and Biome plugins before reaching for Prettier.
- If a plugin already exists, link it and scaffold another only when it is unsuitable or explicitly
  requested.

## Step 1 — Pick the architecture

Ask (or infer) **what language the formatter library is written in**, then route:

| Wrapped formatter is… | Architecture                       | Reference                  | When                                                                                    |
| --------------------- | ---------------------------------- | -------------------------- | --------------------------------------------------------------------------------------- |
| A **Rust crate**      | Rust → Wasm (`SyncPluginHandler`)  | `references/rust-wasm.md`  | **Default.** Smallest artifact, simplest release, sandboxed in dprint's Wasm host.      |
| A **Go package**      | Go → TinyGo → Wasm                 | `references/go-wasm.md`    | Needs a runtime bridge and codegen, but still ships as one sandboxed `.wasm`.           |
| **JS/Node only**      | Process plugin over V8 (deno_core) | `references/process-v8.md` | Last resort when no suitable Wasm formatter exists. Ships native per-platform binaries. |

Decision rule: **Wasm if you possibly can.** Only reach for the V8 process plugin when the formatter is
JavaScript with no Rust/Go equivalent and can't reasonably be ported. If a formatter exists in multiple
languages, prefer the Rust one.

Process plugins **can't be loaded from a remote `extends` config** and **can't run through
`@dprint/formatter`**. They *can* be packaged on npm for the dprint CLI; do not confuse npm transport with
the Wasm-only programmatic host. Read [distribution.md](references/distribution.md) before publishing.

State the choice and why, then open only the matching architecture reference. The shared rules below
apply to every path.

## Step 2 — Shared conventions (bake these in by default)

These are house defaults. Apply them unless the user says otherwise.

### Naming & the proxy

- House repo: `github.com/<USER>/dprint-plugin-<NAME>`. Any public repo works; this prefix enables the
  short **`dprint add <USER>/<NAME>`** form, e.g. `kjanat/dprint-plugin-svg` → `dprint add kjanat/svg`.
- The published wasm asset on each release **must** be named `plugin.wasm` — that's the file the proxy
  serves for `dprint add <USER>/<NAME>`.
- Crate/lib name: `dprint-plugin-<NAME>` / `dprint_plugin_<NAME>`. Config key in `dprint.json`: the short
  camelCase form, e.g. `texFmt`, `svg`, `jsonSchemaSort`.
- Registry metadata should accurately declare `configKey`, `fileExtensions`, and `fileNames`. It may also
  provide `defaultConfig` and file-matched `configItems`, which `dprint init` uses to select plugins and
  scaffold useful configuration ([#1185], [#1186], [#1187]).

[#1185]: https://github.com/dprint/dprint/pull/1185
[#1186]: https://github.com/dprint/dprint/pull/1186
[#1187]: https://github.com/dprint/dprint/pull/1187

### URLs (all interpolate the repo path `<USER>/<NAME>` or short `<USER>/<short>`)

- `config_schema_url`: `https://plugins.dprint.dev/<USER>/<short>/<version>/schema.json`
- `update_url`: `https://plugins.dprint.dev/<USER>/<short>/latest.json`. **Do not forget this one** — it's
  what powers `dprint config update` notifications. Set it on every plugin, regardless of architecture.
- `help_url`: the GitHub repo URL by default, but it can point anywhere useful — a docs site, a hosted
  config reference, the upstream formatter's homepage — if the plugin has one.
- The generated `schema.json` `$id` matches `config_schema_url`.

Derive these at **compile time** from `env!("CARGO_PKG_VERSION")` and `env!("CARGO_PKG_REPOSITORY")` (Rust)
or `-ldflags` injection (Go) so the runtime can never drift from the published artifact.

### Config resolution

- Keys are **camelCase**; unknown keys emit diagnostics (`get_unknown_property_diagnostics`).
- **Inherit from dprint's global config** where it makes sense: `lineWidth` → the formatter's wrap width,
  `indentWidth` → tab/indent size, `useTabs` → tab char, `newLineKind` → EOL. Plugin-specific keys
  override global ones.
- **Track upstream defaults, don't hardcode them.** When the wrapped crate exposes a default options
  struct, source each default from it via `unmap_*` helpers (see the svg reference) so the plugin's
  defaults can never silently diverge from the library's. Only invent a default for options the library
  doesn't model.
- Plugin `associations` are **additive** to default file names/extensions; a negated glob removes a
  default match. All dprint globs are case-sensitive ([#1172], [#1089]).
- Users may place plugin options in per-file `overrides`. dprint resolves and passes the resulting config,
  so the plugin needs no parallel override mechanism; cover it in the CLI end-to-end test ([#1136]).

[#1089]: https://github.com/dprint/dprint/pull/1089
[#1136]: https://github.com/dprint/dprint/pull/1136
[#1172]: https://github.com/dprint/dprint/pull/1172

### Schema generation

- Generate `schema.json` from the Rust config type (`schemars`) — never hand-write it. Either inline in
  `build.rs` (simplest, see tex-fmt) or a feature-gated `generate-schema` bin (when you also generate docs,
  see svg). Go uses a `gen-json-schema` codegen tool from struct tags.
- Commit the generated schema and add a CI drift check (`<generate> && git diff --exit-code`). To keep
  that check reliable, sort the schema into a stable, canonical key order before writing it — the
  [`json-schema-sort`](https://crates.io/crates/json-schema-sort) crate does this (and is also available
  as a dprint plugin, `dprint add kjanat/json-schema-sort`). See `references/rust-wasm.md` for wiring.
- Write useful property descriptions, enum/const descriptions, and defaults. `dprint lsp` downloads each
  resolved plugin's schema to provide config completions and hover information ([#1177]).

[#1177]: https://github.com/dprint/dprint/pull/1177

### Release flow

- Treat released GitHub and npm artifacts as immutable. Never replace a binary for an existing version;
  bump and release again.
- **Tag on bare semver `*.*.*`, not `v*.*.*`.** The house convention is unprefixed tags
  (`tags: ["[0-9]+.[0-9]+.[0-9]+"]`), e.g. `0.1.0`, not `v0.1.0`. Keep tag, `Cargo.toml`/`go.mod` version,
  and schema `$id` in lockstep. The proxy forbids `-` in tags, so prerelease tags such as `1.0.0-beta.1`
  do not resolve even though they are valid SemVer.
- Tag-triggered CI builds and tests the artifact, regenerates the schema, and publishes the GitHub release.
  The proxy selects the newest release that is neither a draft nor marked prerelease, so the proxy-facing
  release must be published and non-prerelease.
- npm is a first-class CLI source for both Wasm and process plugins. If registry `info.json`/`latest.json`
  declares an `npm` package, dprint prefers an npm specifier and resolves its version from npm ([#1215]).
  `dprint add npm:<package>` auto-detects Wasm versus `plugin.json` when no path is supplied ([#1183]).
  Only Wasm packages can additionally expose the plugin through `@dprint/formatter`.
- Read [distribution.md](references/distribution.md) for registry/npm metadata, package layouts, checksums,
  and verification. Read [release-notes.md](references/release-notes.md) for release-body templates and
  optional GitHub hardening.

[#1183]: https://github.com/dprint/dprint/pull/1183
[#1215]: https://github.com/dprint/dprint/pull/1215

## Step 3 — Verify before declaring done

Walk this checklist regardless of architecture:

- [ ] Confirmed no existing `dprint-plugin-<TOOL>` (esp. in dprint's own org) and no lighter Rust-native
      equivalent before building (Step 0).
- [ ] `plugin_info` URLs all interpolate version + repo path; nothing hardcoded.
- [ ] `update_url` is set (not `None`/empty) — points at
      `https://plugins.dprint.dev/<USER>/<short>/latest.json`.
- [ ] Config resolution emits a diagnostic for an unknown key (test it).
- [ ] Formatting an already-formatted file returns "no change" (idempotence test).
- [ ] Invalid UTF-8 input returns an error, not a panic.
- [ ] Rust code, tests, bins, examples, and build scripts pass the strict Clippy profile in
      `rust-wasm-build.md`; do not settle for baseline `-D warnings`.
- [ ] `schema.json` is generated, committed, and CI checks it isn't stale.
- [ ] Schema descriptions/defaults are useful in `dprint lsp` completions and hover.
- [ ] The release artifact is named `plugin.wasm` (Wasm paths) and the README documents
      `dprint add <USER>/<NAME>`.
- [ ] Registry matching metadata is accurate; `defaultConfig`/`configItems` are present when useful.
- [ ] If publishing to npm, package path and registry `npm` metadata agree; process packages contain
      `plugin.json`, while Wasm packages intended for JS expose `getPath()` or `getBuffer()`.
- [ ] Release workflow triggers on a **bare semver tag** (`*.*.*`, not `v*.*.*`).
- [ ] Never plan to re-upload a binary to an existing release — a mistake means **bump + re-release**.
- [ ] At least one fixture pair plus real `dprint fmt`, `dprint add --checksum`, and
      `dprint config update --dry-run` end-to-end checks ([#1184], [#1156]).

[#1156]: https://github.com/dprint/dprint/pull/1156
[#1184]: https://github.com/dprint/dprint/pull/1184

## Reading order

| Task                         | Read                                                                                              |
| ---------------------------- | ------------------------------------------------------------------------------------------------- |
| Rust formatter               | [rust-wasm.md](references/rust-wasm.md), then [rust-wasm-build.md](references/rust-wasm-build.md) |
| Go formatter                 | [go-wasm.md](references/go-wasm.md)                                                               |
| JavaScript formatter over V8 | [process-v8.md](references/process-v8.md)                                                         |
| Publish/register/install     | [distribution.md](references/distribution.md)                                                     |
| Compose release notes        | [release-notes.md](references/release-notes.md)                                                   |

For any path, the user's own repos are the canonical templates to copy from rather than reproduce from
memory:

- Rust/Wasm: [`dprint-plugin-tex-fmt`](https://github.com/kjanat/dprint-plugin-tex-fmt) ·
  [`dprint-plugin-svg`](https://github.com/kjanat/dprint-plugin-svg) ·
  [`dprint-plugin-json-schema-sort`](https://github.com/kjanat/dprint-plugin-json-schema-sort)
- Go/TinyGo: [`dprint-plugin-shfmt`](https://github.com/kjanat/dprint-plugin-shfmt)
- V8 process plugin: [`dprint-plugin-svgo`](https://github.com/kjanat/dprint-plugin-svgo)

When in doubt, open the real source — it's authoritative over anything reconstructed here.
