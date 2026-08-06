"""
jeu/recompenses.py — Module métier récompenses — Philia Summer Quest.
Sprint 3 T7

Responsabilité : gérer l'obtention et la lecture des clés et cristaux
du joueur courant. Persiste en base via data_layer.joueurs.

Ce module porte aussi la PROGRESSION dans une île — parce qu'elle ne se
stocke pas : elle se DÉRIVE des cristaux déjà gagnés (cf. session_courante()).
Aucun champ persistant de progression n'existe, et il ne doit pas en exister :
un cristal gagné EST la preuve qu'une session est validée.

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
    concepts_ile(ile_id)                     -> list[str]
    session_courante(ile_id)                 -> int | None
    ile_terminee(ile_id)                     -> bool
    reset_recompenses()                      -> None
"""

from __future__ import annotations

from datetime import datetime, timezone

from config.constants import CRISTAUX_CATALOGUE
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


# ── Progression dans une île — dérivée, jamais stockée ────────────────────────

def concepts_ile(ile_id: str) -> list[str]:
    """
    Ids des concepts d'une île, dans l'ordre de jeu : ["C1", ..., "C5"].

    Le catalogue des cristaux (config.constants) est la seule liste existante
    des concepts d'une île — on la réutilise plutôt que d'en écrire une seconde.
    Repli sur C1..C5 pour une île absente du catalogue (Île 6, D16) : toutes les
    îles du programme ont cinq sessions.
    """
    catalogue = CRISTAUX_CATALOGUE.get(ile_id, {}).get("cristaux", {})
    if not catalogue:
        return [f"C{i}" for i in range(1, 6)]
    return sorted(catalogue, key=lambda cid: int(cid.lstrip("C") or 0))


def session_courante(ile_id: str) -> int | None:
    """
    Numéro (1-based) de la session que l'enfant doit jouer maintenant dans
    cette île : la première dont le cristal n'est pas encore gagné.

    Retourne None quand les cinq cristaux sont là — l'île est terminée, il n'y
    a plus de session à proposer (l'appelant route vers la fin d'île).

    C'est LA fonction de progression du jeu, et elle ne lit aucun état de
    session Streamlit : les coffres gagnés en base sont la source de vérité.
    Une reprise après fermeture du navigateur retombe donc exactement sur la
    bonne session.

    Sans joueur en base (onboarding non terminé), la quête commence : 1.
    """
    try:
        cristaux_ile = cristaux_obtenus().get(ile_id, {})
    except RuntimeError:
        cristaux_ile = {}
    for numero, concept_id in enumerate(concepts_ile(ile_id), start=1):
        if concept_id not in cristaux_ile:
            return numero
    return None


def ile_terminee(ile_id: str) -> bool:
    """Vrai quand tous les cristaux de l'île sont gagnés (plus aucune session)."""
    return session_courante(ile_id) is None


def reset_recompenses() -> None:
    """
    Efface toutes les clés et cristaux du joueur courant.
    Pour debug uniquement.
    """
    joueur_id = _joueur_id_ou_erreur()
    ecrire_cles_obtenues(joueur_id, {})
    ecrire_cristaux_obtenus(joueur_id, {})
