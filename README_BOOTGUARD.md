# BootGuardAI

**AI Operating System Boot Analysis and Security Intelligence Engine** — analyzes Windows/Linux boot processes, detects boot-level threats, persistence, and bootkits, and produces forensic boot analysis reports.

## Features

- **12 specialized agents**: Windows boot, Linux boot, bootloader integrity, kernel analysis, persistence hunt, firmware/UEFI, rootkit/bootkit heuristics, forensics timeline, script/command guidance, MITRE persistence mapping, reporting, memory/knowledge
- **10-step boot analysis workflow** with **12-section structured reports**
- **Approval gates** for destructive boot remediation (BCD rewrite, EFI changes, etc.)
- **Mock integrations** (Windows Event Log, journalctl, EDR, SIEM) — all labeled `simulated: true`
- **REST API** on port **8081** (default) and interactive **bootguardai>** shell

## Quick Start

```bash
pip install -e ".[bootguard]"
python -m bootguardai              # boot + shell
python -m uvicorn bootguardai.main:app --port 8081
python scripts/bootguard_demo.py
```

## Shell Commands

| Command | Purpose |
|---------|---------|
| `help` | Command list |
| `status` | Kernel / agent health |
| `agents` | List agents |
| `analyze` | Sample boot analysis |
| `windows` | Windows UEFI boot analysis |
| `linux` | Linux GRUB boot analysis |
| `persistence` | Persistence hunt |
| `reports <id>` | Fetch analysis by ID |
| `fs ls\|cat` | Virtual filesystem |
| `approvals` | Pending approval queue |
| `audit` | Audit log |
| `shutdown` | Exit |

## API

| Method | Path |
|--------|------|
| POST | `/api/v1/boot/analyze` |
| POST | `/api/v1/boot/windows` |
| POST | `/api/v1/boot/linux` |
| GET | `/api/v1/reports/{id}` |
| POST | `/api/v1/persistence/hunt` |
| GET | `/api/v1/approvals` |

## Install Paths

| Platform | Path |
|----------|------|
| Windows | `C:\BootGuardAI` |
| Linux | `/opt/bootguardai` |

See [INSTALL_BOOTGUARD.md](INSTALL_BOOTGUARD.md).

## Related

- [MavizOS](README.md) — SOC investigation platform (separate product, same monorepo)
