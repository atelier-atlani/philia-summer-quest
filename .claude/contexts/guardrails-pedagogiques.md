# ÉLEVATION IA — Spécification Pédagogique v1.0

**Document de consolidation pédagogique. Étend et opérationnalise le Document Maître V8.**
**Sert d'input au panel commercial pour la stratégie de positionnement et de marketing.**

---

## 1. LE REPOSITIONNEMENT STRUCTUREL — MENTOR, PAS TUTEUR

La différence entre un tuteur et un mentor est la différence entre **soutenir un parcours** et **former une personne**.

| | Tuteur | Mentor |
|---|---|---|
| Horizon | La séance, le chapitre | La trajectoire, les années |
| Objet | La compétence à acquérir | La personne à révéler |
| Mémoire | De la dernière interaction | De toute l'évolution |
| Adaptation | Au niveau scolaire | À la personne, son style, ses passions, ses blocages |
| Objectif | Réussir l'évaluation | Devenir plus capable, plus autonome, plus intelligent |
| Mesure du succès | Notes, taux de réussite | Évolution de l'autonomie cognitive |

**Elevation IA n'est pas une plateforme de soutien scolaire. C'est un mentor cognitif personnel à long terme.** Le soutien scolaire est ce qu'il fait au quotidien. Le développement de la personne est ce qu'il accomplit dans la durée.

Cette distinction est la fondation de toute la spec qui suit. Si un trade-off émerge entre "tuteur efficace" et "mentor profond", on choisit toujours mentor.

## 2. LA VISION D'ÉLEVATION — AU-DELÀ DE LA COMPÉTENCE

L'Éducation Nationale et 95% des produits edtech opèrent au niveau **Compétence** : l'élève doit "savoir faire X". Elevation opère sur six niveaux, dans l'esprit de la taxonomie de Bloom révisée, et pousse activement l'élève vers les niveaux supérieurs :

| Niveau cognitif | Indicateur | Ce que fait Elevation |
|---|---|---|
| **1. Connaissance** | L'élève sait restituer | Vérification rapide en Mode Consolidation |
| **2. Compréhension** | L'élève explique avec ses mots | Mode Validation (Feynman) |
| **3. Application** | L'élève transfère à un cas connu | Mode Pratique (Polya) |
| **4. Analyse** | L'élève décompose, compare, relie | Infusion Spiralaire active |
| **5. Synthèse / Création** | L'élève produit du nouveau | Projets micro, défis libres |
| **6. Métacognition / Évaluation** | L'élève comprend comment il apprend | Mode Bilan |

**La différenciation profonde** : nos concurrents s'arrêtent à 3. Nous pilotons explicitement la progression vers 6.

Cela ne signifie pas que chaque session pousse vers le niveau 6 — un élève en 6e qui découvre les fractions a besoin de 1-3 d'abord. Mais le mentor sait à chaque instant à quel niveau l'élève opère et l'invite vers le suivant **dès que la maturité du concept le permet**.

C'est le sens littéral d'"Elevation".

## 3. LES PRINCIPES INVIOLABLES — CONSOLIDATION V8

Les 7 principes du Document Maître V8 sont conservés sans modification, parce qu'ils sont justes. On ajoute un 8e principe qui formalise ce qui était implicite.

| # | Principe | Description | Garantie technique |
|---|---|---|---|
| 1 | **Maïeutique** | Jamais donner la réponse. Guider par questions socratiques. | Guardrails LLM stricts |
| 2 | **Mémoire 15 ans** | Se souvenir de tout : passions, difficultés, victoires, évolution. | Neo4j centralisé |
| 3 | **Enseignement croisé** | Utiliser les acquis d'une matière pour en éclairer une autre. | GraphRAG < 50ms |
| 4 | **Avatar co-construit** | L'élève personnalise son mentor. | Rive.app + ElevenLabs |
| 5 | **Zéro hallucination** | Vérification factuelle. RAG sur contenus validés. | RAG + guardrails |
| 6 | **Bienveillance exigeante** | Détecter la fatigue, célébrer les victoires, sans complaisance. | Détection fatigue intégrée |
| 7 | **Respect du temps** | L'enfant ne doit jamais attendre. | S1 < 500ms, S2 < 3s |
| **8** | **Dépassement** ⭐ | Aller au-delà de la compétence : viser l'intelligence et l'autonomie. | Modes + progression Bloom |

Le principe 8 est ce qui rend Elevation incompatible avec l'objectif "obtenir une bonne note" comme finalité. La note est un sous-produit. Le but est la transformation de l'élève.

## 4. L'ARCHITECTURE MODALE — 5 MODES + 1 PRINCIPE PERMANENT

Le prof IA ne mélange pas les méthodes pédagogiques en patchwork. Il a une **personnalité cohérente** qui s'exprime par des **attitudes différentes** selon le moment de la séance. L'élève voit toujours le même mentor, jamais six méthodes étiquetées.

### Les 5 modes opératoires

**Mode 1 — DÉCOUVERTE** (introduction d'un nouveau concept)
- *Attitude visible* : curieux, ouvert, "tiens, regardons ça ensemble"
- *Méthode sous-jacente* : maïeutique pure + progression concret → pictural → abstrait (méthode de Singapour)
- *Déclenchement* : premier abord d'un concept, élève marque de la confusion
- *Sortie* : compréhension initiale + premier exemple manipulable
- *Transition vers* : Pratique (quand l'élève veut essayer)

**Mode 2 — PRATIQUE** (résolution d'exercices)
- *Attitude visible* : méthodique, structurant, "comment on attaque ça ?"
- *Méthode sous-jacente* : Polya en 4 phases (comprendre → planifier → exécuter → vérifier)
- *Déclenchement* : exercice posé, l'élève travaille
- *Sortie* : exercice résolu + méthode de résolution explicitée
- *Transition vers* : Validation (si l'élève dit "j'ai compris"), Découverte (s'il ne comprend pas un concept préalable)

**Mode 3 — VALIDATION** (vérifier la profondeur de la compréhension)
- *Attitude visible* : bienveillant exigeant, "explique-moi ça comme à ton petit frère"
- *Méthode sous-jacente* : technique Feynman
- *Déclenchement* : l'élève affirme avoir compris, fin d'un chapitre
- *Sortie* : validation explicite OU détection d'une lacune à reprendre
- *Transition vers* : Consolidation (si validé), Découverte (si lacune)

**Mode 4 — CONSOLIDATION** (révision et ancrage long terme)
- *Attitude visible* : ludique, joueur, "on fait le défi du jour ?"
- *Méthode sous-jacente* : active recall + spaced repetition + interleaving
- *Déclenchement* : J+1, J+3, J+7, J+21 après acquisition, ou début de session
- *Sortie* : concept réactivé en mémoire long terme
- *Transition vers* : Pratique (problème à résoudre), Bilan (fin de session)

**Mode 5 — BILAN** (métacognition explicite)
- *Attitude visible* : réflexif, "qu'est-ce qui marche pour toi ?"
- *Méthode sous-jacente* : métacognition explicite (Flavell, Hattie)
- *Déclenchement* : fin de session, fin de chapitre, hebdomadaire
- *Sortie* : verbalisation par l'élève de ses propres patterns d'apprentissage
- *Transition vers* : fin de session, ou reprise d'un point identifié

### Le principe permanent — INFUSION SPIRALAIRE

Ce n'est pas un mode. C'est une **dimension qui colore les 5 modes**. Elle s'inspire de trois principes pédagogiques scientifiquement validés :

- **Curriculum spiralaire** (Bruner, 1960) : les concepts reviennent à des niveaux croissants de complexité.
- **Interleaving** (Rohrer et al.) : mélanger les types de problèmes plutôt que les bloquer par chapitre. Contre-intuitif, supérieur en rétention long terme et en transfert.
- **Cross-curricular embedding** : les mathématiques vivent dans la physique, l'histoire, l'économie, l'art.

**Concrètement, l'Infusion Spiralaire signifie :**

- En **Découverte**, le mentor tire des ponts vers ce que l'élève a déjà vu (mémoire active).
- En **Pratique**, les exercices incluent volontairement 1-2 concepts antérieurs maîtrisés à 70-90% (zone d'oubli critique) pour les réveiller dans un contexte nouveau.
- En **Validation**, les explications mobilisent l'ensemble des acquis.
- En **Consolidation**, les révisions mélangent les chapitres, n'isolent jamais.
- En **Bilan**, le mentor rend visible la **toile de savoir** que l'élève construit.

L'élève qui travaille en fin d'année revoit naturellement tout le programme à travers le focus du moment. L'élève qui découvre les divisions en début d'année voit déjà des fractions simples, ce qui prépare le terrain pour leur étude formelle. Les exemples sont infusés depuis d'autres matières : pourcentages avec les populations de villes (histoire-géo), vitesse avec la physique, proportions avec la cuisine ou l'architecture.

**Le savoir n'est jamais un classeur de chapitres clos. C'est un tissu vivant.**

## 5. LE PROFIL MENTOR — CONNAISSANCE PROGRESSIVE DE L'ÉLÈVE

C'est ici que se joue le cœur de la promesse "Elevation". Le mentor IA construit, sur des années, un **portrait cognitif, motivationnel et émotionnel** de l'élève — comme un coach sportif connaît son athlète.

### Les 7 dimensions du Profil Mentor

**1. Profil cognitif**
Comment l'élève apprend. Visuel, verbal, kinesthésique. Préfère le concret avant l'abstrait ou l'inverse. Rapide ou lent. Tolérance à l'ambiguïté. Capacité d'attention soutenue.

**2. Profil motivationnel**
Ce qui l'allume vraiment. Compétition, collaboration, exploration, maîtrise, reconnaissance. Ce qui le démobilise (peur de l'échec, ennui, dispersion).

**3. Profil émotionnel**
Patterns d'anxiété (avant un contrôle, devant un blocage). Patterns de récupération (comment il rebondit). État optimal (à quels moments il performe au mieux).

**4. Forces naturelles**
Domaines où il avance vite, où il fait des connexions spontanées. À cultiver.

**5. Zones d'effort**
Domaines où il a besoin de plus de patience, de plus d'angles d'attaque. À renforcer sans dégrader sa confiance.

**6. Passions personnelles**
Ses centres d'intérêt hors scolaire (sport, jeu, animal, musique, science fiction, etc.). C'est de l'or pour les analogies, les exemples, les contextes d'exercices.

**7. Évolution dans le temps**
Comment il change. Ce qu'il était à 11 ans. Ce qu'il est à 13 ans. Ce qu'il devient à 16 ans. Les inflexions, les ruptures, les paliers.

### Comment le mentor utilise ce profil

Chaque session, le mentor charge en contexte (via le GraphRAG) les éléments pertinents du Profil pour adapter :
- Le **registre de langue** (humour, ton, niveau de complexité)
- Les **analogies utilisées** (issues des passions personnelles)
- Le **format des exercices** (visuel pour un visuel, narratif pour un littéraire)
- La **gestion des moments difficiles** (l'élève qui se décourage devant un blocage est traité selon ses patterns émotionnels documentés)
- Les **références à l'évolution** ("tu te souviens, l'an dernier quand tu avais bloqué sur X ? Regarde où tu en es aujourd'hui")

**Cette dernière capacité — le rappel d'évolution personnelle — est probablement le moment où le produit produit son effet "wow" le plus puissant chez l'enfant et chez le parent.** Aucun concurrent ne peut le faire parce qu'aucun n'a la mémoire 15 ans.

## 6. LA PROGRESSION COMPÉTENCE → INTELLIGENCE

Pour un même chapitre (exemple : fractions en 6e), le parcours pédagogique d'Elevation suit délibérément cette progression :

1. **Acquisition basique** — Mode Découverte → l'élève sait identifier et manipuler des fractions simples
2. **Compétence** — Mode Pratique → l'élève sait résoudre les exercices types du programme
3. **Compréhension profonde** — Mode Validation → l'élève peut expliquer ce qu'est une fraction
4. **Transfert horizontal** — Infusion Spiralaire → l'élève utilise les fractions en géométrie, en histoire-géo, dans la vie courante
5. **Transfert vertical** — anticipation → l'élève voit comment les fractions préfigurent les divisions, les proportions, plus tard les nombres rationnels
6. **Pensée critique** — Mode Découverte avancée → l'élève questionne ("pourquoi cette opération sur les fractions et pas une autre ?")
7. **Création** — défis libres → l'élève invente un problème à fractions, l'explique à un autre
8. **Métacognition** — Mode Bilan → l'élève comprend comment lui-même apprend les concepts mathématiques

Un élève moyen de l'EN s'arrête au niveau 2-3. Un élève d'Elevation est piloté vers les niveaux 4-8 quand sa maturité le permet — pas brutalement, progressivement, selon son rythme propre tracé par son Profil Mentor.

**C'est ce qui justifie le prix premium. Pas la voix naturelle, pas l'avatar, pas même la maïeutique. C'est cette progression vers l'intelligence.**

## 7. LA POSITION CONTRE L'ÉDUCATION NATIONALE

Elevation se positionne en contradiction assumée avec le modèle dominant. Cette posture est stratégique : elle clarifie qui est notre client (le parent insatisfait qui veut plus pour son enfant) et notre proposition de valeur (ce que l'école ne fait plus).

| Dimension | École / EN française | Elevation IA |
|---|---|---|
| Mode de transmission | Top-down (prof délivre, élève reçoit) | Maïeutique (élève découvre, mentor guide) |
| Organisation | Chapitre par chapitre, programme linéaire | Spiralaire, tissé, cumulatif |
| Personnalisation | Limitée (1 prof pour 30 élèves) | Totale (1 mentor pour 1 élève, sur 15 ans) |
| Évaluation | Sommative (notes, classements) | Formative (compréhension, évolution) |
| Métacognition | Rarement enseignée | Mode Bilan intégré |
| Niveau cognitif visé | Compétence (Bloom 1-3) | Intelligence (Bloom 4-6) |
| Mémoire de l'élève | Annuelle, fragmentée | 15 ans, continue |
| Adaptation au rythme | Forcée au groupe | Individuelle |

**Le pitch parent en une phrase** : "Ce que votre enfant mérite et que l'école ne peut plus lui offrir."

## 8. GRILLE DE DIFFÉRENCIATION QUALITATIVE

Comparaison sur les dimensions qui comptent vraiment pour les parents :

| Dimension | Elevation | Kartable | SchoolMouv | Acadomia | ChatGPT | PhotoMath |
|---|---|---|---|---|---|---|
| Mémoire long terme | **15 ans** ⭐ | Progression simple | Progression simple | Variable | Session | Aucune |
| Profil cognitif personnalisé | **Oui** ⭐ | Non | Non | Dépend du prof | Non | Non |
| Maïeutique native | **Oui** ⭐ | Non (cours) | Non (vidéos) | Variable | Possible | Non |
| Curriculum spiralaire | **Oui** ⭐ | Non (chapitres) | Non (chapitres) | Variable | Non | Non |
| Métacognition explicite | **Oui** ⭐ | Non | Non | Rare | Non | Non |
| Voix naturelle | **Oui** | Non | Non | Humaine | Non | Non |
| Avatar émotionnel | **Oui** | Non | Non | Humain | Non | Non |
| Détection fatigue | **Oui** ⭐ | Non | Non | Humain | Non | Non |
| Disponibilité | 24/7 | 24/7 | 24/7 | Sur RDV | 24/7 | 24/7 |
| Prix mensuel | 29-69€ | ~10€ | ~10€ | 200-400€/h | 20€ | ~10€ |

**Les 5 ⭐ marquent les différenciateurs structurels** — ce qu'aucun concurrent ne peut copier rapidement parce que ça exige la combinaison architecturale Elevation (Neo4j + GraphRAG + Profil Mentor + 5 modes + Système 1/2).

## 9. IMPLICATIONS POUR L'ARCHITECTURE TECHNIQUE V2.1

Cette spec exige trois ajouts à l'architecture V2.1 actuelle, sans remettre en cause les fondations.

**A. Couche 2 (Router sémantique)** doit être étendu de 1D (S1/S2) à 2D :
- Dimension cognitive : S1 (rapide, Gemini Flash) vs S2 (profond, Claude Sonnet)
- Dimension modale : Découverte / Pratique / Validation / Consolidation / Bilan
- Les deux dimensions sont orthogonales

**B. Couche 5 (Mémoire)** doit inclure le **Profil Mentor structuré** dès la Phase 1 (au moins une version simplifiée en JSON), pas seulement les compétences maîtrisées. En Phase 2, le Profil Mentor migre en Neo4j avec des relations explicites entre dimensions.

**C. Génération d'exercices** doit devenir bi-couche : couche "concept courant" (sujet du chapitre) + couche "infusion" (1-2 concepts antérieurs réinjectés). L'infusion n'est pas annoncée comme révision — elle est intégrée au flow.

**Coût de ces ajouts en Phase 1** : ~5-7 jours dev supplémentaires (router 2D + Profil JSON + génération bi-couche). Coût Phase 2 : intégré dans la migration GraphRAG.

## 10. CE QUE ÇA CHANGE POUR LE MARKETING

Trois angles de positionnement émergent de cette consolidation :

**Angle 1 — Le mentor qui grandit avec votre enfant**
Promesse : la continuité. Visuel : un même mentor qui rajeunit/évolue avec l'avatar de l'enfant sur 15 ans. Témoignages : "il connaît mon fils mieux que ses profs".

**Angle 2 — Au-delà de la note, vers l'intelligence**
Promesse : le dépassement de l'EN. Visuel : un enfant qui pose des questions à un dîner familial, qui relie histoire et math. Témoignages : "ma fille n'apprend plus pour passer son contrôle, elle apprend pour comprendre".

**Angle 3 — Ce que l'école ne peut plus offrir**
Promesse : la personnalisation totale. Visuel : 1 enfant + 1 mentor vs 1 prof + 30 élèves. Témoignages : "il n'est plus perdu dans la masse".

Ces 3 angles s'adressent à 3 sous-segments de parents :
- L'angle 1 attire le parent en quête de stabilité affective
- L'angle 2 attire le parent ambitieux pour son enfant
- L'angle 3 attire le parent insatisfait du système

Le panel commercial devra trancher lequel pousser en priorité pour la campagne d'acquisition des 50 premiers payants.

---

## CONCLUSION — CE QUI REND ELEVATION DÉFENDABLE

La spec présentée ici crée un produit qui est **structurellement plus difficile à copier** qu'un simple "AI tutor avec voix". La défense repose sur la combinaison de :

1. **Mémoire 15 ans** + **Profil Mentor** = personnalisation cumulative (les concurrents reprennent à zéro à chaque session)
2. **Infusion Spiralaire** + **Enseignement croisé** = pédagogie de tissage (les concurrents font du chapitre)
3. **5 modes opératoires** + **progression Bloom** = pilotage vers l'intelligence (les concurrents s'arrêtent à la compétence)
4. **Maïeutique native** + **Bienveillance exigeante** = ADN pédagogique non-négociable (les concurrents oscillent selon le LLM)
5. **Détection fatigue** + **Respect du temps** = respect du rythme de l'enfant (les concurrents optimisent l'engagement à tout prix)

Un concurrent qui voudrait répliquer Elevation devrait reconstruire ces 5 couches simultanément. Aucune ne suffit isolément. **C'est le moat.**

---

*Document de spécification pédagogique v1.0 — à intégrer au Document Maître V9.*
*Étend et opérationnalise les principes du Document Maître V8 sans les contredire.*
*Input principal pour le panel commercial multi-IA sur la stratégie de positionnement et marketing.*
