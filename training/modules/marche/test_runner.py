"""
training/modules/marche/test_runner.py – Runner tests d'assimilation marché.

Charge les cas critiques YAML et génère un rapport de couverture.
L'évaluation IA (scoring automatique) est un TODO futur.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# Support exécution directe ET import depuis la racine du projet
_HERE = Path(__file__).parent
_PROJECT_ROOT = _HERE.parents[3]  # training/modules/marche/ → projet racine
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    test_id: str
    titre: str
    difficulte: str
    contexte: str
    blocage: str
    modules_concernes: List[int]
    ville: str
    quartier: str
    type_bien: str
    solution_attendue: str
    arguments_cles: List[str]
    erreurs_a_eviter: List[str]
    prompt_test: str
    sources_data: List[str]


@dataclass
class TestResult:
    test_id: str
    titre: str
    difficulte: str
    ville: str
    modules_concernes: List[int]
    loaded: bool = True
    error: Optional[str] = None
    # Champs scoring (remplis par l'évaluateur IA futur)
    passed: Optional[bool] = None
    score: Optional[float] = None
    feedback: str = ""


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

class MarcheTestRunner:
    """Charge et référence les tests d'assimilation marché."""

    TESTS_DIR = Path(__file__).parent / "tests"

    # ------------------------------------------------------------------
    # Chargement
    # ------------------------------------------------------------------

    def load_test(self, test_file: Path) -> TestCase:
        """Charge un fichier YAML de test."""
        if not _YAML_AVAILABLE:
            raise ImportError("Le module 'pyyaml' est requis. Installez-le avec : pip install pyyaml")

        with open(test_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return TestCase(
            test_id=str(data.get("test_id", "")),
            titre=data.get("titre", ""),
            difficulte=data.get("difficulte", ""),
            contexte=data.get("contexte", ""),
            blocage=data.get("blocage", ""),
            modules_concernes=data.get("modules_concernes", []),
            ville=data.get("ville", ""),
            quartier=data.get("quartier", ""),
            type_bien=data.get("type_bien", ""),
            solution_attendue=data.get("solution_attendue", ""),
            arguments_cles=data.get("arguments_cles", []),
            erreurs_a_eviter=data.get("erreurs_a_eviter", []),
            prompt_test=data.get("prompt_test", ""),
            sources_data=data.get("sources_data", []),
        )

    def load_all_tests(self) -> List[TestCase]:
        """Charge tous les tests du répertoire."""
        tests = []
        for test_file in sorted(self.TESTS_DIR.glob("test_*.yaml")):
            try:
                tests.append(self.load_test(test_file))
            except Exception as e:
                print(f"⚠️  Erreur chargement {test_file.name} : {e}")
        return tests

    # ------------------------------------------------------------------
    # Validation structure (sans IA)
    # ------------------------------------------------------------------

    def validate_test(self, test: TestCase) -> TestResult:
        """Valide la structure d'un test (pas le contenu IA)."""
        errors = []

        if not test.titre:
            errors.append("Titre manquant")
        if not test.prompt_test.strip():
            errors.append("prompt_test vide")
        if not test.modules_concernes:
            errors.append("modules_concernes vide")
        if not test.arguments_cles:
            errors.append("arguments_cles vide")

        return TestResult(
            test_id=test.test_id,
            titre=test.titre,
            difficulte=test.difficulte,
            ville=test.ville,
            modules_concernes=test.modules_concernes,
            loaded=True,
            error="; ".join(errors) if errors else None,
            passed=(len(errors) == 0),
            score=1.0 if not errors else 0.0,
            feedback="Structure valide" if not errors else f"Erreurs : {', '.join(errors)}",
        )

    def run_validation(self) -> List[TestResult]:
        """Valide la structure de tous les tests (mode sans IA)."""
        tests = self.load_all_tests()
        return [self.validate_test(t) for t in tests]

    # ------------------------------------------------------------------
    # Rapport
    # ------------------------------------------------------------------

    def generate_report(self, results: List[TestResult], mode: str = "validation") -> str:
        """Génère un rapport Markdown des résultats."""
        total = len(results)
        if total == 0:
            return "⚠️ Aucun test trouvé."

        passed = sum(1 for r in results if r.passed is True)
        avg_score = sum(r.score or 0 for r in results) / total

        report_lines = [
            "# 🧪 Rapport Tests d'Assimilation Marché\n",
            f"**Mode** : {mode}",
            f"**Tests chargés** : {total}",
            f"**Tests valides** : {passed}/{total} ({passed / total * 100:.0f}%)",
            f"**Score moyen** : {avg_score:.0%}",
            "",
            "---",
            "",
            "## Détails par test",
            "",
        ]

        diff_icons = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}

        for r in results:
            status = "✅" if r.passed else ("❓" if r.passed is None else "❌")
            diff_icon = diff_icons.get(r.difficulte, "⚪")
            modules_str = ", ".join(f"M{m}" for m in r.modules_concernes[:5])
            if len(r.modules_concernes) > 5:
                modules_str += f" +{len(r.modules_concernes) - 5}"

            report_lines += [
                f"### {status} Test {r.test_id} — {r.titre}",
                f"- **Difficulté** : {diff_icon} {r.difficulte.capitalize()}",
                f"- **Ville** : {r.ville}",
                f"- **Modules** : {modules_str}",
                f"- **Score** : {r.score:.0%}" if r.score is not None else "- **Score** : —",
                f"- **Résultat** : {r.feedback}",
                "",
            ]

        return "\n".join(report_lines)

    # ------------------------------------------------------------------
    # Stats couverture modules
    # ------------------------------------------------------------------

    def coverage_stats(self, tests: List[TestCase]) -> Dict[int, int]:
        """Retourne le nombre de tests par module couvert."""
        coverage: Dict[int, int] = {}
        for test in tests:
            for module_id in test.modules_concernes:
                coverage[module_id] = coverage.get(module_id, 0) + 1
        return dict(sorted(coverage.items()))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    runner = MarcheTestRunner()

    # Chargement
    tests = runner.load_all_tests()
    print(f"✅ Tests chargés : {len(tests)}\n")

    if not tests:
        print("Aucun test trouvé dans :", runner.TESTS_DIR)
        sys.exit(1)

    # Résumé par test
    for t in tests:
        diff_icon = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}.get(t.difficulte, "⚪")
        print(f"  [{t.test_id}] {diff_icon} {t.titre} ({t.ville})")

    # Validation structure
    print("\n--- Validation structure ---")
    results = runner.run_validation()
    report = runner.generate_report(results, mode="validation structurelle")
    print(report)

    # Couverture modules
    coverage = runner.coverage_stats(tests)
    print("--- Modules couverts ---")
    print(f"Nombre de modules distincts testés : {len(coverage)}")
    for module_id, count in coverage.items():
        print(f"  Module {module_id:3d} : {count} test(s)")
