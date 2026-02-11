"""training/progress.py – Load / save progression in data/progress.json."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _default_progress() -> Dict[str, Any]:
    return {
        "profile": {},
        "current_session": 1,
        "sessions_history": [],
    }


def load_progress() -> Dict[str, Any]:
    """Load training progress from data/progress.json."""
    _ensure_data_dir()
    if not PROGRESS_FILE.exists():
        return _default_progress()
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        for key, default in _default_progress().items():
            if key not in data:
                data[key] = default
        return data
    except Exception:
        return _default_progress()


def save_progress(data: Dict[str, Any]) -> None:
    """Save training progress to data/progress.json."""
    _ensure_data_dir()
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    PROGRESS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def record_session_complete(
    progress: Dict[str, Any],
    session_number: int,
    step_data: Dict[str, Any],
) -> None:
    """Record a completed session and advance to the next one."""
    history = progress.get("sessions_history", [])
    history.append({
        "session": session_number,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "completed_at": datetime.now().isoformat(timespec="seconds"),
        "data": step_data,
    })
    progress["sessions_history"] = history[-120:]
    progress["current_session"] = session_number + 1
    save_progress(progress)
