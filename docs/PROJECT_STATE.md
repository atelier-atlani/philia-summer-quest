# Agent IA Formateur Immobilier — État du projet (checkpoint)

## 0) Objectif produit
Construire une application terminal (puis évolutive) de **formateur IA immobilier terrain** utilisable par des conseillers :
- modes pédagogiques (parcours / jeu de rôle / FAQ / mémo / plan)
- ancrage **RAG** sur documents internes (zéro invention)
- options audio TTS
- audit pédagogique conforme CHARTE V2 (audit-only, anti-correction)

## 1) Architecture actuelle
- `agent_formateur.py` : application terminal (menu + modes)
- `core/rag.py` : FAISS + embeddings + build_context + trace debug
- `core/sanitizer.py` : `sanitize_brand()` + `brand_block()` anti-marque / filtrage sorties
- `prompts/prompt_audit_v2.txt` : prompt audit V2 (audit-only, anti-confusion)
- `scripts/doctor.py` : checks compilation/import + sanity RAG/prompt/guard

## 2) Modes (dans agent_formateur.py)
- Mode 1 : Parcours guidé (modules) avec `ask_and_render()`
- Mode 2 : Jeu de rôle vendeur/agent + débrief (voix OK)
- Mode 3 : FAQ courte (format strict 5 sections) + TTS optionnel
- Mode 4 : Fiche mémo (via `ask_and_render`)
- Mode 5 : Plan d’entretien (via `ask_and_render`)
- Mode 6 : Audit interne (Charte V2) :
  - charge `prompts/prompt_audit_v2.txt`
  - `audit_only_guard()` coupe toute dérive (version corrigée, etc.)
- (Mode 7 : “Réponse formateur audit-ready” si présent dans le menu)

## 3) RAG — fonctionnement validé
- Embeddings : `text-embedding-3-small`
- Index FAISS : métrique confirmée = **L2**
- Fichiers : `base_connaissances.json`, `faiss_index.bin`, `faiss_metadata.json`
- `build_context()` :
  - packing (tronque chunks) + cap par fichier (`max_per_file`)
  - `max_chars` global
  - met à jour `_last_trace` avec included/excluded + reason

### Debug RAG
- Env : `RAG_DEBUG=1` pour afficher la trace
- Trace affichée = top-k + included/excluded + reason (per_file_cap, max_chars)

### Rerank lexical léger (hybride)
- `search()` récupère plus de candidats (`RAG_CAND_MULT`) puis rerank via `_kw_hits()`
- Paramètres env :
  - `RAG_CAND_MULT` (ex 4)
  - `RAG_ALPHA_TEXT` (poids hits texte)
  - `RAG_BETA_FILE` (poids hits nom fichier)

## 4) Prompt Audit V2 — état
- Le prompt est lu depuis `prompts/prompt_audit_v2.txt`
- Il doit rester **audit-only** :
  - interdiction “version corrigée”
  - correction gérée par `audit_only_guard()` en post-traitement

## 5) Qualité / Validation (tests)
Commandes utiles :
- Compilation :
  - `python -m py_compile agent_formateur.py`
  - `python -m py_compile core/rag.py`
- Doctor :
  - `python scripts/doctor.py`
- Run avec debug RAG :
  - `RAG_DEBUG=1 python agent_formateur.py`

✅ État validé dernièrement :
- `doctor.py` OK (compilation + import + prompt audit + RAG build_context + brand_block)
- trace RAG OK (included/excluded avec reason)
- format FAQ strict obtenu (5 sections numérotées)

## 6) Problèmes rencontrés (résolus)
- erreurs d’indentation / return outside function → corrigées
- prompt audit contenait des instructions de “version corrigée” → nettoyé + guard ajouté
- `_kw_hits` bug “set not subscriptable” → patch appliqué
- double affichage de la trace RAG → suppression des prints doublons
- dotenv `find_dotenv()` en one-liner Python → contourné via OPENAI_API_KEY inline

## 7) Points d’attention actuels (à traiter)
A) **Routeur FAQ** : éviter que le prompt “mandat/stock” pollue des sujets “découverte vendeur”
- Si question contient “mandat/stock/renégocier/bilan de promotion…” → prompt mandat
- Sinon → prompt général

B) **RAG pertinence** :
- améliorer sans complexifier : rerank lexical + packing + caps déjà en place
- contrôler les “mots d’action” pour limiter l’invention
- surveiller `max_chars` / `max_per_file` pour ne pas couper des pages utiles

C) **Pylance warnings** (imports non accédés, fonctions non accédées) :
- pas bloquants tant que tests OK
- on nettoiera quand la stabilité fonctionnelle est atteinte

## 8) Prochaine étape concrète (priorité)
1) Stabiliser le rerank lexical (tests sur 5 questions types : mandat stock / découverte / objections / suivi)
2) Stabiliser la FAQ “zéro invention” sans réponse robotique (liste d’actions autorisées par thème)
3) Ajouter une mini-suite de tests (script `scripts/tests_smoke.py`) pour rejouer 10 questions et vérifier :
   - format 5 sections
   - “Non couvert par les extraits…” sur hors-scope
   - trace RAG non vide si question couverte
