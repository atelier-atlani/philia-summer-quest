"""
ui/carte_fragment.py — Gabarit de carte à collectionner (« carte-fragment »).

Trophée de fin d'île : une carte rare, remise à l'enfant quand il a terminé
l'énigme finale d'une île. AUCUNE mécanique de jeu — c'est un objet de
collection, pas une carte à jouer. Le gabarit ne fait qu'afficher.

Réutilisable pour les 7 îles : tous les attributs vivent dans une CarteFragment,
le gabarit n'en connaît aucun. Ajouter la carte de l'Île 2 = ajouter une seconde
constante, sans toucher au rendu.

Module dédié (et non un bloc de ui/ecran_enigme.py) précisément parce que les
6 autres cartes ne seront pas remises depuis l'écran d'énigme de l'Île 1.

Texte toujours en HTML — jamais d'image de texte : les chiffres de collection
doivent être exacts et le texte doit rester sélectionnable et net à tout zoom.
Styles en inline seul, comme ecran_carte.py et celebrations.py — pas de <style>
global qui déborderait sur le reste de l'app.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from html import escape
from pathlib import Path

import streamlit as st

_ASSETS = Path(__file__).parent.parent / "assets"

# Palette « or vieilli » — dérivée du doré de la Clé du Partage
# (rgba(201,169,97) = #C9A961, déjà utilisé pour son halo dans ecran_carte.py
# et celebrations.py) pour que le trophée et la clé soient du même métal.
_OR_CLAIR   = "#EFE3BC"
_OR         = "#C9A961"
_OR_SOMBRE  = "#8C6F35"
_PARCHEMIN  = "#FFFDF6"
_PARCHEMIN2 = "#F6ECD3"
_ENCRE      = "#5C4413"
_ENCRE_DOUX = "#7A6844"

_SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif"


# ── Modèle ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CarteFragment:
    """Attributs d'une carte de collection. Le gabarit ne lit que ça."""
    nom: str
    rarete: str
    ile: str                  # « L'Île des Nombres Brisés — Fractions »
    debloquee_par: str        # libellé de la clé
    cle_icone: str            # chemin de l'icône de clé
    fragment_num: int
    fragment_total: int
    notion_cle: str
    illustration_path: str
    emoji_secours: str = "🏺"  # placeholder si l'illustration n'est pas produite


CARTE_FRAGMENT = CarteFragment(
    nom="Le Secret de la Couronne",
    rarete="Fragment",
    ile="L'Île des Nombres Brisés — Fractions",
    debloquee_par="Clé du Partage",
    cle_icone=str(_ASSETS / "ui" / "cle_partage.png"),
    fragment_num=1,
    fragment_total=7,
    notion_cle="Une fraction, c'est une part d'un tout.",
    illustration_path=str(_ASSETS / "ui" / "illu_couronne_hieron.png"),
    emoji_secours="👑",
)

# Île 2 et suivantes : une seconde constante ici, rien d'autre à écrire.


# ── Helpers ───────────────────────────────────────────────────────────────────


@st.cache_data(show_spinner=False)
def _img_b64(chemin: str) -> str | None:
    """Encode une image en base64. Retourne None si le fichier est absent."""
    p = Path(chemin)
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None


def _coin(vertical: str, horizontal: str) -> str:
    """Ornement d'angle : deux traits fins qui redoublent le cadre."""
    rayon = {
        ("top", "left"): "8px 0 0 0", ("top", "right"): "0 8px 0 0",
        ("bottom", "left"): "0 0 0 8px", ("bottom", "right"): "0 0 8px 0",
    }[(vertical, horizontal)]
    return (
        f"<div style=\"position:absolute;{vertical}:5px;{horizontal}:5px;"
        f"width:19px;height:19px;border-{vertical}:2px solid rgba(255,253,246,.75);"
        f"border-{horizontal}:2px solid rgba(255,253,246,.75);border-radius:{rayon};"
        f"pointer-events:none;\"></div>"
    )


def _fenetre_illustration(carte: CarteFragment) -> str:
    """Fenêtre du cadre. Retombe sur un panneau orné si l'illustration manque —
    jamais d'image cassée, jamais de crash."""
    b64 = _img_b64(carte.illustration_path)
    if b64:
        contenu = (
            f"<img src=\"data:image/png;base64,{b64}\" alt=\"{escape(carte.nom)}\" "
            f"style=\"display:block;width:100%;height:100%;object-fit:cover;\">"
        )
    else:
        # Médaillon orné : sans lui, la fenêtre vide fait « image manquante ».
        contenu = (
            f"<div style=\"display:flex;align-items:center;justify-content:center;"
            f"width:100%;height:100%;\">"
            f"<div style=\"display:flex;align-items:center;justify-content:center;"
            f"width:44%;aspect-ratio:1;border-radius:50%;font-size:52px;line-height:1;"
            f"background:radial-gradient(circle at 50% 40%,rgba(255,253,246,.95),"
            f"rgba(201,169,97,.18));"
            f"box-shadow:inset 0 0 0 1px rgba(201,169,97,.55),"
            f"0 0 0 6px rgba(201,169,97,.13),0 3px 10px rgba(140,111,53,.2);"
            f"filter:drop-shadow(0 3px 5px rgba(140,111,53,.3));\">"
            f"{carte.emoji_secours}</div></div>"
        )
    return (
        f"<div style=\"position:relative;aspect-ratio:4/3;border-radius:9px;"
        f"overflow:hidden;background:radial-gradient(circle at 50% 35%,{_PARCHEMIN} 0%,"
        f"#EFE0BE 70%,#E3D2A8 100%);"
        f"box-shadow:inset 0 0 0 2px {_OR},inset 0 0 0 3px rgba(255,253,246,.85),"
        f"inset 0 6px 18px rgba(140,111,53,.22);\">"
        f"{contenu}</div>"
    )


def _pastilles(num: int, total: int) -> str:
    """Une pastille par île — allumées jusqu'au fragment obtenu."""
    points = []
    for i in range(total):
        if i < num:
            points.append(
                f"<span style=\"width:9px;height:9px;border-radius:50%;"
                f"background:radial-gradient(circle at 35% 30%,{_OR_CLAIR},{_OR} 60%,{_OR_SOMBRE});"
                f"box-shadow:0 0 6px rgba(201,169,97,.9);display:inline-block;\"></span>"
            )
        else:
            points.append(
                f"<span style=\"width:9px;height:9px;border-radius:50%;"
                f"background:rgba(140,111,53,.12);"
                f"box-shadow:inset 0 0 0 1px rgba(140,111,53,.38);display:inline-block;\"></span>"
            )
    return (
        f"<span style=\"display:inline-flex;gap:5px;align-items:center;\">"
        f"{''.join(points)}</span>"
    )


def _ligne_cle(carte: CarteFragment) -> str:
    b64 = _img_b64(carte.cle_icone)
    icone = (
        f"<img src=\"data:image/png;base64,{b64}\" alt=\"\" "
        f"style=\"width:24px;height:auto;vertical-align:middle;"
        f"filter:drop-shadow(0 0 6px rgba(201,169,97,.85));\">"
        if b64 else "<span style=\"font-size:18px;\">🗝️</span>"
    )
    return (
        f"<span style=\"display:inline-flex;align-items:center;gap:7px;\">"
        f"{icone}"
        f"<span style=\"font-family:{_SERIF};font-size:.82rem;color:{_ENCRE};\">"
        f"{escape(carte.debloquee_par)}</span></span>"
    )


# ── Gabarit ───────────────────────────────────────────────────────────────────


def html_carte_fragment(carte: CarteFragment) -> str:
    """Rend la carte en HTML. Pur — testable sans Streamlit."""
    coins = "".join(
        _coin(v, h) for v in ("top", "bottom") for h in ("left", "right")
    )

    entete_rarete = (
        f"<div style=\"text-align:center;margin:0 0 10px;\">"
        f"<span style=\"display:inline-block;padding:3px 14px;border-radius:999px;"
        f"background:linear-gradient(180deg,{_OR_CLAIR},{_OR} 55%,{_OR_SOMBRE});"
        f"box-shadow:0 1px 3px rgba(140,111,53,.45),inset 0 1px 0 rgba(255,255,255,.6);"
        f"font-family:{_SERIF};font-size:.68rem;letter-spacing:.18em;"
        f"text-transform:uppercase;color:#FFFDF6;"
        f"text-shadow:0 1px 1px rgba(92,68,19,.6);\">"
        f"{escape(carte.rarete)}</span></div>"
    )

    titre = (
        f"<div style=\"font-family:{_SERIF};font-size:1.3rem;line-height:1.25;"
        f"font-weight:600;color:{_ENCRE};text-align:center;margin:12px 0 6px;"
        f"letter-spacing:.01em;\">{escape(carte.nom)}</div>"
    )

    # Fleuron : filet or ─ ◆ ─ or
    fleuron = (
        f"<div style=\"display:flex;align-items:center;gap:8px;margin:0 0 8px;\">"
        f"<span style=\"flex:1;height:1px;background:linear-gradient(90deg,"
        f"rgba(201,169,97,0),{_OR});\"></span>"
        f"<span style=\"color:{_OR};font-size:.6rem;\">◆</span>"
        f"<span style=\"flex:1;height:1px;background:linear-gradient(90deg,"
        f"{_OR},rgba(201,169,97,0));\"></span></div>"
    )

    ile = (
        f"<div style=\"font-family:{_SERIF};font-size:.85rem;color:{_ENCRE_DOUX};"
        f"text-align:center;margin:0 0 14px;font-style:italic;\">"
        f"{escape(carte.ile)}</div>"
    )

    # Clé + compteur de collection. flex-wrap : sur écran étroit, le compteur
    # passe sous la clé au lieu de déborder.
    pied = (
        f"<div style=\"display:flex;flex-wrap:wrap;gap:8px;align-items:center;"
        f"justify-content:space-between;padding:9px 11px;border-radius:8px;"
        f"background:rgba(201,169,97,.13);"
        f"box-shadow:inset 0 0 0 1px rgba(201,169,97,.4);margin:0 0 12px;\">"
        f"{_ligne_cle(carte)}"
        f"<span style=\"display:inline-flex;align-items:center;gap:9px;\">"
        f"{_pastilles(carte.fragment_num, carte.fragment_total)}"
        f"<span style=\"font-family:{_SERIF};font-size:.9rem;font-weight:600;"
        f"color:{_ENCRE};letter-spacing:.03em;\">"
        f"{carte.fragment_num} / {carte.fragment_total}</span></span></div>"
    )

    notion = (
        f"<div style=\"border-left:3px solid {_OR};border-radius:0 8px 8px 0;"
        f"background:linear-gradient(90deg,rgba(201,169,97,.16),rgba(201,169,97,.05));"
        f"padding:10px 12px;\">"
        f"<div style=\"font-family:{_SERIF};font-size:.62rem;letter-spacing:.16em;"
        f"text-transform:uppercase;color:{_ENCRE_DOUX};margin:0 0 3px;\">"
        f"Notion-clé</div>"
        f"<div style=\"font-family:{_SERIF};font-size:.95rem;line-height:1.4;"
        f"color:{_ENCRE};\">{escape(carte.notion_cle)}</div></div>"
    )

    interieur = (
        f"<div style=\"position:relative;border-radius:12px;padding:15px 15px 14px;"
        f"background:linear-gradient(175deg,{_PARCHEMIN} 0%,{_PARCHEMIN2} 100%);"
        f"box-shadow:inset 0 0 0 1px rgba(140,111,53,.45),"
        f"inset 0 2px 16px rgba(140,111,53,.13);\">"
        f"{entete_rarete}{_fenetre_illustration(carte)}{titre}{fleuron}{ile}{pied}{notion}"
        f"</div>"
    )

    # Cadre : dégradé métal (reflets clairs aux angles, creux sombre au centre)
    # + halo doré repris de la Clé du Partage.
    cadre = (
        f"<div style=\"position:relative;width:min(380px,92%);padding:13px;"
        f"border-radius:18px;"
        f"background:linear-gradient(145deg,#F7EFD4 0%,#D8BC7A 17%,#A9873F 37%,"
        f"{_OR_SOMBRE} 50%,#B99552 63%,{_OR_CLAIR} 83%,#FBF5E2 100%);"
        f"box-shadow:0 0 34px rgba(201,169,97,.6),0 10px 26px rgba(0,0,0,.32),"
        f"inset 0 0 0 1px rgba(255,253,246,.45);\">"
        f"{coins}{interieur}</div>"
    )

    return (
        f"<div style=\"display:flex;justify-content:center;margin:10px 0 20px;\">"
        f"{cadre}</div>"
    )


def afficher_carte_fragment(carte: CarteFragment = CARTE_FRAGMENT) -> None:
    """Affiche la carte de collection dans l'écran courant."""
    st.markdown(html_carte_fragment(carte), unsafe_allow_html=True)
