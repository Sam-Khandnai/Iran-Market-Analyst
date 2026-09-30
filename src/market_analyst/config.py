from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="MA_", extra="ignore"
    )

    app_name: str = "Iran Market Analyst"
    environment: str = "dev"
    log_level: str = "INFO"
    tsetmc_api_url: str = "https://cdn.tsetmc.com/api"
    retry_backoff_seconds: float = 1.0
    database_url: str = "postgresql+asyncpg://analyst:analyst@localhost:5432/analyst"
    cache_ttl_hours: int = 6

    # TSETMC (در فاز ۲ استفاده می‌شود)
    tsetmc_base_url: str = "https://www.tsetmc.com"
    http_timeout_seconds: float = 20.0
    http_max_retries: int = 3

        # این دو بدون پیشوند MA_ در .env هستند؛ alias صریح باعث می‌شود
    # pydantic-settings مستقیم از نام env استفاده کند، نه MA_OPENROUTER_API_KEY
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    model_name: str = Field(default="", validation_alias="MODEL_NAME")
    openai_base_url: str = Field(default="", validation_alias="OPENAI_BASE_URL")

    use_mcp: bool = False   # MA_USE_MCP در .env

    navasan_api_key: str = Field(default="", validation_alias="NAVASAN_API_KEY")
    navasan_api_url: str = "https://api.navasan.tech/latest/"

    # LLM (فقط برای توضیح نهایی، در فاز آخر)
    llm_model: str = ""
    llm_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()