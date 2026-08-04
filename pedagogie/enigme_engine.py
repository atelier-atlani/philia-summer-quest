"""
pedagogie/enigme_engine.py — State machine de l'énigme finale de l'Île 1 (D43).

Dialogue libre entre Archimède et l'enfant, en 4 temps, joué après l'obtention
de la Clé du Partage. Pas d'exercice YAML, pas de « bonne réponse » à valider :
le moteur fait progresser le dialogue à travers les 4 temps et garantit que le
secret final (temps 4) n'arrive jamais avant que les temps 1-3 soient passés.

Moteur autonome et isolé : il ne dépend ni de session_engine, ni de mentor.py,
ni des 5 modes. Il ne partage avec eux que les prompts de marque
(_shared_persona / _shared_guardrails), qu'il recharge lui-même.

Cycle d'utilisation (côté Streamlit) :
    engine = EnigmeEngine(prenom="Léa", avatar_genre="fille")
    intro  = engine.debut_enigme()
    texte  = engine.repondre(message_enfant)
    ...
    if engine.est_terminee():
        ...  # parchemin
    # Reconstruire depuis session_state :
    engine = EnigmeEngine.from_dict(st.session_state.enigme_active)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from core import llm_client

# ---------------------------------------------------------------------------
# Chargement des prompts
#
# Le chargement est volontairement dupliqué ici (même mécanisme que mentor.py :
# PROMPTS_DIR + _load_prompt) plutôt qu'importé de mentor.py : la spec impose de
# ne pas modifier mentor.py, et _PERSONA / _GUARDRAILS y sont des privés de
# module. Importer un privé coupleraient ce moteur à la tuyauterie des sessions
# (et lui ferait charger au passage les 5 prompts de mode dont il n'a aucun
# usage). Dix lignes dupliquées contre un moteur réellement isolé.
# ---------------------------------------------------------------------------

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts" / "mentor"


def _load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8").strip()


_PERSONA    = _load_prompt("_shared_persona.txt")
_GUARDRAILS = _load_prompt("_shared_guardrails.txt")
_SCRIPT     = _load_prompt("enigme_couronne.txt")


# ---------------------------------------------------------------------------
# Constantes de progression
# ---------------------------------------------------------------------------

MARQUEUR_SUIVANT = "[[TEMPS_SUIVANT]]"
MARQUEUR_FIN     = "[[ENIGME_FIN]]"

_KICKOFF = (
    "[DÉBUT DE L'ÉNIGME — message interne, non montré à l'enfant] "
    "L'enfant vient de terminer l'Île 1 et d'obtenir la Clé du Partage. "
    "Il s'approche de toi. Ouvre l'énigme au TEMPS 1 : pose le mystère de la "
    "couronne d'Hiéron, puis attends sa réponse."
)

_CONSIGNE_AVANCEE = (
    "[CONSIGNE INTERNE — non montrée à l'enfant] "
    "Ce temps a assez duré. Accueille la réponse de l'enfant, conclus ce temps "
    "maintenant et fais avancer l'énigme vers le temps suivant dans cette même "
    "réponse. N'attends pas un tour de plus."
)

_MESSAGE_TERMINEE = (
    "L'énigme est close. Garde bien ce parchemin — il t'attendra sur les "
    "autres îles."
)


class TempsEnigme(str, Enum):
    TEMPS_1  = "temps_1"
    TEMPS_2  = "temps_2"
    TEMPS_3  = "temps_3"
    TEMPS_4  = "temps_4"
    TERMINEE = "terminee"


_ORDRE_TEMPS: list[TempsEnigme] = [
    TempsEnigme.TEMPS_1,
    TempsEnigme.TEMPS_2,
    TempsEnigme.TEMPS_3,
    TempsEnigme.TEMPS_4,
]

_OBJECTIFS: dict[TempsEnigme, str] = {
    TempsEnigme.TEMPS_1: "poser le mystère de la couronne et donner envie d'enquêter",
    TempsEnigme.TEMPS_2: "faire TROUVER à l'enfant que la couronne truquée est une fraction",
    TempsEnigme.TEMPS_3: "valoriser l'enfant : il tient déjà un morceau de l'énigme",
    TempsEnigme.TEMPS_4: "révéler le secret comme un don, ouvrir vers la suite, offrir le parchemin",
}


# ---------------------------------------------------------------------------
# Interpolation et nettoyage
#
# ATTENTION : on N'UTILISE PAS str.format() sur les prompts. Les fichiers de
# prompts sont du texte libre édité à la main (persona, guardrails, script) et
# peuvent à tout moment recevoir une accolade littérale — un exemple de code,
# une notation d'ensemble, un emoji encadré. .format() planterait alors sur un
# KeyError/ValueError à l'exécution. On fait donc un remplacement ciblé des
# seuls placeholders réellement supportés : {prenom} et {accord}.
# ---------------------------------------------------------------------------


def _interpoler(texte: str, prenom: str, avatar_genre: str) -> str:
    accord = "Prête" if avatar_genre == "fille" else "Prêt"
    return texte.replace("{prenom}", prenom).replace("{accord}", accord)


def _extraire_marqueur(reponse: str) -> tuple[str, str | None]:
    """Retire les marqueurs de progression du texte et dit lequel a été vu.

    Le marqueur est attendu seul sur la dernière ligne, mais on le cherche
    n'importe où dans la réponse : un LLM qui le pose au mauvais endroit ne doit
    jamais aboutir à un marqueur affiché à l'enfant.

    Retourne (texte nettoyé, MARQUEUR_FIN | MARQUEUR_SUIVANT | None).
    """
    marqueur: str | None = None
    if MARQUEUR_FIN in reponse:
        marqueur = MARQUEUR_FIN
    elif MARQUEUR_SUIVANT in reponse:
        marqueur = MARQUEUR_SUIVANT

    texte = reponse.replace(MARQUEUR_FIN, "").replace(MARQUEUR_SUIVANT, "")
    return texte.strip(), marqueur


# ---------------------------------------------------------------------------
# Prompt système
# ---------------------------------------------------------------------------


def _build_system_prompt(
    temps: TempsEnigme,
    prenom: str = "Élévateur",
    avatar_genre: str = "fille",
) -> str:
    objectif = _OBJECTIFS.get(temps, "")
    sections = [
        _PERSONA,
        _GUARDRAILS,
        _SCRIPT,
        f"Le prénom de l'enfant que tu accompagnes est : {prenom}",
        "\n".join([
            "═══════════════════════════════════════════════",
            f"TEMPS COURANT : {temps.value}",
            "═══════════════════════════════════════════════",
            "",
            f"Objectif de ce temps : {objectif}.",
            "Concentre-toi sur l'objectif de ce temps uniquement. "
            "Tu ne travailles ni le temps précédent, ni les suivants.",
        ]),
    ]
    return _interpoler("\n\n\n".join(sections), prenom, avatar_genre)


# ---------------------------------------------------------------------------
# Moteur
# ---------------------------------------------------------------------------


@dataclass
class EnigmeEngine:
    prenom: str = "Élévateur"
    avatar_genre: str = "fille"
    temps: TempsEnigme = TempsEnigme.TEMPS_1
    historique: list[dict] = field(default_factory=list)
    tours_dans_temps: int = 0
    PLAFOND_TOURS_PAR_TEMPS: int = 4

    # ------------------------------------------------------------------ #
    # Interface publique                                                   #
    # ------------------------------------------------------------------ #

    def debut_enigme(self) -> str:
        """Ouvre l'énigme au TEMPS 1 et retourne le premier message d'Archimède.

        Le kickoff compte comme un tour du temps 1. Un marqueur émis sur ce
        premier message est retiré mais ignoré : l'enfant n'a pas encore parlé,
        le temps 1 ne peut donc pas être accompli.
        """
        self.temps = TempsEnigme.TEMPS_1
        self.tours_dans_temps = 1
        self.historique = []

        reponse = self._appeler_llm(_KICKOFF)
        texte, _ = _extraire_marqueur(reponse)

        self.historique = [
            {"role": "user",      "content": _KICKOFF},
            {"role": "assistant", "content": texte},
        ]
        return texte

    def repondre(self, message: str) -> str:
        """Traite un message de l'enfant et retourne la réponse d'Archimède.

        Le texte retourné est toujours nettoyé de ses marqueurs de progression.
        """
        if self.est_terminee():
            return _MESSAGE_TERMINEE

        self.tours_dans_temps += 1

        # Garde-fou : au dernier tour autorisé du temps, on pousse le LLM à
        # conclure — et on avancera de toute façon, marqueur ou pas.
        force = self.tours_dans_temps >= self.PLAFOND_TOURS_PAR_TEMPS
        contenu = f"{message}\n\n{_CONSIGNE_AVANCEE}" if force else message

        reponse = self._appeler_llm(contenu)
        texte, marqueur = _extraire_marqueur(reponse)

        # L'historique conserve le message brut de l'enfant : la consigne
        # interne est un coup de pouce ponctuel, pas un tour de dialogue.
        self.historique.append({"role": "user",      "content": message})
        self.historique.append({"role": "assistant", "content": texte})

        # Un [[ENIGME_FIN]] émis avant le temps 4 ne clôt pas l'énigme : il vaut
        # une simple avancée. Aucun temps n'est jamais sauté — c'est le moteur
        # qui le garantit, pas la discipline du LLM.
        if marqueur == MARQUEUR_FIN and self.temps == TempsEnigme.TEMPS_4:
            self.temps = TempsEnigme.TERMINEE
            self.tours_dans_temps = 0
        elif marqueur is not None or force:
            self._avancer()

        return texte

    def est_terminee(self) -> bool:
        return self.temps == TempsEnigme.TERMINEE

    def messages_pour_affichage(self) -> list[dict]:
        """Historique sans le kickoff interne — à utiliser dans l'UI."""
        return [m for m in self.historique if m.get("content") != _KICKOFF]

    # ------------------------------------------------------------------ #
    # Interne                                                              #
    # ------------------------------------------------------------------ #

    def _appeler_llm(self, contenu: str) -> str:
        system_prompt = _build_system_prompt(
            self.temps, self.prenom, self.avatar_genre
        )
        messages = list(self.historique) + [{"role": "user", "content": contenu}]
        return llm_client.chat(system_prompt, messages)

    def _avancer(self) -> None:
        """Passe au temps suivant — ou termine l'énigme si on était au temps 4."""
        try:
            i = _ORDRE_TEMPS.index(self.temps)
        except ValueError:          # déjà TERMINEE
            return
        if i + 1 < len(_ORDRE_TEMPS):
            self.temps = _ORDRE_TEMPS[i + 1]
        else:
            self.temps = TempsEnigme.TERMINEE
        self.tours_dans_temps = 0

    # ------------------------------------------------------------------ #
    # Sérialisation pour st.session_state                                 #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "prenom":                  self.prenom,
            "avatar_genre":            self.avatar_genre,
            "temps":                   self.temps.value,
            "historique":              self.historique,
            "tours_dans_temps":        self.tours_dans_temps,
            "PLAFOND_TOURS_PAR_TEMPS": self.PLAFOND_TOURS_PAR_TEMPS,
        }

    @classmethod
    def from_dict(cls, d: dict) -> EnigmeEngine:
        return cls(
            prenom=d.get("prenom", "Élévateur"),
            avatar_genre=d.get("avatar_genre", "fille"),
            temps=TempsEnigme(d.get("temps", TempsEnigme.TEMPS_1.value)),
            historique=d.get("historique", []),
            tours_dans_temps=d.get("tours_dans_temps", 0),
            PLAFOND_TOURS_PAR_TEMPS=d.get("PLAFOND_TOURS_PAR_TEMPS", 4),
        )
