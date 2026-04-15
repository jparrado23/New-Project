from __future__ import annotations


def score_pump_risk(mention_count: int, unique_authors: int, discussion_type: str) -> float:
    base = 0.2 if discussion_type == "thesis-driven" else 0.5
    concentration_penalty = 0.2 if unique_authors <= 1 and mention_count > 1 else 0.0
    return min(1.0, round(base + concentration_penalty, 2))
