"""Application settings, loaded from environment variables / the backend/.env file."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )

    # LLM (Google Gemini). Leave the key empty to run in offline/fallback mode.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # CORS: comma-separated list of frontend origins allowed to call this API.
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Retrieval / conversation tuning
    top_k: int = 4
    max_history: int = 8
    request_timeout: float = 30.0

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.gemini_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
