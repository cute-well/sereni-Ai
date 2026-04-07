from backend.ai import ml_pipeline


def test_clean_text_removes_urls_and_html():
    text = "Hello <b>world</b> visit https://example.com"
    cleaned = ml_pipeline.clean_text(text)
    assert "example.com" not in cleaned
    assert "<b>" not in cleaned


def test_sentiment_score_returns_compound_and_polarity():
    compound, polarity = ml_pipeline.sentiment_score("I am happy")
    assert isinstance(compound, float)
    assert isinstance(polarity, dict)
    assert "compound" in polarity
