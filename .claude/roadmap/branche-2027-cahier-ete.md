# BRANCHE 2027 — Le Cahier de Vacances 7 Semaines

**Document de mémoire, pas de plan d'exécution. Aucune urgence — ce chantier est mis en pause au profit du Format Révision 10-15 jours (voir `.claude/roadmap/roadmap-15juillet-15aout.md`).**
**v2 — mise à jour du 15 juillet 2026 suite aux décisions du Décideur : mise en pause formalisée par D25, D17 tranché pour le format court (le Scénario A/B originel reste néanmoins ouvert pour le grand format), pricing Summer Premium toujours en suspens.**

---

## CONTEXTE

Le 15 juillet 2026, le Décideur a acté **D25** : le Format Révision 10-15 jours devient la priorité d'exécution immédiate, et le chantier été 7 semaines — **Philia Summer Quest**, l'expérience narrative complète *L'Ascension des Sept Îles* — est **mis en pause**, redevenant un chantier 2027.

Ce n'est pas un abandon. C'est une mise en réserve documentée, pour qu'une reprise en 2027 ne reparte pas de zéro et ne re-décide pas ce qui a déjà été tranché. Voir `.claude/context/00-master-context.md` pour le cadrage stratégique complet des deux formats et l'architecture de marque (Philia = marque ombrelle, Elevation Mentor IA = produit annuel, Summer Quest = format été).

---

## ACTIFS PRÉSERVÉS

Rien de ce qui suit n'est perdu par le pivot. Le Format Révision 10-15j en réutilise une partie (Île 1-3, moteur technique, univers) ; le reste attend 2027 intact.

**Les 7 îles définies** (`.claude/contexts/nommage.md`) : noms, domaines mathématiques et vocabulaire de jeu (Élévateur, Cristal de Loi, Rite d'Élévation, Résurgence, Zone de Profondeur, Sceau) — architecture complète et stable pour les 7 îles, y compris les 4 non encore produites (Île 4-7).

**Narration détaillée** (`.claude/production/narration-iles.md`) : Île 1 rédigée à 100 %, Îles 2-3 à ~80 % (dont une partie sera terminée par la roadmap du format court), Îles 4-7 en esquisse identitaire (atmosphère, palette, Loi Fondamentale). Le lore complet de l'archipel — cataclysme, Sept Lois, Sanctuaire, révélation de la couronne d'Hiéron — est écrit et cohérent de bout en bout.

**Île 1 complète** : contenu pédagogique fini (`pedagogie/contenu_ile1.py`, 5 sessions, cristaux C1-C5 nommés), ancrage narratif Syracuse pur vérifié (audit + correction T8.4, 28 juin), jouable de bout en bout (avatar → carte → session → clé). Le Rite d'Élévation (« Le Jugement de la Balance », 4 Sceaux) est entièrement rédigé et vérifié mathématiquement côté Architect.

**Planches BD de l'Île 1** : la planche C1 (fille + garçon) est produite et intégrée. Les planches C2-C5 et les rites intro/fin sont en cours de complétion via la roadmap du format court (semaine 1) — 2027 en héritera si le pivot réussit.

**Le reste du socle technique et pédagogique**, indépendant du format : ADN d'Archimède, 5 modes pédagogiques et leurs prompts, SessionEngine (séquençage moteur, D6), système clés/cristaux/carte au trésor (`jeu/recompenses.py`), écrans (onboarding avatar, carte, session, modal planches BD), 8 avatars canoniques (Sassou/Mélian, D18), et l'ensemble des décisions structurantes D1-D28 tracées dans `.claude/context/00-master-context.md`.

---

## ACTIFS À PRODUIRE POUR 2027

**Contenu YAML des Îles 4, 5, 6 et 7** — c'est le chantier le plus lourd. Ces quatre îles n'ont aujourd'hui qu'une esquisse narrative (atmosphère, Loi, palette) ; aucun contenu mathématique, aucun cristal nommé (`config/constants.py` les marque « à nommer »). L'Île 6 reste en outre soumise à la décision D16 (reportée pour charge Plotly/SVG géométrie) — à reconfirmer ou révoquer selon l'état des outils en 2027.

**Production graphique complète** — la cible originale du chemin de fer V2 est de 48 à 66 images pour un MVP 3 îles ; 16 étaient produites au 17 juin 2026. Pour couvrir les 7 îles du grand format, le volume de production est bien supérieur à ce chiffre. Choix définitif de l'outil de génération d'image (Midjourney vs Firefly vs autre) toujours à documenter formellement.

**Monétisation et upsell du format long** — pricing mentionné à 29€ pour un dispositif dont le libellé exact reste à clarifier avec toi : ce terme apparaît dans les échanges du 15 juillet associé au chantier 2027, mais sans qu'il soit certain s'il désigne un concours national (mentionné dans `philia-voyage-fondateur.md` comme jalon v1.2 fin août), une révision du pricing Summer Premium (D9, actuellement 24€ et jamais implémenté), ou le carnet d'aventures imprimable. **Point de vigilance Reviewer** : à faire préciser avant de le figer dans une spec de production.

**L'expérience longue durée elle-même** — au-delà du contenu, tout ce qui fait la différence du format 7 semaines reste à construire : le carnet d'aventures imprimable (upsell 15-30€, intégration API imprimeur type Lulu Press, conçu dans `philia-voyage-fondateur.md` §14-15 mais jamais implémenté), les artefacts fonctionnels au-delà du premier, la carte du trésor enrichie complète (49 fragments), et l'ensemble du dispositif commercial (paywall Stripe, RGPD, dashboard parent, bilan hebdo) qui n'a jamais dépassé le stade de la spec.

---

## DÉCISIONS EN SUSPENS

**Scénario A/B de la révélation finale, Île 7 (D17)** — D17 a été tranché le 15 juillet, mais uniquement **pour le format court** : le secret d'Archimède se révèle désormais via une énigme finale après l'Île 3, poster physique différé. Cette décision ne répond pas à la question originelle de D17 pour le **grand format 7 îles** : le Sanctuaire, la révélation au Sommet de l'archipel après les 7 clés, et le poster/parchemin physique (actuellement différé « post-MVP » sans date) restent des éléments du format long à concevoir ou reconfirmer en 2027. Le rôle narratif de l'Île 7 elle-même — simple 7e île ou hôte dédié de la révélation — reste également à retrancher à ce moment-là.

**Monétisation Summer Premium (D9)** — actée sur le papier depuis le début du projet (24€ + tier gratuit), jamais implémentée. Le pricing 19€ du format court (D26/§8.5 du master context) ne s'y substitue pas — ce sont deux produits distincts. À retrancher pour 2027 : le prix reste-t-il à 24€, évolue-t-il (voir le « 29€ » à clarifier ci-dessus), et le dispositif technique (Stripe) est-il enfin construit.

---

## REPRISE

Reprise envisagée à l'**hiver 2026-2027**, après stabilisation d'Elevation Mentor IA (le produit annuel dont le Format Révision 10-15j est la première brique). Ce séquencement n'est pas une date gravée — contrairement à D7/D25 pour le format court, aucun jalon calendaire n'a été fixé pour la reprise du chantier été. Il dépend de la réussite du pivot et de la charge que représentera la suite d'Elevation Mentor IA à ce moment-là.

Si le Format Révision 10-15 jours est mené à bien d'ici la Toussaint 2026, la reprise 2027 ne repartira pas du point exact décrit dans ce document : Île 2 et Île 3 seront dotées d'un contenu pédagogique complet, le système de célébration (D27) aura été testé, et plusieurs cobayes réels auront donné un retour de terrain sur le mentor et l'univers. Ce document sera à mettre à jour à ce moment-là plutôt que d'être pris pour argent comptant tel quel.

---

*Branche 2027 — mémoire du chantier Cahier de Vacances 7 semaines. v2.*
*Rédigé le 15 juillet 2026, mis à jour le même jour suite aux décisions du Décideur. Pas d'urgence de mise à jour — seulement au prochain jalon du format court ou à la reprise du chantier été.*
