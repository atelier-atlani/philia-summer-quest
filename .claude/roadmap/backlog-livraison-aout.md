# BACKLOG DE LIVRAISON — AOÛT 2026

**Document de pilotage vivant. Capture l'état du backlog au 5 août 2026 (deadline MVP : 15 août 2026, Île 1 seule — D42).**
**À cocher/mettre à jour au fil des sessions, pas à réécrire de zéro.**

---

## RÈGLES DE TÊTE — À LIRE AVANT TOUTE REPRISE

**Re-test cobaye avant d'enrichir davantage.** Deux grosses journées d'enrichissement Île 1 (énigme, carte-fragment, collection, tableau de bord) ont eu lieu les 4-5 août. Avant d'ajouter quoi que ce soit de plus, il faut savoir si ce qui est construit répond déjà au désir de gamification exprimé par les cobayes. Deviner coûte plus cher que tester.

**D7 reconduite : on réduit le périmètre, jamais la date.** Le risque au 5 août n'est plus l'absence de contenu — c'est de perfectionner une île qui ne sort pas. À un moment, il faut arrêter d'enrichir, figer, livrer.

---

## A — CORRECTIONS À FAIRE AVANT COBAYE (bloquantes ou quasi)

- [ ] **A1. Contenu des coffres dans le tableau de bord** — Afficher « X objets » sous chaque coffre gagné : « Sens d'une fraction — 5 pierres ». Données déjà existantes (libelle_objet + nombre d'exercices). Petit, prêt à lancer (brief déjà rédigé).
- [ ] **A2. Corrections de mise en page** (audit Décideur initial) — à grouper en un seul passage Claude Code :
  - Images BD trop petites → agrandir / dézoomer pour voir l'image entière
  - Chat non inséré dans l'image → agencement (pas de bulle dessinée dans l'image, composant Streamlit)
  - Texte narratif en bulle/bandeau → composant CSS, pas image générée
- [ ] **A3. RGPD email (D44)** — Consentement parent dans le tunnel d'achat : case distincte, non pré-cochée, finalité + désinscription mentionnées. 3 lignes, requis dès le MVP.

## B — DÉCISIONS OUVERTES (Décideur)

- [ ] **B1. Prix de l'île unique** (D42 laissé ouvert) — 19€ portait sur 3 îles, à réviser pour 1 île. Repères : pas 19÷3 (valeur perçue, pas prorata), « limite de rentabilité » unitaire non pertinente (coût marginal quasi nul). À geler avant lancement.

**Statut au 5 août : ouverte, non tranchée.**

## C — AMÉLIORATIONS SOUHAITÉES (à arbitrer contre la deadline)

- [ ] **C1. Vue isométrique de l'Île 1 en pop-up** (clic vignette → agrandissement) — techniquement simple (st.dialog, pattern connu). Bloqué par : l'asset « vue iso Île 1 » existe-t-il ? Si oui, petite tâche. Si non, à produire d'abord.
- [ ] **C2. Feedback visuel renforcé au gain d'objet** (« +1 pierre » plus visible) — le toast natif Streamlit est sobre, pas de style custom possible. Option : micro-animation CSS locale sur le compteur (objet qui saute/grossit). Pas de ballons (casse la hiérarchie de célébration, déjà retirés — D41). Pas de son (chantier disproportionné + agaçant). Faisable maintenant que le compteur est à sa place définitive (sidebar, D48) — sinon post-cobaye.

## D — POST-MVP (D47, déjà tracé — NE PAS FAIRE avant le 15 août)

- Mini-carte animée avec émoticône qui se déplace sur les sessions
- Son réel (« ding » audio)
- Système de cartes mémoire complet (D46)
- Détection automatique de réussite d'exercice
- Persistance de la carte-fragment
- Versions réduites des assets 2 Mo (perf)

---

## VÉRIFICATIONS EN ATTENTE

- [ ] **Re-test cobaye avec toutes les corrections** (clôture, repère, collection, tableau de bord) — priorité haute. C'est le retour cobaye qui valide si le désir de gamification est comblé, et qui pilote la suite (A2/C1/C2 à arbitrer selon ce retour).

---

## POINT CALENDRIER

5 août, deadline 15 août. Deux grosses journées d'enrichissement Île 1 (énigme, carte, collection, tableau de bord) déjà faites. Reste : A1-A3 (corrections), B1 (prix), re-test cobaye. Le risque n'est plus le manque de contenu — c'est de perfectionner une île qui ne sort pas.

---

## ORDRE RECOMMANDÉ POUR LA REPRISE

1. **D48 à Cowork** (trace, ne pas perdre) — fait, voir `.claude/memory/decisions.md`.
2. **A1** (contenu coffres) — petit, ferme la boucle collection.
3. **Re-test cobaye avec l'existant** — avant d'en ajouter plus.
4. **Selon retour cobaye** : A2 (mise en page) + C1/C2 si réclamés.
5. **A3** (RGPD) + **B1** (prix) — avant de pouvoir vendre.
6. **Passe de validation finale → livraison.**

---

*Backlog de livraison Philia Summer Quest — Île 1, MVP 15 août 2026.*
*Origine : récap session du 5 août 2026. À tenir à jour à chaque session de travail.*
