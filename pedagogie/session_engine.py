"""
pedagogie/session_engine.py — State machine d'une session pédagogique.

Gère le déroulé : ouverture de session → tours de dialogue → clôture.
Ne contient aucune règle pédagogique — elles vivent dans prompts/mentor/.

L'engine reçoit la liste complète et ordonnée des exercices d'une session.
Le séquençage (un exercice à la fois, dans l'ordre, sans saut) est garanti
ici — pas dans l'UI. L'écran Streamlit est une vitre, l'engine est le cerveau.

Cycle d'utilisation (côté Streamlit) :
    engine = SessionEngine(exercices=session_1, prenom="Léa")
    intro  = engine.debut_session()
    out    = engine.repondre(message_enfant)
    ...
    ok     = engine.exercice_suivant()   # True si avancé, False si dernier
    # Reconstruire depuis session_state :
    engine = SessionEngine.from_dict(st.session_state.session_active)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from jeu import recompenses
from pedagogie import mentor
from pedagogie.mentor import Exercice
from pedagogie.mentor_contract import EtatPedagogique, MentorOutput
from pedagogie.modes import MODES_ACTIFS, TRANSITIONS, Mode

_KICKOFF = (
    "[DÉBUT DE SESSION — message interne, non montré à l'enfant] "
    "L'enfant vient d'arriver et est prêt à commencer. "
    "Accueille-le chaleureusement par son prénom et ouvre la découverte "
    "avec une situation concrète, en posant une première question."
)

_MOTS_FIN = {"au revoir", "bye", "/fin", "fin", "stop", "j'ai fini", "j ai fini"}


class PhaseSession(str, Enum):
    DEBUT    = "debut"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"


@dataclass
class SessionEngine:
    exercices: list[Exercice]          # liste ordonnée des exercices de la session
    prenom: str = "Élévateur"
    situation_narrative: str = ""      # contexte narratif transmis au mentor à chaque appel
    mode: Mode = Mode.DECOUVERTE
    phase: PhaseSession = PhaseSession.DEBUT
    index_exercice: int = 0            # position courante dans la liste
    historique: list[dict] = field(default_factory=list)
    etat: EtatPedagogique = field(default_factory=EtatPedagogique)
    nb_tours_bilan: int = 0            # tours de dialogue en Mode BILAN (D-T8.1-F)
    ile_id: str = ""                   # île courante — requis pour gagner_cristal (D-T8.6-C)
    planche_key: str = ""              # ex. "c1" — identifie le cristal de la session

    # ------------------------------------------------------------------ #
    # Exercice courant                                                     #
    # ------------------------------------------------------------------ #

    @property
    def exercice_courant(self) -> Exercice:
        if not self.exercices:
            raise ValueError("SessionEngine initialisé sans exercices.")
        return self.exercices[self.index_exercice]

    @property
    def est_dernier_exercice(self) -> bool:
        return self.index_exercice >= len(self.exercices) - 1

    def exercice_suivant(self) -> bool:
        """Avance à l'exercice suivant dans l'ordre.

        Retourne True si l'avancement a eu lieu, False si on était déjà au
        dernier exercice. Réinitialise les compteurs de tentatives.
        L'appelant (ex. ecran_session) est responsable de déclencher cet appel
        au bon moment — la détection automatique de réussite sera ajoutée au
        Sprint 3.

        Accorde le cristal de la session (D-T8.6-C) — idempotent (T7), sans
        effet si ile_id/planche_key ne sont pas renseignés (ex. tests isolés).
        """
        if self.est_dernier_exercice:
            return False
        self.index_exercice += 1
        self.etat.concept_id = str(self.exercice_courant.get("id", ""))
        self.etat.nb_tentatives = 0
        self.etat.indices_utilises = 0
        if self.ile_id and self.planche_key:
            recompenses.gagner_cristal(self.ile_id, self.planche_key.upper())
        return True

    # ------------------------------------------------------------------ #
    # Interface publique                                                   #
    # ------------------------------------------------------------------ #

    def debut_session(self) -> MentorOutput:
        """Ouvre la session et génère le message d'accueil d'Archimède."""
        self.phase = PhaseSession.EN_COURS
        self.etat = EtatPedagogique(
            mode=self.mode,
            concept_id=str(self.exercice_courant.get("id", "")),
        )
        reponse = mentor.repondre(
            message=_KICKOFF,
            histoire=[],
            exercice=self.exercice_courant,
            mode=self.mode.value,
            prenom=self.prenom,
            situation_narrative=self.situation_narrative,
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
            exercice=self.exercice_courant,
            mode=self.mode.value,
            prenom=self.prenom,
            situation_narrative=self.situation_narrative,
        )

        self.historique.append({"role": "user",      "content": message})
        self.historique.append({"role": "assistant", "content": reponse})

        # Compteur BILAN — gating bouton Terminer chapitre (D-T8.1-F / D24)
        self.echanger_en_bilan()

        if message.strip().lower() in _MOTS_FIN:
            self.phase = PhaseSession.TERMINEE

        return MentorOutput(message=reponse, etat=self.etat)

    def echanger_en_bilan(self) -> None:
        """Incrémente nb_tours_bilan si on est en Mode BILAN (D-T8.1-F / D24)."""
        if self.mode == Mode.BILAN:
            self.nb_tours_bilan += 1

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
        """Historique sans le kickoff interne — à utiliser dans l'UI."""
        return [m for m in self.historique if m.get("content") != _KICKOFF]

    # ------------------------------------------------------------------ #
    # Propriétés                                                           #
    # ------------------------------------------------------------------ #

    @property
    def est_terminee(self) -> bool:
        return self.phase == PhaseSession.TERMINEE

    @property
    def objets_gagnes(self) -> int:
        """Nombre d'objets de collection encaissés dans la session courante.

        Règle de gain (spec collection, option b) : un objet est gagné quand
        l'enfant PASSE à l'exercice suivant — l'exercice en cours n'est pas
        encore acquis. Pendant l'exercice N (1-based), le compteur vaut N-1.

        Le dernier exercice n'a pas de « suivant » : exercice_suivant() y retourne
        False. Son objet est donc encaissé au passage en Mode.BILAN, qui marque
        la fin du parcours d'exercices. En fin de session, total = len(exercices).

        Valeur DÉRIVÉE de index_exercice et mode — aucun champ persistant, donc
        rien de plus à sérialiser et aucun risque de désynchronisation avec la
        progression réelle. Lecture seule : ne modifie aucun état.
        """
        gagnes = self.index_exercice + (1 if self.mode == Mode.BILAN else 0)
        return min(gagnes, len(self.exercices))

    # ------------------------------------------------------------------ #
    # Sérialisation pour st.session_state                                 #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "exercices":           self.exercices,
            "index_exercice":      self.index_exercice,
            "mode":                self.mode.value,
            "phase":               self.phase.value,
            "historique":          self.historique,
            "prenom":              self.prenom,
            "situation_narrative": self.situation_narrative,
            "nb_tours_bilan":      self.nb_tours_bilan,
            "ile_id":              self.ile_id,
            "planche_key":         self.planche_key,
            "etat": {
                "mode":             self.etat.mode.value,
                "concept_id":       self.etat.concept_id,
                "nb_tentatives":    self.etat.nb_tentatives,
                "indices_utilises": self.etat.indices_utilises,
            },
        }

    @classmethod
    def from_dict(cls, d: dict) -> SessionEngine:
        e = d.get("etat", {})
        engine = cls(
            exercices=d.get("exercices", []),
            prenom=d.get("prenom", "Élévateur"),
            situation_narrative=d.get("situation_narrative", ""),
            mode=Mode(d.get("mode", Mode.DECOUVERTE.value)),
            phase=PhaseSession(d.get("phase", PhaseSession.DEBUT.value)),
            index_exercice=d.get("index_exercice", 0),
            historique=d.get("historique", []),
            ile_id=d.get("ile_id", ""),
            planche_key=d.get("planche_key", ""),
        )
        engine.etat = EtatPedagogique(
            mode=Mode(e.get("mode", Mode.DECOUVERTE.value)),
            concept_id=e.get("concept_id", ""),
            nb_tentatives=e.get("nb_tentatives", 0),
            indices_utilises=e.get("indices_utilises", 0),
        )
        engine.nb_tours_bilan = d.get("nb_tours_bilan", 0)
        return engine
