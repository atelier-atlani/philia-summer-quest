"""test_scripts/test_reprise.py — L'accueil de reprise : « Ah, te voilà ! »

Ce qui est gardé ici, c'est l'AIGUILLAGE à l'arrivée d'un enfant qui rouvre son
lien — la partie du code la plus facile à casser sans s'en apercevoir, parce
qu'elle dépend de trois choses à la fois : la progression dérivée des coffres,
les defaults de app.py, et les paramètres d'URL.

  1. partie à peine créée (session 1, aucun coffre) → flux normal, pas de reprise
  2. partie entamée → accueil nommé, « Reprendre » mène à LA BONNE session
  3. île terminée → variante félicitations, qui rejoint le flux de fin d'île
     (jamais une session 6 inexistante)
  4. clic d'île (?ile=) → la reprise ne doit PAS intercepter, sinon l'enfant
     n'entre jamais dans l'île
  5. pas de boucle : après « Reprendre », le rerun ne ramène pas sur la reprise
  6. isolation : la partie d'une famille n'apparaît pas chez l'autre

Aucun appel réseau : l'écran de session est remplacé par un double (voir
_neutraliser_ecran_session) — ce test porte sur le routage, pas sur la session.
Isolé de data/philia.db (base data/_test_reprise.db, recréée à chaque run).

Lancer :
    python test_scripts/test_reprise.py
Sortie : code 0 si tout passe, 1 sinon.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import data_layer.db as db  # noqa: E402

_DB = ROOT / "data" / "_test_reprise.db"
db._DB_PATH = _DB  # jamais data/philia.db

import streamlit as st  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from data_layer.joueurs import (  # noqa: E402
    charger_joueur,
    creer_joueur_pour,
    ecrire_cristaux_obtenus,
)

APP = str(ROOT / "app.py")
_echecs: list[str] = []
_total = 0


def check(nom: str, cond: bool, detail: str = "") -> None:
    global _total
    _total += 1
    if cond:
        print(f"  OK    {nom}")
    else:
        print(f"  ÉCHEC {nom}" + (f" — {detail}" if detail else ""))
        _echecs.append(nom)


def _neutraliser_ecran_session() -> None:
    """Remplace l'écran de session par un double inerte.

    « Reprendre l'aventure » route vers la session : la rendre pour de vrai
    déclencherait le moteur pédagogique, donc des appels réseau. Ce qui se
    vérifie ici est l'aiguillage — où l'enfant atterrit, et sur quelle session.
    app.py importe l'écran à l'intérieur de sa branche de routage : remplacer
    l'attribut du module suffit, il est relu à chaque run.
    """
    import ui.ecran_session as ecran_session

    ecran_session.render_session = lambda: st.markdown("SESSION (double de test)")


def lancer(partie_id: str, **etat):
    """Ouvre l'app comme un navigateur neuf porteur du lien de cette partie."""
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["acces_deverrouille"] = True  # le portail n'est pas l'objet ici
    at.query_params["partie"] = partie_id
    for cle, val in etat.items():
        if cle == "_url":
            for k, v in val.items():
                at.query_params[k] = v
        else:
            at.session_state[cle] = val
    at.run()
    if at.exception:
        raise AssertionError(f"Exception au lancement : {at.exception}")
    return at


def texte(at) -> str:
    return " ".join([str(m.value) for m in at.markdown] + [str(c.value) for c in at.caption])


def labels(at) -> list[str]:
    return [b.label for b in at.button]


def clic(at, motif: str):
    boutons = [b for b in at.button if motif in b.label]
    if not boutons:
        raise AssertionError(f"Bouton « {motif} » absent — présents : {labels(at)}")
    boutons[0].click().run()
    if at.exception:
        raise AssertionError(f"Exception après « {motif} » : {at.exception}")
    return at


def creer(partie_id: str, prenom: str, genre: str = "fille", cristaux: list[str] | None = None):
    creer_joueur_pour(
        partie_id,
        genre=genre,
        avatar_prenom="melian" if genre == "fille" else "sassou",
        role="architecte" if genre == "fille" else "aventurier",
        prenom=prenom,
    )
    if cristaux:
        ecrire_cristaux_obtenus(
            charger_joueur(partie_id)["id"],
            {"ile_1": {c: "2026-08-09T10:00:00Z" for c in cristaux}},
        )


# ── Les parties de référence ──────────────────────────────────────────────────

NEUVE = "repriseneuve00001"     # session 1, aucun coffre
ENTAMEE = "repriseentamee001"   # C1 et C2 gagnés → session 3
FINIE = "reprisefinie00001"     # les cinq cristaux → plus de session


def test_partie_neuve() -> None:
    print("\n=== 1. Partie à peine créée : rien ne change ===")
    at = lancer(NEUVE)
    check("pas d'écran de reprise", at.session_state["ecran_courant"] == "carte",
          str(at.session_state["ecran_courant"]))
    check("Archimède ne dit pas « te voilà »", "te voilà" not in texte(at))


def test_partie_entamee() -> None:
    print("\n=== 2. Partie entamée : accueil et reprise directe ===")
    at = lancer(ENTAMEE)
    check("écran de reprise", at.session_state["ecran_courant"] == "reprise",
          str(at.session_state["ecran_courant"]))
    check("accueil nommé", "Ah, te voilà, Malo !" in texte(at), texte(at)[:160])
    check("propose de reprendre où il s'était arrêté",
          "là où tu t'étais arrêté" in texte(at), texte(at)[:200])
    check("situe la progression", "troisième étape" in texte(at), texte(at)[:300])
    check("les deux boutons attendus",
          any("Reprendre" in lab for lab in labels(at))
          and any("Revoir la carte" in lab for lab in labels(at)), str(labels(at)))

    apres = clic(lancer(ENTAMEE), "Reprendre l'aventure")
    check("« Reprendre » mène à la session", apres.session_state["ecran_courant"] == "session",
          str(apres.session_state["ecran_courant"]))
    check("et à LA BONNE session (3, dérivée des coffres)",
          apres.session_state["session_courante"] == 3,
          str(apres.session_state["session_courante"]))

    print("     → pas de boucle")
    apres.run()
    check("le rerun ne ramène pas sur la reprise",
          apres.session_state["ecran_courant"] == "session",
          str(apres.session_state["ecran_courant"]))

    print("     → un moteur périmé ne doit pas être repris")
    perime = lancer(ENTAMEE, session_courante=1, session_active="MOTEUR_PERIME")
    perime = clic(perime, "Reprendre l'aventure")
    check("moteur périmé jeté", perime.session_state["session_active"] != "MOTEUR_PERIME",
          str(perime.session_state["session_active"])[:60])

    carte = clic(lancer(ENTAMEE), "Revoir la carte")
    check("« Revoir la carte » mène à la carte", carte.session_state["ecran_courant"] == "carte",
          str(carte.session_state["ecran_courant"]))


def test_ile_terminee() -> None:
    print("\n=== 3. Île terminée : félicitations, pas de session fantôme ===")
    at = lancer(FINIE)
    check("écran de reprise, variante fin", at.session_state["ecran_courant"] == "reprise",
          str(at.session_state["ecran_courant"]))
    check("félicite au lieu de proposer une session", "jusqu'au bout" in texte(at), texte(at)[:250])
    check("aucun bouton « Reprendre l'aventure »",
          not any("Reprendre l'aventure" in lab for lab in labels(at)), str(labels(at)))
    check("propose la clé de l'île", any("clé de l'île" in lab for lab in labels(at)),
          str(labels(at)))

    fin = clic(at, "clé de l'île")
    check("rejoint le flux de fin d'île", fin.session_state["ecran_courant"] == "session",
          str(fin.session_state["ecran_courant"]))
    check("célébration de fin armée", "celebration_fin_ile_a_afficher" in fin.session_state)
    check("aucune session inexistante armée", fin.session_state["session_active"] is None)


def test_clic_ile_non_intercepte() -> None:
    print("\n=== 4. Clic d'île : la reprise ne doit pas s'interposer ===")
    # Le lien de la carte recharge la page entière : sans garde, l'enfant
    # reverrait « Ah, te voilà ! » à chaque clic et n'entrerait jamais dans l'île.
    at = lancer(ENTAMEE, _url={"ile": "ile_1"})
    check("entre bien dans l'île", at.session_state["ecran_courant"] == "ile",
          str(at.session_state["ecran_courant"]))
    check("pas d'accueil de reprise", "te voilà" not in texte(at))


def test_isolation() -> None:
    print("\n=== 5. Isolation : chaque famille sa reprise ===")
    entamee = lancer(ENTAMEE)
    neuve = lancer(NEUVE)
    check("l'entamée voit sa reprise", entamee.session_state["ecran_courant"] == "reprise")
    check("la neuve reste sur la carte", neuve.session_state["ecran_courant"] == "carte")
    check("le prénom de l'une n'apparaît pas chez l'autre", "Malo" not in texte(neuve),
          texte(neuve)[:150])
    check("la progression n'a pas fuité",
          not charger_joueur(NEUVE)["cristaux_obtenus"]
          or charger_joueur(NEUVE)["cristaux_obtenus"] in ("{}", ""),
          str(charger_joueur(NEUVE)["cristaux_obtenus"]))


def main() -> int:
    if _DB.exists():
        _DB.unlink()  # état déterministe : base recréée à chaque run
    _neutraliser_ecran_session()

    creer(NEUVE, "Zoe")
    creer(ENTAMEE, "Malo", genre="garcon", cristaux=["C1", "C2"])
    creer(FINIE, "Lou", cristaux=["C1", "C2", "C3", "C4", "C5"])

    try:
        test_partie_neuve()
        test_partie_entamee()
        test_ile_terminee()
        test_clic_ile_non_intercepte()
        test_isolation()
    except AssertionError as exc:
        check("parcours interrompu", False, str(exc))

    print()
    if _echecs:
        print(f"❌ {len(_echecs)} ÉCHEC(S) sur {_total} : {_echecs}")
        return 1
    print(f"✅ {_total}/{_total} vérifications passées")
    return 0


if __name__ == "__main__":
    sys.exit(main())
