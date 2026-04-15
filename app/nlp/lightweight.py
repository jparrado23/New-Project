from __future__ import annotations


class LightweightNLP:
    POSITIVE = {"growth", "beat", "strong", "upside", "improving"}
    NEGATIVE = {"dump", "crash", "bagholder", "collapse", "downside"}

    def sentiment_score(self, text: str) -> float:
        lowered = text.lower()
        pos_hits = sum(token in lowered for token in self.POSITIVE)
        neg_hits = sum(token in lowered for token in self.NEGATIVE)
        total = pos_hits + neg_hits
        return 0.0 if total == 0 else (pos_hits - neg_hits) / total
