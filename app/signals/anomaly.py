from __future__ import annotations

from app.models.market import AggregatedStockDailyFeatures


def compute_anomaly_scores(features: list[AggregatedStockDailyFeatures]) -> list[AggregatedStockDailyFeatures]:
    scored: list[AggregatedStockDailyFeatures] = []
    for feature in features:
        baseline = feature.baseline_mentions or 1.0
        feature.anomaly_score = round(feature.mention_count / baseline, 3)
        scored.append(feature)
    return scored
