"""
ui/modal_planche_bd.py — Modal full-screen pour l'affichage des planches BD.
Sprint 3 T8.1

Implémentation : st.dialog (Streamlit >= 1.31).
Fallback CSS documenté en commentaire si limitation rencontrée.

Cet écran est une vitre : il montre des planches et rend la main. Ce qu'il faut
marquer en base, quels flags effacer et où aller ensuite appartiennent au flux
de fin de chapitre (ui/flux_chapitre.py) — un seul propriétaire pour cet état.

Le modal n'est PAS dismissible : c'est un point de passage du récit, et une
fenêtre fermée à la croix ne déclenche aucun rerun côté Streamlit
(on_dismiss="ignore" par défaut) — l'enfant restait alors devant une page vide.
L'appelant affiche en plus un repli derrière le modal (ceinture et bretelles).

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

from ui import flux_chapitre

# ------------------------------------------------------------------
# Constantes
# ------------------------------------------------------------------

_ASSETS_NARRATIF = "assets/narratif"
_PLACEHOLDER = f"{_ASSETS_NARRATIF}/_placeholder/placeholder_planche_bd.png"


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
    Affiche le modal avec la (ou les) planche(s) BD du chapitre.
    planche_bd_index est resetté à 0 à l'armement du flux
    (flux_chapitre.armer_fin_de_chapitre) et borné ici par sécurité.

    Args :
        ile_id          : identifiant de l'île, ex. "ile_1"
        planche_key     : clé du chapitre, ex. "c1"
        genre           : "fille" ou "garcon"
        chapitre_num    : numéro du chapitre courant
        chapitres_total : nombre total de chapitres de l'île

    # Fallback CSS si st.dialog pose problème :
    #   Remplacer @st.dialog par st.markdown avec overlay CSS + st.image.
    """
    # ── Implémentation st.dialog ──────────────────────────────────────────────
    # st.dialog crée un modal natif Streamlit (>= 1.31).
    # Limitation connue : hauteur 90 % du viewport.
    # use_container_width=True préserve le ratio image.
    #
    # Fallback CSS (si st.dialog pose problème) :
    #   Remplacer le bloc @st.dialog par un overlay CSS via st.markdown :
    #   st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
    #   st.image(chemin, use_container_width=True)
    #   st.markdown('</div>', unsafe_allow_html=True)
    # ─────────────────────────────────────────────────────────────────────────

    sequence = flux_chapitre.PLANCHES_PAR_CHAPITRE.get(planche_key, [planche_key])
    index_key = "planche_bd_index"
    if index_key not in st.session_state:
        st.session_state[index_key] = 0
    # Une séquence raccourcie (ou un index resté d'un chapitre précédent) ne doit
    # pas lever IndexError au milieu du récit : on borne au lieu de casser.
    index = min(max(st.session_state[index_key], 0), len(sequence) - 1)

    @st.dialog("Ta quête continue", width="large", dismissible=False)
    def _modal() -> None:
        chemin = _chemin_planche(ile_id, sequence[index], genre)
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

        if index >= len(sequence) - 1:
            if st.button("Continuer la quête →", use_container_width=True, type="primary"):
                # Marquage des planches vues — clé = f"{ile_id}_{suf}", pas de
                # préfixe "planche_bd_" (D-T8.1-D) — puis sortie unique : c'est
                # elle qui efface les flags et route (ui/flux_chapitre.py).
                flux_chapitre.sortir_de_la_planche(ile_id)
                st.rerun()
        else:
            if st.button("Suite →", use_container_width=True):
                st.session_state[index_key] = index + 1
                st.rerun()

    _modal()


# TESTS MANUELS T8.1 — à exécuter manuellement avant commit
#
# Prérequis : joueur créé (ecran_avatar.py), genre connu.
#
# TEST 1 — Planche C1 fille (2 planches en séquence)
#   1. Lancer l'app, choisir avatar fille
#   2. Session Île 1, faire tous les exercices
#   3. Valider le dernier exercice → Archimède passe en Mode BILAN automatiquement
#   4. Vérifier : bouton "Terminer le chapitre ✓" N'EST PAS visible
#   5. Échanger 1 message avec Archimède en Mode BILAN
#   6. Vérifier : bouton "Terminer le chapitre ✓" apparaît
#   7. Cliquer → modal s'ouvre avec planche_bd_c1_fille.png
#   8. Cliquer "Suite →" → planche_bd_c1_part2_fille.png
#   9. Cliquer "Continuer la quête →" → retour à l'écran session
#   10. Vérifier en base SQLite : planches_bd_vues contient
#       "ile_1_c1" ET "ile_1_c1_part2" (PAS "ile_1_planche_bd_c1")
#
# TEST 2 — Planche C2 (placeholder)
#   Forcer : st.session_state.planche_bd_a_afficher = "c2"
#   Vérifier : placeholder_planche_bd.png s'affiche sans erreur
#
# TEST 3 — Responsive
#   Fenêtre ~375px de large
#   Vérifier : image sans déformation, bouton accessible
#
# TEST 4 — Non-régression
#   Session normale (pas sur le dernier exercice)
#   Vérifier : aucun modal, boutons normaux intacts
#
# TEST 5 — Revue d'une planche déjà vue
#   Rejouer C1, terminer à nouveau
#   Vérifier en base : timestamp "ile_1_c1" mis à jour (pas dupliqué)
#
# TEST 6 — Gating bouton (D-T8.1-F / D24)
#   1. Atteindre le dernier exercice
#   2. Valider → Archimède passe en Mode BILAN automatiquement
#   3. Vérifier : bouton "Terminer le chapitre ✓" N'EST PAS visible
#   4. Échanger 1 message en Mode BILAN
#   5. Vérifier : engine.nb_tours_bilan == 1
#   6. Vérifier : bouton "Terminer le chapitre ✓" apparaît
#   7. Cliquer → modal planche BD s'ouvre
