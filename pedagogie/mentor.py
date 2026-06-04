"""
pedagogie/mentor.py — Tuyauterie de l'agent mentor Archimède.

Ce module assemble le prompt système, contextualise l'exercice courant,
appelle le LLM via core/llm_client. Il ne contient AUCUNE règle pédagogique
écrite en dur — tout ce
qui concerne la pédagogie vit dans prompts/mentor/.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from core import llm_client

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts" / "mentor"

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class Exercice(TypedDict):
    enonce: str
    reponse: str
    solution_etapes: list[str]
    indices: dict[str, str]       # clés : "leger", "moyen", "fort"
    erreurs_typiques: list[dict]  # [{erreur, reponse_maieutique}]


# ---------------------------------------------------------------------------
# Chargement des prompts (une seule fois au démarrage du module)
# ---------------------------------------------------------------------------


def _load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8").strip()


_PERSONA    = _load_prompt("_shared_persona.txt")
_GUARDRAILS = _load_prompt("_shared_guardrails.txt")
_MODES: dict[str, str] = {
    "decouverte":    _load_prompt("mode_decouverte.txt"),
    "pratique":      _load_prompt("mode_pratique.txt"),
}


# ---------------------------------------------------------------------------
# Assemblage du prompt système
# ---------------------------------------------------------------------------


def _build_system_prompt(mode: str) -> str:
    mode_block = _MODES.get(mode, _MODES["decouverte"])
    return "\n\n\n".join([_PERSONA, _GUARDRAILS, mode_block])


def _format_exercise_block(exercice: Exercice) -> str:
    etapes = "\n".join(
        f"  {i + 1}. {e}" for i, e in enumerate(exercice["solution_etapes"])
    )
    idx = exercice["indices"]
    erreurs_lines = "\n".join(
        f"  - Erreur : {e['erreur']}\n    Relance maïeutique : {e['reponse_maieutique']}"
        for e in exercice.get("erreurs_typiques", [])
    )
    return "\n".join([
        "═══════════════════════════════════════════════",
        "CONTEXTE DE L'EXERCICE COURANT (pour toi seul, ne pas révéler à l'enfant)",
        "═══════════════════════════════════════════════",
        "",
        f"ÉNONCÉ :\n{exercice['enonce']}",
        "",
        f"RÉPONSE ATTENDUE : {exercice['reponse']}",
        "",
        f"SOLUTION ÉTAPE PAR ÉTAPE :\n{etapes}",
        "",
        "INDICES ÉTAGÉS (à utiliser dans l'ordre, uniquement si l'enfant bloque) :",
        f"  Léger : {idx.get('leger', '')}",
        f"  Moyen : {idx.get('moyen', '')}",
        f"  Fort  : {idx.get('fort', '')}",
        "",
        f"ERREURS TYPIQUES ET RELANCES MAÏEUTIQUES :\n{erreurs_lines or '  (aucune renseignée)'}",
    ])




# ---------------------------------------------------------------------------
# Interface publique
# ---------------------------------------------------------------------------


def _format_narrative_block(situation_narrative: str) -> str:
    return "\n".join([
        "═══════════════════════════════════════════════",
        "SITUATION NARRATIVE DE LA SESSION (à ancrer dans l'univers du jeu)",
        "═══════════════════════════════════════════════",
        "",
        situation_narrative,
    ])


def repondre(
    message: str,
    histoire: list[dict],
    exercice: Exercice,
    mode: str = "decouverte",
    prenom: str = "Élévateur",
    situation_narrative: str = "",
) -> str:
    """
    Génère la réponse d'Archimède.

    Args:
        message              : message courant de l'enfant.
        histoire             : échanges précédents [{"role": "user"/"assistant", "content": "..."}].
        exercice             : données complètes de l'exercice.
        mode                 : mode pédagogique actif ("decouverte", …).
        prenom               : prénom de l'enfant.
        situation_narrative  : contexte narratif de la session (pont brisé, etc.).

    Returns:
        Réponse textuelle d'Archimède.
    """
    sections = [_build_system_prompt(mode), f"Le prénom de l'enfant que tu accompagnes est : {prenom}"]
    if situation_narrative:
        sections.append(_format_narrative_block(situation_narrative))
    sections.append(_format_exercise_block(exercice))

    system_prompt = "\n\n\n".join(sections)

    messages = list(histoire) + [{"role": "user", "content": message}]

    return llm_client.chat(system_prompt, messages)
