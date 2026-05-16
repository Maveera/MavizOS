"""BootGuardAI FastAPI application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bootguardai import __version__
from bootguardai.api.routes import router
from bootguardai.config import get_settings
from bootguardai.os.desktop.routes import mount_desktop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

settings = get_settings()

app = FastAPI(
    title="BootGuardAI",
    description="AI Operating System Boot Analysis and Security Intelligence Engine",
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
mount_desktop(app)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "BootGuardAI",
        "version": __version__,
        "docs": "/docs",
        "desktop": "/bootguard-desktop",
        "demo_mode": str(settings.demo_mode),
    }


def run() -> None:
    import uvicorn

    uvicorn.run(
        "bootguardai.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.env == "development",
    )


if __name__ == "__main__":
    run()
