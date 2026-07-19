# Learnings — Philia Summer Quest

---

## Sprint 1

### Tâche 1 — Smoke test fork IAXEL (2026-05-25)

**Résultat : OK**

- Python 3.9 (système macOS Darwin 24.2.0)
- venv créé dans `.venv/`
- `pip install -r requirements.txt` → OK (tous les packages installés)
- Tous les imports de `app.py` résolus sans erreur
- `streamlit run app.py` → HTTP 200 sur port 8502

**Sans clés API valides** : l'app se lance, l'UI s'affiche, mais :
- Les appels OpenAI (LLM, TTS) échouent au runtime (clé placeholder)
- Les appels ElevenLabs idem
- L'index FAISS est recréé à chaque démarrage (fichier `faiss_index.bin` présent)

**Observation hors périmètre Sprint 1** :
- Après l'archivage (Tâche 2), `app.py` cassera sur les imports `training.marche_module`, `training.whatsapp_ui`, etc. → à corriger au Sprint 2 lors de la refonte de `app.py`.

---

## Apprentissages Sprint 2 — à intégrer au Sprint 3

### 1. Le questionnement de relance doit être MULTIMODAL, pas généraliste

Quand l'enfant bloque, Archimède reformule en restant dans le même canal
(verbal abstrait). Or la méthode de Singapour (concret → pictural →
abstrait) doit être utilisée comme grille de relance : changer de
canal, pas reformuler.

Quatre canaux à exploiter :
- verbal abstrait (la question pleine)
- verbal concret (analogie, exemple tiré du monde de l'enfant)
- visuel (description d'un schéma à imaginer, ou schéma affiché)
- manipulation (pliage, comptage avec les doigts, dessin demandé)

À traiter au Sprint 3 : enrichir les prompts (mode_decouverte d'abord),
et enrichir le format YAML des exercices avec des relances
multimodales pré-écrites.

### 2. Le visuel est absent — trou architectural

Plusieurs exercices supposent un schéma (Île 1 Session 1 ex.3 et ex.4,
et toute l'Île 6 Géométrie). L'app n'affiche aucun visuel aujourd'hui.
Archimède le décrit verbalement faute de mieux.

À traiter au Sprint 3 : ajouter un champ `visuel:` au format YAML
(chemin SVG), enrichir l'écran de session pour afficher l'image quand
elle existe, produire les SVG nécessaires (chantier visuel à
planifier avec ma femme, peut-être avec aide graphique externe).

### 3. La validation immédiate des bonnes réponses

Quand l'enfant donne la bonne réponse du premier coup, Archimède
ne valide pas — il creuse le sens. C'est de la maïeutique exigeante,
mais peut frustrer un enfant qui a juste. À calibrer : valider d'abord
("oui, c'est bien ça"), puis creuser ("et tu peux m'expliquer pourquoi ?").

À traiter au Sprint 3 : retoucher le prompt mode_decouverte sur
l'accueil de la bonne réponse.

## Session Voyage / Cahier d'Aventures — 2026-06-01

### 4. Le principe "Le YAML coud, le LLM brode"

Le contenu mathématique est intégralement pré-validé par les humains (fondateur et son épouse) avant d'entrer dans le système. Le LLM n'a jamais accès à la création de contenu mathématique : il habille narrativement du contenu pré-existant. Formulé : **le YAML coud, le LLM brode**.

**Ne jamais laisser le LLM inventer de la mathématique.** En cas de doute sur un exercice ou une solution, c'est le fichier YAML validé qui fait autorité, pas la génération du LLM.

### 5. Le scope MVP révisé : 3 îles au 1er juillet

Le périmètre du MVP 1er juillet est confirmé à **3 îles seulement** :
- Îles 1-3 → MVP 1er juillet
- Îles 4-5 → v1.1 mi-juillet
- Îles 6-7 → v1.2 août

Ne pas tenter d'accélérer pour intégrer plus d'îles au MVP. Si dérapage, on réduit le scope, jamais la date.

### 6. Le triple système de récompense — mécanique psychologique calibrée

Trois niveaux de récompense, intentionnellement distincts par fréquence et poids :
- **Clé** (1 par île, hebdomadaire) — grosse victoire, récompense de maîtrise complète d'une île
- **Fragment de carte** (quotidien) — petite victoire fréquente, maintient l'engagement jour après jour
- **Artefact fonctionnel** (ponctuel) — récompense de capacité, marque l'acquisition d'un superpouvoir

Ce calibrage est intentionnel et psychologiquement fondé. Ne pas le simplifier (ex. : fusionner les trois en un seul système) sous prétexte de simplification technique.

### 7. Vigilance Git sur les fichiers déposés manuellement

Quand l'Architecte produit un document que le fondateur dépose dans le repo, vérifier explicitement avec Claude Code que git add a bien été fait. Sinon le document reste sur disque mais hors Git. Cette dette s'est accumulée silencieusement pendant le Sprint 2 (les 3 prompts d'Archimède, le document Voyage, le brief Sprint 2, l'audit Sprint 1 étaient hors Git pendant plusieurs jours). Règle opérationnelle : faire git status à la fin de chaque session de travail, pas seulement avant les commits prévus.

### 8. Détection automatique de réussite d'un exercice — reportée Sprint 3

`exercice_suivant()` dans `SessionEngine` est déclenché **explicitement** par l'appelant (bouton UI ou signal externe). L'engine ne détecte pas automatiquement qu'un enfant a réussi un exercice — cela nécessiterait d'analyser la réponse du LLM pour en extraire un signal de validation, ce qui relève du structured output ou d'un second appel LLM.

**À implémenter Sprint 3** : parser la sortie d'Archimède pour détecter les signaux de réussite ("Voilà, tu l'as trouvé", validation Feynman réussie) et déclencher `exercice_suivant()` automatiquement. Piste : structured output Anthropic ou second LLM call léger (Haiku) en juge de réussite.

### 9. Question d'architecture — refonte du RAG

Le RAG actuel (FAISS sur data/sources_maths/) est plus une dette qu'un actif :

- Contenu source sale (433 fichiers, doublons, exercices résolus mélangés aux cours)
- Largement redondant avec le format YAML enrichi des exercices
- Pas de séparation claire entre "contenu programme" (rigueur factuelle) et "univers narratif" (contextualisation Syracuse/Archimède)

Trois options à trancher dans une session dédiée :

- Option A : nettoyer le RAG actuel (1-2 jours)
- Option B : RAG double couche (Référentiel Mathématique + Univers Narratif) — prépare Philia Année (3-5 jours)
- Option C : suppression du RAG, tout via YAML + prompts enrichis (1 jour)

Statut : tranché au Sprint 3. Voir D13 dans decisions.md pour le détail.

---

## Sprint 3

### 1. Application contextuelle des apprentissages Sprint 2 dans les 5 modes (2026-06-07)

Les deux règles issues du Sprint 2 (relance multimodale 4 canaux + calibration accueil bonnes réponses) s'appliquent différemment selon le mode :

- **Mode Découverte** : calibration accueil bonnes réponses présente (validation Feynman finale). Relance multimodale partiellement présente (le mode est lui-même structuré en Concret → Pictural → Abstrait, ce qui réalise un parcours multimodal naturel).
- **Mode Pratique** : les deux règles sont pleinement intégrées (c'est le mode principal d'application).
- **Mode Validation** : la calibration accueil bonnes réponses se transforme en "valider sans ambiguïté" quand la zone floue est éclairée. La relance multimodale n'est pas pertinente — on ne relance pas un exercice, on creuse une zone floue.
- **Mode Consolidation** : la calibration est implicite (validation rapide + question suivante). La relance multimodale est remplacée par les "indices de récupération" qui sont l'équivalent fonctionnel pour ce mode.
- **Mode Bilan** : les deux règles ne sont pas pertinentes — on ne fait pas résoudre, on fait réfléchir sur sa façon d'apprendre.

Cette application contextuelle est délibérée et défendable : chaque mode a sa propre mécanique, et les règles d'un mode ne doivent pas polluer les autres. Note à conserver pour éviter qu'une future revue les ajoute à tort dans Validation/Consolidation/Bilan.
test 16/07
Fragilité UX carte : le mécanisme <a href="?ile=..."> de ecran_carte.py 
fonctionne au clic souris mais pas en test automatisé Playwright headless. 
Détecté T8.5 (15 juillet). Non-régression, dette héritée. À traiter en 
sprint polish si test cobaye confirme problème.
---

## Sprint 3 (suite) — 16 juillet 2026

### Pattern émergent — mécanismes « marqués faits » sans câblage final dans le vrai flux

Cinquième occurrence cette semaine du même type de bug latent : un mécanisme est implémenté, testé unitairement ou via une app de démo isolée (`app_test_X.py`), puis considéré « livré » — mais jamais réellement câblé dans le parcours de jeu réel. Occurrences : Mode Bilan (T4), écran avatar (T6), système clés/cristaux (T7, `jeu/recompenses.py` jamais appelé hors `app_test_recompenses.py`), progression inter-sessions (découverte pendant l'audit préalable de T8.6 — `ecran_session.py` reste bloqué sur la Session 1 de toute île), et un cas de structure de commit incomplète.

**Règle Reviewer ajoutée** : pour toute tâche qui livre un mécanisme nouveau (récompense, transition d'état, persistance), exiger un test de bout en bout en contexte réel — le vrai parcours de l'app, pas une app de démo isolée — avant de considérer la tâche « livrée ». Un test unitaire ou une démo standalone qui passe ne prouve pas que le mécanisme est atteint depuis le vrai flux. Vérifier l'état en base après action UI, pas seulement le rendu à l'écran.

---

## Sprint 3 T8.6 — 15 juillet 2026 soir

### Pattern : bypass API pour tests d'UI

**Contexte** : test Brique 3 T8.6 (célébration fin d'île) a crashé sur « credit balance too low » alors que le test ne nécessite pas de vrai chat.

**Cause** : Claude Code testait l'UI de célébration en lançant Streamlit avec `app.py` complet, qui appelle l'API Anthropic dès la première session pour le mentor Archimède.

**Correctif** : tout test d'UI qui ne concerne pas le chat maïeutique doit bypasser l'API :
- Soit script de test isolé qui appelle directement les fonctions UI avec état forcé
- Soit forçage direct en base SQLite pour atteindre l'état souhaité sans passer par les sessions
- Soit mock API en mode dev (via variable d'environnement)

**Règle** : ne jamais dépenser de crédits API pour un test d'interface. Les crédits API sont réservés aux tests de qualité du mentor.

À cadrer ultérieurement : un ticket dédié « T-Cobaye » pourrait formaliser les tests qui consomment de vrais crédits API (validation qualité mentor Archimède, fidélité maïeutique, ancrage narratif via dialogue réel). Distinct des tests d'UI sans API. Reporté post-MVP.
