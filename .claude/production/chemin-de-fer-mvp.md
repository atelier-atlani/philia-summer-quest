# PHILIA SUMMER QUEST — Chemin de Fer Narratif MVP V2

**Document de production. Référence pour Seb (Midjourney), Pierre (habillage UI), Cowork (intégration code).**
**Périmètre : MVP 3 îles, livraison 1er juillet 2026.**
**V2 — Mise à jour 13 juin 2026 après storyboard Miro + décisions design écran de session.**

---

## 0. PRINCIPES DIRECTEURS

**Personnalisation visuelle MVP** : 2 versions par scène narrative (fille / garçon). Voir D18.

**Personnages canoniques** :
- Fille : **Sassou** (architecte, brune, cheveux courts, lunettes optionnelles)
- Garçon : **Mélian** (explorateur, brun, à confirmer après validation visuelle de la première version)

**Style visuel global** : aquarelle Studio Ghibli / Pixar / antique Syracuse. Lumière douce, palette terre cuite + vert sauge + ivoire + bleu nuit + or vieilli.

**Architecture immersive** : décor cinématographique en fond, interfaces UI superposées en CSS de manière diégétique (parchemin, bulle, badge mode).

---

## 1. STRUCTURE NARRATIVE COMPLÈTE (19 pages identifiées)

### Phase 1 — Lancement & Onboarding (pages 1 à 6 bis)

| # | Page | Codé ? | Image ? | Fichier(s) | Versions |
|---|---|---|---|---|---|
| 1 | Splash | À faire | Logo Philia | `ui/splash.png` (Pierre) | Unique |
| 2 | Accueil narratif | T6 ✅ | Avatar Archimède | `assets/mentor/.../mentor_archimede_reference.png` | Unique |
| 3 | Choix du genre | T6 ✅ | UI pure | — | — |
| 4 | Grille 4 avatars | T6 ✅ | 8 portraits Syracuse | Existants | Unique |
| 5 | Confirmation | T6 ✅ | Avatar choisi | Existants | Unique |
| 6 | Bienvenue Archimède | T6 ✅ | Avatar Archimède | Existant | Unique |
| **6 bis** | **Présentation archipel** | **À faire** | **Oui** | `globaux/presentation_archipel_<genre>.png` | F + G |

### Phase 2 — Carte (page 7)

| # | Page | Codé ? | Image ? | Fichier(s) | Versions |
|---|---|---|---|---|---|
| 7 | Carte interactive | T5 + T7 ✅ | Carte | `ui/carte_archipel.png` | Existant |

### Phase 3 — Entrée sur une île (pages 8 à 10)

| # | Page | Codé ? | Image ? | Fichier(s) | Versions |
|---|---|---|---|---|---|
| 8 | Vue immersive île | À faire | Oui | `ile_N/vue_immersive.png` | Unique (sans perso) |
| 9 | Arrivée Archimède + élévateur | À faire | Oui | `ile_N/arrivee_<genre>.png` | F + G |
| 10 | Présentation île par Archimède | À faire | Oui | `ile_N/presentation_<genre>.png` | F + G |

### Phase 4 — Session pédagogique (pages 11 à 15)

| # | Page | Codé ? | Image ? | Fichier(s) | Versions |
|---|---|---|---|---|---|
| 11 | Planche BD ouverture C1 | À faire | Oui | `ile_N/planche_bd_c1_<genre>.png` | F + G |
| 11 bis | Planche BD synthèse C5 | À faire | Oui | `ile_N/planche_bd_c5_<genre>.png` | F + G |
| **12** | **Écran de session (chat maïeutique)** ⭐ | **À faire Sprint 4** | **Oui** | `ile_N/ecran_session_<genre>.png` | F + G |
| 13 | Mode Validation Feynman | À faire | Variation page 12 | (badge CSS + même fond) | — |
| 14 | Gain Cristal | À faire | Effet CSS | — | — |
| 15 | Fin de session | À faire | Réutilise fond île | — | — |

### Phase 5 — Sessions C2 à C5

Réutilise pages 12-15. Seule la Session 5 ajoute la page 11 bis.

### Phase 6 — Rite d'Élévation (pages 16 à 19)

| # | Page | Codé ? | Image ? | Fichier(s) | Versions |
|---|---|---|---|---|---|
| 16 | Cinématique intro Rite | À faire | Oui | `ile_N/rite_intro_<genre>.png` | F + G |
| 17 | 4 Sceaux à résoudre | À faire | Template + UI | `globaux/sceau_template.png` | Unique |
| 18 | Cinématique fin Rite + gain clé | À faire | Oui | `ile_N/rite_fin_<genre>.png` | F + G |
| 19 | Animation élévation île | À faire | CSS sur carte | `ui/carte_archipel.png` + effets | Existant |

---

## 2. ÉCRAN DE SESSION (page 12) — WIREFRAME COMPLET

L'écran de session est **le plus important du produit** (l'enfant y passe 80% de son temps). Décisions design validées le 13 juin 2026 :

### Zones de l'écran

```
┌─────────────────────────────────────────────────────────────────┐
│ [≡ SIDEBAR cachable]            [⚖ Mode Validation] ← badge mode│
│                                                                 │
│                              [BULLE ARCHIMÈDE]                  │
│                              ┌─────────────────┐                │
│      [IMAGE FOND immersif    │ Texte LLM       │                │
│       Archimède de face      │ (scroll si long)│                │
│       + élévateur 3/4 dos    └─────────────────┘                │
│       + décor île]                                              │
│                                                                 │
│              ┌───────────────────────────────┐                  │
│              │ PARCHEMIN — historique chat   │                  │
│              │ Archimède : ...               │                  │
│              │ Toi : ...                     │                  │
│              │ ┌───────────────────────────┐ │ ← exercice formel│
│              │ │ EXERCICE [encart doré]    │ │   si applicable  │
│              │ │ Énoncé                    │ │                  │
│              │ │ [_] / [_]   [Valider]     │ │                  │
│              │ └───────────────────────────┘ │                  │
│              │ ↕ scroll                       │                  │
│              └───────────────────────────────┘                  │
│                                                                 │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ [Zone de saisie translucide]                [Envoyer]      │  │
│ └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Décisions design actées

1. **Image de fond cadrée (Option B)** : l'image occupe ~70-80% de l'écran, encadrée par un style "cahier d'aventures"
2. **Bulle d'Archimède** : reste visible tant qu'Archimède ne parle pas à nouveau. Si texte trop long, scroll interne dans la bulle.
3. **Parchemin = historique complet** : tous les anciens messages restent visibles, scroll vertical si trop long. Bonus parental (le parent voit le dialogue).
4. **Sidebar Streamlit native cachable** : cristaux X/35, clés X/7, retour carte, indicateur concept en cours
5. **Input en bas plein largeur** : zone de saisie translucide. À validation, le texte de l'enfant **apparaît sur le parchemin** comme dernière entrée.
6. **Badge mode pédagogique** : icône + texte explicite en haut au centre, apparaît 3 secondes lors d'un changement de mode, puis reste en discret indicateur permanent.
7. **Exercices formels** : mini-encart sur le parchemin (cadre doré), champ de saisie adapté (numérique / fraction à 2 champs / texte court), bouton "Valider" dédié.

### Icônes des 5 modes pédagogiques

À utiliser dans le badge en haut + dans l'indicateur permanent :

| Mode | Icône | Couleur dominante badge |
|---|---|---|
| Découverte | 🔍 | Bleu doux |
| Pratique | ⚙ | Vert sauge |
| Validation | ⚖ | Or vieilli |
| Consolidation | 💎 | Terre cuite |
| Bilan | 📜 | Ivoire / blanc cassé |

### Recommandation LLM (pour Sprint 4)

Le scroll dans la bulle d'Archimède doit rester **rare**. Pour cela, contraindre le LLM dans le prompt système :
> "Tes réponses doivent être courtes : 2-3 phrases maximum par tour. Une question à la fois. Si tu as plus à dire, attends la prochaine intervention de l'élève."

C'est aussi cohérent avec la pédagogie maïeutique : Archimède ne fait pas de monologue, il pose une question, attend une réponse, rebondit.

---

## 3. INVENTAIRE COMPLET DES IMAGES MVP V2

### Récapitulatif quantitatif

| Catégorie | Nombre d'images | Versions par image | Total |
|---|---|---|---|
| Globaux (réutilisables toutes îles) | 2 | F+G ou unique | 3 |
| Vues immersives d'île | 3 | Unique | 3 |
| Scènes narratives par île (arrivée, présentation, rite intro, rite fin) | 4 × 3 = 12 | F + G | 24 |
| Planches BD ouverture (C1) | 3 | F + G | 6 |
| Planches BD synthèse (C5) | 3 | F + G | 6 |
| **Écran de session (NOUVEAU V2)** | **3** | **F + G** | **6** |
| **TOTAL MVP 3 îles V2** | | | **48** |

### Détail des 48 images

**Globaux (3 images)**
- `globaux/presentation_archipel_fille.png`
- `globaux/presentation_archipel_garcon.png`
- `globaux/sceau_template.png`

**Par île (15 images × 3 = 45)**
- `ile_N/vue_immersive.png` (1)
- `ile_N/arrivee_fille.png` + `arrivee_garcon.png` (2)
- `ile_N/presentation_fille.png` + `presentation_garcon.png` (2)
- `ile_N/planche_bd_c1_fille.png` + `planche_bd_c1_garcon.png` (2)
- `ile_N/planche_bd_c5_fille.png` + `planche_bd_c5_garcon.png` (2)
- `ile_N/ecran_session_fille.png` + `ecran_session_garcon.png` (2) ← NOUVEAU V2
- `ile_N/rite_intro_fille.png` + `rite_intro_garcon.png` (2)
- `ile_N/rite_fin_fille.png` + `rite_fin_garcon.png` (2)

---

## 4. INVENTAIRE DES IMAGES DÉJÀ PRODUITES

État au 15 juin 2026 :

| Fichier source | Cible chemin de fer | Statut |
|---|---|---|
| `presentation-archipel-archimede-elevateur-fille-architecte.png` | `globaux/presentation_archipel_fille.png` | À renommer et intégrer |
| `l-ile-des-nombres-brises.png` | `ile_1/vue_immersive.png` | À renommer et intégrer |
| `arrivee-ile-nombres-brises.png` | `ile_1/arrivee_fille.png` | À renommer et intégrer |
| `presentation-ile-nombres-brises-elevateur-fille-architecte.png` | `ile_1/presentation_fille.png` | À renommer et intégrer |
| `philia_Comic_strip_layout_Philia_inspired...png` (planche BD du 13 juin) | `ile_1/planche_bd_c1_fille.png` | À renommer et intégrer |
| **`ChatGPT_Image_15_juin_2026__17_26_35.png` (écran de session)** | **`ile_1/ecran_session_garcon.png`** (à confirmer) | **À renommer et intégrer (NOUVEAU V2)** |

**Bilan V2** : **6 images produites sur 48 cibles.**
**Reste à produire** : **42 images.**

---

## 5. PLAN DE PRODUCTION SUR 16 JOURS (15 juin → 1er juillet)

### Charge ajustée

42 images / 16 jours = **2.6 images / jour** en moyenne.

Charge journalière estimée : **40-60 minutes** de production graphique avec la méthode prompt structurée + IA d'aide aux prompts.

### Découpage proposé V2

| Phase | Période | Production cible | Cumul |
|---|---|---|---|
| **Phase 1** — Compléter Île 1 (versions garçon + planches BD C5 + écran session fille) | J+1 → J+4 (4 jours) | 8 images Île 1 + 2 globaux garçon | 10 images |
| **Phase 2** — Île 2 complète | J+5 → J+10 (6 jours) | 15 images | 25 cumulées |
| **Phase 3** — Île 3 complète | J+11 → J+14 (4 jours) | 15 images | 40 cumulées |
| **Phase 4** — Sceau template + retouches | J+15 → J+16 (2 jours) | 2 images + finitions | 42 cumulées |

**Marge de sécurité** : 1-2 jours en fin de période pour bugs visuels et ajustements.

---

## 6. WORKFLOW DE PRODUCTION

### Pour chaque image à produire

1. **Définir le prompt** en utilisant le template (voir document `prompts-midjourney-template.md` V2)
2. **Générer 4 variantes** Midjourney (1 commande, 4 propositions)
3. **Sélectionner la meilleure variante** selon critères : cohérence personnages, palette, lisibilité narrative
4. **Upscale** la variante retenue
5. **Retouche éventuelle** (recadrage, ajustement densité)
6. **Renommer** selon convention
7. **Placer** dans le dossier cible `assets/narratif/...`
8. **Commit Git** par lot de 5-10 images

### Pour les versions garçon depuis les versions fille

- Reprendre le même prompt
- Remplacer le bloc description Sassou par le bloc description Mélian
- Garder strictement le même bloc scène + style + composition
- Générer et choisir la variante qui correspond le mieux en composition à la version fille

### Sur le cas de l'image écran de session du 15 juin

L'image produite montre un élévateur **avec des mèches bleues + tunique terre cuite + écharpe bleue**, qui diffère de la description canonique Mélian (brun sage green + boussole). Trois options à trancher avec Seb :
- **A** : c'est un brouillon, on regénère selon le canon Mélian strict
- **B** : on adopte cette variante visuelle comme nouveau canon Mélian (mise à jour de D18 et du prompt template)
- **C** : on garde cette image telle quelle pour Île 1 uniquement, et on ajuste pour les autres îles

---

## 7. RÔLE DE PIERRE (graphiste)

Pierre produit l'**habillage UI** :
- Cadres décoratifs pour les scènes narratives (style cahier d'aventures)
- Templates de page (en-tête, transitions)
- Boutons, icônes, badges des modes pédagogiques (5 icônes)
- Animations CSS (élévation d'île, gain de cristal, gain de clé)
- Logo Philia Summer Quest + splash
- Style visuel des bulles, badges, encarts d'exercice

Pierre et Seb travaillent en parallèle sans dépendance critique.

---

## 8. INTÉGRATION CODE — RÈGLES POUR COWORK

### Sélection automatique de la version

```python
def charger_scene_narrative(contexte: str, ile_id: str | None = None) -> str:
    joueur = charger_joueur_courant()
    genre = joueur["avatar_genre"]

    if ile_id is None:
        chemin = f"assets/narratif/globaux/{contexte}_{genre}.png"
    else:
        if contexte == "vue_immersive":
            chemin = f"assets/narratif/{ile_id}/vue_immersive.png"
        else:
            chemin = f"assets/narratif/{ile_id}/{contexte}_{genre}.png"

    return chemin
```

### Gestion des images manquantes

```python
import pathlib

def charger_scene_narrative_safe(contexte: str, ile_id: str | None = None) -> str:
    chemin = charger_scene_narrative(contexte, ile_id)
    if not pathlib.Path(chemin).exists():
        return "assets/narratif/_placeholder/scene_a_venir.png"
    return chemin
```

### Structure de dossiers

```
assets/narratif/
├── _placeholder/
│   └── scene_a_venir.png
├── globaux/
│   ├── presentation_archipel_fille.png
│   ├── presentation_archipel_garcon.png
│   └── sceau_template.png
├── ile_1/
│   ├── vue_immersive.png
│   ├── arrivee_fille.png / arrivee_garcon.png
│   ├── presentation_fille.png / presentation_garcon.png
│   ├── ecran_session_fille.png / ecran_session_garcon.png   ← NOUVEAU V2
│   ├── planche_bd_c1_fille.png / planche_bd_c1_garcon.png
│   ├── planche_bd_c5_fille.png / planche_bd_c5_garcon.png
│   ├── rite_intro_fille.png / rite_intro_garcon.png
│   └── rite_fin_fille.png / rite_fin_garcon.png
├── ile_2/  (idem ile_1)
└── ile_3/  (idem ile_1)
```

---

## 9. CRITÈRES DE VALIDATION D'UNE IMAGE

1. **Cohérence personnages** : Archimède reconnaissable, Sassou/Mélian fidèles à leur description canonique
2. **Cohérence stylistique** : aquarelle, lumière douce, palette respectée
3. **Lisibilité narrative** : la scène raconte ce qu'elle doit raconter
4. **Qualité technique** : pas de défauts majeurs anatomiques
5. **Cadrage exploitable** : composition compatible avec l'affichage UI prévu
6. **Pour l'écran de session** : zone parchemin centrale dégagée pour permettre l'overlay du chat

Si une image échoue à plus de 2 critères, **regénérer** plutôt que retoucher.

---

## 10. PROCHAINES ÉTAPES IMMÉDIATES

1. **Commit V2** : ce document + prompts V2 + wireframe écran de session
2. **Trancher le canon Mélian** (option A/B/C ci-dessus) à partir de l'image du 15 juin
3. **Renommer les 6 images déjà produites** dans `assets/narratif/`
4. **Créer le placeholder** `assets/narratif/_placeholder/scene_a_venir.png`
5. **Brief T8 ajusté** : test E2E avec l'écran de session (placeholders pour images non encore produites)
6. **Démarrer production Phase 1** : Île 1 versions garçon + planches BD C5

---

*Chemin de Fer Narratif MVP V2 — version 2, 15 juin 2026.*
*Mise à jour majeure : ajout écran de session (6 images, total 48), wireframe détaillé page 12, contraintes LLM.*
