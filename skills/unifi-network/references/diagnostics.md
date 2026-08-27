# Diagnosing reachability on a UniFi network

A user rarely opens with "query my firewall policies". They open with "my server is down" or
"this site won't load". The job is to find the layer that is actually broken before touching any
API, and then to confirm the cause in configuration rather than inferring it.

## Read the failure mode first

| Symptom            | Layer                     | What it rules out                                |
| ------------------ | ------------------------- | ------------------------------------------------ |
| Timeout            | network path              | the service is irrelevant; packets never arrived |
| Connection refused | host reached, port closed | routing and firewall are fine                    |
| TLS error          | TCP fine                  | certificate, SNI, or ALPN                        |
| HTTP 502/504       | proxy up, backend down    | network is fine                                  |
| HTTP 404           | everything up             | a routing/matching rule, not connectivity        |

If the symptom is a timeout, inspecting the service, its logs, its container, or its certificate
is wasted effort. Say so early — users often arrive convinced the application is broken.

## Establish where it works before asking why it fails

One measurement is not a diagnosis. Build a matrix; the *pattern* names the cause:

```
from host A on net 1  -> target        works
from host B on net 2  -> target        times out
from target           -> host B        works          <- asymmetry: stateful filter
from host B           -> net 2 gateway works
from host B           -> any other host on net 1  times out   <- whole-segment block
```

Two patterns and what they mean:

**Asymmetric** (A→B fails, B→A works) points at a stateful firewall rule filtering only new
connections. It is not a routing problem: routing is symmetric by nature, so a route that
carries packets one way carries them the other.

**Segment-wide** (every host on the target network fails, but the gateway itself answers) points
at a policy between two networks rather than anything host-specific.

## Three traps specific to UniFi

**A gateway that answers is not a gateway that routes.** A router accepts packets addressed to
its own IP on any interface, before any inter-network policy applies. So `ping 10.30.0.1` from
another VLAN can succeed while every host behind it is blocked. Never conclude "routing works"
from reaching the gateway — test a host.

**One console holds many gateway addresses.** A UDM serving several networks answers on
`10.30.0.1` and `10.20.0.1` and looks like two routers. Check the MAC: consecutive MACs
(`...:aa:01`, `...:aa:02`) are interfaces of one device, and the TLS certificate on the UI is
`CN=unifi.local` with the page title `UniFi OS`. `reportedState.ipAddrs` in `GET /v1/hosts`
lists the console's own addresses. Concluding "there is a second router" sends the whole
investigation into an imaginary double-NAT.

**Both networks in the same zone does not mean traffic flows.** Zone-based firewalling allows
intra-zone traffic by default, so two networks in `Internal` look open — until a user-defined
policy with an explicit source and destination subnet blocks them. Read the actual policy list;
zone membership alone proves nothing.

## The read sequence

Once the pattern points at the gateway, four calls settle it. All through the connector:

1. `network/api/s/default/rest/networkconf` — what networks exist, their subnets, VLAN ids, and
   `firewall_zone_id`. This is the map; nothing else makes sense without it.
2. `network/v2/api/site/default/firewall/zone` — zone names and how many networks each holds.
3. `network/integration/v1/sites/{siteId}/firewall/policies` — filter to
   `metadata.origin == "USER_DEFINED"` and `action.type != "ALLOW"`. A site has dozens of
   predefined rules; the human-written ones are usually a handful and the culprit is nearly
   always among them.
4. `network/v2/api/site/default/trafficroutes` — only if no policy explains it. An enabled route
   sending a network's traffic into a VPN client tunnel makes traffic disappear in a way that
   looks exactly like a firewall drop.

Match each candidate rule against the measured matrix before declaring it the cause. A rule that
blocks 10.20.0.0/24 → 10.30.0.0/24 explains a segment-wide failure; if the reported symptom is a single
port on a single host, keep looking.

## Worked example

Symptom: a browser on 10.20.0.50 times out on `https://app.example.com`, which resolves to
the site's public IP. The service is a container behind a reverse proxy on 10.30.0.10.

Measured:

```
container healthy, serving 200 locally
proxy answers 200 for that hostname on the host itself
10.20.0.50 -> public IP     timeout on 443 AND on 80
10.20.0.50 -> 10.30.0.1     200
10.20.0.50 -> 10.30.0.10    timeout (ICMP and TCP)
10.20.0.50 -> 10.30.0.11    timeout
10.30.0.10 -> 10.20.0.50    0% packet loss
external scanners           reach port 80 fine
```

Reasoning: port 80 failing alongside 443 rules out TLS and the proxy. External traffic arriving
rules out the WAN path and the service. The gateway answering while every host behind it does
not is the segment-wide pattern. Reachability working in reverse is the asymmetry pattern. Both
together: a stateful rule filtering new connections from 10.20.0.0/24 to 10.30.0.0/24.

Confirmed in configuration:

```
name                   Block Default to Servers
action                 BLOCK
index                  10000
source                 10.20.0.0/24   zone Internal
destination            10.30.0.0/24   zone Internal
connectionStateFilter  ["NEW"]
metadata.origin        USER_DEFINED
```

`["NEW"]` is why the reverse direction worked. The public-IP failure is the same rule: hairpin
NAT translates the destination to 10.30.0.10, and the translated packet meets the block.

The fix is a judgement call for the user, not a default. The rule is deliberate segmentation with
a description explaining its intent, so disabling it discards something they wanted. An allow
policy scoped to the single host and the two ports needed, ordered ahead of the block, keeps the
segmentation and opens exactly what is required.

## Before proposing a fix

Reachability problems have several valid fixes at different layers, and the right one depends on
what the user is protecting:

- **Firewall exception** — narrowest, keeps existing segmentation, needs ordering to be correct
- **Split-horizon DNS** — avoids hairpin entirely, but needs a name-by-name decision, which is
  bookkeeping the user may not want
- **Overlay network** (Tailscale and similar) — works from anywhere, not just this network, but
  only for devices on the overlay
- **Static route on one host** — fastest, and wrong: it fixes one machine, breaks when an IP
  changes, and leaves every other client on that segment broken

Prefer the layer where the fault actually is. If every client on a segment has the problem, a
per-machine fix is the wrong altitude no matter how quickly it works.
