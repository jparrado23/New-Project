from pathlib import Path

from app.storage import Database, PipelineRepository


def test_initialize_db(tmp_path: Path):
    db = Database(str(tmp_path / "pipeline.db"))
    db.initialize()
    repo = PipelineRepository(db)
    assert repo.fetch_table_count("run_metadata") == 0
