"""
app_test_recompenses.py — Debug récompenses — Philia Summer Quest
Sprint 3 T7

Usage :
    streamlit run app_test_recompenses.py

Pré-requis : un joueur doit exister en base.
Si ce n'est pas le cas, lance d'abord :
    streamlit run app_test_avatar.py
"""

import streamlit as st

from config.constants import CRISTAUX_CATALOGUE, ILE_IDS, ILE_NOMS
from data_layer.joueurs import joueur_existe
import jeu.recompenses as recompenses
from ui.ecran_carte import render_carte

st.set_page_config(
    page_title="Debug Récompenses — Philia",
    page_icon="🗝",
    layout="wide",
)


# ── Vérification joueur ───────────────────────────────────────────────────────

if not joueur_existe():
    st.error(
        "Aucun joueur en base. "
        "Lance `streamlit run app_test_avatar.py` pour créer un joueur d'abord."
    )
    st.stop()


# ── Zone DEBUG ────────────────────────────────────────────────────────────────

st.markdown("## 🛠 Zone DEBUG — Récompenses")
st.caption("Cette zone est visible uniquement dans app_test_recompenses.py.")

# ── Clés (1 ligne, 7 boutons) ─────────────────────────────────────────────────
st.markdown("#### 🗝 Gagner des clés")
cols_cles = st.columns(7)
for i, ile_id in enumerate(ILE_IDS):
    with cols_cles[i]:
        label = f"Île {i + 1}"
        if st.button(f"🎁 Clé\n{label}", key=f"btn_cle_{ile_id}", use_container_width=True):
            recompenses.gagner_cle(ile_id)
            st.rerun()

# ── Cristaux Île 1 ────────────────────────────────────────────────────────────
st.markdown("#### 💎 Cristaux — Île 1 : L'Île des Nombres Brisés")
ile1 = CRISTAUX_CATALOGUE["ile_1"]["cristaux"]
cols_c1 = st.columns(5)
for i, (concept_id, infos) in enumerate(ile1.items()):
    with cols_c1[i]:
        if st.button(
            f"💎 {concept_id}\n{infos['nom'][:20]}",
            key=f"btn_c_ile1_{concept_id}",
            use_container_width=True,
        ):
            recompenses.gagner_cristal("ile_1", concept_id)
            st.rerun()

# ── Cristaux Île 2 ────────────────────────────────────────────────────────────
st.markdown("#### 💎 Cristaux — Île 2 : La Forêt des Mesures")
ile2 = CRISTAUX_CATALOGUE["ile_2"]["cristaux"]
cols_c2 = st.columns(5)
for i, (concept_id, infos) in enumerate(ile2.items()):
    with cols_c2[i]:
        if st.button(
            f"💎 {concept_id}\n{infos['nom'][:20]}",
            key=f"btn_c_ile2_{concept_id}",
            use_container_width=True,
        ):
            recompenses.gagner_cristal("ile_2", concept_id)
            st.rerun()

# ── Cristaux Île 3 ────────────────────────────────────────────────────────────
st.markdown("#### 💎 Cristaux — Île 3 : Le Labyrinthe des Inconnues")
ile3 = CRISTAUX_CATALOGUE["ile_3"]["cristaux"]
cols_c3 = st.columns(5)
for i, (concept_id, infos) in enumerate(ile3.items()):
    with cols_c3[i]:
        if st.button(
            f"💎 {concept_id}\n{infos['nom'][:20]}",
            key=f"btn_c_ile3_{concept_id}",
            use_container_width=True,
        ):
            recompenses.gagner_cristal("ile_3", concept_id)
            st.rerun()

# ── Resets ────────────────────────────────────────────────────────────────────
st.markdown("---")
col_r1, col_r2, _ = st.columns([2, 2, 6])

with col_r1:
    if st.button("🔄 Reset toutes les récompenses", use_container_width=True):
        recompenses.reset_recompenses()
        st.success("Récompenses effacées.")
        st.rerun()

with col_r2:
    if st.button("👤 Reset joueur complet", use_container_width=True):
        from data_layer.db import get_connection
        with get_connection() as conn:
            conn.execute("DELETE FROM joueurs")
            conn.commit()
        st.success("Joueur supprimé. Relance app_test_avatar.py.")
        st.rerun()

st.markdown("---")

# ── État actuel ───────────────────────────────────────────────────────────────
nb_cles = recompenses.nombre_cles_obtenues()
nb_cristaux = recompenses.nombre_cristaux_obtenus()
st.markdown(
    f"**État courant :** {nb_cles}/7 clés · {nb_cristaux}/35 cristaux"
)

st.markdown("---")

# ── Carte ─────────────────────────────────────────────────────────────────────
st.markdown("## 🗺 Carte de l'Archipel")
render_carte()
