"""
test_scripts/test_collection_compteur_coffre.py — Suite de vérification du
système de collection (spec collection + tableau de bord, commit 2).

Couvre, en pilotant le VRAI render_session() via AppTest (streamlit.testing.v1) :
  A. anti-rejeu du toast de célébration légère (D-T8.6-G) — non-régression
  B. compteur d'objets en cours de session + repère « Exercice N / total »
  C. bilan : dernier objet encaissé, repère « Bilan »
  D. gating du bouton « Terminer le chapitre » (D-T8.1-F / D24) et masquage
     du « Retour à l'île » en bilan
  E. fin de session : coffre nommé du concept, puis enchaînement planche BD
  F. toast « +1 objet » : consommation immédiate, pas de rejeu
  G. imports des écrans non touchés par le commit 2 (dont l'énigme)

Aucun appel à l'API Anthropic : le moteur est injecté déjà initialisé dans
session_state, jamais construit via _init_engine(). Isolé de data/philia.db —
la cible test_celebration_legere_anti_rejeu.py bascule sur une base de test.

Lancer :
    python test_scripts/test_collection_compteur_coffre.py
Sortie : code 0 si tout passe, 1 sinon.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402

# Cible AppTest réutilisée : elle isole la base de données et injecte un moteur
# déjà initialisé. On la pilote en pré-remplissant session_state avant .run().
CIBLE = str(ROOT / "test_scripts" / "test_celebration_legere_anti_rejeu.py")

_echecs: list[str] = []
_total = 0


def check(nom: str, cond: bool, detail: str = "") -> None:
    """Enregistre une vérification. `detail` n'est affiché qu'en cas d'échec."""
    global _total
    _total += 1
    if cond:
        print(f"  OK    {nom}")
    else:
        print(f"  ÉCHEC {nom}" + (f" — {detail}" if detail else ""))
        _echecs.append(nom)


def etat_moteur(index: int, mode: str, tours_bilan: int = 0, phase: str = "en_cours") -> dict:
    """État sérialisé d'un SessionEngine positionné où on veut dans la session."""
    from pedagogie.contenu_ile1 import SESSION_1
    from pedagogie.session_engine import SessionEngine

    engine = SessionEngine(
        exercices=SESSION_1,
        prenom="Léa",
        situation_narrative="test",
        ile_id="ile_1",
        planche_key="c1",
    )
    engine.index_exercice = index
    engine.historique = [{"role": "assistant", "content": "Message déjà affiché."}]
    etat = engine.to_dict()
    etat["mode"] = mode
    etat["phase"] = phase
    etat["nb_tours_bilan"] = tours_bilan
    return etat


def app(**session_state) -> AppTest:
    """Instancie la cible avec un session_state pré-rempli, et la joue."""
    at = AppTest.from_file(CIBLE, default_timeout=30)
    for cle, valeur in session_state.items():
        at.session_state[cle] = valeur
    at.run()
    return at


def texte(at: AppTest) -> str:
    """Tout le texte rendu (markdown + captions), concaténé."""
    return " ".join(
        [str(m.value) for m in at.markdown] + [str(c.value) for c in at.caption]
    )


def ss(at: AppTest, cle: str, defaut=None):
    """session_state.get() — AppTest n'expose pas .get() sur son session_state."""
    return at.session_state[cle] if cle in at.session_state else defaut


def main() -> int:
    from pedagogie.contenu_ile1 import SESSION_1

    total_exercices = len(SESSION_1)

    print("\n=== A. Anti-rejeu du toast de célébration légère (D-T8.6-G) ===")
    at = app()
    check("1er run sans exception", not at.exception, str(at.exception))
    at.run()
    check("2e run sans exception (pas de rejeu)", not at.exception, str(at.exception))

    print("\n=== B. Compteur d'objets en cours de session ===")
    # Règle de gain (option b) : l'objet est encaissé au PASSAGE à l'exercice
    # suivant. Pendant l'exercice N (1-based), le compteur vaut donc N-1.
    for index, attendu in ((0, "0 pierre"), (1, "1 pierre"), (3, "3 pierres")):
        at = app(session_active=etat_moteur(index, "decouverte"))
        corps = texte(at)
        check(f"exercice {index + 1} → « {attendu} »", attendu in corps, corps[:200])
        check(
            f"exercice {index + 1} → repère « Exercice {index + 1} / {total_exercices} »",
            f"Exercice {index + 1} / {total_exercices}" in corps,
            corps[:200],
        )
        check(f"exercice {index + 1} sans exception", not at.exception, str(at.exception))

    print("\n=== C. Bilan : dernier objet encaissé + repère « Bilan » ===")
    at = app(session_active=etat_moteur(total_exercices - 1, "bilan", tours_bilan=1))
    corps = texte(at)
    check("repère « Bilan » (pas un numéro d'exercice)", "· Bilan" in corps, corps[:200])
    check(
        f"compteur au total ({total_exercices} pierres)",
        f"{total_exercices} pierres" in corps,
        corps[:200],
    )
    check("pas d'exception", not at.exception, str(at.exception))

    print("\n=== D. Gating du bouton « Terminer le chapitre » (D-T8.1-F / D24) ===")
    at = app(session_active=etat_moteur(total_exercices - 1, "bilan", tours_bilan=0))
    labels = [b.label for b in at.button]
    check("bouton absent tant que nb_tours_bilan == 0", "Terminer le chapitre ✓" not in labels, str(labels))
    check("« Retour à l'île » masqué en bilan", "← Retour à l'île" not in labels, str(labels))

    at = app(session_active=etat_moteur(total_exercices - 1, "bilan", tours_bilan=1))
    labels = [b.label for b in at.button]
    check("bouton présent après 1 tour de bilan", "Terminer le chapitre ✓" in labels, str(labels))

    print("\n=== E. Fin de session : coffre puis planche BD ===")
    bouton = [b for b in at.button if b.label == "Terminer le chapitre ✓"][0]
    bouton.click().run()
    check("pas d'exception au clic", not at.exception, str(at.exception))
    check(
        "nom du coffre = concept sans son préfixe « Cn — »",
        ss(at, "coffre_session_a_afficher") == "Sens d'une fraction",
        str(ss(at, "coffre_session_a_afficher")),
    )
    check(
        "tally des objets rangés dans le coffre",
        ss(at, "coffre_session_tally") == f"{total_exercices} pierres",
        str(ss(at, "coffre_session_tally")),
    )
    check("flux planche BD toujours armé", ss(at, "planche_bd_a_afficher") == "c1",
          str(ss(at, "planche_bd_a_afficher")))
    check("planche_bd_index resetté (D-T8.1-C)", ss(at, "planche_bd_index") == 0,
          str(ss(at, "planche_bd_index")))

    corps = texte(at)
    check("phrase du coffre affichée", "ce coffre est à toi" in corps, corps[:200])
    # Le nom passe par html.escape() : l'apostrophe devient &#x27; dans l'overlay.
    check("nom du coffre en overlay sur l'image", "Sens d&#x27;une fraction" in corps)
    labels = [b.label for b in at.button]
    check("bouton « Continuer → » présent", "Continuer →" in labels, str(labels))

    [b for b in at.button if b.label == "Continuer →"][0].click().run()
    check("flag coffre effacé", not ss(at, "coffre_session_a_afficher"))
    check("la planche BD prend le relais", ss(at, "planche_bd_a_afficher") == "c1")
    check("pas d'exception après « Continuer »", not at.exception, str(at.exception))

    print("\n=== F. Toast d'objet gagné : consommé une seule fois (D-T8.6-G) ===")
    at = app(objet_gagne_a_afficher="pierre")
    check("toast sans exception", not at.exception, str(at.exception))
    check("flag consommé au render", ss(at, "objet_gagne_a_afficher") is None,
          str(ss(at, "objet_gagne_a_afficher")))
    at.run()
    check("pas de rejeu au rerun suivant", ss(at, "objet_gagne_a_afficher") is None)

    print("\n=== G. Imports des écrans non touchés ===")
    for module in (
        "ui.ecran_enigme",
        "ui.ecran_carte",
        "ui.ecran_ile",
        "ui.modal_planche_bd",
        "ui.carte_fragment",
        "ui.celebrations",
        "pedagogie.enigme_engine",
    ):
        try:
            __import__(module)
            check(f"import {module}", True)
        except Exception as exc:  # noqa: BLE001
            check(f"import {module}", False, repr(exc))

    print()
    if _echecs:
        print(f"❌ {len(_echecs)} ÉCHEC(S) sur {_total} vérifications : {_echecs}")
        return 1
    print(f"✅ {_total}/{_total} vérifications passées")
    return 0


if __name__ == "__main__":
    sys.exit(main())
