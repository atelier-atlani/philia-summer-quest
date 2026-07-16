# BRIEF SPRINT 3 — T8.6 : Système de célébration (D27)

**Produit par l'Architect (Cowork), à l'attention de l'Implementer (Claude Code).**
**Référence : `.claude/context/00-master-context.md` Niveau 4 (D27) et §8.1.**
**Décisions architecturales de cette tâche : D-T8.6-A à G, définies ci-dessous.**
**Statut Sprint 3 au 16 juillet : T8.5 mergé (`develop`, f77dc86 puis fix cc1a9d8), L1.3 (planches BD C2-C5) en cours côté Décideur, L1.4 (ce brief) à livrer aujourd'hui.**

---

## 1. OBJECTIF

Donner à l'enfant un retour émotionnel à deux vitesses, conforme à D27 : une **célébration légère** à chaque progression dans une session (confetti + message court personnalisé au prénom), et une **célébration forte** quand une île est achevée (planche BD spéciale déjà existante + un message d'Archimède écrit comme s'il s'adressait personnellement à l'enfant).

Ce brief ne se limite pas à l'habillage visuel : l'audit préalable du code (§2) a révélé que le système de récompense sous-jacent (`jeu/recompenses.py`) n'est aujourd'hui appelé par **aucun écran de jeu réel** — seulement par une app de test isolée. Célébrer un gain qui n'est jamais enregistré n'aurait aucun sens ; ce brief câble donc l'un et l'autre ensemble.

---

## 2. CONTEXTE — ÉTAT ACTUEL DU CODE

**`jeu/recompenses.py`** : API complète et déjà testée (`gagner_cle`, `gagner_cristal`, idempotentes, T7). **Mais `gagner_cle()` et `gagner_cristal()` ne sont appelées nulle part dans le vrai flux de jeu** — seulement dans `app_test_recompenses.py` (app de démo standalone, hors parcours réel). Un enfant qui termine des exercices aujourd'hui n'obtient techniquement ni cristal ni clé en base.

**`ui/ecran_session.py`** (post-T8.5) : le bouton « Exercice suivant → » avance `SessionEngine` sans jamais appeler `recompenses.gagner_cristal()`. Le bouton « Terminer le chapitre ✓ » clôt la session et déclenche le modal planche BD (`planche_bd_a_afficher = meta["planche_key"]`) sans jamais appeler `recompenses.gagner_cle()`.

**`ui/modal_planche_bd.py`** : contient déjà la détection du **dernier chapitre de l'île** — `chapitres_restants = chapitres_total - chapitre_num`, avec routage vers `"carte"` si `chapitres_restants == 0` (ligne du bloc `_modal()`). C'est le point exact où la clé de l'île devrait être accordée et où la célébration forte a sa place naturelle — mais aujourd'hui, rien ne s'y passe au-delà du routage.

**Aucune détection automatique de réussite d'exercice n'existe** (dette notée dès `learnings.md` Sprint 2, jamais résolue). Le seul signal disponible qu'un enfant « a bien avancé » est une action UI explicite : clic sur « Exercice suivant → » ou sur « Terminer le chapitre ✓ ». Ce brief s'appuie sur ces clics, pas sur une analyse sémantique de la réponse de l'enfant — voir D-T8.6-A.

**Progression inter-sessions au sein d'une île — dépendance bloquante découverte pendant l'audit** : `ecran_session.py::_charger_contenu_session()` charge toujours `META_SESSION_1` / `SESSION_1`, quelle que soit la progression réelle de l'enfant. Il n'existe aucune variable `session_courante` ni logique de passage à `SESSION_2`. Or `pedagogie/contenu_ile1.py` contient bien les 5 sessions complètes (`SESSION_1` à `SESSION_5`, vérifié). Concrètement : **un enfant ne peut aujourd'hui jouer que la Session 1 de n'importe quelle île** — la Session 5 (celle qui déclenche `chapitres_restants == 0`, donc la clé et la célébration forte) n'est atteignable qu'en forçant l'état manuellement. Voir D-T8.6-E.

**Primitives disponibles côté Streamlit, sans dépendance externe** : `st.balloons()` (effet festif intégré, l'équivalent natif le plus proche de « confetti ») et `st.toast()` (notification légère avec texte custom). Le projet n'a jamais introduit de librairie JS/CSS de confetti — cohérent avec la sobriété technique actée (D13 suppression RAG, D25 priorité d'exécution). Voir D-T8.6-B.

---

## 3. DÉCISIONS ARCHITECTURALES D-T8.6-A À G

### D-T8.6-A — Déclencheur de la célébration légère

La célébration légère se déclenche sur le clic « Exercice suivant → » dans `ecran_session.py` — c'est le seul signal disponible en l'absence de détection automatique de réussite (dette non résolue, voir §2). Elle ne se déclenche **pas** sur le bouton « Terminer le chapitre ✓ » (réservé à la célébration forte, D-T8.6-F) ni sur un simple message envoyé au chat.

**Limite assumée** : un enfant qui clique « Exercice suivant » sans avoir vraiment résolu l'exercice recevra quand même la célébration légère (le système ne juge pas la qualité de la réponse). Accepté pour ce sprint — corrigible seulement si la détection automatique de réussite (dette Sprint 2) est un jour traitée.

### D-T8.6-B — Mécanisme technique : primitives Streamlit natives

- **Confetti léger** → `st.balloons()`. Pas de librairie externe.
- **Toast personnalisé** → `st.toast(message, icon="🎉")`, message court incluant le prénom réel de l'enfant (`charger_joueur_courant()["prenom"]`, fallback « Élévateur »).
- Exemple de message : `"Bien joué, {prenom} !"` ou variante courte tirée d'un petit pool de formulations (2-3 variantes) pour éviter la répétition mécanique sur 65 exercices.

### D-T8.6-C — Câblage de `gagner_cristal()` dans le vrai flux

Dans `ui/ecran_session.py`, au clic « Terminer le chapitre ✓ » (pas à chaque exercice — un cristal correspond à un concept, donc à une session entière, cohérent avec `CRISTAUX_CATALOGUE` dans `config/constants.py`) : appel à `jeu.recompenses.gagner_cristal(ile_id, concept_id)`, avec `concept_id = meta["planche_key"].upper()` (ex. `"c1"` → `"C1"`).

### D-T8.6-D — Câblage de `gagner_cle()` dans le vrai flux

Dans `ui/modal_planche_bd.py`, exactement au point où `chapitres_restants == 0` est détecté : appel à `jeu.recompenses.gagner_cle(ile_id)`, avant le routage vers `"carte"`.

### D-T8.6-E — Dépendance bloquante : progression inter-sessions non câblée

**Hors périmètre strict de D27, mais condition nécessaire pour que D-T8.6-D et D-T8.6-F soient testables autrement qu'en forçant l'état manuellement.** Signalé au Décideur pour arbitrage explicite — deux options :
- **Option 1** : inclure dans ce brief un câblage minimal (`session_courante` en session_state, incrémenté à chaque « Terminer le chapitre » sans planche de fin, chargement de `SESSION_{n}` / `META_SESSION_{n}` correspondant dans `_charger_contenu_session()`)
- **Option 2** : ouvrir un ticket dédié séparé (ex. `T8.7`), traiter D-T8.6-A à D et G cette semaine, et considérer D-T8.6-D/F comme livrés mais non testables de bout en bout tant que le ticket séparé n'est pas fait

**Recommandation Architect** : Option 1. Le câblage minimal est petit (une variable d'état + une boucle de sélection du numéro de session), et sans lui, personne ne peut vérifier visuellement que D27 fonctionne avant le test cobaye #1 de fin de semaine 1 (roadmap S1, check-in 21 juillet). Le Décideur tranche avant le lancement de l'Implementer.

### D-T8.6-F — Célébration forte de fin d'île

Déclenchée immédiatement après le câblage D-T8.6-D (gain de la clé confirmé), dans `ui/modal_planche_bd.py`, avant le routage vers `"carte"` :
- `st.balloons()`
- Message d'Archimède écrit à la première personne, personnalisé au prénom (ex. *« {prenom}, tu as réveillé cette île tout seul. Je suis fier de toi. »*), affiché en plus de la planche BD déjà prévue (D22) — pas en remplacement
- Le texte exact du message est un texte narratif : à rédiger par le Décideur (ou avec l'aide de l'Architect si besoin), pas à improviser par l'Implementer — cohérent avec la règle « le YAML/texte coud, le LLM brode » appliquée ici aux textes fixes de célébration (ce ne sont pas des textes générés par le LLM en session, donc validation humaine amont comme tout texte narratif fixe)

### D-T8.6-G — Anti-rejeu

Les fonctions `gagner_cle`/`gagner_cristal` sont déjà idempotentes côté données (T7), mais l'**affichage** de la célébration ne doit pas se redéclencher à chaque `st.rerun()` Streamlit qui suit l'action. Garde via un flag `st.session_state` consommé immédiatement après affichage (pattern déjà utilisé pour `planche_bd_a_afficher` dans `ecran_session.py`).

---

## 4. FICHIERS À CRÉER / MODIFIER

**À créer** :
- `ui/celebrations.py` — petit module partagé, deux fonctions publiques : `afficher_celebration_legere(prenom: str) -> None` (D-T8.6-A/B) et `afficher_celebration_fin_ile(prenom: str, nom_ile: str) -> None` (D-T8.6-F). Évite de dupliquer les textes et la logique de garde (D-T8.6-G) entre `ecran_session.py` et `modal_planche_bd.py`.

**À modifier** :
- `ui/ecran_session.py` — appel à `afficher_celebration_legere()` au clic « Exercice suivant → » (D-T8.6-A) ; appel à `recompenses.gagner_cristal()` au clic « Terminer le chapitre ✓ » (D-T8.6-C) ; **si Option 1 retenue (D-T8.6-E)** : ajout de `session_courante` et sélection dynamique de `SESSION_{n}`
- `ui/modal_planche_bd.py` — appel à `recompenses.gagner_cle()` et `afficher_celebration_fin_ile()` au point `chapitres_restants == 0` (D-T8.6-D/F)

**Non modifié, à vérifier seulement** :
- `jeu/recompenses.py` — aucun changement de logique attendu, l'API existante suffit

---

## 5. CRITÈRES D'ACCEPTANCE

- [ ] Cliquer « Exercice suivant → » déclenche `st.balloons()` + un toast avec le vrai prénom de l'enfant
- [ ] La célébration légère ne se redéclenche pas au simple rerun d'un message de chat (D-T8.6-G)
- [ ] Terminer une session (« Terminer le chapitre ✓ ») enregistre bien un cristal en base (vérifiable via `recompenses.cristaux_obtenus()`)
- [ ] **Si D-T8.6-E Option 1 retenue** : un enfant qui termine la Session 1 accède bien à la Session 2, et ainsi de suite jusqu'à la Session 5
- [ ] Terminer la dernière session d'une île enregistre bien la clé en base (`recompenses.cles_obtenues()`) — **testable seulement si D-T8.6-E est résolu**
- [ ] La célébration forte (balloons + message personnalisé) s'affiche avant le retour à la carte, en plus de la planche BD existante, jamais à sa place
- [ ] Aucune régression sur le flow planche BD existant (D22/D24, tests manuels déjà documentés dans `modal_planche_bd.py`)

---

## 6. TESTS MANUELS

1. **Célébration légère simple** : session en cours, cliquer « Exercice suivant → » → confetti + toast prénom visibles, une seule fois
2. **Non-répétition au rerun** : après le test 1, envoyer un message au chat (qui déclenche un rerun Streamlit) → la célébration ne se réaffiche pas
3. **Cristal enregistré** : terminer une session complète → vérifier en base que le cristal correspondant apparaît dans `cristaux_obtenus()`
4. **Parcours complet d'île (si D-T8.6-E résolu)** : jouer les 5 sessions de l'Île 1 d'affilée → à la fin de la Session 5, vérifier clé enregistrée + célébration forte affichée + planche BD affichée + retour carte fonctionnel
5. **Non-régression planche BD** : rejouer les tests manuels déjà listés dans `modal_planche_bd.py` (tests 1 à 6) → aucun doit régresser

---

## 7. HORS SCOPE

- Détection automatique de réussite d'exercice (dette Sprint 2 non résolue — la célébration légère reste déclenchée par clic, pas par analyse sémantique)
- Fragments de carte au trésor, artefacts fonctionnels (mécaniques du format été, hors périmètre du format court — voir master context §2)
- Rédaction finale du texte narratif de la célébration forte si le Décideur préfère le fournir après ce brief plutôt que d'en discuter maintenant (l'Implementer ne doit pas improviser ce texte, voir D-T8.6-F)
- Câblage complet de la progression inter-sessions si l'Option 2 de D-T8.6-E est retenue à la place de l'Option 1

---

## 8. PROCÉDURE DE LIVRAISON

```bash
git checkout -b feat/T8.6-celebrations develop
# implémentation par l'Implementer (Claude Code)
git add ui/celebrations.py ui/ecran_session.py ui/modal_planche_bd.py
git commit -m "feat(T8.6): célébrations légère + fin d'île (D27) + câblage recompenses"
git push -u origin feat/T8.6-celebrations
# revue Architect/Reviewer avant merge sur develop
```

Commit atomique côté Architect pour ce brief lui-même :
```
docs(plans): brief T8.6 célébrations
```

---

*Brief Sprint 3 T8.6 — célébrations (D27).*
*Produit par l'Architect le 16 juillet 2026. À valider par le Décideur avant lancement de l'Implementer — arbitrage D-T8.6-E requis en priorité.*
