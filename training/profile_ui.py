"""training/profile_ui.py – Onboarding conversationnel guidé par le formateur.

6 questions enchaînées, ton formateur chaleureux, historique visible.
Collecte l'adresse de travail pour personnaliser le marché local.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st

from core.avatar import show_formateur_message
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


def _init_profile_state() -> None:
    """Initialize onboarding state in st.session_state."""
    if "profile_step" not in st.session_state:
        st.session_state.profile_step = 0
    if "profile_draft" not in st.session_state:
        st.session_state.profile_draft = {}


def _reset_profile() -> None:
    """Reset onboarding state."""
    st.session_state.pop("profile_step", None)
    st.session_state.pop("profile_draft", None)


def render_profile_onboarding(existing_profile: Dict[str, Any]) -> Optional[UserProfile]:
    """Onboarding conversationnel guidé par le formateur (6 questions).

    Args:
        existing_profile: Previously saved profile dict (may be empty).

    Returns:
        UserProfile if onboarding is complete, None otherwise.
    """
    _init_profile_state()
    step = st.session_state.profile_step
    data = st.session_state.profile_draft

    # Pre-fill from existing profile on first load
    if not data and existing_profile:
        data.update(existing_profile)
        st.session_state.profile_draft = data

    st.markdown("### Bienvenue dans ta formation")

    # Historique conversation
    for i in range(step):
        _render_past_exchange(i, data)

    # Question courante
    if step == 0:
        return _ask_prenom(data)
    elif step == 1:
        return _ask_niveau(data)
    elif step == 2:
        return _ask_adresse_travail(data)
    elif step == 3:
        return _ask_specialites(data)
    elif step == 4:
        return _ask_objectif(data)
    elif step == 5:
        return _ask_points_faibles(data)
    else:
        return _finalize(data)


def _ask_prenom(data: dict) -> None:
    show_formateur_message(
        "Bonjour ! Bienvenue dans votre formation. Pour commencer, dites-moi : comment vous appelez-vous ?",
        key="onb_q0", mood="happy",
    )
    prenom = st.text_input("Votre prénom", key="onb_prenom", placeholder="Ex : Thomas",
                           value=data.get("prenom", ""))
    if st.button("Continuer", key="btn_onb_0"):
        if prenom.strip():
            data["prenom"] = prenom.strip()
            st.session_state.profile_draft = data
            st.session_state.profile_step = 1
            st.rerun()
        else:
            st.warning("Merci d'entrer votre prénom !")
    return None


def _ask_niveau(data: dict) -> None:
    prenom = data.get("prenom", "")
    show_formateur_message(
        f"Enchanté {prenom} ! Dites-moi, vous débutez dans l'immobilier ou vous avez déjà de l'expérience ?",
        key="onb_q1", mood="neutral",
    )

    labels = [label for label, _ in _NIVEAU_RADIO_OPTIONS]
    current_niveau = data.get("niveau", "debutant")
    default_idx = next((i for i, (_, k) in enumerate(_NIVEAU_RADIO_OPTIONS) if k == current_niveau), 0)

    choix = st.radio("Votre niveau", labels, index=default_idx, key="onb_niveau")

    if st.button("Continuer", key="btn_onb_1"):
        niveau_key = next(k for label, k in _NIVEAU_RADIO_OPTIONS if label == choix)
        data["niveau"] = niveau_key
        st.session_state.profile_draft = data
        st.session_state.profile_step = 2
        st.rerun()
    return None


def _ask_adresse_travail(data: dict) -> None:
    prenom = data.get("prenom", "")
    show_formateur_message(
        f"Parfait {prenom} ! Dans quelle ville travaillez-vous ? "
        "(ou quelle est l'adresse de votre agence ?)<br>"
        "<small>Cette information me permettra de personnaliser les cours sur le marché local de votre zone.</small>",
        key="onb_q2", mood="thinking",
    )

    adresse = st.text_input(
        "Ville ou adresse de votre agence",
        key="onb_adresse",
        placeholder="Ex : Aubervilliers ou 12 rue de Paris, Aubervilliers",
        value=data.get("adresse_travail", ""),
    )

    if st.button("Continuer", key="btn_onb_2"):
        if adresse.strip():
            data["adresse_travail"] = adresse.strip()
            data["ville_travail"] = _extract_ville(adresse.strip())
            st.session_state.profile_draft = data
            st.session_state.profile_step = 3
            st.rerun()
        else:
            st.warning("Merci d'entrer votre ville ou l'adresse de votre agence !")
    return None


def _extract_ville(adresse: str) -> str:
    """Extrait la ville : dernier segment après la virgule, sinon l'adresse entière."""
    if "," in adresse:
        return adresse.split(",")[-1].strip()
    return adresse.strip()


def _ask_specialites(data: dict) -> None:
    prenom = data.get("prenom", "")
    ville = data.get("ville_travail", "")
    ville_txt = f" à {ville}" if ville else ""
    show_formateur_message(
        f"Super{ville_txt} ! Vous faites plutôt de la vente, de la location, ou les deux ?",
        key="onb_q3", mood="neutral",
    )

    spec_options = list(SPECIALITES_LABELS.values())
    current_specs = data.get("specialites", [])
    default_specs = [SPECIALITES_LABELS[s] for s in current_specs if s in SPECIALITES_LABELS]

    selected = st.multiselect("Vos spécialités", spec_options, default=default_specs, key="onb_specialites")

    if st.button("Continuer", key="btn_onb_3"):
        spec_keys = [SPECIALITES[spec_options.index(s)] for s in selected] if selected else ["vendeur"]
        data["specialites"] = spec_keys[:3]
        st.session_state.profile_draft = data
        st.session_state.profile_step = 4
        st.rerun()
    return None


def _ask_objectif(data: dict) -> None:
    prenom = data.get("prenom", "")
    show_formateur_message(
        f"Bien {prenom} ! Qu'est-ce que vous souhaitez améliorer en priorité dans votre métier ?",
        key="onb_q4", mood="thinking",
    )

    objectif = st.text_area(
        "Votre objectif principal",
        key="onb_objectif",
        placeholder="Ex : Améliorer ma prospection, conclure plus de mandats, mieux gérer les objections...",
        value=data.get("objectif_principal", ""),
        height=80,
    )

    if st.button("Continuer", key="btn_onb_4"):
        if objectif.strip():
            data["objectif_principal"] = objectif.strip()
            st.session_state.profile_draft = data
            st.session_state.profile_step = 5
            st.rerun()
        else:
            st.warning("Merci de partager votre objectif principal !")
    return None


def _ask_points_faibles(data: dict) -> None:
    prenom = data.get("prenom", "")
    show_formateur_message(
        f"Dernière question {prenom} : sur quoi rencontrez-vous le plus de difficultés actuellement ? (Soyez honnête, c'est pour vous aider !)",
        key="onb_q5", mood="encouraging",
    )

    current_faibles = data.get("points_faibles", [])
    default_faibles = [f for f in current_faibles if f in _POINTS_FAIBLES_OPTIONS]

    selected = st.multiselect(
        "Vos points à améliorer (max 3)",
        _POINTS_FAIBLES_OPTIONS,
        default=default_faibles,
        key="onb_faibles",
    )
    if len(selected) > 3:
        st.warning("3 points maximum. Les 3 premiers seront retenus.")

    if st.button("Terminer l'onboarding", key="btn_onb_5", type="primary"):
        data["points_faibles"] = selected[:3]
        st.session_state.profile_draft = data
        st.session_state.profile_step = 6
        st.rerun()
    return None


def _render_past_exchange(step_num: int, data: dict) -> None:
    """Affiche un échange passé (question + réponse validée)."""
    exchanges = [
        ("Comment vous appelez-vous ?", data.get("prenom", "")),
        (
            "Votre niveau en immobilier ?",
            next((label for label, k in _NIVEAU_RADIO_OPTIONS if k == data.get("niveau", "")), data.get("niveau", "")),
        ),
        ("Ville ou adresse de votre agence ?", data.get("adresse_travail", "")),
        (
            "Vos spécialités ?",
            ", ".join(SPECIALITES_LABELS.get(s, s) for s in data.get("specialites", [])),
        ),
        ("Votre objectif principal ?", data.get("objectif_principal", "")),
        ("Vos points à améliorer ?", ", ".join(data.get("points_faibles", []))),
    ]
    if step_num < len(exchanges):
        question, reponse = exchanges[step_num]
        if reponse:
            st.markdown(f"**Formateur** : {question}")
            st.markdown(f"**Vous** : {reponse}")
            st.markdown("---")


def _finalize(data: dict) -> Optional[UserProfile]:
    """Construit le UserProfile final et affiche le message de bienvenue.

    Retourne le profil uniquement quand l'utilisateur clique sur
    "Démarrer la formation", None tant qu'il n'a pas cliqué.
    """
    profile = UserProfile(
        prenom=data.get("prenom", ""),
        niveau=data.get("niveau", "debutant"),
        role=data.get("role", "conseiller_vente"),
        specialites=data.get("specialites", ["vendeur"]),
        objectif_principal=data.get("objectif_principal", ""),
        points_faibles=data.get("points_faibles", []),
        format_prefere=data.get("format_prefere", "cas_pratique"),
        adresse_travail=data.get("adresse_travail", ""),
        ville_travail=data.get("ville_travail", ""),
    )

    st.markdown("---")
    st.markdown(f"### C'est parti {profile.prenom} !")

    tone = {
        "debutant": "Nous allons construire vos bases ensemble, pas à pas.",
        "confirme": "Nous allons consolider vos acquis et travailler vos points à améliorer.",
        "expert": "Nous allons vous challenger pour aller encore plus loin.",
    }
    st.write(tone.get(profile.niveau, tone["confirme"]))

    if profile.ville_travail:
        st.markdown(f"**Zone de travail** : {profile.ville_travail}")
    if profile.specialites:
        specs_txt = ", ".join(SPECIALITES_LABELS.get(s, s) for s in profile.specialites)
        st.markdown(f"**Spécialités** : {specs_txt}")
    if profile.objectif_principal:
        st.markdown(f"**Objectif** : {profile.objectif_principal}")
    if profile.points_faibles:
        st.markdown(f"**Axes de travail** : {', '.join(profile.points_faibles)}")

    if st.button("Démarrer la formation", key="btn_start_formation", type="primary"):
        _reset_profile()
        return profile
    return None
