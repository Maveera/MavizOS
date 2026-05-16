#!/usr/bin/env bash
# Roll back MavizOS Linux installation.
set -euo pipefail

INSTALL_ROOT="${MavizOS_INSTALL_ROOT:-/opt/mavizos}"
MavizOS_USER="${MavizOS_USER:-MavizOS}"
REMOVE_DATA="${REMOVE_DATA:-0}"

log() { printf '[*] %s\n' "$*"; }

[[ "$(id -u)" -eq 0 ]] || { echo "Run as root: sudo $0" >&2; exit 1; }

systemctl stop mavizos.service 2>/dev/null || true
systemctl disable mavizos.service 2>/dev/null || true
systemctl stop 'mavizos-getty@tty1.service' 2>/dev/null || true
systemctl disable 'mavizos-getty@tty1.service' 2>/dev/null || true
systemctl stop 'mavizos-shell@tty1.service' 2>/dev/null || true
systemctl disable 'mavizos-shell@tty1.service' 2>/dev/null || true

rm -f /etc/systemd/system/mavizos.service
rm -f /etc/systemd/system/mavizos-getty@.service
rm -f /etc/systemd/system/mavizos-shell@.service
systemctl daemon-reload

rm -f "${INSTALL_ROOT}/install/.installed-linux.json"

if [[ "$REMOVE_DATA" == "1" ]]; then
  log "Removing ${INSTALL_ROOT}..."
  rm -rf "$INSTALL_ROOT"
else
  log "Preserved ${INSTALL_ROOT} (set REMOVE_DATA=1 to delete)"
fi

if id "$MavizOS_USER" &>/dev/null; then
  read -r -p "Remove system user ${MavizOS_USER}? [y/N] " ans
  if [[ "${ans,,}" == "y" ]]; then
    userdel "$MavizOS_USER" 2>/dev/null || true
    log "Removed user ${MavizOS_USER}"
  fi
fi

log "MavizOS Linux uninstall finished."
