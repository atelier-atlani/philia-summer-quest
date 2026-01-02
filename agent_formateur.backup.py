import os
import textwrap
import subprocess
import re
import uuid

from core import rag
from core.sanitizer import sanitize_brand, brand_block

from dotenv import load_dotenv
from openai import OpenAI

# --- Init OpenAI + env ---
load_dotenv()

# Option 1 (recommandé) : explicite
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Init RAG (FAISS + metadata + KB chargés une seule fois)
rag.init(client)
# Modèle Chat (réponses formateur/FAQ/audit)
MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")


def search(query: str, k: int = 5):
    return rag.search(query, k=k)

def sanitize_brand(text: str) -> str:
    """Masque les mentions de marque/réseau/outils propriétaires avant affichage/TTS."""
    if not text:
        return text

    # ⚠️ Remplacements (case-insensitive)
    replacements = [
        # Century 21 (avec ou sans espace / tiret)
        (r"\bcentury[-\s]*21\b", "le réseau"),
        # CenturyNet (avec ou sans espace)
        (r"\bcentury[-\s]*net\b", "la base acquéreurs interne"),
        (r"\bcenturynet\b", "la base acquéreurs interne"),
        # C21 / C-21
        (r"\bc[-\s]*21\b", "le réseau"),
        # "Century" seul (si jamais présent)
        (r"\bcentury\b", "le réseau"),
    ]

    out = text
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out

def tts_to_mp3_file(texte: str, voice: str = "cedar") -> str | None:
    """Génère un MP3 TTS dans un fichier temporaire et renvoie son chemin."""
    texte = (texte or "").strip()
    if not texte:
        return None

    filename = f".tts_{uuid.uuid4().hex}.mp3"

    # Note: response_format (pas "format") :contentReference[oaicite:2]{index=2}
    try:
        # Chemin recommandé si disponible (streaming)
        with client.audio.speech.with_streaming_response.create(
            MODEL="gpt-4o-mini-tts",
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        ) as response:
            response.stream_to_file(filename)
        return filename

    except Exception:
        # Fallback: create() classique
        resp = client.audio.speech.create(
            MODEL="gpt-4o-mini-tts",
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


def tts_to_mp3_file(texte: str, voice: str = "cedar") -> str | None:
    """Génère un MP3 TTS dans un fichier temporaire et renvoie son chemin."""
    texte = (texte or "").strip()
    if not texte:
        return None

    filename = f".tts_{uuid.uuid4().hex}.mp3"

    # Note: response_format (pas "format") :contentReference[oaicite:2]{index=2}
    try:
        # Chemin recommandé si disponible (streaming)
        with client.audio.speech.with_streaming_response.create(
            MODEL="gpt-4o-mini-tts",
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        ) as response:
            response.stream_to_file(filename)
        return filename

    except Exception:
        # Fallback: create() classique
        resp = client.audio.speech.create(
            MODEL="gpt-4o-mini-tts",
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


def tts_to_mp3_file(texte: str, voice: str = "cedar") -> str | None:
    """Génère un MP3 TTS dans un fichier temporaire et renvoie son chemin."""
    texte = (texte or "").strip()
    if not texte:
        return None

    filename = f".tts_{uuid.uuid4().hex}.mp3"

    # Note: response_format (pas "format") :contentReference[oaicite:2]{index=2}
    try:
        # Chemin recommandé si disponible (streaming)
        with client.audio.speech.with_streaming_response.create(
            MODEL="gpt-4o-mini-tts",
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        ) as response:
            response.stream_to_file(filename)
        return filename

    except Exception:
        # Fallback: create() classique
        resp = client.audio.speech.create(
            MODEL="gpt-4o-mini-tts",
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


def tts_to_mp3_file(texte: str, voice: str = "cedar") -> str | None:
    """Génère un MP3 TTS dans un fichier temporaire et renvoie son chemin."""
    texte = (texte or "").strip()
    if not texte:
        return None

    filename = f".tts_{uuid.uuid4().hex}.mp3"

    # Note: response_format (pas "format") :contentReference[oaicite:2]{index=2}
    try:
        # Chemin recommandé si disponible (streaming)
        with client.audio.speech.with_streaming_response.create(
            MODEL="gpt-4o-mini-tts",
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        ) as response:
            response.stream_to_file(filename)
        return filename

    except Exception:
        # Fallback: create() classique
        resp = client.audio.speech.create(
            MODEL="gpt-4o-mini-tts",
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


def tts_to_mp3_file(texte: str, voice: str = "cedar") -> str | None:
    """Génère un MP3 TTS dans un fichier temporaire et renvoie son chemin."""
    texte = (texte or "").strip()
    if not texte:
        return None

    filename = f".tts_{uuid.uuid4().hex}.mp3"

    # Note: response_format (pas "format") :contentReference[oaicite:2]{index=2}
    try:
        # Chemin recommandé si disponible (streaming)
        with client.audio.speech.with_streaming_response.create(
            MODEL="gpt-4o-mini-tts",
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        ) as response:
            response.stream_to_file(filename)
        return filename

    except Exception:
        # Fallback: create() classique
        resp = client.audio.speech.create(
            MODEL="gpt-4o-mini-tts",
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


def tts_to_mp3_file(texte: str, voice: str = "cedar") -> str | None:
    """Génère un MP3 TTS dans un fichier temporaire et renvoie son chemin."""
    texte = (texte or "").strip()
    if not texte:
        return None

    filename = f".tts_{uuid.uuid4().hex}.mp3"

    try:
        # Streaming -> écrit directement dans un fichier
        with client.audio.speech.with_streaming_response.create(
            MODEL="gpt-4o-mini-tts",
            voice=voice,
            input=texte,
            instructions="Voix chaleureuse, posée, légèrement grave. Rythme modéré.",
            response_format="mp3",
        ) as response:
            response.stream_to_file(filename)

        return filename

    except Exception:
        # Fallback: create() classique
        resp = client.audio.speech.create(
            MODEL="gpt-4o-mini-tts",
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



def lire_texte_avec_voix(texte: str):
    """Lit le texte à voix haute sur macOS via afplay."""
    texte = brand_block(texte)  # sécurité (bloque toute mention résiduelle)

    path = None
    try:
        path = tts_to_mp3_file(texte)
        if not path:
            return
        subprocess.run(["afplay", path], check=False)
    except Exception as e:
        print("❌ Erreur lors de la synthèse vocale : ", e)
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass







def construire_contexte(question: str, k: int = 3) -> str:
    """
    Construit un contexte RAG à partir de FAISS via le module core.rag.
    """
    return rag.build_context(question, k=k)


def repondre_comme_formateur(question: str) -> str:
    """
    Utilise le contexte (extraits de PDF) + un prompt de formateur
    pour générer une réponse pédagogique.
    """
    contexte = construire_contexte(question, k=3)

    system_prompt = (
    "Tu es un formateur senior en techniques de vente immobilière. "
    "Tu es à la fois extrêmement pédagogique et ultra-expert. "
    "Tu coaches un conseiller immobilier comme dans une séance individuelle. "

    "Ton style : "
    "- Clair, simple, structuré, motivant. "
    "- Précis, expert, terrain, sans paroles creuses. "
    "- Professionnel, bienveillant, orienté résultats. "
    "- Tu utilises un vocabulaire métier (ACM, découverte vendeur, objections, mandat, estimation…). "

    "Règles fondamentales : "
    "1. Tu t’appuies exclusivement sur les extraits du support fournis : aucune invention extérieure. "
    "2. Tu analyses d’abord la question : quel est l’enjeu commercial réel derrière ? "
    "3. Tu expliques avec des points ou étapes (3 à 5 maximum). "
    "4. Tu donnes des exemples concrets et des phrases types applicables immédiatement. "
    "5. Tu identifies clairement les informations présentes ou absentes des extraits. "
    "6. Tu signales toujours les limites du contenu si certains aspects ne sont pas couverts. "
    "7. Tu conclus par un résumé opérationnel (ce que le conseiller doit retenir / appliquer). "

    "Cas pratiques : "
    "Dans chaque réponse (sauf si cela n’a vraiment aucun sens), tu dois proposer au moins UN cas pratique très précis : "
    "- Tu décris une situation réaliste (contexte vendeur / acheteur, type de bien, objection ou étape de vente). "
    "- Tu indiques ce que le conseiller dit, ce que le client répond, puis comment le conseiller reprend la main. "
    "- Tu présentes ces dialogues sous forme de répliques courtes et applicables sur le terrain. "

    "Objectif : aider un conseiller immobilier à progresser immédiatement grâce à une réponse claire, experte, actionnable et nourrie de cas pratiques concrets, tout en respectant strictement le contenu du support."
)



    user_prompt = textwrap.dedent(f"""
    Question de l'agent immobilier :
    {question}

    Extraits du support de formation (base de connaissances) :
    {contexte}

    Consignes :
    - Appuie-toi sur ces extraits pour construire ta réponse.
    - Organise ta réponse de manière claire (par points ou étapes).
    - Adapte ton vocabulaire à un conseiller immobilier en agence.
    - Si quelque chose n'est pas couvert par ces extraits, dis-le.
    - Propose au moins UN cas pratique très précis, avec un exemple de situation et des répliques concrètes (ce que le conseiller dit, ce que le client répond, comment le conseiller reprend la main).
    """)


    response = client.chat.completions.create(
        MODEL=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,  # un peu de créativité mais pas trop
    )

    return response.choices[0].message.content
def repondre_comme_formateur(question: str) -> str:
    """
    Utilise le contexte (extraits de PDF) + un prompt de formateur
    pour générer une réponse pédagogique.
    """
    contexte = construire_contexte(question, k=3)

    system_prompt = (
        "Tu es un formateur senior en techniques de vente immobilière. "
        "Tu es à la fois extrêmement pédagogique et ultra-expert. "
        "Tu coaches un conseiller immobilier comme dans une séance individuelle. "

        "Ton style : "
        "- Clair, simple, structuré, motivant. "
        "- Précis, expert, terrain, sans paroles creuses. "
        "- Professionnel, bienveillant, orienté résultats. "
        "- Tu utilises un vocabulaire métier (ACM, découverte vendeur, objections, mandat, estimation…). "

        "Règles fondamentales : "
        "1. Tu t’appuies exclusivement sur les extraits du support fournis : aucune invention extérieure. "
        "2. Tu analyses d’abord la question : quel est l’enjeu commercial réel derrière ? "
        "3. Tu expliques avec des points ou étapes (3 à 5 maximum). "
        "4. Tu donnes des exemples concrets et des phrases types applicables immédiatement. "
        "5. Tu identifies clairement les informations présentes ou absentes des extraits. "
        "6. Tu signales toujours les limites du contenu si certains aspects ne sont pas couverts. "
        "7. Tu conclus par un résumé opérationnel (ce que le conseiller doit retenir / appliquer). "

        "Cas pratiques : "
        "Dans chaque réponse (sauf si cela n’a vraiment aucun sens), tu dois proposer au moins UN cas pratique très précis : "
        "- Tu décris une situation réaliste (contexte vendeur / acheteur, type de bien, objection ou étape de vente). "
        "- Tu indiques ce que le conseiller dit, ce que le client répond, puis comment le conseiller reprend la main. "
        "- Tu présentes ces dialogues sous forme de répliques courtes et applicables sur le terrain. "

        "Objectif : aider un conseiller immobilier à progresser immédiatement grâce à une réponse claire, experte, actionnable et nourrie de cas pratiques concrets, tout en respectant strictement le contenu du support."
    )

    user_prompt = textwrap.dedent(f"""
        Question de l'agent immobilier :
        {question}

        Extraits du support de formation (base de connaissances) :
        {contexte}

        Consignes :
        - Appuie-toi sur ces extraits pour construire ta réponse.
        - Organise ta réponse de manière claire (par points ou étapes).
        - Adapte ton vocabulaire à un conseiller immobilier en agence.
        - Si quelque chose n'est pas couvert par ces extraits, dis-le.
        - Propose au moins UN cas pratique très précis, avec un exemple de situation et des répliques concrètes (ce que le conseiller dit, ce que le client répond, comment le conseiller reprend la main).
    """)

    response = client.chat.completions.create(
        MODEL=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,  # un peu de créativité mais pas trop
    )

    return response.choices[0].message.content
def repondre_faq(question: str) -> str:
    """
    Mode réponses rapides : l'IA répond de manière courte et directe,
    en s'appuyant quand même sur le contexte des PDF.
    """
    contexte = construire_contexte(question, k=3)

    system_prompt = (
        "Tu es un formateur expert en vente immobilière. "
        "Tu réponds en mode 'FAQ métier' : court, clair, directement exploitable. "
        "Tes réponses font entre 5 et 10 lignes, avec éventuellement des puces, "
        "et restent strictement basées sur les extraits fournis."
    )

    user_prompt = textwrap.dedent(f"""
        Question de l'agent immobilier :
        {question}

        Extraits du support de formation (base de connaissances) :
        {contexte}

        Consignes :
        - Donne une réponse concise et directe (5 à 10 lignes).
        - Va droit au but : idée principale + 2 ou 3 conseils concrets.
        - Ne détaille pas autant qu'un cours complet, c'est une réponse rapide.
    """)

    response = client.chat.completions.create(
        MODEL=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def generer_fiche_memo(theme: str) -> str:
    """
    Génère une fiche mémo structurée sur un thème précis
    (ex : 'Découverte vendeur', 'Gestion des objections prix').
    """
    contexte = construire_contexte(theme, k=5)

    system_prompt = (
        "Tu es un formateur en vente immobilière chargé de créer une fiche mémo structurée. "
        "Cette fiche doit être utilisable par un conseiller sur le terrain pour se souvenir des essentiels."
    )

    user_prompt = textwrap.dedent(f"""
        Thème de la fiche mémo :
        {theme}

        Extraits du support de formation (base de connaissances) :
        {contexte}

        Consignes :
        - Crée une fiche mémo claire, sous forme de sections.
        - Structure suggérée :
          1) Objectif de la démarche
          2) Points clés à respecter
          3) Questions à poser au client
          4) Erreurs à éviter
          5) 3 à 5 phrases types utilisables sur le terrain
        - Reste strictement aligné avec les extraits fournis.
    """)

    response = client.chat.completions.create(
        MODEL=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content


def generer_plan_entretien(theme: str) -> str:
    """
    Génère un plan d'entretien structuré (étapes) sur un thème donné,
    par exemple la présentation de l'ACM ou la découverte vendeur.
    """
    contexte = construire_contexte(theme, k=5)

    system_prompt = (
        "Tu es un formateur en vente immobilière. "
        "Tu conçois un plan d'entretien structuré pour un conseiller, étape par étape. "
        "Chaque étape doit avoir un objectif clair et des exemples de formulations."
    )

    user_prompt = textwrap.dedent(f"""
        Thème de l'entretien :
        {theme}

        Extraits du support de formation (base de connaissances) :
        {contexte}

        Consignes :
        - Propose un déroulé en étapes numérotées (3 à 7 étapes).
        - Pour chaque étape, précise :
          - l'objectif de l'étape
          - ce que le conseiller doit faire
          - 1 à 2 exemples de formulations possibles.
        - Reste strictement fondé sur les extraits fournis.
    """)

    response = client.chat.completions.create(
        MODEL=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content

def debrief_jeu_de_role(history, situation: str) -> str:
    """
    Analyse le jeu de rôle entre l'agent (toi) et le vendeur (IA)
    et fournit un débrief pédagogique : points forts, axes d'amélioration, suggestions.
    """

    # On reconstruit une transcription lisible à partir de l'historique
    lignes = []
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")

        # On ignore les messages système
        if role == "system":
            continue

        # On ignore le gros message de contexte initial
        if "Contexte pour ton rôle de vendeur" in content:
            continue

        if role == "user":
            lignes.append(f"Agent : {content}")
        elif role == "assistant":
            lignes.append(f"Vendeur : {content}")

    transcription = "\n".join(lignes)

    system_prompt = (
        "Tu es un formateur senior en vente immobilière. "
        "Tu viens d'observer un jeu de rôle entre un conseiller (Agent) et un vendeur (Vendeur). "
        "Ton rôle est de faire un débrief pédagogique, bienveillant mais exigeant. "
        "Tu expliques ce qui est bien, ce qui peut être amélioré, et tu donnes des exemples de meilleures formulations."
    )

    user_prompt = textwrap.dedent(f"""
        Situation de départ décrite : {situation}

        Transcription du jeu de rôle :
        {transcription}

        Consignes pour le débrief :
        1. Commence par un court retour global (climat, posture globale de l'agent).
        2. Liste les points forts de l'agent (ce qu'il a bien fait).
        3. Liste les axes d'amélioration (ce qui pourrait être dit ou fait autrement).
        4. Propose des exemples de formulations plus efficaces pour 2 ou 3 moments clés.
        5. Termine par 3 conseils pratiques à appliquer lors du prochain jeu de rôle.
    """)

    response = client.chat.completions.create(
        MODEL=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content
def parcours_guide():
    """
    Parcours guidé : le formateur IA accueille le stagiaire,
    lui présente un plan en plusieurs étapes et l'accompagne
    progressivement vers plus d'interactivité.
    """

    print("\n👋 Bienvenue dans le parcours guidé avec le formateur IA.")
    prenom = input("Pour commencer, comment t'appelles-tu ? ").strip()
    if not prenom:
        prenom = "le stagiaire"

    print(f"\nRavi de te retrouver {prenom} 😊")

    print("\nAvant de démarrer, j'ai besoin de situer ton niveau.")
    print("1 - Débutant (moins d'un an d'expérience)")
    print("2 - Confirmé (plus d'un an d'expérience)")
    niveau = input("Ton niveau (1 ou 2) : ").strip()

    if niveau == "1":
        profil = "débutant"
    elif niveau == "2":
        profil = "confirmé"
    else:
        profil = "non précisé"

    print(f"\n✅ Très bien {prenom}, tu es considéré comme {profil}.")

    print("\nVoici le plan de ce parcours :")
    print("Étape 1 : Explication structurée + cas pratique sur un thème clé (découverte vendeur ou autre).")
    print("Étape 2 : Mode 'questions rapides' pour clarifier des points précis.")
    print("Étape 3 : Jeu de rôle vendeur / agent pour t'entraîner en conditions quasi réelles.\n")

    input("Appuie sur Entrée pour démarrer l'étape 1...")

    # ÉTAPE 1 : Explication + cas pratique
    print("\n🎓 ÉTAPE 1 – Explication + cas pratique")
    print("Sur quel thème veux-tu commencer ?")
    print("Exemples :")
    print("- Découverte vendeur")
    print("- Présentation de l’ACM")
    print("- Gestion des objections sur le prix\n")

    theme = input("Thème choisi : ").strip()
    if not theme:
        theme = "Découverte vendeur"

    question_etape1 = f"Explique-moi de manière pédagogique {theme}, avec un cas pratique concret applicatif."
    print(f"\n⏳ Le formateur prépare l'explication sur : {theme}...\n")
    try:
        reponse1 = repondre_comme_formateur(question_etape1)
        print("💬 Réponse du formateur (Étape 1) :\n")
        print(reponse1)
    except Exception as e:
        print("❌ Erreur lors de l'étape 1 : ", e)
        return

    input("\n➡️ Quand tu es prêt, appuie sur Entrée pour passer à l'étape 2 (questions rapides)...")

    # ÉTAPE 2 : Questions rapides (FAQ)
    print("\n⚡ ÉTAPE 2 – Questions rapides (FAQ métier)")
    print("Tu peux maintenant poser des questions ciblées en lien avec ce que tu viens de voir.")
    print("Exemples :")
    print("- Quelle question poser pour vérifier la motivation du vendeur ?")
    print("- Comment reformuler une objection sur le prix ?\n")

    while True:
        question_faq = input("Ta question rapide (ou 'suivant' pour passer à l'étape 3) : ").strip()
        if question_faq.lower() in {"suivant", "next"}:
            break
        if not question_faq:
            continue

        

    input("\n➡️ Appuie sur Entrée pour passer à l'étape 3 (jeu de rôle)...")

    # ÉTAPE 3 : Jeu de rôle
    print("\n🎭 ÉTAPE 3 – Jeu de rôle vendeur / agent")
    print("Tu vas maintenant t'entraîner en situation réelle : l'IA joue le vendeur, toi tu joues ton propre rôle.")
    print("Tu pourras t'arrêter à tout moment avec /stop.\n")

    try:
        jeu_de_role_vendeur_agent()
    except Exception as e:
        print("❌ Erreur lors du jeu de rôle : ", e)
        return

    print("\n✅ Parcours guidé terminé.")
    print("Tu peux relancer un nouveau parcours, revenir au menu principal, ou utiliser un des modes individuellement.")

def jeu_de_role_vendeur_agent():
    """
    L'IA joue le rôle du vendeur.
    Toi, tu joues le rôle du conseiller immobilier.
    La conversation est ancrée dans les extraits du support (via la recherche).
    """

    print("\n🎭 Mode jeu de rôle vendeur / agent")
    print("Décris le type de situation que tu veux travailler.")
    print("Exemples :")
    print("- Vendeur pas pressé qui hésite à mettre en vente")
    print("- Vendeur qui pense que son bien vaut plus cher")
    print("- Vendeur méfiant vis-à-vis des agences\n")

    situation = input("Décris la situation du vendeur : ").strip()
    if not situation:
        print("❌ Situation vide, retour au menu.")
        return

    # On utilise la même logique de contexte que le formateur
    contexte = construire_contexte(situation, k=4)

    system_roleplay = (
        "Tu joues le rôle d'un vendeur particulier qui souhaite (ou envisage) vendre un bien immobilier résidentiel. "
        "Tu restes STRICTEMENT dans ton rôle de vendeur : tu ne donnes pas de conseils au conseiller, tu ne sors pas du personnage. "
        "Tu t'appuies sur le contexte fourni (extraits du support de formation) pour définir ton état d'esprit, tes objections, tes attentes. "
        "Tu parles comme un vendeur réel : phrases simples, naturelles, parfois hésitantes ou émotionnelles. "
        "Tes réponses sont courtes (1 à 3 phrases), jamais de longs paragraphes. "
        "Tu ne révèles JAMAIS que tu es une IA ou un formateur, tu es simplement 'le vendeur'. "
        "Tu peux exprimer des doutes, des objections, des hésitations, mais toujours de manière cohérente avec le contexte."
    )

    contexte_message = (
        "Contexte pour ton rôle de vendeur (extraits du support de formation) :\n"
        f"{contexte}\n\n"
        "Tu vas maintenant simuler une discussion avec un conseiller immobilier. "
        "Commence la conversation comme un vendeur dans cette situation."
    )

    history = [
        {"role": "system", "content": system_roleplay},
        {"role": "user", "content": contexte_message},
    ]

    print("\n⏳ Réponse rapide du formateur...\n")
    try:
                    # 1) Nettoyer la question avant envoi au modèle
                    question_clean = sanitize_brand(question)

                    # 2) Générer la réponse
                    reponse = repondre_faq(question_clean)

                    # 3) Nettoyer la réponse avant affichage + voix
                    reponse = sanitize_brand(reponse)

                    print("💬 Réponse FAQ IA :\n")
                    print(reponse)

                    choix_voix = input("\n🔊 Le formateur doit-il lire cette réponse à voix haute ? (o/n) : ").strip().lower()
                    if choix_voix == "o":
                        lire_texte_avec_voix(reponse)

    except Exception as e:
                    print("❌ Erreur lors de la FAQ : ", e)


    history.append({"role": "user", "content": agent_input})

    response = client.chat.completions.create(
            MODEL=MODEL,
            messages=history,
            temperature=0.7,
        )
    vendeur_reply = response.choices[0].message.content

    print(f"\nVendeur : {vendeur_reply}\n")

    history.append({"role": "assistant", "content": vendeur_reply})

    # 🔁 Après la fin du jeu de rôle : proposer un débrief
    choix = input("\n📋 Veux-tu un débrief du formateur sur ce jeu de rôle ? (o/n) : ").strip().lower()
    if choix == "o":
        print("\n⏳ Débrief en cours...\n")
        try:
            feedback = debrief_jeu_de_role(history, situation)
            print("🧠 Débrief du formateur IA :\n")
            print(feedback)
        except Exception as e:
            print("❌ Erreur lors du débrief : ", e)
    else:
        print("\n✅ Jeu de rôle terminé sans débrief.")


        response = client.chat.completions.create(
            MODEL=MODEL,
            messages=history,
            temperature=0.7,
        )
        vendeur_reply = response.choices[0].message.content

        print(f"\nVendeur : {vendeur_reply}\n")

        history.append({"role": "assistant", "content": vendeur_reply})
def formation_par_parcours():
    """
    Mode 1 : le formateur IA guide le stagiaire à travers un parcours de contenu,
    en choisissant une progression pédagogique (découverte, ACM, objections, suivi...).
    """
    print("\n👋 Bienvenue dans le parcours de formation guidé par le formateur IA.")
    prenom = input("Pour commencer, comment t'appelles-tu ? ").strip()
    if not prenom:
        prenom = "le stagiaire"

    print(f"\nRavi de te retrouver {prenom} 😊")

    print("\nPour adapter le rythme, j'ai besoin de situer ton niveau.")
    print("1 - Débutant (moins d'un an d'expérience en agence)")
    print("2 - Confirmé (plus d'un an d'expérience)")
    niveau = input("Ton niveau (1 ou 2) : ").strip()

    if niveau == "1":
        profil = "débutant"
    elif niveau == "2":
        profil = "confirmé"
    else:
        profil = "profil non précisé"

    print(f"\n✅ Très bien {prenom}, je vais te proposer un parcours {profil} structuré en plusieurs étapes.\n")

    print("Voici le déroulé proposé :")
    print("1️⃣ Découverte vendeur")
    print("2️⃣ Présentation de l’ACM au vendeur")
    print("3️⃣ Gestion des objections sur le prix")
    print("4️⃣ Suivi vendeur\n")

    input("Appuie sur Entrée pour démarrer avec l'étape 1 (Découverte vendeur)...")

    modules = [
        {
            "titre": "Découverte vendeur",
            "instruction": "Explique-moi de manière pédagogique la découverte vendeur avec un cas pratique concret d'entretien.",
        },
        {
            "titre": "Présentation de l’ACM au vendeur",
            "instruction": "Explique-moi comment présenter l’ACM à un vendeur, avec un cas pratique de situation où le vendeur hésite sur le prix.",
        },
        {
            "titre": "Gestion des objections sur le prix",
            "instruction": "Explique-moi comment traiter les objections sur le prix, avec un cas pratique de vendeur qui pense que son bien vaut plus cher.",
        },
        {
            "titre": "Suivi vendeur",
            "instruction": "Explique-moi la démarche de suivi vendeur, avec un cas pratique de vendeur qui tarde à prendre une décision.",
        },
    ]

    for idx, module in enumerate(modules, start=1):
        print("\n" + "═" * 60)
        print(f"🎓 MODULE {idx} – {module['titre']}")
        print("═" * 60)

        question_module = module["instruction"]
        print(f"\n⏳ Le formateur prépare le contenu sur : {module['titre']}...\n")

        try:
            # 1) Nettoyer la consigne avant envoi au modèle (anti-marque)
            question_clean = sanitize_brand(question_module)

            # 2) Générer la réponse
            reponse = repondre_comme_formateur(question_clean)

            # 3) Bloquer toute mention résiduelle avant affichage + voix
            reponse = brand_block(reponse)

            print("💬 Réponse du formateur IA :\n")
            print(reponse)

            # Lecture vocale optionnelle
            choix_voix = input("\n🔊 Veux-tu que le formateur lise cette explication à voix haute ? (o/n) : ").strip().lower()
            if choix_voix == "o":
                lire_texte_avec_voix(reponse)

        except Exception as e:
            print("❌ Erreur lors de la génération de la réponse : ", e)
            continue

        # Interaction de fin de module
        print("\nQue souhaites-tu faire maintenant ?")
        print("1 - Poser une question rapide en lien avec ce module")
        print("2 - Passer au module suivant")
        print("3 - Arrêter le parcours")

        choix_module = input("Ton choix (1/2/3) : ").strip()

        if choix_module == "1":
            print("\n⚡ Questions rapides en lien avec ce module.")
            print("Tape 'retour' pour revenir au parcours principal.\n")

            while True:
                question_faq = input("Ta question rapide : ").strip()
                if question_faq.lower() in {"retour", "quit", "q"}:
                    print("⬅️ Retour au parcours.")
                    break
                if not question_faq:
                    continue

                print("\n⏳ Réponse rapide du formateur...\n")
                try:
                    # 1) Nettoyer la question avant envoi au modèle
                    question_faq_clean = sanitize_brand(question_faq)

                    # 2) Générer la réponse
                    reponse_faq = repondre_faq(question_faq_clean)

                    # 3) Bloquer toute mention résiduelle avant affichage + voix
                    reponse_faq = brand_block(reponse_faq)

                    print("💬 Réponse FAQ :\n")
                    print(reponse_faq)

                    choix_voix_faq = input("\n🔊 Lecture vocale de cette réponse ? (o/n) : ").strip().lower()
                    if choix_voix_faq == "o":
                        lire_texte_avec_voix(reponse_faq)

                except Exception as e:
                    print("❌ Erreur lors de la FAQ : ", e)

            choix_apres_faq = input("\nSouhaites-tu continuer vers le module suivant ? (o/n) : ").strip().lower()
            if choix_apres_faq != "o":
                print("\n✅ Fin du parcours de formation.")
                return

        elif choix_module == "2":
            continue

        elif choix_module == "3":
            print("\n✅ Fin du parcours de formation.")
            return

        else:
            print("\nChoix non reconnu, on passe au module suivant.")
            continue

    print("\n🎉 Tu es arrivé au bout du parcours proposé.")
    print("Tu peux maintenant utiliser les autres modes (jeu de rôle, fiches mémo, plans d'entretien).")


def main():
    print("🧠 Agent IA formateur – Vente immobilière")

    while True:
        print("\nChoisis un mode :")
        print("0 - Parcours guidé global (explications + FAQ + jeu de rôle)")
        print("1 - Parcours de formation guidé (contenu structuré piloté par le formateur IA)")
        print("2 - Jeu de rôle vendeur / agent (+ débrief)")
        print("3 - Questions rapides (FAQ métier)")
        print("4 - Fiche mémo (synthèse sur un thème)")
        print("5 - Plan d'entretien structuré")
        print("q - Quitter")

        choix = input("\nTon choix : ").strip().lower()

        # ---------------------------------------------------------------
        # MODE 0 : Parcours guidé global (si tu l'as)
        # ---------------------------------------------------------------
        if choix == "0":
            print("\n🧭 Mode 0 : Parcours guidé global\n")
            try:
                parcours_guide()  # si ta fonction s'appelle autrement, adapte ici
            except Exception as e:
                print("❌ Erreur dans le parcours guidé : ", e)

        # ---------------------------------------------------------------
        # MODE 1 : Parcours de formation piloté par le formateur IA
        # ---------------------------------------------------------------
        elif choix == "1":
            print("\n🎓 Mode 1 : Parcours de formation guidé (contenu structuré)\n")
            try:
                formation_par_parcours()
            except Exception as e:
                print("❌ Erreur dans le parcours de formation : ", e)

        # ---------------------------------------------------------------
        # MODE 2 : Jeu de rôle
        # ---------------------------------------------------------------
        elif choix == "2":
            try:
                jeu_de_role_vendeur_agent()
            except Exception as e:
                print("❌ Erreur dans le jeu de rôle : ", e)

        # ---------------------------------------------------------------
        # MODE 3 : FAQ rapide
        # ---------------------------------------------------------------
        elif choix == "3":
    print("\nMode 3 : Questions rapides (FAQ métier)")
    print("Pose une question courte (ou tape 'quit' pour revenir au menu).")

    while True:
        question = input("\nTa question (FAQ) : ").strip()
        if question.lower() in {"quit", "exit", "q"}:
            print("⬅️ Retour au menu principal.")
            break

        if not question:
            continue

        print("\n⏳ Réponse rapide du formateur...\n")
        try:
            # 1) Nettoyer la question avant envoi au modèle
            question_clean = sanitize_brand(question)

            # 2) Générer la réponse
            reponse = repondre_faq(question_clean)

            # 3) Bloquer toute mention résiduelle avant affichage + voix
            reponse = brand_block(reponse)

            print("💬 Réponse FAQ IA :\n")
            print(reponse)

            choix_voix = input("\n🔊 Le formateur doit-il lire cette réponse à voix haute ? (o/n) : ").strip().lower()
            if choix_voix == "o":
                lire_texte_avec_voix(reponse)

        except Exception as e:
            print("❌ Erreur lors de la FAQ : ", e)


        # ---------------------------------------------------------------
        # MODE 4 : Fiche mémo
        # ---------------------------------------------------------------
        elif choix == "4":
            print("\nMode 4 : Fiche mémo")
            theme = input("Sur quel thème veux-tu une fiche mémo ?\n(ex : Découverte vendeur, objections prix, suivi vendeur) : ").strip()
            if not theme:
                print("❌ Thème vide, retour au menu.")
                continue

            print("\n⏳ Génération de la fiche mémo...\n")
            try:
                theme_clean = sanitize_brand(theme)
                fiche = generer_fiche_memo(theme_clean)
                fiche = brand_block(fiche)

                print("📘 Fiche mémo :\n")
                print(fiche)

                choix_voix = input("\n🔊 Lecture vocale de la fiche ? (o/n) : ").strip().lower()
                if choix_voix == "o":
                    lire_texte_avec_voix(fiche)

            except Exception as e:
                print("❌ Erreur lors de la génération de la fiche mémo : ", e)

        # ---------------------------------------------------------------
        # MODE 5 : Plan d’entretien structuré
        # ---------------------------------------------------------------
        elif choix == "5":
            print("\nMode 5 : Plan d'entretien structuré")
            theme = input("Pour quel type d'entretien ?\n(ex : Présentation de l'ACM, découverte vendeur) : ").strip()
            if not theme:
                print("❌ Thème vide, retour au menu.")
                continue

            print("\n⏳ Génération du plan d'entretien...\n")
            try:
                theme_clean = sanitize_brand(theme)
                plan = generer_plan_entretien(theme_clean)
                plan = brand_block(plan)

                print("🗂️ Plan d'entretien :\n")
                print(plan)

                choix_voix = input("\n🔊 Lecture vocale du plan ? (o/n) : ").strip().lower()
                if choix_voix == "o":
                    lire_texte_avec_voix(plan)

            except Exception as e:
                print("❌ Erreur lors de la génération du plan : ", e)

        elif choix == "q":
            print("👋 Fin du programme.")
            break

        else:
            print("❌ Choix non reconnu, merci de taper 0, 1, 2, 3, 4, 5 ou q.")


if __name__ == "__main__":
    main()






