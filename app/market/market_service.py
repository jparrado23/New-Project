from __future__ import annotations

from datetime import date

from app.models.market import MarketSnapshot
from app.storage.repositories import PipelineRepository


class MarketDataService:
    def __init__(self, provider, repository: PipelineRepository) -> None:
        self.provider = provider
        self.repository = repository

    def fetch_and_store(self, tickers: list[str], as_of_date: date) -> list[MarketSnapshot]:
        snapshots = self.provider.fetch_snapshots(tickers, as_of_date)
        self.repository.insert_market_snapshots(snapshots)
        return snapshots
