"""
app_test_carte.py — Test isolation de l'écran Carte de l'Archipel.

Usage :
    streamlit run app_test_carte.py

Lance UNIQUEMENT l'écran carte sans passer par le routing de app.py.
Permet de vérifier visuellement l'affichage et les interactions
avant de valider l'intégration dans l'application principale.

À NE PAS committer en production — fichier de test Sprint 3.
"""
import streamlit as st

st.set_page_config(
    page_title="[TEST] Carte — Philia Summer Quest",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialisation session state minimale (simule ce que app.py ferait)
if "ecran_courant" not in st.session_state:
    st.session_state.ecran_courant = "carte"
if "ile_courante" not in st.session_state:
    st.session_state.ile_courante = None
if "enfant_id" not in st.session_state:
    st.session_state.enfant_id = None  # Mode dev : île 1 accessible

# Import et affichage de l'écran carte
from ui.ecran_carte import render_carte

render_carte()

# Feedback de navigation (pour tester que le clic fonctionne)
if st.session_state.get("ecran_courant") == "ile":
    st.success(
        f"✅ Navigation déclenchée vers : `{st.session_state.get('ile_courante')}`  "
        f"— `ecran_courant = 'ile'`"
    )
    if st.button("↩️ Revenir à la carte"):
        st.session_state.ecran_courant = "carte"
        st.session_state.ile_courante = None
        st.rerun()
