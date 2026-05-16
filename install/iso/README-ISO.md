# MavizOS Bootable ISO

Build a **live/install hybrid ISO** that boots directly into MavizOS (API + web desktop, optional shell).

> **Note:** The ISO is **not** committed to this repository (multi-GB artifact). You build it locally on **Linux** or **WSL2**.

## Output

```
dist/mavizos-os-<version>-amd64.iso
```

Example: `dist/mavizos-os-0.1.0-amd64.iso`

## Prerequisites

| Environment | Requirements |
|-------------|--------------|
| Linux | `live-build`, `debootstrap`, Docker (optional), root/sudo for loop devices |
| WSL2 | Same as Linux; enable systemd if using services inside WSL |
| Windows | WSL2 only — run `install/iso/build-iso.ps1` |

## Quick build (Docker — recommended)

```bash
cd /path/to/MavizOS
chmod +x install/iso/build-iso.sh
./install/iso/build-iso.sh
```

Uses `install/iso/Dockerfile.builder` when Docker is available.

## Native build (no Docker)

```bash
sudo apt install live-build debootstrap squashfs-tools xorriso
USE_DOCKER=0 ./install/iso/build-iso.sh
```

Build time: typically **30–90 minutes** depending on bandwidth and CPU.

## Windows (WSL2)

```powershell
# PowerShell (from repo root)
.\install\iso\build-iso.ps1
```

Or manually:

```powershell
wsl
cd /mnt/d/Agentic\ OS   # adjust drive letter
bash install/iso/build-iso.sh
```

## What the ISO contains

- Debian bookworm live base (amd64)
- Python 3 + MavizOS installed under `/opt/mavizos`
- `mavizos.service` enabled (API on port 8000)
- Autostart hint for web desktop (`http://127.0.0.1:8000/desktop`)

## Boot instructions

### VirtualBox

1. New VM → Linux / Debian 64-bit
2. Mount ISO as optical drive
3. Boot → open browser to `http://127.0.0.1:8000/desktop`

### VMware

Same as VirtualBox; enable EFI if the image was built with EFI support.

### Bare metal / USB

```bash
sudo dd if=dist/mavizos-os-0.1.0-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

Replace `/dev/sdX` with your USB device. **This overwrites the target disk.**

## Customization

| Path | Purpose |
|------|---------|
| `preseed/mavizos.seed` | Unattended Debian install reference |
| `auto/config` | live-build defaults |
| `chroot-hooks/99-mavizos.sh` | Installs MavizOS inside chroot |
| `Dockerfile.builder` | Reproducible builder image |

## Troubleshooting

- **`lb: command not found`** — Install `live-build` or use Docker (`USE_DOCKER=1`).
- **Permission denied on loop** — Run with Docker `--privileged` or as root on Linux.
- **WSL path issues** — Clone repo inside WSL filesystem (`~/MavizOS`) for faster builds.

## Security

- Live ISO default credentials (if install preseed used): see `preseed/mavizos.seed` — **change before production**.
- Demo mode is enabled via `.env.example`; disable for production deployments.
