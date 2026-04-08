"""
training/modules/marche/cascade_analysis.py

Analyse cascade Global → National → Local.
Lit les données statiques de donnees_cles.yaml.
Pas d'appel LLM, pas d'API externe — lecture YAML + données 2026 fixées.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

_YAML_PATH = Path(__file__).parent / "donnees_cles.yaml"

# Données mondiales/macro figées pour 2026 (mise à jour manuelle si besoin)
_MACRO_2026 = {
    "taux_bce": 2.65,           # % (taux de dépôt BCE — avril 2026)
    "taux_fed": 4.50,           # %
    "inflation_france": 1.4,    # % (glissement annuel)
    "taux_credit_moyen": 3.60,  # % sur 20 ans
    "impact_budget": "−10% de budget d'achat par point de taux supplémentaire",
    "tendance": "stabilisation progressive après pic 2023-2024",
}

# Correspondance nom libre → clé YAML
_VILLE_ALIASES: Dict[str, str] = {
    "lyon": "lyon",
    "lyon 2": "lyon",
    "lyon 3": "lyon",
    "lyon 6": "lyon",
    "lyon 7": "lyon",
    "villeurbanne": "villeurbanne",
    "aubervilliers": "aubervilliers",
    "fort d'aubervilliers": "aubervilliers",
    "quatre chemins": "aubervilliers",
    "front populaire": "aubervilliers",
    "marseille": "marseille",
    "marseille 8": "marseille",
    "marseille 13": "marseille",
    "marseille 1": "marseille",
    "marseille 2": "marseille",
}


def _load_yaml() -> Dict[str, Any]:
    if not _YAML_PATH.exists():
        return {}
    try:
        return yaml.safe_load(_YAML_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _match_ville(ville_travail: str) -> Optional[str]:
    """Retourne la clé YAML correspondant à la ville saisie (insensible à la casse)."""
    if not ville_travail:
        return None
    key = ville_travail.lower().strip()
    if key in _VILLE_ALIASES:
        return _VILLE_ALIASES[key]
    # Recherche partielle
    for alias, yaml_key in _VILLE_ALIASES.items():
        if alias in key or key in alias:
            return yaml_key
    return None


def _prix_median(local_data: Dict[str, Any]) -> Optional[int]:
    """Calcule le prix médian à partir du bloc prix_median_m2."""
    bloc = local_data.get("prix_median_m2", {})
    if not bloc:
        return None
    values = [v for v in bloc.values() if isinstance(v, (int, float))]
    return round(sum(values) / len(values)) if values else None


def _prix_range(local_data: Dict[str, Any]) -> str:
    """Retourne la fourchette de prix (ex: '4 600 – 8 300 €/m²')."""
    bloc = local_data.get("prix_median_m2", {})
    values = sorted(v for v in bloc.values() if isinstance(v, (int, float)))
    if not values:
        return "N/D"
    if len(values) == 1:
        return f"{values[0]:,} €/m²".replace(",", " ")
    return f"{values[0]:,} – {values[-1]:,} €/m²".replace(",", " ")


class CascadeMarche:
    """Analyse cascade Global → National → Local à partir des données statiques 2026."""

    def __init__(self) -> None:
        self._data = _load_yaml()

    def analyze(self, ville_travail: Optional[str] = None) -> Dict[str, Any]:
        """
        Retourne un dict structuré :
          - mondial  : macro BCE/Fed/inflation
          - national : Loi Climat, ZAN, HCSF
          - local    : prix, infra, risques (selon ville_travail)
          - coherence: synthèse des 3 niveaux en 3 phrases
        """
        mondial = self._mondial()
        national = self._national()
        local = self._local(ville_travail)
        coherence = self._coherence(mondial, national, local, ville_travail)

        return {
            "mondial": mondial,
            "national": national,
            "local": local,
            "coherence": coherence,
            "ville": ville_travail or "Non précisée",
        }

    # ------------------------------------------------------------------
    # Niveaux
    # ------------------------------------------------------------------

    def _mondial(self) -> Dict[str, Any]:
        m = _MACRO_2026
        return {
            "taux_bce": m["taux_bce"],
            "taux_fed": m["taux_fed"],
            "inflation": m["inflation_france"],
            "taux_credit": m["taux_credit_moyen"],
            "impact_emprunt": m["impact_budget"],
            "tendance": m["tendance"],
        }

    def _national(self) -> Dict[str, Any]:
        r = self._data.get("reglementations", {})

        loi_climat = r.get("loi_climat", {})
        interdictions = loi_climat.get("interdictions_location", {})
        zan = r.get("zan", {})
        hcsf = r.get("hcsf", {})

        return {
            "loi_climat": {
                "interdiction_g": interdictions.get(2025, "G interdit à la location en 2025"),
                "interdiction_f": interdictions.get(2028, "F interdit en 2028"),
                "interdiction_e": interdictions.get(2034, "E interdit en 2034"),
                "aides": loi_climat.get("aides_disponibles", []),
            },
            "zan": {
                "loi": zan.get("loi", "Loi Climat et Résilience 2021"),
                "objectif_2031": zan.get("objectifs", {}).get(2031, "−50% artificialisation"),
                "impact_foncier": "Raréfaction du foncier constructible",
            },
            "hcsf": {
                "taux_endettement_max": hcsf.get("taux_endettement_max", 35),
                "derogation": hcsf.get("derogation_possible", True),
                "part_derogation": hcsf.get("part_dossiers_eligibles", 20),
            },
        }

    def _local(self, ville_travail: Optional[str]) -> Dict[str, Any]:
        yaml_key = _match_ville(ville_travail or "")
        if not yaml_key or yaml_key not in self._data:
            return {
                "disponible": False,
                "message": f"Données locales non disponibles pour « {ville_travail or 'ville non précisée'} ».",
            }

        loc = self._data[yaml_key]

        infra_raw = loc.get("infrastructure", {})
        infra_points = []
        for projet_nom, details in infra_raw.items():
            if not isinstance(details, dict):
                continue
            # Cas 1 : le projet est directement une fiche (a un impact_valorisation)
            impact = (details.get("impact_valorisation")
                      or details.get("impact_valorisation_estime")
                      or details.get("impact"))
            statut = details.get("statut", "")
            if impact:
                label = projet_nom.replace("_", " ").title()
                infra_points.append(f"{label} ({statut}) : {impact}" if statut else f"{label} : {impact}")
            else:
                # Cas 2 : le projet contient des sous-projets (ex: grand_paris_express → ligne_12)
                for sous_nom, info in details.items():
                    if not isinstance(info, dict):
                        continue
                    impact2 = (info.get("impact_valorisation")
                               or info.get("impact_valorisation_estime")
                               or info.get("impact"))
                    statut2 = info.get("statut", "")
                    if impact2:
                        label = sous_nom.replace("_", " ").title()
                        infra_points.append(f"{label} ({statut2}) : {impact2}" if statut2 else f"{label} : {impact2}")

        servitudes = list(loc.get("servitudes", {}).keys())

        return {
            "disponible": True,
            "ville_yaml": yaml_key,
            "prix_median": _prix_median(loc),
            "prix_range": _prix_range(loc),
            "infrastructures": infra_points[:3],  # top 3
            "servitudes": servitudes,
            "encadrement_loyers": bool(loc.get("encadrement_loyers")),
        }

    def _coherence(
        self,
        mondial: Dict,
        national: Dict,
        local: Dict,
        ville: Optional[str],
    ) -> str:
        taux = mondial["taux_credit"]
        hcsf_taux = national["hcsf"]["taux_endettement_max"]
        prix_range = local.get("prix_range", "N/D") if local.get("disponible") else "N/D"
        loi_g = national["loi_climat"]["interdiction_g"]

        return (
            f"Avec un crédit à {taux}% et le HCSF à {hcsf_taux}% d'endettement max, "
            f"le budget acquéreur est contraint — chaque point de taux enlève ~10% de capacité. "
            f"Les logements G sont interdits à la location ({loi_g}), "
            f"ce qui pèse sur les prix des passoires thermiques. "
            f"Sur votre marché local ({ville or 'N/D'} — {prix_range}), "
            f"les projets d'infrastructure sont le principal levier de valorisation à surveiller."
        )
