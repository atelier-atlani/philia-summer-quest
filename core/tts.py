# core/tts.py
"""
TTS (Text-to-Speech) centralisé via OpenAI API.
Utilisé par CLI (agent_formateur.py) et Streamlit (app.py).
Avec cache pour éviter regénération des mêmes textes.
"""
from __future__ import annotations

import os
import hashlib
from pathlib import Path
from typing import Literal

from openai import OpenAI

# --- Configuration ---
DEFAULT_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
DEFAULT_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")  # Plus naturel que cedar
DEFAULT_INSTRUCTIONS = "Parlez comme un formateur expérimenté qui s'adresse à un collègue. Ton naturel et détendu, comme une conversation entre professionnels. Rythme varié : accélérez sur les transitions, ralentissez sur les points importants. Respirez entre les phrases."

# Dossier de cache
CACHE_DIR = Path("data/tts_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

AudioFormat = Literal["mp3", "wav", "opus", "aac", "flac"]

# Voix disponibles OpenAI
AVAILABLE_VOICES = {
    "alloy": "Voix neutre, claire et naturelle (recommandé)",
    "nova": "Voix féminine chaleureuse",
    "shimmer": "Voix féminine douce",
    "echo": "Voix masculine posée",
    "onyx": "Voix masculine grave",
    "fable": "Voix narrative expressive",
}


def _get_cache_key(text: str, voice: str, model: str, response_format: str) -> str:
    """Génère une clé de cache unique basée sur le contenu."""
    content = f"{text}|{voice}|{model}|{response_format}"
    hash_hex = hashlib.md5(content.encode("utf-8")).hexdigest()
    return f"{hash_hex}.{response_format}"


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


def _clean_text_for_speech(text: str) -> str:
    """Nettoie le texte pour une lecture TTS naturelle."""
    if not text:
        return text

    import re

    # Retirer les numéros de sections (1), 2), 3), etc.)
    text = re.sub(r'^\s*\d+\)\s*', '', text, flags=re.MULTILINE)

    # Retirer les emojis
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)

    # Retirer les puces markdown (-, *, →)
    text = re.sub(r'^\s*[-*→]\s*', '', text, flags=re.MULTILINE)

    # Retirer les astérisques markdown (bold/italic)
    text = re.sub(r'\*\*?', '', text)

    # Retirer les backquotes
    text = re.sub(r'`', '', text)

    # Nettoyer espaces multiples
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def tts_to_bytes(
    client: OpenAI,
    text: str,
    *,
    model: str | None = None,
    voice: str | None = None,
    instructions: str | None = None,
    response_format: AudioFormat = "mp3",
    use_cache: bool = True,
) -> bytes | None:
    """
    Génère l'audio TTS et renvoie les bytes (avec cache).

    Args:
        client: Instance OpenAI initialisée
        text: Texte à synthétiser
        model: Modèle TTS (défaut: OPENAI_TTS_MODEL ou gpt-4o-mini-tts)
        voice: Voix (défaut: OPENAI_TTS_VOICE ou alloy)
        instructions: Instructions de style vocal
        response_format: Format audio (mp3, wav, opus, aac, flac)
        use_cache: Utiliser le cache si disponible

    Returns:
        bytes audio ou None si échec/texte vide
    """
    text = (text or "").strip()
    if not text:
        return None

    text = _clean_text_for_speech(text)

    model = model or DEFAULT_MODEL
    voice = voice or DEFAULT_VOICE

    # Vérifier le cache
    if use_cache:
        cache_key = _get_cache_key(text, voice, model, response_format)
        cache_path = CACHE_DIR / cache_key
        if cache_path.exists():
            try:
                return cache_path.read_bytes()
            except Exception:
                pass  # Fallback vers génération

    # Construction des kwargs
    kwargs = {
        "model": model,
        "voice": voice,
        "input": text,
        "response_format": response_format,
    }

    # Instructions
    if instructions is not None:
        if instructions:
            kwargs["instructions"] = instructions
    else:
        kwargs["instructions"] = DEFAULT_INSTRUCTIONS

    # Génération
    try:
        resp = client.audio.speech.create(**kwargs)
        audio_bytes = _extract_audio_bytes(resp)

        # Sauvegarder en cache
        if use_cache and audio_bytes:
            try:
                cache_key = _get_cache_key(text, voice, model, response_format)
                cache_path = CACHE_DIR / cache_key
                cache_path.write_bytes(audio_bytes)
            except Exception as e:
                print(f"[TTS] Cache write failed: {e}")

        return audio_bytes

    except Exception as e:
        print(f"[TTS] Generation failed: {e}")
        return None


def tts_smart(
    client: OpenAI,
    text: str,
    priority: str = "normal",
    voice: str | None = None,
    response_format: AudioFormat = "wav",
) -> bytes | None:
    """TTS intelligent : ElevenLabs pour les moments clés, OpenAI pour le reste.

    Args:
        client: Instance OpenAI (fallback)
        text: Texte à synthétiser
        priority: "high" = ElevenLabs (transitions, WhatsApp), "normal" = OpenAI
        voice: Override de voix OpenAI (ignoré si ElevenLabs utilisé)
        response_format: Format audio pour OpenAI

    Returns:
        bytes audio ou None
    """
    if priority == "high":
        try:
            from core.tts_elevenlabs import tts_to_bytes as el_tts, is_available
            if is_available():
                audio = el_tts(text)
                if audio:
                    return audio
        except Exception:
            pass

    # Fallback OpenAI
    return tts_to_bytes(
        client, text,
        voice=voice or DEFAULT_VOICE,
        response_format=response_format,
    )


def tts_client_smart(
    client: OpenAI,
    text: str,
    persona_name: str = "",
    response_format: AudioFormat = "wav",
) -> bytes | None:
    """TTS pour clients WhatsApp : ElevenLabs voix client, fallback OpenAI.

    Args:
        client: Instance OpenAI (fallback)
        text: Texte à synthétiser
        persona_name: Nom du persona pour détecter le genre (voix distinctes)
        response_format: Format audio pour le fallback OpenAI

    Returns:
        bytes audio ou None
    """
    try:
        from core.tts_elevenlabs import tts_client as el_client
        audio = el_client(text, persona_name=persona_name)
        if audio:
            return audio
    except Exception:
        pass

    # Fallback OpenAI — gender detection centralisée
    try:
        from core.tts_elevenlabs import _detect_female  # noqa: PLC0415
        is_female = _detect_female(persona_name)
    except Exception:
        name_lower = persona_name.lower()
        is_female = any(w in name_lower for w in ["mme", "madame", "sophie", "marie", "claire"])
    voice = "nova" if is_female else "onyx"
    return tts_to_bytes(
        client, text, voice=voice,
        instructions="Parlez comme un client au téléphone. Spontané et naturel.",
        response_format=response_format,
    )


def tts_to_file(
    client: OpenAI,
    text: str,
    *,
    model: str | None = None,
    voice: str | None = None,
    instructions: str | None = None,
    response_format: AudioFormat = "mp3",
    filepath: str | None = None,
    use_cache: bool = True,
) -> str | None:
    """
    Génère l'audio TTS et l'écrit dans un fichier.

    Args:
        client: Instance OpenAI initialisée
        text: Texte à synthétiser
        model, voice, instructions, response_format: voir tts_to_bytes()
        filepath: Chemin du fichier (si None, utilise le cache)
        use_cache: Utiliser le cache

    Returns:
        Chemin du fichier créé ou None si échec
    """
    audio = tts_to_bytes(
        client,
        text,
        model=model,
        voice=voice,
        instructions=instructions,
        response_format=response_format,
        use_cache=use_cache,
    )
    if not audio:
        return None

    # Si filepath fourni, écrire là
    if filepath is not None:
        try:
            with open(filepath, "wb") as f:
                f.write(audio)
            return filepath
        except Exception as e:
            print(f"[TTS] File write failed: {e}")
            return None

    # Sinon, retourner le chemin du cache
    cache_key = _get_cache_key(text, voice or DEFAULT_VOICE, model or DEFAULT_MODEL, response_format)
    cache_path = CACHE_DIR / cache_key
    return str(cache_path) if cache_path.exists() else None
