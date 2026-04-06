"""training/wa_scenario_generator.py – Génération de scénarios WhatsApp dynamiques.

Génère un scénario WhatsApp cohérent avec le thème cours clé de la session,
via un appel LLM. Le résultat est mis en cache dans st.session_state pour éviter
de régénérer à chaque rerun.

Usage :
    from training.wa_scenario_generator import get_or_generate_wa_scenario
    scenario_data = get_or_generate_wa_scenario(theme_titre, session_number, chat_complete_fn)
"""
from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, Optional

import streamlit as st

_CACHE_KEY = "wa_generated_scenario"

_GENERATION_PROMPT = """Tu es expert en formation d'agents immobiliers.
Génère un scénario WhatsApp réaliste pour mettre en pratique le cours suivant.

THÈME DU COURS : {theme_titre}
SESSION N° : {session_number}

CONTRAINTES :
- Client réaliste avec 2-3 objections terrain authentiques
- Persona varié selon session (vendeur, acquéreur, investisseur, héritier...)
- Message d'ouverture naturel et direct, comme un vrai SMS
- max_exchanges entre 5 et 8
- Les critères d'évaluation doivent être alignés sur le thème

Réponds UNIQUEMENT en JSON valide, sans markdown, sans commentaires :
{{
  "persona": {{
    "name": "Prénom Nom du client",
    "role": "ex: vendeur particulier / primo-accédant / investisseur locatif",
    "context": "2-3 phrases contexte client : bien, situation, motivation, blocage",
    "tone": "ex: direct et pressé / hésitant et méfiant / curieux mais économe"
  }},
  "opening_message": "Le premier SMS du client — naturel, court (1-2 phrases)",
  "max_exchanges": 6,
  "theme_tags": ["{theme_titre}"],
  "evaluation_criteria": [
    {{"name": "Écoute active", "description": "...", "weight": 25}},
    {{"name": "Application cours clé", "description": "Application concrète de : {theme_titre}", "weight": 30}},
    {{"name": "Traitement objections", "description": "...", "weight": 20}},
    {{"name": "Posture professionnelle", "description": "...", "weight": 15}},
    {{"name": "Conclusion / prochaine étape", "description": "...", "weight": 10}}
  ]
}}"""


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extrait le JSON d'une réponse LLM même si elle contient du texte parasite."""
    # Tentative directe
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # Cherche un bloc JSON entre accolades
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def _fallback_scenario(theme_titre: str, session_number: int) -> Dict[str, Any]:
    """Scénario de secours si la génération LLM échoue."""
    personas = [
        {
            "name": "M. Dupont",
            "role": "vendeur particulier",
            "context": f"Propriétaire souhaitant vendre, contacte l'agence pour : {theme_titre}.",
            "tone": "direct, un peu méfiant, pose des questions",
        },
        {
            "name": "Mme Martin",
            "role": "primo-accédante",
            "context": f"Achète son premier bien, cherche des conseils sur : {theme_titre}.",
            "tone": "curieuse, prudente, stressée par le financement",
        },
        {
            "name": "M. Bernard",
            "role": "investisseur locatif",
            "context": f"Investisseur expérimenté, veut maximiser rendement, thème : {theme_titre}.",
            "tone": "précis, exigeant, compare les chiffres",
        },
        {
            "name": "Mme Leroy",
            "role": "vendeuse héritière",
            "context": f"Hérite d'un bien familial, doit vendre rapidement. Thème : {theme_titre}.",
            "tone": "émotive, partagée entre famille et pratique",
        },
    ]
    persona = personas[session_number % len(personas)]
    return {
        "persona": persona,
        "opening_message": f"Bonjour, j'aurais besoin de votre aide concernant {theme_titre.lower()}. Vous pouvez m'aider ?",
        "max_exchanges": 6,
        "theme_tags": [theme_titre],
        "evaluation_criteria": [
            {"name": "Écoute active", "description": "Reformule et montre qu'il a compris", "weight": 25},
            {"name": "Application cours clé", "description": f"Applique : {theme_titre}", "weight": 30},
            {"name": "Traitement objections", "description": "Répond avec méthode", "weight": 20},
            {"name": "Posture professionnelle", "description": "Ton rassurant, pas de pression", "weight": 15},
            {"name": "Conclusion", "description": "Propose une prochaine étape", "weight": 10},
        ],
    }


def get_or_generate_wa_scenario(
    theme_titre: str,
    session_number: int,
    chat_complete_fn: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Retourne un scénario WhatsApp cohérent avec le thème, généré ou depuis cache.

    Le scénario est régénéré si le thème change (nouvelle session).

    Args:
        theme_titre: Titre du cours clé de la session.
        session_number: Numéro de session (pour cache et rotation fallback).
        chat_complete_fn: Fonction LLM pour génération (peut être None).

    Returns:
        Dict compatible avec le format YAML de Scenario.from_dict().
    """
    cache = st.session_state.get(_CACHE_KEY, {})

    # Cache valide si même thème et même session
    if cache.get("theme") == theme_titre and cache.get("session") == session_number:
        return cache["data"]

    # Générer via LLM
    scenario_data = None
    if chat_complete_fn is not None:
        try:
            prompt = _GENERATION_PROMPT.format(
                theme_titre=theme_titre,
                session_number=session_number,
            )
            messages = [{"role": "user", "content": prompt}]
            raw = chat_complete_fn(messages)
            scenario_data = _extract_json(raw)
        except Exception:
            scenario_data = None

    if scenario_data is None or "persona" not in scenario_data:
        scenario_data = _fallback_scenario(theme_titre, session_number)

    # Sauvegarder en cache session
    st.session_state[_CACHE_KEY] = {
        "theme": theme_titre,
        "session": session_number,
        "data": scenario_data,
    }
    return scenario_data
