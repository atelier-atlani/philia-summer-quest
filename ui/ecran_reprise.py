"""
ui/ecran_reprise.py — « Ah, te voilà ! » : l'enfant rouvre son lien.

Un enfant qui revient sur une partie entamée ne doit pas retomber sur la carte
comme un visiteur : Archimède l'accueille par son prénom et lui propose de
repartir directement là où il s'était arrêté.

QUAND CET ÉCRAN S'AFFICHE (decision prise par app.py via doit_proposer_la_reprise)
    - partie à peine créée (session 1, aucun coffre) → NON, flux normal ;
    - session 2 à 5, ou au moins un coffre gagné     → OUI, accueil de reprise ;
    - île terminée (plus aucune session)             → OUI, variante « félicitations »,
      dont le bouton rejoint le flux de fin d'île déjà en place plutôt que de
      proposer une session qui n'existe pas.

La progression n'est jamais stockée : elle se dérive des coffres
(jeu/recompenses.session_courante). Cet écran ne fait que la lire.

Point d'entrée public : afficher_ecran_reprise()
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.constants import ILE_NOMS
from data_layer.joueurs import charger_joueur_courant
import jeu.recompenses as recompenses
import ui.flux_chapitre as flux_chapitre

_ASSETS_NARRATIF = Path(__file__).parent.parent / "assets" / "narratif" / "globaux"

# Paramètre d'URL posé par les liens de la carte : sa présence signale une
# navigation en cours (l'enfant vient de cliquer une île), pas une arrivée.
_PARAM_ILE = "ile"

_ORDINAUX = {1: "première", 2: "deuxième", 3: "troisième", 4: "quatrième", 5: "cinquième"}


# ── Décision : faut-il proposer la reprise ? ──────────────────────────────────

def partie_entamee(ile_id: str) -> bool:
    """Vrai dès que l'enfant a laissé une trace : une session dépassée, ou un
    coffre gagné quelque part dans l'archipel.

    Une île terminée compte aussi : il y a bien quelque chose à reprendre, et
    c'est la variante « félicitations » qui s'affichera.
    """
    numero = recompenses.session_courante(ile_id)
    if numero is None or numero > 1:
        return True
    try:
        return recompenses.nombre_cristaux_obtenus() > 0 or recompenses.nombre_cles_obtenues() > 0
    except RuntimeError:      # aucun joueur : rien à reprendre
        return False


def doit_proposer_la_reprise(ile_id: str) -> bool:
    """Décision d'aiguillage, appelée par app.py au premier rendu d'une session.

    Le paramètre `ile` dans l'URL veut dire que l'enfant vient de cliquer une
    île sur la carte : ce clic recharge la page entière, donc repasse par ici.
    L'intercepter afficherait « Ah, te voilà ! » à chaque clic d'île — et
    l'enfant n'entrerait jamais dans l'île.
    """
    if _PARAM_ILE in st.query_params:
        return False
    return partie_entamee(ile_id)


# ── Écran ─────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _charger_image(chemin: str) -> bytes | None:
    p = Path(chemin)
    return p.read_bytes() if p.exists() else None


def _ou_en_est_il(ile_id: str, numero: int | None) -> str:
    """Une phrase discrète pour situer l'enfant, sans jargon de progression."""
    nom_ile = ILE_NOMS.get(ile_id, "l'archipel")
    if numero is None:
        return f"Tu as réveillé **{nom_ile}** en entier."
    ordinal = _ORDINAUX.get(numero, f"{numero}e")
    return f"Tu en es à la **{ordinal} étape** de **{nom_ile}**."


def afficher_ecran_reprise() -> None:
    joueur = charger_joueur_courant()
    genre = joueur["avatar_genre"] if joueur else "fille"
    prenom = (joueur.get("prenom") if joueur else None) or "Élévateur"

    ile_id = st.session_state.get("ile_courante", "ile_1")
    numero = recompenses.session_courante(ile_id)
    ile_finie = numero is None

    # Même disposition que les autres écrans narratifs (ui/ecran_presentation_archipel) :
    # l'illustration en grand, le texte dessous, des colonnes latérales en marges.
    _, centre, _ = st.columns([1, 5, 1])

    with centre:
        # Asset réutilisé, aucun nouveau visuel : Archimède face à l'enfant, et
        # surtout conçu pour un texte placé DESSOUS. L'illustration de session
        # porte une bulle BD que ui/accueil_ile.py remplit par un overlay
        # calibré au pixel pour ses textes fixes — la reprendre ici afficherait
        # une bulle vide, ou demanderait de re-mesurer ses zones.
        img = _charger_image(str(_ASSETS_NARRATIF / f"presentation_archipel_{genre}.png"))
        if img:
            st.image(img, use_container_width=True)
        else:
            st.markdown("🏺")  # fallback si image absente

        if ile_finie:
            accroche = (
                f"Ah, te voilà, {prenom} ! Content de te revoir.<br>"
                "Tu as mené cette île jusqu'au bout — il me reste quelque chose "
                "à te remettre."
            )
        else:
            accroche = (
                f"Ah, te voilà, {prenom} ! Content de te revoir.<br>"
                "On reprend notre quête là où tu t'étais arrêté ?"
            )

        st.markdown(
            f'<div style="font-size:1.15rem;line-height:1.8;">{accroche}</div>',
            unsafe_allow_html=True,
        )
        st.caption(_ou_en_est_il(ile_id, numero))

        st.markdown("<br>", unsafe_allow_html=True)
        col_reprendre, col_carte = st.columns(2)

        with col_reprendre:
            if ile_finie:
                # Pas de session 6 : on rejoint le flux de fin d'île déjà en
                # place (clé idempotente puis célébration forte).
                if st.button("La clé de l'île t'attend →", key="btn_reprise_fin_ile",
                             type="primary", width="stretch"):
                    flux_chapitre.armer_fin_d_ile(ile_id)
                    st.rerun()
            elif st.button("Reprendre l'aventure →", key="btn_reprendre",
                           type="primary", width="stretch"):
                # Même armement que ui/ecran_ile : le numéro n'est qu'un relais
                # d'affichage, les coffres restent la vérité. Le moteur repart
                # neuf si la session a changé.
                if st.session_state.get("session_courante") != numero:
                    st.session_state["session_courante"] = numero
                    st.session_state["session_active"] = None
                st.session_state["ile_courante"] = ile_id
                st.session_state["ecran_courant"] = "session"
                st.rerun()

        with col_carte:
            if st.button("Revoir la carte", key="btn_reprise_carte", width="stretch"):
                st.session_state["ecran_courant"] = "carte"
                st.rerun()
