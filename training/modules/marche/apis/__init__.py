"""
Module APIs pour données marché immobilier.

Par défaut : version mock pour développement.
Pour production : basculer sur DVFConnector réel.
"""

# Développement (aucune clé API requise)
from .dvf_connector_mock import DVFConnectorMock as DVFConnector

# Production — décommenter quand accès API confirmé :
# from .dvf_connector import DVFConnector

__all__ = ["DVFConnector"]
