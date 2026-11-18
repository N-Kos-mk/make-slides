"""Draws the stand-in images of the gallery: road surfaces with and without cracks, a detection
mask, close-ups of a wide, a fine and a wet crack, and a mock chat screen.

    python make_figures.py

A real deck uses the material's own images instead; these exist only so that the gallery has
something to show without shipping anyone's data. They contain shapes only — no text.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent / "figures"
INK, GREY, PALE, BLUE, RED = "#1a2330", "#a9b0b8", "#e3e7ec", "#1f3f6b", "#c8372d"


def asphalt(w, h, seed, wet=False):
    """Grey asphalt: noise, a little blur, light and dark aggregate."""
    rnd = random.Random(seed)
    base = Image.effect_noise((w, h), 38).convert("L").filter(ImageFilter.GaussianBlur(0.8))
    tone = 96 if wet else 142
    im = Image.merge("RGB", [base.point(lambda v, t=tone, k=k: max(0, min(255, int(t + (v - 128) * 0.55) + k)))
                             for k in (0, 2, 5)])
    d = ImageDraw.Draw(im)
    for _ in range(w * h // 900):
        x, y, r = rnd.randrange(w), rnd.randrange(h), rnd.choice([2, 2, 3, 4])
        c = rnd.choice([(178, 178, 176), (92, 92, 94), (120, 118, 116)]) if not wet else rnd.choice([(70, 72, 76), (118, 120, 124)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    if wet:                                                       # sheen of standing water
        sheen = Image.new("L", (w, h), 0)
        sd = ImageDraw.Draw(sheen)
        for _ in range(7):
            x, y = rnd.randrange(w), rnd.randrange(h)
            sd.ellipse([x - 260, y - 70, x + 260, y + 70], fill=rnd.randint(40, 70))
        sheen = sheen.filter(ImageFilter.GaussianBlur(40))
        im = Image.composite(Image.new("RGB", (w, h), (190, 196, 204)), im, sheen)
    return im


def crack_path(w, h, seed, y0=None, steps=60, wander=14):
    """A crack as a polyline that crosses the image from left to right."""
    rnd = random.Random(seed)
    y = y0 if y0 is not None else rnd.randint(h // 4, 3 * h // 4)
    pts = []
    for k in range(steps + 1):
        x = int(k * w / steps)
        y = max(10, min(h - 10, y + rnd.randint(-wander, wander)))
        pts.append((x, y))
    return pts


def branch(pts, seed, n=4, length=14, wander=16):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = pts[rnd.randrange(len(pts) // 6, len(pts) * 5 // 6)]
        dy = rnd.choice([-1, 1])
        p = [(x, y)]
        for _ in range(length):
            x += rnd.randint(4, 18)
            y += dy * rnd.randint(4, wander)
            p.append((x, y))
        out.append(p)
    return out


def draw_cracks(im, paths, widths, colour=(34, 34, 36)):
    d = ImageDraw.Draw(im)
    for p, wd in zip(paths, widths):
        d.line(p, fill=colour, width=wd, joint="curve")
    return im


def alligator(w, h, seed):
    """Paths of a network of cracks (the badly damaged section)."""
    paths, widths = [], []
    for k in range(6):
        p = crack_path(w, h, seed + k, y0=int((k + 0.5) * h / 6), wander=18)
        paths.append(p)
        widths.append(5 if k % 2 else 7)
        for b in branch(p, seed + 40 + k, n=5):
            paths.append(b)
            widths.append(4)
    rnd = random.Random(seed + 99)                                # cross cracks
    for _ in range(9):
        x = rnd.randint(80, w - 80)
        p = [(x + rnd.randint(-10, 10), int(j * h / 12)) for j in range(13)]
        paths.append(p)
        widths.append(4)
    return paths, widths


def road_sound():
    im = asphalt(1400, 1050, 1)
    p = crack_path(1400, 1050, 2, y0=640, steps=14, wander=6)[:5]   # one short hairline
    return draw_cracks(im, [p], [3])


def road_alligator():
    im = asphalt(1400, 1050, 3)
    paths, widths = alligator(1400, 1050, 10)
    return draw_cracks(im, paths, widths)


def road_mask():
    im = Image.new("RGB", (1400, 1050), "white")
    paths, widths = alligator(1400, 1050, 10)
    return draw_cracks(im, paths, [w + 2 for w in widths], colour=(200, 55, 45))


def crack_closeup(width_px, seed, wet=False):
    im = asphalt(1200, 900, seed, wet=wet)
    p = crack_path(1200, 900, seed + 5, y0=450, steps=40, wander=18)
    paths, widths = [p], [width_px]
    for b in branch(p, seed + 7, n=2, length=10):
        paths.append(b)
        widths.append(max(2, width_px // 2))
    return draw_cracks(im, paths, widths, colour=(26, 26, 28) if not wet else (40, 42, 46))


def chat_screen():
    im = Image.new("RGB", (1600, 900), "#f4f6f8")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1600, 70], fill=BLUE)
    d.rectangle([300, 110, 1300, 780], fill="white", outline=GREY, width=3)          # the chat window
    y = 150
    for k, (side, w, lines) in enumerate([("l", 520, 2), ("r", 380, 1), ("l", 600, 3), ("r", 300, 1), ("l", 460, 2)]):
        hgt = 26 + lines * 30
        x0 = 340 if side == "l" else 1260 - w
        d.rectangle([x0, y, x0 + w, y + hgt], fill=PALE if side == "l" else "#dbe6f3")
        for j in range(lines):
            d.rectangle([x0 + 20, y + 18 + j * 30, x0 + w - (60 if j == lines - 1 else 24), y + 30 + j * 30], fill=GREY)
        y += hgt + 22
    d.rectangle([340, 700, 1140, 750], fill="white", outline=GREY, width=2)          # input box
    d.rectangle([1160, 700, 1260, 750], fill=BLUE)                                 # send button
    return im


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    road_sound().save(OUT / "road_sound.png")
    road_alligator().save(OUT / "road_alligator.png")
    road_mask().save(OUT / "road_mask.png")
    crack_closeup(16, 21).save(OUT / "crack_wide.png")
    crack_closeup(4, 31).save(OUT / "crack_fine.png")
    crack_closeup(4, 41, wet=True).save(OUT / "crack_wet.png")
    chat_screen().save(OUT / "chat_screen.png")
    print("wrote", ", ".join(p.name for p in sorted(OUT.glob("*.png"))))
