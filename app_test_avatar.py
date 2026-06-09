"""
app_test_avatar.py — App test standalone T6
Lancer : streamlit run app_test_avatar.py
"""

import streamlit as st
from ui.ecran_avatar import afficher_ecran_avatar

st.set_page_config(page_title="Test Écran Avatar", layout="wide")
afficher_ecran_avatar()
