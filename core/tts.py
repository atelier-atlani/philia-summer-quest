# core/tts.py
"""
TTS (Text-to-Speech) centralisé via OpenAI API.
Utilisé par CLI (agent_formateur.py) et Streamlit (app.py).
"""
from __future__ import annotations

import os
import uuid
from typing import Literal

from openai import OpenAI

# --- Configuration par défaut (overridable) ---
DEFAULT_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
DEFAULT_VOICE = os.getenv("OPENAI_TTS_VOICE", "cedar")
DEFAULT_INSTRUCTIONS = "Voix chaleureuse, posée, légèrement grave. Rythme modéré."

AudioFormat = Literal["mp3", "wav", "opus", "aac", "flac"]


def _extract_audio_bytes(resp) -> bytes:
    """Extrait les bytes audio de la réponse OpenAI (compatible différentes versions SDK)."""
    if isinstance(resp, (bytes, bytearray)):
        return bytes(resp)

    if hasattr(resp, "read"):
        return resp.read()

    if hasattr(resp, "iter_bytes"):
        return b"".join(resp.iter_bytes())

    if hasattr(resp, "content") and isinstance(resp.content, (bytes, bytearray)):
        return bytes(resp.content)

    raise RuntimeError("Réponse TTS non reconnue (ni bytes, ni read, ni iter_bytes, ni content).")


def tts_generate(
    client: OpenAI,
    text: str,
    *,
    model: str | None = None,
    voice: str | None = None,
    instructions: str | None = None,
    response_format: AudioFormat = "mp3",
) -> bytes | None:
    """
    Génère l'audio TTS et renvoie les bytes.

    Args:
        client: Instance OpenAI initialisée
        text: Texte à synthétiser
        model: Modèle TTS (défaut: OPENAI_TTS_MODEL ou gpt-4o-mini-tts)
        voice: Voix (défaut: OPENAI_TTS_VOICE ou cedar)
        instructions: Instructions de style vocal (défaut: voix chaleureuse)
        response_format: Format audio (mp3, wav, opus, aac, flac)

    Returns:
        bytes audio ou None si échec/texte vide
    """
    text = (text or "").strip()
    if not text:
        return None

    model = model or DEFAULT_MODEL
    voice = voice or DEFAULT_VOICE
    instructions = instructions if instructions is not None else DEFAULT_INSTRUCTIONS

    # Construction des kwargs (instructions optionnel selon API)
    kwargs = {
        "model": model,
        "voice": voice,
        "input": text,
        "response_format": response_format,
    }
    if instructions:
        kwargs["instructions"] = instructions

    try:
        resp = client.audio.speech.create(**kwargs)
        return _extract_audio_bytes(resp)
    except Exception:
        return None


def tts_to_file(
    client: OpenAI,
    text: str,
    *,
    model: str | None = None,
    voice: str | None = None,
    instructions: str | None = None,
    response_format: AudioFormat = "mp3",
    filepath: str | None = None,
) -> str | None:
    """
    Génère l'audio TTS et l'écrit dans un fichier.

    Args:
        client: Instance OpenAI initialisée
        text: Texte à synthétiser
        model, voice, instructions, response_format: voir tts_generate()
        filepath: Chemin du fichier (défaut: .tts_<uuid>.<format>)

    Returns:
        Chemin du fichier créé ou None si échec
    """
    audio = tts_generate(
        client,
        text,
        model=model,
        voice=voice,
        instructions=instructions,
        response_format=response_format,
    )
    if not audio:
        return None

    if filepath is None:
        filepath = f".tts_{uuid.uuid4().hex}.{response_format}"

    try:
        with open(filepath, "wb") as f:
            f.write(audio)
        return filepath
    except Exception:
        return None
