# Dette technique post-T8.5

**Ouvert** : 15 juillet 2026
**À traiter** : Sprint polish semaine 4 ou plus tôt selon impact test cobaye

---

## Dette 1 — Mécanique `<a href>` fragile dans ecran_carte.py

**Localisation** : `ui/ecran_carte.py`

**Description** : navigation Carte → Île via `<a href="?ile=X">` au lieu de `st.button()` ou `st.query_params`. Fonctionne au clic souris mais échoue en tests automatisés.

**Correctif proposé** : refactor vers un pattern Streamlit natif (`st.button()` avec `st.session_state["ile_courante"]` puis `st.rerun()`).

**Effort estimé** : 30 min.

**Priorité** : moyenne — à traiter si test cobaye révèle problème réel, sinon Sprint polish.

---

## Dette 2 — Textes non discriminants entre écrans successifs

**Localisation** : `ui/ecran_presentation_archipel.py` + sous-étape arrivée de `ui/ecran_ile.py`

**Description** : confusion visuelle/narrative entre présentation archipel et arrivée Île 1 (voir Bug UI 3 dans polish-bugs-ui.md).

**Correctif proposé** : réécriture des textes narratifs pour marquer clairement la distinction (archipel = 7 îles + mission globale, arrivée = Syracuse spécifique).

**Effort estimé** : 1h (réécriture + audit visuel).

**Priorité** : moyenne (Sprint polish).

---

## Dette 3 — Assets `ecran_session_<genre>.png` à refondre

**Localisation** : `assets/narratif/globaux/ecran_session_<genre>.png`

**Description** : les images actuelles contiennent une bulle vide destinée au chat, mais Streamlit ne peut pas y intégrer le widget. La bulle reste vide.

**Correctif proposé** : re-générer les 2 images en variante "bandeau décoratif sans bulle vide" via Midjourney.

**Effort estimé** : 1-2h (nouvelles prompts + audit + intégration).

**Priorité** : haute (Sprint polish avant test cobaye final).

---

## Dette 4 — Auditer toutes les tailles d'images (`st.image` sans `use_container_width`)

**Localisation** : tous les fichiers de `ui/`

**Description** : les images narratives sont trop petites (Bug UI 2). Manque d'immersion.

**Correctif proposé** : audit systématique + ajout `use_container_width=True` par défaut.

**Effort estimé** : 1h.

**Priorité** : haute (Sprint polish).

---

## L2.0 — Généraliser `afficher_celebration_fin_ile` avant l'Île 2

**Localisation** : `ui/celebrations.py`

**Description** : le texte de célébration forte de fin d'île (`_MESSAGE_FIN_ILE_1`, ajouté en T8.6.1) est rédigé spécifiquement pour l'Île 1 (« Clé du Partage, la première de ton voyage », « Île des Nombres Brisés »). La fonction `afficher_celebration_fin_ile(prenom, nom_ile)` reste, elle, générique et sera rappelée telle quelle à la fin des Îles 2 et 3 dès que leur contenu pédagogique existera (`contenu_ile2.py`, `contenu_ile3.py`) — elle affichera alors, par erreur, le texte de l'Île 1 (mauvais nom d'île, mauvaise numérotation de clé).

**Correctif proposé** : avant que l'Île 2 soit jouable, remplacer `_MESSAGE_FIN_ILE_1` par un texte paramétré par île — soit un dict `ile_id -> template`, soit un template générique validé par le Décideur qui ne mentionne plus "la première de ton voyage" mais s'adapte au rang de l'île complétée.

**Effort estimé** : 30 min de câblage + rédaction du/des texte(s) par le Décideur (pas improvisée par l'Implementer, même règle que D-T8.6-F).

**Priorité** : haute — bloquant fonctionnel dès que l'Île 2 a du contenu jouable, pas juste une amélioration de confort.

**Dépendance** : contenu pédagogique Île 2 (`pedagogie/contenu_ile2.py`), actuellement inexistant.

---

## P1.1 — Étendre la réduction des illustrations aux écrans restants

**Localisation** : `ui/ecran_ile.py`, `ui/ecran_carte.py`, `ui/ecran_presentation_archipel.py`, `ui/celebrations.py`, `ui/modal_planche_bd.py`

**Description** : le chargeur partagé `ui/images.py` réduit les illustrations à 1200 px avant envoi ; il n'est câblé que sur le portail d'accès et l'écran d'accueil. Les autres écrans servent encore leurs assets en pleine définition.

À ne pas confondre avec D4, qui porte sur la taille d'AFFICHAGE (immersion). Ici il s'agit du poids TRANSMIS.

Chiffres mesurés au niveau réseau, dans un vrai navigateur, sur `accueil_invitation.png` : `st.image` ré-encode déjà en JPEG de lui-même (629 Ko, et non les 3,1 Mo du fichier) ; la réduction de dimensions fait tomber ce chiffre à 346 Ko, soit 45 % de moins. Les assets restants sont du même ordre voire plus lourds : `arrivee_fille.png` 3,7 Mo, `vue_immersive.png` 3,4 Mo, `carte_archipel.png` 3,3 Mo, présentations d'île ~2,8 Mo. Total `assets/` : 158 Mo.

**Correctif proposé** : remplacer chaque lecture d'illustration par `ui.images.charger_image()` — un import et un appel par écran. Le chargeur gère déjà les garde-fous.

**PIÈGE À NE PAS OUBLIER** : la transparence. `assets/ui/` contient des PNG en RGBA (`coffre.png`, `cle_partage.png`) ; aplatis en JPEG ils viendraient sur fond noir. `ui/images.py` détecte le canal alpha et reste alors en PNG — ne pas court-circuiter cette règle en réécrivant l'appel à la main.

**Effort estimé** : 30 min de câblage, plus une vérification visuelle par écran (surtout ceux qui portent des icônes).

**Priorité** : basse pour le lancement — utile, non bloquant. Reporté en v1.1 par arbitrage du Décideur (9 août 2026).

---

## Suivi

| Dette | État | Deadline |
|---|---|---|
| D1 (`<a href>`) | ⏳ | Selon test cobaye |
| D2 (textes archipel/île) | ⏳ | Sprint polish |
| D3 (assets chat) | ⏳ | Sprint polish avant test final |
| D4 (tailles images) | ⏳ | Sprint polish |
| L2.0 (célébration fin d'île générique) | ⏳ | Avant qu'Île 2 soit jouable |
| P1.1 (poids des illustrations) | ⏳ | v1.1, après lancement |

---

*Ouvert par Product Architect (Claude.ai) le 15 juillet 2026 suite au merge T8.5 f77dc86.*
*L2.0 ajoutée le 20 juillet 2026 suite à T8.6.1.*
*P1.1 ajoutée le 9 août 2026 suite à l'habillage du portail (commit 6243751).*