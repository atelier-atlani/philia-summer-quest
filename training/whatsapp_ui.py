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

from typing import Any, Callable, Dict, Optional

import streamlit as st

from training.whatsapp import (
    WhatsAppSession,
    create_whatsapp_session,
    generate_client_reply,
    evaluate_conversation,
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


def _get_or_create_wa(theme_title: str) -> WhatsAppSession:
    if st.session_state.wa_session is not None:
        return WhatsAppSession.from_dict(st.session_state.wa_session)
    ws = create_whatsapp_session(theme_title)
    st.session_state.wa_session = ws.to_dict()
    st.session_state.wa_evaluation = None
    return ws


def _save_wa(ws: WhatsAppSession) -> None:
    st.session_state.wa_session = ws.to_dict()


def _reset_wa() -> None:
    """Clear all WhatsApp state."""
    st.session_state.wa_session = None
    st.session_state.wa_evaluation = None


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


def _render_chat(
    ws: WhatsAppSession,
    construire_contexte_fn: Optional[Callable] = None,
    chat_complete_fn: Optional[Callable] = None,
) -> None:
    """Render the active chat with input and send button."""
    exchanges = ws.exchange_count
    max_ex = ws.scenario.max_exchanges

    st.caption(f"Échange {exchanges}/{max_ex}")

    agent_input = st.text_input(
        "Ton message :",
        placeholder="Tape ta réponse ici...",
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

        # Generate client reply
        if chat_complete_fn and construire_contexte_fn:
            rag_ctx = construire_contexte_fn(ws.scenario.persona_context)
            with st.spinner(f"{ws.scenario.persona_name} écrit..."):
                reply = generate_client_reply(
                    ws.scenario, ws.messages, rag_ctx, chat_complete_fn,
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
) -> Dict[str, Any]:
    """Render evaluation screen. Returns evaluation data."""
    if st.session_state.wa_evaluation is None:
        if chat_complete_fn and construire_contexte_fn:
            rag_ctx = construire_contexte_fn(ws.scenario.persona_context)
            with st.spinner("Le formateur évalue ta conversation..."):
                evaluation = evaluate_conversation(
                    ws.scenario, ws.messages, rag_ctx, chat_complete_fn,
                )
            st.session_state.wa_evaluation = evaluation
        else:
            st.session_state.wa_evaluation = {
                "criteria": [],
                "total_score": 0,
                "debrief": "",
                "suggestions": "",
            }

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

    # Debrief
    debrief = evaluation.get("debrief", "")
    if debrief:
        st.markdown("---")
        st.markdown("#### Débrief du formateur")
        st.write(debrief)

    # Suggestions
    suggestions = evaluation.get("suggestions", "")
    if suggestions:
        st.markdown("#### Ce que tu aurais pu dire")
        st.write(suggestions)

    return evaluation


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def render_whatsapp(
    theme_title: str,
    construire_contexte_fn: Optional[Callable] = None,
    chat_complete_fn: Optional[Callable] = None,
) -> Optional[Dict[str, Any]]:
    """Main entry point: render the full WhatsApp roleplay flow.

    Args:
        theme_title: Theme for scenario selection (previous day's cours clés).
        construire_contexte_fn: RAG context builder (from agent_formateur).
        chat_complete_fn: LLM completion function (from agent_formateur).

    Returns:
        Evaluation data dict when conversation is complete, None otherwise.
    """
    _init_wa_state()

    ws = _get_or_create_wa(theme_title)

    _render_header(ws)
    _render_messages(ws)
    st.markdown("---")

    # Conversation terminated → evaluation
    if ws.is_terminated:
        evaluation = _render_evaluation(
            ws, construire_contexte_fn, chat_complete_fn,
        )
        return evaluation

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
        with st.expander("Ce que tu aurais pu dire", expanded=False):
            st.write(suggestions)
