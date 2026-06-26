#!/bin/sh
# Wait for Netmaker DNS to propagate globally, obtain TLS certs, and verify HTTPS.
# Run: ./scripts/wait-for-netmaker-dns.sh

set -e
HOSTS="dashboard.vpn.multisaas.co.za api.vpn.multisaas.co.za broker.vpn.multisaas.co.za"
EXPECTED_IP="${NETMAKER_EXPECTED_IP:-102.207.62.194}"
CADDY_DIR="${CADDY_DIR:-$HOME/multidesk/rustdesk-api-docker}"
AUTH_NS="${NETMAKER_AUTH_NS:-ns1.dns-h.com}"
PUBLIC_RESOLVERS="8.8.8.8 1.1.1.1"
LOG="$HOME/multidesk/netmaker-docker/scripts/wait-for-netmaker-dns.log"

host_ip() {
  dig +short "$1" A @"$2" 2>/dev/null | head -1
}

check_resolver() {
  resolver=$1
  for host in $HOSTS; do
    ip=$(host_ip "$host" "$resolver")
    if [ "$ip" != "$EXPECTED_IP" ]; then
      echo "  $resolver: $host -> ${ip:-<none>}"
      return 1
    fi
  done
  return 0
}

check_public_dns() {
  ok=0
  for resolver in $PUBLIC_RESOLVERS; do
    if check_resolver "$resolver"; then
      ok=$((ok + 1))
    fi
  done
  [ "$ok" -eq 2 ]
}

check_https() {
  code=$(curl -sk -o /dev/null -w "%{http_code}" "https://dashboard.vpn.multisaas.co.za/" 2>/dev/null) || code=000
  api=$(curl -sk -o /dev/null -w "%{http_code}" "https://api.vpn.multisaas.co.za/api/server/health" 2>/dev/null) || api=000
  echo "HTTPS dashboard=$code api=$api"
  [ "$code" != "000" ] && [ -n "$code" ] && [ "$api" != "000" ] && [ -n "$api" ]
}

echo "=== Netmaker DNS/HTTPS watch started $(date -Is) ==="

echo "Step 1: waiting for authoritative DNS ($AUTH_NS)..."
TRIES=0
until check_resolver "$AUTH_NS"; do
  TRIES=$((TRIES + 1))
  [ "$TRIES" -ge 60 ] && { echo "Timed out on authoritative DNS."; exit 1; }
  sleep 30
done
echo "Authoritative DNS OK."

echo "Step 2: waiting for global propagation (8.8.8.8 + 1.1.1.1)..."
TRIES=0
until check_public_dns; do
  TRIES=$((TRIES + 1))
  [ "$TRIES" -ge 120 ] && { echo "Timed out on public DNS propagation."; exit 1; }
  echo "public DNS not ready yet (try $TRIES)..."
  sleep 30
done
echo "Public DNS OK on Google and Cloudflare."

echo "Step 3: restarting Caddy..."
cd "$CADDY_DIR"
docker compose restart caddy

echo "Step 4: waiting for HTTPS certificates..."
TRIES=0
until check_https; do
  TRIES=$((TRIES + 1))
  if [ "$TRIES" -ge 60 ]; then
    echo "Timed out waiting for HTTPS."
    exit 1
  fi
  if [ $((TRIES % 6)) -eq 0 ]; then
    echo "Retrying Caddy restart..."
    docker compose restart caddy
  fi
  sleep 30
done

echo ""
echo "=== Netmaker is live ==="
echo "Dashboard: https://dashboard.vpn.multisaas.co.za"
echo "API:       https://api.vpn.multisaas.co.za"
echo "Login key: MASTER_KEY in ~/multidesk/netmaker-docker/netmaker.env"
echo "Finished $(date -Is)"
