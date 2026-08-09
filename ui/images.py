"""
ui/images.py — Chargement optimisé des illustrations.

Les assets narratifs sont des PNG de 2,5 à 3,7 Mo, pensés pour l'impression et
non pour le web.

CE QUE CE MODULE APPORTE, MESURÉ — et ce qu'il n'apporte pas.
st.image ré-encode déjà en JPEG ce qu'on lui donne : le PNG de 3,1 Mo de
l'écran d'accueil arrivait au navigateur en 629 Ko, pas en 3,1 Mo. Ce qui
manquait, c'est la RÉDUCTION DE DIMENSIONS : l'image est servie en pleine
définition alors qu'elle s'affiche sur un millier de pixels. En la ramenant à
1200 px, elle passe de 629 à 346 Ko — 45 % de moins sur le premier écran du
parcours, et l'écart grandit avec les assets les plus définis.

Le travail est fait une fois par image et par process (st.cache_data). Même
approche que ui/accueil_ile.py, qui l'avait introduite pour son décor de
session ; elle est ici partagée.

RÈGLES DE SÛRETÉ — un décor n'a jamais le droit de casser un écran :
  - une image avec transparence reste en PNG (une icône passée en JPEG se
    retrouverait sur un fond noir) ;
  - toute erreur — Pillow absent, fichier illisible, format inattendu —
    retombe sur les octets d'origine, voire sur None si le fichier manque.

Point d'entrée public : charger_image(chemin)
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import streamlit as st

# Les illustrations s'affichent au plus sur ~1000 px de large (colonne centrale
# en layout « wide ») : au-delà, les pixels transmis ne sont jamais vus.
_LARGEUR_MAX = 1200
_QUALITE_JPEG = 86


@st.cache_data(show_spinner=False)
def charger_image(chemin: str, largeur_max: int = _LARGEUR_MAX) -> bytes | None:
    """Octets de l'illustration, réduite et ré-encodée. None si le fichier est absent.

    Le résultat est mis en cache : la conversion n'a lieu qu'une fois par image
    et par process, jamais à chaque rerun.
    """
    p = Path(chemin)
    if not p.exists():
        return None

    brut = p.read_bytes()
    try:
        from PIL import Image

        image = Image.open(BytesIO(brut))
        image.load()

        # Transparence : rester en PNG. Un aplatissement en JPEG donnerait un
        # fond noir aux icônes et aux découpes.
        transparente = image.mode in ("RGBA", "LA", "P") and "transparency" in image.info
        transparente = transparente or image.mode in ("RGBA", "LA")

        if image.width > largeur_max:
            image.thumbnail((largeur_max, largeur_max))
        elif not transparente and p.suffix.lower() != ".png":
            return brut  # déjà petite et déjà compressée : rien à gagner

        tampon = BytesIO()
        if transparente:
            image.save(tampon, format="PNG", optimize=True)
        else:
            image.convert("RGB").save(
                tampon,
                format="JPEG",
                quality=_QUALITE_JPEG,
                optimize=True,
                progressive=True,
            )
        optimisee = tampon.getvalue()
    except Exception:  # noqa: BLE001 — Pillow absent, format inattendu, fichier abîmé
        return brut

    # Garde-fou : sur une petite image déjà optimisée, le ré-encodage peut
    # alourdir. On ne sert la version convertie que si elle fait gagner.
    return optimisee if len(optimisee) < len(brut) else brut
