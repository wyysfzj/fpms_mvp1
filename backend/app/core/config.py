from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    fpms_env: str = "dev"
    database_url: str = "sqlite:///./fpms_dev.db"
    cors_origins: List[str] = ["http://localhost:5173"]
    jwt_secret: str = "dev-secret-change-me"
    storage_dir: str = "./storage"


@lru_cache
def get_settings() -> Settings:
    return Settings()
