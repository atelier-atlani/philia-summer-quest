"""
training/modules/marche/test_runner.py – Runner tests d'assimilation marché.

Charge les cas critiques YAML, valide la structure, et score les réponses de
l'agent formateur selon les critères définis (arguments_cles + erreurs_a_eviter).

Modes :
  - validation  : vérification structure YAML uniquement (sans appel IA)
  - scoring     : appel agent formateur + scoring automatique
"""

from __future__ import annotations

import re
import sys
import textwrap
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
    passed: Optional[bool] = None
    score: Optional[float] = None
    feedback: str = ""
    # Champs scoring IA
    response_ia: str = ""
    arguments_found: List[str] = field(default_factory=list)
    arguments_missing: List[str] = field(default_factory=list)
    errors_detected: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# IAScorer
# ---------------------------------------------------------------------------

_STOPWORDS_FR = {
    "pour", "avec", "dans", "cette", "sont", "peut", "plus", "tous",
    "leur", "elle", "être", "faire", "tout", "sans", "très", "bien",
    "aussi", "même", "donc", "autre", "vous", "mais", "comme", "lors",
    "cela", "dont", "quel", "quand", "faut", "doit", "sera", "seul",
}


class IAScorer:
    """Score une réponse IA par rapport aux critères d'un TestCase."""

    ARG_MATCH_RATIO  = 0.35  # 35 % des mots-clés de l'argument (seuil de couverture)
    ERR_MATCH_RATIO  = 0.65  # 65 % des mots-clés de l'erreur (détection)
    PASS_THRESHOLD   = 0.60  # seuil pour passed=True

    # Mots signalant que l'agent mentionne l'erreur pour la prévenir (pas la commettre)
    _NEGATION_PATTERNS = re.compile(
        r"\b(ne\s+pas|n'est\s+pas|ne\s+faut\s+pas|ne\s+jamais|sans\s+|"
        r"éviter|évitez|attention|interdit|interdite|risque|erreur|faux|"
        r"incorrect|incorrect|ne\s+pas\s+|pas\s+de\s+|ni\s+|"
        r"contrairement|incorrectement|abusif|illégal)\b",
        re.IGNORECASE,
    )

    def _keywords(self, text: str) -> List[str]:
        """Tokens significatifs (≥4 chars, hors stopwords)."""
        words = re.findall(r'\b\w{4,}\b', text.lower())
        return list({w for w in words if w not in _STOPWORDS_FR})

    def _match_ratio(self, phrase: str, response_lower: str) -> float:
        kw = self._keywords(phrase)
        if not kw:
            return 0.0
        found = sum(1 for w in kw if w in response_lower)
        return found / len(kw)

    def _error_in_negation_context(self, error_phrase: str, response: str) -> bool:
        """
        Retourne True si les mots-clés de l'erreur apparaissent dans une phrase
        qui contient aussi un marqueur de négation/mise en garde.

        Cela évite de pénaliser un agent qui *mentionne* l'erreur pour l'écarter
        (ex. "La rénovation esthétique ne garantit pas l'amélioration DPE").
        """
        kw = self._keywords(error_phrase)
        if not kw:
            return False

        # Découper en phrases
        sentences = re.split(r"[.!?\n]", response.lower())
        for sent in sentences:
            # La phrase contient-elle ≥40% des mots-clés de l'erreur ?
            kw_in_sent = sum(1 for w in kw if w in sent)
            if kw_in_sent / len(kw) >= 0.40:
                # Contient-elle aussi un marqueur de négation ?
                if self._NEGATION_PATTERNS.search(sent):
                    return True
        return False

    def score(self, response: str, test: TestCase) -> Tuple[float, Dict]:
        """
        Retourne (score_final, detail_dict).

        score_final = 0.6 × score_arguments + 0.4 × score_erreurs
        """
        resp_lower = response.lower()

        # -- Arguments clés (60 %) --
        args_found, args_missing = [], []
        for arg in test.arguments_cles:
            if self._match_ratio(arg, resp_lower) >= self.ARG_MATCH_RATIO:
                args_found.append(arg)
            else:
                args_missing.append(arg)

        n_args = len(test.arguments_cles)
        score_args = len(args_found) / n_args if n_args else 1.0

        # -- Erreurs à éviter (40 %) — pénalité si détectées sans négation --
        errors_detected = []
        for err in test.erreurs_a_eviter:
            if self._match_ratio(err, resp_lower) >= self.ERR_MATCH_RATIO:
                # Ne pénaliser que si l'erreur n'est pas mentionnée dans un
                # contexte de mise en garde (négation / prévention)
                if not self._error_in_negation_context(err, response):
                    errors_detected.append(err)

        n_errs = len(test.erreurs_a_eviter)
        score_errs = 1.0 - (len(errors_detected) / n_errs) if n_errs else 1.0

        score_final = round(0.6 * score_args + 0.4 * score_errs, 4)

        detail = {
            "score_args":       round(score_args, 4),
            "score_errs":       round(score_errs, 4),
            "args_found":       args_found,
            "args_missing":     args_missing,
            "errors_detected":  errors_detected,
        }
        return score_final, detail

    def qualitative_label(self, score: float) -> str:
        if score >= 0.80:
            return "✅ Excellent — Maîtrise complète"
        if score >= 0.60:
            return "🟡 Bien — Quelques points à améliorer"
        if score >= 0.40:
            return "🟠 Moyen — Lacunes importantes"
        return "❌ Insuffisant — Révision nécessaire"

    def feedback_text(self, score: float, detail: Dict) -> str:
        lines = [
            self.qualitative_label(score),
            (f"Arguments : {len(detail['args_found'])}/{len(detail['args_found']) + len(detail['args_missing'])} "
             f"({detail['score_args']:.0%})  |  "
             f"Erreurs détectées : {len(detail['errors_detected'])}  |  "
             f"Score erreurs : {detail['score_errs']:.0%}"),
            "",
        ]
        if detail["args_found"]:
            lines.append("**Arguments couverts :**")
            for a in detail["args_found"][:6]:
                lines.append(f"  ✓ {a}")
            if len(detail["args_found"]) > 6:
                lines.append(f"  … et {len(detail['args_found']) - 6} autres")
            lines.append("")

        if detail["args_missing"]:
            lines.append("**Arguments manquants :**")
            for a in detail["args_missing"][:6]:
                lines.append(f"  ✗ {a}")
            if len(detail["args_missing"]) > 6:
                lines.append(f"  … et {len(detail['args_missing']) - 6} autres")
            lines.append("")

        if detail["errors_detected"]:
            lines.append("**Erreurs présentes dans la réponse :**")
            for e in detail["errors_detected"]:
                lines.append(f"  ⚠ {e}")

        return "\n".join(lines)


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
    # Scoring IA
    # ------------------------------------------------------------------

    def score_test(self, test: TestCase) -> TestResult:
        """
        Appelle repondre_comme_formateur() et score la réponse.
        Nécessite que agent_formateur soit importable depuis la racine.
        """
        try:
            import agent_formateur as af
        except ImportError as e:
            return TestResult(
                test_id=test.test_id, titre=test.titre,
                difficulte=test.difficulte, ville=test.ville,
                modules_concernes=test.modules_concernes,
                loaded=True, passed=False, score=0.0,
                error=f"agent_formateur introuvable : {e}",
                feedback="❌ Import impossible",
            )

        # Construire le prompt : contexte + blocage + prompt_test
        prompt_parts = []
        if test.contexte.strip():
            prompt_parts.append(f"Contexte :\n{test.contexte.strip()}")
        if test.blocage.strip():
            prompt_parts.append(f"Points de blocage à traiter :\n{test.blocage.strip()}")
        prompt_parts.append(test.prompt_test.strip())
        full_prompt = "\n\n".join(prompt_parts)

        try:
            response = af.repondre_comme_formateur(full_prompt)
        except Exception as e:
            return TestResult(
                test_id=test.test_id, titre=test.titre,
                difficulte=test.difficulte, ville=test.ville,
                modules_concernes=test.modules_concernes,
                loaded=True, passed=False, score=0.0,
                error=str(e),
                feedback=f"❌ Erreur appel agent : {traceback.format_exc(limit=3)}",
            )

        scorer = IAScorer()
        score_final, detail = scorer.score(response, test)

        return TestResult(
            test_id=test.test_id,
            titre=test.titre,
            difficulte=test.difficulte,
            ville=test.ville,
            modules_concernes=test.modules_concernes,
            loaded=True,
            passed=(score_final >= IAScorer.PASS_THRESHOLD),
            score=score_final,
            feedback=scorer.feedback_text(score_final, detail),
            response_ia=response[:1000],
            arguments_found=detail["args_found"],
            arguments_missing=detail["args_missing"],
            errors_detected=detail["errors_detected"],
        )

    def run_scoring(self, verbose: bool = True) -> List[TestResult]:
        """Score tous les tests avec l'agent formateur."""
        tests = self.load_all_tests()
        results = []
        for i, t in enumerate(tests, 1):
            if verbose:
                diff = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}.get(t.difficulte, "⚪")
                print(f"  [{i:02d}/{len(tests)}] {diff} Test {t.test_id} : {t.titre[:55]}...")
            result = self.score_test(t)
            if verbose:
                status = "✅" if result.passed else "❌"
                print(f"         {status} Score : {result.score:.0%}")
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # Rapport
    # ------------------------------------------------------------------

    def generate_report(self, results: List[TestResult], mode: str = "validation") -> str:
        """Génère un rapport Markdown des résultats (validation ou scoring)."""
        total = len(results)
        if total == 0:
            return "⚠️ Aucun test trouvé."

        passed = sum(1 for r in results if r.passed is True)
        avg_score = sum(r.score or 0 for r in results) / total

        is_scoring = mode == "scoring"
        title = "# 🧪 Rapport Tests d'Assimilation Marché — Scoring IA\n" if is_scoring \
                else "# 🧪 Rapport Tests d'Assimilation Marché\n"

        report_lines = [
            title,
            f"**Mode** : {mode}",
            f"**Tests** : {total}",
            f"**Réussis** : {passed}/{total} ({passed / total * 100:.0f}%)",
            f"**Score moyen** : {avg_score:.0%}",
        ]
        if is_scoring:
            report_lines.append(f"**Seuil validation** : {IAScorer.PASS_THRESHOLD:.0%}")
        report_lines += ["", "---", "", "## Détails par test", ""]

        diff_icons = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}
        sorted_results = sorted(results, key=lambda r: r.score or 0, reverse=True) \
                         if is_scoring else results

        for r in sorted_results:
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
            ]

            if is_scoring and r.response_ia:
                report_lines += [
                    "",
                    "<details><summary>Extrait réponse IA</summary>",
                    "",
                    textwrap.indent(r.response_ia.strip(), "> "),
                    "",
                    "</details>",
                ]

            report_lines.append("")

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
