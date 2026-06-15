# Go → TinyGo → Wasm plugin

Use when the wrapped formatter is a **Go package** (e.g. `mvdan/sh` for shfmt). Compiles with TinyGo to
`wasm-unknown` and runs in dprint's Wasm host — same single-`.wasm` deployment as the Rust path, but Go
has no first-party dprint SDK, so the plugin carries a small **runtime bridge** package and leans on
`go generate` for boilerplate. Canonical template:
[`dprint-plugin-shfmt`](https://github.com/kjanat/dprint-plugin-shfmt). **Copy that repo and swap the
formatter** rather than reconstructing the bridge from scratch — it's ~10 files of protocol glue.

## What's actually yours to write

Most of the repo is reusable infrastructure. The plugin-specific surface is small:

| You write                  | File(s)                                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| The config struct (tagged) | `handler_config.go` — struct with `json:`, `description:`, `dprint:"default=…,global"` tags |
| The format logic           | `handler_format.go` — parse with the Go lib, print, return change/no-change                 |
| Identity                   | `handler_metadata.go` — `PluginInfo`, license embedding                                     |
| Any input detection        | e.g. `handler_variant.go` (shfmt detects sh/bash/zsh via shebang+extension)                 |
| `main.go`                  | wires `dprint.NewRuntime(&handler{})`                                                       |

| Copy unchanged from shfmt                                              | Dir                                                                           |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Runtime, host imports, config resolver, message protocol, shared bytes | `dprint/`                                                                     |
| Codegen tools                                                          | `dprint/cmd/{gen-main-boilerplate,gen-config-resolver,gen-json-schema,build}` |

## The tag-driven config + schema

The config struct is the single source of truth; codegen derives the resolver spec and the JSON schema
from its struct tags. Example (from shfmt's `handler_config.go`):

```go
//go:generate go run .../gen-config-resolver -type configuration -out handler_config_generated.go -extra-known-keys locked
//go:generate go run .../gen-json-schema -type configuration -out schema.json -schema-id https://plugins.dprint.dev/<USER>/<short>/latest/schema.json -include-locked -locked-description "..."

type configuration struct {
    IndentWidth uint32 `description:"Spaces per indent level." dprint:"default=2,global"  json:"indentWidth"`
    UseTabs     bool   `description:"Use tabs to indent."       dprint:"default=false,global" json:"useTabs"`
    // ...plugin-specific bools...
}
```

- `dprint:"…,global"` marks a key as inheritable from dprint's global config.
- `gen-config-resolver` emits the typed resolver (`generatedConfigurationResolverSpec`) consumed by
  `dprint.ResolveConfigWithSpec`.
- `gen-json-schema` emits `schema.json` from the same tags. Only `bool` and `uint32` fields are supported
  by the codegen — extend the generators if you need string enums.
- Run `go generate ./...` after editing the struct; **never hand-edit** `*_generated.go` or `schema.json`.

## The format method

`handler_format.go` parses with the Go formatter and returns `dprint.Change`/`NoChange`/`FormatError`:

```go
func (h *handler) Format(req dprint.SyncFormatRequest[configuration], _ dprint.HostFormatFunc) dprint.FormatResult {
    prog, err := parser.Parse(bytes.NewReader(req.FileBytes), req.FilePath)
    if err != nil { return dprint.FormatError(err) }

    var buf bytes.Buffer
    if err := printer.Print(&buf, prog); err != nil { return dprint.FormatError(err) }

    out := buf.Bytes()
    if bytes.Equal(req.FileBytes, out) { return dprint.NoChange() } // idempotence-friendly
    return dprint.Change(append([]byte(nil), out...))
}
```

## Identity & metadata injection

TinyGo's `-X` ldflag injection only works on package-level string vars with no constant initializer.
Keep `Version`, `ReleaseTag`, `RepoSlug`, `GitHubRepo` zero-valued in `main.go`; apply fallbacks in
`handler_metadata.go`. The build tool (`dprint/cmd/build`) derives them from `go.mod` + `git describe`
and passes them via ldflags. `PluginInfo` then composes:

- `config_schema_url`: `https://plugins.dprint.dev/<slug>/<version>/schema.json`
- `update_url`: `https://plugins.dprint.dev/<slug>/latest.json`
- `help_url`: `https://github.com/<gh-repo>`

## Build

TinyGo with a conservative GC and trapping panics (smaller, no JS host):

```bash
tinygo build -o plugin.wasm \
  -target=wasm-unknown -gc=conservative -scheduler=none -panic=trap -no-debug \
  -ldflags="-extldflags '-z stack-size=1048576' -X main.Version=… -X main.RepoSlug=…" \
  .
```

shfmt drives this through `mise` tasks (`build-wasm`, `release`) with pinned tool versions in
`.config/mise.toml`, and a PowerShell `rebuild.ps1` for local fork builds. goreleaser handles the GitHub
release (`.config/goreleaser.yaml`), attaching `plugin.wasm` + `.build/schema.json`. Release is
tag-triggered (`tags: ["[0-9]+.[0-9]+.[0-9]+*"]`).

## Tests

- Unit tests for variant detection / config resolution live next to the code (`*_test.go`), table-driven.
- Integration tests under `integration/` (build tag `integration`) build the wasm with TinyGo and run the
  real `dprint fmt --stdin` over fixture cases in `integration/testdata/cases/<case>/{config.json,input.sh,expected.stdout}`.
  This is the real end-to-end gate; keep the idempotence/diagnostic cases here.

## Gotchas

- The wasm artifact must still end up named **`plugin.wasm`** for the proxy.
- High-risk dependency bumps (the core formatter, TinyGo itself) deserve manual review — TinyGo's wasm
  codegen and the formatter's behavior are the two things most likely to regress. shfmt notes this in its
  `AGENTS.md`.
- Codegen supports only `bool`/`uint32` config fields out of the box.
