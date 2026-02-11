"""training/steps.py – Step enum and day sequences.

Jour 1 (onboarding) : 7 steps (pas de WhatsApp)
Jour 2+             : 8 steps (WhatsApp J+1 en ouverture)
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List


class Step(str, Enum):
    PROFIL = "PROFIL"
    WHATSAPP = "WHATSAPP"
    DEBRIEF_WA = "DEBRIEF_WA"
    MINI_COURS = "MINI_COURS"
    QUESTIONS_RAG = "QUESTIONS_RAG"
    COURS_CLES = "COURS_CLES"
    QUIZ = "QUIZ"
    DEBRIEF = "DEBRIEF"
    DEBRIEF_QUIZ = "DEBRIEF_QUIZ"
    SYNTHESE = "SYNTHESE"


# --- Jour 1 : 7 steps (onboarding, pas de WhatsApp) ---
JOUR_1_STEPS: List[Step] = [
    Step.PROFIL,
    Step.MINI_COURS,
    Step.QUESTIONS_RAG,
    Step.COURS_CLES,
    Step.QUIZ,
    Step.DEBRIEF,
    Step.SYNTHESE,
]

# --- Jour 2+ : 8 steps (WhatsApp J+1 en ouverture) ---
JOUR_2_PLUS_STEPS: List[Step] = [
    Step.WHATSAPP,
    Step.DEBRIEF_WA,
    Step.MINI_COURS,
    Step.QUESTIONS_RAG,
    Step.COURS_CLES,
    Step.QUIZ,
    Step.DEBRIEF_QUIZ,
    Step.SYNTHESE,
]


def get_steps_for_session(session_number: int) -> List[Step]:
    """Return step sequence for a given session (1-indexed)."""
    if session_number == 1:
        return list(JOUR_1_STEPS)
    return list(JOUR_2_PLUS_STEPS)


STEP_LABELS: Dict[Step, str] = {
    Step.PROFIL: "Profil stagiaire",
    Step.WHATSAPP: "Mise en situation WhatsApp",
    Step.DEBRIEF_WA: "Débrief WhatsApp",
    Step.MINI_COURS: "Mini-cours",
    Step.QUESTIONS_RAG: "Questions & réponses",
    Step.COURS_CLES: "Cours clés",
    Step.QUIZ: "Quiz",
    Step.DEBRIEF: "Débrief",
    Step.DEBRIEF_QUIZ: "Débrief Quiz",
    Step.SYNTHESE: "Synthèse",
}


STEP_DURATIONS: Dict[Step, str] = {
    Step.PROFIL: "3-5 min",
    Step.WHATSAPP: "8-12 min",
    Step.DEBRIEF_WA: "5 min",
    Step.MINI_COURS: "5-8 min",
    Step.QUESTIONS_RAG: "~5 min",
    Step.COURS_CLES: "10-12 min",
    Step.QUIZ: "8-12 min",
    Step.DEBRIEF: "~5 min",
    Step.DEBRIEF_QUIZ: "~5 min",
    Step.SYNTHESE: "3-5 min",
}
