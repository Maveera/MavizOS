#!/usr/bin/env bash
# Build bootable MavizOS live ISO (Linux or WSL2 required).
# Output: dist/mavizos-os-<version>-amd64.iso
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"
BUILD_DIR="${REPO_ROOT}/.iso-build"
USE_DOCKER="${USE_DOCKER:-auto}"

get_version() {
  if [[ -f "${REPO_ROOT}/VERSION" ]]; then
    tr -d ' \r\n' < "${REPO_ROOT}/VERSION"
  else
    grep -E '^version\s*=' "${REPO_ROOT}/pyproject.toml" | head -1 | sed -E 's/.*"([^"]+)".*/\1/'
  fi
}

log() { printf '[*] %s\n' "$*"; }
die() { printf '[ERROR] %s\n' "$*" >&2; exit 1; }

[[ "$(uname -s)" == "Linux" ]] || die "ISO build requires Linux or WSL2. On Windows, use: wsl bash install/iso/build-iso.sh"

VERSION="$(get_version)"
ISO_NAME="mavizos-os-${VERSION}-amd64.iso"
OUTPUT_ISO="${DIST_DIR}/${ISO_NAME}"

mkdir -p "$DIST_DIR"

docker_available() {
  command -v docker &>/dev/null && docker info &>/dev/null 2>&1
}

build_with_docker() {
  log "Building ISO via Docker (recommended)..."
  local image="MavizOS-iso-builder"
  docker build -t "$image" -f "${SCRIPT_DIR}/Dockerfile.builder" "${SCRIPT_DIR}"

  rm -rf "$BUILD_DIR"
  mkdir -p "$BUILD_DIR"

  docker run --rm --privileged \
    -v "${REPO_ROOT}:/src:ro" \
    -v "${BUILD_DIR}:/work" \
    -v "${DIST_DIR}:/dist" \
    -e MavizOS_VERSION="$VERSION" \
    -e MavizOS_SOURCE=/src \
    "$image" \
    /src/install/iso/build-iso.sh --internal

  if [[ -f "${BUILD_DIR}/live-image-amd64.hybrid.iso" ]]; then
    cp "${BUILD_DIR}/live-image-amd64.hybrid.iso" "$OUTPUT_ISO"
  elif [[ -f "/dist/${ISO_NAME}" ]]; then
    ok_path="/dist/${ISO_NAME}"
    :
  else
    # build-iso internal may have written directly
    find "$BUILD_DIR" -name '*.iso' -type f | head -1 | while read -r iso; do
      cp "$iso" "$OUTPUT_ISO"
    done
  fi

  [[ -f "$OUTPUT_ISO" ]] || die "ISO not produced; see ${BUILD_DIR} logs"
  log "ISO written: $OUTPUT_ISO"
}

build_native() {
  log "Building ISO with native live-build..."
  command -v lb &>/dev/null || die "live-build not installed. apt install live-build OR set USE_DOCKER=1"

  rm -rf "$BUILD_DIR"
  mkdir -p "$BUILD_DIR"
  cd "$BUILD_DIR"

  export MavizOS_SOURCE="$REPO_ROOT"
  cp -r "${SCRIPT_DIR}/auto" ./config 2>/dev/null || true

  # Initialize live-build
  lb config \
    --architectures amd64 \
    --distribution bookworm \
    --linux-flavours amd64 \
    --archive-areas "main contrib non-free non-free-firmware" \
    --debian-installer false \
    --iso-application "MavizOS AI SOC OS" \
    --iso-volume "MavizOS" \
    --memtest none \
    --bootappend-live "boot=live components quiet splash"

  mkdir -p config/hooks/live
  cp "${SCRIPT_DIR}/chroot-hooks/99-mavizos.sh" config/hooks/live/0100-mavizos.hook.chroot
  chmod +x config/hooks/live/0100-mavizos.hook.chroot

  # Inject source into chroot during hook
  cat > config/hooks/live/0050-mount-src.hook.chroot <<HOOK
#!/bin/bash
mkdir -p /src
# Source is copied by 99-MavizOS hook via build env
HOOK
  chmod +x config/hooks/live/0050-mount-src.hook.chroot

  # Pre-copy source for chroot hook
  mkdir -p cache/rootfs-src
  rsync -a --exclude '.git' --exclude '.venv' --exclude 'dist' "${REPO_ROOT}/" cache/rootfs-src/

  sed -i "s|MavizOS_SOURCE:-/src|MavizOS_SOURCE:-/rootfs-src|g" config/hooks/live/0100-mavizos.hook.chroot 2>/dev/null || true

  # Patch hook to use cached source path inside build
  cat > config/hooks/live/0100-mavizos.hook.chroot <<'HOOK'
#!/bin/bash
set -e
SRC="/rootfs-src"
if [[ -d /rootfs-src ]]; then
  export MavizOS_SOURCE="/rootfs-src"
fi
HOOK
  cat "${SCRIPT_DIR}/chroot-hooks/99-mavizos.sh" >> config/hooks/live/0100-mavizos.hook.chroot
  chmod +x config/hooks/live/0100-mavizos.hook.chroot

  # Place source where hook expects it
  mkdir -p chroot/rootfs-src
  rsync -a cache/rootfs-src/ chroot/rootfs-src/ 2>/dev/null || true

  log "Running lb build (this may take 30-60+ minutes)..."
  lb build 2>&1 | tee "${BUILD_DIR}/build.log"

  local built
  built="$(find . -maxdepth 2 -name 'live-image*.iso' -type f | head -1)"
  [[ -n "$built" ]] || die "lb build did not produce an ISO"
  cp "$built" "$OUTPUT_ISO"
  log "ISO written: $OUTPUT_ISO"
}

build_internal() {
  # Runs inside Docker builder container
  apt-get update -qq
  apt-get install -y -qq live-build debootstrap squashfs-tools xorriso rsync python3 python3-venv python3-pip

  WORK=/work
  SRC="${MavizOS_SOURCE:-/src}"
  rm -rf "$WORK"
  mkdir -p "$WORK"
  cd "$WORK"

  lb config \
    --architectures amd64 \
    --distribution bookworm \
    --linux-flavours amd64 \
    --debian-installer false \
    --iso-application "MavizOS AI SOC OS" \
    --iso-volume "MavizOS" \
    --memtest none

  mkdir -p config/hooks/live
  cp /build/chroot-hooks/99-mavizos.sh config/hooks/live/0100-mavizos.hook.chroot
  chmod +x config/hooks/live/0100-mavizos.hook.chroot

  mkdir -p config/includes.chroot/opt/mavizos-src
  rsync -a --exclude '.git' --exclude '.venv' --exclude 'dist' "${SRC}/" config/includes.chroot/opt/mavizos-src/

  # Rewrite hook to use included source
  sed -i 's|MavizOS_SOURCE:-/src|MavizOS_SOURCE:-/opt/mavizos-src|g' config/hooks/live/0100-mavizos.hook.chroot

  lb build

  ISO="$(find . -maxdepth 2 -name 'live-image*.iso' -type f | head -1)"
  if [[ -n "$ISO" ]]; then
    cp "$ISO" "/dist/mavizos-os-${MavizOS_VERSION:-0.1.0}-amd64.iso"
  fi
}

# --- entry ---
if [[ "${1:-}" == "--internal" ]]; then
  build_internal
  exit 0
fi

VERSION="$(get_version)"
log "MavizOS ISO build v${VERSION}"

if [[ "$USE_DOCKER" == "auto" ]]; then
  if docker_available; then USE_DOCKER=1; else USE_DOCKER=0; fi
fi

if [[ "$USE_DOCKER" == "1" ]]; then
  build_with_docker
else
  build_native
fi

ls -lh "$OUTPUT_ISO"
echo ""
echo "Boot the ISO in VirtualBox/VMware or write to USB:"
echo "  sudo dd if=${OUTPUT_ISO} of=/dev/sdX bs=4M status=progress conv=fsync"
