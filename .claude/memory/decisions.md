# Décisions d'Architecture — Philia Summer Quest

## Hors-sprint — 2026-05-26

### ADN Archimède acté comme brique fondatrice du mentor

**Décision** : le document `.claude/contexts/philia-adn-archimede.md` est désigné noyau pédagogique commun à l'ensemble de la marque Philia. Il définit l'identité, la posture et la voix du mentor maïeutique Archimède.

**Portée** : ce document fait autorité pour les deux produits (Philia Summer Quest et Philia année scolaire). Toute implémentation future du mentor dans l'un ou l'autre produit doit s'y conformer. Il prime sur les guardrails pédagogiques en cas de contradiction sur la voix ou la posture du mentor.

**Conséquence** : lors de chaque sprint touchant au comportement de l'agent, l'Implementer doit vérifier la cohérence avec `philia-adn-archimede.md` avant de livrer.

## Sprint 2 — 2026-05-26

### Embeddings RAG : OpenAI text-embedding-3-small conservé

**Décision** : conserver `text-embedding-3-small` (OpenAI) pour les embeddings du RAG maths, identique à l'héritage IAXEL.

**Contexte** : vérification faite sur `build_index.py` et `core/rag.py` d'IAXEL — OpenAI était déjà le seul fournisseur d'embeddings. Aucun nouveau fournisseur d'IA n'a été introduit.

**Conséquence** : une clé `OPENAI_API_KEY` valide est requise pour (re)construire l'index via `scripts/build_rag_index.py`. L'index est hors Git (`data/rag_index/` dans `.gitignore`) et doit être régénéré au déploiement.
