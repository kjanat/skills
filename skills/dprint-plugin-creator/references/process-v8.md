# Process plugin over V8 (deno_core)

**Last resort.** Use only when the wrapped formatter is **JavaScript/Node with no Rust or Go equivalent**
that can reasonably be ported (e.g. SVGO). Unlike the Wasm paths, this ships **native per-platform
binaries** that embed a V8 runtime and run the JS formatter — much heavier to build, release, and
maintain. Prefer Wasm if there's any way to avoid this. Canonical template:
[`dprint-plugin-svgo`](https://github.com/kjanat/dprint-plugin-svgo).

## Why it's different

dprint supports two plugin kinds: **Wasm plugins** (sandboxed, single file, what the other two references
produce) and **process plugins** (a native executable dprint launches and talks to over stdio). JS can't
run in the Wasm host, so a JS formatter must be embedded in a process plugin via an embedded V8
(`deno_core`). Consequences:

- You implement `AsyncPluginHandler`, not `SyncPluginHandler`, and run a stdio message loop.
- Release ships a zipped binary **per platform** (darwin x86_64/aarch64, linux x86_64/aarch64, windows
  x86_64) plus a `plugin.json` manifest with download URLs + checksums — not a single `plugin.wasm`.
- Install is `dprint add <USER>/<NAME>` resolving to that `plugin.json` (the proxy still works), but the
  artifact and CI are far larger.
- **Process plugins are blocked from remote configs.** If a user pulls in a remote config via `extends`
  (e.g. `"extends": "https://github.com/<REPO>/raw/main/dprint.jsonc"`), dprint will **refuse to load any
  process plugin** that config references — running an arbitrary native binary off a remote URL is a
  security risk, so it's disallowed. Wasm plugins load fine from remote configs (they're sandboxed). This
  is a real, user-facing limitation: anyone who wants to share your plugin through a shared/remote config
  simply can't if it's a process plugin. Yet another reason to take a Wasm path if there's any way to.
- **No `@dprint/formatter` / npm consumption.** The JS programmatic ecosystem (see the npm note in
  SKILL.md) is Wasm-only, so a process plugin can't be consumed that way either.

## Workspace layout (two crates)

```
dprint-plugin-<NAME>/
├── Cargo.toml                # workspace: members = ["base", "plugin"]
├── base/                     # reusable deno_core glue (copy from svgo)
│   └── src/{build.rs,channel.rs,runtime.rs,snapshot.rs,util.rs,lib.rs}
├── plugin/                   # the formatter-specific plugin
│   ├── build.rs              # bundles JS + creates a V8 snapshot + extracts extensions
│   └── src/{handler.rs,formatter.rs,config.rs,process_loop.rs,process_messages.rs,...}
├── js/                       # the JS bridge (formatText/getExtensions) + console shim
├── vendor/<formatter>/       # the JS formatter as a submodule
└── scripts/, deno.jsonc, justfile, .github/workflows/
```

**`base/` is generic** — copy it from svgo unchanged. It provides:

- `runtime.rs` — a `JsRuntime` wrapper over `deno_core` (execute scripts, call async fns, deserialize).
- `channel.rs` — a memory-aware thread pool that scales V8 isolates (2.2× safety margin, 30s idle
  shutdown) so concurrent formatting doesn't OOM.
- `snapshot.rs` / `build.rs` — V8 heap snapshot create/deserialize (zstd-compressed in release).

## The JS bridge

`js/svgo.ts` exposes the formatter to Rust on `globalThis.dprint`:

```ts
globalThis.dprint = { getExtensions, formatText };
function getExtensions() {
  return ['svg', 'svgz'];
}
function formatText({ filePath, fileText, config }) {
  const result = optimize(fileText, { path: filePath, ...config, multipass: false });
  return result.data === fileText ? undefined : result.data; // undefined = no change
}
```

`js/console.js` shims `console.*` to **stderr** (stdout is reserved for dprint's IPC). `plugin/build.rs`
bundles this against the vendored formatter, snapshots it, and extracts the supported extensions by
calling `getExtensions()` at build time.

## The Rust plugin

- `handler.rs` — `AsyncPluginHandler`: `plugin_info` (still set `update_url` — point it at the
  `latest.json` proxy URL; don't leave it `None`. The svgo template historically left it unset, but the
  convention is to set it on every plugin), `resolve_config`, and `format` which dispatches to the
  channel/thread pool. Range formatting returns `Ok(None)` (SVGO formats whole documents only).
- `config.rs` — maps dprint config to the formatter's option shape; here SVGO's `js2svg` (indent, eol,
  pretty), `indentWidth`→indent, `newLineKind`→eol, plus `svg.*` legacy aliases. Still diagnostic-first.
- `formatter.rs` — decodes bytes (handles `.svgz` gzip round-trip), validates structure (depth/element
  caps to prevent stack/memory exhaustion), builds the JS call, executes with a timeout, encodes back.
- `process_loop.rs` + `process_messages.rs` — the stdio protocol: schema-version handshake, then a
  message loop handling RegisterConfig/Format/etc. Copy from svgo; it's protocol plumbing, not plugin
  logic.

## Build & release

- `just build` bundles the JS for V8; `cargo build --release` snapshots + compiles. Aggressive release
  profile (opt-level z, lto, panic abort) with per-package opt-level 3 overrides for `deno_core`/`v8`/
  `serde`/`tokio` so the hot paths stay fast.
- CI is a **multi-platform matrix** (macOS x2, Windows, Linux x2, the aarch64-linux via `cross`). It's
  generated from a TypeScript definition (`.github/workflows/ci.generate.ts`) — edit the generator, not
  the YAML. Each platform zips its binary + checksum.
- The release job downloads all platform artifacts, generates `schema.json`, builds `plugin.json` (with
  per-platform zip URLs under the GitHub release), and publishes. Install URL embeds the `plugin.json`
  checksum: `…/releases/download/<tag>/plugin.json@<checksum>`.

### The `plugin.json` manifest (required deliverable)

A process plugin is **not** installed by pointing at a binary — it's installed by pointing at a
`plugin.json` manifest that tells dprint which zipped binary to download per platform and how to verify
each one. This file is the process-plugin analogue of `plugin.wasm`; without it there is nothing to
`dprint add`. It is generated by the release job (never hand-written) and uploaded as a release asset.

Shape (dprint's process-plugin manifest format — see the real one at
[svgo 0.4.1 `plugin.json`](https://github.com/kjanat/dprint-plugin-svgo/releases/download/0.4.1/plugin.json)):

```jsonc
{
  "schemaVersion": 2,
  "kind": "process",
  "name": "dprint-plugin-<NAME>",
  "version": "<VERSION>",
  "windows-x86_64": {
    "reference": "https://github.com/<USER>/dprint-plugin-<NAME>/releases/download/<TAG>/dprint-plugin-<NAME>-x86_64-pc-windows-msvc.zip",
    "checksum": "<sha256 of that zip>",
  },
  "linux-x86_64": { "reference": "…-x86_64-unknown-linux-gnu.zip", "checksum": "<sha256>" },
  "linux-aarch64": { "reference": "…-aarch64-unknown-linux-gnu.zip", "checksum": "<sha256>" },
  "darwin-x86_64": { "reference": "…-x86_64-apple-darwin.zip", "checksum": "<sha256>" },
  "darwin-aarch64": { "reference": "…-aarch64-apple-darwin.zip", "checksum": "<sha256>" },
}
```

Key points:

- `schemaVersion` + `kind` are the discriminators that tell dprint this is a process plugin (vs. a
  Wasm one). The exact top-level fields (`schemaVersion` value, whether `kind: "process"` is present)
  should be **copied verbatim from your real `plugin.json`** — the linked svgo 0.4.1 file is the
  authoritative shape; the block above is reconstructed from dprint's process-plugin manifest format,
  so confirm the top-level keys against the real one rather than trusting them blind.
- One entry per target platform; the key is dprint's platform id (`<os>-<arch>`), the `reference` is the
  public download URL of that platform's zip, and `checksum` is its **sha256** (the same one CI computed
  when it zipped the binary). dprint verifies the zip against this before running it.
- The manifest itself is then checksummed (`shasum -a 256 plugin.json`), and *that* hash is what users
  pin in the install URL (`…/plugin.json@<checksum>`) — so the manifest is immutable end-to-end:
  manifest hash pins the file, and each entry's hash pins its binary.
- Because everything is checksum-pinned and CDN-cached, the immutability rule bites doubly here: a wrong
  checksum or URL can't be patched in place — bump the version and re-release.

Generate it from the per-platform CI outputs (svgo does this in its `scripts/` + generated release
workflow); copy that generator and swap the binary name.

## When NOT to use this

If the formatter exists (or is portable) as a Rust crate or Go package, take that path instead — you
avoid the V8 embedding, the multi-platform build matrix, the snapshot machinery, and the heavier release.
This path exists because some mature JS formatters (SVGO) have no equivalent worth reimplementing.

Also weigh the **distribution** cost, not just the build cost: a process plugin can't be loaded from a
remote `extends` config and can't be consumed via `@dprint/formatter` on npm. If the plugin needs to be
shareable through a hosted config or usable from JS tooling, a process plugin is a dead end — only Wasm
works for those. If you can get acceptable output from a Rust/Go formatter, you keep both doors open.
