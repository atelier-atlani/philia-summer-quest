"""training/engine.py – TrainingSession state machine.

Gère une session de formation : séquence de steps, avancement,
enregistrement des données par step, finalisation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from training.steps import Step, get_steps_for_session, STEP_LABELS
from training.content import get_session_theme, TOTAL_SESSIONS
from training.progress import load_progress, save_progress, record_session_complete


@dataclass
class TrainingSession:
    """State machine for a single training session (45 min – 1 h)."""

    session_number: int
    steps: List[Step] = field(default_factory=list)
    current_step_index: int = 0
    step_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.steps:
            self.steps = get_steps_for_session(self.session_number)

    # --- properties ---

    @property
    def current_step(self) -> Optional[Step]:
        if self.current_step_index >= len(self.steps):
            return None
        return self.steps[self.current_step_index]

    @property
    def is_complete(self) -> bool:
        return self.current_step_index >= len(self.steps)

    @property
    def theme(self) -> Dict[str, str]:
        return get_session_theme(self.session_number)

    @property
    def previous_theme(self) -> Dict[str, str]:
        """Theme from previous session (for WhatsApp J+1)."""
        if self.session_number <= 1:
            return get_session_theme(1)
        return get_session_theme(self.session_number - 1)

    @property
    def progress_pct(self) -> float:
        if not self.steps:
            return 0.0
        return min(self.current_step_index / len(self.steps), 1.0)

    @property
    def total_sessions(self) -> int:
        return TOTAL_SESSIONS

    # --- actions ---

    def step_label(self) -> str:
        step = self.current_step
        if step is None:
            return "Terminé"
        return STEP_LABELS.get(step, step.value)

    def advance(self) -> None:
        """Move to the next step."""
        if not self.is_complete:
            self.current_step_index += 1

    def record(self, step: Step, data: Dict[str, Any]) -> None:
        """Record data for a completed step."""
        self.step_data[step.value] = data

    def complete(self) -> None:
        """Mark session as complete and persist progress."""
        progress = load_progress()
        record_session_complete(progress, self.session_number, self.step_data)

    # --- serialization for st.session_state ---

    @property
    def a_faire_demain(self) -> str:
        """'A faire demain' stored during synthesis step."""
        synthese = self.step_data.get(Step.SYNTHESE.value, {})
        return synthese.get("a_faire_demain", "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_number": self.session_number,
            "steps": [s.value for s in self.steps],
            "current_step_index": self.current_step_index,
            "step_data": self.step_data,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TrainingSession":
        ts = cls(
            session_number=d["session_number"],
            steps=[Step(v) for v in d["steps"]],
            current_step_index=d.get("current_step_index", 0),
            step_data=d.get("step_data", {}),
        )
        return ts
