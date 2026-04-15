"""training/steps.py – Step enum and day sequences.

Jour 1  (onboarding) : PROFIL → MARCHE → QUESTIONS → COURS → QUIZ → WA → DEBRIEF_WA → SYNTHESE
Jour 2+ (récurrence) :          MARCHE → QUESTIONS → COURS → QUIZ → WA → DEBRIEF_WA → SYNTHESE

Clarification :
  - MINI_COURS_MARCHE = module marché complet (1 module / session, rotation modulo 100)
  - COURS_CLES        = points clés extraits par l'IA (résumé, pas un doublon)
  - WHATSAPP + DEBRIEF_WA = roleplay après le quiz (fermeture de session)
  - MINI_COURS supprimé des séquences (doublon avec MINI_COURS_MARCHE)
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List


class Step(str, Enum):
    PROFIL = "PROFIL"
    WHATSAPP = "WHATSAPP"
    DEBRIEF_WA = "DEBRIEF_WA"
    MINI_COURS_MARCHE = "MINI_COURS_MARCHE"
    MINI_COURS = "MINI_COURS"
    QUESTIONS_RAG = "QUESTIONS_RAG"
    COURS_CLES = "COURS_CLES"
    QUIZ = "QUIZ"
    DEBRIEF = "DEBRIEF"
    DEBRIEF_QUIZ = "DEBRIEF_QUIZ"
    SYNTHESE = "SYNTHESE"


# --- Jour 1 : 8 steps (onboarding + WhatsApp en fermeture) ---
JOUR_1_STEPS: List[Step] = [
    Step.PROFIL,            # Onboarding profil
    Step.MINI_COURS_MARCHE, # Modules marché 1-2
    Step.QUESTIONS_RAG,     # Questions du stagiaire
    Step.COURS_CLES,        # Cours IA personnalisé (points clés)
    Step.QUIZ,              # Quiz d'assimilation
    Step.WHATSAPP,          # Roleplay WhatsApp (fermeture)
    Step.DEBRIEF_WA,        # Débrief WhatsApp
    Step.SYNTHESE,          # Synthèse finale
]

# --- Jour 2+ : 7 steps (sans profil, WhatsApp en fermeture) ---
JOUR_2_PLUS_STEPS: List[Step] = [
    Step.MINI_COURS_MARCHE, # Modules marché suivants (3-4, 5-6, …)
    Step.QUESTIONS_RAG,     # Questions du stagiaire
    Step.COURS_CLES,        # Cours IA personnalisé (points clés)
    Step.QUIZ,              # Quiz d'assimilation
    Step.WHATSAPP,          # Roleplay WhatsApp (fermeture)
    Step.DEBRIEF_WA,        # Débrief WhatsApp
    Step.SYNTHESE,          # Synthèse finale
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
    Step.MINI_COURS_MARCHE: "Marché immo",
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
    Step.MINI_COURS_MARCHE: "5-8 min",
    Step.MINI_COURS: "5-8 min",
    Step.QUESTIONS_RAG: "~5 min",
    Step.COURS_CLES: "10-12 min",
    Step.QUIZ: "8-12 min",
    Step.DEBRIEF: "~5 min",
    Step.DEBRIEF_QUIZ: "~5 min",
    Step.SYNTHESE: "3-5 min",
}
