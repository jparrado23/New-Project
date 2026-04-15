from __future__ import annotations

import sqlite3
from pathlib import Path

from app.storage.schema import SCHEMA_STATEMENTS


class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            for statement in SCHEMA_STATEMENTS:
                connection.execute(statement)
            connection.commit()
