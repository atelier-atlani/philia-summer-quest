# Sprint 3 — T8.1 : Intégration des planches BD dans le flow session

**Brief Implementer — Claude Code**
**Rôle** : Implementer (Claude Code dans VS Code)
**Reviewer** : Architect (Cowork) — audit avant merge sur develop
**Version** : V2 — corrections audit Architect (28 juin 2026)
**Branche cible** : `feat/T8.1-planches-bd-modal` → merge sur `develop`

---

## 1. ÉTAT DU CODE AVANT T8.1

### Ce qui existe

| Fichier | Rôle | Pertinent pour T8.1 |
|---|---|---|
| `pedagogie/session_engine.py` | State machine des sessions | Oui — fournit `est_terminee`, `index_exercice`, `mode` |
| `pedagogie/modes.py` | Enum Mode + MODES_ACTIFS | Oui — BILAN déclaré, non activé |
| `ui/ecran_session.py` | Écran session Streamlit | Oui — point d'intégration principal |
| `data_layer/joueurs.py` | CRUD joueur + JSON colonnes | Oui — modèle à suivre pour la persistance |
| `data_layer/schema.sql` | Schéma SQLite | Oui — migration nécessaire |
| `jeu/recompenses.py` | Clés + cristaux | Modèle de référence |
| `assets/narratif/ile_1/` | Planches BD et illustrations | Oui — fichiers cibles |

### Assets BD existants dans `assets/narratif/ile_1/`

```
planche_bd_c1_fille.png        ✅ présent
planche_bd_c1_garcon.png       ✅ présent
planche_bd_c1_part2_fille.png  ✅ présent
planche_bd_c1_part2_garcon.png ✅ présent
planche_bd_c2_*.png            ❌ absent (placeholder)
planche_bd_c3_*.png            ❌ absent (placeholder)
planche_bd_c4_*.png            ❌ absent (placeholder)
planche_bd_c5_*.png            ❌ absent (placeholder)
```

### Ce qui manque / bloque T8.1

1. **Mode BILAN non activé** : `MODES_ACTIFS = frozenset({Mode.DECOUVERTE})` — le prompt `mode_bilan.txt` existe, mais le mode n'est pas dans l'ensemble actif. T8.1 doit activer BILAN.
2. **Aucun composant modal** : Streamlit n'a pas de modal natif pre-1.31.
3. **Aucune colonne de persistance** : la table `joueurs` n'a pas de colonne `planches_bd_vues`.
4. **Pas de fichier placeholder** : `assets/narratif/_placeholder/` est vide.
5. **Clé normalisée manquante** : `META_SESSION_X` n'expose pas `planche_key`. **Voir D23 : `planche_key` est la seule clé autorisée pour construire un chemin d'asset — jamais `meta["concept"]`.**

---

## 2. DÉCISIONS ARCHITECTURALES

### D-T8.1-A — Déclencheur MVP : fin de session = fin de chapitre

Le spec dit "après le Mode Bilan d'un chapitre Cx". En l'état du code, session 1 = chapitre C1.

**Implémentation retenue** :
- Activer `Mode.BILAN` dans `MODES_ACTIFS`
- Quand l'élève valide le **dernier exercice**, l'engine transite **automatiquement** vers Mode.BILAN (transition implicite, sans clic)
- Le dialogue de Bilan avec Archimède se déroule normalement
- Le bouton "Terminer le chapitre ✓" n'apparaît qu'après **au moins 1 tour** en Mode BILAN (voir D-T8.1-F)
- À la fermeture du Bilan : le flag `st.session_state.planche_bd_a_afficher` est posé

### D-T8.1-B — `st.dialog` en priorité, CSS en fallback

Tester `st.dialog` (Streamlit >= 1.31). Fallback CSS si limitation rencontrée. Documenter le choix en commentaire en tête du composant.

### D-T8.1-C — Séquence multi-planches pour C1

C1 a deux planches. Séquence via `st.session_state.planche_bd_index`. **Reset systématique à 0** quand le flag `planche_bd_a_afficher` est posé (évite un bug latent si l'utilisateur ferme le modal en cours de séquence).

### D-T8.1-D — Persistance JSON dans `joueurs.planches_bd_vues`

Suivre le pattern `cles_obtenues` / `cristaux_obtenus` :
- Colonne TEXT DEFAULT `'{}'`
- Format : `{"ile_1_c1": "2026-07-01T10:00:00Z", "ile_1_c1_part2": "..."}`
- **Clé = `f"{ile_id}_{planche_key}"`** où `planche_key` ∈ `{"c1", "c1_part2", "c2", ...}`
- `marquer_planche_vue("ile_1", "c1")` → clé SQLite `"ile_1_c1"` (PAS `"ile_1_planche_bd_c1"`)

### D-T8.1-E — Clé normalisée `planche_key` (D23)

Ajouter `"planche_key"` dans chaque `META_SESSION_X`. Sessions sans planche → `None`. Le composant modal construit les chemins via `_SEQUENCE_PLANCHES[planche_key]`.

### D-T8.1-F — Gating du bouton "Terminer le chapitre ✓" (D24)

**Le bouton n'apparaît PAS dès l'arrivée au dernier exercice.** Il devient visible uniquement après au moins 1 tour en Mode BILAN.

Mécanisme :
- Dernier exercice validé → `engine.transitionner(Mode.BILAN)` automatiquement
- `nb_tours_bilan` (attribut `SessionEngine`) s'incrémente à chaque tour en Mode BILAN
- Condition d'affichage : `engine.mode == Mode.BILAN AND engine.nb_tours_bilan >= 1`

---

## 3. FICHIERS À CRÉER / MODIFIER

### Créer

```
ui/modal_planche_bd.py          ← nouveau composant modal BD
data_layer/planches_bd.py       ← fonctions de persistance planches vues
```

### Modifier

```
pedagogie/modes.py              ← activer Mode.BILAN dans MODES_ACTIFS
pedagogie/session_engine.py     ← ajouter nb_tours_bilan + echanger_en_bilan()
pedagogie/contenu_ile1.py       ← ajouter "planche_key" aux META_SESSION_X
data_layer/schema.sql           ← annotation migration (ALTER TABLE dans db.py)
data_layer/db.py                ← _appliquer_migrations() via PRAGMA
data_layer/joueurs.py           ← fonctions lire/ecrire planches_bd_vues
ui/ecran_session.py             ← intégration modal + gating bouton
```

### Asset à générer

```
assets/narratif/_placeholder/placeholder_planche_bd.png
```

---

## 4. IMPLÉMENTATION DÉTAILLÉE

### 4.1 `pedagogie/modes.py`

```python
MODES_ACTIFS: frozenset[Mode] = frozenset({
    Mode.DECOUVERTE,
    Mode.PRATIQUE,
    Mode.BILAN,
})
```

### 4.2 `pedagogie/contenu_ile1.py`

Ajouter `"planche_key"` dans chaque `META_SESSION_X` (D23) :

```python
META_SESSION_1: dict = {
    "id": "ile1_s1",
    "titre": "Le Pont Fracturé",
    "concept": "C1 — Sens d'une fraction",
    "cristal": "Cristal du Partage",
    "planche_key": "c1",          # ← D23 : clé filesystem, jamais parser "concept"
    "situation_narrative": (...),
}
# META_SESSION_2 → "planche_key": "c2"
# META_SESSION_3 → "planche_key": "c3"
# META_SESSION_4 → "planche_key": "c4"
# META_SESSION_5 → "planche_key": "c5"
```

### 4.3 `data_layer/schema.sql` + `data_layer/db.py`

**`schema.sql`** — ajouter en commentaire de fin (la colonne est créée via `_appliquer_migrations`) :

```sql
-- Sprint 3 T8.1 — planches_bd_vues
-- Colonne gérée via _appliquer_migrations() dans db.py (pattern PRAGMA).
-- Format : {"ile_1_c1": "ISO8601", ...} — clé = f"{ile_id}_{planche_key}" (D-T8.1-D)
```

**`data_layer/db.py`** — remplacer `create_db()` :

```python
def create_db() -> None:
    """Crée data/philia.db, applique le schéma de base et les migrations."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = _SCHEMA_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(_DB_PATH) as conn:
        conn.executescript(schema)
        _appliquer_migrations(conn)
        conn.commit()


def _appliquer_migrations(conn: sqlite3.Connection) -> None:
    """
    Applique les migrations ALTER TABLE via PRAGMA table_info().
    Idempotent. Toutes les futures migrations Sprint 4+ s'ajoutent ici.
    """
    cols = {row[1] for row in conn.execute("PRAGMA table_info(joueurs)")}

    # Sprint 3 T7 — filet de sécurité (déjà dans schema.sql)
    if "cles_obtenues" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN cles_obtenues TEXT DEFAULT '{}'")
    if "cristaux_obtenus" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN cristaux_obtenus TEXT DEFAULT '{}'")

    # Sprint 3 T8.1
    if "planches_bd_vues" not in cols:
        conn.execute("ALTER TABLE joueurs ADD COLUMN planches_bd_vues TEXT DEFAULT '{}'")
```

### 4.4 `data_layer/joueurs.py`

Ajouter en fin de fichier (après les fonctions T7) :

```python
# ── Sprint 3 T8.1 — Planches BD vues ─────────────────────────────────────────

def lire_planches_bd_vues(joueur_id: int) -> dict:
    """
    Clé = f"{ile_id}_{planche_key}" (D-T8.1-D / D23).
    Retourne {} si NULL ou vide.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT planches_bd_vues FROM joueurs WHERE id = ?",
            (joueur_id,),
        ).fetchone()
    if row is None or not row[0]:
        return {}
    return json.loads(row[0])


def ecrire_planches_bd_vues(joueur_id: int, planches: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE joueurs SET planches_bd_vues = ? WHERE id = ?",
            (json.dumps(planches, ensure_ascii=False), joueur_id),
        )
        conn.commit()
```

### 4.5 `data_layer/planches_bd.py` (nouveau)

```python
"""
data_layer/planches_bd.py — Persistance de l'historique des planches BD vues.
Sprint 3 T8.1

Public API :
    marquer_planche_vue(ile_id, planche_key)  -> None
    planche_deja_vue(ile_id, planche_key)     -> bool

Clé SQLite = f"{ile_id}_{planche_key}" (D-T8.1-D)
Exemples : "ile_1_c1", "ile_1_c1_part2", "ile_1_c2"
"""

from __future__ import annotations
from datetime import datetime, timezone
from data_layer.joueurs import (
    charger_joueur_courant,
    lire_planches_bd_vues,
    ecrire_planches_bd_vues,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _joueur_id() -> int:
    joueur = charger_joueur_courant()
    if joueur is None:
        raise RuntimeError("Aucun joueur courant")
    return joueur["id"]


def marquer_planche_vue(ile_id: str, planche_key: str) -> None:
    """
    Idempotent : si déjà vue, met à jour le timestamp.
    planche_key : "c1", "c1_part2", "c2"... (D23 / D-T8.1-D)
    """
    joueur_id = _joueur_id()
    planches = lire_planches_bd_vues(joueur_id)
    planches[f"{ile_id}_{planche_key}"] = _now_iso()
    ecrire_planches_bd_vues(joueur_id, planches)


def planche_deja_vue(ile_id: str, planche_key: str) -> bool:
    joueur_id = _joueur_id()
    return f"{ile_id}_{planche_key}" in lire_planches_bd_vues(joueur_id)
```

### 4.6 `ui/modal_planche_bd.py` (nouveau)

```python
"""
ui/modal_planche_bd.py — Modal full-screen pour l'affichage des planches BD.
Sprint 3 T8.1

Implémentation : st.dialog (Streamlit >= 1.31).
Fallback CSS documenté en commentaire si limitation rencontrée.
"""

from __future__ import annotations
import os
import streamlit as st
from data_layer.planches_bd import marquer_planche_vue

_ASSETS_NARRATIF = "assets/narratif"
_PLACEHOLDER = f"{_ASSETS_NARRATIF}/_placeholder/placeholder_planche_bd.png"

# Mapping planche_key → séquence de suffixes (D-T8.1-C / D23)
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
    Affiche le modal avec la (ou les) planche(s) BD du chapitre.
    planche_bd_index doit être resetté à 0 avant l'appel (garanti par ecran_session).

    # Fallback CSS si st.dialog pose problème :
    #   Remplacer @st.dialog par st.markdown avec overlay CSS + st.image.
    """
    sequence = _SEQUENCE_PLANCHES.get(planche_key, [planche_key])
    index_key = "planche_bd_index"
    if index_key not in st.session_state:
        st.session_state[index_key] = 0
    index = st.session_state[index_key]

    @st.dialog("", width="large")
    def _modal():
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
                # Clé = f"{ile_id}_{suf}" — pas de préfixe "planche_bd_" (D-T8.1-D)
                for suf in sequence:
                    marquer_planche_vue(ile_id, suf)
                st.session_state.pop(index_key, None)
                st.session_state.planche_bd_a_afficher = None
                st.session_state.ecran_courant = "carte" if chapitres_restants == 0 else "session"
                st.rerun()
        else:
            if st.button("Suite →", use_container_width=True):
                st.session_state[index_key] = index + 1
                st.rerun()

    _modal()
```

### 4.7 `ui/ecran_session.py`

**Imports à ajouter** :
```python
from ui.modal_planche_bd import afficher_modal_planche_bd
from data_layer.joueurs import charger_joueur_courant
from pedagogie.modes import Mode
from pedagogie.session_engine import PhaseSession
```

**Helper à ajouter** :
```python
def _numero_chapitre(planche_key: str | None) -> int:
    """Retourne le numéro ordinal du chapitre à partir de sa clé (D23)."""
    return {"c1": 1, "c2": 2, "c3": 3, "c4": 4, "c5": 5}.get(planche_key or "", 1)
```

**`render_session()` complète** :

```python
def render_session() -> None:
    meta, exercices = _charger_session_1()

    # ── Vérification flag modal planche BD ─────────────────────────────────
    if st.session_state.get("planche_bd_a_afficher"):
        joueur = charger_joueur_courant()
        genre = joueur["avatar_genre"] if joueur else "fille"
        afficher_modal_planche_bd(
            ile_id="ile_1",
            planche_key=st.session_state["planche_bd_a_afficher"],
            genre=genre,
            chapitre_num=_numero_chapitre(meta.get("planche_key")),
            chapitres_total=5,
        )
        return
    # ───────────────────────────────────────────────────────────────────────

    st.title(meta["titre"])
    st.info(meta["situation_narrative"])
    st.divider()

    if st.session_state.get("session_active") is None:
        engine = _init_engine(exercices, meta["situation_narrative"])
    else:
        engine = SessionEngine.from_dict(st.session_state.session_active)

    n_total   = len(engine.exercices)
    n_courant = engine.index_exercice + 1
    st.caption(f"{meta['concept']} · Exercice {n_courant} / {n_total}")

    render_chat(engine)

    # Transition automatique vers Mode.BILAN au dernier exercice (D-T8.1-A / D-T8.1-F)
    # Point d'insertion : après render_chat(), qui peut modifier engine.index_exercice
    # via une validation de réponse.
    if engine.est_dernier_exercice and engine.mode != Mode.BILAN and not engine.est_terminee:
        engine.transitionner(Mode.BILAN)

    st.session_state.session_active = engine.to_dict()

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
                    st.rerun()

        elif (
            engine.mode == Mode.BILAN
            and engine.nb_tours_bilan >= 1   # Gating D-T8.1-F / D24
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
                    st.session_state.planche_bd_a_afficher = planche_key
                    st.session_state.planche_bd_index = 0  # reset systématique (D-T8.1-C)
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
```

### 4.8 Placeholder asset

```python
# scripts/generate_placeholder_bd.py
from PIL import Image, ImageDraw
import os

W, H = 800, 1000
img = Image.new("RGB", (W, H), color=(245, 240, 232))
draw = ImageDraw.Draw(img)
draw.ellipse([250, 200, 550, 500], fill=(200, 220, 240))
draw.ellipse([300, 280, 500, 450], fill=(220, 200, 240))
draw.text((W//2, 600), "Planche en cours d'illustration",
          fill=(80, 70, 60), anchor="mm")
draw.text((W//2, 660), "la suite de l'aventure t'attend bientôt !",
          fill=(120, 110, 100), anchor="mm")
os.makedirs("assets/narratif/_placeholder", exist_ok=True)
img.save("assets/narratif/_placeholder/placeholder_planche_bd.png")
print("Placeholder généré.")
```

```bash
pip install Pillow --break-system-packages
python scripts/generate_placeholder_bd.py
```

### 4.9 `pedagogie/session_engine.py` — compteur `nb_tours_bilan`

**Attribut** (dans le `@dataclass`) :
```python
nb_tours_bilan: int = 0          # tours de dialogue en Mode BILAN (D-T8.1-F)
```

**Méthode** (après `transitionner()`) :
```python
def echanger_en_bilan(self) -> None:
    """
    Incrémente nb_tours_bilan si on est en Mode BILAN.
    Appelé dans repondre() a chaque tour quand mode == BILAN.
    Sert au gating du bouton "Terminer le chapitre" (D-T8.1-F / D24).
    """
    if self.mode == Mode.BILAN:
        self.nb_tours_bilan += 1
```

**Intégration dans `repondre()`** :
```python
def repondre(self, message: str) -> MentorOutput:
    # ... code existant ...
    reponse = mentor.repondre(...)
    self.historique.append({"role": "user", "content": message})
    self.historique.append({"role": "assistant", "content": reponse})

    # Compteur BILAN — gating bouton Terminer chapitre (D-T8.1-F)
    self.echanger_en_bilan()

    if message.strip().lower() in _MOTS_FIN:
        self.phase = PhaseSession.TERMINEE

    return MentorOutput(message=reponse, etat=self.etat)
```

**Sérialisation `to_dict()`** — ajouter :
```python
"nb_tours_bilan": self.nb_tours_bilan,
```

**Désérialisation `from_dict()`** — ajouter :
```python
engine.nb_tours_bilan = d.get("nb_tours_bilan", 0)
```

---

## 5. TESTS MANUELS À DOCUMENTER

```python
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
```

---

## 6. CRITÈRES D'ACCEPTANCE

| Critère | Fichier |
|---|---|
| Bouton visible seulement après ≥ 1 tour BILAN (D24) | `session_engine.py` + `ecran_session.py` |
| Bonne planche selon le genre | `ecran_session.py` + `modal_planche_bd.py` |
| Full-screen desktop + mobile | `modal_planche_bd.py` |
| Ratio image sans déformation | `modal_planche_bd.py` |
| Texte positionnement correct | `modal_planche_bd.py` |
| "Continuer la quête" redirige correctement | `modal_planche_bd.py` |
| Placeholder si fichier absent | `modal_planche_bd.py` |
| Clé SQLite `ile_1_c1` (pas `ile_1_planche_bd_c1`) | `planches_bd.py` |
| Reset `planche_bd_index = 0` à la pose du flag | `ecran_session.py` |
| Bouton "Retour à l'île" masqué en Mode BILAN | `ecran_session.py` |
| Pas de régression T1-T7 | Tests 1-6 |

---

## 7. PROCÉDURE DE LIVRAISON

```bash
git checkout develop && git pull
git checkout -b feat/T8.1-planches-bd-modal

# Ordre d'implémentation :
# pedagogie/modes.py
# → pedagogie/session_engine.py (nb_tours_bilan + echanger_en_bilan)
# → pedagogie/contenu_ile1.py (planche_key)
# → data_layer/db.py (_appliquer_migrations via PRAGMA)
# → data_layer/schema.sql (commentaire migration)
# → data_layer/joueurs.py (lire/ecrire planches_bd_vues)
# → data_layer/planches_bd.py (nouveau)
# → ui/modal_planche_bd.py (nouveau)
# → ui/ecran_session.py (intégration + gating)
# → scripts/generate_placeholder_bd.py (générer l'asset)

python scripts/generate_placeholder_bd.py

# Tests manuels 1 à 6 (section 5)

git add .
git commit -m "feat(T8.1): modal planche BD après Bilan (gating nb_tours_bilan)

- Activer Mode.BILAN dans MODES_ACTIFS
- SessionEngine : nb_tours_bilan + echanger_en_bilan() (D-T8.1-F)
- Transition auto vers BILAN au dernier exercice
- Nouveau composant ui/modal_planche_bd.py (st.dialog)
- Nouveau module data_layer/planches_bd.py
- Migration SQLite via PRAGMA : planches_bd_vues
- Placeholder généré (scripts/generate_placeholder_bd.py)
- Gating bouton Terminer chapitre par nb_tours_bilan >= 1 (D24)
- Reset systématique planche_bd_index (D-T8.1-C)
- Clé SQLite ile_1_c1 conforme D-T8.1-D"

git push origin feat/T8.1-planches-bd-modal
```

---

## 8. HORS SCOPE T8.1

- Animation d'entrée/sortie du modal (V1.1)
- Son d'ambiance sur planche BD (V1.1)
- Menu "carnet de voyage" (V1.1)
- Rite intro / rite fin (T8.4)
- Seuil `nb_tours_bilan` configurable (V1.1, actuellement hardcodé à 1)

---

*Brief T8.1 — Planches BD en modal. Version V2.*
*3 corrections bloquantes + 4 améliorations appliquées (audit Architect 28 juin 2026).*
*À implémenter par Claude Code. À auditer par l'Architect avant merge sur develop.*
