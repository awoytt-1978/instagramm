"""Grafik-Rendering aus Vorlagen (Pillow). Jede Vorlage = Farbverlauf + Typografie, 1080x1350 (4:5)."""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350

# Vorlagen: (Farbe oben, Farbe unten, Textfarbe). Auswahl nach Themenbereich, deterministisch.
TEMPLATES = [
    ((120, 190, 235), (245, 180, 205), (20, 20, 30)),   # Blau -> Rosa
    ((255, 225, 90), (240, 90, 110), (20, 20, 30)),     # Gelb -> Rot
    ((20, 20, 30), (70, 110, 200), (245, 245, 245)),    # Nachtblau
    ((235, 245, 240), (150, 200, 180), (25, 40, 35)),   # Mint
]

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _font(size):
    for p in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def render_post_image(title, subtitle, area, out_path):
    idx = int(hashlib.md5(area.encode()).hexdigest(), 16) % len(TEMPLATES)
    top, bottom, fg = TEMPLATES[idx]
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        row = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        for x in range(W):
            px[x, y] = row
    d = ImageDraw.Draw(img)
    f_title, f_sub, f_tag = _font(96), _font(46), _font(34)
    y = 420
    for line in _wrap(d, title, f_title, W - 160):
        d.text((80, y), line, font=f_title, fill=fg)
        y += 115
    y += 20
    for line in _wrap(d, subtitle, f_sub, W - 160):
        d.text((80, y), line, font=f_sub, fill=fg)
        y += 62
    d.text((80, H - 110), "@andwoy", font=f_tag, fill=fg)
    d.text((W - 80 - d.textlength(area.upper(), font=f_tag), H - 110), area.upper(), font=f_tag, fill=fg)
    img.save(out_path, "JPEG", quality=92)
