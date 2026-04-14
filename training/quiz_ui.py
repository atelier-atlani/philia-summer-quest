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


def _get_or_create_quiz(
    theme_title: str,
    difficulty_range: Optional[tuple] = None,
) -> QuizSession:
    """Get existing quiz session or create a new one."""
    if st.session_state.quiz_session is not None:
        return QuizSession.from_dict(st.session_state.quiz_session)
    qs = create_quiz_session(theme_title, difficulty_range=difficulty_range)
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
    st.session_state.pop("_quiz_render_id", None)
    for key in list(st.session_state.keys()):
        if key.startswith("_tts_quiz_"):
            del st.session_state[key]


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
    # Guard : ne pas afficher les boutons si un résultat est déjà en attente
    if st.session_state.quiz_last_result is not None:
        return
    q = qs.current_question
    if q is None:
        return

    # Question text
    st.markdown(f"### Question {qs.current_index + 1}")
    st.markdown(f"**{q.question}**")

    # IAXEL lit la question (une seule fois par question)
    tts_q_key = f"_tts_quiz_q_{qs.current_index}"
    if not st.session_state.get(tts_q_key, False):
        try:
            from core.tts import tts_smart  # noqa: PLC0415
            from openai import OpenAI  # noqa: PLC0415
            import os  # noqa: PLC0415
            _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            audio = tts_smart(_client, q.question, priority="high")
            if audio:
                fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                st.audio(audio, format=fmt, autoplay=False)
            st.session_state[tts_q_key] = True
        except Exception:
            st.session_state[tts_q_key] = True

    # Timer info
    st.caption(f"Temps conseillé : {q.time_limit}s")
    _render_timer()

    st.markdown("---")

    # Ensure timer is started
    if st.session_state.quiz_q_start is None:
        st.session_state.quiz_q_start = time.time()

    # 4 answer buttons in a 2x2 grid
    # render_id force la recréation des widgets après chaque réponse (anti-doublon)
    render_id = st.session_state.get("_quiz_render_id", 0)
    col1, col2 = st.columns(2)
    cols = [col1, col2, col1, col2]

    for i, choice in enumerate(q.choices):
        color = _COLORS[i] if i < len(_COLORS) else "#666"
        label = _answer_button_html(i, choice)
        with cols[i]:
            if st.button(
                label,
                key=f"quiz_choice_{qs.current_index}_{i}_{render_id}",
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
                    "question_index": qs.current_index,
                }
                # Incrémenter render_id pour invalider les clés de boutons
                st.session_state["_quiz_render_id"] = render_id + 1
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
        st.markdown(f"Votre réponse en {lr['elapsed']:.1f}s — 0 pts")

    # RAG explanation
    explanation = st.session_state.quiz_rag_explanation
    if explanation:
        with st.expander("Explication du formateur", expanded=False):
            st.write(explanation)

    # IAXEL lit la correction (une seule fois par question)
    tts_fb_key = f"_tts_quiz_fb_{lr.get('question_index', 0)}"
    if not st.session_state.get(tts_fb_key, False):
        try:
            from core.tts import tts_smart  # noqa: PLC0415
            from openai import OpenAI  # noqa: PLC0415
            import os  # noqa: PLC0415
            _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if lr["is_correct"]:
                feedback_text = f"Bonne réponse ! {explanation or ''}"
            else:
                feedback_text = f"Non — la bonne réponse était : {lr['correct_text']}. {explanation or ''}"
            audio = tts_smart(_client, feedback_text.strip(), priority="high")
            if audio:
                fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                st.audio(audio, format=fmt, autoplay=False)
            st.session_state[tts_fb_key] = True
        except Exception:
            st.session_state[tts_fb_key] = True

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
    speed_bonuses = sum(1 for r in qs.results if r.speed_bonus)
    pct_correct = round(correct / total * 100) if total else 0

    # Big score display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Bonnes réponses", f"{correct}/{total}")
    with col2:
        st.metric("Réussite", f"{pct_correct}%")
    with col3:
        st.metric("Bonus rapidité", f"{speed_bonuses}/{total}")

    st.markdown("---")

    # Final feedback — basé sur le ratio bonnes réponses (cohérent avec les metrics)
    fb = feedback_final(pct_correct, correct, total)
    if pct_correct >= 80:
        st.success(fb)
    elif pct_correct >= 50:
        st.info(fb)
    else:
        st.warning(fb)

    # IAXEL commente le résultat (une seule fois)
    tts_final_key = "_tts_quiz_final"
    if not st.session_state.get(tts_final_key, False):
        try:
            from core.tts import tts_smart  # noqa: PLC0415
            from openai import OpenAI  # noqa: PLC0415
            import os  # noqa: PLC0415
            _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if correct == total:
                comment = f"Parfait — {correct} sur {total}. Vous maîtrisez le sujet. On continue !"
            elif pct_correct >= 80:
                comment = f"Très bien — {correct} sur {total}. Quelques points à revoir, mais la base est là."
            elif pct_correct >= 50:
                comment = f"{correct} sur {total} — c'est correct. Revoyez les questions ratées, vous progressez."
            else:
                comment = f"{correct} sur {total}... C'est un début. On va retravailler ça ensemble — pas d'inquiétude."
            audio = tts_smart(_client, comment, priority="high")
            if audio:
                fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                st.audio(audio, format=fmt, autoplay=False)
            st.session_state[tts_final_key] = True
        except Exception:
            st.session_state[tts_final_key] = True

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
    difficulty_range: Optional[tuple] = None,
) -> Optional[Dict[str, Any]]:
    """Main entry point: render the full quiz flow.

    Args:
        theme_title: Session theme to select questions.
        repondre_faq_fn: Optional FAQ function for RAG explanations.
        difficulty_range: Optional (min, max) difficulty filter from profile.

    Returns:
        Score data dict when quiz is complete, None otherwise.
    """
    _init_quiz_state()

    qs = _get_or_create_quiz(theme_title, difficulty_range=difficulty_range)

    st.markdown(f"### Quiz — {theme_title}")
    _render_progress_bar(qs)

    # Quiz complete → final score
    if qs.is_complete:
        # No pending feedback
        st.session_state.quiz_last_result = None
        score_data = _render_final_score(qs)
        return score_data

    # Container unique : Streamlit remplace le contenu plutôt que d'empiler
    quiz_container = st.container()
    with quiz_container:
        if st.session_state.quiz_last_result is not None:
            _render_feedback()
        else:
            _render_question(qs, repondre_faq_fn)
    return None
