import os
import json

from pathlib import Path
from pypdf import PdfReader

PDF_FOLDER = "pdfs"

def list_pdf_files(folder: str):
    """
    Retourne la liste des PDFs dans folder ET tous ses sous-dossiers.
    Exemple: pdfs/vendeur/xxx.pdf sera trouvé.
    """
    base = Path(folder)
    return [str(p) for p in base.rglob("*.pdf")]

def pdf_to_pages(path: str):
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append({
                "file": os.path.basename(path),   # garde le nom du fichier
                "path": path,                     # ajoute le chemin complet (utile ensuite)
                "page_number": i + 1,
                "text": text.strip()
            })
    return pages

def main():
    pdf_files = list_pdf_files(PDF_FOLDER)
    if not pdf_files:
        print("⚠️ Aucun PDF trouvé dans le dossier 'pdfs' (y compris sous-dossiers).")
        return

    print(f"📦 PDFs trouvés : {len(pdf_files)}")

    all_pages = []

    for pdf_path in pdf_files:
        print(f"🔍 Lecture de : {pdf_path}")
        try:
            pages = pdf_to_pages(pdf_path)
            print(f"   → {len(pages)} pages extraites")
            all_pages.extend(pages)
        except Exception as e:
            print(f"❌ Erreur sur {pdf_path} : {e}")

    print(f"\n✅ Total pages extraites : {len(all_pages)}")
    # Sauvegarde pour construire ensuite la base de connaissances
    out_file = "pages_extraites.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_pages, f, ensure_ascii=False, indent=2)
    print(f"💾 Pages sauvegardées dans {out_file}")

    # Affiche un exemple pour vérifier
    if all_pages:
        sample = all_pages[0]
        print("\n--- Exemple de page extraite ---")
        print(f"Fichier : {sample['file']}")
        print(f"Chemin : {sample['path']}")
        print(f"Page   : {sample['page_number']}")
        print("Texte  :")
        print(sample["text"][:1000])  # limite à 1000 caractères

if __name__ == "__main__":
    main()
