"""
test_scripts/test_fin_ile_bypass.py — Bypass DB pour tester la célébration forte
de fin d'île (Brique 3, D-T8.6-F) sans passer par l'API Anthropic.

Ce projet n'a pas de table "progression" avec sessions_terminees : le
déclencheur réel de la célébration forte est le flag session_state
`celebration_fin_ile_a_afficher`, posé par ui/modal_planche_bd.py quand
chapitres_restants == 0. Ce script force directement ce flag et appelle
render_session() — c'est le point d'entrée exact que la Brique 3 a créé.

Isolé de data/philia.db via une base de test dédiée : jamais la base réelle
n'est touchée par ce script.

Lancer :
    streamlit run test_scripts/test_fin_ile_bypass.py \
        --server.headless true --server.port 8765
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import data_layer.db as db
db._DB_PATH = ROOT / "data" / "_test_fin_ile_bypass.db"  # jamais data/philia.db

import streamlit as st

from config.constants import ILE_NOMS
from data_layer.joueurs import charger_joueur_courant, creer_joueur
from ui.ecran_session import render_session

st.set_page_config(page_title="Test Brique 3 — Célébration fin d'île", layout="wide")

if charger_joueur_courant() is None:
    creer_joueur(genre="fille", avatar_prenom="sassou", role="eleve", prenom="Léa")

st.session_state.setdefault("ile_courante", "ile_1")
st.session_state.setdefault("session_active", None)
st.session_state.setdefault(
    "celebration_fin_ile_a_afficher", {"nom_ile": ILE_NOMS["ile_1"]}
)

render_session()
