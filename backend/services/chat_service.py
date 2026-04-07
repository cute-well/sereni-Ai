"""Chat and analysis service layer separating route handling from business logic."""

from __future__ import annotations

from typing import Any, Dict

from flask import current_app

from backend.ai.confidence_score import compute_confidence
from backend.ai.ml_pipeline import extract_features, sentiment_score
from backend.ai.risk_classifier import classify_risk
from backend.services.analytics import record_grounding_usage, sentiment_trend, track_sentiment


class ChatService:
    """Encapsulates sentiment analysis, risk evaluation, and bot reply generation."""

    def __init__(self, risk_threshold: float | None = None) -> None:
        cfg = current_app.config
        self.risk_threshold = risk_threshold or cfg.get("AI_RISK_THRESHOLD", 0.65)

    def analyze_text(self, text: str, user_id: str) -> Dict[str, Any]:
        """Run full analysis pipeline and return structured data."""
        compound, polarity = sentiment_score(text)
        risk = classify_risk(text)
        confidence = compute_confidence(text)
        trend = sentiment_trend(user_id)
        track_sentiment(user_id, text)

        return {
            "sentiment": {"compound": compound, "polarity": polarity},
            "risk": risk.to_dict(),
            "confidence": confidence,
            "trend": trend,
            "features": extract_features(text),
        }

    def build_reply(self, user_message: str, risk_level: str) -> str:
        """Generate a supportive, non-clinical reply based on detected risk."""
        supportive_prefix = "I'm here to listen. "
        if risk_level == "high":
            return (
                supportive_prefix
                + "It sounds really tough. I'm not a clinician, but your safety matters. "
                "Consider reaching out to someone you trust or contacting 988 right away."
            )
        if risk_level == "moderate":
            return supportive_prefix + "Breathing slowly can help. I can guide a grounding exercise if you'd like."
        return supportive_prefix + "Tell me more about what's on your mind."

    def handle_chat(self, text: str, user_id: str) -> Dict[str, Any]:
        """Full chat handling: analysis + response + optional grounding tracking."""
        result = self.analyze_text(text, user_id)
        reply = self.build_reply(text, result["risk"]["level"])

        if any(keyword in text.lower() for keyword in ("ground", "anxious", "panic")):
            record_grounding_usage(user_id)

        return {
            "response": reply,
            "sentiment": result["sentiment"],
            "risk": result["risk"],
            "confidence": result["confidence"],
        }
