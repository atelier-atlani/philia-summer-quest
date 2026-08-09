import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Philia Summer Quest",
    page_icon="🏝️",
    layout="wide",
    # Tableau de bord permanent (spec collection, commit 3) : l'enfant doit voir
    # sa progression sans avoir à déplier quoi que ce soit.
    initial_sidebar_state="expanded",
)

# Initialisation session_state (clés définies dans brief-implementer-technique-1a §3)
from core.partie import partie_courante
from data_layer.joueurs import charger_joueur_courant

# Identité de la partie AVANT toute lecture du joueur : une base sert plusieurs
# familles, et c'est ce partie_id (porté par l'URL) qui dit laquelle joue.
# Sans lui, charger_joueur_courant() rend None et le visiteur part en onboarding.
_partie_id = partie_courante()

# Une nouvelle session dont le joueur existe déjà (retour de l'enfant, D19bis test 3)
# saute tout l'onboarding — pas de re-saisie du prénom, pas de re-choix d'avatar,
# et plus d'écran de bienvenue à reconsommer : l'enfant reprend à la carte.
_joueur_deja_cree = charger_joueur_courant() is not None

_DEFAULTS = {
    "enfant_id": None,
    "parent_id": None,
    # défaut = accueil narratif + saisie prénom pour un enfant neuf (Sprint 3 T8.5) ;
    # la carte directement si le joueur existe déjà (l'archipel lui a déjà été présenté)
    "ecran_courant": "carte" if _joueur_deja_cree else "accueil",
    "ile_courante": "ile_1",
    "session_active": None,
    "enigme_active": None,          # énigme finale Île 1 (D43)
    "mode_courant": "decouverte",
    "historique_chat": [],
    "profil_cache": None,
    "progression_cache": None,
    "etape_onboarding": "genre",
    "acces_deverrouille": False,
    "partie_id": _partie_id,
}
for key, val in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Portail d'accès — le jeu est déployé publiquement. Tant que le code n'a pas
# été saisi, portail_acces() affiche l'écran de code et coupe le script : rien
# du parcours ne se charge derrière.
from ui.ecran_acces import portail_acces

portail_acces()

# Guard rail : si aucun joueur créé, forcer l'accueil / onboarding
# (protection contre un futur bug qui basculerait ecran_courant sans avatar)
if charger_joueur_courant() is None and st.session_state.ecran_courant not in ("accueil", "avatar"):
    st.session_state.ecran_courant = "accueil"
    st.session_state.etape_onboarding = "genre"

# Routing
ecran = st.session_state.ecran_courant

if ecran == "accueil":
    from ui.ecran_accueil import afficher_ecran_accueil
    afficher_ecran_accueil()
elif ecran == "avatar":
    from ui.ecran_avatar import afficher_ecran_avatar
    afficher_ecran_avatar()
elif ecran == "lien_partie":
    from ui.ecran_lien_partie import afficher_ecran_lien_partie
    afficher_ecran_lien_partie()
elif ecran == "presentation_archipel":
    from ui.ecran_presentation_archipel import afficher_ecran_presentation_archipel
    afficher_ecran_presentation_archipel()
elif ecran == "carte":
    from ui.ecran_carte import render_carte
    render_carte()
elif ecran == "ile":
    from ui.ecran_ile import render_ile
    render_ile()
elif ecran == "session":
    from ui.ecran_session import render_session
    render_session()
elif ecran == "enigme":
    from ui.ecran_enigme import render_enigme
    render_enigme()
else:
    st.error(f"Écran inconnu : {ecran}")
