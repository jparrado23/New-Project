from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from uuid import uuid4

import typer

from app.config import AppConfig, load_config
from app.ingestion import MockRedditProvider, RedditIngestionService
from app.market import MarketDataService, MockMarketDataProvider
from app.models.market import AggregatedStockDailyFeatures
from app.nlp import LightweightNLP, MockLLMClassifier, build_llm_classifier
from app.reporting import render_markdown_report, write_csv_report
from app.signals import compute_anomaly_scores, synthesize_signals
from app.storage import Database, PipelineRepository
from app.tickers import TickerExtractor, load_stock_universe
from app.utils import configure_logging, get_logger, parse_run_date

cli = typer.Typer(help="Reddit US stocks signal pipeline CLI")
logger = get_logger(__name__)


def _bootstrap(config_path: str | None) -> tuple[AppConfig, Database, PipelineRepository]:
    config = load_config(config_path)
    configure_logging(config.logging.level, config.logging.json)
    db = Database(config.database_path)
    repo = PipelineRepository(db)
    return config, db, repo


def _run_stage(repo: PipelineRepository, run_date: str, stage: str, fn):
    run_id = f"{stage}-{uuid4()}"
    repo.start_run(run_id, run_date, stage)
    try:
        count = fn()
        repo.finish_run(run_id, "completed", count)
        return count
    except Exception as exc:
        repo.finish_run(run_id, "failed", 0, str(exc))
        raise


def _shortlist_tickers(
    aggregates: list[AggregatedStockDailyFeatures], config: AppConfig
) -> list[AggregatedStockDailyFeatures]:
    shortlisted = [
        aggregate
        for aggregate in aggregates
        if aggregate.mention_count >= config.shortlist.min_mentions
        and aggregate.unique_authors >= config.shortlist.min_unique_authors
        and aggregate.anomaly_score >= config.shortlist.anomaly_score_threshold
    ]
    shortlisted.sort(key=lambda item: (item.anomaly_score, item.mention_count, item.unique_authors), reverse=True)
    return shortlisted[: config.llm.max_items_per_run]


@cli.command("init-db")
def init_db(config_path: str | None = typer.Option(None, "--config")) -> None:
    _, db, _ = _bootstrap(config_path)
    db.initialize()
    typer.echo(f"Initialized database at {db.path}")


@cli.command("run-all")
def run_all(
    date_str: str | None = typer.Option(None, "--date"),
    config_path: str | None = typer.Option(None, "--config"),
) -> None:
    run_date = parse_run_date(date_str)
    config, db, repo = _bootstrap(config_path)
    db.initialize()

    report_rows = []
    markdown_path = Path(config.report_output_dir) / f"report_{run_date.isoformat()}.md"
    csv_path = Path(config.report_output_dir) / f"report_{run_date.isoformat()}.csv"

    def _execute() -> int:
        nonlocal report_rows
        provider = MockRedditProvider()
        _, normalized_items = RedditIngestionService(provider, repo).ingest(config)

        stock_universe = load_stock_universe(config.stock_universe_path)
        mentions = TickerExtractor(stock_universe).extract(normalized_items)
        repo.insert_ticker_mentions(mentions)

        tickers = sorted({mention.ticker for mention in mentions})
        market_snapshots = MarketDataService(MockMarketDataProvider(), repo).fetch_and_store(tickers, run_date)

        nlp = LightweightNLP()
        grouped_item_ids: dict[str, list[str]] = defaultdict(list)
        grouped_authors: dict[str, set[str]] = defaultdict(set)
        weighted_sentiment: dict[str, float] = defaultdict(float)
        mention_counts: dict[str, int] = defaultdict(int)

        item_by_id = {item.item_id: item for item in normalized_items}
        for mention in mentions:
            mention_counts[mention.ticker] += 1
            grouped_item_ids[mention.ticker].append(mention.item_id)
            author = item_by_id[mention.item_id].author
            grouped_authors[mention.ticker].add(author)
            weighted_sentiment[mention.ticker] += nlp.sentiment_score(item_by_id[mention.item_id].text)

        aggregates = [
            AggregatedStockDailyFeatures(
                run_date=run_date,
                ticker=ticker,
                mention_count=mention_counts[ticker],
                unique_authors=len(grouped_authors[ticker]),
                weighted_sentiment=round(weighted_sentiment[ticker] / mention_counts[ticker], 3),
                anomaly_score=0.0,
                baseline_mentions=1.0,
                discussion_count=len(grouped_item_ids[ticker]),
                source_item_ids=grouped_item_ids[ticker],
            )
            for ticker in tickers
        ]
        aggregates = compute_anomaly_scores(aggregates)
        repo.insert_daily_stock_aggregates(aggregates)

        classifications = []
        llm_candidates = _shortlist_tickers(aggregates, config)
        classifier = build_llm_classifier(config.llm) if config.llm.enabled else MockLLMClassifier()
        if config.llm.enabled:
            logger.info(
                "llm_shortlist_selected",
                extra={
                    "candidate_count": len(llm_candidates),
                    "provider": config.llm.provider,
                    "model": config.llm.model,
                },
            )
        for candidate in (llm_candidates if config.llm.enabled else aggregates):
            texts = [item_by_id[item_id].text for item_id in grouped_item_ids[candidate.ticker]]
            classifications.append(classifier.classify_text(candidate.ticker, "\n\n".join(texts)))
        repo.insert_classifications(classifications)

        market_by_ticker = {snapshot.ticker: snapshot for snapshot in market_snapshots}
        classifications_by_ticker = {item.ticker: item for item in classifications}
        _, report_rows = synthesize_signals(
            aggregates, market_by_ticker, classifications_by_ticker, stock_universe
        )
        repo.insert_report_rows(report_rows)

        output_dir = Path(config.report_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        markdown = render_markdown_report(run_date, report_rows)
        markdown_path.write_text(markdown, encoding="utf-8")
        write_csv_report(str(csv_path), report_rows)
        return len(report_rows)

    _run_stage(repo, run_date.isoformat(), "run-all", _execute)

    typer.echo(f"Run complete for {run_date.isoformat()}: {len(report_rows)} report rows")
    typer.echo(f"Markdown report: {markdown_path}")
    typer.echo(f"CSV report: {csv_path}")


@cli.command("ingest")
def ingest(config_path: str | None = typer.Option(None, "--config")) -> None:
    config, db, repo = _bootstrap(config_path)
    db.initialize()
    run_date = parse_run_date(None).isoformat()
    normalized = []

    def _execute() -> int:
        nonlocal normalized
        _, normalized = RedditIngestionService(MockRedditProvider(), repo).ingest(config)
        return len(normalized)

    _run_stage(repo, run_date, "ingest", _execute)
    typer.echo(f"Ingested {len(normalized)} normalized items")


@cli.command("extract-tickers")
def extract_tickers(config_path: str | None = typer.Option(None, "--config")) -> None:
    config, db, repo = _bootstrap(config_path)
    db.initialize()
    mentions = []

    def _execute() -> int:
        nonlocal mentions
        _, normalized = RedditIngestionService(MockRedditProvider(), repo).ingest(config)
        mentions = TickerExtractor(load_stock_universe(config.stock_universe_path)).extract(normalized)
        repo.insert_ticker_mentions(mentions)
        return len(mentions)

    _run_stage(repo, parse_run_date(None).isoformat(), "extract-tickers", _execute)
    typer.echo(f"Extracted {len(mentions)} ticker mentions")


@cli.command("fetch-market")
def fetch_market(
    date_str: str | None = typer.Option(None, "--date"),
    config_path: str | None = typer.Option(None, "--config"),
) -> None:
    run_date = parse_run_date(date_str)
    config, db, repo = _bootstrap(config_path)
    db.initialize()
    snapshots = []

    def _execute() -> int:
        nonlocal snapshots
        snapshots = MarketDataService(MockMarketDataProvider(), repo).fetch_and_store(
            sorted(load_stock_universe(config.stock_universe_path).keys())[:3], run_date
        )
        return len(snapshots)

    _run_stage(repo, run_date.isoformat(), "fetch-market", _execute)
    typer.echo(f"Fetched {len(snapshots)} market snapshots")


@cli.command("aggregate")
def aggregate(date_str: str | None = typer.Option(None, "--date")) -> None:
    run_date = parse_run_date(date_str)
    _, db, repo = _bootstrap(None)
    db.initialize()
    _run_stage(repo, run_date.isoformat(), "aggregate", lambda: 0)
    typer.echo(f"Aggregate stage placeholder for {run_date.isoformat()}")


@cli.command("classify")
def classify(date_str: str | None = typer.Option(None, "--date")) -> None:
    run_date = parse_run_date(date_str)
    _, db, repo = _bootstrap(None)
    db.initialize()
    _run_stage(repo, run_date.isoformat(), "classify", lambda: 0)
    typer.echo(f"Classify stage placeholder for {run_date.isoformat()}")


@cli.command("detect-signals")
def detect_signals(date_str: str | None = typer.Option(None, "--date")) -> None:
    run_date = parse_run_date(date_str)
    _, db, repo = _bootstrap(None)
    db.initialize()
    _run_stage(repo, run_date.isoformat(), "detect-signals", lambda: 0)
    typer.echo(f"Signal detection placeholder for {run_date.isoformat()}")


@cli.command("report")
def report(date_str: str | None = typer.Option(None, "--date")) -> None:
    run_date = parse_run_date(date_str)
    _, db, repo = _bootstrap(None)
    db.initialize()
    _run_stage(repo, run_date.isoformat(), "report", lambda: 0)
    typer.echo(f"Report stage placeholder for {run_date.isoformat()}")


if __name__ == "__main__":
    cli()
