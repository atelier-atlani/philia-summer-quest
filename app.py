import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Philia Summer Quest",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialisation session_state (clés définies dans brief-implementer-technique-1a §3)
_DEFAULTS = {
    "enfant_id": None,
    "parent_id": None,
    "ecran_courant": "carte",
    "ile_courante": "ile_1",
    "session_active": None,
    "mode_courant": "decouverte",
    "historique_chat": [],
    "profil_cache": None,
    "progression_cache": None,
}
for key, val in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Routing
ecran = st.session_state.ecran_courant

if ecran == "carte":
    from ui.ecran_carte import render_carte
    render_carte()
elif ecran == "ile":
    from ui.ecran_ile import render_ile
    render_ile()
elif ecran == "session":
    from ui.ecran_session import render_session
    render_session()
else:
    st.error(f"Écran inconnu : {ecran}")
