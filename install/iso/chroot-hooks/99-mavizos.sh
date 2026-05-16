#!/bin/bash
# live-build chroot hook: install MavizOS inside the live image rootfs.
set -euo pipefail

CHROOT="${1:-}"
if [[ -z "$CHROOT" || ! -d "$CHROOT" ]]; then
  echo "Usage: 99-mavizos.sh <chroot-path>" >&2
  exit 1
fi

SRC="${MavizOS_SOURCE:-/src}"
INSTALL="/opt/mavizos"

echo "[MavizOS] Installing into chroot: $CHROOT"

if [[ ! -d "$SRC/MavizOS" ]]; then
  echo "[MavizOS] ERROR: source tree not mounted at $SRC" >&2
  exit 1
fi

chroot "$CHROOT" bash -c "
  set -euo pipefail
  apt-get update -qq
  apt-get install -y -qq python3 python3-venv python3-pip sudo curl
  useradd --system --create-home --shell /bin/bash MavizOS || true
  mkdir -p '$INSTALL'
"

rsync -a --exclude '.git' --exclude '.venv' --exclude '__pycache__' \
  "${SRC}/" "${CHROOT}${INSTALL}/"

chroot "$CHROOT" bash -c "
  set -euo pipefail
  python3 -m venv '${INSTALL}/.venv'
  '${INSTALL}/.venv/bin/pip' install --upgrade pip wheel setuptools
  '${INSTALL}/.venv/bin/pip' install -e '${INSTALL}'
  cp -n '${INSTALL}/.env.example' '${INSTALL}/.env' 2>/dev/null || true
  chown -R MavizOS:MavizOS '${INSTALL}'
"

# systemd service for live session (starts on boot inside live environment)
cat > "${CHROOT}/etc/systemd/system/mavizos.service" <<'UNIT'
[Unit]
Description=MavizOS API (live)
After=network.target

[Service]
Type=simple
User=mavizos
WorkingDirectory=/opt/mavizos
ExecStart=/opt/mavizos/.venv/bin/mavizos serve
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

chroot "$CHROOT" systemctl enable mavizos.service || true

# Autostart script for live user session
mkdir -p "${CHROOT}/etc/skel/.config/autostart"
cat > "${CHROOT}/etc/skel/.config/autostart/MavizOS-desktop.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=MavizOS Web Desktop
Exec=xdg-open http://127.0.0.1:8000/desktop
X-GNOME-Autostart-enabled=true
DESKTOP

echo "[MavizOS] Chroot install complete."
