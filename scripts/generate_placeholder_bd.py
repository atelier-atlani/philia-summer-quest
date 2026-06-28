"""scripts/generate_placeholder_bd.py — Génère le placeholder pour les planches BD absentes."""

import os
from PIL import Image, ImageDraw

W, H = 800, 1000
img = Image.new("RGB", (W, H), color=(245, 240, 232))  # beige #F5F0E8
draw = ImageDraw.Draw(img)

# Cercles décoratifs pastel
draw.ellipse([250, 200, 550, 500], fill=(200, 220, 240))
draw.ellipse([300, 280, 500, 450], fill=(220, 200, 240))

# Texte (police par défaut Pillow)
draw.text((W // 2, 600), "Planche en cours d'illustration",
          fill=(80, 70, 60), anchor="mm")
draw.text((W // 2, 660), "la suite de l'aventure t'attend bientôt !",
          fill=(120, 110, 100), anchor="mm")

out = "assets/narratif/_placeholder/placeholder_planche_bd.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print(f"Placeholder généré : {out}")
