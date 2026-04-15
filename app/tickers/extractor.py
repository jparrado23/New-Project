from __future__ import annotations

import re

from app.models.reddit import ExtractedTickerMention, NormalizedRedditItem


class TickerExtractor:
    def __init__(self, stock_universe: dict[str, str]) -> None:
        self.stock_universe = stock_universe
        self.pattern = re.compile(r"\b[A-Z]{1,5}\b")

    def extract(self, items: list[NormalizedRedditItem]) -> list[ExtractedTickerMention]:
        mentions: list[ExtractedTickerMention] = []
        for item in items:
            matches = {token for token in self.pattern.findall(item.text) if token in self.stock_universe}
            for ticker in matches:
                mentions.append(
                    ExtractedTickerMention(
                        mention_id=f"{item.item_id}:{ticker}",
                        item_id=item.item_id,
                        ticker=ticker,
                        company_name=self.stock_universe.get(ticker),
                        confidence=0.4,
                        extraction_method="regex-universe",
                    )
                )
        return mentions
