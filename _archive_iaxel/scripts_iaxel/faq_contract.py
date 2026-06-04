# core/faq_contract.py
"""
FAQ Contract Helpers — anti-hallucination gate + format 5 sections strict.

Constants et fonctions extraits depuis agent_formateur.py.
"""
from __future__ import annotations

import re
import unicodedata

# -------------------------------------------------------------------
# CONSTANTS
# -------------------------------------------------------------------

_FAQ_WORD_RE = re.compile(r"[a-z0-9àâçéèêëîïôûùüÿñæœ]+", re.IGNORECASE)

_FAQ_STOPWORDS = {
    "le","la","les","un","une","des","du","de","d","dans","sur","pour","par","avec","sans","et","ou",
    "a","au","aux","en","ce","cet","cette","ces","se","sa","son","ses","leur","leurs","nous","vous",
    "il","elle","ils","elles","on","que","qui","quoi","dont","où","est","sont","été","être",
    "comment","quoi","quel","quelle","quels","quelles","faire","faut","dois","doit",
}

# Mots trop génériques "immobilier": ne doivent PAS suffire à valider la couverture
_FAQ_GENERIC_DOMAIN = {
    "immobilier","immobiliere","immobiliers","immobilieres",
    "vente","vendre","vendeur","vendeurs","acquereur","acquereurs","client","clients",
    "agence","agent","agents","conseiller","conseillers",
    "prix","bien","biens","service","services",
    "gerer","gere","gestion","optimiser","optimisation",
    "organisation","actions","action","etape","etapes",
}

# Acronymes courts acceptés comme "forts"
_FAQ_STRONG_SHORT = {"acm", "mpm", "ttm", "ocp"}

NON_COUVERT = "Non couvert par les extraits fournis."


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def faq_norm(s: str) -> str:
    """Normalise une chaîne: minuscule + suppression accents."""
    s = (s or "").lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def faq_tokens(question: str) -> list[str]:
    """Tokenize une question en mots significatifs (stopwords exclus)."""
    q = faq_norm(question)
    toks = [t for t in _FAQ_WORD_RE.findall(q) if t and t not in _FAQ_STOPWORDS]
    # dédoublonne en gardant l'ordre
    seen: set[str] = set()
    out: list[str] = []
    for t in toks:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out


def faq_strong_keywords(question: str) -> list[str]:
    """
    Mots-clés "forts" = suffisamment spécifiques pour valider la couverture :
    - longueur >= 6, ou acronyme autorisé (acm/mpm/ttm/ocp)
    - et pas dans la liste générique immobilier
    """
    toks = faq_tokens(question)
    strong: list[str] = []
    for t in toks:
        if t in _FAQ_STRONG_SHORT:
            strong.append(t)
        elif len(t) >= 6:
            strong.append(t)

    strong = [t for t in strong if t not in _FAQ_GENERIC_DOMAIN]
    # dédoublonne
    seen: set[str] = set()
    out: list[str] = []
    for t in strong:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out


def faq_is_covered_by_context(question: str, contexte: str) -> bool:
    """
    Gate anti-hallucination + hors-scope contract.
    - Hors-scope volontaire: copropriété, fiscalité => Non couvert (même si RAG trouve des trucs).
    - Sinon: au moins 1 mot-clé "fort" de la question doit apparaître dans les extraits.
    """
    qn = faq_norm(question)
    ctx = faq_norm(contexte)

    # --- Hors-scope contract ---
    if "copropriete" in qn or "coprop" in qn:
        return False
    if "fiscal" in qn:
        return False

    strong = faq_strong_keywords(question)
    if not strong:
        return False

    return any(k in ctx for k in strong)


def faq_has_5_sections(txt: str) -> bool:
    """
    Vérifie qu'on a bien 1) ... 5) (dans l'ordre).
    On ne force pas les titres ici, juste la présence des sections.
    """
    if not txt:
        return False
    t = txt.strip()
    # Hors-scope = pas de sections attendues
    if t == NON_COUVERT:
        return True

    # Doit contenir 1)2)3)4)5) dans l'ordre
    pos: list[int] = []
    for n in ("1)", "2)", "3)", "4)", "5)"):
        i = t.find(n)
        if i == -1:
            return False
        pos.append(i)
    return pos == sorted(pos)


def faq_force_section5_one_line(txt: str) -> str:
    """
    Force: 5) <action> sur UNE SEULE ligne (contract test).
    - Si le modèle a fait:
      5) Prochaine étape
      Action...
      => on merge
    - Si le modèle a mis plusieurs lignes en section 5 => on garde la 1ère action seulement.
    """
    if not txt:
        return txt
    t = txt.strip()
    if t == NON_COUVERT:
        return t

    lines = t.splitlines()
    # trouve la ligne qui commence par 5)
    idx5: int | None = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("5)"):
            idx5 = i
            break
    if idx5 is None:
        return t

    header = lines[idx5].strip()

    # action sur la même ligne ?
    action = ""
    if ":" in header:
        left, right = header.split(":", 1)
        # normalise "5) Prochaine étape"
        header_left = left.strip()
        action = right.strip()
        header = header_left
    else:
        # action = première ligne non vide après la ligne 5)
        for j in range(idx5 + 1, len(lines)):
            cand = lines[j].strip()
            if cand:
                action = cand.lstrip("-").strip()
                break

    if not action:
        # si on n'a pas d'action, on laisse tel quel (le guard déclenchera un repair)
        return t

    # --- Nettoyage de l'action ---
    # 1) Ne garder que la première ligne
    action = action.split("\n")[0].strip()
    # 2) Supprimer le préfixe "Prochaine étape :" si présent (avec variantes d'espaces)
    action = re.sub(r"^Prochaine\s+[éeÉE]tape\s*:\s*", "", action, flags=re.IGNORECASE).strip()
    # 3) Supprimer puce ou guillemets résiduels
    action = re.sub(r"^[\-\•\*]\s*", "", action).strip()
    action = action.strip("\"'").strip()

    if not action:
        return t

    # Reconstruit le texte :
    # - Tout AVANT la section 5
    # - "5) <action>" (l'action commence par un verbe, une seule ligne)
    before = lines[:idx5]
    before = [ln.rstrip() for ln in before]
    action_line = action.rstrip().rstrip(".") + "."
    out = "\n".join([ln for ln in before if ln is not None]).rstrip()
    if out:
        out += "\n"
    out += "5) " + action_line
    return out.strip()


def faq_section5_is_single_line(txt: str) -> bool:
    """
    Contract: la section 5 doit être :
      5) <action qui commence par un verbe>
    Une seule ligne, pas de "Prochaine étape".
    """
    if not txt:
        return False
    t = txt.strip()
    if t == NON_COUVERT:
        return True
    # Cherche "5) " suivi de l'action sur la même ligne, et rien après
    m = re.search(r"(^|\n)5\)\s+(.+)$", t)
    if not m:
        return False
    # Vérifier qu'il n'y a pas de contenu après cette ligne
    after = t[m.end():].strip()
    return after == ""
