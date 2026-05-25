# GUIDE : Développement contenu marché immobilier (15 jours)

## 🎯 Mission

Créer le contenu pédagogique du mini-cours "Marché immobilier" en 3 niveaux (mondial/national/local) pour enrichir la formation agent-immo-formateur.

**Durée** : 15 jours  
**Environnement** : Qwen 3 8B (chat) + Qwen 2.5 Coder 7B (aide ponctuelle)  
**Branche** : `feat/mini-cours-marche`  
**Tag de retour** : `v1.0-stable`

---

## 🛡️ SÉCURITÉ : Points de contrôle

### ✅ Ce que tu PEUX faire (sans risque)
- ✅ Modifier UNIQUEMENT les fichiers dans `training/modules/marche/`
- ✅ Créer de nouveaux fichiers `.md` dans ce dossier
- ✅ Remplir `sources/sources_web.txt` et `sources/extraits_rag.txt`
- ✅ Commiter sur la branche `feat/mini-cours-marche`

### ❌ Ce que tu NE DOIS PAS faire
- ❌ Modifier AUCUN fichier Python (`.py`)
- ❌ Modifier les fichiers YAML
- ❌ Toucher au code de l'application
- ❌ Merger sur `main` (on fera ça ensemble dans 15j)

### 🆘 Si tu as cassé quelque chose
```bash
# Revenir au tag stable
git checkout v1.0-stable

# Recréer la branche propre
git branch -D feat/mini-cours-marche
git checkout -b feat/mini-cours-marche
```

---

## 📅 Planning suggéré (15 jours)

### Semaine 1 : Recherche et structure

**Jour 1-2 : Marché mondial**
- [ ] Recherche sources (FMI, OCDE, World Bank)
- [ ] Collecte chiffres clés 2025-2026
- [ ] Première version `01_marche_mondial.md`

**Jour 3-4 : Marché national France**
- [ ] Recherche sources (FNAIM, Notaires, INSEE)
- [ ] Collecte stats France (prix, volumes, crédit)
- [ ] Première version `02_marche_national_france.md`

**Jour 5 : Marché local template**
- [ ] Structure `03_marche_local_template.md`
- [ ] Identifier variables à localiser (ville, région, prix m²)

### Semaine 2 : Enrichissement et finalisation

**Jour 6-7 : Exemples terrain**
- [ ] Ajouter 2-3 exemples concrets par niveau
- [ ] Créer dialogues vendeur/agent

**Jour 8-9 : Extraits RAG**
- [ ] Sélectionner 10-15 extraits pertinents
- [ ] Remplir `sources/extraits_rag.txt`

**Jour 10-12 : Relecture et amélioration**
- [ ] Relire chaque fichier
- [ ] Vérifier ton (phrases courtes, verbes d'action)
- [ ] Valider toutes les sources

**Jour 13-15 : Documentation et commit final**
- [ ] Compléter `sources/sources_web.txt`
- [ ] Créer un fichier `CHANGELOG.md` résumant le travail
- [ ] Commit final et push

---

## 📝 Structure détaillée des fichiers .md

### Template à suivre pour chaque fichier

```markdown
# [Titre du niveau de marché]

## 1. Contexte actuel (2026)

### Chiffres clés
- **[Indicateur 1]** : [Valeur] ([Source], [Date])
- **[Indicateur 2]** : [Valeur] ([Source], [Date])
- **[Indicateur 3]** : [Valeur] ([Source], [Date])

### Tendances principales
1. **[Tendance 1]** : [Explication courte]
2. **[Tendance 2]** : [Explication courte]
3. **[Tendance 3]** : [Explication courte]

## 2. Points d'attention pour l'agent

### Ce qu'il faut savoir absolument
- **[Point 1]** : [Pourquoi c'est important]
- **[Point 2]** : [Pourquoi c'est important]
- **[Point 3]** : [Pourquoi c'est important]

### Arguments terrain à utiliser
- "Argument 1 à dire au vendeur/acquéreur"
- "Argument 2 à dire au vendeur/acquéreur"
- "Argument 3 à dire au vendeur/acquéreur"

## 3. Exemples concrets

### Exemple 1 : [Titre situation]
**Contexte** : [Décris la situation]

**Dialogue vendeur/agent** :
- **Vendeur** : "Question ou objection du vendeur"
- **Agent** : "Réponse de l'agent utilisant les données du marché"

### Exemple 2 : [Titre situation]
[Même structure]

## 4. Sources

### Données statistiques
- [Nom source 1] : [URL] (consulté le [Date])
- [Nom source 2] : [URL] (consulté le [Date])

### Analyses et rapports
- [Nom source 3] : [URL] (consulté le [Date])
```

---

## 🔍 Sources recommandées par niveau

### Marché mondial

**Institutions internationales**
- FMI : https://www.imf.org/en/Publications/WEO
- OCDE : https://www.oecd.org/housing/
- World Bank : https://www.worldbank.org/

**Données à chercher**
- Taux d'intérêt directeurs (BCE, Fed)
- Inflation globale
- Prix immobilier résidentiel mondial
- Volumes de transactions

### Marché national France

**Sources officielles**
- FNAIM : https://www.fnaim.fr/
- Notaires de France : https://www.notaires.fr/
- INSEE : https://www.insee.fr/
- Banque de France : https://www.banque-france.fr/

**Données à chercher**
- Prix au m² par région
- Nombre de transactions annuelles
- Taux de crédit immobilier
- Délais de vente moyens
- Part primo-accédants vs investisseurs

### Marché local

**Sources**
- DVF (Demandes Valeurs Foncières) : https://app.dvf.etalab.gouv.fr/
- Observatoires locaux de l'habitat
- Sites notaires par département
- MeilleursAgents, SeLoger (données publiques)

**Données à chercher (par ville/région)**
- Prix moyen au m²
- Évolution prix 12 derniers mois
- Types de biens les plus vendus
- Profil acquéreurs dominants

---

## 💬 Prompts Qwen efficaces

### Pour la recherche

```
Je dois créer un contenu de formation pour agents immobiliers sur le marché immobilier [niveau].

Aide-moi à :
1. Identifier les 5 sources les plus fiables pour obtenir des données à jour
2. Lister les 10 chiffres clés à absolument connaître
3. Résumer les 3 tendances principales en 2026

Ton = pédagogique mais terrain (pour des pros, pas des étudiants)
```

### Pour la rédaction

```
Voici mes notes sur [sujet]. Aide-moi à rédiger une section de 200 mots pour une formation agent immobilier.

Contraintes :
- Phrases courtes (max 15 mots)
- Verbes d'action
- Exemples concrets
- Ton coach terrain, pas académique

Notes :
[Colle tes notes brutes]
```

### Pour les exemples

```
Crée un dialogue vendeur/agent de 4-6 répliques qui illustre comment utiliser cette donnée de marché :

Donnée : [Ex: "Prix au m² Paris a baissé de 5% en 2025"]
Situation : [Ex: "Vendeur parisien qui refuse de baisser son prix"]

Format WhatsApp naturel, langage pro mais direct.
```

---

## 📋 Checklist quotidienne

Chaque jour de travail :

1. **Avant de commencer**
   - [ ] `git status` (vérifier qu'on est sur `feat/mini-cours-marche`)
   - [ ] `git pull origin feat/mini-cours-marche` (si travail multi-machine)

2. **Pendant le travail**
   - [ ] Modifier SEULEMENT les fichiers `.md` dans `training/modules/marche/`
   - [ ] Noter les sources au fur et à mesure

3. **En fin de journée**
   - [ ] `git add training/modules/marche/`
   - [ ] `git commit -m "contenu: [ce que tu as fait aujourd'hui]"`
   - [ ] `git push origin feat/mini-cours-marche`

---

## 🎯 Critères de qualité

### Pour chaque fichier .md

**Contenu**
- [ ] 500-800 mots (lecture 5-7 min)
- [ ] Minimum 5 chiffres/statistiques récentes
- [ ] Minimum 2 exemples concrets terrain
- [ ] Toutes sources citées avec URL et date

**Style**
- [ ] Phrases courtes (moyenne <15 mots)
- [ ] Verbes d'action ("Fais", "Utilise", "Montre")
- [ ] Zéro jargon sans explication
- [ ] Ton coach terrain

**Technique**
- [ ] Markdown valide
- [ ] Pas de caractères spéciaux cassés
- [ ] Liens cliquables testés

---

## 🆘 FAQ et dépannage

### "Je ne trouve pas de sources à jour"

→ Cherche des rapports/bulletins trimestriels :
- FNAIM publie tous les trimestres
- Notaires publient des baromètres mensuels
- INSEE publie indices prix logements

### "Le ton est trop académique"

→ Transforme :
- ❌ "Il conviendrait d'effectuer une analyse comparative"
- ✅ "Fais une ACM pour comparer"

### "Je ne sais pas si mon exemple est bon"

→ Vérifie qu'il contient :
1. Une situation réaliste que l'agent rencontre
2. Un dialogue court (4-6 répliques max)
3. L'utilisation concrète d'une donnée du marché

### "J'ai modifié un fichier Python par erreur"

```bash
# Annuler les modifications
git checkout training/modules/marche/

# Si tu as déjà commité
git reset --hard HEAD~1
```

---

## 📦 Livrable final (Jour 15)

À la fin de tes 15 jours, tu dois avoir :

```
training/modules/marche/
├── README.md (déjà créé)
├── 01_marche_mondial.md (500-800 mots, 5+ stats, 2+ exemples)
├── 02_marche_national_france.md (500-800 mots, 5+ stats, 2+ exemples)
├── 03_marche_local_template.md (structure + variables à localiser)
├── CHANGELOG.md (résumé de ton travail)
└── sources/
    ├── sources_web.txt (toutes les URLs utilisées)
    └── extraits_rag.txt (10-15 extraits pour enrichir RAG)
```

**Dernier commit** :
```bash
git add training/modules/marche/
git commit -m "contenu: mini-cours marché complet (15j)

- Marché mondial 2026 (tendances, chiffres FMI/OCDE)
- Marché national France (prix, volumes, FNAIM/Notaires)
- Template marché local (structure localisable)
- 30+ sources citées
- 6+ exemples terrain
- Extraits RAG préparés"

git push origin feat/mini-cours-marche
```

---

## 🤝 Reprendre ensemble dans 15 jours

Quand on reprendra (avec moi ou avec Claude.ai) :

1. **Tu me montres ton contenu**
2. **On review ensemble** (qualité, ton, exhaustivité)
3. **On intègre techniquement** :
   - Prompts pour générer le mini-cours
   - Détection localisation stagiaire
   - Enrichissement RAG
4. **On teste**
5. **On merge sur main**

---

## ✅ Points de contrôle avant de commencer

Vérifie que tu as bien :
- [x] Tag `v1.0-stable` créé (point de retour sûr)
- [x] Branche `feat/mini-cours-marche` active
- [x] Structure fichiers créée
- [ ] README.md lu et compris
- [ ] Ce GUIDE lu entièrement
- [ ] Qwen 3 8B + Qwen 2.5 Coder opérationnels

**Prêt à démarrer ? GO ! 🚀**
