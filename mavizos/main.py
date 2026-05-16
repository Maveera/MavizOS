"""MavizOS FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mavizos import __version__
from mavizos.api.routes import router
from mavizos.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

settings = get_settings()

app = FastAPI(
    title="MavizOS",
    description="Autonomous Agentic AI SOC Operating System",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

from mavizos.os.desktop.routes import mount_desktop

mount_desktop(app)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "service": "mavizos",
        "version": __version__,
        "docs": "/docs",
        "desktop": "/desktop",
        "demo_mode": str(settings.demo_mode),
    }


def run() -> None:
    """Run uvicorn server."""
    import uvicorn

    uvicorn.run(
        "mavizos.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.env == "development",
    )


if __name__ == "__main__":
    run()
