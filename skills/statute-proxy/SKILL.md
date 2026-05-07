---
name: statute-proxy
description: Use this skill whenever the user is designing, building, scaffolding, reviewing, or debugging Go-based reverse proxy or HTTP edge infrastructure, especially when they mention statute, config-as-code proxies, building an nginx replacement in Go, networking topology, TLS termination, load balancing, HTTP/2, HTTP/3, QUIC, ACME, upstream pools, middleware chains, or graceful shutdown. Trigger this skill even when the user does not explicitly name statute but is clearly working on a Go HTTP server, edge proxy, or networking infrastructure problem where the resulting artefact will be a compiled binary rather than a runtime-configured server. Also trigger when the user asks for explanations of networking protocols (HTTP/1.1, HTTP/2, HTTP/3, WebSockets, gRPC, TLS) in the context of building or operating a proxy, or when they ask about Go net/http pitfalls, transport tuning, or production-grade server defaults.
---

# Statute: Config-as-Code Reverse Proxy in Go

Statute is a config-as-code reverse proxy framework where the user's configuration is itself Go code, compiled into a single standalone binary. There is no runtime configuration file, no hot reload, and no module loader. The entire routing topology, TLS setup, upstream pools, and middleware stack are expressed as Go values, validated at startup, resolved into a canonical schema, and then served.

The mental model is "Lua-as-config but in Go": the user-facing API should read like a configuration file even though it is Go, with the full benefits of type checking, IDE completion, and compile-time validation. The skill exists to teach this API consistently, generate well-structured scaffolds, review existing configurations against best practices, and provide the deeper networking knowledge needed to reason about edge infrastructure decisions.

## API implementation status and accuracy guardrail

The statute API described in this skill is currently a design-stage target unless the user explicitly indicates they are working against an implemented version of the library that matches this documentation.

Treat the documented API as authoritative for architectural intent and desired shape, but do not imply generated code is guaranteed to compile while the implementation is incomplete or unverified.

In scaffold mode, label concrete code as "design-stage statute-style pseudocode" unless implementation status is known.

In review mode, review against the statute design rules and production checklist, while distinguishing production concerns from exact API spelling.

Be precise about external protocol facts such as HTTP/2, HTTP/3, QUIC, TLS, ALPN, ACME, and Go `net/http`. Do not soften real protocol facts just because the statute API is design-stage.

Once the library exists and the skill matches the implementation, this section can be removed and references to "intended framework default" throughout the skill can be flipped back to "framework default."

## When this skill applies

Use this skill in three primary modes, and pick the right one based on what the user is asking for.

The first mode is **explain**. The user asks how something works (a protocol, a feature, a Go networking primitive, a pitfall) and wants an answer that connects the underlying concept to how statute exposes it in the DSL. Lean on the reference files under `references/` for the deeper material and bring it back to the API surface so the explanation is actionable. Explain mode should usually be four to seven paragraphs. Start with the direct answer, then explain the operational consequences for statute. Include a small code snippet only when it clarifies a concrete configuration implication. Avoid exhaustive protocol history unless the user asks for depth.

The second mode is **scaffold**. The user describes a deployment scenario and wants a complete configuration showing the intended shape of statute. Produce a design-stage statute-style configuration that uses the canonical struct-literal style described below, and label it as design-stage pseudocode unless the user has confirmed they are working against an implemented version of statute that matches this skill. Do not produce skeletal stubs with `// TODO` comments where real values belong; pick sensible defaults, name them, and explain the choices in prose around the code. Scaffold mode should produce the configuration first, then a short rationale section. Keep deployment notes separate and limited to facts implied by the prompt. For containers, mention persistent ACME storage, stdout logging, public and private ports, and graceful shutdown. Do not include unrelated build artifacts such as Dockerfiles, Kubernetes manifests, systemd units, or exact `go build` commands unless the user explicitly asks for them.

The third mode is **review**. The user shares an existing statute configuration or a Go HTTP server and wants feedback. Audit it against the production checklist in `references/production-checklist.md`, the pitfalls in `references/go-net-http-pitfalls.md`, and the canonical style described below. Review against the statute design rules, distinguishing production concerns from exact API spelling, and follow the priority ordering documented in the production checklist: behavioural correctness bugs first, then security, then availability and lifecycle, then operability, then performance and hygiene. Be specific about what to change and why, and prefer concrete diffs over abstract advice.

If the request is ambiguous, ask one focused question to disambiguate rather than guessing. Do not silently default to scaffold mode when the user might have wanted an explanation.

## The DSL surface

Statute has a two-layer architecture. The user-facing surface API is optimised for readability; the resolved schema is the canonical, fully-validated form the runtime operates on. Always teach and generate against the surface API. Refer to the resolved schema only when the user is debugging behaviour, generating tooling, or asking specifically about the validation pipeline.

The canonical surface form uses Go struct literals with named fields, mixed with small helper functions for the parts that benefit from being concise. The reference shape looks like this. While statute is design-stage, treat this block as the target API shape rather than verified compilable code.

```go
package main

import "github.com/kjanat/statute"

func main() {
    statute.Run(statute.Config{
        Listeners: statute.Listeners{
            statute.HTTP(":80").RedirectTo("https"),
            statute.HTTPS(":443",
                statute.AutoTLS("example.com", "api.example.com").
                    Email("ops@example.com").
                    Storage("/var/lib/statute/certs"),
                statute.HTTP2(),
                statute.HTTP3(":443/udp"),
            ),
        },

        Upstreams: statute.Upstreams{
            "api": statute.Pool{
                Backends: []statute.Backend{
                    {Address: "10.0.0.1:8080", Weight: 2},
                    {Address: "10.0.0.2:8080", Weight: 1},
                    {Address: "10.0.0.3:8080", Backup: true},
                },
                Strategy:    statute.LeastConnections,
                HealthCheck: statute.HealthCheck{Path: "/healthz", Interval: "10s"},
                Transport:   statute.Transport{MaxIdleConnsPerHost: 10, IdleConnTimeout: "90s"},
            },
        },

        Routes: statute.Routes{
            statute.Match("/api/v1/*").Host("api.example.com").ProxyTo("api").
                With(
                    statute.RateLimit("100/min").Per(statute.ClientIP),
                    statute.Retry(3, statute.OnStatus(502, 503, 504)),
                    statute.Timeout("30s"),
                ),
            statute.Match("/static/*").Serve("./public").
                With(statute.Cache("1h"), statute.Compress(statute.Gzip, statute.Brotli), statute.ETag()),
        },

        Defaults:      statute.Defaults{ReadHeaderTimeout: "5s", WriteTimeout: "30s", IdleTimeout: "120s"},
        Observability: statute.Observability{AccessLog: statute.JSONLog(statute.Stdout), Metrics: statute.Prometheus(":9090", "/metrics")},
        Shutdown:      statute.Shutdown{GracePeriod: "30s", DrainListeners: true},
    })
}
```

The style rules behind this shape are deliberate and the skill should enforce them when scaffolding or reviewing.

Durations are always strings like `"10s"`, `"90s"`, `"1h"`. Statute parses them at startup. Do not use `time.Duration` literals in user-facing configs; they force a `time` import and read worse than the string form. The same principle applies to rate limits (`"100/min"`), sizes (`"1MB"`), and percentages (`"5%"`).

Upstreams are a named map. Routes refer to upstreams by string key. This keeps the routes section readable and lets a single pool be reused across many routes. Never inline backends directly into a route.

Middleware is applied via a single variadic `With(...)` on each route. Each middleware helper is its own constructor; they may chain internally to express their parameters (for example `RateLimit("100/min").Per(statute.ClientIP)`) but the route itself stays one or two lines.

Listeners compose. A single `HTTPS` listener can carry TLS, HTTP/2, and HTTP/3 configuration as sibling arguments rather than nested options. Resist the urge to nest configuration into deep trees; flat composition reads better.

Defaults live in their own block at the top level, not scattered across listeners and routes. The defaults block sets the conservative production baseline; routes override individual values via middleware where needed.

## The resolved schema

When statute starts, it walks the surface configuration through a three-stage pipeline: validate, resolve, run. The validate stage checks for structural and semantic errors (unknown upstream references, malformed durations, conflicting routes, missing TLS material). The resolve stage fills in defaults, parses durations into `time.Duration`, dereferences upstream names into pointers to pool structs, flattens middleware stacks into explicit ordered lists, and computes derived values like the cartesian product of host and path matchers. The output of resolve is a `ResolvedConfig` value with no optional fields, no string-encoded values, and no unresolved references. The run stage hands the `ResolvedConfig` to the server and starts listeners.

The resolved schema is the single source of truth for runtime behaviour. It is exportable to JSON via `statute export`, which means deployments can be diffed, snapshotted in CI, and inspected without a running server. Tests should assert against the resolved form rather than the surface API, because the surface tests the DSL while the resolved form tests the actual configured behaviour.

The resolved types are a public package (`statute/resolved`) but clearly marked as the lower-level layer. Users authoring configs should never need to touch them; users building tooling around statute (validators, dashboards, documentation generators) should always use them. The skill should reach for the resolved schema when the user is debugging unexpected runtime behaviour, comparing two deployments, or asking how a specific surface declaration normalises.

For the full schema definition, the resolution rules, and the validation guarantees, see `references/schema.md`.

## Feature surface

The compiled binary supports the following capabilities, all hardcoded into the source. The skill should treat anything outside this list as out of scope and either redirect the user to a different tool or explicitly note that the feature is not part of statute.

Reverse proxying for HTTP/1.1, HTTP/2, and HTTP/3, including WebSocket upgrades and gRPC pass-through. TLS termination with both static certificates and ACME auto-provisioning via Let's Encrypt or any RFC 8555 directory. Load balancing across upstream pools with round-robin, least-connections, IP-hash, and weighted strategies, plus a backup tier for failover. Active health checks with configurable path, interval, timeout, and healthy/unhealthy thresholds. Per-route rate limiting keyed by client IP, header value, or arbitrary expression. Request and response header manipulation. Static file serving with correct cache headers and ETag handling. Gzip and Brotli compression. Structured JSON access logging with sampling. Prometheus metrics, OpenTelemetry tracing, and pprof endpoints. Graceful shutdown with listener draining and configurable grace period.

Out of scope: dynamic configuration reload, plugin loading, scripting languages, runtime config files of any form, certificate management UIs, web admin interfaces, and clustering or distributed coordination. If the user asks for any of these, explain that they conflict with the design philosophy and suggest Caddy or Traefik as alternatives that fit those requirements.

## Reference files

Load reference files only when they are relevant to the request. Each file is self-contained and assumes the reader understands the surface API described above.

`references/schema.md` covers the resolved schema in full: the type definitions, the resolution rules, the validation pipeline, and the JSON export format. Read this for any debugging, tooling, or schema-level question.

`references/tls-and-acme.md` covers TLS termination, certificate management, ACME flows, OCSP stapling, and the trade-offs between static certificates and auto-provisioning. Read this for TLS configuration questions.

`references/http2-and-http3.md` covers the protocol differences, connection coalescing, server push deprecation, HTTP/3 readiness, and the operational implications of running QUIC. Read this for any protocol-level question.

`references/load-balancing.md` covers the strategies, when to use each, the interaction with health checks, and the operational behaviour during partial outages. Read this for upstream configuration questions.

`references/go-net-http-pitfalls.md` covers the well-known traps in the Go standard library: missing default timeouts, transport pool tuning, body close semantics, context propagation, response writer flushing, graceful shutdown ordering, and connection reuse with HTTP/2. Read this for any review or debugging task.

`references/observability.md` covers structured logging, metrics, tracing, and the integration patterns for each. Read this when scaffolding or reviewing observability configuration.

`references/production-checklist.md` is the audit checklist for review-mode requests. Walk through it explicitly when reviewing a configuration the user has shared.

## Style guidance for generated code

When scaffolding a new configuration, follow these rules without being asked.

Always start with the canonical baseline: an HTTP listener that redirects to HTTPS, an HTTPS listener with HTTP/2 enabled, sensible default timeouts, structured access logging, and a metrics endpoint. The user can remove what they do not need; it is faster to delete than to add the obvious things.

Always set `ReadHeaderTimeout` in the defaults block. The Go standard library has no default, and omitting it is a documented denial-of-service vector (Slowloris). This is the single most common pitfall in production Go HTTP servers and the skill should never produce a configuration without it.

Always include a graceful shutdown block. A reverse proxy without graceful shutdown will drop in-flight requests on every deployment. Thirty seconds is a reasonable default grace period for most workloads.

Always include at least an access log and a metrics endpoint in the observability block. A proxy with no observability is operationally blind and any production user will need to add these immediately.

Prefer named upstream pools over inline backends even when there is only one pool. The named form is the canonical shape and configurations grow; starting with the named form means no restructuring later.

Group related routes together and order them from most specific to least specific. Statute matches routes in declaration order, so a `/*` catch-all at the top will shadow everything below it. Comment the catch-all explicitly.

When the user asks for something that requires explanation of trade-offs (for example, "should I use round-robin or least-connections?"), give the recommendation with the reasoning, not just the recommendation. The user is building infrastructure they will operate, and understanding why matters more than knowing what.
