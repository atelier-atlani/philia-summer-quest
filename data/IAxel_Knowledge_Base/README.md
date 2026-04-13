# IAxel Knowledge Base

## Structure

| Dossier | Contenu | Priorité RAG |
|---|---|---|
| 01_REFERENTIEL_LEGAL | Lois, codes, réglementations officielles | HAUTE — fait foi en cas de contradiction |
| 02_DATA_MARCHE_FLUX | Données chiffrées marché, taux, indices | HAUTE — mise à jour régulière |
| 03_TECHNIQUE_DU_BATI | Diagnostics, DPE, rénovation, pathologies | MOYENNE |
| 04_STRATEGIE_BUSINESS | Scripts, négociation, marketing | NORMALE |
| 05_MICRO_LOCAL | Données spécifiques par ville/quartier | HAUTE pour la ville du stagiaire |

## Convention de nommage

| Type | Format | Exemple |
|---|---|---|
| Légal | LEGAL_Sujet_Annee.md | LEGAL_MaPrimeRenov_2026.md |
| Data | DATA_Type_Zone_Periode.csv | DATA_PrixM2_Lyon_T1_2026.csv |
| Technique | TECH_Sujet_Detail.pdf | TECH_Isolation_ITI_Couts.pdf |
| Local | LOCAL_Ville_Quartier.md | LOCAL_Aubervilliers_Ligne15.md |

## Règle de priorité

Si une information dans 04_STRATEGIE_BUSINESS contredit un document de 01_REFERENTIEL_LEGAL,
ignorer la source business. Toujours priorité au document le plus récent (Date_Validité).

## Remplissage

Les fichiers sont indexés par le RAG FAISS au démarrage de l'app.
Formats acceptés : .pdf, .md, .txt
Placer les fichiers dans le dossier approprié, relancer l'app pour réindexer.
