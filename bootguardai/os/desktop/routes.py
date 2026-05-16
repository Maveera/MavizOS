"""Optional dark web UI for BootGuardAI."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

STATIC = Path(__file__).parent / "static"


def mount_desktop(app: FastAPI) -> None:
    index = STATIC / "index.html"

    @app.get("/bootguard-desktop", response_class=HTMLResponse)
    async def desktop() -> FileResponse:
        return FileResponse(index)

    @app.get("/bootguard-desktop/static/{path:path}")
    async def static_file(path: str) -> FileResponse:
        return FileResponse(STATIC / path)
