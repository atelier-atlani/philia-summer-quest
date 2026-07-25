# Décisions d'Architecture — Philia Summer Quest

## Hors-sprint — 2026-05-26

### ADN Archimède acté comme brique fondatrice du mentor

**Décision** : le document `.claude/contexts/philia-adn-archimede.md` est désigné noyau pédagogique commun à l'ensemble de la marque Philia. Il définit l'identité, la posture et la voix du mentor maïeutique Archimède.

**Portée** : ce document fait autorité pour les deux produits (Philia Summer Quest et Philia année scolaire). Toute implémentation future du mentor dans l'un ou l'autre produit doit s'y conformer. Il prime sur les guardrails pédagogiques en cas de contradiction sur la voix ou la posture du mentor.

**Précision D013 (19 juillet 2026, n'annule pas la décision ci-dessus, la précise)** : le produit "Philia année scolaire" mentionné ci-dessus est rebaptisé **Elevation IA** (nomenclature D013, voir D29 plus bas). La portée de ce document est également précisée : le *noyau pédagogique* (valeurs, principes, architecture maïeutique) fait autorité pour les deux sous-produits, mais le *personnage* Archimède et l'univers narratif de Syracuse restent propres à Summer Quest — Elevation IA aura sa propre identité de mentor, construite sur la même méthodologie. Voir `.claude/contexts/philia-adn-archimede.md` (mis à jour le 19 juillet) et D29.

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

**Conséquence pour Philia Année** [terme rebaptisé Elevation IA depuis D013, 19 juillet 2026 — décision historique non réécrite] : le RAG sera reconstruit de zéro pour Elevation IA (12 mois) avec un référentiel propre, structuré, peut-être en double couche (référentiel mathématique + univers narratif). Le RAG IAXEL actuel n'aurait de toute façon pas servi de base solide.

### D16 — Géométrie (Île 6 — La Cité des Formes) reportée à v1.2

**Décision** : L'Île 6 est exclue du MVP 1er juillet. Elle restera en `statut_mvp: v1_2` (livraison août).

**Justification** : La géométrie 6e implique des manipulations visuelles (constructions, symétries, tracés) qui nécessitent un développement Plotly/SVG plus poussé que les îles numériques. Intégrer ce chantier dans le MVP ferait rater la date — or la règle est : on réduit le scope, jamais la date.

**Périmètre MVP confirmé** : 3 îles — Fractions/décimaux (Île 1), Grandeurs/mesures (Île 2), Calcul littéral (Île 3).

**Communication parents** : "le MVP couvre fractions, mesures, calcul littéral — la géométrie arrive en août".

### D15 — Le calcul numérique est transversal (pas d'île dédiée)

**Décision** : Il n'y a pas d'île dédiée au calcul numérique (priorité des opérations, calcul mental, parenthèses). Ces compétences sont des outils transversaux travaillés dans chaque île, au service du domaine de l'île.

**Note pour les concepteurs de contenu** : chaque île doit inclure des exercices qui mobilisent du calcul numérique propre à son domaine. Ce n'est pas un contenu en plus — c'est une exigence de conception à intégrer dès la rédaction des sessions.

### D17 — Promesse narrative finale du Voyage : le secret d'Archimède (Île 7)

**Décision** : La révélation finale qui couronne le Voyage des Sept Îles est **le principe de la poussée d'Archimède** (Eurêka, IIIᵉ siècle av. J.-C.). Quand l'enfant termine la 7ᵉ île et obtient sa 7ᵉ clé, Archimède lui révèle le secret qu'il a découvert dans son bain il y a plus de 2300 ans : comment distinguer l'or véritable de l'or apparent par la densité (déplacement d'eau).

**Promesse narrative posée dès l'accueil** : "Pour chaque île que tu réveilleras, tu gagneras une clé. Et au bout du voyage, quand les sept clés seront entre tes mains, j'ouvrirai pour toi le coffre de mon secret le plus précieux — celui que j'ai découvert dans un bain, il y a plus de deux mille ans."

**Justification pédagogique — la boucle métaphorique** :
1. Le secret factuel d'Archimède (principe physique) permet de distinguer l'or de l'argent sous une apparence dorée identique : la densité ne ment pas.
2. La métaphore pédagogique pour Philia : on peut dire "j'ai compris" sans avoir compris ; seule la **capacité à expliquer** (Mode Validation, technique Feynman) ne ment pas. C'est la "densité cognitive" de l'enfant.
3. Pendant 7 semaines, l'enfant traverse des Modes Validation Feynman qui le forment exactement à cela : distinguer la compréhension réelle de l'apparence de compréhension.
4. La révélation finale est donc à la fois **historique** (le moment Eurêka d'Archimède), **scientifique** (principe de la poussée) et **réflexive** (l'enfant comprend rétrospectivement qu'il a passé tout son été à pratiquer la méthode d'Archimède sans le savoir).

**Conséquence pour la production** :
- L'Île 7 (statut v1.2 selon D16 — à confirmer si maintenue ou déplacée pour intégrer cette finale) doit culminer sur cette révélation comme cinématique de fin de Voyage.
- Le texte d'accueil narratif (sprint 3, T6) intègre la promesse "secret découvert dans un bain" sans le nommer — suspense narratif construit sur les 7 semaines.
- Tout le storytelling intermédiaire (récompenses, fragments de lore, dialogues d'Archimède en fin d'île) peut graviter autour de ce secret final sans le révéler.

**Note importante pour la cohérence avec D16** : D16 reporte la géométrie (Île 6 — Cité des Formes) en v1.2. La promesse "7 îles + 7 clés + secret final" doit donc être vérifiée à la lumière du périmètre MVP réel (3 îles). Deux scénarios possibles, à trancher avant le sprint contenu :
- **Scénario A** : on accepte que le MVP ne livre pas le secret final (3 îles → 3 clés → message "à suivre dans la prochaine version"). La promesse narrative reste cohérente, mais elle décale la révélation à v1.2/août.
- **Scénario B** : on réécrit la promesse pour qu'elle s'adapte au MVP 3 îles (3 clés ouvrent un "premier coffre" / "premier secret"), et le secret de la poussée d'Archimède devient la révélation de la fin de l'aventure complète (post-v1.2).

Décision sur A vs B à acter avant Sprint 4 (contenu narratif).

# D18 — Stratégie de personnalisation visuelle MVP (Option 4 — Personnalisation binaire)

**Date** : 13 juin 2026 (Sprint 3, jour 4)
**Statut** : Actée

**Contexte** : la planification du chemin de fer narratif pour le MVP 3 îles a soulevé la question du nombre de variantes visuelles nécessaires pour les scènes narratives (cinématiques, planches BD, présentations). Trois options ont été pesées : personnalisation minimale (1 élévateur canonique unique, impersonnel), personnalisation hybride (variantes par archétype, infaisable en 18 jours), personnalisation maximale (8 versions par scène, infaisable). Une 4e option a émergé : personnalisation binaire par genre.

**Décision** :
- L'avatar choisi par l'enfant détermine son apparence dans la sidebar et dans l'écran de session (8 avatars distincts disponibles, T6 livré).
- Les scènes narratives (présentation archipel, arrivée sur île, présentation île par Archimède, planches BD, rite d'élévation) existent en **2 versions** : une avec un élévateur canonique fille, une avec un élévateur canonique garçon.
- L'app sélectionne la version selon le champ `avatar_genre` du joueur courant.

**Personnages canoniques retenus** :
- **Élévatrice canonique fille** : Sassou (archétype architecte, cheveux courts bruns, lunettes ou sans, sac à dos d'architecte) — déjà produite dans les 5 images Midjourney existantes
- **Élévateur canonique garçon** : Mélian (archétype explorateur, brun) — à produire

**Asymétrie d'archétype assumée** : Sassou est architecte, Mélian est explorateur. Cette asymétrie est acceptée pour préserver le travail Midjourney déjà investi. À l'échelle d'un enfant de 11-12 ans, la dimension genre est plus saillante que la dimension archétype.

**Convention de nommage des fichiers** :
- Scènes avec personnage(s) : `<contexte>_<genre>.png` (`genre` ∈ {`fille`, `garcon`})
- Scènes génériques sans personnage : `<contexte>.png`
- Exemples : `assets/narratif/globaux/presentation_archipel_fille.png`, `assets/narratif/ile_1/vue_immersive.png`

**Hors scope MVP** :
- Personnalisation archétypale (architecte / pilote / explorateur / aventurier) dans les scènes narratives
- Animations / cinématiques générées dynamiquement
- Variantes émotionnelles d'Archimède dans les scènes narratives

**Reporté à Sprint 5+** : personnalisation archétypale incrémentale par scène-clé selon la maturité du produit après lancement.

**Conséquences techniques** :
- Code app simple : `image = f"assets/narratif/{contexte}_{genre}.png"`
- Volume de production cible : ~48 images pour MVP 3 îles (voir chemin de fer)

**Amendement D18 — Tolérance d'interprétation visuelle de Sassou et Mélian** (acté le 15 juin 2026) :

La production Midjourney + ChatGPT révèle que les personnages canoniques Sassou
et Mélian subissent naturellement des variations interprétatives entre les
scènes (couleurs de tenue, accessoires secondaires, posture).

Plutôt que de forcer la rigidité canonique au prix de régénérations infinies,
on accepte ces variations d'une scène à l'autre tant que le personnage reste
**reconnaissable comme lui-même** :

- **Critères de reconnaissance Sassou** : fille, brune, cheveux courts au carré,
  silhouette d'architecte (carnet, sac à bandoulière, ou stylet visible),
  regard intelligent et doux.
- **Critères de reconnaissance Mélian** : garçon, brun, cheveux courts ondulés,
  silhouette d'explorateur (sac d'exploration ou accessoire d'aventurier
  visible), regard curieux.

Hors de ces critères, les détails secondaires (couleur exacte de la tunique,
accessoires variés, mèches de cheveux subtiles) peuvent varier d'une scène à
l'autre sans déclencher de régénération.

Méthode de production confirmée : Midjourney pour la génération visuelle
itérative + ChatGPT (ou Claude.ai en parallèle) pour la rédaction des prompts
scènes adaptés. Les blocs canoniques Sassou et Mélian restent les références
mais fonctionnent comme **directives stylistiques** plutôt que comme contraintes
strictes pixel-identiques.

## D20 — Seuil qualité graphique MVP (17 juin 2026)

Acceptation seuil "B" pour les planches BD MVP.

Critères minimaux retenus :
- Personnage principal (Sassou ou Mélian) reconnaissable
- Archimède identifiable (cheveux blancs + robe bleue)
- Lecture narrative globale possible
- Pas de texte halluciné visible en gros plan
- Style aquarelle Syracuse conservé

Refonte qualité "A" planifiée en V1.1 post-lancement.

Raison : 48 images restantes à produire en 15 jours, recherche
d'itération qualité parfaite incompatible avec deadline 1er juillet.

## D21 — Méthodologie scène-narrative-pédagogique (17 juin 2026)

Toute planche BD respecte la règle des 3 beats :
1. Beat problème : conflit mathématique incarné dans objets dénombrables
2. Beat déclencheur : Archimède désigne sans résoudre (maïeutique)
3. Beat résolution : enfant agit sur objets, Eurêka naissant

Règle "lisibilité numérique" : quantités exactes visibles et comptables.
Le calcul reste implicite et visuel (NO NUMBERS WRITTEN).
## D23 — Pattern planche_key normalisée (28 juin 2026)

Toute session pédagogique expose une clé `planche_key` (format `"cN"`)
dans ses métadonnées, indépendamment du label affiché en UI.

**Séparation des responsabilités** :
- `"concept"` : label lisible pour l'UI (`"C1 — Sens d'une fraction"`)
- `"planche_key"` : clé filesystem déterministe (`"c1"`)

**Usage** : construction des chemins d'assets graphiques
`assets/narratif/<ile_id>/planche_bd_<planche_key>_<genre>.png`

**Portée** : toutes les sessions pédagogiques, toutes les îles.
Sessions sans planche associée exposent `"planche_key": None`.

**Conséquences techniques** :
- `META_SESSION_X` dans `pedagogie/contenu_ile1.py` (et futurs `contenu_ile2.py`, etc.)
  doit inclure le champ `planche_key`
- `ui/modal_planche_bd.py` lit `meta["planche_key"]` — jamais `meta["concept"]`
- Aucune extraction/parsing de `"concept"` pour dériver un chemin filesystem
## D22 — UX planches BD (17 juin 2026)
Affichage en modal full-screen après résolution complète du problème
mathématique. Petit texte de positionnement dans la quête (Île N —
Chapitre X validé — Encore Y avant la clé). Placeholders pour planches
non produites.

## D23 — Test E2E avec cobaye 11-12 ans (17 juin 2026)
Cobaye réel disponible avant lancement. T8.2 dépend de sa disponibilité.

## D24 — Maïeutique préservée avant planche BD (17 juin 2026)
Le bouton "Terminer le chapitre ✓" n'apparaît qu'après au moins 1
tour de dialogue de Bilan maïeutique (nb_tours_bilan >= 1). La planche
BD reste la récompense, mais vient après verbalisation guidée.
Implémentation : compteur nb_tours_bilan dans SessionEngine + gating
UI dans ecran_session.py (D-T8.1-F du brief T8.1).


## D29 — Nomenclature Philia / Elevation IA / Summer Quest (19 juillet 2026)

**Décision** : application de la nomenclature D013, décidée dans le repo axon-1, à l'ensemble de la documentation `.claude/` de ce repo.

- **Philia** = le projet / la marque mère.
- **Elevation IA** = sous-produit 1, mentor coach IA sur l'année, de l'élémentaire au supérieur (collège et lycée inclus).
- **Summer Quest** = sous-produit 2, cahier de vacances gamifié courte durée, deux formats : chantier été 7 semaines (en pause, chantier 2027) et Format Révision 10-15 jours / 1-2 semaines (priorité actuelle jusqu'au 15 août 2026).
- **Archimède** = nom du mentor dans l'univers narratif des îles de Syracuse, c'est-à-dire Summer Quest uniquement. Il n'est pas le mentor d'Elevation IA.

**Terminologie écartée** : "Elevation Philia", "Elevation Mentor IA", "Philia Année" — ne plus utiliser dans les nouvelles productions.

**Portée** : documentation `.claude/` (contexts, roadmap, master-context, CLAUDE.md, decisions.md). Aucun fichier de code (`pedagogie/`, `ui/`, `jeu/`, `prompts/`) n'est concerné par cette décision — ces fichiers ne mentionnent pas cette nomenclature de toute façon.

**Cas non tranchés, à valider par le Décideur** :
- L'identité du futur mentor d'Elevation IA (nom, persona) reste entièrement à concevoir — `philia-adn-archimede.md` ne fait que retirer Archimède du périmètre d'Elevation IA, il ne propose pas de remplaçant.
- Les entrées historiques de `decisions.md` (D2, D13) et de `philia-bilan-structurel-v1.md` mentionnant "Philia année scolaire" ou "Philia Année" n'ont pas été réécrites — seulement annotées — pour préserver l'exactitude du journal à la date où ces décisions ont été prises. `learnings.md` n'a pas non plus été modifié pour la même raison (log daté).

**Référence** : D013, repo axon-1 (externe à ce repo).

## D30 — Prix Format Révision 10-15j : 19€ (20 juillet 2026)

**Décision** : le prix du Format Révision 10-15 jours est fixé à 19€.
Remplace le pricing D9 (24€ Summer Premium + tier gratuit / 19.80€
Early Bird), qui portait sur le format été 7 semaines.

**Justification** : changement de format. Le produit n'est plus un
cahier de vacances de 7 semaines mais une révision de 1 à 2 semaines.
Le prix suit la durée d'engagement, pas la marque.

**Portée** : D9 reste valable pour le chantier été 2027 sur sa branche.
Aucune contradiction — deux formats, deux prix.

**Conséquence** : master context §8.5 déjà à jour. Landing page et
dispositif de paiement (Stripe Payment Link, décision ouverte n°1 de
la roadmap) à caler sur 19€.

## D31 — Protocole de test cobaye #1 (20 juillet 2026)

**Décision** : le test cobaye se fait en audio + prise de notes libre,
sans grille papier pendant la session. La grille structurée est
remplie a posteriori à la réécoute.

**Justification** : à 11-12 ans, voir l'adulte noter modifie le
comportement de l'enfant (effet de performance). La grille pendant le
test fait aussi décrocher l'observateur du sujet.

**Règle non négociable** : l'observateur n'intervient pas pendant le
test. Une seule relance autorisée (« qu'est-ce que tu cherches ? »),
3 fois maximum. Le blocage est une donnée, pas un incident à corriger.

**Métrique principale** : restitution narrative spontanée (Q1 du
questionnaire post-test). C'est la mesure de l'effet réel de T8.4 et
T8.5.

**Livrable** : `.claude/production/kit-audit-cobaye-ile1.md`

## D32 — Audit parcours obligatoire avant tout test cobaye (20 juillet 2026)

**Décision** : aucun test cobaye n'est lancé sans un audit parcours
complet préalable (2 passes, fille + garçon, base fraîche, notation
binaire OK/CASSÉ). Critère de sortie : zéro CASSÉ.

**Justification** : un test cobaye est une ressource non répétable
(première impression unique). Un bug de câblage consomme le test et
détruit le signal produit recherché.

**Ajout au protocole d'audit** : test de résistance maïeutique en
4 tentatives de contournement à chaque modification des prompts
d'Archimède. Un seul craquage est bloquant.

## D33 — Paramètre --cref pour les planches BD (20 juillet 2026)

**Décision** : `--cref` sur C1_part1 du genre concerné (C1_part1_fille
pour les planches fille, C1_part1_garcon pour les planches garçon),
`--cw 80`, sur toutes les planches C2 à C5.

**Justification** : sur un pipeline de 8 planches, la description
texte seule dérive (proportions du visage, teinte des cheveux, forme
des lunettes). --cw 80 tient le personnage sans figer la composition
de scène.

*(Décision finalisée le 20 juillet 2026 — remplace le brouillon
« EN ATTENTE ARBITRAGE » de la même journée, arbitrage rendu.)*

## D34 — ANNULÉE (20 juillet 2026)

**Statut** : révoquée le jour même, jamais appliquée en production.

**Contenu erroné** : correction du brief C2 vers « 12 amphores, 5
groupes de 2 + 2 à part » (division euclidienne 12 ÷ 5). Résolvait le
« BLOQUANT OUVERT — Erreur mathématique brief C2 » du même jour (choix
entre 12 amphores/reste 2 et 11 amphores/reste 1), mais sur une
mauvaise base : ce bloquant lui-même partait d'un brief périmé.

**Motif d'annulation** : le concept de C2 est « fraction d'une
quantité » (1/3 de 12 = 4, Cristal de la Juste Part), défini dans
`SESSION_2` de `pedagogie/contenu_ile1.py`. La division euclidienne
n'apparaît nulle part dans l'Île 1. D34 corrigeait l'arithmétique
d'un brief narratif périmé du 1er juillet sans le confronter au code
validé.

**Détectée par** : la conversation de production graphique, qui a
refusé de générer les prompts.

## D35 — Hiérarchie des sources de vérité (20 juillet 2026)

**Décision** : pour toute production dérivée du contenu pédagogique
(planches BD, prompts Midjourney, cinématiques, textes narratifs),
l'ordre de priorité est :
1. Le code validé (`pedagogie/contenu_ileN.py`) — source de vérité absolue
2. Les documents `.claude/` à jour (master-context, decisions)
3. Les briefs historiques — indicatifs, jamais opposables
4. La mémoire de conversation — jamais une source

**Règle opérationnelle** : tout brief graphique cite le concept, le
nom du cristal et l'exercice canonique tels qu'ils figurent DANS LE
CODE. Un brief qui ne peut pas citer sa ligne de code n'est pas un
brief.

**Origine** : incident D34 (20 juillet), rattrapé avant production.

**Rappel lié** : `.claude/pedagogie/ile-1-nombres-brises-CONTENU.md`
porte toujours 27 occurrences d'objets hors-univers non corrigées
depuis l'audit du 28 juin. Même pathologie. À requalifier ou
supprimer.

## D36 — Périmètre des mécaniques de jeu pour le format court (20 juillet 2026)

**Contexte** : l'audit de ile-1-nombres-brises-CONTENU.md a révélé que
plusieurs mécaniques y sont spécifiées mais codées nulle part (grep vide
sur tout le repo) : Résurgences, Zones de Profondeur, Rite d'Élévation
(4 Sceaux), Récompenses d'île, Paliers d'élévation. Ces mécaniques ont
été conçues pour le format été (7 semaines, 7 îles).

**Décision** :
- DANS le périmètre MVP Révision 10-15j : le Rite d'Élévation en version
  MINIMALE — un écran de clôture d'île, pas les 4 Sceaux complets. Il
  ferme le parcours de chaque île (déjà prévu S2, « ouverture du Rite
  compressé »).
- HORS périmètre, reporté : Résurgences, Zones de Profondeur, Paliers
  d'élévation, les 4 Sceaux du Rite complet. Pas de place sur 10 jours /
  3 îles, aucune n'est codée, les intégrer ferait rater le 15 août.

**Justification** : ces mécaniques supposent la durée et le nombre d'îles
du format été pour prendre sens. Sur le format court, elles seraient
tassées et coûteuses. Règle D7 reconduite : on réduit le périmètre, jamais
la date.

**Renvoi 2027** : elles restent spécifiées dans CONTENU.md (§4-§8) comme
référence vivante pour le chantier été, voir branche-2027-cahier-ete.md.
