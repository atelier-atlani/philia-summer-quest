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
    "ecran_courant": "avatar",  # défaut = onboarding, pas carte (Sprint 3 T6)
    "ile_courante": "ile_1",
    "session_active": None,
    "mode_courant": "decouverte",
    "historique_chat": [],
    "profil_cache": None,
    "progression_cache": None,
    "etape_onboarding": "accueil",  # point d'entrée séquence onboarding T6
}
for key, val in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Guard rail : si aucun joueur créé, forcer l'onboarding
# (protection contre un futur bug qui basculerait ecran_courant sans avatar)
from data_layer.joueurs import charger_joueur_courant

if charger_joueur_courant() is None and st.session_state.ecran_courant != "avatar":
    st.session_state.ecran_courant = "avatar"
    st.session_state.etape_onboarding = "accueil"

# Routing
ecran = st.session_state.ecran_courant

if ecran == "avatar":
    from ui.ecran_avatar import afficher_ecran_avatar
    afficher_ecran_avatar()
elif ecran == "carte":
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
