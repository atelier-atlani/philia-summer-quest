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


def _init_engine(exercices: list) -> SessionEngine:
    """Crée un SessionEngine neuf et génère le message d'ouverture d'Archimède."""
    engine = SessionEngine(exercices=exercices, prenom="Élévateur")
    with st.spinner("Archimède arrive…"):
        engine.debut_session()
    st.session_state.session_active = engine.to_dict()
    return engine


def render_session() -> None:
    meta, exercices = _charger_session_1()

    # En-tête narratif
    st.title(meta["titre"])
    st.info(meta["situation_narrative"])

    st.divider()

    # Initialisation ou restauration du moteur
    if st.session_state.get("session_active") is None:
        engine = _init_engine(exercices)
    else:
        engine = SessionEngine.from_dict(st.session_state.session_active)

    # Indicateur de progression
    n_total   = len(engine.exercices)
    n_courant = engine.index_exercice + 1
    st.caption(f"{meta['concept']} · Exercice {n_courant} / {n_total}")

    # Zone de chat — modifie engine in-place
    render_chat(engine)

    # Persistance après chaque tour
    st.session_state.session_active = engine.to_dict()

    # Contrôles de navigation
    st.divider()
    col_suivant, col_retour = st.columns(2)

    with col_suivant:
        if not engine.est_dernier_exercice and not engine.est_terminee:
            if st.button("Exercice suivant →", use_container_width=True):
                engine.exercice_suivant()
                st.session_state.session_active = engine.to_dict()
                st.rerun()

    with col_retour:
        if st.button("← Retour à l'île", use_container_width=True):
            st.session_state.session_active = None
            st.session_state.ecran_courant = "ile"
            st.rerun()
