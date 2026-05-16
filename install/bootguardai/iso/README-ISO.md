# BootGuardAI ISO Build

Builds `dist/bootguardai-os-<version>.iso` for a dedicated boot-analysis appliance.

## Requirements

- Debian/Ubuntu with `live-build`, or Docker
- Repository root mounted at `/build`

## Docker

```bash
docker build -f install/bootguardai/iso/Dockerfile.builder -t bootguardai-iso .
docker run --rm -v "$(pwd)/dist:/build/dist" bootguardai-iso
```

## Safety

ISO installers use preseed for **non-destructive** dedicated partition install only.
They do **not** auto-wipe disks without explicit operator confirmation.
