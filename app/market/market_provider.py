from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from app.models.market import MarketSnapshot


class MarketDataProvider(ABC):
    @abstractmethod
    def fetch_snapshots(self, tickers: list[str], as_of_date: date) -> list[MarketSnapshot]:
        raise NotImplementedError


class MockMarketDataProvider(MarketDataProvider):
    def fetch_snapshots(self, tickers: list[str], as_of_date: date) -> list[MarketSnapshot]:
        snapshots: list[MarketSnapshot] = []
        for idx, ticker in enumerate(sorted(set(tickers)), start=1):
            snapshots.append(
                MarketSnapshot(
                    ticker=ticker,
                    as_of_date=as_of_date,
                    close=100.0 + idx * 10,
                    volume=1_000_000 * idx,
                    market_cap=10_000_000_000.0 * idx,
                    return_1d=0.01 * idx,
                    return_3d=0.02 * idx,
                    return_5d=0.03 * idx,
                )
            )
        return snapshots
