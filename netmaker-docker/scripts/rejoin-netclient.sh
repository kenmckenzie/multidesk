#!/bin/bash
# Add this server to a Netmaker network (or re-sync membership).
# Uses the Netmaker API when the host is already enrolled — no enrollment token needed.
# Run: sudo ./scripts/rejoin-netclient.sh [network]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../netmaker.env"
API_URL="${NETMAKER_API_URL:-https://api.vpn.multisaas.co.za}"
NETWORK="${1:-${NETMAKER_NETWORK:-multisaas}}"
GATEWAY_HOST_ID="${NETMAKER_GATEWAY_HOST_ID:-ebc22300-c17a-4515-b0f4-fd008d6dd8a9}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo $0 [network]"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE"
  exit 1
fi

MASTER_KEY="$(grep '^MASTER_KEY=' "$ENV_FILE" | cut -d= -f2-)"
if [ -z "$MASTER_KEY" ]; then
  echo "MASTER_KEY not set in $ENV_FILE"
  exit 1
fi

if ! command -v netclient >/dev/null 2>&1; then
  echo "Installing netclient binary..."
  curl -sL "https://github.com/gravitl/netclient/releases/download/v1.6.0/netclient-linux-amd64" \
    -o /usr/local/bin/netclient
  chmod +x /usr/local/bin/netclient
fi

echo "Adding host to network: $NETWORK"
RESPONSE="$(
  curl -sk -w "\n%{http_code}" -X POST \
    -H "Authorization: Bearer $MASTER_KEY" \
    -H "Content-Type: application/json" \
    "$API_URL/api/hosts/${GATEWAY_HOST_ID}/networks/${NETWORK}" \
    -d '{}'
)"
HTTP_CODE="${RESPONSE##*$'\n'}"
BODY="${RESPONSE%$'\n'*}"

if [ "$HTTP_CODE" -ge 400 ] && ! echo "$BODY" | grep -qi "already in network"; then
  echo "Failed to add host to network ($HTTP_CODE): $BODY"
  exit 1
fi

echo "Installing netclient daemon (if needed)..."
netclient install || true

echo "Enabling netclient service..."
systemctl enable --now netclient 2>/dev/null || true

echo "Waiting for netclient to sync..."
for _ in $(seq 1 15); do
  if netclient list 2>/dev/null | grep -q "$NETWORK"; then
    break
  fi
  sleep 2
done

echo
echo "=== Status ==="
netclient list || true
echo
wg show 2>/dev/null || echo "(wg: no interface yet — wait a few seconds and run: sudo wg show)"
ip -br addr show netmaker 2>/dev/null || true
echo
echo "Done. Run ensure-network-gateways.sh to enable gateway on this network."
