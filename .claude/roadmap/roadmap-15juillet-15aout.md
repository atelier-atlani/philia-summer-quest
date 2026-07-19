# ROADMAP — Format Révision 10-15 jours (15 juillet → 15 août 2026)

**Document de pilotage du pivot. Produit par l'Architect (Cowork), à valider par le Décideur avant lancement des tâches Implementer.**
**Référence : `.claude/context/00-master-context.md` pour le cadrage stratégique complet et le détail des décisions D25-D28 / Niveau 8.**
**v2 — mise à jour du 15 juillet 2026 (même jour) suite aux décisions produit du Décideur : périmètre resserré (3 sessions Île 2-3), célébrations D27, cinématiques HeyGen D28, énigme finale D17-court, pricing 19€.**

---

## 0. VUE D'ENSEMBLE

| Semaine | Dates | Objectif | Jalon de sortie |
|---|---|---|---|
| S1 | 15 → 21 juillet | Stabilisation + Île 1 finie | Île 1 100 % (narratif, prénom, célébrations, planches BD) + test cobaye #1 |
| S2 | 22 → 28 juillet | Île 2 | Île 2 jouable de bout en bout |
| S3 | 29 juillet → 4 août | Île 3 + cinématiques + énigme finale | Île 3 jouable + énigme finale + 2 cinématiques HeyGen intégrées |
| S4 | 5 → 11 août | Polish + bêta | Version bêta stable, test cobaye formel #4 |
| Tampon | 12 → 15 août | Bug fixing + release | Format Révision 10-15j v1 livré, landing Summer Quest publiée |

Cadre général : périmètre Île 1-2-3, 11 sessions au total (5 + 3 + 3, voir master context §8.2), ~65 exercices. Règle héritée de D7 révisée, reconduite ici : si le rythme dérape, on réduit encore le périmètre avant de toucher au 15 août.

---

## SEMAINE 1 (15 → 21 juillet) — STABILISATION + ÎLE 1 FINIE

**Objectif** : clore définitivement l'Île 1, y compris les chantiers laissés ouverts depuis fin juin, et implémenter les décisions transverses du 15 juillet qui s'appliquent aux trois îles.

**Tâches** :
- Câblage narratif complet (T8.5) : nettoyage du patron `.claude/pedagogie/ile-1-nombres-brises-CONTENU.md` (27 occurrences d'objets hors-univers non corrigées depuis l'audit du 28 juin) et vérification de cohérence avec `pedagogie/contenu_ile1.py`
- D19bis — prénom élève : champ de saisie à l'inscription (onboarding), injection dans les prompts d'Archimède, fallback « Élévateur » si absent
- D27 — célébrations légères : système confetti + toast personnalisé au prénom, déclenché par bonne réponse
- D14bis — asset `archipel_isometrique` : vignette de l'Île 1 sur la carte, câblage
- Planches BD manquantes de l'Île 1 : C2 à C5, rite intro/fin (seuil qualité « B », D20)
- Test cobaye #1 (informel, §8.6) sur l'Île 1 complète

**Répartition des rôles** :
- Toi + ton épouse : disponibilité pour le test cobaye #1, validation finale du contenu Île 1 nettoyé
- Architect : brief technique détaillé D19bis et D27 (specs pour l'Implementer), audit du nettoyage narratif
- Implementer : nettoyage patron, câblage prénom, système célébrations, intégration planches BD manquantes
- Reviewer : audit rapide en fin de semaine (cohérence univers, maïeutique préservée malgré les ajouts)

**Livrables** : Île 1 à 100 % (contenu + narratif + planches + prénom + célébrations) ; rapport du test cobaye #1.

**Check-in** : 21 juillet — Décideur valide le socle avant que la production Île 2 ne démarre sur ce même socle.

---

## SEMAINE 2 (22 → 28 juillet) — ÎLE 2

**Objectif** : produire l'Île 2 intégralement, sur le patron nettoyé de l'Île 1.

**Tâches** :
- Contenu pédagogique YAML — 3 sessions (§8.2), concepts C1-C5 déjà nommés (Étalon, Passage, Contour, Étendue, Sablier) répartis sur les 3 sessions
- Graphique sobre (§8.3) : vue immersive, scène d'arrivée, scène de présentation, une planche BD de synthèse
- Câblage `pedagogie/contenu_ile2.py` sur le patron `contenu_ile1.py`
- Câblage narratif (accueil, élévations, ouverture du Rite compressé) à partir de `narration-iles.md` (déjà ~80 % rédigé)
- Test informel #2 (§8.6)

**Répartition des rôles** :
- Toi + ton épouse : rédaction et validation du contenu mathématique des 3 sessions
- Architect : adaptation du format YAML enrichi aux 3 sessions (au lieu de 5), brief graphique sobre
- Implementer : câblage code, intégration assets, tests de jouabilité solo

**Livrables** : Île 2 jouable de bout en bout.

**Check-in** : 28 juillet — Reviewer audite la cohérence univers et la densité pédagogique (3 sessions restent-elles suffisantes pour les concepts C1-C5 ?).

---

## SEMAINE 3 (29 juillet → 4 août) — ÎLE 3 + CINÉMATIQUES + ÉNIGME FINALE

**Objectif** : produire l'Île 3, livrer les deux cinématiques HeyGen (D28), et construire l'énigme finale qui referme la promesse narrative (D17 tranché).

**Tâches** :
- Contenu pédagogique YAML Île 3 — 3 sessions, concepts C1-C5 déjà nommés (Voile, Révélation, Équilibre, Boussole inverse, Témoin)
- Graphique sobre Île 3 (même gabarit que Île 2)
- Câblage `pedagogie/contenu_ile3.py`
- D28 — cinématiques HeyGen : script + production des 2 vidéos courtes (ouverture avant onboarding, clôture après Île 3 avec teasing Elevation IA), intégration technique
- D17 tranché — énigme finale : conception (Architect, cohérence maïeutique — l'enfant résout, Archimède ne raconte pas) puis implémentation (Implementer). Poster/parchemin physique explicitement différé post-MVP, à ne pas coder cette semaine.
- Test informel #3 (§8.6)

**Répartition des rôles** :
- Toi + ton épouse : contenu mathématique Île 3, relecture du script des cinématiques
- Architect : conception de l'énigme finale, brief technique cinématiques, validation cohérence narrative de clôture
- Implementer : câblage Île 3, intégration vidéos HeyGen, moteur de l'énigme finale

**Livrables** : Île 3 jouable, énigme finale fonctionnelle, 2 cinématiques intégrées.

**Check-in** : 4 août — Reviewer audite le parcours complet Île 1 → Île 2 → Île 3 → énigme finale → cinématique de clôture, de bout en bout.

---

## SEMAINE 4 (5 → 11 août) — POLISH + BÊTA

**Objectif** : stabiliser l'ensemble, faire passer le test cobaye formel, corriger.

**Tâches** :
- Playtest complet des 11 sessions par l'équipe (avant le cobaye externe)
- Corrections de bugs de parcours, calibrage final des célébrations (D27)
- Vérification du pricing (19€, §8.5) — **point de vigilance Architect** : aucune tâche d'intégration paiement n'a été explicitée dans les décisions du 15 juillet. Si le lancement du 15 août doit encaisser réellement, il faut soit un dispositif minimal (lien de paiement Stripe simple, sans paywall applicatif complet) soit une vente manuelle pour la première cohorte — à trancher avec toi avant cette semaine (voir §5)
- **Test cobaye #4 (formel, bêta)** — protocole complet, cobaye si possible élargi au-delà du cercle familial (§8.6)
- Corrections issues du test bêta

**Répartition des rôles** :
- Implementer : corrections en continu
- Architect : audit pré-release, synthèse des retours bêta
- Décideur : organisation et supervision du test formel, arbitrages finaux

**Livrables** : version bêta stable ; rapport du test cobaye formel.

**Check-in** : 11 août — go/no-go pour la semaine tampon.

---

## TAMPON (12 → 15 août) — BUG FIXING + RELEASE + LANDING

**Objectif** : absorber les imprévus, livrer.

**Tâches** :
- Corrections finales issues du retour bêta
- Merge final, tag de version « Format Révision 10-15j — v1 »
- Publication de la landing page (mention Elevation IA en teasing, cohérente avec la cinématique de clôture D28)
- Marge de sécurité : si une semaine précédente a débordé, c'est ici que ça se rattrape — pas en repoussant le 15 août

**Répartition des rôles** :
- Implementer : fixes finaux, merge
- Architect : audit final
- Décideur : go/no-go de lancement, validation landing

**Livrables** : Format Révision 10-15j v1 livré et lançable pour la rentrée.

**Check-in** : 15 août — lancement.

---

## RÉCAPITULATIF DES CHECK-IN

| Date | Check-in | Porté par |
|---|---|---|
| 21 juillet | Île 1 close (100 %) + test cobaye #1 | Décideur |
| 28 juillet | Île 2 jouable | Reviewer |
| 4 août | Île 3 + énigme finale + cinématiques, parcours complet audité | Reviewer |
| 11 août | Test cobaye formel bêta passé, go/no-go tampon | Décideur |
| 15 août | Release + landing publiée | Reviewer + Décideur |

---

## 5. DÉCISIONS ENCORE OUVERTES

1. **Dispositif de paiement pour le 15 août** — le prix (19€) est tranché (§8.5), mais aucune tâche d'intégration paiement n'apparaît dans le détail S1-S4 fourni par le Décideur. Recommandation Architect : un lien de paiement simple (Stripe Payment Link ou équivalent) suffit pour cette première cohorte plutôt qu'un paywall applicatif complet — à confirmer avant S4.
2. **Nom narratif du format court** — toujours non tranché (voir master context §2).
3. **Disponibilité du cobaye élargi** pour le test formel du S4 — condition du check-in du 11 août.
4. **Script des cinématiques HeyGen** — contenu exact à rédiger conjointement (Architect + Décideur) avant le début de S3, pour ne pas bloquer la production vidéo.

---

*Roadmap Format Révision 10-15 jours — 15 juillet au 15 août 2026. v2.*
*À amender à chaque check-in si le périmètre doit être réduit (D7 révisée : jamais la date du 15 août).*
