# Dette technique post-T8.5

**Ouvert** : 15 juillet 2026
**À traiter** : Sprint polish semaine 4 ou plus tôt selon impact test cobaye

---

## Dette 1 — Mécanique `<a href>` fragile dans ecran_carte.py

**Localisation** : `ui/ecran_carte.py`

**Description** : navigation Carte → Île via `<a href="?ile=X">` au lieu de `st.button()` ou `st.query_params`. Fonctionne au clic souris mais échoue en tests automatisés.

**Correctif proposé** : refactor vers un pattern Streamlit natif (`st.button()` avec `st.session_state["ile_courante"]` puis `st.rerun()`).

**Effort estimé** : 30 min.

**Priorité** : moyenne — à traiter si test cobaye révèle problème réel, sinon Sprint polish.

---

## Dette 2 — Textes non discriminants entre écrans successifs

**Localisation** : `ui/ecran_presentation_archipel.py` + sous-étape arrivée de `ui/ecran_ile.py`

**Description** : confusion visuelle/narrative entre présentation archipel et arrivée Île 1 (voir Bug UI 3 dans polish-bugs-ui.md).

**Correctif proposé** : réécriture des textes narratifs pour marquer clairement la distinction (archipel = 7 îles + mission globale, arrivée = Syracuse spécifique).

**Effort estimé** : 1h (réécriture + audit visuel).

**Priorité** : moyenne (Sprint polish).

---

## Dette 3 — Assets `ecran_session_<genre>.png` à refondre

**Localisation** : `assets/narratif/globaux/ecran_session_<genre>.png`

**Description** : les images actuelles contiennent une bulle vide destinée au chat, mais Streamlit ne peut pas y intégrer le widget. La bulle reste vide.

**Correctif proposé** : re-générer les 2 images en variante "bandeau décoratif sans bulle vide" via Midjourney.

**Effort estimé** : 1-2h (nouvelles prompts + audit + intégration).

**Priorité** : haute (Sprint polish avant test cobaye final).

---

## Dette 4 — Auditer toutes les tailles d'images (`st.image` sans `use_container_width`)

**Localisation** : tous les fichiers de `ui/`

**Description** : les images narratives sont trop petites (Bug UI 2). Manque d'immersion.

**Correctif proposé** : audit systématique + ajout `use_container_width=True` par défaut.

**Effort estimé** : 1h.

**Priorité** : haute (Sprint polish).

---

## Suivi

| Dette | État | Deadline |
|---|---|---|
| D1 (`<a href>`) | ⏳ | Selon test cobaye |
| D2 (textes archipel/île) | ⏳ | Sprint polish |
| D3 (assets chat) | ⏳ | Sprint polish avant test final |
| D4 (tailles images) | ⏳ | Sprint polish |

---

*Ouvert par Product Architect (Claude.ai) le 15 juillet 2026 suite au merge T8.5 f77dc86.*