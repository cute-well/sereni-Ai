"""Text preprocessing and sentiment scoring pipeline."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

WORD_RE = re.compile(r"[\w']+")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
MULTISPACE_RE = re.compile(r"\s+")


def _load_sia() -> SentimentIntensityAnalyzer:
    """Load VADER lexicon if present; raise clear error otherwise."""
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError as exc:  # pragma: no cover - startup guard
        raise RuntimeError(
            "VADER lexicon not found. Run 'python -m nltk.downloader vader_lexicon' during build/deploy."
        ) from exc
    return SentimentIntensityAnalyzer()


sia = _load_sia()


def clean_text(text: str) -> str:
    """Normalize text by stripping URLs, HTML tags, and collapsing whitespace."""
    if not text:
        return ""
    text = URL_RE.sub("", text)
    text = HTML_TAG_RE.sub("", text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = MULTISPACE_RE.sub(" ", text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    """Lowercase tokenization with word characters preserved."""
    cleaned = clean_text(text).lower()
    return WORD_RE.findall(cleaned)


def extract_features(text: str) -> Dict[str, float]:
    """Lightweight lexical features to complement VADER scores."""
    tokens = tokenize(text)
    length = len(tokens)
    exclamations = text.count("!")
    questions = text.count("?")
    uppercase_ratio = _uppercase_ratio(text)
    return {
        "token_count": float(length),
        "exclamations": float(exclamations),
        "questions": float(questions),
        "uppercase_ratio": uppercase_ratio,
    }


def sentiment_score(text: str) -> Tuple[float, Dict[str, float]]:
    """Return compound sentiment score and detailed polarity breakdown."""
    cleaned = clean_text(text)
    scores = sia.polarity_scores(cleaned)
    return scores["compound"], scores


def _uppercase_ratio(text: str) -> float:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 0.0
    uppercase = sum(1 for ch in letters if ch.isupper())
    return round(uppercase / len(letters), 4)
