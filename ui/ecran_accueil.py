"""
ui/ecran_accueil.py — Écran d'Accueil narratif + saisie du prénom.
Sprint 3 T8.5 (D-T8.5-D)

Premier écran du parcours (avant tout choix d'avatar) : discours d'ouverture
d'Archimède, image `globaux/accueil_invitation.png`, champ de saisie du
prénom réel de l'enfant (D19bis). Le bouton « Lever l'ancre » est désactivé
tant qu'aucun prénom n'est saisi.

Le prénom saisi est stocké dans st.session_state["prenom_saisi"] — lu par
ui/ecran_avatar.py au moment de la création du joueur (étape confirmation).

Point d'entrée public : afficher_ecran_accueil()
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

_ASSETS_NARRATIF = Path(__file__).parent.parent / "assets" / "narratif" / "globaux"
_IMG_ACCUEIL = _ASSETS_NARRATIF / "accueil_invitation.png"

# ── Texte narratif (déplacé depuis ui/ecran_avatar.py, D-T8.5-A) ──────────────

_TEXTE_ACCUEIL = """\
Approche, jeune élévateur.

Il y a très longtemps, l'Archipel des Sept Îles a sombré.
Chacune garde aujourd'hui une Loi oubliée, scellée par
une épreuve.

Sept îles. Sept lois. Sept épreuves.

Pour chaque île que tu réveilleras, tu gagneras une clé.
Et au bout du voyage, quand les sept clés seront entre
tes mains, j'ouvrirai pour toi le coffre de mon secret
le plus précieux — celui que j'ai découvert dans un bain,
il y a plus de deux mille ans.

Mais sache ceci : on n'élève pas une île en récitant.
On l'élève en comprenant.

Comment dois-je t'appeler ?"""

# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS_FADE_IN = """
<style>
.philia-accueil-ligne {
    opacity: 0;
    animation: philia-fade-up 0.7s ease forwards;
}
.philia-accueil-ligne:nth-child(1)  { animation-delay: 0.0s; }
.philia-accueil-ligne:nth-child(2)  { animation-delay: 0.8s; }
.philia-accueil-ligne:nth-child(3)  { animation-delay: 1.6s; }
.philia-accueil-ligne:nth-child(4)  { animation-delay: 2.4s; }
.philia-accueil-ligne:nth-child(5)  { animation-delay: 3.2s; }
.philia-accueil-ligne:nth-child(6)  { animation-delay: 4.0s; }
.philia-accueil-ligne:nth-child(7)  { animation-delay: 4.8s; }
.philia-accueil-ligne:nth-child(8)  { animation-delay: 5.6s; }
.philia-accueil-ligne:nth-child(9)  { animation-delay: 6.4s; }
.philia-accueil-ligne:nth-child(10) { animation-delay: 7.2s; }

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

def afficher_ecran_accueil() -> None:
    st.markdown(_CSS_FADE_IN, unsafe_allow_html=True)

    col_img, col_txt = st.columns([1, 2], gap="large")

    with col_img:
        img = _charger_image(str(_IMG_ACCUEIL))
        if img:
            st.image(img, use_container_width=True)
        else:
            st.markdown("🏺")  # fallback si image absente

    with col_txt:
        paragraphes = [p.strip() for p in _TEXTE_ACCUEIL.split("\n\n") if p.strip()]
        lignes_html = "\n".join(
            f'<p class="philia-accueil-ligne">{p.replace(chr(10), "<br>")}</p>'
            for p in paragraphes
        )
        st.markdown(
            f'<div style="font-size:1.05rem;line-height:1.8;">{lignes_html}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        prenom = st.text_input(
            "Ton prénom",
            key="prenom_saisi_input",
            placeholder="Écris ton prénom ici…",
            label_visibility="collapsed",
        )
        prenom_valide = bool(prenom and prenom.strip())

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "⚓ Lever l'ancre",
            key="btn_lever_ancre",
            type="primary",
            disabled=not prenom_valide,
        ):
            st.session_state["prenom_saisi"] = prenom.strip()
            st.session_state["ecran_courant"] = "avatar"
            st.rerun()
