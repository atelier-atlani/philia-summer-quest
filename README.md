# Mini-cours : Marché immobilier

## 📁 Structure

```
marche/
├── 01_marche_mondial.md          # Tendances globales 2026
├── 02_marche_national_france.md  # Marché France
├── 03_marche_local_template.md   # Template localisable
└── sources/
    ├── sources_web.txt            # URLs des sources utilisées
    └── extraits_rag.txt           # Extraits pour enrichir le RAG
```

## 🎯 Objectif

Créer un mini-cours de 5-7 minutes sur le marché immobilier avec 3 niveaux :
- **Mondial** : Grandes tendances (inflation, taux, démographie)
- **National** : Spécificités France (Paris vs Province, réglementations)
- **Local** : Données selon localisation du stagiaire (à implémenter)

## 📝 Format des fichiers .md

Chaque fichier suit cette structure :

```markdown
# [Titre du niveau]

## 1. Contexte actuel (2026)
- Chiffres clés
- Tendances principales

## 2. Points d'attention pour l'agent
- Ce qu'il faut savoir absolument
- Arguments terrain à utiliser

## 3. Exemples concrets
- Situations réelles
- Dialogues vendeur/agent

## 4. Sources
- [Liste des sources utilisées]
```

## 🔍 Sources recommandées

### Marché mondial
- FMI (Fonds Monétaire International)
- OCDE
- World Bank

### Marché national France
- FNAIM (statistiques trimestrielles)
- Notaires de France (prix au m²)
- INSEE (démographie, revenus)
- Banque de France (crédit immobilier)

### Marché local
- Observatoires locaux de l'habitat
- DVF (Demandes de Valeurs Foncières)
- Données notariales par département

## ⚠️ Règles importantes

1. **Pas de code Python** : Seulement du contenu (texte markdown)
2. **Sources vérifiables** : Toujours citer les sources avec URL et date
3. **Ton terrain** : Langage agent immobilier, pas académique
4. **Chiffres à jour** : Privilégier données 2025-2026
5. **Exemples concrets** : Toujours illustrer avec du terrain

## 🚀 Intégration future

Une fois le contenu créé, l'intégration technique ajoutera :
- Détection automatique de la localisation du stagiaire
- Adaptation du contenu local selon sa ville/région
- Enrichissement du RAG avec les extraits
- Génération dynamique du mini-cours

## ✅ Checklist de validation

Avant de considérer un fichier terminé :
- [ ] Contenu 500-800 mots (lecture 5-7 min)
- [ ] Au moins 5 chiffres/stats récents
- [ ] Au moins 2 exemples concrets terrain
- [ ] Toutes les sources citées avec URL
- [ ] Ton adapté (phrases courtes, verbes d'action)
- [ ] Relu et corrigé (orthographe, cohérence)
