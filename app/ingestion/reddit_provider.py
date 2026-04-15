from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from app.models.reddit import NormalizedRedditItem, RedditRawItem


class RedditProvider(ABC):
    @abstractmethod
    def fetch_raw_items(
        self, subreddits: list[str], lookback_hours: int, include_comments: bool
    ) -> list[RedditRawItem]:
        raise NotImplementedError

    @abstractmethod
    def normalize_items(self, raw_items: list[RedditRawItem]) -> list[NormalizedRedditItem]:
        raise NotImplementedError


class MockRedditProvider(RedditProvider):
    def fetch_raw_items(
        self, subreddits: list[str], lookback_hours: int, include_comments: bool
    ) -> list[RedditRawItem]:
        created = datetime.utcnow() - timedelta(hours=min(lookback_hours, 4))
        sample = [
            RedditRawItem(
                source_id="post-1",
                subreddit=subreddits[0] if subreddits else "stocks",
                item_type="post",
                author="value_hawk",
                title="Watching AAPL and NVDA into earnings",
                body="AAPL looks stable, NVDA chatter is growing after recent price action.",
                score=120,
                num_comments=35,
                created_utc=created,
                permalink="/r/stocks/post-1",
            ),
            RedditRawItem(
                source_id="post-2",
                subreddit=subreddits[1] if len(subreddits) > 1 else "wallstreetbets",
                item_type="post",
                author="thesis_builder",
                title="Why MSFT cloud margins still matter",
                body="MSFT has a more thesis-driven setup than the usual meme names.",
                score=80,
                num_comments=18,
                created_utc=created,
                permalink="/r/investing/post-2",
            ),
        ]
        if include_comments:
            sample.append(
                RedditRawItem(
                    source_id="comment-1",
                    subreddit=subreddits[0] if subreddits else "stocks",
                    item_type="comment",
                    author="fast_money_42",
                    body="I keep seeing NVDA mentioned everywhere today.",
                    score=15,
                    num_comments=0,
                    created_utc=created,
                    permalink="/r/stocks/comments/comment-1",
                )
            )
        return sample

    def normalize_items(self, raw_items: list[RedditRawItem]) -> list[NormalizedRedditItem]:
        normalized: list[NormalizedRedditItem] = []
        for raw in raw_items:
            combined_text = " ".join(part for part in [raw.title, raw.body] if part).strip()
            normalized.append(
                NormalizedRedditItem(
                    item_id=f"norm-{raw.source_id}",
                    source_id=raw.source_id,
                    subreddit=raw.subreddit,
                    item_type=raw.item_type,
                    author=raw.author,
                    text=combined_text,
                    created_at=raw.created_utc,
                    url=raw.permalink,
                    engagement_score=float(raw.score + raw.num_comments),
                    metadata={"score": raw.score, "num_comments": raw.num_comments},
                )
            )
        return normalized
