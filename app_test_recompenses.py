"""
app_test_recompenses.py — Debug récompenses — Philia Summer Quest
Sprint 3 T7

Usage :
    streamlit run app_test_recompenses.py

OUTIL DE DÉBOGAGE — IL NE DOIT JAMAIS TOUCHER UNE PARTIE RÉELLE.
Il donne des clés, des cristaux, remet des compteurs à zéro et supprime un
joueur : sur la base de production, ce serait la progression d'une famille
qui disparaîtrait. Trois verrous, du plus fort au plus faible :

  1. la base est IMPOSÉE ici (data/_debug_recompenses.db), après le calcul de
     DB_PATH : ni la variable d'environnement ni le disque Render ne peuvent
     la détourner ;
  2. une garde refuse de démarrer si la base résolue n'est pas celle-là —
     fail-closed : elle ne cherche pas à reconnaître une base « de prod », elle
     exige de reconnaître LA base de débogage ;
  3. la partie est imposée elle aussi, et la suppression du joueur ne porte que
     sur elle (plus de DELETE sans filtre, qui effacerait toutes les familles).

Le joueur de débogage est créé automatiquement : plus besoin d'app_test_avatar.
"""

from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Debug Récompenses — Philia",
    page_icon="🗝",
    layout="wide",
)

# ── Verrous : base et partie dédiées ──────────────────────────────────────────
# Posés AVANT la première connexion (les imports ci-dessus n'en ouvrent aucune).

import data_layer.db as db  # noqa: E402

_BASE_DEBUG = Path(__file__).parent / "data" / "_debug_recompenses.db"
_PARTIE_DEBUG = "debugrecompenses1"

db._DB_PATH = _BASE_DEBUG

if db.get_db_path() != _BASE_DEBUG:
    st.error(
        "Garde de sécurité : cet outil de débogage n'accepte que sa base "
        f"dédiée ({_BASE_DEBUG.name}). Base résolue : {db.get_db_path()}"
    )
    st.stop()

from config.constants import CRISTAUX_CATALOGUE, ILE_IDS, ILE_NOMS  # noqa: E402
from data_layer.joueurs import creer_joueur_pour, joueur_existe_pour  # noqa: E402
import jeu.recompenses as recompenses  # noqa: E402
from ui.ecran_carte import render_carte  # noqa: E402

# Toute la page travaille sur la partie de débogage, jamais sur celle d'un
# visiteur : c'est ce qui rend inoffensifs les boutons « gagner » et « reset ».
st.session_state["partie_id"] = _PARTIE_DEBUG

if not joueur_existe_pour(_PARTIE_DEBUG):
    creer_joueur_pour(
        _PARTIE_DEBUG,
        genre="fille",
        avatar_prenom="melian",
        role="architecte",
        prenom="Debug",
    )

st.caption(f"🔒 Base de débogage : `{_BASE_DEBUG.name}` · partie `{_PARTIE_DEBUG}`")


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
            # Filtré sur la partie de débogage : un DELETE nu effacerait toutes
            # les parties, donc toutes les familles.
            conn.execute("DELETE FROM joueurs WHERE partie_id = ?", (_PARTIE_DEBUG,))
            conn.commit()
        st.success("Joueur de débogage supprimé. Il sera recréé au prochain chargement.")
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
