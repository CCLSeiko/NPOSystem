"""NPOSystem Backend Core Configuration."""
from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "NPOSystem API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database (Async)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5434/NPOSystem"

    # Database (Sync — for Alembic)
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5434/NPOSystem"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3001"]

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # LINE Login
    LINE_CHANNEL_ID: str = ""
    LINE_CHANNEL_SECRET: str = ""

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
