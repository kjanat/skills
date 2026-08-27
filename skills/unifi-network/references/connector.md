# Authentication and the cloud connector

## Header

`X-API-KEY: <key>` on every request, to both `api.ui.com` and a local console. The OpenAPI spec
declares exactly one security scheme:

```json
"site-manager-api-key": { "type": "apiKey", "in": "header", "name": "X-API-Key" }
```

Header names are case-insensitive, so `X-API-KEY` and `X-API-Key` both work. Bearer auth does
not exist in any of these APIs and returns 401 with `{"code":"unauthorized"}`. That 401 is
indistinguishable from a revoked key, so rule out the header before suspecting the key.

## Where the key lives

The script and every example here read `UBIQUITI_API_KEY` from the environment. In Claude Code
the durable place for that is the `env` block of `~/.claude/settings.json`:

```json
{
  "env": {
    "UBIQUITI_API_KEY": "…"
  }
}
```

Values there are injected into every session, so the skill works immediately instead of the user
pasting a key each time — which matters for a skill whose whole value is answering questions
without a round trip to a browser.

The tradeoff is that the key sits in plaintext in a file any tool in the session can read. That is
the price of having it available at all, and it is a deliberate choice rather than an oversight
when someone makes it. Worth knowing rather than worth arguing about: a `permissions.deny` rule on
`**/*.env*` does not cover `settings.json`, so denying env-file reads and keeping keys here are
consistent only if the intent is to protect *project* secrets rather than the user's own.

If the key should not live in that file, export it from the shell profile instead — out of `pass`,
a keyring, or a secret manager — and the skill works the same way.

To show such a file in a transcript, a screenshot, or an issue, pipe it through a redactor rather
than trusting yourself to blank the right lines by hand.
[`envctl`](https://github.com/kjanat/envctl) masks secret-looking values on the way through, and
reads from stdin, so it works on `settings.json` as well as on env files:

```sh
curl -fsSL https://raw.githubusercontent.com/kjanat/envctl/master/install.sh | bash
envctl redact < ~/.claude/settings.json
```

Its editing commands (`envctl set <file> <KEY> <VALUE>` and friends) are for `.env`-shaped files
only — they do not understand JSON, so do not point them at `settings.json`. Change that file with
a normal editor, or with a JSON-aware tool.

## Two key types

|                       | Site Manager key                                      | Local Network key                                    |
| --------------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| Created at            | `unifi.ui.com`                                        | console UI → Settings → Control Plane → Integrations |
| Authenticates against | `https://api.ui.com`                                  | `https://<console-ip>/proxy/network/...`             |
| Reaches the console   | only with UniFi Applications scope, via the connector | directly                                             |
| Survives              | account-level                                         | that console only                                    |

A Site Manager key carries scopes chosen when it is created:

- **Site Manager** — inventory only: hosts, sites, devices, ISP metrics, SD-WAN configs
- **UniFi Applications** — Network, Protect, InnerSpace, reachable through the connector
- **Sites** — which sites the key covers

A key with only Site Manager scope is the common trap. It authenticates fine, lists your
hardware, and then fails on everything that matters.

## Failure signatures

| Response                                     | Meaning                                          | Fix                                               |
| -------------------------------------------- | ------------------------------------------------ | ------------------------------------------------- |
| 401 `unauthorized`                           | wrong header (bearer), or bad/revoked key        | use `X-API-KEY`                                   |
| 403 `insufficient permissions for this host` | key lacks UniFi Applications scope               | recreate the key with Applications scope          |
| 404 on `api.ui.com/v1/...`                   | endpoint does not exist in Site Manager          | check the OpenAPI spec, stop guessing             |
| 404 through the connector                    | path does not exist *on the console*             | check the Network spec, or try another generation |
| 000 / timeout to `*.id.ui.direct`            | direct-connect domain is not reachable from here | use the connector instead                         |

Two different causes produce that 403, and they are easy to confuse. The connector routes on the
first path segment, so an unrecognised application prefix is rejected before any permission check
reaches the console. Measured:

```
nope/does/not/exist                 -> 403 insufficient permissions for this host
network/integration/v1/doesnotexist -> 404
```

So a typo in the application name (`netwerk/...`, or forgetting the prefix entirely) reads as a
permission error, while a wrong path *inside* a real application reads as 404. Before concluding
the key is under-scoped, check that the path starts with `network`, `protect`, or `innerspace`.

Once the prefix is right, the 403 is console-wide rather than path-specific: if
`network/integration/v1/sites` returns it, so will `protect/integration/v1/meta/info`. Testing a
second application is the cheap way to confirm a scope problem.

## Connector call shape

```
GET|POST|PUT|PATCH|DELETE  https://api.ui.com/v1/connector/consoles/{id}/{path}
```

The console receives it as `http://127.0.0.1/proxy/{path}`. Everything the console's own web UI
and integration APIs expose is reachable this way.

Limits, from the spec:

- 100 requests per minute per console
- 25 seconds per proxied request, then terminated
- 10 MB response body cap
- console firmware ≥ 5.0.3
- non-organization keys reach only consoles owned by the key's account; organization keys reach
  any console in the organization

## Getting the host id

```bash
curl -sS -H "X-API-KEY: $UBIQUITI_API_KEY" https://api.ui.com/v1/hosts \
  -o hosts.json
jq -r '.data[] | "\(.id)  \(.reportedState.name)  \(.reportedState.ip)"' hosts.json
```

The id looks like `AABBCCDDEEFF0000...:1234567890`. It contains a colon; quote it in shell
interpolation.

`GET /v1/hosts` also carries useful state without touching the console: `reportedState.wans`
(WAN interfaces, external IP, MAC), `reportedState.ipAddrs` (the console's own addresses),
`directConnectDomain`, firmware version, and `consolesOnSameLocalNetwork`.

## What Site Manager itself offers

Fifteen endpoints, complete list:

```
GET|POST|PUT|PATCH|DELETE  /v1/connector/consoles/{id}/*path
GET   /v1/devices
GET   /v1/hosts
GET   /v1/hosts/{id}
GET   /v1/isp-metrics/{type}
POST  /v1/isp-metrics/{type}/query
GET   /v1/sd-wan-configs
GET   /v1/sd-wan-configs/{id}
GET   /v1/sd-wan-configs/{id}/status
GET   /v1/sites
```

There is no networks, clients, firewall, or routing endpoint at this layer. Everything about the
configuration of a site comes through the connector.

`GET /v1/sites` is worth reading even so: its `statistics.counts` includes `lanConfiguration`
and `wanConfiguration`, which tell you how many networks exist before you fetch them, and
`ispInfo` names the actual ISP.
