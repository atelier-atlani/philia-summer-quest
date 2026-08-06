"""
ui/flux_chapitre.py — Le flux de fin de chapitre : coffre → planche BD → suite.

POURQUOI CE MODULE (racine du bug de page vide)
Les flags de ce flux (coffre_session_a_afficher, coffre_session_tally,
planche_bd_a_afficher, planche_bd_index) étaient posés dans ui/ecran_session.py
et effacés dans ui/modal_planche_bd.py, chacun avec sa propre idée de l'étape
en cours et du chapitre concerné. Deux propriétaires pour un même état, c'est
la porte ouverte aux combinaisons intermédiaires qui ne correspondent à aucun
écran affichable — l'enfant se retrouvait devant une page vide entre deux
chapitres.

Ici, un seul endroit les pose (armer_fin_de_chapitre), un seul les lit
(etape_en_cours, chapitre_affiche) et un seul les efface en routant vers un
écran qui a du contenu (fermer_coffre, sortir_de_la_planche). Les écrans ne
manipulent plus ces clés directement.

Le numéro de chapitre est celui de la PLANCHE affichée, jamais celui de la
session courante recalculée : quand l'enfant referme la planche du chapitre 1,
la progression a pu déjà avancer à la session 2, et lire le chapitre depuis la
session courante décalait tout d'un cran (mauvais décompte « encore N
chapitres », mauvaise détection de la fin d'île).

Public API :
    PLANCHES_PAR_CHAPITRE                     -> dict[str, list[str]]
    nb_chapitres(ile_id)                      -> int
    numero_chapitre(planche_key)              -> int
    armer_fin_de_chapitre(...)                -> None
    etape_en_cours()                          -> str | None   ("coffre"|"planche")
    chapitre_affiche()                        -> int
    planche_affichee()                        -> str
    fermer_coffre()                           -> None
    sortir_de_la_planche(ile_id)              -> None
"""

from __future__ import annotations

import streamlit as st

from config.constants import ILE_NOMS
from data_layer.planches_bd import marquer_planche_vue
from jeu import recompenses

# Mapping planche_key → séquence de suffixes de fichier (D-T8.1-C / D23).
# Vit ici et non dans le modal : la sortie du flux doit marquer « vues » les
# mêmes planches que celles qui ont été montrées, sans dépendre de l'écran.
PLANCHES_PAR_CHAPITRE: dict[str, list[str]] = {
    "c1": ["c1", "c1_part2"],
    "c2": ["c2_part1", "c2_part2"],
    "c3": ["c3"],
    "c4": ["c4_part1", "c4_part2"],
    "c5": ["c5_part1", "c5_part2"],
}

# Clés de session_state pilotées par ce module — et par lui seul.
_CLE_COFFRE = "coffre_session_a_afficher"
_CLE_TALLY = "coffre_session_tally"
_CLE_PLANCHE = "planche_bd_a_afficher"
_CLE_PLANCHE_INDEX = "planche_bd_index"
_CLE_CHAPITRE = "planche_bd_chapitre"


# ── Lecture ───────────────────────────────────────────────────────────────────

def nb_chapitres(ile_id: str) -> int:
    """Nombre de chapitres d'une île — dérivé de ses concepts, comme la
    progression (jeu/recompenses.py). Aucune constante « 5 » recopiée."""
    return len(recompenses.concepts_ile(ile_id))


def numero_chapitre(planche_key: str | None) -> int:
    """Numéro ordinal du chapitre à partir de sa clé ("c3" → 3). 1 par défaut."""
    cle = (planche_key or "").strip().lower()
    if cle.startswith("c") and cle[1:].isdigit():
        return int(cle[1:])
    return 1


def etape_en_cours() -> str | None:
    """Étape du flux de fin de chapitre à rendre : "coffre", "planche" ou None.

    Le coffre passe avant la planche : l'enfant voit sa récompense, puis la
    suite de l'histoire. Ordre unique, décidé ici plutôt que par la succession
    des `if` d'un écran.
    """
    if st.session_state.get(_CLE_COFFRE):
        return "coffre"
    if st.session_state.get(_CLE_PLANCHE):
        return "planche"
    return None


def modal_du_flux_ouvert() -> bool:
    """Vrai si un modal du récit doit s'ouvrir à ce render (coffre, planche BD,
    célébration de fin d'île).

    Streamlit n'autorise qu'UN dialog par script run : un second appel lève
    StreamlitAPIException et l'enfant reçoit un écran d'erreur au milieu de son
    chapitre. Les pop-ups d'agrément (vue de l'île en sidebar) doivent donc
    céder le passage — c'est le récit qui a la priorité.
    """
    return (
        bool(st.session_state.get("celebration_fin_ile_a_afficher"))
        or etape_en_cours() is not None
    )


def planche_affichee() -> str:
    """Clé de la planche en cours d'affichage ("c1"), vide si aucune."""
    return st.session_state.get(_CLE_PLANCHE) or ""


def chapitre_affiche() -> int:
    """Numéro du chapitre de la planche affichée — jamais celui de la session
    courante, qui a pu avancer entre-temps."""
    memorise = st.session_state.get(_CLE_CHAPITRE)
    if isinstance(memorise, int) and memorise > 0:
        return memorise
    return numero_chapitre(planche_affichee())


def nom_coffre_affiche() -> str:
    return st.session_state.get(_CLE_COFFRE) or ""


def tally_coffre_affiche() -> str:
    return st.session_state.get(_CLE_TALLY) or ""


# ── Écriture ──────────────────────────────────────────────────────────────────

def armer_fin_de_chapitre(planche_key: str, nom_coffre: str, tally: str) -> None:
    """Arme le flux complet en une fois, à la validation d'un chapitre.

    Les quatre clés sont posées ensemble : il n'existe pas d'instant où le
    coffre est armé sans sa planche, ou la planche sans son numéro de chapitre.
    """
    st.session_state[_CLE_COFFRE] = nom_coffre
    st.session_state[_CLE_TALLY] = tally
    st.session_state[_CLE_PLANCHE] = planche_key
    st.session_state[_CLE_PLANCHE_INDEX] = 0  # reset systématique (D-T8.1-C)
    st.session_state[_CLE_CHAPITRE] = numero_chapitre(planche_key)


def fermer_coffre() -> None:
    """Le coffre est vu : la planche BD (déjà armée) prend le relais au rerun."""
    st.session_state[_CLE_COFFRE] = None
    st.session_state[_CLE_TALLY] = ""


def _effacer_flags() -> None:
    """Aucun flag du flux ne survit à la sortie — y compris ceux d'une étape
    précédente qu'un chemin inhabituel aurait laissés posés."""
    st.session_state[_CLE_COFFRE] = None
    st.session_state[_CLE_TALLY] = ""
    st.session_state[_CLE_PLANCHE] = None
    st.session_state[_CLE_CHAPITRE] = None
    st.session_state.pop(_CLE_PLANCHE_INDEX, None)


def armer_fin_d_ile(ile_id: str) -> None:
    """Fin d'île (D-T8.6-D) : clé — idempotente (T7) — puis célébration forte
    (D-T8.6-F), qui propose l'énigme finale ou le retour à l'archipel.

    Deux chemins y mènent : la dernière planche BD, et un retour sur une île
    déjà terminée (ui/ecran_ile.py). Les deux passent par ici, pour que le flag
    de célébration n'ait qu'un seul endroit où être posé.
    """
    recompenses.gagner_cle(ile_id)
    st.session_state.session_active = None
    st.session_state.celebration_fin_ile_a_afficher = {
        "nom_ile": ILE_NOMS.get(ile_id, ile_id)
    }
    st.session_state.ecran_courant = "session"


def sortir_de_la_planche(ile_id: str) -> None:
    """SEULE sortie du flux de fin de chapitre.

    Marque les planches vues, efface tous les flags, puis route — toujours vers
    un écran qui a du contenu à rendre :
      - dernier chapitre → clé de l'île (idempotente) + célébration forte ;
      - sinon → session suivante, dérivée des coffres (jeu/recompenses.py),
        avec un moteur neuf.

    Appelée par le bouton du modal comme par le repli affiché derrière lui :
    quel que soit le geste de l'enfant, la même sortie s'exécute.
    """
    planche_key = planche_affichee()
    chapitre = chapitre_affiche()

    for suffixe in PLANCHES_PAR_CHAPITRE.get(planche_key, [planche_key] if planche_key else []):
        marquer_planche_vue(ile_id, suffixe)

    _effacer_flags()
    # Moteur neuf dans tous les cas : celui du chapitre qu'on vient de finir est
    # terminé, le laisser en place ferait rouvrir son dialogue.
    st.session_state.session_active = None

    if chapitre >= nb_chapitres(ile_id):
        armer_fin_d_ile(ile_id)
    else:
        # Progression inter-sessions (D-T8.6-E) : la session suivante se dérive
        # des coffres ; repli sur le chapitre suivant si la dérivation n'a plus
        # rien à proposer (chapitre rejoué).
        st.session_state.session_courante = (
            recompenses.session_courante(ile_id) or chapitre + 1
        )

    st.session_state.ecran_courant = "session"
