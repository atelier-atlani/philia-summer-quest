"""
pedagogie/contenu_ile1.py — Contenu pédagogique de l'Île 1.

Source : .claude/pedagogie/ile-1-nombres-brises-CONTENU.md (validé en revue).
Ce module expose les métadonnées et les listes d'exercices par session,
dans le format Exercice attendu par SessionEngine.
Aucune logique ici — uniquement les données.

T8.4 (28 juin 2026) : ancrage narratif Syracuse.
  Tous les énoncés et indices de C1 utilisent des objets de chantier
  (liste blanche). Progression narrative : dalle → ruban → bloc de pierre
  → plan de voûte → amphore → planches du pont.
  Valeurs numériques, solution_etapes et erreurs_typiques inchangées.
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
    # ── Exercice 1 ── Dalle de marbre (6 carreaux, 2 posés → 2/6) ────────────
    {
        "id": "ile1_s1_ex1",
        "enonce": (
            "Une grande dalle de marbre est taillée en 6 carreaux égaux. "
            "On en pose 2 sur le pont. "
            "Quelle fraction de la dalle a-t-on posée ?"
        ),
        "reponse": "2/6",
        "solution_etapes": [
            "Identifier le tout : la dalle est divisée en 6 carreaux. Le nombre total de carreaux est 6.",
            "Identifier la part prise : on prend 2 parts.",
            "Écrire la fraction : parts prises sur parts totales, soit 2/6.",
        ],
        "indices": {
            "leger": (
                "Une fraction, c'est une façon de dire combien de carreaux on a posés, "
                "sur combien de carreaux en tout. Combien de carreaux en tout dans cette dalle ?"
            ),
            "moyen": (
                "Le nombre de carreaux en tout, c'est le nombre du bas de la fraction. "
                "Ici, 6. Maintenant, combien de carreaux a-t-on posés ?"
            ),
            "fort": (
                "Tu as 6 carreaux en tout (le bas) et 2 carreaux posés (le haut). "
                "Comment écris-tu ces deux nombres l'un au-dessus de l'autre ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant écrit 6/2 (inverse le haut et le bas)",
                "reponse_maieutique": (
                    "Réfléchis : on a posé toute la dalle, ou seulement quelques carreaux ? "
                    "Si on en a posé seulement quelques-uns, le nombre du haut doit être "
                    "plus petit ou plus grand que celui du bas ?"
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
    # ── Exercice 2 ── Ruban de mesure (5 morceaux, 3 utilisés → 3/5) ─────────
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
            "leger": "Comme pour la dalle de marbre : combien de morceaux en tout dans ce ruban ?",
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
    # ── Exercice 3 ── Bloc de pierre gravé (8 cases, 3 taillées → 3/8) ───────
    {
        "id": "ile1_s1_ex3",
        "enonce": (
            "Sur ce bloc de pierre, un maçon a gravé 8 cases égales. "
            "Il en a taillé 3 pour former les premières pierres d'angle. "
            "Quelle fraction du bloc a-t-il taillée ?"
        ),
        "reponse": "3/8",
        "solution_etapes": [
            "Compter le nombre total de parts égales sur le schéma : 8.",
            "Compter les parts coloriées : 3.",
            "Écrire la fraction : parts coloriées sur parts totales, 3/8.",
        ],
        "indices": {
            "leger": "Regarde bien le bloc. En combien de cases égales est-il divisé ?",
            "moyen": (
                "Le nombre de cases en tout, c'est le bas de la fraction. "
                "Combien y en a-t-il ? Ensuite, compte les cases taillées."
            ),
            "fort": "Il y a 8 cases en tout, donc le bas est 8. Maintenant, combien de cases sont taillées ?",
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant compte seulement les parts coloriées et oublie le total",
                "reponse_maieutique": (
                    "Tu as bien vu les cases taillées. Mais une fraction compare toujours "
                    "à un tout. Combien de cases y a-t-il en tout sur le bloc ?"
                ),
            },
            {
                "erreur": "L'enfant compte les parts NON coloriées",
                "reponse_maieutique": (
                    "Attention : la question demande les cases TAILLÉES. "
                    "Lesquelles sont taillées sur le bloc ?"
                ),
            },
        ],
    },
    # ── Exercice 4 ── Plan de voûte (4 sections, 3 à marquer → 3/4) ──────────
    {
        "id": "ile1_s1_ex4",
        "enonce": (
            "Sur le plan de voûte du pont, l'arche est divisée en 4 sections égales. "
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
    # ── Exercice 5 ── Amphore d'huile (8 mesures, 5 versées → 5/8) ───────────
    {
        "id": "ile1_s1_ex5",
        "enonce": (
            "Une fraction a pour numérateur 5 et pour dénominateur 8. "
            "Que représente-t-elle concrètement ? Décris une situation."
        ),
        "reponse": (
            "5/8 — cinq parts prises sur un tout divisé en huit parts égales "
            "(par exemple : 5 mesures d'huile versées sur 8 dans une amphore de chantier)."
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
                "Le numérateur (5) est le haut : les parts prises. Imagine un objet divisé en 8."
            ),
            "fort": (
                "Imagine une amphore de chantier divisée en 8 mesures égales. "
                "La fraction 5/8, c'est quoi par rapport à cette amphore ?"
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
    # ── Exercice 6 ── Planches du pont (7/7 = le tout) ───────────────────────
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
