<!-- Généré le 2026-04-04 15:32 par run_ia_tests.py -->

# 🧪 Rapport Tests d'Assimilation Marché — Scoring IA

**Mode** : scoring
**Tests** : 10
**Réussis** : 10/10 (100%)
**Score moyen** : 81%
**Seuil validation** : 60%

---

## Détails par test

### ✅ Test 01 — Le Casse-tête de Gerland (Lyon 7)
- **Difficulté** : 🟡 Moyen
- **Ville** : Lyon
- **Modules** : M7, M8, M9, M55, M56
- **Score** : 92%
- **Résultat** : ✅ Excellent — Maîtrise complète
Arguments : 5/5 (100%)  |  Erreurs détectées : 1  |  Score erreurs : 80%

**Arguments couverts :**
  ✓ Interdiction légale de louer un logement G depuis le 1er janvier 2025
  ✓ La rénovation esthétique ne change pas la classe DPE — seul l'audit énergétique compte
  ✓ Coût rénovation énergétique 45 m² : ~12 000 à 18 000 €, partiellement couvert par MaPrimeRénov'
  ✓ Loyer max légal à Lyon Gerland : 17,50 €/m² × 45 m² = 787,50 €/mois
  ✓ ROI rénovation : bien locatif légal + valorisation DVF +10-15 %

**Erreurs présentes dans la réponse :**
  ⚠ Ignorer l'interdiction de louer un logement G

<details><summary>Extrait réponse IA</summary>

> 1) **Enjeu terrain réel**  
> L'investisseur souhaite louer un T2 de 45 m² à 850 €/mois, mais il fait face à des contraintes réglementaires et de marché qui limitent cette possibilité.

> 2) **Réponse structurée**  
> - **Encadrement des loyers** : Le loyer maximum autorisé est de 787,50 €/mois (17,50 €/m²) .  
> - **Interdiction de louer** : Les logements classés G ne peuvent plus être loués depuis le 1er janvier 2025 .  
> - **Rénovation nécessaire** : Pour louer légalement, des travaux de rénovation énergétique sont indispensables, coûtant entre 12 000 et 18 000 € .  
> - **Valorisation post-travaux** : Après rénovation, le bien pourrait voir sa valeur augmenter de 10 à 15 % .  
> - **ROI à considérer** : Le retour sur investissement doit être évalué en fonction des loyers futurs et de la valorisation du bien.

> 3) **Contextualisation**  
> Dans une situation typique où un investisseur souhaite louer un bien, il est crucial de prendre en compte les réglementations en vigueur et les conditions du mar

</details>

### ✅ Test 07 — La Transformation de Local Commercial (Lyon 3)
- **Difficulté** : 🔴 Difficile
- **Ville** : Lyon
- **Modules** : M48, M37, M45, M64
- **Score** : 92%
- **Résultat** : ✅ Excellent — Maîtrise complète
Arguments : 5/5 (100%)  |  Erreurs détectées : 1  |  Score erreurs : 80%

**Arguments couverts :**
  ✓ Changement d'usage : autorisation mairie obligatoire (Art. L631-7)
  ✓ Compensation Lyon 3 : ~450 €/m² × 55 m² = ~24 750 € de droits à acheter
  ✓ Règlement copropriété : vérification indispensable avant tout projet
  ✓ Airbnb +120 jours/an à Lyon : illégal sans autorisation + compensation
  ✓ Alternative LMNP : rendement 4-5 %, aucune complication réglementaire

**Erreurs présentes dans la réponse :**
  ⚠ Oublier de vérifier le règlement de copropriété

<details><summary>Extrait réponse IA</summary>

> 1) Enjeu terrain réel : L'investisseur souhaite transformer rapidement un local commercial en meublé touristique, mais plusieurs contraintes réglementaires doivent être prises en compte.

> 2) Réponse structurée :
>    - **Changement d'usage** : Vous devez obtenir une autorisation de la mairie pour changer l'usage commercial en habitation.
>    - **Compensation** : Lyon impose un principe de "1 pour 1" pour préserver les surfaces commerciales, ce qui peut compliquer votre projet.
>    - **Interdiction future** : À partir de 2026, la location touristique de meublés pour plus de 120 jours par an sera interdite à Lyon.
>    - **Copropriété** : Vérifiez que le règlement de copropriété autorise ce changement de destination.

> 3) Contextualisation : Dans une situation typique où un investisseur souhaite transformer un local commercial en Airbnb, il est essentiel de naviguer dans les réglementations locales pour éviter des complications.

> 4) Cas pratique :
>    - **Investisseur** : "Comment puis-je transf

</details>

### ✅ Test 10 — Le Client Étranger (Compliance TRACFIN)
- **Difficulté** : 🔴 Difficile
- **Ville** : Lyon
- **Modules** : M24, M51, M73, M76
- **Score** : 90%
- **Résultat** : ✅ Excellent — Maîtrise complète
Arguments : 5/6 (83%)  |  Erreurs détectées : 0  |  Score erreurs : 100%

**Arguments couverts :**
  ✓ 4 signaux TRACFIN cumulés : cash + discrétion + offshore + refus documents
  ✓ Obligation DS sur portail ERMES avant signature de l'acte
  ✓ KYC obligatoire : identité bénéficiaires effectifs + origine des fonds
  ✓ Non-déclaration : 5 % du CA + risque pénal (complicité blanchiment)
  ✓ Tipping off interdit : ne jamais informer le client de la déclaration

**Arguments manquants :**
  ✗ Caïmans sur liste noire UE : vigilance renforcée automatique


<details><summary>Extrait réponse IA</summary>

> 1) **Enjeu terrain réel**  
> Vous êtes confronté à une situation d'achat potentiellement suspecte. Il est crucial de reconnaître les signaux d'alerte pour éviter d'être complice de blanchiment d'argent.

> 2) **Signaux d'alerte TRACFIN**  
>    - Refus de fournir l'origine des fonds.  
>    - Utilisation d'une SCI avec associés offshore (Îles Caïmans).  
>    - Paiement comptant, ce qui augmente le risque.  
>    - Demande de discrétion, qui peut masquer des intentions douteuses.  
>    - Cumul de ces signaux : paiement cash + structure offshore + refus d'origine des fonds + demande de discrétion , .

> 3) **Procédure légale obligatoire**  
>    - Vous devez faire une déclaration de soupçon auprès de TRACFIN via le portail ERMES, avant ou pendant la transaction.  
>    - Ne jamais informer le client de cette déclaration, cela constituerait un délit pénal (tipping off) .

> 4) **Comportement professionnel à adopter**  
>    - Ne pas poursuivre la transaction sans clarifications.  
>    - Documenter toutes les i

</details>

### ✅ Test 04 — La Sortie de Pinel (Investissement)
- **Difficulté** : 🟡 Moyen
- **Ville** : Aubervilliers
- **Modules** : M14, M16, M50, M63, M90
- **Score** : 88%
- **Résultat** : ✅ Excellent — Maîtrise complète
Arguments : 4/5 (80%)  |  Erreurs détectées : 0  |  Score erreurs : 100%

**Arguments couverts :**
  ✓ LMNP : amortissement 6 048 €/an pendant 25 ans → quasi 0 impôt pendant 15-20 ans
  ✓ Rendement LMNP net ~5,7 % vs foncier classique ~2,2 %
  ✓ Loyer meublé : +10-15 % vs loyer nu → 1 230 €/mois au lieu de 1 100 €
  ✓ Plus-value de revente faible (9 000 €) : pas d'intérêt fiscal à vendre maintenant

**Arguments manquants :**
  ✗ Campus Condorcet : 20 000 personnes, vacance locative < 2 % sur T2 meublés


<details><summary>Extrait réponse IA</summary>

> 1) **Enjeu terrain réel**  
> Le propriétaire doit décider entre vendre son T2 à Aubervilliers ou le louer en LMNP après la fin de son dispositif Pinel. Cette décision impacte ses revenus futurs et sa fiscalité.

> 2) **Réponse structurée**  
> - **Scénario 1 : Vente**  
>   - Plus-value souvent faible après 12 ans. L'intérêt fiscal de vendre immédiatement est limité.  
> - **Scénario 2 : Location nue**  
>   - Revenus fonciers classiques : loyer de 1 100 €/mois, imposés au barème de l'IR + 17,2 % de prélèvements sociaux.  
> - **Scénario 3 : LMNP**  
>   - Loyer meublé : 1 230 €/mois (augmentation de 10 à 15 %).  
>   - Amortissement de 6 048 €/an pendant 25 ans, permettant des revenus quasi nets d'impôts.  
>   - Rendement net de 5,7 % contre 2,2 % pour le foncier classique.

> 3) **Contextualisation**  
> Dans une situation typique où un propriétaire hésite après la sortie du dispositif Pinel, il est crucial de peser les avantages de chaque option, notamment en termes de rentabilité et de fiscalité.

> 4) **

</details>

### ✅ Test 05 — Le Dossier de Financement Bloqué (HCSF Lyon)
- **Difficulté** : 🟡 Moyen
- **Ville** : Lyon
- **Modules** : M9, M26, M27, M49
- **Score** : 88%
- **Résultat** : ✅ Excellent — Maîtrise complète
Arguments : 4/5 (80%)  |  Erreurs détectées : 0  |  Score erreurs : 100%

**Arguments couverts :**
  ✓ HCSF : plafond strict 35 % = mensualité max 2 625 €/mois pour ces revenus
  ✓ Budget réel maximal (apport 30 000 €) : ~459 500 € net vendeur
  ✓ Alternatives : apport familial / PTZ / Lyon 8 équivalent ~432 000 €
  ✓ Dérogation HCSF : possible (20 % des dossiers) si profil solide + primo-accédant

**Arguments manquants :**
  ✗ Écart avec 540 000 € : -80 500 € → impossible sans apport complémentaire


<details><summary>Extrait réponse IA</summary>

> 1) **Enjeu terrain réel :** Le couple souhaite acheter un T4 à Lyon, mais leur apport et leur taux d'endettement posent problème pour obtenir un financement.

> 2) **Réponse structurée :**
>    - **Apport insuffisant :** Ils ont un apport de 30 000 € (5,5 %), alors que le standard est de 15 % en 2026. Cela limite leur capacité d'emprunt.
>    - **Taux d'effort élevé :** Leur taux d'effort est de 36 % (mensualité de 2 400 € + charges de 300 €), dépassant le plafond HCSF de 35 %.
>    - **Plafond HCSF :** La règle HCSF impose un taux d'endettement maximum de 35 %, avec des dérogations possibles pour 20 % des dossiers, mais cela nécessite un profil solide.
>    - **Budget finançable :** Avec leur apport, leur budget maximal est d'environ 459 500 € net vendeur, inférieur au prix du bien.

> 3) **Contextualisation :** Dans une situation typique où un couple cherche à acheter un bien, il est crucial de respecter les normes de financement en vigueur, notamment celles du HCSF.

> 4) **Cas pratique :**
>    -

</details>

### ✅ Test 02 — Le Loft d'Aubervilliers (Mutation)
- **Difficulté** : 🔴 Difficile
- **Ville** : Aubervilliers
- **Modules** : M48, M53, M55, M56, M89 +2
- **Score** : 80%
- **Résultat** : ✅ Excellent — Maîtrise complète
Arguments : 4/6 (67%)  |  Erreurs détectées : 0  |  Score erreurs : 100%

**Arguments couverts :**
  ✓ Audit pollution ICPE : 2 000 à 5 000 €, indispensable pour atelier industriel
  ✓ Mezzanine non déclarée : risque amende + régularisation coûteuse
  ✓ Rénovation loft 120 m² clés en main : ~160 000 € (1 300 €/m²)
  ✓ ROI global : acquisition + rénovation 760 000 € pour bien estimé 900 000 € post-travaux

**Arguments manquants :**
  ✗ Permis de louer Plaine Commune : délai 1-2 mois, diagnostic décence obligatoire
  ✗ Ligne 15 GPE : +15-20% valorisation potentielle dès 2027


<details><summary>Extrait réponse IA</summary>

> 1) **Enjeu terrain réel**  
> La famille hésite à acheter un ancien atelier à rénover, mais plusieurs risques réglementaires, techniques et financiers sont à considérer.

> 2) **Réponse structurée**  
> - **Coût de rénovation élevé** : La réhabilitation complète d'un loft de 120 m² est estimée à environ 160 000 €, soit 1 300 €/m² .  
> - **Audit pollution sol** : Un audit de pollution des sols est indispensable, coûtant entre 2 000 et 5 000 € .  
> - **Mezzanine non déclarée** : Cela peut entraîner des amendes et des coûts de régularisation .  
> - **Risque lié au permis de louer** : La zone est soumise à des restrictions qui peuvent limiter la rentabilité .  
> - **Retour sur investissement** : Bien estimé à 900 000 € post-travaux, la marge brute potentielle est de 140 000 € .

> 3) **Contextualisation**  
> Dans une situation typique où la famille envisage l'achat, ces points de blocage doivent être clairement présentés pour prendre une décision éclairée.

> 4) **Cas pratique obligatoire**  
> **Dialogue

</details>

### ✅ Test 03 — La Succession bloquée à Lyon 6
- **Difficulté** : 🟡 Moyen
- **Ville** : Lyon
- **Modules** : M3, M29, M57, M58, M60 +1
- **Score** : 72%
- **Résultat** : 🟡 Bien — Quelques points à améliorer
Arguments : 4/6 (67%)  |  Erreurs détectées : 1  |  Score erreurs : 80%

**Arguments couverts :**
  ✓ DVF rue Bossuet (6 derniers mois) : 8 300 €/m² en moyenne = 788 500 € pour 95 m²
  ✓ Marché Lyon 6 : -6 % cumulé depuis pic 2021-2022 (Notaires du Rhône)
  ✓ Bien en vente 4 mois : décote 'usure portail' estimée -2 % supplémentaire
  ✓ Tunnel prix : 799 000 € (Flash 15j) → 829 000 € (Marché 60j)

**Arguments manquants :**
  ✗ DPE E : malus -3 à -5 % vs DPE C = -24 000 à -40 000 €
  ✗ Coût portage 6 mois supplémentaires : ~6 000 € (charges + TF)

**Erreurs présentes dans la réponse :**
  ⚠ Négliger l'impact DPE E sur le prix

<details><summary>Extrait réponse IA</summary>

> 1) **Enjeu terrain réel :** Les héritiers doivent trouver un accord sur le prix de vente de l'appartement pour éviter de prolonger la vente et de perdre des opportunités.

> 2) **Réponse structurée :**
>    - **Évaluation actuelle :** La valeur moyenne dans la rue Bossuet est de 8 300 €/m², soit environ 788 500 € pour 95 m² .
>    - **Impact du DPE :** Un DPE de classe E entraîne une décote de 3 à 5 %, soit 24 000 à 40 000 € sur le prix .
>    - **Marché en baisse :** Le marché a corrigé de 6 % depuis le pic de 2021-2022 .
>    - **Usure du bien :** Après 4 mois sur le marché, une décote supplémentaire de 2 % est à prévoir .
>    - **Stratégie de prix :** Proposer un prix de 799 000 € pour une vente rapide (flash de 15 jours) ou 829 000 € pour un délai de 60 jours .

> 3) **Contextualisation :** Dans une situation où les héritiers sont en désaccord sur le prix, il est crucial de s'appuyer sur des données de marché pour justifier une baisse de prix.

> 4) **Cas pratique :**
>    - **Héritier 1 :** "Je ne

</details>

### ✅ Test 06 — La Division Parcellaire sous Loi ZAN (Périphérie)
- **Difficulté** : 🔴 Difficile
- **Ville** : Villeurbanne
- **Modules** : M45, M46, M47, M48, M35
- **Score** : 72%
- **Résultat** : 🟡 Bien — Quelques points à améliorer
Arguments : 4/6 (67%)  |  Erreurs détectées : 1  |  Score erreurs : 80%

**Arguments couverts :**
  ✓ CUb obligatoire avant promesse : délai 2 mois, gratuit, condition suspensive
  ✓ DPU Villeurbanne : mairie a 2 mois pour préempter après envoi DIA
  ✓ Valeur terrain 350 m² viabilisé : 245 000 à 315 000 € (700-900 €/m²)
  ✓ Délai procédure complète : 4 à 6 mois

**Arguments manquants :**
  ✗ Loi ZAN n'interdit pas la division en zone U — elle cible les zones naturelles non urbanisées
  ✗ Géomètre-expert : 1 500 à 3 000 € pour le bornage réglementaire

**Erreurs présentes dans la réponse :**
  ⚠ Oublier le droit de préemption de la mairie

<details><summary>Extrait réponse IA</summary>

> 1) Enjeu terrain réel : Le propriétaire souhaite détacher une partie de son jardin pour vendre un terrain à bâtir, mais il s'interroge sur la faisabilité en raison de la loi ZAN.

> 2) Réponse structurée :
> - **Loi ZAN** : Ne s'applique pas en zone U, donc le détachement est possible .
> - **Certificat d'urbanisme opérationnel (CUb)** : Nécessaire avant toute promesse de vente, délai d'instruction de 2 mois .
> - **Procédure de lotissement** : Selon la surface, il faudra une déclaration préalable ou un permis .
> - **Droit de préemption** : La mairie a 2 mois pour préempter après la déclaration d'intention d'aliéner (DIA) .
> - **Estimation de la valeur** : Pour 350 m², cela pourrait rapporter environ 150 000 € .

> 3) Contextualisation : Dans un contexte où un propriétaire envisage de détacher une parcelle, il est essentiel de vérifier les réglementations en vigueur et de suivre les procédures administratives.

> 4) Cas pratique :
> - **Propriétaire** : "Je veux détacher 350 m² de mon jardin. La loi Z

</details>

### ✅ Test 09 — La Fissure RGA (Pathologie Bâtiment)
- **Difficulté** : 🔴 Difficile
- **Ville** : Villeurbanne
- **Modules** : M53, M54, M35, M36
- **Score** : 68%
- **Résultat** : 🟡 Bien — Quelques points à améliorer
Arguments : 3/5 (60%)  |  Erreurs détectées : 1  |  Score erreurs : 80%

**Arguments couverts :**
  ✓ Fissures diagonales > 2 mm aux ouvertures = signal RGA actif, expertise obligatoire
  ✓ Villeurbanne : zone d'aléa RGA moyen — carte Géorisques à consulter
  ✓ Condition suspensive expertise : protège l'acheteur sans bloquer la vente

**Arguments manquants :**
  ✗ Coût réparation RGA : 5 000 à 80 000 € selon gravité
  ✗ Obligation de conseil de l'agent : signalement par écrit indispensable

**Erreurs présentes dans la réponse :**
  ⚠ Signer un compromis sans condition suspensive expertise en cas de fissures actives

<details><summary>Extrait réponse IA</summary>

> 1) Enjeu terrain réel : L'acheteur est inquiet face aux fissures observées, et il est essentiel d'évaluer le risque avant de prendre une décision.

> 2) Réponse structurée :
>    - **Analyse des fissures** : Les fissures diagonales aux angles des ouvertures peuvent indiquer un risque de Retrait-Gonflement des Argiles (RGA) .
>    - **Risque RGA à Villeurbanne** : La zone est classée en aléa RGA moyen, ce qui augmente le risque de dommages structurels .
>    - **Minimisation du vendeur** : Le vendeur minimise la situation sans fournir d'expertise indépendante, ce qui est préoccupant .
>    - **Diagnostic structurel** : Actuellement, un diagnostic structurel n'est pas obligatoire dans le DDT, mais il est conseillé d'en obtenir un .
>    - **Démarche recommandée** : Proposer une condition suspensive pour obtenir un rapport d'expertise confirmant l'absence de désordres RGA actifs .

> 3) Contextualisation : Dans une situation où un acheteur s'interroge sur des fissures, il est crucial de vérifier les ri

</details>

### ✅ Test 08 — Le Vendeur Leboncoin (Objection Mandat)
- **Difficulté** : 🟢 Facile
- **Ville** : Lyon
- **Modules** : M23, M26, M57, M60, M94
- **Score** : 64%
- **Résultat** : 🟡 Bien — Quelques points à améliorer
Arguments : 2/5 (40%)  |  Erreurs détectées : 0  |  Score erreurs : 100%

**Arguments couverts :**
  ✓ 3 semaines sans offre = prix trop haut OU acquéreurs non qualifiés
  ✓ Honoraires agence 4 % = 14 800 € pour sécurité juridique, rapidité et exposition max

**Arguments manquants :**
  ✗ DVF Jean Macé T3 68 m² : 5 200-5 400 €/m² = 353 000 à 367 000 € (vs 370 000 € affiché)
  ✗ Qualification : seuls les acheteurs avec attestation prêt < 30 jours visitent
  ✗ Portage 3 mois Leboncoin = 1 500 € + risque baisse + fatigue vendeur


<details><summary>Extrait réponse IA</summary>

> 1) Enjeu terrain réel :
> Le vendeur souhaite vendre seul pour éviter les frais d'agence, mais cela peut limiter ses chances de succès.

> 2) Réponse structurée :
> - **Accès à un plus grand nombre d'acheteurs** : 60 % des acquéreurs passent par une agence. Pensez-vous pouvoir vous passer de cette clientèle ? 
> - **Sécurité juridique et gain de temps** : Vendre seul implique des risques juridiques et un investissement en temps que vous pourriez éviter avec un professionnel.
> - **Estimation juste du prix** : Votre prix de 370 000 € pourrait être surestimé. Une estimation professionnelle peut vous aider à le fixer correctement.
> - **Qualification des acquéreurs** : Les visiteurs actuels semblent non qualifiés. Un agent peut vous aider à cibler des acheteurs sérieux.

> 3) Contextualisation :
> Dans une situation classique où un vendeur hésite à passer par une agence, il est important de lui montrer les avantages d'un accompagnement professionnel.

> 4) Cas pratique :
> - **Agent** : "Bonjour, je comprend

</details>
