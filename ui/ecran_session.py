import streamlit as st


def render_session():
    st.title("Session — Le Pont Fracturé")
    st.caption("Écran de session — connecté au mentor Archimède (Tâche 5)")
    st.info("Le chat avec Archimède sera disponible après la Tâche 5.")
    if st.button("← Retour à l'île"):
        st.session_state.ecran_courant = "ile"
        st.rerun()
