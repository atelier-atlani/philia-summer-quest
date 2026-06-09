"""
data_layer/joueurs.py — CRUD joueur MVP
Sprint 3 T6 — single-player, avatar irréversible

Public API :
    creer_joueur(genre, prenom, role) -> int
    charger_joueur_courant()          -> dict | None
    joueur_existe()                   -> bool
    mettre_a_jour_session()           -> None
"""

from datetime import datetime, timezone
from data_layer.db import get_connection


# ── Helpers ──────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    """Retourne l'instant courant en ISO 8601 UTC (sans microsecondes)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── API publique ──────────────────────────────────────────────────────────────

def creer_joueur(genre: str, prenom: str, role: str) -> int:
    """
    Insère un nouveau joueur en base et retourne son id.

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
            INSERT INTO joueurs (avatar_genre, avatar_prenom, avatar_role, date_creation)
            VALUES (?, ?, ?, ?)
            """,
            (genre, prenom, role, _now_iso()),
        )
        conn.commit()
        return cursor.lastrowid


def charger_joueur_courant() -> dict | None:
    """
    Retourne le joueur (row → dict) ou None si aucun joueur en base.

    Clés retournées :
        id, avatar_genre, avatar_prenom, avatar_role,
        date_creation, date_derniere_session
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
