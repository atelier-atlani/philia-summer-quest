# BRIEF SPRINT 3 — T8.5 : Câblage narratif complet + réduction avatars à 2 + prénom élève (D19bis)

**Produit par l'Architect (Cowork), à l'attention de l'Implementer (Claude Code).**
**Référence : `.claude/context/00-master-context.md` Niveau 8 (décisions produit du 15 juillet 2026).**
**Décisions architecturales de cette tâche : D-T8.5-A à H, définies ci-dessous.**

---

## 1. OBJECTIF

Rendre l'onboarding et le début du Voyage narratif fluides de bout en bout, sans rupture : de l'accueil d'Archimède (prénom saisi) jusqu'à l'entrée en session sur l'Île 1, chaque écran affiche l'asset narratif qui lui correspond et le prénom réel de l'enfant est utilisé partout où le mentor s'adresse à lui — plus jamais le mot générique « Élévateur » par défaut alors qu'un prénom existe en base.

Cette tâche solde une dette de câblage identifiée dans `.claude/context/00-master-context.md` : plusieurs assets narratifs sont produits mais jamais affichés (`ecran_ile.py` est un écran nu), et plusieurs décisions du 15 juillet (D19bis, D27 partiellement, D14bis) n'ont pas encore de traduction technique.

---

## 2. CONTEXTE — ÉTAT ACTUEL DU CODE

**Routing (`app.py`)** : 4 écrans actifs — `avatar` (défaut), `carte`, `ile`, `session`. Le guard rail force `avatar` si aucun joueur n'existe en base. Il n'y a **aucun écran `accueil`** actuellement — le texte d'accueil narratif d'Archimède vit dans `ui/ecran_avatar.py::_afficher_accueil()`, à l'intérieur même de l'écran avatar.

**`ui/ecran_avatar.py`** : séquence actuelle à 5 étapes pilotées par `st.session_state["etape_onboarding"]` — `accueil` (texte + bouton) → `genre` (choix fille/garçon) → `grille` (4 avatars par genre, 8 au total) → `confirmation` → `bienvenue`. Le prénom n'est jamais demandé à l'enfant ; `avatar_prenom` en base est le prénom **de l'avatar fictif** (ex. « Sassou »), pas celui de l'enfant.

**`ui/ecran_ile.py`** : écran nu. Titre + caption « Sprint 3 » + deux boutons (« Commencer la Session 1 », retour carte). **Aucune image, aucun texte narratif.**

**`ui/ecran_session.py`** : chat + indicateur de progression + modal planches BD. **Aucune image affichée.** Le prénom est câblé en dur : `_init_engine()` appelle `SessionEngine(exercices=exercices, prenom="Élévateur", ...)` — la valeur réelle du joueur n'est jamais lue. La session est aussi **câblée en dur sur l'Île 1** : `from pedagogie.contenu_ile1 import META_SESSION_1, SESSION_1` en tête de fichier.

**`ui/ecran_carte.py`** : affiche `assets/ui/carte_archipel.png` en fond avec zones cliquables en overlay. N'affiche pas `archipel_isometrique.png`.

**`pedagogie/mentor.py::repondre()`** : accepte déjà un paramètre `prenom: str = "Élévateur"` et l'injecte dans le prompt système (`f"Le prénom de l'enfant que tu accompagnes est : {prenom}"`). **Le mécanisme d'injection existe déjà** — ce qui manque, c'est que la vraie valeur remonte jusqu'à lui depuis la base, au lieu du hardcode dans `ecran_session.py`.

**`data_layer/joueurs.py` / `schema.sql`** : la table `joueurs` a `avatar_genre`, `avatar_prenom`, `avatar_role` — **pas de colonne pour le prénom réel de l'enfant**. Le pattern de migration existe et est déjà utilisé trois fois (`cles_obtenues`, `cristaux_obtenus`, `planches_bd_vues`) dans `db.py::_appliquer_migrations()` via `PRAGMA table_info(joueurs)`.

**Assets disponibles** (`assets/narratif/`) :
- `globaux/` (4 fichiers déjà bien placés) : `accueil_invitation.png`, `archipel_isometrique.png`, `presentation_archipel_fille.png`, `presentation_archipel_garcon.png`
- `ile_1/` (12 fichiers, à câbler intégralement — aucun n'est actuellement affiché par un écran sauf les planches BD C1 déjà branchées) : `arrivee_fille/garcon.png`, `ecran_session_fille/garcon.png`, `planche_bd_c1_fille/garcon.png`, `planche_bd_c1_part2_fille/garcon.png`, `presentation_fille/garcon.png`, `vue_immersive.png`, `vue_isometrique.png`
- `ile_2/` (2 fichiers seulement, `vue_immersive.png` et `vue_isometrique.png` — pas encore de production complète, hors scope T8.5)

**Point de vigilance** : parmi les 12 fichiers d'`ile_1/`, `ecran_session_fille.png` et `ecran_session_garcon.png` sont conceptuellement des assets **globaux** (réutilisés par toutes les îles, pas spécifiques à l'Île 1 — voir master context §8.3), mais physiquement mal rangés sous `ile_1/`. Ce sont les 2 seuls fichiers à déplacer physiquement vers `globaux/` ; les 4 autres assets globaux listés au §8.3 du master context (`accueil_invitation`, `archipel_isometrique`, `presentation_archipel_<genre>`) sont déjà correctement rangés.

---

## 3. DÉCISIONS ARCHITECTURALES D-T8.5-A À H

### D-T8.5-A — Saisie du prénom avant le choix d'avatar (nouvelle séquence)

La séquence d'onboarding change d'ordre : le prénom de l'enfant est saisi **avant** tout choix d'avatar, dans le nouvel écran `accueil` (§D). L'ancienne étape `accueil` de `ecran_avatar.py` (texte narratif + bouton « Lever l'ancre ») est déplacée dans ce nouvel écran, avec un champ de saisie du prénom ajouté avant le bouton. `ecran_avatar.py` démarre désormais directement à l'étape `genre`.

### D-T8.5-B — Migration SQLite, colonne `prenom`, via PRAGMA

Nouvelle colonne `joueurs.prenom TEXT` (prénom réel de l'enfant, distinct de `avatar_prenom`). Migration ajoutée dans `db.py::_appliquer_migrations()`, même pattern que les trois migrations précédentes :
```python
if "prenom" not in cols:
    conn.execute("ALTER TABLE joueurs ADD COLUMN prenom TEXT")
```
Commentaire de migration ajouté en fin de `schema.sql`, à la suite du commentaire T8.1 déjà présent (pas d'`ALTER TABLE` dans `schema.sql` lui-même — le pattern établi gère tout via `db.py`).

### D-T8.5-C — Injection du prénom dans les prompts d'Archimède, fallback « Élévateur »

Le mécanisme d'injection existe déjà dans `pedagogie/mentor.py::repondre()` (paramètre `prenom`). Le travail de cette tâche consiste à faire remonter la vraie valeur :
- `ui/ecran_session.py::_init_engine()` doit lire `charger_joueur_courant()["prenom"]` au lieu du hardcode `"Élévateur"`
- Fallback explicite si `prenom` est `None` ou vide (joueur créé avant cette migration, ou faille de saisie) : conserver `"Élévateur"`
- `SessionEngine` reçoit déjà un champ `prenom` dans son constructeur (`pedagogie/session_engine.py`) — aucun changement structurel nécessaire à ce niveau, seule la valeur transmise change

### D-T8.5-D — Nouvel écran `ecran_accueil.py` + route `"accueil"` dans `app.py`

Nouveau fichier `ui/ecran_accueil.py`, point d'entrée `afficher_ecran_accueil()`. Contenu : le texte narratif actuellement dans `_afficher_accueil()` de `ecran_avatar.py`, l'image `globaux/accueil_invitation.png`, un champ de saisie du prénom (`st.text_input`), et le bouton « Lever l'ancre » (désormais désactivé tant que le prénom est vide — validation minimale).

`app.py` : nouvelle route `"accueil"` ; `ecran_courant` par défaut passe de `"avatar"` à `"accueil"` ; le guard rail (si aucun joueur en base) redirige vers `"accueil"` au lieu de `"avatar"`.

### D-T8.5-E — Nouvel écran `ecran_presentation_archipel.py`, post-onboarding

Nouveau fichier `ui/ecran_presentation_archipel.py`, affiché une seule fois entre la fin de l'onboarding (étape « bienvenue » de `ecran_avatar.py`) et l'arrivée sur la carte. Affiche `globaux/presentation_archipel_<genre>.png` avec un texte de transition d'Archimède qui présente l'archipel avant que l'enfant ne voie la carte interactive. Le bouton « Découvrir l'archipel » de `ecran_avatar.py` (actuellement câblé sur `ecran_courant = "carte"`, voir correctif du 13 juillet) route désormais vers ce nouvel écran plutôt que directement vers la carte.

### D-T8.5-F — Refonte de `ecran_ile.py` en 2 sous-étapes (arrivée + présentation)

`ui/ecran_ile.py`, aujourd'hui un écran nu, devient une mini state machine à 2 étapes internes (pattern similaire à `etape_onboarding`, mais scopé à l'écran île) :
1. **Arrivée** — `<ile_id>/arrivee_<genre>.png` + texte « Accueil de l'île » (voir `.claude/production/narration-iles.md`, section par île — au premier accès uniquement, formule courte aux accès suivants)
2. **Présentation** — `<ile_id>/presentation_<genre>.png` + suite du texte d'Archimède qui présente le domaine mathématique de l'île, puis bouton « Commencer la Session 1 »

### D-T8.5-G — Bandeau `ecran_session_<genre>.png` dans `ecran_session.py`

`ui/ecran_session.py` affiche désormais un bandeau `globaux/ecran_session_<genre>.png` (déplacé depuis `ile_1/`, voir point de vigilance §2) en haut de l'écran de session, avant le titre et le chat. Genre lu via `charger_joueur_courant()["avatar_genre"]` (pattern déjà utilisé dans le même fichier pour le modal planche BD, ligne `genre = joueur["avatar_genre"] if joueur else "fille"`).

### D-T8.5-H — Paramétrisation par `ile_id` pour scaling Îles 2-3

Point le plus structurant de cette tâche pour la suite de la roadmap (S2-S3, Îles 2 et 3, voir `.claude/roadmap/roadmap-15juillet-15aout.md`). `ui/ecran_session.py` importe aujourd'hui `META_SESSION_1, SESSION_1` directement depuis `pedagogie.contenu_ile1` — câblé en dur sur l'Île 1. Cette tâche généralise la sélection du contenu de session selon `st.session_state.ile_courante`, par exemple via un petit registre `{"ile_1": pedagogie.contenu_ile1, "ile_2": pedagogie.contenu_ile2, ...}` avec repli explicite si le module de l'île n'existe pas encore (Île 2 et 3 n'ont pas de contenu tant que S2/S3 de la roadmap ne sont pas livrées — ne pas faire planter l'app, afficher un message clair). Le chargement des assets narratifs (`ecran_ile.py`, `ecran_session.py`) doit de même construire ses chemins avec `ile_id` en variable, jamais `"ile_1"` en dur.

---

## 4. FICHIERS À CRÉER / MODIFIER

**À créer** :
- `ui/ecran_accueil.py` (D-T8.5-D)
- `ui/ecran_presentation_archipel.py` (D-T8.5-E)
- Déplacement physique : `assets/narratif/ile_1/ecran_session_fille.png` → `assets/narratif/globaux/ecran_session_fille.png` (et `garcon`)

**À modifier** :
- `app.py` — route `"accueil"`, défaut `ecran_courant`, guard rail (D-T8.5-D)
- `ui/ecran_avatar.py` — séquence `prenom → genre` devient `genre` directement (accueil et prénom sortis vers `ecran_accueil.py`), suppression de l'étape `grille` (réduction à 2 avatars canoniques Sassou/Mélian assignés automatiquement par genre — cohérent avec D18, plus de choix parmi 4) (D-T8.5-A)
- `ui/ecran_carte.py` — affichage de `archipel_isometrique.png` (D14bis)
- `ui/ecran_ile.py` — refonte complète en 2 sous-étapes (D-T8.5-F)
- `ui/ecran_session.py` — bandeau `ecran_session_<genre>.png` (D-T8.5-G), lecture du vrai prénom (D-T8.5-C), généralisation par `ile_id` (D-T8.5-H)
- `data_layer/schema.sql` — commentaire de migration (D-T8.5-B)
- `data_layer/db.py` — migration `PRAGMA` colonne `prenom` (D-T8.5-B)
- `data_layer/joueurs.py` — `creer_joueur()` accepte et enregistre `prenom` ; `charger_joueur_courant()` le retourne (D-T8.5-B, D-T8.5-C)
- `pedagogie/mentor.py` — aucun changement de logique attendu (l'injection existe déjà, voir §2) ; vérifier seulement qu'aucun appelant ne contourne le paramètre `prenom`

**Point d'attention non couvert par la liste ci-dessus** : la réduction à 2 avatars (D-T8.5-A) touche potentiellement `config/constants.py::AVATARS_REGISTRY` (aujourd'hui 4 avatars par genre). Ce fichier n'est pas dans la liste fournie par le Décideur — à confirmer avec toi si `ecran_avatar.py` doit se contenter d'ignorer les 3 avatars superflus du registre existant (solution minimale, ne touche pas `constants.py`) ou si le registre doit être réduit formellement. Recommandation Architect : ne pas toucher `constants.py` dans cette tâche (scope minimal), swagger le choix vers Sassou/Mélian directement dans `ecran_avatar.py`.

---

## 5. CRITÈRES D'ACCEPTANCE

- [ ] Au premier lancement (aucun joueur en base), l'app démarre sur l'écran `accueil`, pas `avatar`
- [ ] Le prénom saisi à l'accueil est bien celui utilisé par Archimède dans la première session de l'Île 1 (vérifiable dans le prompt système ou par observation du dialogue)
- [ ] Le bouton « Lever l'ancre » est inactif tant qu'aucun prénom n'est saisi
- [ ] Le choix d'avatar ne propose plus que 2 options (fille → Sassou, garçon → Mélian), sans étape grille intermédiaire
- [ ] Après confirmation de l'avatar, l'enfant voit l'écran de présentation de l'archipel avant la carte
- [ ] La carte affiche `archipel_isometrique.png`
- [ ] L'écran île affiche successivement l'arrivée puis la présentation, avec les bons visuels genrés, avant de proposer « Commencer la Session 1 »
- [ ] L'écran de session affiche le bandeau `ecran_session_<genre>.png`
- [ ] Un joueur créé avant cette migration (sans colonne `prenom` renseignée) ne fait pas planter l'app — fallback « Élévateur » actif
- [ ] Le code de sélection de contenu de session ne contient plus de référence en dur à `ile_1` / `contenu_ile1` (D-T8.5-H) — seul un registre paramétré par `ile_id` reste, avec message explicite si l'île demandée n'a pas encore de contenu

---

## 6. TESTS MANUELS

1. **Parcours neuf complet** : base vide → accueil (saisie prénom « Léa ») → genre fille → confirmation Sassou → bienvenue → présentation archipel → carte (archipel_isometrique visible) → île 1 (arrivée puis présentation) → session 1 (bandeau visible, Archimède utilise « Léa » dans son premier message)
2. **Fallback prénom absent** : joueur existant en base créé avant la migration (colonne `prenom` NULL) → relancer l'app → aucune erreur, Archimède utilise « Élévateur »
3. **Persistance du prénom entre sessions** : fermer et rouvrir l'app avec un joueur déjà créé (prénom renseigné) → le prénom reste correctement utilisé sans re-saisie
4. **Genre garçon** : reproduire le test 1 avec genre garçon → vérifier assignation Mélian, assets `_garcon` corrects sur tous les écrans traversés
5. **Île sans contenu (Île 2)** : forcer `ile_courante = "ile_2"` manuellement (aucun contenu produit à ce stade du projet) → l'app affiche un message clair plutôt qu'une erreur de crash (`ModuleNotFoundError` ou `ImportError` non gérée)

---

## 7. HORS SCOPE

- Production des assets graphiques Îles 2 et 3 (roadmap S2-S3, `.claude/roadmap/roadmap-15juillet-15aout.md`)
- Contenu pédagogique YAML des Îles 2 et 3
- Vidéos cinématiques HeyGen (D28, prévues S3)
- Système de célébrations D27 (confetti + toast, prévu semaine 1 de la roadmap mais **tâche distincte** de ce brief — ce brief se limite au câblage narratif et au prénom)
- Poster/parchemin physique de fin de parcours (différé post-MVP, D17)
- Réduction formelle du registre `AVATARS_REGISTRY` dans `config/constants.py` (voir point d'attention §4)

---

## 8. PROCÉDURE DE LIVRAISON

```bash
git checkout -b feat/T8.5-cablage-narratif-complet develop
# implémentation par l'Implementer (Claude Code)
git add ui/ecran_accueil.py ui/ecran_presentation_archipel.py \
        app.py ui/ecran_avatar.py ui/ecran_carte.py ui/ecran_ile.py ui/ecran_session.py \
        data_layer/schema.sql data_layer/db.py data_layer/joueurs.py \
        assets/narratif/globaux/ecran_session_fille.png assets/narratif/globaux/ecran_session_garcon.png
git commit -m "feat(T8.5): câblage narratif complet + prénom élève D19bis + réduction avatars"
git push -u origin feat/T8.5-cablage-narratif-complet
# revue Architect/Reviewer avant merge sur develop
```

Commit atomique côté Architect pour ce brief lui-même :
```
docs(plans): brief T8.5 câblage narratif complet
```

---

*Brief Sprint 3 T8.5 — câblage narratif complet, prénom élève (D19bis), réduction avatars.*
*Produit par l'Architect le 15 juillet 2026. À valider par le Décideur avant lancement de l'Implementer.*
