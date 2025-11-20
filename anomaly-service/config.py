from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service configuration."""

    app_name: str = Field("anomaly-service", description="Service name.")
    host: str = Field("0.0.0.0", description="Bind host.")
    port: int = Field(8001, description="Bind port.")
    log_level: str = Field("INFO", description="Logging level.")
    default_model: str = Field("placeholder-v0", description="Default model name.")

    model_config = SettingsConfigDict(env_prefix="ANOMALY_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
