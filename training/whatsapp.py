"""training/whatsapp.py – WhatsApp roleplay engine.

Simulates a WhatsApp conversation where the AI plays a realistic client
(vendeur/acquéreur) and the trainee responds as a real estate agent.

Scoring: 5 weighted criteria, each /10, total /100.
  score = sum(criterion_score_i × weight_i / 10) for all i
  weights sum to 100 → max score = 100
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from training.content import get_session_theme

# --- Constants ---
SCENARIOS_DIR = Path(__file__).resolve().parent / "scenarios"
DEFAULT_MAX_EXCHANGES = 5


# --- Data classes ---
@dataclass
class EvalCriterion:
    name: str
    description: str
    weight: int  # out of 100, all weights sum to 100

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EvalCriterion":
        return cls(
            name=d["name"],
            description=d["description"],
            weight=d["weight"],
        )


@dataclass
class Scenario:
    persona_name: str
    persona_role: str
    persona_context: str
    persona_tone: str
    opening_message: str
    max_exchanges: int
    evaluation_criteria: List[EvalCriterion]
    theme_tags: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Scenario":
        persona = d["persona"]
        return cls(
            persona_name=persona["name"],
            persona_role=persona["role"],
            persona_context=persona["context"],
            persona_tone=persona["tone"],
            opening_message=d["opening_message"],
            max_exchanges=d.get("max_exchanges", DEFAULT_MAX_EXCHANGES),
            evaluation_criteria=[
                EvalCriterion.from_dict(c)
                for c in d.get("evaluation_criteria", [])
            ],
            theme_tags=d.get("theme_tags", []),
        )


@dataclass
class WhatsAppMessage:
    role: str  # "client" or "agent"
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> "WhatsAppMessage":
        return cls(role=d["role"], content=d["content"])


@dataclass
class CriterionScore:
    name: str
    score: int  # 0-10
    weight: int
    comment: str

    def weighted_score(self) -> float:
        return self.score * self.weight / 10.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "weight": self.weight,
            "comment": self.comment,
            "weighted_score": self.weighted_score(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CriterionScore":
        return cls(
            name=d["name"],
            score=d["score"],
            weight=d["weight"],
            comment=d["comment"],
        )


@dataclass
class WhatsAppSession:
    """Full WhatsApp roleplay session state."""

    scenario: Scenario
    messages: List[WhatsAppMessage] = field(default_factory=list)
    is_terminated: bool = False
    evaluation: Optional[Dict[str, Any]] = None

    @property
    def exchange_count(self) -> int:
        """Count agent messages (each agent message = 1 exchange)."""
        return sum(1 for m in self.messages if m.role == "agent")

    @property
    def can_continue(self) -> bool:
        return (
            not self.is_terminated
            and self.exchange_count < self.scenario.max_exchanges
        )

    @property
    def can_terminate(self) -> bool:
        """Can terminate after at least 1 exchange."""
        return self.exchange_count >= 1

    def add_message(self, role: str, content: str) -> WhatsAppMessage:
        msg = WhatsAppMessage(role=role, content=content)
        self.messages.append(msg)
        return msg

    def terminate(self) -> None:
        self.is_terminated = True

    # --- serialization ---
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario": {
                "persona": {
                    "name": self.scenario.persona_name,
                    "role": self.scenario.persona_role,
                    "context": self.scenario.persona_context,
                    "tone": self.scenario.persona_tone,
                },
                "opening_message": self.scenario.opening_message,
                "max_exchanges": self.scenario.max_exchanges,
                "evaluation_criteria": [
                    {
                        "name": c.name,
                        "description": c.description,
                        "weight": c.weight,
                    }
                    for c in self.scenario.evaluation_criteria
                ],
                "theme_tags": self.scenario.theme_tags,
            },
            "messages": [m.to_dict() for m in self.messages],
            "is_terminated": self.is_terminated,
            "evaluation": self.evaluation,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WhatsAppSession":
        scenario = Scenario.from_dict(d["scenario"])
        return cls(
            scenario=scenario,
            messages=[WhatsAppMessage.from_dict(m) for m in d.get("messages", [])],
            is_terminated=d.get("is_terminated", False),
            evaluation=d.get("evaluation"),
        )


# --- Scenario loading ---
def _load_all_scenarios() -> List[Dict[str, Any]]:
    """Load all YAML scenario files."""
    scenarios = []
    if not SCENARIOS_DIR.exists():
        return scenarios
    for f in sorted(SCENARIOS_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            if data and "persona" in data:
                scenarios.append(data)
        except Exception:
            continue
    return scenarios


def _default_criteria() -> List[EvalCriterion]:
    return [
        EvalCriterion("Écoute et reformulation", "Reprend les mots du client, montre qu'il a compris", 25),
        EvalCriterion("Argumentation terrain", "Arguments concrets, basés sur des faits", 20),
        EvalCriterion("Traitement des objections", "Répond aux objections avec méthode et calme", 20),
        EvalCriterion("Posture et ton", "Ton professionnel, rassurant, pas de jargon inutile", 20),
        EvalCriterion("Closing / engagement", "Propose une prochaine étape claire", 15),
    ]


def _generic_scenario(theme_title: str) -> Scenario:
    """Fallback generic scenario when no YAML matches."""
    return Scenario(
        persona_name="M. Durand",
        persona_role="vendeur",
        persona_context=f"Vendeur particulier qui souhaite discuter de : {theme_title}",
        persona_tone="direct, un peu méfiant, phrases courtes",
        opening_message="Bonjour, j'ai vu votre annonce. On m'a dit que vous pourriez m'aider.",
        max_exchanges=DEFAULT_MAX_EXCHANGES,
        evaluation_criteria=_default_criteria(),
        theme_tags=[],
    )


def select_scenario(theme_title: str, tone_override: Optional[str] = None) -> Scenario:
    """Select a scenario matching the given theme, or random fallback.

    Args:
        theme_title: Theme to match against scenario theme_tags.
        tone_override: If provided, overrides the persona tone (from profile adapter).
    """
    all_scenarios = _load_all_scenarios()
    if not all_scenarios:
        scenario = _generic_scenario(theme_title)
        if tone_override:
            scenario.persona_tone = tone_override
        return scenario

    matched = [s for s in all_scenarios if theme_title in s.get("theme_tags", [])]
    if matched:
        scenario = Scenario.from_dict(random.choice(matched))
    else:
        scenario = Scenario.from_dict(random.choice(all_scenarios))

    if tone_override:
        scenario.persona_tone = tone_override
    return scenario


# --- Client AI ---
def build_client_system_prompt(scenario: Scenario, rag_context: str) -> str:
    """Build system prompt for the AI playing the client."""
    return (
        f"Tu joues {scenario.persona_name}, {scenario.persona_role}.\n"
        f"Contexte : {scenario.persona_context}\n"
        f"Ton de base : {scenario.persona_tone}\n\n"

        "RÈGLES DU JEU :\n"
        "- Reste STRICTEMENT dans ton rôle de client particulier\n"
        "- Messages courts (1 à 3 phrases), comme un vrai WhatsApp\n"
        "- Langage simple, zéro jargon immobilier\n"
        "- Ne dis jamais que tu es une IA\n\n"

        "VARIABILITÉ ÉMOTIONNELLE :\n"
        "Tu n'es PAS un script linéaire. Selon le contexte et le comportement de l'agent :\n"
        "- Si l'agent écoute bien → tu t'ouvres progressivement\n"
        "- Si l'agent te presse ou insiste lourdement → tu deviens plus fermé, évasif\n"
        "- Si l'agent te rassure → tu poses plus de questions\n"
        "- Si l'agent est vague → tu exprimes de la méfiance\n\n"

        "OBJECTIONS RÉALISTES :\n"
        "Tes objections ne sont pas toujours frontales. Tu peux :\n"
        "- Être évasif : 'Je vais réfléchir...', 'J'en parle à mon conjoint d'abord'\n"
        "- Temporiser : 'Je ne suis pas pressé', 'On verra ça plus tard'\n"
        "- Exprimer un doute subtil : 'Vous dites ça à tout le monde ?'\n"
        "- Poser une contre-question au lieu de répondre directement\n"
        "- Montrer de l'intérêt puis hésiter : 'Oui mais...' ou 'Ça a l'air bien, sauf que...'\n\n"

        "IMPRÉVISIBILITÉ :\n"
        "- Ne suis pas toujours la même progression\n"
        "- Parfois tu poses une question inattendue\n"
        "- Parfois tu reviens sur un point déjà évoqué\n"
        "- Tes réactions varient selon comment l'agent se comporte\n\n"

        f"CONTEXTE FORMATION (pour rester réaliste) :\n{rag_context}\n"
    )


def generate_client_reply(
    scenario: Scenario,
    messages: List[WhatsAppMessage],
    rag_context: str,
    chat_complete_fn: Callable,
) -> str:
    """Generate the next client reply using the LLM."""
    system_prompt = build_client_system_prompt(scenario, rag_context)

    conversation = ""
    for msg in messages:
        label = scenario.persona_name if msg.role == "client" else "Agent"
        conversation += f"{label} : {msg.content}\n"

    user_prompt = (
        f"Voici la conversation WhatsApp jusqu'ici :\n{conversation}\n"
        "Réponds comme le client, en une à trois phrases courtes. "
        "Reste dans ton rôle."
    )

    reply = chat_complete_fn(system_prompt, user_prompt, temperature=0.7)
    return reply.strip()


# --- Evaluation ---
def evaluate_conversation(
    scenario: Scenario,
    messages: List[WhatsAppMessage],
    rag_context: str,
    chat_complete_fn: Callable,
) -> Dict[str, Any]:
    """Evaluate the trainee's performance on 5 weighted criteria.

    Returns dict with: criteria, total_score (/100), debrief, suggestions.
    """
    criteria = scenario.evaluation_criteria
    if not criteria:
        criteria = _default_criteria()

    transcript = ""
    for msg in messages:
        label = scenario.persona_name if msg.role == "client" else "Agent (stagiaire)"
        transcript += f"{label} : {msg.content}\n"

    criteria_desc = "\n".join(
        f"- {c.name} (poids {c.weight}/100) : {c.description}"
        for c in criteria
    )

    # Adapter le vocabulaire vendeur vs acquéreur
    role_lower = scenario.persona_role.lower()
    if any(w in role_lower for w in ("vendeur", "vendeuse", "propriétaire")):
        role_context = (
            "Le client est un VENDEUR. L'objectif du stagiaire est d'obtenir un mandat "
            "de vente, valoriser ses services, rassurer sur le processus de vente.\n"
            "Vocabulaire attendu : mandat, estimation, mise en vente, prix de vente, "
            "promotion du bien, visites acquéreurs."
        )
    else:
        role_context = (
            "Le client est un ACQUÉREUR. L'objectif du stagiaire est de qualifier "
            "le projet d'achat, proposer des biens adaptés, accompagner vers l'offre.\n"
            "Vocabulaire attendu : recherche, budget, visite, offre d'achat, financement."
        )

    system_prompt = (
        "Tu es un formateur senior terrain en vente immobilière.\n"
        "Tu évalues une conversation WhatsApp de simulation entre un stagiaire (agent) "
        f"et un client ({scenario.persona_role}).\n\n"
        f"CONTEXTE RÔLE :\n{role_context}\n\n"
        "Tu dois :\n"
        "1. Évaluer chaque critère sur 10 avec un commentaire court (1 phrase terrain).\n"
        "2. Donner un débrief global (3-5 lignes) : points forts, axes d'amélioration.\n"
        "3. Proposer 2-3 formulations que le stagiaire AURAIT PU DIRE "
        "(section 'Ce que tu aurais pu dire').\n\n"
        "IMPORTANT : Adapte ton vocabulaire au rôle du client (vendeur OU acquéreur). "
        "Ne confonds JAMAIS les deux.\n\n"
        "Base-toi sur les extraits de formation pour juger la qualité des réponses.\n"
        "Sois bienveillant mais exigeant. Style terrain, pas académique."
    )

    user_prompt = (
        f"Contexte : {scenario.persona_context}\n\n"
        f"Extraits de formation (RAG) :\n{rag_context}\n\n"
        f"Transcription WhatsApp :\n{transcript}\n\n"
        f"Critères d'évaluation :\n{criteria_desc}\n\n"
        "Réponds EXACTEMENT dans ce format :\n"
        "CRITÈRES :\n"
    )

    for c in criteria:
        user_prompt += f"- {c.name} : [note]/10 — [commentaire 1 phrase]\n"

    user_prompt += (
        "\nDÉBRIEF :\n[3-5 lignes terrain]\n\n"
        "CE QUE TU AURAIS PU DIRE :\n"
        "- [formulation 1]\n"
        "- [formulation 2]\n"
        "- [formulation 3 optionnelle]\n"
    )

    raw = chat_complete_fn(system_prompt, user_prompt, temperature=0.2)
    return _parse_evaluation(raw, criteria)


def _parse_evaluation(
    raw: str, criteria: List[EvalCriterion],
) -> Dict[str, Any]:
    """Parse LLM evaluation output into structured data."""
    criterion_scores = []
    for c in criteria:
        score = 5  # default if parsing fails
        comment = ""
        for line in raw.split("\n"):
            if c.name.lower() in line.lower() and "/10" in line:
                match = re.search(r"(\d+)\s*/\s*10", line)
                if match:
                    score = min(10, max(0, int(match.group(1))))
                parts = line.split("\u2014")  # em dash
                if len(parts) > 1:
                    comment = parts[-1].strip()
                elif ":" in line:
                    after_score = line.split("/10")[-1].strip()
                    comment = after_score.lstrip("\u2014-: ").strip()
                break

        criterion_scores.append(CriterionScore(
            name=c.name,
            score=score,
            weight=c.weight,
            comment=comment,
        ))

    total_score = round(sum(cs.weighted_score() for cs in criterion_scores))

    # Extract debrief and suggestions sections
    debrief = ""
    suggestions = ""
    raw_upper = raw.upper()

    debrief_idx = raw_upper.find("DÉBRIEF")
    if debrief_idx == -1:
        debrief_idx = raw_upper.find("DEBRIEF")

    suggestions_idx = raw_upper.find("CE QUE TU AURAIS")
    if suggestions_idx == -1:
        suggestions_idx = raw_upper.find("TU AURAIS PU")

    if debrief_idx != -1:
        end = suggestions_idx if suggestions_idx != -1 else len(raw)
        debrief_block = raw[debrief_idx:end].strip()
        lines = debrief_block.split("\n")
        debrief = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    if suggestions_idx != -1:
        suggestions_block = raw[suggestions_idx:].strip()
        lines = suggestions_block.split("\n")
        suggestions = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    return {
        "criteria": [cs.to_dict() for cs in criterion_scores],
        "total_score": total_score,
        "debrief": debrief,
        "suggestions": suggestions,
    }


# --- Session helpers ---
def get_previous_theme_title(session_number: int) -> str:
    """Get the theme title from the previous session (for WhatsApp J+1)."""
    if session_number <= 1:
        return get_session_theme(1)["titre"]
    return get_session_theme(session_number - 1)["titre"]


def create_whatsapp_session(
    theme_title: str,
    tone_override: Optional[str] = None,
) -> WhatsAppSession:
    """Create a new WhatsApp session with a scenario matching the theme.

    Args:
        theme_title: Theme to match.
        tone_override: Optional tone override from profile adapter.
    """
    scenario = select_scenario(theme_title, tone_override=tone_override)
    ws = WhatsAppSession(scenario=scenario)
    ws.add_message("client", scenario.opening_message.strip())
    return ws
