#!/bin/bash
# Setup xrdp on Debian/Ubuntu for RDP remote desktop.
# Run with: sudo bash scripts/setup_xrdp.sh

set -e
export DEBIAN_FRONTEND=noninteractive

echo "Installing xrdp and xorgxrdp..."
apt-get update
apt-get install -y xrdp xorgxrdp

echo "Adding xrdp to ssl-cert group (for certificate access)..."
adduser xrdp ssl-cert 2>/dev/null || true

echo "Enabling and starting xrdp..."
systemctl enable xrdp
systemctl enable xrdp-sesman
systemctl start xrdp
systemctl start xrdp-sesman

echo "Checking status..."
systemctl is-active xrdp xrdp-sesman

# Optional: open firewall (uncomment if you use ufw)
# ufw allow 3389/tcp
# ufw status

echo "Done. xrdp is listening on port 3389."
echo "Connect with an RDP client (e.g. Microsoft Remote Desktop, Remmina) to this machine's IP."
echo "Session: choose Xorg and log in with your local user."
