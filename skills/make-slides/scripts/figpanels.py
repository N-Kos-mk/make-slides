"""figpanels.py — find the panels of a figure (a paper's figure, a composite image) and cut out the ones a
slide needs. Needs Pillow.

  python figpanels.py <image> [--preview figures/_panels.png]
        list the panels: the figure is split along its white gutters (rows, then columns, recursively),
        and a picture of the figure with each panel boxed and numbered is written to --preview.
        Look at that picture, then choose the panels by number.

  python figpanels.py <image> --crop 2,3 --out figures/fig2_bc.png [--arrange row|col] [--gap 24]
                              [--pad 12] [--max-width 1400]
        cut out panels: one number = that panel; several = the box around them all, or, with --arrange,
        each panel cut on its own and set side by side (row) or one above the other (col), in the
        order given. The white margin around the result is trimmed to --pad.

  python figpanels.py <image> --box 120,40,980,610 --out figures/x.png
        cut out a box given in the image's own pixels (left, top, right, bottom), trimmed the same way.
        Several boxes, separated by ';', with --arrange col: rows picked from a table-like figure, set
        one above the other in the order given (keep the header row first, and the original order).

  python figpanels.py <image> --trim --out figures/x.png
        only trim the white margin of the whole image.

The split is geometry, not understanding: it finds white space between drawn regions. It is right for
most composite figures (panels on a white ground with gutters between them); it can cut a panel from
its letter or its axis title when they stand apart, which the numbered preview shows — then crop a
box or several numbers together. Which panel the slide needs is a judgement you make by looking.
Run it from the deck directory; read the material by its path and write only into figures/.
"""
import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("figpanels.py needs Pillow: python -m pip install pillow")

INK = 236            # a pixel darker than this (0-255 grey) is ink
BOX = getattr(Image, "Resampling", Image).BOX
LANCZOS = getattr(Image, "Resampling", Image).LANCZOS


def ink_mask(im):
    return im.convert("L").point(lambda v: 255 if v < INK else 0)


def profile(mask, box, axis):
    """Share of ink in every row (axis='y') or column (axis='x') of the box, 0-255."""
    crop = mask.crop(box)
    w, h = crop.size
    if axis == "y":
        return list(crop.resize((1, h), BOX).getdata())
    return list(crop.resize((w, 1), BOX).getdata())


def gutters(prof, min_gap, eps=2):
    """Runs of (almost) empty rows / columns at least min_gap long, not touching the ends."""
    runs, start = [], None
    for i, v in enumerate(prof + [255]):
        if v <= eps and start is None:
            start = i
        elif v > eps and start is not None:
            if start > 0 and i < len(prof) and i - start >= min_gap:
                runs.append((start, i))
            start = None
    return runs


def tight(mask, box):
    bb = mask.crop(box).getbbox()
    if not bb:
        return None
    return (box[0] + bb[0], box[1] + bb[1], box[0] + bb[2], box[1] + bb[3])


def split(mask, box, min_gap, depth=0):
    box = tight(mask, box)
    if box is None:
        return []
    if depth > 6:
        return [box]
    l, t, r, b = box
    gy = gutters(profile(mask, box, "y"), min_gap[1])
    gx = gutters(profile(mask, box, "x"), min_gap[0])
    if not gy and not gx:
        return [box]
    widest_y = max((e - s for s, e in gy), default=0)
    widest_x = max((e - s for s, e in gx), default=0)
    out = []
    if widest_y >= widest_x:
        cuts = [t] + [t + (s + e) // 2 for s, e in gy] + [b]
        for a, z in zip(cuts, cuts[1:]):
            out += split(mask, (l, a, r, z), min_gap, depth + 1)
    else:
        cuts = [l] + [l + (s + e) // 2 for s, e in gx] + [r]
        for a, z in zip(cuts, cuts[1:]):
            out += split(mask, (a, t, z, b), min_gap, depth + 1)
    return out


def merge_small(boxes, size):
    """Fold boxes too small to be a panel (a panel letter, a stray label) into their nearest neighbour."""
    W, H = size
    # too small or too thin to be a panel: a panel letter, an axis title, a strip of tick labels
    small = lambda bx: ((bx[2] - bx[0]) * (bx[3] - bx[1]) < 0.02 * W * H      # noqa: E731
                        or (bx[2] - bx[0]) < 0.06 * W or (bx[3] - bx[1]) < 0.06 * H)
    boxes = list(boxes)
    changed = True
    while changed and len(boxes) > 1:
        changed = False
        for i, bx in enumerate(boxes):
            if not small(bx):
                continue
            def dist(o):
                dx = max(o[0] - bx[2], bx[0] - o[2], 0)
                dy = max(o[1] - bx[3], bx[1] - o[3], 0)
                return (dx * dx + dy * dy) ** 0.5
            others = [o for j, o in enumerate(boxes) if j != i]
            near = min(others, key=dist)
            if dist(near) > 0.06 * max(W, H):
                continue
            boxes.remove(near)
            boxes.remove(bx)
            boxes.append((min(near[0], bx[0]), min(near[1], bx[1]), max(near[2], bx[2]), max(near[3], bx[3])))
            changed = True
            break
    # a merged box may now overlap another: merge those too, until no two boxes overlap
    changed = True
    while changed:
        changed = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                p, q = boxes[i], boxes[j]
                if min(p[2], q[2]) > max(p[0], q[0]) and min(p[3], q[3]) > max(p[1], q[1]):
                    boxes[i] = (min(p[0], q[0]), min(p[1], q[1]), max(p[2], q[2]), max(p[3], q[3]))
                    del boxes[j]
                    changed = True
                    break
            if changed:
                break
    return sorted(boxes, key=lambda bx: (round(bx[1] / (0.05 * H)), bx[0]))   # reading order: rows, then left to right


def panels(im):
    mask = ink_mask(im)
    W, H = im.size
    min_gap = (max(8, int(0.005 * W)), max(8, int(0.005 * H)))
    return merge_small(split(mask, (0, 0, W, H), min_gap), (W, H)), mask


def number_tag(n, px):
    """A white number on red, about px tall: a scalable font when one is found, else the built-in
    bitmap font enlarged (so the number is readable on a large figure with any Pillow)."""
    text = str(n)
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "Helvetica.ttc"):
        try:
            f = ImageFont.truetype(name, px)
            break
        except OSError:
            f = None
    if f is not None:
        probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        l, t, r, b = probe.textbbox((0, 0), text, font=f)
        tag = Image.new("RGB", (r - l + px // 2, b - t + px // 2), (200, 55, 45))
        ImageDraw.Draw(tag).text((px // 4 - l, px // 4 - t), text, fill="white", font=f)
        return tag
    small = ImageFont.load_default()
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    l, t, r, b = probe.textbbox((0, 0), text, font=small)
    tag = Image.new("RGB", (r - l + 4, b - t + 4), (200, 55, 45))
    ImageDraw.Draw(tag).text((2 - l, 2 - t), text, fill="white", font=small)
    k = max(1, round(px / tag.size[1]))
    return tag.resize((tag.size[0] * k, tag.size[1] * k), Image.NEAREST)


def preview(im, boxes, path):
    pv = im.convert("RGB").copy()
    d = ImageDraw.Draw(pv)
    lw = max(3, im.size[0] // 400)
    px = max(28, max(im.size) // 25)
    for i, (l, t, r, b) in enumerate(boxes, 1):
        d.rectangle((l, t, r, b), outline=(200, 55, 45), width=lw)
        pv.paste(number_tag(i, px), (l, t))
    path.parent.mkdir(parents=True, exist_ok=True)
    pv.save(path)


def trimmed(im, mask, box, pad):
    bb = tight(mask, box) or box
    l, t, r, b = bb
    out = Image.new("RGB", (r - l + 2 * pad, b - t + 2 * pad), "white")
    out.paste(im.convert("RGB").crop(bb), (pad, pad))
    return out


def arrange(parts, how, gap):
    if how == "row":
        w = sum(p.size[0] for p in parts) + gap * (len(parts) - 1)
        h = max(p.size[1] for p in parts)
        out = Image.new("RGB", (w, h), "white")
        x = 0
        for p in parts:
            out.paste(p, (x, (h - p.size[1]) // 2))
            x += p.size[0] + gap
    else:
        w = max(p.size[0] for p in parts)
        h = sum(p.size[1] for p in parts) + gap * (len(parts) - 1)
        out = Image.new("RGB", (w, h), "white")
        y = 0
        for p in parts:
            out.paste(p, ((w - p.size[0]) // 2, y))
            y += p.size[1] + gap
    return out


def save(out, path, max_width):
    if max_width and out.size[0] > max_width:
        out = out.resize((max_width, round(out.size[1] * max_width / out.size[0])), LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in (".jpg", ".jpeg"):
        out.save(path, quality=90)
    else:
        out.save(path)
    print(f"wrote {path} ({out.size[0]}x{out.size[1]} px)")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("image")
    ap.add_argument("--preview")
    ap.add_argument("--crop", help="panel numbers, e.g. 2 or 2,3")
    ap.add_argument("--box", help="left,top,right,bottom in the image's pixels")
    ap.add_argument("--trim", action="store_true")
    ap.add_argument("--arrange", choices=("row", "col"))
    ap.add_argument("--gap", type=int, default=24)
    ap.add_argument("--pad", type=int, default=12)
    ap.add_argument("--max-width", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args()
    im = Image.open(a.image)
    im.load()
    found, mask = panels(im)
    W, H = im.size
    if not (a.crop or a.box or a.trim):
        print(f"{Path(a.image).name}: {W}x{H} px, {len(found)} panels (left, top, right, bottom)")
        for i, (l, t, r, b) in enumerate(found, 1):
            print(f"  {i:2}  {l:5},{t:5},{r:5},{b:5}   {r - l}x{b - t} px")
        if a.preview:
            preview(im, found, Path(a.preview))
            print(f"preview: {a.preview} — look at it and choose panels by number")
        return
    if not a.out:
        sys.exit("--out is required with --crop / --box / --trim")
    if a.box:
        boxes = []
        for spec in a.box.split(";"):
            l, t, r, b = (int(float(v)) for v in spec.split(","))
            boxes.append((max(0, l), max(0, t), min(W, r), min(H, b)))
        if a.arrange and len(boxes) > 1:
            joined = arrange([trimmed(im, mask, bx, 0) for bx in boxes], a.arrange, a.gap)
            parts = [trimmed(joined, ink_mask(joined), (0, 0) + joined.size, a.pad)]
        else:
            u = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
            parts = [trimmed(im, mask, u, a.pad)]
    elif a.trim:
        parts = [trimmed(im, mask, (0, 0, W, H), a.pad)]
    else:
        ids = [int(v) for v in a.crop.split(",")]
        bad = [i for i in ids if not 1 <= i <= len(found)]
        if bad:
            sys.exit(f"no panel {bad}: the figure has panels 1-{len(found)} (run without --crop to list them)")
        boxes = [found[i - 1] for i in ids]
        if a.arrange and len(boxes) > 1:
            parts = [arrange([trimmed(im, mask, bx, 0) for bx in boxes], a.arrange, a.gap)]
            parts = [trimmed(parts[0], ink_mask(parts[0]), (0, 0) + parts[0].size, a.pad)]
        else:
            u = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
            parts = [trimmed(im, mask, u, a.pad)]
    save(parts[0], Path(a.out), a.max_width)


if __name__ == "__main__":
    main()
