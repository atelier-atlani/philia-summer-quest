"""
ui/ecran_avatar.py — Écran de Choix d'Avatar + Onboarding Narratif
Sprint 3 T6

Séquence des 5 étapes pilotée par st.session_state["etape_onboarding"] :
    "accueil"      → discours d'Archimède + bouton Lever l'ancre
    "genre"        → choix Fille / Garçon
    "grille"       → 4 avatars du genre choisi
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


# ── Textes narratifs ──────────────────────────────────────────────────────────

_TEXTE_ACCUEIL = """\
Approche, jeune élévateur.

Il y a très longtemps, l'Archipel des Sept Îles a sombré.
Chacune garde aujourd'hui une Loi oubliée, scellée par
une épreuve.

Sept îles. Sept lois. Sept épreuves.

Pour chaque île que tu réveilleras, tu gagneras une clé.
Et au bout du voyage, quand les sept clés seront entre
tes mains, j'ouvrirai pour toi le coffre de mon secret
le plus précieux — celui que j'ai découvert dans un bain,
il y a plus de deux mille ans.

Mais sache ceci : on n'élève pas une île en récitant.
On l'élève en comprenant.

Es-tu prêt à commencer ?"""

_TEXTE_BIENVENUE = """\
Bienvenue à bord, {prenom}.

Le voyage commence maintenant. Devant toi, sept îles
silencieuses. La première t'appelle déjà : l'Île des
Nombres Brisés.

Approche la carte de l'archipel et choisis ton point
de départ."""

# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS_FADE_IN = """
<style>
/* Fade-in en cascade pour le texte d'accueil */
.philia-accueil-ligne {
    opacity: 0;
    animation: philia-fade-up 0.7s ease forwards;
}
.philia-accueil-ligne:nth-child(1)  { animation-delay: 0.0s; }
.philia-accueil-ligne:nth-child(2)  { animation-delay: 0.8s; }
.philia-accueil-ligne:nth-child(3)  { animation-delay: 1.6s; }
.philia-accueil-ligne:nth-child(4)  { animation-delay: 2.4s; }
.philia-accueil-ligne:nth-child(5)  { animation-delay: 3.2s; }
.philia-accueil-ligne:nth-child(6)  { animation-delay: 4.0s; }
.philia-accueil-ligne:nth-child(7)  { animation-delay: 4.8s; }
.philia-accueil-ligne:nth-child(8)  { animation-delay: 5.6s; }
.philia-accueil-ligne:nth-child(9)  { animation-delay: 6.4s; }
.philia-accueil-ligne:nth-child(10) { animation-delay: 7.2s; }

@keyframes philia-fade-up {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0);    }
}

/* Vignette avatar */
.philia-vignette {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    padding: 12px;
    border-radius: 12px;
    transition: background-color 0.2s ease, box-shadow 0.2s ease;
}
.philia-vignette:hover {
    background-color: rgba(74, 159, 255, 0.12);
    box-shadow: 0 0 18px rgba(74, 159, 255, 0.4);
}
.philia-prenom {
    font-size: 1.1rem;
    font-weight: 700;
    margin-top: 6px;
    color: #1E2937;
    text-transform: capitalize;
}
.philia-role {
    font-size: 0.78rem;
    color: #9BBFDE;
    margin-top: 2px;
    text-transform: capitalize;
}
</style>
"""

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
        st.session_state["etape_onboarding"] = "accueil"
    if "genre_choisi" not in st.session_state:
        st.session_state["genre_choisi"] = None
    if "avatar_choisi" not in st.session_state:
        st.session_state["avatar_choisi"] = None


# ── Étape 1 : Accueil narratif ────────────────────────────────────────────────

def _afficher_accueil() -> None:
    st.markdown(_CSS_FADE_IN, unsafe_allow_html=True)

    col_img, col_txt = st.columns([1, 2], gap="large")

    with col_img:
        img = _charger_image(str(_ARCHIMEDE_PATH))
        if img:
            st.image(img, use_container_width=True)
        else:
            st.markdown("🏺")  # fallback si image absente

    with col_txt:
        # Découpage du texte en paragraphes → chaque paragraphe = une ligne animée
        paragraphes = [p.strip() for p in _TEXTE_ACCUEIL.split("\n\n") if p.strip()]
        lignes_html = "\n".join(
            f'<p class="philia-accueil-ligne">{p.replace(chr(10), "<br>")}</p>'
            for p in paragraphes
        )
        st.markdown(
            f'<div style="font-size:1.05rem;line-height:1.8;">{lignes_html}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚓ Lever l'ancre", key="btn_lever_ancre", type="primary"):
            st.session_state["etape_onboarding"] = "genre"
            st.rerun()


# ── Étape 2 : Choix du genre ──────────────────────────────────────────────────

def _afficher_choix_genre() -> None:
    st.markdown(
        "<h2 style='text-align:center;margin-bottom:2rem;'>Es-tu garçon ou fille ?</h2>",
        unsafe_allow_html=True,
    )

    col_g, col_f = st.columns(2, gap="large")

    # Représentant visuel : premier avatar de chaque genre
    _REPR = {
        "garcon": ("aurele", AVATARS_REGISTRY["garcon"]["aurele"]),
        "fille":  ("livia",  AVATARS_REGISTRY["fille"]["livia"]),
    }

    for col, genre, label in [
        (col_g, "garcon", "👦 Garçon"),
        (col_f, "fille",  "👧 Fille"),
    ]:
        with col:
            prenom, meta = _REPR[genre]
            chemin = _chemin_avatar(genre, meta["fichier"])
            img = _charger_image(str(chemin))
            if img:
                st.image(img, use_container_width=True)
            if st.button(label, key=f"btn_genre_{genre}", use_container_width=True):
                st.session_state["genre_choisi"] = genre
                st.session_state["etape_onboarding"] = "grille"
                st.rerun()


# ── Étape 3 : Grille des 4 avatars ───────────────────────────────────────────

def _afficher_grille() -> None:
    genre = st.session_state["genre_choisi"]
    avatars = AVATARS_REGISTRY[genre]  # dict prenom → {role, fichier}

    st.markdown(
        "<h2 style='text-align:center;margin-bottom:2rem;'>Quel élévateur seras-tu ?</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(_CSS_FADE_IN, unsafe_allow_html=True)

    cols = st.columns(4, gap="medium")
    for col, (prenom, meta) in zip(cols, avatars.items()):
        chemin = _chemin_avatar(genre, meta["fichier"])
        img = _charger_image(str(chemin))
        with col:
            if img:
                st.image(img, use_container_width=True)
            st.markdown(
                f'<p class="philia-prenom">{_afficher_prenom(prenom)}</p>'
                f'<p class="philia-role">{meta["role"].capitalize()}</p>',
                unsafe_allow_html=True,
            )
            if st.button(
                f"Choisir {_afficher_prenom(prenom)}",
                key=f"btn_avatar_{prenom}",
                use_container_width=True,
            ):
                st.session_state["avatar_choisi"] = {
                    "genre":   genre,
                    "prenom":  prenom,
                    "role":    meta["role"],
                    "fichier": meta["fichier"],
                }
                st.session_state["etape_onboarding"] = "confirmation"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Changer de genre", key="btn_retour_genre"):
        st.session_state["etape_onboarding"] = "genre"
        st.rerun()


# ── Étape 4 : Confirmation ────────────────────────────────────────────────────

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
                        prenom=avatar["prenom"],
                        role=avatar["role"],
                    )
                    st.session_state["etape_onboarding"] = "bienvenue"
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        with col_btn2:
            if st.button("↩ Choisir un autre", key="btn_rechoisir", use_container_width=True):
                st.session_state["avatar_choisi"] = None
                st.session_state["etape_onboarding"] = "grille"
                st.rerun()


# ── Étape 5 : Bienvenue d'Archimède ──────────────────────────────────────────

def _afficher_bienvenue() -> None:
    joueur = charger_joueur_courant()
    prenom_cap = _afficher_prenom(joueur["avatar_prenom"]) if joueur else "élévateur"

    st.markdown(_CSS_BIENVENUE, unsafe_allow_html=True)

    col_img, col_txt = st.columns([1, 2], gap="large")

    with col_img:
        img = _charger_image(str(_ARCHIMEDE_PATH))
        if img:
            st.image(img, use_container_width=True)

    with col_txt:
        texte = _TEXTE_BIENVENUE.format(prenom=prenom_cap)
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
        if st.button("⚓ Découvrir l'archipel", key="btn_decouvrir", type="primary"):
            # Transition vers carte — routing géré dans app.py (hors scope T6)
            st.session_state["ecran"] = "carte"
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
        "accueil":      _afficher_accueil,
        "genre":        _afficher_choix_genre,
        "grille":       _afficher_grille,
        "confirmation": _afficher_confirmation,
        "bienvenue":    _afficher_bienvenue,
    }

    handler = _DISPATCH.get(etape)
    if handler is None:
        st.error(f"Étape d'onboarding inconnue : {etape!r}")
        return

    handler()
