"""training/adapters.py – Profile-based adaptation functions.

Adapts quiz difficulty, WhatsApp scenario tone, formateur tone,
and module ordering based on the trainee's profile.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from training.profile import UserProfile

# --- WhatsApp difficulty levels ---
_DIFFICULTY_MAP: Dict[str, str] = {
    "debutant": "facile",
    "confirme": "moyen",
    "expert": "difficile",
}


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


def get_whatsapp_difficulty(profile: UserProfile) -> str:
    """Return initial WhatsApp client difficulty based on trainee level.

    debutant  → facile   (1-2 objections légères, client ouvert)
    confirme  → moyen    (2-3 objections réalistes, client hésitant)
    expert    → difficile (objections subtiles, client exigeant)
    """
    return _DIFFICULTY_MAP.get(profile.niveau, "moyen")


def evaluate_agent_performance(messages: List[Dict[str, str]]) -> float:
    """Score agent performance from recent messages (0-100).

    Checks last 3 agent messages for positive/negative signals.
    Returns 50.0 if fewer than 4 messages (too early to judge).
    """
    if len(messages) < 4:
        return 50.0

    score = 50.0
    agent_messages = [m["content"] for m in messages if m["role"] == "agent"][-3:]

    for msg in agent_messages:
        msg_lower = msg.lower()
        # Positive signals
        if any(w in msg_lower for w in ["comment", "pourquoi", "qu'est-ce que"]):
            score += 5   # asks questions
        if any(w in msg_lower for w in ["je comprends", "je vois", "effectivement"]):
            score += 3   # active listening
        if len(msg.split()) > 20:
            score += 2   # detailed answer
        # Negative signals
        if any(w in msg_lower for w in ["dois", "faut", "obligé"]):
            score -= 5   # too directive
        if msg.count("!") > 2:
            score -= 3   # overenthusiastic
        if len(msg.split()) < 10:
            score -= 2   # too short

    return max(0.0, min(100.0, score))


def adjust_difficulty_dynamically(
    current_difficulty: str,
    messages: List[Dict[str, str]],
    exchange_count: int,
) -> str:
    """Adjust WhatsApp client difficulty mid-conversation based on agent performance.

    Does nothing before exchange 4. Promotes or demotes by at most one level.
    """
    if exchange_count < 4:
        return current_difficulty

    performance = evaluate_agent_performance(messages)

    if current_difficulty == "facile" and performance > 75:
        return "moyen"
    if current_difficulty == "moyen" and performance > 80:
        return "difficile"
    if current_difficulty == "moyen" and performance < 40:
        return "facile"
    if current_difficulty == "difficile" and performance < 50:
        return "moyen"

    return current_difficulty


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
