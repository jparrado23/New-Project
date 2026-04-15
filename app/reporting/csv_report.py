from __future__ import annotations

import csv
from pathlib import Path

from app.models.report import ReportRow


def write_csv_report(path: str, rows: list[ReportRow]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ReportRow.model_fields.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.model_dump())
