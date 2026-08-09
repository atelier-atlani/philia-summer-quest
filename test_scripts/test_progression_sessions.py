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
  E. fin du chapitre 1 → coffre → planche → session 2 chargée, sans page vide,
     que l'enfant sorte par le bouton du modal ou par le repli derrière lui
  F. le numéro de chapitre affiché suit la planche, pas la session courante
  H. un seul modal par render : le pop-up de la sidebar cède devant le récit
  G. « Terminer le chapitre » n'apparaît qu'après « J'ai terminé cet exercice → »
     ET un tour de bilan (gating D-T8.1-F / D24)

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

import streamlit as st  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from data_layer.joueurs import charger_joueur, creer_joueur_pour  # noqa: E402
from jeu import recompenses  # noqa: E402

CIBLE = str(ROOT / "test_scripts" / "test_progression_target.py")
# Même partie que la cible : le joueur de test appartient à UNE partie, et
# les appels directs à recompenses (hors AppTest) doivent viser la même.
PARTIE_TEST = "testprogression01"
st.session_state["partie_id"] = PARTIE_TEST

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


def etat_moteur(
    numero_session: int,
    index: int | None = None,
    mode: str = "bilan",
    tours_bilan: int = 1,
) -> dict:
    """État sérialisé d'un moteur de la session demandée, placé où on veut.

    Par défaut : dernier exercice, bilan entamé — l'état juste avant
    « Terminer le chapitre ✓ ».
    """
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
    engine.index_exercice = len(exercices) - 1 if index is None else index
    engine.historique = [{"role": "assistant", "content": "Message déjà affiché."}]
    etat = engine.to_dict()
    etat["mode"] = mode
    etat["nb_tours_bilan"] = tours_bilan
    return etat


def etat_bilan(numero_session: int) -> dict:
    """Moteur de la session demandée, positionné au bilan, prêt à être terminé."""
    return etat_moteur(numero_session)


def page_vide(at: AppTest) -> bool:
    """Vrai si le rendu n'offre à l'enfant ni texte ni bouton pour avancer.

    C'est la définition opérationnelle du bug de page vide : un écran qui a
    ouvert un modal puis rendu la main sans rien laisser derrière.
    """
    return not texte(at).strip() and not labels(at)


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
    check(f"S{numero} — écran du coffre non vide", not page_vide(at))
    clic(at, "Continuer →")
    check(f"S{numero} — écran de la planche non vide", not page_vide(at))
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
    """« Retour à l'île » puis traversée présentation → arrivée."""
    clic(at, "← Retour à l'île")
    check("retour à l'île → écran île", ss(at, "ecran_courant") == "ile", str(ss(at, "ecran_courant")))
    check("retour à l'île → on repart de la présentation",
          ss(at, "etape_ile") == "presentation", str(ss(at, "etape_ile")))
    clic(at, "Continuer →")  # présentation → arrivée
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
    clic(at, "Continuer →")  # présentation → arrivée
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
    # L'ordre narratif : Archimède présente l'île, ensuite seulement on y débarque.
    check("entrée dans l'île → étape « presentation » d'abord",
          ss(at, "etape_ile") == "presentation", str(ss(at, "etape_ile")))
    check("la présentation montre l'île avant qu'on y soit",
          "Regarde cette île" in texte(at), texte(at)[:200])
    check("aucun bouton de session sur la présentation",
          not any(lab.startswith(("Commencer la Session", "Continuer — Session"))
                  for lab in labels(at)),
          str(labels(at)))

    clic(at, "Continuer →")  # présentation → arrivée
    check("après la présentation → étape « arrivee »",
          ss(at, "etape_ile") == "arrivee", str(ss(at, "etape_ile")))
    check("l'arrivée dit qu'on y est", "Te voilà" in texte(at), texte(at)[:200])
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
    clic(at, "Continuer →")  # présentation → arrivée
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


def test_fin_de_chapitre_sans_page_vide() -> None:
    """BUG A — fin du chapitre 1 → coffre → planche → session 2 chargée.

    Le parcours est joué deux fois : une fois par les boutons des modals, une
    fois par les replis affichés derrière eux (le geste d'un enfant qui referme
    la fenêtre). Les deux doivent aboutir au même écran, jamais à une page vide.
    """
    print("\n=== E. Fin de chapitre 1 : aucune page vide, session 2 chargée ===")
    from pedagogie.contenu_ile1 import META_SESSION_2

    for chemin, bouton_coffre, bouton_planche in (
        ("par les boutons du modal", "Continuer →", "Continuer la quête →"),
        ("par le repli derrière le modal", "Poursuivre →", "Poursuivre la quête →"),
    ):
        recompenses.reset_recompenses()
        at = app_neuve()
        at.session_state.ecran_courant = "session"
        at.session_state.session_courante = 1
        at.session_state.session_active = etat_bilan(1)
        at.run()

        clic(at, "Terminer le chapitre ✓")
        check(f"coffre affiché ({chemin})", ss(at, "coffre_session_a_afficher") == "Sens d'une fraction",
              str(ss(at, "coffre_session_a_afficher")))
        check(f"écran du coffre non vide ({chemin})", not page_vide(at))

        clic(at, bouton_coffre)
        check(f"planche c1 affichée ({chemin})", ss(at, "planche_bd_a_afficher") == "c1",
              str(ss(at, "planche_bd_a_afficher")))
        check(f"écran de la planche non vide ({chemin})", not page_vide(at))

        while "Suite →" in labels(at):
            clic(at, "Suite →")
        clic(at, bouton_planche)

        check(f"session 2 armée ({chemin})", ss(at, "session_courante") == 2,
              str(ss(at, "session_courante")))
        check(f"tous les flags du flux effacés ({chemin})",
              not ss(at, "coffre_session_a_afficher")
              and not ss(at, "planche_bd_a_afficher")
              and not ss(at, "planche_bd_chapitre"),
              f"coffre={ss(at, 'coffre_session_a_afficher')} "
              f"planche={ss(at, 'planche_bd_a_afficher')} "
              f"chapitre={ss(at, 'planche_bd_chapitre')}")
        check(f"écran de la session 2 rendu, pas une page vide ({chemin})",
              META_SESSION_2["titre"] in texte(at), texte(at)[:200])
        check(f"un moteur est en place pour la session 2 ({chemin})",
              bool(ss(at, "session_active")))
        check(f"pas d'exception sur tout le chemin ({chemin})", not at.exception, str(at.exception))


def test_chapitre_affiche_est_celui_de_la_planche() -> None:
    """BUG A (cause) — le numéro de chapitre suit la planche affichée, pas la
    session courante, qui a pu avancer entre-temps."""
    print("\n=== F. Le chapitre affiché est celui de la planche ===")
    recompenses.reset_recompenses()
    recompenses.gagner_cristal("ile_1", "C1")

    at = AppTest.from_file(CIBLE, default_timeout=60)
    at.session_state["ecran_courant"] = "session"
    at.session_state["session_courante"] = 2          # la progression a déjà avancé…
    at.session_state["planche_bd_a_afficher"] = "c1"  # …mais on montre la planche du 1
    at.session_state["planche_bd_chapitre"] = 1
    at.session_state["planche_bd_index"] = 0
    at.run()
    corps = texte(at)
    check("pas d'exception", not at.exception, str(at.exception))
    check("légende du chapitre 1 (pas du 2)", "Chapitre 1 validé" in corps, corps[:300])
    check("décompte restant calculé sur le chapitre 1",
          "Encore 4 chapitre(s)" in corps, corps[:300])
    check("écran non vide", not page_vide(at))


def test_un_seul_modal_par_render() -> None:
    """Streamlit n'autorise qu'un dialog par script run : le pop-up « Voir l'île »
    de la sidebar ne doit pas s'ouvrir en même temps qu'un modal du récit."""
    print("\n=== H. Un seul modal à la fois (sidebar vs récit) ===")
    recompenses.reset_recompenses()

    at = AppTest.from_file(CIBLE, default_timeout=60)
    at.session_state["ecran_courant"] = "session"
    at.session_state["session_courante"] = 1
    at.session_state["coffre_session_a_afficher"] = "Sens d'une fraction"
    at.session_state["coffre_session_tally"] = "6 pierres"
    at.session_state["planche_bd_a_afficher"] = "c1"
    at.session_state["planche_bd_chapitre"] = 1
    at.session_state["vue_ile_a_afficher"] = "ile_1"  # pop-up d'agrément en attente
    at.run()
    check("pas d'exception avec deux modals en concurrence", not at.exception, str(at.exception))
    check("le pop-up de la sidebar a cédé la place",
          not ss(at, "vue_ile_a_afficher"), str(ss(at, "vue_ile_a_afficher")))
    check("le coffre reste affiché", "ce coffre est à toi" in texte(at), texte(at)[:200])


def test_bouton_terminer_pas_avant_le_bilan() -> None:
    """BUG B — au dernier exercice, « Terminer le chapitre » ne doit pas être là
    tant que l'enfant n'a pas déclaré avoir fini, puis échangé en bilan."""
    print("\n=== G. « Terminer le chapitre » n'apparaît pas pendant le dernier exercice ===")
    from pedagogie.contenu_ile1 import SESSION_1

    dernier = len(SESSION_1) - 1
    recompenses.reset_recompenses()

    at = AppTest.from_file(CIBLE, default_timeout=60)
    at.session_state["ecran_courant"] = "session"
    at.session_state["session_courante"] = 1
    at.session_state["session_active"] = etat_moteur(1, index=dernier, mode="decouverte", tours_bilan=0)
    at.run()
    labs = labels(at)
    corps = texte(at)
    check("pas d'exception", not at.exception, str(at.exception))
    check("« Terminer le chapitre » absent pendant le dernier exercice",
          "Terminer le chapitre ✓" not in labs, str(labs))
    check("bouton « J'ai terminé cet exercice → » proposé",
          "J'ai terminé cet exercice →" in labs, str(labs))
    check(f"repère « Exercice {dernier + 1} / {len(SESSION_1)} », pas « Bilan »",
          f"Exercice {dernier + 1} / {len(SESSION_1)}" in corps and "· Bilan" not in corps,
          corps[:200])
    check("« Retour à l'île » encore accessible hors bilan",
          "← Retour à l'île" in labs, str(labs))

    clic(at, "J'ai terminé cet exercice →")
    check("passage en bilan", ss(at, "session_active", {}).get("mode") == "bilan",
          str(ss(at, "session_active", {}).get("mode")))
    check("repère « Bilan » après le clic", "· Bilan" in texte(at), texte(at)[:200])
    check("dernier objet encaissé (toast armé ou déjà consommé)",
          "objet_gagne_a_afficher" in at.session_state)
    labs = labels(at)
    check("« Terminer le chapitre » toujours absent : aucun tour de bilan échangé",
          "Terminer le chapitre ✓" not in labs, str(labs))
    check("le kickoff de bilan ne compte pas comme un tour",
          ss(at, "session_active", {}).get("nb_tours_bilan") == 0,
          str(ss(at, "session_active", {}).get("nb_tours_bilan")))

    # Un échange de bilan (simulé : le vrai passe par l'API du mentor)
    etat = dict(ss(at, "session_active"))
    etat["nb_tours_bilan"] = 1
    at.session_state["session_active"] = etat
    at.run()
    check("« Terminer le chapitre » apparaît après un tour de bilan",
          "Terminer le chapitre ✓" in labels(at), str(labels(at)))


def main() -> int:
    if _DB_TEST.exists():
        _DB_TEST.unlink()  # état déterministe : base recréée à chaque run
    if charger_joueur(PARTIE_TEST) is None:
        creer_joueur_pour(PARTIE_TEST, genre="fille", avatar_prenom="sassou",
                          role="eleve", prenom="Léa")

    try:
        test_derivation()
        test_reprise()
        test_parcours_complet()
        test_fin_de_chapitre_sans_page_vide()
        test_chapitre_affiche_est_celui_de_la_planche()
        test_un_seul_modal_par_render()
        test_bouton_terminer_pas_avant_le_bilan()
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
