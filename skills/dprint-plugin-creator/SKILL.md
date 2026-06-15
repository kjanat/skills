---
name: dprint-plugin-creator
description: >-
  Scaffolds a new dprint formatter plugin that wraps an existing formatter library and bridges it to the
  dprint plugin protocol. Use this skill whenever the user wants to build, scaffold, or set up a dprint
  plugin, wrap a formatter (a Rust crate, a Go library, or a JS/Node tool) as a dprint plugin, "make
  a given tool work with dprint", or asks anything about dprint plugin structure, config resolution, schema
  generation, the SyncPluginHandler/AsyncPluginHandler traits, or the plugins.dprint.dev release flow —
  even if they don't say the word "skill". Picks the correct plugin architecture (Rust/Wasm, Go/TinyGo
  Wasm, or process-plugin-over-V8) based on what language the formatter being wrapped is written in.
---

# dprint plugin creator

This skill scaffolds a **dprint formatter plugin** whose job is to **bridge an existing formatter to
dprint** — not to write the formatting algorithm itself. The wrapped formatter (a Rust crate, a Go
package, or a JS library) does the actual work; the plugin adapts its options to dprint config and its
output to the dprint protocol.

## Core mental model

A dprint plugin is a small adapter implementing four responsibilities:

1. **Identity** — name, version, config key, schema URL, update URL (`plugin_info`).
2. **Config resolution** — read the user's `dprint.json` slice + global config, produce a typed config
   and a list of diagnostics for bad/unknown keys. Never hard-fail; diagnose.
3. **Format** — decode bytes (UTF-8), run the wrapped formatter, return `None` when the input is already
   canonical (this is what makes `dprint check` work) or the new bytes otherwise.
4. **Schema** — a JSON Schema describing the config, published alongside the artifact.

Two non-negotiable behavioral contracts the wrapped formatter must satisfy through the plugin:

- **Idempotence** — formatting already-formatted output must produce no further change. Always add a test
  that formats twice and asserts the second pass is a no-op.
- **Diagnostic-first config** — invalid or unknown config keys produce `ConfigurationDiagnostic`s, not
  panics or errors.

## Step 0 — Before you build: does it already exist?

This skill wraps existing tools, so the first move is **not** to scaffold — it's to check that you're not
rebuilding something that already ships, and that there isn't a lighter path than the one the language
implies. Do a quick web search before writing any code:

- **Look for an existing plugin by name.** At minimum search GitHub for `dprint-plugin-<TOOL>` across all
  owners (not just the user's) — someone may already maintain it. Pay special attention to **dprint's own
  org**, which ships official plugins (`prettier`, `typescript`, `json`, `markdown`, `toml`, `dockerfile`,
  …); wrapping one of those again is wasted work. Also glance at the plugin list on
  [dprint.dev/plugins](https://dprint.dev/plugins/) and search crates.io / npm for an existing plugin
  package.
- **Prefer a Rust-native equivalent over wrapping JS.** If the tool is JavaScript but a Rust or Go
  formatter produces acceptable output for the same language, recommend that instead of the heavy V8
  process-plugin path. E.g. for JS/TS, dprint's native **TypeScript** plugin and **Biome** (both Rust →
  Wasm) already exist — reach for those before wrapping Prettier. This is the same decision rule as Step 1
  ("if a formatter exists in multiple languages, prefer the Rust one"), just applied *before* committing.
- **If it already exists:** say so, link it, and only build a fresh one if theirs is unmaintained,
  insufficient, or the user specifically wants their own. Don't silently scaffold a duplicate.

If nothing suitable exists (or the user knows and wants their own anyway), continue to Step 1.

## Step 1 — Pick the architecture

Ask (or infer) **what language the formatter library is written in**, then route:

| Wrapped formatter is… | Architecture                       | Reference                  | When                                                                                                                                                          |
| --------------------- | ---------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A **Rust crate**      | Rust → Wasm (`SyncPluginHandler`)  | `references/rust-wasm.md`  | **Default. Prefer this whenever possible.** Smallest artifact, simplest release, runs sandboxed in dprint's Wasm host.                                        |
| A **Go package**      | Go → TinyGo → Wasm                 | `references/go-wasm.md`    | The formatter is Go (e.g. `mvdan/sh`). Needs a runtime bridge + codegen layer; heavier than Rust but still a single `.wasm`.                                  |
| **JS/Node only**      | Process plugin over V8 (deno_core) | `references/process-v8.md` | Last resort. The formatter is JS and can't be compiled to Wasm (e.g. SVGO). Ships native per-platform binaries, not Wasm — much heavier to build and release. |

Decision rule: **Wasm if you possibly can.** Only reach for the V8 process plugin when the formatter is
JavaScript with no Rust/Go equivalent and can't reasonably be ported. If a formatter exists in multiple
languages, prefer the Rust one.

Process plugins also carry two **distribution** limitations Wasm doesn't, worth raising with the user
before committing: they **can't be loaded from a remote `extends` config** (running a native binary off a
remote URL is blocked as a security risk — Wasm is sandboxed, so it's fine), and they **can't be consumed
via `@dprint/formatter` on npm** (that ecosystem is Wasm-only). If the plugin needs to be shareable
through a hosted config or usable from JS tooling, a process plugin can't do it.

State the choice and why in one line, then open the matching reference file and follow it — the reference
has the full file-by-file template for that architecture. Everything below applies to **all three**.

## Step 2 — Shared conventions (bake these in by default)

These are house defaults. Apply them unless the user says otherwise.

### Naming & the proxy

- Repo: `github.com/<USER>/dprint-plugin-<NAME>`.
- dprint's registry proxies that exact repo shape, so users install with **`dprint add <USER>/<NAME>`**
  (note: `dprint-plugin-` is stripped). e.g. repo `kjanat/dprint-plugin-svg` → `dprint add kjanat/svg`.
- The published wasm asset on each release **must** be named `plugin.wasm` — that's the file the proxy
  serves for `dprint add <USER>/<NAME>`.
- Crate/lib name: `dprint-plugin-<NAME>` / `dprint_plugin_<NAME>`. Config key in `dprint.json`: the short
  camelCase form, e.g. `texFmt`, `svg`, `jsonSchemaSort`.

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

### Schema generation

- Generate `schema.json` from the Rust config type (`schemars`) — never hand-write it. Either inline in
  `build.rs` (simplest, see tex-fmt) or a feature-gated `generate-schema` bin (when you also generate docs,
  see svg). Go uses a `gen-json-schema` codegen tool from struct tags.
- Commit the generated schema and add a CI drift check (`<generate> && git diff --exit-code`). To keep
  that check reliable, sort the schema into a stable, canonical key order before writing it — the
  [`json-schema-sort`](https://crates.io/crates/json-schema-sort) crate does this (and is also available
  as a dprint plugin, `dprint add kjanat/json-schema-sort`). See `references/rust-wasm.md` for wiring.

### Build profile (Wasm paths)

A dprint plugin is dominated by **cold-load cost**, so optimize the artifact for size:

```toml
[profile.wasm-release]
inherits      = "release"
opt-level     = "z"
strip         = true
lto           = "fat"
panic         = "abort"
codegen-units = 1
```

### Release flow

- **Released artifacts are immutable — once published, a version is frozen forever.** `plugins.dprint.dev`
  is a CDN-cached proxy in front of the GitHub release asset. Once a version's `plugin.wasm` (or
  `plugin.json`) has been fetched and cached, **re-uploading a corrected binary to the same release does
  nothing** — users keep getting the cached one, and you can't reliably bust it. **Never replace a binary
  on an existing release.** If something's wrong, **bump the version and cut a new release.** Treat every
  published version as permanent.
- **Tag on bare semver `*.*.*`, not `v*.*.*`.** The house convention is unprefixed tags
  (`tags: ["[0-9]+.[0-9]+.[0-9]+"]`), e.g. `0.1.0`, not `v0.1.0`. Keep tag, `Cargo.toml`/`go.mod` version,
  and schema `$id` in lockstep.
- **(Optional, if the user wants belt-and-suspenders)** Because artifacts are immutable anyway, harden it:
  enable **immutable releases** on the repo, and add a tag protection / ruleset that **blocks pushing `v*`
  tags** so nobody accidentally creates a `v`-prefixed release that breaks the convention. Offer this; don't
  force it.
- Tag-triggered workflow builds the artifact, runs tests, regenerates the schema, and publishes a GitHub
  release containing `plugin.wasm` + `schema.json`.
- **Release notes**: two easy approaches, see `references/release-notes.md` for copy-paste templates —
  (a) generate a `release-fragment.md` from schema defaults and pass it via `body_path` +
  `generate_release_notes: true` (the Rust/tex-fmt way), or (b) hand-build a body string with install
  snippet + checksum + config example (the svgo way).
- License: default to **MIT** — it's the house default. `Apache-2.0` or dual `Apache-2.0 OR MIT` are
  equally fine if the user prefers; it doesn't much matter as long as it's permissive. When the plugin
  **wraps or forks** someone else's formatter, preserve/inherit that project's license and copyright
  (e.g. the shfmt fork keeps upstream BSD-3-Clause). Don't overthink it.
- **(Optional) Also publish to npm.** Its main purpose is **programmatic JS use**: ship the `plugin.wasm`
  as an npm package so JS/Deno/Node tooling can run it through
  [`@dprint/formatter`](https://www.npmjs.com/package/@dprint/formatter), the official Wasm-plugin host.
  Follow dprint's own package convention (`@dprint/json`, `@dprint/typescript`, `@dprint/biome`,
  `@dprint/oxc`, `@dprint/ruff`, …): the package bundles the `.wasm` and exports a **`getPath()`** that
  returns the on-disk path to it (some export **`getBuffer()`** instead). Consumers then do
  `createContext()` → `addPlugin(fs.readFileSync(pkg.getPath()), config)` → `formatText({ filePath,
  fileText })`. Publish to JSR too for Deno-native consumption.
  - **Bonus: that same npm publish doubles as a CLI install source.** Because npm packages are mirrored on
    jsdelivr/unpkg, the published wasm is reachable at a stable CDN URL
    (`https://cdn.jsdelivr.net/npm/<pkg>@<version>/<path-to>.wasm`), and the dprint CLI accepts arbitrary
    `.wasm` URLs in the `plugins` array — so that URL works as an install source alongside the
    `plugins.dprint.dev` proxy. The CLI also accepts **local file paths**, so in a project that's already
    `npm install`ed the package you can point straight at `./node_modules/<pkg>/<path-to>.wasm` instead.
    Both are valid; trade-off is you need the wasm's real in-package path, you lose the proxy's
    `latest.json` / `dprint add <USER>/<NAME>` ergonomics, and the local-path form only works where the
    node_modules tree exists — so the proxy + GitHub release stays the *primary* CLI path while these are
    fully legal alternatives, not hacks.
  - Keep the npm `version` in lockstep with the git tag / `Cargo.toml` / schema `$id`; npm publishes are
    **immutable**, so a bad one means a version bump, same rule as everything else.
  - **Wasm-only** either way — `@dprint/formatter` hosts *Wasm* plugins and the CDN trick needs a single
    `.wasm`, so a V8 process plugin can't be distributed through npm at all. Offer it; don't force it.

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
- [ ] `schema.json` is generated, committed, and CI checks it isn't stale.
- [ ] The release artifact is named `plugin.wasm` (Wasm paths) and the README documents
      `dprint add <USER>/<NAME>`.
- [ ] Release workflow triggers on a **bare semver tag** (`*.*.*`, not `v*.*.*`).
- [ ] Never plan to re-upload a binary to an existing release — a mistake means **bump + re-release**.
- [ ] At least one fixture pair (input → expected output) plus a real `dprint fmt` end-to-end check.

## Reference files

- `references/rust-wasm.md` — **default path.** Full Rust `SyncPluginHandler` template: Cargo.toml,
  lib.rs, config resolution, the `unmap_*` defaults pattern, schema gen, wasm-dependency stubbing,
  `.cargo/config.toml`, CI + release.
- `references/go-wasm.md` — TinyGo Wasm path: the `dprint/` runtime bridge, host imports, `go generate`
  codegen for boilerplate/config/schema, ldflag metadata injection, goreleaser/mise.
- `references/process-v8.md` — V8 process-plugin path: deno_core base crate, V8 snapshot of bundled JS,
  the stdio message loop, multi-platform binary release with `plugin.json` + checksums.
- `references/release-notes.md` — release hygiene (immutable artifacts, bare-semver tags, optional GitHub
  hardening) + copy-paste release-note templates for each path.

For any path, the user's own repos are the canonical templates to copy from rather than reproduce from
memory:

- Rust/Wasm: [`dprint-plugin-tex-fmt`](https://github.com/kjanat/dprint-plugin-tex-fmt) ·
  [`dprint-plugin-svg`](https://github.com/kjanat/dprint-plugin-svg) ·
  [`dprint-plugin-json-schema-sort`](https://github.com/kjanat/dprint-plugin-json-schema-sort)
- Go/TinyGo: [`dprint-plugin-shfmt`](https://github.com/kjanat/dprint-plugin-shfmt)
- V8 process plugin: [`dprint-plugin-svgo`](https://github.com/kjanat/dprint-plugin-svgo)

When in doubt, open the real source — it's authoritative over anything reconstructed here.
