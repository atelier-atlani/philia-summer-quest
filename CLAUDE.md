# Agent IA Formateur – Vente Immobilière Terrain

## 1. Nature et vision du projet

### 🎯 Objectif global
Le projet Agent IA Formateur Immobilier vise à créer un formateur IA immersif, dédié aux agents immobiliers, capable de les accompagner 1 heure par jour sur une durée longue (contrat annuel) afin de :
- améliorer leurs décisions commerciales terrain,
- renforcer leur posture face aux vendeurs,
- développer des réflexes professionnels efficaces,
- transformer la connaissance en comportements observables sur le terrain.

Le produit est destiné à être déployé à l'échelle de réseaux / franchises immobilières (≈ 50 agences, ≈ 150 agents dans la première phase).

### 🧠 Positionnement pédagogique
Le projet ne consiste PAS à fournir :
- un chatbot générique,
- un simple LMS,
- une FAQ améliorée.

Il consiste à proposer : **un formateur terrain personnel, incarné, interactif, présent au quotidien**, capable de former par la pratique, le dialogue, le jeu de rôle et le feedback.

La pédagogie est **terrain-first**, orientée action, décision et posture.

---

## 2. Charte officielle du formateur IA (FONDATION)

Principes clés :
- Formateur senior terrain, coach individuel
- Bienveillant mais exigeant
- Jamais théorique sans application
- Toujours structuré : enjeu → structure → cas → phrases → ancrage
- Cas pratiques obligatoires
- Langage naturel, oral, crédible
- Ancrage terrain systématique
- **Respect strict des supports de formation (RAG, pas d'invention)**

👉 **Toute évolution du projet doit respecter cette charte.**

---

## 3. Architecture technique

### Stack
- Python 3.12
- Streamlit (interface)
- RAG avec FAISS (base de connaissances PDF)
- OpenAI API (TTS + LLM)

### Fichiers principaux
- `agent_formateur.py` : Cœur pédagogique (repondre_comme_formateur, repondre_faq, generer_fiche_memo, generer_plan_entretien)
- `app.py` : Interface Streamlit
- `core/rag.py` : Logique RAG hybride (semantic + lexical)
- `prompts/prompt_formateur.txt` : Prompt système du formateur

### Modes utilisateur
- Parcours guidé
- Formateur explicatif
- FAQ métier
- Fiche mémo
- Plan d'entretien

---

## 4. Choix technologiques (À RESPECTER)

- ❌ Pas de LangGraph actuellement
- ❌ Pas de multi-agents autonomes
- ✅ Orchestration contrôlée par le code
- ✅ Une seule entité pédagogique cohérente
- ✅ Simplicité > sophistication

---

## 5. Priorités de développement

1. **Consolidation pédagogique** : Auditer les réponses, standardiser les formats
2. **Parcours annuel** : Structurer 12 mois de formation
3. **Industrialisation** : Séparer backend/frontend, multi-agences, auth
4. **Immersion** : Avatar 2D, sync lèvres/voix

---

## 6. Commandes utiles
```bash
streamlit run app.py          # Lancer l'application
python3 build_index.py        # Reconstruire l'index FAISS
```

---

## 7. Instructions pour l'IA

👉 Ne jamais casser la charte du formateur IA
👉 Toujours privilégier la pédagogie terrain à la performance technique
👉 Toute nouvelle fonctionnalité doit renforcer :
- l'action terrain,
- la prise de décision,
- l'autonomie de l'agent

**La technologie est un moyen, jamais une fin.**
