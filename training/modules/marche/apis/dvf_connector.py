"""
Connecteur API DVF (Demandes de Valeurs Foncières)
Source de données : Open Data Gouv - Transactions immobilières réelles
"""

import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

@dataclass
class DVFSale:
    """Représente une vente DVF"""
    date: str
    adresse: str
    code_postal: str
    commune: str
    surface_terrain: float
    surface_bati: float
    nombre_pieces: int
    valeur_fonciere: float
    type_local: str  # Maison, Appartement, etc.
    
    @property
    def prix_m2(self) -> float:
        """Prix au m² du bien bâti"""
        if self.surface_bati > 0:
            return self.valeur_fonciere / self.surface_bati
        return 0


class DVFConnector:
    """
    Connecteur API DVF (Demandes Valeurs Foncières)
    
    Permet de récupérer les transactions immobilières réelles en France
    depuis 2014. Données publiques via data.gouv.fr.
    """
    
    # API Adresse pour géocodage
    ADRESSE_API_URL = "https://api-adresse.data.gouv.fr/search/"
    
    # API DVF Etalab
    DVF_API_URL = "https://app.dvf.etalab.gouv.fr/api/ventes"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-mmo-Training/1.0'
        })
    
    def geocode_address(
        self, 
        adresse: str, 
        ville: str
    ) -> Optional[Tuple[float, float]]:
        """
        Géocode une adresse en coordonnées GPS
        
        Args:
            adresse: Adresse complète (ex: "12 rue de la Paix")
            ville: Nom de la ville
            
        Returns:
            Tuple (longitude, latitude) ou None si non trouvé
        """
        try:
            params = {
                'q': f"{adresse}, {ville}",
                'limit': 1
            }
            
            response = self.session.get(self.ADRESSE_API_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['features']:
                coords = data['features'][0]['geometry']['coordinates']
                return (coords[0], coords[1])  # lon, lat
            
            return None
            
        except Exception as e:
            print(f"Erreur géocodage: {e}")
            return None
    
    def get_sales_by_coordinates(
        self,
        lon: float,
        lat: float,
        radius_m: int = 500,
        since_date: Optional[str] = None
    ) -> List[DVFSale]:
        """
        Récupère ventes DVF autour de coordonnées GPS
        
        Args:
            lon: Longitude
            lat: Latitude
            radius_m: Rayon de recherche en mètres (défaut: 500m)
            since_date: Date minimum format YYYY-MM-DD (défaut: 1 an)
            
        Returns:
            Liste de ventes DVF
        """
        try:
            # Date par défaut : 1 an en arrière
            if since_date is None:
                one_year_ago = datetime.now() - timedelta(days=365)
                since_date = one_year_ago.strftime("%Y-%m-%d")
            
            params = {
                'lat': lat,
                'lon': lon,
                'dist': radius_m,
                'nature_mutation': 'Vente',
                'date_mutation_min': since_date
            }
            
            response = self.session.get(self.DVF_API_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Parser les ventes
            sales = []
            for item in data.get('results', []):
                try:
                    sale = DVFSale(
                        date=item.get('date_mutation', ''),
                        adresse=item.get('adresse_nom_voie', ''),
                        code_postal=item.get('code_postal', ''),
                        commune=item.get('nom_commune', ''),
                        surface_terrain=float(item.get('surface_terrain', 0)),
                        surface_bati=float(item.get('surface_reelle_bati', 0)),
                        nombre_pieces=int(item.get('nombre_pieces_principales', 0)),
                        valeur_fonciere=float(item.get('valeur_fonciere', 0)),
                        type_local=item.get('type_local', 'Inconnu')
                    )
                    sales.append(sale)
                except (ValueError, KeyError) as e:
                    # Ignorer les ventes mal formées
                    continue
            
            return sales
            
        except Exception as e:
            print(f"Erreur récupération DVF: {e}")
            return []
    
    def get_sales_by_address(
        self,
        adresse: str,
        ville: str,
        radius_m: int = 500,
        since_date: Optional[str] = None
    ) -> List[DVFSale]:
        """
        Récupère ventes DVF autour d'une adresse
        
        Args:
            adresse: Adresse de référence
            ville: Ville
            radius_m: Rayon de recherche (défaut: 500m)
            since_date: Date minimum (défaut: 1 an)
            
        Returns:
            Liste de ventes DVF
        """
        # 1. Géocoder l'adresse
        coords = self.geocode_address(adresse, ville)
        
        if coords is None:
            print(f"Adresse non trouvée: {adresse}, {ville}")
            return []
        
        lon, lat = coords
        
        # 2. Récupérer ventes autour des coordonnées
        return self.get_sales_by_coordinates(
            lon=lon,
            lat=lat,
            radius_m=radius_m,
            since_date=since_date
        )
    
    def calculate_market_stats(
        self,
        sales: List[DVFSale],
        type_local: Optional[str] = None
    ) -> Dict:
        """
        Calcule statistiques marché depuis ventes DVF
        
        Args:
            sales: Liste de ventes DVF
            type_local: Filtrer par type (Appartement, Maison, etc.)
            
        Returns:
            Dict avec stats (prix moyen m², min, max, médiane, etc.)
        """
        # Filtrer par type si spécifié
        if type_local:
            sales = [s for s in sales if s.type_local == type_local]
        
        if not sales:
            return {
                'count': 0,
                'message': 'Aucune vente trouvée'
            }
        
        # Calculer prix au m²
        prix_m2 = [s.prix_m2 for s in sales if s.prix_m2 > 0]
        
        if not prix_m2:
            return {
                'count': len(sales),
                'message': 'Aucune donnée de surface disponible'
            }
        
        return {
            'count': len(prix_m2),
            'prix_m2_moyen': round(statistics.mean(prix_m2), 2),
            'prix_m2_median': round(statistics.median(prix_m2), 2),
            'prix_m2_min': round(min(prix_m2), 2),
            'prix_m2_max': round(max(prix_m2), 2),
            'prix_m2_stdev': round(statistics.stdev(prix_m2), 2) if len(prix_m2) > 1 else 0,
            'valeur_moyenne': round(statistics.mean([s.valeur_fonciere for s in sales]), 2),
            'surface_moyenne': round(statistics.mean([s.surface_bati for s in sales if s.surface_bati > 0]), 2),
            'type_local': type_local or 'Tous types'
        }
    
    def generate_market_report(
        self,
        adresse: str,
        ville: str,
        radius_m: int = 500
    ) -> str:
        """
        Génère un rapport marché formaté pour une adresse
        
        Args:
            adresse: Adresse de référence
            ville: Ville
            radius_m: Rayon d'analyse
            
        Returns:
            Rapport marché formaté en markdown
        """
        sales = self.get_sales_by_address(adresse, ville, radius_m=radius_m)
        
        if not sales:
            return f"❌ **Aucune vente trouvée** autour de {adresse}, {ville} (rayon {radius_m}m)"
        
        # Stats globales
        stats_all = self.calculate_market_stats(sales)
        
        # Stats par type
        stats_appt = self.calculate_market_stats(sales, type_local="Appartement")
        stats_maison = self.calculate_market_stats(sales, type_local="Maison")
        
        # Générer rapport
        report = f"""
## 📊 Rapport Marché DVF

**📍 Secteur** : {adresse}, {ville} (rayon {radius_m}m)
**📅 Période** : 12 derniers mois
**🔢 Transactions** : {stats_all['count']} ventes

---

### Prix au m² (Tous types)

- **Moyenne** : {stats_all['prix_m2_moyen']:.0f} €/m²
- **Médiane** : {stats_all['prix_m2_median']:.0f} €/m²
- **Min - Max** : {stats_all['prix_m2_min']:.0f} € - {stats_all['prix_m2_max']:.0f} €/m²
- **Écart-type** : {stats_all['prix_m2_stdev']:.0f} €/m²

---

### Par Type de Bien

**🏢 Appartements** ({stats_appt['count']} ventes)
- Prix moyen : {stats_appt.get('prix_m2_moyen', 'N/A')} €/m²

**🏠 Maisons** ({stats_maison['count']} ventes)
- Prix moyen : {stats_maison.get('prix_m2_moyen', 'N/A')} €/m²

---

### Dernières Ventes

"""
        
        # Ajouter 5 dernières ventes
        recent_sales = sorted(sales, key=lambda s: s.date, reverse=True)[:5]
        
        for sale in recent_sales:
            report += f"""
**{sale.type_local}** - {sale.adresse}, {sale.commune}
- Date : {sale.date}
- Surface : {sale.surface_bati:.0f} m²
- Prix : {sale.valeur_fonciere:,.0f} € ({sale.prix_m2:.0f} €/m²)
"""
        
        return report


# Exemple d'utilisation
if __name__ == "__main__":
    dvf = DVFConnector()
    
    # Test Lyon 7 - Gerland
    print("🧪 Test DVF - Lyon 7 (Gerland)")
    print("=" * 50)
    
    report = dvf.generate_market_report(
        adresse="Place Jean Macé",
        ville="Lyon",
        radius_m=500
    )
    
    print(report)
