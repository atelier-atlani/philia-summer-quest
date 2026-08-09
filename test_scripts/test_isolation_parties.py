"""test_scripts/test_isolation_parties.py — Deux familles, deux parties, aucune fuite.

C'est le garde-fou du multi-familles. Le bug qu'il guette est invisible en test
mono-utilisateur : un partie_id oublié sur un seul chemin de code, et une
famille se retrouve dans la partie d'une autre — mêmes coffres, même prénom
d'enfant.

Trois niveaux, du plus bas au plus proche du réel :
  1. API pure (data_layer.joueurs, partie_id explicite) — l'isolation en base
  2. app.py en AppTest, deux « navigateurs » avec chacun son ?partie=
  3. écritures concurrentes — deux parties qui progressent en même temps

La validation en VRAI navigateur (deux contextes Playwright) reste séparée :
elle seule exerce le rechargement de page complet des liens de la carte.

Lancer :
    python test_scripts/test_isolation_parties.py
Sortie : code 0 si tout passe, 1 sinon.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import data_layer.db as db  # noqa: E402

_DB = ROOT / "data" / "_test_isolation.db"
db._DB_PATH = _DB  # jamais data/philia.db

import streamlit as st  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from data_layer.joueurs import (  # noqa: E402
    charger_joueur,
    creer_joueur_pour,
    ecrire_cles_obtenues,
    joueur_existe_pour,
    lire_cles_obtenues,
    mettre_a_jour_session_pour,
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


def qp(at, cle):
    """AppTest expose les query params en listes ; l'app lit des chaînes."""
    val = at.query_params.get(cle)
    return val[0] if isinstance(val, list) and val else val


def _arbre_propre(at):
    etat = dict(at.session_state.filtered_state)
    params = {cle: qp(at, cle) for cle in dict(at.query_params)}
    nv = AppTest.from_file(APP, default_timeout=60)
    for cle, val in etat.items():
        nv.session_state[cle] = val
    for cle, val in params.items():
        nv.query_params[cle] = val
    nv.run()
    if nv.exception:
        raise AssertionError(f"Exception : {nv.exception}")
    return nv


def clic(at, label: str):
    boutons = [b for b in at.button if b.label == label]
    if not boutons:
        raise AssertionError(f"Bouton « {label} » absent — présents : {[b.label for b in at.button]}")
    boutons[0].click().run()
    if at.exception:
        raise AssertionError(f"Exception après « {label} » : {at.exception}")
    return _arbre_propre(at)


def onboarder(partie_id: str | None, prenom: str, avatar: str):
    """Joue l'onboarding complet d'une famille et rend son AppTest."""
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["acces_deverrouille"] = True  # le portail n'est pas l'objet ici
    if partie_id:
        at.query_params["partie"] = partie_id
    at.run()
    at.text_input[0].set_value(prenom).run()
    at = clic(at, "⚓ Lever l'ancre")
    at = clic(at, avatar)
    at = clic(at, "✅ Confirmer")
    return at


# ── 1. API pure : l'isolation en base ─────────────────────────────────────────

def test_api_pure() -> None:
    print("\n=== 1. API pure — deux parties en base ===")
    A, B = "isolationAAAAAAA1", "isolationBBBBBBB2"

    id_a = creer_joueur_pour(A, genre="fille", avatar_prenom="melian",
                             role="architecte", prenom="Nina")
    check("créer A ne crée pas B", not joueur_existe_pour(B))
    check("charger(B) rend None alors que A existe", charger_joueur(B) is None)

    id_b = creer_joueur_pour(B, genre="garcon", avatar_prenom="sassou",
                             role="aventurier", prenom="Tom")
    check("B se crée malgré A (plus de refus global)", joueur_existe_pour(B))
    check("deux lignes distinctes", id_a != id_b, f"{id_a}/{id_b}")
    check("A garde son prénom", charger_joueur(A)["prenom"] == "Nina")
    check("B garde le sien", charger_joueur(B)["prenom"] == "Tom")

    ecrire_cles_obtenues(id_a, {"ile_1": "2026-08-09T10:00:00Z"})
    check("la clé de A reste chez A", lire_cles_obtenues(id_a) != {})
    check("B n'a rien reçu", lire_cles_obtenues(id_b) == {}, str(lire_cles_obtenues(id_b)))

    mettre_a_jour_session_pour(A)
    check("la session de B n'a pas bougé",
          charger_joueur(B)["date_derniere_session"] is None,
          str(charger_joueur(B)["date_derniere_session"]))

    try:
        creer_joueur_pour(A, genre="fille", avatar_prenom="melian",
                          role="architecte", prenom="Doublon")
        check("l'avatar reste irréversible DANS une partie", False, "aucune erreur")
    except ValueError:
        check("l'avatar reste irréversible DANS une partie", True)


# ── 2. Niveau app : deux navigateurs ──────────────────────────────────────────

def test_deux_navigateurs() -> None:
    print("\n=== 2. app.py — deux familles, deux ?partie= ===")
    LIEN_A = "prégénéréPourA123".replace("é", "e")  # lien distribué à l'avance

    a = onboarder(LIEN_A, "nina", "L'architecte")
    check("A : joueur créé sous SON identifiant", charger_joueur(LIEN_A) is not None)
    check("A : l'URL porte sa partie", qp(a, "partie") == LIEN_A, str(dict(a.query_params)))

    b = onboarder(None, "tom", "L'aventurier")  # visiteur nu
    PARTIE_B = qp(b, "partie")
    check("B : reçoit un identifiant neuf", bool(PARTIE_B) and PARTIE_B != LIEN_A, str(PARTIE_B))
    check("B n'a pas écrasé A", charger_joueur(LIEN_A)["prenom"] == "Nina",
          str(charger_joueur(LIEN_A)))
    check("A et B ont bien deux prénoms distincts en base",
          charger_joueur(PARTIE_B)["prenom"] == "Tom", str(charger_joueur(PARTIE_B)))

    for nom, partie_id, attendu in [("A", LIEN_A, "Nina"), ("B", PARTIE_B, "Tom")]:
        r = AppTest.from_file(APP, default_timeout=60)
        r.session_state["acces_deverrouille"] = True
        r.query_params["partie"] = partie_id
        r.run()
        check(f"{nom} rouvre son lien et reprend à la carte",
              r.session_state["ecran_courant"] == "carte",
              str(r.session_state["ecran_courant"]))
        check(f"{nom} retrouve {attendu}", charger_joueur(partie_id)["prenom"] == attendu)

    # Le cas qui a motivé tout le chantier
    nu = AppTest.from_file(APP, default_timeout=60)
    nu.session_state["acces_deverrouille"] = True
    nu.run()
    check("un visiteur SANS lien ne tombe sur la partie de personne",
          nu.session_state["ecran_courant"] == "accueil",
          str(nu.session_state["ecran_courant"]))

    # Les liens de la carte doivent emporter la partie, sinon le clic la perd
    import re
    r = AppTest.from_file(APP, default_timeout=60)
    r.session_state["acces_deverrouille"] = True
    r.query_params["partie"] = LIEN_A
    r.run()
    hrefs = re.findall(r'<a href="([^"]+)"', " ".join(str(m.value) for m in r.markdown))
    check("le lien d'île porte la partie", bool(hrefs) and f"partie={LIEN_A}" in hrefs[0],
          str(hrefs))

    apres = AppTest.from_file(APP, default_timeout=60)
    apres.session_state["acces_deverrouille"] = True
    for cle, val in [p.split("=") for p in hrefs[0].lstrip("?").split("&")]:
        apres.query_params[cle] = val
    apres.run()
    check("après le clic, on est toujours dans la partie de A",
          apres.session_state["partie_id"] == LIEN_A,
          str(dict(apres.session_state.filtered_state).get("partie_id")))


# ── 3. Écritures concurrentes ─────────────────────────────────────────────────

def test_ecritures_concurrentes() -> None:
    print("\n=== 3. Deux parties qui écrivent en même temps ===")
    parties = [f"concurrente{i:07d}" for i in range(4)]
    ids = {
        p: creer_joueur_pour(p, genre="fille", avatar_prenom="melian",
                             role="architecte", prenom=f"Enfant{i}")
        for i, p in enumerate(parties)
    }
    erreurs: list[str] = []

    def jouer(partie_id: str) -> None:
        # Lire-modifier-écrire, comme le fait jeu/recompenses : c'est ce cycle
        # qui perdrait des données si les parties se marchaient dessus.
        try:
            for tour in range(15):
                acquis = lire_cles_obtenues(ids[partie_id])
                acquis[f"ile_{tour}"] = partie_id
                ecrire_cles_obtenues(ids[partie_id], acquis)
                mettre_a_jour_session_pour(partie_id)
        except Exception as exc:  # verrou SQLite, contention…
            erreurs.append(f"{partie_id} : {exc}")

    fils = [threading.Thread(target=jouer, args=(p,)) for p in parties]
    for f in fils:
        f.start()
    for f in fils:
        f.join()

    check("aucune écriture n'a échoué (WAL + busy_timeout)", not erreurs, str(erreurs))
    for p in parties:
        cles = lire_cles_obtenues(ids[p])
        check(f"{p} : ses 15 clés, et rien que les siennes",
              len(cles) == 15 and set(cles.values()) == {p}, str(cles)[:120])


def test_creation_base_concurrente() -> None:
    """Deux familles arrivant ENSEMBLE sur une base vierge (premier déploiement).

    Trouvé par la validation deux navigateurs : schema.sql portait des ALTER
    TABLE nus, rejoués par le second arrivant, qui plantait sur « duplicate
    column name ». La base doit pouvoir être préparée par plusieurs threads.
    """
    print("\n=== 4. Création simultanée de la base (disque vierge) ===")
    if _DB.exists():
        _DB.unlink()
    db._migrations_faites.clear()

    erreurs: list[str] = []

    def ouvrir() -> None:
        try:
            conn = db.get_connection()
            conn.execute("SELECT COUNT(*) FROM joueurs").fetchone()
            conn.close()
        except Exception as exc:
            erreurs.append(str(exc))

    fils = [threading.Thread(target=ouvrir) for _ in range(8)]
    for f in fils:
        f.start()
    for f in fils:
        f.join()

    check("8 arrivées simultanées sur une base vierge, aucune erreur",
          not erreurs, str(erreurs[:2]))

    conn = db.get_connection()
    cols = {r[1] for r in conn.execute("PRAGMA table_info(joueurs)")}
    conn.close()
    check("le schéma est complet malgré la course",
          {"partie_id", "cles_obtenues", "cristaux_obtenus", "prenom"} <= cols, str(sorted(cols)))


def main() -> int:
    if _DB.exists():
        _DB.unlink()  # état déterministe
    # Les appels directs à l'API pure n'ont pas besoin de session ; l'app sous
    # AppTest, si — chaque instance porte sa propre partie via ?partie=.
    st.session_state.setdefault("partie_id", None)

    try:
        test_creation_base_concurrente()   # d'abord : il repart d'une base vierge
        test_api_pure()
        test_deux_navigateurs()
        test_ecritures_concurrentes()
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
