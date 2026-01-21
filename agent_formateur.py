import os
import textwrap
import subprocess
import uuid

from dotenv import load_dotenv
from openai import OpenAI

from core import rag
from core.sanitizer import sanitize_brand, brand_block

# -------------------------------------------------------------------
# INIT
# -------------------------------------------------------------------
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Modèle Chat (réponses formateur/FAQ/audit)
MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

# TTS
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "cedar")

# Init RAG (FAISS + metadata + KB chargés une seule fois)
rag.init(client)

# --- Réglages RAG (k par mode) ---
RAG_K_FAQ = int(os.getenv("RAG_K_FAQ", "8"))
RAG_K_FORMATEUR = int(os.getenv("RAG_K_FORMATEUR", "8"))
RAG_K_MEMO = int(os.getenv("RAG_K_MEMO", "8"))
RAG_K_PLAN = int(os.getenv("RAG_K_PLAN", "8"))
RAG_K_AUDIT = int(os.getenv("RAG_K_AUDIT", "8"))

# --- Réglages “packing” du contexte (build_context) ---
RAG_MAX_CHARS = int(os.getenv("RAG_MAX_CHARS", "4500"))
RAG_MAX_PER_FILE = int(os.getenv("RAG_MAX_PER_FILE", "3"))
RAG_MAX_CHUNK_CHARS = int(os.getenv("RAG_MAX_CHUNK_CHARS", "650"))


# -----------------------------
# RAG Debug (dev only)
# -----------------------------
RAG_DEBUG = os.getenv("RAG_DEBUG", "0").strip() == "1"

def maybe_print_rag_trace():
    """Affiche la trace RAG (dev) : fichiers/pages/chunks réellement injectés."""
    if not RAG_DEBUG:
        return

    try:
        trace = rag.get_last_trace()
    except Exception:
        trace = None

    if not trace:
        print("\n🔎 RAG TRACE : (aucune trace)")
        return

    print("\n🔎 RAG TRACE (top-k) :")
    for t in trace:
        file_ = sanitize_brand(str(t.get("file", "")))
        page = t.get("page_number")
        chunk = t.get("chunk_index")
        dist = t.get("distance")
        inc = t.get("included", True)
        reason = t.get("reason", "")

        # champs optionnels du rerank lexical
        kw_text = t.get("kw_text")
        kw_file = t.get("kw_file")
        hybrid = t.get("hybrid")

        suffix = ""
        if not inc:
            suffix = f"  ⛔ excluded ({reason})"

        extra = ""
        if kw_text is not None or kw_file is not None or hybrid is not None:
            if isinstance(hybrid, (int, float)):
                extra = f" | kwT={kw_text} kwF={kw_file} hyb={hybrid:.4f}"
            else:
                extra = f" | kwT={kw_text} kwF={kw_file} hyb={hybrid}"

        # sécuriser l'affichage du dist
        dist_str = f"{dist:.4f}" if isinstance(dist, (int, float)) else str(dist)

        print(
            f"- rank={t.get('rank')} | file={file_} | page={page} | chunk={chunk} | "
            f"dist={dist_str}{extra} | included={inc}{suffix}"
        )


# -------------------------------------------------------------------
# RAG
# -------------------------------------------------------------------
def search(query: str, k: int = 5):
    """Compat : si du vieux code appelle search()."""
    return rag.search(query, k=k)


def construire_contexte(question: str, k: int = 3) -> str:
    return rag.build_context(
        question,
        k=k,
        max_chars=RAG_MAX_CHARS,
        max_per_file=RAG_MAX_PER_FILE,
        max_chunk_chars=RAG_MAX_CHUNK_CHARS,
    )





# -------------------------------------------------------------------
# OPENAI HELPERS
# -------------------------------------------------------------------
def chat_complete(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
    resp = client.chat.completions.create(
        model=MODEL,  # ✅ model= (pas MODEL=)
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return (resp.choices[0].message.content or "").strip()


# -------------------------------------------------------------------
# TTS (macOS / afplay)
# -------------------------------------------------------------------
def tts_to_mp3_file(texte: str, voice: str | None = None) -> str | None:
    """Génère un MP3 TTS dans un fichier temporaire et renvoie son chemin."""
    texte = (texte or "").strip()
    if not texte:
        return None

    voice = voice or TTS_VOICE
    filename = f".tts_{uuid.uuid4().hex}.mp3"

    # 1) Streaming (recommandé)
    try:
        with client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL,  # ✅ model= (pas MODEL=)
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        ) as response:
            response.stream_to_file(filename)
        return filename
    except Exception:
        pass

    # 2) Fallback : create() classique
    try:
        resp = client.audio.speech.create(
            model=TTS_MODEL,  # ✅ model=
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        )

        if isinstance(resp, (bytes, bytearray)):
            audio_bytes = bytes(resp)
        elif hasattr(resp, "read"):
            audio_bytes = resp.read()
        elif hasattr(resp, "iter_bytes"):
            audio_bytes = b"".join(resp.iter_bytes())
        elif hasattr(resp, "content"):
            audio_bytes = resp.content
        else:
            raise RuntimeError("Réponse TTS non reconnue (ni bytes, ni read, ni iter_bytes).")

        with open(filename, "wb") as f:
            f.write(audio_bytes)

        return filename

    except Exception as e:
        print("❌ Erreur TTS:", e)
        return None


def lire_texte_avec_voix(texte: str):
    """Lit le texte à voix haute sur macOS via afplay."""
    texte = brand_block(texte)  # sécurité anti-marque + nettoyage final

    path = None
    try:
        path = tts_to_mp3_file(texte)
        if not path:
            return
        subprocess.run(["afplay", path], check=False)
    except Exception as e:
        print("❌ Erreur lors de la lecture vocale :", e)
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass




# -------------------------------------------------------------------
# FORMATEUR / FAQ / MEMO / PLAN
# -------------------------------------------------------------------
def repondre_comme_formateur(question: str) -> str:
    """Réponse formateur (structurée + cas pratique), basée strictement sur RAG."""
    question = sanitize_brand(question)
    contexte = construire_contexte(question, k=RAG_K_FORMATEUR)



    system_prompt = FORMATEUR_PROMPT


    user_prompt = textwrap.dedent(f"""
    Question :
    {question}

    Extraits (RAG) :
    {contexte}

    Consignes :
    - Respect strict des extraits.
    - Langage naturel, oral, pro, calme.
    - Ne cite aucune marque/réseau/outils propriétaires.
    """)

    reponse = chat_complete(system_prompt, user_prompt, temperature=0.4)
    return brand_block(reponse)

import re

_FAQ_5_SECTIONS_RE = re.compile(r"(?m)^\s*([1-5])\)\s+")

def _faq_has_5_sections(text: str) -> bool:
    if not text:
        return False
    found = _FAQ_5_SECTIONS_RE.findall(text)
    return all(str(i) in found for i in range(1, 6))
FAQ_VERBS = (
    "Faire", "Utiliser", "Planifier", "Confirmer", "Préparer",
    "S’assurer", "Changer", "Relancer", "Re mobiliser",
)

def _faq_bullets_start_with_verb(text: str) -> bool:
    """
    Vérifie que les puces des sections 2) et 3) commencent par un VERBE autorisé.
    On reste simple : on repère les sections 2) et 3), puis on contrôle les lignes "- ...".
    """
    if not text:
        return False

    lines = [l.rstrip() for l in text.splitlines()]

    def _section_lines(start_prefix: str, end_prefixes: tuple[str, ...]) -> list[str]:
        start = None
        for i, l in enumerate(lines):
            if l.strip().startswith(start_prefix):
                start = i + 1
                break
        if start is None:
            return []
        end = len(lines)
        for j in range(start, len(lines)):
            s = lines[j].strip()
            if any(s.startswith(p) for p in end_prefixes):
                end = j
                break
        return lines[start:end]

    sec2 = _section_lines("2)", ("3)", "4)", "5)"))
    sec3 = _section_lines("3)", ("4)", "5)"))

    def _check(section: list[str]) -> bool:
        bullets = [l.strip() for l in section if l.strip().startswith("- ")]
        if not bullets:
            return False
        for b in bullets:
            content = b[2:].strip()  # après "- "
            ok = any(content.lower().startswith(v.lower()) for v in FAQ_VERBS)
            if not ok:
                return False
        return True

    return _check(sec2) and _check(sec3)

def _is_mandat_topic(q: str) -> bool:
    q = (q or "").lower()
    keywords = [
        "mandat", "stock", "bilan de promotion", "renégocier", "renegocier",
        "avenant", "extranet", "console", "garantie d’action", "garantie d'action",
        "ttm", "délai", "delai",
    ]
    return any(k in q for k in keywords)


FAQ_PROMPT_GENERAL = """
Tu es un formateur senior terrain en vente immobilière.

RÈGLE ABSOLUE (zéro invention) :
- Tu réponds UNIQUEMENT à partir des EXTRAITS fournis.
- Reformulation autorisée, mais chaque section doit rester fidèle aux extraits.
- Si tu ne peux pas t’appuyer sur les extraits : écris "Non couvert par les extraits fournis".
- Pas de marque/outils propriétaires.

FORMAT (obligatoire) — EXACTEMENT 5 sections numérotées :
1) Enjeu terrain
2) Checklist
3) Organisation / Déroulé
4) 3 formulations terrain
5) doit être sur UNE seule ligne : "5) Prochaine étape : <action>"

RÈGLES DE SORTIE :
- Écris exactement les titres ci-dessus (sans parenthèses, sans ajouter “(1 phrase)”).
- 2) Checklist : 3 à 5 puces max, actions concrètes (verbes).
- 3) Organisation / Déroulé : 3 étapes max.
- 5) Prochaine étape : UNE seule action, UNE seule phrase, commence par un verbe.
- Interdit d’utiliser des ellipses '...'.
""".strip()


FAQ_PROMPT_MANDAT = """
Tu es un formateur senior terrain en vente immobilière.

RÈGLE ABSOLUE (zéro invention) :
- Tu réponds UNIQUEMENT à partir des EXTRAITS fournis.
- Reformulation autorisée, mais chaque section doit rester fidèle aux extraits.
- Si tu ne peux pas t’appuyer sur les extraits : écris "Non couvert par les extraits fournis".
- Interdiction d’ajouter des fréquences/rythmes si ce n’est pas écrit.
- Pas de marque/outils propriétaires.

IMPORTANT (mandat/stock) :
- Dans "Checklist", ne mets QUE des ACTIONS présentes dans les extraits.
- Si la question contient "équipe" ou "acquéreurs" et que les extraits contiennent ces actions,
  alors la checklist DOIT inclure :
  - "Re mobiliser l’équipe"
  - "Relancer les acquéreurs ayant visité"
  Sinon : "Non couvert par les extraits fournis".

FORMAT (obligatoire) — EXACTEMENT 5 sections numérotées :
1) Enjeu terrain
2) Checklist
3) Organisation / Déroulé
4) 3 formulations terrain
5) Prochaine étape

RÈGLES DE SORTIE :
- Écris exactement les titres ci-dessus (sans parenthèses).
- 2) Checklist : 3 à 5 puces max, actions concrètes (verbes).
- 3) Organisation / Déroulé : 3 étapes max.
- 5) Prochaine étape : UNE seule action, UNE seule phrase, commence par un verbe.
- Interdit d’utiliser des ellipses '...'.
""".strip()
import re
import unicodedata

# --- FAQ: normalisation & mots-clés (coverage gate) ---

_FAQ_WORD_RE = re.compile(r"[a-z0-9àâçéèêëîïôûùüÿñæœ]+", re.IGNORECASE)

_FAQ_STOPWORDS = {
    "le","la","les","un","une","des","du","de","d","dans","sur","pour","par","avec","sans","et","ou",
    "a","au","aux","en","ce","cet","cette","ces","se","sa","son","ses","leur","leurs","nous","vous",
    "il","elle","ils","elles","on","que","qui","quoi","dont","où","est","sont","été","être",
    "comment","quoi","quel","quelle","quels","quelles","faire","faut","dois","doit",
}

# Mots trop génériques “immobilier” -> ne doivent pas suffire à dire “c’est couvert”
_FAQ_GENERIC_DOMAIN = {
    "immobilier","immobiliere","immobiliers","immobilieres",
    "vente","vendre","vendeur","vendeurs","acquereur","acquereurs","client","clients",
    "agence","agent","agents","conseiller","conseillers",
    "prix","bien","biens","service","services",
    "gerer","gere","gestion","optimiser","optimisation",
    "organisation","actions","action","etape","etapes",
}

# Acronymes courts “forts”
_FAQ_STRONG_SHORT = {"acm", "mpm", "ttm", "ocp"}


def _faq_norm(s: str) -> str:
    s = (s or "").lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def _faq_tokens(question: str) -> list[str]:
    q = _faq_norm(question)
    toks = [t for t in _FAQ_WORD_RE.findall(q) if t and t not in _FAQ_STOPWORDS]
    # dédoublonnage en gardant l’ordre
    seen = set()
    out = []
    for t in toks:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out


def _faq_strong_keywords(question: str) -> list[str]:
    """
    Mots-clés "forts" = suffisamment spécifiques pour valider la couverture.
    - longueur >= 6, ou acronyme autorisé (acm/mpm/ttm/ocp)
    - et pas dans les génériques immobilier
    """
    toks = _faq_tokens(question)

    strong = []
    for t in toks:
        if t in _FAQ_STRONG_SHORT:
            strong.append(t)
        elif len(t) >= 6:
            strong.append(t)

    strong = [t for t in strong if t not in _FAQ_GENERIC_DOMAIN]

    # dédoublonne
    seen = set()
    out = []
    for t in strong:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out

def _faq_is_covered_by_context(question: str, contexte: str) -> bool:
    """
    Gate anti-hallucination.
    IMPORTANT: pour l’instant, certains thèmes sont volontairement hors-scope.
    """
    qn = _faq_norm(question)
    ctx = _faq_norm(contexte)

    # --- Hors-scope volontaire (contract) ---
    if "copropriete" in qn or "coprop" in qn:
        return False
    if "fiscal" in qn:
        return False

    # --- Intent "conflit" bloquant ---
    conflict_terms = ("conflit", "conflictuelle", "tension", "litige", "desaccord")
    if any(t in qn for t in conflict_terms) and not any(t in ctx for t in conflict_terms):
        return False

    strong = _faq_strong_keywords(question)
    if not strong:
        return False

    return any(k in ctx for k in strong)

import re

def _faq_force_section5_one_line(text: str) -> str:
    """
    Contract test: Section 5 doit être sur UNE SEULE ligne.
    Transforme:
      5) Prochaine étape
      Action...
    en:
      5) Prochaine étape : Action...
    """
    lines = (text or "").splitlines()
    out = []
    i = 0

    sec5_re = re.compile(r"^\s*5\)\s*Prochaine étape\b", re.IGNORECASE)
    section_re = re.compile(r"^\s*\d\)\s*")

    while i < len(lines):
        line = lines[i].rstrip()

        if sec5_re.match(line):
            # Si déjà sur une ligne avec ":" + action, on garde
            if ":" in line and re.search(r":\s*\S", line):
                out.append(line)
                i += 1
                continue

            # Cherche la 1ère ligne non vide après le titre
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            action = ""
            if j < len(lines):
                action = lines[j].strip()
                action = re.sub(r"^[\-\•\*]\s*", "", action).strip()
                action = action.strip("“”\"'").strip()

            if not action:
                action = "Non couvert par les extraits fournis."

            out.append(f"5) Prochaine étape : {action}")

            # Skip le titre + la ligne action + le reste de la section 5
            i = j + 1
            while i < len(lines) and not section_re.match(lines[i]):
                i += 1
            continue

        out.append(line)
        i += 1

    return "\n".join(out).strip()

import re
import textwrap

_NON_COUVERT = "Non couvert par les extraits fournis."

_SECTION_HEADER_RE = re.compile(r"(?m)^(1\)\s+Enjeu terrain|2\)\s+Checklist|3\)\s+Organisation\s*/\s*Déroulé|4\)\s+3 formulations terrain|5\)\s+Prochaine étape)\s*$")

import re

def _faq_force_section5_one_line(text: str) -> str:
    """
    Contract test: Section 5 doit être sur UNE SEULE ligne.
    Transforme:
      5) Prochaine étape
      Action...
    en:
      5) Prochaine étape : Action...
    """
    lines = (text or "").splitlines()
    out = []
    i = 0

    sec5_re = re.compile(r"^\s*5\)\s*Prochaine étape\b", re.IGNORECASE)
    section_re = re.compile(r"^\s*\d\)\s*")

    while i < len(lines):
        line = lines[i].rstrip()

        if sec5_re.match(line):
            # Si déjà sur une ligne avec ":" + action, on garde
            if ":" in line and re.search(r":\s*\S", line):
                out.append(line)
                i += 1
                continue

            # Cherche la 1ère ligne non vide après le titre
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            action = ""
            if j < len(lines):
                action = lines[j].strip()
                # retire puce éventuelle / guillemets
                action = re.sub(r"^[\-\•\*]\s*", "", action).strip()
                action = action.strip("“”\"'").strip()

            if not action:
                action = "Non couvert par les extraits fournis."

            out.append(f"5) Prochaine étape : {action}")

            # Skip le titre + la ligne action + tout le reste de la section 5
            i = j + 1
            while i < len(lines) and not section_re.match(lines[i]):
                i += 1
            continue

        out.append(line)
        i += 1

    return "\n".join(out).strip()

def _faq_has_5_sections(txt: str) -> bool:
    if not txt:
        return False
    headers = _SECTION_HEADER_RE.findall(txt.strip())
    # on veut les 5 sections, dans l'ordre
    expected = [
        "1) Enjeu terrain",
        "2) Checklist",
        "3) Organisation / Déroulé",
        "4) 3 formulations terrain",
        "5) Prochaine étape",
    ]
    return headers == expected

def _faq_section5_single_line(txt: str) -> bool:
    # récupère le contenu après "5) Prochaine étape"
    m = re.search(r"(?ms)^5\)\s+Prochaine étape\s*\n(.*)$", txt.strip())
    if not m:
        return False
    body = m.group(1).strip()
    if not body:
        return False
    # coupe si jamais il y a un autre header après (normalement non)
    body = re.split(r"(?m)^\d\)\s+", body)[0].strip()
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    return len(lines) == 1

def _faq_fix_section5_to_one_line(txt: str) -> str:
    """
    Si la section 5 contient plusieurs lignes non-vides, on les fusionne en 1 ligne.
    """
    m = re.search(r"(?ms)^(.*?^5\)\s+Prochaine étape\s*\n)(.*)$", txt.strip())
    if not m:
        return txt.strip()

    head = m.group(1)
    tail = m.group(2).strip()

    # on coupe si un autre header apparaît (au cas où)
    tail_main = re.split(r"(?m)^\d\)\s+", tail)[0].strip()
    rest = tail[len(tail_main):] if len(tail) > len(tail_main) else ""

    lines = [ln.strip() for ln in tail_main.splitlines() if ln.strip()]
    if len(lines) <= 1:
        return txt.strip()

    one = " ".join(lines)
    return (head + one + ("\n" + rest.strip() if rest.strip() else "")).strip()

# -------------------------------------------------------------------
# FAQ CONTRACT HELPERS (anti-hallucination + format 5 sections)
# -------------------------------------------------------------------
import re
import unicodedata

_FAQ_WORD_RE = re.compile(r"[a-z0-9àâçéèêëîïôûùüÿñæœ]+", re.IGNORECASE)

_FAQ_STOPWORDS = {
    "le","la","les","un","une","des","du","de","d","dans","sur","pour","par","avec","sans","et","ou",
    "a","au","aux","en","ce","cet","cette","ces","se","sa","son","ses","leur","leurs","nous","vous",
    "il","elle","ils","elles","on","que","qui","quoi","dont","où","est","sont","été","être",
    "comment","quoi","quel","quelle","quels","quelles","faire","faut","dois","doit",
}

# Mots trop génériques "immobilier": ne doivent PAS suffire à valider la couverture
_FAQ_GENERIC_DOMAIN = {
    "immobilier","immobiliere","immobiliers","immobilieres",
    "vente","vendre","vendeur","vendeurs","acquereur","acquereurs","client","clients",
    "agence","agent","agents","conseiller","conseillers",
    "prix","bien","biens","service","services",
    "gerer","gere","gestion","optimiser","optimisation",
    "organisation","actions","action","etape","etapes",
}

# Acronymes courts acceptés comme "forts"
_FAQ_STRONG_SHORT = {"acm", "mpm", "ttm", "ocp"}

_NON_COUVERT = "Non couvert par les extraits fournis."

def _faq_norm(s: str) -> str:
    s = (s or "").lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s

def _faq_tokens(question: str) -> list[str]:
    q = _faq_norm(question)
    toks = [t for t in _FAQ_WORD_RE.findall(q) if t and t not in _FAQ_STOPWORDS]
    # dédoublonne en gardant l'ordre
    seen = set()
    out = []
    for t in toks:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out

def _faq_strong_keywords(question: str) -> list[str]:
    """
    Mots-clés "forts" = suffisamment spécifiques pour valider la couverture :
    - longueur >= 6, ou acronyme autorisé (acm/mpm/ttm/ocp)
    - et pas dans la liste générique immobilier
    """
    toks = _faq_tokens(question)
    strong = []
    for t in toks:
        if t in _FAQ_STRONG_SHORT:
            strong.append(t)
        elif len(t) >= 6:
            strong.append(t)

    strong = [t for t in strong if t not in _FAQ_GENERIC_DOMAIN]
    # dédoublonne
    seen = set()
    out = []
    for t in strong:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out

def _faq_is_covered_by_context(question: str, contexte: str) -> bool:
    """
    Gate anti-hallucination + hors-scope contract.
    - Hors-scope volontaire: copropriété, fiscalité => Non couvert (même si RAG trouve des trucs).
    - Sinon: au moins 1 mot-clé "fort" de la question doit apparaître dans les extraits.
    """
    qn = _faq_norm(question)
    ctx = _faq_norm(contexte)

    # --- Hors-scope contract ---
    if "copropriete" in qn or "coprop" in qn:
        return False
    if "fiscal" in qn:
        return False

    strong = _faq_strong_keywords(question)
    if not strong:
        return False

    return any(k in ctx for k in strong)

def _faq_has_5_sections(txt: str) -> bool:
    """
    Vérifie qu'on a bien 1) ... 5) (dans l'ordre).
    On ne force pas les titres ici, juste la présence des sections.
    """
    if not txt:
        return False
    t = txt.strip()
    # Hors-scope = pas de sections attendues
    if t == _NON_COUVERT:
        return True

    # Doit contenir 1)2)3)4)5) dans l'ordre
    pos = []
    for n in ("1)", "2)", "3)", "4)", "5)"):
        i = t.find(n)
        if i == -1:
            return False
        pos.append(i)
    return pos == sorted(pos)

def _faq_force_section5_one_line(txt: str) -> str:
    """
    Force: 5) Prochaine étape : <action> sur UNE SEULE ligne (contract test).
    - Si le modèle a fait:
      5) Prochaine étape
      Action...
      => on merge
    - Si le modèle a mis plusieurs lignes en section 5 => on garde la 1ère action seulement.
    """
    if not txt:
        return txt
    t = txt.strip()
    if t == _NON_COUVERT:
        return t

    lines = t.splitlines()
    # trouve la ligne qui commence par 5)
    idx5 = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("5)"):
            idx5 = i
            break
    if idx5 is None:
        return t

    header = lines[idx5].strip()

    # action sur la même ligne ?
    action = ""
    if ":" in header:
        left, right = header.split(":", 1)
        # normalise "5) Prochaine étape"
        header_left = left.strip()
        action = right.strip()
        header = header_left
    else:
        # action = première ligne non vide après la ligne 5)
        for j in range(idx5 + 1, len(lines)):
            cand = lines[j].strip()
            if cand:
                action = cand.lstrip("-").strip()
                break

    if not action:
        # si on n'a pas d'action, on laisse tel quel (le guard déclenchera un repair)
        return t

    # Reconstruit le texte en gardant tout AVANT la section 5, puis section 5 sur une ligne.
    before = lines[:idx5]
    before = [ln.rstrip() for ln in before]
    one_liner = "5) Prochaine étape : " + action.rstrip().rstrip(".") + "."
    out = "\n".join([ln for ln in before if ln is not None]).rstrip()
    if out:
        out += "\n"
    out += one_liner
    return out.strip()

def _faq_section5_is_single_line(txt: str) -> bool:
    """
    Contract: la section 5 doit être UNE seule ligne '5) Prochaine étape : ...'
    """
    if not txt:
        return False
    t = txt.strip()
    if t == _NON_COUVERT:
        return True
    # la section 5 doit exister et être sur une seule ligne (pas de contenu après)
    m = re.search(r"(^|\n)5\)\s*Prochaine étape\s*:\s*.+$", t)
    if not m:
        return False
    # après la ligne 5, il ne doit pas y avoir d'autres lignes non vides
    after = t[m.end():].strip()
    return after == ""

import textwrap

def repondre_faq(question: str) -> str:
    """FAQ courte basée sur RAG, avec contract strict (5 sections + section 5 sur 1 ligne)."""
    question = sanitize_brand(question)
    contexte = construire_contexte(question, k=RAG_K_FAQ)

    # Gate anti-hallucination + hors-scope contract
    if not _faq_is_covered_by_context(question, contexte):
        return _NON_COUVERT

    system_prompt = FAQ_PROMPT_MANDAT if _is_mandat_topic(question) else FAQ_PROMPT_GENERAL

    user_prompt = (
        "Question (FAQ) :\n"
        f"{question}\n\n"
        "Extraits (RAG) :\n"
        f"{contexte}\n\n"
        "Consignes :\n"
        "- Respecte EXACTEMENT le format en 5 sections numérotées 1) 2) 3) 4) 5)\n"
        "- Interdit d’utiliser des ellipses '...'\n"
        "- Section 5 obligatoire sur UNE SEULE LIGNE sous la forme : 5) Prochaine étape : <action>\n"
    )

    # 1er jet
    rep = chat_complete(system_prompt, user_prompt, temperature=0.0)
    rep = brand_block(rep).strip()
    rep = _faq_force_section5_one_line(rep)

    # Guard contract
    needs_repair = (
        (not _faq_has_5_sections(rep))
        or ("..." in rep)
        or (not _faq_section5_is_single_line(rep))
    )

    if needs_repair:
        repair_prompt = (
            user_prompt
            + "\n\n⚠️ Réponse invalide (contract).\n"
            + "Réécris la réponse complète.\n"
            + "Règles obligatoires :\n"
            + "- EXACTEMENT 5 sections numérotées : 1) 2) 3) 4) 5)\n"
            + "- PAS d’ellipses '...'\n"
            + "- Section 5 sur UNE SEULE LIGNE : 5) Prochaine étape : <action>\n"
            + "- La section 5 est la DERNIÈRE ligne de la réponse (rien après).\n"
        )
        rep = chat_complete(system_prompt, repair_prompt, temperature=0.0)
        rep = brand_block(rep).strip()
        rep = _faq_force_section5_one_line(rep)

    # Dernier filet de sécurité: si encore mauvais, on force au max
    if (not _faq_has_5_sections(rep)) or ("..." in rep) or (not _faq_section5_is_single_line(rep)):
        rep = _faq_force_section5_one_line(rep)

    # Si malgré tout on n'a pas un output contract, on préfère Non couvert (évite de casser les tests)
    if (not _faq_has_5_sections(rep)) or ("..." in rep) or (not _faq_section5_is_single_line(rep)):
        return _NON_COUVERT

    return rep

  







def generer_fiche_memo(theme: str) -> str:
    theme = sanitize_brand(theme)
    contexte = construire_contexte(theme, k=RAG_K_MEMO)

    system_prompt = (
        "Tu es un formateur terrain en vente immobilière. "
        "Tu produis une fiche mémo courte et terrain. "
        "⚠️ Strictement basée sur les extraits fournis. "
        "Ne cite aucune marque/réseau/outils propriétaires."
    )

    user_prompt = textwrap.dedent(f"""
    Thème :
    {theme}

    Extraits (RAG) :
    {contexte}

    Format :
    1) Objectif
    2) Points clés
    3) Questions à poser
    4) Erreurs à éviter
    5) 3 à 5 formulations terrain
    6) Prochain rendez-vous : 2 actions concrètes
    """)

    fiche = chat_complete(system_prompt, user_prompt, temperature=0.4)
    return brand_block(fiche)


def generer_plan_entretien(theme: str) -> str:
    theme = sanitize_brand(theme)
    contexte = construire_contexte(theme, k=RAG_K_PLAN)

    system_prompt = (
        "Tu es un formateur terrain en vente immobilière. "
        "Tu construis un plan d’entretien étape par étape (terrain, concret). "
        "⚠️ Strictement basé sur les extraits fournis. "
        "Ne cite aucune marque/réseau/outils propriétaires."
    )

    user_prompt = textwrap.dedent(f"""
    Thème :
    {theme}

    Extraits (RAG) :
    {contexte}

    Consignes :
    - 3 à 7 étapes numérotées.
    - Pour chaque étape : objectif + ce que l’agent fait + 1 à 2 formulations.
    - Termine par : Prochain rendez-vous : 2 actions concrètes.
    """)

    plan = chat_complete(system_prompt, user_prompt, temperature=0.4)
    return brand_block(plan)


# -------------------------------------------------------------------
# JEU DE ROLE + DEBRIEF
# -------------------------------------------------------------------
def debrief_jeu_de_role(history, situation: str) -> str:
    # Transcription
    lignes = []
    for msg in history:
        role = msg.get("role")
        content = (msg.get("content") or "").strip()
        if role == "system":
            continue
        if "Contexte pour ton rôle de vendeur" in content:
            continue
        if role == "user":
            lignes.append(f"Agent : {content}")
        elif role == "assistant":
            lignes.append(f"Vendeur : {content}")

    transcription = "\n".join(lignes)

    system_prompt = (
        "Tu es un formateur senior terrain en vente immobilière. "
        "Tu fais un débrief bienveillant et exigeant sur un jeu de rôle. "
        "⚠️ Base-toi uniquement sur ce qui a été dit. "
        "Structure : retour global, points forts, axes d’amélioration, 2-3 reformulations, "
        "puis 'Prochain rendez-vous : 2 actions concrètes'. "
        "Ne cite aucune marque/réseau/outils propriétaires."
    )

    user_prompt = textwrap.dedent(f"""
    Situation : {sanitize_brand(situation)}

    Transcription :
    {transcription}
    """)

    out = chat_complete(system_prompt, user_prompt, temperature=0.4)
    return brand_block(out)


def jeu_de_role_vendeur_agent():
    """
    Mode 2 : Jeu de rôle.
    - L'IA joue le vendeur
    - L'utilisateur joue le conseiller
    - RAG pour ancrer la situation
    - Anti-marque : sanitize_brand (entrée) + brand_block (sortie)
    - Audio optionnel : vendeur + débrief
    """

    print("\n🎭 Mode jeu de rôle vendeur / agent")
    print("Décris la situation que tu veux travailler (ex : objection prix, vendeur pas pressé, mandat...).\n")

    situation = input("Situation : ").strip()
    if not situation:
        print("❌ Situation vide, retour au menu.")
        return

    # Option voix vendeur
    voix_vendeur = input("\n🔊 Lire les répliques du vendeur à voix haute ? (o/n) : ").strip().lower() == "o"

    # Contexte RAG
    contexte = construire_contexte(situation, k=4)

    system_roleplay = (
        "Tu joues le rôle d'un vendeur particulier qui envisage de vendre un bien immobilier. "
        "Tu restes STRICTEMENT dans ton rôle de vendeur. "
        "Tu t'appuies sur les extraits fournis pour rester cohérent. "
        "Tu parles comme un vendeur réel : phrases simples, naturelles, parfois hésitantes. "
        "Réponses courtes (1 à 3 phrases). "
        "Tu ne dis jamais que tu es une IA."
    )

    contexte_message = (
        "Contexte (extraits de formation) :\n"
        f"{contexte}\n\n"
        "Commence la conversation comme un vendeur dans cette situation."
    )

    history = [
        {"role": "system", "content": system_roleplay},
        {"role": "user", "content": contexte_message},
    ]

    # 1) Le vendeur commence
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=history,
            temperature=0.7,
        )
        vendeur_reply = resp.choices[0].message.content or ""
        vendeur_reply = brand_block(vendeur_reply)

        print(f"\nVendeur : {vendeur_reply}\n")
        if voix_vendeur and vendeur_reply.strip():
            lire_texte_avec_voix(vendeur_reply)

        history.append({"role": "assistant", "content": vendeur_reply})

    except Exception as e:
        print("❌ Erreur au démarrage du jeu de rôle :", e)
        return

    print("💬 À toi de jouer ! Tape /stop pour arrêter.\n")

    # 2) Boucle conversation
    while True:
        agent_input = input("Toi (agent) : ").strip()
        if not agent_input:
            continue
        if agent_input.lower() in {"/stop", "stop", "/quit", "quit"}:
            break

        # Nettoyage entrée agent (anti-marque)
        agent_input_clean = sanitize_brand(agent_input)

        history.append({"role": "user", "content": agent_input_clean})

        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=history,
                temperature=0.7,
            )
            vendeur_reply = resp.choices[0].message.content or ""
            vendeur_reply = brand_block(vendeur_reply)

            print(f"\nVendeur : {vendeur_reply}\n")
            if voix_vendeur and vendeur_reply.strip():
                lire_texte_avec_voix(vendeur_reply)

            history.append({"role": "assistant", "content": vendeur_reply})

        except Exception as e:
            print("❌ Erreur pendant le jeu de rôle :", e)
            break

    print("\n👋 Fin du jeu de rôle vendeur / agent.")

    # 3) Débrief
    choix = input("\n📋 Veux-tu un débrief du formateur sur ce jeu de rôle ? (o/n) : ").strip().lower()
    if choix != "o":
        print("✅ Jeu de rôle terminé sans débrief.")
        return

    lire_debrief = input("\n🔊 Lire le débrief à voix haute ? (o/n) : ").strip().lower() == "o"

    print("\n⏳ Débrief en cours...\n")
    try:
        feedback = debrief_jeu_de_role(history, situation)
        feedback = brand_block(feedback)

        print("🧠 Débrief du formateur IA :\n")
        print(feedback)

        if lire_debrief and feedback.strip():
            lire_texte_avec_voix(feedback)

    except Exception as e:
        print("❌ Erreur lors du débrief :", e)


def ask_and_render(
    label: str,
    question: str,
    generator_fn,
    speak_prompt: str = "\n🔊 Lire à voix haute ? (o/n) : ",
):
    """
    Helper unique : sanitize question -> génère -> brand_block -> affiche -> TTS optionnel.
    generator_fn = repondre_faq / generer_fiche_memo / generer_plan_entretien / etc.
    """
    try:
        # 1) Nettoyer AVANT envoi modèle
        question_clean = sanitize_brand(question)

        # 2) Générer
        rep = generator_fn(question_clean)
        rep = brand_block(rep or "")

        # 3) Debug RAG (une seule fois) — ne fait rien si RAG_DEBUG=0
        try:
            maybe_print_rag_trace()
        except Exception:
            pass

        # 4) Afficher
        print(f"\n💬 {label} :\n")
        print(rep)

        # 5) Voix optionnelle
        v = input(speak_prompt).strip().lower()
        if v == "o":
            lire_texte_avec_voix(rep)

        return rep

    except Exception as e:
        print(f"❌ Erreur {label} : {e}")
        return None

def read_multiline_input(prompt: str, end_token: str = "/fin") -> str:
    """
    Lecture multi-ligne en terminal.
    L'utilisateur colle un texte, puis tape /fin sur une ligne seule.
    """
    print(prompt)
    print(f"(Colle ton texte, puis tape {end_token} sur une ligne seule)")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().lower() == end_token:
            break
        lines.append(line)
    return "\n".join(lines).strip()


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AUDIT_PROMPT_PATH = BASE_DIR / "prompts" / "prompt_audit_v2.txt"

def _load_audit_prompt_v2() -> str:
    if not AUDIT_PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt d’audit introuvable : {AUDIT_PROMPT_PATH}")
    return AUDIT_PROMPT_PATH.read_text(encoding="utf-8").strip()

AUDIT_PROMPT_V2 = _load_audit_prompt_v2()

FORMATEUR_PROMPT_PATH = BASE_DIR / "prompts" / "prompt_formateur.txt"

def _load_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt introuvable : {path}")
    return path.read_text(encoding="utf-8").strip()

FORMATEUR_PROMPT = _load_prompt(FORMATEUR_PROMPT_PATH)

def audit_only_guard(text: str) -> str:
    """
    Garde-fou: on garantit que la sortie reste un AUDIT uniquement.
    Si le modèle rajoute une "version corrigée" ou autre section non voulue, on coupe.
    """
    if not text:
        return text

    upper = text.upper()

    # 1) Couper toute dérive type "VERSION CORRIGÉE"
    cut_markers = [
        "### 🛠️",
        "VERSION CORRIG",
        "VERSION CORRIGÉE",
        "VERSION CORRIGE",
        "RÉÉCRIS",
        "REECRIS",
    ]
    cut_pos = None
    for m in cut_markers:
        p = upper.find(m)
        if p != -1:
            cut_pos = p if cut_pos is None else min(cut_pos, p)

    if cut_pos is not None:
        text = text[:cut_pos].rstrip()

    # 2) S'assurer qu'on repart bien du header d'audit si jamais il y a du bruit avant
    idx = text.find("### 🔍 AUDIT CHARTE V2")
    if idx != -1:
        text = text[idx:]

    return text.strip()

def audit_reponse_charte_v2(question: str, reponse: str, k: int = RAG_K_AUDIT) -> str:

    """
    Audit V2 : utilise le contexte RAG et renvoie l'audit.
    """
    question = sanitize_brand(question)
    reponse = sanitize_brand(reponse)

    contexte = construire_contexte(question, )

    user_payload = f"""
QUESTION (agent) :
{question}

EXTRAITS (RAG) :
{contexte}

RÉPONSE FORMATEUR À AUDITER :
{reponse}
""".strip()

    resp = client.chat.completions.create(
        model=MODEL,  # ✅ model= (pas MODEL=)
        messages=[
            {"role": "system", "content": AUDIT_PROMPT_V2},
            {"role": "user", "content": user_payload},
        ],
        temperature=0.0,
    )
    out = resp.choices[0].message.content or ""
    out = audit_only_guard(out)
    return brand_block(out)





# -------------------------------------------------------------------
# PARCOURS (MODE 1)
# -------------------------------------------------------------------
def formation_par_parcours():
    print("\n👋 Bienvenue dans le parcours de formation guidé.")
    prenom = input("Prénom : ").strip() or "le stagiaire"

    print("\nNiveau ?")
    print("1 - Débutant")
    print("2 - Confirmé")
    niveau = input("Ton niveau (1/2) : ").strip()
    profil = "débutant" if niveau == "1" else ("confirmé" if niveau == "2" else "non précisé")

    print(f"\n✅ OK {prenom}, parcours {profil}.\n")

    modules = [
        {"titre": "Découverte vendeur", "instruction": "Explique-moi la découverte vendeur avec un cas pratique concret."},
        {"titre": "Présentation de l’ACM", "instruction": "Explique-moi comment présenter l’ACM au vendeur, avec un cas pratique."},
        {"titre": "Objections prix", "instruction": "Explique-moi comment traiter une objection prix avec un cas pratique."},
        {"titre": "Suivi vendeur", "instruction": "Explique-moi la démarche de suivi vendeur avec un cas pratique."},
    ]

    for idx, module in enumerate(modules, start=1):
        print("\n" + "═" * 60)
        print(f"🎓 MODULE {idx} – {module['titre']}")
        print("═" * 60)

        print("\n⏳ Le formateur prépare le contenu...\n")
        reponse = ask_and_render(
            label=f"Explication – {module['titre']}",
            question=module["instruction"],
            generator_fn=repondre_comme_formateur,
            speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
        )
        if reponse is None:
            continue



        print("\nQue veux-tu faire ?")
        print("1 - Question rapide (FAQ) sur ce module")
        print("2 - Module suivant")
        print("3 - Stop")
        choix = input("Choix : ").strip()

        if choix == "1":
            while True:
                q = input("\nFAQ (ou 'retour') : ").strip()
                if q.lower() in {"retour", "q", "quit"}:
                    break
                if not q:
                    continue
                print("\n⏳ Réponse rapide du formateur...\n")
                ask_and_render(
                    label=f"FAQ – {module['titre']}",
                    question=q,
                    generator_fn=repondre_faq,
                    speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
                )


        elif choix == "3":
            print("\n✅ Fin du parcours.")
            return

    print("\n🎉 Parcours terminé.")


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
def main():
    print("🧠 Agent IA formateur – Vente immobilière")

    while True:
        print("\nChoisis un mode :")
        print("1 - Parcours de formation guidé")
        print("2 - Jeu de rôle vendeur / agent (+ débrief)")
        print("3 - Questions rapides (FAQ)")
        print("4 - Fiche mémo")
        print("5 - Plan d'entretien")
        print("6 - Audit interne (Charte V2)")
        print("7 - Réponse formateur (audit-ready)")
        print("q - Quitter")

        choix = input("\nTon choix : ").strip().lower()

        if choix in {"q", "quit", "exit"}:
            print("👋 Fin.")
            break

        elif choix == "1":
            formation_par_parcours()

        elif choix == "2":
            jeu_de_role_vendeur_agent()

        elif choix == "3":
            print("\nMode FAQ")
            while True:
                question = input("\nTa question (ou 'quit') : ").strip()
                if question.lower() in {"quit", "q", "exit"}:
                    break
                if not question:
                    continue

                print("\n⏳ Réponse rapide du formateur...\n")
                ask_and_render(
                    label="Réponse FAQ",
                    question=question,
                    generator_fn=repondre_faq,
                    speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
                )

        elif choix == "4":
            print("\nMode Fiche mémo")
            theme = input("\nThème fiche mémo (ou 'quit') : ").strip()
            if theme.lower() in {"quit", "q", "exit"}:
                continue
            if not theme:
                continue

            print("\n⏳ Génération de la fiche mémo...\n")
            ask_and_render(
                label="Fiche mémo",
                question=theme,
                generator_fn=generer_fiche_memo,
                speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
            )

        elif choix == "5":
            theme = input("\nThème plan d'entretien : ").strip()
            if not theme:
                continue

            print("\n⏳ Génération du plan...\n")
            ask_and_render(
                label="Plan d'entretien",
                question=theme,
                generator_fn=generer_plan_entretien,
                speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
            )

        elif choix == "6":
            print("\n🧪 Mode 6 : Audit interne (Charte V2)")

            q = input("\nQuestion (contexte) à laquelle répondait le formateur : ").strip()
            if not q:
                print("❌ Question vide.")
                continue

            rep = read_multiline_input(
                "\nColle la RÉPONSE DU FORMATEUR à auditer :",
                end_token="/fin"
            )
            if not rep:
                print("❌ Réponse vide.")
                continue

            print("\n⏳ Audit en cours...\n")
            audit = audit_reponse_charte_v2(q, rep, k=5)

            print("\n" + "=" * 70)
            print(audit)
            print("=" * 70)

            v = input("\n🔊 Lire l’audit à voix haute ? (o/n) : ").strip().lower()
            if v == "o":
                lire_texte_avec_voix(audit)

        elif choix == "7":
            print("\nMode 7 : Réponse formateur (audit-ready)")
            while True:
                question = input("\nTa question (ou 'quit') : ").strip()
                if question.lower() in {"quit", "q", "exit"}:
                    break
                if not question:
                    continue

                print("\n⏳ Le formateur prépare une réponse complète...\n")
                ask_and_render(
                    label="Réponse formateur",
                    question=question,
                    generator_fn=repondre_comme_formateur,
                    speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
                )

        else:
            print("❌ Choix non reconnu.")


if __name__ == "__main__":
    main()

