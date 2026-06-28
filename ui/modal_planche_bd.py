"""
ui/modal_planche_bd.py — Modal full-screen pour l'affichage des planches BD.
Sprint 3 T8.1

Implémentation : st.dialog (Streamlit >= 1.31).
Fallback CSS documenté en commentaire si limitation rencontrée.

Usage dans ecran_session.py :
    from ui.modal_planche_bd import afficher_modal_planche_bd
    afficher_modal_planche_bd(
        ile_id="ile_1",
        planche_key="c1",
        genre="fille",
        chapitre_num=1,
        chapitres_total=5,
    )
"""

from __future__ import annotations

import os

import streamlit as st

from data_layer.planches_bd import marquer_planche_vue

# ------------------------------------------------------------------
# Constantes
# ------------------------------------------------------------------

_ASSETS_NARRATIF = "assets/narratif"
_PLACEHOLDER = f"{_ASSETS_NARRATIF}/_placeholder/placeholder_planche_bd.png"

# Mapping planche_key → liste ordonnée des suffixes de fichiers.
# C1 a deux planches ; les autres n'en ont qu'une.
_SEQUENCE_PLANCHES: dict[str, list[str]] = {
    "c1": ["c1", "c1_part2"],
    "c2": ["c2"],
    "c3": ["c3"],
    "c4": ["c4"],
    "c5": ["c5"],
}


def _chemin_planche(ile_id: str, suffixe: str, genre: str) -> str:
    """Retourne le chemin du fichier planche, ou le placeholder si absent."""
    nom = f"planche_bd_{suffixe}_{genre}.png"
    chemin = os.path.join(_ASSETS_NARRATIF, ile_id, nom)
    if os.path.exists(chemin):
        return chemin
    return _PLACEHOLDER


def afficher_modal_planche_bd(
    ile_id: str,
    planche_key: str,
    genre: str,
    chapitre_num: int,
    chapitres_total: int,
) -> None:
    """
    Affiche le modal full-screen avec la (ou les) planche(s) BD du chapitre.

    Gère la séquence multi-planches (ex. C1 → deux planches).
    Persiste les vues en SQLite après affichage.

    Le modal est déclenché via st.session_state.planche_bd_a_afficher.
    Il se ferme quand l'enfant clique "Continuer la quête".

    Args :
        ile_id          : identifiant de l'île, ex. "ile_1"
        planche_key     : clé du chapitre, ex. "c1"
        genre           : "fille" ou "garcon"
        chapitre_num    : numéro du chapitre courant (pour le texte de positionnement)
        chapitres_total : nombre total de chapitres de l'île (pour le décompte restant)
    """

    sequence = _SEQUENCE_PLANCHES.get(planche_key, [planche_key])
    index_key = "planche_bd_index"

    if index_key not in st.session_state:
        st.session_state[index_key] = 0

    index = st.session_state[index_key]

    # ── Implémentation st.dialog ──────────────────────────────────────────────
    # st.dialog crée un modal natif Streamlit (>= 1.31).
    # Limitation connue : la hauteur est limitée à 90 % du viewport.
    # L'image est affichée avec use_container_width=True pour respecter le ratio.
    #
    # Fallback CSS (si st.dialog pose problème) :
    #   Remplacer le bloc @st.dialog par un overlay CSS via st.markdown :
    #   st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
    #   st.image(chemin, use_container_width=True)
    #   st.markdown('</div>', unsafe_allow_html=True)
    #   Avec un CSS injecté en tête de page via st.markdown(CSS, unsafe_allow_html=True).
    # ─────────────────────────────────────────────────────────────────────────

    @st.dialog("", width="large")
    def _modal() -> None:
        suffixe_courant = sequence[index]
        chemin = _chemin_planche(ile_id, suffixe_courant, genre)

        st.image(chemin, use_container_width=True)

        chapitres_restants = chapitres_total - chapitre_num
        if chapitres_restants > 0:
            texte_pos = (
                f"Île de Syracuse — Chapitre {chapitre_num} validé — "
                f"Encore {chapitres_restants} chapitre(s) avant la clé de l'île"
            )
        else:
            texte_pos = "Île de Syracuse — Tous les chapitres validés — La clé de l'île t'attend !"
        st.caption(texte_pos)

        est_derniere = (index >= len(sequence) - 1)

        if est_derniere:
            if st.button("Continuer la quête →", use_container_width=True, type="primary"):
                for suf in sequence:
                    marquer_planche_vue(ile_id, f"planche_bd_{suf}")
                st.session_state.pop(index_key, None)
                st.session_state.planche_bd_a_afficher = None
                if chapitres_restants == 0:
                    st.session_state.ecran_courant = "carte"
                else:
                    st.session_state.ecran_courant = "session"
                st.rerun()
        else:
            if st.button("Suite →", use_container_width=True):
                st.session_state[index_key] = index + 1
                st.rerun()

    _modal()


# TESTS MANUELS T8.1 — à exécuter manuellement avant commit
#
# Prérequis : joueur créé (passer par ecran_avatar.py), genre connu.
#
# TEST 1 — Planche C1 fille (2 planches en séquence)
#   1. Lancer l'app, choisir avatar fille
#   2. Aller en session Île 1
#   3. Faire tous les exercices, cliquer "Terminer le chapitre ✓"
#   4. Vérifier : modal s'ouvre avec planche_bd_c1_fille.png
#   5. Cliquer "Suite →" → planche_bd_c1_part2_fille.png s'affiche
#   6. Cliquer "Continuer la quête →" → retour à l'écran session
#   7. Vérifier en base : planches_bd_vues contient "ile_1_planche_bd_c1" et "ile_1_planche_bd_c1_part2"
#
# TEST 2 — Planche C2 (placeholder)
#   Forcer dans session_state : st.session_state.planche_bd_a_afficher = "c2"
#   Vérifier : placeholder_planche_bd.png s'affiche sans erreur
#
# TEST 3 — Responsive
#   Redimensionner la fenêtre à ~375px de large
#   Vérifier : image sans déformation, bouton accessible
#
# TEST 4 — Non-régression
#   Lancer l'app en mode normal (pas de session terminée)
#   Vérifier : aucun modal ne s'affiche, boutons "Exercice suivant" et "Retour à l'île" intacts
#
# TEST 5 — Revue d'une planche déjà vue
#   Rejouer la session C1 après l'avoir terminée
#   Terminer à nouveau → modal s'affiche (planche revue)
#   Vérifier en base : timestamp de "ile_1_planche_bd_c1" mis à jour
