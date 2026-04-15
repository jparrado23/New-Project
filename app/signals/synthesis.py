from __future__ import annotations

from app.models.market import AggregatedStockDailyFeatures, MarketSnapshot
from app.models.report import ReportRow
from app.models.signal import CandidateSignal, LLMClassificationResult
from app.signals.lead_lag import label_lead_lag
from app.signals.pump_risk import score_pump_risk


def synthesize_signals(
    features: list[AggregatedStockDailyFeatures],
    market_by_ticker: dict[str, MarketSnapshot],
    classifications: dict[str, LLMClassificationResult],
    company_names: dict[str, str],
) -> tuple[list[CandidateSignal], list[ReportRow]]:
    signals: list[CandidateSignal] = []
    report_rows: list[ReportRow] = []
    for feature in sorted(features, key=lambda item: item.anomaly_score, reverse=True):
        market = market_by_ticker.get(feature.ticker)
        classification = classifications.get(feature.ticker)
        discussion_type = classification.discussion_type if classification else "unknown"
        lead_lag = label_lead_lag(market.return_1d if market else None, feature.anomaly_score)
        pump_risk = score_pump_risk(feature.mention_count, feature.unique_authors, discussion_type)
        quality = round(max(0.0, feature.anomaly_score - pump_risk + (feature.unique_authors * 0.1)), 2)
        explanation = (
            f"Mentions={feature.mention_count}, authors={feature.unique_authors}, "
            f"type={discussion_type}, lead_lag={lead_lag}."
        )
        signal = CandidateSignal(
            signal_id=f"{feature.run_date}:{feature.ticker}",
            run_date=feature.run_date,
            ticker=feature.ticker,
            company_name=company_names.get(feature.ticker),
            anomaly_score=feature.anomaly_score,
            mention_count=feature.mention_count,
            unique_authors=feature.unique_authors,
            weighted_sentiment=feature.weighted_sentiment,
            discussion_type=discussion_type,
            lead_lag_label=lead_lag,
            pump_risk_score=pump_risk,
            signal_quality=quality,
            return_1d=market.return_1d if market else None,
            return_3d=market.return_3d if market else None,
            short_explanation=explanation,
            suggested_action="Manual review",
        )
        signals.append(signal)
        report_rows.append(ReportRow(**signal.model_dump()))
    return signals, report_rows
