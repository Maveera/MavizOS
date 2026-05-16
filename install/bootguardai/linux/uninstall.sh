#!/usr/bin/env bash
# BootGuardAI uninstall — removes /opt/bootguardai only
set -euo pipefail
INSTALL_ROOT="${BOOTGUARD_INSTALL_ROOT:-/opt/bootguardai}"

[[ "$(id -u)" -eq 0 ]] || { echo "Run as root"; exit 1; }

systemctl stop bootguardai.service 2>/dev/null || true
systemctl disable bootguardai.service 2>/dev/null || true
rm -f /etc/systemd/system/bootguardai.service
systemctl daemon-reload
rm -rf "$INSTALL_ROOT"
echo "[OK] BootGuardAI removed from $INSTALL_ROOT"
