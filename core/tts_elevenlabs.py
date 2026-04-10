"""core/tts_elevenlabs.py – TTS via ElevenLabs API.

Utilisé pour les moments à forte valeur (transitions, WhatsApp client).
Fallback sur OpenAI TTS si ElevenLabs échoue ou n'est pas configuré.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Optional

import requests

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
ELEVENLABS_VOICE_CLIENT_MALE = os.getenv("ELEVENLABS_VOICE_CLIENT_MALE", "")
ELEVENLABS_VOICE_CLIENT_FEMALE = os.getenv("ELEVENLABS_VOICE_CLIENT_FEMALE", "")
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# Cache partagé avec OpenAI TTS
CACHE_DIR = Path("data/tts_cache/elevenlabs")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def is_available() -> bool:
    """Vérifie si ElevenLabs est configuré."""
    return bool(ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID)


def _cache_key(text: str, voice_id: str) -> str:
    content = f"elevenlabs|{text}|{voice_id}"
    return hashlib.md5(content.encode("utf-8")).hexdigest() + ".mp3"


def tts_to_bytes(
    text: str,
    voice_id: Optional[str] = None,
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.4,
    use_cache: bool = True,
) -> Optional[bytes]:
    """Génère l'audio via ElevenLabs. Retourne bytes MP3 ou None si échec."""
    text = (text or "").strip()
    if not text:
        return None

    if not is_available():
        return None

    vid = voice_id or ELEVENLABS_VOICE_ID

    # Vérifier cache
    if use_cache:
        key = _cache_key(text, vid)
        cache_path = CACHE_DIR / key
        if cache_path.exists():
            try:
                return cache_path.read_bytes()
            except Exception:
                pass

    # Appel API
    url = f"{ELEVENLABS_API_URL}/{vid}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": True,
        },
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            audio_bytes = resp.content
            # Sauvegarder en cache
            if use_cache and audio_bytes:
                try:
                    key = _cache_key(text, vid)
                    (CACHE_DIR / key).write_bytes(audio_bytes)
                except Exception:
                    pass
            return audio_bytes
        else:
            print(f"[ElevenLabs] Erreur {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"[ElevenLabs] Erreur: {e}")
        return None


_FEMALE_MARKERS = [
    "mme", "madame", "sophie", "marie", "claire", "anne",
    "leroy", "martin", "julie", "sarah", "emma", "léa",
    "catherine", "isabelle", "nathalie",
]


def tts_client(
    text: str,
    persona_name: str = "",
    stability: float = 0.45,
    similarity_boost: float = 0.7,
    style: float = 0.5,
    use_cache: bool = True,
) -> Optional[bytes]:
    """TTS ElevenLabs pour les clients WhatsApp.

    Choisit automatiquement la voix homme/femme selon le persona.
    """
    if not ELEVENLABS_API_KEY:
        return None

    name_lower = persona_name.lower()
    is_female = any(w in name_lower for w in _FEMALE_MARKERS)

    voice_id = ELEVENLABS_VOICE_CLIENT_FEMALE if is_female else ELEVENLABS_VOICE_CLIENT_MALE

    if not voice_id:
        return None

    return tts_to_bytes(
        text,
        voice_id=voice_id,
        stability=stability,
        similarity_boost=similarity_boost,
        style=style,
        use_cache=use_cache,
    )
