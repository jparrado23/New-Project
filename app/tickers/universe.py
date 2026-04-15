from __future__ import annotations

import csv
from pathlib import Path


def load_stock_universe(path: str) -> dict[str, str]:
    file_path = Path(path)
    if not file_path.exists():
        return {"AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "NVDA": "NVIDIA Corp."}

    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row["ticker"].upper(): row["company_name"] for row in reader}
