# PHILIA SUMMER QUEST — Cadre de Progression Jeu-Programme v1.0

**Document de design pédagogique. Pose la grammaire de progression et le patron de construction des 7 îles.**
**À utiliser comme référence par le fondateur et son épouse pour décliner les univers.**

---

## DÉCISIONS STRUCTURANTES ACTÉES

- Stack : Streamlit, UI sobre assumée, élévation des îles en visuels statiques par paliers
- Métaphore : l'Ascension des Sept Îles (Archimède, archipel qui s'élève) — gardée, version faisable
- Rythme : libre, 15-25 min par session, ~5 sessions/semaine recommandées mais non imposées
- Pédagogie : 5 modes + Infusion Spiralaire (spec pédagogique v1.0)
- Découpage : MVP 1er juillet (3 îles) / v1.1 mi-juillet (2 îles) / v1.2 août (2 îles stretch)

---

## 1. LE MONDE — L'ASCENSION DES SEPT ÎLES

L'enfant est un jeune **Élévateur**, apprenti architecte de mondes. Son pouvoir : faire s'élever les îles d'un archipel en ruine grâce à la maîtrise des Lois Fondamentales (les mathématiques).

Chaque île est un univers thématique lié au programme. L'île commence au niveau de la mer. Elle s'élève par paliers visuels au fur et à mesure que l'enfant maîtrise les concepts. À la fin des 7 semaines, l'archipel entier est élevé et révèle le **Sanctuaire de la Raison**.

Le guide : **Archimède** (Maître Archos), hologramme ancien et bienveillant. Il ne donne jamais la réponse. Il pose les questions qui font découvrir. Voix off aux transitions (début/fin de semaine), chat texte le reste du temps.

**Version Streamlit-faisable de l'élévation** : chaque île a 4 états visuels statiques produits par le graphiste — Niveau 0 (île engloutie/basse), Niveau 1 (émergée), Niveau 2 (à mi-hauteur), Niveau 3 (élevée, rayonnante). L'image change quand l'enfant franchit un palier. Pas d'animation 3D, pas de parallax — une transition d'image avec un effet visuel simple (fondu, particules CSS légères).

---

## 2. LA GRAMMAIRE DE PROGRESSION — CE QUI FAIT QU'ON AVANCE

C'est le cœur du cadre. Il faut une règle claire et unique : qu'est-ce qui fait monter l'île ?

### Principe : l'île monte à la VALIDATION, pas à la découverte

L'erreur classique serait de faire monter l'île à chaque exercice réussi. Cela cale le jeu sur le rythme de l'exercice, pas sur le rythme de l'apprentissage. Résultat : l'enfant avance vite et n'ancre rien.

**Règle Philia** : l'île monte d'un palier quand un **bloc de concept** passe en mode Validation réussie — c'est-à-dire quand l'enfant a non seulement résolu, mais a su *expliquer* (technique Feynman). La montée de l'île récompense la compréhension prouvée, pas la performance.

### Les 4 paliers d'une île

| Palier | Condition de franchissement | Sens pédagogique |
|---|---|---|
| **Niveau 0 → 1** | L'enfant a complété les sessions Découverte de l'île | "J'ai rencontré les concepts" |
| **Niveau 1 → 2** | L'enfant a validé (Feynman) 50% des concepts-clés de l'île | "Je commence à comprendre" |
| **Niveau 2 → 3** | L'enfant a validé 100% des concepts-clés + réussi le Rite d'Élévation | "Je maîtrise, l'île rayonne" |

Entre les paliers, l'enfant fait ses sessions quotidiennes (Découverte, Pratique, Consolidation). Les paliers ne sont pas franchis à chaque session — ils marquent les grandes étapes. Cela donne au jeu un rythme calme, cohérent avec l'apprentissage réel.

### Le "Cristal de Loi" — l'unité de progression intermédiaire

Pour que l'enfant ressente une progression *entre* les paliers, chaque concept-clé maîtrisé lui donne un **Cristal de Loi** qu'il place sur la structure de l'île. Visuellement : la structure de l'île se complète cristal par cristal. Quand tous les cristaux d'un palier sont placés, l'île monte.

C'est la granularité fine (le cristal = un concept) sous la granularité large (le palier = un groupe de concepts). L'enfant a un feedback à chaque concept sans que l'île monte de façon désordonnée.

---

## 3. RÉSOLUTION DE LA TENSION 1 — RYTHME PÉDAGOGIE VS RYTHME JEU

Le jeu et la pédagogie ont des rythmes différents. Le point de synchronisation est défini ci-dessus : **le cristal (concept validé) et le palier (groupe validé)**. Mais il faut aussi gérer le quotidien.

### Le core loop quotidien (15-25 min)

1. **Arrivée sur l'île** — Archimède accueille (texte, ou voix si transition de semaine). L'enfant voit l'état actuel de son île.
2. **Échauffement** (3-5 min, optionnel) — un défi de vitesse sur des automatismes déjà acquis (calcul mental, tables). Jamais sur le concept du jour.
3. **Session pédagogique du jour** (10-18 min) — le cœur. Archimède mène le dialogue maïeutique. Le mode (Découverte/Pratique/Validation/Consolidation) dépend de l'avancée de l'enfant dans l'île.
4. **Récolte** (2-3 min) — si un concept a été validé, l'enfant place un Cristal de Loi. Feedback visuel. Révélation éventuelle (fragment de lore).
5. **Note de Raison** (1-2 min) — courte réflexion métacognitive : "Qu'as-tu compris aujourd'hui que tu ne savais pas hier ?"

Le jeu (arrivée, récolte, révélation) encadre la pédagogie (session) sans l'écraser. Le jeu est l'enveloppe émotionnelle ; la session maïeutique est le cœur cognitif.

---

## 4. RÉSOLUTION DE LA TENSION 2 — INFUSION SPIRALAIRE DANS UNE CARTE LINÉAIRE

L'enfant avance île par île. Mais les fractions de l'île 1 doivent réapparaître pendant l'île 4. Comment matérialiser ce retour sans casser la logique de carte ?

### Mécanisme : les "Résurgences"

Pendant qu'il travaille sur une île, l'enfant rencontre parfois une **Résurgence** — un fragment d'une île précédente qui réapparaît dans le contexte de l'île courante.

Exemple concret : dans l'île 4 (Royaume des Proportions), une Résurgence de l'île 1 surgit — un problème de proportion qui nécessite de manipuler des fractions. Archimède le souligne : "Tiens, une Loi de l'Île des Nombres Brisés refait surface ici. Tu te souviens ?"

Narrativement : les îles sont reliées par des courants. Quand une île s'élève, elle fait remonter des fragments des îles voisines. La Résurgence est un cadeau du monde, pas une punition de révision.

Pédagogiquement : c'est l'interleaving. Le concept ancien est réactivé dans un contexte neuf, à distance temporelle — exactement la zone d'oubli critique (70-90% de maîtrise) où la réactivation est la plus puissante.

**Règle de construction** : chaque île à partir de l'île 2 contient 2-3 Résurgences planifiées d'îles antérieures. Elles sont définies dans le YAML de l'île. Ce n'est pas aléatoire — c'est une réactivation pédagogique calculée.

---

## 5. RÉSOLUTION DE LA TENSION 3 — HÉTÉROGÉNÉITÉ DES ENFANTS

Un enfant fragile et un enfant à l'aise sont sur la même île. Le jeu doit absorber cette différence sans humilier ni ennuyer.

### Trois leviers d'adaptation

**Levier 1 — Le rythme libre.** L'enfant fragile prend plus de sessions pour franchir un palier. L'enfant rapide en prend moins. L'île monte pour les deux, mais pas à la même vitesse. Personne n'est "en retard" — chacun élève son île à son rythme. Le rythme libre (déjà acté) est le premier outil d'adaptation.

**Levier 2 — Les Zones de Profondeur.** Dans chaque île, au-delà du parcours principal, existent des **Zones de Profondeur** — des défis optionnels plus difficiles, qui poussent l'anticipation 5e plus loin. L'enfant à l'aise y va et "prend de l'avance" (cohérent avec la promesse "découvre la 5e"). L'enfant fragile les ignore sans pénalité. Les Zones de Profondeur sont la soupape pour les rapides.

**Levier 3 — La maïeutique adaptative d'Archimède.** Le dialogue lui-même s'adapte. Face à un blocage, Archimède décompose plus finement (les 4 niveaux de décomposition des guardrails). Face à une réussite rapide, il pousse vers le niveau cognitif supérieur ("Et pourquoi ça marche ? Peux-tu inventer un cas où ça ne marcherait pas ?"). L'adaptation se joue dans le prompt, en temps réel, selon le profil et les réponses.

**Ce qu'on ne fait PAS** : on ne crée pas des "parcours faciles / difficiles" séparés. Une seule île, une seule carte, un seul monde. L'adaptation est invisible — elle se joue dans le rythme, les zones optionnelles et le dialogue. L'enfant ne se sait jamais "dans le groupe faible".

---

## 6. RÉSOLUTION DE LA TENSION 4 — DENSITÉ PAR ÎLE

Combien de sessions, d'exercices, de temps par île ?

### Calibration de référence

Une île = une semaine. Cible : **5 sessions principales + 1 Rite d'Élévation**.

| Élément | Quantité par île | Note |
|---|---|---|
| Concepts-clés | 4 à 6 | Selon la richesse du chapitre |
| Sessions principales | 5 | ~1 par jour ouvré |
| Durée d'une session | 15-25 min | Variable selon l'enfant |
| Exercices par session | 4 à 8 | Progression de difficulté 1→5 |
| Résurgences | 2 à 3 | Îles 2 à 7 uniquement |
| Zones de Profondeur | 2 à 3 | Optionnelles |
| Rite d'Élévation | 1 | Escape game textuel de synthèse, 25-35 min |

**Total contenu par île** : ~5 sessions × 6 exercices = ~30 exercices + le Rite. Sur 7 îles : ~210 exercices + 7 Rites. C'est cohérent avec l'estimation de contenu du Plan Architecte (~250 exercices YAML).

### Règle anti-survol et anti-lassitude

- Si une île a moins de 4 concepts-clés → on enrichit avec plus d'anticipation 5e ou plus de Résurgences
- Si une île a plus de 6 concepts-clés → on scinde ou on déplace un concept vers une Zone de Profondeur
- Une session ne dépasse jamais 25 min de contenu — au-delà, on scinde

---

## 7. LE RITE D'ÉLÉVATION — L'ESCAPE GAME HEBDOMADAIRE

Fin de semaine. L'enfant doit faire monter son île au Niveau 3 en accomplissant le Rite.

**Version Streamlit-faisable** : le Rite est une **énigme textuelle à étapes**, pas un escape game spatial. L'enfant doit activer 4 "Sceaux" (4 puzzles). Chaque Sceau combine plusieurs concepts de la semaine. Pour activer un Sceau, l'enfant résout une énigme contextualisée.

Structure d'un Rite :
- Narration d'ouverture par Archimède (voix off)
- 4 Sceaux successifs, chacun = un puzzle multi-concepts
- Échec autorisé : si un Sceau résiste, l'île tremble (visuel simple), Archimède aide à analyser sans donner la réponse
- Réussite des 4 Sceaux → l'île monte au Niveau 3, animation visuelle simple, révélation majeure de lore

Le Rite synthétise. Il ne contient pas de concept neuf — il mobilise tout ce qui a été vu. C'est le mode Validation à l'échelle de la semaine entière.

---

## 8. LE PATRON DE CONSTRUCTION D'UNE ÎLE

C'est le livrable réutilisable. Pour construire une île, toi et ta femme remplissez ce patron :

```
ÎLE N — [Nom narratif]

1. IDENTITÉ
   - Thème narratif (le décor, l'ambiance, le problème de l'île)
   - Lien programme : révision 6e + anticipation 5e

2. CONCEPTS-CLÉS (4 à 6)
   Pour chacun :
   - Nom du concept
   - Niveau (6e révision / 5e anticipation)
   - Prérequis (concepts nécessaires avant)
   - Cristal de Loi associé (nom narratif)

3. SESSIONS (5)
   Pour chacune :
   - Concept(s) travaillé(s)
   - Mode dominant (Découverte / Pratique / Validation / Consolidation)
   - Situation narrative (le problème de l'île à résoudre)
   - 4 à 8 exercices, difficulté 1→5

4. RÉSURGENCES (2-3, sauf île 1)
   - Quel concept d'une île antérieure réapparaît
   - Dans quelle session
   - Sous quelle forme contextuelle

5. ZONES DE PROFONDEUR (2-3)
   - Défis optionnels d'anticipation 5e poussée

6. RITE D'ÉLÉVATION
   - Narration d'ouverture
   - 4 Sceaux, chacun = un puzzle multi-concepts
   - Révélation de lore à la réussite

7. RÉCOMPENSES
   - Cristaux de Loi (1 par concept-clé)
   - Révélations de lore (fragments d'histoire de l'archipel)
   - Badge de l'île
   - Déblocage visuel du mentor / de l'île
```

---

## 9. RÉPARTITION DES 7 ÎLES SUR LE PROGRAMME

Synthèse de la proposition (à affiner par toi et ta femme lors de la construction détaillée) :

| Île | Nom | Programme | Statut livraison |
|---|---|---|---|
| 1 | L'Île des Nombres Brisés | Fractions, décimaux, opérations | MVP 1er juillet |
| 2 | La Forêt des Mesures | Grandeurs, périmètres, aires, unités | MVP 1er juillet |
| 3 | Le Labyrinthe des Inconnues | Calcul littéral, équations simples | MVP 1er juillet |
| 4 | Le Royaume des Proportions | Proportionnalité, pourcentages, échelles | v1.1 mi-juillet |
| 5 | La Vallée des Nombres Relatifs | Nombres relatifs (anticipation 5e pure) | v1.1 mi-juillet |
| 6 | La Cité des Formes | Géométrie, angles, symétries, triangles | v1.2 août (stretch) |
| 7 | La Tour des Données | Statistiques, lecture de données | v1.2 août (stretch) |

Note : cet ordre privilégie en MVP les 3 chapitres à plus fort enjeu de transition 6e→5e (fractions, mesures/aires, calcul littéral). L'ordre peut être ajusté — mais la logique "MVP = les transitions les plus risquées" doit être préservée.

---

## 10. PROCHAINE ÉTAPE — L'ÎLE PILOTE

Ce cadre pose la grammaire. L'étape suivante (Temps 2) : construire **entièrement l'Île 1 — L'Île des Nombres Brisés** comme modèle, en aller-retour entre toi et moi.

Une fois l'Île 1 validée comme modèle de référence, toi et ta femme déclinez les îles 2 à 7 sur le patron de la section 8. Je peux auditer chaque île en mode Reviewer.

C'est cohérent avec AXON-1 : je suis l'Architecte du cadre et du modèle, vous êtes les producteurs du contenu, je reste le Reviewer pédagogique.

---

*Cadre de Progression Jeu-Programme Philia Summer Quest v1.0.*
*Pose la grammaire de progression et le patron de construction des îles.*
