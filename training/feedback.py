"""training/feedback.py – Collecte de feedback testeur."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

FEEDBACK_FILE = Path("data/feedback.json")


def save_feedback(entry: dict) -> None:
    """Ajoute un feedback au fichier JSON."""
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    feedbacks = []
    if FEEDBACK_FILE.exists():
        try:
            feedbacks = json.loads(FEEDBACK_FILE.read_text())
        except Exception:
            feedbacks = []

    entry["timestamp"] = datetime.now().isoformat()
    feedbacks.append(entry)
    FEEDBACK_FILE.write_text(json.dumps(feedbacks, ensure_ascii=False, indent=2))


def load_feedbacks() -> list:
    """Charge tous les feedbacks."""
    if not FEEDBACK_FILE.exists():
        return []
    try:
        return json.loads(FEEDBACK_FILE.read_text())
    except Exception:
        return []
