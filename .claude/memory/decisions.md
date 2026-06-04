# Décisions d'Architecture — Philia Summer Quest

## Hors-sprint — 2026-05-26

### ADN Archimède acté comme brique fondatrice du mentor

**Décision** : le document `.claude/contexts/philia-adn-archimede.md` est désigné noyau pédagogique commun à l'ensemble de la marque Philia. Il définit l'identité, la posture et la voix du mentor maïeutique Archimède.

**Portée** : ce document fait autorité pour les deux produits (Philia Summer Quest et Philia année scolaire). Toute implémentation future du mentor dans l'un ou l'autre produit doit s'y conformer. Il prime sur les guardrails pédagogiques en cas de contradiction sur la voix ou la posture du mentor.

**Conséquence** : lors de chaque sprint touchant au comportement de l'agent, l'Implementer doit vérifier la cohérence avec `philia-adn-archimede.md` avant de livrer.

## Hors-sprint — 2026-05-27

### Environnement d'exécution : Python 3.11.14

**Décision** : le projet tourne sur Python 3.11.14. Le `.venv` créé par erreur avec Python 3.9.6 (Python système macOS) a été supprimé et recréé avec `python3.11`.

**Conséquence** : recréer le venv avec `python3.11 -m venv .venv` puis `pip install -r requirements.txt`. Les annotations `from __future__ import annotations` et `Optional[...]` présentes dans le code sont conservées — elles fonctionnent parfaitement en 3.11 et ne doivent pas être réécrites.

## Sprint 2 — 2026-05-27

### Modèle LLM : claude-sonnet-4-6 (sans suffixe de date)

**Décision** : le modèle Anthropic utilisé est `claude-sonnet-4-6`. Le suffixe de date `claude-sonnet-4-6-20260218` était une invention invalide — aucun modèle de ce nom n'existe. Corrigé dans `core/llm_client.py`.

**Conséquence** : la variable d'environnement `ANTHROPIC_CHAT_MODEL` permet de surcharger au déploiement si nécessaire.

## Sprint 2 — 2026-05-26

### Embeddings RAG : OpenAI text-embedding-3-small conservé

**Décision** : conserver `text-embedding-3-small` (OpenAI) pour les embeddings du RAG maths, identique à l'héritage IAXEL.

**Contexte** : vérification faite sur `build_index.py` et `core/rag.py` d'IAXEL — OpenAI était déjà le seul fournisseur d'embeddings. Aucun nouveau fournisseur d'IA n'a été introduit.

**Conséquence** : une clé `OPENAI_API_KEY` valide est requise pour (re)construire l'index via `scripts/build_rag_index.py`. L'index est hors Git (`data/rag_index/` dans `.gitignore`) et doit être régénéré au déploiement.

## Session Voyage / Cahier d'Aventures — 2026-06-01

### D12 — Refonte de la gamification — métaphore Voyage / Cahier d'Aventures

**Décision** : La gamification de Philia Summer Quest est refondée autour de la métaphore unifiée du Voyage à travers les Sept Îles, ancrée dans Syracuse antique avec Archimède comme mentor historique. L'enfant collecte 7 clés (1 par île, récompense hebdomadaire), des fragments de la carte du trésor (récompense quotidienne) et des artefacts fonctionnels. Le secret final est le principe d'Archimède (couronne d'Hiéron). L'aventure se vit sous forme de BD personnalisée, et l'enfant reçoit en fin de parcours un Carnet d'Aventures imprimable.

**Portée** : remplace la spec gamification v1. Document fondateur : `.claude/contexts/philia-voyage-fondateur.md`.

**Conséquence** : Le Sprint 3 est reconçu autour de cette vision. Le scope MVP 1er juillet est révisé (3 îles + 3 clés + 1 artefact + Carnet PDF, impression imprimeur reportée v1.1).

## Sprint 3 — 2026-06-04

### D13 — Suppression du RAG (Option C)

**Décision** : Le RAG (Retrieval Augmented Generation) hérité d'IAXEL est supprimé. Tout le contenu mathématique et narratif nécessaire à Archimède passe désormais par :
- Le YAML enrichi des exercices (énoncé, réponse, solution étapes, indices, erreurs typiques) — déjà en place depuis le Sprint 2
- Les prompts d'Archimède (`prompts/mentor/`) — qui contiennent l'ADN, les guardrails, et les attitudes des 5 modes
- La connaissance native du LLM Claude Sonnet 4.6 sur Syracuse antique, Archimède et les programmes 6e

**Portée** :
- `core/rag.py` et `scripts/build_rag_index.py` archivés dans `_archive_iaxel/rag_archive/`
- `pedagogie/mentor.py` nettoyé (import `rag` retiré, fonctions `_get_rag_context` et `_format_rag_block` supprimées, plus aucun appel RAG dans `repondre()`)
- `data/sources_maths/` (433 fichiers) conservé sur disque mais hors actif. Sera archivé ou supprimé dans une session ultérieure de nettoyage.

**Justification** :
1. Le test maïeutique du Sprint 2 a montré qu'Archimède dialogue correctement sans appel RAG. Le YAML enrichi fournit déjà tout ce dont il a besoin pour ne pas halluciner.
2. Le RAG actuel ajoutait 200-500ms de latence par tour de session (appel FAISS + embeddings OpenAI) sans apport pédagogique mesurable.
3. Le contenu de `data/sources_maths/` était sale (433 fichiers, doublons, exercices résolus mélangés aux cours) et nécessitait un grand nettoyage pour devenir utile — investissement non rentable.
4. La règle "le YAML coud, le LLM brode" (issue de la session Voyage) milite pour la simplicité : ce qui doit être garanti est dans le YAML, ce qui doit être brodé est laissé au LLM, sans intermédiaire.

**Conséquence pour Philia Année** : le RAG sera reconstruit de zéro pour Philia Année (12 mois) avec un référentiel propre, structuré, peut-être en double couche (référentiel mathématique + univers narratif). Le RAG IAXEL actuel n'aurait de toute façon pas servi de base solide.
