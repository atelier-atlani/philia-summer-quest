"""core/avatar.py – Module avatar formateur.

Architecture évolutive :
  Phase 1 : Avatar Lottie animé (actuel)
  Phase 2 : Avatar parlant D-ID / HeyGen (futur)

Usage :
    from core.avatar import show_formateur_message
    show_formateur_message("Bravo !", key="step_1", mood="encouraging")
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import streamlit as st


# ---------------------------------------------------------------------------
# Animations Lottie — URLs publiques (remplacer par des URLs stables en prod)
# ---------------------------------------------------------------------------
_LOTTIE_URLS = {
    "neutral":     "https://lottie.host/4f8c9ea5-8d11-4b44-b64e-8dbdbe6eae7f/VQqyYGKGKw.json",
    "happy":       "https://lottie.host/3d0e4b3c-7e5f-4a3b-9e3c-8c8f8e8f8e8f/abc123.json",
    "thinking":    "https://lottie.host/9f8c9ea5-8d11-4b44-b64e-8dbdbe6eae7f/thinking.json",
    "encouraging": "https://lottie.host/5f8c9ea5-8d11-4b44-b64e-8dbdbe6eae7f/thumbsup.json",
}

_MOOD_EMOJI = {
    "neutral":     "👨‍🏫",
    "happy":       "😊",
    "thinking":    "🤔",
    "encouraging": "💪",
}


@st.cache_data(show_spinner=False)
def _fetch_lottie(url: str) -> Optional[dict]:
    """Télécharge et met en cache une animation Lottie."""
    try:
        import requests  # noqa: PLC0415
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Interface abstraite
# ---------------------------------------------------------------------------
class AvatarProvider(ABC):
    """Interface pour les providers d'avatar formateur."""

    @abstractmethod
    def render(self, message: str, key: str, mood: str = "neutral") -> None:
        """Affiche l'avatar accompagné d'un message."""


# ---------------------------------------------------------------------------
# Phase 1 : Lottie
# ---------------------------------------------------------------------------
class LottieAvatar(AvatarProvider):
    """Avatar animé via streamlit-lottie (Phase 1)."""

    def __init__(self) -> None:
        try:
            from streamlit_lottie import st_lottie  # noqa: PLC0415
            self._st_lottie = st_lottie
        except ImportError:
            self._st_lottie = None

    def render(self, message: str, key: str, mood: str = "neutral") -> None:
        emoji = _MOOD_EMOJI.get(mood, "👨‍🏫")

        # Sans bibliothèque → fallback simple
        if self._st_lottie is None:
            st.info(f"{emoji} **Formateur** : {message}")
            return

        animation = _fetch_lottie(_LOTTIE_URLS.get(mood, _LOTTIE_URLS["neutral"]))

        col_avatar, col_msg = st.columns([1, 3])
        with col_avatar:
            if animation:
                self._st_lottie(
                    animation,
                    height=150,
                    key=f"lottie_{key}",
                    speed=1,
                    loop=True,
                )
            else:
                st.markdown(
                    f'<div style="font-size:56px;text-align:center;margin-top:20px;">'
                    f'{emoji}</div>',
                    unsafe_allow_html=True,
                )

        with col_msg:
            st.markdown(
                f"""
<div style="
    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    color:white;padding:20px;border-radius:12px;margin-top:20px;
    box-shadow:0 4px 6px rgba(0,0,0,0.1);
">
    <strong>Ton formateur</strong><br><br>
    {message}
</div>""",
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Phase 2 : Avatar parlant (stub)
# ---------------------------------------------------------------------------
class TalkingAvatar(AvatarProvider):
    """Avatar parlant D-ID / HeyGen (Phase 2 — à implémenter)."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def render(self, message: str, key: str, mood: str = "neutral") -> None:
        # TODO : appel API D-ID / HeyGen
        st.info(f"🎬 [Avatar parlant à venir] {message}")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
def get_avatar_provider(provider_type: str = "lottie") -> AvatarProvider:
    """Retourne le provider d'avatar selon le type demandé."""
    if provider_type == "talking":
        api_key = st.secrets.get("avatar_api_key", "")
        return TalkingAvatar(api_key)
    return LottieAvatar()


def show_formateur_message(
    message: str,
    key: str,
    mood: str = "neutral",
    provider_type: str = "lottie",
) -> None:
    """Helper global : affiche un message formateur avec avatar."""
    get_avatar_provider(provider_type).render(message, key, mood)
