# Philia Summer Quest — constantes globales

# Palette Philia
COLOR_BG     = "#F8FAFC"
COLOR_BLUE   = "#4A9FFF"
COLOR_TEAL   = "#3CE8C2"
COLOR_ORANGE = "#FF9F4A"
COLOR_DARK   = "#1E2937"

# Îles
ILE_IDS = ["ile_1", "ile_2", "ile_3", "ile_4", "ile_5", "ile_6", "ile_7"]
ILE_NOMS = {
    "ile_1": "L'Île des Nombres Brisés",
    "ile_2": "La Forêt des Mesures",
    "ile_3": "Le Labyrinthe des Inconnues",
    "ile_4": "Le Royaume des Proportions",
    "ile_5": "La Vallée des Nombres Relatifs",
    "ile_6": "La Cité des Formes",
    "ile_7": "La Tour des Données",
}

# Niveaux d'élévation par île (0 → 3)
NIVEAU_MAX = 3

# Session
SESSION_DUREE_MAX_MIN = 45
HISTORIQUE_CHAT_MAX   = 100

# Mentor
MENTOR_NOM     = "Archimède"
MENTOR_NIVEAUX = {1: "Jeune Guide", 2: "Guide Confirmé", 3: "Grand Sage"}

# Avatars — Sprint 3 T6
# Convention fichiers : <genre>_<prenom>_<role>_reference.png
# Dossier racine : assets/mentor/
AVATARS_REGISTRY = {
    "fille": {
        "livia":   {"role": "pilote",       "fichier": "fille_livia_pilote_reference.png"},
        "nina":    {"role": "exploratrice", "fichier": "fille_nina_exploratrice_reference.png"},
        "sassou":  {"role": "architecte",   "fichier": "fille_sassou_architecte_reference.png"},
        "thalia":  {"role": "aventuriere",  "fichier": "fille_thalia_aventuriere_reference.png"},
    },
    "garcon": {
        "aurele":  {"role": "architecte",   "fichier": "garcon_aurele_architecte_reference.png"},
        "caliste": {"role": "aventurier",   "fichier": "garcon_caliste_aventurier_reference.png"},
        "jonas":   {"role": "pilote",       "fichier": "garcon_jonas_pilote_reference.png"},
        "melian":  {"role": "explorateur",  "fichier": "garcon_melian_explorateur_reference.png"},
    },
}

ARCHIMEDE_FICHIER = "mentor_archimede_reference.png"  # assets/mentor/mentor/

# ── Sprint 3 T7 — Catalogue des cristaux ─────────────────────────────────────
# Îles 1, 2, 3 nommées (MVP). Îles 4, 5, 7 = placeholders.
# Île 6 reportée à v1.2 (décision D16) — absente du catalogue.
CRISTAUX_CATALOGUE = {
    "ile_1": {
        "nom_ile": "L'Île des Nombres Brisés",
        "couleur": "#3A5A7C",  # bleu sourd Syracuse
        "cristaux": {
            "C1": {"nom": "Cristal du Partage",       "loi": "Le sens d'une fraction"},
            "C2": {"nom": "Cristal de la Juste Part",  "loi": "Fraction d'une quantité"},
            "C3": {"nom": "Cristal du Reflet",         "loi": "Fractions équivalentes"},
            "C4": {"nom": "Cristal de la Balance",     "loi": "Comparer des fractions"},
            "C5": {"nom": "Cristal de l'Assemblage",   "loi": "Additionner/soustraire"},
        },
    },
    "ile_2": {
        "nom_ile": "La Forêt des Mesures",
        "couleur": "#7C8B5C",  # vert sauge antique
        "cristaux": {
            "C1": {"nom": "Cristal de l'Étalon",       "loi": "Unités de longueur"},
            "C2": {"nom": "Cristal du Passage",        "loi": "Conversions d'unités"},
            "C3": {"nom": "Cristal du Contour",        "loi": "Périmètres"},
            "C4": {"nom": "Cristal de l'Étendue",      "loi": "Aires (rectangle, carré)"},
            "C5": {"nom": "Cristal du Sablier",        "loi": "Durées et conversions horaires"},
        },
    },
    "ile_3": {
        "nom_ile": "Le Labyrinthe des Inconnues",
        "couleur": "#A05A2C",  # terre cuite Syracuse
        "cristaux": {
            "C1": {"nom": "Cristal du Voile",               "loi": "Le symbole inconnu (x)"},
            "C2": {"nom": "Cristal de la Révélation",       "loi": "Calculer une expression"},
            "C3": {"nom": "Cristal de l'Équilibre",         "loi": "Équations simples"},
            "C4": {"nom": "Cristal de la Boussole inverse", "loi": "Résolution par opération inverse"},
            "C5": {"nom": "Cristal du Témoin",              "loi": "Vérification d'une solution"},
        },
    },
    # Placeholders îles 4, 5, 7 — à nommer lors de la revue pédagogique
    "ile_4": {
        "nom_ile": "Le Royaume des Proportions",
        "couleur": "#888888",
        "cristaux": {
            f"C{i}": {"nom": f"Cristal C{i} (Île 4 — à nommer)", "loi": "à définir"}
            for i in range(1, 6)
        },
    },
    "ile_5": {
        "nom_ile": "La Vallée des Nombres Relatifs",
        "couleur": "#888888",
        "cristaux": {
            f"C{i}": {"nom": f"Cristal C{i} (Île 5 — à nommer)", "loi": "à définir"}
            for i in range(1, 6)
        },
    },
    "ile_7": {
        "nom_ile": "La Tour des Données",
        "couleur": "#888888",
        "cristaux": {
            f"C{i}": {"nom": f"Cristal C{i} (Île 7 — à nommer)", "loi": "à définir"}
            for i in range(1, 6)
        },
    },
}

# Constantes utilitaires
NB_ILES_TOTAL = 7
NB_CRISTAUX_TOTAL = 35  # 5 par île × 7 îles (Île 6 incluse, vide en MVP)
