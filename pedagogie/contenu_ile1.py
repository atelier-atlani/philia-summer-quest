"""
pedagogie/contenu_ile1.py — Contenu pédagogique de l'Île 1.

Source : .claude/pedagogie/ile-1-nombres-brises-CONTENU.md (validé en revue).
Ce module expose les métadonnées et les listes d'exercices par session,
dans le format Exercice attendu par SessionEngine.
Aucune logique ici — uniquement les données.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# SESSION 1 — "Le Pont Fracturé"
# Concept C1 : sens d'une fraction (numérateur, dénominateur, le tout et la part)
# Mode : Découverte
# ---------------------------------------------------------------------------

META_SESSION_1: dict = {
    "id": "ile1_s1",
    "titre": "Le Pont Fracturé",
    "concept": "C1 — Sens d'une fraction",
    "cristal": "Cristal du Partage",
    "planche_key": "c1",
    "situation_narrative": (
        "Un grand pont de l'île s'est brisé en morceaux inégaux. "
        "Archimède t'accueille devant les débris : pour reconstruire le pont, "
        "tu dois apprendre à décrire les parts d'un tout. "
        "C'est ainsi que naissent les fractions."
    ),
}

SESSION_1: list[dict] = [
    {
        "id": "ile1_s1_ex1",
        "enonce": (
            "Une tarte est coupée en 6 parts égales. On en prend 2. "
            "Quelle fraction de la tarte a-t-on prise ?"
        ),
        "reponse": "2/6",
        "solution_etapes": [
            "Identifier le tout : la tarte entière est divisée en 6 parts. Le nombre total de parts est 6.",
            "Identifier la part prise : on prend 2 parts.",
            "Écrire la fraction : parts prises sur parts totales, soit 2/6.",
        ],
        "indices": {
            "leger": (
                "Une fraction, c'est une façon de dire combien de parts on a, "
                "sur combien de parts en tout. Combien de parts en tout dans cette tarte ?"
            ),
            "moyen": (
                "Le nombre de parts en tout, c'est le nombre du bas de la fraction. "
                "Ici, 6. Maintenant, combien de parts a-t-on prises ?"
            ),
            "fort": (
                "Tu as 6 parts en tout (le bas) et 2 parts prises (le haut). "
                "Comment écris-tu ces deux nombres l'un au-dessus de l'autre ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant écrit 6/2 (inverse le haut et le bas)",
                "reponse_maieutique": (
                    "Réfléchis : on a pris toute la tarte, ou seulement un morceau ? "
                    "Si on a pris un morceau, le nombre du haut doit être plus petit "
                    "ou plus grand que celui du bas ?"
                ),
            },
            {
                "erreur": "L'enfant répond 2 (oublie le tout)",
                "reponse_maieutique": (
                    "Oui, on a pris 2 parts. Mais 2 parts... sur combien en tout ? "
                    "Une fraction a besoin des deux nombres."
                ),
            },
        ],
    },
    {
        "id": "ile1_s1_ex2",
        "enonce": (
            "Un ruban est partagé en 5 morceaux égaux. On en utilise 3. "
            "Écris la fraction du ruban utilisée."
        ),
        "reponse": "3/5",
        "solution_etapes": [
            "Le tout : le ruban est partagé en 5 morceaux. Total = 5.",
            "La part : on utilise 3 morceaux.",
            "La fraction : 3 sur 5, soit 3/5.",
        ],
        "indices": {
            "leger": "Comme pour la tarte : combien de morceaux en tout dans ce ruban ?",
            "moyen": "5 morceaux en tout, c'est le nombre du bas. Combien en utilise-t-on ?",
            "fort": (
                "Le bas, c'est 5 (les morceaux en tout). Le haut, c'est le nombre "
                "de morceaux utilisés. Combien ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant écrit 5/3",
                "reponse_maieutique": (
                    "Le nombre du bas, c'est toujours le tout — tous les morceaux. "
                    "Lequel est le tout ici, 5 ou 3 ?"
                ),
            },
        ],
    },
    {
        "id": "ile1_s1_ex3",
        "enonce": (
            "Sur ce schéma, une figure est découpée en parts égales et certaines sont coloriées. "
            "Quelle fraction de la figure est coloriée ? (figure : 8 parts égales, 3 coloriées)"
        ),
        "reponse": "3/8",
        "solution_etapes": [
            "Compter le nombre total de parts égales sur le schéma : 8.",
            "Compter les parts coloriées : 3.",
            "Écrire la fraction : parts coloriées sur parts totales, 3/8.",
        ],
        "indices": {
            "leger": "Regarde bien le dessin. En combien de parts égales la figure est-elle découpée ?",
            "moyen": (
                "Le nombre de parts en tout, c'est le bas de la fraction. "
                "Combien y en a-t-il ? Ensuite, compte les coloriées."
            ),
            "fort": "Il y a 8 parts en tout, donc le bas est 8. Maintenant, combien de parts sont coloriées ?",
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant compte seulement les parts coloriées et oublie le total",
                "reponse_maieutique": (
                    "Tu as bien vu les parts coloriées. Mais une fraction compare toujours "
                    "à un tout. Combien de parts y a-t-il en tout sur le dessin ?"
                ),
            },
            {
                "erreur": "L'enfant compte les parts NON coloriées",
                "reponse_maieutique": (
                    "Attention : la question demande les parts COLORIÉES. "
                    "Lesquelles sont coloriées sur le dessin ?"
                ),
            },
        ],
    },
    {
        "id": "ile1_s1_ex4",
        "enonce": (
            "Dessine, ou choisis parmi plusieurs schémas, "
            "une représentation de la fraction 3/4."
        ),
        "reponse": "Une figure découpée en 4 parts égales, dont 3 sont coloriées.",
        "solution_etapes": [
            "Lire le bas de la fraction : 4. Cela veut dire que le tout est découpé en 4 parts égales.",
            "Lire le haut : 3. Cela veut dire que 3 de ces parts sont prises (coloriées).",
            "La bonne représentation : une figure en 4 parts égales avec 3 coloriées.",
        ],
        "indices": {
            "leger": "Le nombre du bas te dit en combien de parts il faut découper. Que dit le bas de 3/4 ?",
            "moyen": (
                "4 en bas : on découpe en 4 parts égales. "
                "3 en haut : on en colorie 3. Quelle figure correspond ?"
            ),
            "fort": (
                "Tu cherches une figure découpée en 4 parts égales "
                "avec exactement 3 parts coloriées. Laquelle est-ce ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant choisit une figure en 4 parts avec 4 coloriées, ou en 3 parts",
                "reponse_maieutique": (
                    "Vérifions ensemble : le bas dit en combien de parts on découpe, "
                    "le haut dit combien on en colorie. Pour 3/4, combien de parts, combien coloriées ?"
                ),
            },
            {
                "erreur": "L'enfant choisit une figure aux parts inégales",
                "reponse_maieutique": (
                    "Regarde bien les parts de ta figure. Sont-elles toutes de la même taille ? "
                    "Pour une fraction, c'est très important."
                ),
            },
        ],
    },
    {
        "id": "ile1_s1_ex5",
        "enonce": (
            "Une fraction a pour numérateur 5 et pour dénominateur 8. "
            "Que représente-t-elle concrètement ? Décris une situation."
        ),
        "reponse": (
            "5/8 — cinq parts prises sur un tout divisé en huit parts égales "
            "(par exemple : 5 morceaux d'une tablette de chocolat coupée en 8)."
        ),
        "solution_etapes": [
            "Le dénominateur (8) indique le nombre total de parts égales du tout.",
            "Le numérateur (5) indique le nombre de parts prises ou considérées.",
            "Décrire une situation concrète : un objet coupé en 8 parts égales dont on prend 5.",
        ],
        "indices": {
            "leger": "Deux mots nouveaux : numérateur et dénominateur. Lequel des deux désigne le tout, déjà ?",
            "moyen": (
                "Le dénominateur (8) est le nombre du bas : le tout en 8 parts. "
                "Le numérateur (5) est le haut : les parts prises. Imagine un objet coupé en 8."
            ),
            "fort": (
                "Imagine une tablette de chocolat coupée en 8 carrés égaux. "
                "La fraction 5/8, c'est quoi par rapport à cette tablette ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant confond numérateur et dénominateur",
                "reponse_maieutique": (
                    "Petit truc : 'dénominateur' et 'dénombrer le tout' commencent pareil. "
                    "Le dénominateur, c'est le tout. Lequel est-ce ici, 5 ou 8 ?"
                ),
            },
        ],
    },
    {
        "id": "ile1_s1_ex6",
        "enonce": (
            "Le pont de l'île a 7 planches. "
            "La fraction 7/7, qu'est-ce que cela représente concrètement ?"
        ),
        "reponse": "Le pont entier — le tout. 7/7 = 1 (l'unité entière).",
        "solution_etapes": [
            "Le dénominateur 7 : le pont est divisé en 7 planches.",
            "Le numérateur 7 : on considère 7 planches.",
            "Si on prend les 7 planches sur 7, on a le pont en entier. 7/7 représente le tout, c'est-à-dire 1.",
        ],
        "indices": {
            "leger": (
                "Le pont a 7 planches en tout. Et la fraction parle de 7 planches. "
                "Combien de planches prend-on, par rapport au total ?"
            ),
            "moyen": (
                "Si tu prends 7 planches sur les 7 que compte le pont... "
                "combien de planches te manque-t-il ?"
            ),
            "fort": (
                "Quand le haut et le bas d'une fraction sont le même nombre, "
                "on prend TOUTES les parts. Que représente alors la fraction par rapport au tout ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond '7 planches' sans voir que c'est le tout",
                "reponse_maieutique": (
                    "Oui, 7 planches. Mais le pont, il a combien de planches en tout ? "
                    "Alors, 7 planches sur 7... il manque quelque chose au pont ?"
                ),
            },
            {
                "erreur": "L'enfant ne fait pas le lien avec 1",
                "reponse_maieutique": (
                    "Si tu as toutes les parts d'un tout, tu as le tout entier. "
                    "En nombre, le tout entier, c'est combien ?"
                ),
            },
        ],
    },
]
