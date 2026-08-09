"""
ui/ecran_lien_partie.py — « Voici ton lien, garde-le », après création de la partie.

Écran destiné au PARENT, montré une seule fois, juste après la création de
l'avatar et avant que le récit ne reprenne. C'est le seul moment où le lien de
la partie peut être transmis : sans compte ni email, ce lien EST la partie.
Le perdre, c'est repartir d'une partie vierge.

Le lien porte les deux paramètres qui doivent survivre à tout rechargement :
le marqueur d'accès (sinon le portail se redemande) et l'identifiant de partie
(sinon l'enfant repart de zéro).

Point d'entrée public : afficher_ecran_lien_partie()
"""

from __future__ import annotations

from urllib.parse import urlencode, urlsplit, urlunsplit

import streamlit as st

from core.partie import parametres_url_partie
from ui.ecran_acces import parametres_url_acces


def _base_url() -> str:
    """Racine publique de l'app, query string retirée.

    st.context.url donne l'URL réelle vue par le navigateur — donc le domaine
    Render en production, et localhost en développement. Si elle manque, on
    retombe sur un lien relatif : moins confortable à copier, mais jamais faux.
    """
    brute = getattr(st.context, "url", None)
    if not brute:
        return ""
    morceaux = urlsplit(brute)
    return urlunsplit((morceaux.scheme, morceaux.netloc, morceaux.path, "", ""))


def lien_partie() -> str:
    """Lien complet à conserver : accès + partie."""
    params = {**parametres_url_acces(), **parametres_url_partie()}
    return f"{_base_url()}?{urlencode(params)}"


def afficher_ecran_lien_partie() -> None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align:center;font-size:3rem;">🔑</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h2 style="text-align:center;">Un mot pour les parents</h2>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align:center;font-size:1.05rem;line-height:1.8;">'
            "Voici le lien de la partie. Il faudra l'ouvrir à chaque fois pour "
            "retrouver l'aventure là où elle a été laissée.<br>"
            "<strong>Mets-le en favori, ou envoie-le-toi par message.</strong>"
            "</p>",
            unsafe_allow_html=True,
        )

        # st.code affiche un bouton copier natif — pas de dépendance, pas de JS.
        st.code(lien_partie(), language=None, wrap_lines=True)

        st.caption(
            "Sans ce lien, l'aventure repart d'une île vierge : la progression "
            "y est attachée."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("J'ai gardé le lien — continuer →", type="primary", width="stretch"):
            st.session_state["ecran_courant"] = "presentation_archipel"
            st.rerun()
