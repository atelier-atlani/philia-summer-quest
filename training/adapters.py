"""training/adapters.py – Profile-based adaptation functions.

Adapts quiz difficulty, WhatsApp scenario tone, formateur tone,
and module ordering based on the trainee's profile.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from training.profile import UserProfile


# --- Quiz difficulty ---
# Maps niveau → (min_difficulty, max_difficulty)
_DIFFICULTY_RANGES: Dict[str, Tuple[int, int]] = {
    "debutant": (1, 2),
    "confirme": (2, 3),
    "expert": (3, 3),
}


def adapt_quiz_difficulty(profile: UserProfile) -> Tuple[int, int]:
    """Return (min_difficulty, max_difficulty) for quiz filtering.

    debutant  → difficulty 1-2
    confirme  → difficulty 2-3
    expert    → difficulty 3
    """
    return _DIFFICULTY_RANGES.get(profile.niveau, (1, 3))


# --- WhatsApp scenario tone ---
_TONE_MAP: Dict[str, str] = {
    "debutant": "coopératif, bienveillant, pose des questions simples",
    "confirme": "réaliste, un peu hésitant, objections classiques",
    "expert": "difficile, méfiant, objections fortes, teste le conseiller",
}


def adapt_whatsapp_tone(profile: UserProfile) -> str:
    """Return adapted client tone for WhatsApp scenario based on level."""
    return _TONE_MAP.get(profile.niveau, _TONE_MAP["confirme"])


# --- Formateur tone ---
_FORMATEUR_TONE: Dict[str, str] = {
    "debutant": "pédagogique, encourageant, explique les bases",
    "confirme": "coach, direct, orienté action",
    "expert": "challenger, exigeant, pousse à l'excellence",
}


def adapt_tone(profile: UserProfile) -> str:
    """Return formateur tone adapted to the trainee's level."""
    return _FORMATEUR_TONE.get(profile.niveau, _FORMATEUR_TONE["confirme"])


# --- Module prioritization ---
# Maps specialite/point_faible keywords → related theme titles (partial match)
_THEME_KEYWORDS: Dict[str, List[str]] = {
    "vendeur": [
        "vendeur", "mandat", "suivi vendeur", "renégociation",
        "enquête qualité", "fidélisation",
    ],
    "acquereur": [
        "acquéreur", "visite", "objections acquéreur",
        "closing", "compte-rendu",
    ],
    "estimation": [
        "ACM", "prix", "estimation", "renégociation",
    ],
    "prospection": [
        "prospection", "relance", "recommandation",
        "fidélisation",
    ],
    "management": [
        "management", "stock", "bilan", "promotion",
    ],
}


def prioritize_modules(
    profile: UserProfile,
    themes: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """Reorder themes to prioritize those matching profile specialties + weaknesses.

    Themes matching specialites or points_faibles are moved to the front,
    preserving relative order among prioritized and non-prioritized themes.
    """
    keywords: List[str] = []
    for spec in profile.specialites:
        keywords.extend(_THEME_KEYWORDS.get(spec, []))
    for faible in profile.points_faibles:
        keywords.extend(_THEME_KEYWORDS.get(faible, []))

    if not keywords:
        return themes

    keywords_lower = [k.lower() for k in keywords]

    def _is_priority(theme: Dict[str, str]) -> bool:
        titre = theme.get("titre", "").lower()
        return any(kw in titre for kw in keywords_lower)

    priority = [t for t in themes if _is_priority(t)]
    rest = [t for t in themes if not _is_priority(t)]
    return priority + rest
