"""Génère une sonnerie téléphone réaliste (style professionnel)."""
import struct
import wave
import math

SAMPLE_RATE = 44100
DURATION = 3.0  # secondes


def generate_ringtone(filepath: str):
    """Génère une sonnerie double-tonalité style téléphone français."""
    samples = []
    t_total = int(SAMPLE_RATE * DURATION)

    for i in range(t_total):
        t = i / SAMPLE_RATE
        # Pattern : 1.5s de sonnerie + 0.5s silence + 1s de sonnerie
        in_ring = (t < 1.5) or (2.0 < t < 3.0)

        if in_ring:
            # Double fréquence style téléphone français (440Hz + 480Hz)
            val = 0.3 * math.sin(2 * math.pi * 440 * t)
            val += 0.3 * math.sin(2 * math.pi * 480 * t)
            # Envelope pour éviter les clics
            if t < 0.01:
                val *= t / 0.01
        else:
            val = 0.0

        samples.append(int(val * 32767))

    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(struct.pack(f'<{len(samples)}h', *samples))


if __name__ == "__main__":
    import os
    os.makedirs("assets/sounds", exist_ok=True)
    generate_ringtone("assets/sounds/phone_ring.wav")
    print("Sonnerie générée : assets/sounds/phone_ring.wav")
