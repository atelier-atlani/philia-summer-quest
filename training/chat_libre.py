"""training/chat_libre.py – Chat libre stagiaire sous avatar formateur.

Chat questions libres :
  - Grand avatar PNG à gauche
  - Historique scrollable
  - Input ancré en bas
  - Réponse via repondre_faq (RAG)
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

# Chemin avatar (priorité images/ puis avatars/)
_AVATAR_PNG = Path("assets/images/IAXEL-formateur.png")
_AVATAR_FALLBACK = Path("assets/avatars/IAXEL-formateur.png")
_AVATAR_CHAT_ICON = "🎓"  # icône mini dans les bulles de chat libre


def _get_avatar_path() -> str | None:
    if _AVATAR_PNG.exists():
        return str(_AVATAR_PNG)
    if _AVATAR_FALLBACK.exists():
        return str(_AVATAR_FALLBACK)
    return None


def _init_chat_libre_state() -> None:
    if "chat_libre_history" not in st.session_state:
        st.session_state.chat_libre_history = []


def render_chat_libre(avatar_name: str = "IAXEL") -> None:
    """Affiche le chat libre sous grand avatar.

    Args:
        avatar_name: Nom du formateur à afficher.
    """
    from agent_formateur import repondre_faq  # noqa: PLC0415 — évite import circulaire

    _init_chat_libre_state()
    history: list[dict] = st.session_state.chat_libre_history

    # --- Grand avatar ---
    avatar_path = _get_avatar_path()
    if avatar_path:
        st.image(avatar_path, width=300)
    else:
        st.markdown(
            '<div style="font-size:80px;text-align:center;">🎓</div>',
            unsafe_allow_html=True,
        )
    st.markdown(f"**{avatar_name}**")
    st.caption("🟢 En direct · Questions libres")

    st.markdown("---")
    st.markdown("### 💬 Questions libres")

    # --- Historique scrollable ---
    chat_container = st.container(height=300)
    with chat_container:
        for msg in history:
            role = msg["role"]
            avatar = avatar_path if role == "assistant" else None
            with st.chat_message(role, avatar=avatar):
                st.markdown(msg["text"])

    # --- Input ---
    user_q = st.chat_input("Votre question...", key="chat_libre_input")
    if user_q and user_q.strip():
        history.append({"role": "user", "text": user_q.strip()})
        with st.spinner(""):
            resp = repondre_faq(user_q.strip())
        history.append({"role": "assistant", "text": resp})
        st.session_state.chat_libre_history = history
        st.rerun()
