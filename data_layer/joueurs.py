"""
data_layer/joueurs.py — CRUD joueur MVP
Sprint 3 T6 — avatar irréversible
Sprint 3 T7 — récompenses (clés + cristaux) en JSON
Sprint 3 T8.5 — prénom réel de l'enfant (D19bis)
Isolation des parties — une ligne joueurs PAR FAMILLE, désignée par partie_id

RÈGLE D'OR : aucune lecture ni écriture du joueur sans identité de partie.
Une base sert désormais plusieurs familles ; un partie_id oublié sur un seul
chemin de code rendrait la partie du voisin, et ce bug-là est invisible en
test mono-utilisateur. La règle est tenue par la structure, pas par la
vigilance : les fonctions du bas prennent un partie_id EXPLICITE et sont donc
inappelables sans identité.

Deux étages :
    API pure (partie_id explicite, sans Streamlit, testable telle quelle)
        charger_joueur(partie_id)                  -> dict | None
        joueur_existe_pour(partie_id)              -> bool
        creer_joueur_pour(partie_id, …)            -> int
        mettre_a_jour_session_pour(partie_id)      -> None

    Façades « partie courante » (résolvent l'identité du visiteur via
    core.partie, signatures inchangées pour les dix écrans appelants)
        creer_joueur(genre, avatar_prenom, role, prenom) -> int
        charger_joueur_courant()          -> dict | None
        joueur_existe()                   -> bool
        mettre_a_jour_session()           -> None

Récompenses, inchangées (elles travaillent sur un joueur_id déjà résolu) :
        lire_cles_obtenues(joueur_id)     -> dict
        ecrire_cles_obtenues(joueur_id, cles) -> None
        lire_cristaux_obtenus(joueur_id)  -> dict
        ecrire_cristaux_obtenus(joueur_id, cristaux) -> None
"""

import json
import sqlite3
from datetime import datetime, timezone

from core.partie import partie_courante, partie_courante_ou_nouvelle
from data_layer.db import get_connection


# ── Helpers ──────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    """Retourne l'instant courant en ISO 8601 UTC (sans microsecondes)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── API pure — partie_id explicite ────────────────────────────────────────────

def charger_joueur(partie_id: str) -> dict | None:
    """
    Retourne le joueur de CETTE partie (row → dict), ou None s'il n'existe pas.

    Clés retournées :
        id, avatar_genre, avatar_prenom, avatar_role,
        date_creation, date_derniere_session, cles_obtenues,
        cristaux_obtenus, planches_bd_vues, prenom, partie_id
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM joueurs WHERE partie_id = ?", (partie_id,)
        ).fetchone()
    if row is None:
        return None
    return dict(row)


def joueur_existe_pour(partie_id: str) -> bool:
    """True si CETTE partie a déjà son joueur. Ne dit rien des autres parties."""
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM joueurs WHERE partie_id = ?", (partie_id,)
        ).fetchone()[0]
    return count > 0


def creer_joueur_pour(
    partie_id: str,
    genre: str,
    avatar_prenom: str,
    role: str,
    prenom: str | None = None,
) -> int:
    """
    Insère le joueur de cette partie et retourne son id.

    avatar_prenom : prénom de l'avatar fictif (ex. "sassou", "melian").
    prenom        : prénom réel de l'enfant (D19bis), saisi à l'accueil.
                    Optionnel pour compatibilité — un joueur sans prénom
                    renseigné retombe sur "Élévateur" côté appelant.

    Règle MVP : un seul joueur PAR PARTIE, l'avatar restant irréversible.
    Une partie déjà pourvue lève ValueError plutôt que d'écraser
    silencieusement — l'existence d'autres parties, elle, n'empêche rien.
    """
    if joueur_existe_pour(partie_id):
        raise ValueError(
            "Un joueur existe déjà pour cette partie. "
            "La recréation d'avatar est désactivée au MVP."
        )
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO joueurs
                    (avatar_genre, avatar_prenom, avatar_role, date_creation, prenom, partie_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (genre, avatar_prenom, role, _now_iso(), prenom, partie_id),
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        # Deux appareils sur le même lien ont créé la partie en même temps :
        # l'index unique a tranché, et le perdant retombe sur la même règle
        # que ci-dessus plutôt que sur une erreur technique.
        raise ValueError(
            "Un joueur existe déjà pour cette partie. "
            "La recréation d'avatar est désactivée au MVP."
        ) from e


def mettre_a_jour_session_pour(partie_id: str) -> None:
    """
    Met à jour date_derniere_session de CETTE partie à maintenant.
    No-op si la partie n'a pas de joueur.
    """
    with get_connection() as conn:
        conn.execute(
            "UPDATE joueurs SET date_derniere_session = ? WHERE partie_id = ?",
            (_now_iso(), partie_id),
        )
        conn.commit()


# ── Façades — la partie courante du visiteur ──────────────────────────────────
#
# Signatures inchangées : les dix écrans appelants continuent d'appeler
# charger_joueur_courant() sans argument. Seule la résolution change.

def charger_joueur_courant() -> dict | None:
    """Le joueur de la partie de CE visiteur, ou None s'il n'en a pas encore.

    None couvre deux cas volontairement confondus, parce que l'app y répond
    pareil (envoyer à l'onboarding) : visiteur sans partie du tout, et visiteur
    arrivé par un lien pré-généré dont la partie n'a pas encore de joueur.
    """
    partie_id = partie_courante()
    if partie_id is None:
        return None
    return charger_joueur(partie_id)


def joueur_existe() -> bool:
    """True si la partie de ce visiteur a déjà son joueur."""
    partie_id = partie_courante()
    if partie_id is None:
        return False
    return joueur_existe_pour(partie_id)


def creer_joueur(genre: str, avatar_prenom: str, role: str, prenom: str | None = None) -> int:
    """Crée le joueur de ce visiteur, en ouvrant sa partie si besoin.

    Un visiteur arrivé par un lien pré-généré garde SON identifiant de partie ;
    un visiteur nu en reçoit un neuf, inscrit aussitôt dans l'URL — c'est ce
    lien que le parent devra conserver.
    """
    partie_id = partie_courante_ou_nouvelle()
    return creer_joueur_pour(partie_id, genre, avatar_prenom, role, prenom)


def mettre_a_jour_session() -> None:
    """Met à jour date_derniere_session de la partie courante. No-op sans partie."""
    partie_id = partie_courante()
    if partie_id is None:
        return
    mettre_a_jour_session_pour(partie_id)


# ── Sprint 3 T7 — Récompenses (clés + cristaux) ───────────────────────────────

def lire_cles_obtenues(joueur_id: int) -> dict:
    """
    Lit la colonne cles_obtenues, désérialise le JSON, retourne dict.
    Retourne {} si la colonne est NULL ou vide.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT cles_obtenues FROM joueurs WHERE id = ?",
            (joueur_id,),
        ).fetchone()
    if row is None or not row[0]:
        return {}
    return json.loads(row[0])


def ecrire_cles_obtenues(joueur_id: int, cles: dict) -> None:
    """Sérialise le dict en JSON et écrit dans la colonne cles_obtenues."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE joueurs SET cles_obtenues = ? WHERE id = ?",
            (json.dumps(cles, ensure_ascii=False), joueur_id),
        )
        conn.commit()


def lire_cristaux_obtenus(joueur_id: int) -> dict:
    """
    Lit la colonne cristaux_obtenus, désérialise le JSON, retourne dict.
    Retourne {} si la colonne est NULL ou vide.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT cristaux_obtenus FROM joueurs WHERE id = ?",
            (joueur_id,),
        ).fetchone()
    if row is None or not row[0]:
        return {}
    return json.loads(row[0])


def ecrire_cristaux_obtenus(joueur_id: int, cristaux: dict) -> None:
    """Sérialise le dict en JSON et écrit dans la colonne cristaux_obtenus."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE joueurs SET cristaux_obtenus = ? WHERE id = ?",
            (json.dumps(cristaux, ensure_ascii=False), joueur_id),
        )
        conn.commit()


# ── Sprint 3 T8.1 — Planches BD vues ─────────────────────────────────────────

def lire_planches_bd_vues(joueur_id: int) -> dict:
    """
    Lit la colonne planches_bd_vues, désérialise le JSON, retourne dict.
    Retourne {} si la colonne est NULL ou vide.
    Format : {"ile_1_c1": "2026-07-01T10:00:00Z", ...} — clé = f"{ile_id}_{planche_key}" (D-T8.1-D)
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT planches_bd_vues FROM joueurs WHERE id = ?",
            (joueur_id,),
        ).fetchone()
    if row is None or not row[0]:
        return {}
    return json.loads(row[0])


def ecrire_planches_bd_vues(joueur_id: int, planches: dict) -> None:
    """Sérialise le dict en JSON et écrit dans la colonne planches_bd_vues."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE joueurs SET planches_bd_vues = ? WHERE id = ?",
            (json.dumps(planches, ensure_ascii=False), joueur_id),
        )
        conn.commit()
