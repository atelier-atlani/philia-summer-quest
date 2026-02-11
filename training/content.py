"""training/content.py – Session themes and pedagogical content.

20 themes couvrant les fondamentaux vendeur/acquéreur/management.
Le moteur boucle (modulo) pour les 104 sessions du parcours 6 mois.
"""
from __future__ import annotations

from typing import Dict, List

# 6 mois × ~4 jours/semaine × ~4.33 semaines/mois ≈ 104 sessions
TOTAL_SESSIONS = 104

SESSION_THEMES: List[Dict[str, str]] = [
    {
        "titre": "Découverte vendeur",
        "mini_cours": (
            "Explique la démarche de découverte vendeur : objectifs, "
            "structure d'entretien, questions clés à poser."
        ),
        "cours_cles": (
            "Quels sont les points essentiels de la découverte vendeur ? "
            "Donne un cas pratique concret d'entretien."
        ),
        "synthese_action": (
            "Préparer 3 questions de découverte pour ton prochain "
            "rendez-vous vendeur."
        ),
    },
    {
        "titre": "Présentation de l'ACM",
        "mini_cours": (
            "Explique comment préparer et présenter une ACM à un vendeur, "
            "avec la structure et les points clés."
        ),
        "cours_cles": (
            "Comment présenter l'ACM à un vendeur qui hésite sur le prix ? "
            "Donne un cas pratique."
        ),
        "synthese_action": (
            "Préparer une ACM pour ton prochain rendez-vous avec les "
            "3 comparables les plus pertinents."
        ),
    },
    {
        "titre": "Objections sur le prix",
        "mini_cours": (
            "Explique les principales objections vendeur sur le prix "
            "et comment les traiter avec méthode."
        ),
        "cours_cles": (
            "Comment traiter les objections sur le prix quand le vendeur "
            "pense que son bien vaut plus cher ? Cas pratique."
        ),
        "synthese_action": (
            "Préparer 2 réponses terrain aux objections prix "
            "les plus fréquentes."
        ),
    },
    {
        "titre": "Suivi vendeur",
        "mini_cours": (
            "Explique la démarche de suivi vendeur : fréquence, "
            "contenu des comptes-rendus, relances."
        ),
        "cours_cles": (
            "Comment structurer un suivi vendeur efficace ? "
            "Cas pratique avec un vendeur qui tarde à décider."
        ),
        "synthese_action": (
            "Planifier tes 3 prochains appels de suivi vendeur "
            "avec un objectif précis par appel."
        ),
    },
    {
        "titre": "Mandat confiance au prix",
        "mini_cours": (
            "Explique le lien entre confiance et prix dans la prise "
            "de mandat. Comment cadrer le prix dès le départ."
        ),
        "cours_cles": (
            "Comment ancrer le prix sur des comparables du marché "
            "et créer la confiance ? Cas pratique."
        ),
        "synthese_action": (
            "Identifier 2 arguments terrain pour ancrer le prix "
            "lors de ta prochaine prise de mandat."
        ),
    },
    {
        "titre": "Vente du service post-ACM",
        "mini_cours": (
            "Après l'ACM, comment vendre ton accompagnement "
            "et ta méthode au vendeur."
        ),
        "cours_cles": (
            "Un vendeur dit 'je veux comparer les agences'. "
            "Comment vendre le service, pas la marque ? Cas pratique."
        ),
        "synthese_action": (
            "Préparer ton pitch service en 3 points "
            "pour le prochain rendez-vous post-ACM."
        ),
    },
    {
        "titre": "Proposition de service",
        "mini_cours": (
            "Explique comment cadrer, prouver et engager "
            "dans une proposition de service."
        ),
        "cours_cles": (
            "Comment relier le service aux priorités du vendeur ? "
            "Cas pratique avec objection."
        ),
        "synthese_action": (
            "Rédiger ta proposition de service type "
            "en 3 étapes claires."
        ),
    },
    {
        "titre": "Découverte du bien",
        "mini_cours": (
            "Explique la collecte d'informations sur un bien : "
            "caractéristiques, points de vigilance, préparation visite."
        ),
        "cours_cles": (
            "Comment identifier les points de vigilance sur un bien "
            "et préparer une visite efficace ? Cas pratique."
        ),
        "synthese_action": (
            "Créer ta checklist de découverte du bien "
            "pour ton prochain rendez-vous."
        ),
    },
    {
        "titre": "Bilan de promotion",
        "mini_cours": (
            "Explique comment faire un bilan de promotion "
            "pour un mandat en stock."
        ),
        "cours_cles": (
            "Mandat en stock : comment faire le bilan des actions "
            "engagées et préparer la suite ? Cas pratique."
        ),
        "synthese_action": (
            "Faire le bilan de promotion de ton mandat "
            "le plus ancien en stock."
        ),
    },
    {
        "titre": "Renégociation du prix",
        "mini_cours": (
            "Explique quand et comment aborder une renégociation "
            "de prix avec un vendeur."
        ),
        "cours_cles": (
            "Quelles actions concrètes mener avant de renégocier "
            "le prix ? Cas pratique terrain."
        ),
        "synthese_action": (
            "Identifier un mandat nécessitant une renégociation "
            "et préparer tes arguments."
        ),
    },
    {
        "titre": "Relance acquéreurs",
        "mini_cours": (
            "Explique la stratégie de relance des acquéreurs "
            "ayant visité un bien."
        ),
        "cours_cles": (
            "Comment remobiliser l'équipe et relancer les acquéreurs "
            "ayant visité ? Cas pratique."
        ),
        "synthese_action": (
            "Lister les acquéreurs à relancer cette semaine "
            "avec un objectif par appel."
        ),
    },
    {
        "titre": "Enquête qualité vendeur",
        "mini_cours": (
            "Explique les objectifs et la méthode "
            "d'une enquête qualité vendeur."
        ),
        "cours_cles": (
            "Que vérifier dans une enquête qualité vendeur "
            "et comment structurer le retour ? Cas pratique."
        ),
        "synthese_action": (
            "Préparer ton guide d'enquête qualité "
            "pour ton prochain compte-rendu vendeur."
        ),
    },
    {
        "titre": "Prise de mandat exclusif",
        "mini_cours": (
            "Explique les avantages du mandat exclusif "
            "et comment le présenter au vendeur."
        ),
        "cours_cles": (
            "Comment argumenter en faveur du mandat exclusif "
            "face à un vendeur réticent ? Cas pratique."
        ),
        "synthese_action": (
            "Préparer 3 arguments pour le mandat exclusif "
            "adaptés à ton prochain rendez-vous."
        ),
    },
    {
        "titre": "Gestion du stock de mandats",
        "mini_cours": (
            "Explique comment gérer efficacement un stock de mandats : "
            "priorisation, actions, suivi."
        ),
        "cours_cles": (
            "Comment redonner du dynamisme à un mandat en stock ? "
            "Quelles actions concrètes ? Cas pratique."
        ),
        "synthese_action": (
            "Classer tes mandats en stock par priorité "
            "et définir une action par mandat."
        ),
    },
    {
        "titre": "Préparation de visite",
        "mini_cours": (
            "Explique comment préparer une visite efficace : "
            "parcours, arguments, anticipation objections."
        ),
        "cours_cles": (
            "Comment structurer le parcours de visite "
            "et préparer les arguments clés ? Cas pratique."
        ),
        "synthese_action": (
            "Préparer le parcours de visite et 3 arguments "
            "pour ta prochaine visite."
        ),
    },
    {
        "titre": "Compte-rendu de visite",
        "mini_cours": (
            "Explique l'importance et la structure "
            "d'un bon compte-rendu de visite."
        ),
        "cours_cles": (
            "Comment rédiger un compte-rendu de visite utile "
            "pour le vendeur et pour toi ? Cas pratique."
        ),
        "synthese_action": (
            "Rédiger un modèle de compte-rendu de visite "
            "que tu pourras réutiliser."
        ),
    },
    {
        "titre": "Traitement des objections acquéreur",
        "mini_cours": (
            "Explique les objections fréquentes des acquéreurs "
            "et comment les traiter."
        ),
        "cours_cles": (
            "Comment répondre aux objections acquéreur sur le prix, "
            "l'emplacement, les travaux ? Cas pratique."
        ),
        "synthese_action": (
            "Préparer 2 réponses aux objections acquéreur "
            "les plus fréquentes sur tes biens."
        ),
    },
    {
        "titre": "Négociation vendeur-acquéreur",
        "mini_cours": (
            "Explique la posture et les techniques de négociation "
            "entre vendeur et acquéreur."
        ),
        "cours_cles": (
            "Comment accompagner une négociation prix "
            "entre vendeur et acquéreur ? Cas pratique."
        ),
        "synthese_action": (
            "Identifier une négociation en cours "
            "et préparer ta stratégie d'accompagnement."
        ),
    },
    {
        "titre": "Closing de vente",
        "mini_cours": (
            "Explique les étapes et les signaux "
            "pour réussir le closing d'une vente."
        ),
        "cours_cles": (
            "Comment détecter les signaux d'achat "
            "et conclure efficacement ? Cas pratique."
        ),
        "synthese_action": (
            "Identifier les signaux d'achat chez tes acquéreurs "
            "en cours et planifier le closing."
        ),
    },
    {
        "titre": "Fidélisation et recommandation",
        "mini_cours": (
            "Explique comment fidéliser un vendeur après la vente "
            "et générer des recommandations."
        ),
        "cours_cles": (
            "Comment transformer un vendeur satisfait "
            "en source de recommandation ? Cas pratique."
        ),
        "synthese_action": (
            "Contacter un ancien client pour prendre des nouvelles "
            "et demander une recommandation."
        ),
    },
]


def get_session_theme(session_number: int) -> Dict[str, str]:
    """Return theme for a given session (1-indexed). Cycles through themes."""
    idx = (session_number - 1) % len(SESSION_THEMES)
    return SESSION_THEMES[idx]
