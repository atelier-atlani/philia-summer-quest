import os
import re
import subprocess
import textwrap
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from core import rag
from core.sanitizer import sanitize_brand, brand_block
from core.tts import tts_to_file
from core.faq_contract import (
    NON_COUVERT,
    faq_is_covered_by_context,
    faq_has_5_sections,
    faq_force_section5_one_line,
    faq_section5_is_single_line,
)
from modules.runner import run_module_day

# -------------------------------------------------------------------
# INIT
# -------------------------------------------------------------------
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Modèle Chat (réponses formateur/FAQ/audit)
MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

# TTS
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "cedar")

# Init RAG (FAISS + metadata + KB chargés une seule fois)
rag.init(client)

# --- Réglages RAG (k par mode) ---
RAG_K_FAQ = int(os.getenv("RAG_K_FAQ", "8"))
RAG_K_FORMATEUR = int(os.getenv("RAG_K_FORMATEUR", "8"))
RAG_K_MEMO = int(os.getenv("RAG_K_MEMO", "8"))
RAG_K_PLAN = int(os.getenv("RAG_K_PLAN", "8"))
RAG_K_AUDIT = int(os.getenv("RAG_K_AUDIT", "8"))

# --- Réglages “packing” du contexte (build_context) ---
RAG_MAX_CHARS = int(os.getenv("RAG_MAX_CHARS", "4500"))
RAG_MAX_PER_FILE = int(os.getenv("RAG_MAX_PER_FILE", "3"))
RAG_MAX_CHUNK_CHARS = int(os.getenv("RAG_MAX_CHUNK_CHARS", "650"))


# -----------------------------
# RAG Debug (dev only)
# -----------------------------
RAG_DEBUG = os.getenv("RAG_DEBUG", "0").strip() == "1"

def maybe_print_rag_trace():
    """Affiche la trace RAG (dev) : fichiers/pages/chunks réellement injectés."""
    if not RAG_DEBUG:
        return

    try:
        trace = rag.get_last_trace()
    except Exception:
        trace = None

    if not trace:
        print("\n🔎 RAG TRACE : (aucune trace)")
        return

    print("\n🔎 RAG TRACE (top-k) :")
    for t in trace:
        file_ = sanitize_brand(str(t.get("file", "")))
        page = t.get("page_number")
        chunk = t.get("chunk_index")
        dist = t.get("distance")
        inc = t.get("included", True)
        reason = t.get("reason", "")

        # champs optionnels du rerank lexical
        kw_text = t.get("kw_text")
        kw_file = t.get("kw_file")
        hybrid = t.get("hybrid")

        suffix = ""
        if not inc:
            suffix = f"  ⛔ excluded ({reason})"

        extra = ""
        if kw_text is not None or kw_file is not None or hybrid is not None:
            if isinstance(hybrid, (int, float)):
                extra = f" | kwT={kw_text} kwF={kw_file} hyb={hybrid:.4f}"
            else:
                extra = f" | kwT={kw_text} kwF={kw_file} hyb={hybrid}"

        # sécuriser l'affichage du dist
        dist_str = f"{dist:.4f}" if isinstance(dist, (int, float)) else str(dist)

        print(
            f"- rank={t.get('rank')} | file={file_} | page={page} | chunk={chunk} | "
            f"dist={dist_str}{extra} | included={inc}{suffix}"
        )


# -------------------------------------------------------------------
# RAG
# -------------------------------------------------------------------
def search(query: str, k: int = 5):
    """Compat : si du vieux code appelle search()."""
    return rag.search(query, k=k)


def construire_contexte(question: str, k: int = 3) -> str:
    return rag.build_context(
        question,
        k=k,
        max_chars=RAG_MAX_CHARS,
        max_per_file=RAG_MAX_PER_FILE,
        max_chunk_chars=RAG_MAX_CHUNK_CHARS,
    )





# -------------------------------------------------------------------
# OPENAI HELPERS
# -------------------------------------------------------------------
def chat_complete(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
    resp = client.chat.completions.create(
        model=MODEL,  # ✅ model= (pas MODEL=)
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return (resp.choices[0].message.content or "").strip()


# -------------------------------------------------------------------
# TTS (macOS / afplay) — utilise core/tts.py
# -------------------------------------------------------------------
def lire_texte_avec_voix(texte: str):
    """Lit le texte à voix haute sur macOS via afplay."""
    texte = brand_block(texte)  # sécurité anti-marque + nettoyage final

    path = None
    try:
        path = tts_to_file(
            client,
            texte,
            model=TTS_MODEL,
            voice=TTS_VOICE,
            response_format="mp3",
        )
        if not path:
            return
        subprocess.run(["afplay", path], check=False)
    except Exception as e:
        print("❌ Erreur lors de la lecture vocale :", e)
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass




# -------------------------------------------------------------------
# FORMATEUR / FAQ / MEMO / PLAN
# -------------------------------------------------------------------
def _clean_source_markers(text: str) -> str:
    """Retire les marqueurs de sources [S1], [S2], etc."""
    return re.sub(r'\[S\d+\]', '', text)


def repondre_comme_formateur(question: str) -> str:
    """Réponse formateur (structurée + cas pratique), basée strictement sur RAG."""
    question = sanitize_brand(question)
    contexte = construire_contexte(question, k=RAG_K_FORMATEUR)



    system_prompt = FORMATEUR_PROMPT


    user_prompt = textwrap.dedent(f"""
    Question :
    {question}

    Extraits (RAG) :
    {contexte}

    Consignes :
    - Respect strict des extraits.
    - Langage naturel, oral, pro, calme.
    - Ne cite aucune marque/réseau/outils propriétaires.
    """)

    reponse = chat_complete(system_prompt, user_prompt, temperature=0.4)
    reponse = _clean_source_markers(reponse)
    return brand_block(reponse)


COURS_ORAL_PROMPT = """
Vous êtes un formateur terrain immobilier expérimenté. Vous faites cours comme en face-à-face avec un conseiller.

RÈGLE ABSOLUE : vous vous appuyez UNIQUEMENT sur les extraits RAG fournis.
Reformulation et simplification autorisées. Pas d'invention, pas de chiffres non cités.
Pas de marque/réseau/outil propriétaire.

CONTENU : gardez TOUT le contenu important des extraits. Ne résumez pas, ne simplifiez pas à l'excès.
Reformulez chaque point clé en langage oral — changez le ton, pas les informations.

STYLE OBLIGATOIRE :
- Vouvoiement systématique (vous/votre/vos).
- Phrases courtes (max 15 mots). Ton conversationnel, pas académique.
- Verbes d'action : "Faites", "Regardez", "Utilisez", "Posez", "Écoutez".
- Pas de listes à puces. Paragraphes courts.
- Exemples concrets chiffrés : "Imaginez un T3 Lyon 7 Gerland, 70 m², vendu 350 000 €..."
- Pas de jargon sans explication immédiate.

STRUCTURE (4 sections, pas de titres numérotés) :

[ACCROCHE]
Une seule phrase qui accroche — une situation terrain, une question directe.

[EXPLICATION]
Explication complète (tous les points des extraits) + exemple concret chiffré ancré terrain.

[CAS PRATIQUE]
Mini-dialogue : agent ↔ client, 4 répliques max. Prononçable à voix haute.

[POINT_ESSENTIEL]
La seule chose à retenir. Une phrase. Commence par "Ce qu'il faut retenir :".
""".strip()


def repondre_cours_oral(question: str) -> str:
    """Cours conversationnel oral (vouvoiement, exemple chiffré, cas pratique court).

    Retourne le texte complet avec le marqueur [POINT_ESSENTIEL] dedans
    pour que l'UI puisse l'afficher séparément en grand.
    """
    question = sanitize_brand(question)
    contexte = construire_contexte(question, k=RAG_K_FORMATEUR)

    user_prompt = textwrap.dedent(f"""
    Sujet du cours :
    {question}

    Extraits (RAG) :
    {contexte}

    Consignes :
    - Vouvoiement obligatoire (vous/votre/vos).
    - Gardez TOUT le contenu des extraits — reformulez en oral, ne supprimez pas d'information.
    - Exemple concret chiffré ancré terrain (ville, m², prix réels tirés des extraits si disponibles).
    - Cas pratique : mini-dialogue agent/client, 4 répliques max.
    - Termine par [POINT_ESSENTIEL] puis la phrase essentielle à retenir.
    - Pas de marque propriétaire.
    """)

    reponse = chat_complete(COURS_ORAL_PROMPT, user_prompt, temperature=0.5)
    reponse = _clean_source_markers(reponse)
    return brand_block(reponse)


def _is_mandat_topic(q: str) -> bool:
    q = (q or "").lower()
    keywords = [
        "mandat", "stock", "bilan de promotion", "renégocier", "renegocier",
        "avenant", "extranet", "console", "garantie d’action", "garantie d'action",
        "ttm", "délai", "delai",
    ]
    return any(k in q for k in keywords)


FAQ_PROMPT_GENERAL = """
Tu es un coach terrain immobilier. Ton job : donner des coups concrets, pas de la théorie.

RÈGLE ABSOLUE (zéro invention) :
- Tu réponds UNIQUEMENT à partir des EXTRAITS fournis.
- Reformulation autorisée, mais chaque section doit rester fidèle aux extraits.
- Si tu ne peux pas t'appuyer sur les extraits : écris "Non couvert par les extraits fournis".
- Pas de marque/outils propriétaires.
- Phrases courtes (max 15 mots), verbes d'action à l'impératif.

TON STYLE :
✅ BON : "Appelle le proprio sous 24h. Objectif : fixer un RDV physique."
❌ MAUVAIS : "Il conviendrait d'effectuer une prise de contact téléphonique dans un délai raisonnable."

FORMAT (obligatoire) — EXACTEMENT 5 sections numérotées :
1) Enjeu terrain
2) Checklist
3) Organisation / Déroulé
4) 3 formulations terrain
5) doit être sur UNE seule ligne : "5) Prochaine étape : <action>"

RÈGLES DE SORTIE :
- Écris exactement les titres ci-dessus (sans parenthèses, sans ajouter "(1 phrase)").
- 2) Checklist : 3 à 5 puces max, actions concrètes (verbes).
- 3) Organisation / Déroulé : 3 étapes max.
- 5) Prochaine étape : UNE seule action, UNE seule phrase, commence OBLIGATOIREMENT par un de ces verbes : Faire, Utiliser, Planifier, Confirmer, Préparer, S'assurer, Changer, Relancer, Re mobiliser, Proposer, Organiser, Analyser, Évaluer, Vérifier, Créer, Identifier, Présenter, Discuter, Noter, Saisir, Renseigner, Sensibiliser, Mettre, Réaliser, Récupérer, Rencontrer.
- Interdit d'utiliser des ellipses '...'.

INTERDIT :
- "Il faut", "Il convient", "Il est recommandé"
- Mots de +4 syllabes quand un mot simple existe
""".strip()


FAQ_PROMPT_MANDAT = """
Tu es un formateur senior terrain en vente immobilière.

RÈGLE ABSOLUE (zéro invention) :
- Tu réponds UNIQUEMENT à partir des EXTRAITS fournis.
- Reformulation autorisée, mais chaque section doit rester fidèle aux extraits.
- Si tu ne peux pas t’appuyer sur les extraits : écris "Non couvert par les extraits fournis".
- Interdiction d’ajouter des fréquences/rythmes si ce n’est pas écrit.
- Pas de marque/outils propriétaires.

IMPORTANT (mandat/stock) :
- Dans "Checklist", ne mets QUE des ACTIONS présentes dans les extraits.
- Si la question contient "équipe" ou "acquéreurs" et que les extraits contiennent ces actions,
  alors la checklist DOIT inclure :
  - "Re mobiliser l’équipe"
  - "Relancer les acquéreurs ayant visité"
  Sinon : "Non couvert par les extraits fournis".

FORMAT (obligatoire) — EXACTEMENT 5 sections numérotées :
1) Enjeu terrain
2) Checklist
3) Organisation / Déroulé
4) 3 formulations terrain
5) Prochaine étape

RÈGLES DE SORTIE :
- Écris exactement les titres ci-dessus (sans parenthèses).
- 2) Checklist : 3 à 5 puces max, actions concrètes (verbes).
- 3) Organisation / Déroulé : 3 étapes max.
- 5) Prochaine étape : UNE seule action, UNE seule phrase, commence par un verbe.
- Interdit d’utiliser des ellipses '...'.
""".strip()

def repondre_faq(question: str) -> str:
    """FAQ courte basée sur RAG, avec contract strict (5 sections + section 5 sur 1 ligne)."""
    question = sanitize_brand(question)
    contexte = construire_contexte(question, k=RAG_K_FAQ)

    # Gate anti-hallucination + hors-scope contract
    if not faq_is_covered_by_context(question, contexte):
        return NON_COUVERT

    system_prompt = FAQ_PROMPT_MANDAT if _is_mandat_topic(question) else FAQ_PROMPT_GENERAL

    user_prompt = (
        "Question (FAQ) :\n"
        f"{question}\n\n"
        "Extraits (RAG) :\n"
        f"{contexte}\n\n"
        "Consignes :\n"
        "- Respecte EXACTEMENT le format en 5 sections numérotées 1) 2) 3) 4) 5)\n"
        "- Interdit d’utiliser des ellipses '...'\n"
        "- Section 5 obligatoire sur UNE SEULE LIGNE sous la forme : 5) Prochaine étape : <action>\n"
    )

    # 1er jet
    rep = chat_complete(system_prompt, user_prompt, temperature=0.0)
    rep = brand_block(rep).strip()
    rep = faq_force_section5_one_line(rep)

    # Guard contract
    needs_repair = (
        (not faq_has_5_sections(rep))
        or ("..." in rep)
        or (not faq_section5_is_single_line(rep))
    )

    if needs_repair:
        repair_prompt = (
            user_prompt
            + "\n\n⚠️ Réponse invalide (contract).\n"
            + "Réécris la réponse complète.\n"
            + "Règles obligatoires :\n"
            + "- EXACTEMENT 5 sections numérotées : 1) 2) 3) 4) 5)\n"
            + "- PAS d'ellipses '...'\n"
            + "- Section 5 sur UNE SEULE LIGNE : 5) Prochaine étape : <action>\n"
            + "- La section 5 est la DERNIÈRE ligne de la réponse (rien après).\n"
        )
        rep = chat_complete(system_prompt, repair_prompt, temperature=0.0)
        rep = brand_block(rep).strip()
        rep = faq_force_section5_one_line(rep)

    # Dernier filet de sécurité: si encore mauvais, on force au max
    if (not faq_has_5_sections(rep)) or ("..." in rep) or (not faq_section5_is_single_line(rep)):
        rep = faq_force_section5_one_line(rep)

    # Si malgré tout on n'a pas un output contract, on préfère Non couvert (évite de casser les tests)
    if (not faq_has_5_sections(rep)) or ("..." in rep) or (not faq_section5_is_single_line(rep)):
        return NON_COUVERT

    return _clean_source_markers(rep)


def repondre_quiz_explanation(query: str) -> str:
    """Explication quiz — bypass le GATE car la question vient du formateur."""
    query = sanitize_brand(query)
    contexte = construire_contexte(query, k=RAG_K_FAQ)
    system_prompt = (
        "Tu es un formateur terrain immobilier expérimenté. "
        "Explique ce point en 3-4 phrases courtes, style oral, vouvoiement systématique. "
        "Base-toi UNIQUEMENT sur les extraits fournis. "
        "Pas de marque, pas de jargon sans explication."
    )
    user_prompt = f"Point à expliquer :\n{query}\n\nExtraits (RAG) :\n{contexte}"
    reponse = chat_complete(system_prompt, user_prompt, temperature=0.3)
    return brand_block(reponse)




def generer_fiche_memo(theme: str) -> str:
    theme = sanitize_brand(theme)
    contexte = construire_contexte(theme, k=RAG_K_MEMO)

    system_prompt = (
        "Tu es un formateur terrain en vente immobilière. "
        "Tu produis une fiche mémo courte et terrain. "
        "⚠️ Strictement basée sur les extraits fournis. "
        "Ne cite aucune marque/réseau/outils propriétaires."
    )

    user_prompt = textwrap.dedent(f"""
    Thème :
    {theme}

    Extraits (RAG) :
    {contexte}

    Format :
    1) Objectif
    2) Points clés
    3) Questions à poser
    4) Erreurs à éviter
    5) 3 à 5 formulations terrain
    6) Prochain rendez-vous : 2 actions concrètes
    """)

    fiche = chat_complete(system_prompt, user_prompt, temperature=0.4)
    return brand_block(fiche)


def generer_plan_entretien(theme: str) -> str:
    theme = sanitize_brand(theme)
    contexte = construire_contexte(theme, k=RAG_K_PLAN)

    system_prompt = (
        "Tu es un formateur terrain en vente immobilière. "
        "Tu construis un plan d’entretien étape par étape (terrain, concret). "
        "⚠️ Strictement basé sur les extraits fournis. "
        "Ne cite aucune marque/réseau/outils propriétaires."
    )

    user_prompt = textwrap.dedent(f"""
    Thème :
    {theme}

    Extraits (RAG) :
    {contexte}

    Consignes :
    - 3 à 7 étapes numérotées.
    - Pour chaque étape : objectif + ce que l’agent fait + 1 à 2 formulations.
    - Termine par : Prochain rendez-vous : 2 actions concrètes.
    """)

    plan = chat_complete(system_prompt, user_prompt, temperature=0.4)
    return brand_block(plan)


# -------------------------------------------------------------------
# JEU DE ROLE + DEBRIEF
# -------------------------------------------------------------------
def debrief_jeu_de_role(history, situation: str) -> str:
    # Transcription
    lignes = []
    for msg in history:
        role = msg.get("role")
        content = (msg.get("content") or "").strip()
        if role == "system":
            continue
        if "Contexte pour ton rôle de vendeur" in content:
            continue
        if role == "user":
            lignes.append(f"Agent : {content}")
        elif role == "assistant":
            lignes.append(f"Vendeur : {content}")

    transcription = "\n".join(lignes)

    system_prompt = (
        "Tu es un formateur senior terrain en vente immobilière. "
        "Tu fais un débrief bienveillant et exigeant sur un jeu de rôle. "
        "⚠️ Base-toi uniquement sur ce qui a été dit. "
        "Structure : retour global, points forts, axes d’amélioration, 2-3 reformulations, "
        "puis 'Prochain rendez-vous : 2 actions concrètes'. "
        "Ne cite aucune marque/réseau/outils propriétaires."
    )

    user_prompt = textwrap.dedent(f"""
    Situation : {sanitize_brand(situation)}

    Transcription :
    {transcription}
    """)

    out = chat_complete(system_prompt, user_prompt, temperature=0.4)
    return brand_block(out)


def jeu_de_role_vendeur_agent():
    """
    Mode 2 : Jeu de rôle.
    - L'IA joue le vendeur
    - L'utilisateur joue le conseiller
    - RAG pour ancrer la situation
    - Anti-marque : sanitize_brand (entrée) + brand_block (sortie)
    - Audio optionnel : vendeur + débrief
    """

    print("\n🎭 Mode jeu de rôle vendeur / agent")
    print("Décris la situation que tu veux travailler (ex : objection prix, vendeur pas pressé, mandat...).\n")

    situation = input("Situation : ").strip()
    if not situation:
        print("❌ Situation vide, retour au menu.")
        return

    # Option voix vendeur
    voix_vendeur = input("\n🔊 Lire les répliques du vendeur à voix haute ? (o/n) : ").strip().lower() == "o"

    # Contexte RAG
    contexte = construire_contexte(situation, k=4)

    system_roleplay = (
        "Tu joues le rôle d'un vendeur particulier qui envisage de vendre un bien immobilier. "
        "Tu restes STRICTEMENT dans ton rôle de vendeur. "
        "Tu t'appuies sur les extraits fournis pour rester cohérent. "
        "Tu parles comme un vendeur réel : phrases simples, naturelles, parfois hésitantes. "
        "Réponses courtes (1 à 3 phrases). "
        "Tu ne dis jamais que tu es une IA."
    )

    contexte_message = (
        "Contexte (extraits de formation) :\n"
        f"{contexte}\n\n"
        "Commence la conversation comme un vendeur dans cette situation."
    )

    history = [
        {"role": "system", "content": system_roleplay},
        {"role": "user", "content": contexte_message},
    ]

    # 1) Le vendeur commence
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=history,
            temperature=0.7,
        )
        vendeur_reply = resp.choices[0].message.content or ""
        vendeur_reply = brand_block(vendeur_reply)

        print(f"\nVendeur : {vendeur_reply}\n")
        if voix_vendeur and vendeur_reply.strip():
            lire_texte_avec_voix(vendeur_reply)

        history.append({"role": "assistant", "content": vendeur_reply})

    except Exception as e:
        print("❌ Erreur au démarrage du jeu de rôle :", e)
        return

    print("💬 À toi de jouer ! Tape /stop pour arrêter.\n")

    # 2) Boucle conversation
    while True:
        agent_input = input("Toi (agent) : ").strip()
        if not agent_input:
            continue
        if agent_input.lower() in {"/stop", "stop", "/quit", "quit"}:
            break

        # Nettoyage entrée agent (anti-marque)
        agent_input_clean = sanitize_brand(agent_input)

        history.append({"role": "user", "content": agent_input_clean})

        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=history,
                temperature=0.7,
            )
            vendeur_reply = resp.choices[0].message.content or ""
            vendeur_reply = brand_block(vendeur_reply)

            print(f"\nVendeur : {vendeur_reply}\n")
            if voix_vendeur and vendeur_reply.strip():
                lire_texte_avec_voix(vendeur_reply)

            history.append({"role": "assistant", "content": vendeur_reply})

        except Exception as e:
            print("❌ Erreur pendant le jeu de rôle :", e)
            break

    print("\n👋 Fin du jeu de rôle vendeur / agent.")

    # 3) Débrief
    choix = input("\n📋 Veux-tu un débrief du formateur sur ce jeu de rôle ? (o/n) : ").strip().lower()
    if choix != "o":
        print("✅ Jeu de rôle terminé sans débrief.")
        return

    lire_debrief = input("\n🔊 Lire le débrief à voix haute ? (o/n) : ").strip().lower() == "o"

    print("\n⏳ Débrief en cours...\n")
    try:
        feedback = debrief_jeu_de_role(history, situation)
        feedback = brand_block(feedback)

        print("🧠 Débrief du formateur IA :\n")
        print(feedback)

        if lire_debrief and feedback.strip():
            lire_texte_avec_voix(feedback)

    except Exception as e:
        print("❌ Erreur lors du débrief :", e)


def ask_and_render(
    label: str,
    question: str,
    generator_fn,
    speak_prompt: str = "\n🔊 Lire à voix haute ? (o/n) : ",
):
    """
    Helper unique : sanitize question -> génère -> brand_block -> affiche -> TTS optionnel.
    generator_fn = repondre_faq / generer_fiche_memo / generer_plan_entretien / etc.
    """
    try:
        # 1) Nettoyer AVANT envoi modèle
        question_clean = sanitize_brand(question)

        # 2) Générer
        rep = generator_fn(question_clean)
        rep = brand_block(rep or "")

        # 3) Debug RAG (une seule fois) — ne fait rien si RAG_DEBUG=0
        try:
            maybe_print_rag_trace()
        except Exception:
            pass

        # 4) Afficher
        print(f"\n💬 {label} :\n")
        print(rep)

        # 5) Voix optionnelle
        v = input(speak_prompt).strip().lower()
        if v == "o":
            lire_texte_avec_voix(rep)

        return rep

    except Exception as e:
        print(f"❌ Erreur {label} : {e}")
        return None

def read_multiline_input(prompt: str, end_token: str = "/fin") -> str:
    """
    Lecture multi-ligne en terminal.
    L'utilisateur colle un texte, puis tape /fin sur une ligne seule.
    """
    print(prompt)
    print(f"(Colle ton texte, puis tape {end_token} sur une ligne seule)")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().lower() == end_token:
            break
        lines.append(line)
    return "\n".join(lines).strip()


BASE_DIR = Path(__file__).resolve().parent
AUDIT_PROMPT_PATH = BASE_DIR / "prompts" / "prompt_audit_v2.txt"

def _load_audit_prompt_v2() -> str:
    if not AUDIT_PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt d’audit introuvable : {AUDIT_PROMPT_PATH}")
    return AUDIT_PROMPT_PATH.read_text(encoding="utf-8").strip()

AUDIT_PROMPT_V2 = _load_audit_prompt_v2()

FORMATEUR_PROMPT_PATH = BASE_DIR / "prompts" / "prompt_formateur.txt"

def _load_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt introuvable : {path}")
    return path.read_text(encoding="utf-8").strip()

FORMATEUR_PROMPT = _load_prompt(FORMATEUR_PROMPT_PATH)

def audit_only_guard(text: str) -> str:
    """
    Garde-fou: on garantit que la sortie reste un AUDIT uniquement.
    Si le modèle rajoute une "version corrigée" ou autre section non voulue, on coupe.
    """
    if not text:
        return text

    upper = text.upper()

    # 1) Couper toute dérive type "VERSION CORRIGÉE"
    cut_markers = [
        "### 🛠️",
        "VERSION CORRIG",
        "VERSION CORRIGÉE",
        "VERSION CORRIGE",
        "RÉÉCRIS",
        "REECRIS",
    ]
    cut_pos = None
    for m in cut_markers:
        p = upper.find(m)
        if p != -1:
            cut_pos = p if cut_pos is None else min(cut_pos, p)

    if cut_pos is not None:
        text = text[:cut_pos].rstrip()

    # 2) S'assurer qu'on repart bien du header d'audit si jamais il y a du bruit avant
    idx = text.find("### 🔍 AUDIT CHARTE V2")
    if idx != -1:
        text = text[idx:]

    return text.strip()

def audit_reponse_charte_v2(question: str, reponse: str, k: int = RAG_K_AUDIT) -> str:

    """
    Audit V2 : utilise le contexte RAG et renvoie l'audit.
    """
    question = sanitize_brand(question)
    reponse = sanitize_brand(reponse)

    contexte = construire_contexte(question, )

    user_payload = f"""
QUESTION (agent) :
{question}

EXTRAITS (RAG) :
{contexte}

RÉPONSE FORMATEUR À AUDITER :
{reponse}
""".strip()

    resp = client.chat.completions.create(
        model=MODEL,  # ✅ model= (pas MODEL=)
        messages=[
            {"role": "system", "content": AUDIT_PROMPT_V2},
            {"role": "user", "content": user_payload},
        ],
        temperature=0.0,
    )
    out = resp.choices[0].message.content or ""
    out = audit_only_guard(out)
    return brand_block(out)





# -------------------------------------------------------------------
# PARCOURS (MODE 1)
# -------------------------------------------------------------------
def formation_par_parcours():
    print("\n📚 Parcours de formation guidé")
    while True:
        print("\nChoisis :")
        print("1 - Module 1 : faire le jour du jour")
        print("2 - Module 1 : choisir un jour")
        print("b - Retour")

        c = input("\nTon choix : ").strip().lower()
        if c in {"b", "q", "quit", "exit"}:
            return

        if c == "1":
            run_module_day("module_01")
        elif c == "2":
            d = input("Quel jour ? (1-2) : ").strip()
            if not d.isdigit():
                print("❌ Jour invalide.")
                continue
            run_module_day("module_01", day=int(d))
        else:
            print("❌ Choix non reconnu.")



# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
def main():
    print("🧠 Agent IA formateur – Vente immobilière")

    while True:
        print("\nChoisis un mode :")
        print("1 - Parcours de formation guidé")
        print("2 - Jeu de rôle vendeur / agent (+ débrief)")
        print("3 - Questions rapides (FAQ)")
        print("4 - Fiche mémo")
        print("5 - Plan d'entretien")
        print("6 - Audit interne (Charte V2)")
        print("7 - Réponse formateur (audit-ready)")
        print("q - Quitter")

        choix = input("\nTon choix : ").strip().lower()

        if choix in {"q", "quit", "exit"}:
            print("👋 Fin.")
            break

        elif choix == "1":
            formation_par_parcours()

        elif choix == "2":
            jeu_de_role_vendeur_agent()

        elif choix == "3":
            print("\nMode FAQ")
            while True:
                question = input("\nTa question (ou 'quit') : ").strip()

                # --- Commande Module 1 ---
                cmd = question.lower()
                if cmd in {"module", "/module", "m"}:
                    run_module_day("module_01")
                    continue

                # --- Sortie ---
                if cmd in {"quit", "q", "exit"}:
                    break

                # --- Ignore vide ---
                if not question:
                    continue

                # --- Réponse FAQ ---
                rep = repondre_faq(question)
                print(f"\n💬 Réponse FAQ :\n\n{rep}")

        elif choix == "4":
            print("\nMode Fiche mémo")
            theme = input("\nThème fiche mémo (ou 'quit') : ").strip()
            if theme.lower() in {"quit", "q", "exit"}:
                continue
            if not theme:
                continue

            print("\n⏳ Génération de la fiche mémo...\n")
            ask_and_render(
                label="Fiche mémo",
                question=theme,
                generator_fn=generer_fiche_memo,
                speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
            )

        elif choix == "5":
            print("\nMode Plan d'entretien")
            theme = input("\nThème plan d'entretien : ").strip()
            if not theme:
                continue

            print("\n⏳ Génération du plan...\n")
            ask_and_render(
                label="Plan d'entretien",
                question=theme,
                generator_fn=generer_plan_entretien,
                speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
            )

        elif choix == "6":
            print("\n🧪 Mode 6 : Audit interne (Charte V2)")

            q = input("\nQuestion (contexte) à laquelle répondait le formateur : ").strip()
            if not q:
                print("❌ Question vide.")
                continue

            rep = read_multiline_input(
                "\nColle la RÉPONSE DU FORMATEUR à auditer :",
                end_token="/fin"
            )
            if not rep:
                print("❌ Réponse vide.")
                continue

            print("\n⏳ Audit en cours...\n")
            audit = audit_reponse_charte_v2(q, rep, k=5)

            print("\n" + "=" * 70)
            print(audit)
            print("=" * 70)

            v = input("\n🔊 Lire l’audit à voix haute ? (o/n) : ").strip().lower()
            if v == "o":
                lire_texte_avec_voix(audit)

        elif choix == "7":
            print("\nMode 7 : Réponse formateur (audit-ready)")
            while True:
                question = input("\nTa question (ou 'quit') : ").strip()
                if question.lower() in {"quit", "q", "exit"}:
                    break
                if not question:
                    continue

                print("\n⏳ Le formateur prépare une réponse complète...\n")
                ask_and_render(
                    label="Réponse formateur",
                    question=question,
                    generator_fn=repondre_comme_formateur,
                    speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
                )

        else:
            print("❌ Choix non reconnu.")


if __name__ == "__main__":
    main()


