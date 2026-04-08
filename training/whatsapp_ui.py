"""training/whatsapp_ui.py – Streamlit WhatsApp-like roleplay UI.

Renders:
  - WhatsApp-style chat bubbles (green for trainee, white for client)
  - Client avatar header
  - "écrit..." indicator during AI response
  - Text input + send
  - Terminate button (after max_exchanges)
  - Evaluation + debrief screen
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

import streamlit as st

from core.avatar import show_formateur_message
from training.adapters import (
    get_whatsapp_difficulty,
    adjust_difficulty_dynamically,
)
from training.whatsapp import (
    WhatsAppSession,
    create_whatsapp_session,
    generate_client_reply,
    evaluate_conversation,
    calculate_realtime_score,
)


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
def _init_wa_state() -> None:
    """Initialize WhatsApp session state keys."""
    if "wa_session" not in st.session_state:
        st.session_state.wa_session = None
    if "wa_evaluation" not in st.session_state:
        st.session_state.wa_evaluation = None
    if "wa_difficulty" not in st.session_state:
        st.session_state.wa_difficulty = "moyen"


def _get_or_create_wa(
    theme_title: str,
    tone_override: str | None = None,
    session_number: int = 1,
    generated_data: Any = None,
) -> WhatsAppSession:
    if st.session_state.wa_session is not None:
        return WhatsAppSession.from_dict(st.session_state.wa_session)
    ws = create_whatsapp_session(
        theme_title,
        tone_override=tone_override,
        session_number=session_number,
        generated_data=generated_data,
    )
    st.session_state.wa_session = ws.to_dict()
    st.session_state.wa_evaluation = None
    return ws


def _save_wa(ws: WhatsAppSession) -> None:
    st.session_state.wa_session = ws.to_dict()


def _reset_wa() -> None:
    """Clear all WhatsApp state."""
    st.session_state.wa_session = None
    st.session_state.wa_evaluation = None
    st.session_state.wa_difficulty = "moyen"
    st.session_state.pop("wa_ringing", None)


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
_BUBBLE_CSS = """
<style>
.wa-container { max-width: 600px; margin: 0 auto; }
.wa-msg {
    padding: 8px 14px; border-radius: 12px; margin: 6px 0;
    max-width: 80%; word-wrap: break-word; font-size: 0.95em; line-height: 1.4;
}
.wa-client {
    background-color: #ffffff; border: 1px solid #e0e0e0;
    margin-right: auto; border-top-left-radius: 4px;
}
.wa-agent {
    background-color: #dcf8c6; margin-left: auto;
    border-top-right-radius: 4px; text-align: right;
}
.wa-name { font-weight: bold; font-size: 0.8em; color: #666; margin-bottom: 2px; }
.wa-bubble-row { display: flex; }
.wa-bubble-row.client { justify-content: flex-start; }
.wa-bubble-row.agent { justify-content: flex-end; }
</style>
"""


def _render_header(ws: WhatsAppSession) -> None:
    """Render WhatsApp header with client avatar."""
    name = ws.scenario.persona_name
    role = ws.scenario.persona_role
    st.markdown(
        f'<div style="background-color:#075e54; color:white; padding:10px 16px; '
        f'border-radius:8px; margin-bottom:12px;">'
        f'<strong>{name}</strong> — {role}</div>',
        unsafe_allow_html=True,
    )


def _render_messages(ws: WhatsAppSession) -> None:
    """Render all messages as WhatsApp-like bubbles."""
    st.markdown(_BUBBLE_CSS, unsafe_allow_html=True)

    html = '<div class="wa-container">'
    for msg in ws.messages:
        # Escape HTML in content
        content = msg.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if msg.role == "client":
            html += (
                f'<div class="wa-bubble-row client">'
                f'<div class="wa-msg wa-client">'
                f'<div class="wa-name">{ws.scenario.persona_name}</div>'
                f'{content}</div></div>'
            )
        else:
            html += (
                f'<div class="wa-bubble-row agent">'
                f'<div class="wa-msg wa-agent">'
                f'<div class="wa-name">Toi</div>'
                f'{content}</div></div>'
            )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def _render_conclusion_hint(ws: WhatsAppSession) -> None:
    """Show coaching tip when trainee should start concluding."""
    exchanges = ws.exchange_count
    max_ex = ws.scenario.max_exchanges

    # Show hint at penultimate exchange
    if exchanges < max_ex - 1:
        return

    st.info(
        "💡 **Conseil formateur** : C'est le moment de conclure ! "
        "Propose une action concrète : un rendez-vous, une deuxième visite, "
        "un rappel à une date précise. "
        "Termine toujours par une prochaine étape claire.",
        icon="🎯",
    )


def _render_performance_indicator(ws: WhatsAppSession) -> None:
    """Affiche l'indicateur de performance temps réel (score, conseil, objectif)."""
    perf = calculate_realtime_score(ws.messages)
    score: int = perf["score"]
    conseil: str = perf["conseil"]
    objectif: str = perf["objectif"]

    if score >= 70:
        color = "#4CAF50"
        mood = "encouraging"
        emoji = "🟢"
    elif score >= 50:
        color = "#FF9800"
        mood = "neutral"
        emoji = "🟠"
    else:
        color = "#F44336"
        mood = "thinking"
        emoji = "🔴"

    # Barre score + objectif
    st.markdown(
        f"""
<div style="border:2px solid {color};border-radius:8px;padding:14px;margin:12px 0;background:#f9f9f9;">
  <div style="font-size:15px;font-weight:bold;margin-bottom:6px;">Objectif : {objectif}</div>
  <div style="font-size:13px;margin-bottom:4px;">Performance : {emoji}</div>
  <div style="background:linear-gradient(90deg,{color} 0%,{color} {score}%,#e0e0e0 {score}%,#e0e0e0 100%);
              height:22px;border-radius:10px;margin:6px 0;">
    <div style="color:white;font-weight:bold;text-align:center;line-height:22px;
                text-shadow:1px 1px 2px rgba(0,0,0,0.5);">{score}%</div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )

    # Conseil formateur avec avatar
    show_formateur_message(
        message=conseil,
        key=f"wa_conseil_{len(ws.messages)}",
        mood=mood,
    )


def _render_chat(
    ws: WhatsAppSession,
    construire_contexte_fn: Optional[Callable] = None,
    chat_complete_fn: Optional[Callable] = None,
) -> None:
    """Render the active chat with input and send button."""
    exchanges = ws.exchange_count
    max_ex = ws.scenario.max_exchanges

    difficulty = st.session_state.wa_difficulty
    difficulty_labels = {"facile": "Débutant", "moyen": "Confirmé", "difficile": "Expert"}
    st.caption(f"Échange {exchanges}/{max_ex} — Niveau client : {difficulty_labels.get(difficulty, difficulty)}")

    # Coaching hint when approaching end
    _render_conclusion_hint(ws)

    agent_input = st.text_input(
        "Votre message :",
        placeholder="Tapez votre réponse ici...",
        key=f"wa_input_{exchanges}",
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        send = st.button(
            "Envoyer",
            key=f"wa_send_{exchanges}",
            use_container_width=True,
        )
    with col2:
        end = st.button(
            "Terminer",
            key=f"wa_end_{exchanges}",
            use_container_width=True,
            disabled=not ws.can_terminate,
        )

    if send and agent_input.strip():
        ws.add_message("agent", agent_input.strip())

        # Max exchanges reached → terminate
        if ws.exchange_count >= ws.scenario.max_exchanges:
            ws.terminate()
            _save_wa(ws)
            st.rerun()

        # Generate client reply with adaptive difficulty
        if chat_complete_fn and construire_contexte_fn:
            rag_ctx = construire_contexte_fn(ws.scenario.persona_context)

            # Adjust difficulty dynamically based on agent performance
            messages_dicts = [{"role": m.role, "content": m.content} for m in ws.messages]
            new_difficulty = adjust_difficulty_dynamically(
                st.session_state.wa_difficulty,
                messages_dicts,
                ws.exchange_count,
            )
            st.session_state.wa_difficulty = new_difficulty

            with st.spinner(f"{ws.scenario.persona_name} écrit..."):
                reply = generate_client_reply(
                    ws.scenario, ws.messages, rag_ctx, chat_complete_fn,
                    difficulty=new_difficulty,
                )
            ws.add_message("client", reply)

        _save_wa(ws)
        st.rerun()

    if end and ws.can_terminate:
        ws.terminate()
        _save_wa(ws)
        st.rerun()


def _render_evaluation(
    ws: WhatsAppSession,
    construire_contexte_fn: Optional[Callable] = None,
    chat_complete_fn: Optional[Callable] = None,
) -> Tuple[Optional[Dict[str, Any]], bool]:
    """Render evaluation screen. Returns (evaluation_data, should_continue)."""

    # PASSE 1 : Génération (si nécessaire)
    if st.session_state.wa_evaluation is None:
        if chat_complete_fn and construire_contexte_fn:
            # Bouton pour déclencher l'évaluation
            if st.button("Voir mon évaluation", key="btn_start_eval", type="primary"):
                rag_ctx = construire_contexte_fn(ws.scenario.persona_context)
                with st.spinner("Le formateur évalue ta conversation..."):
                    evaluation = evaluate_conversation(
                        ws.scenario, ws.messages, rag_ctx, chat_complete_fn,
                    )
                st.session_state.wa_evaluation = evaluation
                st.rerun()  # Rerun pour afficher l'évaluation
            return None, False  # Pas encore d'évaluation
        else:
            st.session_state.wa_evaluation = {
                "criteria": [],
                "total_score": 0,
                "debrief": "",
                "suggestions": "",
                "lacunes": [],
            }
            st.rerun()
            return None, False

    # PASSE 2 : Affichage (évaluation existe)
    evaluation = st.session_state.wa_evaluation

    # --- Score display ---
    st.markdown("### Évaluation")
    total = evaluation.get("total_score", 0)

    if total >= 70:
        st.success(f"Score : {total}/100")
    elif total >= 40:
        st.info(f"Score : {total}/100")
    else:
        st.warning(f"Score : {total}/100")

    # Criteria breakdown (2 rows)
    criteria = evaluation.get("criteria", [])
    if criteria:
        row1 = criteria[:3]
        row2 = criteria[3:]

        cols = st.columns(len(row1))
        for i, c in enumerate(row1):
            with cols[i]:
                st.metric(
                    c["name"][:25],
                    f"{c['score']}/10",
                    help=f"Poids : {c['weight']}%",
                )
                if c.get("comment"):
                    st.caption(c["comment"][:100])

        if row2:
            cols2 = st.columns(len(row2))
            for i, c in enumerate(row2):
                with cols2[i]:
                    st.metric(
                        c["name"][:25],
                        f"{c['score']}/10",
                        help=f"Poids : {c['weight']}%",
                    )
                    if c.get("comment"):
                        st.caption(c["comment"][:100])

    # Moments clés
    debrief = evaluation.get("debrief", "")
    if debrief:
        st.markdown("---")
        st.markdown("#### Moments clés")
        st.write(debrief)

    # Lacunes détectées
    lacunes = evaluation.get("lacunes", [])
    if lacunes:
        st.markdown("---")
        st.markdown("#### Lacunes détectées")
        for lacune in lacunes:
            st.write(f"- {lacune}")

    # Ancrage
    suggestions = evaluation.get("suggestions", "")
    if suggestions:
        st.markdown("---")
        st.markdown("#### Ancrage")
        st.write(suggestions)

    # Bouton Continuer
    st.markdown("---")
    should_continue = st.button("Continuer", key="btn_next_wa_eval")

    return evaluation, should_continue


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def render_whatsapp(
    theme_title: str,
    construire_contexte_fn: Optional[Callable] = None,
    chat_complete_fn: Optional[Callable] = None,
    tone_override: Optional[str] = None,
    profile: Optional[Any] = None,
    session_number: int = 1,
    generated_scenario: Optional[Dict[str, Any]] = None,
) -> Optional[Tuple[Dict[str, Any], bool]]:
    """Main entry point: render the full WhatsApp roleplay flow.

    Args:
        theme_title: Theme for scenario selection (previous day's cours clés).
        construire_contexte_fn: RAG context builder (from agent_formateur).
        chat_complete_fn: LLM completion function (from agent_formateur).
        tone_override: Optional client tone override from profile adapter.
        profile: UserProfile for adaptive difficulty initialization.
        session_number: Used for deterministic scenario rotation.

    Returns:
        (evaluation_data, should_continue) when conversation complete, None otherwise.
    """
    _init_wa_state()

    # Set initial difficulty from profile (only on session creation)
    if st.session_state.wa_session is None and profile is not None:
        st.session_state.wa_difficulty = get_whatsapp_difficulty(profile)

    ws = _get_or_create_wa(
        theme_title,
        tone_override=tone_override,
        session_number=session_number,
        generated_data=generated_scenario,
    )

    _render_header(ws)
    _render_messages(ws)
    st.markdown("---")

    # Conversation terminated → evaluation
    if ws.is_terminated:
        evaluation, should_continue = _render_evaluation(
            ws, construire_contexte_fn, chat_complete_fn,
        )
        return evaluation, should_continue

    # Performance indicator (active conversation, at least 1 agent message)
    if len([m for m in ws.messages if m.role == "agent"]) >= 1:
        _render_performance_indicator(ws)

    # Active chat
    _render_chat(ws, construire_contexte_fn, chat_complete_fn)
    return None


def render_debrief_wa(evaluation: Optional[Dict[str, Any]]) -> None:
    """Render the WhatsApp debrief step (summary from evaluation)."""
    if not evaluation:
        st.info("Pas de données WhatsApp pour cette session.")
        return

    total = evaluation.get("total_score", 0)
    criteria = evaluation.get("criteria", [])

    st.markdown("### Récapitulatif WhatsApp")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Score global", f"{total}/100")
    with col2:
        bonnes = sum(1 for c in criteria if c.get("score", 0) >= 7)
        st.metric("Critères réussis (7/10)", f"{bonnes}/{len(criteria)}")

    for c in criteria:
        score = c.get("score", 0)
        icon = "+" if score >= 7 else "~" if score >= 5 else "-"
        st.markdown(
            f"**{icon} {c['name']}** : {score}/10 (poids {c['weight']}%)"
        )
        if c.get("comment"):
            st.caption(f"  {c['comment']}")

    suggestions = evaluation.get("suggestions", "")
    if suggestions:
        with st.expander("Ancrage — formulation à retenir", expanded=False):
            st.write(suggestions)
