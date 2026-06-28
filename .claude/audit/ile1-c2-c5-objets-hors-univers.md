# Audit T8.4 — Objets hors-univers dans les sessions C2 à C5
**Fichier** : `.claude/pedagogie/ile-1-nombres-brises-CONTENU.md`  
**Scope** : Sessions 2 à 5 (concepts C2, C3, C4, C5) + Bilan Île 1 (§9)  
**Date** : 28 juin 2026  
**Auteur** : Architect (Cowork) — T8.4 Phase 2  
**Action** : lister pour T8.5 (post-MVP) — **NE PAS RÉÉCRIRE ce sprint**

---

## Méthode

Pour chaque violation :
- **CRITIQUE** = mot explicitement en liste noire (tarte, pizza, gâteau, biscuits, pomme, orange, bonbon, chocolat)
- **AMBIGU** = mot hors-liste-blanche, pas explicitement interdit, à décider en T8.5
- **ACCEPTABLE** = objet qui semble hors-univers mais s'intègre plausiblement dans Syracuse antique

---

## SESSION 2 — "Les Réserves de l'Île" (C2)

### Exercice ile1_s2_ex1 — AMBIGU
```
enonce: "Dans une réserve, il y a 12 fruits. Archimède demande d'en prendre 1/3."
```
**Objet** : `fruits`  
**Statut** : AMBIGU — pas explicitement dans la liste noire (ni pomme ni orange), mais générique alimentaire. Dans le contexte d'une réserve d'île antique, des "figues" ou "grenades" seraient plus cohérents, mais l'objet idéal serait un matériau de chantier (pierres, tuiles).  
**Occurrence secondaire** : si_echec : `"par exemple 12 fruits à partager en 3 paniers"` — même objet.  
**Remplacement suggéré pour T8.5** : `"12 briques"` / `"12 carreaux de tuile"` / `"12 pierres taillées"` (cohérent avec le thème chantier C1).

---

## SESSION 3 — "Les Miroirs d'Eau" (C3)

### validation_feynman — CRITIQUE
```
critere_reussite: "Tu peux utiliser l'image d'un gâteau, d'un miroir ou d'une tablette."
```
**Objet** : `gâteau` ← **LISTE NOIRE**  
**Statut** : CRITIQUE — gâteau est explicitement interdit.  
**Remplacement suggéré pour T8.5** : `"Tu peux utiliser l'image d'un bloc de marbre, d'un bassin d'eau ou d'une dalle."`

---

## SESSION 4 — "La Grande Balance" (C4)

### Exercice ile1_s4_ex1 — ACCEPTABLE
```
enonce: "On compare 3/8 d'une tablette et 5/8 de la même tablette."
```
**Objet** : `tablette`  
**Statut** : ACCEPTABLE — "tablette de marbre" ou "tablette de pierre à graver" est cohérent avec Syracuse antique et le chantier. Ne contient pas "chocolat". Pas d'action requise.

---

### Exercice ile1_s4_ex2 — CRITIQUE x3
```
enonce:        "La balance compare 1/4 d'une tarte et 1/8 de la même tarte."
indices.leger: "Imagine deux tartes identiques : l'une coupée en 4, l'autre en 8."
```
**Objet** : `tarte` x2 ← **LISTE NOIRE**  
**Statut** : CRITIQUE.  
**Remplacement suggéré pour T8.5** : `"La balance compare 1/4 d'une dalle de marbre et 1/8 de la même dalle."`

```
erreurs_typiques[2].reponse_maieutique:
  "Imagine une pizza coupée en 4 parts, puis une pizza identique coupée en 8."
```
**Objet** : `pizza` ← **LISTE NOIRE**  
**Statut** : CRITIQUE.  
**Remplacement suggéré pour T8.5** : `"Imagine une dalle coupée en 4 blocs, puis une dalle identique coupée en 8 blocs."`

---

### validation_feynman de C4 — CRITIQUE x2
```
consigne: "Utilise une image de tarte ou de pizza."
si_echec: "deux pizzas identiques, l'une coupée en 4, l'autre en 8"
```
**Objets** : `tarte` + `pizza` x2 ← **LISTE NOIRE**  
**Remplacement suggéré pour T8.5** :
- consigne : `"Utilise l'image d'une dalle de marbre ou d'une planche de pont."`
- si_echec : `"deux planches identiques, l'une coupée en 4, l'autre en 8."`

---

## SESSION 5 — "L'Assemblage des Parts" (C5)

### Aucune violation de liste noire.

```
validation_feynman: "Utilise l'image d'un pont ou d'une tablette."
```
**Objet** : `tablette`  
**Statut** : ACCEPTABLE — "tablette de pierre" en contexte Syracuse antique. Sans "chocolat", pas de violation.

---

## BILAN ÎLE 1 — §9 "Consolidation Spiralaire"

### vigilance_pour_ile_2 — CRITIQUE
```
"Si l'enfant compare les fractions par la taille brute des nombres,
revenir à la Grande Balance avec des pizzas ou des tablettes."
```
**Objet** : `pizzas` ← **LISTE NOIRE**  
**Remplacement suggéré pour T8.5** : `"revenir à la Grande Balance avec des dalles ou des planches du pont."`

---

## Récapitulatif des violations

| ID | Session | Champ | Objet | Statut |
|----|---------|-------|-------|--------|
| V1 | C2/ile1_s2_ex1 | enonce | fruits | AMBIGU |
| V2 | C2/si_echec | si_echec | fruits | AMBIGU |
| V3 | C3/validation_feynman | critere_reussite | gâteau | CRITIQUE |
| V4 | C4/ile1_s4_ex2 | enonce | tarte | CRITIQUE |
| V5 | C4/ile1_s4_ex2 | indices.leger | tarte | CRITIQUE |
| V6 | C4/ile1_s4_ex2 | erreurs_typiques[2] | pizza | CRITIQUE |
| V7 | C4/validation_feynman | consigne | tarte + pizza | CRITIQUE |
| V8 | C4/si_echec | si_echec | pizza | CRITIQUE |
| V9 | §9 bilan vigilance | vigilance_pour_ile_2 | pizza | CRITIQUE |

**Total CRITIQUE : 7 violations (6 lieux distincts)**  
**Total AMBIGU : 2 violations (fruits dans C2)**

---

## Note Architect

Toutes les violations CRITIQUE sont concentrées dans C3/C4 (validation_feynman + un exercice de C4). C2 a un cas ambigu (fruits), C5 est propre. La Session 4 ("La Grande Balance") est le foyer principal — elle devra être entièrement réécrite en T8.5 pour remplacer la métaphore tarte/pizza par dalle/planche.

Aucun objet "scandaleusement" hors-univers (téléphone, ordinateur, etc.) détecté — pas d'escalade requise au-delà de la liste standard.

*— Audit T8.4 Phase 2 terminé.*
