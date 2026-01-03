from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    For local development, values can be provided via a `.env` file
    in the `backend/` directory (Render will provide env vars directly).
    """

    app_name: str = "Finance App API"
    debug: bool = False

    # Database - required in all environments
    # Uses DATABASE_URL env var; if not provided, the app will fail fast on startup.
    database_url: str = Field(..., env="DATABASE_URL")

    # Auth / security
    secret_key: str = Field("CHANGE_ME_IN_PRODUCTION", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        60, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # CORS
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["*"], env="ALLOWED_ORIGINS"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


