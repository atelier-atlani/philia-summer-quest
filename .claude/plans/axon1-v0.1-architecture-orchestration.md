# AXON-1 v0.1 — Architecture d'Orchestration Multi-IA

**Document opérationnel. Pas un manifeste théorique.**
**À utiliser tel quel pour structurer le travail sur Philia, IAXEL et tes prochains projets.**

---

## POURQUOI AXON-1 EXISTE

Tu es pluriactif : Philia (à construire), IAXEL (formateur IA agents immo), école de design (directeur pédagogique), immobilier (bailleur), famille. Le coût cognitif principal pour toi n'est pas l'absence d'idées — c'est le **switching cost** entre projets, plus le risque que tu deviennes le goulot d'étranglement de tout en tentant d'exécuter chaque tâche toi-même.

AXON-1 résout deux problèmes :

1. **Tu décides, tu n'exécutes plus.** Les IA exécutent dans des rôles bien définis. Tu valides aux points-clés.
2. **Les projets se parlent par fichiers, pas par toi.** Le copier-coller manuel entre interfaces disparaît. L'information vit dans le repo Git, lue/écrite par les agents.

C'est aussi la première brique du **moteur pédagogique propriétaire** qui va alimenter Philia, IAXEL formateur, et plus tard tes outils design et la formation adulte. Le `.claude/` partagé est l'embryon de ce qui deviendra la Mémoire 15 ans cross-vertical.

---

## LES 4 MODES OPÉRATIONNELS

Chaque mode est un rôle distinct, avec un modèle IA dédié et des livrables typés. Ce n'est pas une suggestion — c'est la règle.

### Mode 1 — ARCHITECTE
**Qui fait quoi** : conception, planification, spec produit, décisions structurelles.

- **Modèle** : Opus 4.7 (Claude.ai)
- **Quand** : début d'un nouveau projet, refonte importante, décision stratégique
- **Livrables** : documents `.md` dans `.claude/plans/`, spec produits, décisions architecturales tracées
- **Toi** : tu valides ou tu pousses-back. Ton job principal en mode Architecte est de **dire non aux mauvaises directions** avant qu'elles ne se concrétisent en code.

### Mode 2 — IMPLEMENTER
**Qui fait quoi** : codage effectif, écriture des modules, intégration des composants.

- **Modèle** : Sonnet 4.6 (Claude Code dans VS Code)
- **Quand** : phase d'exécution d'un plan Architecte
- **Livrables** : code source, tests unitaires, mise à jour de doc inline
- **Toi** : tu lis les plans avant exécution. Tu lances Claude Code avec instructions claires. Tu interviens si quelque chose dérape.

### Mode 3 — REVIEWER
**Qui fait quoi** : audit qualité, vérification cohérence, détection de dette technique avant qu'elle s'installe.

- **Modèle** : Opus 4.7 (Claude.ai, sessions ciblées)
- **Quand** : avant merge important, avant release, après un sprint de 1-2 semaines
- **Livrables** : rapport d'audit dans `.claude/reviews/`, liste d'actions correctives
- **Toi** : tu lis l'audit, tu décides ce qui passe en correction immédiate vs ce qu'on accepte comme dette

### Mode 4 — MAINTAINER
**Qui fait quoi** : tâches déterministes répétitives — mises à jour de doc, indexation, formatage, tests automatisés.

- **Modèle** : Haiku 4.5 (via API ou Claude Code)
- **Quand** : tâches récurrentes, scripts d'automatisation
- **Livrables** : scripts, docs auto-générés, indexes mis à jour
- **Toi** : tu écris les automatisations une fois, elles tournent sans toi ensuite

---

## STRUCTURE `.claude/` — À CRÉER DANS CHAQUE PROJET

À mettre à la racine de tes projets Philia, IAXEL, et tous les suivants. Versionné Git.

```
.claude/
├── README.md                  # Comment ce projet utilise AXON-1
├── context/
│   ├── project.md             # Vue d'ensemble du projet, état actuel
│   ├── decisions.md           # Log des décisions architecturales prises
│   ├── glossary.md            # Termes spécifiques au projet
│   └── templates/             # Templates de prompts standardisés (voir + bas)
│       ├── architect.md
│       ├── implementer.md
│       ├── reviewer.md
│       ├── maintainer.md
│       └── adaptation.md
├── plans/                     # Plans d'action produits par Architecte
│   ├── 2026-05-18_initial_setup.md
│   └── ...
├── reviews/                   # Rapports d'audit Reviewer
│   └── ...
├── memory/                    # Mémoire partagée cross-session
│   ├── profil_apprenant.json  # Profil utilisateur (commun aux projets pédago)
│   ├── learnings.md           # Ce qu'on a appris, à ne pas réapprendre
│   └── stack_decisions.md     # Choix techno et raisons
└── workflows/                 # Procédures opérationnelles
    ├── new_feature.md
    ├── adaptation_iaxel_to_philia.md
    └── ...
```

**Convention de nommage des fichiers de plan** : `YYYY-MM-DD_short_name.md` — la date donne l'historique chronologique sans avoir à parser le contenu.

---

## LES 5 TEMPLATES DE PROMPTS STANDARDISÉS

À mettre dans `.claude/context/templates/`. Tu colles le template dans Claude.ai ou Claude Code, tu remplaces les `[crochets]` par ton contexte. Tu obtiens un livrable typé.

### Template 1 — ARCHITECT (`architect.md`)

```
Tu es en mode ARCHITECTE pour le projet [NOM PROJET].

Contexte du projet : [résumé en 3-5 lignes ou lien vers .claude/context/project.md]

État actuel : [où on en est, ce qui marche, ce qui manque]

Demande : [ce que je veux concevoir / décider / planifier]

Contraintes :
- Temps disponible : [Xh/semaine]
- Budget : [Y€]
- Stack techno actuelle : [voir .claude/memory/stack_decisions.md]
- Non-négociables : [liste]

Livrable attendu :
1. Plan d'action structuré (étapes, durée, dépendances)
2. Décisions architecturales avec leur justification
3. Critères de succès mesurables
4. Risques identifiés et mitigations
5. Première étape concrète à exécuter immédiatement

Format : markdown, à enregistrer dans .claude/plans/[date]_[shortname].md
```

### Template 2 — IMPLEMENTER (`implementer.md`)

```
Tu es en mode IMPLEMENTER pour le projet [NOM PROJET].

Plan à exécuter : [chemin vers .claude/plans/...]

Périmètre de cette session : [section précise du plan, étape numéro X]

Stack en place :
- [Liste des modules existants relevants]
- Fichiers à modifier : [liste]
- Fichiers à créer : [liste]
- Tests à mettre à jour : [liste]

Règles d'exécution :
1. Lis d'abord le plan complet en entier
2. Pose UNE question si quelque chose est ambigu, sinon démarre
3. Implémente une étape à la fois, commit après chaque étape
4. Écris des tests unitaires pour toute nouvelle logique
5. Ne refactore PAS du code non touché par ce périmètre
6. Si tu identifies une amélioration hors-périmètre, note-la dans .claude/memory/learnings.md

À la fin :
- Récap des fichiers modifiés/créés
- Tests passés (ou non)
- Notes pour le Reviewer
```

### Template 3 — REVIEWER (`reviewer.md`)

```
Tu es en mode REVIEWER pour le projet [NOM PROJET].

Périmètre de l'audit :
- Branche/commit : [git ref]
- Fichiers concernés : [liste ou directory]
- Plan original : [chemin vers .claude/plans/...]

Critères d'audit :
1. Conformité au plan : ce qui a été fait correspond-il au plan ?
2. Qualité du code : lisibilité, modularité, naming, gestion erreurs
3. Tests : couverture, robustesse, edge cases
4. Cohérence avec l'existant : ne casse pas de patterns établis
5. Risques techniques introduits
6. Dette technique acceptable ou non

Livrable :
Rapport markdown dans .claude/reviews/[date]_[shortname].md avec :
- Verdict : APPROUVÉ / À CORRIGER / À REFAIRE
- Liste des points à corriger par sévérité (BLOCKER / MAJOR / MINOR)
- Décisions à acter (toi en tant que fondateur)
```

### Template 4 — MAINTAINER (`maintainer.md`)

```
Tu es en mode MAINTAINER pour le projet [NOM PROJET].

Tâche : [tâche déterministe précise — indexation, mise à jour de doc, formatage, génération de tests, etc.]

Périmètre : [fichiers/dossiers concernés]

Procédure :
1. [Étape 1]
2. [Étape 2]
3. [...]

Output attendu :
- [fichiers à produire/modifier]
- Log d'exécution dans .claude/memory/maintainer_log.md

Règle : pas de jugement, pas de refactor créatif. Exécution stricte.
```

### Template 5 — ADAPTATION (`adaptation.md`)

C'est le template clé pour ton cas Philia, qui est une adaptation pédagogique d'IAXEL formateur.

```
Tu es en mode ARCHITECTE pour une ADAPTATION CROSS-PROJET.

Projet source : [NOM, état actuel, ce qu'il fait]
Projet cible : [NOM, ce qu'il doit faire]

Différences clés (ADN à préserver vs ADN à modifier) :
- À PRÉSERVER : [liste des composants/architectures qui marchent et restent]
- À MODIFIER : [liste des composants à adapter au nouveau contexte]
- À AJOUTER : [nouveaux composants nécessaires]
- À RETIRER : [composants source non pertinents]

Stack source : [résumé technique]
Contraintes cible : [budget, temps, audience]

Livrable :
1. Inventaire des modules réutilisables (file mapping source → cible)
2. Liste des modifications par module (effort estimé en jours)
3. Liste des nouveaux modules à créer (effort estimé)
4. Plan d'exécution séquencé (semaine par semaine)
5. Risques d'adaptation et mitigations
6. Premier module à attaquer en mode Implementer

Format : markdown dans .claude/plans/adaptation_[source]_to_[cible].md
```

---

## LE WORKFLOW STANDARD — DU PLAN À L'EXÉCUTION

### Phase A — Architecte (Claude.ai, toi présent)

Tu ouvres une session Claude.ai. Tu colles le template Architecte avec ton contexte. Claude produit un plan dans `.claude/plans/[date]_[shortname].md`.

**Tu pousses-back ce plan jusqu'à ce qu'il soit propre.** Pas par perfectionnisme — par survie. Un plan mauvais te coûtera 10× son temps en correction en aval.

Tu valides. Le plan devient le contrat.

### Phase B — Implementer (Claude Code dans VS Code, autonomie)

Tu ouvres Claude Code. Tu lui pointes le plan validé via le template Implementer. Tu lui laisses faire son travail en autonomie.

**Tu n'écris pas le code.** Tu lis ce qui sort, tu testes, tu pousses-back si quelque chose ne va pas. Tu commits à chaque étape franchie.

Si Claude Code bloque ou diverge → tu interromps, tu corrige le plan ou le template, tu relances. **Tu ne codes pas la solution à sa place.**

### Phase C — Reviewer (Claude.ai, audit ponctuel)

À la fin d'une étape majeure (1-2 semaines de travail Implementer), tu ouvres une session Claude.ai en mode Reviewer. Tu pointes la branche, le plan, les fichiers modifiés.

Tu reçois un rapport d'audit. Tu décides : on accepte / on corrige immédiatement / on note comme dette.

### Phase D — Maintainer (script automatisé)

Les tâches répétitives (réindexation, regen doc, tests) sont automatisées par scripts Haiku. Tu les lances en CRON ou en pre-commit hook. Ils tournent sans toi.

---

## APPLICATION IMMÉDIATE — PHILIA SUMMER QUEST EN ADAPTATION D'IAXEL FORMATEUR

Le cas concret. Étapes en J+1 à J+5 pour démarrer AXON-1 sur Philia.

### J+1 (2h) — Création de la structure

1. Tu crées un nouveau repo `philia/` (ou tu travailles dans un sous-dossier d'IAXEL si tu préfères pour l'instant)
2. Tu crées la structure `.claude/` complète selon ce document
3. Tu copies les 5 templates dans `.claude/context/templates/`
4. Tu remplis `.claude/context/project.md` avec une vue d'ensemble Philia
5. Tu remplis `.claude/memory/stack_decisions.md` avec la stack d'IAXEL (RAG FAISS, TTS ElevenLabs, Streamlit, etc.)

### J+2 (3-4h) — Session Architecte sur l'adaptation

Tu ouvres Claude.ai. Tu utilises le **Template Adaptation** avec :
- Source : IAXEL formateur (architecture détaillée que tu m'as donnée)
- Cible : Philia Summer Quest (spec produit dans la conversation actuelle)
- À préserver : RAG, TTS+cache, state-machine, profil utilisateur, quiz YAML, PDF export, scoring IA
- À modifier : RAG (immo → maths), prompts (formateur → mentor maïeutique), interface (formateur pro → enfant ludique)
- À ajouter : avatar évolutif (8-10 expressions + unlocks), cognitive radar, mur des victoires, parent reports, 3 tiers de paywall, contest leaderboard
- À retirer : roleplay WhatsApp (pas pertinent enfants), modules marché immo

Claude produit un plan détaillé d'adaptation dans `.claude/plans/2026-05-19_adaptation_iaxel_to_philia.md`

Tu pousses-back jusqu'à ce que le plan soit shippable en 4 semaines (deadline 15 juillet pour ouverture programme été).

### J+3 (1-2h) — Validation et découpage

Tu lis le plan. Tu valides ou tu demandes des ajustements. Une fois validé, tu découpes en sprints d'1 semaine chacun.

Pour chaque sprint, tu prépares un **brief Implementer** dans `.claude/plans/sprint_1.md`, `sprint_2.md`, etc. Chaque brief liste les modules à modifier/créer pour cette semaine.

### J+4 et suivants — Mode Implementer en Claude Code

Tu ouvres Claude Code dans VS Code sur le repo `philia/`. Pour le sprint 1, tu colles le Template Implementer avec le brief sprint_1.md. Tu laisses Claude Code travailler.

Tu commits à chaque étape. Tu ne codes pas toi-même.

### À la fin de chaque sprint (1 fois/semaine, 1h)

Mode Reviewer. Audit. Décisions correctives ou dette acceptée.

---

## LE PONT ENTRE TES PROJETS — `.claude/memory/profil_apprenant.json`

Le fichier le plus stratégique de ton écosystème.

Schéma proposé (à raffiner) :

```json
{
  "id": "user_12345",
  "profil_cognitif": {
    "style_apprentissage": "visuel|kinesthésique|verbal",
    "tolérance_ambiguïté": "haute|moyenne|basse",
    "rythme": "rapide|moyen|lent"
  },
  "profil_motivationnel": {
    "moteurs_principaux": ["compétition", "maîtrise", "...]",
    "démotivateurs": ["peur_échec", "..."]
  },
  "profil_émotionnel": {
    "patterns_anxieté": [...],
    "patterns_récupération": [...]
  },
  "domaines_actifs": {
    "philia_summer_2026": {
      "concepts_maitrisés": ["fractions_simples", "..."],
      "concepts_en_cours": ["calcul_littéral", "..."],
      "concepts_à_revoir": ["nombres_relatifs", "..."]
    },
    "iaxel_formation_immo": {
      "modules_complétés": ["marché_local", "..."],
      "lacunes": ["estimation_complexe", "..."]
    }
  },
  "passions_personnelles": ["football", "manga", "..."],
  "historique_jalons": [
    {"date": "2026-07-01", "événement": "Démarrage Philia Summer", "contexte": "..."}
  ]
}
```

C'est ce fichier qui rend Philia et IAXEL (et plus tard tes outils design, formation adulte) **un seul mentor** plutôt que des produits séparés. Le même user a une mémoire continue cross-projet.

Dès Philia v1, ce fichier vit dans `.claude/memory/`. Quand on migre vers Neo4j en Phase 2 d'architecture, on le passe en graphe — mais la structure logique reste la même.

---

## CE QUE TU FAIS, CE QUE TU NE FAIS PLUS

### Tu fais (Mode Décideur)
- Validation des plans Architecte
- Décisions de design produit
- Pédagogie (le savoir métier)
- Conversations clients/parents
- Choix stratégiques (pricing, scope, calendrier)
- Push-back sur les sorties IA quand elles dérivent

### Tu ne fais plus (Mode Exécutant)
- Écriture de code de A à Z
- Production de copy marketing à la chaîne (→ Grok)
- Rédaction de doc générique (→ Maintainer Haiku)
- Tests manuels répétitifs (→ scripts)
- Indexation, formatage, tâches déterministes

**Cette réorganisation te libère 10-15h/semaine sans toucher à ta charge prof ou immo.** C'est cette libération qui rend Philia Summer Quest livrable pour le 1er juillet, et ouvre la voie à Philia Full pour septembre/octobre.

---

## LIMITES ACTUELLES DE AXON-1 v0.1

Honnête sur ce qu'il faut accepter :

1. **Pas de communication temps réel entre instances Claude.** Le pont reste asynchrone (par fichiers). Cowork améliorera la fluidité mais pas en mai 2026.

2. **Tu restes le superviseur unique.** AXON-1 ne te remplace pas — il démultiplie ton temps utile. Si tu disparais 2 semaines sans supervision, le système dérive.

3. **Cowork pas indispensable mais accélérateur.** En v0.1 on fonctionne en répertoire Git + copier-coller des plans dans Claude.ai. Quand tu maîtrises Cowork, on passe en v0.2 plus fluide.

4. **Le profil apprenant cross-projet existe mais n'est pas encore agentique.** En v0.1 c'est juste un fichier JSON partagé. La "vraie" Mémoire 15 ans avec inférences automatiques cross-vertical est un objectif v1.0 (probable Q4 2026 ou plus tard).

5. **Les modèles Opus 4.7 / Sonnet 4.6 / Haiku 4.5 ont des coûts d'API.** Pour les usages Architecte/Reviewer en Claude.ai, c'est inclus dans ton abonnement. Pour les usages Implementer en Claude Code ou Maintainer en API, ce sont des appels facturés. Budget mensuel à prévoir : 50-200€ selon volume.

---

## PROCHAINE ÉTAPE CONCRÈTE

Une fois ce document lu, deux livrables possibles selon ton choix :

**Option A** : je produis maintenant le contenu de `.claude/context/project.md` et `.claude/memory/stack_decisions.md` pour le projet Philia, prêts à copier dans ton repo. Plus le brief Architecte d'adaptation IAXEL → Philia, prêt à coller dans Claude.ai.

**Option B** : tu fais d'abord ton tour du document, tu poses tes questions, tu adaptes aux contraintes que tu vois. Puis on raffine ensemble la v0.2 avant de matérialiser dans tes repos.

Mon avis hardcore : Option A. La théorie sans application meurt. Le document AXON-1 v0.1 prend toute sa valeur quand tu commences à l'utiliser sur Philia dès demain.

---

*Document AXON-1 v0.1 — première matérialisation de l'orchestration multi-IA pour ton écosystème.*
*À versionner dans `.claude/` de chaque projet, à raffiner par usage réel.*
