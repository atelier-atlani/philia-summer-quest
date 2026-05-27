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
