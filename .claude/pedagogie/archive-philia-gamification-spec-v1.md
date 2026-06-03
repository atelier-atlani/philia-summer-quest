# PHILIA SUMMER QUEST — Spécification Gamification v1.0

**Document de design produit. Définit la structure de jeu et le découpage de livraison.**
**À intégrer au Plan Architecte comme spec fonctionnelle de la couche gamification.**

---

## PRINCIPE FONDATEUR

Philia Summer Quest a un ADN maïeutique : la réflexion lente, la question socratique, le raisonnement profond. La gamification ne doit JAMAIS trahir cet ADN. Elle l'enveloppe, le rend désirable, le rythme — mais elle ne le remplace pas.

Règle d'or : **le jeu sert la pédagogie, jamais l'inverse.** Si une mécanique de jeu pousse l'enfant à aller vite là où il devrait réfléchir, on la retire.

---

## LES 3 COUCHES DE GAMIFICATION

Philia a trois couches de gamification distinctes qui s'articulent sans s'écraser.

### Couche 1 — La structure de progression (la carte-monde)

Comment l'enfant navigue dans le programme.

**Forme retenue : carte-monde semi-linéaire.**

- Les 7 semaines = 7 univers thématiques visibles sur une carte
- L'enfant voit la carte entière dès le début (motivation : voir le chemin)
- Les univers se débloquent dans l'ordre (rigueur : la progression spiralaire l'exige — pas de calcul littéral avant les fractions)
- À l'intérieur d'un univers, l'enfant a de la liberté dans l'ordre des sessions

Les 7 univers :
1. **La Vallée des Fractions** (semaine 1 — Fractions)
2. **La Cité des Proportions** (semaine 2 — Proportionnalité et pourcentages)
3. **La Forteresse du Calcul Littéral** (semaine 3 — Calcul littéral)
4. **Le Royaume des Aires** (semaine 4 — Géométrie et aires)
5. **La Vallée des Nombres Relatifs** (semaine 5 — Nombres relatifs)
6. **Les Miroirs de Symétrie** (semaine 6 — Symétries, stretch)
7. **Le Pic des Statistiques** (semaine 7 — Statistiques, stretch)

Chaque univers a une identité visuelle propre (palette, décor, ambiance) et se franchit en complétant ses sessions puis son Épreuve du Maître.

### Couche 2 — Les types de jeux pédagogiques

Les formats de jeu qui portent les exercices. Chaque format est assigné à un moment pédagogique précis.

| Format de jeu | Mode pédagogique | Registre cognitif | Rôle |
|---|---|---|---|
| **Dialogue maïeutique** | Découverte, Validation | Réflexion lente | Cœur pédagogique — la question socratique |
| **Résolution guidée** | Pratique | Raisonnement structuré | Méthode Polya appliquée |
| **Défi de vitesse** | Consolidation uniquement | Automatismes | Récompense la maîtrise consolidée |
| **Escape game** | Épreuve du Maître (hebdo) | Synthèse | Mobilise tout l'univers de la semaine |
| **Défi créatif** | Bilan, fin d'univers | Création | L'enfant invente un problème |

**Point critique sur les défis de vitesse** : ils ne touchent JAMAIS aux concepts en cours d'apprentissage. On ne chronomètre pas la compréhension d'une fraction. On chronomètre la récitation de fractions équivalentes une fois le concept acquis. La vitesse récompense la maîtrise, elle ne l'enseigne pas. Place : échauffement de début de session, ou mini-défi pour débloquer une porte de la carte.

**Escape game** : une fois par univers, en Épreuve du Maître de fin de semaine. L'enfant entre dans un escape game thématique et doit mobiliser tout ce qu'il a appris pour résoudre l'énigme finale et "sortir". C'est l'aboutissement narratif et pédagogique de la semaine. En faire un format quotidien le banaliserait.

### Couche 3 — Les mécaniques d'engagement

Déjà travaillées en détail (intégration analyse Grok). Rappel synthétique :

- **Mentor évolutif** : l'avatar-mentor que l'enfant fait grandir
- **Radar des 6 superpouvoirs cognitifs** : visualisation des compétences
- **Mur des victoires** : achievements visuels
- **Badges signifiants** : 10-12 badges chargés de sens
- **Collection d'analogies** : analogies personnelles débloquées
- **Quête d'Héritage** : conseil de l'enfant à son moi-de-septembre
- **Jauge d'énergie du mentor** : anti-fatigue par game design

---

## L'ARTICULATION DES 3 COUCHES

Les trois couches sont trois représentations de la même réalité : **l'enfant grandit**.

- La **carte-monde** montre la progression vue "voyage" (où j'en suis dans l'aventure)
- Le **mentor évolutif** montre la progression vue "compagnon" (comment mon mentor a grandi avec moi)
- Le **radar des superpouvoirs** montre la progression vue "compétences" (ce que je sais faire maintenant)

L'enfant qui ouvre Philia voit les trois. Trois angles, une vérité.

---

## LE CORE LOOP QUOTIDIEN

Ce que vit l'enfant à chaque session (15-20 min) :

1. **Accueil** — le mentor accueille l'enfant (illustration + message personnalisé, voix layer A/B pour les tiers payants)
2. **Carte** — l'enfant voit où il en est, choisit sa session du jour dans l'univers courant
3. **Échauffement** (optionnel) — un défi de vitesse court sur des automatismes déjà acquis
4. **Session pédagogique** — le cœur : dialogue maïeutique, le mentor bascule entre les 5 modes
5. **Feedback visuel** — expression du mentor, progression du radar, déblocage éventuel
6. **Réflexion métacognitive** — courte question de mode Bilan
7. **Mise à jour** — le mentor évolue visuellement, la carte se met à jour, badge éventuel

En fin de semaine : **Épreuve du Maître** (escape game de synthèse) pour débloquer l'univers suivant.

---

## DÉCOUPAGE MVP / v1.1 / v1.2

La vision complète ne peut PAS être livrée le 1er juillet. Découpage discipliné.

### MVP — 1er juillet 2026 (lancement)

L'objectif du MVP : un produit qui tient sa promesse pédagogique et offre une expérience gamifiée crédible, sans toutes les fonctionnalités.

**Inclus dans le MVP** :
- Carte-monde avec 3 univers ouverts (Fractions, Proportions, Calcul Littéral)
- Les 5 modes pédagogiques fonctionnels
- Dialogue maïeutique (cœur — non négociable)
- Résolution guidée (mode Pratique)
- Mentor évolutif dégradé : 3 styles × 5 expressions, 1 niveau d'évolution
- Radar des 6 superpouvoirs (version simple)
- Mur des victoires basique
- 5 badges (sur les 10-12 prévus)
- Bilan parent hebdomadaire
- 2 tiers : Quest Gratuit + Summer Premium (voir note tarification ci-dessous)
- Défis de vitesse en mode Consolidation
- 1 Épreuve du Maître (escape game) pour le premier univers

**Reporté en v1.1 et v1.2** :
- Univers 4 et 5 (Aires, Nombres Relatifs) → v1.1 mi-juillet
- Univers 6 et 7 stretch (Symétries, Statistiques) → v1.2 août
- Mentor évolutif complet (8 styles × 10 expressions, 3 niveaux, unlocks tenues/accessoires) → v1.1 et v1.2
- Collection d'analogies → v1.1
- Quête d'Héritage → v1.1 (pas urgente avant la fin du programme de toute façon)
- Escape games des univers 2-7 → déployés au fil des semaines
- Concours national type Kangourou → événement de fin août, construit en juillet

### v1.1 — mi-juillet 2026

- Univers 4 et 5 ouverts
- Mentor évolutif enrichi (5 styles × 8 expressions, 2 niveaux)
- Collection d'analogies active
- Quête d'Héritage active
- Escape games univers 2-5

### v1.2 — août 2026

- Univers 6 et 7 stretch ouverts
- Mentor évolutif complet (8 styles × 10 expressions, 3 niveaux, tous les unlocks)
- Préparation et tenue du Concours National (type Kangourou, fin août)
- Polish général, ajustements selon retours des familles

**Communication produit** : ne jamais promettre tout le contenu au 1er juillet. Parler de "programme qui s'ouvre semaine après semaine, comme un vrai voyage". L'ouverture progressive est cohérente avec le format été — l'enfant n'a pas besoin de la semaine 6 le 1er juillet.

---

## NOTE — IMPACT SUR LA TARIFICATION

Le concours devient gratuit, type Kangourou (compétition amusante et méritante, ouverte à tous). Cela supprime la justification du 3e tier "Quest Premium + Concours" à 29€.

**Recommandation : passer à 2 tiers.**

- **Quest Gratuit** : 0€ — 6 missions découvertes, mentor évolutif basique, carte limitée
- **Summer Premium** : 24€ (early bird 19,80€) — accès illimité 7 semaines, tous modes, voix, rapports parents, certificat, badges complets, **et participation au Concours National incluse**

Le concours devient un argument de valeur du tier Premium (et un événement de marque ouvert), pas un tier à part. Cela simplifie le paywall, simplifie la communication, et retire le frottement du choix à 3 options.

À valider de ton côté — mais c'est la conséquence logique de ta décision sur le concours.

---

## CE QUI RESTE À PRODUIRE

Une fois cette spec validée :

1. **Cahier des charges graphiste** — basé sur cette spec gamification (univers, mentor, expressions, carte). Je peux le produire.
2. **Mise à jour du Plan Architecte v1.1** — intégrer le découpage MVP/v1.1/v1.2 dans les 6 sprints
3. **Schémas YAML des univers et de la carte** — structure de données de la progression

---

*Spécification Gamification Philia Summer Quest v1.0.*
*Sous réserve de validation et d'ajustements du fondateur.*
