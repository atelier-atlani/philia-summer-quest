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
