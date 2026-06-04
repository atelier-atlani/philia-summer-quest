# PHILIA SUMMER QUEST — Bilan Structurel et Document de Pilotage

**Document de référence du projet à date.**
**Sort de la logique conversationnelle pour entrer dans la hiérarchie programme.**
**Sert de point d'entrée à toute reprise de travail.**

---

## NOTE D'USAGE

Ce document remplace, à un instant T, la chronologie des conversations. Il s'organise en hiérarchie : la vision en haut, puis le programme, les chantiers, l'état d'avancement, les décisions actées, les apprentissages, les prochaines étapes. À chaque reprise de travail, on lit ce document. À chaque jalon, on le met à jour.

Il a quatre destinataires : toi (le fondateur), ton épouse (revue pédagogique), Claude.ai en tant qu'Architecte/Reviewer (moi), et Claude Code en tant qu'Implementer.

---

# NIVEAU 1 — LA VISION

## 1.1 Le produit

**Philia** est une marque-mère d'éducation par mentor IA personnel, fondée sur la maïeutique et le respect de l'enfance. Deux produits sont prévus :

- **Philia Summer Quest** — produit d'été, 7 semaines de révision-anticipation maths 6e→5e, sous forme de jeu (L'Ascension des Sept Îles). Premier produit lancé. MVP 1er juillet 2026.
- **Philia Année** — produit d'année scolaire, ambitieux, à concevoir après le succès du Summer Quest. Architecture lourde (mémoire 15 ans, GraphRAG, Système 1/2, multimat).

## 1.2 La proposition de valeur

Un **mentor IA maïeutique** (Archimède) qui ne donne JAMAIS la réponse, guide par questions, ancre la pédagogie dans un univers narratif (les Sept Îles), et fait progresser l'enfant non seulement en compétence mais en intelligence (au sens Bloom : analyse, création, métacognition).

## 1.3 L'ennemi commercial à nommer

Le décrochage silencieux en maths en 6e. Pas l'Éducation Nationale (trop politique). Pas Kartable (mauvaise comparaison). Le décrochage en lui-même — la peur parentale la plus tangible.

## 1.4 Le client visé (50 premiers payants Summer Quest)

Parents CSP+ 38-49 ans, enfants 10-12 ans en CM2/début 6e, métropoles, déjà acheteurs d'edtech. Prix MVP : 24€ Summer Premium (tier gratuit en parallèle).

## 1.5 La fondation théorique

Quatre valeurs fondatrices (issues du Document Maître Élévation V8/V9) : Bienveillance Exigeante, Autonomie de l'Élève, Respect de l'Enfance, Honnêteté.

Trois sources de recherche validées : étude Penn PNAS 2025 (les IA qui donnent les réponses détruisent l'apprentissage), étude Harvard Kestin 2025 (un tuteur IA bien conçu surpasse l'enseignement actif en classe, double effect size), expérience Khanmigo (le tuteur doit recevoir la solution complète et les indices pré-écrits pour ne pas halluciner).

---

# NIVEAU 2 — LE PROGRAMME

## 2.1 Les six chantiers structurels du Summer Quest

Ces six chantiers couvrent tout le travail du MVP. Chaque chantier a son responsable principal.

| # | Chantier | Responsable principal | État |
|---|---|---|---|
| C1 | **Pédagogie & Mentor** — l'ADN d'Archimède, les prompts, la maïeutique, les 5 modes | Architecte (Claude.ai) + Fondateur pour validation | Sprint 2 fait |
| C2 | **Contenu des Îles** — exercices au format enrichi pour 7 îles, validation | Fondateur + Épouse | Île 1 faite, 2-7 à venir |
| C3 | **Technique & App** — code Python/Streamlit, RAG, agent, écrans | Implementer (Claude Code) supervisé par Fondateur | Sprint 2 fait |
| C4 | **Gamification & UX** — îles, élévation, radar, cristaux, carte, mentor évolutif | Implementer + design visuel | À démarrer Sprint 3 |
| C5 | **Conformité & Commercial** — RGPD enfants, paywall, dashboard parent, soft launch | Implementer + Fondateur | Sprint 4-6 |
| C6 | **Production graphique** — illustrations d'îles (4 états × 7), Archimède (10 expressions), assets UI | Graphiste externe + Grok (concept) | En attente |

## 2.2 Architecture du repo

```
philia-summer-quest/
├── .claude/                    # CERVEAU PARTAGÉ DU PROJET
│   ├── CLAUDE.md               # point d'entrée IA
│   ├── contexts/               # documents fondateurs
│   ├── pedagogie/              # contenu pédagogique (îles)
│   ├── plans/                  # briefs de sprint
│   ├── reviews/                # audits Reviewer
│   ├── production/             # specs graphiques
│   ├── commercial/             # stratégie commerciale
│   └── memory/                 # décisions, learnings, état projet
├── _archive_iaxel/             # ancien contenu IAXEL archivé
├── core/                       # RAG, TTS, LLM client, sanitizer
├── data_layer/                 # SQLite (schema, db.py)
├── pedagogie/                  # mentor, session_engine, modes, contract
├── prompts/mentor/             # les 3 fichiers de prompts d'Archimède
├── ui/                         # écrans Streamlit
├── data/                       # base SQLite, RAG index, sources maths
├── assets/                     # illustrations, sons
└── scripts/                    # indexation, ingestion, pre-commit
```

## 2.3 Stack technique actée

- **Langage** : Python 3.11.14 (acté après correction du `.venv` 3.9 hérité)
- **UI** : Streamlit
- **Base de données** : SQLite (schéma 8 tables, en place)
- **RAG** : FAISS + OpenAI embeddings (`text-embedding-3-small`, hérité IAXEL)
- **LLM mentor** : Anthropic Claude Sonnet 4.6 (alias `claude-sonnet-4-6`)
- **TTS** : ElevenLabs (architecture 3 couches, activé Sprint 4)
- **Paiement** : Stripe (Sprint 4)
- **Hébergement** : à choisir Sprint 4-6, UE obligatoire (Railway / Scaleway / OVH)

## 2.4 Workflow opératoire (AXON-1)

Trois acteurs : **Fondateur** (décide, valide, teste) → **Architecte/Reviewer** (Claude.ai, produit specs et audits) → **Implementer** (Claude Code, écrit le code). Cycle : brief → validation → implémentation → test → audit → décision. Six sprints d'une semaine sur le MVP.

**Bascule Cowork prévue au début du Sprint 3** — supprime le copier-coller entre Architecte et repo.

---

# NIVEAU 3 — ÉTAT DES CHANTIERS, DÉTAIL

## 3.1 Chantier C1 — Pédagogie & Mentor

### État : socle fondateur livré

**Livrables produits et validés** :
- **ADN d'Archimède** (`.claude/contexts/philia-adn-archimede.md`) — brique fondatrice, commune aux deux produits Philia. Identité, 4 valeurs, persona, 8 principes inviolables, architecture maïeutique en escalier à 4 niveaux, règle d'or (connaître la solution sans la donner), gestion des cas difficiles, les 5 modes.
- **Trois prompts opérationnels** (`prompts/mentor/`) :
  - `_shared_persona.txt` — identité et voix d'Archimède
  - `_shared_guardrails.txt` — 8 règles inviolables
  - `mode_decouverte.txt` — attitude et mécanique du mode Découverte
- **Cadre des 5 modes pédagogiques** + Infusion Spiralaire (interleaving) — défini dans la spec pédagogique, codé partiellement (seul Découverte est actif au Sprint 2).

**À produire au Sprint 3** :
- Prompts des 4 autres modes (Pratique, Validation, Consolidation, Bilan)
- Enrichissement des prompts pour la **multimodalité de relance** (apprentissage majeur du Sprint 2 — voir §5.1)
- Calibration de l'accueil des bonnes réponses (apprentissage Sprint 2)

### Décisions actées
- ADN d'Archimède = noyau commun aux deux produits Philia. Toute évolution du mentor doit s'y conformer.
- La pédagogie vit dans les `.txt`, jamais en dur dans le code Python.

---

## 3.2 Chantier C2 — Contenu des Îles

### État : Île 1 complète, 6 îles à produire

**Livrable produit et validé** :
- **Île 1 — L'Île des Nombres Brisés** — contenu complet au format enrichi (`.claude/pedagogie/ile-1-nombres-brises-CONTENU.md`, 1066 lignes). 5 sessions, 33 exercices, chacun avec énoncé, réponse, solution étapes, 3 indices étagés, erreurs typiques. Concepts C1-C5 (révision 6e + anticipation 5e fractions). Validé Reviewer.

**Format YAML enrichi acté** — chaque exercice contient :
- `enonce`
- `reponse`
- `solution_etapes` (chemin de résolution)
- `indices` (léger / moyen / fort)
- `erreurs_typiques` (erreur + réponse maïeutique)

**À produire au Sprint 3** (et au-delà) :
- Îles 2 et 3 (MVP 1er juillet) — Forêt des Mesures, Labyrinthe des Inconnues
- Îles 4 et 5 (v1.1 mi-juillet) — Royaume des Proportions, Vallée des Nombres Relatifs
- Îles 6 et 7 (v1.2 août) — Cité des Formes (géométrie, visuel massif), Tour des Données
- **Enrichissement de l'Île 1 au format multimodal** (indices visuels et manipulation, voir §5.1)

### Décisions actées
- Format YAML enrichi est non-négociable (recherche Harvard).
- Le contenu pédagogique est produit par le Fondateur et son épouse, audité par l'Architecte.
- Une seule version de référence par île (pas de double versionnage).

---

## 3.3 Chantier C3 — Technique & App

### État : Sprint 2 terminé, app fonctionnelle

**Livrables Sprint 1 (fondations)** :
- Fork IAXEL → repo `philia-summer-quest`
- Archivage du contenu immobilier IAXEL (`_archive_iaxel/`)
- Structure `.claude/` initialisée
- SQLite schéma + module `data_layer/db.py`
- Modules socle conservés (RAG, TTS, sanitizer, etc.)

**Livrables Sprint 2 (mentor + session)** :
- `core/llm_client.py` — wrapper Anthropic
- `pedagogie/mentor.py` — tuyauterie du mentor (assemble prompts + exercice + situation narrative + RAG, appelle LLM)
- `pedagogie/modes.py` — 5 modes + transitions
- `pedagogie/mentor_contract.py` — `EtatPedagogique` + `MentorOutput`
- `pedagogie/session_engine.py` — state machine de session, séquençage imposé par le code
- `pedagogie/contenu_ile1.py` — exercices Session 1 chargés en mémoire
- `ui/ecran_session.py` + `ui/ecran_chat.py` — écrans
- App tourne sur `localhost:8504`, Archimède dialogue, le test maïeutique a été passé.

**Dette technique notée** :
- L'identifiant de modèle daté `claude-sonnet-4-6-20260218` a renvoyé `NotFoundError` — fallback sur l'alias court `claude-sonnet-4-6`. Conséquence : on a perdu la garantie de version figée du LLM. À revérifier au Sprint 3.
- `data/sources_maths/` contient 433 fichiers en vrac (doublons, exercices déjà résolus mélangés à des cours) — chantier de nettoyage RAG à planifier, non urgent.
- `from __future__ import annotations` et `Optional[...]` restent en place malgré le passage en 3.11 — pas réécrits intentionnellement (le code marche, on ne touche pas).

**À produire au Sprint 3** :
- Affichage visuel (SVG) dans l'écran de session — voir §5.1
- Détection automatique de réussite d'un exercice (aujourd'hui déclenchée explicitement par bouton)
- Activation des 4 autres modes pédagogiques
- Premier câblage de l'élévation des îles (suite de la gamification, C4)

### Décisions actées
- Python 3.11 (vs 3.9 hérité).
- Embeddings OpenAI conservés (héritage IAXEL).
- Séquençage des exercices dans le `SessionEngine`, pas dans l'UI ("vitre vs cerveau").
- `app.py` minimal réécrit (Strategy B, l'app IAXEL archivée).

---

## 3.4 Chantier C4 — Gamification & UX

### État : refondé — métaphore Voyage / Cahier d'Aventures (D12, 2026-06-01)

**Livrables de conception produits** :
- **Document fondateur Voyage** (`.claude/contexts/philia-voyage-fondateur.md`) — métaphore unifiée du Voyage à travers les Sept Îles de Syracuse antique. **Remplace et archive** la spec gamification v1.
- **Cadre de progression jeu-programme** (`.claude/pedagogie/philia-cadre-progression-jeu-programme-v1.md`) — grammaire de progression, Résurgences (interleaving), Zones de Profondeur. Toujours valide.

**Mécaniques de récompense actées (triple système)** :
- **Clé** (1 par île, hebdomadaire) — récompense de maîtrise complète d'une île
- **Fragment de carte du trésor** (quotidien) — petite victoire fréquente
- **Artefact fonctionnel** (ponctuel) — récompense de capacité (superpouvoir)
- Secret final : le principe d'Archimède (couronne d'Hiéron)

**À produire au Sprint 3** :
- `jeu/cles.py` — modèle 7 clés, attribution et listage
- `jeu/carte_tresor.py` — modèle 49 fragments, persistance SQLite
- `jeu/artefacts.py` — modèle 5 artefacts, 1 débloquable au MVP
- `ui/ecran_carte.py` — carte de l'archipel opérationnelle (placeholder → réel)
- `ui/onboarding.py` — choix d'avatar + légende fondatrice + entrée sur la carte
- Prototype planche BD Session 1 Île 1 (preuve de concept Voyage)

---

## 3.5 Chantier C5 — Conformité & Commercial

### État : conçu sur papier, à exécuter Sprint 4-6

**Livrables produits (stratégie)** :
- **Brief commercial opérationnel** issu du panel multi-IA (GPT-5 + Gemini + Grok + Perplexity, mai 2026) — positionnement, ICP, plan d'acquisition 50 payants / 90 jours / 3000€, brief de marque, 5 décisions du fondateur à acter.

**À produire au Sprint 4** :
- `commerce/paywall.py` — 2 tiers Gratuit / Premium 24€
- `commerce/stripe_integration.py` — paiement + webhooks (sandbox d'abord)
- `compliance/rgpd.py` — consentement parental (< 15 ans, double opt-in)
- `ui/onboarding.py` — création profil enfant + RGPD
- `ui/dashboard_parent.py` — espace parent
- `parent/bilan_hebdo.py` + `parent/email.py` — bilan PDF hebdo automatique

**À produire au Sprint 6** :
- Pages légales (CGV, CGU, politique RGPD, mentions légales)
- Choix et déploiement hébergement UE
- Soft launch 30 juin avec 5-10 familles POC

### Décisions actées
- Ennemi commercial = décrochage silencieux en maths, PAS l'EN.
- Pas de double tarification au launch (simplicité).
- Cible : 50 payants à 24€/mois (stretch), 25-35 réaliste, 15 minimum.

---

## 3.6 Chantier C6 — Production graphique

### État : cahier des charges produit, attente production

**Livrable produit** :
- **Cahier des charges graphique** (`.claude/production/philia-cahier-charges-graphiste-v1.md`) — spec pour Archimède (10 expressions) et 7 îles (4 états chacune).

**À démarrer en parallèle des sprints 3-5** :
- Sélection du graphiste
- Concept visuel via Grok (idéations)
- Production des illustrations finales
- Livraison étalée pour ne pas bloquer le code

---

# NIVEAU 4 — ÉTAT DES SPRINTS

| Sprint | Période | Périmètre | État |
|---|---|---|---|
| **Sprint 1** | sem. 1 | Fork, archivage, structure `.claude/`, SQLite | ✅ Terminé |
| **Sprint 2** | sem. 2 | Mentor Archimède + state machine + 1er mode + écran de session | ✅ Terminé |
| **Sprint 3** | sem. 3 | Multimodalité de relance + visuels + 4 autres modes + gamification de base | ⏳ À démarrer |
| **Sprint 4** | sem. 4 | Voix (TTS) + paywall Stripe + RGPD + dashboard parent | À venir |
| **Sprint 5** | sem. 5 | Contenu Îles 2-3 + Rite d'Élévation + bilan PDF | À venir |
| **Sprint 6** | sem. 6 | Stress test + finitions + pages légales + soft launch | À venir |

---

# NIVEAU 5 — APPRENTISSAGES MAJEURS (à intégrer Sprint 3)

## 5.1 Apprentissage n°1 — La relance doit être multimodale, pas généraliste

**Découverte** : au test maïeutique du Sprint 2, Archimède reformulait les questions en restant dans le même canal (verbal abstrait). Or la méthode de Singapour (concret → pictural → abstrait) doit être utilisée comme grille de relance, pas seulement comme progression linéaire.

**Quatre canaux à exploiter** :
- Verbal abstrait (la question pleine)
- Verbal concret (analogie, exemple tiré du monde de l'enfant)
- Visuel (description d'un schéma à imaginer, ou schéma affiché)
- Manipulation (pliage, dessin, comptage avec les doigts)

**Implication Sprint 3** :
- Enrichir les prompts (les 5 modes) avec la grille des 4 canaux
- Enrichir le format YAML des exercices avec des indices multimodaux pré-écrits
- Mettre à jour l'Île 1 au nouveau format

## 5.2 Apprentissage n°2 — Trou architectural du visuel

**Découverte** : plusieurs exercices supposent un schéma (Île 1 Session 1 ex.3 et ex.4, et toute l'Île 6 Géométrie). L'app n'affiche aucun visuel. Archimède décrit en mots — bancal.

**Implication Sprint 3** :
- Ajouter un champ `visuel:` (chemin SVG) au format YAML des exercices
- Enrichir `ui/ecran_session.py` pour afficher l'image quand elle existe
- Produire les SVG nécessaires (chantier visuel à planifier — toi, ton épouse, peut-être Grok)

## 5.3 Apprentissage n°3 — Calibration de l'accueil des bonnes réponses

**Découverte** : quand l'enfant donne la bonne réponse du premier coup, Archimède ne valide pas — il creuse le sens. Maïeutique exigeante, mais peut frustrer un enfant qui a juste.

**Implication Sprint 3** :
- Retoucher le prompt mode_decouverte : valider d'abord ("oui, c'est bien ça"), puis creuser ("et tu peux m'expliquer pourquoi ?"). Garder l'exigence dans le bon ordre.

---

# NIVEAU 6 — DÉCISIONS STRUCTURANTES ACTÉES

| # | Décision | Date | Conséquence |
|---|---|---|---|
| D1 | Nom de marque définitif : **Philia** | début projet | Architecture mère + 2 produits |
| D2 | ADN d'Archimède = brique commune aux 2 produits | Sprint 2 | Toute évolution mentor s'y conforme |
| D3 | Format YAML enrichi des exercices (énoncé + réponse + solution + indices + erreurs) | Sprint 2 | Non négociable (recherche Harvard) |
| D4 | Python 3.11 | Sprint 2 | `.venv` recréé |
| D5 | Embeddings OpenAI conservés (héritage IAXEL) | Sprint 2 | Cohérence avec l'index existant |
| D6 | Séquençage des exercices dans le moteur, pas l'UI | Sprint 2 | "Vitre vs cerveau" |
| D7 | MVP = 3 îles au 1er juillet, périmètre gravé | Sprint 1 | Si dérapage, on réduit le scope, jamais la date |
| D8 | Ennemi commercial = décrochage en maths, pas l'EN | Conception commerciale | Tout le marketing s'y aligne |
| D9 | Pricing MVP = 24€ Summer Premium + tier gratuit | Conception commerciale | Pas de tarification multiple au launch |
| D10 | La maïeutique ne se négocie jamais (Archimède ne donne JAMAIS la réponse) | ADN | Vrai dans tous les modes |
| D11 | Bascule Cowork au début du Sprint 3 | Fin Sprint 2 | Supprime copier-coller Architecte ↔ repo |
| D12 | Refonte gamification — métaphore Voyage / Cahier d'Aventures | 2026-06-01 | Sprint 3 reconçu autour du Voyage ; scope MVP révisé (3 îles + Carnet PDF) ; doc fondateur : `philia-voyage-fondateur.md` |

---

# NIVEAU 7 — PROCHAINES ÉTAPES IMMÉDIATES

## 7.1 Avant le démarrage du Sprint 3 — bascule outillage

1. **Bascule sur Cowork** — première étape du Sprint 3. Tu m'as confirmé que Cowork est installé. À configurer pour qu'il accède au repo `philia-summer-quest`. Session dédiée de 15-30 min.

## 7.2 Conception du Sprint 3 — à formaliser

2. **Brief Architecte Sprint 3** — découpage en tâches du sprint. Périmètre proposé :
   - Tâche 1 — Câblage visuel (champ YAML + affichage + 2-3 SVG de l'Île 1)
   - Tâche 2 — Enrichissement des prompts pour multimodalité de relance
   - Tâche 3 — Calibration accueil des bonnes réponses
   - Tâche 4 — Activation des modes Pratique et Validation
   - Tâche 5 — Premier prototype d'une planche de BD interactive (Session 1 Île 1) + câblage des clés et de la carte du trésor enrichie. Les cristaux deviennent des clés, les paliers d'élévation deviennent des étapes du Voyage.
   - Tâche 6 — Test E2E sur la Session 1 complète, validation par toi.

3. **Chantier de contenu parallèle** — toi et ton épouse commencez l'Île 2 (Forêt des Mesures) au format enrichi multimodal, sur le patron Île 1.

## 7.3 À planifier (sans urgence du jour)

4. **Chantier visuel** — production des SVG d'exercices et des illustrations d'îles. Identifier graphiste, prendre un premier rendez-vous.
5. **Vérification identifiant LLM** — retester le format daté `claude-sonnet-4-6-20260218` pour figer la version d'Archimède.
6. **Nettoyage RAG** — déduplication de `data/sources_maths/`, à programmer hors sprint critique.

---

# NIVEAU 8 — INDEX DES DOCUMENTS DE RÉFÉRENCE

| Document | Emplacement | Sert à |
|---|---|---|
| ADN d'Archimède | `.claude/contexts/philia-adn-archimede.md` | Identité, voix, principes du mentor |
| Prompts d'Archimède | `prompts/mentor/*.txt` | Instructions opérationnelles au LLM |
| Île 1 contenu | `.claude/pedagogie/ile-1-nombres-brises-CONTENU.md` | Source de vérité Île 1 |
| Document fondateur Voyage | `.claude/contexts/philia-voyage-fondateur.md` | Métaphore Voyage, mécaniques de récompense (remplace spec gamification v1) |
| Cadre jeu-programme | `.claude/pedagogie/philia-cadre-progression-jeu-programme-v1.md` | Grammaire de progression |
| Brief Implementer | `.claude/plans/philia-brief-implementer-technique-1a.md` | Spec dev 6 sprints |
| Workflow opératoire | `.claude/philia-workflow-operatoire-1b.md` | Méthode AXON-1 |
| Cahier graphiste | `.claude/production/philia-cahier-charges-graphiste-v1.md` | Brief production visuelle |
| Brief commercial | `.claude/commercial/` (à ranger) | Stratégie de mise en marché |
| Décisions | `.claude/memory/decisions.md` | Log des décisions structurantes |
| Apprentissages | `.claude/memory/learnings.md` | Ce qu'on a appris, à ne pas réapprendre |
| État projet | `.claude/memory/etat-projet.md` | Où on en est (mis à jour chaque sprint) |
| **CE DOCUMENT** | `.claude/memory/philia-bilan-structurel-v1.md` | Document de pilotage hiérarchique |

---

# CONCLUSION

À date, Philia Summer Quest a franchi deux sprints sur six. Le mentor maïeutique Archimède existe, dialogue, tient face à l'insistance, et s'ancre dans l'univers narratif. Le contenu pédagogique modèle (Île 1) est complet et validé. L'architecture technique est saine.

Le Sprint 3 est le sprint le plus structurant du MVP : il transforme un mentor *conversant* en mentor *multimodal*, et un jeu *narratif sur papier* en jeu *visuellement actif*. C'est aussi le sprint où on bascule sur Cowork et où le rythme de production de contenu par le Fondateur + Épouse doit s'industrialiser sur les 6 autres îles.

Le calendrier 1er juillet est tendu mais tenable, à condition de tenir le rythme et de ne jamais sacrifier la maïeutique pour gagner du temps.

---

*Bilan Structurel Philia Summer Quest v1.0 — document de pilotage hiérarchique.*
*À conserver dans `.claude/memory/philia-bilan-structurel-v1.md`.*
*À mettre à jour à chaque fin de sprint et à chaque décision structurante.*

"Refonte de la gamification autour de la métaphore Voyage / Cahier d'Aventures, actée le [1 juin 2026], document fondateur produit."