"""Confidence estimation combining sentiment intensity and risk keywords."""

from __future__ import annotations

from typing import Dict

from .ml_pipeline import sentiment_score
from .risk_classifier import classify_risk


def compute_confidence(text: str) -> Dict[str, float | str | dict]:
    """Return combined confidence and supporting signals.

    Confidence is a weighted blend of absolute sentiment magnitude and
    number of risk keyword matches, capped at 1.0.
    """
    compound, polarity = sentiment_score(text)
    risk = classify_risk(text)

    sentiment_signal = min(1.0, abs(compound))
    keyword_signal = min(1.0, len(risk.matched_terms) * 0.2)

    confidence = round(min(1.0, 0.6 * sentiment_signal + 0.4 * keyword_signal), 4)

    return {
        "confidence": confidence,
        "sentiment_compound": compound,
        "risk_level": risk.level,
        "matched_terms": risk.matched_terms,
        "signals": {
            "sentiment_signal": sentiment_signal,
            "keyword_signal": keyword_signal,
            "polarity": polarity,
        },
    }
