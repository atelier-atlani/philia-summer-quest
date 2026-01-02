import re
import json
import os
from pypdf import PdfReader

PDF_FOLDER = "pdfs"
OUTPUT_FILE = "base_connaissances.json"

def list_pdf_files(folder):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ]

def clean_text(text: str) -> str:
    # Remplace certains caractères spéciaux et normalise les espaces
    text = text.replace("\xa0", " ")  # espaces insécables
    text = re.sub(r"\s+", " ", text)  # plusieurs espaces/sauts de ligne -> un seul espace
    return text.strip()

def split_text(text: str, max_chars: int = 800, overlap: int = 100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    return chunks

def pdf_to_chunks(path):
    reader = PdfReader(path)
    all_chunks = []

    for i, page in enumerate(reader.pages):
        raw_text = page.extract_text()
        if not raw_text:
            continue

        text = clean_text(raw_text)
        chunks = split_text(text, max_chars=800, overlap=100)

        for idx, chunk in enumerate(chunks):
            all_chunks.append({
                "file": os.path.basename(path),
                "page_number": i + 1,
                "chunk_index": idx,
                "text": chunk
            })

    return all_chunks

def main():
    pdf_files = list_pdf_files(PDF_FOLDER)
    if not pdf_files:
        print("⚠️ Aucun PDF trouvé dans le dossier 'pdfs'.")
        return

    kb = []

    for pdf_path in pdf_files:
        print(f"📄 Traitement de : {pdf_path}")
        chunks = pdf_to_chunks(pdf_path)
        print(f"   → {len(chunks)} chunks")
        kb.extend(chunks)

    print(f"\n✅ Total chunks : {len(kb)}")

    # Sauvegarde dans un fichier JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)

    # Affiche un exemple
    if kb:
        sample = kb[0]
        print("\n--- Exemple de chunk ---")
        print(f"Fichier      : {sample['file']}")
        print(f"Page         : {sample['page_number']}")
        print(f"Chunk index  : {sample['chunk_index']}")
        print("Texte        :")
        print(sample['text'])

if __name__ == "__main__":
    main()
