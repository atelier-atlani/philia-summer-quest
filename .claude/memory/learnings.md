# Learnings — Philia Summer Quest

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
