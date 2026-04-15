from __future__ import annotations

import json
from datetime import datetime

from app.models.market import AggregatedStockDailyFeatures, MarketSnapshot
from app.models.reddit import ExtractedTickerMention, NormalizedRedditItem, RedditRawItem
from app.models.report import ReportRow
from app.models.signal import LLMClassificationResult
from app.storage.db import Database


class PipelineRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def insert_raw_reddit_items(self, items: list[RedditRawItem]) -> None:
        with self.db.connect() as connection:
            connection.executemany(
                """
                INSERT OR IGNORE INTO raw_reddit_items
                (source_id, subreddit, item_type, author, title, body, score, num_comments, created_utc, permalink)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.source_id,
                        item.subreddit,
                        item.item_type,
                        item.author,
                        item.title,
                        item.body,
                        item.score,
                        item.num_comments,
                        item.created_utc.isoformat(),
                        item.permalink,
                    )
                    for item in items
                ],
            )
            connection.commit()

    def insert_normalized_reddit_items(self, items: list[NormalizedRedditItem]) -> None:
        with self.db.connect() as connection:
            connection.executemany(
                """
                INSERT OR IGNORE INTO normalized_reddit_items
                (item_id, source_id, subreddit, item_type, author, text, created_at, url, engagement_score, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.item_id,
                        item.source_id,
                        item.subreddit,
                        item.item_type,
                        item.author,
                        item.text,
                        item.created_at.isoformat(),
                        item.url,
                        item.engagement_score,
                        json.dumps(item.metadata),
                    )
                    for item in items
                ],
            )
            connection.commit()

    def insert_ticker_mentions(self, mentions: list[ExtractedTickerMention]) -> None:
        with self.db.connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO ticker_mentions
                (mention_id, item_id, ticker, company_name, mention_count, confidence, extraction_method)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        mention.mention_id,
                        mention.item_id,
                        mention.ticker,
                        mention.company_name,
                        mention.mention_count,
                        mention.confidence,
                        mention.extraction_method,
                    )
                    for mention in mentions
                ],
            )
            connection.commit()

    def insert_market_snapshots(self, snapshots: list[MarketSnapshot]) -> None:
        with self.db.connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO market_snapshots
                (ticker, as_of_date, close, volume, market_cap, return_1d, return_3d, return_5d)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        snapshot.ticker,
                        snapshot.as_of_date.isoformat(),
                        snapshot.close,
                        snapshot.volume,
                        snapshot.market_cap,
                        snapshot.return_1d,
                        snapshot.return_3d,
                        snapshot.return_5d,
                    )
                    for snapshot in snapshots
                ],
            )
            connection.commit()

    def insert_daily_stock_aggregates(self, aggregates: list[AggregatedStockDailyFeatures]) -> None:
        with self.db.connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO daily_stock_aggregates
                (run_date, ticker, mention_count, unique_authors, weighted_sentiment, anomaly_score, baseline_mentions, discussion_count, source_item_ids_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        aggregate.run_date.isoformat(),
                        aggregate.ticker,
                        aggregate.mention_count,
                        aggregate.unique_authors,
                        aggregate.weighted_sentiment,
                        aggregate.anomaly_score,
                        aggregate.baseline_mentions,
                        aggregate.discussion_count,
                        json.dumps(aggregate.source_item_ids),
                    )
                    for aggregate in aggregates
                ],
            )
            connection.commit()

    def insert_classifications(self, classifications: list[LLMClassificationResult]) -> None:
        with self.db.connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO classifications
                (classification_id, ticker, item_id, discussion_type, confidence, summary)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        classification.classification_id,
                        classification.ticker,
                        classification.item_id,
                        classification.discussion_type,
                        classification.confidence,
                        classification.summary,
                    )
                    for classification in classifications
                ],
            )
            connection.commit()

    def insert_report_rows(self, rows: list[ReportRow]) -> None:
        with self.db.connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO report_rows
                (run_date, ticker, company_name, anomaly_score, mention_count, unique_authors, weighted_sentiment, discussion_type, lead_lag_label, pump_risk_score, signal_quality, return_1d, return_3d, short_explanation, suggested_action)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row.run_date.isoformat(),
                        row.ticker,
                        row.company_name,
                        row.anomaly_score,
                        row.mention_count,
                        row.unique_authors,
                        row.weighted_sentiment,
                        row.discussion_type,
                        row.lead_lag_label,
                        row.pump_risk_score,
                        row.signal_quality,
                        row.return_1d,
                        row.return_3d,
                        row.short_explanation,
                        row.suggested_action,
                    )
                    for row in rows
                ],
            )
            connection.commit()

    def start_run(self, run_id: str, run_date: str, stage: str) -> None:
        with self.db.connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO run_metadata
                (run_id, run_date, stage, status, started_at, ended_at, processed_count, error_message)
                VALUES (?, ?, ?, ?, ?, NULL, 0, NULL)
                """,
                (run_id, run_date, stage, "running", datetime.utcnow().isoformat()),
            )
            connection.commit()

    def finish_run(self, run_id: str, status: str, processed_count: int, error_message: str | None = None) -> None:
        with self.db.connect() as connection:
            connection.execute(
                """
                UPDATE run_metadata
                SET status = ?, ended_at = ?, processed_count = ?, error_message = ?
                WHERE run_id = ?
                """,
                (status, datetime.utcnow().isoformat(), processed_count, error_message, run_id),
            )
            connection.commit()

    def fetch_table_count(self, table_name: str) -> int:
        with self.db.connect() as connection:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
            return int(row["count"])
