# Philia Summer Quest

Mentor IA de mathématiques pour enfants de 11-12 ans (révision 6e, anticipation 5e).

L'enfant part en Voyage à travers les Sept Îles de l'archipel de Syracuse, guidé par Archimède — un mentor maïeutique qui ne donne jamais la réponse mais guide vers la découverte. Chaque île conquise révèle une clé, des fragments d'une carte du trésor, et rapproche du secret final : le principe d'Archimède.

Fork du projet IAXEL (agent-immo-formateur), entièrement refondu pour Philia.

---

## Stack

- Python 3.11.14 + Streamlit
- Anthropic Claude Sonnet 4.6 (mentor maïeutique Archimède)
- Pas de RAG — le LLM s'appuie directement sur le YAML enrichi des exercices (décision D13)
- ElevenLabs (voix mentor, activé Sprint 4)
- SQLite (progression enfant)

## Lancement

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # renseigner ANTHROPIC_API_KEY et OPENAI_API_KEY
streamlit run app.py
```

## Contexte projet

Toute la documentation de conception est dans `.claude/` :

```
.claude/
├── CLAUDE.md                  # Point d'entrée — lire en premier
├── contexts/                  # ADN Archimède, produit, stack, guardrails, RGPD, Voyage
├── plans/                     # Briefs sprint
├── pedagogie/                 # Cadre progression, contenu des îles
├── production/                # Cahier des charges graphiste
├── commercial/                # Brief commercial
├── reviews/                   # Audits Reviewer de fin de sprint
└── memory/                    # Décisions, learnings, état du projet, bilan structurel
```

## État

Sprint 2 terminé — Archimède dialogue maïeutiquement, app tourne sur `localhost:8504`.
Sprint 3 en cours — Voyage visuel, 5 modes, écrans carte et avatar, prototype BD.

Voir `.claude/memory/etat-projet.md` et `.claude/memory/philia-bilan-structurel-v1.md`.
