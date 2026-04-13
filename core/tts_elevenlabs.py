"""core/tts_elevenlabs.py – TTS via ElevenLabs API.

Utilisé pour les moments à forte valeur (transitions, WhatsApp client).
Fallback sur OpenAI TTS si ElevenLabs échoue ou n'est pas configuré.

Note : les variables d'environnement sont lues à l'appel (lazy), pas à l'import,
pour éviter les problèmes de timing avec load_dotenv().
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Optional

import requests

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# Cache partagé avec OpenAI TTS
CACHE_DIR = Path("data/tts_cache/elevenlabs")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# --- Lazy getters (lus au moment de l'appel, pas à l'import) ---

def _get_api_key() -> str:
    return os.getenv("ELEVENLABS_API_KEY", "")


def _get_voice_id() -> str:
    return os.getenv("ELEVENLABS_VOICE_ID", "")


def _get_voice_client_male() -> str:
    return os.getenv("ELEVENLABS_VOICE_CLIENT_MALE", "")


def _get_voice_client_female() -> str:
    return os.getenv("ELEVENLABS_VOICE_CLIENT_FEMALE", "")


def is_available() -> bool:
    """Vérifie si ElevenLabs est configuré."""
    return bool(_get_api_key() and _get_voice_id())


def _cache_key(text: str, voice_id: str) -> str:
    content = f"elevenlabs|{text}|{voice_id}"
    return hashlib.md5(content.encode("utf-8")).hexdigest() + ".mp3"


def _enhance_punctuation_for_tts(text: str) -> str:
    """Ajoute des pauses et du dynamisme pour ElevenLabs."""
    import re  # noqa: PLC0415
    text = re.sub(r'\. ([A-Z])', r'.\n\1', text)   # Pause après chaque phrase
    text = text.replace('?', '... ?')
    text = text.replace('!', '... !')
    text = text.replace('... ... ', '... ')
    text = text.replace('.\n\n', '.\n')
    return text.strip()


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
    text = _enhance_punctuation_for_tts(text)

    api_key = _get_api_key()
    default_voice = _get_voice_id()

    if not api_key or not default_voice:
        return None

    vid = voice_id or default_voice

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
        "xi-api-key": api_key,
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


# Titres féminins (priorité absolue, vérifiés en premier)
_FEMALE_TITLES = ["mme ", "madame ", "mme.", "mme\u00a0"]
_MALE_TITLES = ["m. ", "monsieur ", "mr. ", "mr "]

# Prénoms féminins courants (pas de noms de famille ambigus)
_FEMALE_FIRST_NAMES = [
    "sophie", "marie", "claire", "anne", "julie", "sarah",
    "emma", "léa", "lea", "catherine", "isabelle", "nathalie",
    "laura", "charlotte", "alice", "lucie", "camille", "céline",
    "celine", "valérie", "valerie", "sandrine",
]


def _detect_female(persona_name: str) -> bool:
    """Détecte si le persona est féminin.

    Ordre de priorité :
    1. Titre (Mme/Madame → féminin, M./Monsieur → masculin)
    2. Prénom connu féminin
    """
    name_lower = persona_name.lower()
    # 1. Titre — priorité absolue
    if any(name_lower.startswith(t) or f" {t}" in name_lower for t in _FEMALE_TITLES):
        return True
    if any(name_lower.startswith(t) or f" {t}" in name_lower for t in _MALE_TITLES):
        return False
    # 2. Prénom féminin
    return any(fn in name_lower for fn in _FEMALE_FIRST_NAMES)


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
    if not _get_api_key():
        return None

    is_female = _detect_female(persona_name)

    voice_id = _get_voice_client_female() if is_female else _get_voice_client_male()

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
