# HTTP/2 and HTTP/3

This reference covers the protocol differences that matter operationally, the readiness state of HTTP/3 in 2026, and the configuration considerations specific to running multiple HTTP versions on the same listener.

## Why both versions matter

HTTP/2 is the production default for any modern HTTPS deployment. Browser support is universal, server support is mature, and the protocol's multiplexing eliminates the head-of-line blocking that motivated HTTP/1.1's connection-per-resource workarounds. Statute enables HTTP/2 by default on any HTTPS listener via the `HTTP2()` constructor and the user does not need to think about it.

HTTP/3 is now production-ready for public-facing deployments and is enabled by default in major browsers. The operational case for running it is real: HTTP/3 over QUIC eliminates head-of-line blocking at the transport layer (which TCP cannot do, regardless of how clever HTTP/2 is above it), recovers faster from packet loss on lossy networks, and survives client IP changes (mobile networks switching between cellular and Wi-Fi) without renegotiating connections. For deployments with significant mobile traffic or clients on unreliable networks, HTTP/3 produces measurable user-visible improvements.

The case against enabling HTTP/3 has narrowed but is not zero. UDP traffic is sometimes blocked or rate-limited by middleboxes, particularly in corporate networks; clients that cannot reach the QUIC port fall back to HTTP/2 over TCP, but the fallback adds latency to the first request. QUIC implementations are more complex than TCP plus TLS plus HTTP/2 and have a larger attack surface; the Go ecosystem has matured significantly here, but the surface is still larger than HTTP/2. Operational tooling (packet capture, load balancer configuration, observability) is less mature for QUIC than for TCP-based protocols.

The skill's default recommendation is to enable both HTTP/2 and HTTP/3 on public-facing HTTPS listeners and to leave HTTP/3 disabled on internal listeners where the latency benefits are negligible and the operational complexity is unwelcome.

## Connection coalescing

HTTP/2 and HTTP/3 both allow a client to reuse a single connection for multiple hostnames as long as the connection's certificate covers all the hostnames and the hostnames resolve to the same IP. This is called connection coalescing and it has surprising operational implications.

The most common failure mode is a deployment that splits traffic across multiple statute instances by hostname, expecting each hostname to land on a different instance. If the hostnames share a wildcard certificate and resolve to the same load balancer IP, the client may send all requests for both hostnames over a single coalesced connection, which means they all land on the same backend instance. Whether this is a problem depends on the deployment, but operators are frequently surprised by it.

The mitigation is either to use distinct certificates per hostname (which prevents coalescing because the certificate check fails) or to use distinct IPs per hostname (which prevents coalescing because the connection target differs). Statute does not control coalescing directly; it is a client-side decision based on what the server presents.

## HTTP/2 server push

HTTP/2 server push is deprecated. Chrome removed support in 2022, other browsers have followed, and the feature is not coming back. Statute does not expose server push in the surface API. If a configuration review encounters server push being attempted (for example, a `Link` header with `rel=preload; nopush=false`), the recommendation is to use 103 Early Hints instead, which is supported by all current browsers and does not have the cache-pollution problems that killed server push.

## Stream limits and concurrency

HTTP/2 multiplexes streams over a single connection. The Go standard library default for `MaxConcurrentStreams` is 100, which means a single client connection can have up to 100 in-flight requests simultaneously. For a reverse proxy this is usually fine, but for backends that hold connections open for streaming responses (server-sent events, long polling, gRPC server-streaming), the limit can be reached unexpectedly.

The intended framework default in statute is 250 concurrent streams per connection, which gives more headroom for streaming workloads without being unreasonable. The value is exposed on the listener configuration as `HTTP2().MaxConcurrentStreams(n)` for cases where the deployment needs a different value.

HTTP/3 has the same stream concept but the limits are negotiated differently and the intended framework defaults are calibrated separately. Generally, users should not need to tune HTTP/3 stream limits unless they are specifically debugging stream exhaustion.

## Buffer sizes and flow control

HTTP/2 flow control happens at two levels: per-stream and per-connection. The Go standard library defaults are conservative and can produce poor throughput for high-bandwidth-delay-product paths (long-distance connections with high bandwidth). Statute's intended framework defaults bump the per-stream initial window to 1 MiB and the per-connection window proportionally, which improves throughput for clients on long-distance links without significantly increasing memory usage for typical workloads.

HTTP/3 has analogous flow control with different mechanics. The intended framework defaults follow the same principle of being more generous than the standard library default, calibrated for typical reverse proxy workloads.

If a deployment shows poor throughput on long-distance connections specifically, the flow control windows are the first thing to investigate. The relevant metrics are exposed via the Prometheus endpoint and the resolved schema documents the current values.

## ALPN and protocol negotiation

ALPN (Application-Layer Protocol Negotiation) is the TLS extension that lets the client and server agree on which HTTP version to use over a TLS connection. Statute's intended framework default ALPN list for the TCP listener is `["h2", "http/1.1"]`, which means the server prefers HTTP/2 but accepts HTTP/1.1 fallback.

Adding `"http/1.0"` to the ALPN list is unnecessary and not recommended; HTTP/1.0 has no ALPN identifier and clients that want HTTP/1.0 simply do not advertise ALPN. Removing `"http/1.1"` to force HTTP/2-only is occasionally useful for internal listeners where every client is known to support HTTP/2, but it breaks any HTTP/1.1 health checker, observability tool, or debugging client and should be done with eyes open.

HTTP/3 still uses ALPN, but the ALPN exchange happens inside QUIC's integrated TLS 1.3 handshake rather than inside a separate TLS-over-TCP connection. The ALPN value for HTTP/3 is `h3`. Clients commonly discover the HTTP/3 endpoint via the `Alt-Svc` response header or via HTTPS/SVCB DNS records, and then negotiate `h3` over QUIC during the handshake. Statute emits `Alt-Svc` automatically when HTTP/3 is enabled on the corresponding HTTPS listener; the intended default Alt-Svc cache lifetime is 24 hours, which is configurable but rarely needs adjustment.

## Operational pitfalls

The most common HTTP/2-specific production problem is connection-level rate limiting by upstreams that do not understand HTTP/2 multiplexing. An upstream that limits "requests per connection" sees a single multiplexed connection with hundreds of streams and either rejects them all or processes them serially. The mitigation is to ensure upstreams understand HTTP/2 (modern Go services do; older ecosystems sometimes do not) or to disable HTTP/2 to upstreams specifically while keeping it enabled for the client-facing listener.

The second pitfall is the interaction between HTTP/3 and TLS configuration. HTTP/3 requires TLS 1.3, with no fallback. A `MinVersion` of TLS 1.2 alone is not the problem here, because TLS 1.3 remains available; the problem is configurations that disable TLS 1.3 explicitly, cap the maximum TLS version below 1.3, or apply incompatible TLS settings to the QUIC listener specifically. The skill should check for those specific patterns during review rather than flagging any TLS 1.2 minimum as automatically incompatible with HTTP/3.

The third pitfall is debugging. Tools like `curl` support HTTP/3 only if compiled with QUIC support, which is not the default in most distributions. When a user reports "HTTP/3 isn't working" and is testing with curl, the first question to ask is whether their curl binary actually supports HTTP/3 (`curl --version` should list `HTTP3` in the features). The framework's metrics endpoint exposes HTTP/3 connection counts, which is a more reliable way to verify HTTP/3 is being used than client-side testing.
