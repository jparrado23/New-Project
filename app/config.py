from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ShortlistConfig(BaseModel):
    min_mentions: int = 2
    min_unique_authors: int = 2
    anomaly_score_threshold: float = 0.5


class MarketDataConfig(BaseModel):
    price_windows: list[int] = Field(default_factory=lambda: [1, 3, 5])
    provider: str = "mock"


class LLMConfig(BaseModel):
    enabled: bool = False
    provider: str = "mock"
    model: str = "placeholder-model"
    max_items_per_run: int = 25
    api_key_env_var: str = "OPENAI_API_KEY"
    base_url: str | None = None
    system_prompt: str = (
        "You are classifying Reddit discussion about US-listed stocks for a human analyst. "
        "Distinguish between early attention, post-price-move chatter, pump-like behavior, "
        "and thesis-driven discussion. Do not give investment advice."
    )
    max_input_chars: int = 6000


class LoggingConfig(BaseModel):
    level: str = "INFO"
    json: bool = False


class AppConfig(BaseModel):
    subreddits: list[str]
    include_comments: bool = True
    lookback_hours: int = 24
    report_output_dir: str = "reports"
    database_path: str = "data/pipeline.db"
    stock_universe_path: str = "data/us_stock_universe.csv"
    anomaly_baseline_window_days: int = 30
    shortlist: ShortlistConfig = Field(default_factory=ShortlistConfig)
    market_data: MarketDataConfig = Field(default_factory=MarketDataConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_path: str | os.PathLike[str] | None = None) -> AppConfig:
    selected_path = Path(
        config_path or os.getenv("APP_CONFIG_PATH") or "config/config.example.yaml"
    )
    with selected_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    return AppConfig.model_validate(raw)
