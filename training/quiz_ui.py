"""training/quiz_ui.py – Streamlit Kahoot-like quiz component.

Renders:
  - 4 colored answer buttons
  - Timer (elapsed since question shown)
  - Progress bar (questions answered / total)
  - Immediate feedback with RAG explanation
  - Final score screen
"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional

import streamlit as st

from training.quiz import (
    QuizSession,
    create_quiz_session,
    feedback_correct,
    feedback_final,
    feedback_wrong,
)

# Kahoot-style colors for the 4 answer buttons
_COLORS = ["#e21b3c", "#1368ce", "#d89e00", "#26890c"]
_ICONS = ["\u25b2", "\u25c6", "\u25cf", "\u25a0"]  # triangle, diamond, circle, square


def _init_quiz_state() -> None:
    """Initialize quiz-specific session state keys."""
    if "quiz_session" not in st.session_state:
        st.session_state.quiz_session = None
    if "quiz_q_start" not in st.session_state:
        st.session_state.quiz_q_start = None
    if "quiz_last_result" not in st.session_state:
        st.session_state.quiz_last_result = None
    if "quiz_rag_explanation" not in st.session_state:
        st.session_state.quiz_rag_explanation = None


def _get_or_create_quiz(theme_title: str) -> QuizSession:
    """Get existing quiz session or create a new one."""
    if st.session_state.quiz_session is not None:
        return QuizSession.from_dict(st.session_state.quiz_session)
    qs = create_quiz_session(theme_title)
    st.session_state.quiz_session = qs.to_dict()
    st.session_state.quiz_q_start = time.time()
    st.session_state.quiz_last_result = None
    st.session_state.quiz_rag_explanation = None
    return qs


def _save_quiz(qs: QuizSession) -> None:
    st.session_state.quiz_session = qs.to_dict()


def _reset_quiz() -> None:
    """Clear all quiz state."""
    st.session_state.quiz_session = None
    st.session_state.quiz_q_start = None
    st.session_state.quiz_last_result = None
    st.session_state.quiz_rag_explanation = None


def _render_progress_bar(qs: QuizSession) -> None:
    """Show quiz progress."""
    answered = len(qs.results)
    total = qs.total_questions
    pct = answered / total if total else 0.0
    st.progress(pct, text=f"Question {min(answered + 1, total)}/{total}")


def _render_timer() -> None:
    """Show elapsed time since question was displayed."""
    start = st.session_state.quiz_q_start
    if start is None:
        return
    elapsed = int(time.time() - start)
    st.caption(f"Temps écoulé : {elapsed}s")


def _answer_button_html(idx: int, text: str) -> str:
    """Generate styled button label with Kahoot icon."""
    icon = _ICONS[idx] if idx < len(_ICONS) else ""
    return f"{icon}  {text}"


def _render_question(qs: QuizSession, repondre_faq_fn: Optional[Callable] = None) -> None:
    """Render the current question with 4 colored buttons."""
    q = qs.current_question
    if q is None:
        return

    # Question text
    st.markdown(f"### Question {qs.current_index + 1}")
    st.markdown(f"**{q.question}**")

    # Timer info
    st.caption(f"Temps conseillé : {q.time_limit}s")
    _render_timer()

    st.markdown("---")

    # Ensure timer is started
    if st.session_state.quiz_q_start is None:
        st.session_state.quiz_q_start = time.time()

    # 4 answer buttons in a 2x2 grid
    col1, col2 = st.columns(2)
    cols = [col1, col2, col1, col2]

    for i, choice in enumerate(q.choices):
        color = _COLORS[i] if i < len(_COLORS) else "#666"
        label = _answer_button_html(i, choice)
        with cols[i]:
            if st.button(
                label,
                key=f"quiz_choice_{qs.current_index}_{i}",
                use_container_width=True,
            ):
                # Calculate elapsed time
                start = st.session_state.quiz_q_start or time.time()
                elapsed = time.time() - start

                # Record answer
                result = qs.answer(i, elapsed)
                _save_quiz(qs)

                # Store result for feedback display
                st.session_state.quiz_last_result = {
                    "is_correct": result.is_correct,
                    "speed_bonus": result.speed_bonus,
                    "points": result.points,
                    "chosen": result.chosen,
                    "correct": result.correct,
                    "correct_text": q.choices[q.correct],
                    "elapsed": result.elapsed_seconds,
                    "rag_query": q.explanation_rag_query,
                }
                # Fetch RAG explanation
                st.session_state.quiz_rag_explanation = None
                if repondre_faq_fn and q.explanation_rag_query:
                    try:
                        explanation = repondre_faq_fn(q.explanation_rag_query)
                        st.session_state.quiz_rag_explanation = explanation
                    except Exception:
                        pass

                st.session_state.quiz_q_start = None
                st.rerun()


def _render_feedback() -> None:
    """Render feedback for the last answered question."""
    lr = st.session_state.quiz_last_result
    if lr is None:
        return

    if lr["is_correct"]:
        st.success(feedback_correct(lr["speed_bonus"]))
        pts_text = f"+{lr['points']} pts"
        if lr["speed_bonus"]:
            pts_text += " (bonus rapidité !)"
        st.markdown(f"**{pts_text}**")
    else:
        st.error(feedback_wrong(lr["correct_text"]))
        st.markdown(f"Ta réponse en {lr['elapsed']:.1f}s — 0 pts")

    # RAG explanation
    explanation = st.session_state.quiz_rag_explanation
    if explanation:
        with st.expander("Explication du formateur", expanded=False):
            st.write(explanation)

    st.markdown("---")
    if st.button("Question suivante", key="quiz_next_q"):
        st.session_state.quiz_last_result = None
        st.session_state.quiz_rag_explanation = None
        st.session_state.quiz_q_start = time.time()
        st.rerun()


def _render_final_score(qs: QuizSession) -> Dict[str, Any]:
    """Render the final score screen. Returns score data dict."""
    st.markdown("### Résultat du quiz")

    score_pct = qs.score_pct
    correct = qs.correct_count
    total = qs.total_questions
    total_pts = qs.total_points
    max_pts = qs.max_points

    # Big score display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Bonnes réponses", f"{correct}/{total}")
    with col2:
        st.metric("Points", f"{total_pts}/{max_pts}")
    with col3:
        st.metric("Score", f"{score_pct}%")

    # Speed bonuses
    speed_bonuses = sum(1 for r in qs.results if r.speed_bonus)
    if speed_bonuses > 0:
        st.caption(f"Bonus rapidité obtenus : {speed_bonuses}")

    st.markdown("---")

    # Final feedback
    fb = feedback_final(score_pct, correct, total)
    if score_pct >= 80:
        st.success(fb)
    elif score_pct >= 50:
        st.info(fb)
    else:
        st.warning(fb)

    # Recap per question
    with st.expander("Détail par question", expanded=False):
        for i, (q, r) in enumerate(zip(qs.questions, qs.results)):
            icon = "+" if r.is_correct else "x"
            bonus = " (rapide)" if r.speed_bonus else ""
            st.markdown(
                f"**Q{i+1}.** {q.question}  \n"
                f"{'Correct' if r.is_correct else 'Faux'}{bonus} — "
                f"{r.points} pts ({r.elapsed_seconds:.1f}s)"
            )

    return {
        "score_pct": score_pct,
        "correct": correct,
        "total": total,
        "points": total_pts,
        "max_points": max_pts,
        "speed_bonuses": speed_bonuses,
    }


def render_quiz(
    theme_title: str,
    repondre_faq_fn: Optional[Callable] = None,
) -> Optional[Dict[str, Any]]:
    """Main entry point: render the full quiz flow.

    Args:
        theme_title: Session theme to select questions.
        repondre_faq_fn: Optional FAQ function for RAG explanations.

    Returns:
        Score data dict when quiz is complete, None otherwise.
    """
    _init_quiz_state()

    qs = _get_or_create_quiz(theme_title)

    st.markdown(f"### Quiz — {theme_title}")
    _render_progress_bar(qs)

    # Quiz complete → final score
    if qs.is_complete:
        # No pending feedback
        st.session_state.quiz_last_result = None
        score_data = _render_final_score(qs)
        return score_data

    # Pending feedback from last answer
    if st.session_state.quiz_last_result is not None:
        _render_feedback()
        return None

    # Show current question
    _render_question(qs, repondre_faq_fn)
    return None
