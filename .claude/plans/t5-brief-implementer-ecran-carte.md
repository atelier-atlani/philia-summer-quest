# Brief Implémenteur — T5 : Écran Carte de l'Archipel

**Sprint 3 — Philia Summer Quest**
**Fichier cible : `ui/ecran_carte.py`**
**Durée estimée : 3-4h**

---

## CONTEXTE

L'écran Carte est l'écran d'accueil de Philia après le futur onboarding. Pour le MVP du Sprint 3, c'est le premier écran que l'enfant voit au lancement (`ecran_courant: "carte"` dans `app.py`). L'actuel `ecran_carte.py` est un stub : titre + boutons texte bruts. Cette tâche le remplace par un vrai écran visuel.

**Ce que T5 livre :**
- Une carte parchemin stylisée avec les 7 îles positionnées
- Des états visuels distincts : verrouillée / accessible / conquise
- Un porte-clés en sidebar (stub, crochet pour T7)
- La navigation : clic sur l'île accessible → `ecran_courant = "ile"`

---

## CONTRAINTES CONNUES

1. **Pas d'image de fond disponible.** `assets/images/` est vide. Utiliser CSS pur pour simuler l'ambiance parchemin (couleurs chaudes, texture via gradient). Pas besoin d'image réelle pour le MVP.

2. **T7 (jeu/cles.py) n'est pas encore fait.** Le porte-clés sidebar affiche un stub. Laisser un commentaire `# TODO T7: remplacer par jeu.cles.get_cles(enfant_id)`.

3. **T6 (onboarding) n'est pas encore fait.** `st.session_state.enfant_id` est `None` au démarrage. Le code doit gérer ce cas proprement : mode "développement" où `ile_1` est accessible par défaut.

4. **L'écran est une vitre.** Aucune logique pédagogique ici. Juste affichage et navigation.

5. **Pas de `st.components.v1.html()` pour l'interactivité.** Les clics vers Streamlit ne fonctionnent pas depuis du HTML custom. Utiliser les **boutons Streamlit natifs** stylisés par CSS injecté.

---

## APPROCHE TECHNIQUE

### CSS injection Streamlit

Injecter du CSS via `st.markdown(..., unsafe_allow_html=True)` en tête de `render_carte()`. Le CSS cible les boutons Streamlit natifs.

Pattern qui fonctionne pour colorer les boutons :

```python
st.markdown("""
<style>
/* Fond parchemin global */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f4e4bc 0%, #e8d5a3 50%, #d4c08a 100%);
}
/* Bouton île accessible — teal Philia */
div[data-testid="column"] button[kind="secondary"] {
    border-radius: 12px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)
```

> **Note** : les sélecteurs Streamlit évoluent. Si un sélecteur résiste, fallback : utiliser `st.container(border=True)` autour du bouton — c'est suffisant pour le MVP.

### Layout des îles

Utiliser `st.columns()` pour positionner les îles en 3 rangées approximant un archipel. Pas besoin de pixel-perfect — juste lisible et espacé.

**Disposition (3 rangées, 4 colonnes) :**

```
Rangée 1 :  [vide]   [île 1]  [île 2]  [vide]
Rangée 2 :  [île 3]  [vide]   [île 4]  [île 5]
Rangée 3 :  [vide]   [île 6]  [île 7]  [vide]
```

Implémentation :
```python
r1 = st.columns(4)
r2 = st.columns(4)
r3 = st.columns(4)

# Île 1 → r1[1], Île 2 → r1[2]
# Île 3 → r2[0], Île 4 → r2[2], Île 5 → r2[3]
# Île 6 → r3[1], Île 7 → r3[2]
```

### États visuels

```python
EMOJIS_ETAT = {
    "accessible":  "🏝️",
    "conquise":    "⭐",
    "verrouillee": "🔒",
}

LABELS_ETAT = {
    "accessible":  "Accessible",
    "conquise":    "Conquise",
    "verrouillee": "Verrouillée",
}
```

- `accessible` → bouton cliquable, couleur teal
- `conquise` → bouton cliquable (permet de rejouer), couleur or
- `verrouillee` → texte seul + emoji 🔒, aucun bouton

---

## STRUCTURE DU FICHIER

```python
"""
ui/ecran_carte.py — Écran Carte de l'Archipel.

Responsabilité : afficher la carte des 7 îles avec leurs états,
le porte-clés en sidebar, et naviguer vers l'île sélectionnée.
Aucune logique pédagogique ici. L'écran est une vitre.
"""
from __future__ import annotations
import streamlit as st
from config.constants import ILE_IDS, ILE_NOMS


# ── Données ──────────────────────────────────────────────────────────────────

def _get_etats_iles(enfant_id: int | None) -> dict[str, str]:
    """
    Retourne {ile_id: etat} pour chaque île.
    etat ∈ {"accessible", "conquise", "verrouillee"}

    Si enfant_id est None (mode dev / avant T6 onboarding) :
      → ile_1 = accessible, reste = verrouillée.
    Sinon, lit progression_iles depuis la DB.
    """
    ...


# ── Sidebar ──────────────────────────────────────────────────────────────────

def _render_sidebar_cles(enfant_id: int | None) -> None:
    """
    Affiche le porte-clés dans la sidebar.
    Stub Sprint 3 — sera câblé en T7.
    """
    with st.sidebar:
        st.markdown("### 🗝️ Porte-clés")
        # TODO T7: remplacer par jeu.cles.get_cles(enfant_id)
        st.markdown("*0 / 7 clés obtenues*")
        st.caption("Les clés s'obtiennent en maîtrisant chaque île.")


# ── CSS ───────────────────────────────────────────────────────────────────────

def _inject_css() -> None:
    """Injecte le CSS parchemin + états des îles."""
    ...


# ── Layout carte ─────────────────────────────────────────────────────────────

def _render_grille_iles(etats: dict[str, str]) -> None:
    """
    Affiche la grille 7 îles en 3 rangées via st.columns().
    Gère le clic et la navigation.
    """
    ...


# ── Point d'entrée ───────────────────────────────────────────────────────────

def render_carte() -> None:
    enfant_id = st.session_state.get("enfant_id")
    _inject_css()
    _render_sidebar_cles(enfant_id)
    st.title("🗺️ L'Ascension des Sept Îles")
    st.caption("Clique sur une île accessible pour commencer ta quête.")
    etats = _get_etats_iles(enfant_id)
    _render_grille_iles(etats)
```

---

## LOGIQUE `_get_etats_iles` — IMPLÉMENTATION COMPLÈTE

```python
def _get_etats_iles(enfant_id: int | None) -> dict[str, str]:
    if enfant_id is None:
        # Mode dev : ile_1 accessible, reste verrouillé
        return {
            ile_id: ("accessible" if ile_id == "ile_1" else "verrouillee")
            for ile_id in ILE_IDS
        }

    import sqlite3
    conn = sqlite3.connect("data/philia.db")
    try:
        rows = conn.execute(
            "SELECT ile_id, niveau_elevation, rite_reussi "
            "FROM progression_iles WHERE enfant_id = ?",
            (enfant_id,)
        ).fetchall()
    finally:
        conn.close()

    progression = {r[0]: {"niveau": r[1], "rite_reussi": bool(r[2])} for r in rows}

    etats: dict[str, str] = {}
    for i, ile_id in enumerate(ILE_IDS):
        p = progression.get(ile_id)
        if p and p["rite_reussi"]:
            etats[ile_id] = "conquise"
        elif i == 0 or (
            i > 0 and progression.get(ILE_IDS[i - 1], {}).get("rite_reussi")
        ):
            # Accessible si 1ère île, ou si la précédente est conquise
            etats[ile_id] = "accessible"
        else:
            etats[ile_id] = "verrouillee"
    return etats
```

---

## LOGIQUE `_render_grille_iles` — COMPORTEMENT

Chaque case île :

```python
# Pour une île accessible ou conquise :
if st.button(f"{emoji} {nom}", key=f"ile_btn_{ile_id}"):
    st.session_state.ile_courante = ile_id
    st.session_state.ecran_courant = "ile"
    st.rerun()

# Pour une île verrouillée :
st.markdown(f"🔒 **{nom}**")
st.caption("Verrouillée")
```

---

## PALETTE CSS

```
--carte-bg:       #f4e4bc   (parchemin clair)
--carte-bord:     #8b6914   (brun doré)
--ile-accessible: #3CE8C2   (teal Philia)
--ile-conquise:   #FFD700   (or)
--ile-verrouillee:#9CA3AF   (gris)
--texte-carte:    #3D2B1F   (brun foncé)
```

---

## CRITÈRES DE VALIDATION (liste de contrôle avant commit)

- [ ] `streamlit run app.py` démarre sans erreur ni warning Python
- [ ] L'écran carte s'affiche avec un fond non-blanc (parchemin)
- [ ] Île 1 est visuellement distincte (couleur/emoji différents des îles verrouillées)
- [ ] Clic sur Île 1 → `ecran_courant = "ile"`, `ile_courante = "ile_1"`, rerun propre
- [ ] Sidebar affiche "0 / 7 clés obtenues"
- [ ] Aucun import de `jeu.cles` (T7 pas encore fait)
- [ ] Aucune régression sur les écrans `ile` et `session`

---

## COMMIT ATTENDU

```
feat: T5 — écran Carte de l'Archipel opérationnel
```

---

## NE PAS TOUCHER

- `app.py` — routing déjà câblé, rien à modifier
- `config/constants.py` — ILE_IDS et ILE_NOMS utilisés tels quels
- Tout fichier hors `ui/ecran_carte.py`

---

*Brief T5 — Philia Summer Quest Sprint 3*
*Produit par l'Architecte (Cowork) — 5 juin 2026*
