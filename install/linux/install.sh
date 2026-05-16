#!/usr/bin/env bash
# MavizOS Linux dedicated node installer (idempotent where possible).
set -euo pipefail

INSTALL_ROOT="${MavizOS_INSTALL_ROOT:-/opt/mavizos}"
SOURCE_ROOT="${MavizOS_SOURCE_ROOT:-}"
MavizOS_USER="${MavizOS_USER:-MavizOS}"
ENABLE_API="${ENABLE_API:-1}"
ENABLE_AUTOLOGIN="${ENABLE_AUTOLOGIN:-0}"
ENABLE_SHELL_SERVICE="${ENABLE_SHELL_SERVICE:-0}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SOURCE_ROOT="${SOURCE_ROOT:-$REPO_ROOT}"

log() { printf '[*] %s\n' "$*"; }
ok() { printf '[OK] %s\n' "$*"; }
die() { printf '[ERROR] %s\n' "$*" >&2; exit 1; }

[[ "$(id -u)" -eq 0 ]] || die "Run as root: sudo $0"

get_version() {
  if [[ -f "${SOURCE_ROOT}/VERSION" ]]; then
    tr -d ' \r\n' < "${SOURCE_ROOT}/VERSION"
    return
  fi
  grep -E '^version\s*=' "${SOURCE_ROOT}/pyproject.toml" | head -1 | sed -E 's/.*"([^"]+)".*/\1/'
}

detect_pkg_manager() {
  if command -v apt-get &>/dev/null; then echo apt
  elif command -v dnf &>/dev/null; then echo dnf
  elif command -v yum &>/dev/null; then echo yum
  else echo unknown
  fi
}

install_deps() {
  local pm
  pm="$(detect_pkg_manager)"
  case "$pm" in
    apt)
      log "Installing packages (apt)..."
      export DEBIAN_FRONTEND=noninteractive
      apt-get update -qq
      apt-get install -y -qq python3 python3-venv python3-pip python3-dev rsync curl
      ;;
    dnf|yum)
      log "Installing packages ($pm)..."
      "$pm" install -y python3 python3-pip rsync curl
      ;;
    *)
      die "Unsupported package manager. Install python3 (>=3.11), python3-venv, pip, rsync manually."
      ;;
  esac
}

check_python() {
  local ver major minor
  ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  major="${ver%%.*}"
  minor="${ver#*.}"
  if [[ "$major" -lt 3 ]] || [[ "$major" -eq 3 && "$minor" -lt 11 ]]; then
    die "Python 3.11+ required (found $ver). Install python3.11 or newer."
  fi
  ok "Python $ver"
}

ensure_user() {
  if ! id "$MavizOS_USER" &>/dev/null; then
    log "Creating system user: $MavizOS_USER"
    useradd --system --home-dir "$INSTALL_ROOT" --shell /bin/bash "$MavizOS_USER"
  else
    ok "User exists: $MavizOS_USER"
  fi
}

sync_project() {
  log "Syncing ${SOURCE_ROOT} -> ${INSTALL_ROOT}"
  mkdir -p "$INSTALL_ROOT"
  rsync -a --delete \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '.pytest_cache' \
    --exclude 'dist' \
    --exclude 'build' \
    "${SOURCE_ROOT}/" "${INSTALL_ROOT}/"
}

install_venv() {
  local venv="${INSTALL_ROOT}/.venv"
  if [[ ! -x "${venv}/bin/python" ]]; then
    log "Creating virtual environment..."
    python3 -m venv "$venv"
  fi
  log "Installing MavizOS (editable)..."
  "${venv}/bin/pip" install --upgrade pip wheel setuptools
  "${venv}/bin/pip" install -e "${INSTALL_ROOT}"
}

setup_env() {
  if [[ -f "${INSTALL_ROOT}/.env.example" && ! -f "${INSTALL_ROOT}/.env" ]]; then
    cp "${INSTALL_ROOT}/.env.example" "${INSTALL_ROOT}/.env"
    ok "Created .env from .env.example"
  fi
  mkdir -p "${INSTALL_ROOT}/data" "${INSTALL_ROOT}/mavizos_fs"
}

install_systemd() {
  log "Installing systemd units..."
  install -m 0644 "${SCRIPT_DIR}/mavizos.service" /etc/systemd/system/mavizos.service
  if [[ "$ENABLE_SHELL_SERVICE" == "1" ]]; then
    cat > /etc/systemd/system/mavizos-shell@.service <<'UNIT'
[Unit]
Description=MavizOS interactive shell on %I
After=network-online.target

[Service]
Type=simple
User=mavizos
WorkingDirectory=/opt/mavizos
ExecStart=/opt/mavizos/.venv/bin/python -m mavizos
StandardInput=tty
StandardOutput=tty
TTYPath=/dev/%I
TTYReset=yes

[Install]
WantedBy=multi-user.target
UNIT
  fi
  if [[ "$ENABLE_AUTOLOGIN" == "1" ]]; then
    install -m 0644 "${SCRIPT_DIR}/mavizos-getty.service" /etc/systemd/system/mavizos-getty@tty1.service
    systemctl enable mavizos-getty@tty1.service
    ok "Enabled autologin on tty1 (MavizOS user)"
  fi
  systemctl daemon-reload
  if [[ "$ENABLE_API" == "1" ]]; then
    systemctl enable mavizos.service
    systemctl restart mavizos.service || systemctl start mavizos.service
    ok "mavizos.service enabled and started"
  fi
}

set_permissions() {
  chown -R "${MavizOS_USER}:${MavizOS_USER}" "$INSTALL_ROOT"
}

write_marker() {
  local version
  version="$(get_version)"
  cat > "${INSTALL_ROOT}/install/.installed-linux.json" <<EOF
{
  "version": "${version}",
  "installedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "installRoot": "${INSTALL_ROOT}",
  "user": "${MavizOS_USER}"
}
EOF
}

main() {
  local version
  version="$(get_version)"
  echo "========================================"
  echo " MavizOS Linux Installer v${version}"
  echo "========================================"
  echo ""
  echo "SAFETY: Host Linux distribution remains; MavizOS is installed under ${INSTALL_ROOT}."
  echo ""

  install_deps
  check_python
  ensure_user
  sync_project
  install_venv
  setup_env
  set_permissions
  install_systemd
  write_marker

  echo ""
  echo "Installation complete."
  echo "  Root:   ${INSTALL_ROOT}"
  echo "  API:    systemctl status MavizOS"
  echo "  Shell:  sudo -u ${MavizOS_USER} ${INSTALL_ROOT}/.venv/bin/python -m mavizos"
  echo "  Web:    http://localhost:8000/desktop"
  echo ""
  echo "Optional autologin: ENABLE_AUTOLOGIN=1 sudo $0"
  echo "Uninstall:          sudo install/linux/uninstall.sh"
}

main "$@"
