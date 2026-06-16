# PHILIA SUMMER QUEST — Wireframe Écran de Session (Page 12)

**Document technique. Référence pour Cowork lors de l'implémentation Sprint 4.**
**Issu des décisions design du 15 juin 2026 (storyboard Miro + visuel de référence).**
**Cet écran est le plus important du produit : l'enfant y passe ~80% de son temps.**

---

## 1. VISION D'ENSEMBLE

L'écran de session est l'écran où l'enfant **apprend les mathématiques en dialoguant avec Archimède** via les 5 modes pédagogiques. L'écran doit être :

- **Immersif** : décor cinématographique en arrière-plan, interfaces UI superposées de manière diégétique
- **Lisible** : enfant 11-12 ans doit comprendre instantanément où regarder, où taper, où trouver ses récompenses
- **Pédagogiquement structurant** : le mode pédagogique en cours est explicite (métacognition)
- **Performant** : pas de latence perçue, image de fond chargée une fois et réutilisée

---

## 2. ZONES DE L'ÉCRAN

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│ ┌─[ZONE 1: SIDEBAR]─────┐                                       │
│ │ ≡ (toggle)            │       ┌─[ZONE 4: BADGE MODE]──┐       │
│ │                       │       │ ⚖ Mode Validation     │       │
│ │ Concept en cours      │       └────────────────────────┘       │
│ │ C1 - Sens fraction    │                                       │
│ │                       │              ┌─[ZONE 3: BULLE]──────┐ │
│ │ Cristaux 3/35         │              │ Texte d'Archimède    │ │
│ │ Clés 0/7              │              │ (scroll si long)     │ │
│ │ [Retour Carte]        │              └──────────────────────┘ │
│ │                       │                                       │
│ └───────────────────────┘  [ZONE 2: IMAGE FOND IMMERSIVE]       │
│                            Archimède 3/4 face                   │
│                            + élévateur 3/4 dos                  │
│                            + décor île + parchemin sur table    │
│                                                                 │
│           ┌─[ZONE 5: PARCHEMIN = HISTORIQUE]────────┐           │
│           │ Archimède : Bonjour, Élévateur...        │           │
│           │ Toi : Bonjour Archimède.                 │           │
│           │ Archimède : Vois-tu ce pont brisé ?      │           │
│           │ Toi : Oui, il est en morceaux.           │           │
│           │ ┌─[ZONE 5b: ENCART EXERCICE si actif]──┐ │           │
│           │ │ EXERCICE                              │ │           │
│           │ │ Une tarte est partagée en 6 parts.    │ │           │
│           │ │ Tu en prends 2. Écris la fraction.    │ │           │
│           │ │ [_] / [_]   [Valider]                 │ │           │
│           │ └───────────────────────────────────────┘ │           │
│           │ ↕ Scroll vertical si historique long       │           │
│           └────────────────────────────────────────────┘           │
│                                                                 │
│ ┌─[ZONE 6: INPUT TEXTE LIBRE]──────────────────────────────────┐│
│ │ Écris ta réponse à Archimède ici...           [Envoyer →]   ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Détail par zone

#### ZONE 1 — Sidebar Streamlit cachable (gauche)

**Élément Streamlit natif** : `st.sidebar` standard, l'utilisateur peut la fermer/ouvrir avec le bouton `≡` natif.

**Contenu** :
- Bloc "Concept en cours" : affiche le concept actif (ex. "C1 — Sens d'une fraction")
- Bloc "Porte-clés" : `X/7` clés obtenues (réutiliser le composant T7 existant)
- Bloc "Cristaux" : `X/35` cristaux + expanders par île (réutiliser T7)
- Bouton "Retour à la carte" (en bas)

**Code (réutilisation T7)** :
```python
def render_sidebar_session(concept_courant: str):
    with st.sidebar:
        st.markdown(f"### Concept en cours\n{concept_courant}")
        _render_sidebar_recompenses()  # déjà existant T7
        if st.button("← Retour à la carte"):
            st.session_state["ecran_courant"] = "carte"
            st.rerun()
```

#### ZONE 2 — Image de fond immersive

**Image** : `ile_N/ecran_session_<genre>.png` chargée en plein écran derrière les autres zones.

**Implémentation CSS** :
```css
.session-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-image: url('...');
    background-size: cover;
    background-position: center;
    z-index: 0;
}
```

**Sélection dynamique** :
```python
def chemin_fond_session() -> str:
    joueur = charger_joueur_courant()
    ile_id = st.session_state["ile_courante"]
    genre = joueur["avatar_genre"]
    return charger_scene_narrative_safe("ecran_session", ile_id)
```

#### ZONE 3 — Bulle d'Archimède

**Position** : en haut à droite de l'écran, par-dessus le décor (CSS overlay).

**Contenu** : dernier message d'Archimède (sortie LLM). Reste affiché tant qu'Archimède ne produit pas de nouveau message.

**Comportement texte long** : si le texte dépasse la hauteur de la bulle, scroll interne vertical (`overflow-y: auto`).

**Contrainte LLM** : limiter les réponses à 2-3 phrases (consigne dans le prompt système) pour rendre le scroll rare.

**Implémentation CSS** :
```css
.bulle-archimede {
    position: absolute;
    top: 80px;
    right: 40px;
    width: 380px;
    max-height: 200px;
    background: rgba(255, 250, 235, 0.95);
    border: 2px solid #C9A961;
    border-radius: 12px;
    padding: 16px 20px;
    font-family: 'Crimson Text', serif;
    overflow-y: auto;
    z-index: 10;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
.bulle-archimede::after {
    /* Pointe de phylactère orientée vers Archimède */
    content: '';
    position: absolute;
    bottom: -16px;
    left: 30px;
    border: 8px solid transparent;
    border-top-color: rgba(255, 250, 235, 0.95);
}
```

#### ZONE 4 — Badge mode pédagogique

**Position** : en haut au centre, au-dessus du badge.

**Comportement** :
- Lors d'un **changement de mode**, le badge apparaît animé (fade-in), reste pleinement visible 3 secondes, puis se réduit en indicateur permanent discret en haut au centre.
- L'enfant peut survoler/cliquer pour relire la description du mode.

**Implémentation** :
```python
MODES_INFO = {
    "decouverte": {"icone": "🔍", "nom": "Découverte", "couleur": "#5A8FB8"},
    "pratique": {"icone": "⚙", "nom": "Pratique", "couleur": "#7A9A6E"},
    "validation": {"icone": "⚖", "nom": "Validation", "couleur": "#C9A961"},
    "consolidation": {"icone": "💎", "nom": "Consolidation", "couleur": "#B8704A"},
    "bilan": {"icone": "📜", "nom": "Bilan", "couleur": "#E8DCC4"}
}
```

```css
.badge-mode {
    position: absolute;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255, 250, 235, 0.92);
    padding: 8px 20px;
    border-radius: 20px;
    border: 1px solid <couleur du mode>;
    font-family: 'Crimson Text', serif;
    z-index: 20;
}
.badge-mode-grand {
    /* État pleinement visible (3 secondes après changement) */
    transform: translateX(-50%) scale(1.2);
    box-shadow: 0 0 24px <couleur du mode>;
}
.badge-mode-petit {
    /* État permanent réduit */
    transform: translateX(-50%) scale(0.8);
    opacity: 0.7;
}
```

#### ZONE 5 — Parchemin = historique du chat

**Position** : zone centrale, sur le parchemin de l'image de fond (overlay CSS aligné sur le parchemin visible dans l'image).

**Contenu** :
- Historique complet du dialogue
- Format chaque message : `**Archimède** : texte` OU `**Toi** : texte`
- Le plus ancien en haut, le plus récent en bas
- Scroll vertical automatique vers le bas à chaque nouveau message

**Style** :
- Police manuscrite / serif élégante (à choisir avec Pierre)
- Texte de l'enfant en bleu marine (`#1E3A5F`)
- Texte d'Archimède en brun (`#5A4A3A`)
- Léger contraste pour distinguer

**Implémentation CSS** :
```css
.parchemin-historique {
    position: absolute;
    /* Alignement précis sur le parchemin de l'image — à ajuster pixel-perfect */
    top: 48%;
    left: 22%;
    width: 52%;
    height: 38%;
    background: rgba(245, 235, 210, 0.0);  /* Transparent : le parchemin est dans l'image */
    padding: 16px 32px;
    overflow-y: auto;
    font-family: 'Crimson Text', serif;
    font-size: 1.05rem;
    line-height: 1.5;
    z-index: 5;
}
```

**Effet visuel à l'envoi d'un message de l'enfant** : le texte que l'enfant a tapé dans la zone 6 **apparaît avec un fade-in** sur le parchemin comme dernière entrée. Effet "stylet qui écrit" optionnel via animation CSS keyframes.

#### ZONE 5b — Encart exercice formel (overlay sur le parchemin)

**Apparition** : quand Archimède propose un exercice formel (mode Pratique avec exercice structuré).

**Position** : à l'intérieur de la zone 5 (parchemin), comme dernière entrée mais avec un encadrement spécial.

**Contenu** :
- Titre "EXERCICE" en doré
- Énoncé de l'exercice (texte court)
- Champ(s) de saisie adapté(s) au type :
  - **Numérique** : `<input type="number">`
  - **Fraction** : 2 champs séparés par "/" visuellement
  - **Texte court** : `<input type="text">` court
  - **Choix multiple** : boutons radio (future extension)
- Bouton "Valider" doré

**Style** :
```css
.encart-exercice {
    background: rgba(255, 250, 235, 0.95);
    border: 2px solid #C9A961;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(201, 169, 97, 0.3);
}
.encart-exercice-titre {
    color: #C9A961;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}
.encart-exercice-enonce {
    font-style: italic;
    margin-bottom: 12px;
}
.fraction-input {
    display: flex;
    align-items: center;
    gap: 4px;
}
.fraction-input input {
    width: 60px;
    text-align: center;
}
.fraction-input .barre {
    width: 30px;
    height: 2px;
    background: #5A4A3A;
}
```

**Validation** :
- À la validation, on envoie la réponse au moteur pédagogique
- L'encart est remplacé par : `**Toi** : <réponse formatée>` dans l'historique
- Archimède réagit dans sa bulle (juste / faux / partiellement)

#### ZONE 6 — Input texte libre (chat ordinaire)

**Position** : en bas de l'écran, plein largeur (sauf si sidebar ouverte).

**Comportement** :
- Champ texte (`st.chat_input` Streamlit recommandé, ou input custom)
- Placeholder : "Écris ta réponse à Archimède ici..."
- Validation par Enter ou clic sur "Envoyer"
- À la validation : texte ajouté à l'historique zone 5, envoi au LLM, réponse Archimède dans zone 3

**Style** :
```css
.input-chat {
    position: fixed;
    bottom: 16px;
    left: 16px;
    right: 16px;
    background: rgba(255, 250, 235, 0.92);
    border: 1px solid #C9A961;
    border-radius: 12px;
    padding: 12px 16px;
    backdrop-filter: blur(4px);
    z-index: 15;
}
```

---

## 3. ÉTATS DE L'ÉCRAN

### État initial (entrée en session)

- Image de fond chargée
- Sidebar visible avec concept courant
- Badge mode "Découverte" affiché pleinement (3s) puis réduit
- Bulle d'Archimède : premier message (introduction du concept)
- Parchemin : vide ou avec le premier message d'Archimède recopié

### État "Archimède réfléchit" (LLM en train de répondre)

- Bulle d'Archimède : animation "..." (3 points qui se succèdent)
- Input de l'enfant désactivé temporairement
- Sidebar reste interactive

### État "Exercice en cours"

- Encart exercice affiché dans le parchemin
- Input chat libre **désactivé** (ou avec placeholder "Réponds à l'exercice ci-dessus")
- Bouton "Valider" de l'exercice activé

### État "Changement de mode"

- Badge mode prend la forme "grande" pendant 3 secondes avec couleur dominante
- Bulle d'Archimède : phrase de transition ("Maintenant, explique-moi..." pour Validation)
- Décor : optionnellement, légère teinte différente (à itérer post-MVP)

### État "Gain de cristal"

- Animation CSS : un cristal apparaît au centre de l'écran, brille, se déplace vers la sidebar et s'incorpore dans le compteur
- Son optionnel : tintement bref (post-MVP)
- Durée : ~3 secondes
- Pendant l'animation, le reste de l'écran est légèrement assombri

---

## 4. STATE MACHINE (session_state Streamlit)

```python
# Clés session_state pour la page 12
st.session_state["ecran_courant"]      # = "session_chat"
st.session_state["ile_courante"]       # "ile_1", "ile_2", "ile_3"
st.session_state["session_concept"]    # "C1", "C2", "C3", "C4", "C5"
st.session_state["mode_pedagogique"]   # "decouverte" | "pratique" | "validation" | "consolidation" | "bilan"
st.session_state["historique_chat"]    # liste de tuples (role, texte) — role = "archimede" | "eleve"
st.session_state["dernier_message_archimede"]  # texte affiché dans la bulle
st.session_state["exercice_actif"]     # None ou dict {type, enonce, format_reponse}
st.session_state["badge_mode_grand"]   # bool — pour animation 3s
```

---

## 5. INTERACTIONS LLM

### Prompt système (pour Sprint 4)

Le LLM (Claude Sonnet 4.6) recevra à chaque tour :
- Le système prompt (mode pédagogique courant + persona Archimède)
- L'historique complet du dialogue
- Le nouveau message de l'enfant

**Contraintes obligatoires dans le system prompt** :
- Réponses courtes (2-3 phrases max par tour) pour rendre le scroll bulle rare
- Une question à la fois
- Toujours en maïeutique : ne jamais donner directement la réponse
- Adaptation au mode courant (5 modes définis)

### Format de sortie attendu du LLM

Le LLM doit produire un **JSON structuré** (à définir précisément dans le brief Sprint 4) :
```json
{
  "message_bulle": "Texte d'Archimède affiché dans la bulle",
  "nouveau_mode": "validation",  // ou null si pas de changement
  "exercice_propose": null,       // ou dict {type, enonce, format_reponse}
  "concept_valide": false,        // true si Archimède valide la maîtrise du concept
  "cristal_gagne": null            // ou nom du cristal si gain
}
```

Cowork devra parser ce JSON et :
- Afficher `message_bulle` dans la bulle d'Archimède
- Détecter `nouveau_mode` → animer le badge mode
- Afficher l'encart si `exercice_propose`
- Déclencher l'animation gain cristal si `cristal_gagne`

---

## 6. RECOMMANDATIONS PRODUCTION GRAPHIQUE

### Pour l'image de fond `ecran_session_<genre>.png`

**Contraintes pour Midjourney** :
- Composition strictement validée le 15 juin 2026 (cf. image de référence)
- Archimède à gauche, 3/4 face, expressif
- Élévateur à droite, 3/4 dos, en train d'écrire sur le parchemin
- Parchemin central : grande zone clean (l'overlay CSS y posera l'historique)
- Décor en arrière-plan adapté à l'île
- **Pas de texte sur l'image** (sauf labels narratifs subtils comme "Fenêtre de chat d'Archimède IA" — à débattre)

### Variations par île

| Île | Décor d'arrière-plan |
|---|---|
| Île 1 — Nombres Brisés | Vue sur ruines avec fractions sculptées, pont brisé visible |
| Île 2 — Forêt des Mesures | Aqueduc antique, mesures gravées, cyprès |
| Île 3 — Labyrinthe des Inconnues | Marbre, équations avec X gravées, palais grec |

---

## 7. DETTE TECHNIQUE / À ITÉRER POST-MVP

- **Effet "stylet qui écrit"** sur le parchemin : intéressant mais peut être faux ami visuel. Test utilisateur nécessaire.
- **Scroll dans la bulle d'Archimède** : si les enfants ratent du texte, basculer en bulle qui s'agrandit (Option ii).
- **Variantes émotionnelles d'Archimède** : actuellement, l'image de fond est statique. Plus tard : variantes pour réussite, échec, encouragement (3-4 expressions × 6 images = 24 images supplémentaires).
- **Sons** : tintement gain cristal, son d'écriture sur parchemin, voix Archimède (couches A/B/C TTS prévues).
- **Badge mode au survol** : afficher une infobulle expliquant le mode courant à l'enfant qui découvre.

---

## 8. CRITÈRES DE VALIDATION D'IMPLÉMENTATION (Sprint 4)

- [ ] Image de fond charge en moins de 500ms (cache Streamlit @st.cache_resource)
- [ ] Bulle d'Archimède affiche le texte sans débordement
- [ ] Scroll dans la bulle fonctionne si texte long
- [ ] Badge mode s'anime correctement à chaque changement
- [ ] Parchemin scrolle automatiquement vers le bas à chaque nouveau message
- [ ] Input chat libre fonctionne avec Enter et bouton Envoyer
- [ ] Encart exercice s'affiche correctement avec champs adaptés (numérique, fraction, texte)
- [ ] Validation d'exercice met à jour l'historique et déclenche réponse Archimède
- [ ] Sidebar Streamlit reste fonctionnelle et cachable
- [ ] Sélection automatique fille/garçon selon avatar du joueur
- [ ] Fallback placeholder pour images manquantes

---

*Wireframe Écran de Session — version 1, 15 juin 2026.*
*À utiliser comme référence par Cowork lors du Sprint 4 (implémentation moteur pédagogique + UI session).*
