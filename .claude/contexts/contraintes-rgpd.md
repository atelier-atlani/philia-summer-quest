# CONTEXTE — Contraintes RGPD Philia Summer Quest

**Données enfants, consentement parental. Document de contexte — à affiner avec un juriste.**

---

## AVERTISSEMENT


Ce document pose les principes de conception RGPD du produit. Il n'est PAS un avis juridique. Une validation par un professionnel du droit est nécessaire avant le lancement commercial. Ce document guide le développement pour que la conformité soit intégrée dès le départ ("privacy by design").

## LE CONTEXTE PARTICULIER — DES MINEURS

Philia traite des données d'enfants de 11-12 ans. C'est un traitement sensible. En France, un mineur de moins de 15 ans ne peut pas consentir seul au traitement de ses données : le consentement est donné par le titulaire de l'autorité parentale.

Conséquence produit : **le parent est le titulaire du compte et du consentement.** L'enfant utilise le produit, mais c'est le parent qui crée le compte, consent, et reçoit les informations.

## PRINCIPES DE CONCEPTION

**Minimisation des données.** On ne collecte que ce qui est strictement nécessaire au fonctionnement pédagogique : prénom de l'enfant, âge/classe, progression mathématique. Pas de données superflues. Pas de nom de famille de l'enfant si évitable. Pas de données sensibles.

**Consentement parental explicite.** À l'inscription, un flow de consentement clair : le parent comprend quelles données sont traitées, pourquoi, combien de temps. Double opt-in recommandé (confirmation par email).

**Hébergement en Union Européenne.** Les données doivent être stockées sur une infrastructure UE. Google Workspace n'est pas un hébergement applicatif adapté. Hébergeur applicatif UE à choisir (Sprint 4-6 : Railway, Scaleway, OVH ou équivalent).

**Données hors Git.** La base `data/philia.db` contient des données d'enfants : elle est exclue de Git (`.gitignore`). Aucune donnée d'enfant ne doit jamais être committée.

**Droit à l'effacement.** Le parent doit pouvoir demander la suppression du compte et des données. À prévoir dans le dashboard parent.

**Pas de publicité, pas de revente.** Aucune donnée d'enfant n'est utilisée à des fins publicitaires ou commerciales tierces. C'est aussi un argument produit.

## CE QUI EST TRAITÉ AU SPRINT 4

Le module `compliance/rgpd.py` et le flow de consentement parental sont développés au Sprint 4. La conception doit anticiper : tables `parents` (avec `rgpd_consent`, `rgpd_consent_date`) déjà présentes dans le schéma SQLite dès le Sprint 1.

## POINT DE VIGILANCE — AI ACT

Le règlement européen sur l'IA (AI Act) peut classer un système d'IA éducatif touchant des mineurs comme "à haut risque". Ce n'est pas un blocage pour le lancement 2026, mais c'est un coût de conformité à anticiper pour 2027 (documentation technique, supervision humaine, audit de biais). À garder en mémoire, pas à traiter au MVP.

## CE QUI RESTE À FAIRE

- Validation juridique professionnelle avant lancement commercial
- Rédaction des mentions légales, CGU, CGV, politique de confidentialité (Sprint 6)
- Choix de l'hébergeur UE (Sprint 4-6)

---

*Contexte RGPD Philia Summer Quest. À affiner avec un juriste avant lancement.*
