"""
ui/ecran_enigme.py — Écran de l'énigme finale de l'Île 1 (D43).

Responsabilité : orchestrer l'EnigmeEngine, afficher le dialogue, conserver
l'état, et remettre le Parchemin d'Archimède à la fin. L'écran est une vitre —
aucune logique de progression ici, tout est dans pedagogie/enigme_engine.py.

Modèle : ui/ecran_session.py, mais SANS machinerie d'exercice — pas de
compteur, pas de bouton « exercice suivant », pas de modes. L'énigme est un
dialogue libre en 4 temps.

Le rendu du chat est local (et non render_chat de ui/ecran_chat.py) : ce
dernier est typé SessionEngine, lit `est_terminee` comme propriété et persiste
dans `session_active`. L'EnigmeEngine expose `est_terminee()` comme méthode et
vit dans `enigme_active` — les six lignes de boucle sont recopiées plutôt que
de tordre un helper partagé avec les sessions.
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from data_layer.joueurs import charger_joueur_courant
from jeu import recompenses
from pedagogie.enigme_engine import EnigmeEngine

_ASSETS = Path(__file__).parent.parent / "assets"

# L'énigme de la couronne est adossée à l'Île 1 (D43) — elle ne s'ouvre qu'une
# fois sa clé obtenue.
_ILE_ENIGME = "ile_1"

_PARCHEMIN_PATH = _ASSETS / "ui" / "parchemin_archimede.png"

# En-tête : premier asset existant gagne. Le portrait dédié d'Archimède n'est
# pas encore produit — on retombe sur le bandeau déjà utilisé par ecran_session,
# puis sur le titre texte seul. Jamais de placeholder cassé.
_ENTETE_CANDIDATS = (
    _ASSETS / "ui" / "archimede_enigme.png",
    _ASSETS / "mentor" / "mentor" / "archimede.png",
)


# ── Helpers image ─────────────────────────────────────────────────────────────


@st.cache_data(show_spinner=False)
def _charger_image(chemin: str) -> bytes | None:
    """Charge une image en bytes. Retourne None si le fichier est absent."""
    p = Path(chemin)
    if p.exists():
        return p.read_bytes()
    return None


@st.cache_data(show_spinner=False)
def _img_b64(chemin: str) -> str | None:
    """Encode une image en base64. Retourne None si le fichier est absent."""
    p = Path(chemin)
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None


def _afficher_entete(genre: str) -> None:
    candidats = [*_ENTETE_CANDIDATS,
                 _ASSETS / "narratif" / "globaux" / f"ecran_session_{genre}.png"]
    for chemin in candidats:
        img = _charger_image(str(chemin))
        if img:
            st.image(img, use_container_width=True)
            break
    st.title("Le secret de la couronne")


def _afficher_parchemin() -> None:
    """Remise du Parchemin d'Archimède.

    L'asset est produit séparément — tant qu'il est absent, on affiche une
    remise textuelle digne plutôt qu'une image cassée.
    """
    b64 = _img_b64(str(_PARCHEMIN_PATH))
    if b64:
        st.markdown(
            f"<div style='text-align:center;margin:4px 0 18px;'>"
            f"<img src='data:image/png;base64,{b64}' "
            f"alt=\"Parchemin d'Archimède\" style='width:min(420px,90%);height:auto;"
            f"filter:drop-shadow(0 0 30px rgba(201,169,97,0.85)) "
            f"drop-shadow(0 4px 10px rgba(0,0,0,0.35));'>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='text-align:center;font-size:64px;margin:8px 0 4px;'>📜</div>",
            unsafe_allow_html=True,
        )
    st.success(
        "**Le Parchemin d'Archimède** — la couronne d'Hiéron et ce que tu viens "
        "d'y découvrir. Il t'attendra sur les autres îles."
    )


# ── Moteur ────────────────────────────────────────────────────────────────────


def _init_engine() -> EnigmeEngine:
    """Crée un EnigmeEngine neuf et génère le message d'ouverture d'Archimède."""
    joueur = charger_joueur_courant()
    prenom = (joueur.get("prenom") if joueur else None) or "Élévateur"
    genre = (joueur.get("avatar_genre") if joueur else None) or "fille"
    engine = EnigmeEngine(prenom=prenom, avatar_genre=genre)
    _ouvrir(engine)
    return engine


def _ouvrir(engine: EnigmeEngine) -> None:
    """Joue le kickoff du temps 1 et persiste. L'appel LLM vit ici, sur l'écran,
    pour être couvert par un spinner — pas dans le bouton de déclenchement."""
    with st.spinner("Archimède rassemble ses souvenirs…"):
        engine.debut_enigme()
    st.session_state.enigme_active = engine.to_dict()


# ── Écran ─────────────────────────────────────────────────────────────────────


def render_enigme() -> None:
    joueur = charger_joueur_courant()

    # Verrou d'accès : l'énigme ne s'ouvre qu'après la Clé du Partage. Le modal
    # de fin d'île est le seul chemin prévu, mais l'écran se protège lui-même —
    # un ecran_courant="enigme" posé autrement ne doit pas donner accès au
    # secret (ni au parchemin) avant l'heure.
    if joueur is None or not recompenses.a_obtenu_cle(_ILE_ENIGME):
        st.warning(
            "Archimède n'a pas encore de secret à te confier. Termine l'Île des "
            "Nombres Brisés — il t'attendra là-bas."
        )
        if st.button("← Retour à l'archipel", key="btn_enigme_retour_verrou"):
            st.session_state.ecran_courant = "carte"
            st.rerun()
        return

    genre = joueur.get("avatar_genre") or "fille"
    _afficher_entete(genre)
    st.divider()

    # Initialisation ou restauration du moteur — sans ce round-trip
    # to_dict/from_dict, le dialogue serait perdu à chaque rerun.
    if st.session_state.get("enigme_active") is None:
        engine = _init_engine()
    else:
        engine = EnigmeEngine.from_dict(st.session_state.enigme_active)
        # Moteur créé par le bouton de déclenchement mais jamais ouvert :
        # on joue le premier message ici.
        if not engine.historique:
            _ouvrir(engine)

    # Seule source d'affichage des messages — le kickoff interne est déjà exclu
    # par messages_pour_affichage().
    for msg in engine.messages_pour_affichage():
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
            st.markdown(msg["content"])

    if engine.est_terminee():
        st.divider()
        _afficher_parchemin()
        if st.button(
            "Retour à l'archipel →",
            key="btn_enigme_retour_archipel",
            type="primary",
            use_container_width=True,
        ):
            # On NE vide PAS enigme_active : l'énigme est un moment unique, la
            # rejouer la banaliserait. Un retour sur l'écran ré-affiche le
            # dialogue vécu et le parchemin.
            st.session_state.ecran_courant = "carte"
            st.rerun()
        return

    if user_input := st.chat_input("Ta réponse…"):
        with st.spinner("Archimède réfléchit…"):
            engine.repondre(user_input)
        st.session_state.enigme_active = engine.to_dict()
        st.rerun()
