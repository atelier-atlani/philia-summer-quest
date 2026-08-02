"""
ui/ecran_avatar.py — Écran de Choix d'Avatar
Sprint 3 T6
Sprint 3 T8.5 — accueil + prénom déplacés vers ecran_accueil.py (D-T8.5-A/D) ;
                réduction à 2 avatars canoniques, étape "grille" supprimée.

Séquence des 3 étapes pilotée par st.session_state["etape_onboarding"] :
    "genre"        → choix Fille / Garçon → assigne directement l'avatar
                     canonique du genre (fille → Sassou, garçon → Mélian)
    "confirmation" → validation du choix
    "bienvenue"    → accueil personnalisé d'Archimède

Point d'entrée public : afficher_ecran_avatar()
"""

from pathlib import Path

import streamlit as st

from config.constants import ARCHIMEDE_FICHIER, AVATARS_REGISTRY
from data_layer.joueurs import charger_joueur_courant, creer_joueur, joueur_existe

# ── Chemins ───────────────────────────────────────────────────────────────────

_ASSETS_MENTOR = Path(__file__).parent.parent / "assets" / "mentor"
_ARCHIMEDE_PATH = _ASSETS_MENTOR / "mentor" / ARCHIMEDE_FICHIER

# ── Avatars canoniques (D-T8.5-A, cohérent avec D18) ──────────────────────────
# Plus de choix parmi 4 avatars par genre — un seul avatar canonique assigné
# automatiquement. Le registre complet (config/constants.py::AVATARS_REGISTRY)
# n'est pas modifié — reporté au sprint polish semaine 4 (voir brief T8.5 §4).

_AVATAR_CANONIQUE: dict[str, str] = {
    "fille": "sassou",
    "garcon": "melian",
}


# ── Textes narratifs ──────────────────────────────────────────────────────────

_TEXTE_BIENVENUE = """\
Bienvenue à bord, {prenom}.

Le voyage commence maintenant. Devant toi, sept îles
silencieuses. La première t'appelle déjà : l'Île des
Nombres Brisés.

Approche la carte de l'archipel et choisis ton point
de départ."""

# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS_BIENVENUE = """
<style>
.philia-bienvenue {
    opacity: 0;
    animation: philia-fade-up 1s ease 0.3s forwards;
}
@keyframes philia-fade-up {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0);    }
}
</style>
"""


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
        "<h2 style='text-align:center;margin-bottom:2rem;'>Es-tu garçon ou fille ?</h2>",
        unsafe_allow_html=True,
    )

    col_g, col_f = st.columns(2, gap="large")

    for col, genre, label in [
        (col_g, "garcon", "👦 Garçon"),
        (col_f, "fille",  "👧 Fille"),
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
    prenom_cap = _afficher_prenom(avatar["prenom"])

    st.markdown(
        f"<h2 style='text-align:center;margin-bottom:2rem;'>Tu choisis {prenom_cap} ?</h2>",
        unsafe_allow_html=True,
    )

    chemin = _chemin_avatar(avatar["genre"], avatar["fichier"])
    img = _charger_image(str(chemin))

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if img:
            st.image(img, use_container_width=True)
        st.markdown(
            f'<p style="text-align:center;font-size:1.1rem;font-weight:600;">'
            f'{prenom_cap} · {avatar["role"].capitalize()}</p>',
            unsafe_allow_html=True,
        )
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
                    st.session_state["etape_onboarding"] = "bienvenue"
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        with col_btn2:
            if st.button("↩ Changer de genre", key="btn_rechoisir", use_container_width=True):
                st.session_state["avatar_choisi"] = None
                st.session_state["etape_onboarding"] = "genre"
                st.rerun()


# ── Étape 3 : Bienvenue d'Archimède ──────────────────────────────────────────

def _afficher_bienvenue() -> None:
    joueur = charger_joueur_courant()
    prenom_reel = (joueur.get("prenom") if joueur else None) or "Élévateur"

    st.markdown(_CSS_BIENVENUE, unsafe_allow_html=True)

    col_img, col_txt = st.columns([1, 2], gap="large")

    with col_img:
        img = _charger_image(str(_ARCHIMEDE_PATH))
        if img:
            st.image(img, use_container_width=True)

    with col_txt:
        texte = _TEXTE_BIENVENUE.format(prenom=prenom_reel)
        lignes = texte.strip().split("\n\n")
        html = "\n".join(
            f'<p style="margin-bottom:1em;">{p.replace(chr(10), "<br>")}</p>'
            for p in lignes
        )
        st.markdown(
            f'<div class="philia-bienvenue" style="font-size:1.05rem;line-height:1.8;">'
            f'{html}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚓ Embarquer pour l'aventure", key="btn_decouvrir", type="primary"):
            # Transition vers l'écran de présentation de l'archipel (D-T8.5-E)
            st.session_state["ecran_courant"] = "presentation_archipel"
            st.rerun()


# ── Point d'entrée public ─────────────────────────────────────────────────────

def afficher_ecran_avatar() -> None:
    """
    Dispatche vers la bonne étape selon session_state["etape_onboarding"].

    Si un joueur existe déjà en base (session suivante), saute directement
    à l'étape "bienvenue" pour éviter de redemander le choix d'avatar.
    """
    _init_state()

    # Court-circuit : joueur déjà créé (reconnexion)
    if joueur_existe() and st.session_state["etape_onboarding"] not in ("bienvenue",):
        st.session_state["etape_onboarding"] = "bienvenue"

    etape = st.session_state["etape_onboarding"]

    _DISPATCH = {
        "genre":        _afficher_choix_genre,
        "confirmation": _afficher_confirmation,
        "bienvenue":    _afficher_bienvenue,
    }

    handler = _DISPATCH.get(etape)
    if handler is None:
        st.error(f"Étape d'onboarding inconnue : {etape!r}")
        return

    handler()
