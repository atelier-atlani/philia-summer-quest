import os
from datetime import datetime, timedelta

import streamlit as st

from core.avatar import show_formateur_message
from dotenv import load_dotenv
from openai import OpenAI

from agent_formateur import (
    repondre_comme_formateur,
    repondre_cours_oral,
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
from training.marche_module import MarcheModuleRunner, MarcheModuleConfig, get_marche_modules_for_session
from training.content import get_session_theme, TOTAL_SESSIONS
from training.progress import load_progress, save_progress, save_profile, load_profile, save_lacunes, PROGRESS_FILE
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
    page_title="AI-mmo Training",
    page_icon="🏠",
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
    if "transition_message" not in st.session_state:
        st.session_state.transition_message = None
    if "avatar_chat_history" not in st.session_state:
        st.session_state.avatar_chat_history = []  # list of {"role": "user"|"assistant", "text": str}


def _get_transition_message(from_step: Step, to_step: Step, profile) -> str:
    """Génère un message de transition entre deux étapes."""
    prenom = profile.prenom or "champion"

    transitions = {
        # Jour 1
        (Step.PROFIL,            Step.MINI_COURS_MARCHE): f"Parfait {prenom} ! Votre profil est enregistré. On commence par un point marché immobilier — 2 modules rapides pour ancrer vos connaissances terrain. C'est parti !",
        # Jour 2+ (ouverture)
        (Step.MINI_COURS_MARCHE, Step.QUESTIONS_RAG):     f"Marché posé {prenom} ! Des questions sur ce qu'on vient de voir ? C'est le moment.",
        (Step.QUESTIONS_RAG,     Step.COURS_CLES):        "Passons maintenant au cours clés du jour. C'est l'essentiel à retenir absolument.",
        (Step.COURS_CLES,        Step.QUIZ):              "Maintenant, nous allons tester tout cela avec un quiz. Vous allez voir, c'est rapide et interactif.",
        (Step.QUIZ,              Step.WHATSAPP):          f"Quiz terminé {prenom} ! On passe à la mise en situation WhatsApp — un cas terrain concret pour finir la session.",
        (Step.WHATSAPP,          Step.DEBRIEF_WA):        "Simulation terminée ! Nous allons analyser cela ensemble pour vous aider à progresser.",
        (Step.DEBRIEF_WA,        Step.SYNTHESE):          f"Bien joué {prenom} ! Je prépare votre synthèse personnalisée de la session.",
        # Transitions héritées (rétrocompatibilité sessions existantes)
        (Step.MINI_COURS,        Step.QUESTIONS_RAG):     "Bien ! Avez-vous des questions sur ce que nous venons de voir ? C'est le moment de me les poser.",
        (Step.QUIZ,              Step.DEBRIEF):           "Quiz terminé ! Voyons ensemble ce qu'il faut retenir et comment progresser.",
        (Step.DEBRIEF,           Step.SYNTHESE):          f"Dernière étape {prenom} : votre synthèse personnalisée de la session.",
        (Step.DEBRIEF_QUIZ,      Step.SYNTHESE):          f"Nous approchons de la fin {prenom} ! Je prépare votre synthèse de session.",
    }

    return transitions.get((from_step, to_step), f"Passons à l'étape suivante {prenom} !")


def _get_or_create_session() -> TrainingSession:
    """Récupère ou crée la TrainingSession courante."""
    if st.session_state.ts is not None and not st.session_state.ts_force_restart:
        ts = TrainingSession.from_dict(st.session_state.ts)
    else:
        st.session_state.ts_force_restart = False
        progress = load_progress()
        sessions_done = len(progress.get("sessions_history", []))
        session_num = 1 if sessions_done == 0 else progress.get("current_session", 1)
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
    """Avance d'un step avec pattern deux passes (évite crash removeChild DOM).

    PASSE 1 (appel direct depuis un bouton) :
      - Avance ts, sauvegarde, vide tous les états widget de l'étape courante.
      - Pose un flag _do_step_transition + le message de transition en attente.
      - Rerun → Streamlit dispose du DOM proprement avant le changement de rendu.

    PASSE 2 (détectée au sommet de ui_training) :
      - Applique transition_message, rerun final vers le nouvel écran.
    """
    from_step = ts.current_step
    ts.advance()
    _save_ts(ts)
    # Vider les états widget de l'étape sortante
    st.session_state.ts_response = ""
    st.session_state.ts_faq_response = ""
    st.session_state.ts_synthesis = None
    st.session_state.ts_pdf_bytes = None
    st.session_state.ts_editing_profile = False
    _reset_quiz()
    _reset_wa()
    _reset_profile()
    # Stocker le message pour passe 2
    st.session_state._pending_transition_msg = _get_transition_message(
        from_step, ts.current_step, ts.profile
    )
    st.session_state._do_step_transition = True
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

    user_profile = render_profile_onboarding(existing_profile)

    if user_profile is not None:
        # Onboarding complete — save and advance immediately
        save_profile(user_profile)
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


def _render_mini_cours_marche(ts: TrainingSession):
    """Step MINI_COURS_MARCHE : mini-cours marché immobilier avec données DVF locales."""
    modules_ids = get_marche_modules_for_session(ts.session_number)
    prenom = ts.profile.prenom or "vous"
    avatar = ts.profile.avatar_name

    if not modules_ids:
        st.info("Aucun module marché pour cette session.")
        if st.button("Continuer →", key="btn_skip_marche"):
            ts.record(Step.MINI_COURS_MARCHE, {"done": True, "skipped": True})
            _advance_step(ts)
        return

    # --- Intro formateur ---
    if ts.session_number == 1:
        intro = (
            f"Bonjour {prenom} ! Je suis {avatar}, votre formateur IA. "
            f"On commence par un point marché — deux modules courts pour ancrer vos connaissances terrain. "
            f"Lisez attentivement, il y a des données chiffrées à retenir."
        )
    else:
        intro = (
            f"On reprend {prenom} ! Séance {ts.session_number} aujourd'hui. "
            f"Deux nouveaux modules marché — modules {modules_ids[0]} et {modules_ids[1]}. "
            f"Restez concentré·e sur les points clés terrain."
        )

    with st.chat_message("assistant"):
        st.markdown(intro)
        if st.button("🔊 Écouter l'intro", key="tts_marche_intro"):
            play_audio_from_text(intro)

    st.markdown(f"### 📊 Marché immobilier — Modules {modules_ids[0]} & {modules_ids[1]}")

    # Générer le cours (une seule fois, stocké en session state)
    if not st.session_state.ts_response:
        with st.spinner("Chargement du cours marché..."):
            ville = ts.profile.ville_travail or None
            config = MarcheModuleConfig(
                modules_ids=modules_ids,
                ville_travail=ville,
                include_dvf_report=bool(ville),
            )
            runner = MarcheModuleRunner(config)
            st.session_state.ts_response = runner.generate_course()

    st.markdown(st.session_state.ts_response)

    # --- Conclusion formateur ---
    conclusion = (
        f"Voilà pour ces deux modules {prenom}. "
        f"Ces données, vous en aurez besoin face à vos clients — prix au m², encadrement, fiscalité. "
        f"On passe maintenant à vos questions sur ce qu'on vient de voir."
    )
    with st.chat_message("assistant"):
        st.markdown(conclusion)
        if st.button("🔊 Écouter la conclusion", key="tts_marche_conclusion"):
            play_audio_from_text(conclusion)

    st.markdown("---")
    if st.button("Continuer →", type="primary", key="btn_next_marche"):
        ts.record(Step.MINI_COURS_MARCHE, {
            "done": True,
            "modules_ids": modules_ids,
            "ville": ts.profile.ville_travail or "",
        })
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

    # Détecter si on vient d'un module marché (MINI_COURS_MARCHE est juste avant)
    steps = ts.steps
    current_idx = ts.current_step_index
    prev_step = steps[current_idx - 1] if current_idx > 0 else None
    is_after_marche = (prev_step == Step.MINI_COURS_MARCHE)

    if is_after_marche:
        modules_ids = get_marche_modules_for_session(ts.session_number)
        modules_str = f"modules marché {modules_ids[0]} et {modules_ids[1]}" if modules_ids else "modules marché"
        st.markdown(f"### Questions sur le marché immobilier")
        st.write(f"Tu viens d'étudier les {modules_str}. Pose tes questions sur ce contenu.")
        marche_suggestions = [
            "Qu'est-ce que l'encadrement des loyers et comment ça s'applique ?",
            "Comment utiliser les données DVF face à un vendeur ?",
            "Quels sont les impacts du Grand Paris Express sur les prix ?",
            "Comment expliquer la loi Climat et DPE à un acquéreur ?",
            "Quels risques RGA dois-je mentionner à l'acheteur ?",
            "Comment calculer le rendement locatif net en LMNP ?",
        ]
        suggestions = marche_suggestions
        placeholder = "Ex : Comment expliquer l'encadrement des loyers à un vendeur ?"
    else:
        st.markdown(f"### Questions & réponses — {theme['titre']}")
        st.write("Pose 1 ou 2 questions en lien avec le thème du jour.")
        suggestions = _suggested_questions(theme["titre"])
        placeholder = f"Ex : Comment aborder {theme['titre'].lower()} en rendez-vous ?"

    def _on_suggestion_click(suggestion: str) -> None:
        """Callback exécuté AVANT le render → modifie le widget sans conflit."""
        st.session_state.rag_question_input = suggestion

    question = st.text_input(
        "Ta question :",
        placeholder=placeholder,
        key="rag_question_input",
    )

    # Suggestions de questions fréquentes
    with st.expander("Questions fréquentes sur ce sujet", expanded=False):
        st.caption("Tu n'as pas de question ? Voici des pistes :")
        for i, sq in enumerate(suggestions):
            st.button(
                sq,
                key=f"suggested_q_{i}",
                on_click=_on_suggestion_click,
                args=(sq,),
            )

    if st.button("Obtenir une réponse", key="btn_rag_question"):
        if not question.strip():
            st.warning("Merci de saisir une question.")
        else:
            with st.spinner("Le formateur cherche dans la base..."):
                if is_after_marche:
                    # Enrichir la requête RAG avec le contexte marché pour orienter la recherche sémantique
                    enriched = f"[marché immobilier modules marché] {question.strip()}"
                    resp = repondre_faq(enriched)
                else:
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
    """Step COURS_CLES : cours oral conversationnel + point essentiel mis en valeur."""
    theme = ts.theme
    st.markdown(f"### Cours — {theme['titre']}")

    if not st.session_state.ts_response:
        if st.button("Lancer le cours"):
            with st.spinner("Le formateur prépare le cours..."):
                resp = repondre_cours_oral(theme["cours_cles"])
            st.session_state.ts_response = resp
            st.rerun()
        return

    raw = st.session_state.ts_response

    # Séparer le corps et le point essentiel sur le marqueur [POINT_ESSENTIEL]
    marker = "[POINT_ESSENTIEL]"
    if marker in raw:
        body, _, point_essentiel = raw.partition(marker)
        point_essentiel = point_essentiel.strip()
    else:
        # Fallback : pas de marqueur — affiche tout, pas de bloc spécial
        body = raw
        point_essentiel = ""

    st.write(body.strip())

    if point_essentiel:
        st.markdown("---")
        st.markdown("### 🎯 Point essentiel à retenir")
        st.markdown(f"## **{point_essentiel}**")

    if st.button("🔊 Lire à voix haute", key="tts_cours_cles"):
        tts_text = body.strip()
        if point_essentiel:
            tts_text += f"\n\nPoint essentiel à retenir : {point_essentiel}"
        play_audio_from_text(tts_text)

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
    result = _render_wa_component(
        theme_title=prev_theme["titre"],
        construire_contexte_fn=construire_contexte,
        chat_complete_fn=chat_complete,
        tone_override=tone_override,
        profile=ts.profile,
    )

    if result is not None:
        evaluation, should_continue = result
        if evaluation is not None and should_continue:
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

    # --- Message formateur fin de session ---
    st.markdown("---")
    st.markdown("### Message de votre formateur")

    score_quiz = quiz_data.get("score_pct", 0)
    wa_score = wa_data.get("score", 0) if wa_data and not wa_data.get("placeholder") else 0
    if wa_score:
        score_global = (score_quiz + wa_score) / 2
    else:
        score_global = score_quiz if score_quiz else 70

    if score_global >= 75:
        encouragement = "Excellente session aujourd'hui ! Vous progressez vraiment bien."
    elif score_global >= 60:
        encouragement = "Bonne session ! Vous êtes sur la bonne voie. Continuez ainsi."
    else:
        encouragement = "Session complétée ! Nous allons continuer à travailler ensemble. Cela va venir."

    next_day_str = (datetime.now() + timedelta(days=1)).strftime("%A %d %B")
    prenom_display = profile.prenom or ""
    message_fin = (
        f"{'Bravo ' + prenom_display + ' ! ' if prenom_display else 'Bravo ! '}{encouragement}\n\n"
        f"N'oubliez pas de relire votre fiche mémo avant demain. "
        f"Les points que nous avons identifiés ensemble, c'est là-dessus que nous allons travailler.\n\n"
        f"Nous nous retrouvons le {next_day_str} pour votre prochaine session. Reposez-vous bien, et à demain !\n\n"
        f"— Votre formateur IA"
    )

    st.info(message_fin)
    if st.button("Écouter", key="tts_message_fin"):
        play_audio_from_text(message_fin)

    st.markdown("---")
    st.success("Session terminée ! À demain pour continuer votre formation.")

    # --- Terminer (passe 1 — vider les widgets avant de changer de page) ---
    if st.button("Terminer la session"):
        ts.record(Step.SYNTHESE, {
            "done": True,
            "a_faire_demain": a_faire,
            "resume_cours": resume,
            "points_forts": points_forts,
            "axes_amelioration": axes,
        })
        # Sauvegarder ts (avec SYNTHESE enregistré) pour que passe 2 puisse appeler complete()
        _save_ts(ts)
        # Vider états widget avant que Streamlit démonte le DOM
        st.session_state.ts_response = ""
        st.session_state.ts_faq_response = ""
        st.session_state.ts_synthesis = None
        st.session_state.ts_pdf_bytes = None
        _reset_quiz()
        _reset_wa()
        _reset_profile()
        # Flag passe 2 : complete() + ts = None sera appliqué au prochain render
        st.session_state._do_session_end = True
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
        # Passe 1 : poser le flag, passe 2 nettoiera et relancera
        st.session_state._do_next_session = True
        st.rerun()


def ui_training():
    """UI principale du training engine — remplace l'ancien parcours guidé."""

    # ----------------------------------------------------------------
    # PASSE 2 — Transitions différées (anti-removeChild)
    # Ces flags sont posés par les handlers de boutons (passe 1) et
    # traités ici, en tête de render, avant tout widget, pour que le
    # DOM de l'étape précédente soit déjà démonté proprement.
    # ----------------------------------------------------------------

    # Transition step → step
    if st.session_state.pop("_do_step_transition", False):
        msg = st.session_state.pop("_pending_transition_msg", None)
        if msg:
            st.session_state.transition_message = msg
        st.rerun()
        return

    # Fin de session (bouton "Terminer la session") — passe 2
    if st.session_state.pop("_do_session_end", False):
        # Appel de complete() ici (passe 2) pour éviter tout crash DOM en passe 1
        ts_dict = st.session_state.ts
        if ts_dict is not None:
            try:
                ts_end = TrainingSession.from_dict(ts_dict)
                session_num_before = ts_end.session_number
                print(f"[DEBUG] AVANT complete(): session_number={session_num_before}, "
                      f"current_session_fichier={load_progress().get('current_session')}")
                ts_end.complete()
                print(f"[DEBUG] APRÈS complete(): current_session_fichier={load_progress().get('current_session')}")
            except Exception as e:
                # Fallback : incrémenter directement si complete() échoue
                print(f"[DEBUG] complete() a échoué ({e}), fallback increment direct")
                progress = load_progress()
                session_num_before = progress.get("current_session", 1)
                progress["current_session"] = session_num_before + 1
                if "sessions_history" not in progress:
                    progress["sessions_history"] = []
                progress["sessions_history"].append({
                    "session": session_num_before,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "completed_at": datetime.now().isoformat(timespec="seconds"),
                    "data": {},
                })
                save_progress(progress)
                print(f"[DEBUG] Fallback: current_session sauvegardé = {progress['current_session']}")
        st.session_state.ts = None
        st.rerun()
        return

    # Démarrer la session suivante (bouton "Commencer la session suivante")
    if st.session_state.pop("_do_next_session", False):
        st.session_state.ts = None
        st.session_state.ts_response = ""
        st.session_state.ts_faq_response = ""
        st.session_state.ts_synthesis = None
        st.session_state.ts_pdf_bytes = None
        _reset_quiz()
        _reset_wa()
        _reset_profile()
        st.rerun()
        return

    # ----------------------------------------------------------------

    _init_training_state()

    ts = _get_or_create_session()

    # Session terminée ?
    if ts.is_complete:
        _render_session_complete()
        return

    # Header + sidebar : masqués pendant l'onboarding
    # (la sidebar et le layout 3 colonnes sont gérés dans render_profile_onboarding)
    if ts.current_step != Step.PROFIL:
        _render_step_header(ts)
        st.markdown("---")
        with st.sidebar:
            _render_sidebar_training(ts)
    else:
        # Masquer la vraie sidebar Streamlit pour que la colonne CSS prenne toute la place
        st.markdown(
            '<style>[data-testid="stSidebar"]{display:none}</style>',
            unsafe_allow_html=True,
        )

    # Layout 2 colonnes : contenu (gauche) | avatar (droite)
    # Pendant l'onboarding, le layout avatar est géré dans render_profile_onboarding
    step = ts.current_step
    if step == Step.PROFIL:
        _render_profil(ts)
    else:
        col_content, col_avatar = st.columns([3, 1])
        with col_avatar:
            profile = ts.profile if ts.profile.prenom else None
            _render_avatar_panel(profile, ts=ts)
        with col_content:
            # Message de transition entre étapes
            if st.session_state.get("transition_message"):
                message = st.session_state.transition_message
                mood = (
                    "encouraging"
                    if any(w in message for w in ["Quiz", "Simulation", "Excellent", "Bravo"])
                    else "neutral"
                )
                show_formateur_message(
                    message=message,
                    key=f"transition_{ts.current_step.value}",
                    mood=mood,
                )
                if st.button("C'est parti !", key="btn_start_step", type="primary"):
                    st.session_state.transition_message = None
                    st.rerun()
                return

            if step == Step.MINI_COURS_MARCHE:
                _render_mini_cours_marche(ts)
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


# -----------------------------
# APP UI
# -----------------------------
def _render_avatar_panel(profile=None, ts=None) -> None:
    """Colonne avatar droite : vidéo/image puis chat rapide formateur."""
    from pathlib import Path

    if profile is not None:
        avatar_name = profile.avatar_name
        img_path = Path(profile.avatar_image_path)
        vid_path = Path(profile.avatar_video_path)
        emoji = "👨‍🏫" if profile.genre == "homme" else "👩‍🏫"
    else:
        avatar_name = "IALIX"
        img_path = Path("assets/avatars/ialix.png")
        vid_path = Path("assets/avatars/ialix_video.mp4")
        emoji = "👩‍🏫"

    # 1. Avatar (vidéo ou image)
    if vid_path.exists():
        st.video(str(vid_path), autoplay=True, loop=True, muted=True)
    elif img_path.exists():
        st.image(str(img_path), use_container_width=True)
    else:
        st.markdown(
            f"""
<div style="width:100%;aspect-ratio:9/16;background:linear-gradient(135deg,#00B4A6 0%,#1e293b 100%);
            border-radius:16px;display:flex;align-items:center;justify-content:center;
            color:white;font-size:64px;">{emoji}</div>""",
            unsafe_allow_html=True,
        )
    st.markdown(f"**{avatar_name}**")
    st.caption("🟢 Formateur·rice IA · En direct")

    st.markdown("---")

    # 2. Chat rapide sous l'avatar
    st.markdown(f"**💬 Questions à {avatar_name}**")

    history = st.session_state.avatar_chat_history
    # Afficher l'historique (max 6 derniers messages pour ne pas surcharger)
    for msg in history[-6:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

    user_input = st.chat_input("Pose une question...", key="avatar_chat_input")
    if user_input and user_input.strip():
        history.append({"role": "user", "text": user_input.strip()})
        with st.chat_message("user"):
            st.markdown(user_input.strip())
        with st.chat_message("assistant"):
            with st.spinner(""):
                resp = repondre_faq(user_input.strip())
            st.markdown(resp)
        history.append({"role": "assistant", "text": resp})
        st.session_state.avatar_chat_history = history


def _render_sidebar_training(ts) -> None:
    """Sidebar sombre pour le mode Parcours guidé : logo + profil + timeline + actions."""
    from pathlib import Path

    # Logo
    logo_path = Path("assets/logo_aimmo.png")
    if logo_path.exists():
        st.image(str(logo_path), width=180)
    else:
        st.markdown("### 🏠 AI-mmo Training")

    st.markdown("---")

    # Résumé profil
    profile = ts.profile
    if profile.prenom:
        avatar_name = profile.avatar_name
        st.markdown(f"**{avatar_name} × {profile.prenom}**")
        if profile.ville_travail:
            st.caption(f"📍 {profile.ville_travail}")
        st.caption(f"📊 Séance {ts.session_number}/{ts.total_sessions}")

    st.markdown("---")

    # Timeline verticale
    st.markdown("**Déroulé**")
    for idx, step in enumerate(ts.steps):
        label = STEP_LABELS.get(step, step.value)
        if idx < ts.current_step_index:
            st.markdown(f"✅ ~~{label}~~")
        elif idx == ts.current_step_index:
            st.markdown(
                f"<span style='color:#00B4A6;font-weight:600'>▶ {label}</span>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"<span style='opacity:.5'>○ {label}</span>", unsafe_allow_html=True)

    st.markdown("---")

    # Actions
    if st.button("🔄 Recommencer cette session", key="btn_reset_session"):
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

    if st.button("📝 Modifier mon profil", key="btn_edit_profile"):
        _start_edit_profile()

    st.markdown("---")
    col_prev, col_next = st.columns(2)
    with col_prev:
        if ts.session_number > 1:
            if st.button("◀", key="btn_prev_session", help="Session précédente"):
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
            if st.button("▶", key="btn_next_session", help="Session suivante"):
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


def render_header() -> None:
    """Header moderne : logo à gauche + menu profil déroulant à droite."""
    col_logo, col_profile = st.columns([3, 1])

    with col_logo:
        st.markdown("### 🏠 Agent-Immo Formateur")

    with col_profile:
        progress = load_progress()
        profile = progress.get("profile", {})
        prenom = profile.get("prenom", "")

        if prenom:
            with st.popover(f"👤 {prenom} ▼"):
                st.markdown(f"**{prenom}**")

                ville = profile.get("ville_travail", "")
                if ville:
                    st.caption(f"📍 {ville}")

                sessions_done = len(progress.get("sessions_history", []))
                session_num = 1 if sessions_done == 0 else progress.get("current_session", 1)
                st.caption(f"📊 Séance {session_num}/104")

                st.markdown("---")

                if st.button("📝 Mon profil", key="menu_profile"):
                    _start_edit_profile()

                if st.button("📄 Mes mémos", key="menu_memos"):
                    st.info("Fonctionnalité à venir")

                if st.button("📈 Ma progression", key="menu_progress"):
                    st.info("Fonctionnalité à venir")

                st.markdown("---")

                if st.button("🚪 Réinitialiser", key="menu_reset"):
                    if PROGRESS_FILE.exists():
                        PROGRESS_FILE.unlink()
                    st.session_state.ts = None
                    st.session_state.ts_editing_profile = False
                    st.rerun()
        else:
            st.caption("Formation immobilière IA")

    st.markdown("---")


def _start_edit_profile() -> None:
    """Lance l'édition du profil depuis n'importe quelle étape."""
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


def _inject_custom_css() -> None:
    """Injecte le CSS global — palette AI-mmo Training."""
    st.markdown(
        """
<style>
/* Palette AI-mmo Training */
:root {
    --primary: #00B4A6;
    --secondary: #1e293b;
    --bg: #f8fafc;
    --text-dark: #1a202c;
    --text-light: #e2e8f0;
    --card: #ffffff;
}

/* Sidebar dark */
[data-testid="stSidebar"] {
    background-color: var(--secondary) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-light) !important;
}
[data-testid="stSidebar"] hr {
    border-color: #334155 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: #334155;
    color: var(--text-light) !important;
    border: 1px solid #475569;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--primary);
    border-color: var(--primary);
}

/* Titres */
h1, h2, h3 { color: var(--text-dark); font-weight: 600; }

/* Boutons principaux */
.stButton > button {
    border-radius: 8px; font-weight: 500;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,180,166,0.3);
}
button[kind="primary"] {
    background-color: var(--primary) !important;
    border-color: var(--primary) !important;
}
button[kind="primary"]:hover {
    background-color: #008f82 !important;
}

/* Alertes */
.stAlert { border-radius: 12px; border-left: 4px solid var(--primary); }

/* Masquer menu hamburger et footer Streamlit */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>""",
        unsafe_allow_html=True,
    )


def main():
    _inject_custom_css()
    render_header()

    st.sidebar.markdown("### 🎓 Votre parcours guidé")
    st.sidebar.info("Session structurée du jour — suivez les étapes.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎁 Outils bonus")

    bonus_mode = st.sidebar.radio(
        "Accès rapide :",
        [
            "Questions libres",
            "Fiche mémo : que faut-il retenir ?",
            "Préparez votre rendez-vous client",
        ],
        index=None,
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Base de connaissances alimentée par vos PDF de formation.")

    # Résoudre le mode effectif
    if bonus_mode is None:
        mode = "Parcours guidé (contenu structuré)"
    elif bonus_mode == "Questions libres":
        mode = "Questions rapides (FAQ métier)"
    elif bonus_mode == "Fiche mémo : que faut-il retenir ?":
        mode = "Fiche mémo (synthèse sur un thème)"
    else:
        mode = "Plan d'entretien structuré"

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
