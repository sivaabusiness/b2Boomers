# Prépare les images Google Ads (Search) à partir des photos du site.
# Paysage 1,91:1 (1200x628) et carré 1:1 (1200x1200) en JPG ; logo carré PNG fond blanc.
import os
from PIL import Image
ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "..", "site-paysagiste-artois", "photos")
OUT = os.path.join(ICI, "images")
SERVICES = ["amenagement-jardin", "terrasse-allee", "entretien-jardin", "cloture-portail"]
# (fichier source, format, ancrage vertical 0=haut 0.5=centre 1=bas)
PLAN = {s: [(f"action-{s}", "paysage", 0.5), (f"apres-{s}", "paysage", 0.5), (f"apres-{s}", "carre", 0.5)]
        for s in SERVICES}
PLAN["equipe"] = [("equipe", "paysage", 0.5), ("equipe", "carre", 0.5)]   # niveau campagne

def recadre(im, ratio, ancre):
    w, h = im.size
    if w / h > ratio:                      # trop large : on coupe les côtés (centré)
        nw = int(h * ratio); x = (w - nw) // 2; return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio); y = int((h - nh) * ancre); return im.crop((0, y, w, y + nh))

def main():
    os.makedirs(OUT, exist_ok=True)
    for s, lst in PLAN.items():
        for src, fmt, ancre in lst:
            im = Image.open(os.path.join(SRC, src + ".webp")).convert("RGB")
            ratio, taille = (1.91, (1200, 628)) if fmt == "paysage" else (1.0, (1200, 1200))
            im = recadre(im, ratio, ancre)
            if im.size[0] > taille[0]: im = im.resize(taille, Image.LANCZOS)
            im.save(os.path.join(OUT, f"{src}_{fmt}.jpg"), quality=88)
    logo = Image.open(os.path.join(SRC, "logo.webp")).convert("RGBA")
    fond = Image.new("RGB", logo.size, "white"); fond.paste(logo, mask=logo.split()[3])
    c = max(fond.size); carre = Image.new("RGB", (c, c), "white")
    carre.paste(fond, ((c - fond.size[0]) // 2, (c - fond.size[1]) // 2))
    carre.save(os.path.join(OUT, "logo.png"))
    for f in sorted(os.listdir(OUT)):
        print(f, Image.open(os.path.join(OUT, f)).size, os.path.getsize(os.path.join(OUT, f)) // 1024, "Ko")

if __name__ == "__main__":
    main()
