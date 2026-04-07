"""Security utilities: input sanitization and lightweight rate limiting."""

from __future__ import annotations

import html
import re
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Callable, Deque, Dict, Tuple

from flask import abort

# Simple in-memory sliding window limiter (per key). Suitable for single-instance.
# For production multi-instance, move to Redis (maintained separately).
RateWindow = Tuple[int, int]  # (limit, window_seconds)
_request_log: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=256))
_request_lock = Lock()

SCRIPT_TAG_RE = re.compile(r"<\s*/?\s*script[^>]*>", re.IGNORECASE)


def sanitize_text(text: str) -> str:
    """Basic sanitization: escape HTML and strip <script> tags."""
    if text is None:
        return ""
    escaped = html.escape(text)
    sanitized = re.sub(SCRIPT_TAG_RE, "", escaped)
    return sanitized.strip()


def rate_limit(key: str, window: RateWindow = (60, 60)) -> None:
    """Enforce a simple sliding window rate limit (thread-aware, bounded deque)."""
    limit, window_seconds = window
    now = time.time()

    with _request_lock:
        events = _request_log[key]
        while events and events[0] <= now - window_seconds:
            events.popleft()
        if len(events) >= limit:
            abort(429, description="Rate limit exceeded. Please slow down.")
        events.append(now)


def rate_limited(window: RateWindow = (60, 60)) -> Callable:
    """Decorator to rate limit a view based on remote address."""

    def decorator(fn: Callable):
        def wrapper(*args, **kwargs):
            from flask import request

            client_key = request.remote_addr or "anonymous"
            rate_limit(client_key, window)
            return fn(*args, **kwargs)

        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper

    return decorator
