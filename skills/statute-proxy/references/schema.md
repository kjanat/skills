# Resolved Schema

Statute has two layers: the surface API the user writes against, and the resolved schema the runtime operates on. This document describes the resolved layer in full.

## Why a resolved schema exists

The surface API trades unambiguity for ergonomics. Durations are strings, upstream references are names, defaults are implicit, and middleware is expressed as constructor calls. This makes configurations readable but means the surface representation cannot be the authoritative source for runtime behaviour. There would be too many places to interpret a value, too many implicit defaults to track, and too many ways for tooling to disagree about what a configuration "means."

The resolved schema solves this by being the single canonical form. Every duration is a `time.Duration`. Every upstream reference is a pointer to a resolved pool. Every default is filled in. Every middleware stack is a flat ordered list. There are no optional fields and no string-encoded values. If two surface configurations resolve to the same `ResolvedConfig`, they are behaviourally identical. If they resolve to different `ResolvedConfig` values, they will behave differently. There is no third option.

## The resolution pipeline

When `statute.Run` is called, the surface configuration passes through three stages.

The validate stage performs structural and semantic checks on the surface form. Unknown upstream references, malformed durations, conflicting routes, missing TLS material, and impossible matcher combinations are caught here. Validation errors are reported with source locations that point back to the user's Go file via `runtime.Caller` introspection captured by the helper constructors at construction time.

The resolve stage transforms the surface form into the canonical form. Defaults are filled in from the `Defaults` block, then from the framework's hard-coded baseline if the user did not specify defaults. String durations are parsed into `time.Duration`. Rate limit expressions are parsed into structured `RateLimitSpec` values. Upstream name references in routes become pointers to resolved pool structs. Middleware constructors are called in declaration order and their outputs are flattened into a single ordered slice per route. Host and path matchers are compiled into matcher trees suitable for runtime dispatch.

The run stage hands the `ResolvedConfig` to the server. From this point onward, the surface form is no longer consulted; the resolved form is the only input to runtime decisions.

## Type definitions

The resolved types live in `github.com/kjanat/statute/resolved`. They are public so that external tooling can consume them, but users authoring configurations should never import this package directly.

```go
package resolved

import "time"

type Config struct {
    Listeners     []Listener
    Upstreams     map[string]*Pool
    Routes        []Route
    Defaults      Defaults
    Observability Observability
    Shutdown      Shutdown
}

type Listener struct {
    Network  string // "tcp" or "udp"
    Address  string
    TLS      *TLSConfig    // nil for plain HTTP
    Protocols ProtocolSet  // bitfield: HTTP/1.1, HTTP/2, HTTP/3
    Redirect *RedirectRule // nil unless this listener is a pure redirector
}

type TLSConfig struct {
    Certificates []Certificate
    ACME         *ACMEConfig
    MinVersion   uint16
    CipherSuites []uint16
    ALPN         []string
    OCSPStapling bool
}

type Pool struct {
    Name        string
    Backends    []Backend
    Strategy    LBStrategy
    HealthCheck HealthCheck
    Transport   Transport
}

type Backend struct {
    Address string
    Weight  int
    Backup  bool
}

type Route struct {
    Matcher    Matcher          // compiled matcher tree
    Action     Action           // ProxyAction, ServeAction, RedirectAction
    Middleware []MiddlewareSpec // flattened, ordered
}

type MiddlewareSpec struct {
    Kind   string         // "rate_limit", "retry", "timeout", "header", ...
    Params map[string]any // kind-specific, JSON-serialisable
}

type Defaults struct {
    ReadTimeout       time.Duration
    WriteTimeout      time.Duration
    IdleTimeout       time.Duration
    ReadHeaderTimeout time.Duration
    MaxHeaderBytes    int
    TrustedProxies    []CIDR
}
```

The full type set is larger but follows the same pattern: every field that the surface API expressed as a string, an optional, or a reference is a concrete typed value at the resolved layer.

## Validation guarantees

A successfully resolved configuration carries the following guarantees, which the runtime relies on without further checking.

Every route's `Action` has a non-nil target. For `ProxyAction`, the target pointer is non-nil and the pool exists in the `Upstreams` map. For `ServeAction`, the source path has been validated as a readable directory. For `RedirectAction`, the target template has been parsed and any variable references resolved.

Every pool has at least one backend. Empty pools are rejected at validation time, never silently accepted.

Every TLS-enabled listener has either a non-empty `Certificates` slice or a non-nil `ACME` configuration. A listener that requested TLS without a way to obtain a certificate fails validation.

Every duration is non-negative. Zero is permitted only for fields where zero is documented to mean "no limit" (`IdleTimeout`, for instance, where zero disables the idle timeout). Fields where zero would be unsafe (`ReadHeaderTimeout`) reject zero at validation time and require the user to set a value or fall back to the intended framework default.

Every middleware spec has a `Kind` recognised by the runtime and `Params` that match the schema for that kind. Unknown kinds and malformed params fail validation.

Routes do not conflict. Two routes with overlapping matchers and different actions are permitted (the first wins by declaration order), but two routes with literally identical matchers fail validation as a likely user error.

## JSON export

The `statute export` subcommand walks a resolved configuration and emits a JSON document that round-trips through `encoding/json`. Pointer references are flattened into named lookups; the resolved schema's pointer-based form is for runtime efficiency, while the JSON form is for inspection and diffing.

The JSON shape mirrors the Go types but uses `snake_case` field names and string representations for durations (back to `"30s"` form) so that the output is readable in `jq`, diff tools, and dashboards. The export is deterministic: maps are emitted in sorted key order, slices preserve declaration order, and floating point values are not used. Two binaries built from the same source produce byte-identical export output.

This determinism is the point. A deployment pipeline can build the binary in CI, run `statute export > config.json`, commit that file, and on the next deployment diff the new export against the previous one to see exactly what changed in the resolved topology. Surface-level diffs in Go source are noisier and harder to review; the resolved JSON is the canonical artefact for change review.

## Using the resolved schema for testing

Tests that assert against the surface API are testing the DSL: that `statute.Match("/api/*")` produces a route with the matcher you expect. Tests that assert against the resolved schema are testing the actual configured behaviour: that a particular surface configuration resolves to a `ResolvedConfig` with the routes, middleware, and timeouts you expect.

The skill should encourage the second style for any configuration test that matters operationally. The pattern is to construct the surface `Config`, call `statute.Resolve(cfg)` to get a `ResolvedConfig`, and assert against the resolved form using normal Go test assertions or a deep-equal helper. Tests written this way survive surface API refactors as long as the resolved schema is stable, which means they test what the user actually cares about (behaviour) rather than what they happen to have typed (syntax).

## When to reach for the resolved schema in conversation

Use the surface API when teaching, scaffolding, or reviewing user-authored configurations. The resolved schema is rarely the right thing to show a user who is writing a config; it is verbose, low-level, and not what they will type.

Reach for the resolved schema when the user is debugging unexpected behaviour ("why is my middleware running in this order?"), generating tooling around statute (validators, dashboards, schema-driven documentation), comparing two deployments, or asking specifically how a surface declaration normalises. In each of these cases the resolved form is what they actually need to see, and showing the surface form would obscure the answer.
