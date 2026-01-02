import json
import numpy as np
import faiss
import os
from dotenv import load_dotenv
from openai import OpenAI

KB_FILE = "base_connaissances.json"
INDEX_FILE = "faiss_index.bin"
META_FILE = "faiss_metadata.json"
EMBEDDING_MODEL = "text-embedding-3-small"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_index():
    if not os.path.exists(INDEX_FILE) or not os.path.exists(META_FILE):
        raise FileNotFoundError("Index ou métadonnées manquants. Lance d'abord build_index.py.")
    
    index = faiss.read_index(INDEX_FILE)

    with open(META_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    with open(KB_FILE, "r", encoding="utf-8") as f:
        kb = json.load(f)

    return index, metadata, kb

def get_embedding(text: str):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return np.array(response.data[0].embedding, dtype="float32")

def search(query: str, k: int = 3):
    index, metadata, kb = load_index()
    query_emb = np.array([get_embedding(query)], dtype="float32")
    distances, indices = index.search(query_emb, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        meta = metadata[idx]
        chunk = kb[meta["id"]]
        results.append({
            "distance": float(dist),
            "file": meta["file"],
            "page_number": meta["page_number"],
            "chunk_index": meta["chunk_index"],
            "text": chunk["text"]
        })
    return results

def main():
    print("🔎 Moteur de recherche sur ta base de connaissances PDF")
    query = input("\nPose une question : ")

    results = search(query)

    print("\n📌 Résultats les plus pertinents :\n")
    for i, res in enumerate(results, start=1):
        print(f"--- Résultat {i} ---")
        print(f"Fichier : {res['file']}")
        print(f"Page    : {res['page_number']} (chunk {res['chunk_index']})")
        print(f"Score   : {res['distance']:.4f}")
        print("Texte   :")
        print(res["text"])
        print()

if __name__ == "__main__":
    main()
