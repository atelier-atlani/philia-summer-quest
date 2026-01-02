import json
from pathlib import Path

PAGES_FILE = Path("pages_extraites.json")
OUT_FILE = Path("base_connaissances.json")

CHUNK_SIZE = 1200   # caractères
OVERLAP = 200       # caractères

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP):
    text = (text or "").strip()
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks

def main():
    if not PAGES_FILE.exists():
        print("❌ pages_extraites.json introuvable. Lance d'abord: python extract_pdf.py")
        return

    pages = json.loads(PAGES_FILE.read_text(encoding="utf-8"))
    print(f"📄 Pages chargées : {len(pages)}")

    chunks = []
    for p in pages:
        file_name = p.get("file", "unknown.pdf")
        page_number = p.get("page_number", 0)
        text = p.get("text", "")

        for idx, ch in enumerate(chunk_text(text), start=1):
            chunks.append({
                "file": file_name,
                "page": page_number,
                "chunk_id": idx,
                "text": ch
            })

    OUT_FILE.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 base_connaissances.json recréé avec {len(chunks)} chunks")

if __name__ == "__main__":
    main()
