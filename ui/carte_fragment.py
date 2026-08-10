"""
ui/carte_fragment.py — Gabarit de carte à collectionner (« carte-fragment »).

Trophée de fin d'île : une carte rare, remise à l'enfant quand il a terminé
l'énigme finale d'une île. AUCUNE mécanique de jeu — c'est un objet de
collection, pas une carte à jouer. Le gabarit ne fait qu'afficher.

Deux faces, un même cadre (_cadre) :
  - RECTO — le trophée : illustration, nom, rareté, île, clé, collection, notion.
  - VERSO — la fiche mémo : les concepts de l'île, que l'enfant garde pour
    réviser. Un bouton « Retourner la carte » bascule l'une sur l'autre.

Les deux faces se téléchargent aussi en PDF (ui/carte_pdf.py, redessinées à
partir des mêmes attributs) : l'enfant garde son trophée et imprime sa fiche.

Réutilisable pour les 7 îles : tous les attributs vivent dans une CarteFragment,
le gabarit n'en connaît aucun. Ajouter la carte de l'Île 2 = ajouter une seconde
constante, sans toucher au rendu.

Module dédié (et non un bloc de ui/ecran_enigme.py) précisément parce que les
6 autres cartes ne seront pas remises depuis l'écran d'énigme de l'Île 1.

Texte toujours en HTML — jamais d'image de texte : les chiffres de collection
doivent être exacts et le texte doit rester sélectionnable et net à tout zoom.
Styles en inline seul, comme ecran_carte.py et celebrations.py — pas de <style>
global qui déborderait sur le reste de l'app.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from html import escape
from pathlib import Path

import streamlit as st

_ASSETS = Path(__file__).parent.parent / "assets"

# Palette « or vieilli » — dérivée du doré de la Clé du Partage
# (rgba(201,169,97) = #C9A961, déjà utilisé pour son halo dans ecran_carte.py
# et celebrations.py) pour que le trophée et la clé soient du même métal.
_OR_CLAIR   = "#EFE3BC"
_OR         = "#C9A961"
_OR_SOMBRE  = "#8C6F35"
_PARCHEMIN  = "#FFFDF6"
_PARCHEMIN2 = "#F6ECD3"
_ENCRE      = "#5C4413"
_ENCRE_DOUX = "#7A6844"

_SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif"


# ── Modèle ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ConceptMemo:
    """Une entrée de la fiche mémo (verso) : un concept de l'île."""
    code: str        # « C1 »
    titre: str       # « Sens d'une fraction »
    notion: str      # la règle, en une ou deux phrases
    exemple: str     # un exemple chiffré, court
    # Libellé de bonus, vide par défaut : marque une anticipation du niveau
    # suivant, non obligatoire pour franchir l'île. Chaque île pose le sien.
    bonus: str = ""


@dataclass(frozen=True)
class CarteFragment:
    """Attributs d'une carte de collection. Le gabarit ne lit que ça.

    `memo` porte le verso : vide -> le verso affiche un repli explicite, sans
    jamais planter.
    """
    nom: str
    rarete: str
    ile: str                  # « L'Île des Nombres Brisés — Fractions »
    debloquee_par: str        # libellé de la clé
    cle_icone: str            # chemin de l'icône de clé
    fragment_num: int
    fragment_total: int
    notion_cle: str
    illustration_path: str
    emoji_secours: str = "🏺"           # si l'illustration n'est pas produite
    memo: tuple[ConceptMemo, ...] = ()  # verso — fiche mémo de révision
    memo_titre: str = ""                # en-tête du verso ; repli : `ile`
    memo_sous_titre: str = ""           # ligne d'accroche sous le titre


# Verso de l'Île 1 — contenu VALIDÉ par le Décideur, repris mot pour mot.
# Toute correction se fait ici : le gabarit ne dépend pas de ce texte.
_MEMO_ILE_1: tuple[ConceptMemo, ...] = (
    ConceptMemo(
        code="C1",
        titre="Le sens d'une fraction",
        notion="Une fraction, c'est une part d'un tout partagé en parts égales.",
        exemple="Dans 3/4, le 4 dit en combien de parts on partage, le 3 dit "
                "combien on en prend.",
    ),
    ConceptMemo(
        code="C2",
        titre="La fraction d'une quantité",
        notion="Prendre une fraction d'un nombre : on partage, puis on prend "
               "des parts.",
        exemple="1/3 de 12 : on partage 12 en 3 → 4 par part → 1/3 de 12 = 4.",
    ),
    ConceptMemo(
        code="C3",
        titre="Les fractions équivalentes",
        notion="Deux fractions différentes peuvent valoir la même chose.",
        exemple="1/2 = 2/4 = 4/8. On multiplie le haut ET le bas par le même "
                "nombre.",
    ),
    ConceptMemo(
        code="C4",
        titre="Comparer et ranger des fractions",
        notion="Même dénominateur → la plus grande a le plus de parts (3/5 > 2/5).",
        exemple="Même numérateur → plus les parts sont grosses, plus c'est "
                "grand (1/3 > 1/5).",
    ),
    ConceptMemo(
        code="C5",
        titre="Additionner et soustraire (même dénominateur)",
        notion="Même dénominateur : on ajoute (ou enlève) les numérateurs, le "
               "dénominateur ne change pas.",
        exemple="2/7 + 3/7 = 5/7.",
        # C5 est une anticipation 5e : encouragée, mais non requise pour
        # franchir l'île (cf. ile-1-nombres-brises-CONTENU.md §2).
        bonus="Pour aller plus loin",
    ),
)


CARTE_FRAGMENT = CarteFragment(
    nom="Le Secret de la Couronne",
    rarete="Fragment",
    ile="L'Île des Nombres Brisés — Fractions",
    debloquee_par="Clé du Partage",
    cle_icone=str(_ASSETS / "ui" / "cle_partage.png"),
    fragment_num=1,
    fragment_total=7,
    notion_cle="Une fraction, c'est une part d'un tout.",
    illustration_path=str(_ASSETS / "ui" / "illu_couronne_hieron.png"),
    emoji_secours="👑",
    memo=_MEMO_ILE_1,
    memo_titre="Ma fiche des Nombres Brisés",
    memo_sous_titre="Tout ce que tu as appris sur l'Île 1",
)

# Île 2 et suivantes : une seconde constante ici (recto + memo), rien d'autre
# à écrire — ni gabarit, ni rendu, ni bouton de retournement.


# ── Helpers ───────────────────────────────────────────────────────────────────


@st.cache_data(show_spinner=False)
def _img_b64(chemin: str) -> str | None:
    """Encode une image en base64. Retourne None si le fichier est absent."""
    p = Path(chemin)
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None


def _coin(vertical: str, horizontal: str) -> str:
    """Ornement d'angle : deux traits fins qui redoublent le cadre."""
    rayon = {
        ("top", "left"): "8px 0 0 0", ("top", "right"): "0 8px 0 0",
        ("bottom", "left"): "0 0 0 8px", ("bottom", "right"): "0 0 8px 0",
    }[(vertical, horizontal)]
    return (
        f"<div style=\"position:absolute;{vertical}:5px;{horizontal}:5px;"
        f"width:19px;height:19px;border-{vertical}:2px solid rgba(255,253,246,.75);"
        f"border-{horizontal}:2px solid rgba(255,253,246,.75);border-radius:{rayon};"
        f"pointer-events:none;\"></div>"
    )


def _fenetre_illustration(carte: CarteFragment) -> str:
    """Fenêtre du cadre. Retombe sur un panneau orné si l'illustration manque —
    jamais d'image cassée, jamais de crash."""
    b64 = _img_b64(carte.illustration_path)
    if b64:
        contenu = (
            f"<img src=\"data:image/png;base64,{b64}\" alt=\"{escape(carte.nom)}\" "
            f"style=\"display:block;width:100%;height:100%;object-fit:cover;\">"
        )
    else:
        # Médaillon orné : sans lui, la fenêtre vide fait « image manquante ».
        contenu = (
            f"<div style=\"display:flex;align-items:center;justify-content:center;"
            f"width:100%;height:100%;\">"
            f"<div style=\"display:flex;align-items:center;justify-content:center;"
            f"width:44%;aspect-ratio:1;border-radius:50%;font-size:52px;line-height:1;"
            f"background:radial-gradient(circle at 50% 40%,rgba(255,253,246,.95),"
            f"rgba(201,169,97,.18));"
            f"box-shadow:inset 0 0 0 1px rgba(201,169,97,.55),"
            f"0 0 0 6px rgba(201,169,97,.13),0 3px 10px rgba(140,111,53,.2);"
            f"filter:drop-shadow(0 3px 5px rgba(140,111,53,.3));\">"
            f"{carte.emoji_secours}</div></div>"
        )
    return (
        f"<div style=\"position:relative;aspect-ratio:4/3;border-radius:9px;"
        f"overflow:hidden;background:radial-gradient(circle at 50% 35%,{_PARCHEMIN} 0%,"
        f"#EFE0BE 70%,#E3D2A8 100%);"
        f"box-shadow:inset 0 0 0 2px {_OR},inset 0 0 0 3px rgba(255,253,246,.85),"
        f"inset 0 6px 18px rgba(140,111,53,.22);\">"
        f"{contenu}</div>"
    )


def _pastilles(num: int, total: int) -> str:
    """Une pastille par île — allumées jusqu'au fragment obtenu."""
    points = []
    for i in range(total):
        if i < num:
            points.append(
                f"<span style=\"width:9px;height:9px;border-radius:50%;"
                f"background:radial-gradient(circle at 35% 30%,{_OR_CLAIR},{_OR} 60%,{_OR_SOMBRE});"
                f"box-shadow:0 0 6px rgba(201,169,97,.9);display:inline-block;\"></span>"
            )
        else:
            points.append(
                f"<span style=\"width:9px;height:9px;border-radius:50%;"
                f"background:rgba(140,111,53,.12);"
                f"box-shadow:inset 0 0 0 1px rgba(140,111,53,.38);display:inline-block;\"></span>"
            )
    return (
        f"<span style=\"display:inline-flex;gap:5px;align-items:center;\">"
        f"{''.join(points)}</span>"
    )


def _ligne_cle(carte: CarteFragment) -> str:
    b64 = _img_b64(carte.cle_icone)
    icone = (
        f"<img src=\"data:image/png;base64,{b64}\" alt=\"\" "
        f"style=\"width:24px;height:auto;vertical-align:middle;"
        f"filter:drop-shadow(0 0 6px rgba(201,169,97,.85));\">"
        if b64 else "<span style=\"font-size:18px;\">🗝️</span>"
    )
    return (
        f"<span style=\"display:inline-flex;align-items:center;gap:7px;\">"
        f"{icone}"
        f"<span style=\"font-family:{_SERIF};font-size:.82rem;color:{_ENCRE};\">"
        f"{escape(carte.debloquee_par)}</span></span>"
    )


def _fleuron() -> str:
    """Filet or ─ ◆ ─ or, séparateur commun aux deux faces."""
    return (
        f"<div style=\"display:flex;align-items:center;gap:8px;margin:0 0 8px;\">"
        f"<span style=\"flex:1;height:1px;background:linear-gradient(90deg,"
        f"rgba(201,169,97,0),{_OR});\"></span>"
        f"<span style=\"color:{_OR};font-size:.6rem;\">◆</span>"
        f"<span style=\"flex:1;height:1px;background:linear-gradient(90deg,"
        f"{_OR},rgba(201,169,97,0));\"></span></div>"
    )


def _bandeau(libelle: str) -> str:
    """Pastille dorée d'en-tête (rareté au recto, « Fiche mémo » au verso)."""
    return (
        f"<div style=\"text-align:center;margin:0 0 10px;\">"
        f"<span style=\"display:inline-block;padding:3px 14px;border-radius:999px;"
        f"background:linear-gradient(180deg,{_OR_CLAIR},{_OR} 55%,{_OR_SOMBRE});"
        f"box-shadow:0 1px 3px rgba(140,111,53,.45),inset 0 1px 0 rgba(255,255,255,.6);"
        f"font-family:{_SERIF};font-size:.68rem;letter-spacing:.18em;"
        f"text-transform:uppercase;color:#FFFDF6;"
        f"text-shadow:0 1px 1px rgba(92,68,19,.6);\">"
        f"{escape(libelle)}</span></div>"
    )


def _cadre(interieur: str) -> str:
    """Cadre or vieilli commun aux deux faces — même objet, retourné.

    Dégradé métal (reflets clairs aux angles, creux sombre au centre) + halo
    doré repris de la Clé du Partage.
    """
    coins = "".join(
        _coin(v, h) for v in ("top", "bottom") for h in ("left", "right")
    )
    cadre = (
        f"<div style=\"position:relative;width:min(380px,92%);padding:13px;"
        f"border-radius:18px;"
        f"background:linear-gradient(145deg,#F7EFD4 0%,#D8BC7A 17%,#A9873F 37%,"
        f"{_OR_SOMBRE} 50%,#B99552 63%,{_OR_CLAIR} 83%,#FBF5E2 100%);"
        f"box-shadow:0 0 34px rgba(201,169,97,.6),0 10px 26px rgba(0,0,0,.32),"
        f"inset 0 0 0 1px rgba(255,253,246,.45);\">"
        f"{coins}"
        f"<div style=\"position:relative;border-radius:12px;padding:15px 15px 14px;"
        f"background:linear-gradient(175deg,{_PARCHEMIN} 0%,{_PARCHEMIN2} 100%);"
        f"box-shadow:inset 0 0 0 1px rgba(140,111,53,.45),"
        f"inset 0 2px 16px rgba(140,111,53,.13);\">"
        f"{interieur}</div></div>"
    )
    return (
        f"<div style=\"display:flex;justify-content:center;margin:10px 0 20px;\">"
        f"{cadre}</div>"
    )


# ── Gabarit — RECTO (trophée) ─────────────────────────────────────────────────


def html_carte_fragment(carte: CarteFragment) -> str:
    """Rend le recto en HTML. Pur — testable sans Streamlit."""
    entete_rarete = _bandeau(carte.rarete)

    titre = (
        f"<div style=\"font-family:{_SERIF};font-size:1.3rem;line-height:1.25;"
        f"font-weight:600;color:{_ENCRE};text-align:center;margin:12px 0 6px;"
        f"letter-spacing:.01em;\">{escape(carte.nom)}</div>"
    )

    ile = (
        f"<div style=\"font-family:{_SERIF};font-size:.85rem;color:{_ENCRE_DOUX};"
        f"text-align:center;margin:0 0 14px;font-style:italic;\">"
        f"{escape(carte.ile)}</div>"
    )

    # Clé + compteur de collection. flex-wrap : sur écran étroit, le compteur
    # passe sous la clé au lieu de déborder.
    pied = (
        f"<div style=\"display:flex;flex-wrap:wrap;gap:8px;align-items:center;"
        f"justify-content:space-between;padding:9px 11px;border-radius:8px;"
        f"background:rgba(201,169,97,.13);"
        f"box-shadow:inset 0 0 0 1px rgba(201,169,97,.4);margin:0 0 12px;\">"
        f"{_ligne_cle(carte)}"
        f"<span style=\"display:inline-flex;align-items:center;gap:9px;\">"
        f"{_pastilles(carte.fragment_num, carte.fragment_total)}"
        f"<span style=\"font-family:{_SERIF};font-size:.9rem;font-weight:600;"
        f"color:{_ENCRE};letter-spacing:.03em;\">"
        f"{carte.fragment_num} / {carte.fragment_total}</span></span></div>"
    )

    notion = (
        f"<div style=\"border-left:3px solid {_OR};border-radius:0 8px 8px 0;"
        f"background:linear-gradient(90deg,rgba(201,169,97,.16),rgba(201,169,97,.05));"
        f"padding:10px 12px;\">"
        f"<div style=\"font-family:{_SERIF};font-size:.62rem;letter-spacing:.16em;"
        f"text-transform:uppercase;color:{_ENCRE_DOUX};margin:0 0 3px;\">"
        f"Notion-clé</div>"
        f"<div style=\"font-family:{_SERIF};font-size:.95rem;line-height:1.4;"
        f"color:{_ENCRE};\">{escape(carte.notion_cle)}</div></div>"
    )

    return _cadre(
        f"{entete_rarete}{_fenetre_illustration(carte)}{titre}{_fleuron()}"
        f"{ile}{pied}{notion}"
    )


# ── Gabarit — VERSO (fiche mémo de révision) ──────────────────────────────────


def _entree_memo(concept: ConceptMemo) -> str:
    """Une entrée de la fiche : code, titre, notion, exemple."""
    puce = (
        f"<span style=\"flex:0 0 auto;display:inline-block;min-width:26px;"
        f"padding:1px 7px;border-radius:6px;text-align:center;"
        f"background:linear-gradient(180deg,{_OR_CLAIR},{_OR} 60%,{_OR_SOMBRE});"
        f"box-shadow:0 1px 2px rgba(140,111,53,.4),inset 0 1px 0 rgba(255,255,255,.55);"
        f"font-family:{_SERIF};font-size:.7rem;font-weight:700;letter-spacing:.06em;"
        f"color:#FFFDF6;text-shadow:0 1px 1px rgba(92,68,19,.55);\">"
        f"{escape(concept.code)}</span>"
    )
    # Bonus : liseré doré discret, pas de fond plein — l'entrée reste une
    # entrée de plein droit, simplement signalée comme facultative.
    badge_bonus = (
        f"<span style=\"flex:0 0 auto;display:inline-block;padding:1px 8px;"
        f"border-radius:999px;box-shadow:inset 0 0 0 1px rgba(201,169,97,.75);"
        f"background:rgba(201,169,97,.1);font-family:{_SERIF};font-size:.62rem;"
        f"letter-spacing:.1em;text-transform:uppercase;color:{_ENCRE_DOUX};"
        f"white-space:nowrap;\">✦ {escape(concept.bonus)}</span>"
    ) if concept.bonus else ""

    return (
        f"<div style=\"margin:0 0 9px;padding:9px 11px;border-radius:8px;"
        f"background:rgba(255,253,246,.78);"
        f"box-shadow:inset 0 0 0 1px rgba(201,169,97,.38);\">"
        f"<div style=\"display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;"
        f"margin:0 0 4px;\">"
        f"{puce}"
        f"<span style=\"font-family:{_SERIF};font-size:.92rem;font-weight:600;"
        f"line-height:1.25;color:{_ENCRE};\">{escape(concept.titre)}</span>"
        f"{badge_bonus}</div>"
        f"<div style=\"font-family:{_SERIF};font-size:.85rem;line-height:1.45;"
        f"color:{_ENCRE};\">{escape(concept.notion)}</div>"
        f"<div style=\"margin-top:5px;padding:4px 8px;border-radius:6px;"
        f"background:rgba(201,169,97,.14);font-family:{_SERIF};font-size:.82rem;"
        f"line-height:1.4;color:{_ENCRE_DOUX};\">{escape(concept.exemple)}</div>"
        f"</div>"
    )


def html_verso_fragment(carte: CarteFragment) -> str:
    """Rend le verso — fiche mémo de révision. Pur, testable sans Streamlit."""
    # Pastille courte (label fixe) + titre de la fiche en serif dessous.
    # Repli : sans memo_titre, on retombe sur le nom de l'île — le verso d'une
    # île pas encore rédigée reste présentable.
    entete = _bandeau("Fiche mémo")

    marge_titre = "3px" if carte.memo_sous_titre else "9px"
    titre = (
        f"<div style=\"font-family:{_SERIF};font-size:1.05rem;font-weight:600;"
        f"line-height:1.25;color:{_ENCRE};text-align:center;margin:0 0 {marge_titre};\">"
        f"{escape(carte.memo_titre or carte.ile)}</div>"
    )
    if carte.memo_sous_titre:
        titre += (
            f"<div style=\"font-family:{_SERIF};font-size:.8rem;color:{_ENCRE_DOUX};"
            f"text-align:center;margin:0 0 9px;font-style:italic;\">"
            f"{escape(carte.memo_sous_titre)}</div>"
        )

    if carte.memo:
        corps = "".join(_entree_memo(c) for c in carte.memo)
    else:
        # Repli explicite : une île dont la fiche n'est pas encore rédigée
        # affiche un verso vide mais digne, jamais une erreur.
        corps = (
            f"<div style=\"padding:22px 12px;text-align:center;font-family:{_SERIF};"
            f"font-style:italic;font-size:.9rem;color:{_ENCRE_DOUX};\">"
            f"La fiche mémo de cette île reste à écrire.</div>"
        )

    pied = (
        f"<div style=\"display:flex;flex-wrap:wrap;gap:8px;align-items:center;"
        f"justify-content:space-between;margin-top:11px;padding-top:9px;"
        f"border-top:1px solid rgba(201,169,97,.45);"
        f"font-family:{_SERIF};font-size:.78rem;color:{_ENCRE_DOUX};\">"
        f"<span>{escape(carte.nom)}</span>"
        f"<span style=\"font-weight:600;color:{_ENCRE};letter-spacing:.03em;\">"
        f"{carte.fragment_num} / {carte.fragment_total}</span></div>"
    )

    return _cadre(f"{entete}{titre}{_fleuron()}{corps}{pied}")


# ── Téléchargement (PDF) ──────────────────────────────────────────────────────


def _boutons_pdf(carte: CarteFragment, cle_etat: str) -> None:
    """Les deux fichiers à garder : le trophée et la fiche mémo à imprimer.

    Import local — ui/carte_pdf.py lit CarteFragment, l'importer en tête créerait
    un cycle. Génération à la volée, jamais de fichier temporaire : ~60 ms pour
    les deux, sous le coût d'un rerun Streamlit.

    Un PDF est un supplément, pas la carte : si fpdf2 manque ou trébuche, on le
    dit d'un mot et la carte reste affichée. Un trophée ne disparaît pas parce
    qu'une bibliothèque a échoué.
    """
    try:
        from ui.carte_pdf import nom_fichier, pdf_recto, pdf_verso

        fichiers = (
            ("⬇ Télécharger le trophée (PDF)", pdf_recto(carte),
             nom_fichier(carte, "trophee")),
            ("⬇ Télécharger ma fiche-mémo (PDF)", pdf_verso(carte),
             nom_fichier(carte, "fiche-memo")),
        )
    except Exception:
        st.caption("Le téléchargement en PDF n'est pas disponible pour le moment.")
        return

    for rang, (libelle, donnees, nom) in enumerate(fichiers):
        st.download_button(
            libelle,
            data=donnees,
            file_name=nom,
            mime="application/pdf",
            key=f"btn_{cle_etat}_pdf_{rang}",
            use_container_width=True,
        )


# ── Affichage (recto/verso) ───────────────────────────────────────────────────

_RECTO = "recto"
_VERSO = "verso"


def afficher_carte_fragment(
    carte: CarteFragment = CARTE_FRAGMENT,
    cle_etat: str = "carte_fragment_face",
) -> None:
    """Affiche la carte et son bouton de retournement.

    La face visible vit dans st.session_state[cle_etat] — un simple flag, pas
    d'animation CSS (reportée) : le retournement doit être fiable avant d'être
    joli. `cle_etat` distingue plusieurs cartes affichées dans une même app
    (une par île) sans qu'elles se retournent ensemble.
    """
    face = st.session_state.get(cle_etat, _RECTO)
    verso = face == _VERSO

    html = html_verso_fragment(carte) if verso else html_carte_fragment(carte)
    st.markdown(html, unsafe_allow_html=True)

    # Bouton calé sur la largeur de la carte plutôt qu'étiré sur l'écran.
    _, milieu, _ = st.columns([1, 2, 1])
    with milieu:
        st.markdown(
            f"<div style='text-align:center;font-size:.78rem;color:{_ENCRE_DOUX};"
            f"margin:-8px 0 4px;'>"
            f"{'Verso — fiche mémo' if verso else 'Recto — trophée'}</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "Retourner la carte ↻",
            key=f"btn_{cle_etat}_retourner",
            use_container_width=True,
        ):
            st.session_state[cle_etat] = _RECTO if verso else _VERSO
            st.rerun()

        # Les deux faces sont téléchargeables quelle que soit celle affichée :
        # l'enfant n'a pas à retourner la carte pour obtenir sa fiche de révision.
        _boutons_pdf(carte, cle_etat)
