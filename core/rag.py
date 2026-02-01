import json
import numpy as np
import faiss
from functools import lru_cache
import os
from typing import List, Dict, Any
import re
import unicodedata
from collections import defaultdict

_last_trace: List[Dict[str, Any]] = []

def get_last_trace() -> List[Dict[str, Any]]:
    return list(_last_trace)

_client = None
_index = None
_meta = None
_kb = None

EMBEDDING_MODEL = "text-embedding-3-small"
KB_FILE = "base_connaissances.json"
INDEX_FILE = "faiss_index.bin"
META_FILE = "faiss_metadata.json"


def init(client,
         embedding_model: str = EMBEDDING_MODEL,
         kb_file: str = KB_FILE,
         index_file: str = INDEX_FILE,
         meta_file: str = META_FILE):
    global _client, _index, _meta, _kb, EMBEDDING_MODEL, KB_FILE, INDEX_FILE, META_FILE
    _client = client
    EMBEDDING_MODEL = embedding_model
    KB_FILE, INDEX_FILE, META_FILE = kb_file, index_file, meta_file

    _index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "r", encoding="utf-8") as f:
        _meta = json.load(f)
    with open(KB_FILE, "r", encoding="utf-8") as f:
        _kb = json.load(f)


@lru_cache(maxsize=1024)
def _embed_cached(key: str) -> np.ndarray:
    model, text = key.split("||", 1)
    resp = _client.embeddings.create(model=model, input=text)
    return np.array(resp.data[0].embedding, dtype="float32")


# --- RAG: Trace du dernier retrieval (pour debug) ---
#_LAST_TRACE: list[dict] = []

def _domain_file_boost(query: str, file_: str) -> float:
    """
    Petit bonus (réduction du score hybrid) si la requête concerne les mandats/stock
    et si le nom du fichier matche fortement.
    Valeurs faibles car index en L2 (plus petit = meilleur).
    """
    q = (query or "").lower()
    f = (file_ or "").lower()

    # on n’active le boost que si la requête parle "stock/mandat"
    if not any(w in q for w in ("mandat", "stock", "bilan", "promotion", "renégoc", "renegoc", "avenant", "suivi")):
        return 0.0

    bonus = 0.0
    if "mandat" in f:
        bonus += 0.05
    if "stock" in f:
        bonus += 0.08
    if "renégocier" in f or "renegocier" in f:
        bonus += 0.08
    if "suivi du stock" in f:
        bonus += 0.10
    if "bilan de promotion" in f:
        bonus += 0.06

    return bonus


def search(query: str, k: int = 5):
    """
    Recherche vectorielle FAISS + rerank lexical léger (hybride) + diversification simple.
    - On récupère plus de candidats (k * cand_mult)
    - On re-classe avec un score lexical (hits dans texte + hits dans nom de fichier)
    - On sélectionne top-k avec un cap par fichier (RAG_MAX_PER_FILE_SEARCH)
    - On met à jour _last_trace (alignée sur l'ordre renvoyé)
    """
    global _last_trace

    if _client is None or _index is None:
        raise RuntimeError("RAG non initialisé. Appelle rag.init(client) au démarrage.")

    # --- paramètres hybrides (env optionnels) ---
    cand_mult = int(os.getenv("RAG_CAND_MULT", "4"))              # ex: 4 => on prend 4*k candidats
    alpha_text = float(os.getenv("RAG_ALPHA_TEXT", "0.03"))       # poids hits dans texte
    beta_file = float(os.getenv("RAG_BETA_FILE", "0.06"))         # poids hits dans nom de fichier
    max_per_file_search = int(os.getenv("RAG_MAX_PER_FILE_SEARCH", "3"))  # cap par fichier dans le top-k final

    k = max(1, int(k))
    k_candidates = max(k, k * cand_mult)

    qvec = _embed_cached(f"{EMBEDDING_MODEL}||{query}").reshape(1, -1)
    distances, indices = _index.search(qvec, k_candidates)

    candidates = []

    # Sécurité: indices/distances peuvent être plus courts selon FAISS
    n = min(len(indices[0]), len(distances[0]))

    for i, idx in enumerate(indices[0][:n].tolist()):
        if idx < 0 or idx >= len(_meta):
            continue

        meta = _meta[idx]
        kb_id = meta.get("id", idx)
        if kb_id < 0 or kb_id >= len(_kb):
            continue

        item = _kb[kb_id]

        file_ = item.get("file", meta.get("file"))
        page_number = item.get("page_number", item.get("page", meta.get("page_number")))
        chunk_index = item.get("chunk_index", item.get("chunk_id", meta.get("chunk_index")))
        text = item.get("text", "") or ""

        # Fallbacks safe
        if page_number is None:
            page_number = -1
        if chunk_index is None:
            chunk_index = -1

        dist = float(distances[0][i])  # L2 => plus petit = meilleur

        # --- rerank lexical léger ---
        kw_text = _kw_hits(query, text)
        kw_file = _kw_hits(query, file_ or "")
        pen = _file_penalty(query, file_ or "")
        hybrid = dist - (alpha_text * kw_text) - (beta_file * kw_file) + pen


        candidates.append({
            "file": file_,
            "page_number": int(page_number),
            "chunk_index": int(chunk_index),
            "score": dist,          # distance FAISS (on garde ce champ)
            "text": text,
            "_kw_text": int(kw_text),
            "_kw_file": int(kw_file),
            "_hybrid": float(hybrid),
            "_pen": float(pen),

        })

    # Tri : meilleur hybrid d'abord, puis distance
    candidates.sort(key=lambda r: (r["_hybrid"], r["score"]))

    # --- Sélection top-k avec cap par fichier ---
    selected = []
    per_file_sel = defaultdict(int)

    for r in candidates:
        f = r.get("file") or "?"
        if per_file_sel[f] >= max_per_file_search:
            continue
        selected.append(r)
        per_file_sel[f] += 1
        if len(selected) >= k:
            break

    # Si pas assez (cap trop strict), on complète sans cap
    if len(selected) < k:
        used = {id(x) for x in selected}
        for r in candidates:
            if id(r) in used:
                continue
            selected.append(r)
            if len(selected) >= k:
                break

        # On renvoie top-k
    results = candidates[:k]

    # Trace = top-k après rerank (avec détails lexical)
    _last_trace = []
    for rank, r in enumerate(results, start=1):
        _last_trace.append({
            "rank": rank,
            "file": r.get("file"),
            "page_number": r.get("page_number"),
            "chunk_index": r.get("chunk_index"),
            "distance": float(r.get("score", 0.0)),          # distance FAISS (L2)
            "kw_text": int(r.get("_kw_text", 0)),
            "kw_file": int(r.get("_kw_file", 0)),
            "hybrid": float(r.get("_hybrid", r.get("score", 0.0))),
            "included": False,   # sera mis à True par build_context
            "reason": "",
            "pen": float(r.get("_pen", 0.0)),

        })

    # On retire les champs internes du retour utilisateur
    for r in results:
        r.pop("_kw_text", None)
        r.pop("_kw_file", None)
        r.pop("_hybrid", None)

    return results










_WORD_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)

_STOPWORDS_FR = {
    "le","la","les","un","une","des","du","de","d","dans","sur","pour","par","avec","sans","et","ou",
    "a","au","aux","en","ce","cet","cette","ces","se","sa","son","ses","leur","leurs","nous","vous",
    "il","elle","ils","elles","on","que","qui","quoi","dont","où","est","sont","été","être",
}

def _normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

def _keywords(text: str) -> list[str]:
    """Tokens query/texte (liste ordonnée) pour permettre bigrams."""
    text = _normalize_text(text)
    toks = [t for t in _WORD_RE.findall(text) if t and t not in _STOPWORDS_FR]
    return toks[:24]  # cap simple pour rester léger

def _kw_hits(query: str, target: str) -> int:
    """
    Score lexical très léger :
    - +1 par token query présent dans target
    - +2 par bigram query présent (ex: 'mandat stock')
    """
    if not query or not target:
        return 0

    q = _keywords(query)
    if not q:
        return 0

    tgt = _normalize_text(target)
    hits = 0

    # unigrams
    for tok in q:
        if tok and tok in tgt:
            hits += 1

    # bigrams (évite le bug set non subscriptable)
    for a, b in zip(q, q[1:]):
        phrase = f"{a} {b}"
        if phrase in tgt:
            hits += 2

    return hits

def _norm_file_key(file_name: str) -> str:
    return _normalize_text((file_name or "").replace("_", " "))

def _file_penalty(query: str, file_name: str) -> float:
    """
    Petite pénalité si le fichier est manifestement hors-sujet.
    But : faire descendre doucement, pas exclure.
    """
    q = _normalize_text(query)
    f = _norm_file_key(file_name)

    # Ex : si on parle de mandat/stock, pénaliser les fichiers sans "mandat"
    if ("mandat" in q or "stock" in q) and ("mandat" not in f and "mandats" not in f):
        return float(os.getenv("RAG_PENALTY_OFFTOPIC", "0.06"))

    return 0.0




def build_context(
    query: str,
    k: int = 5,
    max_chars: int = 4500,
    max_per_file: int = 2,
    max_chunk_chars: int = 650,
) -> str:
    """
    Construit un contexte RAG lisible et "dense" :
    - Diversifie les sources (cap par fichier)
    - Tronque les chunks pour en inclure davantage (packing)
    - Met à jour _last_trace (included/reason)
    """
    global _last_trace

    res = search(query, k=k)
    if not res:
        _last_trace = []
        return "Aucun extrait pertinent trouvé."

    # Trace produite par search() (1 entrée par résultat renvoyé)
    trace = _last_trace if isinstance(_last_trace, list) else []

    # Si la trace n'est pas alignée avec res, on la reconstruit minimalement
    if len(trace) != len(res):
        trace = []
        for rank, r in enumerate(res, start=1):
            trace.append({
                "rank": rank,
                "file": r.get("file"),
                "page_number": r.get("page_number"),
                "chunk_index": r.get("chunk_index"),
                "distance": float(r.get("score", 0.0)),
                "included": False,
                "reason": "",
            })
    else:
        # reset included/reason avant packing
        for t in trace:
            t["included"] = False
            t["reason"] = ""

    def _set_trace(rank: int, included: bool, reason: str = ""):
        for t in trace:
            if t.get("rank") == rank:
                t["included"] = included
                t["reason"] = reason or ""
                return

    parts: list[str] = []
    total = 0
    per_file = defaultdict(int)

    for rank, r in enumerate(res, start=1):
        file_ = (r.get("file") or "?").strip() or "?"
        if per_file[file_] >= max_per_file:
            _set_trace(rank, False, f"per_file_cap={max_per_file}")
            continue

        text = (r.get("text") or "").strip()
        if not text:
            _set_trace(rank, False, "empty_text")
            continue

        # Tronquer pour "packer" plus de chunks
        if len(text) > max_chunk_chars:
            text = text[:max_chunk_chars].rstrip() + "…"

        page = r.get("page_number", -1)
        chunk = r.get("chunk_index", -1)

        block = (
            f"---\n"
            f"Fichier: {file_}\n"
            f"Page: {page} | Chunk: {chunk}\n"
            f"Texte:\n{text}\n"
        )

        if total + len(block) > max_chars:
            _set_trace(rank, False, f"max_chars={max_chars}")
            continue

        parts.append(block)
        total += len(block)
        per_file[file_] += 1
        _set_trace(rank, True, "")

    # Sauvegarde trace enrichie
    _last_trace = trace

    if not parts:
        return "Aucun extrait pertinent trouvé."

    return "\n".join(parts)





def _mark_included(trace: list[dict], included: list[dict], reason_excluded: str = "") -> list[dict]:
    """
    Marque dans la trace quels chunks ont été inclus dans le contexte final.
    'included' = liste de résultats (dict) effectivement ajoutés au contexte.
    """
    if not trace:
        return trace

    included_keys = {
        (r.get("file"), r.get("page_number"), r.get("chunk_index"))
        for r in (included or [])
    }

    for t in trace:
        key = (t.get("file"), t.get("page_number"), t.get("chunk_index"))
        t["included"] = key in included_keys
        if (not t["included"]) and reason_excluded and not t.get("reason"):
            t["reason"] = reason_excluded

    return trace









