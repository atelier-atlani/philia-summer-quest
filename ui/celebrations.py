"""
ui/celebrations.py — Célébrations D27 : légère (progression) et forte (fin d'île).
Sprint 3 T8.6 (D-T8.6-A, B, F, G)

Célébration légère : toast (formulation variée) à chaque progression d'exercice.
Célébration forte   : modal dédié + Clé du Partage en grand + message
                       d'Archimède à la fin d'une île.

Aucune librairie externe (D-T8.6-B, D13, D25) — uniquement les primitives Streamlit.
La garde anti-rejeu (D-T8.6-G) est de la responsabilité de l'appelant
(flag st.session_state consommé immédiatement après affichage), pas de ce module.
"""

from __future__ import annotations

import base64
import random
from html import escape
from pathlib import Path

import streamlit as st

from data_layer.joueurs import charger_joueur_courant
from pedagogie.enigme_engine import EnigmeEngine

# Dupliqué depuis ui/ecran_carte.py plutôt qu'importé : celebrations.py est un
# utilitaire transverse, le faire dépendre d'un module d'écran inverserait le
# sens des dépendances (ecran_session importe déjà celebrations).
_CLE_IMAGE_PATH = "assets/ui/cle_partage.png"
_COFFRE_IMAGE_PATH = "assets/ui/coffre.png"


@st.cache_data
def _img_b64(path: str) -> str:
    """Charge l'image en base64 (mis en cache — chargée une seule fois)."""
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()


@st.cache_data
def _img_b64_optionnel(path: str) -> str | None:
    """Comme _img_b64 mais retourne None si l'asset n'est pas encore produit."""
    p = Path(path)
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

# Formulations du toast léger, en rotation aléatoire (T8.6.2) — un même
# message répété ~65 fois sur le parcours perd tout signal.
_TOASTS_LEGERS = (
    "Bien joué {prenom} !",
    "{prenom}, tu progresses !",
    "En route, {prenom} !",
    "Continue comme ça, {prenom} !",
)

# Texte narratif définitif de la célébration forte de fin d'Île 1 (T8.6.1).
# D-T8.6-F / §7 du brief : rédigé par le Décideur. Remplace le placeholder.
#
# NOTE (T8.6.1) : ce texte est spécifique à l'Île 1 (« Clé du Partage, la
# première de ton voyage », « Île des Nombres Brisés »). afficher_celebration_fin_ile()
# reste générique (paramétrée par nom_ile) et sera appelée pour les Îles 2 et 3
# quand leur contenu existera — il faudra alors soit des textes équivalents par
# île, soit une généralisation de ce message. Hors scope T8.6.1.
#
# {accord} : accord en genre dérivé de avatar_genre (D18), résolu en dur —
# pas d'écriture inclusive / point médian. "fille" -> "Prête", sinon "Prêt".
_MESSAGE_FIN_ILE_1 = (
    "{prenom}, tu l'as fait.\n\n"
    "L'Île des Nombres Brisés respire à nouveau. Les fractions ne sont plus "
    "un mystère — elles racontent l'histoire de tout ce qui se partage, se "
    "divise, se rassemble.\n\n"
    "Tu as gagné la Clé du Partage, la première de ton voyage. Chaque île "
    "libérée t'ouvrira la suivante.\n\n"
    "{accord} pour le prochain voyage ?"
)


def afficher_celebration_legere(prenom: str) -> None:
    """Célébration légère (D-T8.6-A/B) : toast personnalisé au prénom, formulation
    variée pour ne pas écraser le signal de la célébration forte (T8.6.2).

    Ne gère pas l'anti-rejeu — l'appelant est responsable de ne déclencher
    cet affichage qu'une seule fois par événement de progression (D-T8.6-G).
    """
    st.toast(random.choice(_TOASTS_LEGERS).format(prenom=prenom))


def afficher_coffre_session(prenom: str, nom_coffre: str, tally_objets: str = "") -> None:
    """Coffre plein de fin de session : habillage visuel du cristal DÉJÀ gagné.

    Ne crée aucune récompense — gagner_cristal() reste la seule mécanique et a
    été appelée par l'appelant avant d'armer ce modal. Ici on ne fait qu'afficher.

    Le nom du coffre (le concept de la session) est du TEXTE posé en overlay sur
    l'image, jamais peint dedans (pattern carte-fragment) : un seul asset sert
    les cinq coffres. Repli emoji si coffre.png n'est pas encore produit.

    Doit être appelée à chaque rerun tant que le flag est actif (pattern
    modal_planche_bd) — c'est le bouton interne qui efface le flag.
    """
    b64 = _img_b64_optionnel(_COFFRE_IMAGE_PATH)

    # Non dismissible : c'est un point de passage du flux de fin de chapitre, et
    # une fenêtre fermée à la croix ne déclenche aucun rerun côté Streamlit
    # (on_dismiss="ignore" par défaut) — l'écran appelant resterait vide.
    @st.dialog("Coffre rempli !", width="large", dismissible=False)
    def _modal() -> None:
        if b64:
            visuel = (
                f"<img src='data:image/png;base64,{b64}' alt='Coffre' "
                f"style='width:200px;height:auto;"
                f"filter:drop-shadow(0 0 26px rgba(201,169,97,0.85)) "
                f"drop-shadow(0 4px 10px rgba(0,0,0,0.35));'>"
            )
        else:
            visuel = (
                "<div style='font-size:120px;line-height:1;"
                "filter:drop-shadow(0 0 26px rgba(201,169,97,0.85));'>🧰</div>"
            )
        # Nom en overlay sur le bas du visuel — bandeau lisible, texte net.
        st.markdown(
            f"<div style='position:relative;display:flex;flex-direction:column;"
            f"align-items:center;margin:4px 0 18px;'>{visuel}"
            f"<div style='position:absolute;bottom:0;padding:6px 16px;"
            f"border-radius:8px;background:rgba(20,16,10,0.72);"
            f"color:#FFFDF6;font-weight:700;text-align:center;max-width:92%;'>"
            f"{escape(nom_coffre)}</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{prenom}**, ce coffre est à toi.")
        if tally_objets:
            st.markdown(f"Tu y as rangé {tally_objets}.")

        if st.button(
            "Continuer →",
            key="btn_coffre_session_continuer",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.coffre_session_a_afficher = None
            st.rerun()

    _modal()


def afficher_celebration_fin_ile(prenom: str, nom_ile: str) -> None:
    """Célébration forte de fin d'île (D-T8.6-F) : modal dédié, distinct de la
    célébration légère, avec la Clé du Partage en grand + message d'Archimède
    personnalisé.

    Doit être appelée à chaque rerun tant que la célébration doit rester
    affichée (même pattern que modal_planche_bd.py) — c'est le bouton interne
    qui efface le flag et route vers la carte, pas cette fonction elle-même.
    """
    joueur = charger_joueur_courant()
    avatar_genre = joueur.get("avatar_genre") if joueur else None
    accord = "Prête" if avatar_genre == "fille" else "Prêt"

    # Non dismissible, même raison que le coffre : la fermer à la croix ne
    # rerun pas et laisserait l'enfant devant une page vide.
    @st.dialog("Une île s'élève !", width="large", dismissible=False)
    def _modal() -> None:
        # Climax : la clé remplace st.balloons(). Halo volontairement plus
        # large qu'en sidebar ou sur la carte — c'est le moment de la remise.
        st.markdown(
            f"<div style='text-align:center;margin:4px 0 18px;'>"
            f"<img src='data:image/png;base64,{_img_b64(_CLE_IMAGE_PATH)}' "
            f"alt='Clé du Partage' style='width:200px;height:auto;"
            f"filter:drop-shadow(0 0 30px rgba(201,169,97,0.95)) "
            f"drop-shadow(0 4px 10px rgba(0,0,0,0.35));'>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(f"## {nom_ile}")
        texte = _MESSAGE_FIN_ILE_1.format(prenom=prenom, accord=accord)
        st.markdown(texte)

        # Énigme finale (D43) — proposée, jamais imposée : l'enfant peut aussi
        # rentrer directement. Réservée à l'Île 1, seule île dont l'énigme
        # (la couronne d'Hiéron) est écrite.
        if st.session_state.get("ile_courante", "ile_1") == "ile_1":
            if st.button(
                "Archimède veut te confier quelque chose…",
                key="btn_celebration_fin_ile_enigme",
                use_container_width=True,
            ):
                # Moteur créé et persisté ici ; son premier message est joué par
                # ecran_enigme, qui peut l'entourer d'un spinner.
                if st.session_state.get("enigme_active") is None:
                    st.session_state.enigme_active = EnigmeEngine(
                        prenom=prenom,
                        avatar_genre=avatar_genre or "fille",
                    ).to_dict()
                st.session_state.celebration_fin_ile_a_afficher = None
                st.session_state.ecran_courant = "enigme"
                st.rerun()

        if st.button(
            "Retour à l'archipel →",
            key="btn_celebration_fin_ile_retour",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.celebration_fin_ile_a_afficher = None
            st.session_state.ecran_courant = "carte"
            st.rerun()

    _modal()
