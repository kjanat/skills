# Go net/http Pitfalls

This reference documents the well-known traps in the Go standard library that statute either handles automatically or that users may encounter when extending statute or debugging unexpected behaviour. The skill should consult this file for any review or debugging task and surface the relevant pitfall when a configuration smells like one of these failure modes.

## Missing default timeouts

The Go `http.Server` zero value has no timeouts set. A server constructed with `&http.Server{Handler: h}` and started with `ListenAndServe` will accept connections that never send headers, never finish reading the request body, and never close. This is the canonical Slowloris vector and the single most common production pitfall in Go HTTP servers.

The four timeouts that matter are `ReadHeaderTimeout`, `ReadTimeout`, `WriteTimeout`, and `IdleTimeout`. `ReadHeaderTimeout` bounds how long the server will wait for request headers to arrive after the connection is accepted; without it, a client can hold a connection open indefinitely by sending headers one byte at a time. `ReadTimeout` bounds the entire request including body; for endpoints that accept large uploads, this needs to be generous, which is why `ReadHeaderTimeout` is preferred as the slowloris-specific defence. `WriteTimeout` bounds the entire response. `IdleTimeout` bounds keep-alive connections between requests.

Statute sets all four in its intended framework defaults and the user can override them via the `Defaults` block. The skill should never produce a configuration without `ReadHeaderTimeout` set, even if every other timeout is left to the default, because it is the load-bearing defence against denial-of-service via slow connections.

## Transport pool tuning

The Go `http.Transport` (used by statute for proxy connections to upstreams) has connection pool defaults that are appropriate for a CLI tool talking to one server but inappropriate for a reverse proxy. The default `MaxIdleConnsPerHost` is 2, which means a proxy with high concurrency to a single upstream will repeatedly tear down and rebuild connections, paying the TCP and TLS handshake cost on every request after the first two are in flight.

Statute's intended framework default is 10 idle connections per host with a 90-second idle timeout, which is appropriate for typical reverse proxy workloads. For deployments with very high concurrency to a small number of upstreams, raising `MaxIdleConnsPerHost` further is worthwhile; the metric to watch is the rate of new connections to the upstream, which should be a small fraction of the request rate during steady state.

The related setting `MaxConnsPerHost` is unset by default in both the standard library and statute, meaning the number of concurrent connections per upstream is unbounded. For most deployments this is correct (the upstream's own capacity is the limit), but for upstreams with strict per-client connection limits, setting `MaxConnsPerHost` prevents the proxy from exceeding the limit. The trade-off is that requests beyond the limit queue inside statute waiting for a free connection, which can produce surprising latency spikes if the limit is set too low.

`DisableCompression` should generally be true for proxy transports. Statute decompresses responses only when it needs to inspect or modify them; for pure pass-through, leaving the upstream's compression intact and forwarding the compressed bytes is more efficient than decompressing in the proxy and recompressing for the client.

## Body close semantics

Every `http.Response` returned by an `http.Client` (or by `Transport.RoundTrip`) has a `Body` that must be closed even if the body is never read. Failing to close the body leaks the connection: it cannot be returned to the pool and cannot be reused, which forces the next request to that host to open a new connection.

The pattern that catches people is reading only the headers and returning. The body still needs to be closed. The pattern that catches people more often is reading partway through the body and returning on an error before reading the rest. The remaining bytes need to be drained (read and discarded) before closing, otherwise the connection cannot be reused even though it is closed properly.

Statute handles this internally for proxy responses, but any user-written middleware that inspects upstream responses must drain and close. The `references/observability.md` file shows the canonical pattern for middleware that needs to read the response body.

## Context propagation

`http.Request.Context()` returns the request's context, which is canceled when the client disconnects or when the server's read timeout fires. Any work done on behalf of the request should respect this context: outbound HTTP calls should pass it via `http.NewRequestWithContext`, database queries should use the `Context` variants of query methods, and long-running computations should check `ctx.Done()` periodically.

The pitfall is launching a goroutine from a request handler without propagating the context. The goroutine outlives the request, holds resources, and cannot be canceled when the client disconnects. For genuinely fire-and-forget work, this is sometimes intentional, but it should be done with `context.WithoutCancel` (Go 1.21+) so the lack of propagation is explicit, not accidental.

Statute's middleware stack propagates context through the chain automatically. User-written middleware should accept the context from the incoming request and pass it through to any work done on behalf of the request.

## ResponseWriter flushing

The `http.ResponseWriter` interface buffers writes. For typical request-response handlers this is invisible: the buffer is flushed automatically when the handler returns. For streaming responses (server-sent events, large file downloads, long polling), the handler needs to call `Flush` explicitly to push buffered bytes to the client.

The pitfall is that not every `ResponseWriter` implementation supports flushing. The handler must type-assert to `http.Flusher` and call `Flush` only if the assertion succeeds. With statute, all middleware in the chain must preserve the flusher capability; a middleware that wraps the response writer and does not implement `http.Flusher` itself silently breaks streaming for everything downstream.

Statute provides a `responsewriter` helper package that produces wrappers preserving all the optional interfaces (`Flusher`, `Hijacker`, `Pusher`, `CloseNotifier`). User-written middleware should use these helpers rather than wrapping the response writer directly.

## Graceful shutdown ordering

`http.Server.Shutdown` stops accepting new connections, waits for in-flight requests to complete, and then returns. The default timeout is the context passed to `Shutdown`; if the context expires before in-flight requests complete, `Shutdown` returns an error and the server exits with requests still in flight.

The pitfall is shutting down dependent resources (database connections, upstream connections) before the HTTP server's `Shutdown` completes. In-flight requests need access to those resources to finish; closing them first causes the requests to fail with errors rather than completing successfully.

The correct ordering is: receive shutdown signal, call `Server.Shutdown` with a generous context, wait for it to return, then close downstream resources. Statute handles this internally and the user does not need to think about it for the server itself, but any user-written middleware that holds external resources must follow the same ordering when those resources have their own lifecycle.

## HTTP/2 connection reuse with streaming

HTTP/2 allows many streams over a single connection. The Go standard library's HTTP/2 implementation handles this correctly for typical workloads, but there is a subtle issue with long-running streams (server-sent events, gRPC server streaming). If a single connection has multiple long-running streams, the connection cannot be cleanly closed until all streams complete, which interacts badly with graceful shutdown and idle timeout.

The intended framework default in statute is to limit each connection's stream lifetime indirectly by setting `IdleTimeout` to 120 seconds, which closes connections that have been idle (no active streams) for that long. For deployments with genuinely long-running streams (events that may stay open for hours), the timeout needs to be raised or the streams need a heartbeat mechanism to keep the connection from being torn down for "idleness" while streams are active. The Go standard library considers a connection with active streams "active" for purposes of `IdleTimeout`, so this is rarely a problem in practice, but it is a place where the interaction between protocol and intended framework defaults matters.

## Header canonicalisation

The `http.Header` type canonicalises header names on `Set`, `Add`, and `Get`: `content-type` becomes `Content-Type`, `x-request-id` becomes `X-Request-Id`. This is correct for HTTP/1.1, where headers are case-insensitive. It is also correct for HTTP/2, where headers are required to be lowercase on the wire but the Go implementation handles the conversion transparently.

The pitfall is when middleware constructs header maps directly without going through the canonicalisation methods. A header set as `http.Header{"x-custom": []string{"value"}}` is not canonicalised and will not be found by `headers.Get("X-Custom")`. The fix is always to use `Set` and `Add`, never to construct the map directly.

Statute's middleware helpers handle canonicalisation correctly. User-written middleware that manipulates headers should follow the same discipline.

## TrustedProxies and X-Forwarded-For

When statute runs behind another reverse proxy (a CDN, a cloud load balancer, an on-premises edge), the client IP is not the direct connection peer; it is in the `X-Forwarded-For` header, set by the upstream proxy. Statute uses the `TrustedProxies` setting to determine which `X-Forwarded-For` entries to trust.

The pitfall is leaving `TrustedProxies` empty (the default) when statute is behind another proxy. With no trusted proxies configured, statute uses the direct peer IP, which is the upstream proxy's IP. Every client appears to have the same IP, which breaks IP-hash load balancing, IP-based rate limiting, and any logging that uses client IP for analytics.

The correct configuration is to populate `TrustedProxies` with the IP ranges of the upstream proxy. Statute then walks `X-Forwarded-For` from right to left, accepts entries that are in the trusted ranges, and stops at the first entry that is not, which is the actual client IP. The skill should always ask whether statute is behind another proxy when scaffolding and configure `TrustedProxies` accordingly.

## Body size limits

The Go standard library does not impose a default request body size limit. A handler that reads the entire request body via `io.ReadAll` will happily allocate gigabytes of memory if the client sends a gigabyte. The standard mitigation is `http.MaxBytesReader`, which wraps the body and returns an error after the configured limit is exceeded.

Statute applies a per-route body size limit configurable via the `MaxBodySize` middleware. The intended framework default is 1 MiB, which is generous for typical API requests and prevents memory exhaustion from accidental or hostile large requests. Routes that legitimately need to accept larger bodies (file uploads, bulk imports) should configure a higher limit explicitly. The skill should call out any route that does not have a body size limit configured during review.
