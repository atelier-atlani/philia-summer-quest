# BRIEF ARCHITECTE — Adaptation IAXEL Formateur → Philia Summer Quest

**Document à coller dans une session Claude.ai neuve (modèle Opus 4.7).**
**Sortie attendue : plan détaillé d'adaptation, à enregistrer dans `.claude/plans/2026-05-19_adaptation_iaxel_to_philia.md`**

---

## INSTRUCTIONS POUR L'IA RECEVEUSE

Copie-colle exactement ce qui suit dans une session Claude.ai neuve. Pas de préambule, pas de mise en bouche conversationnelle — c'est un brief technique structuré.

---

```
Tu es en mode ARCHITECTE pour une ADAPTATION CROSS-PROJET.

CONTEXTE GÉNÉRAL

Je suis fondateur d'un écosystème de produits éducatifs propulsés par IA. 
J'ai un produit existant en production (IAXEL formateur, agent IA pour formation 
d'agents immobiliers) que je veux adapter pour créer un nouveau produit 
(Philia Summer Quest, mentor IA pour enfants de 6e révisant les maths l'été).

Les deux produits partagent une architecture pédagogique commune mais ciblent 
des audiences et matières radicalement différentes. L'objectif est de maximiser 
la réutilisation de code et minimiser le temps de mise sur marché.

Contrainte calendaire critique : livraison de Philia Summer Quest pour le 
1er juillet 2026. Date du brief : 19 mai 2026. Soit 6 semaines de build effectif.

PROJET SOURCE — IAXEL FORMATEUR

Architecture existante en production (Streamlit + Python) :

agent-immo-formateur/
├── app.py                          # Application Streamlit principale
├── agent_formateur.py              # Agent IA (FAQ, Formateur, Audit)
├── requirements.txt
│
├── config/
│   └── constants.py                # Constantes (avatars, couleurs, limites)
│
├── core/
│   ├── rag.py                      # FAISS RAG (production, ne pas modifier)
│   ├── faq_contract.py             # Contrat FAQ (production, ne pas modifier)
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
│   ├── quiz_ui.py                  # UI quiz Kahoot
│   ├── whatsapp.py                 # Roleplay WhatsApp + débrief
│   ├── whatsapp_ui.py              # UI WhatsApp
│   ├── synthesis.py                # Synthèse IA session
│   ├── pdf_export.py               # Export PDF (fpdf2)
│   ├── formateur_messages.py       # Messages formateur guidés
│   ├── chat_libre.py               # Chat questions libres
│   ├── marche_module.py            # Runner mini-cours marché
│   │
│   ├── quiz_bank/                  # 39 questions YAML structurées
│   ├── whatsapp/scenarios/         # Scénarios WhatsApp YAML
│   └── modules/marche/             # Mini-cours marché (100 modules MD + tests YAML)
│
├── prompts/
│   ├── prompt_formateur.txt        # Prompt formateur terrain
│   └── prompt_audit_v2.txt         # Prompt audit
│
├── scripts/
│   ├── check_before_merge.sh       # Tests obligatoires pre-commit
│   ├── tests_contract_faq.py       # Tests FAQ contract
│   ├── index_marche_modules.py     # Indexation 100 modules marché
│   └── run_ia_tests.py             # Exécution tests scoring IA
│
├── data/
│   ├── progress.json
│   ├── base_connaissances.json     # 339 entrées RAG (immobilier)
│   ├── rag_index/                  # Index FAISS
│   └── tts_cache/                  # Cache audio TTS (économie ElevenLabs)
│
└── assets/
    ├── logo_iaxel.png
    ├── images/IAXEL-formateur.png  # Avatar formateur statique
    └── videos/, sounds/

Caractéristiques techniques clés :
- Stack : Streamlit, Python, FAISS, ElevenLabs API, OpenAI/Anthropic API
- Cache TTS MD5 : économise 70-90% des appels ElevenLabs
- Scoring IA automatique pour évaluation des réponses
- State machine claire pour le parcours utilisateur
- Profil utilisateur + lacunes persistantes (progress.json)
- Adapters de difficulté et ton selon profil
- Quiz et scénarios en format YAML structuré
- Export PDF des bilans

Architecture pédagogique sous-jacente : 
- Formateur expert sur thème (immobilier)
- Sessions de 1h/jour structurées
- Mix entre cours, quiz, roleplay, chat libre
- Adaptation à la progression de l'apprenant

PROJET CIBLE — PHILIA SUMMER QUEST

Mentor IA pour enfants de 11-12 ans, programme de révision/découverte 
mathématiques 6e→5e sur 7 semaines durant l'été 2026.

Branding : Philia (du grec φιλία, amour entre amis et amour qui poursuit la 
sagesse — racine de philosophie). Marque mère de l'écosystème, "Quest" pour 
le format estival ludique.

Promesse produit : "Découvre la 5e avant la 5e, par des jeux mathématiques. 
Solidifie ton 6e, attaque les concepts les plus complexes, prends de l'avance 
sur le programme de 5e."

Audience : 
- Enfants 11-12 ans (élèves de 6e, sortant de 6e)
- Parents CSP+ de ces enfants (acheteurs payeurs)
- France métropolitaine, métropoles et grandes périphéries

Modèle commercial (3 tiers) :
- Quest Gratuit : 0€ — 6 missions découvertes (1/semaine) + avatar évolutif basique
- Summer Premium : 24€ (early bird 19,80€) — accès illimité 7 semaines, tous modes, 
  voix aux moments-clés, rapports parents, certificat, badges complets
- Quest Premium + Concours : 29€ (early bird 23,30€) — Premium + participation 
  au Défi Philia Été 2026 (contest national avec dotations en abonnements)

Scope pédagogique (5 chapitres core + 2 stretch) :
- CORE 1 : Fractions (consolidation 6e + intro 5e additions/soustractions)
- CORE 2 : Proportionnalité et pourcentages (consolidation 6e + intro 5e formelle)
- CORE 3 : Calcul littéral (intro 6e + formalisation 5e — chapitre stratégique)
- CORE 4 : Géométrie et aires (consolidation 6e + intro triangles/parallélogrammes 5e)
- CORE 5 : Nombres relatifs (introduction pure 5e, nouveauté absolue)
- STRETCH 1 : Symétries (axiale 6e → centrale 5e)
- STRETCH 2 : Statistiques et lecture de données

Pédagogie : maïeutique pure (ne jamais donner la réponse, guider par questions), 
Infusion Spiralaire (les concepts antérieurs réapparaissent dans des contextes 
nouveaux), méthode Polya pour résolution de problèmes, technique Feynman pour 
validation de compréhension.

Spécificité produit majeure — AVATAR ÉVOLUTIF :
L'enfant choisit son avatar de base parmi 6-8 options (silhouette, vêtements, 
accessoire). À chaque accomplissement (4 sourires en série, 1 figure surprise, 
maîtrise d'un chapitre, réussite défi hebdo, top 10 leaderboard), l'enfant 
débloque progressivement des éléments visuels qui s'ajoutent à son avatar.
Avatar = visualisation tangible de la progression cognitive de l'enfant.
8-10 expressions statiques disponibles (content, concentré, encourageant, 
surpris, fier, pensif, joueur, satisfait) qui changent en réaction aux 
réponses de l'enfant.

USAGE DE LA VOIX (ElevenLabs) :
- Tier Gratuit : pas de voix
- Tiers Premium : voix uniquement aux moments-clés (correction d'exercice raté, 
  récap fin de session, encouragement après blocage, célébration milestone). 
  Pas de voix permanente — 2-3 moments par session, ~30 secondes chacun.
  Économie : ~0,30-0,50€/session ElevenLabs par utilisateur payant.

MÉCANIQUES PRODUIT SPÉCIFIQUES :
- Système de quest narratif (parcours sur une carte ou un voyage thématique)
- Radar des compétences cognitives (visualisation Profil Mentor light)
- Mur des Victoires (achievements visuels)
- Feedback instantané riche (expressions avatar, animations légères CSS, sons)
- Rapports parents hebdomadaires automatiques (PDF + email)
- Certificats fin de programme (PDF)
- Leaderboard contest (pour tier Premium+Concours uniquement)

DIFFÉRENCES KEY AVEC IAXEL :
- Audience enfant (11-12 ans) au lieu d'adulte professionnel
- Matière maths au lieu d'immobilier
- Format ludique au lieu d'autoritaire-pro
- Sessions courtes 15-20 min au lieu de 1h
- Avatar évolutif gamifié au lieu d'avatar statique professionnel
- Pas de roleplay WhatsApp (pas pertinent pour enfants)
- Voix ponctuelle au lieu de voix systématique
- 3 tiers de paywall au lieu de modèle B2B/licence
- Système contest avec leaderboard public

LIVRABLE ATTENDU

Produis un plan d'adaptation détaillé en markdown avec les sections suivantes :

1. INVENTAIRE DES MODULES IAXEL ET LEUR DESTIN
   Tableau pour chaque module IAXEL existant :
   | Module IAXEL | Destin pour Philia | Effort estimé (jours) |
   où Destin = "Réutiliser tel quel" / "Adapter" / "Refondre" / "Retirer"
   
   Pour chaque "Adapter" ou "Refondre", explique ce qui change et pourquoi.

2. NOUVEAUX MODULES À CRÉER
   Liste exhaustive des nouveaux modules nécessaires pour Philia qui n'existent 
   pas dans IAXEL, avec :
   - Nom du module et dépendances
   - Fonctionnalité couverte
   - Effort estimé en jours
   - Priorité (P0 critique, P1 important, P2 stretch)

3. STACK TECHNIQUE — DÉCISIONS À ACTER
   Pour chaque composant majeur, recommande :
   - Réutiliser comme IAXEL : oui/non/à adapter
   - Si à adapter, comment précisément
   - Si nouveau, quelle techno et pourquoi
   
   Composants à couvrir : framework UI (Streamlit ou autre ?), base 
   utilisateurs/auth, paiements (Stripe), RAG (FAISS adapté ?), TTS 
   (ElevenLabs réutilisable ?), profil utilisateur (JSON ou DB ?), 
   leaderboard contest (temps réel ou batch ?), rapports parents (génération 
   asynchrone ?), hosting.

4. PLAN D'EXÉCUTION SÉQUENCÉ EN 6 SEMAINES
   Découpe en 6 sprints d'une semaine chacun. Pour chaque sprint :
   - Objectifs précis (3-5 livrables)
   - Modules à modifier/créer
   - Tests à passer pour valider le sprint
   - Risque de glissement et mitigation
   
   Le sprint 6 doit aboutir à un produit shippable au 30 juin pour 
   ouverture des inscriptions le 1er juillet (revenue) et démarrage 
   programme le 1er juillet pour les inscrits.

5. ARCHITECTURE PÉDAGOGIQUE — ADAPTATION DES PROMPTS
   IAXEL utilise un prompt formateur expert. Philia doit utiliser un prompt 
   mentor maïeutique. Donne-moi :
   - Squelette du nouveau prompt mentor maïeutique Philia
   - Variations par mode (Découverte, Pratique, Validation, Consolidation, Bilan)
   - Règles de guardrails (jamais donner la réponse, toujours guider par questions)
   - Comment l'avatar évolutif réagit aux états du dialogue

6. STRUCTURE DES DONNÉES PÉDAGOGIQUES (YAML)
   IAXEL a un format YAML pour quiz et modules. Définis le format YAML pour :
   - Chapitres Philia (structure d'un chapitre)
   - Sessions pédagogiques (séquence de 15-20 min)
   - Exercices avec progression de difficulté
   - Défis hebdomadaires
   - Épreuves du contest finale

7. RISQUES TECHNIQUES ET MITIGATIONS
   Top 5 risques techniques identifiés (par exemple : scaling du contest 
   leaderboard en temps réel, coût ElevenLabs imprévu, complexité de l'avatar 
   évolutif, audit RGPD mineurs, conformité AI Act). Pour chacun : impact, 
   probabilité, mitigation concrète.

8. PREMIER MODULE À ATTAQUER EN MODE IMPLEMENTER
   Le premier module précis à coder dès demain matin. Avec :
   - Fichiers exacts à créer/modifier
   - Spec détaillée
   - Tests d'acceptance
   - Estimation : doit être terminé en 1-2 jours pour valider le pipeline AXON-1

FORMAT ATTENDU

Markdown structuré. Pas de marketing-speak. Pas de "il faudrait penser à...". 
Décisions claires, efforts chiffrés en jours, sprints découpés en livrables 
testables.

CONTRAINTES NON-NÉGOCIABLES

- Maïeutique pure : Philia ne donne JAMAIS la réponse. Aucun shortcut.
- 1er juillet : date d'ouverture inscriptions. Programme démarre 1er juillet.
- Avatar évolutif : différenciateur produit majeur, ne pas le minimiser.
- Voix ponctuelle pour Premium : élément clé du paywall, intégrer dès sprint 3.
- Conformité RGPD enfants (consentement parental < 15 ans) : prévue dès sprint 1.
- Réutiliser au maximum IAXEL : ne pas refonder ce qui marche.

QUESTIONS QUE TU PEUX ME POSER AVANT DE PRODUIRE LE PLAN

Si tu identifies des ambiguïtés ou des trade-offs majeurs, pose-moi 1-3 
questions précises avant de produire le plan complet. Sinon, produis 
directement le plan.
```

---

## NOTES POUR TOI (HORS BRIEF)

**Ce que ce brief va déclencher** : Claude.ai en mode Architecte va probablement te poser 1-3 questions de clarification (sur la stack UI, sur la gestion contest, sur les détails avatar). Tu réponds, puis il produit le plan complet (probablement 3000-5000 mots, ~30 min de génération).

**Tu valides ou tu pousse-back** : si le plan te semble flou ou ambitieux, tu demandes à raffiner. Une fois validé, ce plan devient le contrat pour les 6 prochaines semaines.

**Tu enregistres le plan** dans `.claude/plans/2026-05-19_adaptation_iaxel_to_philia.md` du repo Philia.

**Tu choisis 2-3 modules prioritaires** parmi ceux listés section 8 et tu lances une session Claude Code dans VS Code avec le Template Implementer (du document AXON-1) pointant vers ces modules.

**Tu reviens vers moi** quand :
- Le plan produit te semble incomplet ou problématique → je l'audite en mode Reviewer
- Tu veux raffiner le brief avant relance
- Tu veux que je structure le sprint 1 en détail pour le briefing Implementer
- Tu veux discuter d'une décision technique majeure proposée par l'Architecte

---

*Brief Architecte d'adaptation IAXEL→Philia v1.0 — prêt à coller.*
*À utiliser dans une session Claude.ai neuve, modèle Opus 4.7.*
