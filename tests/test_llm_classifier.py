from app.config import LLMConfig
from app.nlp.llm_classifier import MockLLMClassifier, build_llm_classifier


def test_build_llm_classifier_returns_mock_when_disabled():
    classifier = build_llm_classifier(LLMConfig(enabled=False, provider="mock"))
    assert isinstance(classifier, MockLLMClassifier)


def test_mock_classifier_returns_expected_shape():
    classifier = MockLLMClassifier()
    result = classifier.classify_text("AAPL", "Why AAPL margins may improve because services revenue is growing.")
    assert result.ticker == "AAPL"
    assert result.discussion_type in {"thesis-driven", "headline-chatter"}
    assert result.summary
