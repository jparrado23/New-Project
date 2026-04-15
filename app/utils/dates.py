from __future__ import annotations

from datetime import date


def parse_run_date(raw: str | None) -> date:
    return date.fromisoformat(raw) if raw else date.today()
