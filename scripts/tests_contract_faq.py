import os
# scripts/tests_contract_faq.py
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
    
import agent_formateur as a


CASES = [
    # --- Couvert (doit produire 5 sections) ---
    ("COVER_MANDAT_STOCK_BILAN", "Mandat en stock : comment faire le bilan des actions engagées ?", True),
    ("COVER_MANDAT_DYNAMISER", "Mandat en stock : quelles actions concrètes pour redonner du dynamisme avant de renégocier le prix ?", True),
    ("COVER_EQUIPE_RELANCE", "Mandat en stock : que faire pour remobiliser l’équipe et relancer les acquéreurs ayant visité ?", True),
    ("COVER_DECOUVERTE", "Quel est l’objectif de la découverte vendeur ?", True),
    ("COVER_ENQUETE_QUALITE", "Que vérifier dans une enquête qualité vendeur ?", True),

    # --- Hors-scope (doit répondre Non couvert) ---
    ("OOS_COPRO_CONFLICT", "Comment gérer une copropriété conflictuelle ?", False),
    ("OOS_FISCALITE", "Comment optimiser fiscalement une vente immobilière ?", False),
]


_ALLOWED_VERBS_5 = (
    "Faire", "Utiliser", "Planifier", "Confirmer", "Préparer", "S'assurer", "S'assurer",
    "Changer", "Relancer", "Re mobiliser", "Remobiliser", "Proposer", "Organiser",
    "Analyser", "Évaluer", "Evaluer", "Vérifier", "Verifier", "Créer", "Creer",
    "Identifier", "Présenter", "Presenter", "Discuter", "Noter", "Saisir",
    "Renseigner", "Bloquer", "Sensibiliser", "Mettre",
    "Réaliser", "Realiser", "Récupérer", "Recuperer",
)


def _norm_spaces(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _is_non_couvert(resp: str) -> bool:
    r = (resp or "").strip().lower()
    r = re.sub(r"[*_`>\"]", "", r)          # retire un peu de markdown
    r = _norm_spaces(r)
    return r == "non couvert par les extraits fournis."


def _extract_sections(resp: str) -> dict[int, str]:
    """
    Parse sections 1) ... 5) (avec retours à la ligne),
    renvoie {1: body, ...}
    """
    text = resp or ""
    pat = re.compile(r"(?m)^\s*([1-5])\)\s+")
    matches = list(pat.finditer(text))
    if not matches:
        return {}

    sections: dict[int, str] = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections[num] = body

    return sections


def _assert_contract(resp: str, covered: bool) -> list[str]:
    errors: list[str] = []
    if not resp or not resp.strip():
        return ["Réponse vide."]

    if "..." in resp:
        errors.append("Contient des ellipses '...' (interdit).")

    if covered:
        if _is_non_couvert(resp):
            errors.append("Réponse = Non couvert alors que le cas est censé être couvert.")
            return errors

        sections = _extract_sections(resp)
        nums = sorted(sections.keys())
        if nums != [1, 2, 3, 4, 5]:
            errors.append(f"Sections invalides: trouvées {nums}, attendu [1,2,3,4,5].")
            return errors

        # section bodies non vides
        for n in range(1, 6):
            if not sections.get(n):
                errors.append(f"Section {n}) vide.")

        # checklist (2) : au moins 3 puces
        s2 = sections.get(2, "")
        bullets = [ln.strip() for ln in s2.splitlines() if ln.strip().startswith("-")]
        if len(bullets) < 3:
            errors.append(f"Checklist 2) trop courte: {len(bullets)} puce(s), attendu >= 3.")

        # section 5 : une seule action (une seule ligne non vide)
        s5 = sections.get(5, "")
        lines = [ln.strip() for ln in s5.splitlines() if ln.strip()]
        if len(lines) != 1:
            errors.append(f"Section 5) doit contenir 1 seule ligne d’action, trouvé {len(lines)} ligne(s).")
        else:
            action = lines[0]
            if not any(action.startswith(v) for v in _ALLOWED_VERBS_5):
                errors.append(f"Section 5) ne commence pas par un verbe autorisé: '{action}'.")

    else:
        # hors-scope = doit être exactement Non couvert...
        if not _is_non_couvert(resp):
            errors.append("Hors-scope: réponse attendue = 'Non couvert par les extraits fournis.'")

    return errors


def main() -> int:
    failures = []

    for name, q, covered in CASES:
        print("\n" + "=" * 90)
        print(f"CASE: {name}")
        print(f"Q: {q}")
        resp = a.repondre_faq(q)
        print("-" * 90)
        print(resp)

        errs = _assert_contract(resp, covered=covered)
        if errs:
            failures.append((name, errs))

    print("\n" + "=" * 90)
    if failures:
        print("❌ FAILURES:")
        for name, errs in failures:
            for e in errs:
                print(f"- {name}: {e}")
        return 1

    print("✅ ALL CONTRACT FAQ TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

