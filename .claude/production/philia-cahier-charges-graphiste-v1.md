# PHILIA SUMMER QUEST — Cahier des Charges Graphiste v1.0

**Document de spécification visuelle. Formulé comme instruction à transmettre à Grok.**
**Grok pilote la production avec le graphiste et Midjourney.**
**Le graphisme sert une app Streamlit — contraintes techniques strictes.**

---

## COMMENT UTILISER CE DOCUMENT

Ce cahier des charges est destiné à être transmis à Grok, qui pilotera la production visuelle avec le graphiste et Midjourney. Il définit QUOI produire, dans QUEL ordre, avec QUELLES contraintes. Il ne définit pas les prompts Midjourney précis — c'est le travail de Grok et du graphiste — mais il fixe le cadre que la production doit respecter.

---

## 1. CONTEXTE PRODUIT (pour que Grok comprenne ce qu'il habille)

Philia Summer Quest est un programme de révision mathématique d'été pour enfants de 11-12 ans (fin 6e, entrée 5e). L'enfant incarne un "Élévateur" qui fait remonter les îles d'un archipel en ruine en maîtrisant les mathématiques. Son guide est Archimède, un mentor bienveillant.

7 îles = 7 semaines. Chaque île s'élève visuellement au fur et à mesure des progrès. L'app tourne en Streamlit (interface web sobre). MVP au 1er juillet 2026 avec les 3 premières îles.

L'univers narratif : "L'Ascension des Sept Îles". Ton : chaleureux, positif, aventureux, jamais anxiogène. L'enfant doit avoir envie d'y retourner chaque jour.

---

## 2. CONTRAINTES TECHNIQUES STREAMLIT (non négociables)

Le graphiste doit produire pour une app Streamlit. Cela impose :

- **Formats** : PNG (avec transparence si besoin) et GIF (pour les animations légères). Pas de SVG animé complexe, pas de vidéo.
- **Poids** : chaque image optimisée pour le web. Cible : < 300 Ko par illustration d'île, < 150 Ko par expression de mentor, < 500 Ko par GIF. Une app Streamlit lente à cause d'images lourdes ruine l'expérience enfant.
- **Résolutions** : prévoir 2 tailles par asset (affichage standard + retina). Largeur max utile : 1200 px pour les grandes images d'île, 400 px pour le mentor, 150 px pour les icônes.
- **Cohérence de gabarit** : la structure d'écran est fixe (sidebar, zone centrale, chat, en-tête). Les visuels doivent s'insérer dans ces zones sans les déborder. Voir section 4.
- **Pas de drag & drop, pas de parallax** : les illustrations sont statiques ou en GIF simple. L'interactivité vient des boutons Streamlit, pas du graphisme.

---

## 3. CHARTE GRAPHIQUE (déjà définie, à respecter)

**Style** : cartoon moderne chaleureux. Référence d'esprit : entre l'illustration jeunesse européenne contemporaine et l'animation douce type Pixar light. Éviter l'esthétique manga marquée (polarise) et l'esthétique edtech américaine générique.

**Palette** :
- Fond principal : #F8FAFC (clair)
- Accent bleu : #4A9FFF
- Turquoise élévation (couleur sémantique de la progression) : #3CE8C2
- Orange réussite : #FF9F4A
- Texte : #1E2937

**Principes** :
- Lisibilité maximale sur fond clair
- Couleurs vives mais pas criardes
- Rien d'anxiogène, rien de sombre even pour les états "île endommagée" (l'île abîmée doit être mélancolique, pas effrayante)
- Cohérence absolue d'un asset à l'autre — c'est le point le plus important (voir section 6)

---

## 4. STRUCTURE D'ÉCRAN À HABILLER

Le graphiste produit pour une structure d'écran fixe :

```
┌─────────────────────────────────────────────┐
│  EN-TÊTE : "Semaine X – Nom de l'Île"        │
│            + petite image d'Archimède         │
│            + barre d'élévation turquoise       │
├──────────┬──────────────────────────────────┤
│ SIDEBAR  │  ZONE CENTRALE                    │
│          │                                   │
│ Avatar   │  Grande image de l'île            │
│ mentor   │  (change selon % élévation)       │
│          │                                   │
│ Artefacts│  3-4 boutons "zones cliquables"   │
│ équipés  │                                   │
│          │                                   │
│ Élévation├──────────────────────────────────┤
│ globale  │  ZONE CHAT avec Archimède         │
│          │  (st.chat_message)                │
└──────────┴──────────────────────────────────┘
```

Chaque asset visuel a une place précise dans ce gabarit. Le graphiste doit connaître la zone de destination de chaque image qu'il produit.

---

## 5. INVENTAIRE DES ASSETS À PRODUIRE

### 5.1 Le mentor Archimède (PRIORITÉ ABSOLUE)

Archimède est le personnage central. L'enfant le voit à chaque session. Sa cohérence est non négociable.

**À produire pour le MVP** :
- Archimède en 10 expressions (le même personnage, 10 états émotionnels) :
  1. Neutre / calme
  2. Sourire doux (encouragement)
  3. Grand sourire fier
  4. Concentré / pensif
  5. Surpris / intéressé
  6. Bienveillant exigeant (sourcil levé)
  7. Célébration / joie
  8. Doux / réconfort (après erreur ou fatigue)
  9. Inspiré / brillant (idée créative)
  10. Sage / accompli (fin de quête)

- Format : buste ou personnage en pied, fond transparent (PNG), pour insertion dans la sidebar et en en-tête
- Une version "grande" pour les transitions importantes (début/fin de semaine)

**Note sur le mentor évolutif** : le concept d'avatar évolutif (le mentor qui gagne des éléments visuels au fil des progrès) est prévu mais dégradé en MVP. Pour le 1er juillet : 3 styles de base d'Archimède (l'enfant en choisit un) × les 10 expressions. L'enrichissement (tenues, accessoires débloquables) vient en v1.1 et v1.2. Le graphiste doit concevoir Archimède de façon modulaire dès le départ — un personnage de base sur lequel on pourra ajouter des éléments plus tard.

### 5.2 Les îles — états d'élévation (PRIORITÉ HAUTE)

Chaque île existe en 4 états visuels correspondant à son niveau d'élévation :
- Niveau 0 : île engloutie / très endommagée (mélancolique, pas effrayante)
- Niveau 1 : île émergée, premières réparations
- Niveau 2 : île à mi-hauteur, structures se reconstruisant
- Niveau 3 : île élevée, rayonnante, réparée

**Pour le MVP (1er juillet)** : les 3 premières îles × 4 états = 12 grandes illustrations d'îles.
- Île 1 — L'Île des Nombres Brisés (thème : structures fracturées, ponts cassés, statues penchées)
- Île 2 — La Forêt des Mesures (thème : forêt chaotique, arbres tordus, rivières débordantes)
- Île 3 — Le Labyrinthe des Inconnues (thème : labyrinthe, énigmes, mécanismes mystérieux)

**Pour v1.1 et v1.2** : îles 4 à 7, même principe (4 états chacune).

### 5.3 Les zones cliquables des îles (PRIORITÉ HAUTE)

Chaque île a 3-4 "zones" que l'enfant clique pour accéder aux défis. Chaque zone = une petite illustration ou une icône.

Exemple Île 1 : La Plage Fissurée, La Statue Penchée, Le Chemin des Marches, La Fissure Principale, Le Mur Effondré, La Fontaine Cassée, les Balances Antiques, le Grand Pont.

**Pour le MVP** : environ 5-8 zones par île × 3 îles = ~20 illustrations de zones.

### 5.4 La carte de l'archipel (PRIORITÉ MOYENNE)

Une illustration de la carte des 7 îles, où l'enfant voit sa progression globale. Les îles débloquées rayonnent, les îles verrouillées sont en attente. 1 illustration de carte + états de déblocage.

### 5.5 Les éléments de jeu (PRIORITÉ MOYENNE)

- **Cristaux de Loi** : ~5 cristaux par île, chacun avec une identité visuelle (Cristal du Partage, de la Juste Part, du Reflet, de la Balance, de l'Assemblage pour l'Île 1). Petites icônes.
- **Artefacts** : objets débloqués affichés en sidebar (Clé des Fractions, Calculatrice Ancienne, etc.). ~3-5 par île. Petites icônes.
- **Badges** : 10-12 badges pour tout le programme. Icônes.
- **Radar des superpouvoirs** : le radar lui-même est généré par Plotly (pas le graphiste), mais les 6 icônes des superpouvoirs (Maïeutique, Transfert, Persévérance, Clarté, Créativité, Métacognition) sont à illustrer.

### 5.6 Les animations GIF (PRIORITÉ MOYENNE)

Animations légères, simples :
- Île qui monte d'un palier (transition entre 2 états)
- Particules turquoise d'élévation
- Célébration (déblocage artefact, réussite)
- Échec doux (île qui tremble légèrement — jamais punitif)

Cible : 8-12 GIFs courts pour le MVP.

### 5.7 Éléments d'interface (PRIORITÉ BASSE)

Icônes diverses, boutons stylisés, fond de la zone chat (esprit "parchemin ancien" évoqué), barre d'élévation. Le graphiste harmonise avec la charte.

---

## 6. LE POINT CRITIQUE — LA COHÉRENCE DU PERSONNAGE

C'est le risque n°1 de toute production visuelle par IA générative. Quand on génère 10 expressions d'Archimède avec Midjourney, le visage change subtilement d'une image à l'autre (forme du nez, âge apparent, proportions). Pour un enfant, "son" Archimède doit être reconnaissable et stable sur 7 semaines.

**Instructions impératives pour Grok et le graphiste** :

1. **Figer Archimède d'abord.** Produire UNE image de référence d'Archimède validée, avant toute autre production. Cette image est la "bible" du personnage.

2. **Utiliser les fonctions de cohérence de personnage.** Midjourney dispose de fonctions de référence de personnage (character reference). Elles doivent être utilisées systématiquement pour les 10 expressions. Ne jamais générer une expression "from scratch".

3. **Contrôle humain de cohérence.** Le graphiste doit valider visuellement que les 10 expressions sont bien le même personnage. Si une expression dérive, elle est refaite. C'est non négociable.

4. **Retouche manuelle si nécessaire.** Si l'IA ne tient pas parfaitement la cohérence, le graphiste retouche à la main. C'est son métier. La cohérence prime sur la vitesse.

5. **Même principe pour les îles.** Les 4 états d'une même île doivent clairement être la MÊME île à 4 moments. Pas 4 îles différentes. La structure, la silhouette, les éléments-clés restent identiques — seul l'état (endommagé → réparé) change.

---

## 7. ORDRE DE PRODUCTION (aligné sur le calendrier)

Le graphiste produit dans cet ordre pour ne jamais bloquer le développement :

**Lot 1 — Semaine 1 de production (priorité absolue)**
- Archimède : image de référence + 10 expressions
- Île 1 : les 4 états d'élévation
- Zones cliquables de l'Île 1 (~6 illustrations)

**Lot 2 — Semaine 2 de production**
- Îles 2 et 3 : les 4 états chacune
- Zones cliquables des Îles 2 et 3
- Carte de l'archipel

**Lot 3 — Semaine 3 de production**
- Cristaux, artefacts, badges du MVP
- Icônes des 6 superpouvoirs
- GIFs d'animation
- Éléments d'interface

**Lots 4+ — En parallèle du MVP lancé**
- Îles 4 à 7 (pour v1.1 et v1.2)
- Enrichissement du mentor évolutif (tenues, accessoires)

Le Lot 1 doit être livré avant le Sprint 3 du développement (semaine 3), où le code intègre les assets. Si le graphiste démarre maintenant, le timing est tenable.

---

## 8. CE QUE GROK DOIT FAIRE DE CE DOCUMENT

1. Traduire ce cahier des charges en prompts Midjourney précis pour chaque asset
2. Établir avec le graphiste le planning de production aligné sur les 3 lots
3. Faire valider l'image de référence d'Archimède AVANT de lancer la production de masse
4. Contrôler la cohérence à chaque lot livré
5. Optimiser le poids des fichiers pour Streamlit (compression sans perte de qualité visible)
6. Livrer les assets dans une arborescence claire correspondant à `assets/` du repo :
   ```
   assets/
   ├── mentor/         (Archimède + expressions)
   ├── iles/           (les 4 états × 7 îles)
   ├── zones/          (zones cliquables par île)
   ├── ui/             (cristaux, artefacts, badges, icônes)
   └── sounds/         (hors scope graphiste)
   ```

---

## 9. CRITÈRES DE VALIDATION

Un lot est validé si :
- La cohérence du personnage Archimède est parfaite sur toutes les expressions
- Les 4 états d'une île sont reconnaissables comme la même île
- Les poids de fichiers respectent les cibles Streamlit
- La charte (couleurs, style) est respectée
- Aucun élément anxiogène
- L'arborescence de livraison est correcte

---

*Cahier des Charges Graphiste Philia Summer Quest v1.0.*
*À transmettre à Grok pour pilotage de la production avec le graphiste et Midjourney.*
