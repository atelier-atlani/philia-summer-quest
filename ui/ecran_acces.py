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

import hashlib
import logging
import os
from pathlib import Path

import streamlit as st

from ui.images import charger_image

_LOG = logging.getLogger(__name__)

# Illustration d'accueil : Archimède et deux enfants face à l'archipel.
_IMG_ACCUEIL = (
    Path(__file__).parent.parent / "assets" / "narratif" / "globaux" / "accueil_invitation.png"
)

_CLE_SECRET = "codes_acces"
_VAR_ENV = "CODES_ACCES"
_CLE_SESSION = "acces_deverrouille"
_PARAM_URL = "acces"
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


# ── Marqueur d'URL (survit au rechargement de page) ───────────────────────────
#
# La carte navigue par liens HTML <a href="?ile=…"> : le navigateur recharge la
# page entière, ce qui ouvre une nouvelle session Streamlit et vide
# st.session_state — le déverrouillage était perdu et le portail revenait.
# Les query params, eux, survivent : on y dépose un marqueur au déverrouillage.
#
# Le marqueur n'est pas un simple "ok" : il est DÉRIVÉ des codes configurés.
# Un marqueur devinable (?acces=ok) annulerait le portail — n'importe qui le
# taperait dans la barre d'adresse. Ici, sans connaître un code valide on ne
# peut pas fabriquer le jeton. Il est stable (mêmes codes → même jeton, donc il
# traverse les redémarrages du serveur) et changer les codes invalide d'office
# les anciennes URL.

def _jeton_url() -> str:
    empreinte = hashlib.sha256(
        ("philia-acces:" + "|".join(sorted(_codes_valides()))).encode("utf-8")
    )
    return empreinte.hexdigest()[:16]


def _marqueur_url_valide() -> bool:
    return bool(_codes_valides()) and st.query_params.get(_PARAM_URL) == _jeton_url()


def parametres_url_acces() -> dict[str, str]:
    """Query params à reporter dans les liens HTML de navigation.

    Un href="?ile=X" écrase TOUTE la query string : les écrans qui naviguent
    ainsi (ui/ecran_carte.py) doivent réinjecter ces params, sinon le marqueur
    disparaît au premier clic et le portail se redemande.
    """
    return {_PARAM_URL: _jeton_url()} if _marqueur_url_valide() else {}


# ── Écran ─────────────────────────────────────────────────────────────────────

# L'illustration est en 4/3 : à pleine largeur elle poussait le champ de code
# sous la ligne de flottaison, et l'enfant n'avait sous les yeux qu'une affiche
# sans savoir où taper. La brider en hauteur de fenêtre garantit que la porte
# reste visible sans défiler, quel que soit l'écran.
# La règle peut être posée au niveau de la page : quand le portail s'affiche,
# rien d'autre ne se rend derrière (portail_acces() coupe le script).
_CSS_ILLUSTRATION = """
<style>
[data-testid="stImage"] img {
    max-height: 46vh;
    /* Streamlit impose width:100% ; sans object-fit, plafonner la hauteur
       écraserait l'illustration au lieu de la réduire. */
    object-fit: contain;
}
</style>
"""


def _afficher_ecran() -> None:
    # L'illustration en grand au-dessus, comme sur les écrans narratifs
    # (ui/ecran_presentation_archipel). Les colonnes latérales ne portent rien :
    # ce sont des marges, sans quoi l'image s'étale sur toute la page en layout
    # « wide » et repousse le champ de saisie hors de l'écran.
    st.markdown(_CSS_ILLUSTRATION, unsafe_allow_html=True)
    _, centre, _ = st.columns([1, 5, 1])

    with centre:
        img = charger_image(str(_IMG_ACCUEIL))
        if img:
            st.image(img, use_container_width=True)
        else:
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

        # Le formulaire reste étroit sous une image large : un champ de code
        # étiré sur toute la largeur se lit mal et ne ressemble plus à une porte.
        _, saisie_col, _ = st.columns([1, 2, 1])
        with saisie_col:
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
                    _deverrouiller()
                    st.rerun()
                elif saisie.strip():
                    st.error(
                        "Ce code ne correspond à aucune clé de l'archipel. "
                        "Vérifie-le et réessaie."
                    )
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

def _deverrouiller() -> None:
    """Ouvre l'accès des deux côtés : session_state (la session courante) et
    query params (ce qui survit à un rechargement complet de la page).
    """
    st.session_state[_CLE_SESSION] = True
    # Sans code configuré (dev local ouvert), rien à mémoriser dans l'URL : le
    # portail se rouvrira de lui-même au rechargement.
    if _codes_valides():
        st.query_params[_PARAM_URL] = _jeton_url()


def portail_acces() -> None:
    """Garde le parcours. Rend la main si l'accès est ouvert ; sinon affiche
    l'écran de code et coupe l'exécution du script (st.stop()).
    """
    # Les deux mémoires se réhydratent l'une l'autre : session_state se perd au
    # rechargement de page (liens de la carte), l'URL se perd quand un lien
    # écrase la query string. Il suffit qu'une des deux ait tenu.
    if st.session_state.get(_CLE_SESSION) or _marqueur_url_valide():
        _deverrouiller()
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
        st.session_state[_CLE_SESSION] = True
        return

    _afficher_ecran()
    st.stop()
