"""training/profile_ui.py – 3-step onboarding Streamlit UI.

Steps:
  1. Qui es-tu ? (prenom, niveau, role)
  2. Tes objectifs (specialites, objectif_principal, format_prefere)
  3. Tes axes de travail (points_faibles)
  + personalized welcome message
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st

from training.profile import (
    UserProfile,
    NIVEAUX,
    NIVEAUX_LABELS,
    ROLES,
    ROLES_LABELS,
    SPECIALITES,
    SPECIALITES_LABELS,
    FORMATS,
    FORMATS_LABELS,
)


def _init_profile_state() -> None:
    """Initialize onboarding state in st.session_state."""
    if "profile_step" not in st.session_state:
        st.session_state.profile_step = 1
    if "profile_draft" not in st.session_state:
        st.session_state.profile_draft = {}


def _reset_profile() -> None:
    """Reset onboarding state."""
    st.session_state.pop("profile_step", None)
    st.session_state.pop("profile_draft", None)


def render_profile_onboarding(existing_profile: Dict[str, Any]) -> Optional[UserProfile]:
    """Render 3-step onboarding form.

    Args:
        existing_profile: Previously saved profile dict (may be empty).

    Returns:
        UserProfile if onboarding is complete, None otherwise.
    """
    _init_profile_state()
    step = st.session_state.profile_step
    draft = st.session_state.profile_draft

    # Pre-fill from existing profile
    if not draft and existing_profile:
        draft.update(existing_profile)
        st.session_state.profile_draft = draft

    # Progress indicator
    st.markdown(f"**Étape {step}/3** de ton profil")
    st.progress(step / 3)

    if step == 1:
        return _step_1_identity(draft)
    elif step == 2:
        return _step_2_objectives(draft)
    elif step == 3:
        return _step_3_weaknesses(draft)
    else:
        # Onboarding complete
        return _finalize(draft)

    return None


def _step_1_identity(draft: Dict[str, Any]) -> Optional[UserProfile]:
    """Step 1: Qui es-tu ?"""
    st.markdown("### Qui es-tu ?")
    st.write("Faisons connaissance pour personnaliser ta formation.")

    prenom = st.text_input(
        "Ton prénom :",
        value=draft.get("prenom", ""),
        key="profile_prenom",
    )

    niveau_options = list(NIVEAUX_LABELS.values())
    current_niveau = draft.get("niveau", "debutant")
    niveau_idx = NIVEAUX.index(current_niveau) if current_niveau in NIVEAUX else 0
    niveau_label = st.radio(
        "Ton niveau en immobilier :",
        options=niveau_options,
        index=niveau_idx,
        key="profile_niveau",
    )
    niveau_key = NIVEAUX[niveau_options.index(niveau_label)]

    role_options = list(ROLES_LABELS.values())
    current_role = draft.get("role", "conseiller_vente")
    role_idx = ROLES.index(current_role) if current_role in ROLES else 0
    role_label = st.radio(
        "Ton rôle :",
        options=role_options,
        index=role_idx,
        key="profile_role",
    )
    role_key = ROLES[role_options.index(role_label)]

    if st.button("Suivant", key="profile_next_1"):
        if not prenom.strip():
            st.warning("Merci de saisir ton prénom.")
            return None
        draft["prenom"] = prenom.strip()
        draft["niveau"] = niveau_key
        draft["role"] = role_key
        st.session_state.profile_draft = draft
        st.session_state.profile_step = 2
        st.rerun()

    return None


def _step_2_objectives(draft: Dict[str, Any]) -> Optional[UserProfile]:
    """Step 2: Tes objectifs."""
    st.markdown("### Tes objectifs")
    st.write("Dis-nous ce que tu veux travailler en priorité.")

    # Specialites (multi-select)
    spec_options = list(SPECIALITES_LABELS.values())
    current_specs = draft.get("specialites", [])
    default_specs = [
        SPECIALITES_LABELS[s]
        for s in current_specs
        if s in SPECIALITES_LABELS
    ]
    selected_specs = st.multiselect(
        "Tes spécialités (choisis-en 1 à 3) :",
        options=spec_options,
        default=default_specs,
        key="profile_specialites",
    )

    objectif = st.text_area(
        "Ton objectif principal pour cette formation :",
        value=draft.get("objectif_principal", ""),
        placeholder="Ex : Améliorer ma prise de mandat exclusif",
        height=80,
        key="profile_objectif",
    )

    format_options = list(FORMATS_LABELS.values())
    current_format = draft.get("format_prefere", "cas_pratique")
    format_idx = FORMATS.index(current_format) if current_format in FORMATS else 2
    format_label = st.radio(
        "Format de formation préféré :",
        options=format_options,
        index=format_idx,
        key="profile_format",
    )
    format_key = FORMATS[format_options.index(format_label)]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Précédent", key="profile_prev_2"):
            st.session_state.profile_step = 1
            st.rerun()
    with col2:
        if st.button("Suivant", key="profile_next_2"):
            if len(selected_specs) == 0:
                st.warning("Choisis au moins une spécialité.")
                return None
            # Convert labels back to keys
            spec_keys = [
                SPECIALITES[spec_options.index(s)]
                for s in selected_specs
            ]
            draft["specialites"] = spec_keys[:3]
            draft["objectif_principal"] = objectif.strip()
            draft["format_prefere"] = format_key
            st.session_state.profile_draft = draft
            st.session_state.profile_step = 3
            st.rerun()

    return None


def _step_3_weaknesses(draft: Dict[str, Any]) -> Optional[UserProfile]:
    """Step 3: Tes axes de travail."""
    st.markdown("### Tes axes de travail")
    st.write("Identifie tes points faibles pour que la formation s'adapte.")

    # Points faibles (multi-select from specialites + common areas)
    weakness_options = [
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
    current_faibles = draft.get("points_faibles", [])
    default_faibles = [f for f in current_faibles if f in weakness_options]
    selected = st.multiselect(
        "Tes points faibles (max 3) :",
        options=weakness_options,
        default=default_faibles,
        key="profile_faibles",
    )

    if len(selected) > 3:
        st.warning("3 points faibles maximum. Les 3 premiers seront retenus.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Précédent", key="profile_prev_3"):
            st.session_state.profile_step = 2
            st.rerun()
    with col2:
        if st.button("Valider mon profil", key="profile_validate"):
            draft["points_faibles"] = selected[:3]
            st.session_state.profile_draft = draft
            st.session_state.profile_step = 4
            st.rerun()

    return None


def _finalize(draft: Dict[str, Any]) -> UserProfile:
    """Build UserProfile from draft and show welcome message."""
    profile = UserProfile.from_dict(draft)

    st.markdown("---")
    st.markdown(f"### Bienvenue {profile.prenom} !")

    tone = {
        "debutant": "On va construire tes bases ensemble, pas à pas.",
        "confirme": "On va consolider tes acquis et travailler tes points faibles.",
        "expert": "On va te challenger pour aller encore plus loin.",
    }
    st.write(tone.get(profile.niveau, tone["confirme"]))

    st.markdown(f"**Rôle** : {profile.role_label}")
    if profile.specialites:
        specs_txt = ", ".join(
            SPECIALITES_LABELS.get(s, s) for s in profile.specialites
        )
        st.markdown(f"**Spécialités** : {specs_txt}")
    if profile.objectif_principal:
        st.markdown(f"**Objectif** : {profile.objectif_principal}")
    if profile.points_faibles:
        st.markdown(f"**Axes de travail** : {', '.join(profile.points_faibles)}")
    st.markdown(f"**Format préféré** : {profile.format_label}")

    _reset_profile()
    return profile
