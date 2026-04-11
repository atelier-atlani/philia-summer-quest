"""training/dvf_connector.py – Connecteur DVF (Demandes de Valeurs Foncières).

Source : fichiers CSV open data data.gouv.fr
  https://files.data.gouv.fr/geo-dvf/latest/csv/{année}/departements/{dept}.csv.gz
Résolution commune : https://geo.api.gouv.fr/communes
Pas de clé API nécessaire.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

GEO_API_BASE = "https://geo.api.gouv.fr"
DVF_CSV_BASE = "https://files.data.gouv.fr/geo-dvf/latest/csv"

# Cache fichier pour éviter les appels répétés
CACHE_DIR = Path("data/dvf_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DURATION_HOURS = 24 * 7  # 1 semaine

# Codes commune pour lesquels DVF utilise des arrondissements
# (la commune-mère n'existe pas dans DVF, on filtre par nom)
ARRONDISSEMENT_CITIES = {
    "13055": "Marseille",
    "69123": "Lyon",
    "75056": "Paris",
}


def _cache_path(key: str) -> Path:
    h = hashlib.md5(key.encode()).hexdigest()
    return CACHE_DIR / f"{h}.json"


def _read_cache(key: str) -> Optional[dict]:
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        cached_at = datetime.fromisoformat(data.get("_cached_at", "2000-01-01"))
        if datetime.now() - cached_at > timedelta(hours=CACHE_DURATION_HOURS):
            return None
        return data
    except Exception:
        return None


def _write_cache(key: str, data: dict) -> None:
    try:
        data["_cached_at"] = datetime.now().isoformat()
        _cache_path(key).write_text(json.dumps(data, ensure_ascii=False))
    except Exception:
        pass


def get_commune_info(ville: str) -> Tuple[Optional[str], Optional[str]]:
    """Résout le code INSEE et le nom officiel d'une commune via l'API Geo.

    Args:
        ville: Nom de la ville (ex: "Marseille", "Lyon 7", "Aubervilliers")

    Returns:
        (code_insee, nom_officiel) ou (None, None)
    """
    cache_key = f"geo_{ville.lower().strip()}"
    cached = _read_cache(cache_key)
    if cached and cached.get("code"):
        return cached["code"], cached.get("nom")

    try:
        resp = requests.get(
            f"{GEO_API_BASE}/communes",
            params={"nom": ville.strip(), "limit": 5, "fields": "nom,code,codesPostaux,population"},
            timeout=10,
        )
        if resp.status_code != 200:
            return None, None

        communes = resp.json()
        if not communes:
            return None, None

        best = max(communes, key=lambda c: c.get("population", 0))
        code = best["code"]
        nom = best["nom"]

        _write_cache(cache_key, {"code": code, "nom": nom})
        return code, nom

    except Exception as e:
        print(f"[DVF] Erreur geo API: {e}")
        return None, None


def get_commune_code(ville: str) -> Optional[str]:
    """Retourne uniquement le code INSEE (rétrocompatibilité)."""
    code, _ = get_commune_info(ville)
    return code


def _dept_from_code(code_commune: str) -> str:
    """Extrait le code département depuis le code commune."""
    if code_commune.startswith(("2A", "2B")):
        return code_commune[:2]
    if len(code_commune) >= 3 and code_commune[:2] in ("97", "98"):
        return code_commune[:3]
    return code_commune[:2]


def _load_dept_csv(dept: str, year: int = 2024) -> Optional[pd.DataFrame]:
    """Télécharge et met en cache le CSV département de DVF.

    Args:
        dept: Code département (ex: "13", "69", "33")
        year: Année des données (2020-2025)

    Returns:
        DataFrame pandas ou None si échec
    """
    csv_cache_path = CACHE_DIR / f"dept_{dept}_{year}.csv"
    meta_key = f"dept_meta_{dept}_{year}"

    # Vérifier si le CSV local est encore valide
    meta = _read_cache(meta_key)
    if meta and csv_cache_path.exists():
        try:
            return pd.read_csv(csv_cache_path, dtype=str, low_memory=False)
        except Exception:
            pass

    # Télécharger
    url = f"{DVF_CSV_BASE}/{year}/departements/{dept}.csv.gz"
    try:
        print(f"[DVF] Téléchargement {url} …")
        resp = requests.get(url, timeout=60, stream=False)
        if resp.status_code != 200:
            print(f"[DVF] Erreur {resp.status_code} pour {url}")
            return None

        content = gzip.decompress(resp.content)
        csv_cache_path.write_bytes(content)
        _write_cache(meta_key, {"dept": dept, "year": year})

        return pd.read_csv(io.StringIO(content.decode("utf-8")), dtype=str, low_memory=False)

    except Exception as e:
        print(f"[DVF] Erreur téléchargement dept {dept}: {e}")
        return None


def get_mutations(
    code_commune: str,
    nom_commune: str = "",
    year: int = 2024,
) -> List[Dict[str, Any]]:
    """Récupère les mutations (ventes) pour une commune depuis DVF CSV.

    Args:
        code_commune: Code INSEE (ex: "13055")
        nom_commune: Nom officiel (utilisé pour Marseille/Lyon/Paris)
        year: Année des données (2024 par défaut)

    Returns:
        Liste de mutations avec prix, surface, type, adresse, date
    """
    dept = _dept_from_code(code_commune)
    df = _load_dept_csv(dept, year)
    if df is None or df.empty:
        return []

    # Filtre par commune
    if code_commune in ARRONDISSEMENT_CITIES:
        # Ex: Marseille → filtre sur nom_commune contient "Marseille"
        city_name = ARRONDISSEMENT_CITIES[code_commune]
        mask = df["nom_commune"].str.lower().str.startswith(city_name.lower(), na=False)
    else:
        mask = df["code_commune"] == code_commune

    df_city = df[mask].copy()
    if df_city.empty:
        # Fallback : essai par nom si fourni
        if nom_commune:
            prefix = nom_commune[:8].lower()
            mask2 = df["nom_commune"].str.lower().str.startswith(prefix, na=False)
            df_city = df[mask2].copy()
        if df_city.empty:
            return []

    # Convertir en liste de dicts au format attendu par analyze_market
    mutations = []
    for _, row in df_city.iterrows():
        try:
            prix = float(row.get("valeur_fonciere", "") or 0)
            surface = float(row.get("surface_reelle_bati", "") or 0)
            if not prix or not surface:
                continue

            mutations.append({
                "date_mutation": row.get("date_mutation", ""),
                "valeur_fonciere": prix,
                "surface_reelle_bati": surface,
                "type_local": row.get("type_local", ""),
                "adresse_nom_voie": row.get("adresse_nom_voie", ""),
                "nombre_pieces_principales": int(row.get("nombre_pieces_principales", 0) or 0),
            })
        except (ValueError, TypeError):
            continue

    return mutations


def analyze_market(ville: str, year: int = 2024) -> Dict[str, Any]:
    """Analyse complète du marché d'une ville.

    Args:
        ville: Nom de la ville
        year: Année des données DVF (2024 par défaut)

    Returns:
        Dict avec : ville, code_commune, nb_transactions, prix_median_m2,
        prix_moyen_m2, prix_min_m2, prix_max_m2, types (répartition),
        transactions_recentes (5 dernières), disponible (bool), annee
    """
    result: Dict[str, Any] = {
        "ville": ville,
        "disponible": False,
        "message": "",
        "annee": year,
    }

    code, nom = get_commune_info(ville)
    if not code:
        result["message"] = f"Ville '{ville}' non trouvée dans la base INSEE."
        return result

    mutations = get_mutations(code, nom_commune=nom or ville, year=year)
    if not mutations:
        result["message"] = f"Aucune transaction trouvée pour {ville} (données {year})."
        return result

    # Filtrer les ventes d'appartements et maisons avec prix et surface valides
    ventes = []
    for m in mutations:
        prix = m.get("valeur_fonciere")
        surface = m.get("surface_reelle_bati")
        type_local = m.get("type_local", "")

        if not prix or not surface or surface <= 0:
            continue
        import math
        if math.isnan(prix) or math.isnan(surface):
            continue
        if type_local not in ("Appartement", "Maison"):
            continue

        prix_m2 = round(prix / surface)
        # Exclure les aberrations (< 500 ou > 50 000 €/m²)
        if prix_m2 < 500 or prix_m2 > 50_000:
            continue

        ventes.append({
            "date": m.get("date_mutation", ""),
            "type": type_local,
            "surface": surface,
            "prix": round(prix),
            "prix_m2": prix_m2,
            "adresse": m.get("adresse_nom_voie", ""),
            "pieces": m.get("nombre_pieces_principales", 0),
        })

    if not ventes:
        result["message"] = f"Transactions trouvées mais données incomplètes pour {ville}."
        return result

    # Calculs statistiques
    prix_m2_list = sorted(v["prix_m2"] for v in ventes)
    n = len(prix_m2_list)

    result.update({
        "disponible": True,
        "code_commune": code,
        "nb_transactions": n,
        "prix_median_m2": prix_m2_list[n // 2],
        "prix_moyen_m2": round(sum(prix_m2_list) / n),
        "prix_min_m2": prix_m2_list[0],
        "prix_max_m2": prix_m2_list[-1],
        "prix_q1_m2": prix_m2_list[n // 4] if n >= 4 else prix_m2_list[0],
        "prix_q3_m2": prix_m2_list[3 * n // 4] if n >= 4 else prix_m2_list[-1],
        "types": {
            "Appartement": sum(1 for v in ventes if v["type"] == "Appartement"),
            "Maison": sum(1 for v in ventes if v["type"] == "Maison"),
        },
        "transactions_recentes": sorted(ventes, key=lambda v: v["date"], reverse=True)[:5],
        "periode": f"Données {year}",
    })

    return result
