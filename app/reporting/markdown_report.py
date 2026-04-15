from __future__ import annotations

from datetime import date

from app.models.report import ReportRow


def render_markdown_report(run_date: date, rows: list[ReportRow]) -> str:
    lines = [
        f"# Reddit US Stocks Signal Report - {run_date.isoformat()}",
        "",
        f"Generated rows: {len(rows)}",
        "",
        "| Ticker | Company | Anomaly | Mentions | Authors | Discussion | Lead/Lag | Pump Risk | Quality | 1D | 3D | Action |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.ticker} | {row.company_name or ''} | {row.anomaly_score:.2f} | {row.mention_count} | "
            f"{row.unique_authors} | {row.discussion_type} | {row.lead_lag_label} | {row.pump_risk_score:.2f} | "
            f"{row.signal_quality:.2f} | {row.return_1d or 0:.2%} | {row.return_3d or 0:.2%} | {row.suggested_action} |"
        )
    return "\n".join(lines) + "\n"
