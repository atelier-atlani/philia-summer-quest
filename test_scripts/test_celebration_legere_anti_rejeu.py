"""
test_scripts/test_celebration_legere_anti_rejeu.py — Cible AppTest pour vérifier
la garde anti-rejeu (D-T8.6-G) du st.toast de célébration légère.

Simule l'état juste après un événement de progression (celebration_legere_a_afficher
= True) avec un SessionEngine déjà initialisé en session_state — pour ne jamais
appeler SessionEngine.debut_session()/repondre() ici, qui parlent à l'API Anthropic.
Aucun appel API dans ce script : le moteur est injecté tout fait, jamais construit
via _init_engine().

Isolé de data/philia.db via une base de test dédiée.

Utilisé par un AppTest (streamlit.testing.v1) qui appelle .run() deux fois de
suite sur la même instance pour simuler un rerun Streamlit (ex. un message de
chat envoyé après la célébration) et vérifier que le toast ne se rejoue pas.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import data_layer.db as db
db._DB_PATH = ROOT / "data" / "_test_fin_ile_bypass.db"  # jamais data/philia.db

import streamlit as st

from data_layer.joueurs import charger_joueur_courant, creer_joueur
from pedagogie.contenu_ile1 import SESSION_1
from pedagogie.session_engine import SessionEngine
from ui.ecran_session import render_session

st.set_page_config(page_title="Test anti-rejeu toast", layout="wide")

if charger_joueur_courant() is None:
    creer_joueur(genre="fille", avatar_prenom="sassou", role="eleve", prenom="Léa")

st.session_state.setdefault("ile_courante", "ile_1")
st.session_state.setdefault("session_courante", 1)

# Moteur déjà en cours, injecté directement (pas de debut_session() -> pas d'API).
if "session_active" not in st.session_state:
    engine = SessionEngine(
        exercices=SESSION_1,
        prenom="Léa",
        situation_narrative="test",
        ile_id="ile_1",
        planche_key="c1",
    )
    engine.historique = [{"role": "assistant", "content": "Message déjà affiché."}]
    st.session_state.session_active = engine.to_dict()

# Flag posé une seule fois (simule l'action UI qui le déclenche) — pas reforcé
# à chaque run, exactement comme dans le vrai flux (setdefault, pas assignation).
st.session_state.setdefault("celebration_legere_a_afficher", True)

render_session()
