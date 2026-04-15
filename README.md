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

### LLM Configuration

Stage 1 now supports two LLM modes:

- `provider: mock` for local pipeline testing without external API calls
- `provider: openai` for structured classification through the OpenAI Responses API

The OpenAI path expects:

- `OPENAI_API_KEY` exported in your shell or `.env`
- `llm.enabled: true`
- `llm.provider: openai`
- a supported structured-output model such as `gpt-4o-mini`

Codex itself is not the runtime provider for this repository. Codex can help write and debug the code, but the pipeline needs an API-backed model client at execution time.

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

For a quick local smoke test with isolated output, use [config/config.test.yaml](/Users/juanparrado/Documents/New%20project/config/config.test.yaml):

```bash
python -m app.main init-db --config config/config.test.yaml
python -m app.main run-all --date 2026-04-15 --config config/config.test.yaml
```

To test the real LLM path, use [config/config.openai.test.yaml](/Users/juanparrado/Documents/New%20project/config/config.openai.test.yaml) after exporting `OPENAI_API_KEY`:

```bash
export OPENAI_API_KEY="your_api_key_here"
python -m app.main init-db --config config/config.openai.test.yaml
python -m app.main run-all --date 2026-04-15 --config config/config.openai.test.yaml
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
- The OpenAI LLM path is implemented for structured discussion classification, but the surrounding shortlist and scoring logic is still simplistic.
- Pipeline stages are orchestrated in `run-all`; several stage-specific commands are still scaffolds.

## Planned Stage 2 Improvements

- Real Reddit provider integration with rate-limit handling and comment depth controls
- Better ticker/entity disambiguation for US equities
- Historical baselines for anomaly and lead/lag detection
- Tiered shortlist routing into LLM classification and summarization
- More credible discussion typing and pump/meme heuristics
- Backtesting-oriented feature views and benchmark comparisons
