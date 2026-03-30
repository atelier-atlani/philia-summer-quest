"""training/profile_ui.py – Onboarding conversationnel guidé par le formateur.

Layout moderne : avatar portrait (gauche) + chat style (droite).
7 questions enchaînées (ajout genre) avec historique visible en bulles chat.
Tableau blanc récapitulatif en fin d'onboarding.
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

# Mapping libellé radio → clé interne niveau
_NIVEAU_RADIO_OPTIONS = [
    ("Je débute (moins d'1 an)", "debutant"),
    ("J'ai de l'expérience (1-3 ans)", "confirme"),
    ("Je suis confirmé (3+ ans)", "expert"),
]

_GENRE_RADIO_OPTIONS = [
    ("Un homme", "homme"),
    ("Une femme", "femme"),
    ("Préfère ne pas préciser", "autre"),
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

_ASSETS = Path("assets/avatars")


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def _init_profile_state() -> None:
    """Initialise l'état onboarding dans st.session_state."""
    if "profile_step" not in st.session_state:
        st.session_state.profile_step = 0
    if "profile_draft" not in st.session_state:
        st.session_state.profile_draft = {}


def _reset_profile() -> None:
    """Réinitialise l'état onboarding."""
    st.session_state.pop("profile_step", None)
    st.session_state.pop("profile_draft", None)


# ---------------------------------------------------------------------------
# Avatar portrait
# ---------------------------------------------------------------------------

def _avatar_emoji(genre: str) -> str:
    return "👨‍🏫" if genre == "homme" else "👩‍🏫"


def _avatar_name(genre: str) -> str:
    return "IAXEL" if genre == "homme" else "IALIX"


def _render_avatar_portrait(genre: str = "") -> None:
    """Affiche l'avatar formateur en format portrait (9:16)."""
    name = _avatar_name(genre)
    img_path = _ASSETS / f"{name.lower()}.png"
    vid_path = _ASSETS / f"{name.lower()}_video.mp4"

    if vid_path.exists():
        st.video(str(vid_path), autoplay=True, loop=True, muted=True)
    elif img_path.exists():
        st.image(str(img_path), use_container_width=True)
    else:
        emoji = _avatar_emoji(genre)
        st.markdown(
            f"""
<div style="width:100%;aspect-ratio:9/16;background:linear-gradient(135deg,#00B4A6 0%,#1e293b 100%);
            border-radius:16px;display:flex;align-items:center;justify-content:center;
            color:white;font-size:52px;">{emoji}</div>""",
            unsafe_allow_html=True,
        )
    st.markdown(f"**{name}**")
    st.caption("Votre formateur·rice IA")
    st.caption("● En écoute")


# ---------------------------------------------------------------------------
# Chat bubble helpers
# ---------------------------------------------------------------------------

def _sophie_msg(text: str, avatar_nom: str = "IALIX") -> None:
    """Bulle de message formateur (gris, gauche)."""
    st.markdown(
        f"""
<div style="background:#f0f2f6;padding:14px 18px;border-radius:16px 16px 16px 4px;
            margin:10px 0;line-height:1.5;">
    <strong>💬 {avatar_nom}</strong><br>{text}
</div>""",
        unsafe_allow_html=True,
    )


def _user_msg(text: str) -> None:
    """Bulle de réponse utilisateur (turquoise, droite)."""
    st.markdown(
        f"""
<div style="background:#00B4A6;color:white;padding:14px 18px;
            border-radius:16px 16px 4px 16px;margin:10px 0;text-align:right;line-height:1.5;">
    <strong>Vous</strong><br>{text}
</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Historique des échanges passés
# ---------------------------------------------------------------------------

_GENRE_LABELS = {
    "homme": "Un homme",
    "femme": "Une femme",
    "autre": "Préfère ne pas préciser",
}


def _render_past_message(step_num: int, data: dict) -> None:
    """Affiche un échange passé (question formateur + réponse utilisateur)."""
    exchanges = [
        ("Comment vous appelez-vous ?", "prenom"),
        ("Vous êtes... ?", "genre"),
        ("Quel est votre niveau en immobilier ?", "niveau"),
        ("Dans quelle ville travaillez-vous ?", "adresse_travail"),
        ("Quelles sont vos spécialités ?", "specialites"),
        ("Qu'est-ce que vous souhaitez améliorer en priorité ?", "objectif_principal"),
        ("Sur quoi rencontrez-vous le plus de difficultés ?", "points_faibles"),
    ]
    if step_num >= len(exchanges):
        return
    question, key = exchanges[step_num]
    # Avatar adapté dès que le genre est connu (à partir de l'échange 1)
    genre = data.get("genre", "") if step_num >= 1 else ""
    avatar_nom = _avatar_name(genre)

    answer = data.get(key, "")
    if isinstance(answer, list):
        answer = ", ".join(answer)
    elif key == "genre":
        answer = _GENRE_LABELS.get(answer, answer)

    if answer:
        _sophie_msg(question, avatar_nom)
        _user_msg(answer)


# ---------------------------------------------------------------------------
# Questions d'onboarding (style chat) — 7 étapes
# ---------------------------------------------------------------------------

def _ask_prenom_chat(data: dict) -> None:
    _sophie_msg(
        "Bonjour ! Bienvenue dans votre formation. Pour commencer, comment vous appelez-vous ?",
        "IALIX",
    )
    prenom = st.text_input(
        "Votre prénom", key="onb_prenom", placeholder="Ex : Thomas",
        value=data.get("prenom", ""), label_visibility="collapsed",
    )
    if st.button("Envoyer →", key="btn_onb_0", type="primary"):
        if prenom.strip():
            data["prenom"] = prenom.strip()
            st.session_state.profile_draft = data
            st.session_state.profile_step = 1
            st.rerun()
        else:
            st.warning("Merci d'entrer votre prénom !")


def _ask_genre_chat(data: dict) -> None:
    prenom = data.get("prenom", "")
    _sophie_msg(
        f"Enchanté·e {prenom} ! Pour personnaliser votre expérience, vous êtes… ?",
        "IALIX",
    )
    st.caption("💡 Cela me permet de choisir le formateur ou la formatrice qui vous accompagnera.")
    labels = [label for label, _ in _GENRE_RADIO_OPTIONS]
    current_genre = data.get("genre", "femme")
    default_idx = next(
        (i for i, (_, k) in enumerate(_GENRE_RADIO_OPTIONS) if k == current_genre), 1
    )
    choix = st.radio(
        "Vous êtes", labels, index=default_idx, key="onb_genre",
        label_visibility="collapsed",
    )
    if st.button("Envoyer →", key="btn_onb_1", type="primary"):
        genre_key = next(k for label, k in _GENRE_RADIO_OPTIONS if label == choix)
        data["genre"] = genre_key
        st.session_state.profile_draft = data
        st.session_state.profile_step = 2
        st.rerun()


def _ask_niveau_chat(data: dict) -> None:
    genre = data.get("genre", "")
    avatar_nom = _avatar_name(genre)
    prenom = data.get("prenom", "")
    _sophie_msg(
        f"Vous débutez dans l'immobilier, {prenom}, ou vous avez déjà de l'expérience ?",
        avatar_nom,
    )
    labels = [label for label, _ in _NIVEAU_RADIO_OPTIONS]
    current_niveau = data.get("niveau", "debutant")
    default_idx = next(
        (i for i, (_, k) in enumerate(_NIVEAU_RADIO_OPTIONS) if k == current_niveau), 0
    )
    choix = st.radio(
        "Votre niveau", labels, index=default_idx, key="onb_niveau",
        label_visibility="collapsed",
    )
    if st.button("Envoyer →", key="btn_onb_2", type="primary"):
        niveau_key = next(k for label, k in _NIVEAU_RADIO_OPTIONS if label == choix)
        data["niveau"] = niveau_key
        st.session_state.profile_draft = data
        st.session_state.profile_step = 3
        st.rerun()


def _ask_adresse_chat(data: dict) -> None:
    genre = data.get("genre", "")
    avatar_nom = _avatar_name(genre)
    prenom = data.get("prenom", "")
    _sophie_msg(
        f"Parfait {prenom} ! Dans quelle ville travaillez-vous ? "
        "<small>(ou l'adresse de votre agence)</small><br>"
        "<small style='color:#888'>Cette information me permettra de personnaliser "
        "les cours sur votre marché local.</small>",
        avatar_nom,
    )
    adresse = st.text_input(
        "Ville ou adresse", key="onb_adresse",
        placeholder="Ex : Aubervilliers ou 12 rue de Paris, Aubervilliers",
        value=data.get("adresse_travail", ""), label_visibility="collapsed",
    )
    if st.button("Envoyer →", key="btn_onb_3", type="primary"):
        if adresse.strip():
            data["adresse_travail"] = adresse.strip()
            data["ville_travail"] = _extract_ville(adresse.strip())
            st.session_state.profile_draft = data
            st.session_state.profile_step = 4
            st.rerun()
        else:
            st.warning("Merci d'entrer votre ville ou l'adresse de votre agence !")


def _ask_specialites_chat(data: dict) -> None:
    genre = data.get("genre", "")
    avatar_nom = _avatar_name(genre)
    ville = data.get("ville_travail", "")
    ville_txt = f" à {ville}" if ville else ""
    _sophie_msg(
        f"Super{ville_txt} ! Vous faites plutôt de la vente, de la location, ou les deux ?",
        avatar_nom,
    )
    spec_options = list(SPECIALITES_LABELS.values())
    current_specs = data.get("specialites", [])
    default_specs = [SPECIALITES_LABELS[s] for s in current_specs if s in SPECIALITES_LABELS]
    selected = st.multiselect(
        "Vos spécialités", spec_options, default=default_specs,
        key="onb_specialites", label_visibility="collapsed",
    )
    if st.button("Envoyer →", key="btn_onb_4", type="primary"):
        spec_keys = [SPECIALITES[spec_options.index(s)] for s in selected] if selected else ["vendeur"]
        data["specialites"] = spec_keys[:3]
        st.session_state.profile_draft = data
        st.session_state.profile_step = 5
        st.rerun()


def _ask_objectif_chat(data: dict) -> None:
    genre = data.get("genre", "")
    avatar_nom = _avatar_name(genre)
    prenom = data.get("prenom", "")
    _sophie_msg(
        f"Bien {prenom} ! Qu'est-ce que vous souhaitez améliorer en priorité dans votre métier ?",
        avatar_nom,
    )
    objectif = st.text_area(
        "Votre objectif principal", key="onb_objectif",
        placeholder="Ex : Améliorer ma prospection, conclure plus de mandats, mieux gérer les objections...",
        value=data.get("objectif_principal", ""), height=80,
        label_visibility="collapsed",
    )
    if st.button("Envoyer →", key="btn_onb_5", type="primary"):
        if objectif.strip():
            data["objectif_principal"] = objectif.strip()
            st.session_state.profile_draft = data
            st.session_state.profile_step = 6
            st.rerun()
        else:
            st.warning("Merci de partager votre objectif principal !")


def _ask_points_faibles_chat(data: dict) -> None:
    genre = data.get("genre", "")
    avatar_nom = _avatar_name(genre)
    prenom = data.get("prenom", "")
    _sophie_msg(
        f"Dernière question {prenom} : sur quoi rencontrez-vous le plus de difficultés "
        "actuellement ? (Soyez honnête, c'est pour vous aider !)",
        avatar_nom,
    )
    current_faibles = data.get("points_faibles", [])
    default_faibles = [f for f in current_faibles if f in _POINTS_FAIBLES_OPTIONS]
    selected = st.multiselect(
        "Vos points à améliorer (max 3)", _POINTS_FAIBLES_OPTIONS,
        default=default_faibles, key="onb_faibles", label_visibility="collapsed",
    )
    if len(selected) > 3:
        st.warning("3 points maximum. Les 3 premiers seront retenus.")
    if st.button("Envoyer →", key="btn_onb_6", type="primary"):
        data["points_faibles"] = selected[:3]
        st.session_state.profile_draft = data
        st.session_state.profile_step = 7
        st.rerun()


# ---------------------------------------------------------------------------
# Finalisation — tableau blanc récapitulatif
# ---------------------------------------------------------------------------

def _extract_ville(adresse: str) -> str:
    """Extrait la ville : dernier segment après la virgule, sinon l'adresse entière."""
    if "," in adresse:
        return adresse.split(",")[-1].strip()
    return adresse.strip()


def _finalize(data: dict) -> Optional[UserProfile]:
    """Tableau blanc récapitulatif + bouton Démarrer.

    Retourne le UserProfile uniquement quand l'utilisateur clique sur
    'Démarrer la formation', None sinon.
    """
    profile = UserProfile(
        prenom=data.get("prenom", ""),
        genre=data.get("genre", ""),
        niveau=data.get("niveau", "debutant"),
        role=data.get("role", "conseiller_vente"),
        specialites=data.get("specialites", ["vendeur"]),
        objectif_principal=data.get("objectif_principal", ""),
        points_faibles=data.get("points_faibles", []),
        format_prefere=data.get("format_prefere", "cas_pratique"),
        adresse_travail=data.get("adresse_travail", ""),
        ville_travail=data.get("ville_travail", ""),
    )

    avatar_nom = _avatar_name(profile.genre)
    _sophie_msg(
        f"Parfait {profile.prenom} ! Voici un récapitulatif de votre profil avant de démarrer.",
        avatar_nom,
    )

    st.markdown("#### 📊 Votre profil")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Prénom :** {profile.prenom}")
        st.markdown(f"**Niveau :** {NIVEAUX_LABELS.get(profile.niveau, profile.niveau)}")
        if profile.ville_travail:
            st.markdown(f"**Ville :** {profile.ville_travail}")
    with col2:
        if profile.specialites:
            specs_txt = ", ".join(SPECIALITES_LABELS.get(s, s) for s in profile.specialites)
            st.markdown(f"**Spécialités :** {specs_txt}")
        if profile.objectif_principal:
            obj_short = (
                profile.objectif_principal[:60]
                + ("…" if len(profile.objectif_principal) > 60 else "")
            )
            st.markdown(f"**Objectif :** {obj_short}")
        if profile.points_faibles:
            st.markdown(f"**À travailler :** {', '.join(profile.points_faibles)}")

    st.markdown("---")
    col_edit, col_start = st.columns([1, 2])
    with col_edit:
        if st.button("✏️ Modifier", key="btn_edit_profile_final"):
            st.session_state.profile_step = 0
            st.session_state.profile_draft = {}
            st.rerun()
    with col_start:
        if st.button("🚀 Démarrer la formation", key="btn_start_formation", type="primary"):
            _reset_profile()
            return profile
    return None


# ---------------------------------------------------------------------------
# Point d'entrée public
# ---------------------------------------------------------------------------

def render_profile_onboarding(existing_profile: Dict[str, Any]) -> Optional[UserProfile]:
    """Onboarding conversationnel avec layout avatar portrait + chat.

    7 questions : prénom → genre → niveau → adresse → spécialités →
    objectif → points faibles → récapitulatif.

    Args:
        existing_profile: Profil précédemment enregistré (peut être vide).

    Returns:
        UserProfile quand l'onboarding est validé, None sinon.
    """
    _init_profile_state()
    step = st.session_state.profile_step
    data = st.session_state.profile_draft

    # Pré-remplissage depuis le profil existant au premier chargement
    if not data and existing_profile:
        data.update(existing_profile)
        st.session_state.profile_draft = data

    # Layout : Avatar (25%) | Chat (75%)
    col_avatar, col_chat = st.columns([1, 3])

    with col_avatar:
        _render_avatar_portrait(data.get("genre", ""))

    result: Optional[UserProfile] = None
    with col_chat:
        st.caption(f"Question {min(step + 1, 7)}/7")

        # Historique des échanges validés
        for i in range(step):
            _render_past_message(i, data)

        # Question courante ou finalisation
        if step == 0:
            _ask_prenom_chat(data)
        elif step == 1:
            _ask_genre_chat(data)
        elif step == 2:
            _ask_niveau_chat(data)
        elif step == 3:
            _ask_adresse_chat(data)
        elif step == 4:
            _ask_specialites_chat(data)
        elif step == 5:
            _ask_objectif_chat(data)
        elif step == 6:
            _ask_points_faibles_chat(data)
        else:
            result = _finalize(data)

    return result
