"""
ui/celebrations.py — Célébrations D27 : légère (progression) et forte (fin d'île).
Sprint 3 T8.6 (D-T8.6-A, B, F, G)

Célébration légère : confetti + toast à chaque progression d'exercice.
Célébration forte   : modal dédié + balloons + message d'Archimède à la fin
                       d'une île.

Aucune librairie externe (D-T8.6-B, D13, D25) — uniquement st.balloons()/st.toast().
La garde anti-rejeu (D-T8.6-G) est de la responsabilité de l'appelant
(flag st.session_state consommé immédiatement après affichage), pas de ce module.
"""

from __future__ import annotations

import streamlit as st

# Texte narratif fixe de la célébration forte — PLACEHOLDER.
# D-T8.6-F / §7 du brief : ce texte doit être rédigé par le Décideur (ou avec
# l'aide de l'Architect), pas improvisé par l'Implementer. À remplacer avant
# toute mise en production — ne pas considérer ce contenu comme définitif.
_MESSAGE_FIN_ILE_PLACEHOLDER = (
    "{prenom}, tu l'as fait. {nom_ile} respire à nouveau.\n\n"
    "[Texte à valider par le Décideur — placeholder D-T8.6-F, ui/celebrations.py]"
)


def afficher_celebration_legere(prenom: str) -> None:
    """Célébration légère (D-T8.6-A/B) : confetti + toast personnalisé au prénom.

    Ne gère pas l'anti-rejeu — l'appelant est responsable de ne déclencher
    cet affichage qu'une seule fois par événement de progression (D-T8.6-G).
    """
    st.balloons()
    st.toast(f"Bien joué {prenom} !")


def afficher_celebration_fin_ile(prenom: str, nom_ile: str) -> None:
    """Célébration forte de fin d'île (D-T8.6-F) : modal dédié, distinct de la
    célébration légère, avec balloons + message d'Archimède personnalisé.

    Doit être appelée à chaque rerun tant que la célébration doit rester
    affichée (même pattern que modal_planche_bd.py) — c'est le bouton interne
    qui efface le flag et route vers la carte, pas cette fonction elle-même.
    """
    st.balloons()

    @st.dialog("Une île s'élève !", width="large")
    def _modal() -> None:
        st.markdown(f"## {nom_ile} est libre.")
        texte = _MESSAGE_FIN_ILE_PLACEHOLDER.format(prenom=prenom, nom_ile=nom_ile)
        st.info(texte)
        if st.button(
            "Retour à l'archipel →",
            key="btn_celebration_fin_ile_retour",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.celebration_fin_ile_a_afficher = None
            st.session_state.ecran_courant = "carte"
            st.rerun()

    _modal()
