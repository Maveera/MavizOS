#!/bin/bash
# Chroot hook: install BootGuardAI to /opt/bootguardai
set -e
INSTALL=/opt/bootguardai
mkdir -p "$INSTALL"
if [[ -d /build ]]; then
  rsync -a --exclude .git /build/ "$INSTALL/"
  python3 -m venv "$INSTALL/.venv"
  "$INSTALL/.venv/bin/pip" install -e "$INSTALL"
fi
echo "[OK] BootGuardAI staged in chroot at $INSTALL"
