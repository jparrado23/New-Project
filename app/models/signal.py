from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class LLMClassificationResult(BaseModel):
    classification_id: str
    ticker: str
    item_id: str | None = None
    discussion_type: str
    confidence: float
    summary: str


class CandidateSignal(BaseModel):
    signal_id: str
    run_date: date
    ticker: str
    company_name: str | None = None
    anomaly_score: float
    mention_count: int
    unique_authors: int
    weighted_sentiment: float
    discussion_type: str
    lead_lag_label: str
    pump_risk_score: float
    signal_quality: float
    return_1d: float | None = None
    return_3d: float | None = None
    short_explanation: str
    suggested_action: str
