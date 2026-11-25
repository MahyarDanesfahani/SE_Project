from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ZU Assistant API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://zu:zu@localhost:5432/zu_assistant"
    allowed_origins: str = "http://localhost:3000"
    jwt_secret: str = "change-me-in-production-use-32-byte-secret"
    access_token_expire_minutes: int = 30
    max_upload_size_bytes: int = 5_000_000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
