"""
ui/accueil_ile.py — Écran d'accueil d'île (prototype Île 1).

Responsabilité : afficher l'image d'accueil de session avec le dialogue posé en
overlay — Archimède parle dans la bulle BD, l'enfant répond sur le parchemin —
puis lancer la session 1.

PROTOTYPE (à valider en réel avant généralisation aux Îles 2 et 3) : les textes
sont fixes et propres à l'Île 1 ; les zones d'overlay sont calibrées POUR CES
TEXTES. Rallonger un texte sans re-mesurer le fera déborder.

Zones mesurées sur assets/narratif/globaux/ecran_session_{genre}.png (les deux
genres concordent à 0,6 point près — un seul jeu de coordonnées suffit) :
  - bulle BD   : left 49.5 %, top 5 %,  width 42 %, height 17.5 %
  - parchemin  : left 20 %,   top 61 %, width 46 %, height 29 %
Le parchemin porte un cartouche gravé sur sa bande haute (53–59 % de l'image) :
la zone de texte commence dessous, à 61 %.

Le texte est dimensionné en `cqw` (unités de largeur du conteneur) : il suit
donc exactement la largeur de l'image, sans dépendre du viewport ni de l'état
de la sidebar. Repli en `vw` pour les navigateurs sans container queries.
"""

from __future__ import annotations

import base64
import os
from html import escape
from io import BytesIO

import streamlit as st

# L'image source fait ~3 Mo. Réduite à 1200 px et encodée en JPEG, elle tombe à
# ~390 Ko de base64 — le PNG réduit en pesait encore 2,7 Mo, envoyés à chaque
# render. L'illustration est une aquarelle sans transparence : le JPEG convient
# (le chargeur PNG partagé du tableau de bord sert, lui, des vignettes d'icônes).
_LARGEUR_INLINE = 1200
_QUALITE_JPEG = 86

_IMAGE_PATH = "assets/narratif/globaux/ecran_session_{genre}.png"

# Zones d'overlay : (left %, top %, width %, height %)
_ZONE_BULLE = (49.5, 5.0, 42.0, 17.5)
_ZONE_PARCHEMIN = (20.0, 61.0, 46.0, 29.0)

# Corps de texte, en unités de largeur de conteneur. Calibré pour que chaque
# texte tienne dans sa zone sans rognage (vérifié à 400 px comme à 1200 px).
_TAILLE_BULLE = 1.85
_TAILLE_PARCHEMIN = 2.45

_ENCRE_BULLE = "#241D14"
_ENCRE_PARCHEMIN = "#4A3A1E"
_SERIF = "Georgia,'Iowan Old Style','Times New Roman',serif"


@st.cache_data(show_spinner=False)
def _image_b64(chemin: str) -> str | None:
    """Image réduite et encodée en JPEG base64, ou None si l'asset est absent.

    Mis en cache : l'encodage n'a lieu qu'une fois par image et par process.
    """
    if not os.path.exists(chemin):
        return None
    try:
        from PIL import Image

        im = Image.open(chemin).convert("RGB")
        im.thumbnail((_LARGEUR_INLINE, _LARGEUR_INLINE))
        tampon = BytesIO()
        im.save(tampon, format="JPEG", quality=_QUALITE_JPEG, optimize=True, progressive=True)
        return base64.b64encode(tampon.getvalue()).decode()
    except Exception:  # noqa: BLE001 — un décor manquant ne casse pas l'écran
        return None


def _accord(genre: str) -> str:
    """« prête » / « prêt » — accord résolu en dur (D18), pas de point médian."""
    return "prête" if genre == "fille" else "prêt"


def _texte_archimede(prenom: str, genre: str) -> str:
    return (
        f"Alors {prenom}, {_accord(genre)} pour l'aventure ? Je vais te guider "
        "par mes questions pour percer le secret des fractions et reconstruire "
        "l'Île des Nombres Brisés. Cinq étapes t'attendent. À la fin, tu "
        "gagneras la première clé du Secret de Syracuse."
    )


def _texte_eleve(genre: str) -> str:
    return (
        "D'accord Archimède ! Je relève le défi. Je suis "
        f"{_accord(genre)} à répondre à toutes tes épreuves."
    )


def _bloc_texte(zone: tuple[float, float, float, float], texte: str,
                taille_cqw: float, couleur: str, italique: bool = False) -> str:
    """Un bloc de texte positionné en absolu dans sa zone, centré, sans débord."""
    left, top, largeur, hauteur = zone
    style_italique = "font-style:italic;" if italique else ""
    return (
        f"<div style=\"position:absolute;left:{left}%;top:{top}%;"
        f"width:{largeur}%;height:{hauteur}%;"
        f"display:flex;align-items:center;justify-content:center;"
        f"box-sizing:border-box;padding:0 1%;overflow:hidden;"
        f"text-align:center;line-height:1.34;font-family:{_SERIF};"
        f"{style_italique}color:{couleur};"
        # Repli viewport d'abord, unités de conteneur ensuite : la seconde
        # déclaration l'emporte là où les container queries existent.
        f"font-size:{taille_cqw * 0.62:.2f}vw;font-size:{taille_cqw:.2f}cqw;\">"
        f"<span>{escape(texte)}</span></div>"
    )


def html_accueil_ile(b64_image: str, prenom: str, genre: str) -> str:
    """Assemble l'image de fond et les deux blocs de dialogue en overlay."""
    return (
        "<div style=\"position:relative;width:100%;line-height:0;"
        "container-type:inline-size;border-radius:10px;overflow:hidden;"
        "box-shadow:0 3px 14px rgba(140,111,53,.28);\">"
        f"<img src=\"data:image/jpeg;base64,{b64_image}\" alt=\"\" "
        "style=\"width:100%;display:block;\">"
        f"{_bloc_texte(_ZONE_BULLE, _texte_archimede(prenom, genre), _TAILLE_BULLE, _ENCRE_BULLE)}"
        f"{_bloc_texte(_ZONE_PARCHEMIN, _texte_eleve(genre), _TAILLE_PARCHEMIN, _ENCRE_PARCHEMIN, italique=True)}"
        "</div>"
    )


def _repli_sans_image(prenom: str, genre: str) -> None:
    """Sans l'image, le dialogue reste lisible — on ne perd que le décor."""
    st.info(_texte_archimede(prenom, genre))
    st.markdown(f"*{_texte_eleve(genre)}*")


def afficher_accueil_ile(genre: str, prenom: str) -> bool:
    """Rend l'écran d'accueil. Retourne True si l'enfant a cliqué pour commencer.

    L'appelant reste responsable du routage et du marquage « déjà vu » — cet
    écran ne décide pas de la navigation, il la signale.
    """
    b64 = _image_b64(_IMAGE_PATH.format(genre=genre))
    if b64:
        st.markdown(html_accueil_ile(b64, prenom, genre), unsafe_allow_html=True)
    else:
        _repli_sans_image(prenom, genre)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    return st.button(
        "Commencer l'aventure →",
        key="btn_accueil_ile_commencer",
        type="primary",
        use_container_width=True,
    )
