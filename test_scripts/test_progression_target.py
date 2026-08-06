"""
test_scripts/test_progression_target.py — Cible AppTest du parcours complet
Île 1 (sessions 1 → 5, coffres, planches BD, fin d'île).

Mini-app calquée sur app.py : même routage sur ecran_courant, mêmes écrans réels
(ecran_ile, ecran_session, modal planche BD, célébrations). C'est ce qui permet
de vérifier la progression telle que l'enfant la vit, et pas une simulation.

Deux écarts avec app.py, tous deux nécessaires pour un test hors-ligne :
  - base de données dédiée (jamais data/philia.db) ;
  - _init_engine() est remplacé par une version qui construit le SessionEngine
    sans l'ouvrir : le vrai appelle debut_session(), donc l'API Anthropic.
    Aucun appel réseau n'est fait par ce script.

Piloté par test_scripts/test_progression_sessions.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import data_layer.db as db

db._DB_PATH = ROOT / "data" / "_test_progression.db"  # jamais data/philia.db

import streamlit as st  # noqa: E402

import ui.ecran_session as ecran_session  # noqa: E402
from data_layer.joueurs import charger_joueur_courant, creer_joueur  # noqa: E402
from pedagogie.session_engine import SessionEngine  # noqa: E402
from ui.ecran_ile import render_ile  # noqa: E402

st.set_page_config(page_title="Test progression sessions", layout="wide")


def _init_engine_hors_ligne(
    exercices: list, situation_narrative: str, ile_id: str, planche_key: str
) -> SessionEngine:
    """Même contrat que ecran_session._init_engine, sans debut_session().

    Le moteur est rendu comme s'il venait de s'ouvrir : un message d'Archimède
    déjà affiché, l'exercice 1 en cours.
    """
    engine = SessionEngine(
        exercices=exercices,
        prenom="Léa",
        situation_narrative=situation_narrative,
        ile_id=ile_id,
        planche_key=planche_key,
    )
    engine.historique = [{"role": "assistant", "content": "Message déjà affiché."}]
    st.session_state.session_active = engine.to_dict()
    return engine


ecran_session._init_engine = _init_engine_hors_ligne

if charger_joueur_courant() is None:
    creer_joueur(genre="fille", avatar_prenom="sassou", role="eleve", prenom="Léa")

st.session_state.setdefault("ile_courante", "ile_1")
st.session_state.setdefault("ecran_courant", "ile")
st.session_state.setdefault("session_active", None)

ecran = st.session_state.ecran_courant

if ecran == "ile":
    render_ile()
elif ecran == "session":
    ecran_session.render_session()
elif ecran == "carte":
    # L'écran carte n'est pas la cible de ce test : on note seulement qu'on y a
    # été routé (le rendu réel de la carte est couvert ailleurs).
    st.markdown("ÉCRAN CARTE")
elif ecran == "enigme":
    # Idem : y entrer ouvrirait EnigmeEngine.debut_enigme(), donc l'API.
    st.markdown("ÉCRAN ÉNIGME")
else:
    st.error(f"Écran inconnu : {ecran}")
