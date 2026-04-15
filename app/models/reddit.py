from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RedditRawItem(BaseModel):
    source_id: str
    subreddit: str
    item_type: str
    author: str
    title: str | None = None
    body: str = ""
    score: int = 0
    num_comments: int = 0
    created_utc: datetime
    permalink: str | None = None


class NormalizedRedditItem(BaseModel):
    item_id: str
    source_id: str
    subreddit: str
    item_type: str
    author: str
    text: str
    created_at: datetime
    url: str | None = None
    engagement_score: float = 0.0
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class ExtractedTickerMention(BaseModel):
    mention_id: str
    item_id: str
    ticker: str
    company_name: str | None = None
    mention_count: int = 1
    confidence: float = 0.0
    extraction_method: str = "naive"
