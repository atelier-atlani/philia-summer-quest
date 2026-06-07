"""
ui/ecran_carte.py — Écran Carte de l'Archipel — Philia Summer Quest.

Responsabilité : afficher la carte des 7 îles avec leurs états visuels,
le porte-clés en sidebar, et déclencher la navigation vers l'île sélectionnée.

Technique de positionnement : CSS absolu sur image de fond (validé Sprint 3).
Les positions viennent de data/iles.yaml (champ position_carte: {x, y}).
Aucune logique pédagogique ici. L'écran est une vitre.
"""
from __future__ import annotations

import base64
import os
import sqlite3

import streamlit as st
import yaml

from config.constants import ILE_IDS, ILE_NOMS


# ── Constantes ────────────────────────────────────────────────────────────────

_CARTE_IMAGE_PATH = "assets/ui/carte_archipel.png"


# ── CSS ───────────────────────────────────────────────────────────────────────

def _fond_css() -> str:
    """
    Retourne la déclaration CSS du fond de l'app.
    Si l'image graphiste existe → fond parchemin via l'app container.
    Sinon → gradient parchemin de substitution.
    """
    if os.path.exists(_CARTE_IMAGE_PATH):
        # La carte est rendue en inline via st.markdown — pas besoin de la
        # dupliquer en background de l'app. On met un fond neutre.
        return "background: #f4e4bc;"
    return "background: linear-gradient(135deg, #f4e4bc 0%, #e8d5a3 55%, #d4c08a 100%);"


def _inject_css() -> None:
    """Injecte le CSS global de l'écran carte."""
    fond = _fond_css()
    st.markdown(
        f"<style>[data-testid='stAppViewContainer'] {{ {fond} min-height:100vh; }}"
        "[data-testid='stHeader'] { background: transparent; }</style>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<style>
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #e8d5a3 0%, #c9a84c 100%);
}

/* ── Padding réduit pour que la carte prenne toute la largeur ── */
.main .block-container {
    padding-top: 0.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


# ── Image ─────────────────────────────────────────────────────────────────────

@st.cache_data
def _img_b64(path: str) -> str:
    """Charge l'image en base64 (mis en cache — chargée une seule fois)."""
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()


# ── Données ───────────────────────────────────────────────────────────────────

@st.cache_data
def _charger_iles_yaml() -> dict[str, dict]:
    """Charge data/iles.yaml et retourne un dict {ile_id: données}."""
    with open("data/iles.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {ile["id"]: ile for ile in data["iles"]}


def _get_etats_iles(enfant_id: int | None) -> dict[str, str]:
    """
    Retourne {ile_id: etat} pour chaque île.
    etat ∈ {"accessible", "conquise", "verrouillee"}

    Si enfant_id est None (mode dev / avant T6 onboarding) :
      → ile_1 accessible, reste verrouillé.
    Sinon, lit progression_iles depuis la DB.
    """
    if enfant_id is None:
        return {
            ile_id: ("accessible" if ile_id == "ile_1" else "verrouillee")
            for ile_id in ILE_IDS
        }

    conn = sqlite3.connect("data/philia.db")
    try:
        rows = conn.execute(
            "SELECT ile_id, niveau_elevation, rite_reussi "
            "FROM progression_iles WHERE enfant_id = ?",
            (enfant_id,),
        ).fetchall()
    finally:
        conn.close()

    progression = {
        r[0]: {"niveau": r[1], "rite_reussi": bool(r[2])} for r in rows
    }

    etats: dict[str, str] = {}
    for i, ile_id in enumerate(ILE_IDS):
        p = progression.get(ile_id)
        if p and p["rite_reussi"]:
            etats[ile_id] = "conquise"
        elif i == 0 or (
            i > 0 and progression.get(ILE_IDS[i - 1], {}).get("rite_reussi")
        ):
            etats[ile_id] = "accessible"
        else:
            etats[ile_id] = "verrouillee"
    return etats


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _render_sidebar_cles(enfant_id: int | None) -> None:
    """
    Affiche le porte-clés dans la sidebar.
    Stub Sprint 3 — sera câblé en T7.
    """
    with st.sidebar:
        st.markdown("### 🗝️ Porte-clés")
        # TODO T7: remplacer par jeu.cles.get_cles(enfant_id)
        st.markdown("*0 / 7 clés obtenues*")
        st.caption("Les clés s'obtiennent en maîtrisant chaque île.")
        st.divider()
        st.caption("Philia Summer Quest — MVP")


# ── Zones île (HTML) ──────────────────────────────────────────────────────────

def _zone_accessible(ile_id: str, nom: str, x: int, y: int) -> str:
    """
    Cercle doré semi-transparent, cliquable.
    Clic → navigation vers ?ile=<id> → rerun → session_state mis à jour.
    """
    base = (
        f"position:absolute;left:{x}%;top:{y}%;"
        "transform:translate(-50%,-50%);"
        "width:100px;height:100px;border-radius:50%;"
        "display:block;cursor:pointer;text-decoration:none;"
        "background-color:rgba(255,215,0,0.20);"
        "border:2px solid rgba(255,215,0,0.7);"
        "box-shadow:0 0 20px rgba(255,215,0,0.5);"
        "transition:box-shadow 0.2s ease, background-color 0.2s ease;"
        "z-index:10;"
    )
    hover_on = (
        "this.style.boxShadow='0 0 38px rgba(255,215,0,0.9)';"
        "this.style.backgroundColor='rgba(255,215,0,0.38)'"
    )
    hover_off = (
        "this.style.boxShadow='0 0 20px rgba(255,215,0,0.5)';"
        "this.style.backgroundColor='rgba(255,215,0,0.20)'"
    )
    return (
        f'<a href="?ile={ile_id}" title="{nom}" '
        f'style="{base}" '
        f'onmouseover="{hover_on}" '
        f'onmouseout="{hover_off}">'
        f'</a>'
    )


def _zone_conquise(ile_id: str, nom: str, x: int, y: int) -> str:
    """
    Cercle doré opaque avec étoile — île déjà maîtrisée.
    """
    base = (
        f"position:absolute;left:{x}%;top:{y}%;"
        "transform:translate(-50%,-50%);"
        "width:100px;height:100px;border-radius:50%;"
        "display:flex;align-items:center;justify-content:center;"
        "cursor:pointer;text-decoration:none;"
        "background-color:rgba(255,215,0,0.55);"
        "border:2px solid #FFD700;"
        "box-shadow:0 0 28px rgba(255,215,0,0.75);"
        "transition:box-shadow 0.2s ease;"
        "font-size:1.8rem;"
        "z-index:10;"
    )
    hover_on = "this.style.boxShadow='0 0 44px rgba(255,215,0,1)'"
    hover_off = "this.style.boxShadow='0 0 28px rgba(255,215,0,0.75)'"
    return (
        f'<a href="?ile={ile_id}" title="{nom} (conquise)" '
        f'style="{base}" '
        f'onmouseover="{hover_on}" '
        f'onmouseout="{hover_off}">'
        f'⭐'
        f'</a>'
    )


def _zone_verrouillee(x: int, y: int) -> str:
    """
    Cadenas discret — non cliquable. Ne doit pas polluer la carte.
    """
    return (
        f'<div style="'
        f'position:absolute;left:{x}%;top:{y}%;'
        f'transform:translate(-50%,-50%);'
        f'width:50px;height:50px;'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-size:1.4rem;opacity:0.5;'
        f'pointer-events:none;z-index:10;">'
        f'🔒</div>'
    )


# ── Rendu carte ───────────────────────────────────────────────────────────────

def _build_map_html(
    b64: str,
    etats: dict[str, str],
    iles_data: dict[str, dict],
) -> str:
    """
    Assemble le HTML complet : image de fond + zones îles positionnées en absolu.
    Les coordonnées viennent de iles_data[ile_id]["position_carte"].
    """
    zones: list[str] = []
    for ile_id, ile in iles_data.items():
        pos = ile.get("position_carte", {})
        x = pos.get("x", 50)
        y = pos.get("y", 50)
        nom = ILE_NOMS.get(ile_id, ile.get("nom", ile_id))
        etat = etats.get(ile_id, "verrouillee")

        if etat == "accessible":
            zones.append(_zone_accessible(ile_id, nom, x, y))
        elif etat == "conquise":
            zones.append(_zone_conquise(ile_id, nom, x, y))
        else:
            zones.append(_zone_verrouillee(x, y))

    zones_html = "\n".join(zones)
    # line-height:0 supprime le gap de 4px sous l'<img> (artefact baseline)
    return (
        '<div style="position:relative;width:100%;line-height:0;">'
        f'<img src="data:image/png;base64,{b64}" '
        "style=\"width:100%;display:block;\" alt=\"Carte de l'Archipel\">"
        f"{zones_html}"
        "</div>"
    )


# ── Point d'entrée ────────────────────────────────────────────────────────────

def render_carte() -> None:
    """Point d'entrée de l'écran carte — appelé par app.py."""
    enfant_id: int | None = st.session_state.get("enfant_id")

    # ── Traitement du clic île (query param → session_state → rerun) ──
    ile_cliquee = st.query_params.get("ile")
    if ile_cliquee:
        # Effacer le param pour éviter une boucle au prochain rerun
        st.query_params.clear()
        st.session_state.ile_courante = ile_cliquee
        st.session_state.ecran_courant = "ile"
        st.rerun()

    _inject_css()
    _render_sidebar_cles(enfant_id)

    etats = _get_etats_iles(enfant_id)
    iles_data = _charger_iles_yaml()

    if not os.path.exists(_CARTE_IMAGE_PATH):
        st.error(f"Carte non trouvée : `{_CARTE_IMAGE_PATH}`")
        st.stop()

    b64 = _img_b64(_CARTE_IMAGE_PATH)
    map_html = _build_map_html(b64, etats, iles_data)
    st.markdown(map_html, unsafe_allow_html=True)
