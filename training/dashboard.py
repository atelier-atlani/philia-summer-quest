"""training/dashboard.py – Dashboard de progression du stagiaire."""
from __future__ import annotations

from collections import Counter

import plotly.graph_objects as go
import streamlit as st

from training.content import TOTAL_SESSIONS
from training.progress import load_progress


def render_dashboard() -> None:
    """Affiche le dashboard de progression complet."""
    progress = load_progress()
    history = progress.get("sessions_history", [])
    profile = progress.get("profile", {})
    prenom = profile.get("prenom", "Stagiaire")

    st.markdown(f"### 📈 Progression de {prenom}")

    if not history:
        st.info("Aucune session terminée pour l'instant. Complétez votre première session !")
        return

    # Métriques globales
    total_done = len(history)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sessions complétées", f"{total_done}/{TOTAL_SESSIONS}")
    with col2:
        pct = round(total_done / TOTAL_SESSIONS * 100)
        st.metric("Avancement", f"{pct}%")
    with col3:
        quiz_scores = [
            s["data"]["QUIZ"]["score_pct"]
            for s in history
            if s.get("data", {}).get("QUIZ", {}).get("score_pct") is not None
        ]
        avg_quiz = round(sum(quiz_scores) / len(quiz_scores)) if quiz_scores else 0
        st.metric("Moyenne Quiz", f"{avg_quiz}%")

    st.markdown("---")

    # Graphique évolution scores
    sessions_nums, quiz_pcts, wa_scores = [], [], []
    for s in history:
        num = s.get("session", 0)
        data = s.get("data", {})
        sessions_nums.append(f"S{num}")

        quiz = data.get("QUIZ", {})
        quiz_pcts.append(quiz.get("score_pct", None))

        wa = data.get("WHATSAPP", {})
        wa_score = wa.get("score", None) if wa and not wa.get("placeholder") else None
        wa_scores.append(wa_score)

    fig = go.Figure()

    quiz_valid = [(s, v) for s, v in zip(sessions_nums, quiz_pcts) if v is not None]
    if quiz_valid:
        fig.add_trace(go.Scatter(
            x=[s for s, _ in quiz_valid],
            y=[v for _, v in quiz_valid],
            mode="lines+markers",
            name="Quiz (%)",
            line=dict(color="#00B4A6", width=3),
            marker=dict(size=10),
        ))

    wa_valid = [(s, v) for s, v in zip(sessions_nums, wa_scores) if v is not None]
    if wa_valid:
        fig.add_trace(go.Scatter(
            x=[s for s, _ in wa_valid],
            y=[v for _, v in wa_valid],
            mode="lines+markers",
            name="WhatsApp (/100)",
            line=dict(color="#1368ce", width=3),
            marker=dict(size=10),
        ))

    fig.update_layout(
        title="📊 Évolution de vos scores",
        xaxis_title="Session",
        yaxis_title="Score",
        yaxis=dict(range=[0, 105]),
        template="plotly_white",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tableau récapitulatif
    st.markdown("---")
    with st.expander("📋 Détail par session", expanded=False):
        for s in reversed(history):
            num = s.get("session", "?")
            date = s.get("date", "")
            data = s.get("data", {})
            quiz = data.get("QUIZ", {})
            wa = data.get("WHATSAPP", {})

            quiz_str = f"{quiz.get('score_pct')}%" if quiz.get("score_pct") is not None else "—"
            wa_str = f"{wa.get('score')}/100" if wa and wa.get("score") is not None else "—"
            st.markdown(f"**Session {num}** ({date}) — Quiz: {quiz_str} | WhatsApp: {wa_str}")

    # Points faibles récurrents
    all_lacunes = []
    for s in history:
        lacunes = s.get("data", {}).get("WHATSAPP", {}).get("lacunes", [])
        all_lacunes.extend(lacunes)

    if all_lacunes:
        st.markdown("---")
        st.markdown("#### 🎯 Points à travailler (récurrents)")
        lacune_counts = Counter(all_lacunes)
        for lacune, count in lacune_counts.most_common(5):
            st.markdown(f"- **{lacune}** (mentionné {count}×)")
