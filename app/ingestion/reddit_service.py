from __future__ import annotations

from app.config import AppConfig
from app.models.reddit import NormalizedRedditItem, RedditRawItem
from app.storage.repositories import PipelineRepository
from app.utils.logging import get_logger


class RedditIngestionService:
    def __init__(self, provider, repository: PipelineRepository) -> None:
        self.provider = provider
        self.repository = repository
        self.logger = get_logger(__name__)

    def ingest(self, config: AppConfig) -> tuple[list[RedditRawItem], list[NormalizedRedditItem]]:
        raw_items = self.provider.fetch_raw_items(
            subreddits=config.subreddits,
            lookback_hours=config.lookback_hours,
            include_comments=config.include_comments,
        )
        normalized = self.provider.normalize_items(raw_items)
        self.repository.insert_raw_reddit_items(raw_items)
        self.repository.insert_normalized_reddit_items(normalized)
        self.logger.info(
            "reddit_ingestion_completed",
            extra={"raw_count": len(raw_items), "normalized_count": len(normalized)},
        )
        return raw_items, normalized
