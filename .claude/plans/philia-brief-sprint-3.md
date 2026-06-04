# PHILIA SUMMER QUEST — Brief Sprint 3

**Sprint 3 du MVP. Le sprint le plus structurant du calendrier 1er juillet.**
**Durée : 4 jours pleins (mercredi → lundi).**
**Objectif : faire passer Philia d'un mentor conversant à un Voyage visuel et incarné.**

---

## NOTE D'USAGE

Ce brief découpe le Sprint 3 en 8 tâches calibrées sur 4 journées de travail concentré du fondateur (environ 25-30h au total), plus du travail parallèle de l'épouse sur le contenu pédagogique. Chaque tâche a un objectif, des livrables, des critères de validation, et un temps estimé.

Pour chaque tâche : le fondateur lance, Cowork exécute (ou Claude Code selon la nature), le fondateur valide par revue, on commit, on enchaîne.

Le sprint est dense mais réalisable à condition de respecter le séquençage. Ne pas mélanger les tâches, ne pas commencer T8 avant que T7 soit validée, ne pas démarrer la production de planches BD sans les visuels prérequis.

---

## CONTEXTE DU SPRINT

### Ce qui est en place au démarrage (Sprint 2 + sessions de conception)

- ADN d'Archimède (`.claude/contexts/philia-adn-archimede.md`)
- Document fondateur Voyage / Cahier d'Aventures (`.claude/contexts/philia-voyage-fondateur.md`)
- Mode Découverte opérationnel (`prompts/mentor/mode_decouverte.txt`)
- Mentor Python câblé
- Île 1 contenu complet au format Sprint 2 (33 exercices)
- 9 avatars validés dans `assets/mentor/v2-syracuse/`
- Repo propre, Cowork opérationnel
- Bilan structurel et mémoire projet à jour

### Ce que le Sprint 3 doit livrer (engagement)

- Les 5 modes pédagogiques opérationnels
- Multimodalité de relance intégrée dans les prompts
- Calibration accueil bonnes réponses
- Décision RAG actée et exécutée
- Hygiène du repo (archivage scripts IAXEL résiduels, README à jour, bilan structurel aligné Voyage)
- Système des clés et de la carte du trésor enrichie fonctionnel
- Écran de la Carte de l'Archipel opérationnel
- Écran de Choix d'Avatar opérationnel
- Premier prototype de planche BD intégrée à une session pédagogique
- Test E2E du parcours complet

### Hors scope du Sprint 3 (reporté Sprints 4-6)

- Voix TTS aux moments-clés (Sprint 4)
- Paywall Stripe et RGPD (Sprint 4)
- Dashboard parent et bilan PDF hebdo (Sprint 5)
- Contenu Îles 2 et 3 finalisé (Sprint 5)
- Stress test et soft launch (Sprint 6)

---

## RÉPARTITION DES JOURNÉES

| Jour | Tâches | Volume |
|---|---|---|
| Mercredi | T1 Bascule Cowork code, T2 Hygiène repo, T3 RAG + mode Pratique | journée pleine |
| Samedi | T4 Les 3 derniers modes, T5 Écran Carte de l'Archipel | journée pleine |
| Dimanche | T6 Écran Choix d'Avatar, T7 Système clés + carte du trésor | journée pleine |
| Lundi | T8 Prototype planche BD + Test E2E | journée pleine |

En parallèle, par l'épouse : enrichissement Île 1 au format multimodal.

---

## LES 8 TÂCHES — DÉTAIL

### TÂCHE 1 — Bascule Cowork pour la production de code (mercredi, 1h)

Confirmer que Cowork peut modifier des fichiers Python (`prompts/`, `pedagogie/`) sans rupture de style. Si tout va bien, Cowork devient l'outil principal du Sprint 3. Le terminal Mac reste l'outil de commit.

Test : demander à Cowork d'ajouter un commentaire à `pedagogie/mentor.py` puis l'annuler. Vérifier le diff propre.

### TÂCHE 2 — Hygiène du repo (mercredi, 2h)

Régler les dettes Important de l'audit de la veille :
1. Archiver les scripts IAXEL résiduels racine + dans `scripts/`
2. Archiver `core/faq_contract.py` (orphelin)
3. Vérifier `core/avatar.py` et `core/sanitizer.py`
4. Mettre à jour le README.md (stack actuelle, Sprint 2 fini, mention du Voyage)
5. Mettre à jour les sections obsolètes du bilan structurel (§3.4 et §N8 — terminologie Voyage)

Commit : `chore: hygiène repo — archivage scripts IAXEL, README actualisé, bilan structurel aligné Voyage`

### TÂCHE 3 — Décision RAG + mode Pratique (mercredi, 3-4h)

**Partie A — Décision RAG**

Recommandation Architecte : Option C (suppression du RAG). Le test maïeutique du Sprint 2 a montré qu'Archimède dialogue correctement sans RAG. Le YAML enrichi suffit. Le RAG actuel ralentit chaque tour de 200-500ms sans apport.

Exécution si validé : modifier `pedagogie/mentor.py` pour ne plus appeler `core/rag.py`. Archiver `core/rag.py`, `scripts/build_rag_index.py`, `data/rag_index/`, `data/sources_maths/` vers `_archive_iaxel/`.

**Partie B — Rédaction de `prompts/mentor/mode_pratique.txt`**

Structure : attitude Polya en 4 phases (comprendre, planifier, exécuter, vérifier), avec la règle de relance multimodale (4 canaux) et la calibration accueil bonnes réponses intégrées.

Commit : `feat: mode Pratique opérationnel + décision RAG actée (Option C)`

### TÂCHE 4 — Les 3 derniers modes mentor (samedi matin, 3h)

Rédaction de `mode_validation.txt` (Feynman), `mode_consolidation.txt` (active recall), `mode_bilan.txt` (métacognition).

Chaque prompt inclut : relance multimodale, calibration bonnes réponses, ancrage narratif Voyage, format de sortie standard.

Commit : `feat: les 4 modes pédagogiques manquants opérationnels`

### TÂCHE 5 — Écran Carte de l'Archipel (samedi après-midi, 4h)

1. Préparation visuelle : image de fond carte parchemin, positions des 7 îles, états (verrouillée / accessible / conquise)
2. Implémentation de `ui/ecran_carte.py` : affichage, indicateur de position, porte-clés en sidebar, gestion des clics

Critère : l'enfant ouvre Philia, voit la carte, peut cliquer sur l'île accessible.

Commit : `feat: écran Carte de l'Archipel opérationnel`

### TÂCHE 6 — Écran de Choix d'Avatar (dimanche matin, 3h)

1. Préparation des assets (sélection des variantes de référence pour les 8 avatars, recadrage uniforme)
2. Création de `ui/onboarding.py` : légende fondatrice → grille 4×2 des avatars → choix → accueil par Archimède → entrée sur la carte

Commit : `feat: écran de choix d'avatar + onboarding narratif Voyage`

### TÂCHE 7 — Système clés + carte du trésor + artefacts (dimanche après-midi, 4h)

1. `jeu/cles.py` : modèle 7 clés, fonctions d'attribution et de listage
2. `jeu/carte_tresor.py` : modèle 49 fragments, persistance SQLite (nouvelle table)
3. `jeu/artefacts.py` : modèle 5 artefacts, conditions de déblocage. Pour le MVP : 1 seul artefact débloquable

Pas de visuel raffiné dans cette tâche, juste la mécanique fonctionnelle.

Commit : `feat: système des clés, fragments et artefacts (mécanique fonctionnelle)`

### TÂCHE 8 — Prototype planche BD Session 1 Île 1 (lundi, 6-7h)

LE pari du Sprint 3. Une vraie planche BD intégrée à une session pédagogique.

**Matin (3h) : Production de la planche**
1. Découpage scénaristique en 8 cases (1h)
2. Génération des cases via Midjourney avec `--sref` cohérent (1h30)
3. Composition de la planche (30 min)

**Après-midi (3-4h) : Intégration et test E2E**
4. Modifier `ui/ecran_session.py` pour afficher la planche au-dessus/autour du chat (2h)
5. Test E2E complet : onboarding → choix avatar → carte → session avec planche BD (1-2h)

Critère : la planche s'affiche, est belle, raconte la session, ne gêne pas le dialogue maïeutique.

Commit : `feat: prototype planche BD Session 1 Île 1 — preuve de concept Voyage`

---

## TÂCHE PARALLÈLE — ENRICHISSEMENT ÎLE 1 MULTIMODAL (épouse)

Sur les 4 jours, ~1 journée de travail étalée. Pour chaque exercice de l'Île 1 :
- Ajouter le champ `visuel:` quand pertinent
- Enrichir les indices en 4 canaux : leger (verbal abstrait), moyen (verbal concret), fort (visuel), manipulation (action physique)
- Si possible, démarrer l'Île 2

---

## RISQUES ET MITIGATIONS

| Risque | Mitigation |
|---|---|
| La planche BD du lundi ne s'intègre pas bien | Fallback : planche affichée séparément (image cliquable). Forme moins élégante mais intention préservée. |
| Décision RAG casse quelque chose | Tests E2E après modification. Rollback possible (RAG archivé, pas supprimé). |
| Épouse ne peut pas livrer le contenu multimodal | Pas bloquant pour le Sprint 3. Reporté en début Sprint 4. |
| Cowork rencontre problèmes Git | Workflow acté : Cowork modifie, terminal Mac commit. |
| Fatigue sur 4 jours pleins | Pauses entre tâches. Pas de travail tard le soir. |

---

## CRITÈRES DE RÉUSSITE DU SPRINT 3

À la fin du sprint (lundi soir), répondre OUI à :

1. Les 5 modes pédagogiques sont opérationnels ?
2. La décision RAG est exécutée et l'app tourne ?
3. Le repo est propre ?
4. Un enfant peut démarrer Philia, voir la légende, choisir un avatar, voir la carte ?
5. Le système des clés et des fragments est fonctionnel ?
6. Une session pédagogique se déroule sous forme de planche BD partiellement ?
7. Le test E2E complet tourne sans erreur ?

Si OUI à 6/7 minimum, le Sprint 3 est validé.

---

## EN SORTIE DU SPRINT 3

Un produit qui ressemble à Philia. Pas complet (3 îles, pas 7), pas commercial (Sprint 4), mais identifiable comme Philia :
- Univers Syracuse antique incarné
- Avatar de l'enfant
- Mentor Archimède maïeutique aux 5 modes
- Carte de l'archipel visible
- Premières mécaniques de récompense
- Premier prototype de planche BD

C'est la preuve de concept du Voyage. Sprints 4-6 = industrialiser, raffiner, commercialiser.

---

*Brief Sprint 3 Philia Summer Quest — calibré 4 jours pleins.*
*À déposer dans `.claude/plans/philia-brief-sprint-3.md` au démarrage du sprint.*
*Co-conçu entre le fondateur et l'Architecte — 3 juin 2026.*
