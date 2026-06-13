"""
jeu/recompenses.py — Module métier récompenses — Philia Summer Quest.
Sprint 3 T7

Responsabilité : gérer l'obtention et la lecture des clés et cristaux
du joueur courant. Persiste en base via data_layer.joueurs.

Règles métier :
- Toutes les fonctions opèrent sur le joueur courant
  (data_layer.joueurs.charger_joueur_courant()).
- Si aucun joueur en base → RuntimeError("Aucun joueur courant").
- Les fonctions de gain sont idempotentes : appeler deux fois ne
  duplique pas la récompense.
- Les timestamps sont ISO 8601 UTC (timezone-aware, sans microsecondes).

Public API :
    gagner_cle(ile_id)                       -> dict
    gagner_cristal(ile_id, concept_id)       -> dict
    a_obtenu_cle(ile_id)                     -> bool
    a_obtenu_cristal(ile_id, concept_id)     -> bool
    nombre_cles_obtenues()                   -> int
    nombre_cristaux_obtenus()                -> int
    cles_obtenues()                          -> dict
    cristaux_obtenus()                       -> dict
    reset_recompenses()                      -> None
"""

from __future__ import annotations

from datetime import datetime, timezone

from data_layer.joueurs import (
    charger_joueur_courant,
    ecrire_cles_obtenues,
    ecrire_cristaux_obtenus,
    lire_cles_obtenues,
    lire_cristaux_obtenus,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    """Instant courant en ISO 8601 UTC, sans microsecondes."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _joueur_id_ou_erreur() -> int:
    """
    Retourne l'id du joueur courant.
    Lève RuntimeError si aucun joueur n'existe en base.
    """
    joueur = charger_joueur_courant()
    if joueur is None:
        raise RuntimeError("Aucun joueur courant")
    return joueur["id"]


# ── API publique ──────────────────────────────────────────────────────────────

def gagner_cle(ile_id: str) -> dict:
    """
    Ajoute la clé de l'île au joueur courant avec timestamp ISO.
    Retourne le dict cles_obtenues mis à jour.
    Idempotent : si la clé existe déjà, ne fait rien et retourne l'état actuel.
    """
    joueur_id = _joueur_id_ou_erreur()
    cles = lire_cles_obtenues(joueur_id)
    if ile_id not in cles:
        cles[ile_id] = _now_iso()
        ecrire_cles_obtenues(joueur_id, cles)
    return cles


def gagner_cristal(ile_id: str, concept_id: str) -> dict:
    """
    Ajoute le cristal au joueur courant avec timestamp ISO.
    Retourne le dict cristaux_obtenus mis à jour.
    Idempotent : si le cristal existe déjà, ne fait rien.
    """
    joueur_id = _joueur_id_ou_erreur()
    cristaux = lire_cristaux_obtenus(joueur_id)
    ile_cristaux = cristaux.setdefault(ile_id, {})
    if concept_id not in ile_cristaux:
        ile_cristaux[concept_id] = _now_iso()
        ecrire_cristaux_obtenus(joueur_id, cristaux)
    return cristaux


def a_obtenu_cle(ile_id: str) -> bool:
    """Le joueur courant a-t-il obtenu la clé de l'île ?"""
    joueur_id = _joueur_id_ou_erreur()
    return ile_id in lire_cles_obtenues(joueur_id)


def a_obtenu_cristal(ile_id: str, concept_id: str) -> bool:
    """Le joueur courant a-t-il obtenu ce cristal ?"""
    joueur_id = _joueur_id_ou_erreur()
    cristaux = lire_cristaux_obtenus(joueur_id)
    return concept_id in cristaux.get(ile_id, {})


def nombre_cles_obtenues() -> int:
    """Compteur global de clés."""
    joueur_id = _joueur_id_ou_erreur()
    return len(lire_cles_obtenues(joueur_id))


def nombre_cristaux_obtenus() -> int:
    """Compteur global de cristaux (toutes îles confondues)."""
    joueur_id = _joueur_id_ou_erreur()
    cristaux = lire_cristaux_obtenus(joueur_id)
    return sum(len(c) for c in cristaux.values())


def cles_obtenues() -> dict:
    """
    Dict complet des clés avec leurs dates d'obtention.
    Format : {"ile_1": "2026-07-05T14:23:00Z", ...}
    """
    joueur_id = _joueur_id_ou_erreur()
    return lire_cles_obtenues(joueur_id)


def cristaux_obtenus() -> dict:
    """
    Dict complet des cristaux avec dates.
    Format : {"ile_1": {"C1": "2026-07-05T14:23:00Z", "C2": "..."}, ...}
    """
    joueur_id = _joueur_id_ou_erreur()
    return lire_cristaux_obtenus(joueur_id)


def reset_recompenses() -> None:
    """
    Efface toutes les clés et cristaux du joueur courant.
    Pour debug uniquement.
    """
    joueur_id = _joueur_id_ou_erreur()
    ecrire_cles_obtenues(joueur_id, {})
    ecrire_cristaux_obtenus(joueur_id, {})
