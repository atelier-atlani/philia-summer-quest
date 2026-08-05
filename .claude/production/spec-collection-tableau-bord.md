# SPEC CLAUDE CODE — COLLECTION + TABLEAU DE BORD (Île 1)

**Système de récompense enrichi : objets par exercice, coffre par session, tableau de bord permanent.**
**Répond au désir de gamification exprimé par 2 cobayes de 12 ans.**
**Architecture : on RHABILLE l'existant (gagner_cristal / cristaux_obtenus), on ne migre PAS le stockage.**

---

## PRINCIPE VALIDÉ (Décideur)

- Chaque exercice traversé (passage à l'exercice suivant) → +1 objet de la session.
- 1 type d'objet par session : S1 pierres, S2 amphores, S3 cristaux d'eau,
  S4 poids, S5 planches.
- Fin de session = coffre plein, nommé du nom de la session (« Sens d'une fraction »).
- Le coffre REMPLACE visuellement le cristal. Mécanique inchangée : gagner_cristal()
  reste la source de vérité (un cristal gagné = un coffre affiché). On change
  l'HABILLAGE, pas le stockage.
- Tableau de bord = sidebar permanente, visible sur tous les écrans, dépliée
  par défaut.

Assets attendus dans assets/ui/ (produits séparément, placeholder gracieux si absents) :
coffre.png, objet_pierre.png, objet_amphore.png, objet_cristal_eau.png,
objet_poids.png, objet_planche.png

---

## COMMIT 1 — Table de correspondance session → objet + nom de coffre

Créer une table de configuration (dans un module dédié, ex. jeu/collection.py,
OU dans contenu_ile1.py si plus cohérent — justifier le choix) qui associe
chaque session de l'Île 1 à :
- son type d'objet (pierre, amphore, cristal_eau, poids, planche)
- le chemin de l'asset objet
- le nom affiché du coffre = le concept de la session (déjà dans META_SESSION_N["concept"])

Exemple de structure :

    COLLECTION_ILE_1 = {
        "c1": {"objet": "pierre",      "asset": "assets/ui/objet_pierre.png"},
        "c2": {"objet": "amphore",     "asset": "assets/ui/objet_amphore.png"},
        "c3": {"objet": "cristal_eau", "asset": "assets/ui/objet_cristal_eau.png"},
        "c4": {"objet": "poids",       "asset": "assets/ui/objet_poids.png"},
        "c5": {"objet": "planche",     "asset": "assets/ui/objet_planche.png"},
    }

Clé = planche_key de la session (déjà existant, D23). Le nom du coffre se
dérive du concept de la session, pas besoin de le dupliquer ici.

Réutilisable pour les futures îles : une table par île.

Commit : feat(collection): table session → objet + coffre (Île 1)

---

## COMMIT 2 — Compteur d'objets en session + coffre en fin de session

Dans le moteur de session (session_engine.py) et/ou l'écran (ecran_session.py) :

1. COMPTEUR D'OBJETS
   Le nombre d'objets gagnés dans la session courante = le nombre d'exercices
   traversés = engine.index_exercice (0-based → l'exercice 1 fini = 1 objet).
   Attention : bien définir le moment où l'objet est "gagné" = au passage à
   l'exercice suivant (clic « Exercice suivant → », qui appelle exercice_suivant()).
   Donc objets_gagnes = index_exercice (l'exercice courant pas encore "encaissé"
   tant qu'on n'est pas passé au suivant), OU index_exercice + 1 si on compte
   l'exercice en cours comme acquis dès qu'on l'aborde. CHOISIR la convention
   la plus intuitive pour un enfant (probablement : +1 quand il passe au suivant)
   et la documenter.

2. AFFICHAGE EN SESSION
   Pendant la session, afficher le compteur d'objets de la session courante,
   avec l'icône de l'objet : « [icône pierre] 3 pierres ». Discret, près du
   repère « Exercice 3/6 » déjà présent.
   À chaque objet gagné (passage exercice), micro-feedback léger : un st.toast
   type « +1 pierre ! » (réutiliser le pattern toast de celebrations.py). PAS
   de son, PAS d'animation lourde — juste le toast, c'est le « ding » minimal.

3. COFFRE EN FIN DE SESSION
   Quand la session est validée (le cristal est gagné via gagner_cristal, code
   existant), afficher le coffre plein nommé du concept de la session, dans la
   célébration de fin de session. Réutiliser l'asset coffre.png + le nom du
   concept en texte par-dessus (pattern titre de la carte-fragment : texte net
   en overlay, jamais peint dans l'image).
   Ne PAS créer de nouvelle mécanique de récompense : le coffre est l'habillage
   visuel du cristal déjà gagné.

Commit : feat(collection): compteur objets en session + coffre de fin de session

---

## COMMIT 3 — Tableau de bord (sidebar permanente)

Une sidebar visible sur tous les écrans, dépliée par défaut.

1. Changer dans app.py : initial_sidebar_state="collapsed" → "expanded".

2. Une fonction unique de rendu du tableau de bord (ex. dans un module
   ui/tableau_bord.py) appelée sur les écrans de jeu (carte, île, session,
   énigme). Réutiliser / fusionner avec _render_sidebar_recompenses existant
   dans ecran_carte.py plutôt que dupliquer — cette fonction fait déjà une
   partie du travail (porte-clés). L'étendre, ne pas la doubler.

3. Contenu du tableau de bord :
   - OÙ JE SUIS : nom de l'île courante + session courante si en session
     (« L'Île des Nombres Brisés — Sens d'une fraction »)
   - MES COFFRES : les sessions validées (cristaux obtenus via cristaux_obtenus(),
     code existant), affichées comme coffres gagnés (mini coffre + nom du concept).
     Montrer la progression : X / 5 coffres.
   - MA COLLECTION EN COURS : si en session, le compteur d'objets courant.
   - MA CLÉ : la Clé du Partage (gagnée ou pas) — le porte-clés existant.
   - MA CARTE : la carte-fragment, accessible quand gagnée (l'énigme finale
     donne la carte — lien vers son affichage si déjà obtenue).

4. Placeholder gracieux partout : si un asset manque, emoji ou libellé de
   secours, jamais de crash (pattern déjà utilisé pour clé/carte).

CONTRAINTES
- Ne pas migrer le stockage : gagner_cristal / cristaux_obtenus / cles_obtenues
  restent la source de vérité. Le tableau de bord LIT ces données, ne crée pas
  de nouveau système.
- Réutiliser _render_sidebar_recompenses (l'étendre), pas de doublon de sidebar.
- Styles inline, base64 pour les images (pattern clé/carte).
- Tester en MOCK_LLM (le tableau de bord n'appelle pas le LLM).

Commit : feat(collection): tableau de bord permanent (sidebar)

---

## HORS PÉRIMÈTRE (D47 — post-MVP)
- Mini-carte animée avec émoticône qui se déplace sur les sessions
- Son réel (« ding » audio)
- Animations lourdes
Le tableau de bord remplace fonctionnellement la mini-carte (l'enfant voit
sa position textuellement).

## ORDRE
Commit 1 (table) → Commit 2 (compteur + coffre) → Commit 3 (sidebar).
Chacun atomique, testé, non poussé. Lister les fichiers à chaque étape.
