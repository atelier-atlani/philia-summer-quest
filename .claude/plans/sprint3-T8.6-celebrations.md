# BRIEF SPRINT 3 — T8.6 : Progression + Récompenses + Célébrations

**Produit par l'Architect (Cowork), à l'attention de l'Implementer (Claude Code).**
**Référence : `.claude/context/00-master-context.md` Niveau 4 (D27) et §8.1.**
**Décisions architecturales de cette tâche : D-T8.6-A à G, définies ci-dessous.**
**Statut Sprint 3 au 16 juillet : T8.5 mergé (`develop`, f77dc86 puis fix cc1a9d8), L1.3 (planches BD C2-C5) en cours côté Décideur.**
**v2 — 16 juillet 2026 : périmètre étendu par décision du Décideur. Le brief ne se limite plus à l'habillage des célébrations, il couvre les trois briques nécessaires à ce que D27 soit réellement observable en jeu.**

---

## 1. OBJECTIF

Ce brief livre **trois briques imbriquées**, dans un ordre de dépendance strict — chacune est un prérequis de la suivante :

1. **Progression** — faire en sorte qu'un enfant puisse réellement traverser les 5 sessions d'une île (Session 1 → 2 → 3 → 4 → 5), condition sans laquelle « fin d'île » n'existe pas dans l'app.
2. **Récompenses** — câbler `jeu/recompenses.py` (`gagner_cristal`, `gagner_cle`) dans le vrai flux de jeu, pour qu'une progression réelle se traduise par un gain réel en base.
3. **Célébrations (D27)** — habiller ces deux mécaniques d'un retour émotionnel à deux vitesses : une **célébration légère** à chaque progression dans une session (confetti + message court personnalisé au prénom), et une **célébration forte** quand une île est achevée (planche BD spéciale + message d'Archimède personnalisé).

**Pourquoi cet ordre, et pas l'inverse** : célébrer un gain qui n'est jamais enregistré n'a aucun sens (brique 3 sans brique 2), et enregistrer un gain qu'on ne peut jamais atteindre en jouant n'a aucun sens non plus (brique 2 sans brique 1). L'Implementer doit livrer et vérifier dans cet ordre — du bas de la pile vers le haut — pas les trois en parallèle.

---

## 2. CONTEXTE — ÉTAT ACTUEL DU CODE

**Progression inter-sessions (brique 1) — absente aujourd'hui.** `ecran_session.py::_charger_contenu_session()` charge toujours `META_SESSION_1` / `SESSION_1`, quelle que soit la progression réelle de l'enfant. Il n'existe aucune variable `session_courante` ni logique de passage à `SESSION_2`. Or `pedagogie/contenu_ile1.py` contient bien les 5 sessions complètes (`SESSION_1` à `SESSION_5`, vérifié). Concrètement : **un enfant ne peut aujourd'hui jouer que la Session 1 de n'importe quelle île.**

**Récompenses (brique 2) — API prête, jamais câblée.** `jeu/recompenses.py` expose `gagner_cle(ile_id)` et `gagner_cristal(ile_id, concept_id)`, complètes et déjà testées (idempotentes, T7), mais **appelées nulle part dans le vrai flux de jeu** — seulement dans `app_test_recompenses.py` (app de démo standalone, hors parcours réel). Un enfant qui termine des exercices aujourd'hui n'obtient techniquement ni cristal ni clé en base.

**Point de vigilance sur la signature des fonctions** : la demande du Décideur mentionne `gagner_cristal(joueur_id, cristal_id)` et `gagner_cle(joueur_id, cle_id)`. L'API réellement implémentée dans `jeu/recompenses.py` est `gagner_cristal(ile_id: str, concept_id: str)` et `gagner_cle(ile_id: str)` — le joueur courant est résolu **implicitement** en interne via `charger_joueur_courant()`, pas passé en paramètre (cohérent avec la règle MVP « un seul joueur autorisé », `data_layer/joueurs.py::creer_joueur()`). Ce brief conserve l'API existante telle quelle plutôt que de la retoucher pour ajouter un paramètre `joueur_id` aujourd'hui inutile — l'intention du Décideur (associer le gain au bon joueur, au bon concept) est déjà pleinement couverte. À signaler si ce n'est pas ce qui était voulu.

**`ui/modal_planche_bd.py`** : contient déjà la détection du **dernier chapitre de l'île** — `chapitres_restants = chapitres_total - chapitre_num`, avec routage vers `"carte"` si `chapitres_restants == 0`. C'est le point exact où la clé de l'île doit être accordée (brique 2) et où la célébration forte a sa place naturelle (brique 3).

**Aucune détection automatique de réussite d'exercice n'existe** (dette notée dès `learnings.md` Sprint 2, jamais résolue — voir aussi la note ajoutée aujourd'hui sur le pattern récurrent, §9). Le seul signal disponible qu'un enfant « a bien avancé » est une action UI explicite : clic sur « Exercice suivant → » ou sur « Terminer le chapitre ✓ ».

**Primitives disponibles côté Streamlit, sans dépendance externe** : `st.balloons()` et `st.toast()`. Le projet n'a jamais introduit de librairie JS/CSS de confetti — cohérent avec la sobriété technique actée (D13, D25). Confirmé par le Décideur : aucune librairie externe.

---

## 3. DÉCISIONS ARCHITECTURALES D-T8.6-A À G

**Ordre d'implémentation (tranché par le Décideur)** :

| Ordre | Brique | Décisions |
|---|---|---|
| 1 | Progression | D-T8.6-E |
| 2 | Récompenses | D-T8.6-C, D-T8.6-D |
| 3 | Célébrations | D-T8.6-A, D-T8.6-B, D-T8.6-F, D-T8.6-G |

Les identifiants de décision restent ceux du brief v1 (traçabilité) — seul l'ordre de lecture/implémentation ci-dessous change.

### D-T8.6-E — Câblage de la progression inter-sessions (brique 1, à livrer en premier)

**Tranché par le Décideur : inclus dans ce brief (plus d'arbitrage à faire).** Ajout d'une variable `session_courante` (session_state), incrémentée quand une session se termine sans planche de fin de chapitre restant, avec sélection dynamique de `SESSION_{n}` / `META_SESSION_{n}` dans `_charger_contenu_session()` (généralisation du registre déjà posé en T8.5, D-T8.5-H). Reset de `session_courante` à 1 au changement d'île.

### D-T8.6-C — Câblage de `gagner_cristal()` dans le vrai flux (brique 2)

**Déclencheur, précisé par le Décideur** : après chaque bonne réponse validée, pas seulement en fin de session. En pratique, `SessionEngine` (`pedagogie/session_engine.py`) est l'endroit recommandé — cohérent avec D6 (« le moteur est le cerveau, l'écran est une vitre ») : le gain de cristal est un effet de la progression pédagogique, pas un détail d'affichage.

Point technique à trancher par l'Implementer au moment du câblage : `exercice_suivant()` n'est jamais appelé sur le **dernier** exercice d'une session (pas de bouton « Exercice suivant » sur le dernier — voir `ecran_session.py`, transition automatique vers Mode BILAN à la place). Pour garantir que le cristal est bien accordé même dans ce cas, appeler `gagner_cristal(ile_id, concept_id)` à la fois :
- dans `SessionEngine.exercice_suivant()` (progression en cours de session)
- et au clic « Terminer le chapitre ✓ » (filet de sécurité pour le dernier exercice)

Idempotent des deux côtés (T7) — appeler deux fois ne duplique rien. `concept_id = meta["planche_key"].upper()` (ex. `"c1"` → `"C1"`).

### D-T8.6-D — Câblage de `gagner_cle()` dans le vrai flux (brique 2)

**Confirmé par le Décideur : à la fin d'île complétée** (après la dernière session terminée — C5 pour l'Île 1). Dans `ui/modal_planche_bd.py`, exactement au point où `chapitres_restants == 0` est détecté : appel à `jeu.recompenses.gagner_cle(ile_id)`, avant le routage vers `"carte"`.

**Vérification systématique demandée par le Décideur** : après chaque test manuel de ce brief, vérifier en base (`recompenses.cristaux_obtenus()` / `recompenses.cles_obtenues()`) qu'un cristal ou une clé apparaît bien — pas seulement que l'UI s'affiche correctement. Voir §9 (pattern émergent) : c'est exactement le type de vérification qui a manqué sur les livrables précédents.

### D-T8.6-A — Déclencheur de la célébration légère (brique 3)

La célébration légère se déclenche sur le même événement que le gain de cristal (D-T8.6-C) — clic « Exercice suivant → », ou passage automatique en Mode BILAN sur le dernier exercice. Elle ne se déclenche pas sur un simple message envoyé au chat qui ne fait pas progresser l'exercice.

**Limite assumée** : en l'absence de détection automatique de réussite, un enfant qui avance sans avoir vraiment résolu l'exercice reçoit quand même la célébration légère. Accepté pour ce sprint.

### D-T8.6-B — Mécanisme technique : primitives Streamlit natives (brique 3)

**Confirmé par le Décideur, sans changement** :
- `st.balloons()` pour la bonne réponse
- `st.toast(f"Bien joué {prenom} !")` pour le feedback textuel
- Aucune librairie externe

### D-T8.6-F — Célébration forte de fin d'île (brique 3)

**Confirmé par le Décideur** :
- Modal planche BD spéciale, réutilisant le pattern déjà en place en T8.1 (`ui/modal_planche_bd.py` / `@st.dialog`)
- `st.balloons()` renforcé — dans les limites de l'API Streamlit (une seule primitive `balloons()` existe, pas de variante « intensité »). Le renforcement vient de la combinaison : balloons + modal dédié + message personnalisé, à distinguer visuellement de la célébration légère plutôt que d'empiler plusieurs appels à `st.balloons()`
- Message d'Archimède personnalisé avec `{prenom}`, ton **« comme si le message venait d'Archimède lui-même »** — texte à la première personne, chaleureux, distinct du texte du Mode Bilan
- Le texte exact est un texte narratif fixe : à rédiger par le Décideur (ou avec l'aide de l'Architect), pas à improviser par l'Implementer — même règle que tout texte narratif fixe du projet (le YAML/texte coud, le LLM brode)

### D-T8.6-G — Anti-rejeu (brique 3)

Les fonctions `gagner_cle`/`gagner_cristal` sont déjà idempotentes côté données (T7), mais l'**affichage** de la célébration ne doit pas se redéclencher à chaque `st.rerun()` Streamlit qui suit l'action. Garde via un flag `st.session_state` consommé immédiatement après affichage (pattern déjà utilisé pour `planche_bd_a_afficher`).

---

## 4. FICHIERS À CRÉER / MODIFIER

**À créer** :
- `ui/celebrations.py` — deux fonctions publiques : `afficher_celebration_legere(prenom: str) -> None` (D-T8.6-A/B) et `afficher_celebration_fin_ile(prenom: str, nom_ile: str) -> None` (D-T8.6-F).

**À modifier** :
- `pedagogie/session_engine.py` — progression inter-sessions si portée à ce niveau (D-T8.6-E), appel `gagner_cristal()` dans `exercice_suivant()` (D-T8.6-C)
- `ui/ecran_session.py` — sélection dynamique de `SESSION_{n}` via `session_courante` (D-T8.6-E) ; appel `afficher_celebration_legere()` (D-T8.6-A) ; appel `gagner_cristal()` au clic « Terminer le chapitre ✓ » en filet de sécurité (D-T8.6-C)
- `ui/modal_planche_bd.py` — appel `gagner_cle()` et `afficher_celebration_fin_ile()` au point `chapitres_restants == 0` (D-T8.6-D/F)

**Non modifié, à vérifier seulement** :
- `jeu/recompenses.py` — aucun changement de logique attendu, l'API existante suffit (voir point de vigilance §2)

---

## 5. CRITÈRES D'ACCEPTANCE

**Brique 1 — Progression** :
- [ ] Un enfant qui termine la Session 1 accède à la Session 2, puis 3, 4, 5, sans intervention manuelle sur `session_courante`
- [ ] `session_courante` repart à 1 sur une nouvelle île

**Brique 2 — Récompenses** :
- [ ] Terminer une session enregistre un cristal en base, vérifié via `recompenses.cristaux_obtenus()` (pas seulement observé à l'écran)
- [ ] Terminer la Session 5 de l'Île 1 (dernière session) enregistre la clé en base, vérifié via `recompenses.cles_obtenues()`
- [ ] Appeler deux fois le même gain (re-render, double clic) ne duplique rien

**Brique 3 — Célébrations** :
- [ ] Chaque progression d'exercice déclenche `st.balloons()` + toast avec le vrai prénom de l'enfant
- [ ] La célébration légère ne se redéclenche pas au simple rerun d'un message de chat (D-T8.6-G)
- [ ] La fin d'île déclenche la célébration forte (modal spécial + balloons + message personnalisé) avant le retour à la carte, en plus de la planche BD existante, jamais à sa place

---

## 6. TESTS MANUELS

1. **Progression complète** : jouer les 5 sessions de l'Île 1 d'affilée sans intervention manuelle → chaque session s'enchaîne correctement
2. **Cristal enregistré à chaque étape** : après chaque session terminée, vérifier en base que le cristal correspondant apparaît dans `cristaux_obtenus()` — pas seulement que l'écran progresse
3. **Clé enregistrée en fin d'île** : après la Session 5, vérifier en base `cles_obtenues()` contient `"ile_1"`
4. **Célébration légère** : à chaque progression d'exercice, confetti + toast prénom visibles, une seule fois par événement
5. **Non-répétition au rerun** : envoyer un message au chat après une célébration → elle ne se réaffiche pas
6. **Célébration forte de bout en bout** : à la fin de la Session 5 → modal spécial + balloons + message personnalisé + planche BD existante, dans cet ordre ou combinés, puis retour carte fonctionnel
7. **Non-régression planche BD** : rejouer les tests manuels déjà listés dans `modal_planche_bd.py` (tests 1 à 6) → aucun ne doit régresser

---

## 7. HORS SCOPE

- Détection automatique de réussite d'exercice (dette Sprint 2 non résolue — la célébration légère et le gain de cristal restent déclenchés par une action UI explicite, pas par analyse sémantique)
- Fragments de carte au trésor, artefacts fonctionnels (mécaniques du format été, hors périmètre du format court)
- Rédaction finale du texte narratif de la célébration forte si le Décideur préfère le fournir séparément (l'Implementer ne doit pas improviser ce texte, voir D-T8.6-F)
- Refactor de `jeu/recompenses.py` pour ajouter un paramètre `joueur_id` explicite (voir point de vigilance §2 — non nécessaire au MVP single-player)

---

## 8. PROCÉDURE DE LIVRAISON

```bash
git checkout -b feat/T8.6-progression-recompenses-celebrations develop
# implémentation par l'Implementer (Claude Code), dans l'ordre : progression → récompenses → célébrations
git add pedagogie/session_engine.py ui/ecran_session.py ui/modal_planche_bd.py ui/celebrations.py
git commit -m "feat(T8.6): progression inter-sessions + câblage récompenses + célébrations (D27)"
git push -u origin feat/T8.6-progression-recompenses-celebrations
# revue Architect/Reviewer avant merge sur develop — vérification base de données à chaque test, pas seulement UI
```

Commit atomique côté Architect pour ce brief lui-même :
```
docs(plans): T8.6 étendu progression + récompenses + célébrations
```

---

## 9. NOTE — PATTERN ÉMERGENT (voir aussi `.claude/memory/learnings.md`)

Ce brief est le cinquième cas cette semaine où un mécanisme livré et « marqué fait » s'est révélé non câblé dans le vrai parcours de jeu (Mode Bilan T4, écran avatar T6, système clés/cristaux T7, progression inter-sessions découverte ici, plus un cas de structure de commit incomplète). Voir §9 de `learnings.md` pour la règle Reviewer ajoutée en conséquence : tout mécanisme nouveau doit être testé de bout en bout en contexte réel, pas seulement via une app de démo isolée, avant d'être considéré « livré ».

---

*Brief Sprint 3 T8.6 — Progression + Récompenses + Célébrations (D27).*
*Produit par l'Architect le 16 juillet 2026, étendu le même jour suite aux décisions du Décideur.*
