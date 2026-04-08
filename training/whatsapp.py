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
        opening_message="Bonjour, c'est M. Durand. J'ai vu votre annonce. On m'a dit que vous pourriez m'aider.",
        max_exchanges=DEFAULT_MAX_EXCHANGES,
        evaluation_criteria=_default_criteria(),
        theme_tags=[],
    )


def select_scenario(
    theme_title: str,
    tone_override: Optional[str] = None,
    session_number: int = 1,
    generated_data: Optional[Dict[str, Any]] = None,
) -> Scenario:
    """Select a scenario matching the given theme.

    Priority: 1) generated_data (LLM dynamic), 2) YAML tag match, 3) rotation fallback.

    Args:
        theme_title: Theme to match against scenario theme_tags.
        tone_override: If provided, overrides the persona tone (from profile adapter).
        session_number: Used for deterministic rotation across sessions.
        generated_data: Pre-generated scenario dict from wa_scenario_generator.
    """
    # Priorité 1 : scénario généré dynamiquement par LLM
    if generated_data and "persona" in generated_data:
        scenario = Scenario.from_dict(generated_data)
        if tone_override:
            scenario.persona_tone = tone_override
        return scenario

    # Priorité 2 : YAML statique avec tag correspondant
    all_scenarios = _load_all_scenarios()
    if not all_scenarios:
        scenario = _generic_scenario(theme_title)
        if tone_override:
            scenario.persona_tone = tone_override
        return scenario

    matched = [s for s in all_scenarios if theme_title in s.get("theme_tags", [])]
    pool = matched if matched else all_scenarios

    # Rotation déterministe par session
    scenario = Scenario.from_dict(pool[session_number % len(pool)])

    if tone_override:
        scenario.persona_tone = tone_override
    return scenario


# --- Difficulty instructions ---
_DIFFICULTY_INSTRUCTIONS: Dict[str, str] = {
    "facile": (
        "NIVEAU DÉBUTANT — CLIENT COLLABORATIF :\n"
        "- Tu es ouvert et bienveillant\n"
        "- Questions simples et directes\n"
        "- Tu acceptes facilement les arguments bien présentés\n"
        "- Maximum 1-2 objections légères pendant la conversation\n"
        "- Tu conclus positivement si l'agent te rassure\n"
    ),
    "moyen": (
        "NIVEAU CONFIRMÉ — CLIENT HÉSITANT :\n"
        "- Tu es intéressé mais prudent\n"
        "- Tu poses des questions plus précises\n"
        "- Tu as 2-3 objections réalistes à soulever\n"
        "- Tu veux être convaincu avant de t'engager\n"
        "- Tu conclus si l'agent démontre sa valeur ajoutée\n"
    ),
    "difficile": (
        "NIVEAU EXPERT — CLIENT EXIGEANT :\n"
        "- Tu es difficile et très sélectif\n"
        "- Objections subtiles et bien argumentées\n"
        "- Tu compares avec d'autres agences\n"
        "- Tu testes la réactivité et l'expertise de l'agent\n"
        "- Tu ne te satisfais pas de réponses génériques\n"
        "- Tu conclus uniquement si l'agent dépasse vraiment tes attentes\n"
    ),
}


# --- Client AI ---
def build_client_system_prompt(
    scenario: Scenario,
    rag_context: str,
    difficulty: str = "moyen",
) -> str:
    """Build system prompt for the AI playing the client.

    Args:
        scenario: WhatsApp scenario with persona details.
        rag_context: RAG context string for realism.
        difficulty: Client difficulty level — "facile", "moyen", or "difficile".
    """
    difficulty_block = _DIFFICULTY_INSTRUCTIONS.get(
        difficulty, _DIFFICULTY_INSTRUCTIONS["moyen"]
    )

    # Role-specific motivations to prevent vendeur/acquéreur confusion
    role_lower = scenario.persona_role.lower()
    is_vendeur = any(w in role_lower for w in ("vendeur", "vendeuse", "propriétaire"))
    is_acquereur = any(w in role_lower for w in ("acquéreur", "acquéreure", "acheteur", "acheteuse"))

    if is_vendeur:
        role_block = (
            "TON RÔLE : VENDEUR / PROPRIÉTAIRE\n"
            "- Ton objectif : vendre ton bien au MEILLEUR PRIX possible\n"
            "- Tu t'inquiètes si l'agent propose un prix TROP BAS\n"
            "- Tu veux savoir comment l'agent va VALORISER ton bien\n"
            "- Objections typiques : 'Vous trouvez pas que c'est un peu bas ?', "
            "'Mon voisin a vendu plus cher', 'J'ai fait des travaux, ça compte pas ?'\n"
            "- Tu es sensible à : stratégie de prix, photos pro, réseau acheteurs\n"
            "INTERDIT : ne dis jamais que le prix est 'trop élevé' (c'est un réflexe acquéreur).\n"
        )
    elif is_acquereur:
        role_block = (
            "TON RÔLE : ACQUÉREUR / ACHETEUR\n"
            "- Ton objectif : acheter un bien qui correspond à tes critères et ton budget\n"
            "- Tu t'inquiètes si le prix est TROP ÉLEVÉ pour ton budget\n"
            "- Tu veux savoir si c'est une bonne affaire\n"
            "- Objections typiques : 'C'est cher pour ce quartier', "
            "'Il y a des travaux à prévoir', 'Mon budget est serré'\n"
            "- Tu es sensible à : rapport qualité/prix, potentiel du bien, financement\n"
            "INTERDIT : ne dis jamais que le prix est 'trop bas' (c'est un réflexe vendeur).\n"
        )
    else:
        role_block = "Reste strictement cohérent avec ton rôle décrit dans ton contexte.\n"

    return (
        f"Tu joues {scenario.persona_name}, {scenario.persona_role}.\n"
        f"Contexte : {scenario.persona_context}\n"
        f"Ton de base : {scenario.persona_tone}\n\n"

        f"{role_block}\n"
        f"{difficulty_block}\n"

        "RÈGLES DU JEU :\n"
        "- Reste STRICTEMENT dans ton rôle de client particulier\n"
        "- Messages courts (1 à 3 phrases), comme un vrai WhatsApp\n"
        "- Langage simple, zéro jargon immobilier\n"
        "- Ne dis jamais que tu es une IA\n\n"

        "OUVERTURE DE CONVERSATION :\n"
        "- Le premier message est DÉJÀ envoyé (opening_message). Ne le répète pas.\n"
        "- Pour tes messages SUIVANTS : reste naturel, messages courts (1-3 phrases)\n\n"

        "CLÔTURE DE CONVERSATION :\n"
        "- Si l'agent propose un rendez-vous ou une prochaine étape et que tu es convaincu → accepte clairement\n"
        "  Exemple : 'D'accord, on fait comme ça. Merci pour vos explications.'\n"
        "- Si tu n'es pas convaincu → exprime-le poliment mais clairement\n"
        "  Exemple : 'Je vais réfléchir, je vous recontacte si besoin. Bonne journée.'\n"
        "- Ne laisse JAMAIS la conversation en suspens sans issue claire\n\n"

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
    difficulty: str = "moyen",
) -> str:
    """Generate the next client reply using the LLM."""
    system_prompt = build_client_system_prompt(scenario, rag_context, difficulty=difficulty)

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
        "Tu analyses une conversation WhatsApp de simulation entre un stagiaire (agent) "
        f"et un client ({scenario.persona_role}).\n\n"
        f"CONTEXTE RÔLE :\n{role_context}\n\n"
        "STRUCTURE OBLIGATOIRE EN 4 PARTIES :\n\n"
        "1) CRITÈRES : évalue chaque critère /10 avec 1 phrase terrain courte.\n"
        "2) MOMENTS CLÉS : identifie 2-3 moments importants de la conversation.\n"
        "   Pour chaque moment, montre ce que le stagiaire a dit et ce qu'il aurait pu dire.\n"
        "3) LACUNES DÉTECTÉES : liste les connaissances manquantes du stagiaire.\n"
        "4) ANCRAGE : 1 formulation terrain à retenir absolument.\n\n"
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
        "Réponds EXACTEMENT dans ce format :\n\n"
        "CRITÈRES :\n"
    )

    for c in criteria:
        user_prompt += f"- {c.name} : [note]/10 — [commentaire 1 phrase]\n"

    user_prompt += (
        "\nMOMENTS CLÉS :\n"
        "[Pour 2-3 moments importants]\n"
        "Stagiaire : '[ce qu'il a dit]'\n"
        "Mieux : '[ce qu'il aurait pu dire]' — [explication courte]\n\n"
        "LACUNES DÉTECTÉES :\n"
        "[Pour chaque lacune]\n"
        "Manque : [sujet précis]\n"
        "Point clé : [1 phrase concrète à retenir]\n\n"
        "ANCRAGE :\n"
        "À retenir : [1 formulation terrain courte et prononçable]\n"
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

    # Extract sections by header markers
    sections = _extract_sections(raw)

    return {
        "criteria": [cs.to_dict() for cs in criterion_scores],
        "total_score": total_score,
        "debrief": sections.get("moments_cles", ""),
        "suggestions": sections.get("ancrage", ""),
        "lacunes": _extract_lacunes(raw),
    }


def _extract_sections(raw: str) -> Dict[str, str]:
    """Extract named sections from LLM evaluation output."""
    raw_upper = raw.upper()

    # Section markers in order
    markers = [
        ("moments_cles", ["MOMENTS CLÉS", "MOMENTS CLES"]),
        ("lacunes", ["LACUNES DÉTECTÉES", "LACUNES DETECTEES", "LACUNES"]),
        ("ancrage", ["ANCRAGE"]),
    ]

    positions: list[tuple[str, int]] = []
    for key, variants in markers:
        for variant in variants:
            idx = raw_upper.find(variant)
            if idx != -1:
                positions.append((key, idx))
                break

    positions.sort(key=lambda x: x[1])

    sections: Dict[str, str] = {}
    for i, (key, start) in enumerate(positions):
        end = positions[i + 1][1] if i + 1 < len(positions) else len(raw)
        block = raw[start:end].strip()
        lines = block.split("\n")
        sections[key] = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    return sections


def _extract_lacunes(raw: str) -> list[str]:
    """Extract detected lacunes from evaluation output."""
    lacunes = re.findall(r'[Mm]anque\s*:\s*(.+)', raw)
    return [l.strip() for l in lacunes if l.strip()]


# --- Real-time performance analysis ---

def analyze_agent_message(message: str) -> Dict[str, int]:
    """Analyse a single agent message and return signed points per category."""
    msg_lower = message.lower()
    points: Dict[str, int] = {
        "ecoute_active": 0,
        "questions_ouvertes": 0,
        "arguments_concrets": 0,
        "gestion_objections": 0,
        "insistance_lourde": 0,
        "langage_pro": 0,
    }

    # Écoute active (+5 per marker, cap 10)
    ecoute_markers = [
        "je comprends", "je vois", "effectivement", "tout à fait", "d'accord",
        "bien sûr", "absolument", "je note", "vous avez raison", "c'est normal",
        "je vous écoute", "en effet", "parfaitement", "vous dites", "si je comprends bien",
    ]
    points["ecoute_active"] = min(10, sum(5 for m in ecoute_markers if m in msg_lower))

    # Questions ouvertes (+5 per marker, cap 15)
    question_markers = [
        "comment", "pourquoi", "qu'est-ce que", "quels sont", "parlez-moi",
        "pouvez-vous", "quel est", "que pensez", "qu'attendez", "avez-vous",
        "souhaitez-vous", "préférez-vous", "envisagez-vous", "?",
    ]
    points["questions_ouvertes"] = min(15, sum(5 for m in question_markers if m in msg_lower))

    # Arguments concrets (+5 per marker, cap 15)
    concrete_markers = [
        "euros", "jours", "semaines", "clients", "%", "m²",
        "rendez-vous", "estimation", "mandat", "visite", "comparaison",
        "marché", "prix", "vente", "offre", "acquéreur", "vendeur",
    ]
    points["arguments_concrets"] = min(15, sum(5 for m in concrete_markers if m in msg_lower))

    # Gestion objections (+20 si présent)
    objection_responses = [
        "justement", "au contraire", "c'est pourquoi", "précisément",
        "en revanche", "cependant", "néanmoins", "toutefois",
        "permettez-moi", "si vous le souhaitez", "je propose",
    ]
    if any(m in msg_lower for m in objection_responses):
        points["gestion_objections"] = 20

    # Insistance lourde (-20)
    insistance_markers = ["vous devez", "il faut absolument", "vous êtes obligé", "sinon vous"]
    if any(m in msg_lower for m in insistance_markers):
        points["insistance_lourde"] = -20

    # Langage pro : réponse structurée avec question (+10)
    if len(message.split()) > 15 and "?" in message:
        points["langage_pro"] = 10

    # Bonus longueur (réponse structurée)
    word_count = len(message.split())
    if word_count >= 20:
        points["langage_pro"] = max(points["langage_pro"], 10)
    if word_count >= 40:
        points["langage_pro"] = min(20, points["langage_pro"] + 10)

    return points


def _generate_contextual_advice(agent_msg: str, client_msg: str, score: int) -> str:
    """Return a short contextual coaching tip based on the last exchange."""
    agent_lower = agent_msg.lower()
    client_lower = client_msg.lower()

    if any(w in client_lower for w in ["mais", "cependant", "hésit", "réfléchir", "pas sûr"]):
        return "Le client hésite. Posez-lui une question pour comprendre ce qui le bloque."
    if "?" in client_msg:
        return "Le client pose une question. Répondez de façon précise et concrète."
    if "?" not in agent_msg and len(agent_msg.split()) > 10:
        return "Vous parlez beaucoup. Posez une question pour impliquer le client."
    if score < 40:
        return "Écoutez davantage, parlez moins. Posez des questions ouvertes pour relancer."
    if score < 70:
        return "Vous êtes bien parti. Maintenant, proposez une action concrète : RDV ou document."
    return "Excellent échange. Concluez maintenant sur un RDV ou un prochain contact."


def calculate_realtime_score(messages: List[WhatsAppMessage]) -> Dict[str, Any]:
    """Compute a 0-100 live performance score with contextual advice.

    Returns dict with: score (int), conseil (str), objectif (str).
    """
    agent_messages = [m for m in messages if m.role == "agent"]

    if len(messages) < 2 or not agent_messages:
        return {
            "score": 50,
            "conseil": "Commence par écouter les besoins du client.",
            "objectif": "Décrocher un RDV",
        }

    total_points = sum(
        sum(analyze_agent_message(m.content).values())
        for m in agent_messages
    )

    max_possible = 70 * len(agent_messages)
    score = max(20, min(100, 50 + int((total_points / max(max_possible, 1)) * 50)))

    last_agent = agent_messages[-1].content
    last_client_msg = next(
        (m for m in reversed(messages) if m.role == "client"), None
    )
    last_client = last_client_msg.content if last_client_msg else ""

    conseil = _generate_contextual_advice(last_agent, last_client, score)

    if score >= 70:
        objectif = "Décrocher un RDV confirmé"
    elif score >= 50:
        objectif = "Garder le contact (doc/rappel)"
    else:
        objectif = "Récupérer la situation"

    return {"score": score, "conseil": conseil, "objectif": objectif}


# --- Session helpers ---
def get_previous_theme_title(session_number: int) -> str:
    """Get the theme title from the previous session (for WhatsApp J+1)."""
    if session_number <= 1:
        return get_session_theme(1)["titre"]
    return get_session_theme(session_number - 1)["titre"]


def create_whatsapp_session(
    theme_title: str,
    tone_override: Optional[str] = None,
    session_number: int = 1,
    generated_data: Optional[Dict[str, Any]] = None,
) -> WhatsAppSession:
    """Create a new WhatsApp session with a scenario matching the theme.

    Args:
        theme_title: Theme to match.
        tone_override: Optional tone override from profile adapter.
        session_number: Used for deterministic scenario rotation.
        generated_data: Pre-generated scenario dict (from wa_scenario_generator).
    """
    scenario = select_scenario(
        theme_title,
        tone_override=tone_override,
        session_number=session_number,
        generated_data=generated_data,
    )
    ws = WhatsAppSession(scenario=scenario)
    ws.add_message("client", scenario.opening_message.strip())
    return ws
