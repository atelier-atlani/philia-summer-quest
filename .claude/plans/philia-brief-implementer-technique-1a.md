# PHILIA SUMMER QUEST — Brief Implementer Technique v1.0

**Document 1A du Chantier 1. Spec de développement exécutable par Claude Code.**
**Fork réel du code IAXEL (disponible local + GitHub).**
**Stack : Streamlit / Python / SQLite / FAISS / ElevenLabs.**
**Horizon : 6 semaines — MVP livrable 1er juillet 2026 (3 îles).**

---

## 0. COMMENT UTILISER CE BRIEF

Ce brief se découpe en 6 sprints d'une semaine. Pour chaque sprint, tu (le fondateur) extrais la section correspondante, tu la déposes dans `.claude/plans/sprint-X.md`, et tu la donnes à Claude Code en mode Implementer.

Claude Code ne code jamais hors du périmètre du sprint courant. À chaque fin de sprint : test E2E + audit Reviewer.

---

## 1. ARCHITECTURE CIBLE DE L'APPLICATION

Structure du repo `philia-summer-quest/` après fork et adaptation :

```
philia-summer-quest/
├── app.py                          # Point d'entrée Streamlit, routing
├── requirements.txt                # + stripe, sendgrid, pydantic, Pillow
├── .claude/                        # Cerveau projet (voir workflow 1B)
│
├── config/
│   └── constants.py                # Couleurs Philia, niveaux, limites session
│
├── core/
│   ├── rag.py                      # FAISS RAG — REPRIS d'IAXEL tel quel
│   ├── tts.py                      # TTS + cache MD5 — REPRIS, étendu 3 couches
│   ├── sanitizer.py                # Nettoyage inputs — REPRIS tel quel
│   └── llm_client.py               # Wrapper API Anthropic — REPRIS d'IAXEL
│
├── data_layer/
│   ├── db.py                       # SQLite — accès base, NOUVEAU
│   ├── schema.sql                  # Schéma base de données, NOUVEAU
│   ├── profil.py                   # CRUD profil enfant, ADAPTÉ de profile.py
│   └── progression.py              # CRUD progression/élévation, ADAPTÉ
│
├── pedagogie/
│   ├── mentor.py                   # Agent mentor — REFONTE de agent_formateur.py
│   ├── mode_router.py              # Choix du mode pédagogique, NOUVEAU
│   ├── modes.py                    # Enum 5 modes + transitions, NOUVEAU
│   ├── mentor_contract.py          # Contrat sortie LLM, ADAPTÉ de faq_contract.py
│   └── session_engine.py           # State machine de session, REFONTE de engine.py
│
├── jeu/
│   ├── iles.py                     # Gestion des 7 îles + élévation, NOUVEAU
│   ├── elevation.py                # Logique des paliers, cristaux, NOUVEAU
│   ├── mentor_evolutif.py          # Avatar évolutif + expressions, NOUVEAU
│   ├── radar.py                    # Radar 6 superpouvoirs (Plotly), NOUVEAU
│   ├── rite.py                     # Rite d'Élévation (escape game), NOUVEAU
│   └── recompenses.py              # Cristaux, badges, révélations, NOUVEAU
│
├── ui/
│   ├── ecran_ile.py                # Écran principal — île + situations
│   ├── ecran_chat.py               # Zone chat Archimède
│   ├── ecran_carte.py              # Carte des 7 îles
│   ├── sidebar.py                  # Avatar + artefacts + élévation globale
│   ├── onboarding.py               # Création profil enfant + RGPD
│   └── dashboard_parent.py         # Espace parent, NOUVEAU
│
├── commerce/
│   ├── paywall.py                  # 2 tiers (Gratuit / Premium), NOUVEAU
│   └── stripe_integration.py       # Paiement + webhooks, NOUVEAU
│
├── compliance/
│   └── rgpd.py                     # Consentement parental < 15 ans, NOUVEAU
│
├── parent/
│   ├── bilan_hebdo.py              # Génération bilan PDF, ADAPTÉ de pdf_export.py
│   └── email.py                    # Envoi email parent (SendGrid), NOUVEAU
│
├── prompts/
│   └── mentor/                     # Prompts des 5 modes — NOUVEAUX
│
├── data/
│   ├── philia.db                   # Base SQLite
│   ├── base_connaissances_maths.json  # RAG maths, NOUVEAU contenu
│   ├── rag_index/                  # Index FAISS régénéré
│   ├── iles/                       # YAML des 7 îles
│   └── tts_cache/                  # Cache audio
│
├── assets/
│   ├── iles/                       # Illustrations îles (4 états × 7)
│   ├── mentor/                     # Archimède + expressions
│   ├── ui/                         # Icônes, badges, cristaux
│   └── sounds/                     # Sons de célébration
│
└── scripts/
    ├── build_rag_index.py          # Indexation FAISS, ADAPTÉ
    ├── ingest_content.py           # Pipeline PDF → YAML, NOUVEAU
    └── check_before_merge.sh       # Tests pre-commit, ADAPTÉ
```

---

## 2. MODÈLE DE DONNÉES SQLITE

Remplacement du `progress.json` d'IAXEL par une vraie base SQLite. Schéma `data_layer/schema.sql` :

```sql
-- Profil de l'enfant
CREATE TABLE enfants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prenom TEXT NOT NULL,
    age INTEGER,
    classe TEXT,                          -- "6e" ou "entrée 5e"
    style_mentor TEXT,                    -- style d'Archimède choisi
    date_creation TEXT,
    parent_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES parents(id)
);

-- Parent (acheteur, titulaire RGPD)
CREATE TABLE parents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    tier TEXT DEFAULT 'gratuit',          -- 'gratuit' | 'premium'
    stripe_customer_id TEXT,
    rgpd_consent INTEGER DEFAULT 0,        -- 0/1 consentement validé
    rgpd_consent_date TEXT,
    date_creation TEXT
);

-- Progression par île
CREATE TABLE progression_iles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    ile_id TEXT,                          -- "ile_1", "ile_2"...
    niveau_elevation INTEGER DEFAULT 0,    -- 0 à 3
    cristaux_obtenus TEXT,                 -- JSON liste des cristaux
    rite_reussi INTEGER DEFAULT 0,
    date_derniere_activite TEXT,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

-- Maîtrise par concept
CREATE TABLE maitrise_concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    concept_id TEXT,                      -- "C1", "C2"... par île
    ile_id TEXT,
    statut TEXT DEFAULT 'non_aborde',      -- non_aborde | decouvert | pratique | valide
    score_feynman INTEGER,                 -- validation profondeur 0-100
    date_validation TEXT,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

-- Radar des superpouvoirs
CREATE TABLE superpouvoirs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    maieutique INTEGER DEFAULT 0,
    transfert INTEGER DEFAULT 0,
    perseverance INTEGER DEFAULT 0,
    clarte INTEGER DEFAULT 0,
    creativite INTEGER DEFAULT 0,
    metacognition INTEGER DEFAULT 0,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

-- Historique de sessions (pour bilan parent)
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    ile_id TEXT,
    date TEXT,
    duree_minutes INTEGER,
    concepts_travailles TEXT,              -- JSON
    expressions_mentor TEXT,               -- JSON compteur émotions
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

-- Mentor évolutif
CREATE TABLE mentor_etat (
    enfant_id INTEGER PRIMARY KEY,
    niveau_mentor INTEGER DEFAULT 1,       -- 1 Jeune Guide, 2 Confirmé, 3 Grand Sage
    elements_debloques TEXT,               -- JSON liste
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);

-- Collection d'analogies (v1.1, table créée dès le départ)
CREATE TABLE analogies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enfant_id INTEGER,
    concept_id TEXT,
    texte_analogie TEXT,
    date_creation TEXT,
    FOREIGN KEY (enfant_id) REFERENCES enfants(id)
);
```

**Règle de persistance** : sauvegarde après chaque action critique (fin de session, validation de concept, franchissement de palier). Jamais de perte de données si l'enfant ferme l'onglet.

**Migration de schéma** : un fichier `data_layer/migrations/` avec les évolutions numérotées. Si le schéma change en sprint 4, on ajoute une migration, on ne casse pas les profils existants.

---

## 3. STRUCTURE `session_state` STREAMLIT

Streamlit réexécute le script à chaque interaction. Le `session_state` maintient l'état entre les reruns. Clés principales :

```python
# Identité et navigation
st.session_state.enfant_id          # int, l'enfant connecté
st.session_state.parent_id          # int
st.session_state.ecran_courant      # "carte" | "ile" | "session" | "rite" | "parent"
st.session_state.ile_courante       # "ile_1"...

# Session pédagogique en cours
st.session_state.session_active     # dict — concept, mode, étape, historique chat
st.session_state.mode_courant       # "decouverte" | "pratique" | ...
st.session_state.historique_chat    # liste des messages Archimède <-> enfant

# Cache d'affichage (éviter rechargements)
st.session_state.profil_cache       # profil enfant chargé
st.session_state.progression_cache  # progression chargée
```

**Règle anti-latence** : les images d'îles, le mentor, les assets sont chargés via `@st.cache_data` ou `@st.cache_resource`. Une image ne se recharge jamais deux fois. C'est ce qui rend l'expérience fluide pour l'enfant malgré le modèle de rerun de Streamlit.

---

## 4. LES 6 SPRINTS

### SPRINT 1 (semaine 1) — Fork, fondations, première session maïeutique

**Objectif** : l'app forkée tourne, la base SQLite existe, une session de découverte sur les fractions fonctionne en maïeutique.

Livrables :
- [ ] Fork d'IAXEL → repo `philia-summer-quest`, smoke test (l'app IAXEL forkée tourne)
- [ ] `.claude/` initialisé (CLAUDE.md + contexts)
- [ ] Base SQLite : `schema.sql` créé, `data_layer/db.py` opérationnel
- [ ] `core/rag.py`, `core/tts.py`, `core/sanitizer.py`, `core/llm_client.py` repris d'IAXEL, vérifiés
- [ ] `pedagogie/mentor.py` : refonte de l'agent — prompt mentor maïeutique de base
- [ ] `prompts/mentor/mode_decouverte.txt` + `_shared_guardrails.txt` rédigés
- [ ] `pedagogie/mentor_contract.py` : contrat de sortie JSON du mentor
- [ ] RAG : `base_connaissances_maths.json` avec contenu Île 1 (fractions), index FAISS construit
- [ ] **Test E2E** : un enfant fait une session Découverte sur "le sens d'une fraction", Archimède ne donne jamais la réponse

Critère de validation : `streamlit run app.py` → parcours d'une session Découverte fractions du début à la fin. Test de stress maïeutique : un testeur insiste 10 fois pour avoir la réponse, Archimède tient.

### SPRINT 2 (semaine 2) — Les 5 modes pédagogiques + state machine

**Objectif** : l'architecture pédagogique complète fonctionne sur l'Île 1.

Livrables :
- [ ] `prompts/mentor/` : les 5 modes rédigés + meta_router + _shared_persona + _shared_output_contract
- [ ] `pedagogie/modes.py` : enum des 5 modes + transitions autorisées
- [ ] `pedagogie/mode_router.py` : choisit le mode selon le contexte
- [ ] `pedagogie/session_engine.py` : state machine refondue
- [ ] `data_layer/progression.py` + `maitrise_concepts` : suivi de la validation des concepts
- [ ] Logique d'élévation de base : `jeu/elevation.py` — cristaux et paliers
- [ ] **Test E2E** : sur l'Île 1, un enfant traverse Découverte → Pratique → Validation, un concept passe en "validé", un cristal est placé

Critère de validation : les 5 modes s'activent correctement, la validation Feynman fonctionne, l'élévation de l'île répond aux validations.

### SPRINT 3 (semaine 3) — Le jeu : îles, mentor évolutif, radar, carte

**Objectif** : l'enveloppe de jeu est en place et visible.

Livrables :
- [ ] `jeu/iles.py` : gestion des îles, chargement YAML
- [ ] `jeu/mentor_evolutif.py` : avatar + expressions (intégration assets graphiste)
- [ ] `jeu/radar.py` : radar 6 superpouvoirs en Plotly
- [ ] `jeu/recompenses.py` : cristaux, badges, révélations de lore
- [ ] `ui/ecran_ile.py`, `ui/ecran_carte.py`, `ui/sidebar.py` : les écrans de jeu
- [ ] `ui/ecran_chat.py` : zone chat Archimède intégrée
- [ ] Système d'élévation visuelle : l'île change d'image selon le niveau
- [ ] **Test E2E** : un enfant voit son île, joue une session, voit son île monter d'un palier, son radar progresser

Critère de validation : l'expérience de jeu est lisible et cohérente. Retours de 3-5 enfants testeurs.

### SPRINT 4 (semaine 4) — Voix, paywall, RGPD

**Objectif** : le produit est commercialisable et conforme.

Livrables :
- [ ] `core/tts.py` étendu : voix aux moments-clés (3 couches A/B/C)
- [ ] `commerce/paywall.py` : 2 tiers (Gratuit / Premium 24€)
- [ ] `commerce/stripe_integration.py` : paiement + webhooks
- [ ] `compliance/rgpd.py` : flow consentement parental, double opt-in
- [ ] `ui/onboarding.py` : création profil enfant + consentement parent
- [ ] **Test E2E paiement** : un parent paie en environnement Stripe test, l'enfant accède au contenu Premium

Critère de validation : flow inscription → consentement RGPD → paiement → accès enfant complet. Vérifier qu'aucun appel voix hors couche cachée.

### SPRINT 5 (semaine 5) — Contenu 3 îles + dashboard parent + Rite

**Objectif** : les 3 îles du MVP sont jouables en entier, le parent a son espace.

Livrables :
- [ ] Contenu complet Îles 1, 2, 3 (YAML sessions, exercices, RAG) — issu de la revue pédagogique fondateur+épouse
- [ ] `jeu/rite.py` : le Rite d'Élévation (escape game textuel 4 Sceaux)
- [ ] `ui/dashboard_parent.py` : espace parent
- [ ] `parent/bilan_hebdo.py` + `parent/email.py` : bilan PDF hebdomadaire automatique
- [ ] **Test E2E** : un enfant parcourt une île entière jusqu'au Rite, le parent reçoit le bilan

Critère de validation : les 3 îles sont jouables intégralement. Le bilan parent arrive par email.

### SPRINT 6 (semaine 6) — Stress test, finitions, soft launch

**Objectif** : le produit est prêt pour le 1er juillet.

Livrables :
- [ ] Stress test : 200 puis 500 utilisateurs simulés
- [ ] Optimisation cache et latence si nécessaire
- [ ] Pages légales : CGV, CGU, politique RGPD, mentions légales
- [ ] 10 scénarios de test d'acceptance joués (toi + testeurs)
- [ ] Infrastructure prod choisie et déployée (hébergement UE)
- [ ] **Soft launch** : 30 juin avec 5-10 familles POC avant ouverture publique

Critère de validation : tous les tests d'acceptance au vert, l'app tient la charge, le soft launch est concluant.

---

## 5. CE QUI N'EST PAS DANS LE MVP (reporté v1.1 / v1.2)

Pour protéger le calendrier, sont explicitement reportés :
- Îles 4 et 5 → v1.1 mi-juillet
- Îles 6 et 7 (dont géométrie avec Plotly interactif) → v1.2 août
- Mentor évolutif complet (MVP = 3 styles × 5 expressions, 1 niveau)
- Collection d'analogies → v1.1
- Quête d'Héritage → v1.1
- Concours national → événement fin août, construit en juillet

---

## 6. RISQUES TECHNIQUES — RAPPEL

| Risque | Mitigation |
|---|---|
| Délai 6 semaines | Scope MVP gravé, réduction de périmètre jamais de date |
| Maïeutique qui craque | Test de stress dès sprint 1, raffinage guardrails avant sprint 2 |
| Latence Streamlit | Cache systématique des assets dès sprint 3 |
| Coût ElevenLabs | Architecture 3 couches + kill switch voix |
| RGPD enfants | Flow consentement traité sprint 4, données minimales, hébergement UE |
| Charge au lancement | Stress test sprint 6, file d'attente d'inscription si pic |

---

## 7. PREMIER PAS — CE QUE CLAUDE CODE FAIT EN PREMIER

Sprint 1, première tâche : le fork.

```bash
git clone https://github.com/[ton-compte]/iaxel-formateur philia-summer-quest
cd philia-summer-quest
git remote remove origin
# créer un nouveau repo GitHub philia-summer-quest, puis :
git remote add origin https://github.com/[ton-compte]/philia-summer-quest.git
git checkout -b develop
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py   # smoke test : l'app IAXEL forkée doit tourner
```

Une fois le smoke test passé, Claude Code enchaîne sur la création de la structure de dossiers Philia et du `.claude/`, puis la base SQLite.

---

*Brief Implementer Technique Philia Summer Quest v1.0 — document 1A du Chantier 1.*
*À découper sprint par sprint dans `.claude/plans/`. Exécuté par Claude Code.*
