"""
jeu/collection.py — Table de correspondance session → objet de collection.

Responsabilité : dire, pour une session donnée, QUEL objet l'enfant collectionne
pendant cette session et quel asset le représente. Uniquement des données et des
accès en lecture — aucune logique de gain, aucun stockage, aucune UI.

Pourquoi un module dédié dans jeu/ plutôt que dans pedagogie/contenu_ile1.py :
  - c'est de la donnée de JEU (habillage des récompenses), pas de la donnée
    PÉDAGOGIQUE. contenu_ile1.py décrit les exercices et les concepts ; y mettre
    des chemins d'assets mélangerait deux couches.
  - la couche jeu possède déjà les récompenses (jeu/recompenses.py). La collection
    est l'habillage visuel du même système : les deux vivent au même endroit.
  - réutilisable pour les futures îles sans dupliquer le motif : une table par île,
    toutes déclarées ici et exposées par le registre _COLLECTION_PAR_ILE.
  - évite que l'UI importe le contenu pédagogique juste pour afficher une icône.

Le nom du coffre n'est PAS stocké ici : il se dérive du concept de la session,
déjà présent dans META_SESSION_N["concept"] (cf. nom_coffre()). Une seule source
de vérité pour le nom d'une session.

Rappel d'architecture (spec collection + tableau de bord) : gagner_cristal() /
cristaux_obtenus() restent la source de vérité du stockage. Cette table ne fait
que RHABILLER ces données.

Public API :
    COLLECTION_ILE_1                        -> dict
    objet_de_session(ile_id, planche_key)   -> dict | None
    nom_coffre(meta_session)                -> str
    libelle_objet(objet, quantite)          -> str
    emoji_objet(objet)                      -> str
"""

from __future__ import annotations

# Clé = planche_key de la session (D23), déjà portée par META_SESSION_N.
# Les assets sont des chemins relatifs à la racine du projet, comme les autres
# assets d'interface (cf. ui/ecran_carte.py, ui/celebrations.py). Ils peuvent ne
# pas encore exister : l'appelant doit prévoir un repli gracieux.
COLLECTION_ILE_1: dict[str, dict[str, str]] = {
    "c1": {"objet": "pierre",      "asset": "assets/ui/objet_pierre.png"},
    "c2": {"objet": "amphore",     "asset": "assets/ui/objet_amphore.png"},
    "c3": {"objet": "cristal_eau", "asset": "assets/ui/objet_cristal_eau.png"},
    "c4": {"objet": "poids",       "asset": "assets/ui/objet_poids.png"},
    "c5": {"objet": "planche",     "asset": "assets/ui/objet_planche.png"},
}

# Une table par île. Les îles 2 et 3 n'ont pas encore de contenu produit — elles
# s'ajouteront ici le moment venu, sans changer les appelants.
_COLLECTION_PAR_ILE: dict[str, dict[str, dict[str, str]]] = {
    "ile_1": COLLECTION_ILE_1,
}


# Accord singulier / pluriel par type d'objet — le français ne s'obtient pas en
# collant un « s » ("cristal d'eau" -> "cristaux d'eau", "poids" invariable).
_LIBELLES: dict[str, tuple[str, str]] = {
    "pierre":      ("pierre",         "pierres"),
    "amphore":     ("amphore",        "amphores"),
    "cristal_eau": ("cristal d'eau",  "cristaux d'eau"),
    "poids":       ("poids",          "poids"),
    "planche":     ("planche",        "planches"),
}

# Repli quand l'asset PNG n'existe pas encore : jamais d'image cassée.
_EMOJIS_SECOURS: dict[str, str] = {
    "pierre":      "🪨",
    "amphore":     "🏺",
    "cristal_eau": "💧",
    "poids":       "⚖️",
    "planche":     "🪵",
}


def objet_de_session(ile_id: str, planche_key: str) -> dict[str, str] | None:
    """
    Retourne {"objet": ..., "asset": ...} pour la session demandée.
    Retourne None si l'île ou la session n'a pas d'objet déclaré — l'appelant
    affiche alors un repli gracieux plutôt que de planter.
    """
    table = _COLLECTION_PAR_ILE.get(ile_id)
    if table is None:
        return None
    return table.get(planche_key)


def libelle_objet(objet: str, quantite: int) -> str:
    """
    Libellé accordé d'une quantité d'objets : « 1 pierre », « 3 pierres »,
    « 2 cristaux d'eau ». Centralisé ici pour que le compteur de session, le
    toast de gain et le futur tableau de bord disent tous la même chose.
    """
    singulier, pluriel = _LIBELLES.get(objet, (objet, f"{objet}s"))
    return f"{quantite} {pluriel if quantite > 1 else singulier}"


def emoji_objet(objet: str) -> str:
    """Emoji de secours, affiché quand l'asset PNG n'est pas encore produit."""
    return _EMOJIS_SECOURS.get(objet, "🎁")


def nom_coffre(meta_session: dict) -> str:
    """
    Nom affiché du coffre d'une session, dérivé de son concept.

    Le concept est stocké préfixé de son identifiant ("C1 — Sens d'une fraction").
    Le coffre porte le nom lisible seul ("Sens d'une fraction") : c'est ce que
    l'enfant reconnaît. On dérive, on ne duplique pas.
    """
    concept = (meta_session.get("concept") or "").strip()
    return concept.split("—", 1)[-1].strip()
