"""
scripts/index_donnees_locales.py — Indexe donnees_marche_locales.md dans FAISS.

Chunking par section H2. Chaque section = 1 entrée KB avec embedding.

Usage :
    .venv/bin/python scripts/index_donnees_locales.py [--force]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

try:
    import faiss
except ImportError:
    print("❌ faiss manquant. pip install faiss-cpu")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

import os
from openai import OpenAI

# ---------------------------------------------------------------------------
SOURCE_FILE = _ROOT / "training/modules/marche/donnees_marche_locales.md"
SOURCE_TAG  = "donnees_locales"

KB_FILE     = _ROOT / "base_connaissances.json"
INDEX_FILE  = _ROOT / "faiss_index.bin"
META_FILE   = _ROOT / "faiss_metadata.json"
EMBEDDING_MODEL = "text-embedding-3-small"
# ---------------------------------------------------------------------------


def parse_sections(md_path: Path) -> list[dict]:
    """Découpe le fichier par sections H2 (## Titre)."""
    content = md_path.read_text(encoding="utf-8")
    chunks = []

    # Découper par "## "
    parts = re.split(r"(?=^## )", content, flags=re.MULTILINE)
    for part in parts:
        part = part.strip()
        if not part or part.startswith("#") and not part.startswith("## "):
            continue  # skip H1 header
        if not part.startswith("## "):
            continue

        title_match = re.match(r"^## (.+)", part)
        if not title_match:
            continue

        title = title_match.group(1).strip()
        body  = part[len(title_match.group(0)):].strip()

        text = f"{title}\n\n{body}"
        chunks.append({"titre": title, "text": text})

    return chunks


def run(force: bool = False) -> int:
    print("🚀 Indexation données marché locales dans FAISS\n")

    sections = parse_sections(SOURCE_FILE)
    print(f"📖 {len(sections)} sections extraites de {SOURCE_FILE.name}")
    for s in sections:
        print(f"   • {s['titre']}")

    # Charger KB et FAISS
    with open(KB_FILE, encoding="utf-8") as f:
        kb: list[dict] = json.load(f)
    with open(META_FILE, encoding="utf-8") as f:
        meta: list[dict] = json.load(f)
    index = faiss.read_index(str(INDEX_FILE))

    print(f"\n📊 KB : {len(kb)} entrées existantes | FAISS : {index.ntotal} vecteurs")

    # Détecter doublons
    existing = {e.get("titre") for e in kb if e.get("source") == SOURCE_TAG}
    if existing and not force:
        print(f"\n⚠️  {len(existing)} sections déjà indexées. Utilise --force pour ré-indexer.")
        return 0

    if existing and force:
        kb   = [e for e in kb   if e.get("source") != SOURCE_TAG]
        meta = [e for e in meta if e.get("source") != SOURCE_TAG]
        print(f"⚡ --force : {len(existing)} entrées supprimées, ré-indexation...")

    # Embeddings
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY manquante")
        return 0

    client = OpenAI(api_key=api_key)

    print("\n🔢 Génération embeddings...")
    start_id = len(kb)
    new_embeddings = []
    indexed = 0

    for i, section in enumerate(sections):
        try:
            resp = client.embeddings.create(model=EMBEDDING_MODEL, input=section["text"])
            emb = resp.data[0].embedding
            new_embeddings.append(emb)

            kb_id = start_id + indexed
            kb.append({
                "file":    SOURCE_FILE.name,
                "page":    i + 1,
                "chunk_id": 0,
                "text":    section["text"],
                "source":  SOURCE_TAG,
                "titre":   section["titre"],
            })
            meta.append({
                "id":          kb_id,
                "file":        SOURCE_FILE.name,
                "page_number": i + 1,
                "chunk_index": 0,
                "source":      SOURCE_TAG,
            })

            indexed += 1
            print(f"   ✓ {section['titre'][:65]}")

        except Exception as e:
            print(f"   ✗ {section['titre'][:65]} — {e}")

    if not new_embeddings:
        return 0

    # Ajouter au FAISS
    index.add(np.array(new_embeddings, dtype="float32"))
    print(f"\n💾 FAISS : {index.ntotal} vecteurs")

    faiss.write_index(index, str(INDEX_FILE))
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"✅ {indexed} sections indexées. KB : {len(kb)} entrées.")
    return indexed


if __name__ == "__main__":
    force = "--force" in sys.argv
    count = run(force=force)
    sys.exit(0 if count > 0 else 1)
