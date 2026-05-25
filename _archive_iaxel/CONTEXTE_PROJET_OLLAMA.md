# CONTEXTE PROJET — À coller au début de chaque session Ollama
# Usage : ollama run qwen3:8b → colle ce bloc → puis pose ta question

Projet : "agent-immo-formateur" — App Streamlit de formation IA pour agents immobiliers.
Stack : Python 3.12, Streamlit, OpenAI API, FAISS RAG, fpdf2.
Repo GitHub : appIAtlani/agent-immo-formateur

## ARCHITECTURE

State machine avec 2 séquences :
- Jour 1 : PROFIL → MINI_COURS → QUESTIONS_RAG → COURS_CLES → QUIZ → DEBRIEF → SYNTHESE
- Jour 2+ : WHATSAPP → DEBRIEF_WA → MINI_COURS → QUESTIONS_RAG → COURS_CLES → QUIZ → DEBRIEF_QUIZ → SYNTHESE

## FICHIERS PRINCIPAUX

- app.py : routing Streamlit, UI par step, sidebar navigation
- training/engine.py : TrainingSession state machine, sérialisation
- training/steps.py : Step enum + séquences jour1/jour2+
- training/progress.py : load/save data/progress.json
- training/content.py : 20 thèmes pédagogiques, rotation 104 sessions
- training/profile.py + profile_ui.py : UserProfile, onboarding 3 étapes
- training/adapters.py : adaptation difficulté quiz/ton WhatsApp/style formateur
- training/quiz.py + quiz_ui.py : quiz Kahoot, 39 questions YAML, scoring
- training/whatsapp.py + whatsapp_ui.py : roleplay client IA, 4 scénarios YAML
- training/synthesis.py : synthèse IA (résumé, points forts/faibles, actions)
- training/pdf_export.py : export PDF fpdf2
- core/rag.py : FAISS + rerank hybride ← NE PAS MODIFIER
- core/faq_contract.py : FAQ contract strict ← NE PAS MODIFIER

## BUG OUVERT

Bouton "Modifier mon profil" boucle. Cause : dans app.py, _get_or_create_session() skip PROFIL même quand ts_editing_profile=True.
Fix : ajouter `and not st.session_state.get("ts_editing_profile", False)` dans la condition du skip PROFIL.

## TRAVAIL EN COURS — PR F Qualité

1. Améliorer prompts formateur : style coach terrain, phrases courtes, verbes d'action
2. Améliorer prompts WhatsApp : objections client plus réalistes
3. TTS : cache, choix voix, fallback
4. Réduire les "Non couvert" inutiles

## RÈGLES

- Tests obligatoires : ./scripts/check_before_merge.sh
- NE PAS MODIFIER : core/rag.py, core/faq_contract.py, scripts/tests_contract_faq.py
- Style formateur : coach terrain, pas académique
