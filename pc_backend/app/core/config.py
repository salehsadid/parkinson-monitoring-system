"""
Core configuration for the Parkinson's Monitoring System.

This module loads configuration from environment variables and .env files
using Pydantic Settings for type-safe configuration management.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.

    All settings can be overridden via environment variables.
    Sensitive values should never be committed to version control.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Parkinson's Monitoring System"
    APP_VERSION: str = "0.1.0"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./parkinson_monitoring.db"

    # Data Retention (hours)
    RETENTION_HOURS: int = 72

    # Logging
    LOG_LEVEL: str = "INFO"

    # Sensor Configuration
    DEFAULT_SAMPLING_RATE_HZ: int = 50

    # Device Configuration
    DEFAULT_DEVICE_ID: str = "ESP32_001"
    DEFAULT_PATIENT_ID: str = "P001"

    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 10

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for SQLAlchemy."""
        return self.DATABASE_URL

    @property
    def database_url_async(self) -> str:
        """Get async database URL for SQLAlchemy."""
        if self.DATABASE_URL.startswith("sqlite:///"):
            # For async SQLite, use aiosqlite driver
            path = self.DATABASE_URL.replace("sqlite:///", "")
            return f"sqlite+aiosqlite:///{path}"
        return self.DATABASE_URL

    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent.parent

    @property
    def data_directory(self) -> Path:
        """Get the data directory path."""
        return self.project_root / "data"

    @property
    def models_directory(self) -> Path:
        """Get the saved models directory path."""
        return self.project_root / "ml" / "saved_models"


def get_settings() -> Settings:
    """
    Get application settings instance.

    Returns:
        Settings: Configured settings object
    """
    return Settings()


# Global settings instance
settings = get_settings()
