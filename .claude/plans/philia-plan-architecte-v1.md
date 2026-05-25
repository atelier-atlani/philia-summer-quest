# Fork IAXEL → Philia Summer Quest 2026
**Plan Architecte v1.0 — 19 mai 2026**
**Horizon : 6 semaines (19 mai → 30 juin) — Ouverture inscriptions 1er juillet 2026**

---

## 0. Hypothèses structurantes validées

| Sujet | Décision | Impact |
|---|---|---|
| **Stack** | Streamlit/Python conservé tel quel (fork IAXEL) | Réutilisation maximale, zéro migration |
| **Illustrations mentor** | Génération IA (Nano Banana primaire, Midjourney v7 fallback) | Pipeline parallèle à construire, scope MVP-then-expand |
| **Contenu maths** | Pipeline d'ingestion PDF + transcripts → YAML via Claude API + revue humaine | Sprint 1 inclut la construction du pipeline d'ingestion |
| **Voix ElevenLabs** | Architecture 3 couches (templates globaux + per-user pré-gen + dynamique MD5-cached) | Budget ~2000€ pour 2000 utilisateurs/été, voix Turbo v2.5 |
| **Mentor évolutif** | MVP dégradé au lancement (3 styles × 5 expressions + 1 niveau évolution), expansion V1.1 mi-juillet | Différenciateur visible dès le 1er juillet sans bloquer le calendrier |
| **Contest tier 29€** | Mécanique simple à l'ouverture (inscription + leaderboard placeholder), épreuve finale construite en juillet pour 30 août | Découpe le contest en 2 phases : amorçage / finale |

---

## 1. Procédure de fork initial (J1-J2)

### 1.1 Commandes git précises

```bash
# Étape 1 : Sur GitHub, créer le nouveau repo "philia-summer-quest" (privé)

# Étape 2 : Clone d'IAXEL + remap remote
cd ~/projets
git clone --no-hardlinks ./agent-immo-formateur philia-summer-quest
cd philia-summer-quest

# Étape 3 : Réécrire l'historique (optionnel mais propre) ou repartir d'un commit propre
git checkout main
git remote remove origin
git remote add origin git@github.com:atlani-ia/philia-summer-quest.git

# Étape 4 : Premier commit "fork point" sans rien casser
git checkout -b fork/initial-from-iaxel
git commit --allow-empty -m "fork: point de départ depuis IAXEL agent-immo-formateur @ <SHA_IAXEL>"
git push -u origin fork/initial-from-iaxel

# Étape 5 : Smoke test avant toute modification
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # à remplir avec clés API
streamlit run app.py
# Vérifier que l'app IAXEL tourne en local sur http://localhost:8501
# Tester un parcours complet : onboarding → 1 session → quiz → synthèse

# Étape 6 : Tag du fork point
git tag -a v0.0.0-fork-from-iaxel -m "Point de départ avant adaptation Philia"
git push --tags
```

### 1.2 Renommage namespace et imports (J2)

```bash
# Renommage répertoires
mv data/base_connaissances.json data/base_connaissances_immo.json.archive  # à remplacer plus tard
mv training/quiz_bank training/quiz_bank_immo.archive
mv training/whatsapp/scenarios training/whatsapp_scenarios_immo.archive
mv prompts/prompt_formateur.txt prompts/prompt_formateur_iaxel.txt.archive
mv prompts/prompt_audit_v2.txt prompts/prompt_audit_iaxel.txt.archive

# Renommage assets
mv assets/logo_iaxel.png assets/logo_iaxel.png.archive
mv assets/images/IAXEL-formateur.png assets/images/IAXEL-formateur.png.archive

# Création structure Philia
mkdir -p prompts/mentor
mkdir -p data/chapters
mkdir -p data/sessions
mkdir -p data/exercises
mkdir -p data/weekly_challenges
mkdir -p data/unlocks
mkdir -p data/badges
mkdir -p assets/mentor/expressions
mkdir -p assets/mentor/styles
mkdir -p assets/mentor/unlocks
mkdir -p assets/sounds/celebrations
mkdir -p assets/voice/layer_a_global
mkdir -p assets/voice/layer_b_per_user

# Rechercher/remplacer (sed sur Mac, attention BSD vs GNU)
grep -rln "IAXEL\|iaxel\|immobilier\|agent immobilier" --include="*.py" --include="*.md" .
# Traiter au cas par cas, ne pas remplacer aveuglément
```

### 1.3 Mise en place .claude/ selon AXON-1 v0.1

```bash
mkdir -p .claude/{contexts,commands,axons}
touch .claude/CLAUDE.md
touch .claude/contexts/produit-philia.md
touch .claude/contexts/stack-technique.md
touch .claude/contexts/guardrails-pedagogiques.md
touch .claude/contexts/contraintes-rgpd.md
touch .claude/axons/philia-summer-quest-axon.md
```

Le `.claude/CLAUDE.md` racine doit déclarer : "Ce projet est un fork d'IAXEL, voir `.claude/axons/philia-summer-quest-axon.md` pour le contexte produit complet."

### 1.4 Critères d'acceptance Sprint 0 (J1-J2)

- [ ] Repo `philia-summer-quest` existe sur GitHub, privé, accessible
- [ ] `streamlit run app.py` lance l'app forkée sans erreur
- [ ] Tag `v0.0.0-fork-from-iaxel` poussé
- [ ] Structure de dossiers Philia créée
- [ ] `.claude/CLAUDE.md` rédigé avec contexte fork
- [ ] Branche `develop` créée pour les sprints suivants
- [ ] `requirements.txt` validé (toutes les libs IAXEL toujours présentes)

---

## 2. Inventaire des modules IAXEL et leur destin pour Philia

| Module IAXEL | Destin | Effort (jours) | Notes |
|---|---|---|---|
| `app.py` | **Adapter** | 1.5 | Routing nouvelles pages (parcours enfant, dashboard parent, paywall, contest). Conserver le squelette Streamlit, refonte du sidebar et de la home. |
| `agent_formateur.py` | **Refondre → `agent_mentor.py`** | 3 | Logique d'appel LLM conservée, refonte complète du système de prompts (5 modes vs FAQ/Formateur/Audit). Garder le wrapper API Anthropic/OpenAI. |
| `requirements.txt` | **Conserver + extensions** | 0.5 | Ajouter : stripe, sendgrid (emails parents), pydantic (validation YAML), Pillow (compose avatar) |
| `config/constants.py` | **Adapter** | 0.5 | Remplacer constantes immo par constantes Philia (couleurs marque, limites session, niveaux mentor). Garder la structure. |
| `core/rag.py` | **Conserver tel quel** | 0 | Production éprouvée. On change uniquement l'index (Sprint 1) et la base de connaissances (Sprint 1-2). |
| `core/faq_contract.py` | **Adapter → `core/mentor_contract.py`** | 1.5 | Contrat sortie LLM différent (modes, expressions à déclencher, superpouvoir activé). Réutiliser la logique de validation Pydantic. |
| `core/tts.py` | **Adapter** | 1 | Cache MD5 conservé. Extension : système 3 couches (layer_a_global, layer_b_per_user, layer_c_dynamic). Documentation dans docstring. |
| `core/sanitizer.py` | **Conserver tel quel** | 0 | Nettoyage inputs identique pour enfants. À reconfigurer toléranceonly. |
| `training/engine.py` | **Refondre → `training/session_engine.py`** | 3 | State machine repensée : modes pédagogiques au lieu de FAQ/Quiz/WhatsApp. Garder le pattern session-progress-save. |
| `training/steps.py` | **Refondre → `training/modes.py`** | 1.5 | Enum des 5 modes pédagogiques (Découverte, Pratique, Validation, Consolidation, Bilan) + transitions autorisées. |
| `training/progress.py` | **Adapter** | 2 | Schéma `progress.json` étendu : profil mentor, déblocages, radar superpouvoirs, expressions accumulées, jauge énergie, analogies collectées. |
| `training/profile.py` | **Adapter** | 1 | Profil enfant : prénom, âge, classe, style de mentor choisi, parent_email, RGPD consent. |
| `training/profile_ui.py` | **Refondre → `training/onboarding_ui.py`** | 2.5 | UI onboarding enfant + parent : consentement RGPD, choix du style de mentor parmi 8 (ou 3 en MVP), test de niveau initial. |
| `training/adapters.py` | **Conserver + adapter** | 1 | Adaptation difficulté/ton conservée. Refonte des paliers (élève 11-12 ans, pas agent immo). |
| `training/content.py` | **Refondre → `training/curriculum.py`** | 2 | Au lieu de 20 thèmes immo, 5 chapitres core + 2 stretch avec progression spiralaire. |
| `training/quiz.py` | **Conserver + adapter** | 1 | Engine quiz Kahoot-style conservé. Refonte des YAML quiz (maths au lieu d'immo). |
| `training/quiz_ui.py` | **Conserver tel quel** | 0.5 | Style Kahoot fonctionne. Repaint visuel léger pour aligner sur charte Philia. |
| `training/whatsapp.py` | **Supprimer** | 0 | Pas de roleplay client en Philia. |
| `training/whatsapp_ui.py` | **Supprimer** | 0 | Idem. |
| `training/synthesis.py` | **Adapter** | 1 | Synthèse session conservée. Refonte contenu : bilan émotionnel + maths au lieu d'immo. |
| `training/pdf_export.py` | **Adapter** | 1.5 | Garder fpdf2. Nouveaux templates : bilan parent hebdo + certificat fin de programme. |
| `training/formateur_messages.py` | **Supprimer** | 0 | Remplacé par les prompts modes + couche voix layer A. |
| `training/chat_libre.py` | **Adapter** | 0.5 | Chat questions libres conservé mais routé vers mode Découverte du mentor. |
| `training/marche_module.py` | **Refondre → `training/chapter_module.py`** | 1.5 | Runner mini-cours conservé. Adaptation pour chapitres maths. |
| `training/quiz_bank/*.yaml` | **Supprimer + remplacer** | 0 | Banque immo archivée. Nouvelle banque maths créée Sprint 2-5. |
| `training/whatsapp/scenarios/*.yaml` | **Supprimer** | 0 | — |
| `training/modules/marche/` | **Supprimer + remplacer** | 0 | 100 modules immo → ~50 modules maths par chapitre construits Sprint 2-5. |
| `prompts/prompt_formateur.txt` | **Refondre intégral** | inclus Sect. 4 | Voir architecture prompts §4. |
| `prompts/prompt_audit_v2.txt` | **Supprimer** | 0 | — |
| `scripts/check_before_merge.sh` | **Conserver + adapter** | 0.5 | Adapter les checks aux nouveaux modules. |
| `scripts/tests_contract_faq.py` | **Adapter → `tests_contract_mentor.py`** | 1 | Tests contrat sortie LLM nouveau format. |
| `scripts/index_marche_modules.py` | **Adapter → `index_chapter_modules.py`** | 0.5 | Indexation des modules chapitres. |
| `scripts/run_ia_tests.py` | **Adapter** | 0.5 | Suite de tests IA adaptée au mentor. |
| `data/progress.json` | **Adapter (schéma)** | inclus dans progress.py | Voir §2 row progress.py |
| `data/base_connaissances.json` | **Remplacer** | voir §6 | Création `base_connaissances_maths.json` |
| `data/rag_index/` | **Régénérer** | 0.5 | Reindexation FAISS Sprint 1 |
| `data/tts_cache/` | **Conserver structure + vider** | 0 | Cache vide au démarrage, se reconstruit. |
| `assets/logo_iaxel.png` | **Remplacer** | 0 | Nouveau logo Philia (design en cours/livraison) |
| `assets/videos/`, `assets/sounds/` | **Conserver + ajouter** | 0 | Sons de célébration enfant-friendly à ajouter Sprint 3 |

**Effort total adaptation modules existants** : ~30 jours dev (à paralléliser autant que possible).

---

## 3. Nouveaux modules à créer pour Philia

| Module | Priorité | Effort (j) | Sprint | Dépendances |
|---|---|---|---|---|
| `mentor/evolution.py` | P0 | 2.5 | S3 | progress.py, assets mentor générés |
| `mentor/expressions.py` | P0 | 1.5 | S3 | core/mentor_contract.py |
| `mentor/style_composer.py` | P1 | 2 | S3 | Pillow, assets unlocks |
| `pedagogy/mode_router.py` | P0 | 2 | S2 | prompts/mentor/*, progress.py |
| `pedagogy/mode_decouverte.py` | P0 | 1.5 | S2 | mode_router |
| `pedagogy/mode_pratique.py` | P0 | 1.5 | S2 | mode_router |
| `pedagogy/mode_validation.py` | P0 | 1.5 | S2 | mode_router |
| `pedagogy/mode_consolidation.py` | P0 | 1.5 | S2 | mode_router |
| `pedagogy/mode_bilan.py` | P0 | 1.5 | S2 | mode_router |
| `pedagogy/spiral_infusion.py` | P1 | 2 | S5 | curriculum.py, mode_router |
| `radar/superpouvoirs.py` | P0 | 2 | S3 | progress.py |
| `radar/radar_ui.py` | P0 | 1.5 | S3 | superpouvoirs.py, Plotly (déjà dans IAXEL) |
| `gamification/mur_victoires.py` | P0 | 1.5 | S3 | progress.py |
| `gamification/badges.py` | P0 | 1.5 | S3 | superpouvoirs.py, YAML badges |
| `gamification/jauge_energie.py` | P1 | 1 | S3 | session_engine.py |
| `gamification/collection_analogies.py` | P1 | 1.5 | S5 | progress.py |
| `gamification/voyage_narratif.py` | P1 | 1.5 | S5 | curriculum.py |
| `legacy/quete_heritage.py` | P1 | 1.5 | S5 | progress.py, pdf_export.py |
| `parent/dashboard_ui.py` | P0 | 2.5 | S5 | progress.py |
| `parent/bilan_hebdo.py` | P0 | 2 | S5 | pdf_export.py, sendgrid |
| `parent/email_sender.py` | P0 | 1 | S5 | sendgrid |
| `commerce/paywall.py` | P0 | 2 | S4 | Stripe |
| `commerce/stripe_integration.py` | P0 | 2.5 | S4 | Stripe API, webhooks |
| `commerce/tier_manager.py` | P0 | 1 | S4 | profile.py |
| `compliance/rgpd_consent.py` | P0 | 2 | S4 | parent/email_sender |
| `compliance/parent_verification.py` | P0 | 1.5 | S4 | email_sender |
| `contest/inscription.py` | P0 | 1 | S6 | tier_manager |
| `contest/leaderboard.py` | P0 | 2 | S6 | progress.py |
| `contest/epreuve_finale.py` | P1 | 2 | post-launch (juillet) | session_engine |
| `pipeline/ingest_content.py` | P0 | 2 | S1 | Claude API |
| `pipeline/yaml_validator.py` | P0 | 1 | S1 | pydantic |
| `voice/layer_a_generator.py` | P0 | 1 | S4 | ElevenLabs API |
| `voice/layer_b_per_user.py` | P0 | 1.5 | S4 | layer_a, profile.py |
| `voice/voice_router.py` | P0 | 1.5 | S4 | core/tts.py |

**Effort total nouveaux modules** : ~55 jours dev. **Total fork + new ≈ 85 jours dev** → faisable en 6 semaines à condition de paralléliser (toi sur architecture + 1-2 contributeurs sur contenu/assets) et de respecter le scope MVP.

---

## 4. Architecture des prompts Philia (refonte intégrale)

### 4.1 Structure des fichiers prompts

```
prompts/
├── mentor/
│   ├── _shared_guardrails.txt       # Maïeutique pure, jamais de réponse directe
│   ├── _shared_persona.txt          # Identité du mentor (sage, bienveillant exigeant)
│   ├── _shared_output_contract.txt  # Contrat de sortie JSON strict
│   ├── meta_router.txt              # Choix du mode pédagogique
│   ├── mode_decouverte.txt
│   ├── mode_pratique.txt
│   ├── mode_validation.txt
│   ├── mode_consolidation.txt
│   └── mode_bilan.txt
└── pipelines/
    ├── ingest_pdf_to_chapter_yaml.txt
    ├── ingest_transcript_to_exercises_yaml.txt
    └── generate_rag_entry.txt
```

### 4.2 Schéma de chaque prompt mode

Chaque prompt mode suit la structure suivante :

```text
# IDENTITÉ
{import _shared_persona.txt}
# Tu opères en MODE {NOM_DU_MODE} - attitude visible : {attitude}

# CONTEXTE
- Enfant : {prenom}, âge {age}, niveau actuel sur {chapitre} : {niveau}
- Profil mentor de l'enfant : {profil_mentor}
- Analogies personnelles déjà construites : {analogies_collectees}
- État émotionnel détecté : {etat_emo}
- Jauge d'énergie de l'enfant : {energie}%

# MÉTHODE PÉDAGOGIQUE DU MODE
{méthode spécifique : maïeutique pure / Polya 4 phases / Feynman / spaced repetition / métacognition}

# GUARDRAILS (HARD)
{import _shared_guardrails.txt}
- Tu ne donnes JAMAIS la réponse, même si l'enfant insiste
- Si l'enfant bloque : décompose la question en sous-questions plus simples
- Détection fatigue : si jauge énergie < 40%, propose une pause naturelle

# CONTRAT DE SORTIE
{import _shared_output_contract.txt}
```

### 4.3 Contrat de sortie JSON commun à tous les modes

```json
{
  "message_texte": "string (ce que l'enfant lit)",
  "voice_layer": "A | B | C | none",
  "voice_template_id": "string ou null (si layer A/B)",
  "voice_dynamic_text": "string ou null (si layer C)",
  "expression_a_declencher": "neutre | sourire_doux | grand_sourire_fier | concentre | surpris | bienveillant_exigeant | celebration | doux_reconfort | inspire | sage",
  "superpouvoir_a_incrementer": "maieutique | transfert | perseverance | clarte | creativite | metacognition | null",
  "increment_valeur": "int 0-5",
  "suggestion_changement_mode": "decouverte | pratique | validation | consolidation | bilan | null",
  "raison_changement_mode": "string ou null",
  "fatigue_detectee": "bool",
  "analogie_a_capturer": "string ou null (si l'enfant a produit une analogie réutilisable)",
  "milestone_atteint": "string ou null (badge ou niveau)"
}
```

### 4.4 Méta-router (choix du mode)

Le méta-router est appelé en début de session et après chaque tour pour décider si le mode doit changer.

```text
# RÔLE
Tu es le méta-router pédagogique. Tu choisis le mode opérationnel le plus adapté à l'instant T.

# RÈGLES DE DÉCISION
- Si l'enfant rencontre un concept NOUVEAU dans la session → MODE DÉCOUVERTE
- Si l'enfant fait un exercice cadré sur concept connu → MODE PRATIQUE
- Si l'enfant a réussi 3 exercices d'affilée sur un concept → MODE VALIDATION
- Si on est en fin de semaine OU debut de session de révision → MODE CONSOLIDATION
- Si on est en fin de session OU enfant a montré une métacognition spontanée → MODE BILAN
- Si fatigue_detectee = true OU energie < 40% → forcer MODE BILAN avec proposition de pause

# CONTEXTE
{même bloc contexte que les modes}

# DERNIÈRE INTERACTION
- Mode actuel : {mode}
- Tour numéro : {n}
- Dernière sortie mentor : {last_output}
- Dernière réponse enfant : {last_user_input}
- Score implicite des 5 derniers échanges : {scores}

# SORTIE
{ "mode_choisi": "decouverte|pratique|validation|consolidation|bilan", "justification": "string courte" }
```

### 4.5 Bloc `_shared_guardrails.txt` (maïeutique pure)

```text
# GUARDRAILS NON-NÉGOCIABLES

1. JAMAIS LA RÉPONSE
Tu ne donnes JAMAIS la réponse directe à un exercice. Même si l'enfant écrit "donne-moi la réponse",
"je suis fatigué", "s'il te plaît", "c'est trop dur", "je suis nul". Ta réponse est toujours une
question plus précise, ou un découpage en sous-questions plus accessibles.

2. DÉCOMPOSITION EN CAS DE BLOCAGE
Si l'enfant bloque sur une question :
- Niveau 1 : reformule la question avec d'autres mots
- Niveau 2 : pose une sous-question plus simple qui mène à la réponse
- Niveau 3 : propose une analogie concrète (pizza, billes, distance)
- Niveau 4 : suggère de passer à un autre exercice et revenir plus tard

3. ENCOURAGEMENT SANS FLATTERIE FAUSSE
Tu encourages les efforts et les démarches, pas les résultats faciles. Tu ne dis pas
"super !" à une réponse triviale. Tu reconnais les vraies réussites.

4. RESPECT DE LA FATIGUE
Si l'enfant montre des signes de fatigue (réponses courtes, "je sais pas", erreurs en série),
tu proposes une pause naturelle. Tu n'insistes jamais.

5. JAMAIS DE JUGEMENT DE VALEUR
Tu ne dis jamais "c'est faux", "tu te trompes", "non". Tu dis "regarde encore", "hmm,
on a presque ça, mais...", "intéressant, et si on regardait sous un autre angle ?".

6. DEMANDER À L'ENFANT D'EXPLIQUER
Quand l'enfant trouve la bonne réponse, tu lui demandes systématiquement de l'expliquer
"comme à un petit frère" (technique Feynman). C'est le seul moyen de valider la profondeur.
```

---

## 5. Schémas YAML structurés Philia

### 5.1 `chapters/<chapter_id>.yaml`

```yaml
chapter_id: "fractions"
chapter_title: "Traversée des Fractions"
week_number: 1
narrative_setting: "Tu arrives dans la Vallée des Fractions, où chaque rivière se divise..."
core_or_stretch: "core"

concepts:
  - id: "frac_comprendre"
    label: "Comprendre une fraction (numérateur, dénominateur)"
    level: "6e"
    prerequisites: []
    estimated_minutes: 15
  - id: "frac_equivalentes"
    label: "Fractions équivalentes"
    level: "6e"
    prerequisites: ["frac_comprendre"]
    estimated_minutes: 20
  - id: "frac_comparer"
    label: "Comparer des fractions"
    level: "6e"
    prerequisites: ["frac_equivalentes"]
    estimated_minutes: 20
  - id: "frac_add_sous_meme_denom"
    label: "Addition/soustraction de fractions de même dénominateur"
    level: "5e_intro"
    prerequisites: ["frac_comprendre"]
    estimated_minutes: 25

candidate_analogies:
  - "Découper une pizza avec ses amis"
  - "Partager une tablette de chocolat"
  - "Un terrain de foot divisé en zones"

common_misconceptions:
  - misconception: "Pour additionner 1/4 + 1/4, on additionne les numérateurs ET les dénominateurs (2/8)"
    intervention_mode: "validation"
    intervention_prompt_key: "frac_add_misconception_01"

weekly_challenge_id: "challenge_fractions_w1"
boss_id: "epreuve_maitre_fractions"
unlocks_on_completion:
  - badge: "harmoniste_initiate"
  - mentor_outfit: "robe_de_partage"
```

### 5.2 `sessions/<session_id>.yaml`

```yaml
session_id: "frac_s01_decouverte"
chapter_id: "fractions"
concept_id: "frac_comprendre"
estimated_duration_minutes: 18
default_mode: "decouverte"

opening:
  voice_layer: "A"
  voice_template_id: "open_decouverte_001"
  text: "Aujourd'hui, on plonge dans le monde des fractions. Tu sais déjà ce que c'est ?"

steps:
  - step_id: 1
    mode: "decouverte"
    socratic_question: "Si tu partages une tarte en 4 parts égales et que tu en manges 1, comment tu écrirais ça en maths ?"
    fallback_decomposition:
      - "Combien de parts au total ?"
      - "Combien de parts tu as mangées ?"
      - "Comment on note ça avec des chiffres l'un au-dessus de l'autre ?"
    expected_concepts_to_emerge: ["numerateur", "denominateur"]

  - step_id: 2
    mode: "decouverte"
    socratic_question: "Et si tu mangeais 2 parts sur 4, comment ça s'écrit ?"

  - step_id: 3
    mode: "validation"
    feynman_prompt: "Explique-moi comment fonctionne une fraction comme si je n'avais jamais entendu ça."

closing:
  voice_layer: "B"
  voice_template_id: "close_decouverte_with_name"
  text: "Bravo {prenom}, tu viens de comprendre ce qu'est une fraction !"
  expression: "grand_sourire_fier"
  superpouvoir_increment:
    superpouvoir: "maieutique"
    valeur: 2
```

### 5.3 `exercises/<exercise_id>.yaml`

```yaml
exercise_id: "frac_ex_001"
chapter_id: "fractions"
concept_ids: ["frac_comprendre"]
difficulty: 1   # 1-5
type: "construction"  # construction | choix_multiple | feynman | analogie | application
statement: "Sur cette pizza coupée en 6 parts, tu en manges 2. Comment écris-tu la fraction de pizza que tu as mangée ?"
expected_answer_form: "2/6"
hints_progressifs:
  - "Combien de parts au total ?"
  - "Combien de parts tu as mangées ?"
  - "Le total va en bas, ce que tu as mangé en haut."
common_wrong_answers:
  - answer: "6/2"
    intervention: "Tu as inversé ! Réfléchis : c'est quoi le total des parts, et c'est quoi ce que tu as mangé ?"
estimated_seconds: 90
xp_reward: 10
```

### 5.4 `weekly_challenges/<week_id>.yaml`

```yaml
challenge_id: "challenge_fractions_w1"
week_number: 1
chapter_id: "fractions"
title: "Le Défi des Tartes de Sigma"
narrative: "Sigma, la sage gardienne des fractions, te lance trois énigmes..."
exercises_sequence:
  - "frac_ex_007"
  - "frac_ex_012"
  - "frac_ex_015"
success_criteria:
  min_correct: 2
  max_attempts_per_exercise: 3
rewards_on_success:
  - badge: "harmoniste"
  - mentor_unlock: "aura_lumineuse_semaine_1"
  - xp: 50
```

### 5.5 `unlocks/<unlock_id>.yaml`

```yaml
unlock_id: "robe_de_partage"
unlock_type: "outfit"  # outfit | accessory | companion | aura | halo
asset_path: "assets/mentor/unlocks/outfits/robe_de_partage_{style}.png"
condition:
  type: "completion_chapter"
  chapter_id: "fractions"
  min_correct_rate: 0.7
narrative_unlock: "Tu as maîtrisé l'art de partager : ton mentor revêt la Robe de Partage."
expression_at_unlock: "celebration"
voice_layer: "B"
voice_template_id: "unlock_outfit_with_name"
```

### 5.6 `badges/<badge_id>.yaml`

```yaml
badge_id: "harmoniste"
badge_name: "Harmoniste"
badge_description: "A trouvé l'harmonie dans les fractions et les proportions."
icon_path: "assets/badges/harmoniste.png"
condition:
  type: "combined"
  rules:
    - chapter_completion: "fractions"
    - min_correct_rate: 0.75
    - feynman_explanations_count: 3
reflection_prompt: "Tu viens de gagner le badge Harmoniste. Comment as-tu réussi à comprendre les fractions ? Qu'est-ce qui t'a aidé ?"
rarity: "common"  # common | rare | epic | legendary
```

### 5.7 `contest_final/epreuve_30_aout.yaml`

```yaml
contest_id: "philia_summer_2026_final"
date: "2026-08-30T18:00:00+02:00"
duration_minutes: 60
eligibility:
  required_tier: "premium_contest"
  min_chapters_completed: 4
sections:
  - section_id: "vitesse"
    duration_minutes: 15
    exercise_pool: ["frac_ex_*", "prop_ex_*"]
    selection_count: 10
  - section_id: "profondeur"
    duration_minutes: 30
    type: "feynman_challenges"
    challenge_count: 3
  - section_id: "creativite"
    duration_minutes: 15
    type: "inventer_probleme"
prizes:
  top_1: "1 abonnement Philia Année à vie"
  top_10: "1 an Philia Année gratuit"
  top_100: "6 mois Philia Année gratuit"
```

---

## 6. Adaptation du RAG

### 6.1 Volume cible

Pour couvrir 5 chapitres core de manière dense :
- **~80 entrées par chapitre** (concepts, exemples résolus, contre-exemples, analogies pré-construites, méta-stratégies)
- **+ 30 entrées transverses** (méthodologie Polya, technique Feynman, gestion erreurs, encouragements pédagogiques)
- **Total cible : ~430 entrées** pour V1 (proche des 339 entrées immo d'IAXEL, donc proportions tenables).

### 6.2 Pipeline d'ingestion `scripts/ingest_content.py`

```python
"""
Usage:
    python scripts/ingest_content.py \
        --input data/sources/fractions_manuel.pdf \
        --chapter fractions \
        --output data/chapters/fractions.draft.yaml \
        --rag-output data/rag_drafts/fractions_entries.jsonl

Process:
    1. Lit PDF ou .txt transcript
    2. Découpe en chunks sémantiques (~1500 chars)
    3. Pour chaque chunk, appelle Claude avec prompt d'extraction structurée
    4. Génère :
       - Concepts identifiés
       - Exemples résolus
       - Exercices candidats
       - Analogies suggérées
       - Misconceptions repérées
       - Entrées RAG candidates (avec sources)
    5. Output: YAML chapitre brouillon + JSONL entrées RAG
    6. Étape humaine : Seb relit, corrige, valide, commit
"""

import anthropic, pypdf, yaml, json
from pathlib import Path
# ... (squelette d'implémentation détaillé en Sprint 1)
```

**Prompt d'extraction** : `prompts/pipelines/ingest_pdf_to_chapter_yaml.txt` (à rédiger en Sprint 1 J1).

### 6.3 Reindexation FAISS

```bash
# Après génération des entrées maths
python scripts/build_rag_index.py \
    --input data/base_connaissances_maths.json \
    --output data/rag_index/maths/

# Vérification du recall sur 20 questions test
python scripts/test_rag_recall.py --queries data/test_queries.yaml
```

### 6.4 Charge de travail estimée pour le contenu

| Tâche | Effort |
|---|---|
| Construction du pipeline d'ingestion | 2j dev (Sprint 1) |
| Ingestion auto de tous tes PDF + transcripts | 0.5j compute |
| Revue + correction humaine des YAML chapitres (Seb, 5 chap × 3h) | 15h (~2j) |
| Revue + curation des entrées RAG (430 entrées × 2 min) | ~15h (~2j) |
| Création des exercices manquants (~50 par chap) | 3j (partageable) |
| **Total contenu** | **~10 jours** sur Sprints 1-5 (parallélisable avec dev) |

---

## 7. Plan d'exécution séquencé en 6 sprints

### Sprint 1 (19-25 mai) — Setup + smoke test + premier mode

**Livrables**
- [ ] Fork IAXEL en `philia-summer-quest` + smoke test OK (J1-J2)
- [ ] Structure dossiers Philia + `.claude/` initialisé (J2)
- [ ] Pipeline d'ingestion contenu opérationnel sur 1 chapitre test (Fractions) (J3-J4)
- [ ] Premier prompt `mentor/mode_decouverte.txt` rédigé (J3)
- [ ] `core/faq_contract.py` → `core/mentor_contract.py` adapté (J4)
- [ ] `agent_formateur.py` → `agent_mentor.py` opérationnel sur mode Découverte (J5)
- [ ] RAG basique reindexé sur Fractions (J5)
- [ ] **Test E2E** : un enfant peut faire une session maïeutique sur "comprendre une fraction" du début à la fin (J5)

**Critères validation** : `streamlit run app.py` permet à un testeur de parcourir une session Découverte Fractions. Le mentor ne donne jamais la réponse. La sortie LLM respecte le contrat JSON.

**Risque/mitigation** : Pipeline d'ingestion plus long que prévu → fallback rédaction manuelle d'1 chapitre (1j) pour ne pas bloquer.

---

### Sprint 2 (26 mai - 1er juin) — Architecture pédagogique 5 modes

**Livrables**
- [ ] Tous les prompts modes rédigés : `_shared_guardrails.txt`, `_shared_persona.txt`, `_shared_output_contract.txt`, `meta_router.txt`, 5 modes
- [ ] `pedagogy/mode_router.py` opérationnel (choisit le mode en fonction du contexte)
- [ ] `pedagogy/mode_*.py` × 5 implémentés
- [ ] `training/session_engine.py` refondu avec state machine des 5 modes
- [ ] Tests `tests_contract_mentor.py` au vert
- [ ] **Test E2E** : sur le chapitre Fractions, un enfant traverse les 5 modes au cours d'une session (Découverte → Pratique → Validation → Consolidation → Bilan)

**Critères validation** : 5 sessions de test menées par toi, chaque mode active la bonne attitude, l'enfant n'obtient jamais une réponse.

**Risque/mitigation** : Router incohérent → ajouter logs détaillés + dashboard interne pour observer les choix de mode.

---

### Sprint 3 (2-8 juin) — Mentor évolutif + radar superpouvoirs + paywall préparé

**Livrables**
- [ ] **Pipeline assets parallèle** (toi ou équipe) : génération Nano Banana de 3 styles × 5 expressions = 15 assets MVP livrés
- [ ] `mentor/expressions.py` : déclenche la bonne expression selon sortie LLM
- [ ] `mentor/evolution.py` : mécanique de déblocage (3 niveaux + 1 unlock visuel par chapitre)
- [ ] `mentor/style_composer.py` : compose le mentor avec Pillow (style de base + accessoire éventuel)
- [ ] `radar/superpouvoirs.py` + `radar/radar_ui.py` : radar Plotly visible sur la home
- [ ] `gamification/mur_victoires.py` + `gamification/badges.py` + 5 premiers badges YAML
- [ ] `gamification/jauge_energie.py` : décroît avec sessions longues, déclenche pause naturelle
- [ ] **Test E2E** : enfant fait 3 sessions, voit son mentor évoluer visuellement, voit son radar progresser, débloque 1 badge

**Critères validation** : retours testeurs (3-5 enfants) sur l'engagement visuel du mentor évolutif.

**Risque/mitigation** : Assets en retard → MVP à 2 styles × 4 expressions = 8 assets, scope encore réduit. Évolution mentor à 2 niveaux visibles minimum.

---

### Sprint 4 (9-15 juin) — Voix + paywall + RGPD

**Livrables**
- [ ] `voice/voice_router.py` : route entre layer A/B/C selon contrat sortie
- [ ] `voice/layer_a_generator.py` : génère les ~250 phrases globales en batch, commit dans repo
- [ ] `voice/layer_b_per_user.py` : génère les ~20 phrases per-user au signup (post-payment)
- [ ] Extension `core/tts.py` pour layer C dynamique avec MD5 cache
- [ ] `commerce/paywall.py` + UI 3 tiers
- [ ] `commerce/stripe_integration.py` + webhooks
- [ ] `commerce/tier_manager.py` (gère accès Tier 1/2/3)
- [ ] `compliance/rgpd_consent.py` : flow consentement parental complet
- [ ] `compliance/parent_verification.py` : double opt-in email parent
- [ ] **Test E2E paiement** : un parent peut payer un tier Premium en environnement Stripe test, l'enfant accède au contenu derrière paywall

**Critères validation** : Test du flow complet inscription → paiement → consentement → accès enfant. Test voix sur 3 sessions, vérifier qu'aucun appel ElevenLabs hors layer C n'est fait (cache vérifié).

**Risque/mitigation** : Compliance RGPD complexe → consultation rapide avec juriste (1h) pour valider le flow consentement < 15 ans.

---

### Sprint 5 (16-22 juin) — Contenu complet 5 chapitres + dashboard parent

**Livrables**
- [ ] Ingestion + revue contenu pédagogique pour les 5 chapitres core
- [ ] ~250 exercices YAML produits (50 par chapitre)
- [ ] 5 weekly challenges + 5 boss "Épreuve du Maître"
- [ ] ~430 entrées RAG maths reindexées dans FAISS
- [ ] `parent/dashboard_ui.py` : page parent (login séparé via email)
- [ ] `parent/bilan_hebdo.py` : génération PDF + email automatique dimanche soir (cron)
- [ ] `parent/email_sender.py` : intégration SendGrid
- [ ] `gamification/voyage_narratif.py` + `gamification/collection_analogies.py`
- [ ] `legacy/quete_heritage.py` : enfant écrit son conseil à son moi-de-septembre
- [ ] **Test E2E** : enfant parcourt 1 session par chapitre, parent reçoit bilan hebdo PDF

**Critères validation** : Bilan parent reçu par email avec contenu fidèle au parcours enfant. Pas d'oubli sur un chapitre.

**Risque/mitigation** : Contenu en retard → priorité sur 3 chapitres core (Fractions, Proportionnalité, Calcul littéral) au lancement, 2 autres déployés mid-juillet.

---

### Sprint 6 (23-30 juin) — Contest + stress test + finitions

**Livrables**
- [ ] `contest/inscription.py` : inscription tier 29€ avec leaderboard placeholder
- [ ] `contest/leaderboard.py` : leaderboard visible pour tier Concours uniquement
- [ ] Note : `contest/epreuve_finale.py` construit en juillet, pas bloquant pour le 1er juillet
- [ ] **Stress test infrastructure** : simulation 200 utilisateurs concurrents puis 500 (locust ou k6)
- [ ] Optimisation FAISS et cache si bottlenecks détectés
- [ ] Pages légales : CGV, CGU, politique RGPD, mentions légales
- [ ] **Tests d'acceptance** : 10 scénarios E2E joués par toi + 2 testeurs (parent + enfant)
- [ ] Préparation infrastructure prod (Streamlit Cloud Pro / VPS dédié / Railway)
- [ ] **Soft launch** : 30 juin en interne avec 5-10 familles bêta avant ouverture publique 1er juillet

**Critères validation** : 100% des tests d'acceptance au vert. Stress test passe à 500 users concurrents avec latence < 3s.

**Risque/mitigation** : Streamlit ne tient pas la charge → fallback queue (Redis + workers) ou bascule sur instance plus grosse. Plan B documenté dès le début de Sprint 6.

---

## 8. Risques techniques et mitigations (top 5)

### R1 — Délai serré 6 semaines

- **Impact** : Critique (date 1er juillet immuable)
- **Probabilité** : Forte
- **Mitigations** :
  - Scope MVP strict : 3 chapitres core + 1 stretch au lancement, 2 chapitres déployés mi-juillet
  - Parallélisation : asset generation (Nano Banana) en track parallèle dès Sprint 1
  - Mentor évolutif dégradé acceptable (3 styles × 5 expressions au lieu de 8 × 10) - V1.1 expand en juillet
  - Contest mécanique simple au lancement, épreuve finale construite en juillet pour 30 août
  - Communication produit : ne pas promettre tous les chapitres au D-day, parler de "ouverture par paliers"

### R2 — Coût ElevenLabs imprévu

- **Impact** : Modéré (budget annoncé 2000€, dérive possible à 5000-8000€)
- **Probabilité** : Modérée
- **Mitigations** :
  - Architecture 3 couches stricte : layer A pré-généré commit, layer B per-user one-shot au signup, layer C avec MD5 cache global
  - **Monitoring** : compteur d'appels ElevenLabs par jour, alerte si > 100k chars/jour
  - **Kill switch** : variable d'env `VOICE_LAYER_C_ENABLED` à false en cas de dérive (dégradation gracieuse vers texte seul)
  - Choix Turbo v2.5 par défaut (50% moins cher que Multilingual v2)
  - Tier gratuit : pas de voix layer B ni C, layer A uniquement → coût marginal nul

### R3 — Complexité mentor évolutif

- **Impact** : Modéré (différenciateur produit)
- **Probabilité** : Forte (asset pipeline non éprouvé)
- **Mitigations** :
  - Scope MVP strict (cf Sprint 3)
  - Asset pipeline isolé : ne bloque pas le dev pédagogique
  - Sb test visuel sur 2-3 enfants en Sprint 3 pour valider l'engagement
  - V1.1 expand programmé mi-juillet : 5 styles × 8 expressions
  - V1.2 août : unlockables tenues et compagnons

### R4 — Conformité RGPD enfants < 15 ans

- **Impact** : Critique (sanction CNIL possible, mais surtout image de marque)
- **Probabilité** : Modérée
- **Mitigations** :
  - **Consultation juriste 1h en Sprint 4 J1** (budget 200-400€) pour valider le flow consentement
  - Double opt-in parent : email parent vérifié AVANT toute collecte de donnée enfant
  - Données minimales : prénom enfant (pas nom), âge approximatif, niveau scolaire, email parent uniquement
  - Hébergement données en UE (Streamlit Cloud EU ou VPS OVH)
  - Page RGPD claire et exportable depuis le dashboard parent
  - DPO : si pas en interne, désigner Seb avec adresse `rgpd@philia.app`

### R5 — Stress du contest / charge simultanée

- **Impact** : Modéré (qualité de service)
- **Probabilité** : Faible-Modérée
- **Mitigations** :
  - Streamlit n'est pas un framework haute concurrence : prévoir Streamlit Cloud Pro ou VPS dédié avec autoscaling (Railway, Fly.io)
  - Stress test en Sprint 6 (k6 ou locust) à 200 puis 500 users concurrents
  - Si pic d'inscriptions au 1er juillet : queue d'inscriptions + email "compte actif sous 1h"
  - Leaderboard contest mis à jour en async (toutes les 5 min, pas en temps réel)
  - Plan B documenté : bascule sur architecture queue+workers en cas de dépassement

---

## 9. Premier module à attaquer en mode IMPLEMENTER (Sprint 1, J1-J2)

### Module : Fork initial + smoke test + structure Philia

**Fichiers à créer/modifier** :
- `philia-summer-quest/` (nouveau repo, fork d'IAXEL)
- `.claude/CLAUDE.md` (rédigé)
- `.claude/axons/philia-summer-quest-axon.md` (rédigé)
- `.claude/contexts/produit-philia.md`, `stack-technique.md`, `guardrails-pedagogiques.md`, `contraintes-rgpd.md`
- Structure dossiers Philia créée (voir §1.2)
- `requirements.txt` étendu (stripe, sendgrid, pydantic, Pillow ajoutés)
- `README.md` mis à jour avec contexte Philia + lien vers ce plan
- Tag git `v0.0.0-fork-from-iaxel`

**Spec détaillée** :

1. **Préparation (30 min)**
   - Création du repo GitHub privé `philia-summer-quest`
   - Récupération du SHA actuel d'IAXEL main pour traçabilité
   - Vérification que `agent-immo-formateur` tourne en local (smoke test pré-fork)

2. **Fork mécanique (1h)**
   - Commandes git de §1.1 exécutées dans l'ordre
   - Vérification : `git log` montre l'historique IAXEL préservé
   - Push initial sur GitHub

3. **Smoke test post-fork (30 min)**
   - `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
   - Copie `.env` IAXEL → `.env` Philia (temporairement, à isoler)
   - `streamlit run app.py`
   - Parcourir : onboarding → 1 session formateur immo → quiz → synthèse PDF
   - Si KO : noter l'erreur, ne pas commit la modif, débugger sur IAXEL d'abord

4. **Renommage et structure (2h)**
   - Archives `.archive` des assets/prompts/data immo (cf §1.2)
   - Création des nouveaux dossiers Philia
   - Commit : `chore: rename immo assets to .archive, create philia structure`

5. **Initialisation .claude/ (1h)**
   - `.claude/CLAUDE.md` racine : préambule projet
   - `.claude/axons/philia-summer-quest-axon.md` : context produit complet (copier-coller de Section 2 du brief)
   - `.claude/contexts/` : 4 fichiers de contexte spécifiques
   - Commit : `feat: initialize .claude/ workspace per AXON-1 v0.1`

6. **Documentation README (1h)**
   - README.md : positionnement Philia, lien vers ce plan architecte, commandes de dev, état d'avancement
   - Commit : `docs: README philia-summer-quest`

7. **Tag fork point (10 min)**
   - `git tag -a v0.0.0-fork-from-iaxel -m "Point de départ avant adaptation"`
   - `git push --tags`

**Critères d'acceptance (validation J2 soir)** :
- [ ] Repo `philia-summer-quest` existe, privé, accessible
- [ ] `streamlit run app.py` lance l'app forkée et un parcours IAXEL complet est jouable en local
- [ ] Tag `v0.0.0-fork-from-iaxel` poussé
- [ ] `.claude/CLAUDE.md` et `.claude/axons/philia-summer-quest-axon.md` rédigés (au moins 200 lignes au total)
- [ ] Structure de dossiers Philia créée sans casser le code IAXEL
- [ ] README.md à jour
- [ ] Branche `develop` créée et poussée
- [ ] Aucune fuite de clés API dans le repo (vérifier `.gitignore`)

**Estimé : 1.5 à 2 jours** (J1 PM + J2 complet).

**Sortie attendue côté Claude Code** : à l'issue de J2, Claude Code peut prendre le relais sur Sprint 1 J3-J5 (rédaction premier prompt mentor + adaptation `mentor_contract.py` + premier test E2E session Découverte Fractions).

---

## Annexe A — Budget global estimé

| Poste | Estimation |
|---|---|
| ElevenLabs (2000 users, 7 semaines, stratégie 3 couches) | 2 000 € |
| Nano Banana / Midjourney / Sora (génération assets V1 + V1.1) | 200 - 500 € |
| Anthropic API (sessions enfants + pipeline ingestion) | 1 500 - 3 000 € |
| Stripe (frais ~1.5% + 0.25€/transaction) | si 2000 × 24€ ≈ 720 € + 500 € = 1 220 € |
| SendGrid (emails parents) | 0 - 30 € (free tier jusqu'à 100/jour, sinon 20 €/mois) |
| Hébergement Streamlit Cloud Pro / Railway / VPS | 50 - 200 €/mois |
| Juriste RGPD (consultation Sprint 4) | 200 - 400 € |
| **Total coûts opérationnels été 2026** | **~5 000 - 7 500 €** |
| Revenu prévisionnel à 2000 users (mix tiers, hypothèse 80% T2 + 20% T3) | 2000 × (0.8 × 19.80 + 0.2 × 23.30) ≈ **40 000 €** |
| **Marge brute estimée** | **~85%** (avant coûts dev/marketing/acquisition) |

---

## Annexe B — Décisions à confirmer rapidement (J1-J3)

1. **Choix générateur d'images** : Nano Banana recommandé, à valider avec un POC J1 (générer un mentor "explorateur" en 3 expressions et comparer à Midjourney)
2. **Choix voix ElevenLabs** : test A/B Turbo v2.5 vs Multilingual v2 sur 3 phrases avec 3 enfants testeurs avant Sprint 4
3. **Infrastructure prod** : Streamlit Cloud Pro vs Railway vs VPS — décision finale Sprint 6 mais POC Railway en Sprint 4 (la migration Streamlit → Railway est trivial mais à valider)
4. **DPO / juriste RGPD** : trouver et briefer dès Sprint 1 (pas en Sprint 4)
5. **Déclaration jeux-concours France** : le tier 29€ avec dotations relève potentiellement de la réglementation jeux-concours. Vérifier avec juriste si déclaration auprès d'huissier nécessaire (généralement requis si tirage au sort, optionnel si pur mérite).

---

*Fin du Plan Architecte v1.0. Prochaine session recommandée : mode IMPLEMENTER sur Sprint 1 J1-J2 (fork + smoke test).*
