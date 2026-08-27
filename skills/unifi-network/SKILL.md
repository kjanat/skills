---
name: unifi-network
description: Query and configure Ubiquiti UniFi through the official APIs — Site Manager (api.ui.com), the on-prem Network and Protect APIs, and the cloud connector that bridges them. Use when the user mentions UniFi, Ubiquiti, a UDM/UDR/UXG/Cloud Key, a UniFi API key, firewall zones or policies, VLANs and networks, traffic routes, or port forwards. Use for any reachability failure on a network where a UniFi gateway routes between subnets, even when no API is named — "why can't my laptop reach my server", "is my VLAN isolated", "which firewall rule is blocking this" are all UniFi questions once a UniFi gateway sits in the path. Also use before writing any script that talks to api.ui.com, since guessing endpoints there wastes far more time than reading the published spec.
license: MIT
metadata:
  author: kjanat
  version: "1.0"
  ui:
    network: "v10.4.57"
    site-manager: "v1.0.0"
---

# UniFi Network: querying and changing a UniFi site through the official APIs

Ubiquiti ships several APIs that look similar and are not. Getting useful work done depends
almost entirely on picking the right one, authenticating it correctly, and knowing which of
three overlapping endpoint generations actually answers your question. Almost every hour lost
to these APIs is lost to guessing rather than to difficulty, so this skill front-loads the
discovery mechanism and the failure signatures.

## Never guess an endpoint

Ubiquiti publishes machine-readable indexes. Read them before writing a single request. Probing
paths and reading the 404s is slower, produces a false picture of what exists, and reliably
misses the one endpoint that solves the problem.

| What you need                      | Where it lives                                                         |
| ---------------------------------- | ---------------------------------------------------------------------- |
| Which APIs exist, current versions | `https://developer.ui.com/llms.txt`                                    |
| Full endpoint list for one service | `https://developer.ui.com/{service}/{version}/llms.txt`                |
| Request and response shapes        | `https://developer.ui.com/{service}/{version}/openapi.json`            |
| Ready-made calls                   | `https://developer.ui.com/{service}/{version}/postman-collection.json` |

Services as of writing: `network`, `protect`, `mobility`, `innerspace`, `site-manager`,
`carrier-fabric`. Versions move — take them from the root `llms.txt` rather than from memory or
from this file. The docs pages themselves are JavaScript-rendered, so fetching the HTML gives
you a title and nothing else; fetch the JSON.

`jq '.paths | keys' openapi.json` gives the complete surface of a service in one command. Do
that first and the rest of the work is mechanical.

## Authentication

Every Ubiquiti API uses `X-API-KEY`. Bearer tokens return 401 everywhere — if a user tells you
to use bearer auth, they are misremembering, and the 401 will look like a bad key rather than a
bad header.

Two kinds of key exist and they are not interchangeable:

**Site Manager key** (created at `unifi.ui.com`) authenticates against `https://api.ui.com`. Its
scopes are chosen at creation time. A key scoped only to Site Manager can read inventory —
hosts, sites, devices, ISP metrics — and nothing else. A key that also has **UniFi Applications**
scope (Network, Protect, InnerSpace) can reach through the connector into the console itself,
which is what you almost always need.

**Local Network key** (created in the console UI under Settings → Control Plane → Integrations)
authenticates directly against the console at `https://<console-ip>/proxy/network/...`. It is a
different string and the two do not cross over.

The key belongs in the environment as `UBIQUITI_API_KEY`. In Claude Code the durable place for
that is the `env` block of `~/.claude/settings.json`, which is injected into every session, so
the skill answers questions immediately instead of asking the user to fetch a key first. If the
key must not sit in that file, exporting it from the shell profile works identically —
`references/connector.md` covers both and the tradeoff between them.

Read that file for the scope failure signatures too. A 403 saying `insufficient permissions for
this host` usually means the key lacks Applications scope — but it is also what a typo in the
application prefix produces, since the connector routes on the first path segment and rejects an
unknown one before any permission check. A wrong path inside a real application returns 404
instead. Checking the prefix before concluding the key is under-scoped saves a long detour.

## The connector is the way in

The Site Manager API exposes a proxy that forwards to the console's own APIs, so you can reach
the on-prem Network and Protect APIs from anywhere without a VPN:

```
GET|POST|PUT|PATCH|DELETE  https://api.ui.com/v1/connector/consoles/{hostId}/{path}
```

The request lands on the console as `http://127.0.0.1/proxy/{path}`. So `network/integration/v1/sites`
becomes `/proxy/network/integration/v1/sites` locally. `hostId` comes from `GET /v1/hosts`.

Constraints worth knowing before you build on it: 100 requests per minute per console, 25 second
timeout per proxied request, 10 MB response cap, and console firmware ≥ 5.0.3. A non-organization
key only reaches consoles owned by the key's account.

`scripts/unifi-query.sh` wraps this call. Use it rather than re-deriving the curl invocation each
time — it handles the host lookup, the header, and reports the real HTTP status instead of
swallowing it.

## Three generations of endpoint live on the console

This is the part that wastes the most time. The console answers three different API families and
they cover different ground:

**`network/integration/v1/...`** is the official, documented, versioned API. It is what
`openapi.json` describes, it is stable, and it is the only one you should write changes through.
Firewall policies, zones, clients, devices, and site listings all live here. Prefer it always.

**`network/api/s/{site}/rest/...`** is the legacy controller API. Undocumented publicly but
stable in practice, and it still holds things the integration API has not surfaced —
`networkconf` (the LAN/VLAN definitions) is the important one.

**`network/v2/api/site/{site}/...`** is the internal API the web UI itself calls. It exposes
`trafficroutes`, `firewall-policies` in the UI's own shape, and other newer features. Useful for
reading when nothing else has the data; treat it as unstable and never write through it.

Note the two different site identifiers: the integration API uses a UUID
(`c3d4e5f6-3333-4333-8333-...`), while legacy and v2 use the short name (`default`). Mixing them up
produces confusing empty results rather than errors.

`references/endpoints.md` lists the paths verified to work through the connector, with what each
returns.

## Reading is free, writing is not

Reading configuration is safe and you should do it liberally — the whole point of this skill is
to replace guesswork with facts about the actual site.

Changing configuration is different. A firewall policy, a network definition, or a port forward
is live infrastructure on someone's home or business network, and a wrong rule can lock the user
out of their own gateway or silently expose a segment they meant to keep closed. Get explicit
confirmation before any POST, PUT, PATCH, or DELETE, and show the exact request body first. If
the user has already said "yes, make the change", that authorization covers the change you
described, not adjacent tidying you noticed along the way.

When you do write, prefer the narrowest change that solves the stated problem. If a block rule is
in the way, disabling it discards intent the user had; the fix is to make that rule match less.
A policy's match is composable — address and port filters, each with a `matchOpposite` flag — so
"block this subnet except on 80 and 443" is one rule, not a rule plus an ordered exception above
it. Reach for an ordering change only when the model genuinely cannot express the intent in
place, because ordering is a separate call (`PUT /firewall/policies/ordering`) and a pair of
rules whose meaning depends on their order is easy for a later edit to break.

Read one existing policy in full before designing any of this. Filtering the list down to name,
action, and addresses hides the port filters entirely, and a site's own rules usually already
show which mechanism fits.

## Diagnosing "X cannot reach Y"

Most UniFi questions arrive as a reachability failure, not as an API question. The failure mode
tells you which layer to look at, and starting at the wrong layer is how an hour disappears:

| Symptom            | What it means                                           |
| ------------------ | ------------------------------------------------------- |
| Timeout            | Packets went nowhere — routing, firewall, or wrong path |
| Connection refused | Path works, nothing is listening                        |
| TLS error          | You arrived; certificate or SNI is wrong                |
| HTTP 502/504       | Reverse proxy is up, the service behind it is not       |
| HTTP 404           | Everything is up; the routing rule does not match       |

Only the last two are application problems. A timeout is a network problem and no amount of
inspecting the service will explain it.

`references/diagnostics.md` has the full triage recipe, including the traps that make a UniFi
network lie to you — a gateway that answers pings while refusing to route, a device inventory
that looks like a network inventory, and a firewall rule that filters only new connections and
therefore breaks reachability in exactly one direction.

## Bundled resources

- `references/connector.md` — auth, key scopes, failure signatures, connector limits
- `references/endpoints.md` — verified endpoints per generation, with what each returns
- `references/diagnostics.md` — reachability triage, UniFi-specific traps, worked example
- `scripts/unifi-query.sh` — connector call wrapper; resolves the host id, reports real status
