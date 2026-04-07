from backend.ai.risk_classifier import classify_risk


def test_classify_high_risk_phrase():
    result = classify_risk("I want to kill myself")
    assert result.level == "high"
    assert any("kill" in term for term in result.matched_terms)


def test_classify_moderate_risk_phrase():
    result = classify_risk("I feel anxious and stressed")
    assert result.level == "moderate"


def test_classify_low_risk_phrase():
    result = classify_risk("I am doing okay and had a good day")
    assert result.level == "low"
