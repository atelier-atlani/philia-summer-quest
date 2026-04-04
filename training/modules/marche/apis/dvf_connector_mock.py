"""
Version Mock du connecteur DVF pour tests et développement

En production, remplacer par le vrai DVFConnector qui appelle les APIs.
"""

from typing import List, Dict
from dataclasses import dataclass
import random
from datetime import datetime, timedelta

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
    type_local: str
    
    @property
    def prix_m2(self) -> float:
        if self.surface_bati > 0:
            return self.valeur_fonciere / self.surface_bati
        return 0


class DVFConnectorMock:
    """
    Version mock du connecteur DVF
    Génère des données réalistes pour Lyon et Aubervilliers
    """
    
    # Données réalistes par ville
    CITY_DATA = {
        'lyon': {
            'prix_m2_base': 5200,
            'variation': 800,
            'code_postal': '69007'
        },
        'aubervilliers': {
            'prix_m2_base': 5000,
            'variation': 600,
            'code_postal': '93300'
        },
        'paris': {
            'prix_m2_base': 10500,
            'variation': 2000,
            'code_postal': '75001'
        }
    }
    
    def get_sales_by_address(
        self,
        adresse: str,
        ville: str,
        radius_m: int = 500,
        since_date: str = None
    ) -> List[DVFSale]:
        """Génère ventes mock réalistes"""
        
        ville_key = ville.lower()
        city_data = self.CITY_DATA.get(ville_key, self.CITY_DATA['lyon'])
        
        # Générer 10-20 ventes
        num_sales = random.randint(10, 20)
        sales = []
        
        for i in range(num_sales):
            # Type aléatoire
            type_local = random.choice(['Appartement', 'Appartement', 'Maison'])
            
            # Surface selon type
            if type_local == 'Appartement':
                surface = random.randint(25, 120)
                pieces = min(int(surface / 20), 5)
            else:
                surface = random.randint(80, 200)
                pieces = random.randint(3, 6)
            
            # Prix avec variation
            prix_m2 = city_data['prix_m2_base'] + random.randint(
                -city_data['variation'],
                city_data['variation']
            )
            valeur = surface * prix_m2
            
            # Date aléatoire derniers 12 mois
            days_ago = random.randint(1, 365)
            date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            sale = DVFSale(
                date=date,
                adresse=f"{random.randint(1, 150)} {random.choice(['rue', 'avenue', 'boulevard'])} {random.choice(['de la Paix', 'Victor Hugo', 'Jean Jaurès'])}",
                code_postal=city_data['code_postal'],
                commune=ville.capitalize(),
                surface_terrain=random.randint(0, 500) if type_local == 'Maison' else 0,
                surface_bati=surface,
                nombre_pieces=pieces,
                valeur_fonciere=valeur,
                type_local=type_local
            )
            
            sales.append(sale)
        
        return sales
    
    def calculate_market_stats(
        self,
        sales: List[DVFSale],
        type_local: str = None
    ) -> Dict:
        """Calcule stats marché"""
        if type_local:
            sales = [s for s in sales if s.type_local == type_local]
        
        if not sales:
            return {'count': 0}
        
        prix_m2 = [s.prix_m2 for s in sales if s.prix_m2 > 0]
        
        return {
            'count': len(prix_m2),
            'prix_m2_moyen': round(sum(prix_m2) / len(prix_m2), 2),
            'prix_m2_median': round(sorted(prix_m2)[len(prix_m2)//2], 2),
            'prix_m2_min': round(min(prix_m2), 2),
            'prix_m2_max': round(max(prix_m2), 2),
            'prix_m2_stdev': round((max(prix_m2) - min(prix_m2)) / 4, 2),
            'valeur_moyenne': round(sum([s.valeur_fonciere for s in sales]) / len(sales), 2),
            'surface_moyenne': round(sum([s.surface_bati for s in sales]) / len(sales), 2),
            'type_local': type_local or 'Tous types'
        }
    
    def generate_market_report(
        self,
        adresse: str,
        ville: str,
        radius_m: int = 500
    ) -> str:
        """Génère rapport marché"""
        sales = self.get_sales_by_address(adresse, ville, radius_m=radius_m)
        
        stats_all = self.calculate_market_stats(sales)
        stats_appt = self.calculate_market_stats(sales, type_local="Appartement")
        stats_maison = self.calculate_market_stats(sales, type_local="Maison")
        
        report = f"""
## 📊 Rapport Marché DVF (Données Mock)

**📍 Secteur** : {adresse}, {ville} (rayon {radius_m}m)
**📅 Période** : 12 derniers mois
**🔢 Transactions** : {stats_all['count']} ventes

---

### Prix au m² (Tous types)

- **Moyenne** : {stats_all['prix_m2_moyen']:.0f} €/m²
- **Médiane** : {stats_all['prix_m2_median']:.0f} €/m²
- **Min - Max** : {stats_all['prix_m2_min']:.0f} € - {stats_all['prix_m2_max']:.0f} €/m²

---

### Par Type de Bien

**🏢 Appartements** ({stats_appt['count']} ventes)
- Prix moyen : {stats_appt.get('prix_m2_moyen', 'N/A'):.0f} €/m²

**🏠 Maisons** ({stats_maison['count']} ventes)
- Prix moyen : {stats_maison.get('prix_m2_moyen', 'N/A'):.0f} €/m²

---

### Exemples de Ventes Récentes

"""
        
        recent_sales = sorted(sales, key=lambda s: s.date, reverse=True)[:5]
        
        for sale in recent_sales:
            report += f"""
**{sale.type_local}** - {sale.adresse}
- Date : {sale.date}
- Surface : {sale.surface_bati:.0f} m² | {sale.nombre_pieces} pièces
- Prix : {sale.valeur_fonciere:,.0f} € ({sale.prix_m2:.0f} €/m²)
"""
        
        report += "\n\n**⚠️ Note** : Données mock pour développement. En production, utiliser `DVFConnector`."
        
        return report


# Test
if __name__ == "__main__":
    print("🧪 Test DVF Mock")
    print("=" * 60)
    
    dvf = DVFConnectorMock()
    
    # Test Lyon
    print("\n### LYON 7 (Gerland)")
    report = dvf.generate_market_report("Place Jean Macé", "Lyon")
    print(report)
    
    # Test Aubervilliers
    print("\n\n### AUBERVILLIERS")
    report = dvf.generate_market_report("Fort d'Aubervilliers", "Aubervilliers")
    print(report)
