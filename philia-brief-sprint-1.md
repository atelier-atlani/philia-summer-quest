# PHILIA SUMMER QUEST — Brief Sprint 1 (ajusté au réel)

**Document à donner à Claude Code dans VS Code, en mode Implementer.**
**Ajusté à la structure réelle du repo IAXEL forké le 24 mai 2026.**
**Périmètre : Sprint 1 uniquement. Claude Code ne code rien hors de ce périmètre.**

---

## CONTEXTE POUR CLAUDE CODE

Ce repo est un fork du projet IAXEL (agent-immo-formateur), cloné depuis GitHub. Il devient **Philia Summer Quest**, un mentor IA de mathématiques pour enfants de 11-12 ans (révision 6e, anticipation 5e), sous forme d'un jeu où l'enfant fait s'élever des îles en maîtrisant les maths.

Le fork est déjà fait. La branche `develop` est créée. Le remote `origin` a été retiré. Ta mission : transformer proprement ce repo IAXEL en fondations Philia, **sans rien casser**, étape par étape, avec un commit après chaque étape.

**Stack** : Streamlit, Python, FAISS (RAG), ElevenLabs (TTS), SQLite (à introduire). Tu conserves cette stack.

**Règle absolue** : à ce sprint, on ne développe AUCUNE fonctionnalité Philia nouvelle. On prépare le terrain : archivage de l'existant immobilier, structure de dossiers, `.claude/`, base SQLite vide, smoke test. Le développement pédagogique commence au Sprint 2.

---

## ÉTAT DES LIEUX DU REPO (déjà constaté)

Racine : `app.py` (102 Ko), `agent_formateur.py` (31 Ko), `requirements.txt`, `README.md`, `CLAUDE.md` (contexte IAXEL), `.gitignore` (propre, `.env` exclu), `Procfile`, plusieurs fichiers `.md` de documentation IAXEL, des scripts à la racine (`build_index.py`, `build_kb.py`, `build_kb_from_pages.py`, `extract_pdf.py`, `search_kb.py`, `test_tts.py`), `base_connaissances.json` (RAG immo), `faiss_index.bin`, `faiss_metadata.json`, `pages_extraites.json`, `oracle_immo_master.rtf`.

Dossiers : `core/`, `training/`, `data/`, `config/`, `prompts/`, `scripts/`, `modules/`, `assets/`, `docs/`, `pdfs/`.

`core/` : `rag.py`, `tts.py`, `tts_elevenlabs.py`, `sanitizer.py`, `faq_contract.py`, `avatar.py`, `__init__.py`.

`training/` : `engine.py`, `profile.py`, `progress.py`, `adapters.py`, `synthesis.py`, `pdf_export.py`, `content.py`, `chat_libre.py`, `quiz.py`, `quiz_ui.py`, `steps.py`, `formateur_messages.py`, `dashboard.py`, `feedback.py`, et modules immo (`whatsapp.py`, `whatsapp_ui.py`, `wa_scenario_generator.py`, `dvf_connector.py`, `marche_module.py`, `marche_quiz.py`, `marche_charts.py`, `profile_ui.py`), sous-dossiers `quiz_bank/`, `scenarios/`, `modules/`.

---

## TÂCHE 1 — Smoke test du fork (vérifier que l'app IAXEL tourne)

Avant toute modification, vérifier que le fork est sain.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Créer un fichier `.env` local (NON committé, déjà dans `.gitignore`) avec des clés API de test ou les vraies clés du fondateur — le fondateur fournira les clés. Sans clés, noter ce qui échoue.

```bash
streamlit run app.py
```

**Critère** : l'app IAXEL forkée se lance. Si elle ne se lance pas, documenter précisément l'erreur dans `.claude/memory/learnings.md` (à créer) et la corriger AVANT de continuer. Ne pas avancer sur un fork cassé.

Commit : `chore: smoke test fork IAXEL OK`

---

## TÂCHE 2 — Archivage de l'existant immobilier

On n'efface rien — on archive. Créer un dossier `_archive_iaxel/` à la racine et y déplacer tout ce qui est spécifiquement immobilier et non réutilisable pour Philia :

Fichiers de documentation IAXEL à archiver :
- `BILAN_FINAL_MVP_MARCHE.md`
- `CONTEXTE_PROJET_OLLAMA.md`
- `GUIDE_DEV_CONTENU_MARCHE.md` et `GUIDE_DEV_CONTENU_MARCHE (1).md`
- `GUIDE_TRAVAIL_LOCAL_OLLAMA.md`
- `PLAN_INTEGRATION_MARCHE_IMMOBILIER.md` et `PLAN_INTEGRATION_MARCHE_IMMOBILIER (1).md`
- `PROMPT_CLAUDE_AI_SONNET.md`, `PROMPT_CLAUDE_CODE.md`
- `SYNTHESE_SESSION_MARCHE_IMMOBILIER.md`
- `oracle_immo_master.rtf`

Données immobilières à archiver :
- `base_connaissances.json` (RAG immo)
- `faiss_index.bin`, `faiss_metadata.json` (index immo — sera régénéré pour les maths)
- `pages_extraites.json`
- `data/progress_backup_20260404_162119.json`
- `data/IAxel_Knowledge_Base/` (déplacer le dossier entier)
- `data/test_results_ia.md`

Modules de code immobilier à archiver (dans `_archive_iaxel/training/`) :
- `training/whatsapp.py`, `training/whatsapp_ui.py`, `training/wa_scenario_generator.py`
- `training/dvf_connector.py`
- `training/marche_module.py`, `training/marche_quiz.py`, `training/marche_charts.py`
- `training/scenarios/` (scénarios WhatsApp immo)

**Ne PAS archiver** (ce sont les modules socle réutilisables) : `core/rag.py`, `core/tts.py`, `core/tts_elevenlabs.py`, `core/sanitizer.py`, `core/avatar.py`, `training/engine.py`, `training/profile.py`, `training/progress.py`, `training/adapters.py`, `training/synthesis.py`, `training/pdf_export.py`, `training/content.py`, `training/chat_libre.py`, `training/quiz.py`, `training/quiz_ui.py`, `training/steps.py`.

Note : `core/faq_contract.py` et `training/formateur_messages.py` seront refondus plus tard (Sprint 2), pas archivés — les laisser en place.

Pour `app.py` et `agent_formateur.py` : NE PAS les toucher ce sprint. Ils contiennent la logique immo mais seront refondus progressivement. Les laisser tels quels pour l'instant — le smoke test doit continuer à passer.

Commit : `chore: archivage contenu et modules specifiques IAXEL immobilier`

---

## TÂCHE 3 — Création de la structure `.claude/`

Créer l'arborescence `.claude/` à la racine selon le workflow AXON-1 :

```
.claude/
├── CLAUDE.md
├── contexts/
│   ├── produit-philia.md
│   ├── stack-technique.md
│   ├── guardrails-pedagogiques.md
│   ├── nommage.md
│   └── contraintes-rgpd.md
├── plans/
├── reviews/
├── pedagogie/
├── production/
└── memory/
    ├── decisions.md
    ├── learnings.md
    └── etat-projet.md
```

Le `CLAUDE.md` existant à la racine du repo (contexte IAXEL) : le déplacer vers `_archive_iaxel/CLAUDE_iaxel.md`. Créer un nouveau `.claude/CLAUDE.md` qui sera le point d'entrée Philia (le fondateur fournira le contenu, ou mettre un placeholder : "Philia Summer Quest — fork d'IAXEL — voir .claude/contexts/ pour le détail").

Les fichiers de `contexts/` et `memory/` : créer les fichiers avec un placeholder de titre. Le fondateur y déposera le contenu depuis les documents produits avec l'Architecte.

Commit : `feat: initialisation structure .claude/ workspace AXON-1`

---

## TÂCHE 4 — Rangement des documents de conception

Le fondateur a un dossier `philia-docs-temporaire` contenant les documents de conception produits avec l'Architecte. Ces documents doivent être copiés dans le repo. Claude Code indique au fondateur où placer chaque fichier :

- `philia-workflow-operatoire-1b.md` → `.claude/`
- `philia-brief-implementer-technique-1a.md` → `.claude/plans/`
- `philia-cadre-progression-jeu-programme-v1.md` → `.claude/pedagogie/`
- `philia-ile-1-nombres-brises-modele.md` → `.claude/pedagogie/`
- `philia-gamification-spec-v1.md` → `.claude/pedagogie/`
- `philia-cahier-charges-graphiste-v1.md` → `.claude/production/`
- spec pédagogique (5 modes) → `.claude/contexts/guardrails-pedagogiques.md` (contenu à intégrer)
- stratégie marketing/commerciale → `.claude/contexts/` ou un dossier `.claude/commercial/`

Le contenu RAG maths du fondateur → `data/` (dossier à préciser, `data/sources_maths/`).
Les images avatar → `assets/mentor/` (créer le dossier).

Commit : `docs: integration documents de conception Philia dans .claude/`

---

## TÂCHE 5 — Préparation de la base SQLite (structure seule, pas de logique)

Créer le dossier `data_layer/` à la racine. Y créer `schema.sql` avec le schéma SQLite défini dans le brief Implementer technique 1A (tables : enfants, parents, progression_iles, maitrise_concepts, superpouvoirs, sessions, mentor_etat, analogies).

Créer `data_layer/db.py` : un module minimal qui sait créer la base `data/philia.db` à partir de `schema.sql` et ouvrir une connexion. Pas de logique métier ce sprint — juste create + connect.

Créer `data_layer/__init__.py`.

Tester : un script qui exécute `schema.sql` et crée `data/philia.db`. Vérifier que les 8 tables existent.

Ajouter `data/philia.db` au `.gitignore` (la base locale ne se commit pas).

Commit : `feat: schema SQLite Philia + module db.py (creation base)`

---

## TÂCHE 6 — Mise à jour du README et bilan de sprint

Remplacer le contenu de `README.md` par un README Philia minimal : nom du projet, description courte, stack, commande de lancement, lien vers `.claude/` pour le contexte complet.

Créer `.claude/memory/etat-projet.md` avec un bilan du Sprint 1 : ce qui a été fait, l'état du fork, ce qui reste pour le Sprint 2.

Commit : `docs: README Philia + bilan Sprint 1`

---

## CRITÈRES DE VALIDATION DU SPRINT 1

Le Sprint 1 est terminé quand :
- [ ] L'app forkée se lance toujours (`streamlit run app.py`) — smoke test OK
- [ ] Tout le contenu immobilier spécifique est archivé dans `_archive_iaxel/`
- [ ] Les modules socle réutilisables sont restés en place et intacts
- [ ] La structure `.claude/` existe et est correctement organisée
- [ ] Les documents de conception sont rangés dans `.claude/`
- [ ] `data_layer/schema.sql` et `db.py` existent, la base `data/philia.db` se crée avec ses 8 tables
- [ ] `README.md` est à jour pour Philia
- [ ] Chaque tâche a fait l'objet d'un commit propre sur la branche `develop`
- [ ] Aucune clé API n'est committée (vérifier que `.env` n'est pas dans Git)

---

## CE QUE CLAUDE CODE NE FAIT PAS CE SPRINT

- Ne touche pas à `app.py` ni `agent_formateur.py` (refonte au Sprint 2)
- Ne développe aucune fonctionnalité pédagogique Philia
- Ne refond pas les prompts
- Ne crée pas le contenu des îles
- Ne touche pas au RAG (la régénération maths est au Sprint 2)

Si Claude Code identifie une amélioration hors périmètre, il la note dans `.claude/memory/learnings.md` et continue.

---

## APRÈS LE SPRINT 1

Le fondateur teste, puis revient vers l'Architecte (Claude.ai) pour l'audit Reviewer du Sprint 1 et la production du brief Sprint 2 (refonte de l'agent en mentor maïeutique + premier mode pédagogique).

---

*Brief Sprint 1 Philia Summer Quest — ajusté à la structure réelle du repo.*
*À exécuter par Claude Code en mode Implementer.*
