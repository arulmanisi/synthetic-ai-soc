from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str = Field("0.0.0.0", description="Bind host for llm-reasoner.")
    port: int = Field(8002, description="Bind port for llm-reasoner.")
    log_level: str = Field("INFO", description="Logging level.")

    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
