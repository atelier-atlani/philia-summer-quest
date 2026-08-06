"""
ui/tableau_bord.py — Tableau de bord permanent (sidebar) — Philia Summer Quest.

Responsabilité : montrer en permanence, sur tous les écrans de jeu, où en est
l'enfant et ce qu'il a gagné. Répond au test réel : les coffres n'étaient plus
visibles après la session, et le compteur d'objets disparaissait au scroll.

Ce module reprend et étend _render_sidebar_recompenses(), qui vivait dans
ecran_carte.py et n'était donc affichée que sur la carte. Il n'y a toujours
qu'UNE sidebar — elle a juste déménagé pour être appelable partout.

Sections :
  - vignette de l'archipel (repris tel quel)
  - OÙ JE SUIS      : île courante, session courante, exercice en cours
  - MA COLLECTION   : objets de la session en cours (compteur permanent)
  - MES COFFRES     : sessions validées de l'île, X / 5
  - PORTE-CLÉS      : clés obtenues N / 7 (repris tel quel)
  - MA CARTE        : carte-fragment de l'énigme finale, si gagnée

Toutes les données sont LUES depuis l'existant (jeu.recompenses, le moteur de
session en session_state). Aucun stockage créé ici. Repli gracieux partout :
sans joueur en base, sans asset, sans session en cours, la sidebar s'affiche
quand même — elle montre juste moins de choses.
"""

from __future__ import annotations

import base64
import importlib
import os
from io import BytesIO

import streamlit as st

from config.constants import CRISTAUX_CATALOGUE, ILE_NOMS
from jeu import recompenses
from jeu.collection import emoji_objet, libelle_objet, nom_coffre, objet_de_session

# ── Constantes ────────────────────────────────────────────────────────────────

# Dupliqués depuis ecran_carte.py / celebrations.py plutôt qu'importés : un
# import croisé entre modules d'écrans inverserait le sens des dépendances
# (c'est la convention déjà suivie pour _CLE_IMAGE_PATH dans celebrations.py).
_ARCHIPEL_ISO_PATH = "assets/narratif/globaux/archipel_isometrique.png"
_CLE_IMAGE_PATH = "assets/ui/cle_partage.png"
_COFFRE_IMAGE_PATH = "assets/ui/coffre.png"


def _vue_isometrique_path(ile_id: str) -> str:
    """Vue isométrique de l'île — une image par île, déjà titrée dans le visuel.

    Paramétré plutôt qu'en dur : les îles rangent déjà leurs visuels sous
    assets/narratif/<ile_id>/. L'Île 2 a le sien, l'Île 3 pas encore — l'absence
    du fichier suffit à masquer la vignette, sans condition sur l'île.
    """
    return f"assets/narratif/{ile_id}/vue_isometrique.png"

# Registre du contenu pédagogique, dupliqué depuis ecran_session.py pour la même
# raison. Sert uniquement à retrouver le nom d'un coffre (le concept de la
# session) ; si l'île n'a pas encore de contenu, on retombe sur le catalogue.
_CONTENU_REGISTRY: dict[str, str] = {
    "ile_1": "pedagogie.contenu_ile1",
    "ile_2": "pedagogie.contenu_ile2",
    "ile_3": "pedagogie.contenu_ile3",
}

_ENCRE = "#1E2937"
_TITRE = "#3A5A7C"
_SEPARATEUR = (
    "<hr style='border:none;border-top:1px solid rgba(30,41,55,0.2);margin:10px 0;'/>"
)


# ── Assets ────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def charger_icone_b64(chemin: str, taille: int = 48) -> str | None:
    """Icône en base64, réduite à `taille` px, ou None si l'asset est absent.

    Les assets objets/coffre pèsent ~2 Mo pièce : les inliner tels quels pour
    des vignettes de 20 px enverrait plusieurs Mo de base64 à chaque render. On
    réduit avant d'encoder — résultat mis en cache, calculé une fois par asset.

    Helper partagé : ecran_session.py l'importe d'ici plutôt que d'en garder une
    copie (le sens de dépendance écran → tableau de bord est déjà celui-là).
    """
    if not os.path.exists(chemin):
        return None
    with open(chemin, "rb") as fh:
        brut = fh.read()
    try:
        from PIL import Image  # dépendance déjà tirée par Streamlit

        vignette = Image.open(BytesIO(brut))
        vignette.thumbnail((taille, taille))
        tampon = BytesIO()
        vignette.save(tampon, format="PNG")
        brut = tampon.getvalue()
    except Exception:  # noqa: BLE001 — jamais bloquant : on garde l'original
        pass
    return base64.b64encode(brut).decode()


def _icone_html(chemin: str, secours: str, taille_px: int = 20) -> str:
    """Vignette inline, ou emoji de secours si l'asset n'est pas encore produit."""
    b64 = charger_icone_b64(chemin)
    if b64:
        return (
            f"<img src='data:image/png;base64,{b64}' alt='' style='width:{taille_px}px;"
            f"height:{taille_px}px;object-fit:contain;vertical-align:middle;'>"
        )
    return f"<span style='font-size:{taille_px - 3}px;line-height:1;'>{secours}</span>"


# ── Fragments HTML ────────────────────────────────────────────────────────────

def _titre_section(libelle: str, icone: str = "") -> None:
    st.markdown(
        f"<p style='color:{_TITRE};font-weight:700;font-size:1rem;margin-bottom:4px;"
        f"display:flex;align-items:center;gap:6px;'>{icone}{libelle}</p>",
        unsafe_allow_html=True,
    )


def _ligne(html: str, indent: int = 0, taille: str = "0.9rem") -> None:
    st.markdown(
        f"<p style='color:{_ENCRE};font-size:{taille};margin:2px 0 2px {indent}px;'>"
        f"{html}</p>",
        unsafe_allow_html=True,
    )


def _separateur() -> None:
    st.markdown(_SEPARATEUR, unsafe_allow_html=True)


# ── Lecture de l'état ─────────────────────────────────────────────────────────

def _meta_session(ile_id: str, session_num: int) -> dict | None:
    """META_SESSION_N de l'île, ou None si l'île n'a pas encore de contenu."""
    module_path = _CONTENU_REGISTRY.get(ile_id)
    if module_path is None:
        return None
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return None
    return getattr(module, f"META_SESSION_{session_num}", None)


def _nom_coffre_de(ile_id: str, concept_id: str) -> str:
    """Nom affiché d'un coffre gagné, à partir de son concept_id (« C1 »).

    Source première : le concept de la session — le même nom que celui affiché
    sur le coffre en fin de session, pour que l'enfant reconnaisse le sien.
    Repli : le catalogue des cristaux, qui couvre les 7 îles.
    """
    try:
        numero = int(concept_id[1:])
    except (ValueError, IndexError):
        numero = 0
    meta = _meta_session(ile_id, numero) if numero else None
    if meta:
        return nom_coffre(meta)
    catalogue = CRISTAUX_CATALOGUE.get(ile_id, {}).get("cristaux", {})
    return catalogue.get(concept_id, {}).get("loi", concept_id)


def _nb_exercices_session(ile_id: str, session_num: int) -> int:
    """Nombre d'exercices d'une session, 0 si le contenu n'est pas disponible."""
    module_path = _CONTENU_REGISTRY.get(ile_id)
    if module_path is None:
        return 0
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return 0
    return len(getattr(module, f"SESSION_{session_num}", ()) or ())


def _contenu_coffre(ile_id: str, concept_id: str) -> str:
    """Contenu d'un coffre gagné : « 6 pierres ».

    Un coffre validé est plein — il contient un objet par exercice de sa session.
    Le concept_id stocké en base (« C1 ») redevient le planche_key (« c1 ») pour
    retrouver le type d'objet dans la table de collection.
    Retourne "" si le type d'objet ou le contenu de l'île sont inconnus : la
    ligne affiche alors le seul nom du coffre, sans jamais casser.
    """
    planche_key = concept_id.lower()
    objet = objet_de_session(ile_id, planche_key)
    if not objet:
        return ""
    try:
        numero = int(planche_key[1:])
    except (ValueError, IndexError):
        return ""
    nombre = _nb_exercices_session(ile_id, numero)
    if not nombre:
        return ""
    return libelle_objet(objet["objet"], nombre)


def _etat_session() -> dict | None:
    """État lisible de la session en cours, ou None si aucune session active.

    Retourne {objet, objets_gagnes, repere} — les objets gagnés viennent de
    SessionEngine.objets_gagnes (source unique), jamais d'un calcul refait ici.
    """
    brut = st.session_state.get("session_active")
    if not brut:
        return None
    # Import tardif : sur la carte ou l'île, inutile de charger le moteur (et
    # avec lui le client LLM) juste pour afficher une sidebar.
    from pedagogie.session_engine import SessionEngine

    engine = SessionEngine.from_dict(brut)
    if not engine.exercices:
        return None
    ile_id = st.session_state.get("ile_courante", "ile_1")
    if engine.mode.value == "bilan" or engine.est_dernier_exercice:
        repere = "Bilan"
    else:
        repere = f"Exercice {engine.index_exercice + 1} / {len(engine.exercices)}"
    return {
        "objet": objet_de_session(ile_id, engine.planche_key),
        "objets_gagnes": engine.objets_gagnes,
        "repere": repere,
    }


def _carte_fragment_gagnee() -> bool:
    """Vrai si l'énigme finale a été résolue — la carte-fragment est alors à
    l'enfant. Lu depuis le moteur d'énigme en session_state (l'énigme ne crée
    pas d'entrée en base : enigme_active n'est jamais vidée après résolution).
    """
    brut = st.session_state.get("enigme_active")
    if not brut:
        return False
    try:
        from pedagogie.enigme_engine import EnigmeEngine

        return EnigmeEngine.from_dict(brut).est_terminee()
    except Exception:  # noqa: BLE001 — la sidebar ne casse jamais un écran
        return False


# ── Sections ──────────────────────────────────────────────────────────────────

def _section_ou_je_suis(ile_id: str, etat_session: dict | None) -> None:
    _titre_section("OÙ JE SUIS", "🧭")
    _ligne(f"<strong>{ILE_NOMS.get(ile_id, ile_id)}</strong>")
    if etat_session is None:
        return
    meta = _meta_session(ile_id, st.session_state.get("session_courante", 1))
    if meta:
        _ligne(nom_coffre(meta), indent=8, taille="0.82rem")
    _ligne(etat_session["repere"], indent=8, taille="0.82rem")


def _section_vue_ile(ile_id: str) -> None:
    """Vignette cliquable de la vue isométrique de l'île, agrandie en pop-up.

    L'image pèse ~3 Mo : la vignette passe par le chargeur réduit (120 px), le
    pop-up seul la sert en pleine résolution — et seulement quand il s'ouvre.
    Rien n'est affiché si l'île n'a pas encore de vue produite.
    """
    chemin = _vue_isometrique_path(ile_id)
    if not os.path.exists(chemin):
        return

    b64 = charger_icone_b64(chemin, taille=120)
    if b64:
        st.markdown(
            f"<div style='margin:6px 0 2px;'><img src='data:image/png;base64,{b64}' "
            f"alt='' style='width:100%;border-radius:8px;display:block;"
            f"box-shadow:0 2px 6px rgba(140,111,53,.35);'></div>",
            unsafe_allow_html=True,
        )
    if st.button("🔍 Voir l'île", key="btn_tb_vue_ile", use_container_width=True):
        st.session_state.vue_ile_a_afficher = ile_id
        st.rerun()


def _modal_vue_ile(ile_id: str) -> None:
    """Pop-up plein format. L'image porte déjà son titre — on n'en rajoute pas."""
    chemin = _vue_isometrique_path(ile_id)

    @st.dialog(" ", width="large")
    def _modal() -> None:
        if os.path.exists(chemin):
            st.image(chemin, use_container_width=True)
        else:
            st.markdown(
                "<div style='text-align:center;font-size:64px;'>🏝️</div>",
                unsafe_allow_html=True,
            )
            st.caption("La vue de cette île n'est pas encore dessinée.")
        if st.button("Fermer", key="btn_tb_vue_ile_fermer", use_container_width=True):
            st.session_state.vue_ile_a_afficher = None
            st.rerun()

    _modal()


def _section_collection(etat_session: dict | None) -> None:
    """Compteur d'objets de la session en cours — visible en permanence, c'est
    ce que le scroll faisait perdre sur l'écran de session."""
    if etat_session is None or not etat_session["objet"]:
        return
    _separateur()
    objet = etat_session["objet"]
    _titre_section("MA COLLECTION")
    icone = _icone_html(objet["asset"], emoji_objet(objet["objet"]), taille_px=22)
    _ligne(
        f"{icone} <strong>{libelle_objet(objet['objet'], etat_session['objets_gagnes'])}</strong>"
    )


def _section_coffres(ile_id: str, cristaux: dict) -> None:
    """Les cristaux obtenus, rhabillés en coffres (mécanique inchangée)."""
    _separateur()
    coffres = cristaux.get(ile_id, {})
    total = len(CRISTAUX_CATALOGUE.get(ile_id, {}).get("cristaux", {})) or 5
    _titre_section("MES COFFRES", _icone_html(_COFFRE_IMAGE_PATH, "🧰", taille_px=24))
    _ligne(f"<strong>{len(coffres)} / {total}</strong> coffres")
    if not coffres:
        _ligne("Ton premier coffre t'attend.", indent=8, taille="0.82rem")
        return
    mini = _icone_html(_COFFRE_IMAGE_PATH, "🧰", taille_px=18)
    for concept_id in sorted(coffres):
        # Le coffre montre ce qu'il contient : l'enfant retrouve les objets
        # qu'il a ramassés, pas seulement l'intitulé du concept.
        libelle = _nom_coffre_de(ile_id, concept_id)
        contenu = _contenu_coffre(ile_id, concept_id)
        if contenu:
            libelle += f" — {contenu}"
        _ligne(f"{mini} {libelle}", indent=8, taille="0.82rem")


def _section_portecles(cles: dict) -> None:
    _separateur()
    _titre_section("PORTE-CLÉS", _icone_html(_CLE_IMAGE_PATH, "🗝️", taille_px=26))
    _ligne(f"<strong>{len(cles)} / 7</strong> clés obtenues")
    for ile_id in cles:
        _ligne(f"✓ {ILE_NOMS.get(ile_id, ile_id)}", indent=8, taille="0.82rem")


def _section_carte() -> None:
    if not _carte_fragment_gagnee():
        return
    _separateur()
    _titre_section("MA CARTE", "🗺️")
    _ligne("Fragment du secret d'Archimède", taille="0.82rem")
    if st.session_state.get("ecran_courant") != "enigme":
        if st.button("Revoir ma carte", key="btn_tb_carte_fragment", use_container_width=True):
            st.session_state.ecran_courant = "enigme"
            st.rerun()


# ── Point d'entrée ────────────────────────────────────────────────────────────

def _injecter_css() -> None:
    """Fond parchemin de la sidebar. Il vivait dans ecran_carte._inject_css() et
    ne s'appliquait donc qu'à la carte ; les couleurs de texte de ce module
    (encre sombre) sont calibrées pour ce fond clair — sans lui, la sidebar
    serait illisible en thème sombre sur les autres écrans.
    """
    st.markdown(
        "<style>[data-testid='stSidebar'] "
        "{ background: linear-gradient(180deg, #e8d5a3 0%, #c9a84c 100%); }</style>",
        unsafe_allow_html=True,
    )


def render_tableau_bord() -> None:
    """Rend le tableau de bord dans la sidebar. Appelé par les écrans de jeu
    (carte, île, session, énigme). Sans joueur en base, affiche les compteurs à
    zéro sans erreur — jamais d'exception remontée à l'écran appelant.
    """
    try:
        cles = recompenses.cles_obtenues()
        cristaux = recompenses.cristaux_obtenus()
    except RuntimeError:
        cles, cristaux = {}, {}

    ile_id = st.session_state.get("ile_courante", "ile_1")
    etat_session = _etat_session()
    _injecter_css()

    with st.sidebar:
        # Vignette isométrique de l'archipel (D14bis) — reprise telle quelle.
        if os.path.exists(_ARCHIPEL_ISO_PATH):
            st.image(
                _ARCHIPEL_ISO_PATH,
                use_container_width=True,
                caption="L'Archipel de la Raison",
            )
            _separateur()

        _section_ou_je_suis(ile_id, etat_session)
        _section_vue_ile(ile_id)
        _section_collection(etat_session)
        _section_coffres(ile_id, cristaux)
        _section_portecles(cles)
        _section_carte()

        _separateur()
        st.caption("Quête estivale de Philia — MVP")

    # Le pop-up se rend HORS du bloc sidebar : un st.dialog est plein écran, il
    # n'appartient pas à la colonne qui l'a déclenché. Il cède la place aux
    # modals du récit : Streamlit n'autorise qu'un dialog par script run, et
    # deux ouvertures dans le même render lèvent une exception en pleine partie.
    if st.session_state.get("vue_ile_a_afficher"):
        from ui import flux_chapitre  # import tardif : la sidebar est chargée partout

        if flux_chapitre.modal_du_flux_ouvert():
            st.session_state.vue_ile_a_afficher = None
        else:
            _modal_vue_ile(st.session_state["vue_ile_a_afficher"])
