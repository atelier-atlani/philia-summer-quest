# PHILIA SUMMER QUEST — Workflow Opératoire v1.0

**Document 1B du Chantier 1. Définit la méthode de travail concrète.**
**Application d'AXON-1 v0.1 au projet Philia Summer Quest.**
**À lire avant le brief Implementer technique (1A).**

---

## OBJET DE CE DOCUMENT

Tu vas construire Philia Summer Quest en 6 semaines, en pluriactif, sans co-fondateur technique. La seule façon d'y arriver est de ne pas coder toi-même ligne à ligne, mais d'orchestrer des instances IA dans des rôles définis.

Ce document répond à une question simple : **concrètement, lundi matin, qu'est-ce que tu fais ?**

---

## 1. LES TROIS ACTEURS ET LEURS RÔLES

### Toi — le Décideur / Chef de projet
Tu valides, tu tranches, tu pousses-back, tu testes. Tu ne codes pas ligne à ligne. Ton métier sur ce projet : garder le cap, valider la pédagogie, décider les arbitrages, vérifier que ce qui sort est juste.

### Claude.ai (cette interface) — l'Architecte / Reviewer
Moi. Je produis les plans, les specs, les briefs. J'audite ce qui est produit. Je maintiens la cohérence d'ensemble. Je ne code pas non plus — je conçois et je contrôle.

### Claude Code (dans VS Code) — l'Implementer
L'instance qui écrit réellement le code. Elle lit les briefs produits par l'Architecte, exécute, teste, commit. C'est l'ouvrier qualifié qui construit sur plan.

### Le rôle de Cowork
Cowork est le pont. Il permet à Claude.ai (moi) de lire et écrire dans les fichiers de ton projet sans copier-coller manuel. En v0.1, comme tu ne maîtrises pas encore Cowork, on fonctionne en mode dégradé (copier-coller assumé) et on activera Cowork progressivement. Ce n'est pas bloquant.

---

## 2. LE RÉPERTOIRE `.claude/` — LE CERVEAU PARTAGÉ DU PROJET

Tout le projet Philia se pilote depuis un répertoire `.claude/` à la racine du repo. C'est là que vivent les plans, les specs, la mémoire, les décisions. Versionné Git.

Structure pour Philia Summer Quest :

```
philia-summer-quest/
├── .claude/
│   ├── CLAUDE.md                      # Point d'entrée — explique le projet à toute IA
│   ├── contexts/
│   │   ├── produit-philia.md          # Vision produit, brand, audience
│   │   ├── stack-technique.md         # Streamlit, SQLite, RAG, choix techniques
│   │   ├── guardrails-pedagogiques.md # Maïeutique non-négociable, les 5 modes
│   │   ├── nommage.md                 # Philia / Summer Quest / Sept Îles / Archimède
│   │   └── contraintes-rgpd.md        # Données enfants, consentement parental
│   ├── plans/
│   │   ├── 2026-05-XX_brief-implementer-mvp.md   # Le brief technique (1A)
│   │   ├── sprint-1.md                # Détail du sprint en cours
│   │   └── ...
│   ├── reviews/
│   │   └── ...                        # Mes audits Reviewer
│   ├── pedagogie/
│   │   ├── cadre-progression.md       # Le cadre jeu-programme (déjà produit)
│   │   ├── ile-1-nombres-brises.md    # L'Île 1 modèle (déjà produit)
│   │   └── ile-2...7.md               # Les autres îles, au fur et à mesure
│   └── memory/
│       ├── decisions.md               # Log de toutes les décisions prises
│       ├── learnings.md               # Ce qu'on a appris, à ne pas réapprendre
│       └── etat-projet.md             # Où on en est, mis à jour chaque semaine
└── [le code de l'app]
```

**Règle d'or** : si une information compte pour le projet, elle vit dans un fichier `.claude/`, pas seulement dans une conversation. Les conversations s'oublient, les fichiers persistent.

---

## 3. CE QU'ON REPREND D'IAXEL

Philia Summer Quest est un fork d'IAXEL. Voici ce qui est repris tel quel, ce qui est adapté, ce qui est nouveau. Détail complet dans le brief Implementer (1A) — ici la vue d'ensemble.

**Repris quasi tel quel** (le socle éprouvé) :
- L'architecture RAG (FAISS) — on change le contenu, pas le moteur
- Le système TTS avec cache MD5 — économie ElevenLabs déjà résolue
- Le pattern de state machine de session
- La gestion de profil utilisateur et de progression
- L'export PDF
- La structure de tests pre-commit

**Adapté** (la logique reste, le contenu change) :
- Les prompts (formateur immo → mentor maïeutique Archimède)
- Le contenu RAG (immobilier → maths 6e-5e)
- Les données structurées YAML (scénarios immo → îles, sessions, exercices)
- L'interface (formateur pro → expérience enfant + dashboard parent)

**Nouveau** (à construire) :
- Le système d'élévation des îles
- Le mentor évolutif et ses expressions
- Le radar des superpouvoirs
- La carte des 7 îles
- Le paywall 2 tiers + Stripe
- Le dashboard parent
- Le module RGPD/consentement

---

## 4. LE CYCLE DE TRAVAIL — COMMENT UNE FONCTIONNALITÉ NAÎT

Voici le cycle concret, répété pour chaque sprint et chaque fonctionnalité.

### Étape 1 — ARCHITECTE (Claude.ai, avec moi)
Tu viens me voir avec un objectif de sprint. Je produis un **brief de sprint** détaillé : quoi construire, quels fichiers, quels critères d'acceptance. Le brief est enregistré dans `.claude/plans/sprint-X.md`.

### Étape 2 — VALIDATION (toi)
Tu lis le brief. Tu pousses-back si quelque chose te paraît faux, flou ou hors-scope. Une fois validé, le brief devient le contrat du sprint.

### Étape 3 — IMPLEMENTER (Claude Code, dans VS Code)
Tu ouvres Claude Code. Tu lui donnes le brief de sprint (`.claude/plans/sprint-X.md`). Il code, teste, commit étape par étape. Tu le supervises sans coder à sa place.

### Étape 4 — TEST (toi)
Tu lances l'app localement. Tu vérifies que ce qui devait marcher marche. Tu joues le parcours comme un enfant le ferait.

### Étape 5 — REVIEWER (Claude.ai, avec moi)
En fin de sprint, tu me montres ce qui a été produit (le code, ou le résumé de Claude Code). Je fais un audit : conformité au brief, qualité, dette technique, risques. Rapport dans `.claude/reviews/`.

### Étape 6 — DÉCISION (toi)
Tu décides : on accepte, on corrige, on note comme dette. Puis on enchaîne sur le sprint suivant.

Ce cycle complet dure une semaine (un sprint). Six cycles = six semaines = le MVP.

---

## 5. LE WORKFLOW CONCRET SANS COWORK (mode v0.1, dès maintenant)

Tant que tu ne maîtrises pas Cowork, voici le mode opératoire réel, simple et fonctionnel :

**Pour produire un plan ou un brief (Architecte)** :
1. Tu viens dans cette conversation Claude.ai
2. Je produis le document
3. Tu le télécharges et tu le places dans `.claude/plans/` de ton repo local
4. Tu commits

**Pour coder (Implementer)** :
1. Tu ouvres VS Code avec l'extension Claude Code
2. Claude Code lit directement les fichiers `.claude/` du repo (il a accès au système de fichiers local)
3. Tu lui dis : "Lis `.claude/plans/sprint-1.md` et exécute le périmètre du sprint 1"
4. Il code dans le repo

**Pour auditer (Reviewer)** :
1. Claude Code peut te produire un résumé de ce qu'il a fait
2. Tu colles ce résumé (ou les fichiers clés) dans cette conversation Claude.ai
3. Je produis l'audit

Le seul "copier-coller manuel" qui subsiste : faire transiter les documents entre Claude.ai (moi) et le repo. C'est quelques minutes par jour. Acceptable.

## 6. LE WORKFLOW AVEC COWORK (mode v0.2, quand tu seras prêt)

Quand tu auras pris en main Cowork, l'amélioration : Cowork me donne accès direct (lecture/écriture) au répertoire `.claude/` de ton projet. Je peux alors lire l'état du projet et écrire les plans directement, sans que tu fasses transiter les fichiers. Le copier-coller disparaît.

Ce n'est pas urgent. On migre à Cowork après le sprint 1, quand le cycle de base tourne déjà. Ne pas ajouter une courbe d'apprentissage d'outil au démarrage.

---

## 7. RÈGLES DE DISCIPLINE OPÉRATIONNELLE

**Règle 1 — Un sprint = une semaine = un objectif clair.** Pas de sprint flou. Si le brief de sprint ne tient pas en une page de livrables testables, il est mal défini.

**Règle 2 — Le brief avant le code, toujours.** Claude Code ne code jamais sans un brief écrit validé. "Code-moi vite un truc" est interdit — c'est ce qui crée la dette ingérable.

**Règle 3 — Test E2E à chaque fin de sprint.** Chaque vendredi, l'app doit tourner et le parcours du sprint doit être jouable. Si ça ne tourne pas, le sprint n'est pas fini.

**Règle 4 — `decisions.md` tenu à jour.** Chaque décision d'arbitrage (technique, pédagogique, produit) est consignée en une ligne dans `.claude/memory/decisions.md` avec la date. Dans 4 semaines, tu auras oublié pourquoi tu as tranché — le log te le rappellera.

**Règle 5 — La maïeutique ne se négocie jamais.** Quel que soit le retard, la pression, la tentation de simplifier : Archimède ne donne jamais la réponse. C'est le cœur du produit. Tout le reste est négociable, pas ça.

**Règle 6 — Scope MVP gravé.** 3 îles au 1er juillet. Si un sprint dérape, on réduit le périmètre d'une fonctionnalité, on ne décale pas la date. Le 1er juillet est immuable.

---

## 8. RYTHME HEBDOMADAIRE TYPE

Pour tes 15-20h/semaine sur Philia, voici une ventilation indicative :

| Moment | Activité | Durée |
|---|---|---|
| Lundi | Session Architecte avec Claude.ai : brief du sprint | 1-2h |
| Lundi-vendredi | Supervision Claude Code : lancement, validation par étapes | 8-12h |
| Mercredi | Point mi-sprint : test de ce qui est produit | 1h |
| Vendredi | Test E2E du sprint + session Reviewer avec Claude.ai | 2-3h |
| Continu | Revue pédagogique des îles avec ton épouse (en parallèle) | 2-3h |

C'est tenable si tu protèges ces créneaux. Le risque n'est pas la charge — c'est la dispersion. Bloque ces heures dans ton agenda comme des rendez-vous non-déplaçables.

---

## 9. CE QUI EST PRODUIT, OÙ ÇA VIT

| Livrable | Produit par | Vit dans |
|---|---|---|
| Specs, plans, briefs de sprint | Claude.ai (Architecte) | `.claude/plans/` |
| Audits | Claude.ai (Reviewer) | `.claude/reviews/` |
| Code de l'app | Claude Code (Implementer) | le repo (hors `.claude/`) |
| Contenu pédagogique des îles | Toi + épouse, avec moi | `.claude/pedagogie/` |
| Contenu visuel (illustrations, GIFs) | Grok + graphiste + Midjourney | `assets/` du repo |
| Décisions et mémoire projet | Toi | `.claude/memory/` |
| Contenu marketing/com | Grok + toi | hors repo (canaux marketing) |

---

## 10. PROCHAINE ÉTAPE

Ce workflow étant posé, le document suivant est le **1A — Brief Implementer technique** : la spec de développement de l'app Philia Summer Quest, structurée pour être exécutée par Claude Code sprint par sprint.

Le brief 1A s'appuiera sur ce workflow : il sera découpé en sprints, chaque sprint produisant un `.claude/plans/sprint-X.md`.

---

*Workflow Opératoire Philia Summer Quest v1.0 — document 1B du Chantier 1.*
*Application concrète d'AXON-1 v0.1.*
