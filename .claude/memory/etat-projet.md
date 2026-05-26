# État du Projet — Philia Summer Quest

## Sprint 1 — Bilan (terminé le 2026-05-26)

### Ce qui a été fait

**Tâche 1 — Smoke test fork IAXEL**
- venv créé, requirements installés, tous les imports résolus
- `streamlit run app.py` → HTTP 200 confirmé
- Fork déclaré sain avant toute modification

**Tâche 2 — Archivage contenu immobilier**
- 43 fichiers déplacés dans `_archive_iaxel/` (rien supprimé)
- Docs racine, données FAISS/RAG immo, modules training immo (whatsapp, dvf, marche)
- 18 modules socle vérifiés intacts : `core/`, `training/{engine,profile,progress,adapters,synthesis,pdf_export,content,chat_libre,quiz*,steps,formateur_messages}`
- `app.py` cassé sur ses imports immo — attendu, réparé au Sprint 2

**Tâche 3 — Structure `.claude/`**
- `CLAUDE.md` IAXEL archivé → `_archive_iaxel/CLAUDE_iaxel.md`
- Nouveau `.claude/CLAUDE.md` point d'entrée Philia
- Arborescence complète : `contexts/`, `plans/`, `reviews/`, `pedagogie/`, `production/`, `commercial/`, `memory/`
- 5 fichiers `contexts/` créés (guardrails rempli au Sprint 1 Tâche 4)

**Tâche 4 — Documents de conception rangés**
- `.claude/plans/` : `philia-brief-implementer-technique-1a.md` + `philia-brief-sprint-1.md`
- `.claude/pedagogie/` : cadre-progression, île-1-nombres-brisés, gamification
- `.claude/production/` : cahier-charges-graphiste
- `.claude/commercial/` : brief-commercial
- `.claude/contexts/guardrails-pedagogiques.md` : spec pédagogique v1 complète (5 modes, 8 principes, profil mentor, Bloom)
- `assets/mentor/` : 70 PNG avatars (fille/garçon × 5 archétypes)
- `data/sources_maths/` : 434 fichiers RAG maths 6e/5e (80 Mo, hors Git)

**Tâche 5 — Base SQLite**
- `data_layer/schema.sql` : 8 tables (parents, enfants, progression_iles, maitrise_concepts, superpouvoirs, sessions, mentor_etat, analogies)
- `data_layer/db.py` : `create_db()` + `get_connection()`
- `data/philia.db` créée et vérifiée (8 tables), ignorée par Git

**Tâche 6 — README + bilan**
- `README.md` réécrit pour Philia

---

### État du repo à la fin du Sprint 1

| Critère | Statut |
|---|---|
| Smoke test fork | ✅ |
| Contenu immo archivé | ✅ |
| Modules socle intacts | ✅ |
| Structure `.claude/` | ✅ |
| Documents de conception rangés | ✅ |
| `data_layer/schema.sql` + `db.py` | ✅ |
| Base `philia.db` (8 tables) | ✅ |
| README Philia | ✅ |
| Aucune clé API committée | ✅ |
| Commits propres sur `develop` | ✅ |

---

### Ce qui reste pour le Sprint 2

- Refonte `app.py` → `ui/` (point d'entrée Philia, routing, écran carte)
- Refonte `agent_formateur.py` → `pedagogie/mentor.py` (agent maïeutique)
- Premier mode pédagogique (Découverte) opérationnel
- RAG maths : indexation FAISS depuis `data/sources_maths/`
- Première session Île 1 jouable de bout en bout

---

### Décisions techniques prises au Sprint 1

- `data/sources_maths/` hors Git (80 Mo de binaires, `.gitignore`)
- `data/philia.db` hors Git (base locale, `.gitignore`)
- `_archive_iaxel/` dans le repo (conservation de l'historique IAXEL)
- `assets/mentor/` dans le repo (avatars nécessaires au Sprint 3)
