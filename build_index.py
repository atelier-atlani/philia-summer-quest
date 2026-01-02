import json
import numpy as np
import faiss
import os
from dotenv import load_dotenv
from openai import OpenAI

# Chargement des variables d'environnement (.env)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

KB_FILE = "base_connaissances.json"
INDEX_FILE = "faiss_index.bin"
META_FILE = "faiss_metadata.json"

EMBEDDING_MODEL = "text-embedding-3-small"  # modèle d'embeddings


def load_kb():
    with open(KB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_embedding(text: str):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def build_index():
    kb = load_kb()
    print(f"📚 Chunks chargés : {len(kb)}")

    embeddings = []
    metadata = []

    processed = 0

    for i, item in enumerate(kb):
        text = (item.get("text") or "").strip()
        if not text:
            continue

        emb = get_embedding(text)
        embeddings.append(emb)

        metadata.append({
            "id": i,
            "file": item.get("file", "unknown.pdf"),
            "page_number": item.get("page_number", item.get("page", None)),
            "chunk_index": item.get("chunk_index", item.get("chunk_id", i)),
        })

        processed += 1
        if processed % 50 == 0:
            print(f"   → {processed} chunks traités")

    if not embeddings:
        print("⚠️ Aucun embedding généré (textes vides ?).")
        return

    embeddings = np.array(embeddings).astype("float32")
    dimension = embeddings.shape[1]
    print(f"🧠 Dimension des embeddings : {dimension}")

    # Création de l'index FAISS
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Sauvegarde de l'index
    faiss.write_index(index, INDEX_FILE)
    print(f"💾 Index sauvegardé dans {INDEX_FILE}")

    # Sauvegarde des métadonnées
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"💾 Métadonnées sauvegardées dans {META_FILE}")

    print("✅ Index vectoriel construit avec succès.")


def main():
    if not os.path.exists(KB_FILE):
        print(f"⚠️ Fichier {KB_FILE} introuvable. Lance d'abord build_kb_from_pages.py.")
        return

    build_index()


if __name__ == "__main__":
    main()
