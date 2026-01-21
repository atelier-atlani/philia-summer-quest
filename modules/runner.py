# modules/runner.py
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


# --- Config ---
ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = ROOT / "modules"
DATA_DIR = ROOT / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"


@dataclass
class QuizQ:
    q: str
    choices: List[str]
    answer_index: int  # 0-based
    explain: str = ""


@dataclass
class Day:
    day: int
    title: str
    md_file: str
    warmup_q: str
    warmup_keywords: List[str]
    scenario_q: str
    scenario_keywords: List[str]
    quiz: List[QuizQ]


# ⚠️ Mapping volontairement simple:
# Jour 1 = 01_*.md
# Jour 2 = 03_*.md (on assume que c’est ton “jour 2” pour l’instant)
MODULE_01_DAYS: List[Day] = [
    Day(
        day=1,
        title="Mandat confiance au prix",
        md_file="01_mandat_confiance_au_prix.md",
        warmup_q="(Warm-up) Cite 2 actions concrètes pour cadrer le prix avec un vendeur.",
        warmup_keywords=["acm", "prix", "marché", "biens", "comparative", "analyse"],
        scenario_q=(
            "Mise en situation :\n"
            "Le vendeur dit : « Je ne baisse pas, mon voisin a vendu plus cher. »\n"
            "Réponds en 6 à 10 lignes, avec une posture formateur terrain."
        ),
        scenario_keywords=["acm", "marché", "biens", "vendus", "invendus", "prix"],
        quiz=[
            QuizQ(
                q="Quel objectif principal sert l’ACM dans une discussion prix ?",
                choices=[
                    "Prouver que l’agence a raison",
                    "Ancrer le prix sur des comparables du marché",
                    "Forcer le vendeur à signer",
                    "Éviter toute négociation",
                ],
                answer_index=1,
                explain="L’ACM sert à objectiver avec des comparables (vendus / à vendre / invendus).",
            ),
            QuizQ(
                q="Avant d’aborder une baisse, que dois-tu vérifier en priorité ?",
                choices=[
                    "Que le vendeur est sympathique",
                    "Que toutes les actions de promotion ont été faites",
                    "Que le voisin est d’accord",
                    "Que l’acheteur a un crédit",
                ],
                answer_index=1,
                explain="Logique stock : d’abord actions + retours, ensuite prix.",
            ),
        ],
    ),
    Day(
        day=2,
        title="Vente du service post-ACM",
        md_file="03_vente_du_service_post_ACM.md",
        warmup_q="(Warm-up) Donne 2 éléments concrets à montrer après une ACM pour vendre ton accompagnement.",
        warmup_keywords=["acm", "plan", "actions", "promotion", "suivi", "arguments"],
        scenario_q=(
            "Mise en situation :\n"
            "Après l’ACM, le vendeur dit : « Je vais réfléchir, je veux comparer les agences. »\n"
            "Réponds en 6 à 10 lignes en vendant le service (pas la marque)."
        ),
        scenario_keywords=["service", "accompagnement", "plan", "actions", "suivi", "promotion"],
        quiz=[
            QuizQ(
                q="Dans une vente du service, qu’est-ce qui convainc le plus ?",
                choices=[
                    "Les promesses vagues",
                    "Un plan d’actions clair + suivi",
                    "Une réduction d’honoraires",
                    "Un discours long",
                ],
                answer_index=1,
                explain="C’est le plan + le suivi qui matérialisent la valeur.",
            ),
            QuizQ(
                q="Quel est le risque si tu parles uniquement du prix sans service ?",
                choices=[
                    "Le vendeur achète plus vite",
                    "Tu te mets en concurrence directe",
                    "Le mandat devient exclusif",
                    "Tu gagnes du temps",
                ],
                answer_index=1,
                explain="Sans service, tu es comparé comme un “coût” uniquement.",
            ),
        ],
    ),
]


def _read_md(filename: str) -> str:
    path = MODULES_DIR / filename
    if not path.exists():
        return f"(Fichier introuvable : {filename})"
    return path.read_text(encoding="utf-8", errors="ignore")


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_progress() -> Dict[str, Any]:
    _ensure_data_dir()
    if not PROGRESS_FILE.exists():
        return {}
    try:
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_progress(p: Dict[str, Any]) -> None:
    _ensure_data_dir()
    PROGRESS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")


def _today_key() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _score_keywords(text: str, keywords: List[str]) -> int:
    t = (text or "").lower()
    hits = 0
    for k in keywords:
        if k.lower() in t:
            hits += 1
    return hits


def _read_multiline(prompt: str, end_token: str = "/fin") -> str:
    print(prompt)
    print(f"(Termine par {end_token})")
    lines: List[str] = []
    while True:
        line = input()
        if line.strip() == end_token:
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _ask_quiz(quiz: List[QuizQ]) -> int:
    score = 0
    for i, qq in enumerate(quiz, start=1):
        print(f"\nQ{i}. {qq.q}")
        for j, c in enumerate(qq.choices):
            letter = chr(ord("a") + j)
            print(f"  {letter}) {c}")
        ans = input("Réponse (a/b/c/d) : ").strip().lower()
        if not ans:
            print("  ❌ Réponse vide.")
            continue
        idx = ord(ans[0]) - ord("a")
        if idx == qq.answer_index:
            print("  ✅ Correct.")
            score += 1
        else:
            good = chr(ord("a") + qq.answer_index)
            print(f"  ❌ Faux. Bonne réponse : {good}) {qq.choices[qq.answer_index]}")
        if qq.explain:
            print(f"  ℹ️ {qq.explain}")
    return score


def run_module_day(module_id: str, day: Optional[int] = None) -> None:
    if module_id != "module_01":
        print(f"❌ Module inconnu: {module_id}")
        return

    days = MODULE_01_DAYS
    max_day = len(days)

    prog = _load_progress()
    m = prog.get(module_id, {})
    current_day = int(m.get("current_day", 1))

    if day is None:
        day = current_day

    if day < 1:
        day = 1
    if day > max_day:
        day = max_day

    d = next((x for x in days if x.day == day), None)
    if d is None:
        print(f"❌ Jour {day} introuvable.")
        return

    print("\n" + "=" * 70)
    print(f"📘 MODULE 01 — JOUR {d.day}/{max_day} : {d.title}")
    print("=" * 70)

    # 1) Micro-cours
    lesson = _read_md(d.md_file)
    print("\n🧠 Micro-cours (extrait du support) :\n")
    print(lesson.strip())

    # 2) Warm-up (si pas jour 1)
    warmup_score = 0
    if d.day > 1:
        print("\n🟦 Mise à l’épreuve des acquis (veille) :")
        warm = input(d.warmup_q + "\n> ").strip()
        warmup_score = _score_keywords(warm, d.warmup_keywords)
        print(f"Score warm-up (indices détectés) : {warmup_score}/{len(d.warmup_keywords)}")

    # 3) Mise en situation
    print("\n🎭 Mise en situation :")
    scenario_answer = _read_multiline(d.scenario_q, end_token="/fin")
    scen_score = _score_keywords(scenario_answer, d.scenario_keywords)
    print(f"Score mise en situation (indices détectés) : {scen_score}/{len(d.scenario_keywords)}")

    # 4) Quiz
    print("\n🧩 Quiz :")
    quiz_score = _ask_quiz(d.quiz)

    # 5) Score + synthèse
    total_quiz = len(d.quiz)
    print("\n" + "-" * 70)
    print("✅ Synthèse du jour")
    print(f"- Warm-up : {warmup_score}")
    print(f"- Mise en situation : {scen_score}")
    print(f"- Quiz : {quiz_score}/{total_quiz}")
    print("-" * 70)

    # Progression : on avance le jour si quiz >= 50%
    passed = (total_quiz == 0) or (quiz_score / max(total_quiz, 1) >= 0.5)
    next_day = min(d.day + 1, max_day) if passed else d.day

    hist = m.get("history", [])
    hist.append({
        "date": _today_key(),
        "day": d.day,
        "quiz_score": quiz_score,
        "quiz_total": total_quiz,
        "scenario_score": scen_score,
        "warmup_score": warmup_score,
        "passed": bool(passed),
    })

    prog[module_id] = {
        "current_day": next_day,
        "history": hist[-60:],  # on garde les 60 derniers
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    _save_progress(prog)

    print(f"\n➡️ Prochain jour proposé : Jour {next_day} (tape 'module' en FAQ ou passe par Mode 1).")
