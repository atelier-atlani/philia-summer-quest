"""
scripts/index_marche_modules.py — Indexation des 100 modules marché dans FAISS.

Ajoute les modules marché à la base existante (base_connaissances.json,
faiss_index.bin, faiss_metadata.json) sans supprimer les entrées PDF.

Usage :
    .venv/bin/python scripts/index_marche_modules.py [--dry-run] [--force]

Options :
    --dry-run   Parse et affiche les modules sans modifier les fichiers
    --force     Ré-indexe même si des modules marché sont déjà présents
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List, Dict

import numpy as np

# Résolution du path projet (scripts/ → racine)
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

try:
    import faiss
except ImportError:
    print("❌ faiss manquant. Installe avec : pip install faiss-cpu")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

import os
from openai import OpenAI

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

MODULES_DIR = _ROOT / "training/modules/marche/modules"
KB_FILE     = _ROOT / "base_connaissances.json"
INDEX_FILE  = _ROOT / "faiss_index.bin"
META_FILE   = _ROOT / "faiss_metadata.json"

EMBEDDING_MODEL = "text-embedding-3-small"
SOURCE_TAG      = "marche_module"  # identifiant pour détecter les doublons

FILE_MAP = [
    "01_fondamentaux_marche_1-20.md",
    "02_analyse_marche_france_7-20.md",
    "03_juridique_prospection_21-40.md",
    "04_technique_estimation_41-60.md",
    "05_marketing_vente_61-80.md",
    "06_operationnel_local_81-100.md",
]

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_modules_from_file(file_path: Path) -> List[Dict]:
    """Extrait tous les modules (### Module N : Titre) d'un fichier markdown."""
    content = file_path.read_text(encoding="utf-8")
    modules = []

    # Chaque module commence par "### Module N :" et finit au prochain "### Module" ou "## "
    pattern = r"### Module (\d+) : (.+?)\n(.*?)(?=\n### Module |\n## |\Z)"
    for match in re.finditer(pattern, content, re.DOTALL):
        module_id = int(match.group(1))
        titre = match.group(2).strip()
        body = match.group(3).strip()

        # Extraire objectif
        obj_m = re.search(r"\*\*Objectif\*\* : (.+?)(?=\n\*\*|\n\n|\Z)", body, re.DOTALL)
        objectif = obj_m.group(1).strip() if obj_m else ""

        # Extraire tags
        tags_m = re.search(r"\*\*Tags\*\* : (.+)", body)
        tags = tags_m.group(1).strip() if tags_m else ""

        # Texte complet à indexer
        text = f"Module {module_id} : {titre}\n\nObjectif : {objectif}\n\n{body}\n\nTags : {tags}"

        modules.append({
            "module_id": module_id,
            "titre": titre,
            "file": file_path.name,
            "text": text,
        })

    return modules


def parse_all_modules() -> List[Dict]:
    all_modules: List[Dict] = []
    for filename in FILE_MAP:
        path = MODULES_DIR / filename
        if not path.exists():
            print(f"⚠️  Fichier introuvable : {path}")
            continue
        mods = parse_modules_from_file(path)
        print(f"   📖 {filename} → {len(mods)} modules")
        all_modules.extend(mods)
    return sorted(all_modules, key=lambda m: m["module_id"])


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

def get_embedding(client: OpenAI, text: str) -> List[float]:
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return resp.data[0].embedding


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

def already_indexed(kb: List[Dict]) -> set[int]:
    """Retourne les module_id déjà dans la KB."""
    ids: set[int] = set()
    for item in kb:
        if item.get("source") == SOURCE_TAG:
            ids.add(int(item.get("module_id", -1)))
    return ids


def run(dry_run: bool = False, force: bool = False) -> int:
    print("🚀 Indexation modules marché dans FAISS\n")

    # 1. Parser les modules
    print("📂 Parsing des fichiers markdown...")
    modules = parse_all_modules()
    total = len(modules)
    print(f"\n✅ {total} modules extraits (attendu : 100)")

    if total == 0:
        print("❌ Aucun module trouvé. Vérifier MODULES_DIR.")
        return 0

    # Détecter manquants
    found_ids = {m["module_id"] for m in modules}
    missing = sorted(set(range(1, 101)) - found_ids)
    if missing:
        print(f"⚠️  Modules manquants : {missing}")

    if dry_run:
        print("\n[DRY-RUN] Aucune modification.")
        for m in modules:
            print(f"  Module {m['module_id']:3d} — {m['titre'][:60]}")
        return total

    # 2. Charger KB et FAISS existants
    print("\n📊 Chargement de la base existante...")
    with open(KB_FILE, encoding="utf-8") as f:
        kb: List[Dict] = json.load(f)
    with open(META_FILE, encoding="utf-8") as f:
        meta: List[Dict] = json.load(f)
    index = faiss.read_index(str(INDEX_FILE))

    print(f"   KB : {len(kb)} entrées existantes")
    print(f"   FAISS : {index.ntotal} vecteurs, dim {index.d}")

    # Vérifier doublons
    existing_ids = already_indexed(kb)
    if existing_ids and not force:
        print(f"\n⚠️  {len(existing_ids)} modules marché déjà indexés : {sorted(existing_ids)[:10]}{'...' if len(existing_ids) > 10 else ''}")
        print("   Utilise --force pour ré-indexer.")
        return 0

    if existing_ids and force:
        print(f"⚡ --force : suppression de {len(existing_ids)} entrées marché existantes...")
        kb   = [e for e in kb   if e.get("source") != SOURCE_TAG]
        meta = [e for e in meta if e.get("source") != SOURCE_TAG]
        # Reconstruire le FAISS sans les entrées marché — on reconstruira tout à la fin
        # (approche la plus simple : rebuild complet via build_index.py n'est pas forcé ici
        #  on repart de l'index nettoyé basé sur meta restant)

    # 3. Initialiser client OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY manquante (.env ou variable d'environnement)")
        return 0
    client = OpenAI(api_key=api_key)

    # 4. Indexer chaque module
    print("\n🔢 Génération embeddings et indexation...")
    start_kb_id = len(kb)
    new_embeddings: List[List[float]] = []
    indexed = 0

    for m in modules:
        if m["module_id"] in existing_ids and not force:
            print(f"   ↩ Module {m['module_id']:3d} : déjà indexé (skip)")
            continue

        try:
            emb = get_embedding(client, m["text"])
            new_embeddings.append(emb)

            kb_id = start_kb_id + indexed
            kb.append({
                "file":      m["file"],
                "page":      m["module_id"],   # module_id en guise de "page"
                "chunk_id":  0,
                "text":      m["text"],
                "source":    SOURCE_TAG,
                "module_id": m["module_id"],
                "titre":     m["titre"],
            })
            meta.append({
                "id":          kb_id,
                "file":        m["file"],
                "page_number": m["module_id"],
                "chunk_index": 0,
                "source":      SOURCE_TAG,
                "module_id":   m["module_id"],
            })

            indexed += 1
            print(f"   ✓ Module {m['module_id']:3d} : {m['titre'][:55]}")

        except Exception as e:
            print(f"   ✗ Module {m['module_id']:3d} : Erreur embedding — {e}")

    if indexed == 0:
        print("\nRien à indexer.")
        return 0

    # 5. Ajouter les nouveaux vecteurs au FAISS
    print(f"\n💾 Ajout de {indexed} vecteurs dans FAISS...")
    emb_array = np.array(new_embeddings, dtype="float32")
    index.add(emb_array)
    print(f"   FAISS total : {index.ntotal} vecteurs")

    # 6. Sauvegarder
    print("\n💾 Sauvegarde des fichiers...")
    faiss.write_index(index, str(INDEX_FILE))
    print(f"   ✅ {INDEX_FILE.name}")

    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    print(f"   ✅ {KB_FILE.name} ({len(kb)} entrées)")

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"   ✅ {META_FILE.name} ({len(meta)} entrées)")

    print(f"\n🎉 {indexed}/{total} modules marché indexés avec succès !")
    return indexed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    force   = "--force"   in sys.argv
    count   = run(dry_run=dry_run, force=force)
    sys.exit(0 if count > 0 else 1)
