import streamlit as st
from config.constants import ILE_NOMS


def render_carte():
    st.title("L'Ascension des Sept Îles")
    st.caption("Carte de l'archipel — Sprint 3")
    for ile_id, nom in ILE_NOMS.items():
        if st.button(nom, key=f"btn_{ile_id}"):
            st.session_state.ile_courante = ile_id
            st.session_state.ecran_courant = "ile"
            st.rerun()
