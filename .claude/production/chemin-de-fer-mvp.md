# PHILIA SUMMER QUEST — Chemin de Fer Narratif MVP

**Document de production. Référence pour Seb (Midjourney), Pierre (habillage UI), Cowork (intégration code).**
**Périmètre : MVP 3 îles, livraison 1er juillet 2026.**
**Acté lors de la session du 13 juin 2026 (Sprint 3, jour 4). S'appuie sur la décision D18.**

---

## 0. PRINCIPES DIRECTEURS

**Personnalisation visuelle MVP** : 2 versions par scène narrative (fille / garçon). Voir D18.

**Personnages canoniques** :
- Fille : **Sassou** (architecte, brune, cheveux courts, lunettes optionnelles)
- Garçon : **Mélian** (explorateur, brun)

**Style visuel global** : aquarelle Studio Ghibli / Pixar / antique Syracuse. Lumière douce, palette terre cuite + vert sauge + ivoire + bleu nuit + or vieilli. Pas de glow vidéoludique, pas de couleurs saturées.

**Compatibilité Archimède** : présence cohérente — cheveux gris ondulés, barbe taillée, lunettes rondes dorées, robe bleue à motifs mathématiques, cape ivoire, grande clé suspendue à la ceinture.

---

## 1. STRUCTURE NARRATIVE COMPLÈTE (1.1 → 4.6)

### Phase 1 — Lancement (première fois)

| # | Étape | Type | Image ? | Fichier(s) | Versions |
|---|---|---|---|---|---|
| 1.1 | Onboarding texte + choix avatar | Écran T6 | Non | — | — |
| 1.2 | Bienvenue d'Archimède | Écran texte | Non | — | — |
| 1.3 | Présentation de l'archipel | Cinématique narrative | **Oui** | `globaux/presentation_archipel_<genre>.png` | F + G |
| 1.4 | Découverte carte interactive | Écran T5 | Non | `ui/carte_archipel.png` (existant) | Existant |
| 1.5 | Clic sur Île 1 | Transition | Non | — | — |

### Phase 2 — Session de jeu (Île N, Session 1)

| # | Étape | Type | Image ? | Fichier(s) | Versions |
|---|---|---|---|---|---|
| **2.0** | **Vue immersive de l'île** (NOUVEAU) | Fond d'immersion | **Oui** | `ile_N/vue_immersive.png` | Unique (pas de perso) |
| 2.1 | Arrivée Archimède + élévateur sur l'île | Cinématique narrative | **Oui** | `ile_N/arrivee_<genre>.png` | F + G |
| 2.2 | Présentation de l'île par Archimède (atelier) | Cinématique narrative | **Oui** | `ile_N/presentation_<genre>.png` | F + G |
| 2.3 | Planche BD ouverture Session 1 (concept C1) | Planche BD multi-cases | **Oui** | `ile_N/planche_bd_c1_<genre>.png` | F + G |
| 2.4 | Dialogue maïeutique sur C1 | Écran chat + avatar sidebar | Non | — | — |
| 2.5 | Validation Feynman | Écran chat | Non | — | — |
| 2.6 | Gain du Cristal C1 | Effet CSS + icône sidebar | Non | — | — |
| 2.7 | Retour île ou continuer | Transition | Non | — | — |

### Phase 3 — Sessions C2 à C5 (Île N)

| # | Étape | Type | Image ? | Fichier(s) | Versions |
|---|---|---|---|---|---|
| 3.1 | Session C2 (juste part) | Chat + avatar sidebar | Non | — | — |
| 3.2 | Session C3 (reflet) | Chat + avatar sidebar | Non | — | — |
| 3.3 | Session C4 (balance) | Chat + avatar sidebar | Non | — | — |
| 3.4 | Session C5 (assemblage, anticipation 5e) | Chat + planche BD synthèse | **Oui** | `ile_N/planche_bd_c5_<genre>.png` | F + G |

**Note pédagogique** : C5 reçoit une planche BD pour deux raisons : (1) c'est le concept-pivot de l'anticipation 5e, un palier symbolique ; (2) la planche permet de visualiser la synthèse des concepts précédents avant le Rite. C1 = ouverture narrative, C5 = clôture narrative.

### Phase 4 — Rite d'Élévation (Île N)

| # | Étape | Type | Image ? | Fichier(s) | Versions |
|---|---|---|---|---|---|
| 4.1 | Cinématique d'introduction du Rite | Cinématique narrative | **Oui** | `ile_N/rite_intro_<genre>.png` | F + G |
| 4.2 | 4 Sceaux à résoudre | Visuel récurrent | **Oui** | `globaux/sceau_template.png` | Unique |
| 4.3 | Cinématique de fin du Rite (triomphe) | Cinématique narrative | **Oui** | `ile_N/rite_fin_<genre>.png` | F + G |
| 4.4 | Gain de la Clé Île N | Effet CSS + clé sidebar | Non | — | — |
| 4.5 | Animation élévation de l'île | Effet CSS sur carte | Non | — | — |
| 4.6 | Retour carte (île N+1 accessible) | Écran T5 | Non | — | — |

---

## 2. INVENTAIRE COMPLET DES IMAGES MVP

### Récapitulatif quantitatif

| Catégorie | Nombre d'images | Versions par image | Total |
|---|---|---|---|
| Globaux (réutilisables toutes îles) | 2 | F+G ou unique | 3 |
| Vues immersives d'île | 3 | Unique | 3 |
| Scènes narratives par île (arrivée, présentation, rite intro, rite fin) | 4 × 3 = 12 | F + G | 24 |
| Planches BD ouverture (C1) | 3 | F + G | 6 |
| Planches BD synthèse (C5) | 3 | F + G | 6 |
| **TOTAL MVP 3 îles** | | | **42** |

### Détail des 42 images

**Globaux (3 images)**
- `globaux/presentation_archipel_fille.png`
- `globaux/presentation_archipel_garcon.png`
- `globaux/sceau_template.png`

**Île 1 — L'Île des Nombres Brisés (13 images)**
- `ile_1/vue_immersive.png` (unique, pas de perso)
- `ile_1/arrivee_fille.png` / `ile_1/arrivee_garcon.png`
- `ile_1/presentation_fille.png` / `ile_1/presentation_garcon.png`
- `ile_1/planche_bd_c1_fille.png` / `ile_1/planche_bd_c1_garcon.png`
- `ile_1/planche_bd_c5_fille.png` / `ile_1/planche_bd_c5_garcon.png`
- `ile_1/rite_intro_fille.png` / `ile_1/rite_intro_garcon.png`
- `ile_1/rite_fin_fille.png` / `ile_1/rite_fin_garcon.png`

**Île 2 — La Forêt des Mesures (13 images)**
Identique en structure à l'Île 1.

**Île 3 — Le Labyrinthe des Inconnues (13 images)**
Identique en structure à l'Île 1.

---

## 3. INVENTAIRE DES IMAGES DÉJÀ PRODUITES

État au 13 juin 2026 :

| Fichier source (à renommer) | Cible chemin de fer | Statut |
|---|---|---|
| `presentation-archipel-archimede-elevateur-fille-architecte.png` | `globaux/presentation_archipel_fille.png` | À renommer et intégrer |
| `l-ile-des-nombres-brises.png` | `ile_1/vue_immersive.png` | À renommer et intégrer |
| `arrivee-ile-nombres-brises.png` | `ile_1/arrivee_fille.png` | À renommer et intégrer |
| `presentation-ile-nombres-brises-elevateur-fille-architecte.png` | `ile_1/presentation_fille.png` | À renommer et intégrer |
| `philia_Comic_strip_layout_Philia_inspired...png` (la planche BD du 13 juin) | `ile_1/planche_bd_c1_fille.png` | À renommer et intégrer |

**Bilan** : **5 images produites sur 42 cibles.**
**Reste à produire** : **37 images.**

---

## 4. PLAN DE PRODUCTION SUR 18 JOURS (13 juin → 1er juillet)

### Charge par jour

37 images / 18 jours = **2.1 images / jour** en moyenne.

À ~10-15 minutes par génération Midjourney (incluant prompt, génération, sélection, retouche légère) :
**Charge journalière estimée : 30-45 minutes de production graphique** (hors blocages créatifs).

### Découpage proposé

| Phase | Période | Production cible | Cumul |
|---|---|---|---|
| **Phase 1** — Compléter Île 1 (versions garçon + planche BD C5) | J+1 → J+3 (3 jours) | 6 images garçon Île 1 + 2 BD C5 (F+G) | 8 images |
| **Phase 2** — Versions garçon des images globales | J+1 → J+3 | 1 image (présentation archipel garçon) | 1 image |
| **Phase 3** — Île 2 complète | J+4 → J+10 (7 jours) | 13 images | 22 images cumulées |
| **Phase 4** — Île 3 complète | J+11 → J+16 (6 jours) | 13 images | 35 images cumulées |
| **Phase 5** — Sceau template + retouches + intégration | J+17 → J+18 (2 jours) | 1 image + finitions | 36 images cumulées |

**Marge de sécurité** : 1 jour avant lancement (30 juin) pour bugs visuels et ajustements de dernière minute.

---

## 5. WORKFLOW DE PRODUCTION

### Pour chaque image à produire

1. **Définir le prompt** en utilisant le template (voir document `prompts-midjourney-template.md`)
2. **Générer 4 variantes** Midjourney (1 commande, 4 propositions)
3. **Sélectionner la meilleure variante** selon critères : cohérence personnages, cohérence palette, lisibilité narrative
4. **Upscale** la variante retenue
5. **Retouche éventuelle** (recadrage, ajustement densité, suppression défauts)
6. **Renommer** selon convention
7. **Placer** dans le dossier cible `assets/narratif/...`
8. **Commit Git** par lot de 5-10 images avec message descriptif

### Pour les versions garçon depuis les versions fille

Méthode recommandée :
- Reprendre le même prompt que la version fille
- Remplacer le bloc description Philia/Sassou par le bloc description Mélian
- Garder strictement le même prompt scène + style + composition
- Générer et choisir la variante qui correspond le mieux en composition à la version fille (pour cohérence inter-genres)

---

## 6. RÔLE DE PIERRE (graphiste, livraison sous quelques jours)

Pierre ne produit **pas les scènes narratives** (c'est ta production Midjourney). Pierre produit **l'habillage UI** :

- Cadres décoratifs pour les scènes narratives (style parchemin antique)
- Templates de page (en-tête, sidebar, transitions)
- Boutons, icônes, badges, cristaux finaux
- Animations CSS (effet d'élévation d'île, gain de cristal, gain de clé)
- Logo Philia Summer Quest

Pierre et toi travaillez en parallèle, **sans dépendance critique**. Si Pierre livre en retard, le MVP tient quand même grâce à un habillage UI minimaliste fait par Cowork.

---

## 7. INTÉGRATION CODE — RÈGLES POUR COWORK

### Sélection automatique de la version

```python
# Dans le code de chargement d'une scène narrative
def charger_scene_narrative(contexte: str, ile_id: str | None = None) -> str:
    """
    contexte : 'arrivee', 'presentation', 'planche_bd_c1', etc.
    ile_id : 'ile_1', 'ile_2', 'ile_3' ou None pour les globaux
    Retourne le chemin relatif vers l'image à charger.
    """
    joueur = charger_joueur_courant()
    genre = joueur["avatar_genre"]  # 'fille' ou 'garcon'

    if ile_id is None:
        # Image globale
        chemin = f"assets/narratif/globaux/{contexte}_{genre}.png"
    else:
        # Image spécifique d'île
        if contexte == "vue_immersive":
            # Pas de variante par genre
            chemin = f"assets/narratif/{ile_id}/vue_immersive.png"
        else:
            chemin = f"assets/narratif/{ile_id}/{contexte}_{genre}.png"

    return chemin
```

### Gestion des images manquantes

Pendant la production (jusqu'au 1er juillet), de nombreuses images n'existeront pas encore en local. Le code doit gérer gracieusement les fichiers manquants :

```python
import pathlib

def charger_scene_narrative_safe(contexte: str, ile_id: str | None = None) -> str:
    chemin = charger_scene_narrative(contexte, ile_id)
    if not pathlib.Path(chemin).exists():
        # Placeholder pendant la production
        return "assets/narratif/_placeholder/scene_a_venir.png"
    return chemin
```

**Le fichier `_placeholder/scene_a_venir.png`** est à créer (un simple visuel "Illustration à venir" avec le logo Philia, suffit pour le test E2E).

### Convention de structure

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
│   ├── arrivee_fille.png
│   ├── arrivee_garcon.png
│   ├── presentation_fille.png
│   ├── presentation_garcon.png
│   ├── planche_bd_c1_fille.png
│   ├── planche_bd_c1_garcon.png
│   ├── planche_bd_c5_fille.png
│   ├── planche_bd_c5_garcon.png
│   ├── rite_intro_fille.png
│   ├── rite_intro_garcon.png
│   ├── rite_fin_fille.png
│   └── rite_fin_garcon.png
├── ile_2/
│   └── (idem ile_1)
└── ile_3/
    └── (idem ile_1)
```

---

## 8. RÈGLES DE COHÉRENCE INTER-IMAGES

**Cohérence Archimède** :
- Cheveux gris ondulés tirés en arrière, barbe taillée blanche
- Lunettes rondes dorées
- Robe bleue à motifs mathématiques (fractions, géométrie) brodés or
- Cape ivoire flottante
- Grande clé antique suspendue à la ceinture
- Âge apparent : 58-62 ans
- Regard bleu chaleureux

**Cohérence Sassou (fille)** :
- Brune, cheveux courts au carré, frange ou raie
- Yeux bleu clair ou verts
- Tenue d'architecte : tunique claire, ceinture de cuir, sac à bandoulière en cuir vieilli
- Carnet et stylet souvent visibles
- Âge apparent : 13-15 ans
- Posture studieuse, attentive

**Cohérence Mélian (garçon)** :
- Brun foncé, cheveux courts ondulés
- Yeux noisette
- Tenue d'explorateur : tunique vert sauge, pantalon de toile, sandales montantes
- Sac d'exploration, boussole ou carte parfois visible
- Âge apparent : 13-15 ans
- Posture curieuse, observatrice

**Cohérence environnement** :
- Toujours univers antique méditerranéen (Syracuse, IIIe siècle av. J.-C.)
- Marbre, colonnes ioniques, oliviers, cyprès, mer Égée bleue
- Lumière dorée et chaleureuse
- Pas de technologie moderne visible

**Cohérence palette** :
- Beige clair / ivoire (dominante)
- Bleu nuit / bleu marbre (Archimède, ciel)
- Vert sauge / vert olive (végétation, Mélian)
- Terre cuite (accents)
- Or vieilli (détails ornementaux, clés)

---

## 9. CRITÈRES DE VALIDATION D'UNE IMAGE

Avant intégration, chaque image doit passer 5 critères :

1. **Cohérence personnages** : Archimède reconnaissable, Sassou/Mélian fidèles à leur description
2. **Cohérence stylistique** : aquarelle, lumière douce, palette respectée
3. **Lisibilité narrative** : la scène raconte ce qu'elle doit raconter (un enfant doit comprendre)
4. **Qualité technique** : pas de défauts majeurs (mains déformées, visages tordus, anomalies anatomiques)
5. **Cadrage exploitable** : composition compatible avec un affichage 16:9 ou 4:3 selon contexte UI

Si une image échoue à un critère, **regénérer** plutôt que tenter de retoucher.

---

## 10. PROCHAINES ÉTAPES

1. **Acter D18** dans `.claude/memory/decisions.md`
2. **Sauvegarder ce chemin de fer** dans `.claude/production/chemin-de-fer-mvp.md`
3. **Sauvegarder les templates de prompts** dans `.claude/production/prompts-midjourney-template.md`
4. **Renommer et intégrer les 5 images déjà produites** dans `assets/narratif/`
5. **Créer le placeholder** `assets/narratif/_placeholder/scene_a_venir.png`
6. **Démarrer brief T8** en parallèle de la production graphique

---

*Chemin de Fer Narratif MVP — version 1, 13 juin 2026.*
*Document vivant. À mettre à jour si une décision narrative évolue.*
