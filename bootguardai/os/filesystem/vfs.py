"""Virtual filesystem for BootGuardAI artifacts."""

from pathlib import Path

from bootguardai.config import get_settings


class VirtualFilesystem:
    def __init__(self) -> None:
        self.root = Path(get_settings().vfs_root)
        self._init_tree()

    def _init_tree(self) -> None:
        for sub in (
            "etc",
            "var/reports",
            "var/logs",
            "var/audit",
            "var/boot",
            "home",
        ):
            (self.root / sub).mkdir(parents=True, exist_ok=True)

    def resolve(self, path: str) -> Path:
        clean = path.strip().lstrip("/").replace("\\", "/") or "."
        target = (self.root / clean).resolve()
        if not str(target).startswith(str(self.root.resolve())):
            raise PermissionError("Path outside VFS root")
        return target

    def ls(self, path: str = ".") -> list[str]:
        target = self.resolve(path)
        if not target.exists():
            raise FileNotFoundError(path)
        if target.is_file():
            return [target.name]
        return sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())

    def cat(self, path: str) -> str:
        target = self.resolve(path)
        if not target.is_file():
            raise FileNotFoundError(path)
        return target.read_text(encoding="utf-8")

    def write_report(self, analysis_id: str, content: str) -> Path:
        path = self.root / "var" / "reports" / f"{analysis_id}.md"
        path.write_text(content, encoding="utf-8")
        return path
