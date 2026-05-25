# PLAN D'INTÉGRATION : MODULE MARCHÉ IMMOBILIER

## 📊 VISION GLOBALE

**Objectif** : Intégrer 100 modules marché immobilier + données dynamiques + tableau blanc interactif dans l'application de formation AI-mmo Training.

**Durée estimée** : 8-12h de développement
**Priorités** : Contenu pédagogique > Voix naturelle > Stabilité

---

## 📁 STRUCTURE CIBLE

```
training/modules/marche/
├── README.md (existant)
├── modules/
│   ├── 01_fondamentaux_mondial.md (modules 1-6)
│   ├── 02_analyse_marche_france.md (modules 7-20)
│   ├── 03_juridique_climat.md (modules 21-32)
│   ├── 04_technique_estimation.md (modules 33-52)
│   ├── 05_expertise_locale.md (modules 53-64)
│   ├── 06_marketing_vente.md (modules 65-80)
│   └── 07_operationnel_local.md (modules 81-100)
├── tests/
│   ├── test_01_gerland.yaml
│   ├── test_02_aubervilliers.yaml
│   ├── ... (10 tests)
├── apis/
│   ├── dvf_connector.py (API DVF)
│   ├── dpe_connector.py (API DPE/ADEME)
│   ├── geo_connector.py (API Géoportail)
│   └── insee_connector.py (API INSEE)
├── prompts/
│   ├── oracle_immo_system.txt (prompt principal)
│   └── function_calling_tools.json (définition outils)
└── config/
    ├── sources_rag.txt (URLs sources)
    └── module_mapping.yaml (mapping modules → tags)
```

---

## 🔄 PHASE 1 : CONVERSION & STRUCTURATION CONTENU (3-4h)

### Étape 1.1 : Conversion RTF → Markdown (1h)

**Objectif** : Convertir les 23 fichiers RTF en 7 fichiers markdown structurés

**Méthode** :
```bash
# Extraire tous les RTF
cd /tmp && unzip -q /mnt/user-data/uploads/23_modules_marche_immobilier.zip

# Convertir chaque fichier
for file in *.rtf; do
    pandoc "$file" -t markdown -o "${file%.rtf}.md"
done

# Regrouper par thématique
# Modules 1-6 → 01_fondamentaux_mondial.md
# Modules 7-20 → 02_analyse_marche_france.md
# etc.
```

**Résultat** : 7 fichiers markdown propres, prêts pour RAG

### Étape 1.2 : Création tests d'assimilation (1h)

**Format YAML pour chaque test** :

```yaml
# tests/test_01_gerland.yaml
test_id: 01
titre: "Le Casse-tête de Gerland (Lyon 7)"
contexte: |
  Un investisseur possède un T2 de 45 m² classé G.
  Il veut le louer 850 €/mois car il est "refait à neuf".
blocage: |
  - Encadrement des loyers limite à 17,50 €/m² (787,50 €)
  - Loi Climat interdit location G depuis 2025
modules_concernes:
  - 15  # Loi Climat & Résilience
  - 28  # Encadrement loyers
  - 42  # Rénovation énergétique
solution_attendue: |
  1. Alerter interdiction location G immédiate
  2. Proposer rénovation (ITE/ITI + VMC) → passer en D
  3. Recalculer loyer référence
  4. Suggérer complément de loyer si critères exceptionnels
prompt_test: |
  Un investisseur à Lyon 7 (Gerland) possède un T2 de 45 m² classé G.
  Il veut le louer 850 €/mois. Analyse cette situation et propose
  une stratégie complète en t'appuyant sur les données DVF et
  réglementations 2026.
```

**Résultat** : 10 fichiers YAML de test

### Étape 1.3 : Extraction sources RAG (1h)

**Créer** `config/sources_rag.txt` :

```txt
# SOURCES PUBLIQUES (Open Data - Gratuites)
API DVF : https://app.dvf.etalab.gouv.fr/
API Géoportail Urbanisme : https://www.geoportail-urbanisme.gouv.fr/
Base DPE ADEME : https://data.ademe.fr/
API INSEE : https://api.insee.fr/

# SOURCES PRIVÉES (Professionnelles)
Meilleurs Agents (API Pro) : https://www.meilleursagents.com/api/
SeLoger Data : https://www.seloger.com/
DVF+ : https://www.data.gouv.fr/fr/datasets/dvf/

# SOURCES JURIDIQUES
Légifrance Loi Climat : https://www.legifrance.gouv.fr/
Service-Public.fr : https://www.service-public.fr/

# SOURCES MARCHÉ
FNAIM : https://www.fnaim.fr/
Notaires de France : https://www.notaires.fr/
Banque de France : https://www.banque-france.fr/
```

**Résultat** : Sources documentées pour enrichissement RAG

---

## 🔧 PHASE 2 : INTÉGRATION TECHNIQUE (3-4h)

### Étape 2.1 : RAG - Indexation modules (1h)

**Enrichir** `core/rag.py` :

```python
# Ajouter indexation modules marché
def index_marche_modules():
    """Indexe les 100 modules marché dans FAISS"""
    modules_dir = Path("training/modules/marche/modules")
    
    for module_file in modules_dir.glob("*.md"):
        content = module_file.read_text()
        
        # Découper en chunks sémantiques
        chunks = split_by_module(content)  # Un module = un chunk
        
        # Indexer avec métadonnées
        for chunk in chunks:
            add_to_faiss(
                text=chunk['content'],
                metadata={
                    'source': 'marche_immobilier',
                    'module_id': chunk['module_id'],
                    'tags': chunk['tags'],
                    'file': str(module_file)
                }
            )
```

**Résultat** : 100 modules indexés dans RAG

### Étape 2.2 : Function Calling - APIs externes (2h)

**Créer** `training/modules/marche/apis/dvf_connector.py` :

```python
import requests
from typing import Dict, List, Optional
from datetime import datetime

class DVFConnector:
    """Connecteur API DVF (Demandes Valeurs Foncières)"""
    
    BASE_URL = "https://app.dvf.etalab.gouv.fr/api"
    
    def get_sales_by_address(
        self,
        adresse: str,
        ville: str,
        radius_m: int = 500
    ) -> List[Dict]:
        """Récupère ventes DVF dans un rayon autour d'une adresse"""
        
        # 1. Géocoder l'adresse
        coords = self._geocode(adresse, ville)
        
        # 2. Requête DVF par coordonnées
        params = {
            'lat': coords['lat'],
            'lon': coords['lon'],
            'dist': radius_m
        }
        
        response = requests.get(f"{self.BASE_URL}/ventes", params=params)
        return response.json()
    
    def _geocode(self, adresse: str, ville: str) -> Dict:
        """Géocode une adresse via API Adresse"""
        url = "https://api-adresse.data.gouv.fr/search/"
        params = {'q': f"{adresse} {ville}"}
        
        resp = requests.get(url, params=params).json()
        coords = resp['features'][0]['geometry']['coordinates']
        
        return {'lon': coords[0], 'lat': coords[1]}
    
    def calculate_avg_price_m2(self, sales: List[Dict]) -> float:
        """Calcule prix moyen au m² depuis ventes DVF"""
        prices_m2 = [
            s['valeur_fonciere'] / s['surface_reelle_bati']
            for s in sales
            if s.get('surface_reelle_bati', 0) > 0
        ]
        
        return sum(prices_m2) / len(prices_m2) if prices_m2 else 0
```

**Créer** `training/modules/marche/apis/dpe_connector.py` :

```python
class DPEConnector:
    """Connecteur API DPE ADEME"""
    
    BASE_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe-v2-logements-existants"
    
    def get_dpe_stats_quartier(self, code_postal: str) -> Dict:
        """Stats DPE pour un code postal"""
        params = {
            'q': f'code_postal:{code_postal}',
            'size': 1000
        }
        
        response = requests.get(f"{self.BASE_URL}/lines", params=params)
        dpe_data = response.json()['results']
        
        # Calculer distribution A-G
        distribution = {}
        for dpe in dpe_data:
            classe = dpe.get('classe_consommation_energie', 'N/A')
            distribution[classe] = distribution.get(classe, 0) + 1
        
        return {
            'total': len(dpe_data),
            'distribution': distribution,
            'pct_passoires': (
                distribution.get('F', 0) + distribution.get('G', 0)
            ) / len(dpe_data) * 100
        }
```

**Définir outils Function Calling** dans `prompts/function_calling_tools.json` :

```json
[
  {
    "type": "function",
    "function": {
      "name": "get_local_market_data",
      "description": "Récupère prix DVF et ITI pour une adresse précise",
      "parameters": {
        "type": "object",
        "properties": {
          "adresse": {
            "type": "string",
            "description": "Adresse complète (ex: 12 rue de la Paix)"
          },
          "ville": {
            "type": "string",
            "description": "Ville (ex: Lyon)"
          },
          "radius_m": {
            "type": "integer",
            "description": "Rayon de recherche en mètres (défaut: 500)"
          }
        },
        "required": ["adresse", "ville"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_dpe_neighborhood_stats",
      "description": "Statistiques DPE d'un quartier par code postal",
      "parameters": {
        "type": "object",
        "properties": {
          "code_postal": {
            "type": "string",
            "description": "Code postal (ex: 69007)"
          }
        },
        "required": ["code_postal"]
      }
    }
  }
]
```

**Résultat** : APIs DVF et DPE fonctionnelles

### Étape 2.3 : Intégration dans session training (1h)

**Modifier** `training/steps.py` :

```python
class Step(Enum):
    PROFIL = "profil"
    MINI_COURS = "mini_cours"
    MINI_COURS_MARCHE = "mini_cours_marche"  # NOUVEAU
    QUIZ = "quiz"
    # ... autres steps
```

**Créer** `training/marche_module.py` :

```python
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class MarcheModuleConfig:
    """Configuration module marché pour une session"""
    modules_ids: List[int]  # Ex: [1, 2, 3] pour Session 1
    use_local_data: bool = True  # Utiliser APIs DVF/DPE
    ville_travail: Optional[str] = None  # Depuis profil
    
class MarcheModuleRunner:
    """Gère l'exécution d'un mini-cours marché"""
    
    def __init__(self, config: MarcheModuleConfig):
        self.config = config
        self.dvf = DVFConnector()
        self.dpe = DPEConnector()
    
    def generate_course(self) -> str:
        """Génère le contenu du cours personnalisé"""
        
        # 1. Récupérer contenu modules depuis RAG
        modules_content = self._get_modules_content()
        
        # 2. Enrichir avec données locales si ville_travail
        if self.config.ville_travail and self.config.use_local_data:
            local_data = self._fetch_local_data()
            modules_content = self._enrich_with_local(
                modules_content, 
                local_data
            )
        
        # 3. Générer cours structuré
        return self._format_course(modules_content)
    
    def _fetch_local_data(self) -> Dict:
        """Récupère données locales DVF/DPE"""
        ville = self.config.ville_travail
        
        # Exemple pour Aubervilliers
        if "aubervilliers" in ville.lower():
            cp = "93300"
            adresse_ref = "Place de la Mairie"
        elif "lyon" in ville.lower():
            cp = "69007"
            adresse_ref = "Place Jean Macé"
        else:
            cp = ville[:5]  # Fallback
            adresse_ref = "Centre-ville"
        
        return {
            'dvf_sales': self.dvf.get_sales_by_address(adresse_ref, ville),
            'dpe_stats': self.dpe.get_dpe_stats_quartier(cp),
            'ville': ville,
            'code_postal': cp
        }
```

**Modifier** `app.py` pour ajouter step MINI_COURS_MARCHE :

```python
def ui_training():
    ts = _get_or_create_session()
    
    # ... autres steps
    
    elif ts.current_step == Step.MINI_COURS_MARCHE:
        st.markdown("### 📊 Mini-cours : Marché Immobilier")
        
        # Déterminer modules selon session
        session_num = len(ts.sessions_history)
        modules_ids = get_marche_modules_for_session(session_num)
        
        # Config
        config = MarcheModuleConfig(
            modules_ids=modules_ids,
            ville_travail=ts.profile.ville_travail,
            use_local_data=True
        )
        
        # Générer cours
        runner = MarcheModuleRunner(config)
        course_content = runner.generate_course()
        
        # Afficher
        st.markdown(course_content)
        
        # Bouton continuer
        if st.button("Continuer →"):
            ts.advance_step()
            st.rerun()
```

**Résultat** : Module marché intégré dans le flow de formation

---

## 🎨 PHASE 3 : TABLEAU BLANC INTERACTIF (2-3h)

### Étape 3.1 : Détection balises visuelles (1h)

**Créer** `training/modules/marche/whiteboard.py` :

```python
import re
from typing import Dict, List, Tuple
import streamlit as st

class WhiteboardRenderer:
    """Interprète et affiche balises tableau blanc"""
    
    PATTERNS = {
        'canvas': r'\[CANVAS_DRAW\](.*?)\[/CANVAS_DRAW\]',
        'map': r'\[MAP_VIEW\](.*?)\[/MAP_VIEW\]',
        'table': r'\[TABLE_GEN\](.*?)\[/TABLE_GEN\]',
        'image': r'\[IMAGE_PROMPT\](.*?)\[/IMAGE_PROMPT\]'
    }
    
    def render(self, content: str) -> str:
        """Interprète contenu et affiche composants visuels"""
        
        # Extraire toutes les balises
        components = self._extract_components(content)
        
        # Remplacer par rendus Streamlit
        rendered = content
        for comp_type, comp_content in components:
            rendered = self._render_component(
                rendered, 
                comp_type, 
                comp_content
            )
        
        return rendered
    
    def _extract_components(self, content: str) -> List[Tuple[str, str]]:
        """Extrait toutes les balises du contenu"""
        components = []
        
        for comp_type, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                components.append((comp_type, match.group(1).strip()))
        
        return components
    
    def _render_component(
        self, 
        content: str, 
        comp_type: str, 
        comp_content: str
    ) -> str:
        """Remplace balise par rendu Streamlit"""
        
        if comp_type == 'canvas':
            # Mermaid diagram
            st.code(comp_content, language='mermaid')
            return content.replace(
                f"[CANVAS_DRAW]{comp_content}[/CANVAS_DRAW]",
                ""
            )
        
        elif comp_type == 'table':
            # Tableau markdown
            st.markdown(comp_content)
            return content.replace(
                f"[TABLE_GEN]{comp_content}[/TABLE_GEN]",
                ""
            )
        
        elif comp_type == 'map':
            # Carte (Folium/Streamlit map)
            coords = self._parse_map_coords(comp_content)
            st.map(coords)
            return content.replace(
                f"[MAP_VIEW]{comp_content}[/MAP_VIEW]",
                ""
            )
        
        return content
```

**Résultat** : Parser balises visuelles fonctionnel

### Étape 3.2 : Composants visuels Streamlit (1-2h)

**Créer** `training/modules/marche/components.py` :

```python
import streamlit as st
import pandas as pd
from typing import Dict, List

def render_mermaid_diagram(mermaid_code: str):
    """Affiche diagramme Mermaid"""
    st.components.v1.html(f"""
    <div class="mermaid">
        {mermaid_code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    """, height=400)

def render_price_comparison_table(dvf_data: List[Dict]):
    """Tableau comparatif prix DVF"""
    df = pd.DataFrame(dvf_data)
    
    st.dataframe(
        df[['date_mutation', 'adresse', 'surface_reelle_bati', 
            'valeur_fonciere', 'prix_m2']],
        use_container_width=True
    )
    
    # Stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Prix moyen m²", f"{df['prix_m2'].mean():.0f} €")
    col2.metric("Prix min", f"{df['prix_m2'].min():.0f} €")
    col3.metric("Prix max", f"{df['prix_m2'].max():.0f} €")

def render_dpe_distribution(dpe_stats: Dict):
    """Graphique distribution DPE"""
    df = pd.DataFrame(
        list(dpe_stats['distribution'].items()),
        columns=['Classe', 'Nombre']
    )
    
    st.bar_chart(df.set_index('Classe'))
    st.caption(f"Passoires thermiques (F+G) : {dpe_stats['pct_passoires']:.1f}%")
```

**Résultat** : Composants visuels prêts

---

## 🎤 PHASE 4 : VOIX NATURELLE (2h)

### Étape 4.1 : Architecture modulaire audio (1h)

**Déjà planifié dans session précédente** : 
- Créer `core/audio.py` avec interface abstraite
- Implémenter `BasicTTSProvider`, `AzureTTSProvider`, `ElevenLabsProvider`
- Config `.env` pour switch provider

**Spécificité marché** : Voix sur transitions modules

```python
# Dans training/marche_module.py
def generate_course(self) -> str:
    course_content = self._format_course(modules_content)
    
    # Générer audio introduction
    intro_text = f"Aujourd'hui, nous allons voir {len(self.config.modules_ids)} modules sur le marché immobilier."
    
    audio_provider = get_audio_provider()
    intro_audio = audio_provider.get_audio(
        text=intro_text,
        voice_id="ialix_voice"  # Ou iaxel selon genre
    )
    
    # Afficher avec player
    st.audio(intro_audio, format="audio/mp3")
    
    return course_content
```

**Résultat** : Voix intégrée sur mini-cours marché

---

## 🧪 PHASE 5 : TESTS & VALIDATION (1-2h)

### Étape 5.1 : Tests unitaires APIs (30 min)

```python
# tests/test_marche_apis.py
def test_dvf_connector():
    dvf = DVFConnector()
    sales = dvf.get_sales_by_address("Place Jean Macé", "Lyon")
    assert len(sales) > 0
    assert 'valeur_fonciere' in sales[0]

def test_dpe_connector():
    dpe = DPEConnector()
    stats = dpe.get_dpe_stats_quartier("69007")
    assert stats['total'] > 0
    assert 'distribution' in stats
```

### Étape 5.2 : Tests d'assimilation IA (1h)

**Exécuter les 10 cas critiques** :

```python
# scripts/run_assimilation_tests.py
from training.modules.marche.tests import load_test_cases

def run_all_tests():
    test_cases = load_test_cases()
    
    for test in test_cases:
        print(f"\n🧪 Test {test.test_id}: {test.titre}")
        
        # Générer réponse IA
        response = oracle_immo.analyze(test.prompt_test)
        
        # Valider réponse
        score = validate_response(response, test.solution_attendue)
        
        print(f"Score: {score}/100")
        
        if score < 70:
            print(f"❌ ÉCHEC - Modules à renforcer: {test.modules_concernes}")
```

**Résultat** : Validation expertise IA

---

## 📊 PHASE 6 : INTÉGRATION DANS SCÉNARIO SESSION (1h)

### Scénario recommandé : Progressive intégration

**Session 1-10 : Fondamentaux**
- Modules 1-20 (Marché mondial + France)
- 2 modules par session = 10 sessions

**Session 11-30 : Expertise technique**
- Modules 21-60 (Juridique + Technique)
- 2 modules par session = 20 sessions

**Session 31-50 : Opérationnel local**
- Modules 61-100 (Marketing + Local)
- 2 modules par session = 20 sessions

**Sessions 51-104 : Révisions + Cas pratiques**
- Révisions modules critiques
- Tests d'assimilation
- Cas pratiques terrain

### Mapping session → modules

```python
# training/modules/marche/config/module_mapping.yaml
session_modules:
  1: [1, 2]    # Marché mondial : Puissance + Comparaison
  2: [3, 4]    # Cycles mondiaux + Géopolitique
  3: [5, 6]    # Marché France + Spécificités
  4: [7, 8]    # Loi Climat + DPE
  5: [9, 10]   # Encadrement loyers + HCSF
  # ... jusqu'à session 50
  
  # Sessions révisions
  51: [1, 5, 15]   # Révision marché + Climat
  52: [42, 53, 64] # Révision technique
  # ...
```

---

## ✅ CHECKLIST LIVRABLE MVP MARCHÉ

### MVP-1 : Contenu pédagogique (1 semaine)
- [ ] 23 fichiers RTF convertis en 7 .md structurés
- [ ] 100 modules indexés dans RAG
- [ ] 10 tests d'assimilation en YAML
- [ ] Step MINI_COURS_MARCHE intégré
- [ ] Mapping sessions → modules défini
- [ ] Tests parcours complet Session 1

### MVP-2 : Données dynamiques (1 semaine)
- [ ] API DVF fonctionnelle
- [ ] API DPE fonctionnelle
- [ ] Function Calling configuré
- [ ] Enrichissement cours avec données locales
- [ ] Tests cas pratiques (Gerland, Aubervilliers)

### MVP-3 : Voix + Tableau blanc (1 semaine)
- [ ] Architecture audio modulaire
- [ ] Azure TTS intégré
- [ ] Parser balises visuelles
- [ ] Composants Mermaid/Tableaux/Cartes
- [ ] Tests UX complète

---

## 🎯 PRIORITÉS IMMÉDIATES (AUJOURD'HUI)

**Option A : Conversion contenu (2-3h)**
- Extraire + convertir RTF → MD
- Créer 7 fichiers structurés
- Préparer indexation RAG

**Option B : Architecture technique (2-3h)**
- Créer structure dossiers
- Implémenter DVFConnector
- Tester Function Calling

**Option C : Mix (3-4h)**
- Conversion 3 premiers modules (1-20)
- API DVF basique
- Test intégration Session 1

---

## 📈 ROADMAP 3 SEMAINES

**Semaine 1 : Contenu**
- Conversion complète modules
- Indexation RAG
- Tests assimilation

**Semaine 2 : APIs**
- Connecteurs DVF/DPE
- Function Calling
- Enrichissement local

**Semaine 3 : Polish**
- Voix naturelle
- Tableau blanc
- Tests utilisateur

---

## 🚀 DÉCISION MAINTENANT

**Quelle phase lancer en premier ?**

**A** : Conversion contenu (fondation solide)
**B** : APIs dynamiques (différenciation)
**C** : Mix contenu + API (équilibré)

**Mon recommandation : Option C**
= Convertir modules 1-20 + API DVF basique
= Valeur immédiate + démonstration capacités
