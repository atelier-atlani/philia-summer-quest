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
Génère un scénario WhatsApp qui TESTE si le stagiaire applique les techniques du cours.

THÈME DU COURS : {theme_titre}
SESSION N° : {session_number}

RÈGLES IMPÉRATIVES :
- Le client doit pousser le stagiaire sur EXACTEMENT les points du cours
- Le contexte doit inclure des CHIFFRES CONCRETS : prix du bien, surface, ville, étage
- Le client a une situation PERSONNELLE précise : famille, projet, contraintes budget
- 2-3 objections qui testent directement les techniques enseignées dans le cours
- Le message d'ouverture est naturel, court, comme un vrai SMS WhatsApp

VARIÉTÉ DES PROFILS (alterner selon session_number) :
- Sessions paires : VENDEUR (propriétaire qui veut vendre)
- Sessions impaires : ACQUÉREUR (cherche à acheter)
- Varier : jeune couple, retraité, investisseur, héritier, divorcé, expatrié

Réponds UNIQUEMENT en JSON valide, sans markdown, sans commentaires :
{{
  "persona": {{
    "name": "Prénom Nom réaliste",
    "role": "vendeur particulier / primo-accédant / investisseur locatif / héritier...",
    "context": "Situation précise avec CHIFFRES : bien (type, surface, ville, prix), situation familiale, motivation, blocage. Ex: Propriétaire d'un T3 de 68m² à Marseille 8e, acheté 195 000€ en 2018, estime son bien à 260 000€ alors que le marché est à 220 000€. En instance de divorce, besoin de vendre dans les 3 mois.",
    "tone": "direct et pressé / hésitant et méfiant / curieux mais économe / émotif et attaché au bien"
  }},
  "opening_message": "SMS naturel et court du client (1-2 phrases max). Ex: Bonjour, j'ai reçu votre estimation et franchement je suis surpris. On peut en discuter ?",
  "max_exchanges": 6,
  "theme_tags": ["{theme_titre}"],
  "evaluation_criteria": [
    {{"name": "Écoute active", "description": "Reformule les propos du client, montre qu'il comprend sa situation", "weight": 20}},
    {{"name": "Application du cours : {theme_titre}", "description": "Utilise concrètement les techniques enseignées dans le cours clé", "weight": 30}},
    {{"name": "Traitement des objections", "description": "Répond aux objections avec méthode, chiffres et calme", "weight": 20}},
    {{"name": "Posture professionnelle", "description": "Ton rassurant, pas de pression, vocabulaire adapté vendeur/acquéreur", "weight": 15}},
    {{"name": "Conclusion / prochaine étape", "description": "Propose une action concrète : RDV, rappel, document", "weight": 15}}
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
            "context": f"Propriétaire d'un T4 de 85m² à Lyon 3e, acheté 280 000€ en 2019. Pense que son bien vaut 340 000€. En mutation professionnelle, doit vendre sous 4 mois. Thème : {theme_titre}.",
            "tone": "pressé, un peu stressé, veut aller vite",
        },
        {
            "name": "Mme Martin",
            "role": "primo-accédante",
            "context": f"Jeune couple avec un enfant, budget max 220 000€, cherche un T3 en proche banlieue. Premier achat, beaucoup de questions sur le financement. Thème : {theme_titre}.",
            "tone": "curieuse mais anxieuse, pose beaucoup de questions",
        },
        {
            "name": "M. Bernard",
            "role": "investisseur locatif",
            "context": f"Investisseur avec 2 biens en location, cherche un studio pour du LMNP. Budget 150 000€, veut 5% de rendement net minimum. Compare avec d'autres agences. Thème : {theme_titre}.",
            "tone": "précis, exigeant, compare les chiffres",
        },
        {
            "name": "Mme Leroy",
            "role": "vendeuse héritière",
            "context": f"Hérite d'une maison familiale de 120m² en zone périurbaine, estimée entre 180 000€ et 220 000€. Attachée sentimentalement, hésite à vendre. Fratrie en désaccord sur le prix. Thème : {theme_titre}.",
            "tone": "émotive, indécise, a besoin d'être rassurée",
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
            raw = chat_complete_fn(
                "Tu es un expert en formation immobilière. Réponds UNIQUEMENT en JSON valide, sans markdown.",
                _GENERATION_PROMPT.format(theme_titre=theme_titre, session_number=session_number),
                0.7,
            )
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
