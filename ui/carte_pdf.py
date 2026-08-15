"""
ui/carte_pdf.py — Export PDF de la carte-fragment (recto trophée, verso mémo).

L'enfant garde sa carte : deux fichiers téléchargeables à la fin de l'île.
  - pdf_recto(carte) — le trophée, à afficher.
  - pdf_verso(carte) — la fiche mémo, à IMPRIMER et à relire (c'est une fiche
    de révision : lisible en noir sur clair, marges franches, rien de décoratif
    qui gênerait la lecture).

POURQUOI REDESSINER PLUTÔT QUE CONVERTIR LE HTML.
Le gabarit d'écran (ui/carte_fragment.py) est du HTML/CSS. Le convertir
demanderait weasyprint ou un navigateur headless (playwright) : trop lourd pour
l'hébergement. On repart donc des DONNÉES de la CarteFragment — le même
contenu, redessiné à la règle avec fpdf2 (déjà au requirements). Conséquence
assumée : le PDF n'est pas un clone pixel du HTML, c'est la même carte dans
l'autre médium. Ajouter une île ne demande rien ici, comme pour le HTML.

FORMAT A4 PORTRAIT pour les deux faces : un enfant imprime sur du A4, pas sur
du A5. Le trophée est composé comme une carte centrée dans son cadre or.

POLICES : Liberation Serif est embarquée (assets/fonts/, licence OFL). Les
polices de base du PDF (Times) sont encodées en latin-1 : elles savent écrire
les accents mais pas les flèches des exemples (« on partage 12 en 3 → 4 par
part »), qui finissaient translittérées en « -> » — et l'étiquette
« NOTION-CLÉ », mise en capitales, perdait son accent.

POURQUOI LIBERATION SERIF ET PAS UNE AUTRE. Elle a les MÊMES MÉTRIQUES que
Times : chaque mot occupe exactement la largeur qu'il occupait, donc la mise en
page — césures, hauteurs de blocs, fiche mémo tenant sur une page — est
inchangée. Une serif plus large (DejaVu Serif, essayée) recompose tout le texte
et pousse le dernier concept sur une seconde page. Trois styles seulement
(régulier, gras, italique), ~1,1 Mo au dépôt ; fpdf2 n'incorpore au PDF que les
glyphes employés, donc les fichiers produits restent légers.

Repli assumé : si les fichiers de fonte manquent (dépôt incomplet), on retombe
sur Times et sur la translittération — un PDF imparfait vaut mieux qu'une page
de téléchargement en erreur.

Point d'entrée public : pdf_recto(carte), pdf_verso(carte) -> bytes
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ui.carte_fragment import CarteFragment, ConceptMemo

try:
    from fpdf import FPDF
except ImportError:  # pragma: no cover — fpdf2 est au requirements
    FPDF = None


# ── Palette (reprise de ui/carte_fragment.py, en RVB) ─────────────────────────

_OR_CLAIR   = (239, 227, 188)   # #EFE3BC
_OR         = (201, 169,  97)   # #C9A961
_OR_SOMBRE  = (140, 111,  53)   # #8C6F35
_PARCHEMIN  = (255, 253, 246)   # #FFFDF6
_PARCHEMIN2 = (246, 236, 211)   # #F6ECD3
_ENCRE      = ( 92,  68,  19)   # #5C4413
_ENCRE_DOUX = (122, 104,  68)   # #7A6844
_OR_PALE    = (245, 236, 213)   # fonds des blocs (or à ~13 % sur parchemin)

# ── Fonte embarquée ───────────────────────────────────────────────────────────

# Trois styles seulement — le tracé n'utilise que régulier, gras et italique.
# Ajouter un gras-italique demanderait d'ajouter ici son fichier.
_FONTES = Path(__file__).parent.parent / "assets" / "fonts"
_FICHIERS = {
    "": "LiberationSerif-Regular.ttf",
    "B": "LiberationSerif-Bold.ttf",
    "I": "LiberationSerif-Italic.ttf",
}

_UNICODE = all((_FONTES / f).exists() for f in _FICHIERS.values())
_SERIF = "LiberationSerif" if _UNICODE else "Times"

# Géométrie de la page (mm) — commune aux deux faces.
_PAGE_L, _PAGE_H = 210.0, 297.0
_CADRE_M = 12.0                  # marge du cadre or
_CADRE_EP = 5.0                  # épaisseur du cadre or
_PANNEAU_PAD = 11.0              # marge interne du panneau parchemin

_CADRE_L = _PAGE_L - 2 * _CADRE_M
_CADRE_HT = _PAGE_H - 2 * _CADRE_M
_PANNEAU_X = _CADRE_M + _CADRE_EP
_PANNEAU_Y = _CADRE_M + _CADRE_EP
_PANNEAU_L = _CADRE_L - 2 * _CADRE_EP
_PANNEAU_HT = _CADRE_HT - 2 * _CADRE_EP

_X = _PANNEAU_X + _PANNEAU_PAD                  # colonne de contenu
_L = _PANNEAU_L - 2 * _PANNEAU_PAD
_Y_HAUT = _PANNEAU_Y + _PANNEAU_PAD
_Y_BAS = _PANNEAU_Y + _PANNEAU_HT - _PANNEAU_PAD


# ── Texte : ce que la fonte ne sait pas tracer ────────────────────────────────

# Les rares signes décoratifs absents de Liberation Serif : sans remplacement,
# ils sortiraient en rectangle vide. Tout le reste — flèches, accents, tirets
# longs, apostrophes courbes, guillemets français, signes mathématiques — est
# tracé tel quel. (Le losange du fleuron est un polygone, pas un caractère.)
_HORS_FONTE = {"✦": "*", "◆": "*", "★": "*", "☆": "*", "⇒": "=>"}

# Repli sans fonte embarquée : les polices de base sont en latin-1, et tout ce
# qui en sort doit être translittéré — sans quoi fpdf2 lève sur la fiche mémo,
# qui contient une flèche.
_TRANSLIT = {
    "→": "->", "←": "<-", "↔": "<->", "⇒": "=>",
    "—": "-", "–": "-", "‑": "-", "−": "-",
    "’": "'", "‘": "'", "“": '"', "”": '"', "«": "<<", "»": ">>",
    "…": "...", "•": "-", "✦": "*", "◆": "*", "★": "*", "☆": "*",
    "≠": "!=", "≤": "<=", "≥": ">=", "≈": "~",
    " ": " ", " ": " ", "​": "",
}


def _texte(brut: str) -> str:
    """Texte tel qu'il sera tracé — jamais tronqué, jamais cause d'exception.

    Avec la fonte embarquée, le texte passe intact : « → » reste une flèche et
    « NOTION-CLÉ » garde son accent. Sans elle, on retombe sur les polices de
    base — translittération, puis filet de sécurité latin-1 : on préfère un
    « ? » isolé à une fiche mémo absente.
    """
    if _UNICODE:
        for source, cible in _HORS_FONTE.items():
            brut = brut.replace(source, cible)
        return brut
    for source, cible in _TRANSLIT.items():
        brut = brut.replace(source, cible)
    return brut.encode("latin-1", "replace").decode("latin-1")


def _slug(carte: CarteFragment) -> str:
    """Fragment de nom de fichier tiré du nom de l'île — « nombres-brises ».

    On ne garde que la partie avant le tiret (« L'Île des Nombres Brisés »
    dans « L'Île des Nombres Brisés — Fractions »), sans les mots d'articulation.

    La coupure se fait sur le tiret RÉEL du titre, quelle que soit sa forme :
    depuis que la fonte embarquée trace le cadratin, _texte() ne le ramène plus
    à un trait d'union — s'appuyer dessus ferait ressurgir « Fractions » dans le
    nom du fichier.
    """
    titre = re.split(r"[-—–]", carte.ile)[0]
    sans_accent = unicodedata.normalize("NFKD", titre).encode("ascii", "ignore").decode()
    vides = {"l", "la", "le", "les", "de", "des", "du", "d", "ile", "iles"}
    mots = [
        m for m in "".join(c if c.isalnum() else " " for c in sans_accent).lower().split()
        if m not in vides
    ]
    return "-".join(mots) or f"ile-{carte.fragment_num}"


def nom_fichier(carte: CarteFragment, face: str) -> str:
    """« trophee-nombres-brises.pdf » / « fiche-memo-nombres-brises.pdf »."""
    return f"{face}-{_slug(carte)}.pdf"


# ── Images ────────────────────────────────────────────────────────────────────


_QUALITE_JPEG = 88


def _image_reduite(chemin: str, largeur_px: int):
    """(source pour fpdf2, largeur px, hauteur px). None si l'image est indisponible.

    Réduire ET ré-encoder AVANT d'incorporer : les assets font 1,6 Mo chacun,
    pensés pour l'impression grand format. Posés tels quels, ils donnaient un
    trophée de 2 Mo — fpdf2 incorpore un PNG sans perte. Ramenés à la définition
    utile (≈ 200 ppp au format d'impression) et passés en JPEG, les deux PDF
    tiennent en quelques dizaines de kilo-octets, sans différence visible à
    l'œil. Même arbitrage que ui/images.py pour le web.

    RÈGLE DE SÛRETÉ reprise de ui/images.py : une image avec transparence reste
    en PNG — la clé passée en JPEG arriverait sur un fond noir.
    """
    fichier = Path(chemin)
    if not fichier.exists():
        return None
    try:
        from io import BytesIO

        from PIL import Image  # dépendance déjà tirée par fpdf2 et Streamlit

        image = Image.open(fichier)
        image.load()
        if image.width > largeur_px:
            hauteur = round(image.height * largeur_px / image.width)
            image = image.resize((largeur_px, hauteur), Image.LANCZOS)

        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            return image, image.width, image.height

        tampon = BytesIO()
        image.convert("RGB").save(tampon, format="JPEG", quality=_QUALITE_JPEG)
        tampon.seek(0)
        return tampon, image.width, image.height
    except Exception:
        # Une illustration n'a jamais le droit d'empêcher le trophée d'exister.
        return None


def _pose_image_ajustee(pdf, image, cx: float, y: float, max_l: float, max_h: float):
    """Pose l'image centrée en cx, contenue dans la boîte. Retourne son rectangle."""
    source, largeur_px, hauteur_px = image
    ratio = largeur_px / hauteur_px
    largeur, hauteur = max_l, max_l / ratio
    if hauteur > max_h:
        largeur, hauteur = max_h * ratio, max_h
    x = cx - largeur / 2
    pdf.image(source, x=x, y=y, w=largeur, h=hauteur)
    return x, y, largeur, hauteur


# ── Primitives de dessin ──────────────────────────────────────────────────────


def _fond_et_cadre(pdf) -> None:
    """Fond parchemin, cadre or vieilli, panneau intérieur, ornements d'angle.

    Le dégradé métal du HTML n'a pas d'équivalent simple en PDF : on le rend
    par trois filets or (clair / plein / sombre), qui donnent le même relief.
    """
    pdf.set_fill_color(*_PARCHEMIN2)
    pdf.rect(0, 0, _PAGE_L, _PAGE_H, style="F")

    pdf.set_fill_color(*_OR)
    pdf.set_draw_color(*_OR_SOMBRE)
    pdf.set_line_width(0.6)
    pdf.rect(_CADRE_M, _CADRE_M, _CADRE_L, _CADRE_HT,
             style="DF", round_corners=True, corner_radius=5)

    pdf.set_draw_color(*_OR_CLAIR)
    pdf.set_line_width(0.4)
    pdf.rect(_CADRE_M + 1.2, _CADRE_M + 1.2, _CADRE_L - 2.4, _CADRE_HT - 2.4,
             style="D", round_corners=True, corner_radius=4)

    pdf.set_fill_color(*_PARCHEMIN)
    pdf.set_draw_color(*_OR_SOMBRE)
    pdf.set_line_width(0.3)
    pdf.rect(_PANNEAU_X, _PANNEAU_Y, _PANNEAU_L, _PANNEAU_HT,
             style="DF", round_corners=True, corner_radius=3)

    # Équerres d'angle : les deux traits fins qui redoublent le cadre en HTML.
    pdf.set_draw_color(*_OR_CLAIR)
    pdf.set_line_width(0.5)
    marge, longueur = 3.0, 8.0
    for gauche in (True, False):
        for haut in (True, False):
            x = _CADRE_M + marge if gauche else _CADRE_M + _CADRE_L - marge
            y = _CADRE_M + marge if haut else _CADRE_M + _CADRE_HT - marge
            pdf.line(x, y, x + (longueur if gauche else -longueur), y)
            pdf.line(x, y, x, y + (longueur if haut else -longueur))


def _bandeau(pdf, y: float, libelle: str, largeur: float = 46.0, hauteur: float = 7.0) -> float:
    """Pastille dorée d'en-tête. Retourne l'ordonnée sous le bandeau."""
    pdf.set_font(_SERIF, "B", 10)
    largeur = max(largeur, pdf.get_string_width(_texte(libelle).upper()) + 16)
    x = _PAGE_L / 2 - largeur / 2

    pdf.set_fill_color(*_OR)
    pdf.set_draw_color(*_OR_SOMBRE)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, largeur, hauteur, style="DF", round_corners=True, corner_radius=hauteur / 2)

    pdf.set_text_color(*_PARCHEMIN)
    pdf.set_char_spacing(1.2)
    pdf.set_xy(x, y)
    pdf.cell(largeur, hauteur, _texte(libelle).upper(), align="C")
    pdf.set_char_spacing(0)
    pdf.set_text_color(*_ENCRE)
    return y + hauteur


def _fleuron(pdf, y: float, largeur: float = 70.0) -> float:
    """Filet or — losange — filet or. Séparateur commun aux deux faces."""
    cx = _PAGE_L / 2
    pdf.set_draw_color(*_OR)
    pdf.set_line_width(0.4)
    pdf.line(cx - largeur / 2, y, cx - 4, y)
    pdf.line(cx + 4, y, cx + largeur / 2, y)
    pdf.set_fill_color(*_OR)
    pdf.polygon([(cx, y - 1.5), (cx + 1.5, y), (cx, y + 1.5), (cx - 1.5, y)], style="F")
    return y + 1.5


def _paragraphe(pdf, x: float, y: float, largeur: float, texte: str,
                police: str, taille: float, couleur, align: str = "L",
                interligne: float = 1.35) -> float:
    """Écrit un texte multi-lignes. Retourne l'ordonnée juste sous la dernière."""
    pdf.set_font(_SERIF, police, taille)
    pdf.set_text_color(*couleur)
    hauteur_ligne = taille * interligne * 0.3528  # points -> mm
    pdf.set_xy(x, y)
    pdf.multi_cell(largeur, hauteur_ligne, _texte(texte), align=align)
    return pdf.get_y()


def _hauteur_paragraphe(pdf, largeur: float, texte: str, police: str, taille: float,
                        interligne: float = 1.35) -> float:
    """Hauteur qu'occuperait _paragraphe — sans rien écrire (pagination du verso)."""
    pdf.set_font(_SERIF, police, taille)
    hauteur_ligne = taille * interligne * 0.3528
    return pdf.multi_cell(largeur, hauteur_ligne, _texte(texte),
                          align="L", dry_run=True, output="HEIGHT")


def _nouvelle_page(pdf) -> None:
    pdf.add_page()
    _fond_et_cadre(pdf)


def _document():
    """Document A4 portrait, sans saut de page automatique (on pagine à la main)."""
    if FPDF is None:  # pragma: no cover
        raise RuntimeError(
            "fpdf2 est introuvable : impossible de générer le PDF de la carte."
        )
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    # Les fontes s'enregistrent par document, pas globalement. fpdf2 n'incorpore
    # ensuite que les glyphes réellement employés (sous-ensemble) : les trois
    # fichiers pèsent ~1 Mo au dépôt, quelques kilo-octets dans le PDF.
    if _UNICODE:
        for style, fichier in _FICHIERS.items():
            pdf.add_font(_SERIF, style, str(_FONTES / fichier))
    pdf.set_auto_page_break(False)
    pdf.set_margins(_X, _Y_HAUT, _PAGE_L - _X - _L)
    return pdf


# ── RECTO — le trophée ────────────────────────────────────────────────────────


def _fenetre_illustration(pdf, y: float, carte: CarteFragment, hauteur_max: float) -> float:
    """Illustration dans sa fenêtre or. Repli orné si l'image manque."""
    cx = _PAGE_L / 2
    image = _image_reduite(carte.illustration_path, 900)

    if image is not None:
        x, y, largeur, hauteur = _pose_image_ajustee(pdf, image, cx, y, _L * 0.62, hauteur_max)
    else:
        # Médaillon vide mais digne, comme le repli emoji du gabarit HTML : une
        # fenêtre nue passerait pour une image cassée.
        largeur, hauteur = _L * 0.5, hauteur_max * 0.62
        x = cx - largeur / 2
        pdf.set_fill_color(*_OR_PALE)
        pdf.rect(x, y, largeur, hauteur, style="F")
        pdf.set_fill_color(*_OR)
        pdf.polygon(
            [(cx, y + hauteur / 2 - 9), (cx + 9, y + hauteur / 2),
             (cx, y + hauteur / 2 + 9), (cx - 9, y + hauteur / 2)],
            style="F",
        )

    pdf.set_draw_color(*_OR)
    pdf.set_line_width(1.0)
    pdf.rect(x - 1.4, y - 1.4, largeur + 2.8, hauteur + 2.8, style="D")
    pdf.set_draw_color(*_OR_SOMBRE)
    pdf.set_line_width(0.3)
    pdf.rect(x - 2.6, y - 2.6, largeur + 5.2, hauteur + 5.2, style="D")
    return y + hauteur + 2.6


def _pastilles(pdf, x_droite: float, y: float, num: int, total: int) -> float:
    """Une pastille par île, allumées jusqu'au fragment obtenu. Retourne x du bord gauche."""
    d, ecart = 2.6, 1.7
    largeur = total * d + (total - 1) * ecart
    x = x_droite - largeur
    for i in range(total):
        cx = x + i * (d + ecart)
        if i < num:
            pdf.set_fill_color(*_OR)
            pdf.set_draw_color(*_OR_SOMBRE)
            pdf.set_line_width(0.2)
            pdf.ellipse(cx, y, d, d, style="DF")
        else:
            pdf.set_draw_color(*_OR)
            pdf.set_line_width(0.2)
            pdf.ellipse(cx, y, d, d, style="D")
    return x


def _bandeau_pied(pdf, y: float, carte: CarteFragment, hauteur: float = 14.0) -> float:
    """Clé de déblocage à gauche, compteur de collection à droite."""
    pdf.set_fill_color(*_OR_PALE)
    pdf.set_draw_color(*_OR)
    pdf.set_line_width(0.3)
    pdf.rect(_X, y, _L, hauteur, style="DF", round_corners=True, corner_radius=2.5)

    x_texte = _X + 5
    icone = _image_reduite(carte.cle_icone, 200)
    if icone is not None:
        _, _, largeur, _ = _pose_image_ajustee(
            pdf, icone, _X + 5 + 4.5, y + 1.6, 9.0, hauteur - 3.2
        )
        x_texte = _X + 5 + 4.5 + largeur / 2 + 3

    pdf.set_font(_SERIF, "", 11)
    pdf.set_text_color(*_ENCRE)
    pdf.set_xy(x_texte, y)
    pdf.cell(0, hauteur, _texte(carte.debloquee_par), align="L")

    compteur = f"{carte.fragment_num} / {carte.fragment_total}"
    pdf.set_font(_SERIF, "B", 12)
    largeur_compteur = pdf.get_string_width(compteur)
    x_compteur = _X + _L - 5 - largeur_compteur
    pdf.set_xy(x_compteur, y)
    pdf.cell(largeur_compteur, hauteur, compteur, align="R")
    _pastilles(pdf, x_compteur - 4, y + hauteur / 2 - 1.3,
               carte.fragment_num, carte.fragment_total)
    return y + hauteur


def _hauteur_notion(pdf, carte: CarteFragment) -> float:
    """Hauteur du bloc notion-clé — connue avant de dessiner, pour l'ancrer en bas."""
    return 8 + _hauteur_paragraphe(pdf, _L - 12, carte.notion_cle, "", 12) + 4


def _bloc_notion(pdf, y: float, carte: CarteFragment) -> float:
    """Notion-clé : filet or à gauche, étiquette, phrase. Ancré en bas de page."""
    hauteur = _hauteur_notion(pdf, carte)

    pdf.set_fill_color(*_OR_PALE)
    pdf.rect(_X, y, _L, hauteur, style="F", round_corners=True, corner_radius=2)
    pdf.set_fill_color(*_OR)
    pdf.rect(_X, y, 1.6, hauteur, style="F")

    pdf.set_font(_SERIF, "", 8)
    pdf.set_text_color(*_ENCRE_DOUX)
    pdf.set_char_spacing(1.0)
    pdf.set_xy(_X + 6, y + 2)
    pdf.cell(0, 4, _texte("NOTION-CLÉ"), align="L")
    pdf.set_char_spacing(0)

    _paragraphe(pdf, _X + 6, y + 7, _L - 12, carte.notion_cle, "", 12, _ENCRE)
    return y + hauteur


def pdf_recto(carte: CarteFragment) -> bytes:
    """Le trophée en PDF, une page A4 portrait. Pur : testable hors Streamlit."""
    pdf = _document()
    _nouvelle_page(pdf)

    y = _bandeau(pdf, _Y_HAUT, carte.rarete) + 10

    # Le bas de page est ancré (notion-clé puis bandeau clé/collection) : la
    # fenêtre d'illustration prend simplement la place qui reste, quelle que
    # soit la longueur du titre. Une île au nom long ne décale rien.
    y_notion = _Y_BAS - _hauteur_notion(pdf, carte)
    y_pied = y_notion - 6 - 14
    hauteur_titre = _hauteur_paragraphe(pdf, _L, carte.nom, "B", 24)
    hauteur_ile = _hauteur_paragraphe(pdf, _L, carte.ile, "I", 12)
    hauteur_illu = y_pied - y - (hauteur_titre + 6 + hauteur_ile + 14)

    y = _fenetre_illustration(pdf, y + 2.6, carte, max(hauteur_illu, 40)) + 8
    y = _paragraphe(pdf, _X, y, _L, carte.nom, "B", 24, _ENCRE, align="C", interligne=1.2)
    y = _fleuron(pdf, y + 4) + 3
    _paragraphe(pdf, _X, y, _L, carte.ile, "I", 12, _ENCRE_DOUX, align="C")

    _bandeau_pied(pdf, y_pied, carte)
    _bloc_notion(pdf, y_notion, carte)

    return bytes(pdf.output())


# ── VERSO — la fiche mémo ─────────────────────────────────────────────────────

_ENTREE_PAD = 4.0
_ENTREE_ECART = 4.5


def _hauteur_entree(pdf, concept: ConceptMemo) -> float:
    """Hauteur totale d'une entrée de fiche — sert à décider du saut de page."""
    interne = _L - 2 * _ENTREE_PAD
    return (
        _ENTREE_PAD
        + 6                                                        # ligne de titre
        + _hauteur_paragraphe(pdf, interne, concept.notion, "", 11)
        + 2
        + 3 + _hauteur_paragraphe(pdf, interne - 6, concept.exemple, "", 10) + 3
        + _ENTREE_PAD
    )


def _entree_memo(pdf, y: float, concept: ConceptMemo) -> float:
    """Une entrée : code, titre, éventuel bonus, notion, exemple encadré."""
    hauteur = _hauteur_entree(pdf, concept)
    interne = _L - 2 * _ENTREE_PAD

    pdf.set_fill_color(*_PARCHEMIN)
    pdf.set_draw_color(*_OR)
    pdf.set_line_width(0.3)
    pdf.rect(_X, y, _L, hauteur, style="DF", round_corners=True, corner_radius=2)

    # Ligne de titre : pastille du code, titre, badge « bonus » aligné à droite.
    x = _X + _ENTREE_PAD
    y_ligne = y + _ENTREE_PAD
    pdf.set_font(_SERIF, "B", 8)
    largeur_code = max(9.0, pdf.get_string_width(_texte(concept.code)) + 5)
    pdf.set_fill_color(*_OR)
    pdf.set_draw_color(*_OR_SOMBRE)
    pdf.rect(x, y_ligne, largeur_code, 5, style="DF", round_corners=True, corner_radius=1.2)
    pdf.set_text_color(*_PARCHEMIN)
    pdf.set_xy(x, y_ligne)
    pdf.cell(largeur_code, 5, _texte(concept.code), align="C")

    if concept.bonus:
        pdf.set_font(_SERIF, "I", 8)
        libelle = _texte("✦ " + concept.bonus)
        largeur_bonus = pdf.get_string_width(libelle) + 6
        x_bonus = _X + _L - _ENTREE_PAD - largeur_bonus
        pdf.set_draw_color(*_OR)
        pdf.set_line_width(0.3)
        pdf.rect(x_bonus, y_ligne, largeur_bonus, 5, style="D",
                 round_corners=True, corner_radius=2.5)
        pdf.set_text_color(*_ENCRE_DOUX)
        pdf.set_xy(x_bonus, y_ligne)
        pdf.cell(largeur_bonus, 5, libelle, align="C")

    pdf.set_font(_SERIF, "B", 12)
    pdf.set_text_color(*_ENCRE)
    pdf.set_xy(x + largeur_code + 3, y_ligne)
    pdf.cell(0, 5, _texte(concept.titre), align="L")

    y_texte = _paragraphe(pdf, x, y_ligne + 6, interne, concept.notion, "", 11, _ENCRE)

    hauteur_exemple = _hauteur_paragraphe(pdf, interne - 6, concept.exemple, "", 10) + 6
    pdf.set_fill_color(*_OR_PALE)
    pdf.rect(x, y_texte + 2, interne, hauteur_exemple, style="F",
             round_corners=True, corner_radius=1.5)
    _paragraphe(pdf, x + 3, y_texte + 5, interne - 6, concept.exemple, "", 10, _ENCRE_DOUX)

    return y + hauteur + _ENTREE_ECART


def _pied_verso(pdf, carte: CarteFragment) -> None:
    """Filet or, nom de la carte à gauche, compteur à droite — sur chaque page."""
    y = _Y_BAS - 6
    pdf.set_draw_color(*_OR)
    pdf.set_line_width(0.3)
    pdf.line(_X, y, _X + _L, y)
    pdf.set_font(_SERIF, "I", 10)
    pdf.set_text_color(*_ENCRE_DOUX)
    pdf.set_xy(_X, y + 1)
    pdf.cell(_L / 2, 5, _texte(carte.nom), align="L")
    pdf.set_font(_SERIF, "B", 10)
    pdf.set_text_color(*_ENCRE)
    pdf.set_xy(_X + _L / 2, y + 1)
    pdf.cell(_L / 2, 5, f"{carte.fragment_num} / {carte.fragment_total}", align="R")


def pdf_verso(carte: CarteFragment) -> bytes:
    """La fiche mémo en PDF. Autant de pages A4 que les concepts en demandent."""
    pdf = _document()
    _nouvelle_page(pdf)

    y = _bandeau(pdf, _Y_HAUT, "Fiche mémo") + 8
    y = _paragraphe(pdf, _X, y, _L, carte.memo_titre or carte.ile, "B", 18,
                    _ENCRE, align="C", interligne=1.2)
    if carte.memo_sous_titre:
        y = _paragraphe(pdf, _X, y + 1, _L, carte.memo_sous_titre, "I", 11,
                        _ENCRE_DOUX, align="C")
    y = _fleuron(pdf, y + 4) + 6

    if not carte.memo:
        # Même repli que le gabarit HTML : une île dont la fiche n'est pas
        # encore rédigée donne un PDF vide mais présentable, jamais une erreur.
        _paragraphe(pdf, _X, y + 20, _L, "La fiche mémo de cette île reste à écrire.",
                    "I", 12, _ENCRE_DOUX, align="C")
        _pied_verso(pdf, carte)
        return bytes(pdf.output())

    limite = _Y_BAS - 10  # le pied de page mange les 10 derniers millimètres
    for concept in carte.memo:
        if y + _hauteur_entree(pdf, concept) > limite:
            _pied_verso(pdf, carte)
            _nouvelle_page(pdf)
            y = _Y_HAUT
        y = _entree_memo(pdf, y, concept)

    _pied_verso(pdf, carte)
    return bytes(pdf.output())
