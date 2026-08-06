"""
ui/ecran_presentation_archipel.py — Écran de présentation de l'archipel.
Sprint 3 T8.5 (D-T8.5-E)

Affiché une seule fois, entre la confirmation de l'avatar (ui/ecran_avatar.py)
et l'arrivée sur la carte interactive. Affiche
`globaux/presentation_archipel_<genre>.png` avec un texte de transition
d'Archimède qui présente l'archipel avant que l'enfant ne voie la carte.

C'est le SEUL écran d'annonce de l'archipel : l'étape "bienvenue" de
ecran_avatar.py, qui disait la même chose juste avant, a été retirée et son
mot d'accueil personnalisé est repris ici.

Point d'entrée public : afficher_ecran_presentation_archipel()
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from data_layer.joueurs import charger_joueur_courant

_ASSETS_NARRATIF = Path(__file__).parent.parent / "assets" / "narratif" / "globaux"

_TEXTE_PRESENTATION = """\
Bienvenue à bord, {prenom}.

Voici l'Archipel de la Raison. Sept îles, autrefois reliées par des
ponts de cristal, aujourd'hui silencieuses. Chacune garde une Loi
Fondamentale, scellée depuis le cataclysme.

La première t'appelle déjà : l'Île des Nombres Brisés.

Choisis une île sur la carte. C'est là que ton voyage commence."""

# Le fondu qui accompagnait le mot de bienvenue est conservé : c'est le même
# moment du parcours, il ne change que d'écran.
_CSS_FADE = """
<style>
.philia-archipel {
    opacity: 0;
    animation: philia-fade-up 1s ease 0.3s forwards;
}
@keyframes philia-fade-up {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0);    }
}
</style>
"""


# ── Helpers image ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _charger_image(chemin: str) -> bytes | None:
    """Charge une image en bytes. Retourne None si le fichier est absent."""
    p = Path(chemin)
    if p.exists():
        return p.read_bytes()
    return None


# ── Point d'entrée public ─────────────────────────────────────────────────────

def afficher_ecran_presentation_archipel() -> None:
    joueur = charger_joueur_courant()
    genre = joueur["avatar_genre"] if joueur else "fille"
    prenom = (joueur.get("prenom") if joueur else None) or "Élévateur"

    chemin_img = _ASSETS_NARRATIF / f"presentation_archipel_{genre}.png"
    img = _charger_image(str(chemin_img))

    st.markdown(_CSS_FADE, unsafe_allow_html=True)

    # Même disposition que les écrans d'île (ui/ecran_ile.py) : l'illustration
    # en grand au-dessus, le texte dessous. Les colonnes latérales ne portent
    # rien — ce sont des marges, sans quoi l'image s'étale sur toute la page en
    # layout « wide » et repousse le bouton hors de l'écran.
    _, centre, _ = st.columns([1, 5, 1])

    with centre:
        if img:
            st.image(img, use_container_width=True)
        else:
            st.markdown("🗺️")  # fallback si image absente

        texte = _TEXTE_PRESENTATION.format(prenom=prenom)
        lignes = texte.strip().split("\n\n")
        html = "\n".join(
            f'<p style="margin-bottom:1em;">{p.replace(chr(10), "<br>")}</p>'
            for p in lignes
        )
        st.markdown(
            f'<div class="philia-archipel" style="font-size:1.05rem;line-height:1.8;">'
            f'{html}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗺️ Ouvrir la carte de l'archipel", key="btn_decouvrir_archipel", type="primary"):
            st.session_state["ecran_courant"] = "carte"
            st.rerun()
