"""
ui/ecran_avatar.py — Écran de Choix d'Avatar
Sprint 3 T6
Sprint 3 T8.5 — accueil + prénom déplacés vers ecran_accueil.py (D-T8.5-A/D) ;
                réduction à 2 avatars canoniques, étape "grille" supprimée.

Séquence des 2 étapes pilotée par st.session_state["etape_onboarding"] :
    "genre"        → choix de l'avatar → assigne directement l'avatar
                     canonique du genre (fille → Sassou, garçon → Mélian)
    "confirmation" → validation du choix, puis création du joueur et sortie
                     vers l'écran de présentation de l'archipel

L'étape "bienvenue" (accueil personnalisé d'Archimède) a été retirée : elle
annonçait l'archipel et invitait à ouvrir la carte, exactement comme l'écran
de présentation qui la suivait. Son texte est repris par celui-ci.

Point d'entrée public : afficher_ecran_avatar()
"""

from pathlib import Path

import streamlit as st

from config.constants import AVATARS_REGISTRY
from data_layer.joueurs import creer_joueur, joueur_existe

# ── Chemins ───────────────────────────────────────────────────────────────────

_ASSETS_MENTOR = Path(__file__).parent.parent / "assets" / "mentor"

# ── Avatars canoniques (D-T8.5-A, cohérent avec D18) ──────────────────────────
# Plus de choix parmi 4 avatars par genre — un seul avatar canonique assigné
# automatiquement. Le registre complet (config/constants.py::AVATARS_REGISTRY)
# n'est pas modifié — reporté au sprint polish semaine 4 (voir brief T8.5 §4).

_AVATAR_CANONIQUE: dict[str, str] = {
    "fille": "sassou",
    "garcon": "melian",
}

# Libellés affichés à l'enfant. On ne parle plus de genre à l'écran : chaque
# avatar est nommé par son archétype. Purement cosmétique — le genre stocké
# (avatar_genre) et le rôle du registre restent inchangés.
_LIBELLE_AVATAR: dict[str, str] = {
    "garcon": "L'aventurier",
    "fille":  "L'architecte",
}


# ── Helpers image ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _charger_image(chemin: str) -> bytes | None:
    """Charge une image en bytes. Retourne None si le fichier est absent."""
    p = Path(chemin)
    if p.exists():
        return p.read_bytes()
    return None


def _chemin_avatar(genre: str, fichier: str) -> Path:
    return _ASSETS_MENTOR / genre / fichier


# Prénoms avec accents que .capitalize() ne peut pas restituer
# (clés = valeurs du registre en minuscules sans accent)
_PRENOMS_DISPLAY: dict[str, str] = {
    "aurele": "Aurèle",
    "melian": "Mélian",
}


def _afficher_prenom(prenom: str) -> str:
    """Retourne le prénom correctement accentué et capitalisé."""
    return _PRENOMS_DISPLAY.get(prenom, prenom.capitalize())


# ── Initialisation session_state ─────────────────────────────────────────────

def _init_state() -> None:
    if "etape_onboarding" not in st.session_state:
        st.session_state["etape_onboarding"] = "genre"
    if "genre_choisi" not in st.session_state:
        st.session_state["genre_choisi"] = None
    if "avatar_choisi" not in st.session_state:
        st.session_state["avatar_choisi"] = None


# ── Étape 1 : Choix du genre → assignation directe de l'avatar canonique ─────

def _afficher_choix_genre() -> None:
    st.markdown(
        "<h2 style='text-align:center;margin-bottom:2rem;'>Qui sera ton avatar ?</h2>",
        unsafe_allow_html=True,
    )

    col_g, col_f = st.columns(2, gap="large")

    for col, genre, label in [
        (col_g, "garcon", _LIBELLE_AVATAR["garcon"]),
        (col_f, "fille",  _LIBELLE_AVATAR["fille"]),
    ]:
        with col:
            prenom = _AVATAR_CANONIQUE[genre]
            meta = AVATARS_REGISTRY[genre][prenom]
            chemin = _chemin_avatar(genre, meta["fichier"])
            img = _charger_image(str(chemin))
            if img:
                st.image(img, use_container_width=True)
            if st.button(label, key=f"btn_genre_{genre}", use_container_width=True):
                st.session_state["genre_choisi"] = genre
                st.session_state["avatar_choisi"] = {
                    "genre":   genre,
                    "prenom":  prenom,
                    "role":    meta["role"],
                    "fichier": meta["fichier"],
                }
                st.session_state["etape_onboarding"] = "confirmation"
                st.rerun()


# ── Étape 2 : Confirmation ────────────────────────────────────────────────────

def _afficher_confirmation() -> None:
    avatar = st.session_state["avatar_choisi"]
    libelle = _LIBELLE_AVATAR[avatar["genre"]]

    st.markdown(
        f"<h2 style='text-align:center;margin-bottom:2rem;'>{libelle}</h2>",
        unsafe_allow_html=True,
    )

    chemin = _chemin_avatar(avatar["genre"], avatar["fichier"])
    img = _charger_image(str(chemin))

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if img:
            st.image(img, use_container_width=True)
        # Le nom du personnage (Sassou / Mélian) n'est plus affiché : l'enfant
        # choisit un archétype, pas un prénom déjà écrit pour lui.
        st.markdown("<br>", unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ Confirmer", key="btn_confirmer", type="primary", use_container_width=True):
                try:
                    creer_joueur(
                        genre=avatar["genre"],
                        avatar_prenom=avatar["prenom"],
                        role=avatar["role"],
                        prenom=st.session_state.get("prenom_saisi"),
                    )
                    # La partie vient d'être ouverte : son lien est montré une
                    # fois au parent (sans compte ni email, ce lien EST la
                    # partie). Le récit reprend juste après, à l'unique écran
                    # d'annonce de l'archipel (D-T8.5-E).
                    st.session_state["ecran_courant"] = "lien_partie"
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        with col_btn2:
            if st.button("↩ Changer d'avatar", key="btn_rechoisir", use_container_width=True):
                st.session_state["avatar_choisi"] = None
                st.session_state["etape_onboarding"] = "genre"
                st.rerun()


# ── Point d'entrée public ─────────────────────────────────────────────────────

def afficher_ecran_avatar() -> None:
    """
    Dispatche vers la bonne étape selon session_state["etape_onboarding"].

    Si un joueur existe déjà en base, l'avatar est irréversible : on ne
    repropose pas le choix, on renvoie à la carte. app.py y route déjà les
    sessions suivantes — ce court-circuit est le filet si un état résiduel
    ramenait quand même sur cet écran.
    """
    _init_state()

    if joueur_existe():
        st.session_state["ecran_courant"] = "carte"
        st.rerun()

    etape = st.session_state["etape_onboarding"]

    _DISPATCH = {
        "genre":        _afficher_choix_genre,
        "confirmation": _afficher_confirmation,
    }

    handler = _DISPATCH.get(etape)
    if handler is None:
        st.error(f"Étape d'onboarding inconnue : {etape!r}")
        return

    handler()
