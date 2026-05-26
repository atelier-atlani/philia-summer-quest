# Philia Summer Quest

Mentor IA de mathématiques pour enfants de 11-12 ans (révision 6e, anticipation 5e).

L'enfant fait s'élever des îles en maîtrisant les maths, guidé par Archimède — un mentor maïeutique qui ne donne jamais la réponse mais guide vers la découverte.

Fork du projet IAXEL (agent-immo-formateur).

---

## Stack

- Python 3.12 + Streamlit
- OpenAI GPT-4o (mentor maïeutique)
- FAISS (RAG sur contenus maths)
- ElevenLabs (voix mentor + moments-clés)
- SQLite (progression enfant)

## Lancement

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # renseigner les clés API
streamlit run app.py
```

## Contexte projet

Toute la documentation de conception est dans `.claude/` :

```
.claude/
├── CLAUDE.md                  # Point d'entrée
├── contexts/                  # Produit, stack, guardrails pédagogiques, RGPD
├── plans/                     # Briefs sprint + spec technique
├── pedagogie/                 # Cadre progression, modèle île, gamification
├── production/                # Cahier des charges graphiste
├── commercial/                # Brief commercial
└── memory/                    # Décisions, learnings, état du projet
```

## État

Sprint 1 terminé — fondations posées. Voir `.claude/memory/etat-projet.md`.
