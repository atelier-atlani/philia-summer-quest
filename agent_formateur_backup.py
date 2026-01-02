import os
import textwrap
import subprocess
import uuid

from dotenv import load_dotenv
from openai import OpenAI

from core import rag
from core.sanitizer import sanitize_brand, brand_block

# -------------------------------------------------------------------
# INIT
# -------------------------------------------------------------------
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "cedar")

# Init RAG (FAISS + metadata + KB chargés une seule fois)
rag.init(client)


# -------------------------------------------------------------------
# RAG
# -------------------------------------------------------------------
def search(query: str, k: int = 5):
    """Compat : si du vieux code appelle search()."""
    return rag.search(query, k=k)


def construire_contexte(question: str, k: int = 3) -> str:
    """Construit un contexte RAG via core.rag."""
    return rag.build_context(question, k=k)


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
# TTS (macOS / afplay)
# -------------------------------------------------------------------
def tts_to_mp3_file(texte: str, voice: str | None = None) -> str | None:
    """Génère un MP3 TTS dans un fichier temporaire et renvoie son chemin."""
    texte = (texte or "").strip()
    if not texte:
        return None

    voice = voice or TTS_VOICE
    filename = f".tts_{uuid.uuid4().hex}.mp3"

    # 1) Streaming (recommandé)
    try:
        with client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL,  # ✅ model= (pas MODEL=)
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        ) as response:
            response.stream_to_file(filename)
        return filename
    except Exception:
        pass

    # 2) Fallback : create() classique
    try:
        resp = client.audio.speech.create(
            model=TTS_MODEL,  # ✅ model=
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        )

        if isinstance(resp, (bytes, bytearray)):
            audio_bytes = bytes(resp)
        elif hasattr(resp, "read"):
            audio_bytes = resp.read()
        elif hasattr(resp, "iter_bytes"):
            audio_bytes = b"".join(resp.iter_bytes())
        elif hasattr(resp, "content"):
            audio_bytes = resp.content
        else:
            raise RuntimeError("Réponse TTS non reconnue (ni bytes, ni read, ni iter_bytes).")

        with open(filename, "wb") as f:
            f.write(audio_bytes)

        return filename

    except Exception as e:
        print("❌ Erreur TTS:", e)
        return None


def lire_texte_avec_voix(texte: str):
    """Lit le texte à voix haute sur macOS via afplay."""
    texte = brand_block(texte)  # sécurité anti-marque + nettoyage final

    path = None
    try:
        path = tts_to_mp3_file(texte)
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
def repondre_comme_formateur(question: str) -> str:
    """Réponse formateur (structurée + cas pratique), basée strictement sur RAG."""
    question = sanitize_brand(question)
    contexte = construire_contexte(question, k=3)

    system_prompt = (
        "Tu es un formateur senior terrain en vente immobilière (mentor quotidien). "
        "Tu aides un conseiller à progresser avec des réponses courtes, structurées, applicables. "

        "⚠️ RÈGLE ABSOLUE (anti-invention) : "
        "Tu t’appuies UNIQUEMENT sur les extraits fournis. "
        "Si une info n’est pas dans les extraits : dis 'Non couvert par les extraits fournis'. "

        "Structure obligatoire : "
        "1) Enjeu terrain réel (1-2 phrases). "
        "2) 3 à 5 points max (logique terrain). "
        "3) Contextualisation seulement si présente dans les extraits (sinon neutre). "
        "4) Cas pratique obligatoire : situation réaliste + dialogue vendeur/agent (répliques courtes). "
        "5) Formulations terrain : 3 à 6 phrases exactes à dire. "
        "6) Limites du support. "
        "7) Prochain rendez-vous : résumé + 2 actions concrètes."
    )

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
    return brand_block(reponse)


def repondre_faq(question: str) -> str:
    """FAQ courte (5–10 lignes), basée sur RAG."""
    question = sanitize_brand(question)
    contexte = construire_contexte(question, k=3)

    system_prompt = (
        "Tu es un formateur terrain en vente immobilière. "
        "Mode FAQ métier : court, clair, directement actionnable. "
        "⚠️ Strictement basé sur les extraits fournis. "
        "Si non couvert : 'Non couvert par les extraits fournis'. "
        "Ne cite aucune marque/réseau/outils propriétaires."
    )

    user_prompt = textwrap.dedent(f"""
    Question (FAQ) :
    {question}

    Extraits (RAG) :
    {contexte}

    Consignes :
    - 5 à 10 lignes max.
    - 1 idée principale + 2/3 conseils concrets.
    """)

    reponse = chat_complete(system_prompt, user_prompt, temperature=0.3)
    return brand_block(reponse)


def generer_fiche_memo(theme: str) -> str:
    theme = sanitize_brand(theme)
    contexte = construire_contexte(theme, k=5)

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
    contexte = construire_contexte(theme, k=5)

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


def ask_and_render(label: str, question: str, generator_fn, speak_prompt: str = "\n🔊 Lire à voix haute ? (o/n) : "):
    """
    Helper unique : brand_block question -> génère -> brand_block réponse -> affiche -> TTS optionnel.
    """
    try:
        question_clean = brand_block(question)   # <- garde-fou aussi côté input
        rep = generator_fn(question_clean)
        rep = brand_block(rep)

        print(f"\n💬 {label} :\n")
        print(rep)

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


AUDIT_PROMPT_V2 = """
Tu es un auditeur qualité du “Formateur IA – Vente Immobilière Terrain” selon la CHARTE V2.

RÈGLE ABSOLUE (anti-invention)
- Tu t’appuies UNIQUEMENT sur les extraits fournis (RAG).
- Tu as le droit de REFORMULER, mais pas d’ajouter une info/outil/process qui n’est pas présent dans les extraits.
- Si une info n’est pas couverte : tu dois le signaler explicitement.

Ta mission :
1) Auditer la réponse du formateur fournie par rapport à la CHARTE V2.
2) Pointer précisément les écarts (phrases “non couvertes par les extraits”).
3) Proposer une VERSION CORRIGÉE conforme (si possible), strictement basée sur les extraits.

CHARTE V2 – critères à vérifier (avec verdict ✅ / ⚠️ / ❌) :
A. Enjeu terrain réel (1–2 phrases)
B. Structure 3–5 points (logique terrain)
C. Contextualisation : UNIQUEMENT si présente dans les extraits (sinon neutre)
D. Cas pratique obligatoire : situation réaliste + mini dialogue vendeur/agent en répliques courtes
E. Formulations terrain : 3 à 6 phrases exactes à dire, naturelles
F. Limites du support : ce qui manque, sans combler
G. Ancrage opérationnel : résumé + “Prochain rendez-vous : …” + 1 à 2 actions concrètes
H. Fidélité aux extraits : aucune invention / aucun ajout non justifié

FORMAT DE SORTIE OBLIGATOIRE :

### 📌 SYNTHÈSE AUDIT
- Niveau global : 🟢 / 🟠 / 🔴
- Exploitable tel quel :
- À retravailler :
- Manques côté base documentaire :

### ✅/⚠️/❌ DÉTAIL PAR CRITÈRE
- A. …
- B. …
- C. …
- D. …
- E. …
- F. …
- G. …
- H. …

### 🔎 ÉCARTS “NON COUVERT PAR LES EXTRAITS”
- Liste des phrases/éléments de la réponse qui ne sont pas justifiés par les extraits.

### 🛠️ VERSION CORRIGÉE (conforme CHARTE V2)
- Réécris la réponse en respectant la structure V2.
- Reste STRICTEMENT dans les extraits.
- Si un point manque dans les extraits : écrire “Non couvert par les extraits fournis”.
""".strip()

from pathlib import Path

AUDIT_PROMPT_PATH = Path("prompts") / "prompt_audit_v2.txt"

def _load_audit_prompt_v2() -> str:
    if not AUDIT_PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt d’audit introuvable : {AUDIT_PROMPT_PATH}")
    return AUDIT_PROMPT_PATH.read_text(encoding="utf-8").strip()

def audit_reponse_charte_v2(question: str, reponse: str, k: int = 5) -> str:
    """
    Audit V2 : utilise le contexte RAG et renvoie un AUDIT (sans améliorer la réponse).
    """
    question = (question or "").strip()
    reponse = (reponse or "").strip()
    if not question or not reponse:
        return "❌ Question ou réponse vide."

    # 1) Nettoyage anti-marque AVANT RAG + audit
    question_clean = sanitize_brand(question)
    reponse_clean = sanitize_brand(reponse)

    # 2) Contexte RAG
    contexte = construire_contexte(question_clean, k=k)
    contexte = sanitize_brand(contexte)

    # 3) Prompt auditeur depuis fichier
    system_prompt = _load_audit_prompt_v2()

    user_payload = f"""
QUESTION (agent) :
{question_clean}

EXTRAITS (RAG) :
{contexte}

RÉPONSE FORMATEUR À AUDITER :
{reponse_clean}
""".strip()

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload},
        ],
        temperature=0.0,
    )

    out = resp.choices[0].message.content or ""

# Garde-fou format : si le modèle n'a pas respecté le format strict, on relance 1 fois.
if "### 🔍 AUDIT CHARTE V2" not in out:
    resp2 = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": AUDIT_PROMPT_V2 + "\n\nIMPORTANT: Respecte STRICTEMENT le FORMAT DE SORTIE demandé, sans rien ajouter ni enlever."},
            {"role": "user", "content": user_payload},
        ],
        temperature=0.0,
    )
    out = resp2.choices[0].message.content or ""

    return brand_block(out)



# -------------------------------------------------------------------
# PARCOURS (MODE 1)
# -------------------------------------------------------------------
def formation_par_parcours():
    print("\n👋 Bienvenue dans le parcours de formation guidé.")
    prenom = input("Prénom : ").strip() or "le stagiaire"

    print("\nNiveau ?")
    print("1 - Débutant")
    print("2 - Confirmé")
    niveau = input("Ton niveau (1/2) : ").strip()
    profil = "débutant" if niveau == "1" else ("confirmé" if niveau == "2" else "non précisé")

    print(f"\n✅ OK {prenom}, parcours {profil}.\n")

    modules = [
        {"titre": "Découverte vendeur", "instruction": "Explique-moi la découverte vendeur avec un cas pratique concret."},
        {"titre": "Présentation de l’ACM", "instruction": "Explique-moi comment présenter l’ACM au vendeur, avec un cas pratique."},
        {"titre": "Objections prix", "instruction": "Explique-moi comment traiter une objection prix avec un cas pratique."},
        {"titre": "Suivi vendeur", "instruction": "Explique-moi la démarche de suivi vendeur avec un cas pratique."},
    ]

    for idx, module in enumerate(modules, start=1):
        print("\n" + "═" * 60)
        print(f"🎓 MODULE {idx} – {module['titre']}")
        print("═" * 60)

        print("\n⏳ Le formateur prépare le contenu...\n")
        reponse = ask_and_render(
            label=f"Explication – {module['titre']}",
            question=module["instruction"],
            generator_fn=repondre_comme_formateur,
            speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
        )
        if reponse is None:
            continue



        print("\nQue veux-tu faire ?")
        print("1 - Question rapide (FAQ) sur ce module")
        print("2 - Module suivant")
        print("3 - Stop")
        choix = input("Choix : ").strip()

        if choix == "1":
            while True:
                q = input("\nFAQ (ou 'retour') : ").strip()
                if q.lower() in {"retour", "q", "quit"}:
                    break
                if not q:
                    continue
                print("\n⏳ Réponse rapide du formateur...\n")
                ask_and_render(
                    label=f"FAQ – {module['titre']}",
                    question=q,
                    generator_fn=repondre_faq,
                    speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
                )


        elif choix == "3":
            print("\n✅ Fin du parcours.")
            return

    print("\n🎉 Parcours terminé.")


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
                if question.lower() in {"quit", "q", "exit"}:
                    break
                if not question:
                    continue

                print("\n⏳ Réponse rapide du formateur...\n")
                ask_and_render(
                    label="Réponse FAQ",
                    question=question,
                    generator_fn=repondre_faq,
                    speak_prompt="\n🔊 Lire à voix haute ? (o/n) : ",
                )

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

