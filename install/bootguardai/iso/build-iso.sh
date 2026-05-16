#!/usr/bin/env bash
# Build BootGuardAI live ISO (requires live-build on Debian/Ubuntu host)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
VERSION="$(tr -d ' \r\n' < "${REPO_ROOT}/bootguardai/VERSION" 2>/dev/null || echo 0.1.0)"
DIST="${REPO_ROOT}/dist"
OUT="${DIST}/bootguardai-os-${VERSION}.iso"

mkdir -p "$DIST"
echo "[*] BootGuardAI ISO build — output: $OUT"
echo "[*] Use Dockerfile.builder for reproducible builds:"
echo "    docker build -f install/bootguardai/iso/Dockerfile.builder -t bootguardai-iso ."
echo "[*] This script is a stub wrapper; full lb build runs in CI/Docker."

if command -v lb &>/dev/null; then
  echo "[*] live-build detected — configure preseed and run lb build manually per README-ISO.md"
else
  echo "[WARN] live-build not installed. See README-ISO.md"
  touch "${OUT}.placeholder"
  echo "placeholder" > "${OUT}.placeholder"
fi
