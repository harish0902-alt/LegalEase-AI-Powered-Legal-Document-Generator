from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str | None = Field(
        default=None,
        validation_alias="GEMINI_API_KEY",
    )

    gemini_model: str = Field(
        default="gemini-3.1-flash-lite",
        validation_alias="GEMINI_MODEL",
    )

    gemini_fallback_models: str = Field(
        default="gemini-3.6-flash,gemini-3.8-flash,gemini-flash-latest,gemini-flash-lite-latest",
        validation_alias="GEMINI_FALLBACK_MODELS",
    )

    mock_ai: bool = Field(
        default=False,
        validation_alias="MOCK_AI",
    )

    backend_url: str = Field(
        default="http://127.0.0.1:8000",
        validation_alias="BACKEND_URL",
    )

    cors_origins: str = Field(
        default="http://localhost:8501,http://127.0.0.1:8501",
        validation_alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def fallback_model_list(self) -> list[str]:
        return [
            m.strip()
            for m in self.gemini_fallback_models.split(",")
            if m.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()