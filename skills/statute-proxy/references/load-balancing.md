# Load Balancing

This reference covers the load balancing strategies statute exposes, when each is appropriate, how they interact with health checks, and how upstream pools behave during partial outages. The surface API exposes strategies via the `Strategy` field on `Pool`; this document explains how to choose.

## Round-robin

Round-robin distributes requests across backends in declaration order, advancing one position per request. With weighted backends, the rotation is biased proportionally: a backend with weight 2 receives twice as many requests as a backend with weight 1 over any sufficiently long window. Round-robin is the simplest strategy, has no per-request state beyond a counter, and produces predictable distribution.

Round-robin is appropriate when backends are functionally identical, when request processing time is roughly uniform across requests, and when the deployment is small enough that even distribution by request count produces even distribution by load. It is the right default for most web service deployments where the request mix is varied and processing time averages out.

Round-robin is inappropriate when request processing times vary widely. A backend that gets unlucky with a sequence of expensive requests will queue up while other backends sit idle, because round-robin has no visibility into backend load. For workloads with bimodal or long-tailed request distributions, prefer least-connections.

## Least-connections

Least-connections routes each request to the backend with the fewest in-flight requests at the moment of routing. Statute tracks in-flight count per backend and updates the count on request start and completion. The strategy adapts naturally to varying request processing times: a backend that is slow processing one request will accumulate fewer new requests because its in-flight count stays high.

Least-connections is appropriate for any workload where request processing times vary, particularly long-running requests like file uploads, large API responses, or server-sent events. It is also appropriate when backends have heterogeneous capacity (different instance sizes, different hardware) because the in-flight count reflects each backend's effective capacity rather than just request count.

Least-connections is inappropriate when the workload includes many very short requests that complete before the routing decision matters. For sub-millisecond requests at high RPS, the overhead of tracking in-flight counts can outweigh the distribution benefit; round-robin is simpler and effectively equivalent.

The interaction with weights is worth understanding. Statute computes effective load as in-flight count divided by weight, so a backend with weight 2 is permitted twice as many in-flight requests before being considered "as loaded" as a backend with weight 1. This produces sensible behaviour for heterogeneous capacity but means that weights must be set thoughtfully; setting weights based on instance size is straightforward, but setting weights based on observed performance is a maintenance burden the operator should be aware of.

## IP-hash

IP-hash routes each request to a backend selected by hashing the client's IP address. The same client is routed to the same backend across all requests as long as the backend remains healthy and the pool composition does not change. This produces session affinity without requiring cookies or any client cooperation.

IP-hash is appropriate for workloads where session affinity matters and the application cannot use a shared session store. The classic example is a stateful application with in-memory sessions where the session is lost if requests for the same user land on different backends. IP-hash is also useful for caching layers where consistent routing improves cache hit rates by ensuring the same client repeatedly hits the same cache.

IP-hash is inappropriate when client IP is not a reliable identifier. Mobile clients change IPs frequently, corporate clients share a single IP via NAT, and clients behind a reverse proxy without proper `X-Forwarded-For` configuration will all hash to the same backend. IP-hash also produces uneven distribution when the client population is small or skewed; a single client generating most of the traffic will overload one backend regardless of pool size.

The IP used for hashing respects the `TrustedProxies` setting in the defaults block. If trusted proxies are configured, the leftmost IP in `X-Forwarded-For` that is not in the trusted proxy ranges is used. Otherwise, the direct connection peer IP is used. This is the only load balancing strategy whose behaviour depends on `TrustedProxies`, and the skill should call out the dependency during review of any IP-hash configuration.

## Random

Random selects a uniformly random backend per request. With weighted backends, the selection is biased proportionally to the weights. Random has no per-request state and produces distribution that is statistically equivalent to round-robin over long windows but with more variance over short windows.

Random's main appeal is that it is stateless and produces independent decisions across multiple proxy instances. If a deployment runs multiple statute instances in parallel (load-balanced upstream by some other layer), round-robin on each instance produces correlated load patterns when their counters happen to align; random across all instances produces independent load with no correlation.

In practice, the difference between random and round-robin rarely matters at scale. Statute exposes random for completeness and for the specific case of multi-instance deployments where the user wants to avoid correlation, but round-robin or least-connections is the more common choice.

## Health checks

All strategies skip backends that are currently marked unhealthy. Statute runs active health checks against each backend at the configured interval, marking a backend unhealthy after `UnhealthyThreshold` consecutive failures and healthy again after `HealthyThreshold` consecutive successes.

The health check default is to GET the configured `Path` (commonly `/healthz`) with a 2-second timeout and consider any 2xx response healthy. Non-2xx responses, timeouts, and connection errors all count as failures. The path, timeout, and success criteria are configurable; the skill should suggest configuring a dedicated health endpoint on backends rather than reusing a real application endpoint, because health checks should test reachability and basic process liveness rather than exercising real business logic.

The interval, unhealthy threshold, and healthy threshold form a trade-off between detection speed and false positives. A short interval with a low threshold detects failures quickly but is more likely to mark a backend unhealthy due to transient network blips. A long interval with a high threshold is robust to transients but slow to react. The intended framework defaults are 10-second interval, 3 consecutive failures, and 2 consecutive successes; these are reasonable for typical web workloads and should rarely need tuning.

Backends marked as `Backup: true` do not receive traffic while any non-backup backend is healthy. They are activated only when all primary backends are unhealthy, which provides a tier of failover capacity that does not consume resources during normal operation. This is useful for reserve capacity (a smaller backup pool that absorbs traffic during incidents) or for cross-region failover (backup backends in a different region that take traffic only when the primary region is fully down).

## Behaviour during partial outages

When some backends are unhealthy, the surviving backends absorb the redirected traffic. With round-robin, the load is redistributed evenly across survivors; with least-connections, the survivors absorb proportionally to their available capacity; with IP-hash, the affected client IPs are remapped to survivors and the unaffected IPs continue routing to their original backends. Once an unhealthy backend recovers and passes the healthy threshold, it rejoins the pool and starts receiving its share of traffic again.

The behaviour during the recovery transition matters operationally. Least-connections will route disproportionately to a recovering backend because its in-flight count is zero, which can produce a thundering-herd effect on a backend that is technically healthy but still warming up caches or JIT-compiling. The intended framework default includes a slow-start mode that ramps a recovering backend's effective weight from zero to its configured weight over 30 seconds, which avoids the thundering herd. Slow-start is enabled by default for least-connections and disabled by default for the other strategies; it can be configured explicitly via `Strategy: statute.LeastConnections.SlowStart("60s")` for longer or shorter ramps.

## Choosing a strategy: a short decision tree

If the workload requires session affinity and the application cannot use shared sessions, use IP-hash. If request processing times vary substantially, use least-connections. If multiple proxy instances run in parallel and decision correlation is a concern, consider random. Otherwise, use round-robin.

This tree handles most cases. The skill should still ask the user about their workload during scaffolding rather than picking blindly, but in the absence of specific information, round-robin is the safe default and the user can change it cheaply later.
