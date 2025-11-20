from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service configuration loaded from environment."""

    host: str = Field("0.0.0.0", description="Server host for FastAPI.")
    port: int = Field(8001, description="Server port for FastAPI.")
    model_path: str = Field(
        "models/dev_isolation_forest.pkl",
        description="Path to the anomaly detection model artifact.",
    )
    feature_store_url: str = Field(
        "redis://feature-store:6379", description="Feature store connection string."
    )
    alert_store_url: str = Field(
        "http://alert-store:8000", description="Alert store base URL."
    )
    log_level: str = Field("INFO", description="Logging level for the service.")
    service_version: str = Field(
        "0.1.0", description="Semantic version for the service."
    )

    model_config = SettingsConfigDict(env_prefix="ANOMALY_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
