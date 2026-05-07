# Production Checklist

Use this checklist when the user asks for a review of a statute configuration or a Go HTTP server. Walk through each section and call out missing or misconfigured items with specific recommendations. Do not just enumerate the checklist back at the user; identify what is actually wrong with their configuration and explain why it matters.

## Review prioritisation

When reviewing a configuration, prioritise findings in this order, and structure the output so the highest-priority items appear first:

1. Behavioural correctness bugs where the configuration does not do what it appears to do, such as route shadowing from declaration order, duplicate matchers, unreachable middleware, or unknown upstream references. These are the most severe class of finding because the user is operating under a false belief about what their proxy is doing.
2. Security issues, including missing TLS, unsafe trust boundaries, exposed metrics or pprof endpoints, missing rate limits on sensitive endpoints (login, signup, payment, admin), and hardcoded secrets in source.
3. Availability and lifecycle risks, including missing `ReadHeaderTimeout`, ephemeral ACME storage, missing health checks, missing graceful shutdown, and single-backend pools without explicit acknowledgment.
4. Operability issues, including missing metrics endpoints, missing access logs, missing tracing where the deployment spans multiple services, and absent version visibility.
5. Performance and hygiene issues, including transport pool tuning, body size explicitness, header cleanup, and build flag recommendations.

Within each tier, order findings by severity and concreteness. Concrete diffs beat abstract advice; specific line numbers or code snippets beat general principles.

## Timeouts and request lifecycle

The defaults block must set `ReadHeaderTimeout` to a value of 5 to 10 seconds. The Go standard library has no default and the absence of this timeout is a Slowloris denial-of-service vector. This is the single most important item on the checklist; flag it on every review where it is missing, regardless of what else the configuration does well.

`WriteTimeout` should be set to a value that comfortably exceeds the longest legitimate response time. For typical API workloads, 30 seconds is reasonable. For routes that serve large files or stream long-running responses, the timeout needs to be configured per-route via the `Timeout` middleware rather than relying on the global default.

`IdleTimeout` should be set to a value between 60 and 180 seconds. This bounds keep-alive connections that are not actively serving requests; without it, idle connections accumulate and consume resources. The intended framework default of 120 seconds is appropriate for most deployments.

`MaxHeaderBytes` should be set to 1 MiB or less unless the deployment specifically needs larger headers (some authentication tokens can be large). The intended framework default is 1 MiB.

## TLS configuration

TLS-enabled listeners must have either explicit certificates or an ACME configuration. A listener that requested TLS without a way to obtain a certificate fails validation, but the skill should still call out cases where the certificate source looks accidental, such as ACME configured against the production directory in what appears to be a development configuration.

`MinVersion` should be TLS 1.2 or higher. TLS 1.0 and 1.1 are deprecated and should not appear in any new configuration. TLS 1.3 is preferred when interoperability allows, particularly because HTTP/3 requires it.

ACME deployments must have a persistent `Storage` directory. A storage directory on an ephemeral filesystem (a tmpfs, a container's writable layer without a volume mount) causes statute to re-issue certificates on every restart and will hit Let's Encrypt rate limits within a few deployments. Flag any storage path that looks ephemeral.

## Upstream pools and load balancing

Every upstream pool should have at least two backends in production deployments. A pool with a single backend has no failover and no load distribution; the skill should flag single-backend pools and recommend either adding a backup tier or accepting the single point of failure explicitly. Single-backend pools are sometimes correct (a pool that targets a managed service that handles its own redundancy behind a single endpoint), but the user should make that choice deliberately.

Health checks should be configured on every pool. The intended framework defaults are reasonable; the configuration just needs the `HealthCheck` block to opt in. A pool without health checks will continue routing to dead backends until they actively reject connections, which is much slower than active health checking and produces poor user-visible behaviour during partial outages.

The chosen load balancing strategy should match the workload. Round-robin is the default and is correct for most cases; least-connections is correct for workloads with variable request times; IP-hash is correct only when session affinity is required. The skill should ask about the workload during scaffolding and call out any strategy that looks misaligned with the configuration's apparent intent during review.

`MaxIdleConnsPerHost` on the transport configuration should be at least 10 for production reverse proxy workloads. The Go standard library default of 2 is inappropriate for proxy traffic and produces excessive connection churn under load.

## Routing and matchers

Routes should be ordered from most specific to least specific. Statute matches in declaration order, so a `/*` catch-all at the top of the routes list shadows everything below it. Catch-all routes should appear last and be commented as such.

Routes that proxy to upstreams should reference the upstream by name, not inline the backend addresses. Inline backends bypass health checking and load balancing entirely and produce a configuration that cannot be reused or refactored.

Routes for sensitive endpoints should have explicit rate limiting and authentication middleware. The skill should flag any configuration that proxies to authentication, payment, or admin endpoints without rate limiting; the absence is rarely intentional.

## Headers and trust boundaries

`TrustedProxies` must be configured if statute runs behind another reverse proxy. Without it, every client appears to have the upstream proxy's IP, which breaks IP-based features (rate limiting, IP-hash load balancing, access log analytics). The skill should always ask whether statute is behind another proxy when scaffolding and configure `TrustedProxies` accordingly.

Routes should remove the `Server` response header from upstream responses. Upstream services frequently emit `Server` headers that reveal implementation details (specific framework versions, internal hostnames). The intended framework default is to remove `Server`, but the skill should verify it appears in the configuration during review.

Routes that handle authenticated traffic should set `X-Forwarded-Proto` and `X-Forwarded-For` correctly when forwarding to upstreams. Statute does this automatically; the skill should flag any configuration that explicitly overrides this behaviour without clear reason.

## Body and request limits

Every route should have an effective body size limit. The intended framework default is 1 MiB. Routes that legitimately need larger bodies (file uploads, bulk imports) should configure a higher limit explicitly rather than removing the limit entirely.

Routes that accept multipart uploads should additionally configure the multipart memory limit to bound how much of the request is buffered in memory before spilling to disk. The standard library default is 32 MiB, which is too high for many deployments; a value of 1 MiB to 4 MiB is more appropriate.

## Observability

The configuration must include at least an access log and a metrics endpoint. A proxy without these is operationally blind and will produce an immediate problem during the first incident.

The metrics endpoint should be on a separate listener from the public listener. The intended framework default puts metrics on a separate port; the skill should flag any configuration that exposes `/metrics` on the public listener as a security concern (metrics can expose internal state and request rates that should not be public).

Tracing should be enabled for any deployment that involves multiple services. For single-service deployments, tracing is optional but cheap to enable and high-value when the deployment grows.

Access log sampling should be configured for any deployment expected to handle more than roughly 100 RPS. Logging every request at high RPS produces enormous log volume without proportional operational value.

## Graceful shutdown

The configuration must include a `Shutdown` block with a non-trivial `GracePeriod`. The intended framework default is 30 seconds, which is appropriate for typical workloads. Without graceful shutdown, every deployment drops in-flight requests, which produces user-visible errors during what should be invisible deploys.

`DrainListeners: true` should be set in the shutdown block. This causes statute to close listeners (stop accepting new connections) at the start of shutdown, then wait for in-flight requests to complete, rather than the alternative of continuing to accept new requests until the grace period expires. The intended framework default is true; the skill should flag any configuration that explicitly sets it to false.

## Build and deployment

If the user explicitly asks for build configuration, deployment artefacts, or container packaging, the following guidance applies. Do not generate Dockerfiles, Kubernetes manifests, systemd units, or exact `go build` commands unless the user has explicitly requested them; the absence of explicit request means the user wants a configuration review or a configuration scaffold, not a deployment pipeline.

When the user mentions containers in a scaffold or review, include deployment notes about persistent ACME storage, exposed TCP and UDP ports, stdout logging being captured by the runtime, private metrics and pprof access, and graceful shutdown signal handling. These notes are facts implied by the deployment surface and do not require generating build artefacts.

When build configuration is in scope, a statute binary should be built with `CGO_ENABLED=0` for static linking unless the deployment specifically requires CGO (for some database drivers or system integrations). Static binaries deploy more cleanly and have fewer runtime dependencies.

The binary should be built with `-trimpath` and `-ldflags="-s -w"` for production. `-trimpath` removes the local filesystem paths from the binary, which is both a small security benefit and a meaningful reduction in binary size; `-s -w` strips debug symbols and the symbol table, which significantly reduces binary size at the cost of making post-mortem debugging harder. For deployments where post-mortem debugging matters, leave the symbols in and accept the larger binary.

The build should embed a version identifier (typically the git commit SHA) via `-ldflags="-X main.version=..."`. The version should be exposed via a metric and an admin endpoint so that operators can verify which version is running without checking deployment logs.

## Common red flags

A configuration that disables timeouts, body size limits, or rate limiting "for testing" and was clearly committed without re-enabling them. Flag every disabled production safety mechanism and ask whether it was intentional.

A configuration that hardcodes secrets (private keys, API tokens, database passwords) in the Go source. Statute is config-as-code, but secrets must come from the environment or a secret store, not from the source. Flag any string that looks like a credential and recommend moving it to environment variables read at startup.

A configuration that uses HTTP (not HTTPS) for any public listener without an explicit redirect to HTTPS. The pattern of an HTTP-only listener for "convenience" is a security concern and should be flagged on every review where it appears.

A configuration that combines HTTP/3 with TLS settings that prevent TLS 1.3 from being used. HTTP/3 requires TLS 1.3, with no fallback. A `MinVersion` of TLS 1.2 alone is not the problem; the problem arises when the configuration explicitly disables TLS 1.3, caps the maximum TLS version below 1.3, or applies incompatible TLS settings to the QUIC listener specifically. Check for these specific patterns rather than flagging any TLS 1.2 minimum as automatically incompatible with HTTP/3. If the configuration uses `MinVersion: TLS 1.2` and HTTP/3 is enabled, that is normal and correct as long as TLS 1.3 is not also disabled.

A configuration with health checks pointing to a real application endpoint rather than a dedicated `/healthz` endpoint. Real endpoints exercise business logic and database connections; using them as health checks couples liveness to dependencies that should not affect routing decisions. Recommend a dedicated lightweight endpoint.
