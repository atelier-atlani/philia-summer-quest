import os
from datetime import datetime, timedelta
from pathlib import Path

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
from config.constants import AVATAR_CHAT_EMOJI, VIDEO_INTRO, LOGO_IAXEL, LOGO_AIMMO
from core.tts import tts_to_bytes
from training.engine import TrainingSession
from training.steps import Step, STEP_LABELS, get_steps_for_session
from training.marche_module import MarcheModuleRunner, MarcheModuleConfig, get_marche_modules_for_session
from training.modules.marche.cascade_analysis import CascadeMarche
from training.content import TOTAL_SESSIONS
from training.progress import load_progress, save_progress, save_profile, save_lacunes, PROGRESS_FILE
from training.profile_ui import render_profile_onboarding, _reset_profile
from training.chat_libre import render_chat_libre
from training.formateur_messages import message_formateur
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
    # Debug désactivé en prod

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
    if "_show_dashboard" not in st.session_state:
        st.session_state._show_dashboard = False
    if "ts_editing_profile" not in st.session_state:
        st.session_state.ts_editing_profile = False
    if "transition_message" not in st.session_state:
        st.session_state.transition_message = None
    if "chat_libre_history" not in st.session_state:
        st.session_state.chat_libre_history = []


def _get_transition_message(from_step: Step, to_step: Step, profile) -> str:
    """Génère un message de transition entre deux étapes."""
    prenom = profile.prenom or "champion"

    transitions = {
        # Jour 1
        (Step.PROFIL,            Step.MINI_COURS_MARCHE): f"Parfait {prenom} ! Votre profil est enregistré. On commence par un point marché immobilier — 2 modules rapides pour ancrer vos connaissances terrain. C'est parti !",
        # Jour 2+ (ouverture)
        (Step.MINI_COURS_MARCHE, Step.QUESTIONS_RAG):     f"Bien {prenom} — vous avez vu les données. Maintenant... c'est à vous. Des questions sur ce qu'on vient de voir ? Un point qui vous a surpris — ou que vous aimeriez approfondir ? C'est le moment d'en discuter.",
        (Step.QUESTIONS_RAG,     Step.COURS_CLES):        "Passons maintenant au cours clés du jour. C'est l'essentiel à retenir absolument.",
        (Step.COURS_CLES,        Step.QUIZ):              "Maintenant, nous allons tester tout cela avec un quiz. Vous allez voir, c'est rapide et interactif.",
        (Step.QUIZ,              Step.WHATSAPP):          f"Quiz terminé {prenom} — bien joué ! Maintenant... on passe aux choses sérieuses. Un client va vous appeler — un cas terrain concret. Montrez-moi ce que vous savez faire.",
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
        session_num = max(1, progress.get("current_session", 1))
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


def _reset_all_step_states() -> None:
    """Nettoie tous les états liés aux steps pour éviter les fuites entre étapes.

    À appeler avant chaque transition : advance, reset session, navigation.
    NE gère PAS : ts (session), transition_message, chat_libre_history, bonus_*.
    """
    st.session_state.ts_response = ""
    st.session_state.ts_faq_response = ""
    st.session_state.ts_synthesis = None
    st.session_state.ts_pdf_bytes = None
    st.session_state.ts_editing_profile = False
    _reset_quiz()
    _reset_wa()       # nettoie wa_session, wa_evaluation, wa_difficulty, wa_ringing, _tts_wa_*
    _reset_profile()
    st.session_state.pop("cascade_answers", None)
    st.session_state.pop("cascade_submitted", None)
    st.session_state.pop("marche_intro_text", None)
    st.session_state.pop("cours_cles_intro", None)
    st.session_state.pop("marche_c_mondial", None)
    st.session_state.pop("marche_c_national", None)
    st.session_state.pop("marche_c_local", None)
    st.session_state.pop("_tts_cas_pratique_audio", None)
    st.session_state.pop("_tts_cas_pratique_concat", None)
    for key in list(st.session_state.keys()):
        if key.startswith("_tts_") or key.startswith("dvf_data_") or key.startswith("rag_suggestions_"):
            st.session_state.pop(key, None)


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
    _reset_all_step_states()
    # Stocker le message pour passe 2
    st.session_state._pending_transition_msg = _get_transition_message(
        from_step, ts.current_step, ts.profile
    )
    st.session_state._do_step_transition = True
    st.rerun()


def _render_step_header(ts: TrainingSession):
    """Affiche le header commun : info stagiaire + barre de progression."""
    profile = ts.profile
    if profile.prenom:
        st.markdown(
            f'<p style="color:#1f3a5f;margin:0 0 8px 0;">'
            f"<strong>Stagiaire :</strong> {profile.prenom} — "
            f"<strong>Niveau :</strong> {profile.niveau_label} — "
            f"<strong>Rôle :</strong> {profile.role_label}"
            f"</p>",
            unsafe_allow_html=True,
        )

    steps = ts.steps
    idx = ts.current_step_index
    total = len(steps)
    progress = (idx + 1) / total if total else 0.0
    step_label = ts.step_label()

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
            with st.spinner("IAXEL prépare le cours..."):
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

    if not modules_ids:
        st.info("Aucun module marché pour cette session.")
        if st.button("Continuer →", key="btn_skip_marche"):
            ts.record(Step.MINI_COURS_MARCHE, {"done": True, "skipped": True})
            _advance_step(ts)
        return

    # --- Intro formateur (LLM, mise en cache) ---
    ville = ts.profile.ville_travail or "votre secteur"
    if "marche_intro_text" not in st.session_state:
        intro_prompt_system = (
            "Tu es IAXEL, formateur immobilier senior passionné. "
            "Tu fais une introduction ORALE de 4-5 phrases pour ton cours marché. "
            "STYLE ORAL OBLIGATOIRE : "
            "- Utilise des tirets — pour créer des pauses "
            "- Utilise ... pour les hésitations naturelles "
            "- Phrases courtes, rythme varié "
            "- Termine par une invitation à lire les 3 onglets ET annonce le petit test de 4 questions après "
            "- Vouvoiement, ton mentor passionné "
            "Exemple de ton : 'Les taux de la BCE à Francfort... ça vous semble loin ? "
            "Et pourtant — c'est exactement ce qui détermine le budget de votre client demain matin. "
            "Lisez les trois onglets — mondial, national, et surtout local avec les vraies données de votre marché. "
            "Ensuite... quatre questions pour vérifier que vous avez capté l'essentiel.'"
        )
        ville = ts.profile.ville_travail or "votre ville"
        intro_prompt_user = (
            f"Stagiaire : {prenom}, travaille à {ville}.\n"
            f"Session n°{ts.session_number}.\n\n"
            "Fais une intro COURTE (4-5 phrases max) qui :\n"
            "1. Accroche avec un fait marquant sur les taux ou la crise\n"
            "2. Fait le lien mondial → national → local en UNE phrase\n"
            f"3. Invite à lire les 3 onglets et comparer les données de {ville}\n"
            "4. Annonce les questions dans chaque onglet et les 4 questions du test final\n"
            "5. Utilise — pour les pauses et ... pour les hésitations\n"
            "IMPORTANT : sois COURT. 4-5 phrases maximum. Pas de listes."
        )
        with st.spinner("IAXEL prépare l'introduction..."):
            intro = chat_complete(intro_prompt_system, intro_prompt_user, 0.6)
        st.session_state["marche_intro_text"] = intro
    else:
        intro = st.session_state["marche_intro_text"]

    with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
        st.markdown(intro)

    # TTS auto-play de l'intro (une seule fois)
    if not st.session_state.get("_tts_marche_intro", False):
        try:
            from core.tts import tts_smart
            audio_data = tts_smart(client, intro, priority="high")
            if audio_data:
                fmt = "audio/mpeg" if audio_data[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                st.audio(audio_data, format=fmt, autoplay=False)
        except Exception:
            pass
        st.session_state["_tts_marche_intro"] = True

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

    # --- Mentorat en entonnoir : Mondial → National → Local ---
    ville = ts.profile.ville_travail or None
    cascade = CascadeMarche().analyze(ville)
    m = cascade["mondial"]
    n = cascade["national"]
    loc = cascade["local"]

    from training.marche_charts import (  # noqa: PLC0415
        chart_taux_credit, chart_volumes_ventes,
        chart_impact_taux_budget, chart_dpe_repartition,
    )

    tab_mondial, tab_national, tab_local = st.tabs(
        ["🌐 Niveau Mondial", "🇫🇷 Niveau National", f"📍 Niveau Local — {cascade['ville']}"]
    )

    with tab_mondial:
        st.markdown("#### Les taux directeurs et leur impact sur votre marché")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Taux crédit moyen", f"{m['taux_credit']}%")
        with col2:
            st.metric("Taux BCE", f"{m['taux_bce']}%")
        with col3:
            st.metric("Inflation France", f"{m['inflation']}%")
        st.info(f"**Ce que ça change pour vos clients** : {m['impact_emprunt']}")
        st.plotly_chart(chart_taux_credit(), use_container_width=True)
        st.plotly_chart(chart_impact_taux_budget(taux_actuel=float(m['taux_credit'])), use_container_width=True)
        with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
            st.markdown(
                "Ces chiffres ne sont pas abstraits. "
                "Quand la BCE monte ses taux, vos clients empruntent moins facilement — "
                "et votre argumentaire prix doit en tenir compte."
            )
        st.markdown("---")
        st.markdown("**🎯 Question IAXEL :**")
        q_mondial = "Comment expliquez-vous à un vendeur que les taux BCE impactent le prix de son bien ?"
        st.markdown(f"*{q_mondial}*")
        answer_mondial = st.text_area(
            "Votre réponse :",
            key="marche_q_mondial",
            height=100,
            placeholder="Répondez comme si vous étiez face au vendeur...",
        )
        if st.button("Valider ma réponse", key="btn_marche_q_mondial"):
            if answer_mondial.strip():
                with st.spinner("IAXEL analyse votre réponse..."):
                    correction_system = (
                        "Tu es IAXEL, formateur immobilier. Un stagiaire répond à ta question. "
                        "Évalue sa réponse en 3-4 phrases ORALES : "
                        "1) Ce qui est bien. 2) Ce qui manque ou peut être amélioré. "
                        "3) Une formulation terrain idéale réutilisable. "
                        "Utilise — pour les pauses et ... pour les hésitations. Vouvoiement."
                    )
                    correction_user = (
                        f"Question : {q_mondial}\n"
                        f"Réponse du stagiaire : {answer_mondial}\n"
                        "Contexte : taux BCE ~3.6%, chaque point de taux en plus = ~10% de capacité d'emprunt en moins."
                    )
                    st.session_state["marche_c_mondial"] = chat_complete(correction_system, correction_user, 0.4)
                st.rerun()
            else:
                st.warning("Tapez votre réponse avant de valider.")
        if st.session_state.get("marche_c_mondial"):
            correction = st.session_state["marche_c_mondial"]
            with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
                st.markdown(correction)
            tts_key = "_tts_marche_c_mondial"
            if not st.session_state.get(tts_key, False):
                try:
                    from core.tts import tts_smart  # noqa: PLC0415
                    audio = tts_smart(client, correction, priority="high")
                    if audio:
                        fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                        st.audio(audio, format=fmt, autoplay=False)
                except Exception:
                    pass
                st.session_state[tts_key] = True

    with tab_national:
        st.markdown("#### Les règles nationales qui impactent chaque vente")
        st.markdown("**Loi Climat — DPE :**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.error("DPE G\nInterdit location 2025")
        with col2:
            st.warning("DPE F\nInterdit location 2028")
        with col3:
            st.info("DPE E\nInterdit location 2034")
        st.markdown("---")
        st.markdown(f"**ZAN (Zéro Artificialisation Nette)** : {n['zan']['objectif_2031']}")
        st.markdown(
            f"**HCSF** : endettement max {n['hcsf']['taux_endettement_max']}% "
            f"(dérogation possible pour {n['hcsf']['part_derogation']}% des dossiers)"
        )
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.plotly_chart(chart_volumes_ventes(), use_container_width=True)
        with col_chart2:
            st.plotly_chart(chart_dpe_repartition(), use_container_width=True)
        with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
            st.markdown(
                "Ces règles nationales, vos acquéreurs et vendeurs n'en ont souvent pas conscience. "
                "C'est votre rôle de les alerter — surtout sur le DPE."
            )
        st.markdown("---")
        st.markdown("**🎯 Question IAXEL :**")
        q_national = "Face à un bien classé DPE F, que conseillez-vous au propriétaire ?"
        st.markdown(f"*{q_national}*")
        answer_national = st.text_area(
            "Votre réponse :",
            key="marche_q_national",
            height=100,
            placeholder="Répondez comme si vous étiez face au propriétaire...",
        )
        if st.button("Valider ma réponse", key="btn_marche_q_national"):
            if answer_national.strip():
                with st.spinner("IAXEL analyse votre réponse..."):
                    correction_system = (
                        "Tu es IAXEL, formateur immobilier. Un stagiaire répond à ta question. "
                        "Évalue sa réponse en 3-4 phrases ORALES : ce qui est juste, ce qui manque, "
                        "et donne une formulation terrain percutante. "
                        "Utilise — pour les pauses. Vouvoiement. Sois direct, pas condescendant."
                    )
                    correction_user = (
                        f"Question : {q_national}\n"
                        f"Réponse du stagiaire : {answer_national}\n"
                        "Contexte : DPE F interdit à la location dès 2028, DPE G dès 2025. "
                        "Conseils possibles : travaux de rénovation, décote prix, stratégie de vente avant la date limite."
                    )
                    st.session_state["marche_c_national"] = chat_complete(correction_system, correction_user, 0.4)
                st.rerun()
            else:
                st.warning("Tapez votre réponse avant de valider.")
        if st.session_state.get("marche_c_national"):
            correction = st.session_state["marche_c_national"]
            with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
                st.markdown(correction)
            tts_key = "_tts_marche_c_national"
            if not st.session_state.get(tts_key, False):
                try:
                    from core.tts import tts_smart  # noqa: PLC0415
                    audio = tts_smart(client, correction, priority="high")
                    if audio:
                        fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                        st.audio(audio, format=fmt, autoplay=False)
                except Exception:
                    pass
                st.session_state[tts_key] = True

    with tab_local:
        st.markdown(f"#### Le marché concret à {cascade['ville']}")

        # --- Données DVF dynamiques ---
        ville_travail = ts.profile.ville_travail or ""
        dvf_key = f"dvf_data_{ville_travail}" if ville_travail else None

        if ville_travail:
            if dvf_key not in st.session_state:
                with st.spinner(f"Chargement des données DVF pour {ville_travail}..."):
                    from training.dvf_connector import analyze_market  # noqa: PLC0415
                    st.session_state[dvf_key] = analyze_market(ville_travail)

            dvf = st.session_state[dvf_key]

            if dvf.get("disponible"):
                st.caption(
                    f"Données réelles DVF — {dvf.get('periode', 'Données 2024')} — "
                    f"{dvf['nb_transactions']} transactions"
                )
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix médian", f"{dvf['prix_median_m2']:,} €/m²".replace(",", " "))
                with col2:
                    st.metric("Prix moyen", f"{dvf['prix_moyen_m2']:,} €/m²".replace(",", " "))
                with col3:
                    st.metric("Transactions", str(dvf["nb_transactions"]))

                st.markdown(
                    f"**Fourchette** : {dvf['prix_min_m2']:,} — {dvf['prix_max_m2']:,} €/m² "
                    f"(Q1 : {dvf.get('prix_q1_m2', 0):,} | Q3 : {dvf.get('prix_q3_m2', 0):,})".replace(",", " ")
                )

                types = dvf.get("types", {})
                if types:
                    st.markdown(
                        f"**Répartition** : {types.get('Appartement', 0)} appartements, "
                        f"{types.get('Maison', 0)} maisons"
                    )

                recentes = dvf.get("transactions_recentes", [])
                if recentes:
                    st.markdown("---")
                    st.markdown("**5 dernières ventes**")
                    for t in recentes:
                        pieces_str = f"{t['pieces']}p" if t.get("pieces") else ""
                        st.markdown(
                            f"• **{t['type']}** {t['surface']}m² {pieces_str} — "
                            f"**{t['prix']:,} €** ({t['prix_m2']:,} €/m²) — "
                            f"{t.get('adresse', '')} — {t['date']}".replace(",", " ")
                        )

                st.markdown("---")
                st.info(
                    f"**Pour votre prochain rendez-vous** : le prix médian à {ville_travail} est de "
                    f"**{dvf['prix_median_m2']:,} €/m²**. Utilisez ce chiffre face au vendeur "
                    f"pour ancrer la discussion sur des données objectives.".replace(",", " ")
                )
            else:
                # Fallback sur données statiques si DVF indisponible
                st.warning(f"DVF : {dvf.get('message', 'Données non disponibles')}")
                if loc.get("disponible"):
                    col1, col2 = st.columns(2)
                    with col1:
                        prix_str = f"{loc['prix_median']:,} €/m²".replace(",", " ") if loc.get("prix_median") else "N/D"
                        st.metric("Prix médian (estimé)", prix_str)
                    with col2:
                        st.metric("Fourchette", loc["prix_range"])
                    if loc.get("encadrement_loyers"):
                        st.success("Encadrement des loyers en vigueur dans cette zone")
                else:
                    st.caption(loc.get("message", ""))
        else:
            st.warning("Renseignez votre ville de travail dans votre profil pour voir les données DVF de votre marché local.")
            if loc.get("disponible"):
                col1, col2 = st.columns(2)
                with col1:
                    prix_str = f"{loc['prix_median']:,} €/m²".replace(",", " ") if loc.get("prix_median") else "N/D"
                    st.metric("Prix médian (estimé)", prix_str)
                with col2:
                    st.metric("Fourchette", loc["prix_range"])

        st.markdown("---")
        st.info(f"**Cohérence 3 niveaux** : {cascade['coherence']}")
        with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
            st.markdown(
                "Voilà les données locales qui comptent vraiment. "
                "Ce sont ces chiffres que vous sortez en rendez-vous vendeur — "
                "pas des estimations vagues, des données réelles."
            )
        st.markdown("---")
        st.markdown("**🎯 Question IAXEL :**")
        prix_median_local = ""
        if ville_travail and st.session_state.get(f"dvf_data_{ville_travail}", {}).get("disponible"):
            prix_median_local = f" (médiane DVF : {st.session_state[f'dvf_data_{ville_travail}']['prix_median_m2']:,} €/m²)".replace(",", " ")
        ville_label = ville_travail or cascade["ville"]
        q_local = f"Un vendeur à {ville_label} vous dit que son bien vaut 20% de plus que le prix médian DVF. Que répondez-vous ?"
        st.markdown(f"*{q_local}*")
        answer_local = st.text_area(
            "Votre réponse :",
            key="marche_q_local",
            height=100,
            placeholder="Répondez comme si vous étiez face au vendeur...",
        )
        if st.button("Valider ma réponse", key="btn_marche_q_local"):
            if answer_local.strip():
                with st.spinner("IAXEL analyse votre réponse..."):
                    correction_system = (
                        "Tu es IAXEL, formateur immobilier. Un stagiaire répond à ta question. "
                        "Évalue sa réponse en 3-4 phrases ORALES : ce qui est juste, ce qui manque, "
                        "et donne une formulation terrain percutante. "
                        "Utilise — pour les pauses. Vouvoiement. Sois direct, pas condescendant."
                    )
                    correction_user = (
                        f"Question : {q_local}\n"
                        f"Réponse du stagiaire : {answer_local}\n"
                        f"Contexte : données DVF réelles{prix_median_local}. "
                        "L'ACM avec comparables vendus récents est l'argument clé. "
                        "Eviter de valider l'estimation haute du vendeur sans données."
                    )
                    st.session_state["marche_c_local"] = chat_complete(correction_system, correction_user, 0.4)
                st.rerun()
            else:
                st.warning("Tapez votre réponse avant de valider.")
        if st.session_state.get("marche_c_local"):
            correction = st.session_state["marche_c_local"]
            with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
                st.markdown(correction)
            tts_key = "_tts_marche_c_local"
            if not st.session_state.get(tts_key, False):
                try:
                    from core.tts import tts_smart  # noqa: PLC0415
                    audio = tts_smart(client, correction, priority="high")
                    if audio:
                        fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                        st.audio(audio, format=fmt, autoplay=False)
                except Exception:
                    pass
                st.session_state[tts_key] = True

    # Support du cours complet (optionnel)
    with st.expander("📖 Support du cours complet", expanded=False):
        st.markdown(st.session_state.ts_response)

    # --- Jeu interactif Cascade ---
    st.markdown("---")
    st.markdown("### 🎯 Mini-jeu : Comprenez-vous les liens du marché ?")
    st.caption("Testez votre compréhension des connexions Mondial → National → Local")

    from training.marche_quiz import get_cascade_questions  # noqa: PLC0415

    cascade_qs = get_cascade_questions()

    if "cascade_answers" not in st.session_state:
        st.session_state.cascade_answers = {}
    if "cascade_submitted" not in st.session_state:
        st.session_state.cascade_submitted = False

    if not st.session_state.cascade_submitted:
        for i, q in enumerate(cascade_qs):
            st.markdown(f"**{q['event']}**")
            st.markdown(f"*{q['level']}* — {q['question']}")
            answer = st.radio(
                "Votre réponse :",
                q["choices"],
                key=f"cascade_q_{i}",
                index=None,
            )
            if answer is not None:
                st.session_state.cascade_answers[i] = q["choices"].index(answer)
            st.markdown("---")

        all_answered = len(st.session_state.cascade_answers) == len(cascade_qs)
        if all_answered:
            if st.button("Valider mes réponses", type="primary", key="btn_cascade_submit"):
                st.session_state.cascade_submitted = True
                st.rerun()
        else:
            st.info(f"Répondez aux {len(cascade_qs)} questions pour valider.")
    else:
        score = 0
        for i, q in enumerate(cascade_qs):
            chosen = st.session_state.cascade_answers.get(i, -1)
            is_correct = chosen == q["correct"]
            if is_correct:
                score += 1
            st.markdown(f"**{q['event']}**")
            if is_correct:
                st.success(f"✅ Bonne réponse ! {q['explanation']}")
            else:
                st.error(
                    f"❌ Votre réponse : {q['choices'][chosen]}\n\n"
                    f"**Bonne réponse** : {q['choices'][q['correct']]}\n\n"
                    f"{q['explanation']}"
                )
            st.markdown("---")

        pct = round(score / len(cascade_qs) * 100)
        if pct >= 75:
            st.success(f"🎯 {score}/{len(cascade_qs)} — Excellent ! Vous comprenez les mécanismes du marché.")
            cascade_comment = f"Excellent — {score} sur {len(cascade_qs)}. Vous avez bien saisi les liens entre les niveaux du marché. C'est exactement ce qu'on cherche."
        elif pct >= 50:
            st.info(f"🎯 {score}/{len(cascade_qs)} — Pas mal ! Quelques liens à consolider.")
            cascade_comment = f"{score} sur {len(cascade_qs)} — c'est bien. Quelques connexions à solidifier... mais la logique est là."
        else:
            st.warning(f"🎯 {score}/{len(cascade_qs)} — Revoyez les onglets ci-dessus, les liens vont devenir clairs.")
            cascade_comment = f"{score} sur {len(cascade_qs)}. Pas d'inquiétude — ces liens marché mondial, national, local — ça s'acquiert avec la pratique. Relisez les onglets."
        tts_cascade_key = "_tts_cascade_result"
        if not st.session_state.get(tts_cascade_key, False):
            try:
                from core.tts import tts_smart  # noqa: PLC0415
                audio = tts_smart(client, cascade_comment, priority="high")
                if audio:
                    fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                    st.audio(audio, format=fmt, autoplay=False)
            except Exception:
                pass
            st.session_state[tts_cascade_key] = True

    # --- Conclusion formateur ---
    conclusion = (
        f"Voilà pour ces deux modules {prenom}. "
        f"Ces données, vous en aurez besoin face à vos clients — prix au m², encadrement, fiscalité. "
        f"On passe maintenant à vos questions sur ce qu'on vient de voir."
    )
    with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
        st.markdown(conclusion)
        if st.button("🔊 Écouter la conclusion", key="tts_marche_conclusion"):
            play_audio_from_text(conclusion)

    st.markdown("---")
    if st.button("Continuer →", type="primary", key="btn_next_marche"):
        cascade_qs_for_record = get_cascade_questions()
        cascade_answers_record = st.session_state.get("cascade_answers", {})
        cascade_score = sum(
            1 for i, q in enumerate(cascade_qs_for_record)
            if cascade_answers_record.get(i, -1) == q["correct"]
        )
        ts.record(Step.MINI_COURS_MARCHE, {
            "done": True,
            "modules_ids": modules_ids,
            "ville": ts.profile.ville_travail or "",
            "marche_scores": {
                "mondial_answered": bool(st.session_state.get("marche_c_mondial")),
                "national_answered": bool(st.session_state.get("marche_c_national")),
                "local_answered": bool(st.session_state.get("marche_c_local")),
            },
            "cascade_score": cascade_score,
            "cascade_total": len(cascade_qs_for_record),
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


def _sticky_continue_button(label: str, key: str, ts: TrainingSession, step: Step, record_data: dict | None = None):
    """Bouton Continuer toujours visible en bas de l'écran (sticky)."""
    st.markdown(
        '<div style="position:sticky;bottom:0;background:white;padding:12px 0;'
        'border-top:1px solid #e2e8f0;z-index:100;">',
        unsafe_allow_html=True,
    )
    if st.button(label, key=key, type="primary", use_container_width=True):
        if record_data is not None:
            ts.record(step, record_data)
        _advance_step(ts)
    st.markdown('</div>', unsafe_allow_html=True)


def _render_questions_rag(ts: TrainingSession):
    """Step QUESTIONS_RAG : 1-2 questions libres + réponses RAG."""
    theme = ts.theme

    # Détecter si on vient d'un module marché (MINI_COURS_MARCHE est juste avant)
    steps = ts.steps
    current_idx = ts.current_step_index
    prev_step = steps[current_idx - 1] if current_idx > 0 else None
    is_after_marche = (prev_step == Step.MINI_COURS_MARCHE)

    if is_after_marche:
        st.markdown("### Questions sur le marché immobilier")
        with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
            st.markdown(
                f"Vous venez de voir pas mal de données — taux, volumes, DPE, "
                f"et les chiffres de {ts.profile.ville_travail or 'votre marché'}... "
                f"Des questions ? Un point que vous aimeriez creuser ? "
                f"Choisissez une question ci-dessous ou posez la vôtre."
            )
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
        suggestions_key = f"rag_suggestions_{ts.session_number}"
        if suggestions_key not in st.session_state:
            ville = ts.profile.ville_travail or "votre ville"
            try:
                sg_system = (
                    "Tu es IAXEL. Génère 4 questions terrain qu'un agent immobilier "
                    "se poserait après ce cours. Questions concrètes, liées au quotidien en agence. "
                    "Inclus au moins 1 question liée au marché local. "
                    "Réponds UNIQUEMENT avec les 4 questions, une par ligne, sans numérotation."
                )
                sg_user = (
                    f"Thème du cours : {theme['titre']}\n"
                    f"Ville du stagiaire : {ville}\n"
                    f"Session n°{ts.session_number}"
                )
                raw = chat_complete(sg_system, sg_user, 0.5)
                suggestions_list = [q.strip().lstrip("-•").strip() for q in raw.strip().split("\n") if q.strip()]
                st.session_state[suggestions_key] = suggestions_list[:4] if suggestions_list else _suggested_questions(theme["titre"])
            except Exception:
                st.session_state[suggestions_key] = _suggested_questions(theme["titre"])
        suggestions = st.session_state[suggestions_key]
        placeholder = f"Ex : Comment aborder {theme['titre'].lower()} en rendez-vous ?"

    def _on_suggestion_click(suggestion: str) -> None:
        """Callback exécuté AVANT le render → modifie le widget sans conflit."""
        st.session_state.rag_question_input = suggestion

    question = st.text_input(
        "Votre question :",
        placeholder=placeholder,
        key="rag_question_input",
    )

    # Suggestions de questions fréquentes
    with st.expander("Questions fréquentes sur ce sujet", expanded=False):
        st.caption("Vous n'avez pas de question ? Voici des pistes :")
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
            with st.spinner("IAXEL cherche dans la base..."):
                ville = ts.profile.ville_travail or ""
                if is_after_marche:
                    # Enrichir la requête RAG avec le contexte marché + ville
                    enriched = f"[marché immobilier modules marché] {question.strip()}"
                    if ville:
                        enriched += f" (contexte : marché de {ville})"
                    resp = repondre_faq(enriched)
                else:
                    # Enrichir avec contexte local pour des réponses plus concrètes
                    if ville:
                        enriched_question = f"{question.strip()} (contexte : marché de {ville})"
                    else:
                        enriched_question = question.strip()
                    resp = repondre_faq(enriched_question)
            st.session_state.ts_faq_response = resp
            # Reset TTS flag pour rejouer si nouvelle question
            st.session_state.pop("_tts_faq_response", None)

    if st.session_state.ts_faq_response:
        st.markdown("#### Réponse d'IAXEL")
        with st.container(height=350):
            st.write(st.session_state.ts_faq_response)

        # TTS IAXEL lit la réponse automatiquement (une seule fois par réponse)
        tts_faq_key = "_tts_faq_response"
        if not st.session_state.get(tts_faq_key, False):
            try:
                from core.tts import tts_smart  # noqa: PLC0415
                audio = tts_smart(client, st.session_state.ts_faq_response, priority="high")
                if audio:
                    fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                    st.audio(audio, format=fmt, autoplay=False)
            except Exception:
                pass
            st.session_state[tts_faq_key] = True

    st.markdown("---")
    _sticky_continue_button("Continuer →", "btn_next_rag", ts, Step.QUESTIONS_RAG, {"done": True})


def _render_cours_cles(ts: TrainingSession):
    """Step COURS_CLES : cours oral conversationnel + point essentiel mis en valeur."""
    theme = ts.theme
    st.markdown(f"### Cours — {theme['titre']}")

    # Intro IAXEL (LLM, générée une seule fois)
    cours_intro_key = "cours_cles_intro"
    if not st.session_state.get(cours_intro_key):
        with st.spinner("IAXEL prépare l'introduction..."):
            intro_system = (
                "Tu es IAXEL, formateur terrain. En 2-3 phrases ORALES, "
                "présente le thème du cours et pourquoi c'est crucial sur le terrain. "
                "Utilise — pour les pauses et ... pour les hésitations. "
                "Termine par 'Allez — on y va.' Vouvoiement."
            )
            intro_user = f"Thème : {theme['titre']}\nCours clé : {theme['cours_cles']}"
            st.session_state[cours_intro_key] = chat_complete(intro_system, intro_user, 0.6)

    cours_intro = st.session_state[cours_intro_key]
    with st.chat_message("assistant", avatar=AVATAR_CHAT_EMOJI):
        st.markdown(cours_intro)

    tts_ci_key = "_tts_cours_intro"
    if not st.session_state.get(tts_ci_key, False):
        try:
            from core.tts import tts_smart  # noqa: PLC0415
            audio = tts_smart(client, cours_intro, priority="high")
            if audio:
                fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                st.audio(audio, format=fmt, autoplay=False)
        except Exception:
            pass
        st.session_state[tts_ci_key] = True

    if not st.session_state.ts_response:
        if st.button("Lancer le cours"):
            with st.spinner("IAXEL prépare le cours..."):
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

    # Séparer accroche/explication et cas pratique
    sections: dict[str, list[str]] = {"accroche": [], "cas_pratique": []}
    current_sec = "accroche"
    for line in body.strip().split("\n"):
        ls = line.strip()
        if not ls:
            sections[current_sec].append("")
            continue
        ls_lower = ls.lower()
        if current_sec == "accroche" and (
            "imaginez ce dialogue" in ls_lower
            or "cas pratique" in ls_lower
            or ls_lower.startswith("agent")
            or ls_lower.startswith("vous :")
        ):
            current_sec = "cas_pratique"
        sections[current_sec].append(ls)

    accroche_lines = sections["accroche"]
    cas_lines = sections["cas_pratique"]

    # Afficher accroche (visible directement, tronquée si trop longue)
    accroche_text = "\n".join(accroche_lines).strip()
    if len(accroche_text) > 600:
        visible = accroche_text[:500].rsplit(". ", 1)[0] + "."
        reste = accroche_text[len(visible):]
        st.write(visible)
        with st.expander("Lire la suite de l'explication", expanded=False):
            st.write(reste)
    else:
        st.write(accroche_text)

    # Cas pratique dans un expander
    cas = "\n".join(cas_lines)
    if cas:
        with st.expander("🎭 Cas pratique — Dialogue agent ↔ client", expanded=False):

            # 1. Parser les répliques
            repliques = []
            for line in cas.strip().split("\n"):
                ls = line.strip()
                if not ls:
                    continue
                is_agent = ls.lower().startswith(("agent", "vous"))
                is_client = ls.lower().startswith(("client", "vendeur", "acquéreur"))
                if is_agent:
                    text = ls.split(":", 1)[-1].strip().strip('"').strip("«»").strip()
                    if text:
                        repliques.append(("agent", text))
                elif is_client:
                    text = ls.split(":", 1)[-1].strip().strip('"').strip("«»").strip()
                    if text:
                        repliques.append(("client", text))

            # 2. Détecter le genre du client
            cas_lower = cas.lower()
            if any(w in cas_lower for w in ["mme ", "madame", "vendeuse", "acquéreuse", "elle "]):
                client_persona = "Mme Cliente"
            else:
                client_persona = "M. Client"

            # 3. Afficher les bulles
            for role, text in repliques:
                if role == "agent":
                    st.markdown(
                        f'<div style="background:#dcf8c6;padding:10px 14px;border-radius:12px;'
                        f'margin:6px 0 6px 25%;max-width:75%;text-align:right;">'
                        f'<small><strong>Vous (agent)</strong></small><br>{text}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div style="background:#f1f0f0;padding:10px 14px;border-radius:12px;'
                        f'margin:6px 25% 6px 0;max-width:75%;">'
                        f'<small><strong>{client_persona}</strong></small><br>{text}</div>',
                        unsafe_allow_html=True,
                    )

            # 4. Générer audio concaténé (une seule fois par session)
            tts_cas_key = "_tts_cas_pratique_concat"
            if tts_cas_key not in st.session_state:
                from core.tts import tts_to_bytes as oai_tts  # noqa: PLC0415
                from openai import OpenAI  # noqa: PLC0415
                import io, struct, wave  # noqa: PLC0415
                _client_oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                is_female = "mme" in client_persona.lower()

                wav_chunks = []
                with st.spinner("Préparation du dialogue audio..."):
                    for role, text in repliques:
                        if role == "agent":
                            audio = oai_tts(
                                _client_oai, text,
                                voice="echo",
                                instructions="Agent immobilier professionnel en rendez-vous vendeur.",
                                response_format="wav",
                            )
                        else:
                            audio = oai_tts(
                                _client_oai, text,
                                voice="nova" if is_female else "onyx",
                                instructions="Client particulier au téléphone. Naturel et spontané.",
                                response_format="wav",
                            )
                        if audio and audio[:4] == b'RIFF':
                            wav_chunks.append(audio)
                            # Silence 0.4s entre répliques
                            n = int(24000 * 0.4)
                            sil_buf = io.BytesIO()
                            with wave.open(sil_buf, "w") as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(24000)
                                wf.writeframes(struct.pack(f"<{n}h", *([0] * n)))
                            wav_chunks.append(sil_buf.getvalue())

                if wav_chunks:
                    try:
                        combined = io.BytesIO()
                        out_wav = wave.open(combined, "w")
                        first = True
                        for chunk in wav_chunks:
                            try:
                                r = wave.open(io.BytesIO(chunk), "r")
                                if first:
                                    out_wav.setparams(r.getparams())
                                    first = False
                                out_wav.writeframes(r.readframes(r.getnframes()))
                                r.close()
                            except Exception:
                                continue
                        out_wav.close()
                        st.session_state[tts_cas_key] = combined.getvalue()
                    except Exception:
                        st.session_state[tts_cas_key] = None
                else:
                    st.session_state[tts_cas_key] = None

            # 5. Lecteur unique — autoplay safe (dans expander, pas de rerun immédiat)
            concat_audio = st.session_state.get(tts_cas_key)
            if concat_audio:
                st.audio(concat_audio, format="audio/wav", autoplay=True)

    # Point essentiel toujours visible
    if point_essentiel:
        st.markdown("---")
        st.markdown("### 🎯 Point essentiel à retenir")
        st.markdown(f"## **{point_essentiel}**")

        tts_pe_key = "_tts_point_essentiel"
        if not st.session_state.get(tts_pe_key, False):
            try:
                from core.tts import tts_smart  # noqa: PLC0415
                audio = tts_smart(client, f"Ce qu'il faut retenir — {point_essentiel}", priority="high")
                if audio:
                    fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                    st.audio(audio, format=fmt, autoplay=False)
            except Exception:
                pass
            st.session_state[tts_pe_key] = True

    if st.button("🔊 Lire à voix haute", key="tts_cours_cles"):
        tts_text = body.strip()
        if point_essentiel:
            tts_text += f"\n\nPoint essentiel à retenir : {point_essentiel}"
        play_audio_from_text(tts_text)

    st.markdown("---")
    _sticky_continue_button("Continuer →", "btn_next_cours_cles", ts, Step.COURS_CLES, {"done": True})


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
    """Step WHATSAPP : simulation WhatsApp, thème lié au cours clé de la session."""
    from training.wa_scenario_generator import get_or_generate_wa_scenario  # noqa: PLC0415

    theme = ts.theme   # thème du cours clé de cette session

    # Générer scénario dynamique cohérent avec le cours clé (mis en cache par session)
    generated_scenario = get_or_generate_wa_scenario(
        theme_titre=theme["titre"],
        session_number=ts.session_number,
        chat_complete_fn=chat_complete,
    )

    # --- Écran sonnerie + décrocher ---
    if not st.session_state.get("wa_ringing"):
        ring_path = Path("assets/sounds/phone_ring.wav")
        if ring_path.exists():
            st.audio(str(ring_path), autoplay=True)

        st.markdown(
            '<div style="text-align:center;padding:40px 0;">'
            '<div style="font-size:72px">📲</div>'
            '<h2>Appel entrant...</h2>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"**Un client vous contacte au sujet de : {theme['titre']}**")

        # Brief contexte client (depuis scénario généré)
        persona = generated_scenario.get("persona", {})
        if persona.get("context"):
            st.info(
                f"**{persona.get('name', 'Client')}** — {persona.get('role', '')}\n\n"
                f"{persona['context']}\n\n"
                f"*Objectif : appliquer les techniques du cours clé sur {theme['titre']}*"
            )

        if st.button("📱 Décrocher", type="primary", use_container_width=True, key="btn_wa_decrocher"):
            st.session_state.wa_ringing = True
            st.rerun()
        return

    # --- Simulation WhatsApp ---
    st.markdown(f"### Mise en situation WhatsApp — {theme['titre']}")
    st.caption("Scénario basé sur le cours clé de cette session.")

    # TTS message d'ouverture : lu une seule fois au démarrage de la simulation
    if not st.session_state.get("_tts_wa_opening", False):
        opening_msg = generated_scenario.get("opening_message", "")
        if opening_msg:
            try:
                from core.tts import tts_client_smart
                from openai import OpenAI
                _oa = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                persona = generated_scenario.get("persona", {})
                persona_name = persona.get("name", "")
                audio = tts_client_smart(_oa, opening_msg, persona_name=persona_name)
                if audio:
                    fmt = "audio/mpeg" if audio[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                    st.audio(audio, format=fmt, autoplay=True)
            except Exception:
                pass
        st.session_state["_tts_wa_opening"] = True

    tone_override = adapt_whatsapp_tone(ts.profile)
    result = _render_wa_component(
        theme_title=theme["titre"],
        construire_contexte_fn=construire_contexte,
        chat_complete_fn=chat_complete,
        tone_override=tone_override,
        profile=ts.profile,
        session_number=ts.session_number,
        generated_scenario=generated_scenario,
    )

    if result is not None:
        evaluation, should_continue = result
        if evaluation is not None and should_continue:
            lacunes = evaluation.get("lacunes", [])
            wa_session_data = st.session_state.get("wa_session", {})
            messages_raw = wa_session_data.get("messages", [])
            persona_name = (
                wa_session_data.get("scenario", {})
                .get("persona", {})
                .get("name", "Client")
            )

            # Générer les commentaires par échange
            exchange_comments = []
            try:
                from training.whatsapp import (  # noqa: PLC0415
                    generate_exchange_comments,
                    Scenario,
                    WhatsAppMessage,
                )
                msgs = [WhatsAppMessage.from_dict(m) for m in messages_raw]
                scen = Scenario.from_dict(wa_session_data.get("scenario", {}))
                rag_ctx = construire_contexte(theme["titre"])
                with st.spinner("IAXEL prépare son débrief..."):
                    exchange_comments = generate_exchange_comments(
                        scen, msgs, rag_ctx, chat_complete
                    )
            except Exception:
                exchange_comments = []

            ts.record(Step.WHATSAPP, {
                "score": evaluation.get("total_score", 0),
                "criteria": evaluation.get("criteria", []),
                "debrief": evaluation.get("debrief", ""),
                "suggestions": evaluation.get("suggestions", ""),
                "lacunes": lacunes,
                "theme_titre": theme["titre"],
                "messages": messages_raw,
                "persona_name": persona_name,
                "exchange_comments": exchange_comments,
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
            st.info("Ces points seront couverts dans vos prochaines sessions !")

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

    st.write(f"Bravo {prenom} ! Vous avez terminé la session {ts.session_number}.")
    st.write(f"**Thème du jour** : {theme['titre']}")

    # Generate AI synthesis (cached in session state)
    if st.session_state.ts_synthesis is None:
        with st.spinner("IAXEL prépare votre synthèse personnalisée..."):
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

    # --- Axes d'amelioration (repliable) ---
    axes = synthesis.get("axes_amelioration", "")
    if axes:
        with st.expander("🔧 Axes d'amélioration", expanded=False):
            st.info(axes)

    # --- A faire demain (visible — c'est l'action clé) ---
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

    # --- Message formateur fin de session (repliable) ---
    score_quiz = quiz_data.get("score_pct", 0)
    wa_score = wa_data.get("score", 0) if wa_data and not wa_data.get("placeholder") else 0
    score_global = (score_quiz + wa_score) / 2 if wa_score else (score_quiz or 70)

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
        f"— IAXEL, votre formateur"
    )

    with st.expander("💬 Message d'IAXEL", expanded=False):
        st.info(message_fin)
        if st.button("Écouter", key="tts_message_fin"):
            play_audio_from_text(message_fin)

    st.markdown("---")
    st.success("Session terminée ! À demain pour continuer votre formation.")

    # --- Outils bonus (accessibles en fin de session uniquement) ---
    st.markdown("---")
    st.markdown("### 🎁 Outils bonus")
    st.caption("Approfondissez votre session avec ces outils supplémentaires.")

    col_memo, col_plan = st.columns(2)
    with col_memo:
        with st.expander("📘 Fiche mémo"):
            memo_theme_val = st.text_input(
                "Thème :",
                value=theme["titre"],
                key="bonus_memo_theme",
            )
            if st.button("Générer", key="btn_bonus_memo"):
                with st.spinner("IAXEL prépare votre fiche mémo..."):
                    fiche = generer_fiche_memo(memo_theme_val.strip())
                st.session_state["bonus_memo_fiche"] = fiche
            fiche_result = st.session_state.get("bonus_memo_fiche")
            if fiche_result:
                st.write(fiche_result)
                memo_pdf = generate_memo_pdf(memo_theme_val, fiche_result)
                st.download_button(
                    "Télécharger PDF",
                    data=bytes(memo_pdf),
                    file_name="fiche_memo.pdf",
                    mime="application/pdf",
                    key="btn_dl_bonus_memo",
                )

    with col_plan:
        with st.expander("🗂️ Plan d'entretien"):
            plan_theme_val = st.text_input(
                "Type d'entretien :",
                value=theme["titre"],
                key="bonus_plan_theme",
            )
            if st.button("Générer", key="btn_bonus_plan"):
                with st.spinner("IAXEL prépare votre plan..."):
                    plan = generer_plan_entretien(plan_theme_val.strip())
                st.session_state["bonus_plan_result"] = plan
            plan_result = st.session_state.get("bonus_plan_result")
            if plan_result:
                st.write(plan_result)

    # --- Terminer (passe 1 — vider les widgets avant de changer de page) ---
    st.markdown("---")
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
        _reset_all_step_states()
        # Flag passe 2 : complete() + ts = None sera appliqué au prochain render
        st.session_state._do_session_end = True
        st.rerun()


def _render_session_complete():
    """Écran affiché quand la session courante est terminée."""
    progress = load_progress()
    session_num = progress.get("current_session", 1)
    completed = len(progress.get("sessions_history", []))

    st.success(
        f"Vous avez complété {completed} session(s) sur {TOTAL_SESSIONS}. "
        f"Votre prochaine session sera la n°{session_num}."
    )
    st.write("Revenez demain pour continuer votre formation !")

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
        ts_dict = st.session_state.pop("ts", None)
        incremented = False
        if ts_dict is not None:
            try:
                ts_end = TrainingSession.from_dict(ts_dict)
                session_num_before = ts_end.session_number
                ts_end.complete()
                incremented = True
            except Exception:
                pass
        if not incremented:
            # Fallback garanti : incrémenter directement depuis le fichier
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
        st.rerun()
        return

    # Démarrer la session suivante (bouton "Commencer la session suivante")
    if st.session_state.pop("_do_next_session", False):
        # Nettoyer TOUT l'état de la session précédente pour éviter removeChild
        for key in ["ts", "transition_message", "chat_libre_history",
                    "bonus_memo_fiche", "bonus_plan_result"]:
            st.session_state.pop(key, None)
        _reset_all_step_states()
        st.rerun()
        return

    # ----------------------------------------------------------------

    # Dashboard progression (remplace l'affichage du parcours)
    if st.session_state.get("_show_dashboard", False):
        from training.dashboard import render_dashboard  # noqa: PLC0415
        render_dashboard()
        if st.button("← Retour au parcours", key="btn_back_from_dashboard", type="primary"):
            st.session_state._show_dashboard = False
            st.rerun()
        return

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
    step = ts.current_step
    if step == Step.PROFIL:
        _render_profil(ts)
    else:
        col_content, col_avatar = st.columns([3, 1])
        with col_avatar:
            avatar_name = ts.profile.avatar_name if ts.profile.prenom else "IAXEL"
            render_chat_libre(avatar_name)
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

                # TTS automatique (une seule fois par transition)
                tts_key = f"_tts_played_{ts.current_step.value}"
                if not st.session_state.get(tts_key, False):
                    from core.tts import tts_smart
                    audio_data = tts_smart(client, message, priority="high")
                    if audio_data:
                        fmt = "audio/mpeg" if audio_data[:3] in (b'\xff\xfb\x90', b'ID3') else "audio/wav"
                        st.audio(audio_data, format=fmt, autoplay=True)
                    st.session_state[tts_key] = True

                if st.button("C'est parti !", key="btn_start_step", type="primary"):
                    st.session_state.transition_message = None
                    st.session_state.pop(tts_key, None)
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
def _render_sidebar_training(ts) -> None:
    """Sidebar sombre pour le mode Parcours guidé : logo + profil + timeline + actions."""

    st.markdown("### IAxel-le Formation Immobilière")

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
        _reset_all_step_states()
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
                _reset_all_step_states()
                st.rerun()
    with col_next:
        if ts.session_number < TOTAL_SESSIONS:
            if st.button("▶", key="btn_next_session", help="Session suivante"):
                progress = load_progress()
                progress["current_session"] = ts.session_number + 1
                save_progress(progress)
                st.session_state.ts = None
                st.session_state.ts_force_restart = True
                _reset_all_step_states()
                st.rerun()


def render_header() -> None:
    """Header moderne : logo à gauche + menu profil déroulant à droite."""

    col_logo, col_profile = st.columns([3, 1])

    with col_logo:
        logo_iaxel = Path(LOGO_IAXEL)
        logo_fallback = Path(LOGO_AIMMO)
        logo_to_show = logo_iaxel if logo_iaxel.exists() else (logo_fallback if logo_fallback.exists() else None)
        _prog = load_progress()
        _snum = _prog.get("current_session", 1)
        _theme_list = _prog.get("sessions_history", [])
        _theme_title = _theme_list[-1].get("theme", "") if _theme_list else ""
        _caption = f"Session {_snum}/104" + (f" — {_theme_title}" if _theme_title else "")

        if logo_to_show:
            import base64  # noqa: PLC0415
            with open(str(logo_to_show), "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f"""
<div style="display:flex;align-items:center;gap:14px;padding:4px 0;">
  <img src="data:image/png;base64,{logo_b64}"
       style="width:110px;height:auto;object-fit:contain;flex-shrink:0;">
  <div>
    <div style="font-size:1.5rem;font-weight:700;line-height:1.2;
                color:#1a202c;">IAxel-le Formation Immobilière</div>
    <div style="font-size:0.8rem;color:#64748b;margin-top:2px;">{_caption}</div>
  </div>
</div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("# IAxel-le Formation Immobilière")
            st.caption(_caption)

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

                if st.button("📄 Mes documents", key="menu_memos"):
                    st.info("Fonctionnalité à venir")

                if st.button("📈 Ma progression", key="menu_progress"):
                    st.session_state._show_dashboard = True
                    st.rerun()

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
    _reset_all_step_states()
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

/* Masquer menu hamburger, header et footer Streamlit */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Layout compact */
div.block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; }
</style>""",
        unsafe_allow_html=True,
    )


def main():
    _inject_custom_css()
    render_header()
    ui_training()


if __name__ == "__main__":
    main()
