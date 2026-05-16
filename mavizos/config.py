"""Application configuration via environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MavizOS runtime settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MavizOS_",
        extra="ignore",
    )

    env: str = "development"
    demo_mode: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    memory_persist_path: str = "./data/memory.json"
    audit_log_path: str = "./data/audit.log"
    require_approval: bool = True


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
