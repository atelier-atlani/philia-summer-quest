"""
training/marche_module.py – Runner mini-cours marché immobilier.

Extrait le contenu des modules markdown et génère un cours personnalisé
enrichi de données DVF locales selon la ville de travail du stagiaire.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from training.modules.marche.apis import DVFConnector


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class MarcheModuleConfig:
    """Configuration d'un mini-cours marché pour une session."""
    modules_ids: List[int]
    ville_travail: Optional[str] = None
    include_dvf_report: bool = True


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

class MarcheModuleRunner:
    """Génère le contenu d'un mini-cours marché à partir des fichiers markdown."""

    MODULES_DIR = Path("training/modules/marche/modules")

    # Mapping plage → fichier (ordre important : évalué dans l'ordre)
    _FILE_MAP = [
        (range(1, 7),   "01_fondamentaux_marche_1-20.md"),
        (range(7, 21),  "02_analyse_marche_france_7-20.md"),
        (range(21, 41), "03_juridique_prospection_21-40.md"),
        (range(41, 61), "04_technique_estimation_41-60.md"),
        (range(61, 81), "05_marketing_vente_61-80.md"),
        (range(81, 101),"06_operationnel_local_81-100.md"),
    ]

    def __init__(self, config: MarcheModuleConfig):
        self.config = config
        self.dvf = DVFConnector()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def generate_course(self) -> str:
        """Génère le contenu Markdown complet du cours."""
        parts: List[str] = ["# 📊 Mini-cours : Marché Immobilier\n"]

        for module_id in self.config.modules_ids:
            content = self._extract_module_content(module_id)
            parts.append(content)
            parts.append("\n\n---\n")

        if self.config.ville_travail and self.config.include_dvf_report:
            parts.append(self._generate_local_section())

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _get_module_file(self, module_id: int) -> Path:
        for module_range, filename in self._FILE_MAP:
            if module_id in module_range:
                return self.MODULES_DIR / filename
        raise ValueError(f"Module {module_id} introuvable (hors plage 1-100)")

    def _extract_module_content(self, module_id: int) -> str:
        try:
            file_path = self._get_module_file(module_id)
        except ValueError as e:
            return f"⚠️ {e}"

        if not file_path.exists():
            return f"❌ Fichier {file_path.name} introuvable"

        content = file_path.read_text(encoding="utf-8")

        # Match depuis "### Module N :" jusqu'au prochain "### Module" ou "## " ou fin
        pattern = rf"### Module {module_id} :.*?(?=\n### Module |\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return match.group(0).strip()

        return f"⚠️ Module {module_id} non trouvé dans {file_path.name}"

    def _generate_local_section(self) -> str:
        ville = self.config.ville_travail
        section = f"\n## 📍 Focus Marché : {ville}\n\n"
        section += f"Voici comment ces concepts s'appliquent concrètement sur **{ville}**.\n\n"

        try:
            report = self.dvf.generate_market_report(
                adresse="Centre-ville",
                ville=ville,
                radius_m=1000,
            )
            section += report
        except Exception:
            section += f"⚠️ Données DVF pour {ville} temporairement indisponibles.\n"

        return section


# ---------------------------------------------------------------------------
# Helper : modules par session
# ---------------------------------------------------------------------------

def get_marche_modules_for_session(session_num: int) -> List[int]:
    """Retourne 1 ID de module marché par session, rotation modulo 100.

    Session 1 → [1], Session 2 → [2], …, Session 100 → [100],
    Session 101 → [1], … (boucle sur les 104 sessions).
    """
    TOTAL_MODULES = 100
    idx = (session_num - 1) % TOTAL_MODULES
    return [idx + 1]


# ---------------------------------------------------------------------------
# Test standalone
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("🧪 Test MarcheModuleRunner\n" + "=" * 50)

    config = MarcheModuleConfig(
        modules_ids=[1, 2],
        ville_travail="Lyon",
        include_dvf_report=True,
    )
    runner = MarcheModuleRunner(config)
    course = runner.generate_course()

    print(course[:800])
    print(f"\n...\n\nLongueur totale : {len(course)} caractères")
