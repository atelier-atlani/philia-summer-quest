"""
ui/ecran_session.py — Écran d'une session pédagogique.

Responsabilité : afficher la situation narrative, orchestrer le SessionEngine,
conserver l'état et exposer les contrôles de navigation.
L'écran est une vitre. Aucune logique pédagogique ici.
"""

from __future__ import annotations

import streamlit as st

from pedagogie.contenu_ile1 import META_SESSION_1, SESSION_1
from pedagogie.session_engine import SessionEngine
from ui.ecran_chat import render_chat


@st.cache_data
def _charger_session_1() -> tuple[dict, list]:
    """Retourne (métadonnées, exercices) de la Session 1. Mis en cache."""
    return META_SESSION_1, SESSION_1


def _init_engine(exercices: list, situation_narrative: str) -> SessionEngine:
    """Crée un SessionEngine neuf et génère le message d'ouverture d'Archimède."""
    engine = SessionEngine(
        exercices=exercices,
        prenom="Élévateur",
        situation_narrative=situation_narrative,
    )
    with st.spinner("Archimède arrive…"):
        engine.debut_session()
    st.session_state.session_active = engine.to_dict()
    return engine


def _kickoff_exercice_suivant(engine: SessionEngine) -> None:
    """Envoie un kickoff interne pour ouvrir le nouvel exercice après avance.

    engine.repondre() ajoute les deux entrées (user + assistant) à l'historique.
    On supprime ensuite le message interne côté user pour que l'affichage reste propre.
    """
    _KICKOFF_SUIVANT = (
        "[EXERCICE SUIVANT — message interne] "
        "L'enfant passe à l'exercice suivant. "
        "Présente-lui brièvement la nouvelle situation et pose ta première question."
    )
    engine.repondre(_KICKOFF_SUIVANT)
    # Retire uniquement l'entrée user du kickoff — la réponse d'Archimède reste
    engine.historique = [
        m for m in engine.historique
        if not (m["role"] == "user" and m.get("content") == _KICKOFF_SUIVANT)
    ]


def render_session() -> None:
    meta, exercices = _charger_session_1()

    # En-tête narratif
    st.title(meta["titre"])
    st.info(meta["situation_narrative"])

    st.divider()

    # Initialisation ou restauration du moteur
    if st.session_state.get("session_active") is None:
        engine = _init_engine(exercices, meta["situation_narrative"])
    else:
        engine = SessionEngine.from_dict(st.session_state.session_active)

    # Indicateur de progression
    n_total   = len(engine.exercices)
    n_courant = engine.index_exercice + 1
    st.caption(f"{meta['concept']} · Exercice {n_courant} / {n_total}")

    # Zone de chat — modifie engine in-place
    render_chat(engine)

    # Persistance après chaque tour de chat
    st.session_state.session_active = engine.to_dict()

    # Contrôles de navigation
    st.divider()
    col_suivant, col_retour = st.columns(2)

    with col_suivant:
        if not engine.est_dernier_exercice and not engine.est_terminee:
            if st.button("Exercice suivant →", key="btn_exercice_suivant", use_container_width=True):
                avance = engine.exercice_suivant()
                if avance:
                    with st.spinner("Archimède prépare le prochain exercice…"):
                        _kickoff_exercice_suivant(engine)
                    st.session_state.session_active = engine.to_dict()
                    st.rerun()

    with col_retour:
        if st.button("← Retour à l'île", key="btn_retour_ile", use_container_width=True):
            st.session_state.session_active = None
            st.session_state.ecran_courant = "ile"
            st.rerun()
