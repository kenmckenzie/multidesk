#!/bin/sh
# Open firewall ports for Netmaker WireGuard listeners.
# Run on the VPN server: sudo ./netmaker-open-ports.sh

set -e
if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo"
  exit 1
fi

if command -v ufw >/dev/null 2>&1; then
  ufw allow 51821:51830/udp comment 'Netmaker WireGuard'
  ufw reload
  echo "Done (ufw). UDP 51821-51830 allowed."
elif command -v firewall-cmd >/dev/null 2>&1; then
  firewall-cmd --permanent --add-port=51821-51830/udp
  firewall-cmd --reload
  echo "Done (firewalld). UDP 51821-51830 allowed."
else
  echo "No ufw or firewalld found. Open UDP 51821-51830 manually."
  exit 1
fi
