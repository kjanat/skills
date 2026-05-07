# TLS and ACME

This reference covers TLS termination, certificate management, ACME flows, and the trade-offs between static certificates and auto-provisioning. The surface API exposes both modes through the `HTTPS` listener constructor; this document explains when to reach for each and what to configure.

## Static certificates versus ACME

Static certificates are appropriate when the certificates are managed by an external system and provisioned onto the host out of band. This includes deployments behind a corporate PKI, deployments where certificates are issued by a hardware security module, deployments using mTLS with private CAs, and any environment where the host running statute does not have outbound HTTP access to an ACME directory or cannot expose the ACME challenge endpoints publicly.

ACME provisioning via Let's Encrypt or any RFC 8555 directory is appropriate when the deployment is internet-facing, the host can serve the HTTP-01 or TLS-ALPN-01 challenge, and the operator wants automated renewal without manual intervention. ACME is the right default for the common case of a public web service. Statute uses the TLS-ALPN-01 challenge by default because it does not require a separate port-80 listener for the challenge; HTTP-01 is available for environments where TLS-ALPN-01 is blocked.

A single listener can mix both modes. Certificates supplied via `Certificates` take precedence; ACME fills in any hostname not covered by a static certificate. This is useful for hybrid deployments where some hostnames use organisation-managed certificates and others use Let's Encrypt.

## ACME storage and rate limits

ACME-issued certificates must be persisted across restarts. The `Storage` directive on `AutoTLS` specifies the directory where certificates, account keys, and ACME state are written. The directory must be writable by the statute process and should be on persistent storage; using an ephemeral filesystem causes statute to re-issue certificates on every restart, which will hit the Let's Encrypt rate limits within a few deployments.

The Let's Encrypt rate limits that matter for statute users in practice are the Certificates per Registered Domain limit (50 per week, counted per registered domain across all subdomains) and the Duplicate Certificate limit (5 per week, counted per exact set of hostnames). Hitting either of these limits during a deployment storm is the most common ACME failure mode. The recommended mitigations are to use the staging directory during development and CI, to ensure the storage directory is persistent in production, and to avoid issuing certificates from short-lived containers without shared storage.

For the staging directory, configure `AutoTLS` with `.Directory("https://acme-staging-v02.api.letsencrypt.org/directory")`. Staging certificates are not trusted by browsers but use much higher rate limits and are appropriate for any non-production environment.

## TLS configuration defaults

The intended framework default for `MinVersion` is TLS 1.2. TLS 1.3 is supported and preferred when both peers support it; the minimum version exists to set the floor, not the ceiling. There is rarely a reason to lower the minimum below TLS 1.2 in 2026, and doing so should be treated as a configuration smell during review.

The intended framework default for `CipherSuites` is the Go standard library's secure cipher list, which excludes RC4, 3DES, and CBC-mode ciphers without AEAD. Statute does not allow users to enable insecure ciphers through the surface API; if a deployment requires interoperability with a system that only supports older ciphers, the user must reach into the resolved schema directly and accept the security implications.

The intended framework default for `ALPN` on the TCP listener is `["h2", "http/1.1"]`. When HTTP/3 is enabled, statute advertises it via the `Alt-Svc` response header on HTTPS responses, which is one of the mechanisms clients use to discover HTTP/3 endpoints; HTTPS/SVCB DNS records are an alternative discovery path. HTTP/3 itself still negotiates via ALPN with the value `h3`, but that exchange happens inside QUIC's integrated TLS 1.3 handshake rather than over a TCP-based TLS connection.

OCSP stapling is enabled by default. This requires the certificate's issuer to operate a reachable OCSP responder, which Let's Encrypt does. For private PKIs that do not run an OCSP responder, OCSP stapling should be explicitly disabled to avoid startup delays from failing OCSP fetches.

## Certificate selection at handshake time

When a TLS ClientHello arrives, statute selects a certificate based on the SNI hostname. The selection rules in declaration order are: an exact match in the static `Certificates` slice; a wildcard match in the static slice (a certificate for `*.example.com` matches `api.example.com` but not `example.com` itself); an ACME-issued certificate for the requested hostname; ACME issuance on the fly if the hostname is in the `AutoTLS` allow-list and no certificate exists yet.

On-demand issuance during the handshake is convenient but adds handshake latency for the first connection to each new hostname and exposes the ACME provisioning flow to any client that can complete a TLS ClientHello. For deployments with a known fixed set of hostnames, pre-warming certificates at startup is preferred and is the default behaviour for hostnames listed explicitly in `AutoTLS`.

## mTLS and client certificates

Statute supports mutual TLS for client authentication. The surface API exposes this via `RequireClientCert` and `ClientCAs` on the TLS configuration. The most common pattern is to require client certificates on a specific listener used for service-to-service traffic while leaving the public listener using normal server-only TLS.

When using mTLS, the intended framework default is to verify the client certificate against the configured CA pool and fail the handshake if verification fails. Less strict modes (request but do not require, or require but do not verify) are available but should be treated as advanced configurations and called out in review for explicit justification.

## Operational pitfalls

The most common TLS-related production problem is certificate expiry caused by the renewal process failing silently. ACME renewals happen in the background, and if the storage is misconfigured or the ACME challenge cannot complete, the renewal fails and statute continues serving with the existing certificate until it expires. Statute logs renewal failures at warn level and exposes them as the `statute_acme_renewal_failures_total` metric; both should be alerted on in any production deployment.

The second most common problem is OCSP responder failures during startup. If `OCSPStapling` is enabled and the OCSP responder is unreachable, statute logs a warning and proceeds without stapling rather than failing startup. The certificate is still served correctly; only the stapled OCSP response is missing. This is rarely user-visible but does cause some clients (notably older Apple devices with hard-fail OCSP) to reject the connection. The mitigation is to ensure OCSP responder reachability or to disable stapling explicitly.

The third pitfall worth flagging is the interaction between HTTP/3 and TLS configuration. HTTP/3 requires TLS 1.3, with no fallback. A `MinVersion` of TLS 1.2 alone is not the issue, because TLS 1.3 remains available; the issue arises when a configuration disables TLS 1.3 explicitly, caps the maximum TLS version below 1.3, or applies incompatible TLS settings to the QUIC listener specifically. The skill should look for those specific patterns during review rather than treating any TLS 1.2 minimum as automatically incompatible with HTTP/3.
