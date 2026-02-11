"""training/synthesis.py – AI-generated daily synthesis via RAG.

Generates:
  - resume_cours: 3-4 phrases terrain summarizing today's key learning
  - a_faire_demain: 3 concrete field actions for tomorrow
  - points_forts: strengths based on quiz + WhatsApp scores
  - axes_amelioration: improvement areas based on scores
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, Optional


def generate_synthesis(
    session_number: int,
    theme_title: str,
    step_data: Dict[str, Any],
    prenom: str,
    chat_complete_fn: Callable,
    construire_contexte_fn: Callable,
) -> Dict[str, str]:
    """Generate the daily AI synthesis based on RAG + session scores.

    Args:
        session_number: Current session (1-indexed).
        theme_title: Today's theme title.
        step_data: All recorded step data for this session.
        prenom: Trainee first name.
        chat_complete_fn: LLM completion function.
        construire_contexte_fn: RAG context builder.

    Returns:
        Dict with keys: resume_cours, a_faire_demain, points_forts,
        axes_amelioration.
    """
    rag_context = construire_contexte_fn(theme_title)

    quiz_data = step_data.get("QUIZ", {})
    wa_data = step_data.get("WHATSAPP", {})
    is_jour1 = session_number == 1

    # Build score context for the LLM
    score_lines = []
    if quiz_data:
        score_lines.append(
            f"Quiz : {quiz_data.get('score', 0)}/{quiz_data.get('total', 0)} "
            f"bonnes réponses ({quiz_data.get('score_pct', 0)}%), "
            f"bonus rapidité : {quiz_data.get('speed_bonuses', 0)}"
        )

    if not is_jour1 and wa_data and not wa_data.get("placeholder"):
        wa_score = wa_data.get("score", 0)
        score_lines.append(f"WhatsApp simulation : {wa_score}/100")
        criteria = wa_data.get("criteria", [])
        for c in criteria:
            score_lines.append(
                f"  - {c.get('name', '?')} : {c.get('score', 0)}/10 "
                f"(poids {c.get('weight', 0)}%)"
            )

    scores_block = "\n".join(score_lines) if score_lines else "Aucun score disponible."

    system_prompt = (
        "Tu es un formateur senior terrain en vente immobilière.\n"
        "Tu rédiges la synthèse de fin de session pour un stagiaire.\n"
        "Style : coach terrain, direct, verbes d'action, pas de blabla académique.\n"
        "Base-toi sur les extraits fournis (RAG) pour le résumé du cours.\n"
        "Base-toi sur les scores pour l'analyse points forts / axes d'amélioration.\n"
        "Ne cite aucune marque/réseau/outils propriétaires."
    )

    comparison_instruction = ""
    if not is_jour1 and wa_data and not wa_data.get("placeholder"):
        comparison_instruction = (
            "- Compare les scores WhatsApp et Quiz : "
            "identifie les écarts et ce que ça révèle.\n"
        )

    user_prompt = (
        f"Stagiaire : {prenom}\n"
        f"Session n°{session_number}\n"
        f"Thème du jour : {theme_title}\n\n"
        f"Extraits de formation (RAG) :\n{rag_context}\n\n"
        f"Scores de la session :\n{scores_block}\n\n"
        "Rédige la synthèse EXACTEMENT dans ce format :\n\n"
        "RÉSUMÉ DU COURS :\n"
        "[3-4 phrases terrain résumant les points clés du thème du jour. "
        "Concret, orienté action.]\n\n"
        "POINTS FORTS :\n"
        "[2-3 puces identifiant ce que le stagiaire maîtrise bien, "
        "basé sur les scores.]\n\n"
        "AXES D'AMÉLIORATION :\n"
        "[2-3 puces identifiant les points à travailler, "
        "basé sur les scores. Constructif, pas négatif.]\n"
        f"{comparison_instruction}\n"
        "À FAIRE DEMAIN :\n"
        "[3 actions concrètes terrain, commençant par un verbe d'action. "
        "Réalistes, applicables dès le prochain rendez-vous.]\n"
    )

    raw = chat_complete_fn(system_prompt, user_prompt, temperature=0.4)
    return _parse_synthesis(raw)


def _parse_synthesis(raw: str) -> Dict[str, str]:
    """Parse the LLM output into structured sections."""
    sections = {
        "resume_cours": "",
        "a_faire_demain": "",
        "points_forts": "",
        "axes_amelioration": "",
    }

    raw_upper = raw.upper()

    # Define section markers and their keys
    markers = [
        ("RÉSUMÉ DU COURS", "RESUME DU COURS", "resume_cours"),
        ("POINTS FORTS", "POINTS FORTS", "points_forts"),
        ("AXES D'AMÉLIORATION", "AXES D'AMELIORATION", "axes_amelioration"),
        ("À FAIRE DEMAIN", "A FAIRE DEMAIN", "a_faire_demain"),
    ]

    # Find positions of all markers
    positions = []
    for marker_accent, marker_plain, key in markers:
        idx = raw_upper.find(marker_accent)
        if idx == -1:
            idx = raw_upper.find(marker_plain)
        if idx != -1:
            positions.append((idx, key))

    positions.sort(key=lambda x: x[0])

    # Extract content between markers
    for i, (pos, key) in enumerate(positions):
        start = pos
        end = positions[i + 1][0] if i + 1 < len(positions) else len(raw)
        block = raw[start:end].strip()
        # Remove header line
        lines = block.split("\n")
        content = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        sections[key] = content

    return sections
