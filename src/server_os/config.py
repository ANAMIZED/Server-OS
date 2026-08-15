"""Runtime configuration."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SERVER_OS_", env_file=".env", extra="ignore")

    data_dir: Path = Path("./data")
    host: str = "0.0.0.0"
    port: int = 8080
    llm_mode: Literal["mock", "openai"] = "mock"
    llm_base: str = "https://api.openai.com/v1"
    openai_api_key: str | None = None
    default_model: str = "mock-gpt"
    log_level: str = "INFO"
    max_agent_steps: int = 20
    default_budget_usd: float = 1.0


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
