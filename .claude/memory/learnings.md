# Learnings — Philia Summer Quest

## Sprint 2

### Détection automatique de réussite d'un exercice — reportée Sprint 3

`exercice_suivant()` dans `SessionEngine` est déclenché **explicitement** par l'appelant (bouton UI ou signal externe). L'engine ne détecte pas automatiquement qu'un enfant a réussi un exercice — cela nécessiterait d'analyser la réponse du LLM pour en extraire un signal de validation, ce qui relève du structured output ou d'un second appel LLM.

**À implémenter Sprint 3** : parser la sortie d'Archimède pour détecter les signaux de réussite ("Voilà, tu l'as trouvé", validation Feynman réussie) et déclencher `exercice_suivant()` automatiquement. Piste : structured output Anthropic ou second LLM call léger (Haiku) en juge de réussite.

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

Apprentissage — vigilance Git sur les fichiers déposés manuellement.
Quand l'Architecte produit un document que le fondateur dépose dans le repo, vérifier explicitement avec Claude Code que git add a bien été fait. Sinon le document reste sur disque mais hors Git. Cette dette s'est accumulée silencieusement pendant le Sprint 2 (les 3 prompts d'Archimède, le document Voyage, le brief Sprint 2, l'audit Sprint 1 étaient hors Git pendant plusieurs jours). Règle opérationnelle : faire git status à la fin de chaque session de travail, pas seulement avant les commits prévus.

Question d'architecture identifiée — refonte du RAG
Le RAG actuel (FAISS sur data/sources_maths/) est plus une dette qu'un actif :

Contenu source sale (433 fichiers, doublons, exercices résolus mélangés aux cours)
Largement redondant avec le format YAML enrichi des exercices
Pas de séparation claire entre "contenu programme" (rigueur factuelle) et "univers narratif" (contextualisation Syracuse/Archimède)

Trois options à trancher dans une session dédiée :

Option A : nettoyer le RAG actuel (1-2 jours)
Option B : RAG double couche (Référentiel Mathématique + Univers Narratif) — prépare Philia Année (3-5 jours)
Option C : suppression du RAG, tout via YAML + prompts enrichis (1 jour)

À traiter au Sprint 3 ou Sprint 4. Décision pédagogique à prendre en cohérence avec la règle "le YAML coud, le LLM brode".