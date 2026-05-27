"""
pedagogie/mentor_contract.py — Contrat de sortie du mentor Archimède.

Définit les structures de données qui encapsulent la réponse du mentor :
- EtatPedagogique : état interne de la session (mode actif, concept courant,
  compteurs de tentatives et d'indices utilisés).
- MentorOutput    : sortie structurée d'un tour de dialogue.

Ces structures sont alimentées par SessionEngine (session_engine.py).
Le LLM lui-même ne produit que du texte ; c'est l'engine qui construit l'état.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pedagogie.modes import Mode


@dataclass
class EtatPedagogique:
    mode: Mode = Mode.DECOUVERTE
    concept_id: str = ""
    nb_tentatives: int = 0
    # Nombre d'indices étagés déjà fournis (0-3, escalier de l'ADN §4).
    # Mis à jour manuellement ou via structured output — Sprint 3.
    indices_utilises: int = 0

    @property
    def niveau_escalier(self) -> int:
        """Niveau de décomposition courant (0 = question pleine, 3 = indice fort)."""
        return min(self.indices_utilises, 3)


@dataclass
class MentorOutput:
    message: str
    etat: EtatPedagogique = field(default_factory=EtatPedagogique)

    def est_valide(self) -> bool:
        return bool(self.message.strip())
