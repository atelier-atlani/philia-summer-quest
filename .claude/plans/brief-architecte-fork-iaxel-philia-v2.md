# BRIEF ARCHITECTE v2.0 — Fork IAXEL → Philia Summer Quest

**Document à coller dans une session Claude.ai neuve (modèle Opus 4.7).**
**Sortie attendue : plan détaillé d'adaptation, à enregistrer dans `.claude/plans/2026-05-19_fork_iaxel_to_philia.md`**

**Différences vs v1.0** : 
- IAXEL est un code base figé qu'on fork (et non un produit en mouvement à adapter)
- Intégration des mécaniques produit issues du brainstorm Grok (Mentor Évolutif, radar 6 superpouvoirs, etc.)
- Stack confirmée : Streamlit (même que IAXEL, zéro migration tech)

---

## INSTRUCTIONS POUR L'IA RECEVEUSE

Copie-colle exactement ce qui suit dans une session Claude.ai neuve. Pas de préambule, pas de mise en bouche conversationnelle.

---

```
Tu es en mode ARCHITECTE pour un FORK DE CODE et adaptation pédagogique.

CONTEXTE GÉNÉRAL

Je suis fondateur d'un écosystème de produits éducatifs IA. J'ai un produit 
existant en production (IAXEL formateur, agent IA pour formation d'agents 
immobiliers) actuellement en phase de test terrain en agences immobilières.

Je veux forker le code base IAXEL pour créer un nouveau produit (Philia Summer 
Quest, mentor IA pour enfants de 6e révisant les maths l'été 2026). Le fork 
sera totalement indépendant : aucune coexistence avec IAXEL en prod, je peux 
casser ce que je veux dans le fork.

Objectif : maximiser la réutilisation du code IAXEL éprouvé, minimiser le 
temps de mise sur marché, intégrer les spécificités pédagogiques et UX de 
Philia.

CONTRAINTE CALENDAIRE CRITIQUE
- Date du brief : 19 mai 2026
- Date d'ouverture inscriptions Philia Summer : 1er juillet 2026
- Démarrage programme : 1er juillet 2026
- Soit 6 semaines de build effectif (19 mai → 30 juin)

STACK TECHNIQUE
Streamlit + Python conservé tel quel (pas de migration vers Next.js ou autre).
J'ai déjà la stack IAXEL en production qui fonctionne bien :
- Streamlit (UI)
- FAISS (RAG)
- ElevenLabs API + cache MD5 TTS
- Anthropic/OpenAI API
- fpdf2 (PDF)
- YAML pour données structurées

==========================================
SECTION 1 — INVENTAIRE COMPLET DU CODE BASE IAXEL À FORKER
==========================================

agent-immo-formateur/
├── app.py                          # Application Streamlit principale
├── agent_formateur.py              # Agent IA (FAQ, Formateur, Audit)
├── requirements.txt
│
├── config/
│   └── constants.py                # Constantes (avatars, couleurs, limites)
│
├── core/
│   ├── rag.py                      # FAISS RAG (production éprouvée)
│   ├── faq_contract.py             # Contrat FAQ
│   ├── tts.py                      # Text-to-speech + cache MD5 ElevenLabs
│   └── sanitizer.py                # Nettoyage inputs
│
├── training/
│   ├── engine.py                   # TrainingSession (state machine)
│   ├── steps.py                    # Enum steps + séquences Jour 1/2+
│   ├── progress.py                 # Load/save progress.json + lacunes
│   ├── profile.py                  # Profil utilisateur
│   ├── profile_ui.py               # UI onboarding
│   ├── adapters.py                 # Adaptation difficulté/ton
│   ├── content.py                  # 20 thèmes rotation
│   ├── quiz.py                     # Quiz engine
│   ├── quiz_ui.py                  # UI quiz Kahoot-style
│   ├── whatsapp.py                 # Roleplay WhatsApp (immo)
│   ├── whatsapp_ui.py              # UI WhatsApp
│   ├── synthesis.py                # Synthèse IA session
│   ├── pdf_export.py               # Export PDF (fpdf2)
│   ├── formateur_messages.py       # Messages formateur guidés
│   ├── chat_libre.py               # Chat questions libres
│   ├── marche_module.py            # Runner mini-cours marché
│   │
│   ├── quiz_bank/                  # 39 questions YAML structurées
│   ├── whatsapp/scenarios/         # Scénarios WhatsApp YAML (immo)
│   └── modules/marche/             # 100 modules marché immo + tests
│
├── prompts/
│   ├── prompt_formateur.txt
│   └── prompt_audit_v2.txt
│
├── scripts/
│   ├── check_before_merge.sh
│   ├── tests_contract_faq.py
│   ├── index_marche_modules.py
│   └── run_ia_tests.py
│
├── data/
│   ├── progress.json
│   ├── base_connaissances.json     # 339 entrées RAG immobilier
│   ├── rag_index/                  # Index FAISS
│   └── tts_cache/                  # Cache audio TTS
│
└── assets/
    ├── logo_iaxel.png
    ├── images/IAXEL-formateur.png
    └── videos/, sounds/

CARACTÉRISTIQUES TECHNIQUES CLÉS DE IAXEL
- Stack mature et éprouvée en production
- Cache TTS MD5 : économie 70-90% des appels ElevenLabs
- Scoring IA automatique pour évaluation des réponses
- State machine claire pour parcours utilisateur
- Profil utilisateur + lacunes persistantes (progress.json)
- Adapters de difficulté et ton selon profil
- Quiz et scénarios en format YAML structuré
- Export PDF des bilans
- Tests pre-commit scriptés

==========================================
SECTION 2 — SPECIFICATION PRODUIT PHILIA SUMMER QUEST
==========================================

BRAND ET POSITIONNEMENT

Marque mère : Philia (du grec φιλία, amour entre amis et amour qui poursuit 
la sagesse — racine de philosophie). Mentor cognitif IA pour enfants, 
ambition d'écosystème pédagogique multi-décennies (Philia Summer, Philia 
Année Scolaire, futur Philia Pro, Philia Studio).

Produit actuel : Philia Summer Quest 2026 (édition été)
Tagline : "Découvre la 5e avant la 5e, par des jeux mathématiques."

Promesse produit : 7 semaines de jeux mathématiques pour solidifier ce que 
l'enfant a vu en 6e, attaquer les notions les plus complexes, et explorer le 
programme de 5e en avant-première. L'enfant arrive à la rentrée avec une 
longueur d'avance.

AUDIENCE
- Enfants 11-12 ans (sortie de 6e, entrée 5e)
- Parents CSP+ acheteurs payeurs (38-49 ans, métropoles France)
- Défiance modérée envers l'Éducation Nationale, non militante

MODÈLE COMMERCIAL — 3 TIERS

Tier 1 — Quest Gratuit : 0€
- 6 missions découvertes (1/semaine)
- Mentor évolutif basique (silhouette + 4-5 éléments déblocables)
- Avatar évolutif visuel statique
- Radar des 6 Superpouvoirs Cognitifs basique
- Mur des Victoires limité

Tier 2 — Summer Premium : 24€ (early bird 19,80€ jusqu'au 15 juillet)
- Accès illimité 7 semaines, tous les modes pédagogiques
- Mentor évolutif complet (toute la garde-robe et accessoires)
- Voix ElevenLabs aux moments-clés (correction, récap, encouragement, 
  célébration) — pas de voix continue, 2-3 moments par session
- Rapports parents hebdomadaires automatiques (PDF + email)
- Certificat de fin de programme
- Badges complets (10-12 badges signifiants)
- Bilan émotionnel hebdomadaire
- Quête d'Héritage (conseil de l'enfant à son moi de septembre)
- Collection d'Analogies personnelles

Tier 3 — Quest Premium + Concours : 29€ (early bird 23,30€)
- Tout le tier 2
- Participation au Défi Philia Été 2026 (contest national)
- Leaderboard contest (visible uniquement pour ce tier)
- Chance de gagner : 1 abonnement Philia Année à vie / 1 an gratuit / 6 mois 
  gratuit (top 1, top 10, top 100)
- Épreuve finale 30 août en ligne
- Live finale streamée

SCOPE PÉDAGOGIQUE — 5 CORE + 2 STRETCH

CORE 1 — Fractions
- Consolidation 6e : comprendre, comparer, fractions équivalentes
- Introduction 5e : additionner/soustraire fractions de même dénominateur

CORE 2 — Proportionnalité et pourcentages
- Consolidation 6e : tableaux, échelles, vitesses
- Introduction 5e : pourcentages formalisés, situations contextualisées

CORE 3 — Calcul littéral (chapitre stratégique)
- Introduction 6e : lettres pour nombres, calcul avec inconnue
- Formalisation 5e : substitution, expressions simples, simplification

CORE 4 — Géométrie et aires
- Consolidation 6e : rectangle, carré, cercle, triangle
- Introduction 5e : triangles, parallélogrammes, trapèzes

CORE 5 — Nombres relatifs (introduction pure 5e)
- Concept nouveau pour l'élève
- Effet "wahou" pour le parent : l'enfant arrive en 5e en sachant déjà ce 
  qu'est un nombre négatif

STRETCH 1 — Symétries
- Consolidation 6e (axiale) + introduction 5e (centrale)

STRETCH 2 — Statistiques et lecture de données
- Transversal, ludique, facile à pédagogiser

ARCHITECTURE PÉDAGOGIQUE — 5 MODES + INFUSION SPIRALAIRE

L'agent prof IA opère selon 5 modes opérationnels avec attitudes distinctes :

Mode 1 — DÉCOUVERTE (introduction d'un nouveau concept)
- Attitude : curieux, ouvert, "tiens, regardons ça ensemble"
- Méthode : maïeutique pure + progression concret → pictural → abstrait

Mode 2 — PRATIQUE (résolution d'exercices)
- Attitude : méthodique, structurant, "comment on attaque ça ?"
- Méthode : Polya en 4 phases (comprendre, planifier, exécuter, vérifier)

Mode 3 — VALIDATION (vérifier la profondeur)
- Attitude : bienveillant exigeant, "explique-moi ça comme à ton petit frère"
- Méthode : technique Feynman

Mode 4 — CONSOLIDATION (révision active)
- Attitude : ludique, joueur, "on fait le défi du jour ?"
- Méthode : active recall + spaced repetition + interleaving

Mode 5 — BILAN (métacognition explicite)
- Attitude : réflexif, "qu'est-ce qui marche pour toi ?"
- Méthode : métacognition explicite

Principe permanent — INFUSION SPIRALAIRE
- Curriculum spiralaire (Bruner)
- Interleaving (mélanger les types de problèmes)
- Cross-curricular embedding (maths dans physique, histoire-géo, vie courante)

L'enfant ne voit jamais les 5 modes. Il voit un mentor cohérent qui s'adapte 
intuitivement. L'agent bascule entre modes selon des règles claires.

GUARDRAILS PÉDAGOGIQUES NON-NÉGOCIABLES

- Maïeutique pure : ne JAMAIS donner la réponse directement
- Toujours guider par questions socratiques
- Tolérance erreur ZÉRO sur ce point — l'agent doit refuser même si l'enfant 
  insiste pour avoir la réponse
- Si l'enfant bloque vraiment : décomposer la question, pas répondre
- Détection fatigue : si l'enfant donne signes de saturation, le mentor 
  propose une pause au lieu de continuer

==========================================
SECTION 3 — MÉCANIQUES PRODUIT SPÉCIFIQUES PHILIA
==========================================

MÉCANIQUE CENTRALE — LE MENTOR ÉVOLUTIF

L'enfant ne joue pas un avatar : il fait grandir SON mentor au fil du Summer Quest.

Démarrage : le mentor est une silhouette simple (8 styles de base au choix : 
explorateur, scientifique, ingénieur, architecte, artiste, philosophe, 
sportif, naturaliste).

Évolution progressive par déblocages :
- 70% de bonnes réponses cumulées sur 5 sessions → tenue spécifique débloquée
- 5 réflexions métacognitives fortes (mode Bilan) → accessoire "lunettes 
  Visionnaire"
- Complétion d'une semaine sans fatigue détectée → aura lumineuse
- Maîtrise complète d'un chapitre → compagnon de quête qui suit le mentor
- Réussite défi hebdomadaire → costume thématique de la semaine
- Top 10 leaderboard (tier Concours uniquement) → halo de champion
- Défi créatif réussi → accessoire unique créé par l'enfant

Niveaux du mentor :
- Niveau 1 : Jeune Guide (début du programme)
- Niveau 2 : Mentor Confirmé (mi-programme)
- Niveau 3 : Grand Sage Mathématique (fin de programme)

SYSTÈME D'EXPRESSIONS — 10 ILLUSTRATIONS

10 illustrations principales du mentor selon état émotionnel :
1. Neutre / Calme (état par défaut)
2. Sourire doux (encouragement léger)
3. Grand sourire fier (victoire)
4. Concentré / Pensif (réflexion en cours)
5. Surpris / "Oh intéressant !" (réponse créative)
6. Bienveillant exigeant (sourcil levé, "tu peux mieux")
7. Célébration / Joie explosive (milestone)
8. Doux / Réconfort (après erreur ou fatigue)
9. Inspiré / Brillant (idée créative)
10. Sage / Mentor accompli (fin du quest)

Mécanique : chaque session accumule des "Émotions Débloquées". 
Bilan hebdomadaire : "Cette semaine, ton mentor t'a souri 12 fois, a été 
surpris 4 fois par tes idées, et t'a encouragé 8 fois."

RADAR DES 6 SUPERPOUVOIRS COGNITIFS

Visualisation centrale du Profil Mentor (matérialisation visuelle du Profil 
en 7 dimensions de la spec pédagogique).

Les 6 superpouvoirs et leur progression :
1. Maîtrise Maïeutique (capacité à se poser des questions soi-même)
2. Transfert / Analogies (utiliser un concept dans un autre contexte)
3. Persévérance (ne pas abandonner face à un blocage)
4. Clarté d'Explication (Feynman — expliquer simplement)
5. Créativité Mathématique (inventer des problèmes, des solutions)
6. Métacognition (comprendre comment on apprend)

Niveaux : Débutant → Apprenti → Maître → Légende
Radar visible en permanence sur l'écran d'accueil.

BADGES SIGNIFIANTS (10-12 MAXIMUM SUR L'ÉTÉ)

Badges chargés de sens, pas juste "j'ai fini 10 exercices" :
- Harmoniste (excellence géométrie)
- Stratège Polya (excellence résolution de problèmes)
- Visionnaire Spiralaire (excellence transferts)
- Architecte du Doute (excellence questions métacognitives)
- Compagnon du Mentor (assiduité)
- ...etc.

Chaque badge déclenche une réflexion : "Comment as-tu réussi ça ?"

QUÊTE D'HÉRITAGE (pont vers Philia Année Scolaire)

À la fin du Summer Quest, l'enfant écrit un conseil à son "moi de septembre".
- Le conseil est stocké dans le profil utilisateur
- Le mentor le ressort à la rentrée si l'enfant convertit en Philia Année
- Mécanisme de conversion émotionnelle puissant

JAUGE D'ÉNERGIE DU MENTOR (anti-fatigue)

Le mentor a une "énergie" qui descend si l'enfant fait trop de sessions 
longues d'affilée. À basse énergie, le mentor propose une pause naturellement.
Anti-fatigue par game design, pas par interruption autoritaire.

COLLECTION D'ANALOGIES PERSONNELLES

L'enfant débloque des analogies personnelles par chapitre :
- "Les fractions = découper une pizza avec tes amis"
- "Les pourcentages = la part de chocolat dans une mousse"
- Etc.

Ces analogies persistent dans la mémoire long terme du mentor (Profil 
Mentor) et sont rappelées dans les sessions futures pour Infusion Spiralaire.

NARRATIVE — VOYAGE DU SUMMER QUEST

L'enfant est un "Apprenti Élevé" qui part en quête pour devenir 
"Maître Élevé" ou "Architecte du Savoir".

Chaque semaine = un nouveau chapitre du voyage :
- Semaine 1 : Traversée des Fractions
- Semaine 2 : Cité des Proportions
- Semaine 3 : Forteresse du Calcul Littéral
- Semaine 4 : Royaume des Aires
- Semaine 5 : Vallée des Nombres Relatifs
- Semaine 6 : Symétries Miroir (stretch)
- Semaine 7 : Pic des Statistiques (stretch)

Boss de fin de semaine renommé "Épreuve du Maître" (sortir du vocabulaire 
gaming pur pour rester premium).

BILAN PARENT HEBDOMADAIRE

Email + PDF automatique chaque dimanche soir :
- Ce que l'enfant a appris cette semaine
- Bilan émotionnel ("votre enfant a connu 3 moments 'Brillant' cette semaine")
- Difficultés détectées et stratégie du mentor pour les adresser
- Conseil aux parents (soutenir sans donner les réponses)
- Aperçu de la semaine à venir

==========================================
SECTION 4 — LIVRABLE ATTENDU DE LA SESSION ARCHITECTE
==========================================

Produis un plan d'adaptation détaillé en markdown avec les sections suivantes :

1. PROCÉDURE DE FORK INITIAL (jour 1-2)
   Étapes git précises pour forker IAXEL en projet philia/ indépendant :
   - Commandes git de fork
   - Renommage repository, namespace, imports
   - Premier commit "fork point"
   - Vérification que le code IAXEL forké tourne en l'état (smoke test)
   - Mise en place de .claude/ selon AXON-1 v0.1

2. INVENTAIRE DES MODULES IAXEL ET LEUR DESTIN POUR PHILIA
   Tableau exhaustif :
   | Module IAXEL | Destin | Effort (jours) | Notes |
   où Destin = "Conserver tel quel" / "Adapter" / "Refondre" / "Supprimer"
   
   Pour chaque "Adapter" ou "Refondre", explique :
   - Ce qui change précisément
   - Ce qui est conservé
   - Effort détaillé

3. NOUVEAUX MODULES À CRÉER POUR PHILIA
   Liste exhaustive des modules sans équivalent dans IAXEL :
   - mentor_evolutif.py (avatar + déblocages)
   - radar_superpouvoirs.py (visualisation + tracking)
   - mur_victoires.py (achievements)
   - quete_heritage.py (conseil moi-de-septembre)
   - bilan_emotionnel.py (compteur expressions hebdo)
   - collection_analogies.py (analogies par enfant)
   - voyage_narratif.py (chapitres semaines)
   - jauge_energie.py (anti-fatigue)
   - parent_dashboard.py (interface parent)
   - bilan_parent_hebdo.py (email + PDF)
   - paywall.py (3 tiers + Stripe)
   - contest.py (leaderboard + épreuve finale)
   - rgpd_consent.py (consentement parental < 15 ans)
   - ...etc.
   
   Pour chaque : effort estimé en jours, priorité P0/P1/P2, dépendances.

4. ARCHITECTURE DES PROMPTS PHILIA (REFONTE INTÉGRALE vs IAXEL)
   IAXEL utilise prompt_formateur.txt (formateur expert). 
   Philia doit utiliser des prompts mentor maïeutique.
   
   Livrable : squelette de prompts pour chaque mode pédagogique :
   - prompts/mentor_decouverte.txt
   - prompts/mentor_pratique.txt
   - prompts/mentor_validation.txt
   - prompts/mentor_consolidation.txt
   - prompts/mentor_bilan.txt
   - prompts/mentor_meta_router.txt (qui choisit le mode)
   
   Chaque prompt doit encoder :
   - L'attitude visible
   - La méthode pédagogique
   - Les guardrails (jamais donner la réponse)
   - La relation à l'avatar (quelle expression déclencher quand)
   - La relation au radar (quel superpouvoir activer)

5. STRUCTURE DES DONNÉES YAML POUR PHILIA
   IAXEL a YAML pour quiz et scénarios WhatsApp. 
   Philia doit avoir YAML pour :
   - chapters/ (un fichier par chapitre core/stretch)
   - sessions/ (séquences de 15-20 min)
   - exercises/ (exercices par niveau de difficulté)
   - weekly_challenges/ (défis hebdomadaires)
   - contest_final/ (épreuve 30 août)
   - unlocks/ (conditions de déblocage avatar)
   - badges/ (10-12 badges signifiants)
   
   Pour chaque type, propose le schéma YAML structuré complet avec exemple.

6. ADAPTATION DU RAG
   - Création de data/base_connaissances_maths.json (équivalent des 339 entrées 
     immo mais sur les maths 6e-5e)
   - Reindexation FAISS
   - Sources de contenu : programme officiel + supports pédagogiques + 
     exemples concrets de maïeutique en maths
   - Estimation du nombre d'entrées RAG nécessaires pour couvrir 5 chapitres
   - Procédure pour générer ce contenu (manual / IA-assisted / mix)

7. PLAN D'EXÉCUTION SÉQUENCÉ EN 6 SPRINTS
   Découpe en 6 sprints d'une semaine chacun :
   
   Sprint 1 (19-25 mai) — Setup + smoke test
   - Fork IAXEL, mise en place .claude/, smoke test
   - Premier prompt mentor maïeutique en remplacement formateur
   - RAG basique sur 1 chapitre (fractions)
   - Test E2E : une session maïeutique sur fractions fonctionne
   
   Sprint 2 (26 mai - 1er juin) — Architecture pédagogique 5 modes
   - Implémentation des 5 modes opérationnels
   - Router méta (choix du mode)
   - Premier mode (Découverte) fonctionnel sur chapitre Fractions
   
   Sprint 3 (2-8 juin) — Mentor évolutif + radar
   - 10 expressions du mentor (intégration illustrations)
   - Mécanique de déblocage avatar
   - Radar 6 superpouvoirs visible
   - Mur des victoires basique
   
   Sprint 4 (9-15 juin) — Voix + paywall
   - Intégration voix ElevenLabs aux moments-clés (réutilisation cache TTS)
   - Implémentation 3 tiers Stripe
   - RGPD consentement parental
   - Test paiement E2E
   
   Sprint 5 (16-22 juin) — Tous chapitres + dashboard parent
   - Contenu pédagogique complet 5 chapitres core
   - Stretch 1 si temps disponible
   - Dashboard parent + bilan hebdo automatique
   - Quête d'Héritage
   
   Sprint 6 (23-30 juin) — Contest + finitions + lancement
   - Mécanique contest (leaderboard, inscription tier 29€)
   - Tests d'acceptance
   - Stress test infrastructure (200-2000 utilisateurs)
   - Préparation ouverture 1er juillet
   
   Pour chaque sprint : livrables précis, tests de validation, risque de 
   glissement et mitigation.

8. RISQUES TECHNIQUES ET MITIGATIONS
   Top 5 risques :
   - Délai serré 6 semaines
   - Coût ElevenLabs imprévu (à monitorer par cache)
   - Complexité mentor évolutif (à scopiser : commencer simple)
   - Conformité RGPD enfants < 15 ans
   - Stress du contest leaderboard si beaucoup d'utilisateurs simultanés
   
   Pour chaque : impact, probabilité, mitigation concrète.

9. PREMIER MODULE À ATTAQUER EN MODE IMPLEMENTER
   Le premier livrable précis du sprint 1 :
   - Fichiers à créer/modifier
   - Spec détaillée
   - Critères d'acceptance
   - Estimé : 1-2 jours

FORMAT ATTENDU

Markdown structuré. Décisions claires, efforts chiffrés en jours, sprints 
découpés en livrables testables.

CONTRAINTES NON-NÉGOCIABLES

- Maïeutique pure : Philia ne donne JAMAIS la réponse
- 1er juillet : date d'ouverture inscriptions
- Mentor évolutif : différenciateur produit majeur, à intégrer dès sprint 3
- Radar 6 superpouvoirs : visualisation centrale, dès sprint 3
- Voix Premium aux moments-clés : sprint 4
- RGPD < 15 ans : dès sprint 4 (avant tout paiement)
- Réutiliser au maximum IAXEL : ne pas refonder ce qui marche

QUESTIONS QUE TU PEUX ME POSER AVANT DE PRODUIRE LE PLAN

Si tu identifies des ambiguïtés ou trade-offs majeurs, pose-moi 1-3 questions 
précises avant de produire le plan complet. Sinon, produis directement.
```

---

## NOTES POUR TOI (HORS BRIEF)

**Ce que ce brief va déclencher** : 
Claude.ai en mode Architecte va probablement te poser quelques questions de clarification (sur les illustrations à produire, sur le contenu RAG maths à sourcer, sur les détails du paywall Stripe). Tu réponds, puis il produit le plan complet.

**Tu enregistres le plan** dans `.claude/plans/2026-05-19_fork_iaxel_to_philia.md`.

**Tu reviens vers moi** quand :
- Le plan est produit pour audit Reviewer
- Tu veux raffiner le brief avant relance
- Tu veux que je structure le sprint 1 en détail pour le briefing Claude Code

---

## PROCHAINS LIVRABLES QUE JE PRÉPARE EN PARALLÈLE

Pendant que tu lances cette session Claude.ai, je prépare :

1. **project.md** pour le repo Philia — vue d'ensemble, brand, audience, pédagogie, business model, état du projet
2. **stack_decisions.md** — choix techniques consolidés et raisons
3. **glossary.md** — termes spécifiques au projet (mentor évolutif, superpouvoirs, modes pédagogiques, etc.)

Tu n'as qu'à me dire "lance" et je te livre ces 3 fichiers dans la foulée — prêts à copier dans `.claude/context/` de ton repo Philia.

---

*Brief Architecte d'adaptation IAXEL→Philia v2.0 — prêt à coller.*
*À utiliser dans une session Claude.ai neuve, modèle Opus 4.7.*
