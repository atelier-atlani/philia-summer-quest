# GUIDE COMPLET — Travailler hors-ligne avec Ollama + Continue
## Expliqué pas à pas pour agent-immo-formateur

---

## LES 2 FAÇONS DE TRAVAILLER

Tu as **2 outils** qui remplacent Claude pendant 15 jours :

| Outil | Remplace quoi | Pour quoi faire |
|---|---|---|
| `ollama run qwen3:8b` dans le **Terminal Mac** | Claude.ai | Réfléchir, architecture, design, debug |
| **Continue** dans **VS Code** | Claude Code | Coder, modifier du code, autocomplétion |

---

## MÉTHODE 1 — Chat Terminal (Architecture / Design / Debug)

### Comment lancer

Ouvre le **Terminal** de ton Mac (pas celui de VS Code, le vrai Terminal) :
```bash
ollama run qwen3:8b
```

Tu es maintenant dans un chat. Tu tapes ta question, Entrée, il répond.
Pour quitter : tape `/bye`

### Le problème : il ne connaît pas ton projet

Contrairement à Claude qui avait tout le contexte, Qwen part de zéro à chaque conversation.
**Tu dois lui donner le contexte toi-même.**

### Comment lui donner le contexte — 3 méthodes

#### Méthode A — Le "prompt de contexte" (la plus simple)

Au début de chaque session, colle un résumé de ton projet.
Copie-colle ce bloc tel quel au début de chaque chat :

```
Tu es l'architecte du projet "agent-immo-formateur".
C'est une app Streamlit (Python 3.12) de formation IA pour agents immobiliers.
Stack : Streamlit, OpenAI API, FAISS RAG, fpdf2.

L'app a une state machine avec :
- Jour 1 : PROFIL → MINI_COURS → QUESTIONS_RAG → COURS_CLES → QUIZ → DEBRIEF → SYNTHESE
- Jour 2+ : WHATSAPP → DEBRIEF_WA → MINI_COURS → QUESTIONS_RAG → COURS_CLES → QUIZ → DEBRIEF_QUIZ → SYNTHESE

Fichiers principaux :
- app.py : routing + UI Streamlit
- training/engine.py : state machine TrainingSession
- training/quiz.py + quiz_ui.py : quiz Kahoot
- training/whatsapp.py + whatsapp_ui.py : roleplay WhatsApp
- training/synthesis.py + pdf_export.py : synthèse + PDF
- training/profile.py + profile_ui.py : profil utilisateur
- core/rag.py : RAG FAISS (NE PAS MODIFIER)
```

Puis pose ta question normalement après.

#### Méthode B — Coller du code directement

Tu veux de l'aide sur un fichier ? Copie-colle le code dans le chat :

```
Voici mon fichier training/engine.py :

[COLLE LE CODE ICI]

Question : comment je peux ajouter un step REVISION entre QUIZ et DEBRIEF ?
```

⚠️ Limite : Qwen 3 8B a une fenêtre de ~32K tokens. Un fichier de 200 lignes passe facilement. 
Évite de coller 5 fichiers d'un coup — un à la fois.

#### Méthode C — Lui faire lire un fichier (astuce avancée)

Tu peux envoyer le contenu d'un fichier directement dans le prompt :

```bash
cat training/engine.py | ollama run qwen3:8b "Explique ce code et trouve les bugs potentiels"
```

Ou pour plusieurs fichiers :

```bash
echo "=== app.py ===" && cat app.py && echo "=== engine.py ===" && cat training/engine.py | ollama run qwen3:8b "Voici 2 fichiers de mon projet. Explique le flow principal."
```

### Exemples concrets de prompts

**Pour l'architecture :**
```
[colle le contexte projet]

Je veux ajouter un dashboard de progression qui montre :
- Les scores quiz sur les 10 dernières sessions
- Un graphique de progression
- Les thèmes les plus faibles

Quel design tu proposes ? Quels fichiers créer/modifier ?
```

**Pour le debug :**
```
Voici mon code app.py (lignes 90-120) :

[colle le code]

Quand je clique "Modifier profil", ça boucle au lieu d'afficher le formulaire.
Le flag ts_editing_profile est mis à True mais le skip PROFIL l'écrase.
Comment fixer ça ?
```

**Pour un plan de PR :**
```
[colle le contexte projet]

Je veux améliorer les prompts du formateur pour un style plus "coach terrain" :
- Phrases courtes
- Verbes d'action
- Pas de blabla académique

Fais-moi un plan détaillé : quels fichiers modifier, dans quel ordre, quoi changer.
```

---

## MÉTHODE 2 — Continue dans VS Code (Coder)

### Les 4 façons d'utiliser Continue

#### 1. Chat (Cmd+L) — Poser des questions sur le code

- Ouvre un fichier dans VS Code
- **Sélectionne du code** avec ta souris
- Tape **Cmd+L**
- Le code sélectionné est envoyé dans le chat Continue (sidebar)
- Tape ta question : "Explique cette fonction" / "Trouve le bug" / "Refactorise"
- Il répond dans le chat

**Exemple :**
1. Ouvre `training/quiz.py`
2. Sélectionne la classe `QuizSession`
3. `Cmd+L`
4. Tape : "Comment ajouter un timer de 30 secondes par question ?"

#### 2. Édition inline (Cmd+I) — Modifier le code sur place

C'est le plus puissant — le modèle modifie TON code directement.

1. Ouvre un fichier
2. **Sélectionne les lignes à modifier**
3. Tape **Cmd+I**
4. Un champ de texte apparaît dans le code
5. Tape une instruction : "Ajoute la gestion d'erreur" / "Traduis les commentaires en français"
6. **Entrée**
7. Le modèle propose une modification → **Accepte** (✓) ou **Refuse** (✗)

**Exemple :**
1. Ouvre `training/whatsapp.py`
2. Sélectionne la fonction `generate_client_reply()`
3. `Cmd+I`
4. Tape : "Rends les objections du client plus réalistes et naturelles"
5. Il modifie le code → tu vois un diff vert/rouge → accepte ou refuse

#### 3. Autocomplétion (Tab) — Pendant que tu tapes

- Quand tu écris du code, des **suggestions grises** apparaissent
- Tape **Tab** pour accepter
- C'est automatique, rien à configurer

**Exemple :**
1. Ouvre un fichier Python
2. Tape : `def calculate_quiz_score(`
3. Le modèle suggère automatiquement les paramètres et le corps de la fonction
4. Tab pour accepter

#### 4. Chat en plein écran

Si la sidebar est trop petite :
- Clic droit sur l'onglet Continue → **"Move to Editor Area"**
- Ou `Cmd+Shift+P` → "Continue: New Chat in Editor"

---

## MÉTHODE 3 — Combiner Terminal + VS Code (la plus efficace)

### Workflow recommandé pour une journée type

```
MATIN — Réflexion (Terminal)
│
│  ollama run qwen3:8b
│  → "Je veux implémenter X. Fais-moi le plan."
│  → Il te donne le design + fichiers à modifier
│  → /bye
│
APRÈS-MIDI — Implémentation (VS Code + Continue)
│
│  Ouvre les fichiers indiqués par le plan
│  → Cmd+I pour modifier le code
│  → Cmd+L pour poser des questions
│  → Tab pour l'autocomplétion
│  → Teste : streamlit run app.py
│
SOIR — Commit
│
│  git add -A
│  git commit -m "feat: description"
│  (git push quand tu retrouves internet)
```

### Astuce : sauvegarder les conversations importantes

Le chat Ollama dans le terminal disparaît quand tu fais /bye.
Pour garder une trace :

```bash
ollama run qwen3:8b 2>&1 | tee ~/conversations/session_$(date +%Y%m%d_%H%M).txt
```

Ça enregistre toute la conversation dans un fichier.
Crée le dossier d'abord : `mkdir -p ~/conversations`

---

## RÉSUMÉ DES RACCOURCIS

| Action | Raccourci / Commande |
|---|---|
| Chat architecture (terminal) | `ollama run qwen3:8b` |
| Quitter le chat terminal | `/bye` |
| Envoyer un fichier au chat | `cat fichier.py \| ollama run qwen3:8b "ta question"` |
| Chat dans VS Code | `Cmd+L` |
| Édition inline | `Cmd+I` (sélectionne du code d'abord) |
| Autocomplétion | `Tab` |
| Chat plein écran | `Cmd+Shift+P` → "Continue: New Chat in Editor" |
| Changer de modèle | Menu déroulant en haut du chat Continue |

---

## CHANGER DE MODÈLE DANS CONTINUE

En haut du chat Continue, tu as un **menu déroulant** avec tes modèles :
- **Qwen 3 8B** → pour les questions générales, l'architecture, le debug
- **Qwen 2.5 Coder 7B** → pour écrire/modifier du code (meilleur en code pur)

Utilise Coder 7B quand tu fais du `Cmd+I` (édition de code).
Utilise Qwen 3 8B quand tu poses des questions dans le chat.

---

## CE QUE QWEN NE FAIT PAS AUSSI BIEN QUE CLAUDE

Sois réaliste sur les limites :

- **Gros refactors multi-fichiers** → Fais-les fichier par fichier, pas tout d'un coup
- **Contexte long** → Ne colle pas plus de 300 lignes à la fois
- **Architecture complexe** → Donne plus de détails dans tes prompts, sois très précis
- **Qualité des réponses** → Parfois il faut reformuler ou poser la question autrement

**Règle d'or** : si Qwen te donne une réponse moyenne, précise ta question. 
Exemple mauvais : "Améliore ce code"
Exemple bon : "Refactorise cette fonction pour séparer la logique de scoring du rendering Streamlit"

---

## CHECKLIST AVANT DE COUPER INTERNET

- [ ] `git push` de tout ton code sur GitHub
- [ ] Ollama fonctionne : `ollama list` montre 3 modèles
- [ ] Continue fonctionne dans VS Code sans wifi
- [ ] Tu as le fichier PROMPT_CLAUDE_AI_SONNET.md dans ton repo (pour la reprise)
- [ ] Tu as le fichier PROMPT_CLAUDE_CODE.md dans ton repo (pour la reprise)
- [ ] Tu as ce guide (GUIDE_TRAVAIL_LOCAL_OLLAMA.md) accessible en local

Copie ce guide dans ton projet :
```bash
cp ~/Downloads/GUIDE_TRAVAIL_LOCAL_OLLAMA.md docs/GUIDE_TRAVAIL_LOCAL_OLLAMA.md
```
