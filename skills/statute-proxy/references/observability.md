# Observability

This reference covers structured logging, metrics, and tracing in statute. The surface API exposes all three through the `Observability` block in the top-level `Config`. This document explains what each provides, the integration patterns for each, and how they compose into a coherent operational picture.

## Access logging

Statute emits one access log entry per completed request. The intended framework default format is structured JSON written to standard output, which is the right default for any deployment running under a process supervisor or container runtime that captures stdout. Other formats and destinations are available but should be chosen for specific reasons rather than aesthetic preference.

The default fields in each log entry are the timestamp, the client IP after `TrustedProxies` resolution, the request method and full URL, the matched route identifier, the upstream that handled the request (or the static path or redirect target), the response status code, the response size in bytes, the total request duration in milliseconds, and the trace ID if tracing is enabled. Additional fields can be added per-route via the `AccessLog` middleware, which accepts a list of header names to include in the log entry. Sensitive headers should never be included; the framework filters `Authorization`, `Cookie`, and `Set-Cookie` from access logs even if they are explicitly added, and the skill should call out any attempt to log them.

Sampling matters for high-traffic deployments. Logging every request at high RPS produces enormous log volume, most of which is uninteresting (successful requests with normal latency). Statute supports three sampling modes via `SampleErrors`, `SampleSlow`, and a generic `Sample` with a configurable rate. `SampleErrors` logs every non-2xx response and one in N successful responses; `SampleSlow` logs every request slower than a threshold and one in N fast responses; `Sample` applies a uniform sampling rate. The intended framework default is to log everything, which is correct for low-traffic deployments and wrong for high-traffic ones. The skill should infer expected request volume from the prompt when possible (phrases like "moderate traffic," "high traffic," "internal service," or stated RPS figures are all sufficient signal) and recommend sampling for anything above roughly 100 RPS. If traffic volume is unclear and the logging choice materially depends on it, state the assumption inline rather than blocking on a clarifying question.

## Metrics

Statute exposes Prometheus-compatible metrics on a separate listener configured via the `Metrics` block. The separate listener is deliberate: the metrics endpoint should not be reachable from the public internet, and putting it on a different port lets the deployment expose only that port to the metrics scraper without firewalling logic on the main listener.

The metrics statute emits cover the request lifecycle (requests received, requests in flight, requests completed by status class, request duration histogram), the upstream lifecycle (connections active, connection errors, upstream response time histogram, retries attempted, retry exhaustions), the TLS lifecycle (handshakes completed, handshake duration, certificate expiry timestamp per loaded certificate, ACME renewal attempts and failures), and the runtime lifecycle (Go runtime metrics including goroutines, memory, and GC behaviour).

Histogram buckets matter for latency metrics. The intended framework defaults are tuned for typical web workloads (buckets at 1ms, 5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s, 10s); deployments with consistently sub-millisecond latency or consistently multi-second latency benefit from custom buckets. The buckets are configurable on the `Metrics` block but rarely need adjustment.

The metrics endpoint should be scraped at 15-second intervals for typical Prometheus deployments. Shorter intervals produce higher cardinality in the time series store without proportional benefit; longer intervals lose resolution on rapid changes during incidents.

## Tracing

Statute supports OpenTelemetry tracing via OTLP export. The `Tracing` block configures the exporter endpoint and the sampling rate. Each incoming request becomes a root span (or a child span if the upstream propagated a trace context); each upstream call becomes a child span; each middleware that opts in becomes a child span around the wrapped handler.

Sampling is the operational lever that matters most. Tracing every request produces large data volumes and high CPU overhead in the proxy. The intended framework default is 10 percent sampling, which catches enough traces to be representative without exploding storage. For production debugging of specific issues, the operator deploys a new binary built with a higher sampling rate for a fixed window; statute does not support runtime reload of the resolved schema, in keeping with the no-hot-reload design principle.

Trace context propagation uses the W3C Trace Context standard (the `traceparent` and `tracestate` headers). Statute always propagates these headers to upstreams whether or not the request was sampled, so that downstream services can record their own spans for the same trace if they sample independently. This is the correct behaviour and matches the OpenTelemetry specification; the skill should not override it without explicit reason.

Trace IDs appear in access logs when tracing is enabled. This is the load-bearing integration between logs and traces: an operator looking at a slow request in the access log can copy the trace ID and find the corresponding distributed trace, which shows where the time was spent across services. The skill should always recommend enabling tracing and including trace IDs in access logs together; either alone is half the picture.

## Profiling

Statute exposes Go's pprof endpoints on the same listener as the metrics endpoint, under `/debug/pprof/`. This is appropriate for any non-public listener and should never be exposed publicly because pprof can expose internal state (goroutine stacks, heap contents) that leaks information.

The pprof endpoints are useful in three situations. Heap profiles diagnose memory leaks and excessive allocation; the `/debug/pprof/heap` endpoint produces a profile that can be analysed with `go tool pprof`. CPU profiles diagnose latency or throughput issues; the `/debug/pprof/profile` endpoint runs a 30-second CPU sampling profile. Goroutine profiles diagnose hangs or leaks; the `/debug/pprof/goroutine` endpoint produces a snapshot of all goroutine stacks.

PProf is high-value during incidents and reasonable to enable on a strictly private listener. The skill should verify that the listener is not publicly exposed before recommending that pprof remain enabled. If the exposure boundary is unclear, recommend disabling pprof or binding it to localhost or a private interface only. The intended framework default may expose pprof on the same listener as metrics only when that listener is private by deployment design; the verification step is not optional, because "private by design" tends to mean "public by Terraform typo" often enough to make the safer default worth enforcing.

## The integrated picture

Logs, metrics, and traces serve different purposes and are most valuable when used together. Metrics tell you what is happening across the whole population of requests; logs tell you what happened to one specific request; traces tell you why that request behaved the way it did across multiple services.

The standard incident-response workflow uses all three. The operator sees a metrics alert (latency p99 above threshold), drops into the access log to find example requests in the affected window, picks a request and follows its trace to find the slow service, and uses the trace to identify the specific operation that took the time. Each step depends on the previous one and on the integration between the three signals; trace IDs in logs link logs to traces, common identifiers (request ID, user ID) link logs across services, and metric labels link metrics to the dimensions that matter (route, upstream, status).

Statute's intended framework defaults produce this integration automatically: trace IDs flow through to logs, metric labels include route and upstream, and the same request ID appears in logs, traces, and any error responses. The skill should preserve this integration and call out any change that would break it (disabling tracing while keeping logs, omitting route labels from custom metrics, replacing the default request ID generator with something that does not propagate to upstreams).

## Operational defaults the skill should always include

Every scaffolded configuration should include at least the access log and the metrics endpoint. A proxy without these is operationally blind. The skill should never produce a configuration that omits both, even for trivial examples; it is faster to delete what the user does not want than to remember to add what they will need on day two.

Tracing should be enabled by default for any configuration where the user mentions multiple services or microservices. For a single-service deployment without distributed dependencies, tracing produces overhead without proportional benefit and can be left out, but the skill should mention that it is available and easy to enable when the deployment grows.

PProf can be left at the intended framework default (enabled) only when the metrics listener exposure is verified to be private. If exposure is unclear or the listener is reachable from outside the trust boundary, disable pprof or bind it to localhost. The operational value during incidents is high, but the leak risk if exposure is misconfigured is also high; private exposure is the load-bearing assumption.
