"""
ui/ecran_session.py — Écran d'une session pédagogique.

Responsabilité : afficher la situation narrative, orchestrer le SessionEngine,
conserver l'état et exposer les contrôles de navigation.
L'écran est une vitre. Aucune logique pédagogique ici.

Sprint 3 T8.5 :
  - bandeau narratif genré en tête d'écran (D-T8.5-G)
  - lecture du vrai prénom de l'enfant, fallback "Élévateur" (D-T8.5-C)
  - sélection du contenu de session paramétrée par ile_courante, avec repli
    explicite si l'île n'a pas encore de contenu pédagogique (D-T8.5-H)
"""

from __future__ import annotations

import importlib
from pathlib import Path

import streamlit as st

from config.constants import ILE_NOMS
from data_layer.joueurs import charger_joueur_courant
from jeu import recompenses
from pedagogie.modes import Mode
from pedagogie.session_engine import PhaseSession, SessionEngine
from ui.celebrations import afficher_celebration_fin_ile, afficher_celebration_legere
from ui.ecran_chat import render_chat
from ui.modal_planche_bd import afficher_modal_planche_bd

_ASSETS_NARRATIF = Path(__file__).parent.parent / "assets" / "narratif"

# Registre du contenu pédagogique par île (D-T8.5-H). Les îles 2 et 3 n'ont
# pas encore de module de contenu produit — importlib lève ModuleNotFoundError,
# géré explicitement dans _charger_contenu_session().
_CONTENU_REGISTRY: dict[str, str] = {
    "ile_1": "pedagogie.contenu_ile1",
    "ile_2": "pedagogie.contenu_ile2",
    "ile_3": "pedagogie.contenu_ile3",
}


@st.cache_data(show_spinner=False)
def _charger_image(chemin: str) -> bytes | None:
    """Charge une image en bytes. Retourne None si le fichier est absent."""
    p = Path(chemin)
    if p.exists():
        return p.read_bytes()
    return None


@st.cache_data(show_spinner=False)
def _charger_contenu_session(ile_id: str, session_num: int) -> tuple[dict, list] | None:
    """
    Retourne (métadonnées, exercices) de la Session `session_num` de l'île demandée.
    Retourne None si l'île n'a pas encore de contenu pédagogique produit, ou si
    la session demandée n'existe pas (île terminée / hors bornes) — l'appelant
    doit afficher un message clair plutôt que de laisser planter l'app (D-T8.5-H).
    """
    module_path = _CONTENU_REGISTRY.get(ile_id)
    if module_path is None:
        return None
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return None
    meta = getattr(module, f"META_SESSION_{session_num}", None)
    exercices = getattr(module, f"SESSION_{session_num}", None)
    if meta is None or exercices is None:
        return None
    return meta, exercices


def _afficher_bandeau(genre: str) -> None:
    chemin = _ASSETS_NARRATIF / "globaux" / f"ecran_session_{genre}.png"
    img = _charger_image(str(chemin))
    if img:
        st.image(img, use_container_width=True)


def _init_engine(
    exercices: list, situation_narrative: str, ile_id: str, planche_key: str
) -> SessionEngine:
    """Crée un SessionEngine neuf et génère le message d'ouverture d'Archimède."""
    joueur = charger_joueur_courant()
    prenom = (joueur.get("prenom") if joueur else None) or "Élévateur"
    engine = SessionEngine(
        exercices=exercices,
        prenom=prenom,
        situation_narrative=situation_narrative,
        ile_id=ile_id,
        planche_key=planche_key,
    )
    with st.spinner("Archimède arrive…"):
        engine.debut_session()
    st.session_state.session_active = engine.to_dict()
    return engine


def _kickoff_exercice_suivant(engine: SessionEngine) -> None:
    """Envoie un kickoff interne pour ouvrir le nouvel exercice après avance.

    engine.repondre() ajoute les deux entrées (user + assistant) à l'historique.
    On supprime ensuite le message interne côté user pour que l'affichage reste propre.
    """
    _KICKOFF_SUIVANT = (
        "[EXERCICE SUIVANT — message interne] "
        "L'enfant passe à l'exercice suivant. "
        "Présente-lui brièvement la nouvelle situation et pose ta première question."
    )
    engine.repondre(_KICKOFF_SUIVANT)
    # Retire uniquement l'entrée user du kickoff — la réponse d'Archimède reste
    engine.historique = [
        m for m in engine.historique
        if not (m["role"] == "user" and m.get("content") == _KICKOFF_SUIVANT)
    ]


def _numero_chapitre(planche_key: str | None) -> int:
    """Retourne le numéro ordinal du chapitre à partir de sa clé."""
    _MAP = {"c1": 1, "c2": 2, "c3": 3, "c4": 4, "c5": 5}
    return _MAP.get(planche_key or "", 1)


def render_session() -> None:
    ile_id = st.session_state.get("ile_courante", "ile_1")
    session_courante = st.session_state.get("session_courante", 1)

    joueur = charger_joueur_courant()
    genre = joueur["avatar_genre"] if joueur else "fille"
    prenom = (joueur.get("prenom") if joueur else None) or "Élévateur"

    # ── Célébration forte de fin d'île (D-T8.6-F) — priorité d'affichage max,
    # rappelée à chaque rerun tant que le flag est actif (pattern planche BD)
    if st.session_state.get("celebration_fin_ile_a_afficher"):
        data = st.session_state["celebration_fin_ile_a_afficher"]
        afficher_celebration_fin_ile(prenom=prenom, nom_ile=data["nom_ile"])
        return
    # ───────────────────────────────────────────────────────────────────────

    contenu = _charger_contenu_session(ile_id, session_courante)
    if contenu is None:
        st.warning(
            f"Le contenu de « {ILE_NOMS.get(ile_id, ile_id)} » n'est pas encore "
            "disponible. Archimède prépare cette île — reviens bientôt !"
        )
        if st.button("← Retour à la carte", key="btn_retour_carte_sans_contenu"):
            st.session_state.ecran_courant = "carte"
            st.rerun()
        return

    meta, exercices = contenu

    # ── Vérification flag modal planche BD ─────────────────────────────────
    if st.session_state.get("planche_bd_a_afficher"):
        afficher_modal_planche_bd(
            ile_id=ile_id,
            planche_key=st.session_state["planche_bd_a_afficher"],
            genre=genre,
            chapitre_num=_numero_chapitre(meta.get("planche_key")),
            chapitres_total=5,
        )
        return
    # ───────────────────────────────────────────────────────────────────────

    # ── Célébration légère (D-T8.6-A/B) — consommée immédiatement (D-T8.6-G)
    if st.session_state.get("celebration_legere_a_afficher"):
        st.session_state.celebration_legere_a_afficher = False
        afficher_celebration_legere(prenom)
    # ───────────────────────────────────────────────────────────────────────

    _afficher_bandeau(genre)

    # En-tête narratif
    st.title(meta["titre"])
    st.info(meta["situation_narrative"])

    st.divider()

    # Initialisation ou restauration du moteur
    if st.session_state.get("session_active") is None:
        engine = _init_engine(
            exercices, meta["situation_narrative"], ile_id, meta.get("planche_key", "")
        )
    else:
        engine = SessionEngine.from_dict(st.session_state.session_active)

    # Indicateur de progression. En phase de clôture on nomme la phase plutôt
    # qu'un numéro d'exercice, pour que l'enfant sente qu'il termine et n'enchaîne
    # pas un exercice de plus. Le passage effectif en Mode.BILAN est déclenché
    # plus bas dans ce même render dès le dernier exercice (D-T8.1-A) — on teste
    # donc aussi est_dernier_exercice pour que le repère ne retarde pas d'un tour.
    if engine.mode == Mode.BILAN or engine.est_dernier_exercice:
        repere = "Bilan"
    else:
        n_total   = len(engine.exercices)
        n_courant = engine.index_exercice + 1
        repere = f"Exercice {n_courant} / {n_total}"
    st.caption(f"{meta['concept']} · {repere}")

    # Zone de chat — modifie engine in-place
    render_chat(engine)

    # Transition automatique vers Mode.BILAN au dernier exercice (D-T8.1-A / D-T8.1-F)
    if engine.est_dernier_exercice and engine.mode != Mode.BILAN and not engine.est_terminee:
        if engine.transitionner(Mode.BILAN):
            # Célébration légère sur ce dernier pas de progression (D-T8.6-A) —
            # affichée au prochain render (flag posé après le point de contrôle
            # de ce rerun-ci, cf. D-T8.6-G)
            st.session_state.celebration_legere_a_afficher = True

    # Persistance après chaque tour de chat
    st.session_state.session_active = engine.to_dict()

    # Contrôles de navigation
    st.divider()
    col_suivant, col_retour = st.columns(2)

    with col_suivant:
        if not engine.est_dernier_exercice and not engine.est_terminee:
            if st.button("Exercice suivant →", key="btn_exercice_suivant", use_container_width=True):
                avance = engine.exercice_suivant()
                if avance:
                    with st.spinner("Archimède prépare le prochain exercice…"):
                        _kickoff_exercice_suivant(engine)
                    st.session_state.session_active = engine.to_dict()
                    st.session_state.celebration_legere_a_afficher = True  # D-T8.6-A
                    st.rerun()

        elif (
            engine.mode == Mode.BILAN
            and engine.nb_tours_bilan >= 1   # gating D-T8.1-F / D24
            and not engine.est_terminee
        ):
            if st.button(
                "Terminer le chapitre ✓",
                key="btn_terminer_chapitre",
                use_container_width=True,
                type="primary",
            ):
                engine.phase = PhaseSession.TERMINEE
                st.session_state.session_active = engine.to_dict()
                planche_key = meta.get("planche_key")
                if planche_key:
                    # Filet de sécurité (D-T8.6-C) : garantit le cristal même
                    # si exercice_suivant() n'a jamais tourné sur le dernier
                    # exercice (pas de bouton "Exercice suivant" au dernier).
                    # Idempotent (T7).
                    recompenses.gagner_cristal(ile_id, planche_key.upper())
                    st.session_state.planche_bd_a_afficher = planche_key
                    st.session_state.planche_bd_index = 0  # reset systématique (D-T8.1-C)
                else:
                    st.session_state.ecran_courant = "ile"
                st.rerun()

    with col_retour:
        # Masqué en Mode BILAN pour forcer le flow BD (D-T8.1-F)
        if engine.mode != Mode.BILAN or engine.est_terminee:
            if st.button("← Retour à l'île", key="btn_retour_ile", use_container_width=True):
                st.session_state.session_active = None
                st.session_state.ecran_courant = "ile"
                st.rerun()
