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

Règle de rendu des modals (célébration de fin d'île, coffre, planche BD) :
un st.dialog fermé à la croix ou par Échap ne déclenche AUCUN rerun
(on_dismiss="ignore" par défaut). Un écran qui se contente d'ouvrir un modal
puis de `return` n'a donc plus rien à montrer si l'enfant le referme : c'est la
page vide observée entre deux chapitres. Chaque modal du flux est donc rendu
non dismissible ET doublé d'un repli visible derrière lui, qui emprunte la même
sortie que son bouton (ui/flux_chapitre.py).
"""

from __future__ import annotations

import importlib
from pathlib import Path

import streamlit as st

from config.constants import ILE_NOMS
from data_layer.joueurs import charger_joueur_courant
from jeu import recompenses
from jeu.collection import libelle_objet, nom_coffre, objet_de_session
from pedagogie.modes import Mode
from pedagogie.session_engine import PhaseSession, SessionEngine
from ui.celebrations import (
    afficher_celebration_fin_ile,
    afficher_celebration_legere,
    afficher_coffre_session,
)
from ui import flux_chapitre
from ui.tableau_bord import render_tableau_bord
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


_KICKOFF_SUIVANT = (
    "[EXERCICE SUIVANT — message interne] "
    "L'enfant passe à l'exercice suivant. "
    "Présente-lui brièvement la nouvelle situation et pose ta première question."
)

_KICKOFF_BILAN = (
    "[BILAN — message interne] "
    "L'enfant vient de terminer le dernier exercice du chapitre. "
    "Ouvre le bilan : félicite-le brièvement, puis fais-lui formuler LUI-MÊME "
    "ce qu'il a compris, par une question. Ne récapitule pas à sa place."
)


def _kickoff_interne(engine: SessionEngine, message: str) -> None:
    """Envoie un message interne au mentor pour ouvrir une nouvelle étape.

    engine.repondre() ajoute les deux entrées (user + assistant) à l'historique.
    On supprime ensuite le message interne côté user pour que l'affichage reste propre.
    """
    engine.repondre(message)
    # Retire uniquement l'entrée user du kickoff — la réponse d'Archimède reste
    engine.historique = [
        m for m in engine.historique
        if not (m["role"] == "user" and m.get("content") == message)
    ]


def _kickoff_exercice_suivant(engine: SessionEngine) -> None:
    """Ouvre le nouvel exercice après avance."""
    _kickoff_interne(engine, _KICKOFF_SUIVANT)


def _kickoff_bilan(engine: SessionEngine) -> None:
    """Ouvre le bilan quand l'enfant déclare avoir fini le dernier exercice.

    Le compteur de tours de bilan est remis à zéro juste après : engine.repondre()
    l'incrémente (echanger_en_bilan), or ce kickoff est un message interne, pas un
    échange de l'enfant. Sans ce reset, « Terminer le chapitre » serait déverrouillé
    sans qu'un seul mot ait été dit en bilan — le gating D-T8.1-F / D24 tomberait.
    """
    _kickoff_interne(engine, _KICKOFF_BILAN)
    engine.nb_tours_bilan = 0


def _repli_modal(message: str, libelle: str, cle: str, action) -> None:
    """Contenu de secours affiché DERRIÈRE un modal du flux.

    Son libellé diffère volontairement de celui du bouton du modal : les deux
    ne doivent jamais être confondus, à l'écran comme dans les tests.

    Les modals du flux sont non dismissible, donc ce repli n'est normalement
    jamais utilisé. Il existe pour qu'un modal qui ne s'ouvrirait pas (asset
    manquant, version de Streamlit différente, dismissal ignoré) ne laisse pas
    l'enfant devant une page sans rien — il emprunte exactement la même sortie
    que le bouton du modal, donc aucun état intermédiaire n'est possible.
    """
    st.caption(message)
    if st.button(libelle, key=cle, use_container_width=True):
        action()
        st.rerun()


def _sortir_de_la_celebration_fin_ile() -> None:
    """Referme la célébration de fin d'île et rend la main à l'archipel."""
    st.session_state.celebration_fin_ile_a_afficher = None
    st.session_state.ecran_courant = "carte"


def render_session() -> None:
    ile_id = st.session_state.get("ile_courante", "ile_1")
    session_courante = st.session_state.get("session_courante", 1)

    joueur = charger_joueur_courant()
    genre = joueur["avatar_genre"] if joueur else "fille"
    prenom = (joueur.get("prenom") if joueur else None) or "Élévateur"

    # Tableau de bord : rendu avant les sorties anticipées (célébrations, modals)
    # pour rester visible quel que soit le chemin pris par ce render.
    render_tableau_bord()

    # ── Célébration forte de fin d'île (D-T8.6-F) — priorité d'affichage max,
    # rappelée à chaque rerun tant que le flag est actif (pattern planche BD)
    if st.session_state.get("celebration_fin_ile_a_afficher"):
        data = st.session_state["celebration_fin_ile_a_afficher"]
        afficher_celebration_fin_ile(prenom=prenom, nom_ile=data["nom_ile"])
        _repli_modal(
            "L'île est remontée.",
            "Revenir à l'archipel →",
            "btn_repli_fin_ile",
            _sortir_de_la_celebration_fin_ile,
        )
        return
    # ───────────────────────────────────────────────────────────────────────

    # ── Fin de chapitre : coffre puis planche BD (ui/flux_chapitre.py) ──────
    # Ces deux étapes passent AVANT le chargement du contenu : elles racontent
    # le chapitre qu'on vient de finir, pas celui qui vient. Les lier à la
    # session courante — qui a pu avancer entre-temps — décalait le numéro de
    # chapitre affiché, et une session courante hors bornes faisait carrément
    # disparaître la planche derrière l'avertissement « contenu indisponible ».
    etape = flux_chapitre.etape_en_cours()

    if etape == "coffre":
        afficher_coffre_session(
            prenom=prenom,
            nom_coffre=flux_chapitre.nom_coffre_affiche(),
            tally_objets=flux_chapitre.tally_coffre_affiche(),
        )
        _repli_modal(
            "Ton coffre t'attend.",
            "Poursuivre →",
            "btn_repli_coffre",
            flux_chapitre.fermer_coffre,
        )
        return

    if etape == "planche":
        afficher_modal_planche_bd(
            ile_id=ile_id,
            planche_key=flux_chapitre.planche_affichee(),
            genre=genre,
            chapitre_num=flux_chapitre.chapitre_affiche(),
            chapitres_total=flux_chapitre.nb_chapitres(ile_id),
        )
        _repli_modal(
            "Ta quête continue.",
            "Poursuivre la quête →",
            "btn_repli_planche",
            lambda: flux_chapitre.sortir_de_la_planche(ile_id),
        )
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

    # ── Célébration légère (D-T8.6-A/B) — consommée immédiatement (D-T8.6-G)
    if st.session_state.get("celebration_legere_a_afficher"):
        st.session_state.celebration_legere_a_afficher = False
        afficher_celebration_legere(prenom)
    # ───────────────────────────────────────────────────────────────────────

    # ── Toast « +1 pierre ! » du dernier objet encaissé — consommé immédiatement,
    # même garde anti-rejeu que la célébration légère (D-T8.6-G). Pas de son,
    # pas d'animation : le toast est le « ding » minimal.
    if st.session_state.get("objet_gagne_a_afficher"):
        slug = st.session_state["objet_gagne_a_afficher"]
        st.session_state.objet_gagne_a_afficher = None
        st.toast(f"+{libelle_objet(slug, 1)} !")
    # ───────────────────────────────────────────────────────────────────────

    _afficher_bandeau(genre)

    # En-tête narratif
    st.title(meta["titre"])
    st.info(meta["situation_narrative"])

    st.divider()

    # Initialisation ou restauration du moteur
    if st.session_state.get("session_active") is None:
        try:
            engine = _init_engine(
                exercices, meta["situation_narrative"], ile_id, meta.get("planche_key", "")
            )
        except Exception as exc:  # noqa: BLE001
            # L'ouverture d'une session passe par le mentor, donc par le réseau.
            # Un échec ici arrive juste après la planche BD, au moment le plus
            # fragile du parcours : l'enfant doit voir un écran qui lui parle et
            # un moyen de repartir, jamais une trace d'exception ni une page nue.
            st.warning(
                "Archimède n'a pas réussi à ouvrir ce chapitre. "
                "Ce n'est pas ta faute — réessaie dans un instant."
            )
            col_reessayer, col_ile = st.columns(2)
            with col_reessayer:
                if st.button("Réessayer", key="btn_reessayer_ouverture", type="primary",
                             use_container_width=True):
                    st.rerun()
            with col_ile:
                if st.button("← Retour à l'île", key="btn_retour_ile_echec_init",
                             use_container_width=True):
                    st.session_state.ecran_courant = "ile"
                    st.rerun()
            with st.expander("Détail technique"):
                st.exception(exc)
            return
    else:
        engine = SessionEngine.from_dict(st.session_state.session_active)

    # Indicateur de progression. En phase de clôture on nomme la phase plutôt
    # qu'un numéro d'exercice, pour que l'enfant sente qu'il termine et n'enchaîne
    # pas un exercice de plus. Le bilan ne s'ouvre plus tout seul à l'arrivée sur
    # le dernier exercice : tant que l'enfant y travaille, le repère doit dire
    # « Exercice N / N », pas « Bilan ».
    if engine.mode == Mode.BILAN:
        repere = "Bilan"
    else:
        n_total   = len(engine.exercices)
        n_courant = engine.index_exercice + 1
        repere = f"Exercice {n_courant} / {n_total}"
    st.caption(f"{meta['concept']} · {repere}")

    # Le compteur d'objets n'est plus rendu ici : il vit dans le tableau de bord,
    # qui ne disparaît pas au scroll (retour de test réel). L'objet de la session
    # reste lu ici pour armer les toasts de gain.
    objet_session = objet_de_session(ile_id, meta.get("planche_key", ""))

    # Zone de chat — modifie engine in-place
    render_chat(engine)

    # Le passage en Mode.BILAN n'est plus automatique (D-T8.1-A révisé). Il se
    # déclenchait à l'ARRIVÉE sur le dernier exercice, donc pendant que l'enfant
    # le travaillait encore : « Terminer le chapitre » s'affichait au milieu du
    # dialogue, et le bilan se superposait à l'exercice. C'est désormais l'enfant
    # qui déclare avoir fini, avec le bouton « J'ai terminé cet exercice → ».

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
                    # Un objet est encaissé à chaque passage d'exercice (option b)
                    if objet_session:
                        st.session_state.objet_gagne_a_afficher = objet_session["objet"]
                    st.rerun()

        elif (
            engine.est_dernier_exercice
            and engine.mode != Mode.BILAN
            and not engine.est_terminee
        ):
            # Pendant du « Exercice suivant → » pour le dernier exercice, qui n'a
            # pas de suivant : le clic ouvre le bilan et encaisse le dernier objet
            # (cf. SessionEngine.objets_gagnes, qui compte le passage en BILAN).
            if st.button(
                "J'ai terminé cet exercice →",
                key="btn_dernier_exercice_termine",
                use_container_width=True,
            ):
                if engine.transitionner(Mode.BILAN):
                    with st.spinner("Archimède prépare le bilan…"):
                        _kickoff_bilan(engine)
                    st.session_state.session_active = engine.to_dict()
                    st.session_state.celebration_legere_a_afficher = True  # D-T8.6-A
                    if objet_session:
                        st.session_state.objet_gagne_a_afficher = objet_session["objet"]
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
                    # Coffre plein (habillage du cristal qu'on vient de gagner,
                    # aucune récompense supplémentaire) puis planche BD : le flux
                    # est armé d'un bloc, avec le chapitre de CETTE session.
                    flux_chapitre.armer_fin_de_chapitre(
                        planche_key=planche_key,
                        nom_coffre=nom_coffre(meta),
                        tally=(
                            libelle_objet(objet_session["objet"], engine.objets_gagnes)
                            if objet_session else ""
                        ),
                    )
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
