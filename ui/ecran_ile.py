import streamlit as st
from config.constants import ILE_NOMS


def render_ile():
    ile_id = st.session_state.get("ile_courante", "ile_1")
    nom = ILE_NOMS.get(ile_id, ile_id)
    st.title(nom)
    st.caption("Écran île — Sprint 3")
    if st.button("Commencer la Session 1"):
        st.session_state.ecran_courant = "session"
        st.rerun()
    if st.button("← Retour à la carte"):
        st.session_state.ecran_courant = "carte"
        st.rerun()
