# Endpoints that work, by generation

All paths below are the `{path}` part of a connector call:

```
https://api.ui.com/v1/connector/consoles/{hostId}/{path}
```

They also work locally as `https://<console-ip>/proxy/{path}` with a local Network key.

## Integration API — official, documented, safe to write through

Base: `network/integration/v1/`. Described by
`https://developer.ui.com/network/{version}/openapi.json` (44 paths at v10.4.57). Site id here is
a **UUID**, from `network/integration/v1/sites`.

```
GET    sites
GET    sites/{siteId}/clients
GET    sites/{siteId}/devices
GET    sites/{siteId}/firewall/zones
POST   sites/{siteId}/firewall/zones
GET    sites/{siteId}/firewall/zones/{firewallZoneId}
PUT    sites/{siteId}/firewall/zones/{firewallZoneId}
DELETE sites/{siteId}/firewall/zones/{firewallZoneId}
GET    sites/{siteId}/firewall/policies
POST   sites/{siteId}/firewall/policies
GET    sites/{siteId}/firewall/policies/{firewallPolicyId}
PUT    sites/{siteId}/firewall/policies/{firewallPolicyId}
PATCH  sites/{siteId}/firewall/policies/{firewallPolicyId}
DELETE sites/{siteId}/firewall/policies/{firewallPolicyId}
GET    sites/{siteId}/firewall/policies/ordering
PUT    sites/{siteId}/firewall/policies/ordering
GET    sites/{siteId}/dns/policies
POST   sites/{siteId}/dns/policies
```

Fetch the spec for the rest and for exact request bodies. Do not reconstruct a body from a GET
response — several fields are read-only and rejected on write.

### Firewall policy shape

A policy from the integration API looks like this. The nesting is where mistakes happen, so copy
the shape rather than inventing it:

```json
{
  "id": "a1b2c3d4-1111-4111-8111-aaaaaaaaaaaa",
  "enabled": true,
  "name": "Block Default to Servers",
  "description": "...",
  "index": 10000,
  "action": { "type": "BLOCK" },
  "source": {
    "zoneId": "b2c3d4e5-2222-4222-8222-bbbbbbbbbbbb",
    "trafficFilter": {
      "type": "IP_ADDRESS",
      "ipAddressFilter": {
        "type": "IP_ADDRESSES",
        "matchOpposite": false,
        "items": [{ "type": "SUBNET", "value": "10.20.0.0/24" }]
      }
    }
  },
  "destination": { "...same shape..." },
  "ipProtocolScope": { "ipVersion": "IPV4" },
  "connectionStateFilter": ["NEW"],
  "loggingEnabled": false,
  "metadata": { "origin": "USER_DEFINED" }
}
```

`metadata.origin` separates `USER_DEFINED` rules from `PREDEFINED` ones. A site typically has
dozens of predefined zone-pair rules that are noise; filter on origin when hunting for the rule
a human wrote.

`connectionStateFilter` is the field that explains one-directional symptoms. `["NEW"]` blocks
only connection initiation, so established and related return traffic still flows — meaning A
cannot reach B while B reaches A perfectly. See `diagnostics.md`.

`index` is the evaluation order. Lower runs first.

## Legacy controller API — read, and only for what integration lacks

Base: `network/api/s/{site}/rest/`. Site id is the **short name**, usually `default`.

```
networkconf     LAN/VLAN/WAN/VPN definitions — subnets, VLAN ids, purpose, firewall zone
routing         user-defined static routes
firewallrule    pre-zone-based firewall rules (empty on modern zone-based sites)
portforward     port forwards
```

`networkconf` is the one you will actually need: it is the only place that maps a network name to
its subnet, VLAN id, and `firewall_zone_id`. Fields worth reading per network: `name`, `purpose`
(`corporate` / `wan` / `remote-user-vpn` / `vpn-client` / `guest`), `ip_subnet`, `vlan`,
`enabled`, `firewall_zone_id`, `internet_access_enabled`.

Note `purpose=vpn-client` entries: those are outbound VPN tunnels to a commercial provider. Their
presence means policy-based routing may be in play, which is a separate way for traffic to
vanish. Cross-check against traffic routes below.

## Internal v2 API — read only, unstable

Base: `network/v2/api/site/{site}/`. Site id is the short name.

```
trafficroutes        policy-based routing — which traffic goes down which VPN
firewall-policies    the UI's own view of policies
firewall/zone        zone definitions with member network counts
```

`trafficroutes` has no integration equivalent and is the only way to see policy-based routing.
Each entry has `enabled`, `description`, `network_id` (the VPN client network it routes into),
and a `matching_target` of `INTERNET`, `DOMAIN`, `IP`, or `REGION`.

`firewall/zone` is a fast way to see zone membership counts before pulling the full policy list:

```
Internal  3 networks     External 8      Gateway 0
Vpn       1 network      Hotspot  1      Dmz     0
```

## Careful with `/v1/devices`

`GET https://api.ui.com/v1/devices` lists **adopted Ubiquiti hardware only** — gateways,
switches, access points, cameras. It is not a network inventory. Clients (servers, laptops,
phones, anything not made by Ubiquiti) never appear.

Treating this list as "what is on the network" produces confidently wrong conclusions. For actual
clients use `network/integration/v1/sites/{siteId}/clients`.
