"""
ui/ecran_chat.py — Zone de chat avec Archimède.

Responsabilité unique : afficher l'historique et traiter le message courant.

Pattern Streamlit correct :
- La boucle sur messages_pour_affichage() est la SEULE source d'affichage.
- Sur saisie : engine.repondre() sous spinner → persist → st.rerun().
- Au rerun, la boucle ré-affiche tout proprement, sans doublon.
"""

from __future__ import annotations

import streamlit as st

from pedagogie.session_engine import SessionEngine


def render_chat(engine: SessionEngine) -> None:
    # Seule source d'affichage des messages — ne rien afficher manuellement ailleurs
    for msg in engine.messages_pour_affichage():
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
            st.markdown(msg["content"])

    if engine.est_terminee:
        st.success("Session terminée. À bientôt, Élévateur !")
        return

    if user_input := st.chat_input("Ta réponse…"):
        with st.spinner("Archimède réfléchit…"):
            engine.repondre(user_input)
        st.session_state.session_active = engine.to_dict()
        st.rerun()
