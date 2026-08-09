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
from urllib.parse import urlencode

import streamlit as st
import yaml

from config.constants import ILE_IDS, ILE_NOMS
from core.partie import parametres_url_partie
from data_layer.joueurs import joueur_existe
import jeu.recompenses as recompenses
from ui.ecran_acces import parametres_url_acces
from ui.tableau_bord import render_tableau_bord


# ── Constantes ────────────────────────────────────────────────────────────────

_CARTE_IMAGE_PATH = "assets/ui/carte_archipel.png"
_ARCHIPEL_ISO_PATH = "assets/narratif/globaux/archipel_isometrique.png"
_CLE_IMAGE_PATH = "assets/ui/cle_partage.png"

_PARAM_ILE = "ile"


# ── Navigation par lien ───────────────────────────────────────────────────────

def _href_ile(ile_id: str) -> str:
    """URL du clic sur une île.

    Un href de la forme "?ile=X" écrase toute la query string. Tout ce qui doit
    survivre au rechargement complet est donc réinjecté ici : le marqueur de
    déverrouillage, sans quoi le portail se redemande, et l'identifiant de
    partie, sans quoi l'enfant repart sur une partie vierge — ou pire, sur
    celle d'une autre famille.
    """
    a_preserver = {**parametres_url_acces(), **parametres_url_partie()}
    return "?" + urlencode({**a_preserver, _PARAM_ILE: ile_id})


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
    # Le fond de sidebar est désormais injecté par ui/tableau_bord.py : la même
    # sidebar s'affiche sur tous les écrans, son style doit la suivre.
    st.markdown(
        """
<style>
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

    T7 — cascade basée sur les clés obtenues (joueurs.cles_obtenues).
    Règle : île N accessible si a_obtenu_cle("ile_(N-1)") est vrai.
    Si aucun joueur → île_1 accessible, reste verrouillé.
    """
    try:
        cles = recompenses.cles_obtenues()
    except RuntimeError:
        cles = {}

    etats: dict[str, str] = {}
    for i, ile_id in enumerate(ILE_IDS):
        if ile_id in cles:
            etats[ile_id] = "conquise"
        elif i == 0 or ILE_IDS[i - 1] in cles:
            etats[ile_id] = "accessible"
        else:
            etats[ile_id] = "verrouillee"
    return etats


# ── Sidebar ───────────────────────────────────────────────────────────────────
#
# _render_sidebar_recompenses() vivait ici et n'était donc rendue que sur la
# carte. Elle est devenue ui/tableau_bord.py — même sidebar, appelée par tous
# les écrans de jeu. Rien n'est dupliqué : render_carte() l'importe et l'appelle
# exactement là où l'ancienne fonction était appelée.


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
        "transition:box-shadow 0.2s ease, background-color 0.2s ease, transform 0.2s ease;"
        "z-index:10;"
    )
    hover_on = (
        "this.style.boxShadow='0 0 60px rgba(255,215,0,1)';"
        "this.style.backgroundColor='rgba(255,215,0,0.55)';"
        "this.style.transform='translate(-50%,-50%) scale(1.1)'"
    )
    hover_off = (
        "this.style.boxShadow='0 0 20px rgba(255,215,0,0.5)';"
        "this.style.backgroundColor='rgba(255,215,0,0.20)';"
        "this.style.transform='translate(-50%,-50%) scale(1)'"
    )
    return (
        f'<a href="{_href_ile(ile_id)}" title="{nom}" '
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
        f'<a href="{_href_ile(ile_id)}" title="{nom} (conquise)" '
        f'style="{base}" '
        f'onmouseover="{hover_on}" '
        f'onmouseout="{hover_off}">'
        f'⭐'
        f'</a>'
    )


def _zone_verrouillee(x: int, y: int) -> str:
    """
    Cas A — Île verrouillée : cadenas discret, non cliquable.
    """
    return (
        f'<div style="'
        f'position:absolute;left:{x}%;top:{y}%;'
        f'transform:translate(-50%,-50%);'
        f'width:50px;height:50px;'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-size:1.8rem;opacity:0.75;'
        f'background-color:rgba(255,255,255,0.4);border-radius:50%;padding:4px;'
        f'pointer-events:none;z-index:10;">'
        f'🔒</div>'
    )


def _zone_cle_doree(x: int, y: int) -> str:
    """
    Cas B — Île conquise : clé dorée avec léger halo, non cliquable.
    Remplace le cadenas quand recompenses.a_obtenu_cle(ile_id) == True.
    """
    return (
        f'<img src="data:image/png;base64,{_img_b64(_CLE_IMAGE_PATH)}" '
        f'alt="Clé du Partage" style="'
        f'position:absolute;left:{x}%;top:{y}%;'
        f'transform:translate(-50%,-50%);'
        f'width:68px;height:auto;'
        # Halo doré : text-shadow ne s'applique pas à une image — le
        # rayonnement passe par un drop-shadow supplémentaire, qui épouse
        # la silhouette détourée du PNG transparent.
        f'filter:drop-shadow(0 0 14px rgba(201,169,97,0.9)) '
        f'drop-shadow(0 2px 4px rgba(0,0,0,0.3));'
        f'pointer-events:none;z-index:11;">'
    )


# ── Rendu carte ───────────────────────────────────────────────────────────────

def _build_map_html(
    b64: str,
    etats: dict[str, str],
    iles_data: dict[str, dict],
    cles: dict,
) -> str:
    """
    Assemble le HTML complet : image de fond + zones îles positionnées en absolu.
    Les coordonnées viennent de iles_data[ile_id]["position_carte"].

    Logique de rendu pour les îles verrouillées / conquises :
      - Cas B : île conquise (clé obtenue)    → clé dorée (_zone_cle_doree)
      - Cas C : île accessible (pas de clé)   → halo doré (_zone_accessible)
      - Cas A : île verrouillée               → cadenas (_zone_verrouillee)
    Note : _zone_conquise (étoile) est conservée mais non atteinte en T7 ;
    elle sera activée quand le rite de passage sera implémenté (Sprint 4).
    """
    zones: list[str] = []
    for ile_id, ile in iles_data.items():
        pos = ile.get("position_carte", {})
        x = pos.get("x", 50)
        y = pos.get("y", 50)
        nom = ILE_NOMS.get(ile_id, ile.get("nom", ile_id))
        etat = etats.get(ile_id, "verrouillee")

        # Cas B : clé obtenue → clé dorée, indépendamment de l'état "conquise"
        if ile_id in cles:
            zones.append(_zone_cle_doree(x, y))
        elif etat == "accessible":
            zones.append(_zone_accessible(ile_id, nom, x, y))
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
    ile_cliquee = st.query_params.get(_PARAM_ILE)
    if ile_cliquee:
        # Effacer le param pour éviter une boucle au prochain rerun — celui-là
        # seulement : un clear() emporterait le marqueur d'accès et le portail
        # se redemanderait au prochain rechargement de page.
        del st.query_params[_PARAM_ILE]
        if st.session_state.get("ile_courante") != ile_cliquee:
            # Changement d'île (ou première entrée) : la progression de l'île
            # visée se dérive de ses coffres (D-T8.6-E), jamais un 1 en dur —
            # sinon revenir sur une île déjà entamée rejouerait sa session 1.
            # Île déjà terminée (None) : la valeur n'est pas jouée, ecran_ile
            # route vers la fin d'île.
            st.session_state.session_courante = recompenses.session_courante(ile_cliquee) or 1
            st.session_state.session_active = None
        st.session_state.ile_courante = ile_cliquee
        st.session_state.ecran_courant = "ile"
        st.rerun()

    _inject_css()
    render_tableau_bord()

    etats = _get_etats_iles(enfant_id)
    iles_data = _charger_iles_yaml()

    # Récupère les clés pour afficher la clé dorée sur la carte (Cas B)
    try:
        cles = recompenses.cles_obtenues()
    except RuntimeError:
        cles = {}

    if not os.path.exists(_CARTE_IMAGE_PATH):
        st.error(f"Carte non trouvée : `{_CARTE_IMAGE_PATH}`")
        st.stop()

    b64 = _img_b64(_CARTE_IMAGE_PATH)
    map_html = _build_map_html(b64, etats, iles_data, cles)
    st.markdown(map_html, unsafe_allow_html=True)
