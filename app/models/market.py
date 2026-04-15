from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class MarketSnapshot(BaseModel):
    ticker: str
    as_of_date: date
    close: float
    volume: int
    market_cap: float | None = None
    return_1d: float | None = None
    return_3d: float | None = None
    return_5d: float | None = None


class AggregatedStockDailyFeatures(BaseModel):
    run_date: date
    ticker: str
    mention_count: int = 0
    unique_authors: int = 0
    weighted_sentiment: float = 0.0
    anomaly_score: float = 0.0
    baseline_mentions: float = 0.0
    discussion_count: int = 0
    source_item_ids: list[str] = Field(default_factory=list)
