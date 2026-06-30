"""Typed application settings.

All configuration is read from environment variables (inherited from the
repository-root ``.env`` — template ``../.env.example``). This module is the
single, typed source of truth for configuration across the API, workers, and
collectors. Nothing else should read ``os.environ`` directly.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed view over the process environment.

    Field names mirror the variables documented in ``../.env.example``. Defaults
    are dev-friendly; secrets default to empty and must be provided in real
    environments.
    """

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- App ----
    app_env: str = "development"
    app_name: str = "cognivest"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: str = "http://localhost:3000"

    # ---- Backend / FastAPI ----
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # ---- Postgres ----
    database_url: str = "postgresql+asyncpg://cognivest:change_me@localhost:5432/cognivest"

    # ---- Redis (cache + Celery broker/backend) ----
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")  # type: ignore[assignment]
    celery_broker_url: RedisDsn = Field(default="redis://localhost:6379/1")  # type: ignore[assignment]
    celery_result_backend: RedisDsn = Field(default="redis://localhost:6379/2")  # type: ignore[assignment]

    # ---- Auth / JWT (RS256) ----
    jwt_algorithm: str = "RS256"
    jwt_private_key_path: str = "./secrets/jwt_private.pem"
    jwt_public_key_path: str = "./secrets/jwt_public.pem"
    jwt_access_token_ttl_minutes: int = 15
    jwt_refresh_token_ttl_days: int = 7
    service_token: str = "change_me_internal_service_token"

    # ---- OAuth (Google) ----
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""

    # ---- Cognee ----
    cognee_vector_db_provider: str = "lancedb"
    cognee_graph_db_provider: str = "kuzu"
    cognee_data_dir: str = "/data/cognee"
    cognee_llm_provider: str = "anthropic"

    # ---- LLM (Anthropic Claude) ----
    anthropic_api_key: str = ""
    llm_model: str = "claude-opus-4-8"
    llm_max_tokens: int = 2048

    # ---- External data vendors (all pluggable) ----
    market_data_provider: str = "polygon"
    market_data_api_key: str = ""
    news_api_provider: str = "newsapi"
    news_api_key: str = ""
    web_search_provider: str = "tavily"
    web_search_api_key: str = ""

    # ---- Scheduling ----
    price_collect_cron: str = "0 22 * * 1-5"
    news_collect_interval_hours: int = 2
    ingest_dedup_enabled: bool = True

    # ---- Rate limiting ----
    query_rate_limit_per_minute: int = 20

    @field_validator("backend_cors_origins")
    @classmethod
    def _strip_origins(cls, value: str) -> str:
        """Normalise the comma-separated CORS origin list."""
        return value.strip()

    @property
    def cors_origins(self) -> list[str]:
        """CORS origins as a parsed, de-whitespaced list."""
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """True when running in the production environment."""
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide cached :class:`Settings` instance."""
    return Settings()
