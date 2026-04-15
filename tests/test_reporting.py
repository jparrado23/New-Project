from datetime import date

from app.models.report import ReportRow
from app.reporting.markdown_report import render_markdown_report


def test_markdown_report_shape():
    report = render_markdown_report(
        date(2026, 4, 15),
        [
            ReportRow(
                run_date=date(2026, 4, 15),
                ticker="AAPL",
                company_name="Apple Inc.",
                anomaly_score=1.5,
                mention_count=5,
                unique_authors=4,
                weighted_sentiment=0.2,
                discussion_type="thesis-driven",
                lead_lag_label="possible-early-attention",
                pump_risk_score=0.2,
                signal_quality=1.8,
                return_1d=0.01,
                return_3d=0.02,
                short_explanation="placeholder",
                suggested_action="Manual review",
            )
        ],
    )
    assert "# Reddit US Stocks Signal Report - 2026-04-15" in report
    assert "| AAPL | Apple Inc." in report
