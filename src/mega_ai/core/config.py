from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", validation_alias="APP_ENV")
    log_level: str = Field(default="info", validation_alias="LOG_LEVEL")
    database_url: str = Field(default="sqlite:///./mega_ai.db", validation_alias="DATABASE_URL")
    job_worker_poll_seconds: int = Field(default=2, validation_alias="JOB_WORKER_POLL_SECONDS")
    code_sandbox_timeout_seconds: int = Field(default=2, validation_alias="CODE_SANDBOX_TIMEOUT_SECONDS")
    max_query_chars: int = Field(default=4000, validation_alias="MAX_QUERY_CHARS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
