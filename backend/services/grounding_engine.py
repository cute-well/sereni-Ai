"""5-4-3-2-1 grounding flow with session-scoped state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from flask import session


@dataclass
class GroundingStep:
    prompt: str
    expected_count: int
    sensory_domain: str


FLOW: List[GroundingStep] = [
    GroundingStep("Name five things you can see", 5, "sight"),
    GroundingStep("Name four things you can touch", 4, "touch"),
    GroundingStep("Name three things you can hear", 3, "hearing"),
    GroundingStep("Name two things you can smell", 2, "smell"),
    GroundingStep("Name one thing you can taste", 1, "taste"),
]

SESSION_KEY = "grounding_state"


@dataclass
class GroundingState:
    index: int = 0
    responses: List[List[str]] = field(default_factory=lambda: [[] for _ in range(5)])

    def as_dict(self) -> Dict[str, object]:
        return {"index": self.index, "responses": self.responses}

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "GroundingState":
        if not data:
            return cls()
        return cls(index=int(data.get("index", 0)), responses=data.get("responses", [[] for _ in range(5)]))


class GroundingEngine:
    """Manages the 5-4-3-2-1 grounding exercise per user session."""

    @staticmethod
    def current_state() -> GroundingState:
        stored = session.get(SESSION_KEY, {})
        return GroundingState.from_dict(stored)

    @staticmethod
    def reset() -> GroundingState:
        state = GroundingState()
        session[SESSION_KEY] = state.as_dict()
        return state

    @staticmethod
    def prompt() -> Optional[GroundingStep]:
        state = GroundingEngine.current_state()
        return FLOW[state.index] if state.index < len(FLOW) else None

    @staticmethod
    def record_response(items: List[str]) -> Dict[str, object]:
        state = GroundingEngine.current_state()
        step = GroundingEngine.prompt()

        if step is None:
            return {"completed": True, "message": "Grounding already completed."}

        # Normalize and limit to expected_count
        cleaned = [item.strip() for item in items if item and item.strip()]
        state.responses[state.index] = cleaned[: step.expected_count]
        state.index += 1

        session[SESSION_KEY] = state.as_dict()

        next_step = GroundingEngine.prompt()
        return {
            "completed": next_step is None,
            "next_prompt": next_step.prompt if next_step else None,
            "next_expected": next_step.expected_count if next_step else 0,
            "state": state.as_dict(),
        }

    @staticmethod
    def progress() -> Dict[str, object]:
        state = GroundingEngine.current_state()
        return {
            "current_index": state.index,
            "total_steps": len(FLOW),
            "completed": state.index >= len(FLOW),
            "next": GroundingEngine.prompt().prompt if GroundingEngine.prompt() else None,
            "responses": state.responses,
        }
