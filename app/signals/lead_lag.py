from __future__ import annotations


def label_lead_lag(return_1d: float | None, anomaly_score: float) -> str:
    if return_1d is not None and return_1d > 0.03 and anomaly_score < 1.5:
        return "lagging-price-move"
    if anomaly_score >= 1.5:
        return "possible-early-attention"
    return "unclear"
