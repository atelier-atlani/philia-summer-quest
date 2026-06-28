"""
ui/ecran_session.py — Écran d'une session pédagogique.

Responsabilité : afficher la situation narrative, orchestrer le SessionEngine,
conserver l'état et exposer les contrôles de navigation.
L'écran est une vitre. Aucune logique pédagogique ici.
"""

from __future__ import annotations

import streamlit as st

from data_layer.joueurs import charger_joueur_courant
from pedagogie.contenu_ile1 import META_SESSION_1, SESSION_1
from pedagogie.modes import Mode
from pedagogie.session_engine import PhaseSession, SessionEngine
from ui.ecran_chat import render_chat
from ui.modal_planche_bd import afficher_modal_planche_bd


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


def _numero_chapitre(planche_key: str | None) -> int:
    """Retourne le numéro ordinal du chapitre à partir de sa clé."""
    _MAP = {"c1": 1, "c2": 2, "c3": 3, "c4": 4, "c5": 5}
    return _MAP.get(planche_key or "", 1)


def render_session() -> None:
    meta, exercices = _charger_session_1()

    # ── Vérification flag modal planche BD ─────────────────────────────────
    if st.session_state.get("planche_bd_a_afficher"):
        joueur = charger_joueur_courant()
        genre = joueur["avatar_genre"] if joueur else "fille"
        afficher_modal_planche_bd(
            ile_id="ile_1",
            planche_key=st.session_state["planche_bd_a_afficher"],
            genre=genre,
            chapitre_num=_numero_chapitre(meta.get("planche_key")),
            chapitres_total=5,
        )
        return
    # ───────────────────────────────────────────────────────────────────────

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

    # Transition automatique vers Mode.BILAN au dernier exercice (D-T8.1-A / D-T8.1-F)
    if engine.est_dernier_exercice and engine.mode != Mode.BILAN and not engine.est_terminee:
        engine.transitionner(Mode.BILAN)

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

        elif (
            engine.mode == Mode.BILAN
            and engine.nb_tours_bilan >= 1   # gating D-T8.1-F / D24
            and not engine.est_terminee
        ):
            if st.button(
                "Terminer le chapitre ✓",
                key="btn_terminer_chapitre",
                use_container_width=True,
                type="primary",
            ):
                engine.phase = PhaseSession.TERMINEE
                st.session_state.session_active = engine.to_dict()
                planche_key = meta.get("planche_key")
                if planche_key:
                    st.session_state.planche_bd_a_afficher = planche_key
                    st.session_state.planche_bd_index = 0  # reset systématique (D-T8.1-C)
                else:
                    st.session_state.ecran_courant = "ile"
                st.rerun()

    with col_retour:
        # Masqué en Mode BILAN pour forcer le flow BD (D-T8.1-F)
        if engine.mode != Mode.BILAN or engine.est_terminee:
            if st.button("← Retour à l'île", key="btn_retour_ile", use_container_width=True):
                st.session_state.session_active = None
                st.session_state.ecran_courant = "ile"
                st.rerun()
