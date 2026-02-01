from __future__ import annotations

import sys
import py_compile
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))

    print("🩺 Doctor — root:", root)

    target = root / "agent_formateur.py"
    print("✅ Compilation", target.name)
    py_compile.compile(str(target), doraise=True)
    print("✅ Compilation OK")

    print("✅ Import agent_formateur…")
    import agent_formateur as a  # noqa
    print("✅ Import OK")
    # ------------------------------------------------------------
    # Check: audit_only_guard (doit couper toute "version corrigée")
    # ------------------------------------------------------------
    print("🔎 Check: audit_only_guard…")

    fake_out = """
Bruit avant header (doit être ignoré)

### 🔍 AUDIT CHARTE V2

**Enjeu terrain :**
- Conforme
- Commentaire : OK

### 🛠️ VERSION CORRIGÉE (conforme CHARTE V2)
Ceci ne doit jamais apparaître après guard.
""".strip()

    guarded = a.audit_only_guard(fake_out)

    assert guarded.startswith("### 🔍 AUDIT CHARTE V2"), "Guard: le header audit n'est pas en tête"
    assert "VERSION CORRIG" not in guarded.upper(), "Guard: 'VERSION CORRIG' n'a pas été coupé"
    assert "ne doit jamais apparaître" not in guarded.lower(), "Guard: le texte après marker n'a pas été coupé"

    print("✅ audit_only_guard OK (coupe 'version corrigée' + recentre sur header)")

    # --- Sanity checks rapides ---
    print("🔎 Check: AUDIT prompt chargé…")
        # ------------------------------------------------------------
    # Check: prompt audit V2 (anti-confusion + pas de version corrigée)
    # ------------------------------------------------------------
    print("🔎 Check: AUDIT prompt contenu…")
    up = a.AUDIT_PROMPT_V2.upper()

    assert "NE CONFONDS JAMAIS" in up, "Prompt: anti-confusion manquant"
    assert "CE QUI MANQUE DANS LA BASE DOCUMENTAIRE" in up, "Prompt: section base documentaire manquante"
    assert "NON COUVERT PAR LES EXTRAITS FOURNIS" in up, "Prompt: mention 'Non couvert…' manquante"

    # Interdits: le prompt ne doit pas demander de correction
       # Interdits: le prompt ne doit pas DEMANDER une correction.
    # (On autorise qu'il mentionne "version corrigée" uniquement pour l'interdire.)
    forbidden_requests = [
        "### 🛠️",  # section typique de correction
        "PROPOSER UNE VERSION CORRIG",
        "VERSION CORRIGÉE (CONFORME",
        "VERSION CORRIGE (CONFORME",
        "RÉÉCRIS LA RÉPONSE",
        "REECRIS LA REPONSE",
        "AMÉLIORE LA RÉPONSE",
        "AMELIORE LA REPONSE",
    ]
    for bm in forbidden_requests:
        assert bm not in up, f"Prompt: demande une correction ({bm})"

    # On vérifie qu'on a bien un garde-fou explicite côté prompt
    assert "NE PRODUIS JAMAIS" in up, "Prompt: garde-fou 'Ne produis jamais…' manquant"

    assert "RÉÉCRIS" not in up and "REECRIS" not in up, "Prompt: demande une réécriture (interdit)"

    print("✅ Prompt audit OK (anti-confusion + pas de correction)")

    assert hasattr(a, "AUDIT_PROMPT_V2") and isinstance(a.AUDIT_PROMPT_V2, str)
    print("   len =", len(a.AUDIT_PROMPT_V2))

    # Petit warning utile si ton prompt contient des commandes shell collées par erreur
    if a.AUDIT_PROMPT_V2.lstrip().lower().startswith("cat "):
        print("⚠️ AUDIT_PROMPT_V2 commence par 'cat …' → ton prompts/prompt_audit_v2.txt contient probablement une commande shell.")
    assert len(a.AUDIT_PROMPT_V2) > 500

    print("🔎 Check: RAG build_context…")
    ctx = a.construire_contexte("Découverte vendeur", k=2)
    assert isinstance(ctx, str) and len(ctx) > 50
    print("✅ RAG OK (ctx len =", len(ctx), ")")

    print("🔎 Check: brand_block…")
    s = a.brand_block("Century 21 / CenturyNet / C21 / century")
    assert "century" not in s.lower()
    print("✅ brand_block OK ->", s)

    print("\n✅ Doctor OK")


if __name__ == "__main__":
    main()
