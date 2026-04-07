"""Rule-based risk classification for safety routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

from .ml_pipeline import tokenize

HIGH_RISK = {
    "suicide",
    "kill myself",
    "kill me",
    "end it",
    "jump",
    "overdose",
    "hang",
    "gun",
    "shotgun",
    "no reason to live",
    "self harm",
    "self-harm",
    "cutting",
    "cut myself",
    "bleed",
    "die",
    "dying",
    "can't go on",
}

MODERATE_RISK = {
    "depressed",
    "anxious",
    "panic",
    "panic attack",
    "can't sleep",
    "insomnia",
    "hopeless",
    "lonely",
    "worthless",
    "overwhelmed",
    "crying",
    "fear",
    "scared",
    "stressed",
    "burned out",
}

PROTECTIVE = {
    "therapist",
    "counselor",
    "friend",
    "family",
    "support",
    "help",
    "call",
    "talk",
    "safe",
    "calm",
    "cope",
}


@dataclass
class RiskResult:
    level: str
    matched_terms: List[str]
    protective_terms: List[str]
    reasoning: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "level": self.level,
            "matched_terms": self.matched_terms,
            "protective_terms": self.protective_terms,
            "reasoning": self.reasoning,
        }


def classify_risk(text: str) -> RiskResult:
    tokens = tokenize(text)
    lowered = " ".join(tokens)

    matched_high = _find_matches(lowered, HIGH_RISK)
    matched_mod = _find_matches(lowered, MODERATE_RISK)
    matched_prot = _find_matches(lowered, PROTECTIVE)

    if matched_high:
        level = "high"
        reasoning = "High-risk phrases detected; escalate to crisis flow."
    elif matched_mod:
        level = "moderate"
        reasoning = "Moderate-risk indicators present; monitor closely."
    else:
        level = "low"
        reasoning = "No acute risk keywords detected."

    if matched_prot:
        reasoning += " Protective factors mentioned."

    return RiskResult(level, matched_high or matched_mod, matched_prot, reasoning)


def _find_matches(text: str, keywords: Set[str]) -> List[str]:
    found = []
    for phrase in keywords:
        if phrase in text:
            found.append(phrase)
    return found
