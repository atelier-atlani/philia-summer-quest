from __future__ import annotations

import os
import sys
import re
from pathlib import Path

# --- permet d'importer agent_formateur depuis /scripts ---
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import agent_formateur as a  # noqa


def _has_5_sections(txt: str) -> bool:
    """Vérifie qu'on a bien 1) 2) 3) 4) 5) dans l'ordre."""
    if not txt:
        return False
    # tolère espaces, retours ligne
    return all(s in txt for s in ["1)", "2)", "3)", "4)", "5)"]) and txt.find("1)") < txt.find("2)") < txt.find("3)") < txt.find("4)") < txt.find("5)")


def _contains_ellipsis(txt: str) -> bool:
    return "..." in (txt or "")


def _is_non_couvert(txt: str) -> bool:
    return "Non couvert par les extraits fournis" in (txt or "")


def _print_case(title: str, question: str, rag_trace, answer: str):
    print("\n" + "=" * 90)
    print(f"CASE: {title}")
    print(f"Q: {question}")
    print("-" * 90)
    if rag_trace:
        # top 3 seulement
        for t in rag_trace[:3]:
            print(
                f"- rank={t.get('rank')} file={t.get('file')} p={t.get('page_number')} "
                f"chunk={t.get('chunk_index')} dist={t.get('distance')} included={t.get('included')}"
            )
    else:
        print("(no rag trace)")
    print("-" * 90)
    print(answer.strip()[:1200])


def main():
    # Important : active la trace RAG pendant les tests
    os.environ["RAG_DEBUG"] = "1"

    # Questions “couvertes” (doivent produire 5 sections + pas d’ellipses)
    covered = [
        ("MANDAT_STOCK_BILAN", "Mandat en stock : comment faire le bilan des actions engagées ?"),
        ("MANDAT_STOCK_DYNAMISER", "Mandat en stock : quelles actions concrètes pour redonner du dynamisme avant de renégocier le prix ?"),
        ("EQUIPE_RELANCE", "Mandat en stock : que faire pour remobiliser l’équipe et relancer les acquéreurs ayant visité ?"),
        ("VISITE_MARKETING", "Que faire pour changer ou reprendre des photos et organiser une seconde visite marketing ?"),
        ("ACM_PRIx", "Après l’ACM, comment traiter le sujet du prix quand le bien ne se vend pas ?"),
        ("SUIVI_CONTACTS", "Quel est l’objectif d’un bon suivi vendeur et comment le structurer ?"),
        ("ENQUETE_QUALITE", "Que vérifier dans une enquête qualité vendeur ?"),
        ("DECOUVERTE_VENDEUR", "Quel est l’objectif de la découverte vendeur ?"),
    ]

    # Questions “hors-scope” (doivent répondre Non couvert…)
    out_of_scope = [
        ("COPRO_CONFLICT", "Comment gérer une copropriété conflictuelle ?"),
        ("FISCALITE", "Comment optimiser fiscalement une vente immobilière ?"),
    ]

    failures = []

    # --- tests couverts ---
    for title, q in covered:
        ans = a.repondre_faq(q)
        trace = []
        try:
            trace = a.rag.get_last_trace()  # type: ignore
        except Exception:
            pass

        _print_case(title, q, trace, ans)

        if not _has_5_sections(ans):
            failures.append((title, "format 5 sections manquant"))
        if _contains_ellipsis(ans):
            failures.append((title, "contient des ellipses '...'"))
        if _is_non_couvert(ans):
            failures.append((title, "répond Non couvert alors que couvert attendu"))

        # trace RAG attendue non vide
        if not trace:
            failures.append((title, "trace RAG vide"))

    # --- tests hors scope ---
    for title, q in out_of_scope:
        ans = a.repondre_faq(q)
        trace = []
        try:
            trace = a.rag.get_last_trace()  # type: ignore
        except Exception:
            pass

        _print_case(title, q, trace, ans)

        if not _is_non_couvert(ans):
            failures.append((title, "devrait répondre Non couvert"))

    print("\n" + "=" * 90)
    if failures:
        print("❌ FAILURES:")
        for t, why in failures:
            print(f"- {t}: {why}")
        sys.exit(1)
    else:
        print("✅ ALL SMOKE TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
