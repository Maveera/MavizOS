# SentinelOS ISO builder image (run on Linux or WSL2 with Docker).
# Build:  docker build -t sentinelos-iso-builder -f install/iso/Dockerfile.builder install/iso
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LB_BUILDING=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    isolinux \
    syslinux-utils \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
  python3 \
  python3-venv \
  python3-pip \
  rsync \
  git \
  ca-certificates \
  curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY auto/ /build/auto/
COPY preseed/ /build/preseed/
COPY chroot-hooks/ /build/chroot-hooks/

ENTRYPOINT ["/bin/bash"]
