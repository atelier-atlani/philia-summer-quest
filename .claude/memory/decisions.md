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

## D37 — Réalignement §3 de ile-1-nombres-brises-CONTENU.md (20 juillet 2026)

**Décision** : le §3 (les 5 sessions) de
.claude/pedagogie/ile-1-nombres-brises-CONTENU.md est réaligné par copie
exacte des énoncés/indices déjà validés dans pedagogie/contenu_ile1.py.
Un en-tête de hiérarchie par section est ajouté : §3 → le code fait foi ;
§1-2 et §4-§11 → ce document fait foi tant qu'aucun code équivalent n'existe.

**Raison** : le document portait ~40 occurrences d'objets hors-univers
(tarte, fruits, pizza, gâteau, chocolat) absentes du code, et se présentait
comme source de vérité. Mais §1-2 et §4-§11 sont la seule spec existante de
mécaniques non codées — le document ne pouvait donc être ni intégralement
récupéré ni intégralement archivé. Réalignement scopé au seul §3 périmé.
Fichier conservé dans .claude/pedagogie/, pas déplacé. Ref D35.

## D38 — Mode MOCK_LLM pour tests UI hors API (20 juillet 2026)

**Décision** : core/llm_client.py accepte la variable d'environnement
MOCK_LLM=1 qui court-circuite l'appel à l'API Anthropic et retourne 3
questions maïeutiques factices en rotation, sans appel réseau. Comportement
inchangé sans la variable. Commit e7221e9.

**Raison** : chaque tour de dialogue consommait l'API ; le crédit épuisé
bloquait l'audit parcours. Le mock sépare le test du parcours (UI, gratuit,
reproductible) du test du mentor (LLM réel, payant, à faire au Workbench).
Garde-fou préservé : le mock ne renvoie jamais la solution de l'exercice.

## D39 — Structure des planches BD par cristal, Île 1 (20 juillet 2026)

**Décision** : le nombre de parts d'une planche BD suit la narration du
cristal, pas une règle d'uniformité.
- C1 : 2 parts (c1 + c1_part2)
- C2 : 2 parts (c2_part1 + c2_part2)
- C3 : 1 part (c3) — planche 3-panels autosuffisante
- C4 : 2 parts (c4_part1 + c4_part2)
- C5 : 2 parts (c5_part1 + c5_part2)

**Raison** : proposition d'uniformiser tous les cristaux en 2 parts
rejetée. L'asymétrie du mapping _SEQUENCE_PLANCHES ne coûte rien à
l'usage ; passer C3 en 2 parts aurait exigé une production graphique
supplémentaire et dilué le beat eurêka pour un seul bénéfice de lisibilité
du code. Un changement de planche se justifie par la narration, jamais par
le confort de mapping. Seul motif qui rouvrirait la question : illisibilité
avérée de la C3 3-panels (non constatée à ce jour).

**Bug corrigé au passage** : le mapping portait C2/C4/C5 en une seule part
alors que les fichiers part1/part2 étaient livrés — les 3 cristaux tombaient
silencieusement sur le placeholder. Corrigé dans le même commit.

**Historique** : aucune décision antérieure ne logue la structure des
planches C3 ; le code portait ["c3"] sans justification écrite. D39 est la
première trace formelle. (La conversation de production graphique référençait
une « D31 » à tort — D31 est le protocole de test cobaye.)

## D40 — Navigation onboarding : lever la confusion archipel/carte (2 août 2026)

**Décision** : l'écran presentation_archipel est conservé (option b), mais
les deux boutons successifs autrefois libellés identiquement « Découvrir
l'archipel » reçoivent des libellés distincts décrivant leur destination
réelle :
- ecran_avatar.py → « Embarquer pour l'aventure » (mène à presentation_archipel)
- ecran_presentation_archipel.py → « Ouvrir la carte de l'archipel » (mène à carte)

Le passage carte → île reste inchangé : clic sur ancres HTML superposées
à la carte (pas de bouton), le nom de l'île s'affiche au survol via {nom}
interpolé depuis le YAML. Aucun libellé codé en dur (éviterait d'afficher
« Île des Nombres Brisés » au survol des îles 2-3).

**Raison** : confusion signalée à l'audit du 2 août — deux boutons au même
nom, la même image d'archipel deux fois, la cible (l'Île 1) absente des
libellés. Machine à états ecran_courant/etape_ile non touchée : correctif
purement cosmétique.

## D41 — Identité visuelle de la Clé du Partage + refonte célébration forte (3 août 2026)

**Contexte** : audit du 2-3 août. Les clés de progression n'avaient aucune
existence graphique (emoji 🗝 unicode, rendu variable selon l'OS, peu visible
sur la carte). La célébration forte de fin d'île reposait sur st.balloons(),
jugée pauvre pour le climax du parcours.

**Décisions** :
1. Création d'un asset unique et générique, cle_partage.png (assets/ui/,
   PNG fond transparent 1024×1024, style watercolor Syracuse, anneau à motif
   de partage). La MÊME clé sert les 3 îles du MVP — le nom change en texte
   (« Clé du Partage », « Clé de la Mesure »...), l'image reste identique.
   Déclinaison par île reportée post-MVP.
2. Intégration à trois emplacements, tailles et halos différenciés :
   carte (~68px), porte-clés sidebar (~30px), modal de fin d'île (~200px).
3. st.balloons() supprimé du projet (célébration forte comme légère). La
   célébration forte est désormais portée par la clé en grand + halo doré
   dans le modal, devant le message d'Archimède.

**Raison** : la clé est le symbole central de progression ; un emoji système
ne pouvait pas le porter. Un asset unique donne le meilleur rapport
valeur/effort — une production, trois usages — sans tripler la charge
graphique à trois semaines de la livraison.

**Choix technique** : _CLE_IMAGE_PATH et le helper _img_b64 dupliqués dans
celebrations.py plutôt qu'importés de ecran_carte, pour ne pas inverser le
sens des dépendances (celebrations est un utilitaire transverse). Refactor
ui/_assets.py partagé identifié comme sortie propre, reporté.

**Backlog associé** : GIF animé de célébration NON retenu pour le MVP — le
modal statique avec clé suffit au climax (validé à l'audit). À rouvrir
seulement si le test cobaye juge la fin d'île fade.

## D42 — MVP resserré à une seule île (3 août 2026)

**Décision** : le MVP du 15 août 2026 est resserré à l'Île 1 seule
(L'Île des Nombres Brisés, fractions). Les Îles 2 et 3 sortent du
périmètre de livraison — reportées post-lancement.

**Raison** : au 3 août, l'Île 2 n'est pas commencée ; la session du jour
a été consacrée à la finition de l'Île 1 (navigation, Clé du Partage,
célébration). Livrer une Île 1 impeccable et narrativement complète vaut
mieux que trois îles bâclées. Application directe de D7 : on réduit le
périmètre, jamais la date.

**Conséquence narrative (à produire)** : l'énigme finale du secret
d'Archimède (D17), prévue après l'Île 3, doit remonter en clôture de
l'Île 1 pour que l'arc narratif se referme. Une île unique doit être une
aventure complète, pas un tiers de produit interrompu. C'est le chantier
« potentialisation storytelling » de fin d'Île 1.

**Pricing — DÉCISION OUVERTE, NON TRANCHÉE CE JOUR** : le prix de 19€
(D30) portait sur 3 îles. Il doit être révisé pour une île unique. Le
Décideur envisage une tarification « par île ». Note Architect : sur un
MVP à une seule île, « par île » se réduit à « un prix pour une île » ;
le modèle de tarification par île n'a d'objet qu'en 2027 avec le format
multi-îles. Repères : ne pas diviser 19€/3 (valeur perçue, pas prorata) ;
« limite de rentabilité » unitaire non pertinente (coût marginal quasi
nul). Prix provisoire à geler avant lancement. Débat modèle tarifaire
renvoyé post-cobaye / panel commercial.

## D43 — Énigme finale de clôture, Île 1 : le secret de la couronne (3 août 2026)

**Décision** : l'Île 1 se referme sur une énigme-enquête maïeutique
(couronne d'Hiéron), jouée après la Clé du Partage. L'enfant y découvre
que ses connaissances des fractions lui donnent une pièce de la solution
(la couronne truquée = un mélange exprimable en fraction, part d'or / part
d'argent). Le secret complet (mesurer la part cachée = densité, eau
déplacée) lui est révélé en don narratif au dernier temps, et la partie
« comment mesurer » reste ouverte vers la suite du voyage.

**Forme** : dialogue maïeutique libre en 4 temps, sans exercice YAML.
Archimède ne donne jamais le lien fraction (temps 2 maïeutique) ; le secret
densité n'est lâché qu'au temps 4. Interpolation {prenom}/{accord}.

**Objet gagné** : le Parchemin d'Archimède (asset Midjourney unique) —
couronne dessinée, fraction lisible, zone « comment mesurer » effacée.
Matérialise la découverte partielle + la promesse de suite. PAS de « bon »
codé (abandonné, trop d'engagement technique sur un Elevation IA non
construit) — la relance commerciale passe par email parent avec consentement
RGPD (voir D44).

**Repli deadline** : si le dialogue libre + state machine ne tient pas dans
les 12 jours, dégradation en planche BD 4 cases avec 1 choix au temps 2.
Décision de bascule au plus tard le 8 août.

**Brique réutilisable** : ce dialogue libre est le prototype du « dialogue
libre guidé » d'Elevation IA. Conception détaillée :
.claude/production/enigme-finale-ile1.md

## D44 — Consentement email parent, RGPD (3 août 2026)

**Décision** : la relance Summer Quest → Elevation IA passe par email parent.
Collecte soumise à consentement explicite du parent au moment de l'achat :
case distincte de l'achat, non pré-cochée, finalité mentionnée, désinscription
possible. Requis dès le MVP — ne pas construire de base email sans ce
consentement.

**Raison** : produit destiné à mineurs, prospection = RGPD. Le master context
listait la conformité RGPD mineurs comme risque non traité ; D44 le traite
a minima pour la fonction email.

## D45 — Énigme finale : implémentation et rejouabilité (4 août 2026)

**Complète D43 (conception).** L'énigme de la couronne est implémentée et
validée en conditions réelles.

**Architecture retenue** : moteur dédié pedagogie/enigme_engine.py, isolé de
session_engine (qui est adossé aux exercices). Réutilise l'appel LLM et l'ADN
d'Archimède (_PERSONA/_GUARDRAILS dupliqués, pas importés, pour ne pas coupler
le moteur à la tuyauterie des sessions). Prompt script :
prompts/mentor/enigme_couronne.txt. Écran : ui/ecran_enigme.py.
Déclenchement : bouton dans le modal de fin d'Île 1 (conditionné à
ile_courante == "ile_1").

**Progression** : le LLM signale la fin d'un temps via marqueur [[TEMPS_SUIVANT]]
/ [[ENIGME_FIN]], retiré avant affichage. Garde-fou de tours
(PLAFOND_TOURS_PAR_TEMPS=4) force l'avancée si le marqueur n'arrive pas —
garantit que l'énigme atteint toujours sa fin (vérifié : terminée au tour 15
en MOCK, sans aucun marqueur).

**Règle de robustesse** : un [[ENIGME_FIN]] émis prématurément (avant le temps 4)
vaut simple avancée d'un cran, pas fin. C'est le moteur qui garantit que le
secret n'arrive jamais avant les temps 1-3, pas la discipline du LLM (principe
ADN : la state machine impose la séquence, le prompt seul n'y suffit pas).

**Rejouabilité — dette assumée MVP** : enigme_active persiste en session_state.
Revenir sur l'écran ré-affiche le dialogue vécu + parchemin, sans rejouer.
Mais fermer l'onglet perd cet état → l'enfant peut rejouer. Pas de persistance
en base (« énigme faite ») : hors spec, cas marginal, raffinement reporté
post-cobaye. Rejouer l'énigme n'est pas un dégât (histoire, pas exercice noté).

**Parchemin** : asset assets/ui/parchemin_archimede.png à produire (Midjourney).
Placeholder gracieux en attendant, pas de crash si absent.

## D46 — Carte-fragment comme récompense d'énigme, graine d'un futur système de cartes mémoire (4 août 2026)

**Décision** : la récompense de l'énigme finale d'Île 1 (remplace le
parchemin, jugé trop passif) est une CARTE À COLLECTIONNER de type carte
de jeu — belle, précieuse, avec nom, rareté, île, Clé du Partage, marque
de collection 1/7, et la notion-clé de l'île (« une fraction = une part
d'un tout »).

**Portée MVP** : la carte est un TROPHÉE de collection uniquement. Aucune
mécanique de jeu (pas de combat, points, deck, révision espacée) dans le
MVP. Elle ne fait qu'être gagnée et gardée.

**Graine assumée** : la carte est conçue compatible avec un FUTUR système
de jeu basé sur des cartes mémoire / cartes mentales (projet séparé, hors
MVP, non planifié). En portant dès le MVP la notion-clé de l'île, la carte
est déjà une « carte mémo » — le système futur la réutilisera sans qu'elle
soit refaite. Aucune mécanique de ce système n'est construite maintenant.

**Garde-fou** : le système de cartes mémoire NE doit PAS être conçu ni codé
avant le 15 août. La carte MVP en est la première brique, pas le système.

**Production** : illustration (couronne héroïque + fraction visuelle) par
Midjourney ; cadre + attributs texte par gabarit HTML/CSS (réutilisable
pour les 7 futures cartes) — Midjourney ne rend pas le texte proprement.

## D47 — Vision tableau de bord et enrichissement du parcours — POST-MVP (4 août 2026)

**Décision** : les enrichissements de parcours listés ci-dessous sont
capturés comme vision produit mais EXCLUS du MVP du 15 août. À construire
post-lancement, priorisés avec le retour du test cobaye.

**Idées capturées (audit Décideur du 4 août)** :
- Tableau de bord permanent : où j'en suis dans l'aventure (île courante,
  session courante), mes cristaux, une carte actuelle consultable, ma carte-
  fragment collectionnée
- Décompte de gains par exercice (pierres, amphores selon le décor) avec
  mini-célébration sonore/visuelle (« ding »)
- Célébration de fin de session cumulant les gains de la session
- Mini-carte de l'île avec émoticône du personnage qui progresse sur les
  sessions
- Dézoom des planches BD pour voir l'image entière + le décor de tableau de
  bord autour
- Texte narratif sur les planches BD (bandeau parchemin ou bulle) pour porter
  le récit
- Amélioration de la lisibilité des énoncés à double question (ex. exercice
  6 session 2 : « combien utilisées / combien reste-t-il »)

**Garde-fou** : aucun de ces éléments n'est construit avant le 15 août. Le MVP
livre déjà cristaux, clé, carte-fragment, célébrations légère/forte, repère
N/total, clôture de session — suffisant pour tester le produit. Le tableau de
bord et ses satellites relèvent d'une itération produit ultérieure, distincte
aussi du futur système de cartes mémoire (D46).

**Lien** : certaines de ces idées (carte consultable, gains) convergeront avec
le système de cartes mémoire de D46 — à concevoir ensemble post-MVP.

## D48 — Système de collection + resynchronisation dialogue/moteur (5 août 2026)

**Contexte** : deux cobayes de 12 ans ont exprimé un désir de gamification
(voir sa progression, ses gains, sa collection). Réponse construite en
gardant le cap MVP une-île.

**Système de collection (rhabillage, pas nouveau stockage)** :
- Chaque exercice traversé (clic « Exercice suivant ») → +1 objet de la
  session.
- 1 type d'objet par session, Île 1 : S1 pierres, S2 amphores, S3 cristaux
  d'eau, S4 poids, S5 planches.
- Fin de session = coffre plein, nommé du concept de la session.
- Le coffre REMPLACE visuellement le cristal : gagner_cristal() /
  cristaux_obtenus() restent la source de vérité, on change l'habillage,
  pas le stockage. Aucune migration.
- Table de correspondance session→objet dans jeu/collection.py (réutilisable
  par île). Compteur dérivé de index_exercice (pas de champ persistant).

**Tableau de bord permanent (sidebar, tous écrans, déplié par défaut)** :
- OÙ JE SUIS (île, session, exercice), MA COLLECTION (compteur en session),
  MES COFFRES (X/5 nommés), PORTE-CLÉS, MA CARTE (fragment si gagné).
- Sidebar extraite de ecran_carte.py vers ui/tableau_bord.py (module
  partagé, pas de duplication). Répond au retour test réel : progression
  non visible, compteur perdu au scroll, coffres invisibles après la
  session.
- Icônes réduites 48px avant encodage base64 (assets sources ~2Mo → 4,4Ko).

**Fix majeur — resynchronisation dialogue/moteur** : Archimède débordait de
l'exercice courant (il enchaînait 6/6, 0/6, un autre exercice dans un seul
tour de dialogue), désynchronisant le dialogue et la state machine — le
moteur restait à l'exercice 1, le compteur à 0, les coffres ne se
déclenchaient pas. Cause : le prompt ne disait pas à Archimède de s'arrêter
à son exercice et de rendre la main au bouton. Corrigé par RÈGLE 9
(_shared_guardrails) + section clôture d'exercice (mode_decouverte) +
alignement mode_pratique. Archimède traite désormais UN exercice, le
valide, s'arrête, invite au bouton. La maïeutique À L'INTÉRIEUR de
l'exercice est préservée. Ce fix corrigeait aussi un débordement de contenu
non validé pédagogiquement (Archimède inventait des exercices hors YAML).

**Tests** : suite pérenne test_collection_compteur_coffre.py créée (38
vérifications) — comble un angle mort (le repo n'avait quasi aucun test
versionné). À maintenir verte sur les commits suivants.

**Rejouabilité carte-fragment** : non persistée (déduite de session_state),
disparaît au redémarrage. Dette assumée MVP, cas marginal.

## D49 — Prix de l'île unique fixé à 9,90 € (6 août 2026)

**Décision** : l'Île des Nombres Brisés (MVP une-île : 5 sessions +
énigme finale + carte-fragment) est vendue 9,90 €. Ferme le D42 (prix
laissé ouvert lors du resserrement à une île).

**Rationale** : prix d'appel sous la barre des 10 €, assumé comme produit
d'ACQUISITION et non de rentabilisation. L'île est la porte d'entrée du
funnel vers Elevation IA (39 €/mois) — elle se rentabilise sur la
conversion, pas sur la vente unitaire. Le « 19€÷3 » a été écarté (valeur
perçue, pas calcul mécanique).

## D50 — Périmètre de lancement PSQ : tunnel semi-manuel (6 août 2026)

**Contexte** : plan de lancement du 6 août (fenêtre 6-15 août). Prix fermé
en D49. Ce qui reste à trancher pour vendre : le tunnel d'achat et
l'hébergement.

**Décisions** :
- **Périmètre** : grand public, tunnel SEMI-MANUEL. Vente automatisée
  (Stripe), livraison du code automatisée par Stripe (option A : un code
  partagé, changé à la main si fuite). PAS de webhook ni système de
  comptes au MVP.
- **Persistance** : la reprise de partie est nécessaire → hébergement avec
  disque persistant (Render ou Railway), PAS Streamlit Community Cloud
  (pas de disque persistant, progression perdue à chaque redéploiement).
- **Contrôle d'accès** : un code partagé, vérifié contre une liste dans
  les secrets. Niveau de sécurité simple assumé pour ce lancement.
- **SIRET** : attendu sous 48h (~8 août). Débloque Stripe — bloquant pour
  la Brique 3 (Stripe), pas pour les Briques 1-2 (déploiement, contrôle
  d'accès).
- **Jeu** : Île 1 complète, jouable de bout en bout, onboarding bouclé.
  Considéré PRÊT — le chemin critique restant est mise en marché
  (déploiement, paiement, RGPD), pas contenu du jeu.

**Note Architect** : le texte source référence « D46-lancement » pour
justifier la simplicité du contrôle d'accès. D46 porte sur la carte-
fragment / le futur système de cartes mémoire, sans lien avec le contrôle
d'accès — probable erreur de référence à la frappe. Le principe lui-même
(simplicité assumée pour tenir la date, D7) n'est pas remis en cause,
seule la référence D46 semble erronée. Signalé plutôt que corrigé
silencieusement — à confirmer.

**Chemin critique et plan d'exécution** (Briques 1-6, ordre des jours,
garde-fous D7) : capturés séparément, voir note de suivi.
