# PROMPT CLAUDE CODE — IMPLÉMENTATION
# Colle ce prompt dans Claude Code (terminal VS Code) pour reprendre le travail.

Tu reprends le développement du projet "agent-immo-formateur" — formation IA agents immobiliers, Streamlit + OpenAI + FAISS RAG.

## ÉTAPE 0 — ORIENTATION

Lis ces fichiers dans cet ordre pour comprendre le projet :
1. cat CLAUDE.md
2. cat docs/HANDOFF_FOR_CLAUDE.md (si existant)
3. cat app.py
4. cat training/engine.py
5. cat training/profile_ui.py
6. cat data/progress.json

## ÉTAT : 5 PRs livrées (A→E), tout mergé sur main, checks passent.

## BUG PRIORITAIRE — Fixer AVANT tout le reste

Le bouton "Modifier mon profil" (sidebar) ne fonctionne pas. Cause : dans `_get_or_create_session()` (app.py), le skip PROFIL s'exécute même quand `ts_editing_profile=True`.

Fix :
1. Dans `_get_or_create_session()`, change le bloc skip PROFIL :
```python
# AVANT (bug)
if existing_profile and existing_profile.get("prenom"):
    if ts.current_step == Step.PROFIL:
        ts.step_data[Step.PROFIL.value] = existing_profile
        ts.current_step_index = 1

# APRÈS (fix)
if (existing_profile and existing_profile.get("prenom")
    and not st.session_state.get("ts_editing_profile", False)):
    if ts.current_step == Step.PROFIL:
        ts.step_data[Step.PROFIL.value] = existing_profile
        ts.current_step_index = 1
```

2. Dans `_advance_step()`, après `ts.advance()`, ajoute :
```python
if ts.current_step != Step.PROFIL:
    st.session_state.ts_editing_profile = False
```

3. Vérifie que `ts_editing_profile` est initialisé dans `_init_training_state()` et mis à True dans le bouton "Modifier mon profil" de la sidebar.

4. Teste : `streamlit run app.py` → Parcours guidé → sidebar → "Modifier mon profil" → doit afficher le formulaire onboarding.

5. Lance `./scripts/check_before_merge.sh` — tout doit passer.

## FICHIERS PROTÉGÉS — NE PAS MODIFIER
- core/rag.py
- core/faq_contract.py
- scripts/tests_contract_faq.py

## TESTS OBLIGATOIRES
```bash
./scripts/check_before_merge.sh
```

## APRÈS LE BUGFIX — PR F Qualité & Naturalité

Crée branche `feat/quality-naturalite` et :
1. Améliore `prompts/prompt_formateur.txt` : style coach terrain, phrases courtes, verbes d'action, pas de blabla académique
2. Améliore les prompts WhatsApp dans `training/whatsapp.py` : client plus réaliste, objections naturelles
3. Améliore TTS dans `core/tts.py` : cache, choix de voix, fallback gracieux
4. Nettoyage : supprime les fichiers .tts_*.wav/.mp3 à la racine, ajoute le pattern au .gitignore
5. Supprime agent_formateur_backup.py, agent_formateur.backup.py, agent_formateur.py.bak

Tests obligatoires à la fin.
