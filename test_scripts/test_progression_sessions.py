"""
test_scripts/test_progression_sessions.py — Vérification du fix de progression :
les sessions 2 à 5 sont jouables, et une reprise retombe sur la bonne session.

Le bug corrigé : session_courante était forcée à 1 (ecran_ile, ecran_carte), donc
l'enfant qui terminait la session 1 se voyait reproposer « Commencer la Session 1 ».
La règle est désormais : la session courante SE DÉRIVE des coffres gagnés
(recompenses.session_courante) — rien de nouveau n'est stocké.

Couvre :
  A. la dérivation elle-même (jeu/recompenses.py), sur la vraie base de test
  B. la reprise : un joueur à 2 coffres entre dans l'île → session 3 proposée
  C. le parcours COMPLET en AppTest, sessions 1 → 5 : chaque fin de session
     (coffre + planches BD + retour à l'île) doit proposer la session SUIVANTE
  D. la fin d'île : aucune session 6, routage vers la clé + célébration + énigme

Aucun appel à l'API Anthropic : la cible remplace ecran_session._init_engine par
une version hors-ligne, et les états de moteur sont injectés directement.
Isolé de data/philia.db (base data/_test_progression.db, recréée à chaque run).

Lancer :
    python test_scripts/test_progression_sessions.py
Sortie : code 0 si tout passe, 1 sinon.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import data_layer.db as db  # noqa: E402

_DB_TEST = ROOT / "data" / "_test_progression.db"
db._DB_PATH = _DB_TEST  # doit être posé AVANT toute connexion

from streamlit.testing.v1 import AppTest  # noqa: E402

from data_layer.joueurs import charger_joueur_courant, creer_joueur  # noqa: E402
from jeu import recompenses  # noqa: E402

CIBLE = str(ROOT / "test_scripts" / "test_progression_target.py")

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


# ── Helpers AppTest ───────────────────────────────────────────────────────────

def labels(at: AppTest) -> list[str]:
    return [b.label for b in at.button]


def texte(at: AppTest) -> str:
    return " ".join(
        [str(m.value) for m in at.markdown]
        + [str(c.value) for c in at.caption]
        + [str(t.value) for t in at.title]
        + [str(i.value) for i in at.info]
    )


def ss(at: AppTest, cle: str, defaut=None):
    """session_state.get() — AppTest n'expose pas .get() sur son session_state."""
    return at.session_state[cle] if cle in at.session_state else defaut


def clic(at: AppTest, label: str) -> AppTest:
    """Clique le bouton portant ce libellé et rejoue l'app."""
    boutons = [b for b in at.button if b.label == label]
    if not boutons:
        raise AssertionError(f"Bouton « {label} » absent — présents : {labels(at)}")
    boutons[0].click().run()
    if at.exception:
        raise AssertionError(f"Exception après clic sur « {label} » : {at.exception}")
    return at


def app_neuve() -> AppTest:
    """Une session navigateur neuve (session_state vide, base inchangée)."""
    at = AppTest.from_file(CIBLE, default_timeout=60)
    at.run()
    return at


def etat_bilan(numero_session: int) -> dict:
    """Moteur de la session demandée, positionné au bilan, prêt à être terminé."""
    import pedagogie.contenu_ile1 as contenu
    from pedagogie.session_engine import SessionEngine

    exercices = getattr(contenu, f"SESSION_{numero_session}")
    engine = SessionEngine(
        exercices=exercices,
        prenom="Léa",
        situation_narrative="test",
        ile_id="ile_1",
        planche_key=f"c{numero_session}",
    )
    engine.index_exercice = len(exercices) - 1
    engine.historique = [{"role": "assistant", "content": "Message déjà affiché."}]
    etat = engine.to_dict()
    etat["mode"] = "bilan"
    etat["nb_tours_bilan"] = 1
    return etat


def terminer_session(at: AppTest, numero: int) -> AppTest:
    """Joue la fin de session : bilan → coffre → planches BD → sortie du modal."""
    at.session_state.session_active = etat_bilan(numero)
    at.run()
    check(f"S{numero} — écran de session sans exception", not at.exception, str(at.exception))
    clic(at, "Terminer le chapitre ✓")
    check(
        f"S{numero} — coffre affiché",
        bool(ss(at, "coffre_session_a_afficher")),
        str(ss(at, "coffre_session_a_afficher")),
    )
    clic(at, "Continuer →")
    # Les chapitres ont 1 ou 2 planches BD (cf. _SEQUENCE_PLANCHES).
    while "Suite →" in labels(at):
        clic(at, "Suite →")
    clic(at, "Continuer la quête →")
    check(
        f"S{numero} — coffre C{numero} gagné en base",
        recompenses.a_obtenu_cristal("ile_1", f"C{numero}"),
        str(recompenses.cristaux_obtenus()),
    )
    return at


def retour_a_l_ile(at: AppTest) -> AppTest:
    """« Retour à l'île » puis traversée arrivée → présentation."""
    clic(at, "← Retour à l'île")
    check("retour à l'île → écran île", ss(at, "ecran_courant") == "ile", str(ss(at, "ecran_courant")))
    clic(at, "Continuer →")  # arrivée → présentation
    return at


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_derivation() -> None:
    print("\n=== A. Dérivation de la session courante depuis les coffres ===")
    recompenses.reset_recompenses()
    check("concepts de l'Île 1 dans l'ordre",
          recompenses.concepts_ile("ile_1") == ["C1", "C2", "C3", "C4", "C5"],
          str(recompenses.concepts_ile("ile_1")))
    check("aucun coffre → session 1", recompenses.session_courante("ile_1") == 1)
    check("aucun coffre → île non terminée", not recompenses.ile_terminee("ile_1"))

    recompenses.gagner_cristal("ile_1", "C1")
    check("1 coffre → session 2", recompenses.session_courante("ile_1") == 2)
    recompenses.gagner_cristal("ile_1", "C2")
    check("2 coffres → session 3", recompenses.session_courante("ile_1") == 3)

    for concept in ("C3", "C4", "C5"):
        recompenses.gagner_cristal("ile_1", concept)
    check("5 coffres → plus de session (None)", recompenses.session_courante("ile_1") is None)
    check("5 coffres → île terminée", recompenses.ile_terminee("ile_1"))
    check("une autre île reste à sa session 1", recompenses.session_courante("ile_2") == 1)
    check("île hors catalogue → 5 sessions par défaut",
          recompenses.concepts_ile("ile_6") == ["C1", "C2", "C3", "C4", "C5"])


def test_reprise() -> None:
    print("\n=== B. Reprise : 2 coffres déjà gagnés → session 3 proposée ===")
    recompenses.reset_recompenses()
    recompenses.gagner_cristal("ile_1", "C1")
    recompenses.gagner_cristal("ile_1", "C2")

    at = app_neuve()
    check("entrée dans l'île sans exception", not at.exception, str(at.exception))
    clic(at, "Continuer →")  # arrivée → présentation
    labs = labels(at)
    check("bouton « Continuer — Session 3 »", "Continuer — Session 3" in labs, str(labs))
    check("plus de « Commencer la Session 1 »", "Commencer la Session 1" not in labs, str(labs))

    clic(at, "Continuer — Session 3")
    check("l'accueil d'île ne se rejoue pas", ss(at, "ecran_courant") == "session",
          f"ecran={ss(at, 'ecran_courant')} etape={ss(at, 'etape_ile')}")
    check("session_courante = 3", ss(at, "session_courante") == 3, str(ss(at, "session_courante")))

    from pedagogie.contenu_ile1 import META_SESSION_3

    check("le contenu joué est celui de la session 3",
          META_SESSION_3["titre"] in texte(at), texte(at)[:200])


def test_parcours_complet() -> None:
    print("\n=== C. Parcours complet : sessions 1 → 5 enchaînées ===")
    recompenses.reset_recompenses()
    at = app_neuve()
    clic(at, "Continuer →")  # arrivée → présentation
    check("première entrée → « Commencer la Session 1 »",
          "Commencer la Session 1" in labels(at), str(labels(at)))

    clic(at, "Commencer la Session 1")
    check("l'accueil d'île s'intercale à la toute première entrée",
          ss(at, "etape_ile") == "accueil", str(ss(at, "etape_ile")))
    clic(at, "Commencer l'aventure →")
    check("session 1 lancée", ss(at, "session_courante") == 1, str(ss(at, "session_courante")))

    import pedagogie.contenu_ile1 as contenu

    for numero in range(1, 5):
        terminer_session(at, numero)
        suivante = numero + 1
        check(
            f"S{numero} terminée → session {suivante} armée",
            ss(at, "session_courante") == suivante,
            str(ss(at, "session_courante")),
        )
        retour_a_l_ile(at)
        labs = labels(at)
        check(
            f"retour à l'île après S{numero} → « Continuer — Session {suivante} »",
            f"Continuer — Session {suivante}" in labs,
            str(labs),
        )
        check(
            f"retour à l'île après S{numero} → plus de « Commencer la Session 1 »",
            "Commencer la Session 1" not in labs,
            str(labs),
        )
        clic(at, f"Continuer — Session {suivante}")
        meta = getattr(contenu, f"META_SESSION_{suivante}")
        check(
            f"la session {suivante} est bien celle qui se joue",
            meta["titre"] in texte(at),
            texte(at)[:200],
        )

    print("\n=== D. Fin d'île : pas de session 6 ===")
    terminer_session(at, 5)
    check("clé de l'île obtenue", recompenses.a_obtenu_cle("ile_1"))
    check("célébration forte de fin d'île armée",
          bool(ss(at, "celebration_fin_ile_a_afficher")),
          str(ss(at, "celebration_fin_ile_a_afficher")))
    labs = labels(at)
    check("l'énigme finale est proposée",
          "Archimède veut te confier quelque chose…" in labs, str(labs))
    check("aucun bouton de session ne subsiste",
          not any(lab.startswith(("Commencer la Session", "Continuer — Session")) for lab in labs),
          str(labs))

    clic(at, "Retour à l'archipel →")
    check("retour à la carte", ss(at, "ecran_courant") == "carte", str(ss(at, "ecran_courant")))

    # Retour sur une île terminée : jamais de session 6, la fin d'île est rejouable.
    at.session_state.ecran_courant = "ile"
    at.run()
    check("retour sur l'île terminée sans exception", not at.exception, str(at.exception))
    clic(at, "Continuer →")  # arrivée → présentation
    labs = labels(at)
    check("île terminée → « La clé de l'île t'attend → »",
          "La clé de l'île t'attend →" in labs, str(labs))
    check("île terminée → aucun bouton de session",
          not any(lab.startswith(("Commencer la Session", "Continuer — Session")) for lab in labs),
          str(labs))
    clic(at, "La clé de l'île t'attend →")
    check("routage vers la fin d'île", ss(at, "ecran_courant") == "session"
          and bool(ss(at, "celebration_fin_ile_a_afficher")),
          f"ecran={ss(at, 'ecran_courant')} flag={ss(at, 'celebration_fin_ile_a_afficher')}")


def main() -> int:
    if _DB_TEST.exists():
        _DB_TEST.unlink()  # état déterministe : base recréée à chaque run
    if charger_joueur_courant() is None:
        creer_joueur(genre="fille", avatar_prenom="sassou", role="eleve", prenom="Léa")

    try:
        test_derivation()
        test_reprise()
        test_parcours_complet()
    except AssertionError as exc:
        check("parcours interrompu", False, str(exc))

    print()
    if _echecs:
        print(f"❌ {len(_echecs)} ÉCHEC(S) sur {_total} vérifications : {_echecs}")
        return 1
    print(f"✅ {_total}/{_total} vérifications passées")
    return 0


if __name__ == "__main__":
    sys.exit(main())
