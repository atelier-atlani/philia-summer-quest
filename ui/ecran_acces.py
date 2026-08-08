"""
ui/ecran_acces.py — Portail d'accès par code, au tout début du parcours.

Le jeu est déployé publiquement (Render) : sans code valide, aucun écran ne
doit se charger. `portail_acces()` est appelé dans app.py avant le routing ;
tant que l'accès n'est pas déverrouillé, il affiche l'écran de saisie puis
st.stop() — rien d'autre ne s'exécute.

Le déverrouillage vit en session_state ("acces_deverrouille") : il n'est
demandé qu'une fois par session. Fermer l'onglet redemande le code (accepté au
MVP ; une persistance côté joueur serait un plus futur).

D'OÙ VIENNENT LES CODES (aucun code n'est écrit dans le repo)
    1. st.secrets["codes_acces"] — liste TOML ou chaîne séparée par virgules.
    2. sinon la variable d'environnement CODES_ACCES (même format chaîne),
       chargée depuis .env en local via load_dotenv() (app.py).
    3. sinon : aucun code configuré → voir ci-dessous, ça dépend de l'environnement.

Ce triple étage est le seul montage qui marche des deux côtés sans code en dur :
en local, .streamlit/secrets.toml n'existe pas (st.secrets lève alors une
exception, d'où le try/except) et .env suffit ; sur Render, les deux marchent —
un Secret File .streamlit/secrets.toml, ou plus simplement une variable
d'environnement CODES_ACCES dans les réglages du service.

AUCUN CODE CONFIGURÉ : FAIL-CLOSED EN PRODUCTION
Render expose RENDER=true dans l'environnement du service ; c'est ce qui
distingue les deux cas.
    - en production (RENDER défini) → portail FERMÉ, message neutre, st.stop().
      Un oubli de configuration ne doit jamais ouvrir le jeu à tous ; il ferme
      la porte et laisse une trace dans les logs Render.
    - en local (pas de RENDER) → portail ouvert, le dev n'a rien à configurer.

Point d'entrée public : portail_acces()
"""

from __future__ import annotations

import logging
import os

import streamlit as st

_LOG = logging.getLogger(__name__)

_CLE_SECRET = "codes_acces"
_VAR_ENV = "CODES_ACCES"
_VAR_ENV_PROD = "RENDER"  # Render la pose à "true" dans l'environnement du service


def _en_production() -> bool:
    """Vrai sur Render. Une valeur explicitement négative est respectée, pour
    qu'un dev puisse simuler le local avec RENDER=false.
    """
    return os.getenv(_VAR_ENV_PROD, "").strip().casefold() not in ("", "false", "0")


# ── Lecture des codes ─────────────────────────────────────────────────────────

def _depuis_secrets() -> str | list | None:
    """Lit st.secrets[_CLE_SECRET]. None si absent — ou si st.secrets n'existe
    pas du tout : sans fichier secrets.toml, le simple accès lève.
    """
    try:
        return st.secrets[_CLE_SECRET]
    except Exception:
        return None


def _normaliser(code: str) -> str:
    """Insensible à la casse et aux espaces : « Philia-4K7M » ≡ « philia-4k7m »."""
    return code.strip().casefold()


def _codes_valides() -> list[str]:
    """Codes autorisés, normalisés. Liste vide = aucun code configuré."""
    brut = _depuis_secrets()
    if brut is None:
        brut = os.getenv(_VAR_ENV)
    if brut is None:
        return []

    # Les secrets TOML peuvent porter une vraie liste ; l'env, seulement une chaîne.
    morceaux = brut if isinstance(brut, (list, tuple)) else str(brut).split(",")
    return [n for n in (_normaliser(str(m)) for m in morceaux) if n]


def code_est_valide(saisie: str) -> bool:
    return _normaliser(saisie) in _codes_valides()


# ── Écran ─────────────────────────────────────────────────────────────────────

def _afficher_ecran() -> None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align:center;font-size:3rem;">🏝️</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h1 style="text-align:center;">Philia Summer Quest</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align:center;font-size:1.05rem;line-height:1.8;">'
            "L'archipel t'attend, jeune élévateur.<br>"
            "Entre ton code d'accès pour commencer l'aventure."
            "</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # Un form pour que la touche Entrée valide aussi bien que le bouton.
        with st.form("form_acces", clear_on_submit=False):
            saisie = st.text_input(
                "Ton code d'accès",
                key="code_acces_saisi",
                placeholder="Écris ton code ici…",
                label_visibility="collapsed",
            )
            valide = st.form_submit_button("⚓ Entrer", type="primary", width="stretch")

        if valide:
            if code_est_valide(saisie):
                st.session_state["acces_deverrouille"] = True
                st.rerun()
            elif saisie.strip():
                st.error("Ce code ne correspond à aucune clé de l'archipel. Vérifie-le et réessaie.")
            else:
                st.warning("Entre d'abord ton code d'accès.")


def _afficher_ecran_indisponible() -> None:
    """Écran de repli quand la production n'a aucun code configuré. Rien de
    technique n'y transparaît : côté enfant, c'est une panne, pas une faille.
    """
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align:center;font-size:3rem;">🏝️</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h1 style="text-align:center;">Philia Summer Quest</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align:center;font-size:1.05rem;line-height:1.8;">'
            "L'accès est momentanément indisponible.<br>"
            "L'archipel refait surface bientôt — reviens dans un moment."
            "</p>",
            unsafe_allow_html=True,
        )


# ── Point d'entrée public ─────────────────────────────────────────────────────

def portail_acces() -> None:
    """Garde le parcours. Rend la main si l'accès est ouvert ; sinon affiche
    l'écran de code et coupe l'exécution du script (st.stop()).
    """
    if st.session_state.get("acces_deverrouille"):
        return

    if not _codes_valides():
        if _en_production():
            # Oubli de configuration sur Render : on ferme. Un jeu ouvert à tous
            # est un incident plus coûteux qu'une porte close.
            _LOG.warning(
                "Aucun code d'accès configuré (st.secrets['%s'] ni %s) en production : "
                "portail fermé. Définir %s dans les réglages du service.",
                _CLE_SECRET,
                _VAR_ENV,
                _VAR_ENV,
            )
            _afficher_ecran_indisponible()
            st.stop()

        # En local, pas de secrets à configurer pour lancer le jeu.
        _LOG.warning(
            "Aucun code d'accès configuré (st.secrets['%s'] ni %s) : "
            "portail ouvert (dev local).",
            _CLE_SECRET,
            _VAR_ENV,
        )
        st.session_state["acces_deverrouille"] = True
        return

    _afficher_ecran()
    st.stop()
