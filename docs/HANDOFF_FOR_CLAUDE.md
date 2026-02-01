Agent IA Formateur Immobilier — Synthèse Projet & Reprise
1. Vision produit

Objectif
Créer une application de formation immersive pour agents immobiliers, basée sur un formateur IA terrain, utilisée 1h par jour pendant 1 an.

Cible initiale :

50 agences

~150 agents immobiliers

Contrat annuel

Le formateur IA doit :

transmettre du contenu utile terrain (pas de théorie abstraite),

faire pratiquer (mises en situation),

évaluer (quiz, scoring),

débriefer,

produire une synthèse quotidienne (PDF + “à faire demain”).

Le positionnement est coach terrain quotidien, pas “cours magistral”.

2. Logique pédagogique (actée)
Jour 1 — Onboarding (version corrigée)

Accueil + profil stagiaire (3–5 min)

Mini-cours magistral marché/copro (5–8 min)

1–2 questions + réponses RAG (~5 min)

Cours “Clés” (RAG actuel : vendeur / acquéreur / management) (10–12 min)

Quiz type Kahoot (8–12 min)

Débrief quiz + score (~5 min)

Synthèse + PDF + “à faire demain” (3–5 min)

✅ Pas de WhatsApp J+1 le jour 1

Jour 2+ — Rythme standard

Mise en situation WhatsApp J+1 (8–12 min) basée sur le cours “Clés” de la veille

Débrief + score (5 min)

Mini-cours magistral marché/copro (5–7 min)

1–2 questions RAG (~5 min)

Cours “Clés” du jour (10–12 min)

Quiz Kahoot (8–12 min)

Débrief + comparaison scores WhatsApp vs Quiz

Synthèse + PDF + “à faire demain”

3. Architecture technique actuelle (stabilisée)
A. Application

agent_formateur.py : point central CLI

multi-modes : Formateur, FAQ, Audit, Memo, Plan, Parcours guidé, TTS

prompts séparés

app.py : interface Streamlit (parcours guidé + audio)

B. RAG (Retrieval Augmented Generation)

core/rag.py : cœur du système

Données :

base_connaissances.json

faiss_index.bin

faiss_metadata.json

Init unique via rag.init(client)

Recherche :

FAISS + rerank lexical simple

trace complète accessible (get_last_trace())

C. Garde-fous anti-hallucination (FAQ)

Format contractuel strict :
1 à 5 sections numérotées

Hors-scope → réponse exacte :
"Non couvert par les extraits fournis."

Section 5 = une seule ligne d’action

Gate _faq_is_covered_by_context() actif

D. OpenAI helper

gestion des réponses tronquées (finish_reason == length)

continuation automatique

max_tokens configurable

E. Tests & debug

scripts/tests_smoke.py

scripts/tests_contract_faq.py

RAG_DEBUG=1 pour inspection contrôlée

4. Ce qui est déjà réalisé (figé)

Qualité RAG stable (FAISS + caps + rerank simple)

FAQ contractuelle respectée

Infra propre (.env, .gitignore)

Branches feature déjà mergées sur main

5. Évolutions pédagogiques actées (à implémenter)

Mini-cours marché/copro (nouveau corpus)

Séquence WhatsApp J+1 (MVP CLI → UI plus tard)

Quiz dynamique type Kahoot

Scoring + débrief + PDF quotidien

Comparaison scores mise en situation / quiz

6. Priorités de développement (roadmap MVP)
Priorité 1 — Module 1 / 1h complète

Orchestration via YAML (modules/module_01.yaml)

Lien clair jour N / jour N+1

Priorité 2 — Quiz engine

QCM depuis contexte RAG

scoring + feedback

Priorité 3 — WhatsApp simulation

MVP CLI

dialogue + scoring + débrief

Priorité 4 — PDF de synthèse

résumé

scores

“à faire demain”

Priorité 5 — Nouveau RAG marché/copro

corpus séparé ou filtré par metadata

Priorité 6 — Refactor léger

core/training_engine.py

prompts centralisés

logs structurés

7. Contraintes de continuité (non-régression)

Ne pas casser :

tests_smoke.py

tests_contract_faq.py

RAG volontairement simple (lisible, explicable)

Hors-scope copro/fiscalité maintenu par contrat

Pas de LangGraph / multi-agents pour l’instant

8. Pack reprise développeur / IA
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=...
python agent_formateur.py
python scripts/tests_smoke.py
python scripts/tests_contract_faq.py
