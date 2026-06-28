"""
data_layer/planches_bd.py — Persistance de l'historique des planches BD vues.
Sprint 3 T8.1

Public API :
    marquer_planche_vue(ile_id, planche_key)   -> None
    planche_deja_vue(ile_id, planche_key)      -> bool
"""

from __future__ import annotations

from datetime import datetime, timezone

from data_layer.joueurs import (
    charger_joueur_courant,
    lire_planches_bd_vues,
    ecrire_planches_bd_vues,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _joueur_id() -> int:
    joueur = charger_joueur_courant()
    if joueur is None:
        raise RuntimeError("Aucun joueur courant")
    return joueur["id"]


def marquer_planche_vue(ile_id: str, planche_key: str) -> None:
    """
    Enregistre qu'une planche a été vue (ou revue) par le joueur courant.
    Idempotent : si déjà vue, met à jour le timestamp (revue).
    Clé SQLite : f"{ile_id}_{planche_key}"
    """
    joueur_id = _joueur_id()
    planches = lire_planches_bd_vues(joueur_id)
    cle = f"{ile_id}_{planche_key}"
    planches[cle] = _now_iso()
    ecrire_planches_bd_vues(joueur_id, planches)


def planche_deja_vue(ile_id: str, planche_key: str) -> bool:
    """Retourne True si la planche a déjà été vue par le joueur courant."""
    joueur_id = _joueur_id()
    planches = lire_planches_bd_vues(joueur_id)
    return f"{ile_id}_{planche_key}" in planches
