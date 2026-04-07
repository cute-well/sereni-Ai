"""Analytics service for sentiment trends and grounding usage."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Tuple

from backend.ai.ml_pipeline import sentiment_score
from config import BaseConfig

# In-memory stores; swap to persistent analytics/warehouse later.
SentimentPoint = Tuple[datetime, float]
_grounding_usage: Dict[str, int] = defaultdict(int)
_sentiment_history: Dict[str, Deque[SentimentPoint]] = defaultdict(
    lambda: deque(maxlen=BaseConfig.ANALYTICS_MAX_POINTS)
)
DEFAULT_WINDOW = timedelta(hours=24)


def track_sentiment(user_id: str, text: str) -> float:
    """Compute and store sentiment compound score for a user."""
    compound, _ = sentiment_score(text)
    history = _sentiment_history[user_id]
    history.append((datetime.utcnow(), compound))
    return compound


def sentiment_trend(user_id: str, window: timedelta = DEFAULT_WINDOW) -> Dict[str, float]:
    """Return average and last sentiment within a time window."""
    cutoff = datetime.utcnow() - window
    history = _sentiment_history[user_id]
    filtered = [score for ts, score in history if ts >= cutoff]

    if not filtered:
        return {"average": 0.0, "last": 0.0, "count": 0}

    avg = sum(filtered) / len(filtered)
    return {"average": round(avg, 4), "last": round(filtered[-1], 4), "count": len(filtered)}


def record_grounding_usage(user_id: str) -> int:
    """Increment and return grounding usage count for a user."""
    _grounding_usage[user_id] += 1
    return _grounding_usage[user_id]


def grounding_usage(user_id: str) -> int:
    return _grounding_usage.get(user_id, 0)


def aggregate_trends(window: timedelta = DEFAULT_WINDOW) -> Dict[str, object]:
    """Aggregate sentiment averages and grounding counts across users."""
    user_stats: List[Dict[str, object]] = []
    for user_id in _sentiment_history.keys():
        trend = sentiment_trend(user_id, window)
        user_stats.append({"user_id": user_id, **trend, "grounding_usage": grounding_usage(user_id)})

    return {
        "users": user_stats,
        "total_grounding": sum(_grounding_usage.values()),
    }
