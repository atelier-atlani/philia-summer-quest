import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from agent_formateur import (
    repondre_comme_formateur,
    repondre_faq,
    generer_fiche_memo,
    generer_plan_entretien,
)
from core.tts import tts_to_bytes
from training.engine import TrainingSession
from training.steps import Step, STEP_LABELS, STEP_DURATIONS
from training.content import get_session_theme, TOTAL_SESSIONS
from training.progress import load_progress, save_progress

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


def _get_or_create_session() -> TrainingSession:
    """Récupère ou crée la TrainingSession courante."""
    if st.session_state.ts is not None:
        return TrainingSession.from_dict(st.session_state.ts)
    progress = load_progress()
    session_num = progress.get("current_session", 1)
    ts = TrainingSession(session_number=session_num)
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
    st.rerun()


def _render_step_header(ts: TrainingSession):
    """Affiche le header commun : session, theme, barre de progression."""
    theme = ts.theme
    st.subheader(f"Session {ts.session_number}/{ts.total_sessions} — {theme['titre']}")

    progress = load_progress()
    profile = progress.get("profile", {})
    if profile.get("prenom"):
        st.info(
            f"Stagiaire : **{profile['prenom']}** — "
            f"Niveau : **{profile.get('niveau', 'non renseigné')}**"
        )

    steps = ts.steps
    idx = ts.current_step_index
    total = len(steps)
    pct = idx / total if total else 0.0
    step_label = ts.step_label()
    duration = STEP_DURATIONS.get(ts.current_step, "")
    dur_txt = f" ({duration})" if duration else ""
    st.progress(pct, text=f"Étape {idx + 1}/{total} — {step_label}{dur_txt}")


def _render_profil(ts: TrainingSession):
    """Step PROFIL : collecte prénom + niveau."""
    st.markdown("### Bienvenue dans ton parcours de formation")
    st.write(
        "Le formateur IA va t'accompagner au quotidien pendant 6 mois. "
        "Commençons par faire connaissance."
    )

    progress = load_progress()
    profile = progress.get("profile", {})

    prenom = st.text_input("Ton prénom :", value=profile.get("prenom", ""))
    niveau = st.radio(
        "Ton niveau en agence immobilière :",
        options=["Débutant (moins d'un an)", "Confirmé (plus d'un an)"],
        index=0 if profile.get("niveau", "") != "Confirmé (plus d'un an)" else 1,
    )

    if st.button("Démarrer la session"):
        progress["profile"] = {
            "prenom": prenom or "le stagiaire",
            "niveau": niveau,
        }
        save_progress(progress)
        ts.record(Step.PROFIL, {"prenom": prenom, "niveau": niveau})
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


def _render_questions_rag(ts: TrainingSession):
    """Step QUESTIONS_RAG : 1-2 questions libres + réponses RAG."""
    theme = ts.theme
    st.markdown(f"### Questions & réponses — {theme['titre']}")
    st.write("Pose 1 ou 2 questions en lien avec le thème du jour.")

    question = st.text_input(
        "Ta question :",
        placeholder=f"Ex : Comment aborder {theme['titre'].lower()} en rendez-vous ?",
        key="rag_question_input",
    )

    if st.button("Obtenir une réponse", key="btn_rag_question"):
        if not question.strip():
            st.warning("Merci de saisir une question.")
        else:
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


def _render_quiz_placeholder(ts: TrainingSession):
    """Step QUIZ : placeholder (quiz Kahoot à venir)."""
    theme = ts.theme
    st.markdown(f"### Quiz — {theme['titre']}")
    st.info(
        "Le quiz interactif (type Kahoot) sera disponible prochainement. "
        "Pour l'instant, prends un moment pour revoir mentalement "
        "les points clés du cours."
    )

    if st.button("Continuer", key="btn_next_quiz"):
        ts.record(Step.QUIZ, {"placeholder": True, "score": 0, "total": 0})
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
    if quiz_data.get("placeholder"):
        st.markdown("- Quiz : (bientôt disponible)")
    elif quiz_data:
        score = quiz_data.get("score", 0)
        total = quiz_data.get("total", 0)
        st.markdown(f"- Quiz : {score}/{total}")

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
        st.metric(
            "WhatsApp",
            "bientôt" if wa_data.get("placeholder") else wa_data.get("score", "—"),
        )
    with col2:
        st.metric(
            "Quiz",
            "bientôt" if quiz_data.get("placeholder") else quiz_data.get("score", "—"),
        )

    st.write(
        "La comparaison détaillée des scores WhatsApp / Quiz sera "
        "disponible une fois ces modules activés."
    )

    st.markdown("---")
    if st.button("Continuer", key="btn_next_debrief_quiz"):
        ts.record(Step.DEBRIEF_QUIZ, {"done": True})
        _advance_step(ts)


def _render_whatsapp_placeholder(ts: TrainingSession):
    """Step WHATSAPP : placeholder (simulation WhatsApp J+1 à venir)."""
    theme = ts.theme
    st.markdown(f"### Mise en situation WhatsApp — {theme['titre']}")
    st.info(
        "La simulation WhatsApp J+1 (basée sur le cours clés de la veille) "
        "sera disponible prochainement. "
        "En attendant, repense aux points clés de ta dernière session."
    )

    if st.button("Continuer", key="btn_next_wa"):
        ts.record(Step.WHATSAPP, {"placeholder": True, "score": 0})
        _advance_step(ts)


def _render_debrief_wa(ts: TrainingSession):
    """Step DEBRIEF_WA : débrief WhatsApp placeholder."""
    st.markdown("### Débrief WhatsApp")
    st.info(
        "Le débrief WhatsApp sera généré automatiquement "
        "une fois la simulation WhatsApp activée."
    )

    if st.button("Continuer", key="btn_next_debrief_wa"):
        ts.record(Step.DEBRIEF_WA, {"placeholder": True})
        _advance_step(ts)


def _render_synthese(ts: TrainingSession):
    """Step SYNTHESE : synthèse + action terrain pour demain."""
    theme = ts.theme
    st.markdown("### Synthèse de la session")

    progress = load_progress()
    profile = progress.get("profile", {})
    prenom = profile.get("prenom", "stagiaire")

    st.write(f"Bravo {prenom} ! Tu as terminé la session {ts.session_number}.")
    st.write(f"**Thème du jour** : {theme['titre']}")

    st.markdown("---")
    st.markdown("#### Ce que tu as fait aujourd'hui")

    data = ts.step_data
    steps_done = [k for k, v in data.items() if v]
    for s in steps_done:
        label = STEP_LABELS.get(Step(s), s) if s in Step.__members__ else s
        st.markdown(f"- {label}")

    st.markdown("---")
    st.markdown("#### Action terrain pour demain")
    st.success(theme["synthese_action"])

    st.markdown("---")
    if st.button("Terminer la session"):
        ts.record(Step.SYNTHESE, {"done": True})
        ts.complete()
        # Reset pour la prochaine session
        st.session_state.ts = None
        st.session_state.ts_response = ""
        st.session_state.ts_faq_response = ""
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
        _render_quiz_placeholder(ts)
    elif step == Step.DEBRIEF:
        _render_debrief(ts)
    elif step == Step.DEBRIEF_QUIZ:
        _render_debrief_quiz(ts)
    elif step == Step.WHATSAPP:
        _render_whatsapp_placeholder(ts)
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
            st.session_state.ts_response = ""
            st.session_state.ts_faq_response = ""
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

                st.markdown("### 📘 Fiche mémo générée")
                st.write(fiche)

                if lire_voix:
                    play_audio_from_text(fiche)

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
