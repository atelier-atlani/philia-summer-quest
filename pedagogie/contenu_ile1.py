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

# ---------------------------------------------------------------------------
# SESSION 2 — "Les Réserves de l'Île"
# Concept C2 : Fraction d'une quantité (prendre une part d'un nombre)
# Mode : Découverte puis Pratique
# ---------------------------------------------------------------------------

META_SESSION_2: dict = {
    "id": "ile1_s2",
    "titre": "Les Réserves de l'Île",
    "concept": "C2 — Fraction d'une quantité",
    "cristal": "Cristal de la Juste Part",
    "planche_key": "c2",
    "situation_narrative": (
        "Dans les cavernes de l'île, des réserves anciennes ont été réparties "
        "en parts égales : cordes, pierres, amphores, cristaux. "
        "Pour avancer, l'Élévateur doit apprendre à prendre une fraction "
        "d'une quantité réelle. Archimède l'amène à comprendre que le dénominateur "
        "indique en combien de groupes égaux on partage, et que le numérateur "
        "indique combien de groupes on prend."
    ),
}

SESSION_2: list[dict] = [
    # ── Exercice 1 ── Amphores d'huile (12 amphores, 1/3 → 4) ── V1 corrigé ──
    {
        "id": "ile1_s2_ex1",
        "enonce": (
            "Dans une réserve, il y a 12 amphores d'huile. "
            "Archimède demande d'en prendre 1/3. "
            "Combien d'amphores faut-il prendre ?"
        ),
        "reponse": "4 amphores d'huile",
        "solution_etapes": [
            "Identifier la quantité totale : 12 amphores d'huile.",
            "Lire le dénominateur : 3. Cela veut dire qu'on partage les 12 amphores en 3 groupes égaux.",
            "Calculer la taille d'un groupe : 12 ÷ 3 = 4.",
            "Comme on prend 1 groupe sur 3, on prend 4 amphores.",
        ],
        "indices": {
            "leger": (
                "1/3 veut dire : on partage en 3 parts égales et on prend une part. "
                "Combien de groupes égaux dois-tu former ?"
            ),
            "moyen": (
                "Tu dois partager 12 amphores en 3 groupes égaux. "
                "Combien y aura-t-il d'amphores dans chaque groupe ?"
            ),
            "fort": (
                "Cherche d'abord combien vaut un seul tiers de 12. "
                "Pour cela, quelle opération fais-tu avec 12 et 3 ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant divise par le numérateur : 12 ÷ 1 = 12",
                "reponse_maieutique": (
                    "Regarde la fraction : 1/3. Le nombre qui dit en combien de groupes "
                    "on partage, c'est celui du haut ou celui du bas ?"
                ),
            },
            {
                "erreur": "L'enfant répond 3 amphores parce qu'il voit le dénominateur 3",
                "reponse_maieutique": (
                    "Le 3 ne dit pas combien d'amphores on prend. "
                    "Il dit en combien de groupes on partage. "
                    "Si tu partages 12 amphores en 3 groupes, chaque groupe contient combien d'amphores ?"
                ),
            },
            {
                "erreur": "L'enfant veut prendre 1 amphore d'huile",
                "reponse_maieutique": (
                    "Le 1 dit qu'on prend un groupe. Mais ce groupe peut contenir plusieurs amphores. "
                    "Combien d'amphores contient un groupe si les 12 amphores sont partagées en 3 groupes égaux ?"
                ),
            },
        ],
    },
    # ── Exercice 2 ── Corde (16 mètres, 1/4 → 4 m) ───────────────────────────
    {
        "id": "ile1_s2_ex2",
        "enonce": (
            "Une corde mesure 16 mètres. "
            "On en utilise 1/4 pour réparer une passerelle. "
            "Combien de mètres utilise-t-on ?"
        ),
        "reponse": "4 mètres",
        "solution_etapes": [
            "Identifier le tout : 16 mètres de corde.",
            "Lire le dénominateur : 4. On partage la corde en 4 parts égales.",
            "Calculer une part : 16 ÷ 4 = 4.",
            "Comme on prend 1/4, on prend une seule part : 4 mètres.",
        ],
        "indices": {
            "leger": (
                "1/4, c'est une part quand le tout est partagé en 4 parts égales. "
                "En combien de parts partage-t-on la corde ?"
            ),
            "moyen": (
                "La corde mesure 16 mètres. "
                "Si tu la coupes en 4 parties égales, combien mesure chaque partie ?"
            ),
            "fort": "Le quart de 16, c'est 16 partagé en 4. Quelle opération peux-tu poser ?",
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant multiplie 16 par 4",
                "reponse_maieutique": (
                    "Si tu prends un quart de la corde, tu dois obtenir moins que 16 mètres "
                    "ou plus que 16 mètres ? Ton opération donne-t-elle un résultat plus petit ?"
                ),
            },
            {
                "erreur": "L'enfant répond 4 sans savoir l'expliquer",
                "reponse_maieutique": (
                    "Tu as peut-être trouvé. Maintenant, explique-moi : "
                    "pourquoi le 4 du bas fait-il partager la corde en 4 parties ?"
                ),
            },
            {
                "erreur": "L'enfant confond quart et quatre mètres automatiquement",
                "reponse_maieutique": (
                    "Attention : un quart ne vaut pas toujours 4. "
                    "Un quart de 16 vaut 4, mais un quart de 20 serait différent. "
                    "Qu'est-ce qui change selon le tout ?"
                ),
            },
        ],
    },
    # ── Exercice 3 ── Coquillages (20, 3/4 → 15) ─────────────────────────────
    {
        "id": "ile1_s2_ex3",
        "enonce": (
            "La réserve contient 20 coquillages. "
            "Pour ouvrir la porte de pierre, il faut utiliser 3/4 des coquillages. "
            "Combien de coquillages faut-il utiliser ?"
        ),
        "reponse": "15 coquillages",
        "solution_etapes": [
            "Identifier le tout : 20 coquillages.",
            "Lire le dénominateur : 4. On partage les 20 coquillages en 4 groupes égaux.",
            "Calculer un quart : 20 ÷ 4 = 5.",
            "Lire le numérateur : 3. Il faut prendre 3 groupes.",
            "Calculer 3 groupes : 3 × 5 = 15.",
        ],
        "indices": {
            "leger": "Avant de prendre 3/4, cherche d'abord combien vaut 1/4 de 20.",
            "moyen": "Partage 20 coquillages en 4 groupes égaux. Puis prends 3 de ces groupes.",
            "fort": (
                "Un groupe contient 20 ÷ 4 coquillages. "
                "Quand tu connais la taille d'un groupe, que dois-tu faire pour en prendre 3 ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant fait 20 ÷ 3 au lieu de 20 ÷ 4",
                "reponse_maieutique": (
                    "Dans 3/4, quel nombre dit en combien de groupes on partage le tout ? "
                    "Est-ce le 3 ou le 4 ?"
                ),
            },
            {
                "erreur": "L'enfant trouve 5 et s'arrête",
                "reponse_maieutique": (
                    "Tu as trouvé un quart. Mais la question demande 3/4. "
                    "Combien de quarts dois-tu prendre ?"
                ),
            },
            {
                "erreur": "L'enfant additionne 5 + 3 au lieu de multiplier par 3",
                "reponse_maieutique": (
                    "Si un quart contient 5 coquillages, alors trois quarts, "
                    "c'est trois groupes de 5. Comment comptes-tu trois groupes de 5 ?"
                ),
            },
        ],
    },
    # ── Exercice 4 ── Pierres de lumière (30, 2/5 → 12) ─────────────────────
    {
        "id": "ile1_s2_ex4",
        "enonce": (
            "Un coffre contient 30 pierres de lumière. "
            "Pour réparer le Pont Fracturé, on utilise 2/5 des pierres. "
            "Combien de pierres utilise-t-on ?"
        ),
        "reponse": "12 pierres",
        "solution_etapes": [
            "Identifier le tout : 30 pierres.",
            "Lire le dénominateur : 5. On partage les 30 pierres en 5 groupes égaux.",
            "Calculer un cinquième : 30 ÷ 5 = 6.",
            "Lire le numérateur : 2. On prend 2 groupes.",
            "Calculer 2 groupes de 6 : 2 × 6 = 12.",
        ],
        "indices": {
            "leger": (
                "2/5 veut dire : on partage en 5 groupes égaux, puis on en prend 2. "
                "Quelle est la première étape ?"
            ),
            "moyen": "Commence par trouver 1/5 de 30. Ensuite seulement, tu pourras trouver 2/5.",
            "fort": (
                "30 partagé en 5 groupes donne la taille d'un groupe. "
                "Après, il faudra prendre deux groupes. Quelle opération vient après le partage ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant fait 30 ÷ 2 = 15",
                "reponse_maieutique": (
                    "Le 2 dit combien de groupes on prend. "
                    "Mais pour savoir la taille des groupes, quel nombre faut-il utiliser ?"
                ),
            },
            {
                "erreur": "L'enfant calcule 30 × 2 = 60 puis divise par 5 sans comprendre",
                "reponse_maieutique": (
                    "Ton calcul peut fonctionner, mais Archimède veut savoir si tu comprends. "
                    "Peux-tu d'abord me dire combien vaut 1/5 de 30 pierres ?"
                ),
            },
            {
                "erreur": "L'enfant répond 6",
                "reponse_maieutique": (
                    "6, c'est une seule part sur les 5. "
                    "Mais on te demande 2 parts sur 5. Que dois-tu faire avec ce 6 ?"
                ),
            },
        ],
    },
    # ── Exercice 5 ── Jarre d'eau bleue (24 gouttes, 5/6 → 20) ─────────────
    {
        "id": "ile1_s2_ex5",
        "enonce": (
            "Une jarre contient 24 gouttes d'eau bleue. "
            "Philia en garde 5/6 pour le rituel du cristal. "
            "Combien de gouttes garde-t-elle ?"
        ),
        "reponse": "20 gouttes",
        "solution_etapes": [
            "Identifier le tout : 24 gouttes.",
            "Lire le dénominateur : 6. La jarre est partagée en 6 parts égales.",
            "Calculer une part : 24 ÷ 6 = 4.",
            "Lire le numérateur : 5. Philia garde 5 parts.",
            "Calculer 5 parts de 4 gouttes : 5 × 4 = 20.",
        ],
        "indices": {
            "leger": "Ne cherche pas directement 5/6. Cherche d'abord combien vaut 1/6 de 24.",
            "moyen": (
                "Si 24 gouttes sont partagées en 6 parts égales, "
                "chaque part contient combien de gouttes ?"
            ),
            "fort": (
                "Une part vaut 24 ÷ 6. Philia garde 5 parts. "
                "Quand tu as la valeur d'une part, comment trouves-tu la valeur de 5 parts ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant calcule 24 ÷ 5",
                "reponse_maieutique": (
                    "Dans une fraction, le nombre du bas découpe le tout. "
                    "Ici, quel nombre découpe les 24 gouttes ?"
                ),
            },
            {
                "erreur": "L'enfant donne 4, qui correspond à 1/6",
                "reponse_maieutique": (
                    "Tu as trouvé une part. Mais la fraction dit 5/6. "
                    "Est-ce qu'on garde une seule part, ou cinq parts ?"
                ),
            },
            {
                "erreur": "L'enfant ne comprend pas que 5/6 est presque tout",
                "reponse_maieutique": (
                    "Imagine 6 parts égales de la jarre. "
                    "Si Philia en garde 5, est-ce une petite partie ou presque toute la jarre ? "
                    "Ton résultat doit-il être proche de 24 ou très petit ?"
                ),
            },
        ],
    },
    # ── Exercice 6 ── Stock de pierres (40, 3/8 → 15 utilisées, 25 restantes) ─
    {
        "id": "ile1_s2_ex6",
        "enonce": (
            "Pour consolider la porte de l'île, il faut 3/8 d'un stock de 40 pierres. "
            "Combien de pierres sont utilisées ? Combien reste-t-il de pierres dans le stock ?"
        ),
        "reponse": "15 pierres utilisées ; 25 pierres restantes",
        "solution_etapes": [
            "Identifier le tout : 40 pierres.",
            "Calculer un huitième : 40 ÷ 8 = 5.",
            "Calculer trois huitièmes : 3 × 5 = 15. On utilise 15 pierres.",
            "Calculer ce qui reste : 40 - 15 = 25.",
            "Répondre aux deux questions : 15 utilisées, 25 restantes.",
        ],
        "indices": {
            "leger": (
                "Il y a deux questions. D'abord : combien vaut 3/8 de 40 ? "
                "Ensuite seulement : combien reste-t-il ?"
            ),
            "moyen": (
                "Commence par partager 40 pierres en 8 groupes égaux. "
                "Combien y a-t-il dans un groupe ?"
            ),
            "fort": (
                "Un huitième vaut 5 pierres. Pour 3/8, tu prends 3 groupes de 5. "
                "Puis tu enlèves ce nombre au stock de départ."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant trouve 15 mais oublie le reste",
                "reponse_maieutique": (
                    "Tu as répondu à la première question. Relis l'énoncé : "
                    "Archimède demande aussi ce qu'il reste. "
                    "De quel nombre pars-tu pour trouver le reste ?"
                ),
            },
            {
                "erreur": "L'enfant calcule 40 - 3 ou 40 - 8",
                "reponse_maieutique": (
                    "On ne retire pas le 3 ou le 8 directement. "
                    "Il faut d'abord savoir combien de pierres représente 3/8 de 40. "
                    "Quelle étape manque ?"
                ),
            },
            {
                "erreur": "L'enfant confond utilisé et restant",
                "reponse_maieutique": (
                    "Faisons deux paniers dans ta tête : le panier 'utilisé' et le panier 'reste'. "
                    "Le 3/8 va dans quel panier ?"
                ),
            },
        ],
    },
]

VALIDATION_SESSION_2: dict = {
    "consigne": (
        "En fin de session, Archimède demande : "
        "'Explique à un autre Élévateur comment trouver 3/4 de 20 "
        "sans lui donner directement le résultat. "
        "Quelle est la première chose à faire ? Et pourquoi ?'"
    ),
    "critere_reussite": (
        "L'enfant explique qu'il faut d'abord partager la quantité totale "
        "selon le dénominateur, puis prendre autant de parts que l'indique le numérateur. "
        "Il peut le dire avec ses mots : 'je coupe en 4 groupes, puis j'en prends 3'."
    ),
    # V2 corrigé : AMBIGU → chantier Syracuse
    "si_echec": (
        "Archimède revient à une quantité très concrète manipulable, "
        "par exemple 12 amphores à répartir en 3 lots. "
        "Il fait verbaliser : 'le nombre du bas découpe, le nombre du haut choisit'."
    ),
}

# ---------------------------------------------------------------------------
# SESSION 3 — "Les Miroirs d'Eau"
# Concept C3 : Fractions équivalentes
# Mode : Découverte
# ---------------------------------------------------------------------------

META_SESSION_3: dict = {
    "id": "ile1_s3",
    "titre": "Les Miroirs d'Eau",
    "concept": "C3 — Fractions équivalentes",
    "cristal": "Cristal du Reflet",
    "planche_key": "c3",
    "situation_narrative": (
        "L'Élévateur arrive devant des bassins d'eau parfaitement calmes. "
        "Chaque bassin reflète une même part de lumière, mais les découpes ne se ressemblent pas. "
        "Archimède fait découvrir que deux fractions peuvent avoir des nombres différents "
        "tout en représentant la même part du tout. "
        "C'est le concept le plus abstrait de l'île : "
        "il faut passer par le dessin, le pliage mental, puis la règle multiplicative."
    ),
}

SESSION_3: list[dict] = [
    # ── Exercice 1 ── Miroir d'eau 1/2 → 2/4 ────────────────────────────────
    {
        "id": "ile1_s3_ex1",
        "enonce": (
            "Un miroir d'eau est coloré à moitié : 1/2. "
            "On redécoupe le même miroir en 4 parts égales. "
            "Combien de parts sur 4 seront colorées pour représenter la même moitié ?"
        ),
        "reponse": "2/4",
        "solution_etapes": [
            "Comprendre que 1/2 représente une moitié du tout.",
            "Redécouper le tout en 4 parts égales.",
            "Observer que la moitié de 4 parts correspond à 2 parts.",
            "Écrire la fraction équivalente : 2/4.",
        ],
        "indices": {
            "leger": (
                "Imagine un rectangle coupé en 2 : une moitié est colorée. "
                "Si tu coupes maintenant le même rectangle en 4, combien de petits morceaux font une moitié ?"
            ),
            "moyen": (
                "La moitié de 4 parts, ce n'est pas 1 part. "
                "C'est combien de parts sur les 4 ?"
            ),
            "fort": (
                "Pour garder la même surface colorée, il faut colorier la moitié des 4 parts. "
                "Quelle est la moitié de 4 ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond 1/4",
                "reponse_maieutique": (
                    "Regarde bien : 1/4, c'est une seule part sur 4. "
                    "Est-ce que cela fait encore la moitié du miroir, ou une part plus petite ?"
                ),
            },
            {
                "erreur": "L'enfant pense que 1/2 et 2/4 sont différents parce que les nombres changent",
                "reponse_maieutique": (
                    "Les nombres changent, oui. "
                    "Mais la surface colorée change-t-elle vraiment si on redécoupe les mêmes morceaux plus finement ?"
                ),
            },
            {
                "erreur": "L'enfant répond 4/4",
                "reponse_maieutique": (
                    "4/4, c'est tout le miroir. "
                    "Mais au départ, avait-on colorié tout le miroir ou seulement la moitié ?"
                ),
            },
        ],
    },
    # ── Exercice 2 ── Bassin 2/3 → 4/6 ─────────────────────────────────────
    {
        "id": "ile1_s3_ex2",
        "enonce": (
            "Un bassin est rempli aux 2/3. "
            "On redécoupe chaque tiers en 2 petites parts égales. "
            "Quelle fraction équivalente obtient-on ?"
        ),
        "reponse": "4/6",
        "solution_etapes": [
            "Le bassin est d'abord découpé en 3 parts, dont 2 sont remplies.",
            "Chaque tiers est redécoupé en 2 parts : le nombre total de parts devient 3 × 2 = 6.",
            "Les 2 tiers remplis sont eux aussi redécoupés en 2 : le nombre de parts remplies devient 2 × 2 = 4.",
            "La fraction équivalente est donc 4/6.",
        ],
        "indices": {
            "leger": (
                "Chaque part est coupée en 2. "
                "Le nombre de parts en tout va-t-il rester 3 ou devenir plus grand ?"
            ),
            "moyen": (
                "Les 3 parts du bas sont chacune coupées en 2. "
                "Combien de petites parts y aura-t-il en tout ?"
            ),
            "fort": (
                "Les 2 parts remplies sont aussi coupées en 2. "
                "Le haut et le bas sont donc tous les deux multipliés par le même nombre. Lequel ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond 2/6",
                "reponse_maieutique": (
                    "Tu as bien changé le nombre de parts en tout. "
                    "Mais les parts remplies ont-elles été redécoupées elles aussi ? "
                    "Que devient chaque part remplie quand on la coupe en deux ?"
                ),
            },
            {
                "erreur": "L'enfant répond 4/3",
                "reponse_maieutique": (
                    "Le nombre du bas dit combien il y a de parts en tout. "
                    "Après la redécoupe, y a-t-il 3 parts en tout ou 6 ?"
                ),
            },
            {
                "erreur": "L'enfant ajoute 2 seulement au dénominateur",
                "reponse_maieutique": (
                    "Quand on redécoupe, on ne colle pas 2 parts en plus au bassin. "
                    "On coupe chaque part en 2. Est-ce une addition ou une multiplication ?"
                ),
            },
        ],
    },
    # ── Exercice 3 ── Parmi 2/4, 3/4, 4/8, lesquelles valent 1/2 ? ──────────
    {
        "id": "ile1_s3_ex3",
        "enonce": (
            "Parmi ces fractions, lesquelles représentent la même quantité que 1/2 : "
            "2/4, 3/4, 4/8 ?"
        ),
        "reponse": "2/4 et 4/8",
        "solution_etapes": [
            "Comprendre que 1/2 signifie la moitié du tout.",
            "Tester 2/4 : 2 est la moitié de 4, donc 2/4 représente la moitié.",
            "Tester 3/4 : 3 n'est pas la moitié de 4, donc 3/4 ne représente pas la moitié.",
            "Tester 4/8 : 4 est la moitié de 8, donc 4/8 représente la moitié.",
            "Répondre : 2/4 et 4/8.",
        ],
        "indices": {
            "leger": (
                "Cherche les fractions où le nombre du haut représente "
                "exactement la moitié du nombre du bas."
            ),
            "moyen": "Dans 2/4, 2 est-il la moitié de 4 ? Dans 3/4, 3 est-il la moitié de 4 ?",
            "fort": (
                "Teste chaque fraction avec cette question : "
                "'si le bas est tout le miroir, le haut est-il exactement la moitié ?'"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant choisit seulement 2/4 et oublie 4/8",
                "reponse_maieutique": (
                    "Tu as trouvé une moitié. Mais regarde 4/8 : "
                    "si tu as 8 parts en tout, combien de parts font la moitié ?"
                ),
            },
            {
                "erreur": "L'enfant choisit 3/4 parce que 3 et 4 sont proches",
                "reponse_maieutique": (
                    "Être proche ne veut pas dire être la moitié. "
                    "La moitié de 4, c'est combien ?"
                ),
            },
            {
                "erreur": "L'enfant pense qu'une seule fraction peut être égale à 1/2",
                "reponse_maieutique": (
                    "Si tu coupes la même moitié en morceaux plus petits, "
                    "est-ce que la quantité change ? "
                    "Peut-on alors écrire la même quantité de plusieurs façons ?"
                ),
            },
        ],
    },
    # ── Exercice 4 ── Compléter 3/5 = 12/? ──────────────────────────────────
    {
        "id": "ile1_s3_ex4",
        "enonce": "Complète la fraction équivalente : 3/5 = 12/?",
        "reponse": "20",
        "solution_etapes": [
            "Comparer les numérateurs : 3 devient 12.",
            "Chercher par combien on multiplie 3 pour obtenir 12 : 3 × 4 = 12.",
            "Pour garder une fraction équivalente, multiplier aussi le dénominateur par le même nombre.",
            "Calculer 5 × 4 = 20.",
            "La fraction équivalente est 12/20.",
        ],
        "indices": {
            "leger": (
                "Dans une fraction équivalente, le haut et le bas changent de la même façon. "
                "Que devient le 3 pour arriver à 12 ?"
            ),
            "moyen": "3 est multiplié par 4 pour devenir 12. Le 5 doit subir la même transformation.",
            "fort": (
                "Tu as trouvé que le haut est multiplié par 4. "
                "Applique exactement la même multiplication au nombre du bas."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant ajoute 9 au dénominateur : 5 + 9 = 14",
                "reponse_maieutique": (
                    "Tu as vu que 3 devient 12 en ajoutant 9. "
                    "Mais pour les fractions équivalentes, est-ce qu'on ajoute le même nombre, "
                    "ou est-ce qu'on multiplie par le même nombre ?"
                ),
            },
            {
                "erreur": "L'enfant écrit 12/5",
                "reponse_maieutique": (
                    "Tu as changé le haut mais pas le bas. "
                    "Si on redécoupe les parts du haut, que doit-il arriver au nombre total de parts ?"
                ),
            },
            {
                "erreur": "L'enfant multiplie le dénominateur par 12",
                "reponse_maieutique": (
                    "Le nombre qui transforme 3 en 12 n'est pas 12. "
                    "Quelle multiplication fait passer de 3 à 12 ?"
                ),
            },
        ],
    },
    # ── Exercice 5 ── Simplifier 6/8 → 3/4 ─────────────────────────────────
    {
        "id": "ile1_s3_ex5",
        "enonce": (
            "Simplifie la fraction 6/8 en trouvant une fraction équivalente "
            "avec des nombres plus petits."
        ),
        "reponse": "3/4",
        "solution_etapes": [
            "Chercher un nombre qui divise à la fois 6 et 8.",
            "Constater que 6 et 8 sont tous les deux divisibles par 2.",
            "Diviser le numérateur par 2 : 6 ÷ 2 = 3.",
            "Diviser le dénominateur par 2 : 8 ÷ 2 = 4.",
            "Obtenir la fraction équivalente simplifiée : 3/4.",
        ],
        "indices": {
            "leger": (
                "Simplifier, c'est garder la même part, mais avec des nombres plus petits. "
                "Par quel même nombre peux-tu diviser 6 et 8 ?"
            ),
            "moyen": "6 et 8 sont tous les deux pairs. Quel nombre peut diviser les deux ?",
            "fort": "Divise le haut et le bas par 2. Que devient 6 ? Que devient 8 ?",
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant simplifie seulement le haut : 3/8",
                "reponse_maieutique": (
                    "Si tu changes seulement le haut, est-ce encore la même quantité ? "
                    "Que dois-tu faire au bas pour garder le même reflet ?"
                ),
            },
            {
                "erreur": "L'enfant soustrait 2 aux deux nombres : 4/6",
                "reponse_maieutique": (
                    "Soustraire le même nombre ne garde pas forcément la même fraction. "
                    "Pour simplifier, quelle opération utilise-t-on sur le haut et le bas ?"
                ),
            },
            {
                "erreur": "L'enfant répond 6/8 est déjà simple",
                "reponse_maieutique": (
                    "Regarde 6 et 8 : ont-ils un diviseur commun ? "
                    "Peux-tu les partager tous les deux par 2 ?"
                ),
            },
        ],
    },
    # ── Exercice 6 ── Miroir A (2/4) vs Miroir B (3/6) : même part ? ─────────
    {
        "id": "ile1_s3_ex6",
        "enonce": (
            "Deux miroirs montrent-ils la même part d'eau colorée ? "
            "Miroir A : 2/4. Miroir B : 3/6. Explique ton choix."
        ),
        "reponse": "Oui, ils montrent la même part : 2/4 = 3/6 = 1/2.",
        "solution_etapes": [
            "Analyser 2/4 : 2 est la moitié de 4, donc 2/4 représente la moitié.",
            "Analyser 3/6 : 3 est la moitié de 6, donc 3/6 représente aussi la moitié.",
            "Conclure que les deux fractions sont équivalentes.",
            "Expliquer avec des mots : les découpes sont différentes, mais la surface colorée est la même.",
        ],
        "indices": {
            "leger": (
                "Ne regarde pas seulement les nombres. "
                "Demande-toi quelle part du miroir est colorée dans chaque cas."
            ),
            "moyen": "Dans 2/4, le haut est-il la moitié du bas ? Et dans 3/6 ?",
            "fort": (
                "Si les deux fractions représentent chacune une moitié du tout, "
                "alors que peux-tu dire sur elles ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond non parce que les nombres sont différents",
                "reponse_maieutique": (
                    "Les nombres sont différents, oui. "
                    "Mais est-ce que deux découpes différentes peuvent montrer la même surface colorée ?"
                ),
            },
            {
                "erreur": "L'enfant compare seulement les numérateurs 2 et 3",
                "reponse_maieutique": (
                    "Le haut seul ne suffit pas. "
                    "3 parts sur 6, est-ce forcément plus que 2 parts sur 4 ? "
                    "Quelle part du tout cela représente-t-il ?"
                ),
            },
            {
                "erreur": "L'enfant ne sait pas justifier",
                "reponse_maieutique": (
                    "Essaie avec le mot 'moitié'. "
                    "Dans chaque miroir, est-ce que la partie colorée représente la moitié du tout ?"
                ),
            },
        ],
    },
    # ── Exercice 7 ── 4/6 et 6/9 sont-elles équivalentes ? ──────────────────
    {
        "id": "ile1_s3_ex7",
        "enonce": (
            "Les fractions 4/6 et 6/9 sont-elles équivalentes ? "
            "Justifie sans dessin, en utilisant une méthode."
        ),
        "reponse": "Oui. 4/6 = 2/3 et 6/9 = 2/3, donc elles sont équivalentes.",
        "solution_etapes": [
            "Simplifier 4/6 en divisant le haut et le bas par 2 : 4 ÷ 2 = 2 et 6 ÷ 2 = 3, donc 4/6 = 2/3.",
            "Simplifier 6/9 en divisant le haut et le bas par 3 : 6 ÷ 3 = 2 et 9 ÷ 3 = 3, donc 6/9 = 2/3.",
            "Comparer les formes simplifiées : elles sont toutes les deux égales à 2/3.",
            "Conclure que 4/6 et 6/9 sont équivalentes.",
        ],
        "indices": {
            "leger": (
                "Quand les dessins deviennent difficiles, on peut simplifier les fractions. "
                "Peux-tu simplifier 4/6 ?"
            ),
            "moyen": (
                "4 et 6 ont un diviseur commun. 6 et 9 aussi. "
                "Cherche la forme plus simple de chaque fraction."
            ),
            "fort": (
                "Essaie de ramener chaque fraction à une fraction avec un 3 au dénominateur. "
                "Que devient 4/6 ? Que devient 6/9 ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond non parce que 4, 6 et 9 sont différents",
                "reponse_maieutique": (
                    "Les nombres sont différents, mais les fractions équivalentes "
                    "ont justement souvent des nombres différents. "
                    "Quelle méthode peut vérifier si elles montrent la même part ?"
                ),
            },
            {
                "erreur": "L'enfant ajoute 2 à 4/6 pour obtenir 6/8 et compare à 6/9",
                "reponse_maieutique": (
                    "Attention : ajouter ne conserve pas le même reflet. "
                    "Quelle opération garde l'équivalence quand elle est faite au haut et au bas ?"
                ),
            },
            {
                "erreur": "L'enfant simplifie 4/6 en 4/3 ou 2/6",
                "reponse_maieutique": (
                    "Pour simplifier, on divise le haut et le bas par le même nombre. "
                    "Si tu divises le haut par 2, que dois-tu faire au bas ?"
                ),
            },
        ],
    },
]

# V3 corrigé : CRITIQUE → objet chantier Syracuse
VALIDATION_SESSION_3: dict = {
    "consigne": (
        "Archimède demande : "
        "'Explique pourquoi 1/2, 2/4 et 4/8 peuvent être trois écritures différentes "
        "de la même part. "
        "Tu peux utiliser l'image d'un bloc de marbre, d'un bassin d'eau ou d'une dalle.'"
    ),
    "critere_reussite": (
        "L'enfant explique que le tout peut être découpé plus finement sans changer "
        "la quantité coloriée ou prise. "
        "Il comprend que l'on multiplie ou divise le numérateur et le dénominateur "
        "par le même nombre."
    ),
    "si_echec": (
        "Archimède revient au concret : un rectangle à moitié colorié, "
        "puis redécoupé en 4, puis en 8. "
        "Il évite la règle formelle tant que l'enfant ne voit pas la même surface."
    ),
}

# ---------------------------------------------------------------------------
# SESSION 4 — "La Grande Balance"
# Concept C4 : Comparer et ranger des fractions
# Mode : Pratique puis Validation
# ---------------------------------------------------------------------------

META_SESSION_4: dict = {
    "id": "ile1_s4",
    "titre": "La Grande Balance",
    "concept": "C4 — Comparer et ranger des fractions",
    "cristal": "Cristal de la Balance",
    "planche_key": "c4",
    "situation_narrative": (
        "Au centre de l'île se trouve une grande balance de pierre. "
        "Elle ne pèse pas des objets, mais des parts de tout. "
        "Pour franchir la salle, l'Élévateur doit apprendre à comparer des fractions "
        "sans se laisser piéger par les nombres. "
        "Archimède guide d'abord par le sens : plus de parts de même taille, "
        "parts plus petites quand on découpe davantage, "
        "puis recours aux équivalences."
    ),
}

SESSION_4: list[dict] = [
    # ── Exercice 1 ── Tablette : 3/8 vs 5/8 ─────────────────────────────────
    {
        "id": "ile1_s4_ex1",
        "enonce": (
            "Sur la balance, on compare 3/8 d'une tablette et 5/8 de la même tablette. "
            "Quelle fraction est la plus grande ?"
        ),
        "reponse": "5/8",
        "solution_etapes": [
            "Les deux fractions ont le même dénominateur : 8. Les parts sont donc de même taille.",
            "Comparer les numérateurs : 3 parts contre 5 parts.",
            "Quand les parts ont la même taille, la fraction avec le plus grand numérateur est la plus grande.",
            "5/8 est plus grand que 3/8.",
        ],
        "indices": {
            "leger": (
                "Les deux tablettes sont coupées en 8 parts égales. "
                "Les morceaux ont-ils la même taille ?"
            ),
            "moyen": "Si les morceaux ont la même taille, que préfères-tu : 3 morceaux ou 5 morceaux ?",
            "fort": (
                "Même dénominateur : on compare seulement le nombre de parts prises. "
                "Compare 3 et 5."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant compare les deux fractions comme deux nombres séparés et hésite",
                "reponse_maieutique": (
                    "Ici, les parts sont de même taille : des huitièmes. "
                    "Donc il suffit de demander : combien de huitièmes prend-on ?"
                ),
            },
            {
                "erreur": "L'enfant dit que 3/8 est plus petit sans pouvoir justifier",
                "reponse_maieutique": (
                    "Tu as peut-être raison. Mais Archimède veut ton raisonnement : "
                    "pourquoi peut-on comparer seulement 3 et 5 ici ?"
                ),
            },
            {
                "erreur": "L'enfant pense que les dénominateurs doivent aussi être comparés",
                "reponse_maieutique": (
                    "Les deux nombres du bas sont identiques. "
                    "Est-ce que la taille des parts change entre les deux fractions ?"
                ),
            },
        ],
    },
    # ── Exercice 2 ── Dalle de marbre : 1/4 vs 1/8 ── V4, V5, V6 corrigés ───
    {
        "id": "ile1_s4_ex2",
        "enonce": (
            "La balance compare 1/4 d'une dalle de marbre et 1/8 de la même dalle. "
            "Quelle fraction est la plus grande ?"
        ),
        "reponse": "1/4",
        "solution_etapes": [
            "Les deux fractions ont le même numérateur : 1. On prend une seule part dans les deux cas.",
            "Comparer la taille des parts : quand on coupe une dalle de marbre en 4, "
            "les parts sont plus grandes que quand on la coupe en 8.",
            "Un quart est donc plus grand qu'un huitième.",
            "1/4 est plus grand que 1/8.",
        ],
        "indices": {
            # V5 corrigé : CRITIQUE → dalles de marbre
            "leger": (
                "Imagine deux dalles identiques : l'une coupée en 4 blocs, l'autre en 8 blocs. "
                "Dans laquelle un seul bloc est-il plus grand ?"
            ),
            "moyen": (
                "Plus on coupe un tout en beaucoup de parts, plus chaque part devient petite. "
                "Une part sur 4 est-elle plus grande qu'une part sur 8 ?"
            ),
            "fort": (
                "Dans les deux fractions, on prend 1 seule part. "
                "Il faut donc comparer la taille d'une part quand le tout est coupé en 4 ou en 8."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond 1/8 parce que 8 est plus grand que 4",
                "reponse_maieutique": (
                    "Le 8 signifie qu'on coupe en 8 morceaux. "
                    "Est-ce que couper en plus de morceaux rend chaque morceau plus grand ou plus petit ?"
                ),
            },
            {
                "erreur": "L'enfant dit que les deux sont égales parce que le numérateur est 1",
                "reponse_maieutique": (
                    "On prend bien une part dans les deux cas. "
                    "Mais ces deux parts ont-elles la même taille si les découpes sont différentes ?"
                ),
            },
            {
                # V6 corrigé : CRITIQUE → dalle
                "erreur": "L'enfant ne visualise pas",
                "reponse_maieutique": (
                    "Imagine une dalle coupée en 4 blocs, puis une dalle identique coupée en 8 blocs. "
                    "Quel bloc aimerais-tu recevoir si tu as besoin du plus grand morceau ?"
                ),
            },
        ],
    },
    # ── Exercice 3 ── 3/5 vs 3/7 ────────────────────────────────────────────
    {
        "id": "ile1_s4_ex3",
        "enonce": "Compare 3/5 et 3/7. Laquelle est la plus grande ?",
        "reponse": "3/5",
        "solution_etapes": [
            "Les deux fractions ont le même numérateur : 3. On prend 3 parts dans les deux cas.",
            "Comparer la taille des parts : des cinquièmes sont plus grands que des septièmes, "
            "car le tout est coupé en moins de parts.",
            "Trois grandes parts de cinquièmes valent plus que trois petites parts de septièmes.",
            "3/5 est plus grand que 3/7.",
        ],
        "indices": {
            "leger": "Dans les deux cas, on prend 3 parts. Mais les parts ont-elles la même taille ?",
            "moyen": (
                "Des parts de cinquième sont-elles plus grandes ou plus petites "
                "que des parts de septième ?"
            ),
            "fort": (
                "Même numérateur : regarde la taille des parts. "
                "Plus le dénominateur est petit, plus chaque part est grande."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond 3/7 parce que 7 est plus grand",
                "reponse_maieutique": (
                    "Le 7 ne veut pas dire qu'on a plus. "
                    "Il veut dire que le tout est découpé en 7 morceaux. "
                    "Ces morceaux sont-ils plus grands ou plus petits que des cinquièmes ?"
                ),
            },
            {
                "erreur": "L'enfant pense que même numérateur signifie égalité",
                "reponse_maieutique": (
                    "On prend bien 3 parts dans les deux cas. "
                    "Mais 3 grandes parts et 3 petites parts, est-ce la même quantité ?"
                ),
            },
            {
                "erreur": "L'enfant inverse la règle",
                "reponse_maieutique": (
                    "Teste avec une planche du pont : préfères-tu 3 parts d'une planche coupée en 5, "
                    "ou 3 parts d'une planche coupée en 7 ? Pourquoi ?"
                ),
            },
        ],
    },
    # ── Exercice 4 ── Portail : 7/7 vs 5/7 ─────────────────────────────────
    {
        "id": "ile1_s4_ex4",
        "enonce": (
            "Le portail est presque réparé. "
            "Compare 7/7 et 5/7. "
            "Quelle fraction représente la plus grande partie du portail ?"
        ),
        "reponse": "7/7",
        "solution_etapes": [
            "Les deux fractions ont le même dénominateur : 7. Les parts sont de même taille.",
            "Comparer les numérateurs : 7 parts contre 5 parts.",
            "7/7 représente toutes les parts du portail, donc le portail entier.",
            "7/7 est plus grand que 5/7.",
        ],
        "indices": {
            "leger": (
                "Le portail est découpé en 7 parties dans les deux cas. "
                "Combien de parties prend-on dans chaque fraction ?"
            ),
            "moyen": (
                "7/7 signifie qu'on prend les 7 parties sur 7. "
                "Est-ce qu'il manque une partie ?"
            ),
            "fort": (
                "Quand le haut et le bas sont identiques, on a le tout entier. "
                "Compare ce tout entier à 5 parts sur 7."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant ne reconnaît pas 7/7 comme le tout",
                "reponse_maieutique": (
                    "Si le portail a 7 parties et que tu as les 7, "
                    "manque-t-il quelque chose au portail ?"
                ),
            },
            {
                "erreur": "L'enfant pense que 5/7 et 7/7 sont proches donc presque égales",
                "reponse_maieutique": (
                    "Elles sont proches, mais pas égales. "
                    "Combien de parts manque-t-il dans 5/7 pour avoir le portail entier ?"
                ),
            },
            {
                "erreur": "L'enfant dit 5/7 parce qu'il se méfie de 7/7",
                "reponse_maieutique": (
                    "Regarde seulement les septièmes : "
                    "que vaut plus, 7 morceaux de même taille ou 5 morceaux de même taille ?"
                ),
            },
        ],
    },
    # ── Exercice 5 ── Réserve : 2/3 vs 3/4 (dénominateurs différents) ───────
    {
        "id": "ile1_s4_ex5",
        "enonce": (
            "La balance compare 2/3 d'une réserve et 3/4 de la même réserve. "
            "Quelle fraction est la plus grande ?"
        ),
        "reponse": "3/4",
        "solution_etapes": [
            "Les dénominateurs sont différents : 3 et 4. On ne peut pas comparer directement les numérateurs.",
            "Chercher un dénominateur commun : 12.",
            "Transformer 2/3 en douzièmes : 2/3 = 8/12.",
            "Transformer 3/4 en douzièmes : 3/4 = 9/12.",
            "Comparer 8/12 et 9/12 : 9/12 est plus grand.",
            "Donc 3/4 est plus grand que 2/3.",
        ],
        "indices": {
            "leger": (
                "Ici, les parts ne sont pas de même taille. "
                "On peut les transformer pour les comparer avec le même type de parts."
            ),
            "moyen": (
                "Peux-tu écrire 2/3 et 3/4 avec un même dénominateur ? Pense à 12."
            ),
            "fort": (
                "Transforme 2/3 en douzièmes, puis 3/4 en douzièmes. "
                "Après, tu pourras comparer les numérateurs."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond 3/4 parce que 4 est plus grand que 3 sans méthode",
                "reponse_maieutique": (
                    "Tu as peut-être la bonne réponse, mais Archimède ne cherche pas un pari. "
                    "Comment peux-tu le prouver avec des fractions équivalentes ?"
                ),
            },
            {
                "erreur": "L'enfant compare seulement 2 et 3",
                "reponse_maieutique": (
                    "Les parts ne sont pas les mêmes : des tiers et des quarts. "
                    "Peut-on comparer seulement le nombre de parts si les parts n'ont pas la même taille ?"
                ),
            },
            {
                "erreur": "L'enfant transforme mal 2/3 en 2/12",
                "reponse_maieutique": (
                    "Si tu changes le bas de 3 à 12, par combien as-tu multiplié le bas ? "
                    "Que dois-tu faire au haut pour garder la même fraction ?"
                ),
            },
        ],
    },
    # ── Exercice 6 ── Ranger 1/2, 3/4, 2/8 ──────────────────────────────────
    {
        "id": "ile1_s4_ex6",
        "enonce": "Range ces fractions de la plus petite à la plus grande : 1/2, 3/4, 2/8.",
        "reponse": "2/8 < 1/2 < 3/4",
        "solution_etapes": [
            "Transformer ou reconnaître chaque fraction.",
            "2/8 se simplifie en 1/4, donc c'est un quart.",
            "1/2 est une moitié.",
            "3/4 est trois quarts.",
            "Comparer les quarts : 1/4 < 2/4 < 3/4.",
            "Donc 2/8 < 1/2 < 3/4.",
        ],
        "indices": {
            "leger": (
                "Essaie de penser en parts de même type. "
                "Peux-tu transformer ces fractions en quarts ?"
            ),
            "moyen": (
                "2/8 représente quelle part simple du tout ? "
                "Et 1/2, combien de quarts cela fait-il ?"
            ),
            "fort": (
                "Écris tout en quarts : 2/8 devient 1/4, 1/2 devient 2/4, "
                "et 3/4 est déjà en quarts."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant range selon les dénominateurs : 1/2, 3/4, 2/8",
                "reponse_maieutique": (
                    "Ranger les dénominateurs ne suffit pas. "
                    "Le 8 signifie des parts plus petites, pas forcément une plus grande quantité. "
                    "Peux-tu transformer en quarts ?"
                ),
            },
            {
                "erreur": "L'enfant pense que 2/8 est plus grand que 1/2 parce que 8 est grand",
                "reponse_maieutique": (
                    "2/8, c'est 2 petites parts sur 8. "
                    "Est-ce plus ou moins qu'une moitié du tout ?"
                ),
            },
            {
                "erreur": "L'enfant oublie que 1/2 = 2/4",
                "reponse_maieutique": (
                    "Si une figure est coupée en 4 parts, "
                    "combien de parts faut-il colorier pour avoir une moitié ?"
                ),
            },
        ],
    },
    # ── Exercice 7 ── Réservoir : 5/6 > 2/3 ? ───────────────────────────────
    {
        "id": "ile1_s4_ex7",
        "enonce": (
            "Pour ouvrir la porte de l'île, le réservoir doit être rempli à plus de 2/3. "
            "Il est rempli aux 5/6. La porte peut-elle s'ouvrir ? Justifie."
        ),
        "reponse": "Oui, car 5/6 est plus grand que 2/3.",
        "solution_etapes": [
            "Comparer 5/6 et 2/3.",
            "Transformer 2/3 en sixièmes : 2/3 = 4/6.",
            "Comparer 5/6 et 4/6 : les dénominateurs sont identiques, donc on compare 5 et 4.",
            "5/6 est plus grand que 4/6, donc 5/6 est plus grand que 2/3.",
            "La porte peut s'ouvrir.",
        ],
        "indices": {
            "leger": "Il faut comparer 5/6 avec 2/3. Peux-tu écrire 2/3 en sixièmes ?",
            "moyen": (
                "Chaque tiers peut être coupé en 2 sixièmes. "
                "Que deviennent 2 tiers quand on les écrit en sixièmes ?"
            ),
            "fort": (
                "Transforme 2/3 en une fraction avec 6 en bas. "
                "Puis compare cette fraction avec 5/6."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond non parce que 2/3 lui paraît plus grand",
                "reponse_maieutique": (
                    "Avant de décider, mets les deux fractions dans le même langage. "
                    "Combien vaut 2/3 en sixièmes ?"
                ),
            },
            {
                "erreur": "L'enfant transforme 2/3 en 2/6",
                "reponse_maieutique": (
                    "Si tu coupes chaque tiers en deux, le nombre total de parts double. "
                    "Mais les parts remplies doublent-elles aussi ?"
                ),
            },
            {
                "erreur": "L'enfant répond oui sans justification",
                "reponse_maieutique": (
                    "La porte de l'île ne s'ouvre pas avec une intuition. "
                    "Quelle preuve peux-tu donner à la balance ?"
                ),
            },
        ],
    },
]

# V7 + V8 corrigés : CRITIQUE × 2 → dalle / planche du pont
VALIDATION_SESSION_4: dict = {
    "consigne": (
        "Archimède demande : "
        "'Explique pourquoi 1/4 est plus grand que 1/8, même si 8 est plus grand que 4. "
        "Utilise l'image d'une dalle de marbre ou d'une planche de pont.'"
    ),
    "critere_reussite": (
        "L'enfant explique que plus on coupe un tout en beaucoup de parts, "
        "plus chaque part est petite. "
        "Il distingue le nombre de parts et la taille de chaque part."
    ),
    # V8 corrigé : CRITIQUE → deux planches
    "si_echec": (
        "Archimède revient à une situation très concrète : "
        "deux planches identiques, l'une coupée en 4, l'autre en 8. "
        "Il fait choisir le bloc le plus grand visuellement "
        "avant de revenir à l'écriture fractionnaire."
    ),
}

# ---------------------------------------------------------------------------
# SESSION 5 — "L'Assemblage des Parts"
# Concept C5 : Addition et soustraction de fractions de même dénominateur
# Mode : Découverte puis Consolidation
# ---------------------------------------------------------------------------

META_SESSION_5: dict = {
    "id": "ile1_s5",
    "titre": "L'Assemblage des Parts",
    "concept": "C5 — Addition et soustraction de fractions (même dénominateur)",
    "cristal": "Cristal de l'Assemblage",
    "planche_key": "c5",
    "situation_narrative": (
        "Les fragments du pont, des miroirs et des réserves doivent maintenant être assemblés. "
        "L'Élévateur comprend que lorsque les parts sont du même type — "
        "des septièmes avec des septièmes, des dixièmes avec des dixièmes — "
        "on additionne ou on soustrait seulement le nombre de parts. "
        "Le dénominateur reste stable : il décrit la découpe du tout."
    ),
}

SESSION_5: list[dict] = [
    # ── Exercice 1 ── Pont 7 planches : 1/7 + 3/7 → 4/7 ────────────────────
    {
        "id": "ile1_s5_ex1",
        "enonce": (
            "Sur le pont, il y a 7 planches identiques. "
            "Tu en poses d'abord 1/7, puis 3/7 de plus. "
            "Quelle fraction du pont as-tu posée en tout ?"
        ),
        "reponse": "4/7",
        "solution_etapes": [
            "Les deux fractions ont le même dénominateur : 7. "
            "Les planches sont du même type, le pont est découpé en 7 parts.",
            "Additionner les numérateurs : 1 + 3 = 4.",
            "Le dénominateur ne change pas : il décrit le nombre total de planches du pont.",
            "Le résultat est 4/7.",
        ],
        "indices": {
            "leger": (
                "Tu poses 1 planche sur 7, puis 3 planches sur 7. "
                "Combien de planches as-tu posées en tout ?"
            ),
            "moyen": (
                "Le pont a toujours 7 emplacements. "
                "Quand tu ajoutes des planches posées, est-ce que le nombre total d'emplacements change ?"
            ),
            "fort": (
                "Additionne seulement les nombres du haut : 1 et 3. "
                "Le nombre du bas reste 7 parce que le pont a toujours 7 planches possibles."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant additionne les dénominateurs : 1/7 + 3/7 = 4/14",
                "reponse_maieutique": (
                    "Réfléchis au pont. Il avait 7 emplacements au départ. "
                    "Quand tu poses des planches, est-ce que le pont gagne soudain 14 emplacements ?"
                ),
            },
            {
                "erreur": "L'enfant répond 4 sans fraction",
                "reponse_maieutique": (
                    "4 dit combien de planches sont posées. "
                    "Mais on veut une fraction du pont. "
                    "4 planches sur combien d'emplacements en tout ?"
                ),
            },
            {
                "erreur": "L'enfant donne le bon résultat mais ne sait pas pourquoi le bas reste 7",
                "reponse_maieutique": (
                    "Tu as trouvé. Maintenant, explique-moi : "
                    "que représente le 7 du bas ? Et pourquoi ne change-t-il pas ?"
                ),
            },
        ],
    },
    # ── Exercice 2 ── Miroir : 2/9 + 4/9 → 6/9 ─────────────────────────────
    {
        "id": "ile1_s5_ex2",
        "enonce": (
            "Dans le miroir d'eau, 2/9 de la surface brillent déjà. "
            "Puis 4/9 de la surface s'allument. "
            "Quelle fraction de la surface brille maintenant ?"
        ),
        "reponse": "6/9",
        "solution_etapes": [
            "Les deux fractions ont le même dénominateur : 9. On parle de neuvièmes dans les deux cas.",
            "Additionner les parts brillantes : 2 + 4 = 6.",
            "Garder le dénominateur 9, car le miroir est toujours découpé en 9 parts.",
            "La fraction brillante est 6/9.",
            "Optionnellement, on peut remarquer que 6/9 est équivalent à 2/3, mais ce n'est pas nécessaire ici.",
        ],
        "indices": {
            "leger": (
                "On ajoute des neuvièmes avec des neuvièmes. "
                "Quelle partie de la fraction compte le nombre de parts brillantes ?"
            ),
            "moyen": (
                "Le miroir est découpé en 9 parts. "
                "Il y en a 2 qui brillent, puis 4 de plus. Combien brillent en tout ?"
            ),
            "fort": (
                "Additionne les nombres du haut. "
                "Le 9 du bas reste le même, car les parts sont toujours des neuvièmes."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond 6/18",
                "reponse_maieutique": (
                    "Si le miroir était découpé en 9 parts au début, "
                    "est-il soudain découpé en 18 parts parce que certaines s'allument ?"
                ),
            },
            {
                "erreur": "L'enfant simplifie en 2/3 sans expliquer 6/9",
                "reponse_maieutique": (
                    "2/3 peut être une forme simplifiée. "
                    "Mais avant de simplifier, quelle fraction obtient-on quand on additionne les neuvièmes ?"
                ),
            },
            {
                "erreur": "L'enfant additionne 2 + 4 mais oublie le dénominateur",
                "reponse_maieutique": (
                    "6 parts brillent, oui. "
                    "Mais pour savoir quelle fraction cela représente, "
                    "il faut dire 6 parts sur combien de parts en tout ?"
                ),
            },
        ],
    },
    # ── Exercice 3 ── Barrière : 5/8 − 2/8 → 3/8 ───────────────────────────
    {
        "id": "ile1_s5_ex3",
        "enonce": (
            "Une barrière de l'île est réparée aux 5/8. "
            "Une tempête abîme 2/8 de la barrière réparée. "
            "Quelle fraction reste réparée ?"
        ),
        "reponse": "3/8",
        "solution_etapes": [
            "Les fractions ont le même dénominateur : 8. On parle de huitièmes dans les deux cas.",
            "Il s'agit d'une soustraction : on retire 2/8 à 5/8.",
            "Soustraire les numérateurs : 5 - 2 = 3.",
            "Garder le dénominateur 8.",
            "Il reste 3/8 de la barrière réparée.",
        ],
        "indices": {
            "leger": (
                "On avait 5 huitièmes réparés. On en perd 2 huitièmes. "
                "Est-ce une addition ou une soustraction ?"
            ),
            "moyen": (
                "Les parts sont toutes des huitièmes. "
                "Combien de huitièmes restent si on enlève 2 huitièmes à 5 huitièmes ?"
            ),
            "fort": (
                "Soustrais seulement les nombres du haut : 5 - 2. "
                "Le bas reste 8 parce que la barrière est toujours découpée en huit parts."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant fait 5/8 - 2/8 = 3/0",
                "reponse_maieutique": (
                    "Le bas ne dit pas combien de parts on enlève. "
                    "Il dit le type de découpe. "
                    "Si la barrière est en 8 parts, est-ce que cette découpe disparaît "
                    "quand on retire des parts ?"
                ),
            },
            {
                "erreur": "L'enfant fait 5 - 2 mais répond 3",
                "reponse_maieutique": (
                    "3 est le nombre de parts restantes. "
                    "Mais ces parts sont des quoi ? Des huitièmes, des cinquièmes, ou autre chose ?"
                ),
            },
            {
                "erreur": "L'enfant additionne au lieu de soustraire",
                "reponse_maieutique": (
                    "La tempête ajoute-t-elle des réparations ou en abîme-t-elle ? "
                    "Quelle opération correspond à 'il en reste' après une perte ?"
                ),
            },
        ],
    },
    # ── Exercice 4 ── Fresque : 3/10 + 6/10 → 9/10 ─────────────────────────
    {
        "id": "ile1_s5_ex4",
        "enonce": (
            "Pour allumer une fresque, Philia active 3/10 des symboles le matin "
            "et 6/10 le soir. "
            "Quelle fraction des symboles est activée au total ?"
        ),
        "reponse": "9/10",
        "solution_etapes": [
            "Les deux fractions sont en dixièmes : elles ont le même dénominateur.",
            "Additionner les numérateurs : 3 + 6 = 9.",
            "Garder le dénominateur 10.",
            "La fraction activée au total est 9/10.",
            "Vérifier le sens : 9/10 est presque toute la fresque, ce qui est cohérent "
            "car 3/10 + 6/10 représente beaucoup de symboles.",
        ],
        "indices": {
            "leger": (
                "Les deux fractions parlent du même type de parts : des dixièmes. "
                "Combien de dixièmes sont activés en tout ?"
            ),
            "moyen": (
                "Additionne les symboles activés : 3 dixièmes et 6 dixièmes. "
                "Le nombre total de parts de la fresque change-t-il ?"
            ),
            "fort": (
                "3 dixièmes + 6 dixièmes = 9 dixièmes. "
                "Comment écris-tu 9 dixièmes en fraction ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond 9/20",
                "reponse_maieutique": (
                    "La fresque était découpée en 10 symboles au départ. "
                    "Quand Philia en active certains le matin puis le soir, "
                    "est-ce que la fresque passe à 20 symboles ?"
                ),
            },
            {
                "erreur": "L'enfant pense que 9/10 dépasse le tout",
                "reponse_maieutique": (
                    "Le tout serait 10/10. "
                    "Ici, on a 9/10. Est-ce plus que le tout ou presque le tout ?"
                ),
            },
            {
                "erreur": "L'enfant écrit 3 + 6 = 9 mais hésite sur le bas",
                "reponse_maieutique": (
                    "Le bas répond à la question : 'sur combien de parts la fresque est-elle découpée ?' "
                    "Quelle est cette réponse ici ?"
                ),
            },
        ],
    },
    # ── Exercice 5 ── Pont en sixièmes : 2/6 + 4/6 → 6/6 = 1 ───────────────
    {
        "id": "ile1_s5_ex5",
        "enonce": (
            "Deux équipes réparent le pont. "
            "La première répare 2/6 du pont. La seconde répare 4/6 du pont. "
            "Quelle fraction du pont est réparée ? Que représente ce résultat ?"
        ),
        "reponse": "6/6, c'est-à-dire le pont entier",
        "solution_etapes": [
            "Les deux fractions ont le même dénominateur : 6.",
            "Additionner les numérateurs : 2 + 4 = 6.",
            "Garder le dénominateur 6.",
            "Le résultat est 6/6.",
            "Reconnaître que 6/6 signifie toutes les parts sur toutes les parts : "
            "le pont entier, donc 1.",
        ],
        "indices": {
            "leger": (
                "On ajoute des sixièmes avec des sixièmes. "
                "Combien de sixièmes sont réparés en tout ?"
            ),
            "moyen": (
                "2 parts sur 6, puis 4 parts sur 6. "
                "Combien de parts sur 6 cela fait-il ?"
            ),
            "fort": (
                "Tu obtiens 6 parts sur 6. "
                "Quand le haut et le bas sont égaux, que représente la fraction ?"
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond 6/12",
                "reponse_maieutique": (
                    "Le pont n'est pas passé de 6 parts à 12 parts. "
                    "Il est toujours découpé en 6 parties. "
                    "Combien de ces 6 parties sont réparées ?"
                ),
            },
            {
                "erreur": "L'enfant répond 6/6 mais ne comprend pas que c'est 1",
                "reponse_maieutique": (
                    "Si les 6 parties du pont sur 6 sont réparées, "
                    "reste-t-il une partie cassée ? "
                    "Comment appelle-t-on toutes les parts d'un tout ?"
                ),
            },
            {
                "erreur": "L'enfant pense que 6/6 est impossible car une fraction doit être plus petite que 1",
                "reponse_maieutique": (
                    "Une fraction peut représenter une partie, mais aussi le tout. "
                    "Quand on prend toutes les parts, quelle fraction écrit-on ?"
                ),
            },
        ],
    },
    # ── Exercice 6 ── Réserve en 15 parts : 4/15 + 7/15, reste ? ───────────
    {
        "id": "ile1_s5_ex6",
        "enonce": (
            "La réserve d'eau est divisée en 15 parts égales. "
            "Le matin, on utilise 4/15 de la réserve. "
            "L'après-midi, on utilise encore 7/15. "
            "Quelle fraction de la réserve a été utilisée en tout ? "
            "Quelle fraction reste-t-il ?"
        ),
        "reponse": "11/15 utilisés ; 4/15 restants",
        "solution_etapes": [
            "Additionner les fractions utilisées : 4/15 + 7/15.",
            "Les dénominateurs sont identiques : on additionne les numérateurs.",
            "Calculer 4 + 7 = 11.",
            "La fraction utilisée est 11/15.",
            "Le tout vaut 15/15.",
            "Calculer ce qui reste : 15/15 - 11/15 = 4/15.",
            "Répondre : 11/15 utilisés et 4/15 restants.",
        ],
        "indices": {
            "leger": (
                "Il y a deux étapes : d'abord trouver la fraction utilisée en tout, "
                "puis trouver ce qui reste."
            ),
            "moyen": (
                "Additionne 4/15 et 7/15. "
                "Ensuite, rappelle-toi que la réserve entière vaut 15/15."
            ),
            "fort": (
                "Pour le total utilisé, additionne les nombres du haut. "
                "Pour le reste, enlève ce résultat à 15/15."
            ),
        },
        "erreurs_typiques": [
            {
                "erreur": "L'enfant répond seulement 11/15 et oublie la deuxième question",
                "reponse_maieutique": (
                    "Tu as trouvé ce qui est utilisé. Relis l'énoncé : "
                    "Archimède demande aussi ce qui reste. "
                    "Combien vaut la réserve entière en quinzièmes ?"
                ),
            },
            {
                "erreur": "L'enfant calcule 11/30",
                "reponse_maieutique": (
                    "Les parts sont déjà toutes des quinzièmes. "
                    "Quand on utilise des parts d'une même réserve, "
                    "est-ce que la réserve se redécoupe en 30 parts ?"
                ),
            },
            {
                "erreur": "L'enfant fait 15 - 11 = 4 mais répond 4 sans fraction",
                "reponse_maieutique": (
                    "4 parts restent, oui. "
                    "Mais 4 parts sur combien de parts égales dans toute la réserve ?"
                ),
            },
            {
                "erreur": "L'enfant retire 11/15 à 1 sans savoir écrire 1 en quinzièmes",
                "reponse_maieutique": (
                    "Pour soustraire des quinzièmes, il faut écrire le tout en quinzièmes. "
                    "Si la réserve entière est complète, c'est combien sur 15 ?"
                ),
            },
        ],
    },
]

VALIDATION_SESSION_5: dict = {
    "consigne": (
        "Archimède demande : "
        "'Explique pourquoi 2/7 + 3/7 ne donne pas 5/14. "
        "Utilise l'image d'un pont ou d'une tablette.'"
    ),
    "critere_reussite": (
        "L'enfant explique que le dénominateur indique le nombre total de parts du tout "
        "ou le type de découpe. "
        "Comme on additionne des parts de même type, on additionne les numérateurs seulement. "
        "Le tout reste découpé en 7 parts."
    ),
    "si_echec": (
        "Archimède reprend avec un dessin mental : un pont de 7 planches. "
        "Il fait verbaliser : "
        "'si j'ajoute des planches posées, le pont ne gagne pas de nouveaux emplacements'."
    ),
}

# ---------------------------------------------------------------------------
# BILAN ÎLE 1 — §9 "Consolidation Spiralaire"
# ---------------------------------------------------------------------------

BILAN_ILE1: dict = {
    "id": "ile1_bilan",
    "titre": "Le Serment du Cristal des Nombres Brisés",
    "competences_acquises": [
        "Comprendre qu'une fraction représente une ou plusieurs parts égales d'un tout.",
        "Identifier le rôle du numérateur et du dénominateur.",
        "Calculer une fraction simple d'une quantité.",
        "Reconnaître et produire des fractions équivalentes simples.",
        "Comparer des fractions dans les cas fondamentaux.",
        "Additionner et soustraire des fractions de même dénominateur.",
    ],
    "questions_archimede": [
        "Quand tu vois une fraction, quelle est la première chose que tu regardes ? Pourquoi ?",
        "Pourquoi les parts doivent-elles être égales ?",
        "Comment peux-tu expliquer que 1/2 et 2/4 représentent la même chose ?",
        "Pourquoi 1/4 est-il plus grand que 1/8 ?",
        "Pourquoi, dans 2/7 + 3/7, le 7 ne change-t-il pas ?",
    ],
    "criteres_de_maitrise": {
        "essentiel": [
            "L'enfant sait lire une fraction comme parts prises sur parts totales.",
            "L'enfant sait calculer 1/n d'une quantité simple.",
            "L'enfant ne confond plus systématiquement numérateur et dénominateur.",
        ],
        "solide": [
            "L'enfant sait calculer a/b d'une quantité en deux temps.",
            "L'enfant reconnaît des équivalences simples comme 1/2 = 2/4 = 4/8.",
            "L'enfant compare correctement les fractions de même dénominateur ou de même numérateur.",
        ],
        "avance": [
            "L'enfant justifie ses comparaisons avec des équivalences.",
            "L'enfant explique pourquoi on n'additionne pas les dénominateurs.",
            "L'enfant peut créer une situation concrète correspondant à une fraction donnée.",
        ],
    },
    # V9 corrigé : CRITIQUE → dalles / planches du pont
    "vigilance_pour_ile_2": [
        "Si l'enfant confond encore haut et bas, réactiver la Session 1 avant d'avancer.",
        "Si l'enfant calcule une fraction de quantité en divisant par le numérateur, "
        "prévoir une remédiation courte avant toute proportionnalité.",
        "Si l'enfant additionne les dénominateurs, réactiver l'image du pont à 7 emplacements.",
        "Si l'enfant compare les fractions par la taille brute des nombres, "
        "revenir à la Grande Balance avec des dalles ou des planches du pont.",
    ],
}
