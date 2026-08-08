"""test_scripts/test_onboarding_parcours.py — Le parcours d'onboarding réel,
écran par écran, du lancement jusqu'à l'entrée en session 1.

Joue app.py en AppTest sur une base dédiée, et vérifie l'ORDRE des écrans —
c'est ce que les refactors de flux déplacent, et rien d'autre ne le garde :

  A. enfant neuf : accueil → avatar → confirmation → UN écran d'annonce de
     l'archipel → carte → île (présentation PUIS arrivée) → accueil d'île
  B. enfant qui revient : la carte directement, sans écran à reconsommer

Aucun appel réseau : le parcours s'arrête avant l'entrée en session, qui est
couverte par test_progression_sessions.py.
Isolé de data/philia.db (base data/_test_onboarding.db, recréée à chaque run).

Lancer :
    python test_scripts/test_onboarding_parcours.py
Sortie : code 0 si tout passe, 1 sinon.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import data_layer.db as db  # noqa: E402

_DB = ROOT / "data" / "_test_onboarding.db"
db._DB_PATH = _DB  # jamais data/philia.db

from streamlit.testing.v1 import AppTest  # noqa: E402

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


def labels(at) -> list[str]:
    return [b.label for b in at.button]


def texte(at) -> str:
    return " ".join(
        [str(m.value) for m in at.markdown]
        + [str(c.value) for c in at.caption]
        + [str(t.value) for t in at.title]
        + [str(i.value) for i in at.info]
        + [str(h.value) for h in at.header]
    )


def ss(at, cle, defaut=None):
    return at.session_state[cle] if cle in at.session_state else defaut


def _arbre_propre(at):
    """Repart d'un AppTest neuf en conservant session_state.

    Un st.rerun() dans le script laisse dans l'arbre AppTest les widgets de la
    passe précédente (le champ prénom survit à l'écran d'accueil). Le clic
    suivant tente alors de lire un widget que Streamlit a déjà nettoyé.
    Rejouer l'app sur le même état donne l'arbre réel de l'écran courant.
    """
    etat = dict(at.session_state.filtered_state)
    nv = AppTest.from_file(APP, default_timeout=60)
    for cle, val in etat.items():
        nv.session_state[cle] = val
    nv.run()
    if nv.exception:
        raise AssertionError(f"Exception au rendu de {ecran(nv)} : {nv.exception}")
    return nv


def clic(at, label: str):
    boutons = [b for b in at.button if b.label == label]
    if not boutons:
        raise AssertionError(f"Bouton « {label} » absent — présents : {labels(at)}")
    boutons[0].click().run()
    if at.exception:
        raise AssertionError(f"Exception après « {label} » : {at.exception}")
    return _arbre_propre(at)


def ecran(at) -> str:
    return f"{ss(at, 'ecran_courant')}/{ss(at, 'etape_onboarding')}/{ss(at, 'etape_ile')}"


def parcours_enfant_neuf() -> None:
    print("\n=== Enfant neuf : lancement → session 1 ===")
    if _DB.exists():
        _DB.unlink()

    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["acces_deverrouille"] = True  # le portail de code n'est pas l'objet du test
    at.run()
    check("1. lancement sans exception", not at.exception, str(at.exception))
    print(f"     écran={ecran(at)} boutons={labels(at)}")
    check("1. accueil narratif affiché", "Approche, jeune élévateur" in texte(at), texte(at)[:120])

    # Saisi en minuscule et avec des espaces : c'est ce qu'un enfant tape.
    at.text_input[0].set_value("  jean-luc ").run()
    at = clic(at, "⚓ Lever l'ancre")
    print(f"     écran={ecran(at)} boutons={labels(at)}")
    check("2. choix d'avatar", "Qui sera ton avatar ?" in texte(at), texte(at)[:120])

    at = clic(at, "L'architecte")
    print(f"     écran={ecran(at)} boutons={labels(at)}")
    check("3. confirmation", "L'architecte" in texte(at), texte(at)[:120])
    check("3. aucun nom de personnage affiché",
          "Sassou" not in texte(at) and "Mélian" not in texte(at), texte(at)[:200])

    at = clic(at, "✅ Confirmer")
    print(f"     écran={ecran(at)} boutons={labels(at)}")
    print(f"     texte={texte(at)[:300]!r}")

    check("4. le mot de bienvenue personnalisé est conservé, prénom capitalisé",
          "Bienvenue à bord, Jean-Luc" in texte(at), texte(at)[:400])
    check("4. l'archipel n'est annoncé qu'ici",
          "Voici l'Archipel de la Raison" in texte(at), texte(at)[:400])

    # Enchaîne les écrans de transition jusqu'à la carte, quels qu'ils soient.
    ecrans_transition = 0
    while ss(at, "ecran_courant") not in ("carte", None):
        labs = labels(at)
        if not labs:
            raise AssertionError(f"Écran sans bouton : {ecran(at)}")
        ecrans_transition += 1
        print(f"     → transition {ecrans_transition} : « {labs[0]} »")
        at = clic(at, labs[0])
        print(f"     écran={ecran(at)} boutons={labels(at)}")
        if ecrans_transition > 5:
            raise AssertionError("boucle de transition")
    check("4. arrivée sur la carte", ss(at, "ecran_courant") == "carte")
    check("4. un seul écran d'annonce entre l'avatar et la carte",
          ecrans_transition == 1, f"{ecrans_transition} écrans")
    print(f"     ÉCRANS D'ANNONCE ENTRE AVATAR ET CARTE : {ecrans_transition}")

    # La carte n'a pas de bouton : on simule le clic sur l'île 1.
    at.session_state["ile_courante"] = "ile_1"
    at.session_state["ecran_courant"] = "ile"
    at.run()
    check("5. entrée dans l'île sans exception", not at.exception, str(at.exception))
    print(f"     écran={ecran(at)} boutons={labels(at)}")
    check("5. présentation d'abord", ss(at, "etape_ile") == "presentation", str(ss(at, "etape_ile")))

    at = clic(at, "Continuer →")
    print(f"     écran={ecran(at)} boutons={labels(at)}")
    check("6. arrivée ensuite", ss(at, "etape_ile") == "arrivee", str(ss(at, "etape_ile")))
    check("6. bouton de session sur l'arrivée",
          "Commencer la Session 1" in labels(at), str(labels(at)))

    at = clic(at, "Commencer la Session 1")
    print(f"     écran={ecran(at)} boutons={labels(at)}")
    check("7. accueil d'île intercalé", ss(at, "etape_ile") == "accueil", str(ss(at, "etape_ile")))
    check("7. bouton « Commencer l'aventure → »",
          "Commencer l'aventure →" in labels(at), str(labels(at)))
    check("7. routage prêt pour la session", ss(at, "ecran_courant") == "ile")


def parcours_enfant_qui_revient() -> None:
    print("\n=== Enfant qui revient (joueur déjà en base) ===")
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["acces_deverrouille"] = True  # le portail de code n'est pas l'objet du test
    at.run()
    check("relance sans exception", not at.exception, str(at.exception))
    print(f"     écran={ecran(at)} boutons={labels(at)}")
    print(f"     texte={texte(at)[:200]!r}")

    ecrans = 0
    while ss(at, "ecran_courant") != "carte":
        labs = labels(at)
        if not labs:
            raise AssertionError(f"Écran sans bouton : {ecran(at)}")
        ecrans += 1
        print(f"     → clic {ecrans} : « {labs[0]} »")
        at = clic(at, labs[0])
        if ecrans > 5:
            raise AssertionError("boucle")
    check("l'enfant qui revient atteint la carte", ss(at, "ecran_courant") == "carte")
    check("l'enfant qui revient y arrive sans écran à reconsommer",
          ecrans == 0, f"{ecrans} clic(s)")
    print(f"     CLICS AVANT LA CARTE POUR UN RETOUR : {ecrans}")


def main() -> int:
    try:
        parcours_enfant_neuf()
        parcours_enfant_qui_revient()
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
