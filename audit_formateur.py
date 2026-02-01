import os
import json
import argparse
import textwrap
from dotenv import load_dotenv

import numpy as np
import faiss
from openai import OpenAI


# =========================
# CONFIG
# =========================
KB_FILE = "base_connaissances.json"
INDEX_FILE = "faiss_index.bin"
META_FILE = "faiss_metadata.json"

EMBEDDING_MODEL = "text-embedding-3-small"
ANSWER_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
AUDIT_MODEL = os.getenv("OPENAI_AUDIT_MODEL", "gpt-4o-mini")

AUDIT_PROMPT_FILE = os.path.join("prompts", "prompt_audit_v2.txt")
FORMATEUR_PROMPT_FILE = os.path.join("prompts", "prompt_formateur.txt")  # optionnel


# =========================
# INIT
# =========================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================
# UTILS
# =========================
def load_text_file(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip() or None


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_embedding(text: str) -> list[float]:
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return resp.data[0].embedding


def format_sources(sources: list[dict]) -> str:
    out = []
    for idx, s in enumerate(sources, start=1):
        out.append(textwrap.dedent(f"""
        [S{idx}] Fichier : {s.get('file')} | Page : {s.get('page_number')} | Chunk : {s.get('chunk_index')} | Score : {s.get('score')}
        Texte :
        {s.get('text')}
        """).strip())
    return "\n\n".join(out).strip()



def build_rag_sources(question: str, k: int = 5) -> list[dict]:
    kb = load_json(KB_FILE)
    meta = load_json(META_FILE)
    index = faiss.read_index(INDEX_FILE)

    # ✅ Multi-queries : on enrichit la requête avec des mots-clés métier
    queries = [
        question,
        question + " vente du service",
        question + " mandat confiance",
        question + " actions de promotion",
        question + " sécuriser signature mandat",
        question + " moyens outils de promotion",
        question + " vente du service mandat",
        question + " argumentaire mandat confiance",
        question + " objections signature mandat",
        question + " plan de commercialisation",
        question + " moyens et outils de promotion",
        question + " plan de commercialisation",
        question + " actions de promotion",
        question + " visite marketing",
        question + " panneau",
        question + " extranet vendeur",
        question + " compte rendu de visite",
        

        
    ]

    # Recherche sur chaque requête puis fusion des résultats
    seen = set()
    merged = []

    for q in queries:
        q_emb = np.array([get_embedding(q)], dtype="float32")
        distances, indices = index.search(q_emb, k)

        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(meta):
                continue
            if idx in seen:
                continue
            seen.add(idx)

            m = meta[idx]
            kb_id = m.get("id", None)
            chunk_text = ""
            if isinstance(kb_id, int) and 0 <= kb_id < len(kb):
                chunk_text = (kb[kb_id].get("text") or "").strip()

            score = round(1.0 / (1.0 + float(dist)), 4)

            merged.append({
                "rank": None,
                "score": score,
                "distance": float(dist),
                "file": m.get("file", "unknown.pdf"),
                "page_number": m.get("page_number", None),
                "chunk_index": m.get("chunk_index", None),
                "text": chunk_text[:1200]
            })

    # Trie par pertinence (score décroissant) et garde top-k final
    merged.sort(key=lambda x: x["score"], reverse=True)
    merged = merged[:k]

    # remettre un rank propre
    for i, s in enumerate(merged, start=1):
        s["rank"] = i

    return merged



def default_formateur_system_prompt() -> str:
    # Fallback si prompt_formateur.txt absent
    return (
        "Tu es un formateur senior terrain en vente immobilière. "
        "Posture mentor : bienveillant, exigeant, calme. "
        "Tu respectes STRICTEMENT la charte : "
        "1) identifier l’enjeu terrain réel, "
        "2) structurer 3 à 5 points max, "
        "3) contextualiser (type vendeur + situation + émotion), "
        "4) proposer au moins 1 cas pratique (dialogue vendeur/agent), "
        "5) donner des formulations terrain, "
        "6) signaler les limites du support (sans inventer), "
        "7) conclure par un ancrage opérationnel (action prochain RDV). "
        "Tu t’appuies uniquement sur les extraits fournis."
    )


def generate_formateur_answer(question: str, sources: list[dict]) -> str:
    system_prompt = load_text_file(FORMATEUR_PROMPT_FILE) or default_formateur_system_prompt()
    contexte = format_sources(sources)

    user_prompt = textwrap.dedent(f"""
    Question du conseiller immobilier :
    {question}

    Extraits du support (RAG) :
    {contexte}

    Consignes :
    - Réponds uniquement à partir des extraits.
    - Contextualisation : utilise un détail vendeur/situation UNIQUEMENT si un extrait le mentionne explicitement ; sinon fais une contextualisation neutre ("dans un contexte typique...") sans inventer.
    - 3 à 5 points maximum.
    - Ajoute au moins 1 cas pratique (dialogue court vendeur/agent).
    - Donne des formulations terrain prononçables.
    - Dans "Ancrage opérationnel", écris explicitement : "Prochain rendez-vous : ..." + 2 actions concrètes.
    - Signale clairement ce qui n’est pas couvert par les extraits.
    - Termine par un résumé opérationnel + action terrain.
    """).strip()

    resp = client.chat.completions.create(
        model=ANSWER_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content


def audit_answer_v2(question: str, sources: list[dict], answer: str) -> str:
    audit_system = load_text_file(AUDIT_PROMPT_FILE)
    if not audit_system:
        raise FileNotFoundError(
            f"Prompt d’audit introuvable : {AUDIT_PROMPT_FILE}\n"
            "Crée-le (prompts/prompt_audit_v2.txt) et colle le prompt d’audit V2."
        )

    contexte = format_sources(sources)

    audit_user = textwrap.dedent(f"""
    QUESTION :
    {question}

    EXTRAITS (RAG) :
    {contexte}

    RÉPONSE À AUDITER :
    {answer}

    Fais l’audit selon le FORMAT DE SORTIE STRICT demandé.
    """).strip()

    resp = client.chat.completions.create(
        model=AUDIT_MODEL,
        messages=[
            {"role": "system", "content": audit_system},
            {"role": "user", "content": audit_user},
        ],
        temperature=0.1,
    )
    return resp.choices[0].message.content


# =========================
# CLI
# =========================
def main():
    parser = argparse.ArgumentParser(description="Mode AUDIT interne (RAG + audit Charte V2)")
    parser.add_argument("-k", type=int, default=5, help="Nombre d'extraits RAG à afficher (top-k)")
    parser.add_argument("--no-answer", action="store_true", help="Ne génère pas la réponse formateur")
    parser.add_argument("-q", "--question", type=str, help="Question à auditer (sinon demandé en input)")
    parser.add_argument("--no-audit", action="store_true", help="Ne fait pas l'audit (affiche seulement RAG + réponse)")
    args = parser.parse_args()

    # sanity checks
    for f in [KB_FILE, INDEX_FILE, META_FILE]:
        if not os.path.exists(f):
            print(f"❌ Fichier manquant : {f}")
            print("➡️ Assure-toi d’avoir généré base_connaissances.json + faiss_index.bin + faiss_metadata.json")
            return

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY manquante (vérifie .env)")
        return

    print("\n🔍 MODE AUDIT INTERNE (terminal)")
    question = (args.question or input("\nTa question à auditer : ")).strip()

    if not question:
        print("❌ Question vide.")
        return

    print("\n⏳ Recherche RAG...")
    sources = build_rag_sources(question, k=args.k)

    print("\n📌 Résultats RAG (top-k) :\n")
    print(format_sources(sources))

    answer = ""
    if not args.no_answer:
        print("\n⏳ Génération de la réponse formateur (pour audit)...")
        answer = generate_formateur_answer(question, sources)
        print("\n🧠 RÉPONSE FORMATEUR (à auditer) :\n")
        print(answer)

    if args.no_audit:
        return

    if not answer:
        print("\n⚠️ Pas de réponse à auditer (utilise sans --no-answer).")
        return

    print("\n⏳ AUDIT CHARTE V2...")
    audit = audit_answer_v2(question, sources, answer)
    print("\n" + audit + "\n")


if __name__ == "__main__":
    main()
