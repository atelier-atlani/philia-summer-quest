"""
Build FAISS index from data/sources_maths/.
Reads PDF and docx files, chunks text, generates embeddings, saves index.

Usage:
    python scripts/build_rag_index.py [--test]

Options:
    --test  Index only the first 3 files (fast, for CI / smoke tests)
"""

import json
import sys
import os
import argparse
from pathlib import Path

import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ROOT       = Path(__file__).parent.parent
SOURCES    = ROOT / "data" / "sources_maths"
OUT_DIR    = ROOT / "data" / "rag_index"
KB_FILE    = OUT_DIR / "base_connaissances_maths.json"
INDEX_FILE = OUT_DIR / "faiss_index.bin"
META_FILE  = OUT_DIR / "faiss_metadata.json"

EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE      = 400   # caractères
CHUNK_OVERLAP   = 50
MIN_CHUNK_CHARS = 60    # ignorer les chunks trop courts


# ---------------------------------------------------------------------------
# Extracteurs de texte
# ---------------------------------------------------------------------------

def _extract_pdf(path: Path) -> str:
    try:
        import PyPDF2
        text = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text() or ""
                text.append(t)
        return "\n".join(text)
    except Exception as e:
        print(f"  [WARN] PDF non lisible ({path.name}) : {e}")
        return ""


def _extract_docx(path: Path) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f"  [WARN] DOCX non lisible ({path.name}) : {e}")
        return ""


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix == ".docx":
        return _extract_docx(path)
    return ""


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, file_name: str) -> list[dict]:
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if len(chunk) >= MIN_CHUNK_CHARS:
            chunks.append({
                "text": chunk,
                "file": file_name,
                "chunk_index": idx,
                "page_number": -1,
            })
            idx += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

def get_embeddings_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Appel par batch de 100 (limite OpenAI)."""
    all_embs = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        all_embs.extend([e.embedding for e in resp.data])
        print(f"   → {min(i + batch_size, len(texts))}/{len(texts)} embeddings générés")
    return all_embs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_index(test_mode: bool = False) -> None:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Collecter les fichiers à indexer
    extensions = {".pdf", ".docx"}
    files = sorted(p for p in SOURCES.rglob("*") if p.suffix.lower() in extensions)
    if test_mode:
        files = files[:3]
        print(f"[TEST MODE] Indexation de {len(files)} fichier(s) seulement.")
    else:
        print(f"Fichiers à indexer : {len(files)}")

    # 2. Extraire + chunker
    kb = []
    for path in files:
        text = extract_text(path)
        if not text.strip():
            continue
        chunks = chunk_text(text, path.name)
        kb.extend(chunks)
        print(f"  {path.name} → {len(chunks)} chunks")

    print(f"\nTotal chunks : {len(kb)}")
    if not kb:
        print("⚠️  Aucun chunk extrait. Vérifier data/sources_maths/.")
        sys.exit(1)

    # 3. Sauvegarder la base de connaissances
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    print(f"KB sauvegardée → {KB_FILE}")

    # 4. Générer les embeddings
    texts = [item["text"] for item in kb]
    print(f"\nGénération de {len(texts)} embeddings ({EMBEDDING_MODEL})...")
    embeddings = get_embeddings_batch(client, texts)

    # 5. Construire et sauvegarder l'index FAISS
    emb_array = np.array(embeddings, dtype="float32")
    dimension = emb_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(emb_array)
    faiss.write_index(index, str(INDEX_FILE))
    print(f"Index FAISS sauvegardé → {INDEX_FILE} ({index.ntotal} vecteurs, dim {dimension})")

    # 6. Sauvegarder les métadonnées
    metadata = [
        {"id": i, "file": item["file"], "chunk_index": item["chunk_index"], "page_number": item["page_number"]}
        for i, item in enumerate(kb)
    ]
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Métadonnées sauvegardées → {META_FILE}")
    print("\nIndex RAG maths construit avec succès.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Indexer seulement 3 fichiers (test rapide)")
    args = parser.parse_args()
    build_index(test_mode=args.test)
