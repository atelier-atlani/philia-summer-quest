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
# PARCOURS GUIDÉ (contenu)
# -----------------------------
def init_parcours_state():
    if "parcours_prenom" not in st.session_state:
        st.session_state.parcours_prenom = ""
    if "parcours_niveau" not in st.session_state:
        st.session_state.parcours_niveau = ""
    if "parcours_step" not in st.session_state:
        st.session_state.parcours_step = 0
    if "parcours_module_index" not in st.session_state:
        st.session_state.parcours_module_index = 0
    if "parcours_reponse_courante" not in st.session_state:
        st.session_state.parcours_reponse_courante = ""


def get_parcours_modules():
    return [
        {
            "titre": "Découverte vendeur",
            "instruction": "Explique-moi de manière pédagogique la découverte vendeur avec un cas pratique concret d'entretien.",
        },
        {
            "titre": "Présentation de l’ACM au vendeur",
            "instruction": "Explique-moi comment présenter l’ACM à un vendeur, avec un cas pratique de situation où le vendeur hésite sur le prix.",
        },
        {
            "titre": "Gestion des objections sur le prix",
            "instruction": "Explique-moi comment traiter les objections sur le prix, avec un cas pratique de vendeur qui pense que son bien vaut plus cher.",
        },
        {
            "titre": "Suivi vendeur",
            "instruction": "Explique-moi la démarche de suivi vendeur, avec un cas pratique de vendeur qui tarde à prendre une décision.",
        },
    ]


def ui_parcours_guide_contenu():
    init_parcours_state()
    modules = get_parcours_modules()

    st.subheader("🎓 Parcours de formation guidé – contenu structuré")

    # Étape 0 : infos stagiaire
    if st.session_state.parcours_step == 0:
        st.write("Le formateur IA va te proposer un parcours structuré en plusieurs modules.")
        st.write("Commençons par faire connaissance 👇")

        prenom = st.text_input("Ton prénom :", value=st.session_state.parcours_prenom)
        niveau = st.radio(
            "Ton niveau en agence immobilière :",
            options=["Débutant (moins d'un an)", "Confirmé (plus d'un an)"],
            index=0 if st.session_state.parcours_niveau in ["", "Débutant (moins d'un an)"] else 1,
        )

        if st.button("Démarrer le parcours"):
            st.session_state.parcours_prenom = prenom or "le stagiaire"
            st.session_state.parcours_niveau = niveau
            st.session_state.parcours_step = 1
            st.session_state.parcours_module_index = 0
            st.session_state.parcours_reponse_courante = ""
            st.rerun()
        return

    # Infos stagiaire
    st.info(
        f"Stagiaire : **{st.session_state.parcours_prenom}** — Niveau : **{st.session_state.parcours_niveau}**"
    )

    # Fin de parcours
    if st.session_state.parcours_module_index >= len(modules):
        st.success(
            "🎉 Tu es arrivé au bout du parcours. "
            "Tu peux maintenant utiliser les autres modes (FAQ, fiches mémo, plans d’entretien)."
        )
        if st.button("Recommencer le parcours"):
            st.session_state.parcours_step = 0
            st.session_state.parcours_module_index = 0
            st.session_state.parcours_reponse_courante = ""
            st.rerun()
        return

    module = modules[st.session_state.parcours_module_index]

    st.markdown("---")
    st.markdown(f"### 🎓 Module {st.session_state.parcours_module_index + 1} — {module['titre']}")

    # Lancer le module
    if st.button("▶️ Lancer ce module", key=f"launch_module_{st.session_state.parcours_module_index}"):
        with st.spinner("Le formateur prépare le contenu..."):
            reponse = repondre_comme_formateur(module["instruction"])
        st.session_state.parcours_reponse_courante = reponse

    # Affichage de la réponse
    if st.session_state.parcours_reponse_courante:
        st.markdown("#### 💬 Explication du formateur IA (avec cas pratique)")
        st.write(st.session_state.parcours_reponse_courante)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔊 Lire cette explication à voix haute", key=f"audio_module_{st.session_state.parcours_module_index}"):
                play_audio_from_text(st.session_state.parcours_reponse_courante)

        st.markdown("#### ⚡ Questions rapides en lien avec ce module")
        question_faq = st.text_input(
            "Pose une question rapide si tu veux approfondir ce module :",
            key=f"faq_module_input_{st.session_state.parcours_module_index}",
        )

        if st.button("Obtenir une réponse rapide", key=f"btn_faq_module_{st.session_state.parcours_module_index}"):
            if not question_faq.strip():
                st.warning("Merci de saisir une question.")
            else:
                with st.spinner("Réponse rapide du formateur..."):
                    reponse_faq = repondre_faq(question_faq.strip())

                st.markdown("##### 💬 Réponse FAQ")
                st.write(reponse_faq)

                if st.checkbox("🔊 Lire la réponse FAQ à voix haute", key=f"audio_faq_check_{st.session_state.parcours_module_index}"):
                    play_audio_from_text(reponse_faq)

        st.markdown("---")
        if st.button("➡️ Passer au module suivant", key=f"next_module_{st.session_state.parcours_module_index}"):
            st.session_state.parcours_module_index += 1
            st.session_state.parcours_reponse_courante = ""
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

    # 1) Parcours guidé
    if mode == "Parcours guidé (contenu structuré)":
        ui_parcours_guide_contenu()
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
