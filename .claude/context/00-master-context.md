# PHILIA / ELEVATION — Master Context

**Document de pilotage hiérarchique v2. Remplace `philia-bilan-structurel-v1.md` comme point d'entrée principal à toute reprise de travail.**
**Rédigé le 15 juillet 2026, à la suite du pivot stratégique acté ce jour par le fondateur.**
**Mis à jour le 15 juillet 2026 (même jour) — décisions du Décideur intégrées : architecture de marque tranchée, D7 révisée, D14/D19 reformulées, D17 tranché pour le format court, D23 dédoublé, D25-D28 actées, Niveau 8 ajouté.**

---

## NOTE D'USAGE

Ce document s'insère dans une lignée : `philia-bilan-structurel-v1.md` (4 juin 2026) racontait un projet à un seul produit et un seul format. Ce document en raconte deux. Il ne supprime pas l'ancien — l'ancien reste la mémoire du chantier été 7 semaines (voir `.claude/roadmap/branche-2027-cahier-ete.md`) — mais il devient la référence de pilotage courante.

À lire en entier à chaque reprise de travail. À mettre à jour à chaque décision structurante.

---

# NIVEAU 1 — LA VISION PRODUIT GLOBALE

## 1.1 Ce qui n'a pas changé

**Philia** reste la marque-mère. **Archimède** reste le mentor maïeutique unique, dont l'ADN (`.claude/contexts/philia-adn-archimede.md`) fait toujours autorité sur toute production, quel que soit le format. La règle d'or ne bouge pas : Archimède ne donne jamais la réponse.

## 1.2 Ce qui change — le pivot du 15 juillet 2026

Le projet portait jusqu'ici un seul produit : **Philia Summer Quest**, un chantier narratif de 7 semaines (*L'Ascension des Sept Îles*) destiné à l'été. Le fondateur acte un pivot en deux temps :

1. **Un nouveau format court** — la **Révision 10-15 jours** — vient s'intercaler avant le grand format été. Objectif : livrable pour la rentrée d'août et pour les vacances de la Toussaint 2026. Ce format reprend le même mentor, le même univers Syracuse/Archimède, mais compresse l'expérience sur 10 à 15 jours au lieu de 7 semaines.
2. Ce format court n'est pas un produit isolé : il est désigné **brique fondatrice d'Elevation Mentor IA**, le futur produit de tutorat annuel.

### Architecture de marque — tranchée le 15 juillet 2026 (Lecture A adoptée)

`nommage.md` (D1) écartait formellement le nom « Elevation IA » au profit de « Philia ». Le pivot réintroduisait « Elevation » pour le produit annuel, ce qui créait une tension avec D1. Le Décideur a tranché : **Lecture A**, la moins disruptive vis-à-vis de D1 — Philia reste la marque commerciale ombrelle, Elevation Mentor IA est un nom de produit sous cette marque.

| Niveau | Nom | Ce que c'est |
|---|---|---|
| Marque ombrelle | **Philia** | La marque commerciale globale, celle que voient les familles |
| Produit annuel | **Elevation Mentor IA** (nom provisoire, D26) | Tutorat continu. Vision longue : élémentaire → supérieur. Démarre par le collège, arc 6e → 3e → lycée |
| Format été | **Philia Summer Quest** | Le chantier narratif 7 semaines, *L'Ascension des Sept Îles* — en pause, chantier 2027 (voir `branche-2027-cahier-ete.md`) |
| Brique fondatrice | **Format Révision 10-15 jours** | Première brique / MVP d'Elevation Mentor IA, priorité d'exécution immédiate (D25) |

Le nom commercial définitif d'Elevation Mentor IA reste ouvert (D26) — ce document utilise le nom de travail jusqu'à décision contraire.

## 1.3 La proposition de valeur, dans les deux formats

Un mentor IA maïeutique (Archimède) qui ne donne jamais la réponse, ancré dans l'univers narratif de Syracuse antique, qui fait progresser l'enfant en compétence et en autonomie de raisonnement. Ce qui distingue les deux formats n'est pas la pédagogie — identique dans les deux cas — mais le rythme, la durée d'engagement et la fonction commerciale.

---

# NIVEAU 2 — POSITIONNEMENT DES DEUX FORMATS

| | **Format Chantier d'Été** (existant) | **Format Révision 10-15j** (nouveau) |
|---|---|---|
| Nom narratif | L'Ascension des Sept Îles | À nommer (pas encore acté — proposition à valider : un « chapitre » ou une « expédition » de l'Ascension, pas un univers séparé) |
| Durée | 7 semaines | 10 à 15 jours |
| Périmètre pédagogique | 7 îles à terme (3 au MVP initial) | 3 îles (Île 1, 2, 3 — fractions, mesures, calcul littéral) |
| Fenêtre de lancement | Été (juillet-août) | Rentrée d'août 2026 + vacances de la Toussaint 2026 — lancement désormais fixé au 15 août 2026 (D7 révisée) |
| Fonction stratégique | Produit d'appel été, expérience complète et immersive (carnet imprimable, BD, triple récompense) | Brique fondatrice d'Elevation Mentor IA — produit de test, plus court, réutilisable plusieurs fois par an |
| Public visé | Enfants 10-12 ans, CM2/6e | Élargi à terme 6e-3e-lycée (mais MVP 10-15j reste calé sur le contenu 6e existant — voir Niveau 3) |
| État de production | Île 1 codée et jouable ; Îles 2-3 en narration seulement ; Îles 4-7 en esquisse ou reportées | À construire à partir de l'existant — voir roadmap dédiée et Niveau 8 |
| Document de pilotage | `.claude/roadmap/branche-2027-cahier-ete.md` | `.claude/roadmap/roadmap-15juillet-15aout.md` |

**Lecture stratégique** : le format été n'est pas abandonné, il est **mis en pause** et redevient un chantier 2027 (voir document 3). Le format court devient la priorité d'exécution immédiate, parce qu'il est atteignable avant la rentrée avec l'existant (Île 1 complète, moteur technique opérationnel, univers narratif posé) et parce qu'il sert un objectif plus large : prouver le modèle Elevation Mentor IA sur un cycle court avant d'investir dans l'architecture lourde du produit annuel (mémoire 15 ans, GraphRAG, Système 1/2, multimatière — mentionnée dans le bilan v1 comme vision Philia Année).

---

# NIVEAU 3 — ÉTAT DES 7 ÎLES ET STATUT MVP

| # | Île | Concept | Statut contenu | Statut technique | MVP Format Révision 10-15j |
|---|---|---|---|---|---|
| 1 | L'Île des Nombres Brisés | Fractions (6e + anticipation 5e) | Complet (`pedagogie/contenu_ile1.py`, 5 sessions, cristaux nommés C1-C5) | Jouable de bout en bout (avatar -> carte -> session -> clé) | **Dans le périmètre — prête, densité préservée (5 sessions, voir §8.2)** |
| 2 | La Forêt des Mesures | Grandeurs, périmètres, aires | Narration ~80% rédigée (`narration-iles.md`), cristaux nommés (`constants.py`) | Aucun contenu pédagogique codé (`contenu_ile2.py` inexistant) | **Dans le périmètre — à produire, resserré à 3 sessions (§8.2)** |
| 3 | Le Labyrinthe des Inconnues | Calcul littéral, équations simples | Narration ~80% rédigée, cristaux nommés | Aucun contenu pédagogique codé (`contenu_ile3.py` inexistant) | **Dans le périmètre — à produire, resserré à 3 sessions. Accueille désormais l'énigme finale de révélation (D17 tranché, §8.4)** |
| 4 | Le Royaume des Proportions | Proportionnalité, pourcentages | Esquisse narrative seulement, cristaux placeholders (« à nommer ») | Rien | Hors périmètre |
| 5 | La Vallée des Nombres Relatifs | Nombres relatifs (anticipation 5e) | Esquisse narrative seulement, cristaux placeholders | Rien | Hors périmètre |
| 6 | La Cité des Formes | Géométrie | Reportée v1.2 (D16) — hors catalogue cristaux | Rien | Hors périmètre |
| 7 | La Tour des Données | Statistiques | Esquisse narrative | Rien | Hors périmètre — **la révélation finale ne l'attend plus** : D17 a été tranché pour rattacher le secret d'Archimède à la fin de l'Île 3 dans le format court (voir D17 au Niveau 4). Pour le grand format 2027, la question de la place de l'Île 7 reste ouverte, voir `branche-2027-cahier-ete.md`. |

**Point de vigilance Reviewer, toujours actif** : l'audit `.claude/audit/ile1-c2-c5-objets-hors-univers.md` (28 juin 2026) a catalogué des objets hors-univers (tarte, gâteau, fruits...) dans les sessions C2-C5 de l'Île 1. Le code (`pedagogie/contenu_ile1.py`) a depuis été corrigé (commit T8.4 Phase 3, 28 juin — zéro occurrence vérifiée). **Mais le document source `.claude/pedagogie/ile-1-nombres-brises-CONTENU.md` n'a pas été mis à jour** (27 occurrences des mêmes termes proscrits toujours présentes). Ce document n'est donc plus la source de vérité qu'il prétend être — à corriger ou à requalifier en amont de toute production Île 2/3 qui s'en inspirerait.

---

# NIVEAU 4 — DÉCISIONS ACTÉES D1 À D28, EN SYNTHÈSE

| # | Décision | Statut |
|---|---|---|
| D1 | Nom de marque définitif : Philia (Elevation IA et MAÏA écartés) | Actée — **tension avec Elevation Mentor IA résolue le 15 juillet, Lecture A adoptée (voir §1.2)** |
| D2 | ADN d'Archimède = brique commune à tous les produits Philia | Actée, toujours en vigueur |
| D3 | Format YAML enrichi des exercices, non négociable | Actée, toujours en vigueur |
| D4 | Python 3.11 | Actée |
| D5 | Embeddings OpenAI conservés | **Obsolète — voir D13 (RAG supprimé)** |
| D6 | Séquençage des exercices dans le moteur (SessionEngine), pas l'UI | Actée, toujours en vigueur |
| D7 | MVP = 3 îles au 1er juillet, périmètre gravé, jamais la date | **Révisée le 15 juillet 2026** : le 1er juillet n'a pas été tenu (voir Niveau 5). Le Décideur repart de la réalité du terrain plutôt que de forcer l'ancienne date. Nouveau jalon : lancement du Format Révision 10-15j fixé au **15 août 2026**. L'esprit de la règle est reconduit à l'identique sur ce nouveau jalon (voir roadmap §0) : on réduit le périmètre, jamais la date. |
| D8 | Ennemi commercial = décrochage en maths, pas l'EN | Actée |
| D9 | Pricing MVP Summer Quest = 24€ Summer Premium + tier gratuit | Actée sur le papier, jamais implémentée (pas de paywall codé). Le pricing du Format Révision 10-15j est distinct — voir D26 et §8.5 (19€) |
| D10 | La maïeut2ique ne se négocie jamais | Actée, non-négociable, toujours en vigueur |
| D11 | Bascule Cowork au début du Sprint 3 | Actée et opérationnelle depuis le 4 juin |
| D12 | Refonte gamification — métaphore Voyage / Cahier d'Aventures | Actée, structure toujours en vigueur |
| D13 | Suppression du RAG (Option C) — tout passe par YAML + prompts | Actée, implémentée |
| D14bis | **(reformulée le 15 juillet, remplace l'ancienne D14 jamais rédigée)** — `archipel_isometrique` : vignette de l'Île 1 sur la carte de l'archipel (câblage assets narratifs) | Actée |
| D15 | Le calcul numérique est transversal, pas d'île dédiée | Actée |
| D16 | Île 6 (géométrie) reportée à v1.2, hors MVP | Actée, toujours en vigueur |
| D17 | Promesse narrative finale = secret d'Archimède (couronne d'Hiéron) | **Tranchée le 15 juillet pour le format court** : l'enfant qui termine les Îles 1-2-3 découvre le secret de la poussée d'Archimède via une **énigme finale après l'Île 3**, résolue par l'enfant lui-même (maïeutique préservée, pas de récit passif). Le poster/parchemin physique en récompense est **différé post-MVP**. Pour le grand format 2027 (7 îles), le Scénario A/B originel n'est pas re-tranché par cette décision — voir `branche-2027-cahier-ete.md`. |
| D18 | Personnalisation visuelle binaire (fille/garçon), personnages canoniques Sassou/Mélian | Actée, avec amendement de tolérance interprétative (15 juin) |
| D19bis | **(renommée le 15 juillet depuis l'ancienne D19 jamais rédigée)** — Le prénom de l'élève est saisi à l'inscription, injecté dans les prompts d'Archimède, avec fallback « Élévateur » si absent | Actée |
| D20 | Seuil qualité graphique MVP = « B » (reconnaissable, lisible, pas de texte halluciné) | Actée |
| D21 | Méthodologie des 3 beats pour les planches BD (problème / déclencheur maïeutique / résolution) | Actée |
| D22 | UX planches BD : modal full-screen après résolution, placeholders si non produite | Actée, implémentée (T8.1) |
| D23a | **(renumérotée le 15 juillet, ancienne D23 première occurrence)** — Pattern `planche_key` normalisé | Actée |
| D23b | **(renumérotée le 15 juillet, ancienne D23 seconde occurrence)** — Test E2E avec cobaye 11-12 ans | Actée |
| D24 | Maïeutique préservée avant planche BD (bouton « Terminer » gaté par au moins 1 tour de bilan) | Actée, implémentée |
| **D25** | **Format Révision 10-15 jours = priorité d'exécution immédiate.** Le chantier été 7 semaines est mis en pause, redevient chantier 2027. | **Actée le 15 juillet 2026** |
| **D26** | **Elevation Mentor IA = nom provisoire du produit annuel sous marque Philia.** Périmètre visé : élémentaire → supérieur, démarre par le collège 6e-3e. Décision de nom commercial définitif reportée. | **Actée le 15 juillet 2026** |
| **D27** | **Célébrations** : légères par bonne réponse (confetti + toast personnalisé au prénom de l'enfant). Fin d'île : célébration forte via planche BD spéciale + message d'Archimède écrit comme s'il venait personnellement de lui. | **Actée le 15 juillet 2026** |
| **D28** | **Cinématiques HeyGen** : 2 vidéos courtes — ouverture avant l'onboarding (présentation de l'aventure) et clôture après l'Île 3 (secret découvert + teasing Elevation Mentor IA annuel). | **Actée le 15 juillet 2026** |

**Dette documentaire restante, à reporter dans `decisions.md` lui-même** (ce document de synthèse intègre les reformulations D14bis/D19bis/D23a/D23b/D25-D28, mais le journal source `.claude/memory/decisions.md` n'a pas encore été mis à jour en miroir — travail à faire par toi ou l'Implementer, ce document n'y touche pas).

---

# NIVEAU 5 — RÉALITÉ DU CALENDRIER AU 15 JUILLET 2026

À dire clairement, parce que c'est la base factuelle de tout le reste : **le MVP du 1er juillet 2026 n'a pas été livré tel que prévu par l'ancienne D7.**

Ce qui a été fait, dans les faits (git log à l'appui) :
- Sprint 1 (24-26 mai) et Sprint 2 (27 mai) : fondations, mentor Archimède, mode Découverte — terminés dans les temps.
- Sprint 3 (4-28 juin) : les tâches T1 à T8.4 ont été livrées — 5 modes pédagogiques, carte de l'archipel, onboarding avatar, système clés/cristaux, modal planches BD, ancrage narratif pur Syracuse sur l'Île 1. C'est un sprint dense et réellement abouti.
- **28 juin -> 13 juillet : silence quasi total sur le repo.** Le seul commit de la période (13 juillet) est un correctif mineur de câblage de l'écran avatar dans le routing.
- Aucun Sprint 4, 5 ou 6 n'a eu lieu. Conséquence directe : **paywall Stripe, conformité RGPD, dashboard parent, bilan hebdo email — tout cela reste à l'état de plan sur le papier, aucune ligne de code.** Îles 2 et 3 n'ont aucun contenu pédagogique produit malgré une narration avancée.

Ce n'est pas un jugement, c'est un constat nécessaire pour que la roadmap du pivot (document 2) parte d'un périmètre réel et non du périmètre rêvé de mai.

**Suite donnée le 15 juillet** : D7 a été formellement révisée (voir Niveau 4). Le nouveau jalon n'est plus le 1er juillet mais le **15 août 2026**, avec le même principe de gravure : on réduit le périmètre avant de toucher à la date.

---

# NIVEAU 6 — RÔLES AXON-1 (mise à jour post-pivot)

Le workflow AXON-1 passait jusqu'ici par trois acteurs. Avec la bascule Cowork opérationnelle (D11) et le pivot du jour, il se précise en quatre rôles :

| Rôle | Qui | Fait quoi |
|---|---|---|
| **Décideur** | Toi, le fondateur | Décide, tranche les arbitrages restants (nom narratif du format court, nom commercial définitif d'Elevation Mentor IA — D26, cadence Reviewer), valide le contenu mathématique avec ton épouse, teste le produit |
| **Architect (Cowork)** | Claude, en session Cowork sur ce repo | Produit les specs, les briefs de sprint, les roadmaps, les audits, les documents de conception — directement dans le repo, sans copier-coller. C'est le rôle de ce document. |
| **Reviewer (Claude.ai)** | Claude, en session Claude.ai séparée (hors repo) | Seconde paire d'yeux ponctuelle, notamment pour des revues de fin de sprint ou des arbitrages où l'indépendance du regard compte. Rôle hérité de l'ancien workflow à 3 acteurs — sa cadence exacte dans le nouveau rythme (10-15j) reste à définir avec toi. |
| **Implementer** | Claude Code, dans VS Code | Écrit le code, sprint par sprint, dans le périmètre défini par l'Architect. Ne code jamais hors du périmètre du sprint courant. |

**Règle inchangée** : l'Architect ne code pas. Il produit, l'Implementer exécute, le Décideur valide avant tout commit significatif.

---

# NIVEAU 7 — INDEX DES DOCUMENTS DE RÉFÉRENCE

| Document | Emplacement | Sert à |
|---|---|---|
| Ce document | `.claude/context/00-master-context.md` | Point d'entrée courant, synthèse vision + décisions + rôles |
| Ancien bilan (pré-pivot) | `.claude/memory/philia-bilan-structurel-v1.md` | Mémoire de l'état du projet au 4 juin, avant le pivot — conservé, non mis à jour |
| Roadmap Format Révision 10-15j | `.claude/roadmap/roadmap-15juillet-15aout.md` | Plan d'exécution du pivot, S1-S4 + tampon |
| Mémoire du chantier été (branche 2027) | `.claude/roadmap/branche-2027-cahier-ete.md` | Ce qui est préservé et ce qui reste pour l'été 2027 |
| ADN d'Archimède | `.claude/contexts/philia-adn-archimede.md` | Identité et voix du mentor — commune aux deux formats |
| Nommage | `.claude/contexts/nommage.md` | Architecture des noms — à revisiter à la lumière du pivot |
| Voyage fondateur | `.claude/contexts/philia-voyage-fondateur.md` | Vision narrative et gamification du format été |
| Narration des îles | `.claude/production/narration-iles.md` | Textes narratifs île par île |
| Décisions | `.claude/memory/decisions.md` | Log détaillé D1-D24 — **à mettre à jour en miroir avec les reformulations D14bis/D19bis/D23a/D23b/D25-D28 de ce document, non fait automatiquement** |

---

# NIVEAU 8 — DÉCISIONS PRODUIT DU 15 JUILLET 2026 (DÉTAIL D'EXÉCUTION)

Ce niveau détaille les décisions produit prises par le Décideur le 15 juillet 2026, en complément de la synthèse D25-D28 du Niveau 4. Il sert de cahier des charges resserré pour `.claude/roadmap/roadmap-15juillet-15aout.md`.

## 8.1 Périmètre technique MVP

- Îles 1, 2, 3 — seul périmètre pédagogique du Format Révision 10-15j (inchangé depuis le pivot initial)
- Prénom de l'élève (D19bis) — saisi à l'inscription, injecté dans les prompts d'Archimède, fallback « Élévateur »
- Cinématiques HeyGen (D28) — 2 vidéos courtes, ouverture avant onboarding + clôture après Île 3
- Célébrations (D27) — confetti + toast personnalisé au prénom par bonne réponse, planche BD spéciale + message d'Archimède en fin d'île

## 8.2 Périmètre pédagogique

- Île 1 : 5 sessions (profondeur préservée — contenu déjà validé, ne pas retoucher)
- Île 2 et Île 3 : 3 sessions chacune (resserré par rapport aux 5 sessions d'Île 1 — arbitrage de densité pour tenir le calendrier)
- Total : 11 sessions, environ 65 exercices sur 10 à 15 jours de jeu

**Note Architect** : ce resserrement (3 sessions au lieu de 5 pour Île 2-3) allège la charge de production contenu par rapport à ce qu'une symétrie stricte avec l'Île 1 aurait impliqué. Répercuté dans la roadmap.

## 8.3 Périmètre graphique

Sobriété assumée : environ 12 images restantes à produire après l'Île 1.

**Assets mutualisés** (« globaux », réutilisés sur tout le parcours) :
- `accueil_invitation` — image d'ouverture avant onboarding
- `archipel_isometrique` — vignette de l'Île 1 sur la carte de l'archipel (D14bis)
- `presentation_archipel_<genre>` — existant (chemin de fer V1)
- `ecran_session_<genre>` — existant partiellement (chemin de fer V2)

**Assets par île** (×3, Île 1-2-3) :
- Vue immersive
- Scène d'arrivée
- Scène de présentation
- Planche BD de synthèse (une seule par île — resserré par rapport au standard « une planche par session » du format été)

## 8.4 Périmètre narratif

Univers Syracuse intégralement préservé, aucune dilution malgré la compression du format. La promesse narrative se referme sur une **énigme finale après l'Île 3**, révélant le secret de la poussée d'Archimède — résolue par l'enfant, jamais racontée par le mentor (cohérence maïeutique, D17 tranché).

## 8.5 Périmètre commercial

- Prix : **19€**, vendu sur deux fenêtres — rentrée et Toussaint (même produit, deux occasions de vente dans l'année)
- Passerelle vers Elevation Mentor IA : teasing en cinématique de clôture (D28), pas de vente agressive intégrée au parcours — le format court sert d'abord à prouver l'expérience avant de vendre la suite

## 8.6 Cadence des tests cobaye

- Tests informels continus, entre les semaines, sur les enfants du fondateur (fils/fille) — retour de terrain rapide, non structuré
- Test formel en semaine 4 (bêta), protocole plus complet — cobaye élargi au-delà du cercle familial si possible

---

*Master Context Philia/Elevation — document de pilotage hiérarchique v2.*
*À mettre à jour à chaque décision structurante du pivot.*
