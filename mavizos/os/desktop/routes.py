"""Mount web desktop on FastAPI."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).parent / "static"

desktop_router = APIRouter(tags=["desktop"])


@desktop_router.get("/desktop")
async def desktop_home() -> FileResponse:
    """SOC web desktop."""
    return FileResponse(STATIC_DIR / "index.html")


def mount_desktop(app) -> None:
    """Attach desktop routes and static assets to app."""
    app.include_router(desktop_router)
    app.mount(
        "/desktop/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="desktop_static",
    )
