# CONTEXTE — Stack Technique Philia Summer Quest

**Choix techniques et contraintes. Document de contexte pour Claude Code et l'Architecte.**

---

## LA STACK

| Couche | Technologie | Origine |
|---|---|---|
| Interface | Streamlit (Python) | Repris d'IAXEL |
| Langage | Python 3 | Repris d'IAXEL |
| Base de données | SQLite | Nouveau (Sprint 1) |
| RAG | FAISS | Repris d'IAXEL, contenu régénéré |
| Embeddings RAG | OpenAI text-embedding-3-small | Repris d'IAXEL |
| Synthèse vocale | ElevenLabs + cache MD5 | Repris d'IAXEL |
| LLM | API Anthropic | Repris d'IAXEL |
| Paiement | Stripe | Nouveau (Sprint 4) |
| Email | SendGrid | Nouveau (Sprint 4) |

## POURQUOI STREAMLIT

Streamlit a été retenu pour la rapidité de développement et parce que le fondateur le maîtrise (via IAXEL). C'est un choix assumé pour le MVP d'été — un produit saisonnier de 7 semaines ne justifie pas une stack lourde.

**Forces exploitées** : chat natif fluide, gestion d'état simple (`session_state`), affichage rapide d'images et GIFs, intégration Plotly, simplicité de maintenance.

**Contraintes acceptées** : pas de drag & drop complexe, pas de parallax, animations limitées aux GIFs et transitions CSS. L'immersion vient de la narration, du feedback visuel et de la personnalisation — pas de mécaniques de jeu vidéo lourdes.

**Note d'avenir** : le produit Philia année scolaire (rentrée 2026) pourra justifier une migration vers une PWA React. Le Summer Quest reste en Streamlit.

## RÈGLES TECHNIQUES STRUCTURANTES

**Persistance** : SQLite, sauvegarde après chaque action critique (fin de session, validation de concept, franchissement de palier). Jamais de perte de données si l'enfant ferme l'onglet. Le `progress.json` d'IAXEL est remplacé par une vraie base.

**Anti-latence Streamlit** : Streamlit réexécute le script à chaque interaction. Les assets (images d'îles, mentor) sont chargés via `@st.cache_data` / `@st.cache_resource`. Une image ne se recharge jamais deux fois. C'est essentiel au confort de l'enfant.

**Géométrie (île 6, v1.2)** : pas de dessin libre. Figures pré-produites analysées par l'enfant (Option A) + manipulations Plotly là où le déplacement de points apporte (Option B). Décision actée.

## CE QUI EST HORS GIT

- `data/sources_maths/` — 80 Mo de binaires sources du RAG, gardés en local
- `data/philia.db` — base locale, contient des données d'enfants
- `.env` — clés API
- `.venv/` — environnement virtuel

## STRUCTURE DU REPO

Voir le détail dans `.claude/plans/philia-brief-implementer-technique-1a.md`, section 1. Les dossiers clés : `core/` (RAG, TTS, LLM — socle IAXEL), `data_layer/` (SQLite), `pedagogie/` (mentor, modes), `jeu/` (îles, élévation, radar), `ui/` (écrans), `commerce/` (paywall, Stripe), `compliance/` (RGPD).

## CE QUI EST REPRIS D'IAXEL

Socle réutilisé tel quel ou adapté : architecture RAG FAISS, système TTS avec cache, wrapper LLM, state machine de session, gestion de profil et progression, export PDF, tests pre-commit. Le contenu change (immobilier → maths), le moteur reste.

---

*Contexte technique Philia Summer Quest. À tenir à jour si la stack évolue.*
