"""training/profile.py – UserProfile dataclass for trainee personalization.

Stores:
  - prenom, niveau, role, specialites
  - objectif_principal, points_faibles, format_prefere
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


# --- Allowed values ---
NIVEAUX = ["debutant", "confirme", "expert"]
NIVEAUX_LABELS = {
    "debutant": "Débutant (moins d'un an)",
    "confirme": "Confirmé (1-3 ans)",
    "expert": "Expert (plus de 3 ans)",
}

ROLES = ["conseiller_vente", "conseiller_location", "manager", "independant"]
ROLES_LABELS = {
    "conseiller_vente": "Conseiller vente",
    "conseiller_location": "Conseiller location",
    "manager": "Manager d'agence",
    "independant": "Indépendant / mandataire",
}

SPECIALITES = ["acquereur", "vendeur", "estimation", "prospection", "management"]
SPECIALITES_LABELS = {
    "acquereur": "Acquéreur",
    "vendeur": "Vendeur",
    "estimation": "Estimation / ACM",
    "prospection": "Prospection",
    "management": "Management",
}

FORMATS = ["court", "detaille", "cas_pratique"]
FORMATS_LABELS = {
    "court": "Court et direct",
    "detaille": "Détaillé avec explications",
    "cas_pratique": "Cas pratiques en priorité",
}


@dataclass
class UserProfile:
    """Trainee profile for personalization."""

    prenom: str = ""
    niveau: str = "debutant"  # debutant | confirme | expert
    role: str = "conseiller_vente"
    specialites: List[str] = field(default_factory=list)
    objectif_principal: str = ""
    points_faibles: List[str] = field(default_factory=list)  # max 3
    format_prefere: str = "cas_pratique"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prenom": self.prenom,
            "niveau": self.niveau,
            "role": self.role,
            "specialites": self.specialites,
            "objectif_principal": self.objectif_principal,
            "points_faibles": self.points_faibles,
            "format_prefere": self.format_prefere,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "UserProfile":
        return cls(
            prenom=d.get("prenom", ""),
            niveau=d.get("niveau", "debutant"),
            role=d.get("role", "conseiller_vente"),
            specialites=d.get("specialites", []),
            objectif_principal=d.get("objectif_principal", ""),
            points_faibles=d.get("points_faibles", []),
            format_prefere=d.get("format_prefere", "cas_pratique"),
        )

    @property
    def niveau_label(self) -> str:
        return NIVEAUX_LABELS.get(self.niveau, self.niveau)

    @property
    def role_label(self) -> str:
        return ROLES_LABELS.get(self.role, self.role)

    @property
    def format_label(self) -> str:
        return FORMATS_LABELS.get(self.format_prefere, self.format_prefere)
