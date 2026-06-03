# Audit de Dettes Techniques — Philia Summer Quest
*Produit par l'Architecte (Claude.ai Cowork) — session du 2026-06-03*
*Diagnostic uniquement — pas de plan de résolution.*

---

## Famille 1 — Dette de code

### 1.1 — TODO/FIXME dans le code Python
Un seul TODO dans le code actif :
- `core/avatar.py` ligne 139 : `# TODO : appel API D-ID / HeyGen`

**Criticité : Mineur** — Phase 2 assumée, pas bloquant MVP. **Effort : 1 sprint (Sprint 4).**

---

### 1.2 — Modules importés mais code mort

**`core/faq_contract.py`** — 160 lignes de logique anti-hallucination FAQ immobilière (gate "Non couvert", 5 sections, section 5 une ligne). N'est importé nulle part dans Philia (pédagogie/, ui/, app.py). Code 100% hérité IAXEL, actif dans le repo mais mort dans le produit.

**Criticité : Important** — confusion pour l'Implementer. **Effort : 1h (archivage ou suppression).**

**`core/avatar.py`** — importé uniquement dans sa propre docstring (`Usage:` en commentaire), pas dans le reste du projet Philia.

**Criticité : Important** — code orphelin, risque de dérive. **Effort : 1h (vérifier si Sprint 3 le câble, sinon archiver).**

**`core/tts.py` + `core/tts_elevenlabs.py`** — importés uniquement depuis `training/quiz_ui.py` (module IAXEL). Pas importés dans les modules Philia.

**Criticité : Mineur** — prévu Sprint 4, aucun câblage Philia pour l'instant. **Effort : 1h de vérification, 1 jour de câblage Sprint 4.**

**`core/sanitizer.py`** — non importé dans aucun module Philia actif.

**Criticité : Mineur. Effort : 1h.**

`core/rag.py` — importé dans `pedagogie/mentor.py` ✅ — pas mort.

---

### 1.3 — Modules stub (squelettes vides ou placeholder)

**`jeu/__init__.py`** — vide. Tout le chantier C4 Sprint 3 est à zéro en code.

**Criticité : Important.** **Effort : 1 sprint (Sprint 3).**

**`ui/ecran_carte.py`** — version placeholder Sprint 2 (boutons bruts, aucun visuel carte, aucune logique de progression). Caption littérale `"Carte de l'archipel — Sprint 3"`. C'est l'écran d'entrée affiché à l'enfant.

**Criticité : Important. Effort : 1 sprint (Sprint 3).**

**`ui/ecran_ile.py`** — même état. Caption `"Écran île — Sprint 3"`, aucun visuel.

**Criticité : Important. Effort : 1 sprint (Sprint 3).**

---

### 1.4 — Scripts racine — héritage IAXEL oubliés hors `_archive_iaxel/`

| Fichier | Verdict | Criticité |
|---|---|---|
| `build_index.py` | IAXEL — indexe `base_connaissances.json` (KB immo). Code mort Philia. | Important |
| `build_kb.py` | IAXEL — lit des PDF immo, produit KB immo. Code mort Philia. | Important |
| `build_kb_from_pages.py` | IAXEL — transforme `pages_extraites.json` → KB immo. Code mort Philia. | Important |
| `extract_pdf.py` | IAXEL — extrait des PDF. Potentiellement réutilisable, mais non référencé. | Mineur |
| `search_kb.py` | IAXEL — interroge la KB immo FAISS. Code mort Philia. | Important |
| `test_tts.py` | IAXEL — teste OpenAI TTS avec formateur immo. Code mort Philia. | Important |
| `scripts/build_rag_index.py` | ✅ Philia — indexe `data/sources_maths/`. Actif et utile. | — |
| `scripts/index_marche_modules.py` | IAXEL — indexe 100 modules marché immo. Code mort Philia. | Important |
| `scripts/run_ia_tests.py` | IAXEL — tests d'assimilation marché. Code mort Philia. | Important |
| `scripts/tests_contract_faq.py` | IAXEL — tests du contrat FAQ. Code mort Philia. | Important |

**6 fichiers racine + 3 scripts/ sont des dettes IAXEL hors `_archive_iaxel/`.**
**Criticité globale : Important. Effort : 1h (archivage ou suppression).**

---

## Famille 2 — Dette de contenu

### 2.1 — Format des documents pédagogiques

**`ile-1-nombres-brises-CONTENU.md`** — au format Sprint 2 (énoncé, réponse, solution_etapes, indices, erreurs_typiques). Les indices sont au format verbal (3 niveaux : léger / moyen / fort). Aucun champ `visuel:`, `manipulation:`, `relance_concrete:` ou équivalent multimodal.

Les occurrences de "visuel/concret/manipulation" dans le fichier sont dans des champs narratifs libres (`si_echec:`, descriptions du Rite d'Élévation), pas dans des champs structurés YAML.

**→ L'Île 1 est au format Sprint 2, pas au format multimodal Sprint 3.**
**Criticité : Important** — l'Île 1 sert de modèle pour les Îles 2 et 3. **Effort : 1 jour.**

---

### 2.2 — Modes pédagogiques activés dans `prompts/mentor/`

Présents : `_shared_persona.txt`, `_shared_guardrails.txt`, `mode_decouverte.txt` — **1 mode sur 5 activé**.

Manquants : `mode_pratique.txt`, `mode_validation.txt`, `mode_consolidation.txt`, `mode_bilan.txt`.

Le `SessionEngine` et `modes.py` sont câblés pour 5 modes mais 4 ne peuvent pas être appelés sans leur prompt.

**Criticité : Important. Effort : 1 sprint (Sprint 3).**

---

### 2.3 — Document gamification archivé mais référencé

`archive-philia-gamification-spec-v1.md` préfixé `archive-` dans `.claude/pedagogie/` — archivé in-situ mais toujours référencé dans le bilan structurel §3.4 et §N8 comme document actif.

**Criticité : Mineur. Effort : 1h.**

---

## Famille 3 — Dette de versionnement

### 3.1 — `git status` au moment de l'audit (2026-06-03)

- `learnings.md` modifié, non commité (modifications session)
- `assets/mentor/garçon/` non tracké — problème d'encodage de l'accent sur le volume monté macOS. Le dossier a été renommé en `garcon` (sans accent) pour résoudre. Commit en attente.

**Criticité : Importante** — sans commit, les avatars garçon manquent au clone. **Effort : 1h.**

---

### 3.2 — Nommages incohérents dans `.claude/`

La majorité des fichiers suivent le préfixe `philia-`. Exceptions sans préfixe dans `contexts/` : `guardrails-pedagogiques.md`, `contraintes-rgpd.md`, `nommage.md`, `produit-philia.md`, `stack-technique.md`. Dans `memory/` : convention sans préfixe cohérente entre elles (probable délibérée).

**Criticité : Mineur. Effort : 1h.**

---

### 3.3 — Doublons suspectés

- `build_index.py` (racine) vs `scripts/build_rag_index.py` : deux indexeurs FAISS, l'un IAXEL, l'autre Philia. Doublon de rôle perçu.
- `archive-philia-gamification-spec-v1.md` dans `.claude/pedagogie/` : archivée in-situ mais toujours référencée dans §3.4 et §N8 du bilan structurel comme document actif.

**Criticité : Mineur. Effort : 1h.**

---

## Famille 4 — Dette d'architecture (compilation explicite depuis learnings.md et decisions.md)

| Dette | Source | Report déclaré | Criticité |
|---|---|---|---|
| Décision architecture RAG non tranchée (Options A/B/C) alors que le RAG est appelé à chaque tour mentor | learnings.md | Sprint 3 ou 4 | **Critique** |
| Détection automatique de réussite (structured output ou juge Haiku) | learnings.md | Sprint 3 | Important |
| Enrichissement prompts pour multimodalité de relance (4 canaux) | learnings.md | Sprint 3 | Important |
| Champ `visuel:` dans YAML + affichage SVG dans `ecran_session.py` | learnings.md | Sprint 3 | Important |
| Calibration accueil des bonnes réponses dans `mode_decouverte.txt` | learnings.md | Sprint 3 | Important |
| Vérification identifiant LLM daté `claude-sonnet-4-6-20250218` (figer version) | bilan-structurel §N7 | À planifier | Mineur |
| Nettoyage `data/sources_maths/` (433 fichiers, doublons) | bilan-structurel §3.3 | Hors sprint critique | Mineur |
| Garantie `git status` en fin de session (doc hors Git silencieux Sprint 2) | learnings.md | Règle opérationnelle actée | Mineur |

---

## Famille 5 — Dette de documentation

### 5.1 — README.md obsolète sur trois points

1. Stack déclarée : `Python 3.12 + OpenAI GPT-4o` → stack réelle : `Python 3.11.14 + Anthropic Claude Sonnet 4.6`
2. État déclaré : `"Sprint 1 terminé"` → Sprint 2 terminé
3. Aucune mention du Voyage / Cahier d'Aventures, ni de la gamification révisée

**Criticité : Important** — premier fichier lu par tout nouvel intervenant. **Effort : 1h.**

---

### 5.2 — Sections obsolètes dans le bilan structurel

- **§3.4 (Chantier C4)** : liste des modules `jeu/` (`jeu/elevation.py`, `jeu/radar.py`, `jeu/recompenses.py`) et référence à `gamification-spec-v1` comme document fondateur — écrasé par D12 mais pas mis à jour dans ce paragraphe.
- **§N8 (Index des documents)** : `philia-gamification-spec-v1.md` listée comme document actif alors qu'archivée.
- **§3.2 et §3.4** : mentions de "cristaux", "paliers d'élévation", "Rite d'Élévation" comme mécaniques actives — la terminologie Voyage n'a remplacé l'ancienne que dans la Tâche 5 du §N7, pas dans le reste du document.

**Criticité : Important** — risque de confusion ancienne/nouvelle gamification pour l'Implementer Sprint 3. **Effort : 2h.**

---

## Synthèse par criticité

**Critique (1)**
- Décision architecture RAG non tranchée — RAG appelé à chaque tour mentor sur contenu source non nettoyé.

**Important (10)**
- 4 modes mentors absents (`prompts/mentor/`)
- Île 1 non multimodale (format Sprint 2)
- 6 scripts racine + 3 scripts/ IAXEL oubliés hors archive
- `core/faq_contract.py` orphelin (héritage IAXEL)
- `assets/mentor/garcon/` (ex-`garçon/`) hors Git — commit en attente
- `ui/ecran_carte.py` et `ui/ecran_ile.py` placeholders Sprint 2
- Tout le dossier `jeu/` vide (C4 à zéro en code)
- README.md obsolète (stack, état, gamification)
- Bilan structurel §3.4 et §N8 contradictoires avec D12

**Mineur (6)**
- 1 TODO D-ID/HeyGen dans `core/avatar.py`
- `core/avatar.py`, `core/sanitizer.py` orphelins dans Philia
- Nommages `contexts/` inconsistants (préfixe `philia-` vs sans préfixe)
- Doublon de rôle indexeurs FAISS (racine vs `scripts/`)
- Figer la version LLM (identifiant daté)
- `archive-philia-gamification-spec-v1.md` toujours référencée dans bilan structurel

---

*Audit produit en session Cowork — 2026-06-03. Référence pour la planification du Sprint 3.*
