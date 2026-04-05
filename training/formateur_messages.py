"""training/formateur_messages.py – Messages formateur dans le parcours guidé.

Usage :
    from training.formateur_messages import message_formateur
    message_formateur("Voici le point clé du jour.", ts=ts)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from config.constants import AVATAR_CHAT_EMOJI

if TYPE_CHECKING:
    from training.engine import TrainingSession


def message_formateur(texte: str, ts: "TrainingSession | None" = None) -> None:
    """Affiche un message formateur dans le parcours guidé.

    Utilise un emoji mini (pas le grand PNG) pour rester compact dans la
    colonne centrale. Le grand PNG est réservé au chat libre (colonne droite).

    Args:
        texte: Message à afficher.
        ts: Session en cours (optionnel, pour personnaliser le nom).
    """
    with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
        st.markdown(texte)
