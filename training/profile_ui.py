"""training/profile_ui.py – Onboarding compact (formulaire horizontal).

Layout : formulaire à gauche + vidéo IAxel à droite.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

from training.profile import (
    UserProfile,
    NIVEAUX_LABELS,
    SPECIALITES,
    SPECIALITES_LABELS,
)

_ASSETS = Path("assets/avatars")

_NIVEAU_OPTIONS = [
    ("0–2 ans", "debutant"),
    ("3–5 ans", "confirme"),
    ("5+ ans", "expert"),
]

_GENRE_OPTIONS = [
    ("Masculin", "homme"),
    ("Féminin", "femme"),
]

_POINTS_FAIBLES_OPTIONS = [
    "Découverte vendeur",
    "Estimation / ACM",
    "Objections prix",
    "Prise de mandat",
    "Suivi vendeur",
    "Closing de vente",
    "Relance acquéreurs",
    "Prospection",
    "Négociation",
    "Fidélisation",
]


# ---------------------------------------------------------------------------
# State helpers (conservés — utilisés par app.py)
# ---------------------------------------------------------------------------

def _init_profile_state() -> None:
    if "profile_step" not in st.session_state:
        st.session_state.profile_step = 0
    if "profile_draft" not in st.session_state:
        st.session_state.profile_draft = {}


def _reset_profile() -> None:
    st.session_state.pop("profile_step", None)
    st.session_state.pop("profile_draft", None)
    st.session_state.pop("_tts_played_profil", None)


# ---------------------------------------------------------------------------
# Avatar helpers (conservés)
# ---------------------------------------------------------------------------

def _avatar_emoji(genre: str) -> str:
    return "👨‍🏫" if genre == "homme" else "👩‍🏫"


def _avatar_name(genre: str) -> str:
    return "IAXEL" if genre == "homme" else "IALIX"


def _render_avatar_portrait(genre: str = "") -> None:
    """Affiche la vidéo intro IAxel (ou image fallback)."""
    vid_path = _ASSETS / "IAxel - Parcours Formation Dynamique_720p_caption.mp4"
    img_path = Path("assets/images/IAXEL-formateur.png")
    if not img_path.exists():
        img_path = _ASSETS / "IAXEL-formateur.png"

    if vid_path.exists():
        st.video(str(vid_path), autoplay=True, loop=True, muted=True)
        st.caption("🔊 Cliquez sur la vidéo pour activer le son")
    elif img_path.exists():
        st.image(str(img_path), use_container_width=True)
    else:
        st.markdown(
            """
<div style="width:100%;aspect-ratio:9/16;background:linear-gradient(135deg,#00B4A6 0%,#1e293b 100%);
            border-radius:16px;display:flex;align-items:center;justify-content:center;
            color:white;font-size:64px;">🎓</div>""",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Utilitaire
# ---------------------------------------------------------------------------

def _extract_ville(adresse: str) -> str:
    if "," in adresse:
        return adresse.split(",")[-1].strip()
    return adresse.strip()


# ---------------------------------------------------------------------------
# Point d'entrée public
# ---------------------------------------------------------------------------

def render_profile_onboarding(existing_profile: Dict[str, Any]) -> Optional[UserProfile]:
    """Formulaire de profil compact — retourne UserProfile à la validation, None sinon."""

    col_form, col_video = st.columns([3, 2])

    with col_video:
        _render_avatar_portrait(existing_profile.get("genre", ""))

    with col_form:
        # Message d'accueil formateur
        is_new = not existing_profile.get("prenom")
        if is_new:
            accueil = (
                "Bonjour ! Je suis IAXEL, votre formateur immobilier. "
                "Avant de commencer, j'aimerais vous connaître un peu — "
                "ça me permettra d'adapter la formation à votre niveau et vos besoins. "
                "C'est rapide, 2 minutes."
            )
        else:
            accueil = (
                f"Rebonjour {existing_profile.get('prenom', '')} ! "
                "Vous souhaitez mettre à jour votre profil ? Pas de problème, modifiez ce qui a changé."
            )

        st.info(accueil)

        st.markdown("### Faisons connaissance" if is_new else "### 👤 Votre profil")

        # Ligne 1 : Prénom
        prenom = st.text_input(
            "Prénom",
            value=existing_profile.get("prenom", ""),
            placeholder="Ex : Thomas",
            key="pf_prenom",
        )

        # Ligne 2 : Expérience + Ville
        col1, col2 = st.columns(2)
        with col1:
            niveau_labels = [label for label, _ in _NIVEAU_OPTIONS]
            current_niveau = existing_profile.get("niveau", "debutant")
            default_niv = next(
                (i for i, (_, k) in enumerate(_NIVEAU_OPTIONS) if k == current_niveau), 0
            )
            exp_choix = st.selectbox(
                "Expérience", niveau_labels, index=default_niv, key="pf_niveau"
            )
        with col2:
            ville = st.text_input(
                "Ville de travail",
                value=existing_profile.get("adresse_travail", ""),
                placeholder="Ex : Lyon",
                key="pf_ville",
            )

        # Ligne 3 : Spécialités
        spec_options = list(SPECIALITES_LABELS.values())
        current_specs = existing_profile.get("specialites", [])
        default_specs = [SPECIALITES_LABELS[s] for s in current_specs if s in SPECIALITES_LABELS]
        selected_specs = st.multiselect(
            "Spécialités", spec_options, default=default_specs, key="pf_specs"
        )

        # Ligne 4 : Points à travailler
        current_faibles = existing_profile.get("points_faibles", [])
        default_faibles = [f for f in current_faibles if f in _POINTS_FAIBLES_OPTIONS]
        selected_faibles = st.multiselect(
            "Points à travailler (max 3)", _POINTS_FAIBLES_OPTIONS,
            default=default_faibles, key="pf_faibles"
        )

        # Ligne 5 : Genre
        genre_labels = [label for label, _ in _GENRE_OPTIONS]
        current_genre = existing_profile.get("genre", "homme")
        default_genre = next(
            (i for i, (_, k) in enumerate(_GENRE_OPTIONS) if k == current_genre), 0
        )
        genre_choix = st.radio(
            "Votre genre", genre_labels, index=default_genre,
            horizontal=True, key="pf_genre"
        )

        st.markdown("---")

        if st.button("Valider →", type="primary", key="pf_submit"):
            if not prenom.strip():
                st.warning("Merci d'entrer votre prénom.")
                return None

            niveau_key = next(k for label, k in _NIVEAU_OPTIONS if label == exp_choix)
            genre_key = next(k for label, k in _GENRE_OPTIONS if label == genre_choix)
            spec_keys = [SPECIALITES[spec_options.index(s)] for s in selected_specs] if selected_specs else ["vendeur"]

            profile = UserProfile(
                prenom=prenom.strip(),
                genre=genre_key,
                niveau=niveau_key,
                role=existing_profile.get("role", "conseiller_vente"),
                specialites=spec_keys[:3],
                objectif_principal=existing_profile.get("objectif_principal", ""),
                points_faibles=selected_faibles[:3],
                format_prefere=existing_profile.get("format_prefere", "cas_pratique"),
                adresse_travail=ville.strip(),
                ville_travail=_extract_ville(ville.strip()) if ville.strip() else "",
            )
            _reset_profile()
            return profile

    return None
