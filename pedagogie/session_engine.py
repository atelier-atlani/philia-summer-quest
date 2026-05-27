"""
pedagogie/session_engine.py — State machine d'une session pédagogique.

Gère le déroulé : ouverture de session → tours de dialogue → clôture.
Ne contient aucune règle pédagogique — elles vivent dans prompts/mentor/.

Cycle d'utilisation (côté Streamlit) :
    engine = SessionEngine(exercice=ex, prenom="Léa")
    intro  = engine.debut_session()           # afficher intro.message
    out    = engine.repondre(message_enfant)  # afficher out.message
    ...
    # Pour reconstruire depuis session_state :
    engine = SessionEngine.from_dict(st.session_state.session_active, exercice)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from pedagogie import mentor
from pedagogie.mentor import Exercice
from pedagogie.mentor_contract import EtatPedagogique, MentorOutput
from pedagogie.modes import MODES_ACTIFS, TRANSITIONS, Mode

# Message interne utilisé pour déclencher l'ouverture de session.
# Jamais affiché à l'enfant — filtré par messages_pour_affichage().
_KICKOFF = (
    "[DÉBUT DE SESSION — message interne, non montré à l'enfant] "
    "L'enfant vient d'arriver et est prêt à commencer. "
    "Accueille-le chaleureusement par son prénom et ouvre la découverte "
    "avec une situation concrète, en posant une première question."
)

# Mots-clés qui signalent une demande de fin de session de la part de l'enfant.
_MOTS_FIN = {"au revoir", "bye", "/fin", "fin", "stop", "j'ai fini", "j ai fini"}


class PhaseSession(str, Enum):
    DEBUT    = "debut"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"


@dataclass
class SessionEngine:
    exercice: Exercice
    prenom: str = "Élévateur"
    mode: Mode = Mode.DECOUVERTE
    phase: PhaseSession = PhaseSession.DEBUT
    # Tous les messages API (y compris le kickoff interne).
    # Utiliser messages_pour_affichage() pour l'UI.
    historique: list[dict] = field(default_factory=list)
    etat: EtatPedagogique = field(default_factory=EtatPedagogique)

    # ------------------------------------------------------------------ #
    # Interface publique                                                   #
    # ------------------------------------------------------------------ #

    def debut_session(self) -> MentorOutput:
        """Ouvre la session et génère le message d'accueil d'Archimède."""
        self.phase = PhaseSession.EN_COURS
        self.etat = EtatPedagogique(
            mode=self.mode,
            concept_id=str(self.exercice.get("id", "")),
        )
        reponse = mentor.repondre(
            message=_KICKOFF,
            histoire=[],
            exercice=self.exercice,
            mode=self.mode.value,
            prenom=self.prenom,
        )
        self.historique = [
            {"role": "user",      "content": _KICKOFF},
            {"role": "assistant", "content": reponse},
        ]
        return MentorOutput(message=reponse, etat=self.etat)

    def repondre(self, message: str) -> MentorOutput:
        """Traite un message de l'enfant et retourne la réponse d'Archimède."""
        if self.phase == PhaseSession.TERMINEE:
            return MentorOutput(
                message="La session est terminée. À bientôt, Élévateur !",
                etat=self.etat,
            )

        self.etat.nb_tentatives += 1

        reponse = mentor.repondre(
            message=message,
            histoire=self.historique,
            exercice=self.exercice,
            mode=self.mode.value,
            prenom=self.prenom,
        )

        self.historique.append({"role": "user",      "content": message})
        self.historique.append({"role": "assistant", "content": reponse})

        if message.strip().lower() in _MOTS_FIN:
            self.phase = PhaseSession.TERMINEE

        return MentorOutput(message=reponse, etat=self.etat)

    def transitionner(self, nouveau_mode: Mode) -> bool:
        """Tente une transition de mode. Retourne True si acceptée."""
        if nouveau_mode not in TRANSITIONS.get(self.mode, []):
            return False
        if nouveau_mode not in MODES_ACTIFS:
            return False
        self.mode = nouveau_mode
        self.etat.mode = nouveau_mode
        self.etat.nb_tentatives = 0
        self.etat.indices_utilises = 0
        return True

    def messages_pour_affichage(self) -> list[dict]:
        """Retourne l'historique sans le kickoff interne — à utiliser dans l'UI."""
        return [m for m in self.historique if m.get("content") != _KICKOFF]

    # ------------------------------------------------------------------ #
    # Propriétés                                                           #
    # ------------------------------------------------------------------ #

    @property
    def est_terminee(self) -> bool:
        return self.phase == PhaseSession.TERMINEE

    # ------------------------------------------------------------------ #
    # Sérialisation pour st.session_state                                 #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "mode":      self.mode.value,
            "phase":     self.phase.value,
            "historique": self.historique,
            "prenom":    self.prenom,
            "etat": {
                "mode":             self.etat.mode.value,
                "concept_id":       self.etat.concept_id,
                "nb_tentatives":    self.etat.nb_tentatives,
                "indices_utilises": self.etat.indices_utilises,
            },
        }

    @classmethod
    def from_dict(cls, d: dict, exercice: Exercice) -> SessionEngine:
        e = d.get("etat", {})
        engine = cls(
            exercice=exercice,
            prenom=d.get("prenom", "Élévateur"),
            mode=Mode(d.get("mode", Mode.DECOUVERTE.value)),
            phase=PhaseSession(d.get("phase", PhaseSession.DEBUT.value)),
            historique=d.get("historique", []),
        )
        engine.etat = EtatPedagogique(
            mode=Mode(e.get("mode", Mode.DECOUVERTE.value)),
            concept_id=e.get("concept_id", ""),
            nb_tentatives=e.get("nb_tentatives", 0),
            indices_utilises=e.get("indices_utilises", 0),
        )
        return engine
