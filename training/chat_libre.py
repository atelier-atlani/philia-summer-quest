"""training/chat_libre.py – Chat libre stagiaire sous avatar formateur.

Chat questions libres :
  - Grand avatar PNG à gauche
  - Historique scrollable (hauteur fixe)
  - Input ancré en bas (2 lignes max)
  - Réponse via RAG prioritaire + GPT-4o pour tout l'immobilier
  - Pas de GATE FAQ — bypass volontaire pour couvrir tout l'immobilier français
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.constants import AVATAR_DISPLAY_PNG, AVATAR_FALLBACK_PNG, CHAT_CONTAINER_HEIGHT

# Chemins avatar
_AVATAR_PNG = Path(AVATAR_DISPLAY_PNG)
_AVATAR_FALLBACK = Path(AVATAR_FALLBACK_PNG)

CHAT_LIBRE_SYSTEM = """Tu es IAXEL, formateur immobilier senior. Tu réponds aux questions \
du stagiaire dans un chat libre pendant sa session de formation.

HIÉRARCHIE DES SOURCES (par ordre de priorité) :

1. EXTRAITS RAG (formation interne — PRIORITÉ ABSOLUE)
   Si les extraits fournis répondent à la question, base-toi dessus exclusivement.

2. RÉFÉRENTIEL LÉGAL (fait foi en cas de contradiction avec toute autre source)
   - service-public.fr — fiches pratiques juridiquement exactes
   - legifrance.gouv.fr — textes de loi bruts (ALUR, ELAN, Code Construction)
   - anil.org — droits locataires/propriétaires, aides locales
   - anah.fr — MaPrimeRénov', aides rénovation, plafonds ressources
   - notaires.fr — frais acquisition, successions, compromis

3. DATA MARCHÉ (chiffres officiels)
   - dvf.etalab.gouv.fr — prix de vente réels (actes notariés)
   - immobilier.notaires.fr — statistiques prix officielles
   - banque-france.fr — taux d'usure, statistiques crédit immobilier
   - insee.fr — construction neuve, parc logements
   - meilleursagents.com — ITI (Indice Tension Immobilière), prévisions marché
   - etudes-lpi.com — prix signés (compromis)

4. TECHNIQUE DU BÂTI
   - ecologie.gouv.fr — DPE, rénovation énergétique, loi Climat
   - cohesion-territoires.gouv.fr — encadrement loyers, permis louer

5. STRATÉGIE & BUSINESS (contexte professionnel)
   - journaldelagence.com — outils, marketing, management agence
   - businessimmo.com — immobilier tertiaire, grands acteurs
   - immoweek.fr — actualités quotidiennes secteur
   - leparticulier.lefigaro.fr — réformes fiscales, gestion locative
   - boursorama.com/patrimoine — financement, SCPI, fiscalité
   - pap.fr — vente particuliers, permis louer, plafonnement loyers

RÈGLE DE PRIORITÉ :
Si une information business (source 5) contredit une source légale (source 2), \
IGNORE la source business. La loi prime TOUJOURS.
Entre deux sources, privilégie la plus RÉCENTE.

RÈGLES DE RÉPONSE :
- Vouvoiement systématique
- Si le RAG couvre la question → réponse basée sur les extraits
- Si le RAG ne couvre pas → utilise tes connaissances + cite la source officielle avec URL
- Si la question N'EST PAS liée à l'immobilier → refuse poliment :
  "Je suis IAXEL, votre formateur immobilier. Cette question sort de mon domaine — \
mais si vous avez une question sur le marché, la réglementation, les techniques de vente \
ou la gestion de clientèle... je suis là !"
- Style : oral, terrain, concret. Pas académique.
- Phrases courtes. Exemples chiffrés quand possible.
- Quand tu cites une source, donne le nom du site + l'URL racine.
- Pas de marque/réseau/outil propriétaire d'agence.

PÉRIMÈTRE IMMOBILIER AUTORISÉ :
- Transaction (vente/achat résidentiel et professionnel)
- Location (baux, encadrement, régulations)
- Financement (crédit, taux, assurance emprunteur, PTZ)
- Fiscalité immobilière (plus-values, LMNP, Pinel, IFI)
- Rénovation énergétique (DPE, MaPrimeRénov', audit)
- Urbanisme (PLU, permis construire, ZAN)
- Copropriété (charges, AG, travaux)
- Techniques de vente et prospection immobilière
- Droit immobilier (servitudes, mitoyenneté, bornage)
- Gestion locative et investissement
- Marché immobilier (tendances, prix, volumes)
"""


def _get_avatar_path() -> str | None:
    if _AVATAR_PNG.exists():
        return str(_AVATAR_PNG)
    if _AVATAR_FALLBACK.exists():
        return str(_AVATAR_FALLBACK)
    return None


def _init_chat_libre_state() -> None:
    if "chat_libre_history" not in st.session_state:
        st.session_state.chat_libre_history = []


def _chat_libre_response(question: str, chat_history: list | None = None) -> str:
    """Réponse chat libre — RAG prioritaire, connaissances GPT-4o en complément.

    Bypass volontaire du GATE FAQ : le chat libre couvre tout l'immobilier français,
    pas seulement les thèmes indexés dans la base RAG.
    """
    from agent_formateur import construire_contexte, chat_complete  # noqa: PLC0415
    from core.sanitizer import sanitize_brand, brand_block  # noqa: PLC0415

    question = sanitize_brand(question)
    contexte = construire_contexte(question, k=5)

    # Historique des 3 derniers échanges pour la continuité conversationnelle
    history_block = ""
    if chat_history:
        for msg in chat_history[-6:]:
            role_label = "Stagiaire" if msg["role"] == "user" else "IAXEL"
            history_block += f"{role_label} : {msg['content']}\n"

    user_prompt = ""
    if history_block:
        user_prompt += f"Historique récent :\n{history_block}\n\n"

    user_prompt += f"Question du stagiaire :\n{question}\n\n"

    if contexte.strip():
        user_prompt += f"Extraits de formation (RAG) :\n{contexte}\n\n"
        user_prompt += (
            "Si les extraits répondent à la question, base-toi dessus en priorité. "
            "Sinon, utilise tes connaissances immobilier et cite la source de référence."
        )
    else:
        user_prompt += (
            "Aucun extrait RAG pertinent. Réponds avec tes connaissances immobilier. "
            "Cite la source de référence (site officiel) si applicable."
        )

    response = chat_complete(CHAT_LIBRE_SYSTEM, user_prompt, 0.5)
    return brand_block(response)


def render_chat_libre(avatar_name: str = "IAXEL") -> None:
    """Affiche le chat libre sous grand avatar.

    Args:
        avatar_name: Nom du formateur à afficher.
    """
    _init_chat_libre_state()
    history: list[dict] = st.session_state.chat_libre_history

    # --- Grand avatar ---
    avatar_path = _get_avatar_path()
    if avatar_path:
        st.image(avatar_path, width=300)
    else:
        st.markdown(
            '<div style="font-size:80px;text-align:center;">🎓</div>',
            unsafe_allow_html=True,
        )
    st.markdown(f"**{avatar_name}**")
    st.caption("🟢 En direct · Questions libres")

    st.markdown("---")
    st.markdown("### 💬 Questions libres")

    # Limiter la hauteur de la zone de saisie à 2 lignes visibles
    st.markdown(
        """<style>
        [data-testid="stChatInput"] textarea {
            max-height: 68px !important;
            overflow-y: auto !important;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    # --- Historique scrollable (hauteur fixe) ---
    chat_container = st.container(height=CHAT_CONTAINER_HEIGHT)
    with chat_container:
        for msg in history:
            role = msg["role"]
            avatar = avatar_path if role == "assistant" else None
            with st.chat_message(role, avatar=avatar):
                st.markdown(msg["content"])

    # --- Input ---
    user_q = st.chat_input("Votre question...", key="chat_libre_input")
    if user_q and user_q.strip():
        history.append({"role": "user", "content": user_q.strip()})
        with st.spinner(""):
            resp = _chat_libre_response(user_q.strip(), chat_history=history[:-1])
        history.append({"role": "assistant", "content": resp})
        st.session_state.chat_libre_history = history
        st.rerun()
