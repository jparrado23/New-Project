from datetime import datetime
from pathlib import Path

from app.models.reddit import RedditRawItem
from app.storage import Database, PipelineRepository


def test_repository_insert_raw_items(tmp_path: Path):
    db = Database(str(tmp_path / "pipeline.db"))
    db.initialize()
    repo = PipelineRepository(db)
    repo.insert_raw_reddit_items(
        [
            RedditRawItem(
                source_id="abc",
                subreddit="stocks",
                item_type="post",
                author="user1",
                body="Watching AAPL",
                created_utc=datetime.utcnow(),
            )
        ]
    )
    assert repo.fetch_table_count("raw_reddit_items") == 1
