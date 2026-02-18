import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from agent_formateur import (
    repondre_comme_formateur,
    repondre_faq,
    repondre_quiz_explanation,
    generer_fiche_memo,
    generer_plan_entretien,
    construire_contexte,
    chat_complete,
)
from core.tts import tts_to_bytes
from training.engine import TrainingSession
from training.steps import Step, STEP_LABELS, get_steps_for_session
from training.content import get_session_theme, TOTAL_SESSIONS
from training.progress import load_progress, save_progress, save_profile, load_profile, save_lacunes
from training.profile_ui import render_profile_onboarding, _reset_profile
from training.adapters import adapt_quiz_difficulty, adapt_whatsapp_tone
from training.quiz_ui import render_quiz as _render_quiz_component, _reset_quiz
from training.whatsapp_ui import (
    render_whatsapp as _render_wa_component,
    render_debrief_wa as _render_debrief_wa_component,
    _reset_wa,
)
from training.synthesis import generate_synthesis
from training.pdf_export import generate_session_pdf, generate_memo_pdf, save_pdf

# Charger la clé API depuis .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="Agent IA Formateur Immobilier",
    layout="wide",
)


# -----------------------------
# AUDIO (TTS) — utilise core/tts.py
# -----------------------------
# Config Streamlit : WAV + voix "alloy" (pas d'instructions custom)
_STREAMLIT_TTS_VOICE = "alloy"


def play_audio_from_text(texte: str):
    """Génère l'audio et affiche un lecteur Streamlit + debug si besoin."""
    data = tts_to_bytes(
        client,
        texte,
        voice=_STREAMLIT_TTS_VOICE,
        instructions="",  # pas d'instructions pour Streamlit
        response_format="wav",
    )
    if not data:
        st.error("Impossible de générer l'audio.")
        return

    if isinstance(data, bytearray):
        data = bytes(data)

    # Debug : taille + signature WAV (RIFF....WAVE)
    st.caption(f"🔎 Debug audio: {len(data)} bytes | header={data[:12]!r}")

    # Signature WAV attendue : b'RIFF' ... b'WAVE'
    if not (data.startswith(b"RIFF") and b"WAVE" in data[:16]):
        st.error("⚠️ Le contenu reçu n'est pas un WAV valide. Je te montre le début :")
        st.code(data[:400])
        return

    st.audio(data, format="audio/wav")




# -----------------------------
# TRAINING ENGINE (parcours 6 mois)
# -----------------------------
def _init_training_state():
    """Initialise le state Streamlit pour le training engine."""
    if "ts" not in st.session_state:
        st.session_state.ts = None  # TrainingSession dict
    if "ts_response" not in st.session_state:
        st.session_state.ts_response = ""
    if "ts_faq_response" not in st.session_state:
        st.session_state.ts_faq_response = ""
    if "ts_synthesis" not in st.session_state:
        st.session_state.ts_synthesis = None
    if "ts_pdf_bytes" not in st.session_state:
        st.session_state.ts_pdf_bytes = None
    if "ts_force_restart" not in st.session_state:
        st.session_state.ts_force_restart = False
    if "ts_editing_profile" not in st.session_state:
        st.session_state.ts_editing_profile = False


def _get_or_create_session() -> TrainingSession:
    """Récupère ou crée la TrainingSession courante."""
    if st.session_state.ts is not None and not st.session_state.ts_force_restart:
        ts = TrainingSession.from_dict(st.session_state.ts)
    else:
        st.session_state.ts_force_restart = False
        progress = load_progress()
        session_num = progress.get("current_session", 1)
        ts = TrainingSession(session_number=session_num)

    # Skip PROFIL si le profil existe déjà — sauf en mode édition profil
    if not st.session_state.ts_editing_profile:
        progress = load_progress()
        existing_profile = progress.get("profile", {})
        if existing_profile and existing_profile.get("prenom"):
            if ts.current_step == Step.PROFIL:
                ts.step_data[Step.PROFIL.value] = existing_profile
                ts.current_step_index = 1

    st.session_state.ts = ts.to_dict()
    return ts


def _save_ts(ts: TrainingSession):
    """Persiste la session dans le state Streamlit."""
    st.session_state.ts = ts.to_dict()


def _advance_step(ts: TrainingSession):
    """Avance d'un step et rerun."""
    ts.advance()
    _save_ts(ts)
    st.session_state.ts_response = ""
    st.session_state.ts_faq_response = ""
    st.session_state.ts_synthesis = None
    st.session_state.ts_pdf_bytes = None
    st.session_state.ts_editing_profile = False
    _reset_quiz()
    _reset_wa()
    _reset_profile()
    st.rerun()


def _render_step_header(ts: TrainingSession):
    """Affiche le header commun : session, theme, barre de progression."""
    theme = ts.theme
    st.subheader(f"Session {ts.session_number}/{ts.total_sessions} — {theme['titre']}")

    profile = ts.profile
    if profile.prenom:
        st.info(
            f"Stagiaire : **{profile.prenom}** — "
            f"Niveau : **{profile.niveau_label}** — "
            f"Rôle : **{profile.role_label}**"
        )

    steps = ts.steps
    idx = ts.current_step_index
    total = len(steps)
    progress = (idx + 1) / total if total else 0.0
    step_label = ts.step_label()

    # Barre de progression visuelle stylisée
    pct_css = progress * 100
    st.markdown(
        f'<div style="'
        f"background: linear-gradient(90deg, #4CAF50 0%, #4CAF50 {pct_css}%, "
        f"#e0e0e0 {pct_css}%, #e0e0e0 100%);"
        f'padding: 10px 18px; border-radius: 8px; margin-bottom: 12px;">'
        f'<span style="color: white; font-weight: bold; font-size: 15px;">'
        f"Étape {idx + 1}/{total} : {step_label}"
        f"</span></div>",
        unsafe_allow_html=True,
    )

    # Timeline des étapes
    cols = st.columns(total)
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < idx:
                icon = "✅"
            elif i == idx:
                icon = "🔵"
            else:
                icon = "⚪"
            label = STEP_LABELS.get(step, step.value)
            st.markdown(
                f'<div style="text-align:center; font-size:16px;">{icon}</div>'
                f'<div style="text-align:center; font-size:0.65em; '
                f'color:#555; line-height:1.2;">{label}</div>',
                unsafe_allow_html=True,
            )


def _render_profil(ts: TrainingSession):
    """Step PROFIL : onboarding avancé en 3 étapes."""
    progress = load_progress()
    existing_profile = progress.get("profile", {})

    # Guard: if profile already exists, skip — sauf en mode édition profil
    if (existing_profile and existing_profile.get("prenom")
            and not st.session_state.get("ts_editing_profile", False)):
        ts.record(Step.PROFIL, existing_profile)
        _advance_step(ts)
        return

    st.markdown("### Bienvenue dans ton parcours de formation")
    st.write(
        "Le formateur IA va t'accompagner au quotidien pendant 6 mois. "
        "Commençons par faire connaissance."
    )

    user_profile = render_profile_onboarding(existing_profile)

    if user_profile is not None:
        # Onboarding complete — save and advance
        save_profile(user_profile)
        if st.button("Démarrer la session"):
            ts.record(Step.PROFIL, user_profile.to_dict())
            _advance_step(ts)


def _render_mini_cours(ts: TrainingSession):
    """Step MINI_COURS : mini-cours magistral via RAG."""
    theme = ts.theme
    st.markdown(f"### Mini-cours — {theme['titre']}")

    if not st.session_state.ts_response:
        if st.button("Lancer le mini-cours"):
            with st.spinner("Le formateur prépare le cours..."):
                resp = repondre_comme_formateur(theme["mini_cours"])
            st.session_state.ts_response = resp
            st.rerun()
        return

    st.write(st.session_state.ts_response)

    if st.button("Lire à voix haute", key="tts_mini_cours"):
        play_audio_from_text(st.session_state.ts_response)

    st.markdown("---")
    if st.button("Continuer"):
        ts.record(Step.MINI_COURS, {"done": True})
        _advance_step(ts)


def _suggested_questions(theme_titre: str) -> list[str]:
    """Retourne 3-5 questions fréquentes adaptées au thème du jour."""
    _questions_map = {
        "découverte": [
            "Comment identifier si le vendeur est vraiment motivé ?",
            "Quelles questions poser en priorité lors de la découverte ?",
            "Comment créer la confiance dès le premier contact ?",
        ],
        "acm": [
            "Comment présenter l'ACM de façon convaincante ?",
            "Que faire si le vendeur conteste les comparables ?",
            "Comment utiliser l'ACM pour cadrer le prix ?",
        ],
        "objection": [
            "Comment répondre à 'mon voisin a vendu plus cher' ?",
            "Quelle posture adopter face à un vendeur qui refuse de baisser ?",
            "Comment rester calme face à un vendeur agressif sur le prix ?",
        ],
        "suivi": [
            "À quelle fréquence contacter le vendeur ?",
            "Comment faire un bilan de promotion efficace ?",
            "Que faire quand un vendeur ne répond plus ?",
        ],
        "mandat": [
            "Quelle est la différence entre mandat simple et exclusif ?",
            "Comment argumenter le mandat exclusif ?",
            "Que faire si le vendeur refuse le mandat exclusif ?",
        ],
        "service": [
            "Comment vendre ma méthode plutôt que ma marque ?",
            "Quel plan d'actions présenter au vendeur ?",
            "Comment me différencier des autres agences ?",
        ],
        "visite": [
            "Comment préparer une visite efficacement ?",
            "Que faire si l'acquéreur est silencieux pendant la visite ?",
            "Comment structurer un bon compte-rendu de visite ?",
        ],
        "négociation": [
            "Comment gérer un acquéreur qui fait une offre basse ?",
            "Comment présenter une offre au vendeur ?",
            "Quels arguments utiliser pour rapprocher vendeur et acquéreur ?",
        ],
        "relance": [
            "Comment relancer un acquéreur qui a visité sans nouvelles ?",
            "Quel délai avant de relancer ?",
            "Comment créer un sentiment d'urgence sans pression ?",
        ],
        "renégociation": [
            "Quand proposer une baisse de prix au vendeur ?",
            "Comment présenter les retours acquéreurs pour justifier un ajustement ?",
            "Que vérifier avant de proposer une baisse ?",
        ],
        "stock": [
            "Comment prioriser mes mandats en stock ?",
            "Quelles actions pour redonner du dynamisme à un mandat ?",
            "Comment faire le bilan des actions engagées ?",
        ],
        "qualité": [
            "Quand récupérer l'enquête qualité vendeur ?",
            "Quels points vérifier dans les retours clients ?",
            "Comment utiliser les retours pour m'améliorer ?",
        ],
        "fidélisation": [
            "Comment transformer un vendeur satisfait en source de recommandation ?",
            "Quand demander une recommandation ?",
            "Comment garder le contact après la vente ?",
        ],
    }
    titre_lower = theme_titre.lower()
    for key, questions in _questions_map.items():
        if key in titre_lower:
            return questions
    return [
        "Comment gérer les objections courantes sur ce sujet ?",
        "Quelles sont les erreurs à éviter ?",
        "Comment préparer efficacement mon prochain rendez-vous ?",
    ]


def _render_questions_rag(ts: TrainingSession):
    """Step QUESTIONS_RAG : 1-2 questions libres + réponses RAG."""
    theme = ts.theme
    st.markdown(f"### Questions & réponses — {theme['titre']}")
    st.write("Pose 1 ou 2 questions en lien avec le thème du jour.")

    if "selected_suggestion" not in st.session_state:
        st.session_state.selected_suggestion = ""

    default_value = st.session_state.selected_suggestion or ""

    question = st.text_input(
        "Ta question :",
        value=default_value,
        placeholder=f"Ex : Comment aborder {theme['titre'].lower()} en rendez-vous ?",
        key="rag_question_input",
    )

    # Suggestions de questions fréquentes
    suggestions = _suggested_questions(theme["titre"])
    with st.expander("Questions fréquentes sur ce sujet", expanded=False):
        st.caption("Tu n'as pas de question ? Voici des pistes :")
        for i, sq in enumerate(suggestions):
            if st.button(sq, key=f"suggested_q_{i}"):
                st.session_state.selected_suggestion = sq
                st.rerun()

    if st.button("Obtenir une réponse", key="btn_rag_question"):
        if not question.strip():
            st.warning("Merci de saisir une question.")
        else:
            st.session_state.selected_suggestion = ""
            with st.spinner("Le formateur cherche dans la base..."):
                resp = repondre_faq(question.strip())
            st.session_state.ts_faq_response = resp

    if st.session_state.ts_faq_response:
        st.markdown("#### Réponse du formateur")
        st.write(st.session_state.ts_faq_response)

        if st.button("Lire à voix haute", key="tts_rag_question"):
            play_audio_from_text(st.session_state.ts_faq_response)

    st.markdown("---")
    if st.button("Continuer", key="btn_next_rag"):
        ts.record(Step.QUESTIONS_RAG, {"done": True})
        _advance_step(ts)


def _render_cours_cles(ts: TrainingSession):
    """Step COURS_CLES : cours clés du jour via RAG."""
    theme = ts.theme
    st.markdown(f"### Cours clés — {theme['titre']}")

    if not st.session_state.ts_response:
        if st.button("Lancer le cours clés"):
            with st.spinner("Le formateur prépare le cours clés..."):
                resp = repondre_comme_formateur(theme["cours_cles"])
            st.session_state.ts_response = resp
            st.rerun()
        return

    st.write(st.session_state.ts_response)

    if st.button("Lire à voix haute", key="tts_cours_cles"):
        play_audio_from_text(st.session_state.ts_response)

    st.markdown("---")
    if st.button("Continuer", key="btn_next_cours_cles"):
        ts.record(Step.COURS_CLES, {"done": True})
        _advance_step(ts)


def _render_quiz(ts: TrainingSession):
    """Step QUIZ : quiz Kahoot-like interactif, difficulté adaptée au profil."""
    theme = ts.theme
    difficulty_range = adapt_quiz_difficulty(ts.profile)

    score_data = _render_quiz_component(
        theme_title=theme["titre"],
        repondre_faq_fn=repondre_quiz_explanation,
        difficulty_range=difficulty_range,
    )

    # Quiz terminé → bouton pour avancer
    if score_data is not None:
        st.markdown("---")
        if st.button("Continuer", key="btn_next_quiz"):
            ts.record(Step.QUIZ, {
                "score_pct": score_data["score_pct"],
                "score": score_data["correct"],
                "total": score_data["total"],
                "points": score_data["points"],
                "max_points": score_data["max_points"],
                "speed_bonuses": score_data["speed_bonuses"],
            })
            _advance_step(ts)


def _render_debrief(ts: TrainingSession):
    """Step DEBRIEF : débrief de la session (Jour 1)."""
    st.markdown("### Débrief de la session")

    data = ts.step_data
    st.write("Voici un résumé de ta session :")

    if data.get(Step.MINI_COURS.value):
        st.markdown("- Mini-cours : terminé")
    if data.get(Step.QUESTIONS_RAG.value):
        st.markdown("- Questions RAG : terminé")
    if data.get(Step.COURS_CLES.value):
        st.markdown("- Cours clés : terminé")

    quiz_data = data.get(Step.QUIZ.value, {})
    if quiz_data:
        score = quiz_data.get("score", 0)
        total = quiz_data.get("total", 0)
        score_pct = quiz_data.get("score_pct", 0)
        st.markdown(f"- Quiz : {score}/{total} ({score_pct}%)")

    st.markdown("---")
    if st.button("Continuer", key="btn_next_debrief"):
        ts.record(Step.DEBRIEF, {"done": True})
        _advance_step(ts)


def _render_debrief_quiz(ts: TrainingSession):
    """Step DEBRIEF_QUIZ : débrief comparatif WhatsApp vs Quiz (Jour 2+)."""
    st.markdown("### Débrief — Comparaison scores")

    data = ts.step_data
    wa_data = data.get(Step.WHATSAPP.value, {})
    quiz_data = data.get(Step.QUIZ.value, {})

    col1, col2 = st.columns(2)
    with col1:
        wa_score = wa_data.get("score")
        if wa_score is not None:
            st.metric("WhatsApp", f"{wa_score}/100")
        else:
            st.metric("WhatsApp", "—")
    with col2:
        if quiz_data.get("score_pct") is not None:
            st.metric("Quiz", f"{quiz_data['score_pct']}%")
            st.caption(f"{quiz_data.get('score', 0)}/{quiz_data.get('total', 0)} bonnes réponses")
        else:
            st.metric("Quiz", "—")

    st.markdown("---")
    if st.button("Continuer", key="btn_next_debrief_quiz"):
        ts.record(Step.DEBRIEF_QUIZ, {"done": True})
        _advance_step(ts)


def _render_whatsapp(ts: TrainingSession):
    """Step WHATSAPP : simulation WhatsApp J+1, ton client adapté au profil."""
    prev_theme = ts.previous_theme
    st.markdown(f"### Mise en situation WhatsApp — {prev_theme['titre']}")
    st.caption("Basé sur le cours clés de ta session précédente.")

    tone_override = adapt_whatsapp_tone(ts.profile)
    evaluation = _render_wa_component(
        theme_title=prev_theme["titre"],
        construire_contexte_fn=construire_contexte,
        chat_complete_fn=chat_complete,
        tone_override=tone_override,
    )

    if evaluation is not None:
        st.markdown("---")
        if st.button("Continuer", key="btn_next_wa"):
            lacunes = evaluation.get("lacunes", [])
            ts.record(Step.WHATSAPP, {
                "score": evaluation.get("total_score", 0),
                "criteria": evaluation.get("criteria", []),
                "debrief": evaluation.get("debrief", ""),
                "suggestions": evaluation.get("suggestions", ""),
                "lacunes": lacunes,
                "theme_veille": prev_theme["titre"],
            })
            if lacunes:
                save_lacunes(lacunes)
            _advance_step(ts)


def _render_debrief_wa(ts: TrainingSession):
    """Step DEBRIEF_WA : débrief WhatsApp avec récapitulatif."""
    st.markdown("### Débrief WhatsApp")

    wa_data = ts.step_data.get(Step.WHATSAPP.value, {})
    if not wa_data or wa_data.get("placeholder"):
        st.info("Pas de données WhatsApp pour cette session.")
    else:
        _render_debrief_wa_component(wa_data)

        # Afficher les lacunes détectées
        lacunes = wa_data.get("lacunes", [])
        if lacunes:
            st.markdown("---")
            st.warning("Points à approfondir détectés :")
            for lacune in lacunes:
                st.write(f"- {lacune}")
            st.info("Ces points seront couverts dans tes prochaines sessions !")

    st.markdown("---")
    if st.button("Continuer", key="btn_next_debrief_wa"):
        ts.record(Step.DEBRIEF_WA, {"done": True})
        _advance_step(ts)


def _render_synthese(ts: TrainingSession):
    """Step SYNTHESE : synthèse IA + PDF quotidien + action terrain demain."""
    theme = ts.theme
    st.markdown("### Synthèse de la session")

    profile = ts.profile
    prenom = profile.prenom or "stagiaire"
    niveau = profile.niveau_label
    is_jour1 = ts.session_number == 1

    st.write(f"Bravo {prenom} ! Tu as terminé la session {ts.session_number}.")
    st.write(f"**Thème du jour** : {theme['titre']}")

    # Generate AI synthesis (cached in session state)
    if st.session_state.ts_synthesis is None:
        with st.spinner("Le formateur prépare ta synthèse personnalisée..."):
            synthesis = generate_synthesis(
                session_number=ts.session_number,
                theme_title=theme["titre"],
                step_data=ts.step_data,
                prenom=prenom,
                chat_complete_fn=chat_complete,
                construire_contexte_fn=construire_contexte,
                profile=profile,
            )
        st.session_state.ts_synthesis = synthesis

    synthesis = st.session_state.ts_synthesis

    # --- Resume du cours ---
    resume = synthesis.get("resume_cours", "")
    if resume:
        st.markdown("---")
        st.markdown("#### Résumé du cours")
        st.write(resume)

    # --- Scores recap ---
    st.markdown("---")
    st.markdown("#### Scores")
    data = ts.step_data
    quiz_data = data.get(Step.QUIZ.value, {})
    wa_data = data.get(Step.WHATSAPP.value, {})

    if is_jour1:
        if quiz_data:
            st.metric(
                "Quiz",
                f"{quiz_data.get('score_pct', 0)}%",
                help=f"{quiz_data.get('score', 0)}/{quiz_data.get('total', 0)} bonnes réponses",
            )
    else:
        col1, col2 = st.columns(2)
        with col1:
            if quiz_data:
                st.metric(
                    "Quiz",
                    f"{quiz_data.get('score_pct', 0)}%",
                    help=f"{quiz_data.get('score', 0)}/{quiz_data.get('total', 0)} bonnes réponses",
                )
            else:
                st.metric("Quiz", "—")
        with col2:
            if wa_data and not wa_data.get("placeholder"):
                st.metric("WhatsApp", f"{wa_data.get('score', 0)}/100")
            else:
                st.metric("WhatsApp", "—")

    # --- Points forts ---
    points_forts = synthesis.get("points_forts", "")
    if points_forts:
        st.markdown("---")
        st.markdown("#### Points forts")
        st.success(points_forts)

    # --- Axes d'amelioration ---
    axes = synthesis.get("axes_amelioration", "")
    if axes:
        st.markdown("#### Axes d'amélioration")
        st.info(axes)

    # --- A faire demain ---
    a_faire = synthesis.get("a_faire_demain", "")
    if a_faire:
        st.markdown("---")
        st.markdown("#### À faire demain")
        st.warning(a_faire)

    # --- PDF download ---
    st.markdown("---")
    if st.session_state.ts_pdf_bytes is None:
        pdf_bytes = generate_session_pdf(
            session_number=ts.session_number,
            theme_title=theme["titre"],
            prenom=prenom,
            niveau=niveau,
            synthesis=synthesis,
            quiz_data=quiz_data,
            wa_data=wa_data if not is_jour1 else None,
            is_jour1=is_jour1,
        )
        st.session_state.ts_pdf_bytes = pdf_bytes
        save_pdf(pdf_bytes, ts.session_number)

    st.download_button(
        label="Télécharger la synthèse PDF",
        data=st.session_state.ts_pdf_bytes,
        file_name=f"synthese_session_{ts.session_number:03d}.pdf",
        mime="application/pdf",
        key="btn_download_pdf",
    )

    # --- Terminer ---
    st.markdown("---")
    if st.button("Terminer la session"):
        ts.record(Step.SYNTHESE, {
            "done": True,
            "a_faire_demain": a_faire,
            "resume_cours": resume,
            "points_forts": points_forts,
            "axes_amelioration": axes,
        })
        ts.complete()
        # Reset pour la prochaine session
        st.session_state.ts = None
        st.session_state.ts_response = ""
        st.session_state.ts_faq_response = ""
        st.session_state.ts_synthesis = None
        st.session_state.ts_pdf_bytes = None
        _reset_quiz()
        _reset_wa()
        _reset_profile()
        st.rerun()


def _render_session_complete():
    """Écran affiché quand la session courante est terminée."""
    progress = load_progress()
    session_num = progress.get("current_session", 1)
    completed = len(progress.get("sessions_history", []))

    st.success(
        f"Tu as complété {completed} session(s) sur {TOTAL_SESSIONS}. "
        f"Ta prochaine session sera la n°{session_num}."
    )
    st.write("Reviens demain pour continuer ta formation !")

    if st.button("Commencer la session suivante"):
        st.session_state.ts = None
        st.session_state.ts_response = ""
        st.session_state.ts_faq_response = ""
        st.session_state.ts_synthesis = None
        st.session_state.ts_pdf_bytes = None
        _reset_quiz()
        _reset_wa()
        _reset_profile()
        st.rerun()


def ui_training():
    """UI principale du training engine — remplace l'ancien parcours guidé."""
    _init_training_state()

    ts = _get_or_create_session()

    # Session terminée ?
    if ts.is_complete:
        _render_session_complete()
        return

    # Header commun
    _render_step_header(ts)

    st.markdown("---")

    # Dispatch vers le bon renderer
    step = ts.current_step
    if step == Step.PROFIL:
        _render_profil(ts)
    elif step == Step.MINI_COURS:
        _render_mini_cours(ts)
    elif step == Step.QUESTIONS_RAG:
        _render_questions_rag(ts)
    elif step == Step.COURS_CLES:
        _render_cours_cles(ts)
    elif step == Step.QUIZ:
        _render_quiz(ts)
    elif step == Step.DEBRIEF:
        _render_debrief(ts)
    elif step == Step.DEBRIEF_QUIZ:
        _render_debrief_quiz(ts)
    elif step == Step.WHATSAPP:
        _render_whatsapp(ts)
    elif step == Step.DEBRIEF_WA:
        _render_debrief_wa(ts)
    elif step == Step.SYNTHESE:
        _render_synthese(ts)

    # Sidebar : reset session
    with st.sidebar:
        st.markdown("---")
        st.caption(f"Session {ts.session_number}/{ts.total_sessions}")
        if st.button("Recommencer cette session", key="btn_reset_session"):
            st.session_state.ts = None
            st.session_state.ts_force_restart = True
            st.session_state.ts_response = ""
            st.session_state.ts_faq_response = ""
            st.session_state.ts_synthesis = None
            st.session_state.ts_pdf_bytes = None
            _reset_quiz()
            _reset_wa()
            _reset_profile()
            st.rerun()

        if st.button("Modifier mon profil", key="btn_edit_profile"):
            progress = load_progress()
            session_num = progress.get("current_session", 1)
            steps = get_steps_for_session(session_num)
            if steps[0] != Step.PROFIL:
                steps.insert(0, Step.PROFIL)
            ts_edit = TrainingSession(
                session_number=session_num,
                steps=steps,
                current_step_index=0,
            )
            st.session_state.ts = ts_edit.to_dict()
            st.session_state.ts_editing_profile = True
            st.session_state.ts_response = ""
            st.session_state.ts_faq_response = ""
            st.session_state.ts_synthesis = None
            st.session_state.ts_pdf_bytes = None
            _reset_quiz()
            _reset_wa()
            _reset_profile()
            st.rerun()

        st.markdown("---")
        col_prev, col_next = st.columns(2)
        with col_prev:
            if ts.session_number > 1:
                if st.button("Session precedente", key="btn_prev_session"):
                    progress = load_progress()
                    progress["current_session"] = ts.session_number - 1
                    save_progress(progress)
                    st.session_state.ts = None
                    st.session_state.ts_force_restart = True
                    st.session_state.ts_response = ""
                    st.session_state.ts_faq_response = ""
                    st.session_state.ts_synthesis = None
                    st.session_state.ts_pdf_bytes = None
                    _reset_quiz()
                    _reset_wa()
                    _reset_profile()
                    st.rerun()
        with col_next:
            if ts.session_number < TOTAL_SESSIONS:
                if st.button("Session suivante", key="btn_next_session"):
                    progress = load_progress()
                    progress["current_session"] = ts.session_number + 1
                    save_progress(progress)
                    st.session_state.ts = None
                    st.session_state.ts_force_restart = True
                    st.session_state.ts_response = ""
                    st.session_state.ts_faq_response = ""
                    st.session_state.ts_synthesis = None
                    st.session_state.ts_pdf_bytes = None
                    _reset_quiz()
                    _reset_wa()
                    _reset_profile()
                    st.rerun()


# -----------------------------
# APP UI
# -----------------------------
def main():
    st.title("🧠 Agent IA Formateur — Vente immobilière")

    st.sidebar.title("⚙️ Modes de formation")
    mode = st.sidebar.radio(
        "Choisis un mode :",
        (
            "Parcours guidé (contenu structuré)",
            "Réponse formateur (explications + cas pratique)",
            "Questions rapides (FAQ métier)",
            "Fiche mémo (synthèse sur un thème)",
            "Plan d'entretien structuré",
        ),
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Base de connaissances alimentée par tes PDF de formation.")

    # 1) Parcours guidé (training engine)
    if mode == "Parcours guidé (contenu structuré)":
        ui_training()
        return

    # 2) Formateur
    if mode == "Réponse formateur (explications + cas pratique)":
        st.subheader("🎓 Mode formateur — réponse détaillée + cas pratique")

        question = st.text_area(
            "Pose ta question :",
            placeholder="Ex : Comment présenter l’ACM à un vendeur sceptique ?",
            height=140,
        )
        lire_voix = st.checkbox("🔊 Lire la réponse à voix haute", key="audio_formateur_check")

        if st.button("Obtenir la réponse du formateur", key="btn_formateur"):
            if not question.strip():
                st.warning("Merci de saisir une question.")
            else:
                with st.spinner("Le formateur réfléchit..."):
                    reponse = repondre_comme_formateur(question.strip())

                st.markdown("### 💬 Réponse du formateur IA")
                st.write(reponse)

                if lire_voix:
                    play_audio_from_text(reponse)

        return

    # 3) FAQ
    if mode == "Questions rapides (FAQ métier)":
        st.subheader("⚡ Mode FAQ — réponses rapides")

        question = st.text_input(
            "Question courte :",
            placeholder="Ex : Comment gérer un vendeur pas pressé ?",
            key="faq_input",
        )
        lire_voix = st.checkbox("🔊 Lire la réponse à voix haute", key="audio_faq_global_check")

        if st.button("Réponse rapide", key="btn_faq_global"):
            if not question.strip():
                st.warning("Merci de saisir une question.")
            else:
                with st.spinner("Le formateur prépare une réponse concise..."):
                    reponse = repondre_faq(question.strip())

                st.markdown("### 💬 Réponse FAQ")
                st.write(reponse)

                if lire_voix:
                    play_audio_from_text(reponse)

        return

    # 4) Fiche mémo
    if mode == "Fiche mémo (synthèse sur un thème)":
        st.subheader("📘 Mode fiche mémo")

        theme = st.text_input(
            "Thème de la fiche mémo :",
            placeholder="Ex : Découverte vendeur",
            key="memo_theme",
        )
        lire_voix = st.checkbox("🔊 Lire la fiche à voix haute", key="audio_memo_check")

        if st.button("Générer la fiche mémo", key="btn_memo"):
            if not theme.strip():
                st.warning("Merci de saisir un thème.")
            else:
                with st.spinner("Génération de la fiche mémo..."):
                    fiche = generer_fiche_memo(theme.strip())
                st.session_state.memo_fiche = fiche
                st.session_state.memo_theme = theme.strip()

        # Afficher la fiche si elle existe
        fiche = st.session_state.get("memo_fiche")
        if fiche:
            st.markdown("### 📘 Fiche mémo générée")
            st.write(fiche)

            if lire_voix:
                play_audio_from_text(fiche)

            memo_pdf = generate_memo_pdf(
                st.session_state.get("memo_theme", "Fiche memo"),
                fiche,
            )
            st.download_button(
                label="Télécharger la fiche mémo (PDF)",
                data=bytes(memo_pdf),
                file_name="fiche_memo.pdf",
                mime="application/pdf",
                key="btn_download_memo_pdf",
            )

        return

    # 5) Plan d'entretien
    if mode == "Plan d'entretien structuré":
        st.subheader("🗂️ Mode plan d’entretien")

        theme = st.text_input(
            "Type d’entretien :",
            placeholder="Ex : Présentation de l’ACM",
            key="plan_theme",
        )
        lire_voix = st.checkbox("🔊 Lire le plan à voix haute", key="audio_plan_check")

        if st.button("Générer le plan d’entretien", key="btn_plan"):
            if not theme.strip():
                st.warning("Merci de saisir un thème.")
            else:
                with st.spinner("Génération du plan d’entretien..."):
                    plan = generer_plan_entretien(theme.strip())

                st.markdown("### 🗂️ Plan d’entretien proposé")
                st.write(plan)

                if lire_voix:
                    play_audio_from_text(plan)

        return


if __name__ == "__main__":
    main()
