# SPEC CLAUDE CODE — MOTEUR ÉNIGME FINALE ÎLE 1

**Implémentation de D43 (énigme de la couronne). Dialogue libre maïeutique, 4 temps, sans exercice YAML.**
**Conception narrative de référence : `.claude/production/enigme-finale-ile1.md`.**
**Architecture validée : moteur DÉDIÉ, isolé de session_engine (qui est adossé aux exercices).**

---

## PRINCIPE

L'énigme est un dialogue libre entre Archimède et l'enfant, en 4 temps, joué
après l'obtention de la Clé du Partage. Pas d'exercice YAML, pas de « bonne
réponse » à valider. Le moteur fait progresser le dialogue à travers les 4 temps
et interdit de révéler le secret final (temps 4) avant que les temps 1-3 soient
passés.

**Réutilise** : `llm_client.chat`, les prompts partagés `_PERSONA` /
`_GUARDRAILS`, le pattern to_dict/from_dict, MOCK_LLM.
**Ne touche PAS** : session_engine.py, mentor.py existant, les 5 modes.

---

## FICHIER 1 — `prompts/mentor/enigme_couronne.txt` (nouveau)

Le script des 4 temps, formulé comme guardrails de progression pour le LLM.
Contenu à créer à partir de la section 3 du doc de conception. Structure :

```
Tu es Archimède, et tu confies à l'enfant l'énigme de ta vie : la couronne
du roi Hiéron. Ce n'est pas une leçon, c'est un moment de confidence entre
un maître et son élève qui vient de terminer sa première île.

Tu mènes l'enfant à travers 4 temps. Tu ne sautes jamais un temps. Tu ne
révèles JAMAIS le secret final (l'eau déplacée, la densité) avant le TEMPS 4.

═══ TEMPS 1 — L'ÉNIGME POSÉE ═══
[poser le mystère : or pur ou mélange truqué ? sans briser ni fondre.
Voir texte temps 1 du doc de conception.]
Quoi que réponde l'enfant, tu passes au TEMPS 2.

═══ TEMPS 2 — LA PIÈCE QUE L'ENFANT DÉTIENT (maïeutique) ═══
[faire trouver à l'enfant que la couronne truquée = une fraction, une part
d'or + une part d'argent. NE PAS donner ce lien — le faire trouver.]
Indices étagés si blocage (léger → moyen → fort). Voir doc §3.
Quand l'enfant a fait le lien (ou après indice fort), tu passes au TEMPS 3.

═══ TEMPS 3 — LA RÉVÉLATION DE L'ENQUÊTEUR ═══
[valoriser : l'enfant sait déjà lire les fractions, il tient un morceau de
l'énigme. Il a appris à voir sous les apparences.]
Tu passes au TEMPS 4.

═══ TEMPS 4 — LE SECRET ET LE PARCHEMIN ═══
[révéler enfin le secret (Eurêka, l'eau déplacée) comme un DON. Ouvrir vers
la suite : "comment mesurer" reste pour les autres îles. Annoncer le parchemin.]
C'est la fin de l'énigme.

RÈGLE DE SIGNALEMENT (pour le moteur, invisible à l'enfant) :
Quand un temps est accompli et que tu passes au suivant, termine ta réponse
par un marqueur sur sa propre ligne : [[TEMPS_SUIVANT]]
Ne mets ce marqueur QUE si le temps courant est réellement accompli.
Au TEMPS 4 accompli, termine par : [[ENIGME_FIN]]
```

Persona + guardrails partagés préfixés par le moteur, comme pour les sessions.

---

## FICHIER 2 — `pedagogie/enigme_engine.py` (nouveau)

State machine dédiée, sur le modèle structurel de session_engine.py mais SANS
exercices.

```python
class TempsEnigme(str, Enum):
    TEMPS_1 = "temps_1"
    TEMPS_2 = "temps_2"
    TEMPS_3 = "temps_3"
    TEMPS_4 = "temps_4"
    TERMINEE = "terminee"

@dataclass
class EnigmeEngine:
    prenom: str = "Élévateur"
    avatar_genre: str = "fille"
    temps: TempsEnigme = TempsEnigme.TEMPS_1
    historique: list[dict] = field(default_factory=list)
    tours_dans_temps: int = 0
    PLAFOND_TOURS_PAR_TEMPS: int = 4
```

**Progression (option 1 + garde-fou) :**
- Le LLM signale la fin d'un temps via `[[TEMPS_SUIVANT]]` (ou `[[ENIGME_FIN]]`
  au temps 4). Le moteur détecte le marqueur, le RETIRE du texte affiché, avance.
- GARDE-FOU : si `tours_dans_temps >= PLAFOND_TOURS_PAR_TEMPS` sans marqueur,
  le moteur force l'avancée (injecte au prochain appel une consigne interne
  « fais avancer vers le temps suivant maintenant »).
- Au changement de temps, `tours_dans_temps` repart à 0.
- `[[ENIGME_FIN]]` ou plafond au temps 4 → TERMINEE.

**Méthodes (miroir session_engine) :**
- `debut_enigme() -> str` : ouvre au TEMPS_1, kickoff interne, retourne le
  premier message.
- `repondre(message) -> str` : traite, appelle le LLM, détecte/retire marqueur,
  avance ou garde-fou, retourne texte nettoyé.
- `est_terminee() -> bool`
- `to_dict()` / `from_dict()` : persistance session_state.

**Prompt système** (nouvelle fonction dans enigme_engine.py ou helper séparé —
NE PAS modifier mentor.py) : réutiliser _PERSONA + _GUARDRAILS (chargés comme
mentor.py le fait) + enigme_couronne.txt + bloc TEMPS COURANT :

    sections = [_PERSONA, _GUARDRAILS, script_enigme,
                f"Prénom de l'enfant : {prenom}",
                f"TEMPS COURANT : {temps.value} — concentre-toi sur l'objectif "
                f"de ce temps uniquement."]

**Appel** : `llm_client.chat(system_prompt, messages)`, compatible MOCK_LLM
(en mock pas de marqueur → le garde-fou de tours fait avancer, ce qui teste
le flux UI).

---

## FICHIER 3 — `ui/ecran_enigme.py` (nouveau)

Écran léger sur le modèle de ecran_session.py, SANS machinerie d'exercice
(pas de compteur, pas de bouton « exercice suivant »).

- Reconstruit EnigmeEngine depuis session_state (from_dict).
- Affiche l'historique + champ de saisie.
- Quand est_terminee() : affiche le Parchemin d'Archimède
  (assets/ui/parchemin_archimede.png — placeholder si absent, pattern planches BD)
  + bouton « Retour à l'archipel » vers la carte.
- Image d'Archimède grand format en haut (ton solennel).

---

## FICHIER 4 — Déclenchement

Bouton « Archimède veut te confier quelque chose… » depuis le modal de fin
d'île (celebrations.py) OU l'écran carte → pose `ecran_courant = "enigme"` +
initialise EnigmeEngine.
Router dans app.py sur le modèle des autres écrans (lignes 46-56).
Condition : seulement après Île 1 complétée (Clé du Partage obtenue).

---

## CONTRAINTES

- Ne modifie PAS session_engine.py, mentor.py, les 5 modes, les prompts de mode.
- Moteur autonome et isolé.
- Compatible MOCK_LLM (garde-fou de tours garantit la progression).
- Interpolation {prenom} partout ; {accord} si un texte en a besoin.
- Le marqueur [[...]] TOUJOURS retiré avant affichage.
- Persistance session_state via to_dict/from_dict (sinon dialogue perdu au rerun).

## COMMITS (atomiques, séparés)

1. feat(enigme): prompt script énigme couronne (4 temps)
2. feat(enigme): moteur EnigmeEngine (dialogue libre 4 temps + garde-fou)
3. feat(enigme): écran énigme + déclenchement fin Île 1

Ne pas pousser. Lister les fichiers à chaque commit.
Le parchemin (asset) est produit séparément — placeholder en attendant.
