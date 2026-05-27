# CLAUDE.md — Point d'entrée du projet Philia Summer Quest

**Ce fichier est le premier que toute IA (Claude Code, Architecte, Reviewer) doit lire.**
**Il oriente vers le reste du contexte. Il ne contient que l'essentiel.**

---

## CE QU'EST LE PROJET

**Philia Summer Quest** est un programme de révision mathématique d'été pour enfants de 11-12 ans (fin de 6e, entrée en 5e). L'enfant incarne un "Élévateur" qui fait remonter les îles d'un archipel en ruine en maîtrisant les mathématiques. Son guide est un mentor maïeutique nommé Archimède.

C'est une application web Streamlit, fork du projet IAXEL. MVP livrable le **1er juillet 2026** avec 3 îles.

Philia Summer Quest est le premier produit de la marque **Philia**. Un second produit, Philia (année scolaire), suivra à la rentrée.

## L'ADN NON NÉGOCIABLE

**La maïeutique.** Archimède ne donne JAMAIS la réponse. Il guide par questions socratiques. C'est le cœur du produit. Toute fonctionnalité, tout arbitrage, toute simplification doit respecter ce principe. En cas de doute, c'est la règle qui tranche.

## OÙ TROUVER QUOI

- `.claude/contexts/philia-adn-archimede.md` — **brique fondatrice** : identité, posture et voix du mentor maïeutique (commun aux deux produits Philia)
- `.claude/contexts/produit-philia.md` — vision produit, marque, audience cible
- `.claude/contexts/stack-technique.md` — choix techniques (Streamlit, SQLite, RAG)
- `.claude/contexts/guardrails-pedagogiques.md` — la pédagogie : 5 modes, maïeutique, principes
- `.claude/contexts/nommage.md` — l'architecture des noms (Philia, Archimède, les îles)
- `.claude/contexts/contraintes-rgpd.md` — données enfants, consentement parental
- `.claude/plans/` — le brief technique et les briefs de sprint
- `.claude/pedagogie/` — le cadre de progression et le contenu des îles
- `.claude/production/` — le cahier des charges graphique
- `.claude/reviews/` — les audits Reviewer de fin de sprint
- `.claude/memory/` — décisions, apprentissages, état du projet

## LA MÉTHODE DE TRAVAIL

Le projet suit le workflow AXON-1 (voir `.claude/philia-workflow-operatoire-1b.md`). Trois rôles :
- **Le fondateur** décide, valide, teste
- **Claude.ai (Architecte/Reviewer)** produit les specs et audite
- **Claude Code (Implementer)** écrit le code, sprint par sprint

Règle : Claude Code ne code jamais hors du périmètre du sprint courant défini dans `.claude/plans/sprint-X.md`.

## ÉTAT ACTUEL

Voir `.claude/memory/etat-projet.md` pour l'état à jour. Au moment de la rédaction de ce fichier : Sprint 1 terminé (fork, archivage, structure, base SQLite), Sprint 2 en préparation (refonte de l'agent en mentor maïeutique).

---

*CLAUDE.md — point d'entrée Philia Summer Quest. Tenu à jour à chaque évolution structurante.*
