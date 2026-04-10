"""training/marche_quiz.py – Mini-jeu interactif Cascade marché immobilier.

Teste la compréhension des liens Mondial → National → Local.
"""
from __future__ import annotations

from typing import List

CASCADE_QUESTIONS = [
    {
        "event": "🌍 La BCE relève son taux directeur de 0.5%",
        "level": "Mondial → National",
        "question": "Quel est l'impact immédiat sur le marché français ?",
        "choices": [
            "Les prix de l'immobilier augmentent",
            "Les taux de crédit immobilier augmentent, le pouvoir d'achat des acquéreurs baisse",
            "Les loyers baissent dans les grandes villes",
        ],
        "correct": 1,
        "explanation": "Quand la BCE monte ses taux, les banques françaises répercutent sur les crédits immobiliers. Un point de taux en plus, c'est ~10% de capacité d'emprunt en moins pour vos clients.",
    },
    {
        "event": "🇫🇷 Les logements DPE G sont interdits à la location depuis 2025",
        "level": "National → Local",
        "question": "Quel impact sur votre marché local ?",
        "choices": [
            "Les propriétaires de passoires thermiques veulent vendre → plus de mandats disponibles",
            "Les prix augmentent pour tous les biens",
            "Aucun impact, les DPE ne concernent pas la vente",
        ],
        "correct": 0,
        "explanation": "Les propriétaires de DPE G ne peuvent plus louer. Beaucoup préfèrent vendre plutôt que rénover. C'est une source de mandats pour vous — mais ces biens se vendent avec décote.",
    },
    {
        "event": "📉 Les volumes de ventes ont chuté de 25% en France depuis 2022",
        "level": "National → Local",
        "question": "Que devez-vous dire à un vendeur qui veut vendre au prix d'il y a 3 ans ?",
        "choices": [
            "Votre bien vaut le même prix, le marché est stable",
            "Le marché a changé : moins d'acheteurs, budgets réduits. Voici les ventes récentes dans votre rue pour fixer un prix réaliste.",
            "Baissez votre prix de 30% sinon ça ne se vendra pas",
        ],
        "correct": 1,
        "explanation": "Ni optimiste ni alarmiste. Vous utilisez les données DVF (ventes récentes comparables) pour montrer la réalité du marché au vendeur. C'est votre crédibilité terrain.",
    },
    {
        "event": "📍 Un projet de tramway est annoncé dans votre secteur",
        "level": "Local",
        "question": "Comment utilisez-vous cette information face à un acquéreur hésitant ?",
        "choices": [
            "Ce n'est pas pertinent pour une vente immobilière",
            "Le tramway va faire monter les prix, il faut acheter maintenant avant que ça augmente",
            "Ce projet améliore l'accessibilité du quartier. C'est un facteur de valorisation à moyen terme que je vous recommande de prendre en compte.",
        ],
        "correct": 2,
        "explanation": "Une infrastructure de transport valorise un quartier de 5 à 15%. Vous ne promettez pas une hausse certaine, vous informez l'acquéreur d'un facteur objectif de valorisation.",
    },
]


def get_cascade_questions() -> List[dict]:
    """Retourne les questions du jeu cascade."""
    return CASCADE_QUESTIONS
