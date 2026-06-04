import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TEXT = "Bonjour, je suis ton formateur. On va travailler ensemble, pas à pas."

def to_bytes(resp) -> bytes:
    # Selon versions du SDK, la réponse peut être bytes, ou avoir .read(), ou être streamée.
    if isinstance(resp, (bytes, bytearray)):
        return bytes(resp)
    if hasattr(resp, "read"):
        return resp.read()
    if hasattr(resp, "iter_bytes"):
        return b"".join(resp.iter_bytes())
    raise TypeError(f"Type de réponse audio inattendu: {type(resp)}")

resp = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=TEXT,
)

audio = to_bytes(resp)

out = "test_tts.mp3"
with open(out, "wb") as f:
    f.write(audio)

print(f"✅ Fichier audio généré : {out} ({len(audio)} bytes)")
