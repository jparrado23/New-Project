# Reddit US Stocks Signal Pipeline

Stage 1 provides a production-style Python skeleton for a daily Reddit-based US stock intelligence workflow. The current goal is local execution, SQLite persistence, and a report for human review rather than automated trading.

## Setup

1. Create a Python 3.11+ virtual environment.
2. Install the project with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

3. Copy environment defaults if needed:

```bash
cp .env.example .env
```

## Configuration

The pipeline reads YAML configuration validated by Pydantic. A sample file lives at [config/config.example.yaml](/Users/juanparrado/Documents/New project/config/config.example.yaml). Key settings include:

- selected subreddits
- comment ingestion toggle
- lookback window
- database/report paths
- shortlist thresholds
- market data provider settings
- LLM placeholder settings
- logging settings

Set `APP_CONFIG_PATH` or pass `--config` on the CLI.

## Database Initialization

```bash
python -m app.main init-db --config config/config.example.yaml
```

This creates the SQLite schema for:

- raw Reddit items
- normalized Reddit items
- ticker mentions
- market snapshots
- daily stock aggregates
- LLM classifications
- report rows
- run metadata

## CLI Commands

```bash
python -m app.main ingest --config config/config.example.yaml
python -m app.main extract-tickers --config config/config.example.yaml
python -m app.main fetch-market --date 2026-04-15 --config config/config.example.yaml
python -m app.main run-all --date 2026-04-15 --config config/config.example.yaml
```

Implemented Stage 1 commands are runnable with mock providers. The `aggregate`, `classify`, `detect-signals`, and `report` commands currently exist as scaffolding placeholders.

## Reports

`run-all` writes:

- Markdown report to `reports/report_YYYY-MM-DD.md`
- CSV report to `reports/report_YYYY-MM-DD.csv`

Report rows already expose the intended downstream shape:

- `ticker`
- `company_name`
- `anomaly_score`
- `mention_count`
- `unique_authors`
- `weighted_sentiment`
- `discussion_type`
- `lead_lag_label`
- `pump_risk_score`
- `signal_quality`
- `return_1d`
- `return_3d`
- `short_explanation`
- `suggested_action`

## Testing

```bash
pytest
```

The test suite covers config loading, DB initialization, repository plumbing, CLI invocation, and report formatting.

## Stage 1 Limitations

- Reddit ingestion uses a mock provider rather than live API integration.
- Market data uses a mock provider instead of a production source.
- Ticker extraction is regex-based and only checks a local universe file.
- Sentiment, anomaly scoring, lead/lag labeling, pump-risk detection, and LLM classification are placeholders.
- Pipeline stages are orchestrated in `run-all`; several stage-specific commands are still scaffolds.

## Planned Stage 2 Improvements

- Real Reddit provider integration with rate-limit handling and comment depth controls
- Better ticker/entity disambiguation for US equities
- Historical baselines for anomaly and lead/lag detection
- Tiered shortlist routing into LLM classification and summarization
- More credible discussion typing and pump/meme heuristics
- Backtesting-oriented feature views and benchmark comparisons
