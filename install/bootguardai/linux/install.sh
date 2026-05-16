#!/usr/bin/env bash
# BootGuardAI Linux installer — /opt/bootguardai (non-destructive)
set -euo pipefail

INSTALL_ROOT="${BOOTGUARD_INSTALL_ROOT:-/opt/bootguardai}"
BOOTGUARD_USER="${BOOTGUARD_USER:-bootguardai}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SOURCE_ROOT="${BOOTGUARD_SOURCE_ROOT:-$REPO_ROOT}"

log() { printf '[*] %s\n' "$*"; }
die() { printf '[ERROR] %s\n' "$*" >&2; exit 1; }

[[ "$(id -u)" -eq 0 ]] || die "Run as root: sudo $0"
log "BootGuardAI installer — non-destructive; does not wipe the root filesystem or modify bootloaders"

if command -v apt-get &>/dev/null; then
  apt-get update -qq
  apt-get install -y -qq python3 python3-venv python3-pip rsync
fi

python3 -c 'import sys; assert sys.version_info >= (3, 11)' || die "Python 3.11+ required"

id "$BOOTGUARD_USER" &>/dev/null || useradd --system --home-dir "$INSTALL_ROOT" --shell /bin/bash "$BOOTGUARD_USER"

log "Syncing to $INSTALL_ROOT"
rsync -a --delete \
  --exclude '.git' --exclude '.venv' --exclude '__pycache__' \
  "$SOURCE_ROOT/" "$INSTALL_ROOT/"

python3 -m venv "$INSTALL_ROOT/.venv"
"$INSTALL_ROOT/.venv/bin/pip" install --upgrade pip wheel setuptools
"$INSTALL_ROOT/.venv/bin/pip" install -e "$INSTALL_ROOT"

chown -R "$BOOTGUARD_USER:$BOOTGUARD_USER" "$INSTALL_ROOT"
install -m 644 "$SCRIPT_DIR/bootguardai.service" /etc/systemd/system/bootguardai.service
systemctl daemon-reload
systemctl enable bootguardai.service
log "Enable API: systemctl start bootguardai"
log "[OK] BootGuardAI installed to $INSTALL_ROOT"
