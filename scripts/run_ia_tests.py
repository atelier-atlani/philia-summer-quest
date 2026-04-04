"""
scripts/run_ia_tests.py — Exécute les 10 tests d'assimilation marché avec scoring IA.

Usage :
    .venv/bin/python scripts/run_ia_tests.py [--test <id>] [--output <fichier.md>]

Options :
    --test <id>       N'exécuter qu'un seul test (ex: --test 01)
    --output <path>   Chemin du rapport Markdown (défaut: data/test_results_ia.md)
"""

from __future__ import annotations

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Racine projet
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from training.modules.marche.test_runner import MarcheTestRunner, IAScorer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tests d'assimilation marché — scoring IA")
    parser.add_argument("--test", metavar="ID", help="Exécuter un seul test (ex: 01, 05)")
    parser.add_argument("--output", metavar="PATH",
                        default="data/test_results_ia.md",
                        help="Chemin du rapport Markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("=" * 65)
    print("🧪  TESTS D'ASSIMILATION MARCHÉ — SCORING IA")
    print("=" * 65)
    print()

    runner = MarcheTestRunner()

    # ----------------------------------------------------------------
    # Sélection des tests
    # ----------------------------------------------------------------
    if args.test:
        test_id = args.test.zfill(2)
        test_files = list(runner.TESTS_DIR.glob(f"test_{test_id}_*.yaml"))
        if not test_files:
            # Fallback : glob sur l'ID sans underscore
            test_files = list(runner.TESTS_DIR.glob(f"test_{test_id}*.yaml"))
        if not test_files:
            print(f"❌ Aucun fichier trouvé pour test ID '{args.test}'")
            return 1

        print(f"🔍 Mode test unique : {test_files[0].name}\n")
        try:
            test = runner.load_test(test_files[0])
        except Exception as e:
            print(f"❌ Erreur chargement : {e}")
            return 1

        print(f"  Test    : {test.test_id} — {test.titre}")
        print(f"  Ville   : {test.ville} / {test.quartier}")
        print(f"  Niveau  : {test.difficulte}")
        print()
        print("⏳ Appel agent formateur...\n")

        result = runner.score_test(test)

        print(f"Score   : {result.score:.0%}")
        print(f"Statut  : {'✅ Réussi' if result.passed else '❌ Échoué'}")
        print()
        print(result.feedback)
        print()
        if result.response_ia:
            print("─── Extrait réponse IA ─────────────────────────────────────")
            print(result.response_ia[:600])
            print("─────────────────────────────────────────────────────────────")

        return 0 if result.passed else 1

    # ----------------------------------------------------------------
    # Tous les tests
    # ----------------------------------------------------------------
    all_tests = runner.load_all_tests()
    print(f"📋 {len(all_tests)} tests chargés\n")
    print("🚀 Exécution (peut prendre 2-5 min)...\n")

    results = runner.run_scoring(verbose=True)

    # ----------------------------------------------------------------
    # Résumé console
    # ----------------------------------------------------------------
    total  = len(results)
    passed = sum(1 for r in results if r.passed)
    avg    = sum(r.score or 0 for r in results) / total if total else 0

    print()
    print("=" * 65)
    print("📊  RÉSUMÉ")
    print("=" * 65)
    print(f"Tests réussis  : {passed}/{total} ({passed / total * 100:.0f}%)")
    print(f"Score moyen    : {avg:.0%}  (seuil : {IAScorer.PASS_THRESHOLD:.0%})")
    print()

    sorted_r = sorted(results, key=lambda r: r.score or 0, reverse=True)
    print("🏆 Top 3 :")
    for r in sorted_r[:3]:
        print(f"  {r.score:.0%}  Test {r.test_id} — {r.titre}")
    print()
    print("⚠️  Bottom 3 :")
    for r in sorted_r[-3:]:
        status = "✅" if r.passed else "❌"
        print(f"  {status} {r.score:.0%}  Test {r.test_id} — {r.titre}")

    # Modules les plus souvent en échec
    missing_counter: dict[str, int] = {}
    for r in results:
        for arg in r.arguments_missing:
            missing_counter[arg] = missing_counter.get(arg, 0) + 1

    if missing_counter:
        print()
        print("📌 Arguments les plus souvent manquants :")
        top_missing = sorted(missing_counter.items(), key=lambda x: -x[1])[:5]
        for arg, count in top_missing:
            print(f"  ×{count}  {arg[:75]}")

    # ----------------------------------------------------------------
    # Rapport Markdown
    # ----------------------------------------------------------------
    print()
    report = runner.generate_report(results, mode="scoring")

    # Ajouter horodatage en entête
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"<!-- Généré le {ts} par run_ia_tests.py -->\n\n" + report

    output_path = _ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"📝 Rapport sauvegardé : {output_path}")

    # ----------------------------------------------------------------
    # Code de sortie
    # ----------------------------------------------------------------
    if passed == total:
        print("\n✅ TOUS LES TESTS RÉUSSIS !\n")
        return 0
    elif passed >= total * 0.6:
        print(f"\n🟡 {passed}/{total} réussis — améliorations possibles.\n")
        return 0
    else:
        print(f"\n❌ Trop d'échecs ({total - passed}/{total}) — révision agent recommandée.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
