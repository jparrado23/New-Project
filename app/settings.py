from __future__ import annotations

from functools import lru_cache

from app.config import AppConfig, load_config


@lru_cache(maxsize=1)
def get_settings(config_path: str | None = None) -> AppConfig:
    return load_config(config_path)
