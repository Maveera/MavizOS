"""BootGuardAI configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(env_prefix="BOOTGUARD_", env_file=".env", extra="ignore")

    env: str = "development"
    demo_mode: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8081
    require_approval: bool = True
    vfs_root: str = "./bootguardai_fs"
    shell_prompt: str = "bootguardai>"
    audit_log_path: str = "./data/bootguard_audit.log"
    memory_path: str = "./data/bootguard_memory.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
