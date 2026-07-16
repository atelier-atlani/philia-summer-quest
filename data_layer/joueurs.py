"""
data_layer/joueurs.py — CRUD joueur MVP
Sprint 3 T6 — single-player, avatar irréversible
Sprint 3 T7 — récompenses (clés + cristaux) en JSON
Sprint 3 T8.5 — prénom réel de l'enfant (D19bis)

Public API :
    creer_joueur(genre, avatar_prenom, role, prenom) -> int
    charger_joueur_courant()          -> dict | None
    joueur_existe()                   -> bool
    mettre_a_jour_session()           -> None
    lire_cles_obtenues(joueur_id)     -> dict
    ecrire_cles_obtenues(joueur_id, cles) -> None
    lire_cristaux_obtenus(joueur_id)  -> dict
    ecrire_cristaux_obtenus(joueur_id, cristaux) -> None
"""

import json
from datetime import datetime, timezone
from data_layer.db import get_connection


# ── Helpers ──────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    """Retourne l'instant courant en ISO 8601 UTC (sans microsecondes)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── API publique ──────────────────────────────────────────────────────────────

def creer_joueur(genre: str, avatar_prenom: str, role: str, prenom: str | None = None) -> int:
    """
    Insère un nouveau joueur en base et retourne son id.

    avatar_prenom : prénom de l'avatar fictif (ex. "sassou", "melian").
    prenom        : prénom réel de l'enfant (D19bis), saisi à l'accueil.
                    Optionnel pour compatibilité — un joueur sans prénom
                    renseigné retombe sur "Élévateur" côté appelant.

    Règle MVP : un seul joueur autorisé. Si un joueur existe déjà,
    lève ValueError plutôt que d'écraser silencieusement.
    """
    if joueur_existe():
        raise ValueError(
            "Un joueur existe déjà en base. "
            "La recréation d'avatar est désactivée au MVP."
        )
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO joueurs (avatar_genre, avatar_prenom, avatar_role, date_creation, prenom)
            VALUES (?, ?, ?, ?, ?)
            """,
            (genre, avatar_prenom, role, _now_iso(), prenom),
        )
        conn.commit()
        return cursor.lastrowid


def charger_joueur_courant() -> dict | None:
    """
    Retourne le joueur (row → dict) ou None si aucun joueur en base.

    Clés retournées :
        id, avatar_genre, avatar_prenom, avatar_role,
        date_creation, date_derniere_session, cles_obtenues,
        cristaux_obtenus, planches_bd_vues, prenom
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM joueurs ORDER BY id LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    return dict(row)


def joueur_existe() -> bool:
    """Retourne True si au moins un joueur est enregistré en base."""
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM joueurs").fetchone()[0]
    return count > 0


def mettre_a_jour_session() -> None:
    """
    Met à jour date_derniere_session du joueur courant à maintenant.
    No-op si aucun joueur en base.
    """
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE joueurs
            SET date_derniere_session = ?
            WHERE id = (SELECT id FROM joueurs ORDER BY id LIMIT 1)
            """,
            (_now_iso(),),
        )
        conn.commit()


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
