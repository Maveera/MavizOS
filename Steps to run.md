# Steps to Run — MavizOS + BootGuardAI

Step-by-step guide to go from zero to running **MavizOS** (AI SOC OS) and **BootGuardAI** (boot analysis) in development or production. Commands match the **MavizOS v0.1.0** monorepo ([github.com/Maveera/MavizOS](https://github.com/Maveera/MavizOS)).

---

## 1. Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Python 3.11+** | Required for both products (`requires-python = ">=3.11"` in `pyproject.toml`) |
| **Git** | Clone and version control |
| **GitHub CLI (`gh`)** | Optional — PRs, `gh auth setup-git` if HTTPS push fails |
| **Windows** | Windows 10/11; PowerShell 5.1+; Administrator for production installers |
| **Linux** | Debian/Ubuntu/RHEL/Fedora; `python3-venv` package; **root** for production installers |
| **ISO build** | Linux or **WSL2** only; 20+ GB disk; 30–90 min build time |

**Verify Python:**

| Windows (PowerShell) | Linux (bash) |
|----------------------|--------------|
| `python --version` | `python3 --version` |
| `python -m venv --help` | `python3 -m venv --help` |

---

## 2. Clone repository

### Windows (PowerShell)

```powershell
git clone https://github.com/Maveera/MavizOS.git
cd MavizOS
```

### Linux (bash)

```bash
git clone https://github.com/Maveera/MavizOS.git
cd MavizOS
```

If you already have the repo locally, `cd` to the project root (e.g. `d:\Agentic OS` or `~/MavizOS`).

---

## 3. Development setup

All commands below run from the **repository root**.

### 3.1 Create virtual environment

| Windows (PowerShell) | Linux (bash) |
|----------------------|--------------|
| `python -m venv .venv` | `python3 -m venv .venv` |
| `.\.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3.2 Install packages

**Option A — recommended (editable + dev + BootGuardAI extra):**

| Windows / Linux (venv active) |
|-------------------------------|
| `pip install -U pip` |
| `pip install -e ".[dev,bootguard]"` |

**Option B — separate extras (same result):**

```text
pip install -e ".[dev]"
pip install -e ".[bootguard]"
```

**Option C — requirements file (README quickstart):**

```text
pip install -r requirements.txt
pip install -e .
```

For BootGuard-only deps file: `pip install -r requirements-bootguard.txt` (optional if you used `.[bootguard]`).

### 3.3 Environment file (optional)

| Windows | Linux |
|---------|-------|
| `Copy-Item .env.example .env` | `cp .env.example .env` |

Defaults: MavizOS API **8000**, demo mode on. BootGuardAI uses `BOOTGUARD_*` vars (see [INSTALL_BOOTGUARD.md](INSTALL_BOOTGUARD.md)).

### 3.4 Verify CLI

With venv activated:

```text
mavizos help
bootguardai
```

- `mavizos` — prints boot/serve help (entry: `mavizos.os.shell.main:cli_entry`)
- `bootguardai` — boots interactive shell (no separate `help` subcommand; use `python -m bootguardai` for shell)

Also verify modules:

```text
python -m mavizos --help
python -c "import mavizos, bootguardai; print('OK')"
```

---

## 4. Run MavizOS

### 4.1 Interactive shell (SOC REPL)

```text
python -m mavizos
```

Equivalent:

```text
mavizos
mavizos boot
python -m mavizos.boot
```

You should see the ASCII boot sequence and prompt:

```text
MavizOS>
```

Use `help` at the prompt for shell commands (`triage`, `investigate`, `fs ls`, etc.).

### 4.2 API server + web desktop

**Terminal 1** — start API (pick one):

```text
python -m mavizos.main
```

or:

```text
mavizos serve
```

**Browser:**

| URL | Purpose |
|-----|---------|
| http://localhost:8000/docs | OpenAPI / Swagger |
| http://localhost:8000/desktop | Web SOC desktop |
| http://localhost:8000/api/v1/health | Health check |

Default port: **8000** (`MavizOS_API_PORT` in `.env`).

### 4.3 Demo scripts

With venv active, from repo root:

```text
python scripts/demo.py
python scripts/os_demo.py
```

- `demo.py` — API-style investigation demo  
- `os_demo.py` — scripted boot + shell commands  

### 4.4 Virtual filesystem

Artifacts are written under:

```text
./mavizos_fs/
```

Config: `etc/mavizos/config.json`

---

## 5. Run BootGuardAI

Install BootGuard extra first: `pip install -e ".[bootguard]"` (see §3).

### 5.1 Interactive shell

```text
python -m bootguardai
```

Prompt: `bootguardai>` (or similar per REPL). Commands: `help`, `analyze`, `windows`, `linux`, `persistence`, `fs ls`, etc.

### 5.2 API server (port 8081)

**Terminal 1:**

```text
python -m bootguardai.main
```

or:

```text
python -m uvicorn bootguardai.main:app --host 0.0.0.0 --port 8081
```

**Browser:**

| URL | Purpose |
|-----|---------|
| http://localhost:8081/docs | API docs |
| http://localhost:8081/bootguard-desktop | Web desktop |
| http://localhost:8081/api/v1/... | REST routes |

Default port: **8081** (`BOOTGUARD_API_PORT`).

### 5.3 Demo script

```text
python scripts/bootguard_demo.py
```

### 5.4 Virtual filesystem

```text
./bootguardai_fs/
```

Example `.env` (BootGuard):

```env
BOOTGUARD_DEMO_MODE=true
BOOTGUARD_API_PORT=8081
BOOTGUARD_VFS_ROOT=./bootguardai_fs
```

---

## 6. Run tests

From repo root with venv active and dev extras installed:

```text
pytest -v
```

Runs tests under `tests/` (MavizOS, BootGuardAI, install scripts, e2e). Requires `pip install -e ".[dev]"` or `requirements.txt` (includes pytest).

---

## 7. Windows production install (MavizOS)

**Non-destructive** — does not wipe Windows. Requires **Administrator** PowerShell.

1. Open PowerShell **as Administrator**.
2. Go to repo root:

   ```powershell
   cd "D:\MavizOS"   # or your clone path
   ```

3. Allow script execution for this session:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

4. Install (appliance mode):

   ```powershell
   .\install\windows\install.ps1 -Autostart -ConfigureAppliance
   ```

   Simpler (autostart only):

   ```powershell
   .\install\windows\install.ps1 -Autostart
   ```

5. **Result:** files at `C:\MavizOS`, venv at `C:\MavizOS\.venv`, scheduled task **MavizOS-Shell-Autostart**.

6. **Daily use:**

   ```cmd
   C:\MavizOS\install\windows\mavizos-shell.cmd
   ```

7. **API + desktop:**

   ```powershell
   C:\MavizOS\.venv\Scripts\mavizos.exe serve
   ```

   Open http://localhost:8000/desktop

8. **Uninstall:**

   ```powershell
   .\install\windows\uninstall.ps1
   ```

Full detail: [INSTALL.md](INSTALL.md)

---

## 8. Linux production install (MavizOS)

Requires **root**.

```bash
cd /path/to/MavizOS
sudo chmod +x install/linux/install.sh install/linux/uninstall.sh
sudo ./install/linux/install.sh
```

Optional autologin on tty1:

```bash
sudo ENABLE_AUTOLOGIN=1 ./install/linux/install.sh
```

| Item | Location |
|------|----------|
| Install root | `/opt/mavizos` |
| API service | `mavizos.service` (port **8000**) |
| Shell (manual) | `sudo -u MavizOS /opt/mavizos/.venv/bin/python -m mavizos` |

Check API:

```bash
curl http://localhost:8000/api/v1/health
sudo systemctl status mavizos
```

Uninstall:

```bash
sudo ./install/linux/uninstall.sh
```

Full detail: [INSTALL.md](INSTALL.md)

---

## 9. BootGuardAI production install (brief)

### Windows (Administrator)

```powershell
cd "D:\MavizOS"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install\bootguardai\windows\install.ps1
```

Install root: `C:\BootGuardAI`

### Linux (root)

```bash
sudo bash install/bootguardai/linux/install.sh
sudo systemctl start bootguardai
```

Install root: `/opt/bootguardai`

Full detail: [INSTALL_BOOTGUARD.md](INSTALL_BOOTGUARD.md)

---

## 10. ISO build

### 10.1 MavizOS ISO

**Linux / WSL2:**

```bash
chmod +x install/iso/build-iso.sh
./install/iso/build-iso.sh
```

**Windows (delegates to WSL2):**

```powershell
.\install\iso\build-iso.ps1
```

**Output:** `dist/mavizos-os-<version>-amd64.iso` (e.g. `dist/mavizos-os-0.1.0-amd64.iso`)

**Boot:** VM or USB → http://127.0.0.1:8000/desktop or `python -m mavizos` as user `MavizOS`.

See [install/iso/README-ISO.md](install/iso/README-ISO.md).

### 10.2 BootGuardAI ISO

```bash
bash install/bootguardai/iso/build-iso.sh
```

**Output:** `dist/bootguardai-os-<version>.iso`

Docker alternative: see [install/bootguardai/iso/README-ISO.md](install/bootguardai/iso/README-ISO.md).

**Warning:** `dd` to USB overwrites the target device — confirm `/dev/sdX` before writing.

---

## 11. Using Prompt.md

[`Prompt.md`](Prompt.md) contains **system prompts** for AI agents working on this platform.

| Section | Use for |
|---------|---------|
| **MavizOS System Prompt** | SOC agents — triage, investigation, IR, hunting, detection engineering, 14-section reports |
| **BootGuardAI System Prompt** | Boot chain analysis, persistence, bootkit heuristics, 12-section reports |
| **Platform & Deployment Context** | Monorepo layout, install paths, ports, security rules |

**How to use:**

1. Open `Prompt.md` in the repo root.
2. Copy the **MavizOS** or **BootGuardAI** system prompt block into your agent host:
   - **Cursor:** Project rules, Agent instructions, or chat system context
   - **Claude / ChatGPT:** Custom instructions or project knowledge
   - **SDK / API:** System message for `Agent.create` / chat completions
3. Keep **Platform & Deployment Context** attached when agents edit installers, docs, or paths.
4. Enforce rules in prompts: demo data labeled `simulated: true`, destructive actions need human approval, no fabricated evidence.

Do not commit API keys or secrets into `Prompt.md` or rules files.

---

## 12. GitHub workflow

Remote: `https://github.com/Maveera/MavizOS.git`

### Push changes to `main`

| Windows (PowerShell) | Linux (bash) |
|----------------------|--------------|
| `git status` | `git status` |
| `git add Prompt.md "Steps to run.md"` | same |
| `git commit -m "docs: your message"` | same |
| `git push origin main` | same |

### Branch basics

```text
git checkout -b feature/my-change
# ... edit, commit ...
git push -u origin feature/my-change
gh pr create    # optional, if gh is installed
```

### Auth troubleshooting

If `git push` fails with auth errors and `gh` is logged in:

```text
gh auth setup-git
git push origin main
```

Never force-push to `main` unless you intend to and understand the impact.

---

## 13. Troubleshooting

| Issue | What to try |
|-------|-------------|
| **`python` not found** | Install Python 3.11+; on Linux use `python3` |
| **venv activate fails (Windows)** | `Set-ExecutionPolicy -Scope Process Bypass` then activate |
| **`mavizos` / `bootguardai` not recognized** | Activate venv; run `pip install -e ".[dev,bootguard]"` |
| **Port 8000 in use** | Stop other process or set `MavizOS_API_PORT` in `.env` |
| **Port 8081 in use** | Set `BOOTGUARD_API_PORT` in `.env` |
| **Import errors for `bootguardai`** | `pip install -e ".[bootguard]"` |
| **pytest not found** | `pip install -e ".[dev]"` |
| **`gh` / HTTPS push denied** | `gh auth login` then `gh auth setup-git` |
| **ISO build on Windows only** | Use WSL2: `.\install\iso\build-iso.ps1` |
| **Production install permission** | Windows: Admin PowerShell; Linux: `sudo` |
| **Demo vs production** | Set `MavizOS_DEMO_MODE=false` and review `.env` before exposure |

---

## Quick reference

| Task | Command |
|------|---------|
| Clone | `git clone https://github.com/Maveera/MavizOS.git` |
| Venv (Win) | `python -m venv .venv` → `.\.venv\Scripts\Activate.ps1` |
| Venv (Linux) | `python3 -m venv .venv` → `source .venv/bin/activate` |
| Dev install | `pip install -e ".[dev,bootguard]"` |
| MavizOS shell | `python -m mavizos` |
| MavizOS API | `mavizos serve` or `python -m mavizos.main` |
| MavizOS web UI | http://localhost:8000/desktop |
| MavizOS demo | `python scripts/demo.py` |
| BootGuard shell | `python -m bootguardai` |
| BootGuard API | `python -m bootguardai.main` |
| BootGuard web UI | http://localhost:8081/bootguard-desktop |
| BootGuard demo | `python scripts/bootguard_demo.py` |
| Tests | `pytest -v` |
| Win install (MavizOS) | `.\install\windows\install.ps1 -Autostart` |
| Linux install (MavizOS) | `sudo ./install/linux/install.sh` |
| Win install (BootGuard) | `.\install\bootguardai\windows\install.ps1` |
| Linux install (BootGuard) | `sudo bash install/bootguardai/linux/install.sh` |
| MavizOS ISO | `./install/iso/build-iso.sh` |
| BootGuard ISO | `bash install/bootguardai/iso/build-iso.sh` |
| Agent prompts | `Prompt.md` |

---

## Related documentation

| Document | Content |
|----------|---------|
| [README.md](README.md) | MavizOS features, API, architecture |
| [README_BOOTGUARD.md](README_BOOTGUARD.md) | BootGuardAI quick start |
| [INSTALL.md](INSTALL.md) | MavizOS production + ISO |
| [INSTALL_BOOTGUARD.md](INSTALL_BOOTGUARD.md) | BootGuardAI production + ISO |
| [Prompt.md](Prompt.md) | AI agent system prompts |

---

*MavizOS monorepo v0.1.0 — May 16, 2026*
