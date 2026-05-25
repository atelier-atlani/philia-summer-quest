# CLAUDE.md — agent-immo-formateur

## Projet

App Streamlit de formation IA pour agents immobiliers. 45min–1h/jour, 4j/semaine, 6 mois (~104 sessions).
Repo GitHub privé : `appIAtlani/agent-immo-formateur`

---

## Stack

- **Python 3.12** + **Streamlit** (UI)
- **OpenAI GPT-4o** (LLM principal : cours, quiz explanations, synthèses, évaluations)
- **FAISS** (RAG : recherche sémantique dans les PDFs de formation)
- **ElevenLabs** (TTS haute qualité : 3 voix — IAXEL formateur + 2 clients WhatsApp)
- **OpenAI TTS** (fallback TTS si ElevenLabs down, aussi pour contenus longs)
- **Plotly** (graphiques cours marché : taux, volumes, DPE, capacité emprunt)
- **fpdf2** (export PDF synthèses + fiches mémo)
- **API DVF data.gouv.fr** (données immobilières réelles, toutes villes de France)
- **API Geo gouv.fr** (résolution code INSEE depuis nom de ville)
- **PyYAML** (quiz banks + scénarios WhatsApp)

---

## Architecture

### State machine (training/engine.py)

Chaque session est une séquence de Steps gérée par `TrainingSession`.

**Jour 1** : PROFIL → MINI_COURS_MARCHE → QUESTIONS_RAG → COURS_CLES → QUIZ → WHATSAPP → DEBRIEF_WA → SYNTHESE

**Jour 2+** : MINI_COURS_MARCHE → QUESTIONS_RAG → COURS_CLES → QUIZ → WHATSAPP → DEBRIEF_WA → SYNTHESE

La progression est sauvée dans `data/progress.json` (fichier plat, gitignored).

### Pattern deux passes anti-removeChild (app.py)

Streamlit crashe si on change le DOM pendant qu'un widget est actif. Solution :
- **Passe 1** (bouton cliqué) : pose un flag `_do_step_transition` + sauvegarde le state + `st.rerun()`
- **Passe 2** (début de `ui_training()`) : détecte le flag, applique la transition, `st.rerun()` final
- Même pattern pour fin de session (`_do_session_end`) et session suivante (`_do_next_session`)

### TTS intelligent (core/tts.py + core/tts_elevenlabs.py)

- `tts_smart(client, text, priority)` : priority="high" → ElevenLabs (IAXEL), fallback OpenAI
- `tts_client_smart(client, text, persona_name)` : ElevenLabs voix client (homme/femme selon persona), fallback OpenAI onyx/nova
- Cache fichier dans `data/tts_cache/` et `data/tts_cache/elevenlabs/`
- Variables lazy-loaded (`_get_api_key()`) pour éviter lecture avant `load_dotenv()`

### RAG (core/rag.py — NE PAS MODIFIER)

- FAISS + rerank hybride (lexical + sémantique)
- Index créé dynamiquement au démarrage (pas versionné Git)
- `construire_contexte(question, k)` → string de contexte pour les prompts
- `RAG_K_FAQ=8`, configurable via .env

### GATE FAQ (core/faq_contract.py — NE PAS MODIFIER)

- `faq_is_covered_by_context()` : vérifie que la question est couverte par le RAG avant de répondre
- Extrait des mots-clés "forts" (≥6 chars) et vérifie leur présence dans le contexte
- Le quiz bypasse le GATE via `repondre_quiz_explanation()` (les questions viennent du formateur, pas de l'utilisateur)

### DVF dynamique (training/dvf_connector.py)

- Télécharge les CSV gzip de `files.data.gouv.fr/geo-dvf/` par département
- Gestion spéciale Paris/Lyon/Marseille (arrondissements)
- Cache fichier 7 jours dans `data/dvf_cache/`
- `analyze_market(ville)` → dict avec nb_transactions, prix_median_m2, transactions_recentes, etc.
- Résolution ville → code INSEE via `geo.api.gouv.fr`

---

## Arborescence clé

```
app.py                              # UI Streamlit principale (1500+ lignes)
agent_formateur.py                  # Agent IA : prompts, chat_complete, FAQ, formateur, audit
core/
  rag.py                            # FAISS RAG ← NE PAS MODIFIER
  faq_contract.py                   # GATE FAQ ← NE PAS MODIFIER
  tts.py                            # TTS OpenAI + tts_smart + tts_client_smart
  tts_elevenlabs.py                 # TTS ElevenLabs (3 voix)
  avatar.py                         # Avatar Lottie/PNG + show_formateur_message()
  sanitizer.py                      # Nettoyage marques/brand
training/
  engine.py                         # TrainingSession state machine
  steps.py                          # Step enum + séquences + STEP_LABELS
  progress.py                       # Load/save data/progress.json
  content.py                        # 20 thèmes pédagogiques, rotation 104 sessions
  profile.py                        # UserProfile dataclass
  profile_ui.py                     # Onboarding conversationnel
  adapters.py                       # Adaptation difficulté/ton/modules selon profil
  quiz.py                           # Quiz engine, scoring, YAML banks
  quiz_ui.py                        # UI Kahoot-like
  quiz_bank/*.yaml                  # 39+ questions (4 banques)
  whatsapp.py                       # Roleplay engine, évaluation 5 critères, scoring temps réel
  whatsapp_ui.py                    # UI WhatsApp (bulles, TTS client, débrief replay)
  wa_scenario_generator.py          # Génération LLM scénarios dynamiques
  scenarios/*.yaml                  # 4 scénarios statiques (fallback)
  synthesis.py                      # Synthèse IA fin de session
  pdf_export.py                     # Export PDF fpdf2
  marche_module.py                  # Runner modules marché
  marche_charts.py                  # 4 graphiques Plotly (taux, volumes, DPE, budget)
  marche_quiz.py                    # Jeu interactif Cascade (4 questions)
  dvf_connector.py                  # API DVF dynamique toutes villes
  dashboard.py                      # Dashboard progression (Plotly courbes + lacunes)
  formateur_messages.py             # Messages formateur (wrapper st.chat_message)
  chat_libre.py                     # Chat libre IAXEL (colonne droite)
  modules/marche/cascade_analysis.py # Analyse cascade Mondial→National→Local
config/
  constants.py                      # Emojis, chemins logos, vidéo intro
prompts/
  prompt_formateur.txt              # Prompt système formateur
  prompt_audit_v2.txt               # Prompt système audit charte
scripts/
  check_before_merge.sh             # Tests obligatoires (smoke + contract + HTTP 200)
  tests_contract_faq.py             # Tests contract FAQ ← NE PAS MODIFIER
  test_smoke.py                     # Smoke tests
data/
  progress.json                     # Progression stagiaire (gitignored)
  pdfs/                             # PDFs générés (gitignored)
  tts_cache/                        # Cache TTS OpenAI (gitignored)
  tts_cache/elevenlabs/             # Cache TTS ElevenLabs (gitignored)
  dvf_cache/                        # Cache API DVF (gitignored)
assets/
  avatars/                          # Vidéo IAXEL + images
  sounds/phone_ring.wav             # Sonnerie WhatsApp
  images/                           # Logos, avatars PNG
```

---

## Variables d'environnement (.env)

```
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=echo
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=FwLiEqGhLI7eYezarFY5          # IAXEL formateur
ELEVENLABS_VOICE_CLIENT_MALE=7Pm7442WzqlfkW9vjmO9   # Client homme
ELEVENLABS_VOICE_CLIENT_FEMALE=FFXYdAYPzn8Tw8KiHZqg # Cliente femme
RAG_K_FAQ=8
RAG_K_FORMATEUR=8
```

---

## Fichiers protégés — NE JAMAIS MODIFIER

- `core/rag.py` — RAG FAISS + rerank hybride
- `core/faq_contract.py` — GATE FAQ + validation 5 sections
- `scripts/tests_contract_faq.py` — Tests contract (7 cas)

Ces fichiers ont un contrat strict. Les tests doivent passer à 7/7.

---

## Tests obligatoires

```bash
./scripts/check_before_merge.sh
```

Lance : smoke tests + contract FAQ tests + Streamlit HTTP 200 health check.
**Toujours lancer avant chaque commit.**

---

## Décisions d'architecture récentes (avril 2026)

- **GPT-4o** remplace gpt-4o-mini pour toutes les réponses formateur/évaluation
- **Bypass GATE pour quiz** : `repondre_quiz_explanation()` ne passe pas par `faq_is_covered_by_context()` car les questions viennent du formateur
- **ElevenLabs pour moments haute valeur** : transitions formateur (voix IAXEL) + messages client WhatsApp (2 voix distinctes). OpenAI TTS pour contenus longs (cours, FAQ)
- **DVF dynamique** : CSV gzip de data.gouv.fr (pas l'API REST qui est instable), cache 7 jours par département
- **Scénarios WhatsApp générés par LLM** : le prompt force des chiffres concrets, une situation personnelle, et des objections calées sur le cours clé. Fallback 4 scénarios statiques si LLM échoue
- **Cours marché en 3 onglets** : Mondial/National/Local au lieu d'un mur de texte. Graphiques Plotly intégrés. Jeu cascade interactif pour tester la compréhension
- **Outils bonus (fiche mémo, plan entretien)** : retirés de la sidebar, accessibles uniquement en fin de session dans la synthèse
- **Pattern TTS lazy-loading** : les variables ElevenLabs sont lues via `_get_api_key()` au moment de l'appel (pas à l'import) pour éviter les reads avant `load_dotenv()`

---

## Points de vigilance / dettes techniques

### Critiques
- **app.py fait 1500+ lignes** — candidat au refactoring en modules (un fichier par step)
- **progress.json fichier plat** — ne supporte pas le multi-utilisateur. Migration SQLite ou Supabase nécessaire pour la prod
- **Index FAISS non versionné** — recréé à chaque démarrage, résultats potentiellement non déterministes entre sessions. Bug connu : 2 tests contract passent sur main mais échouent sur certaines branches
- **Code de reset dupliqué** — le même bloc de 8-10 lignes (reset quiz, WA, profile, states) est copié 5+ fois dans app.py. Extraire en `_reset_all_step_states()`

### Importants
- **URLs Lottie cassées** dans `core/avatar.py` — seule la première URL "neutral" est réelle, les autres sont des placeholders. Le fallback PNG fonctionne
- **Parsing synthesis fragile** — cherche des marqueurs textuels exacts. Si GPT-4o change le format, les sections ne sont pas parsées
- **Scoring WhatsApp temps réel** — basé sur des marqueurs mot-clé (élargi à ~15 par catégorie). Plus robuste qu'avant mais pas parfait. Idéal : évaluation LLM temps réel (coûteux)
- **Vouvoiement** — corrigé partout en UI, mais les quiz YAML banks peuvent encore contenir du tutoiement dans les questions. Vérifier quiz_bank/*.yaml
- **ElevenLabs permissions API** — la clé doit avoir la permission "text_to_speech". Erreur 401 sinon

### Mineurs
- **Sonnerie WhatsApp** — générée par script Python (double tonalité 440Hz+480Hz). Remplaçable par un vrai fichier audio
- **Données cascade statiques** — `cascade_analysis.py` a des données codées en dur pour quelques villes. Le DVF dynamique couvre mieux mais la cascade (réglementation, infra) reste statique
- **HeyGen voice_id** — `07ca39b243184dbcb82e7e0f0e524b21` est stocké côté HeyGen, pas compatible ElevenLabs. La voix IAXEL ElevenLabs est un clone de la voix HeyGen

---

## Commandes utiles

```bash
# Lancer l'app
streamlit run app.py

# Tests avant commit
./scripts/check_before_merge.sh

# Tester ElevenLabs
.venv/bin/python -c "
from dotenv import load_dotenv; load_dotenv()
from core.tts_elevenlabs import tts_to_bytes
audio = tts_to_bytes('Test voix IAXEL.')
print(f'OK: {len(audio)} bytes' if audio else 'ECHEC')
"

# Tester DVF
.venv/bin/python -c "
import sys; sys.path.insert(0,'.')
from training.dvf_connector import analyze_market
r = analyze_market('Marseille')
print(f\"{r['nb_transactions']} ventes, médiane {r['prix_median_m2']} €/m²\")
"

# Reset progression stagiaire
rm data/progress.json
```

---

## Workflow développement

1. `git checkout -b feat/xxx` ou `fix/xxx`
2. Implémenter
3. `./scripts/check_before_merge.sh` → tout vert
4. `git commit -m "feat: description"` ou `"fix: description"`
5. `git push`
6. Merge sur main
