#!/usr/bin/env bash
# Ensure the Rustdesk server is gateway on every Netmaker network and assign
# existing NAT clients to relay through it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/../netmaker.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

export MASTER_KEY
export NETMAKER_API_URL="${NETMAKER_API_URL:-https://api.vpn.multisaas.co.za}"
export NETMAKER_GATEWAY_HOST_ID="${NETMAKER_GATEWAY_HOST_ID:-ebc22300-c17a-4515-b0f4-fd008d6dd8a9}"

python3 <<'PY'
import json
import os
import urllib.error
import urllib.request

api_url = os.environ["NETMAKER_API_URL"].rstrip("/")
master_key = os.environ["MASTER_KEY"]
gateway_host = os.environ["NETMAKER_GATEWAY_HOST_ID"]
headers = {"Authorization": f"Bearer {master_key}"}


def request(method: str, path: str, body: dict | None = None):
    data = None
    req_headers = dict(headers)
    if body is not None:
        data = json.dumps(body).encode()
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{api_url}{path}", data=data, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}


networks = request("GET", "/api/networks")
nodes = request("GET", "/api/nodes")

for network in networks:
    netid = network["netid"]
    print(f"== Network: {netid} ==")

    host_node = next(
        (n for n in nodes if n.get("network") == netid and n.get("hostid") == gateway_host),
        None,
    )
    if not host_node:
        print(f"  Joining gateway host to {netid} via API")
        try:
            request(
                "POST",
                f"/api/hosts/{gateway_host}/networks/{netid}",
                {},
            )
        except urllib.error.HTTPError as err:
            body = err.read().decode("utf-8", errors="replace")
            if "already in network" not in body.lower():
                raise
        nodes = request("GET", "/api/nodes")
        host_node = next(
            (n for n in nodes if n.get("network") == netid and n.get("hostid") == gateway_host),
            None,
        )
    if not host_node:
        print(f"  Could not join gateway host to {netid}")
        continue

    gw_id = host_node["id"]
    if not host_node.get("is_gw"):
        print(f"  Creating gateway on node {gw_id}")
        result = request("POST", f"/api/nodes/{netid}/{gw_id}/gateway", {})
        response = result.get("Response") if isinstance(result, dict) else None
        if isinstance(response, dict) and response.get("is_gw"):
            host_node = response
    else:
        print(f"  Gateway already active on node {gw_id}")

    nodes = request("GET", "/api/nodes")
    assigned = 0
    for node in nodes:
        if node.get("network") != netid:
            continue
        if node.get("id") == gw_id or node.get("is_gw"):
            continue
        relayed_by = (node.get("relayedby") or "").strip()
        if node.get("isrelayed") and relayed_by == gw_id:
            continue
        request(
            "POST",
            f"/api/nodes/{netid}/{node['id']}/gateway/assign?gw_id={gw_id}&auto_assign_gw=true",
        )
        assigned += 1

    print(f"  Assigned {assigned} unrelayed node(s) to gateway")

print("Done.")
PY

echo
if [ "$(id -u)" -eq 0 ]; then
  "$SCRIPT_DIR/../../rustdesk-api-docker/scripts/sync-netclient.sh" || true
else
  echo "Run sync-netclient.sh as root if new networks were added."
fi
