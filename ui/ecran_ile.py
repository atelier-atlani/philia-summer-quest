"""
ui/ecran_ile.py — Écran île : arrivée puis présentation, avant la session.
Sprint 3 T8.5 (D-T8.5-F)

Mini state machine à 2 étapes, scopée à cet écran, pilotée par
st.session_state["etape_ile"] :
    "arrivee"      → image <ile_id>/arrivee_<genre>.png + accueil d'Archimède
    "presentation" → image <ile_id>/presentation_<genre>.png + présentation
                     du domaine mathématique de l'île, puis bouton d'entrée
                     dans la session courante

Au tout premier accès à une île (dans cette session navigateur), le texte
d'accueil complet est affiché. Aux accès suivants, une formule de retour
courte est utilisée à la place (voir .claude/production/narration-iles.md).

La session proposée n'est JAMAIS la session 1 en dur : elle est dérivée des
coffres déjà gagnés par recompenses.session_courante() — c'est ce qui rend les
sessions 2 à 5 jouables et la reprise correcte après fermeture du navigateur.
Quand les cinq coffres sont gagnés, l'île n'a plus de session à proposer et
l'écran route vers la fin d'île (clé + célébration + énigme).

Textes narratifs source : .claude/production/narration-iles.md (Île 1, 2, 3).
Point d'entrée public : render_ile()
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.constants import ILE_NOMS
from data_layer.joueurs import charger_joueur_courant
from jeu import recompenses
from ui.accueil_ile import afficher_accueil_ile
from ui.tableau_bord import render_tableau_bord

_ASSETS_NARRATIF = Path(__file__).parent.parent / "assets" / "narratif"

# ── Textes narratifs par île (source : narration-iles.md) ────────────────────

_TEXTES_NARRATIFS: dict[str, dict[str, str]] = {
    "ile_1": {
        "arrivee": (
            "Te voilà, Élévateur.\n\n"
            "Regarde cette île. Elle était entière, autrefois. Un cataclysme "
            "l'a brisée en morceaux — chaque partie séparée du tout. Depuis, "
            "elle attend.\n\n"
            "Les mathématiciens appellent ça une *fraction* : un morceau d'un "
            "tout brisé. *Fractio*, en latin — l'action de briser. Cette île "
            "porte ce nom jusque dans ses pierres."
        ),
        "presentation": (
            "Pour la faire remonter, tu vas apprendre à manier les parts. "
            "Pas à les mémoriser : à les *voir*, à les *sentir*, à les "
            "*utiliser*.\n\n"
            "On commence par le pont. Il a sept planches. Il en manque "
            "quelques-unes."
        ),
    },
    "ile_2": {
        "arrivee": (
            "La Forêt des Mesures. Elle n'est pas brisée — elle est perdue.\n\n"
            "Ici, tout a un périmètre et une aire. Mais personne ne les a "
            "mesurés depuis très longtemps. Les sentiers ont disparu parce "
            "que personne ne savait plus où ils finissaient."
        ),
        "presentation": (
            "Mesurer, c'est donner une frontière aux choses. C'est voir où "
            "le tout commence et où il s'arrête. C'est exactement ce que tu "
            "vas apprendre ici."
        ),
    },
    "ile_3": {
        "arrivee": (
            "Le Labyrinthe des Inconnues. Chaque porte ici porte une "
            "question.\n\n"
            "Les anciens ont utilisé des lettres là où ils ne connaissaient "
            "pas encore les nombres. Pas des lettres pour écrire des mots — "
            "des lettres pour dire « ce nombre qu'on cherche »."
        ),
        "presentation": (
            "Ici, *x* n'est pas un signe d'alarme. C'est une invitation.\n\n"
            "La première porte t'attend."
        ),
    },
}

_TEXTE_GENERIQUE_ARRIVEE = "Une nouvelle île se dévoile devant toi."
_TEXTE_GENERIQUE_PRESENTATION = "Archimède prépare la première épreuve."


# ── Helpers image ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _charger_image(chemin: str) -> bytes | None:
    """Charge une image en bytes. Retourne None si le fichier est absent."""
    p = Path(chemin)
    if p.exists():
        return p.read_bytes()
    return None


def _afficher_texte(texte: str) -> None:
    paragraphes = [p.strip() for p in texte.split("\n\n") if p.strip()]
    html = "\n".join(
        f'<p style="margin-bottom:1em;">{p.replace(chr(10), "<br>")}</p>'
        for p in paragraphes
    )
    st.markdown(
        f'<div style="font-size:1.05rem;line-height:1.8;">{html}</div>',
        unsafe_allow_html=True,
    )


# ── Initialisation session_state ─────────────────────────────────────────────

def _init_state() -> None:
    if "etape_ile" not in st.session_state:
        st.session_state["etape_ile"] = "arrivee"
    if "iles_visitees" not in st.session_state:
        st.session_state["iles_visitees"] = set()
    # Îles dont l'écran d'accueil (dialogue en overlay) a déjà été montré :
    # il ne se joue qu'une fois, à l'entrée, avant la session 1.
    if "accueils_ile_vus" not in st.session_state:
        st.session_state["accueils_ile_vus"] = set()


def _accueil_ile_a_montrer(ile_id: str) -> bool:
    """L'écran d'accueil est un PROTOTYPE propre à l'Île 1 : ses textes nomment
    les fractions et l'Île des Nombres Brisés. Les autres îles gardent le flux
    actuel tant qu'elles n'ont pas leurs propres textes.

    Il ne se joue qu'à la TOUTE première entrée dans l'île : accueils_ile_vus le
    garantit dans la session navigateur, et le premier coffre le garantit d'une
    session à l'autre — un enfant qui reprend en session 3 ne se fait pas
    réaccueillir comme s'il découvrait l'île.
    """
    return (
        ile_id == "ile_1"
        and ile_id not in st.session_state["accueils_ile_vus"]
        and recompenses.session_courante(ile_id) == 1
    )


# ── Progression : quelle session proposer ? ──────────────────────────────────

def _armer_session(ile_id: str, numero: int) -> None:
    """Prépare l'entrée dans la session `numero` de l'île.

    session_courante n'est qu'un relais d'affichage pour ecran_session : la
    valeur de vérité reste les coffres. On repart d'un moteur neuf dès que le
    numéro change, sinon l'enfant reprendrait le chat de la session précédente.
    """
    if st.session_state.get("session_courante") != numero:
        st.session_state.session_courante = numero
        st.session_state.session_active = None


def _router_fin_ile(ile_id: str, nom_ile: str) -> None:
    """Les cinq coffres sont gagnés : il n'y a plus de session à jouer.

    On rejoint le flux de fin d'île déjà en place (ui/modal_planche_bd.py) :
    clé de l'île — idempotente (T7), filet si la dernière planche BD n'a jamais
    été refermée — puis célébration forte, qui propose l'énigme finale ou le
    retour à l'archipel. Aucun écran nouveau, aucune session 6 inexistante.
    """
    recompenses.gagner_cle(ile_id)
    st.session_state.celebration_fin_ile_a_afficher = {"nom_ile": nom_ile}
    st.session_state.session_active = None
    st.session_state["etape_ile"] = "arrivee"  # reset pour le prochain accès
    st.session_state.ecran_courant = "session"


def _libelle_bouton_session(numero: int) -> str:
    """« Commencer » à la première session, « Continuer » ensuite : l'enfant doit
    lire d'un coup d'œil qu'il reprend là où il s'était arrêté."""
    if numero == 1:
        return "Commencer la Session 1"
    return f"Continuer — Session {numero}"


# ── Étape 1 : Arrivée ─────────────────────────────────────────────────────────

def _afficher_arrivee(ile_id: str, genre: str, prenom: str, nom_ile: str) -> None:
    chemin = _ASSETS_NARRATIF / ile_id / f"arrivee_{genre}.png"
    img = _charger_image(str(chemin))

    col_img, col_txt = st.columns([1, 2], gap="large")
    with col_img:
        if img:
            st.image(img, use_container_width=True)
        else:
            st.markdown("🏝️")  # fallback si image absente

    with col_txt:
        deja_visitee = ile_id in st.session_state["iles_visitees"]
        if deja_visitee:
            texte = f"Bon retour, {prenom}. {nom_ile} t'attendait."
        else:
            texte = _TEXTES_NARRATIFS.get(ile_id, {}).get("arrivee", _TEXTE_GENERIQUE_ARRIVEE)
        _afficher_texte(texte)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Continuer →", key="btn_ile_continuer_arrivee", type="primary"):
            st.session_state["iles_visitees"].add(ile_id)
            st.session_state["etape_ile"] = "presentation"
            st.rerun()

    if st.button("← Retour à la carte", key="btn_retour_carte_arrivee"):
        st.session_state["etape_ile"] = "arrivee"
        st.session_state.ecran_courant = "carte"
        st.rerun()


# ── Étape 2 : Présentation ───────────────────────────────────────────────────

def _afficher_presentation(ile_id: str, genre: str, nom_ile: str) -> None:
    chemin = _ASSETS_NARRATIF / ile_id / f"presentation_{genre}.png"
    img = _charger_image(str(chemin))

    col_img, col_txt = st.columns([1, 2], gap="large")
    with col_img:
        if img:
            st.image(img, use_container_width=True)
        else:
            st.markdown("🏝️")  # fallback si image absente

    with col_txt:
        texte = _TEXTES_NARRATIFS.get(ile_id, {}).get("presentation", _TEXTE_GENERIQUE_PRESENTATION)
        _afficher_texte(texte)

        st.markdown("<br>", unsafe_allow_html=True)
        numero = recompenses.session_courante(ile_id)

        if numero is None:
            # Île terminée : on ne propose pas une session 6 qui n'existe pas.
            if st.button(
                "La clé de l'île t'attend →",
                key="btn_fin_ile",
                type="primary",
            ):
                _router_fin_ile(ile_id, nom_ile)
                st.rerun()
        elif st.button(
            _libelle_bouton_session(numero), key="btn_commencer_session", type="primary"
        ):
            _armer_session(ile_id, numero)
            if _accueil_ile_a_montrer(ile_id):
                # L'accueil s'intercale ici : c'est lui qui routera vers la session.
                st.session_state["etape_ile"] = "accueil"
            else:
                st.session_state["etape_ile"] = "arrivee"  # reset pour le prochain accès à une île
                st.session_state.ecran_courant = "session"
            st.rerun()

    if st.button("← Retour à la carte", key="btn_retour_carte_presentation"):
        st.session_state["etape_ile"] = "arrivee"
        st.session_state.ecran_courant = "carte"
        st.rerun()


# ── Étape 3 : Accueil d'île (dialogue en overlay) ────────────────────────────

def _afficher_accueil(ile_id: str, genre: str, prenom: str, nom_ile: str) -> None:
    if afficher_accueil_ile(genre=genre, prenom=prenom):
        st.session_state["accueils_ile_vus"].add(ile_id)
        numero = recompenses.session_courante(ile_id)
        if numero is None:
            _router_fin_ile(ile_id, nom_ile)
        else:
            # Même dérivation qu'à la présentation : jamais de « session 1 » en dur.
            _armer_session(ile_id, numero)
            st.session_state["etape_ile"] = "arrivee"  # reset pour le prochain accès
            st.session_state.ecran_courant = "session"
        st.rerun()


# ── Point d'entrée public ─────────────────────────────────────────────────────

def render_ile() -> None:
    _init_state()
    render_tableau_bord()

    ile_id = st.session_state.get("ile_courante", "ile_1")
    nom_ile = ILE_NOMS.get(ile_id, ile_id)

    joueur = charger_joueur_courant()
    genre = joueur["avatar_genre"] if joueur else "fille"
    prenom = (joueur.get("prenom") if joueur else None) or "Élévateur"

    st.title(nom_ile)

    etape = st.session_state["etape_ile"]
    if etape == "accueil":
        _afficher_accueil(ile_id, genre, prenom, nom_ile)
    elif etape == "presentation":
        _afficher_presentation(ile_id, genre, nom_ile)
    else:
        _afficher_arrivee(ile_id, genre, prenom, nom_ile)
