#!/usr/bin/env bash
# unifi-query.sh — call a UniFi console API through the Site Manager connector.
#
# The connector forwards to http://127.0.0.1/proxy/<path> on the console, so any
# path the console's own APIs expose is reachable:
#
#   network/integration/v1/sites                     official, documented, writable
#   network/api/s/default/rest/networkconf           legacy; LAN/VLAN definitions
#   network/v2/api/site/default/trafficroutes        internal; policy-based routing
#
# Usage:
#   unifi-query.sh <path> [curl args...]
#   unifi-query.sh --hosts                    list consoles and their host ids
#   UNIFI_HOST_ID=<id> unifi-query.sh <path>  skip host lookup (saves a request)
#
# Requires: UBIQUITI_API_KEY in the environment, curl, jq.
#
# Writes the body to stdout and the HTTP status to stderr. The status is reported
# rather than swallowed, because a 403 here means "key lacks UniFi Applications
# scope" and a 404 means "no such path on the console" — two different problems
# that look identical if you only see an empty body.

set -euo pipefail

: "${UBIQUITI_API_KEY:?set UBIQUITI_API_KEY (create at unifi.ui.com, needs UniFi Applications scope)}"

API="https://api.ui.com"
tmp="$(mktemp)"
trap 'rm -f "${tmp}"' EXIT

usage() {
	sed -n '2,21p' "$0" >&2
	exit 64
}

# request <url> [curl args...] — fetch, print body, explain the status.
request() {
	local url="$1"
	shift
	local code
	code="$(curl -sS -m 30 -o "${tmp}" -w '%{http_code}' \
		-H "X-API-KEY: ${UBIQUITI_API_KEY}" \
		-H 'Accept: application/json' \
		"$@" "${url}")"
	echo "HTTP ${code}  ${url}" >&2
	cat "${tmp}"
	case "${code}" in
		2*) return 0 ;;
		401)
			echo "-> 401: use X-API-KEY (not bearer), or the key is invalid" >&2
			return 1
			;;
		403)
			echo "-> 403: either the key lacks UniFi Applications scope for this console," >&2
			echo "        or the first path segment is not an application the connector" >&2
			echo "        routes to (network, protect, innerspace). A typo there reads as" >&2
			echo "        a permission error; an unknown path inside a real application" >&2
			echo "        would have been a 404." >&2
			return 1
			;;
		404)
			echo "-> 404: no such path on the console; check the OpenAPI spec at" >&2
			echo "        https://developer.ui.com/network/<version>/openapi.json" >&2
			return 1
			;;
		*) return 1 ;;
	esac
}

# first_host_id — the console this account owns, or empty when there is none.
first_host_id() {
	local id
	curl -sS -m 30 -o "${tmp}" -H "X-API-KEY: ${UBIQUITI_API_KEY}" "${API}/v1/hosts"
	id="$(jq -r '.data[0].id // empty' "${tmp}")"
	printf '%s' "${id}"
}

if [[ "${1:-}" == "--hosts" ]]; then
	hosts="$(mktemp)"
	trap 'rm -f "${tmp}" "${hosts}"' EXIT
	request "${API}/v1/hosts" >"${hosts}"
	jq -r '.data[] | "\(.id)\n  name: \(.reportedState.name // "?")  ip: \(.reportedState.ip // "?")  fw: \(.reportedState.version // "?")"' "${hosts}"
	exit 0
fi

[[ $# -ge 1 ]] || usage

path="$1"
shift

host_id="${UNIFI_HOST_ID:-}"
if [[ -z "${host_id}" ]]; then
	host_id="$(first_host_id)"
	if [[ -z "${host_id}" ]]; then
		echo "no console found on this account" >&2
		exit 1
	fi
	echo "console: ${host_id}" >&2
fi

request "${API}/v1/connector/consoles/${host_id}/${path#/}" "$@"
