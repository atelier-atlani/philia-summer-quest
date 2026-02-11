"""training/quiz.py – Quiz engine: load YAML banks, scoring, selection.

Scoring:
  - Bonne réponse : 100 pts
  - Bonus rapidité (< 50% du time_limit) : +50 pts
  - Mauvaise réponse : 0 pts
  - Score final = pourcentage du max possible
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# --- Constants ---
QUIZ_BANK_DIR = Path(__file__).resolve().parent / "quiz_bank"
PTS_CORRECT = 100
PTS_SPEED_BONUS = 50
SPEED_BONUS_THRESHOLD = 0.5  # < 50% du time_limit
DEFAULT_TIME_LIMIT = 25
QUESTIONS_PER_QUIZ = 8


# --- Data classes ---
@dataclass
class QuizQuestion:
    question: str
    choices: List[str]
    correct: int  # 0-indexed
    explanation_rag_query: str
    difficulty: int  # 1-3
    time_limit: int  # seconds

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QuizQuestion":
        return cls(
            question=d["question"],
            choices=d["choices"],
            correct=d["correct"],
            explanation_rag_query=d.get("explanation_rag_query", ""),
            difficulty=d.get("difficulty", 1),
            time_limit=d.get("time_limit", DEFAULT_TIME_LIMIT),
        )


@dataclass
class QuizResult:
    """Result for a single answered question."""
    question_index: int
    chosen: int  # 0-indexed choice
    correct: int
    is_correct: bool
    elapsed_seconds: float
    time_limit: int
    points: int
    speed_bonus: bool


@dataclass
class QuizSession:
    """Full quiz session state."""
    questions: List[QuizQuestion] = field(default_factory=list)
    results: List[QuizResult] = field(default_factory=list)
    current_index: int = 0

    @property
    def is_complete(self) -> bool:
        return self.current_index >= len(self.questions)

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def current_question(self) -> Optional[QuizQuestion]:
        if self.is_complete:
            return None
        return self.questions[self.current_index]

    @property
    def total_points(self) -> int:
        return sum(r.points for r in self.results)

    @property
    def max_points(self) -> int:
        return len(self.questions) * (PTS_CORRECT + PTS_SPEED_BONUS)

    @property
    def score_pct(self) -> int:
        if self.max_points == 0:
            return 0
        return round(self.total_points / self.max_points * 100)

    @property
    def correct_count(self) -> int:
        return sum(1 for r in self.results if r.is_correct)

    def answer(self, chosen: int, elapsed_seconds: float) -> QuizResult:
        """Record answer for current question and advance."""
        q = self.questions[self.current_index]
        is_correct = chosen == q.correct
        speed_bonus = is_correct and elapsed_seconds < q.time_limit * SPEED_BONUS_THRESHOLD
        points = 0
        if is_correct:
            points = PTS_CORRECT
            if speed_bonus:
                points += PTS_SPEED_BONUS

        result = QuizResult(
            question_index=self.current_index,
            chosen=chosen,
            correct=q.correct,
            is_correct=is_correct,
            elapsed_seconds=elapsed_seconds,
            time_limit=q.time_limit,
            points=points,
            speed_bonus=speed_bonus,
        )
        self.results.append(result)
        self.current_index += 1
        return result

    # --- serialization ---
    def to_dict(self) -> Dict[str, Any]:
        return {
            "questions": [
                {
                    "question": q.question,
                    "choices": q.choices,
                    "correct": q.correct,
                    "explanation_rag_query": q.explanation_rag_query,
                    "difficulty": q.difficulty,
                    "time_limit": q.time_limit,
                }
                for q in self.questions
            ],
            "results": [
                {
                    "question_index": r.question_index,
                    "chosen": r.chosen,
                    "correct": r.correct,
                    "is_correct": r.is_correct,
                    "elapsed_seconds": r.elapsed_seconds,
                    "time_limit": r.time_limit,
                    "points": r.points,
                    "speed_bonus": r.speed_bonus,
                }
                for r in self.results
            ],
            "current_index": self.current_index,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QuizSession":
        qs = cls(
            questions=[QuizQuestion.from_dict(qd) for qd in d["questions"]],
            results=[
                QuizResult(**rd) for rd in d.get("results", [])
            ],
            current_index=d.get("current_index", 0),
        )
        return qs


# --- Bank loading ---
def _load_all_banks() -> List[Dict[str, Any]]:
    """Load all YAML quiz bank files."""
    banks = []
    if not QUIZ_BANK_DIR.exists():
        return banks
    for f in sorted(QUIZ_BANK_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            if data and "questions" in data:
                banks.append(data)
        except Exception:
            continue
    return banks


def select_questions(theme_title: str, count: int = QUESTIONS_PER_QUIZ) -> List[QuizQuestion]:
    """Select quiz questions matching a session theme.

    Strategy:
    1. Find banks whose theme_tags contain the theme_title.
    2. Collect all their questions.
    3. If not enough, add questions from other banks.
    4. Shuffle and pick `count` questions, mixing difficulties.
    """
    banks = _load_all_banks()
    matched: List[Dict[str, Any]] = []
    other: List[Dict[str, Any]] = []

    for bank in banks:
        tags = bank.get("theme_tags", [])
        if theme_title in tags:
            matched.extend(bank["questions"])
        else:
            other.extend(bank["questions"])

    # If no match at all, use everything
    if not matched:
        matched = other
        other = []

    random.shuffle(matched)

    # Fill up to count
    pool = matched[:count]
    if len(pool) < count:
        random.shuffle(other)
        pool.extend(other[: count - len(pool)])

    # Sort by difficulty for a progressive quiz
    pool.sort(key=lambda q: q.get("difficulty", 1))

    return [QuizQuestion.from_dict(q) for q in pool[:count]]


def create_quiz_session(theme_title: str) -> QuizSession:
    """Create a new quiz session for the given theme."""
    questions = select_questions(theme_title)
    return QuizSession(questions=questions)


# --- Feedback helpers (style terrain) ---
def feedback_correct(speed_bonus: bool) -> str:
    """Encouraging feedback for correct answer."""
    if speed_bonus:
        return random.choice([
            "Bonne réponse, et rapide en plus ! C'est le réflexe terrain.",
            "Exactement ! Tu as le bon automatisme, et vite.",
            "Parfait, réponse juste et réactive. Continue comme ça.",
        ])
    return random.choice([
        "Bonne réponse ! C'est ça le réflexe terrain.",
        "Exactement. Tu as le bon raisonnement.",
        "Juste. C'est comme ça qu'on fait sur le terrain.",
        "Bien joué. Tu maîtrises ce point.",
    ])


def feedback_wrong(correct_choice: str) -> str:
    """Constructive feedback for wrong answer."""
    return random.choice([
        f"Pas tout à fait. La bonne réponse : « {correct_choice} ». "
        "C'est un point à retravailler en situation.",
        f"Non, la réponse attendue était : « {correct_choice} ». "
        "Prends note, ça reviendra en rendez-vous.",
        f"Raté sur celle-ci. Retiens : « {correct_choice} ». "
        "C'est en pratiquant qu'on ancre les réflexes.",
    ])


def feedback_final(score_pct: int, correct: int, total: int) -> str:
    """Final score feedback, terrain style."""
    if score_pct >= 80:
        return (
            f"Excellent : {correct}/{total} bonnes réponses ({score_pct}%). "
            "Tu as de solides bases terrain. Continue à les appliquer en rendez-vous."
        )
    if score_pct >= 50:
        return (
            f"Pas mal : {correct}/{total} bonnes réponses ({score_pct}%). "
            "Quelques points à consolider, mais la direction est bonne."
        )
    return (
        f"Score : {correct}/{total} bonnes réponses ({score_pct}%). "
        "C'est normal de tâtonner au début. Revois les points clés "
        "et repasse le quiz demain, tu verras la différence."
    )
