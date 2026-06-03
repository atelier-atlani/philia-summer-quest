# PHILIA SUMMER QUEST — Brief Sprint 2

**Document à donner à Claude Code dans VS Code, en mode Implementer.**
**Périmètre : Sprint 2 uniquement. Claude Code ne code rien hors de ce périmètre.**
**Prérequis : Sprint 1 validé (fork, structure `.claude/`, base SQLite).**

---

## CONTEXTE POUR CLAUDE CODE

Le Sprint 1 a posé les fondations : fork d'IAXEL nettoyé, structure `.claude/`, base SQLite à 8 tables. L'app ne tourne plus (app.py cassé après archivage — c'était attendu).

Le Sprint 2 fait naître le cœur de Philia : **le mentor maïeutique Archimède** et la **première session pédagogique jouable**. À la fin du sprint, un enfant doit pouvoir vivre une session de Découverte sur les fractions, où Archimède le guide par questions sans jamais donner la réponse.

Avant de commencer, lire impérativement :
- `.claude/CLAUDE.md` (point d'entrée)
- `.claude/contexts/guardrails-pedagogiques.md` (la pédagogie — les 5 modes, la maïeutique)
- `.claude/pedagogie/philia-ile-1-nombres-brises-modele.md` (le contenu de l'Île 1)
- `.claude/contexts/stack-technique.md` (les choix techniques)

**Règle absolue du produit** : Archimède ne donne JAMAIS la réponse. Il guide par questions socratiques. C'est non négociable. Tout le sprint sert cette règle.

---

## DÉCISION D'ARCHITECTURE — app.py NEUF

Décision actée par le fondateur : on ne répare pas l'`app.py` d'IAXEL (102 Ko de logique immobilière). On l'archive et on écrit un `app.py` Philia neuf et minimal.

- `app.py` actuel → déplacer vers `_archive_iaxel/app_iaxel.py`
- `agent_formateur.py` actuel → déplacer vers `_archive_iaxel/agent_formateur_iaxel.py`
- Nouveau `app.py` : court, ne fait que le routing entre écrans + initialisation `session_state`

Ces deux fichiers archivés restent consultables comme référence de patterns (gestion session Streamlit, appels LLM). Claude Code peut s'en inspirer mais ne les réutilise pas tels quels.

---

## TÂCHE 1 — app.py minimal + structure des dossiers de code

**Objectif** : un squelette d'application Philia qui démarre, même si les écrans sont des stubs.

- Archiver `app.py` et `agent_formateur.py` vers `_archive_iaxel/`
- Créer un nouveau `app.py` minimal : configuration Streamlit, initialisation `session_state` (clés définies dans le brief 1A section 3), routing vers un écran selon `st.session_state.ecran_courant`
- Créer les dossiers de code Philia avec leurs `__init__.py` : `pedagogie/`, `jeu/`, `ui/`, `config/` (si absent)
- Créer `config/constants.py` : couleurs Philia (charte : #F8FAFC, #4A9FFF, #3CE8C2, #FF9F4A, #1E2937), constantes de niveaux, limites de session
- Créer des stubs d'écrans dans `ui/` : `ecran_carte.py`, `ecran_ile.py`, `ecran_session.py` — chacun affiche juste un titre pour l'instant
- **Test** : `streamlit run app.py` démarre, affiche un écran stub, le routing fonctionne

Commit : `feat: app.py Philia minimal + structure dossiers de code`

---

## TÂCHE 2 — Le RAG maths : indexation des sources

**Objectif** : le moteur RAG interroge le contenu mathématique, pas l'immobilier.

- Adapter le script d'indexation (repris de `build_index.py` d'IAXEL) → `scripts/build_rag_index.py`
- Le script lit les sources depuis `data/sources_maths/` (84 PDF, 75 docx, etc. — déjà présents, hors Git)
- Pipeline : extraction du texte des sources → découpage en chunks → génération de l'index FAISS → sauvegarde dans `data/rag_index/`
- Adapter `core/rag.py` (repris d'IAXEL) pour pointer sur le nouvel index maths
- **Test** : une requête test ("qu'est-ce qu'une fraction ?") retourne des chunks pertinents du contenu maths

Note : `data/rag_index/` — décider s'il est versionné ou régénérable. Recommandation : régénérable, ajouté au `.gitignore`, reconstruit au déploiement. À confirmer avec le fondateur.

Commit : `feat: indexation RAG du contenu mathematique 6e-5e`

---

## TÂCHE 3 — Le mentor Archimède : agent et prompt de base

**Objectif** : l'agent mentor existe, avec sa personnalité et ses guardrails maïeutiques.

- Créer `pedagogie/mentor.py` : l'agent mentor (inspiré du pattern de `agent_formateur.py` archivé, mais réécrit pour Philia)
- Créer `prompts/mentor/_shared_persona.txt` : la personnalité d'Archimède (mentor bienveillant exigeant, sage, chaleureux — ton défini dans les guardrails pédagogiques)
- Créer `prompts/mentor/_shared_guardrails.txt` : les règles inviolables — ne jamais donner la réponse, guider par questions, décomposer en cas de blocage (4 niveaux de décomposition), détecter la fatigue
- Créer `prompts/mentor/mode_decouverte.txt` : le prompt du mode Découverte (maïeutique pure, progression concret → pictural → abstrait)
- Le mentor s'appuie sur le RAG (Tâche 2) pour la justesse factuelle
- `core/llm_client.py` : repris d'IAXEL, vérifié

Commit : `feat: agent mentor Archimede + prompts persona et guardrails`

---

## TÂCHE 4 — Le contrat de sortie et la state machine de session

**Objectif** : structurer le dialogue pédagogique de façon fiable.

- Créer `pedagogie/mentor_contract.py` : le contrat de sortie du mentor (adapté de `faq_contract.py` d'IAXEL). Le mentor renvoie une sortie structurée : message à l'enfant, état pédagogique (concept en cours, niveau de compréhension détecté, mode actif)
- Créer `pedagogie/modes.py` : énumération des 5 modes (Découverte, Pratique, Validation, Consolidation, Bilan) + transitions autorisées entre modes
- Créer `pedagogie/session_engine.py` : la state machine d'une session (refonte de `engine.py` d'IAXEL). Gère le déroulé : début de session → étapes du dialogue → fin de session
- Pour ce sprint, seul le mode Découverte est pleinement implémenté. Les 4 autres modes sont déclarés dans `modes.py` mais seront activés au Sprint 3.

Commit : `feat: contrat de sortie mentor + state machine de session`

---

## TÂCHE 5 — L'écran de session et le chat Archimède

**Objectif** : l'enfant peut dialoguer avec Archimède dans une vraie interface.

- Créer `ui/ecran_session.py` (remplace le stub) : l'écran d'une session pédagogique
- Créer `ui/ecran_chat.py` : la zone de chat avec Archimède, via `st.chat_message` et `st.chat_input`
- Connecter le chat au `session_engine` et au `mentor` : les messages de l'enfant passent au mentor, les réponses d'Archimède s'affichent
- Le contenu pédagogique vient de l'Île 1 (`philia-ile-1-nombres-brises-modele.md`), Session 1 — "Le Pont Fracturé", Découverte du concept C1 (sens d'une fraction)
- Gestion de `session_state.historique_chat` pour la persistance du dialogue pendant la session

Commit : `feat: ecran de session + chat Archimede connecte au mentor`

---

## TÂCHE 6 — Test E2E maïeutique + bilan de sprint

**Objectif** : valider que la maïeutique tient, et documenter.

- **Test E2E** : lancer l'app, parcourir la Session 1 de l'Île 1 du début à la fin. Archimède introduit le concept de fraction par questions, l'enfant répond, le dialogue progresse concret → pictural → abstrait.
- **Test de stress maïeutique** : un testeur insiste 10 fois pour obtenir la réponse directe ("dis-moi juste le résultat", "donne-moi la solution"). Archimède doit tenir à chaque fois — recadrer avec bienveillance, jamais céder.
- Si le test de stress échoue, raffiner `_shared_guardrails.txt` jusqu'à ce qu'il tienne. C'est le critère bloquant du sprint.
- Mettre à jour `.claude/memory/etat-projet.md` : bilan Sprint 2, état, ce qui reste pour le Sprint 3
- Mettre à jour `.claude/memory/decisions.md` : décisions techniques du sprint

Commit : `test: validation E2E session Decouverte + bilan Sprint 2`

---

## CRITÈRES DE VALIDATION DU SPRINT 2

Le Sprint 2 est terminé quand :
- [ ] `app.py` Philia minimal tourne, routing fonctionnel
- [ ] Le RAG interroge le contenu maths (plus l'immobilier)
- [ ] L'agent Archimède existe avec persona + guardrails
- [ ] Les 5 modes sont déclarés, le mode Découverte est pleinement fonctionnel
- [ ] Un enfant peut vivre la Session 1 de l'Île 1 en dialogue avec Archimède
- [ ] **Test de stress maïeutique réussi : Archimède ne donne jamais la réponse, même sous insistance**
- [ ] Chaque tâche a un commit propre sur `develop`

Le critère en gras est le critère central. Si la maïeutique craque, le sprint n'est pas validé, quel que soit l'état du reste.

---

## CE QUE CLAUDE CODE NE FAIT PAS CE SPRINT

- Pas les 4 autres modes pédagogiques (Sprint 3)
- Pas le système d'élévation des îles, le radar, le mentor évolutif (Sprint 3)
- Pas la voix / TTS (Sprint 4)
- Pas le paywall ni le RGPD (Sprint 4)
- Pas le contenu des Îles 2 et 3 (Sprint 5)
- Pas la carte des 7 îles fonctionnelle (stub suffisant ce sprint)

Si Claude Code identifie une amélioration hors périmètre, il la note dans `.claude/memory/learnings.md` et continue.

---

## APRÈS LE SPRINT 2

Le fondateur teste la session de Découverte, fait le test de stress maïeutique lui-même, puis revient vers l'Architecte (Claude.ai) pour l'audit Reviewer du Sprint 2 et le brief Sprint 3 (les 4 autres modes + l'enveloppe de jeu : îles, élévation, radar, carte).

---

*Brief Sprint 2 Philia Summer Quest — le cœur pédagogique.*
*À exécuter par Claude Code en mode Implementer.*
