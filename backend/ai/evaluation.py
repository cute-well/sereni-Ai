"""Lightweight evaluation helpers for offline sanity checks."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

Label = str


def precision_recall_f1(y_true: Sequence[Label], y_pred: Sequence[Label]) -> Dict[str, float]:
    """Micro-averaged precision/recall/F1 for single-label classification."""
    assert len(y_true) == len(y_pred), "y_true and y_pred must align"

    total = len(y_true)
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    fp = total - tp
    fn = fp  # micro-average with equal lengths implies fp==fn

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def confusion_matrix(y_true: Sequence[Label], y_pred: Sequence[Label]) -> Dict[Label, Dict[Label, int]]:
    labels = sorted(set(y_true) | set(y_pred))
    matrix = {actual: {pred: 0 for pred in labels} for actual in labels}
    for actual, pred in zip(y_true, y_pred):
        matrix[actual][pred] += 1
    return matrix


def simulate_evaluation(samples: Iterable[Tuple[str, Label]], predictor) -> Dict[str, object]:
    """Run a predictor(text)->label over samples and compute metrics."""
    y_true: List[Label] = []
    y_pred: List[Label] = []

    for text, label in samples:
        y_true.append(label)
        y_pred.append(predictor(text))

    metrics = precision_recall_f1(y_true, y_pred)
    matrix = confusion_matrix(y_true, y_pred)
    return {"metrics": metrics, "confusion_matrix": matrix}


if __name__ == "__main__":  # pragma: no cover - manual sanity run
    demo_samples = [
        ("I feel hopeless and want to end it all", "high"),
        ("I'm anxious but talking to my therapist", "moderate"),
        ("Today was great!", "low"),
        ("I'm stressed and can't sleep", "moderate"),
        ("I have a plan to kill myself", "high"),
    ]

    from .risk_classifier import classify_risk

    def predict(text: str) -> str:
        return classify_risk(text).level

    results = simulate_evaluation(demo_samples, predict)
    import json

    print(json.dumps(results, indent=2))
