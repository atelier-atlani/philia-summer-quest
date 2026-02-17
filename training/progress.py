"""training/progress.py – Load / save progression in data/progress.json."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from training.profile import UserProfile

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


def save_profile(profile: UserProfile) -> None:
    """Save enriched UserProfile into progress.json."""
    progress = load_progress()
    progress["profile"] = profile.to_dict()
    save_progress(progress)


def load_profile() -> UserProfile:
    """Load UserProfile from progress.json (returns default if empty)."""
    progress = load_progress()
    profile_data = progress.get("profile", {})
    if not profile_data:
        return UserProfile()
    return UserProfile.from_dict(profile_data)


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


def save_lacunes(lacunes: list[str]) -> None:
    """Stocke les lacunes détectées dans le profil stagiaire."""
    if not lacunes:
        return
    progress = load_progress()
    existing = progress.get("lacunes", [])
    for lacune in lacunes:
        if lacune not in existing:
            existing.append(lacune)
    progress["lacunes"] = existing[-20:]
    save_progress(progress)


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
