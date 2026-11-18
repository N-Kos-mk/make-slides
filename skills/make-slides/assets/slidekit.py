"""slidekit v2 — write a make-slides deck in Python; the library writes the HTML.

    import slidekit as sk

    deck = sk.Deck(title="発表タイトル", minutes=10, ratio="16:9", date="2026/9/16")
    deck.cover(event="○○発表会", lines=["所属", "氏名", "2026年9月16日"], sec=15)
    deck.slide(
        "結果 - 精度",                              # heading: the part of the talk (+ " - topic")
        "**幅1mm未満**のひび割れも9割を検出",          # message: one short claim, no 「、」; bold marks its point
        sk.bars(data, hot=["幅1mm未満"]),            # the figure is the main thing on the slide
        sk.points(["…"]),                            # then at most three full-line bullets …
        sk.conclusion("…"),                          # … or one bold centred line
        sec=60, notes="話す内容はここに書く（スライドには出ない）",
    )
    deck.save()          # writes deck.html next to this script

Every content slide has the same anatomy: heading -> message -> figure -> a few words.
The slide does not explain everything; the speaker does. What you would say aloud goes to notes=.

You describe WHAT is on the slide; the theme decides how it looks. There is no way to set a font
size, a colour or a margin from here, on purpose.

Inline markup understood in every text argument:
    **語**      bold keyword                [[語]]   the accent colour
    !!語!!      red (the one thing to look at; once per slide at most)
    [1] [2][3]  citation marks              $x_j$    inline math (KaTeX)
    \\n          line break — YOU choose where a line breaks, at a phrase boundary
Everything else is escaped, so "<", ">" and "&" are safe to type.

Reference for every function: references/layouts.md in the skill.
"""
from __future__ import annotations

import builtins
import html as _html
import re
import struct
import sys
from pathlib import Path

__version__ = "2.4"

HERE = Path(__file__).resolve().parent
try:
    ROOT = Path(sys.argv[0]).resolve().parent if sys.argv and str(sys.argv[0]).endswith(".py") else Path.cwd()
except Exception:  # pragma: no cover
    ROOT = Path.cwd()


class DeckError(Exception):
    """Raised when a component is used in a way the theme does not support."""


def _err(msg: str):
    raise DeckError(msg)


_WARNINGS: list = []


def _warn(msg: str):
    if msg not in _WARNINGS:
        _WARNINGS.append(msg)


class H(str):
    """A string that is already HTML (returned by every component)."""


# --------------------------------------------------------------------------------------------
# geometry (mirror of theme/slide.css + ratio files)
# --------------------------------------------------------------------------------------------
_GEOM = {
    "16:9": {"w": 1280, "h": 720, "pad_x": 72, "gutter": 40, "css": "16x9"},
    "4:3": {"w": 960, "h": 720, "pad_x": 56, "gutter": 32, "css": "4x3"},
}
_BODY_H = 506          # px under heading + message (553 when the slide has no message)
_PX = {"head": 45.33, "msg": 29.33, "body": 26.67}
_RATIOS = {"6-6": 2, "5-7": 2, "7-5": 2, "4-8": 2, "8-4": 2, "4-4-4": 3}
_RATIO = "16:9"        # ratio of the deck being built (set by Deck); used for length checks


def span_px(n: int, ratio: str = "16:9") -> int:
    """Width in px of an n-column span of the 12-column grid (12 = full content width)."""
    g = _GEOM[ratio]
    content = g["w"] - 2 * g["pad_x"]
    unit = (content - 11 * g["gutter"]) / 12
    return int(n * unit + (n - 1) * g["gutter"])


def _content_w() -> int:
    g = _GEOM[_RATIO]
    return g["w"] - 2 * g["pad_x"]


# --------------------------------------------------------------------------------------------
# text
# --------------------------------------------------------------------------------------------
_CITE = re.compile(r"((?:\[\d{1,3}\])+)")
_JA = re.compile(r"[぀-ヿ㐀-鿿]")


def inline(text) -> str:
    """Escape text and apply the inline markup. Already-built HTML (H) passes through."""
    if isinstance(text, H):
        return str(text)
    if text is None:
        return ""
    if not isinstance(text, (str, int, float)):
        _err(f"expected text, got {type(text).__name__}: {text!r}")
    s = _html.escape(str(text), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[\[(.+?)\]\]", r'<span class="key">\1</span>', s)
    s = re.sub(r"!!(.+?)!!", r'<span class="alert">\1</span>', s)
    s = _CITE.sub(r'<cite class="ref">\1</cite>', s)
    return s.replace("\n", "<br>")


def _plain(text) -> str:
    """The text as the audience reads it: markup, citation marks and math delimiters removed."""
    t = re.sub(r"\*\*|\[\[|\]\]|!!", "", str(text))
    t = _CITE.sub("", t)
    return t


def _units(text) -> float:
    """Approximate width of one line in full-width characters (1.0 = one kanji)."""
    n = 0.0
    for ch in _plain(text).replace("$", ""):
        o = ord(ch)
        if o > 0x2E7F or ch in "、。「」（）・〜→":
            n += 1.0
        elif ch == " ":
            n += 0.3
        elif ch.isupper():
            n += 0.68
        elif ch.isdigit():
            n += 0.58
        elif ch in ".,:;'|!()[]":
            n += 0.32
        else:
            n += 0.54
    return n


def _lines(text, what: str, per_line: float, max_lines: int) -> str:
    """Display text (message, conclusion, boxed): never auto-wrapped. The author breaks it with \\n."""
    if not isinstance(text, str) or not text.strip():
        _err(f"{what}: expected a short text")
    lines = text.strip().split("\n")
    if len(lines) > max_lines:
        _err(f"{what}: {len(lines)} lines (max {max_lines}). Cut words — the rest is said aloud: {text!r}")
    for ln in lines:
        if _units(ln) > per_line:
            _err(f"{what}: the line {ln!r} is about {_units(ln):.0f} characters wide; one line holds {per_line:.0f}. "
                 "Shorten it, or break it with \\n at a phrase boundary so that the lines have similar lengths")
    return inline("\n".join(ln.strip() for ln in lines))


def _ind(s: str, n: int = 2) -> str:
    pad = " " * n
    return "\n".join((pad + ln if ln else ln) for ln in str(s).split("\n"))


def _cls(*names) -> str:
    return " ".join(n for n in names if n)


def _flat(items) -> list:
    """Children of a container: components as they are; a bare string is not allowed."""
    out = []
    for it in items:
        if it is None:
            continue
        if isinstance(it, H):
            out.append(it)
        elif isinstance(it, str):
            _err(f"a bare string cannot be placed on a slide: {it!r}. Use sk.points([...]) for bullets, "
                 "sk.conclusion(...) for the one-line conclusion, or move the sentence to notes=")
        elif isinstance(it, (list, tuple)):
            out.extend(_flat(it))
        else:
            _err(f"cannot place {type(it).__name__} on a slide: {it!r}")
    return out


def raw(html: str) -> H:
    """Escape hatch: hand-written HTML. Use theme classes only; the linter still measures it."""
    return H(html)


def note(text) -> H:
    """A small grey remark: a condition or a caveat (14pt, centred). At most one per slide."""
    return H(f'<p class="note">{inline(text)}</p>')


def source(text) -> H:
    """A source line (12pt), the last thing in the body."""
    return H(f'<p class="source">{inline(text)}</p>')


# --------------------------------------------------------------------------------------------
# words: bullets, the conclusion line, the framed statement
# --------------------------------------------------------------------------------------------
def points(items, *, size=None, tone=None) -> H:
    """Bullets. One level, at most five; next to a figure, at most three.

    The list is flush left at the margin, on the same edge as the heading. It is never centred
    (only a list inside a column of cols() is centred, in its column). So the bullets must carry
    their width: each is ONE LINE THAT REACHES WELL ACROSS THE SLIDE — a fact with its number,
    its condition or its source — not a keyword that leaves the right half empty.
        × "精度は不十分"                       (a stub: the slide tips to the left)
        ○ "幅1mm未満のひび割れは目視点検でも3割を見落とし[2]"
    If there is too little to say for that, do not use a list: use conclusion() (one centred
    line), or put the list beside the figure with cols().

    items: noun-ending phrases, roughly 60–90% of the line (about 18–28 characters at 4:3).
           Lines are never wrapped for you. A bullet that fits on one line stays on one line; one
           that does not is broken by YOU with \\n at the phrase boundary nearest the end of the
           line, so that the first line is long — a list on its own is not balanced by breaking
           lines early (that empties the right side; lint T10). A consequence goes on a second
           line that starts with "→", and is no longer than the line it follows:
               "細いひび割れをどこまで画像で拾えるか\\n→実際の路面では未検証"
           Parentheses at most once per bullet; put a qualifier in front of its noun instead
           ("研修を修了した経験5年以上の点検員が判定", not "点検員が判定（経験5年以上・研修修了）").
           A bullet that later slides refer to may start with a bold label: "**[仮説1]** …".
    size:  None | 'large' (24pt — a text-only slide; for the summary use summary())
    tone:  None | 'accent' (blue)
    """
    if isinstance(items, (str, H)):
        items = [items]
    items = list(items)
    if not items:
        _err("points(): no items")
    if len(items) > 5:
        _err(f"points(): {len(items)} bullets. Five is the limit (three next to a figure): "
             "keep what the audience must read, say the rest aloud (notes=)")
    if size not in (None, "large") or tone not in (None, "accent"):
        _err("points(): size is None or 'large'; tone is None or 'accent'")
    cap = _content_w() / (32.0 if size == "large" else _PX["body"]) - 1.4
    lis = []
    for it in items:
        if isinstance(it, H):
            lis.append(f"  <li>{it}</li>")
            continue
        if not isinstance(it, str):
            _err(f"points(): bullets have one level only (no sub-items, no grey second line): {it!r}. "
                 "Make it its own bullet, or say it aloud")
        parts = [p.strip() for p in it.split("\n") if p.strip()]
        if len(parts) > 2:
            _err(f"points(): a bullet of {len(parts)} lines is a paragraph: {it!r}. Two lines at most; say the rest aloud")
        for ln in parts:
            if _units(ln) > cap:
                _err(f"points(): the line {ln!r} is about {_units(ln):.0f} characters wide; one line holds {cap:.0f}. "
                     "Lines are never wrapped for you: cut words (say them aloud), or break the bullet with \\n "
                     "where the meaning turns so that the two lines have similar lengths")
        html = inline(parts[0])
        for extra in parts[1:]:
            if extra.startswith(("→", "->", "⇒")):
                html += f'<span class="then">{inline(extra.lstrip("→⇒->").strip())}</span>'
            else:
                html += "<br>" + inline(extra)
        lis.append(f"  <li>{html}</li>")
    c = _cls("points", "large" if size == "large" else "", "accent" if tone == "accent" else "")
    return H(f'<ul class="{c}">\n' + "\n".join(lis) + "\n</ul>")


def conclusion(text) -> H:
    """One bold centred line with no box: what the slide comes to. One per slide.

    Up to two lines; break with \\n at a phrase boundary so the lines have similar lengths.
    """
    per = _content_w() / _PX["msg"] - 1
    return H(f'<p class="conclusion">{_lines(text, "conclusion()", per, 2)}</p>')


def boxed(text) -> H:
    """A framed statement (the purpose, the research question). The frame hugs the text.

    Up to three lines; break with \\n yourself. Use it once in a deck, twice at most.
    """
    per = (_content_w() - 66) / _PX["msg"] - 1
    return H(f'<p class="boxed">{_lines(text, "boxed()", per, 3)}</p>')


_ARROW_DOWN = ('<svg class="arrow-down" width="72" height="70" viewBox="0 0 58 56" aria-hidden="true">'
               '<path d="M18 0h22v27h16L29 56 2 27h16z"/></svg>')


def therefore(premises, result) -> H:
    """Premises -> a thick arrow -> one framed statement. The shape of a "purpose" slide.

    The three form one composition on the centre line: here the list of premises is centred as a
    block (its lines flush left inside it), with the arrow and the frame under it. Premises that
    reach the right edge look flush left anyway; shorter ones would otherwise leave the right
    side empty beside a centred arrow and frame. Full lines are still better than stubs.

    premises: 2–4 bullets, each a full line (what is known / what is missing, with the specifics)
    result:   the purpose in one line (\\n for a second line); set a size larger than boxed()
    """
    per = (_content_w() - 86) / 32.0 - 1                     # 24pt inside the frame of the purpose
    frame = H(f'<p class="boxed">{_lines(result, "therefore(): the purpose", per, 3)}</p>')
    # the purpose slide has the whole body for three lines and a frame: set the premises large
    # when every line fits at 24pt, so that the composition fills the slide
    items = [premises] if isinstance(premises, str) else list(premises)
    cap_large = _content_w() / 32.0 - 1.4
    fits = all(_units(ln) <= cap_large for it in items if isinstance(it, str) for ln in it.split("\n"))
    lst = points(items, size="large" if fits else None)
    return H('<div class="therefore">\n' + _ind(lst) + f"\n  {_ARROW_DOWN}\n" + _ind(frame) + "\n</div>")


def _sparse(items, size, who: str) -> None:
    """Warn when a top-level list is too thin to carry the width of the slide."""
    cap = _content_w() / (32.0 if size == "large" else _PX["body"]) - 1.4
    lines = [ln for it in ([items] if isinstance(items, str) else items) if isinstance(it, str) for ln in it.split("\n")]
    longest = builtins.max((_units(ln) for ln in lines), default=0)
    if longest < (0.65 if _RATIO == "16:9" else 0.7) * cap:
        _warn(f"{who}: the longest line is about {longest:.0f} characters; a line holds {cap:.0f}. A list is flush left, so "
              "stubs leave the right half of the slide empty. Write fuller bullets — the fact with its number, condition "
              "or source, not more adjectives — or use another form (conclusion(), or the list beside the figure in cols())")


def summary(conclusions, future=None) -> H:
    """The summary slide: the conclusions (black), then what comes next (blue), in large bullets.

    Both lists are flush left at the margin. Each bullet is a full line (or two).
    Five bullets in all at most; same line rules as points().
    """
    conclusions = [conclusions] if isinstance(conclusions, str) else list(conclusions)
    future = [future] if isinstance(future, str) else list(future or [])
    if len(conclusions) + len(future) > 5:
        _err("summary(): five bullets in all at most (two or three conclusions, then what comes next)")
    _sparse(conclusions + future, "large", "summary()")
    parts = [points(conclusions, size="large")]
    if future:
        parts.append(points(future, size="large", tone="accent"))
    return H('<div class="summary">\n' + "\n".join(_ind(p) for p in parts) + "\n</div>")


# --------------------------------------------------------------------------------------------
# images
# --------------------------------------------------------------------------------------------
def _image_size(path: Path):
    """Intrinsic size in CSS px for svg/png/jpeg/gif, or None."""
    data = path.read_bytes()
    suf = path.suffix.lower()
    if suf == ".svg":
        head = data[:4000].decode("utf-8", "ignore")
        m = re.search(r"<svg\b[^>]*>", head, re.S)
        if not m:
            return None
        tag = m.group(0)

        def dim(name):
            mm = re.search(rf'\b{name}="([\d.]+)\s*(pt|px|in|mm|cm)?"', tag)
            if not mm:
                return None
            k = {"pt": 96 / 72, "px": 1, None: 1, "in": 96, "mm": 96 / 25.4, "cm": 96 / 2.54}[mm.group(2)]
            return float(mm.group(1)) * k

        w, hh = dim("width"), dim("height")
        if w and hh:
            return w, hh
        vb = re.search(r'viewBox="[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)"', tag)
        return (float(vb.group(1)), float(vb.group(2))) if vb else None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, hh = struct.unpack(">II", data[16:24])
        return float(w), float(hh)
    if data[:6] in (b"GIF87a", b"GIF89a"):
        w, hh = struct.unpack("<HH", data[6:10])
        return float(w), float(hh)
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                hh, w = struct.unpack(">HH", data[i + 5:i + 9])
                return float(w), float(hh)
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def _src(src) -> str:
    return _html.escape(str(src).replace(chr(92), "/"))


def _need_file(src, who: str) -> Path:
    path = ROOT / src
    if not path.exists():
        _err(f"{who}: file not found: {path}")
    return path


def fig(src, *, width=None, fill: bool = False, caption=None, alt: str = "", shot: bool = False) -> H:
    """An image file (path relative to the deck directory), centred.

    SVG figures made with new_fig()/save_fig() are placed at their own size — do not pass width;
    to change the size, regenerate the figure.
    Photos and screenshots: fill=True lets the image take all the height the slide has left
    (the usual choice), or pass width in px. shot=True draws a hairline around a screenshot.
    caption: one short line under the image; leave it out when the message already says it.
    """
    path = _need_file(src, "fig()")
    size = _image_size(path)
    is_svg = path.suffix.lower() == ".svg"
    if is_svg:
        if size is None:
            _err(f"fig(): cannot read the size of {src}")
        if fill or (width is not None and abs(width - size[0]) > 1):
            _err(f"fig(): {src} is {size[0]:.0f}px wide; an SVG is never scaled on the slide (its text would change size) "
                 "— regenerate it at the size you want")
        attrs = f' width="{size[0]:.0f}" height="{size[1]:.0f}"'
    elif fill:
        if width is not None:
            _err("fig(): pass fill=True or width=, not both")
        if size and size[0] < 700:
            _warn(f"{src} is only {size[0]:.0f}px wide; it will look soft when it fills the slide")
        attrs = ""
    else:
        if width is None:
            _err(f"fig(): pass fill=True (take the free height) or width= (px on the slide) for the image {src}")
        if size and size[0] / width < 1.3:
            _warn(f"{src} has {size[0]:.0f}px for {width}px on the slide; it will look soft (want >= {int(width * 1.5)}px)")
        attrs = f' width="{int(width)}"'
    img = f'<img{" class=" + chr(34) + "shot" + chr(34) if shot else ""} src="{_src(src)}"{attrs} alt="{_html.escape(alt)}">'
    cap = f"\n  <figcaption>{inline(caption)}</figcaption>" if caption else ""
    return H(f'<figure class="{_cls("fig", "fill" if fill else "")}">\n  {img}{cap}\n</figure>')


class _Sample(dict):
    pass


def sample(src, value=None, note=None, *, tone=None, alt: str = "", shot: bool = True) -> _Sample:  # noqa: A002
    """One image of samples(): the picture, the value read off it, and (rarely) one short remark.

    src:   image path relative to the deck directory
    value: the number or word this example stands for ('0.11', '6.5点'); set large and bold
    note:  one short grey line (e.g. '平均評定 6.48点') — only if the comparison needs it
    tone:  None | 'accent' | 'hot' — colour of the value
    """
    if tone not in (None, "accent", "hot"):
        _err("sample(): tone is None, 'accent' or 'hot'")
    return _Sample(src=src, value=value, note=note, tone=tone, alt=alt, shot=shot)


def samples(*items, caption=None, tight: bool = False, small: bool = False, stack: bool = False) -> H:
    """Real examples side by side — screenshots, photos, outputs — each with its value underneath.

    samples(sample('figures/a.png', '0.11', '平均評定 6.48点'), sample('figures/b.png', '0.38', '平均評定 1.74点'))
    The images share the height the slide has left, so the examples are as large as they can be.
    2 images for a contrast; up to 6 for a series (tight=True narrows the gaps, small=True the values).
    stack=True puts them one above the other — for a column beside a plot.
    """
    if len(items) == 1 and isinstance(items[0], (list, tuple)) and not isinstance(items[0], _Sample):
        items = tuple(items[0])
    if not 2 <= len(items) <= 6:
        _err("samples() takes 2 to 6 images; for a single image use fig(..., fill=True)")
    out = []
    for it in items:
        if isinstance(it, (list, tuple)):
            it = sample(*it)
        elif isinstance(it, str):
            it = sample(it)
        if not isinstance(it, _Sample):
            _err(f"samples(): use sample(path, value, note) for each image; got {it!r}")
        path = _need_file(it["src"], "samples()")
        size = _image_size(path)
        if size and size[0] < 480:
            _warn(f"{it['src']} is only {size[0]:.0f}px wide; it will look soft on the slide")
        img = (f'<img{" class=" + chr(34) + "shot" + chr(34) if it["shot"] else ""} src="{_src(it["src"])}" '
               f'alt="{_html.escape(it["alt"])}">')
        cap = ""
        if it["value"] is not None or it["note"]:
            v = f'<span class="{_cls("sample-value", it["tone"] or "")}">{inline(it["value"])}</span>' if it["value"] is not None else ""
            n = f'<span class="sample-note">{inline(it["note"])}</span>' if it["note"] else ""
            cap = f"\n    <figcaption>{v}{n}</figcaption>"
        out.append(f'  <figure class="sample">\n    {img}{cap}\n  </figure>')
    c = _cls("samples", "tight" if tight else "", "sm" if small else "", "stack" if stack else "")
    inner = f'<div class="{c}">\n' + "\n".join(out) + "\n</div>"
    cap = f'\n  <p class="samples-caption">{inline(caption)}</p>' if caption else ""
    return H('<div class="samples-wrap">\n' + _ind(inner) + cap + "\n</div>")


# --------------------------------------------------------------------------------------------
# bar charts drawn in HTML: they take the height the slide has left, in the deck's own type
# --------------------------------------------------------------------------------------------
def _num(v, who: str, label) -> float:
    try:
        return float(str(v).replace(",", "").replace("−", "-").replace("+", ""))
    except ValueError:
        _err(f"{who}: value {v!r} for {label!r} is not a number")


def _mark(label, idx, highlight, light, hot) -> str:
    def hit(key):
        if isinstance(key, (str, int)):
            key = [key]
        return label in key or idx in [k for k in key if isinstance(k, int) and not isinstance(k, bool)]
    return "hot" if hit(hot) else ("hl" if hit(highlight) else ("hl2" if hit(light) else ""))


def bars(data, *, highlight=(), light=(), hot=(), axis_max=None, title=None, signed: bool = False,
         ends=None) -> H:
    """Horizontal bar chart: rankings, breakdowns — every bar carries its value.

    data:      [(label, value), …]. value is a number, or a string such as '11.0' to fix the printed digits.
               Sort it yourself (largest first, unless the order means something).
    hot:       labels (or indexes) drawn in red  — the bars the slide is about.
    highlight: labels drawn in dark blue         — the subject, when nothing needs red.
    light:     labels drawn in light blue        — a variant of the subject.
               Everything else is grey: it is there only for comparison.
    axis_max:  value at the right end (default: the largest value). A round number just above the
               largest value — never a total far beyond the data (the bars would stop short and
               leave the right side of the chart empty). If the share of a total is the point,
               chart the share.
    title:     what the numbers are, with the unit ('寄与（%）') — small, above the chart.
    signed:    True for values with a sign: bars grow left / right from a centre line.
    ends:      with signed=True, what each direction means, written under the two ends of the axis:
               ends=("晴天より低い", "晴天より高い"). Without it the audience has to work out what a
               bar to the left means; give it whenever that is not obvious.
    """
    rows_, vals = [], []
    for i, it in enumerate(data):
        if not isinstance(it, (list, tuple)) or len(it) != 2:
            _err(f"bars(): each entry is (label, value); got {it!r}")
        label, v = it
        f = _num(v, "bars()", label)
        if f < 0 and not signed:
            _err("bars(): negative value; pass signed=True")
        vals.append(f)
        rows_.append((label, f, v if isinstance(v, str) else f"{v:g}", _mark(label, i, highlight, light, hot)))
    if not vals:
        _err("bars(): no data")
    top = float(axis_max) if axis_max is not None else builtins.max(abs(v) for v in vals)
    biggest = builtins.max(abs(v) for v in vals)
    if top <= 0 or top < biggest:
        _err("bars(): axis_max must be at least the largest value")
    if biggest < 0.6 * top:
        _warn(f"bars(): axis_max={top:g} but the largest value is {biggest:g}; the bars stop short and the right side of "
              "the chart is empty. Set axis_max just above the largest value. If a total (a time limit, a maximum) "
              "matters, say it in the title or a bullet, or chart the share of it")
    if ends is not None:
        if not signed:
            _err("bars(): ends= labels the two directions of signed bars; pass signed=True")
        if not (isinstance(ends, (list, tuple)) and len(ends) == 2 and all(isinstance(e, str) for e in ends)):
            _err('bars(): ends=("what a bar to the left means", "what a bar to the right means")')
    out = []
    for label, f, disp, mod in rows_:
        if signed:
            if not disp.startswith(("+", "−", "-")) and f > 0:
                disp = "+" + disp
            disp = disp.replace("-", "−")
            out.append(
                f'  <div class="{_cls("bar", mod)}"><span class="bar-label">{inline(label)}</span>'
                f'<span class="bar-track {"pos" if f >= 0 else "neg"}" style="--f: {abs(f) / top:.4f}"><i></i>'
                f'<span class="bar-val">{inline(disp)}</span></span></div>')
        else:
            out.append(
                f'  <div class="{_cls("bar", mod)}"><span class="bar-label">{inline(label)}</span>'
                f'<span class="bar-track"><i style="--f: {f / top:.4f}"></i><span class="bar-val">{inline(disp)}</span></span></div>')
    if ends is not None:
        out.append(f'  <span class="bar-label"></span><span class="bar-ends"><span>{inline(ends[0])}</span>'
                   f'<span>{inline(ends[1])}</span></span>')
    head = f'  <p class="chart-title">{inline(title)}</p>\n' if title else ""
    extra = (30 if title else 0) + (34 if ends is not None else 0)
    style = f"--n: {len(rows_)}" + (f"; --extra: {extra}px" if extra else "")
    c = _cls("bars", "signed" if signed else "", "dense" if len(rows_) >= 9 else "", "has-ends" if ends is not None else "")
    return H(f'<div class="chart bars-chart" style="{style}">\n{head}'
             f'  <div class="{c}">\n' + "\n".join("  " + o for o in out) + "\n  </div>\n</div>")


def vbars(data, *, highlight=(), light=(), hot=(), axis_max=None, title=None) -> H:
    """Vertical bar chart: a few values to compare (2–7 bars), every bar with its value on top.

    data:  [(label, value), …]; a label may contain \\n. Same colour options as bars().
    title: what the numbers are ('決定係数 R²') — small, above the chart.
    Put two charts side by side with cols() when the numbers are of different kinds:
    never mix kinds in one chart.
    """
    if not 2 <= len(data) <= 7:
        _err("vbars() takes 2 to 7 bars; for more, use bars()")
    vals = [_num(v, "vbars()", label) for label, v in data]
    if builtins.min(vals) < 0:
        _err("vbars() draws non-negative values; use bars(signed=True)")
    top = float(axis_max) if axis_max is not None else builtins.max(vals)
    if top <= 0 or top < builtins.max(vals):
        _err("vbars(): axis_max must be at least the largest value")
    out = []
    for i, ((label, v), f) in enumerate(zip(data, vals)):
        mod = _mark(label, i, highlight, light, hot)
        disp = v if isinstance(v, str) else f"{v:g}"
        out.append(f'    <div class="{_cls("vbar", mod)}"><div class="vbar-plot"><span class="vbar-val">{inline(disp)}</span>'
                   f'<i style="--f: {f / top:.4f}"></i></div><div class="vbar-label">{inline(label)}</div></div>')
    head = f'  <p class="chart-title">{inline(title)}</p>\n' if title else ""
    return H(f'<div class="chart vbars-chart">\n{head}  <div class="vbars" style="--n: {len(out)}">\n'
             + "\n".join(out) + "\n  </div>\n</div>")


def shares(rows, *, parts, title, hot=None, highlight=None, unit: str = "%") -> H:
    """Bars that each run to 100%, split into named parts: what share of a whole each part is.

    rows:  [(name of the whole, [value of each part, in the order of parts]), …] — one bar per whole:
           [("導入前", ["38", "62"]), ("導入後", ["71", "29"])]. Every row is split into the SAME parts,
           and the rows are wholes of one kind (before / after, group A / group B). Shares of
           different wholes (all inquiries; the inquiries by phone) are separate charts, never rows
           of one. Values are printed as given ('38.5' keeps its digit); the widths are shares of the
           row's total, so counts work too (unit='件').
    parts: the names of the parts, in words the audience knows without the speaker: 「自動で回答」
           「担当者が対応」. A code or a grade they do not know (「等級A〜C」) is named by what it
           means (「補修が不要な区間」). The part the slide is about comes first, so that its bars
           start together at the left and can be compared.
    title: what 100% is, and the unit — the whole, named: '問い合わせ全体に占める割合（%）'. Required:
           a share whose whole is not named cannot be read.
    hot / highlight: the part (its name or index) the slide is about — red / dark blue. The other
           parts are greys. Every segment carries its value; the name goes in too wherever it fits.
    2–4 parts, each wide enough to hold its name in at least one bar. For more parts, or small
    ones, chart the shares with bars(), sorted.
    """
    if not isinstance(title, str) or not title.strip():
        _err("shares(): title= says what 100% is and the unit — '問い合わせ全体に占める割合（%）'. "
             "A share whose whole is not named cannot be read")
    parts = list(parts)
    if not 2 <= len(parts) <= 4 or not all(isinstance(p, str) and p.strip() for p in parts):
        _err("shares(): parts= names 2 to 4 parts; for more, chart the shares with bars(), sorted")
    rows = list(rows)
    if not rows:
        _err("shares(): no rows")
    for it in rows:
        if not (isinstance(it, (list, tuple)) and len(it) == 2 and isinstance(it[0], str)
                and isinstance(it[1], (list, tuple))):
            _err(f"shares(): each row is (name of the whole, [values of the parts]); got {it!r}")
        if len(it[1]) != len(parts):
            _err(f"shares(): the row {it[0]!r} has {len(it[1])} values for {len(parts)} parts. Every row is split "
                 "into the same parts; a whole split into other parts is a chart of its own")

    def idx(key, what):
        if key is None:
            return None
        if isinstance(key, int) and not isinstance(key, bool) and 0 <= key < len(parts):
            return key
        if key in parts:
            return parts.index(key)
        _err(f"shares(): {what}={key!r} is not one of the parts {parts}")
    i_hot, i_hl = idx(hot, "hot"), idx(highlight, "highlight")
    # rough fit: the track is the content width less the row names; a full-width character at 17pt
    # is about 22.7px. lint measures the real widths (O3).
    per = 22.67
    track = _content_w() - builtins.max(_units(r[0]) for r in rows) * per - 14
    greys = iter(("p1", "p2", "p3", "p3"))
    tone = [("hot" if k == i_hot else "hl" if k == i_hl else None) for k in range(len(parts))]
    tone = [t or next(greys) for t in tone]
    named = [False] * len(parts)
    body = []
    for name, vals in rows:
        nums = [_num(v, "shares()", name) for v in vals]
        if builtins.min(nums) < 0:
            _err("shares(): shares are not negative")
        total = sum(nums)
        if total <= 0:
            _err(f"shares(): the row {name!r} adds up to 0")
        segs = []
        for k, (v, f) in enumerate(zip(vals, nums)):
            if f == 0:
                continue
            disp = (v if isinstance(v, str) else f"{v:g}") + (unit or "")
            w = f / total * track
            with_name = (_units(parts[k]) + _units(disp)) * per + 34 <= w
            if not with_name and _units(disp) * per + 20 > w:
                _err(f"shares(): the part {parts[k]!r} ({disp}) of {name!r} is too narrow to carry its value; "
                     "merge small parts into one, or chart the shares with bars()")
            named[k] = named[k] or with_name
            label = (f'<span class="share-name">{inline(parts[k])}</span>' if with_name else "") + \
                f'<span class="share-val">{inline(disp)}</span>'
            segs.append(f'<i class="share-seg {tone[k]}" style="--f: {f / total:.4f}">{label}</i>')
        body.append(f'    <span class="share-label">{inline(name)}</span><span class="share-track">{"".join(segs)}</span>')
    for k, ok in enumerate(named):
        if not ok:
            _err(f"shares(): the part {parts[k]!r} is too narrow in every bar to be named in it. Shorten its "
                 "name, merge small parts into one, or chart the shares with bars()")
    return H(f'<div class="chart shares-chart" style="--n: {len(rows)}">\n  <p class="chart-title">{inline(title)}</p>\n'
             '  <div class="shares">\n' + "\n".join(body) + "\n  </div>\n</div>")


def legend(*entries) -> H:
    """Colour key, only when a chart has 2+ colours that the labels do not explain:
    legend(('補修が必要な区間', 'hot'), ('その他', None))
    """
    out = []
    for name, colour in entries:
        if colour not in (None, "accent", "light", "hot"):
            _err("legend colours are 'accent' (dark blue), 'light' (light blue), 'hot' (red) or None (grey)")
        out.append(f'<span class="{_cls("k", colour or "")}">{inline(name)}</span>')
    return H('<div class="legend">' + "".join(out) + "</div>")


# --------------------------------------------------------------------------------------------
# flow: things in boxes, operations on the arrows
# --------------------------------------------------------------------------------------------
class _Thing(dict):
    pass


class _Op(str):
    pass


_OPLIKE = re.compile(r"(する|化|計算|算出|抽出|分析|解析|学習|回帰|推定|分解|選択|処理|変換|収集|検証|比較|集計|分類|検出|生成|最適化|フィルタ|クラスタリング)$")


def thing(label, *, img=None, value=None, values=None, media=None, width: int = 132, accent: bool = False) -> _Thing:
    """A box of flow(): a THING — data, an artefact, a result. Never an action.

    A box SHOWS the thing, it does not just name it. A flow of bare words is a list with arrows
    drawn through it; what makes it a figure is what is inside the boxes — one real case walking
    through the pipeline:

    label:  a noun, one line, no sub-label ('路面画像', 'ひび割れ画素', '区間の指標')
    img:    the thing is a picture: the actual image (path), `width` px wide
    values: the thing is a set of numbers: [(name, number), …] — three to five real values of
            this case, then (optionally) a last entry with an empty number such as
            ('ほか3指標', '') to say that there are more
    value:  the thing is one number: the actual number, set large ('4.2%')
    media:  anything else: a small component (e.g. a tiny chart of the real data drawn with sk.svg)
    accent: True for the one box the talk is about (usually the last)
    """
    if not isinstance(label, str) or not label.strip() or "\n" in label:
        _err(f"thing(): the label is one short noun on one line; got {label!r}")
    if _units(label) > 11:
        _err(f"thing(): label {label!r} is too long for a box; name the thing in a few characters")
    if _OPLIKE.search(_plain(label)):
        _warn(f'thing("{label}") reads like an operation. A box is a thing; an operation goes on the arrow: '
              f'sk.op("{label}"), followed by the thing it produces')
    if values is not None:
        values = [tuple(v) for v in values]
        if not 2 <= len(values) <= 6:
            _err("thing(values=…): 2 to 6 entries — a few real numbers of this case, not the whole table")
        for v in values:
            if len(v) != 2:
                _err(f"thing(values=…): each entry is (name, number); got {v!r}")
            num = re.sub(r"\s*(?:[A-Za-zµ°‰%]+|[点件秒分年回倍人枚台個円万千位])+$", "", str(v[1]).strip())   # a number with its unit
            if str(v[1]).strip() and not _NUMERIC.match(num):
                _err(f"thing(values=…): {v[1]!r} is not a number. The box holds named numbers; words go nowhere in a flow")
    return _Thing(label=label, img=img, value=value, values=values, media=media, width=width, accent=accent)


def op(label: str = "") -> _Op:
    """An arrow of flow(), with the operation written on it ('指標を計算', '線形回帰')."""
    if "\n" in label or _units(label) > 9:
        _err(f"op(): the operation is a few characters on one line; got {label!r}")
    return _Op(label)


def flow(*parts) -> H:
    """A left-to-right pipeline: boxes are things, arrows are operations.

    flow(thing('路面画像', img='figures/road.png', width=160), op('検出'),
         thing('ひび割れ画素', img='figures/road_mask.png', width=160), op('集計'),
         thing('区間の指標', values=[('ひび割れ率', '4.2%'), ('最大幅', '3.1mm'), ('ほか2指標', '')]),
         op('順位付け'), thing('補修の順位', media=tiny_chart, accent=True))

    Draw a flow only when the boxes have something to show. Follow ONE real case through it: the
    actual input, the actual numbers computed from it, the actual result. A row of words joined
    by arrows says nothing a sentence would not, and leaves the slide empty.

    2–5 things. A plain string is a thing. Two things in a row get a bare arrow.
    The data never "becomes" an operation: 「線形回帰」「検出」 are not boxes, they are what an arrow does.
    """
    seq = []
    for part in parts:
        if isinstance(part, _Op):
            if not seq or isinstance(seq[-1], _Op):
                _err("flow(): an op() must sit between two things")
            seq.append(part)
            continue
        if isinstance(part, str):
            part = thing(part)
        if not isinstance(part, _Thing):
            _err(f"flow(): parts are thing(...) / a string (things) and op(...) (arrows); got {part!r}")
        if seq and isinstance(seq[-1], _Thing):
            seq.append(_Op(""))
        seq.append(part)
    if not seq or isinstance(seq[-1], _Op):
        _err("flow(): the flow must end with a thing (what comes out)")
    n_things = sum(isinstance(s, _Thing) for s in seq)
    if not 2 <= n_things <= 5:
        _err("flow() takes 2 to 5 things; group a longer process into phases")
    n_shown = sum(1 for s in seq if isinstance(s, _Thing)
                  and (s["img"] or s["value"] is not None or s["values"] or s["media"] is not None))
    if n_shown * 2 < n_things:
        _warn(f"flow(): only {n_shown} of {n_things} boxes show anything but a word. A flow of words is a list with arrows — "
              "it says nothing a sentence would not. Follow one real case through it (img=, values=, value=), "
              "or do not draw a flow")
    out = []
    for s in seq:
        if isinstance(s, _Op):
            lab = f'<span class="op-label">{inline(str(s))}</span>' if str(s) else ""
            out.append(f'  <div class="{_cls("op", "" if str(s) else "bare")}">{lab}<span class="op-arrow"></span></div>')
            continue
        media = ""
        if s["img"]:
            _need_file(s["img"], "thing()")
            media = f'<div class="thing-media"><img class="shot" src="{_src(s["img"])}" width="{int(s["width"])}" alt=""></div>'
        elif s["values"]:
            rows_ = "".join(
                f'<div><dt>{inline(k)}</dt><dd>{inline(v)}</dd></div>' if str(v).strip()
                else f'<div class="more"><dt>{inline(k)}</dt></div>' for k, v in s["values"])
            media = f'<dl class="thing-values">{rows_}</dl>'
        elif s["value"] is not None:
            media = f'<p class="thing-value">{inline(s["value"])}</p>'
        elif s["media"] is not None:
            if not isinstance(s["media"], H):
                _err("thing(media=…) takes a component")
            media = f'<div class="thing-media">{s["media"]}</div>'
        out.append(f'  <div class="{_cls("thing", "accent" if s["accent"] else "")}">{media}'
                   f'<p class="thing-label">{inline(s["label"])}</p></div>')
    return H('<div class="flow">\n' + "\n".join(out) + "\n</div>")


# --------------------------------------------------------------------------------------------
# diagrams, math, table
# --------------------------------------------------------------------------------------------
def svg(inner: str, width: int, height: int, *, label: str = "", caption=None) -> H:
    """An inline SVG diagram drawn at scale 1 (coordinates are slide px).

    inner is the SVG content without the <svg> wrapper; use the diagram classes listed in
    references/figures.md (ln, f-tint, f-accent, t-sm, t-bold, …) — no colours or font sizes of your own.
    People: person(); things with a shape (a hand, a phone, a camera): icon().
    Text sits on its baseline: put a 17pt label's y at least 24 px below the top of the drawing
    (14pt: 20 px). Inside a column of cols(), make the drawing the column's width
    (deck.span_px(n) for an n-of-12 column) — it is never scaled.
    """
    if "<svg" in inner:
        _err("svg(): pass the inner markup only; the <svg> element is added for you")
    if re.search(r'\b(fill|stroke|font-size|font-family|style)\s*=', inner):
        _err("svg(): do not set fill/stroke/font-size/style attributes; use the diagram classes (references/figures.md)")
    tag = (f'<svg class="dia" width="{int(width)}" height="{int(height)}" viewBox="0 0 {int(width)} {int(height)}" '
           f'role="img" aria-label="{_html.escape(label)}">')
    body = "\n".join("  " + ln.strip() for ln in inner.strip().split("\n"))
    cap = f"\n  <figcaption>{inline(caption)}</figcaption>" if caption else ""
    return H('<figure class="fig">\n' + _ind(f"{tag}\n{body}\n</svg>") + f"{cap}\n</figure>")


def person(x: float, y: float, height: float = 80, *, cls: str = "f-mute") -> str:
    """SVG markup for a person (head and shoulders, seen from the front), for use inside svg().

    A diagram of a setting — who sits where, who watches what — reads at once when people look
    like people. A circle labelled 「被験者」 makes the audience decode a symbol; draw the shape.
    For anything else with a familiar outline — a hand, a phone, a camera, a monitor, a person
    seen from the side — take an icon from the bundled sets (scripts/icons.mjs, then icon());
    draw by hand only what no set has, and only if it comes out recognisable.

    x, y:   top-centre of the head, in slide px (the figure occupies x ± 0.32·height, y … y + height)
    height: total height in px
    cls:    a fill class — 'f-mute' (grey, the default), 'f-accent' (the subject), 'f-accent-2', 'f-hot'

        sk.svg(sk.person(110, 40, 90, cls="f-accent")
               + '<rect class="f-ink2" x="220" y="44" width="120" height="74"/>'      # the screen
               + sk.person(450, 40, 90)
               + '<text class="t-mid" x="110" y="160">被験者</text><text class="t-mid" x="280" y="160">画面</text>'
               + '<text class="t-mid" x="450" y="160">実験者</text>',
               560, 170, label="視聴実験の配置")
    """
    if cls not in ("f-mute", "f-accent", "f-accent-2", "f-hot", "f-ink2"):
        _err("person(): cls is 'f-mute', 'f-accent', 'f-accent-2', 'f-hot' or 'f-ink2'")
    h = float(height)
    r = 0.17 * h
    cy = y + r
    sw, top, bot = 0.32 * h, y + 0.47 * h, y + h          # shoulders: half width, top of the body, bottom
    body = (f'M{x - sw:.1f} {bot:.1f}V{top + 0.16 * h:.1f}'
            f'Q{x - sw:.1f} {top:.1f} {x - 0.16 * h:.1f} {top:.1f}H{x + 0.16 * h:.1f}'
            f'Q{x + sw:.1f} {top:.1f} {x + sw:.1f} {top + 0.16 * h:.1f}V{bot:.1f}Z')
    return (f'<circle class="{cls}" cx="{x:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>'
            f'<path class="{cls}" d="{body}"/>')


_FILL_CLASSES = ("f-mute", "f-accent", "f-accent-2", "f-hot", "f-ink2", "f-tint", "f-accent-tint", "f-bg")


def _icon_clean(body: str) -> str:
    """Turn an icon's own colour attributes into theme classes (svg() allows no colours of its own)."""
    def fix(m):
        tag, attrs, close = m.group(1), m.group(2), m.group(3)
        classes = []
        cm = re.search(r'\sclass="([^"]*)"', attrs)
        if cm:
            classes.append(cm.group(1))
            attrs = attrs.replace(cm.group(0), "")
        for prop in ("fill", "stroke"):
            pm = re.search(rf'\s{prop}="([^"]*)"', attrs)
            if not pm:
                continue
            val = pm.group(1).strip().lower()
            attrs = attrs.replace(pm.group(0), "")
            if prop == "fill":
                if val == "none":
                    classes.append("ic-nofill")
                elif val in ("#fff", "#ffffff", "white"):
                    classes.append("f-bg")
            elif val not in ("none", ""):
                classes.append("ic-s")
        attrs = re.sub(r'\sstyle="[^"]*"', "", attrs)
        cls = f' class="{" ".join(classes)}"' if classes else ""
        return f"<{tag}{attrs}{cls}{close}>"
    return re.sub(r'<([a-zA-Z][\w:-]*)((?:\s+[^\s=>/]+(?:="[^"]*")?)*)\s*(/?)>', fix, body)


def _icon_geom(src, x: float, y: float, size: float, flip: bool):
    """Read an icon file; return (body, transform, (left, top, width, height)) for placing it."""
    path = _need_file(src, "icon()")
    text = path.read_text(encoding="utf-8")
    m = re.search(r'viewBox="([-\d.]+)[ ,]+([-\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)"', text)
    if not m:
        _err(f"icon(): {src} has no viewBox; fetch icons with scripts/icons.mjs get")
    vx, vy, vw, vh = (float(v) for v in m.groups())
    body = re.sub(r"^.*?<svg\b[^>]*>|</svg>\s*$", "", text.strip(), flags=re.S)
    s = float(size) / vw
    h = vh * s
    top = y - h / 2
    if flip:
        tr = f"translate({x + size / 2:.1f} {top:.1f}) scale({-s:.5f} {s:.5f}) translate({-vx:g} {-vy:g})"
    else:
        tr = f"translate({x - size / 2:.1f} {top:.1f}) scale({s:.5f}) translate({-vx:g} {-vy:g})"
    return body, tr, (x - size / 2, top, float(size), h)


def icon_box(src, x: float, y: float, size: float = 64):
    """Where icon(src, x, y, size) lands: (left, top, width, height) in px of the drawing — for
    placing a name under it or a line to it."""
    return _icon_geom(src, x, y, size, False)[2]


def icon_point(src, x: float, y: float, size: float, px: float, py: float, *, flip: bool = False):
    """Where a point given in the icon's OWN coordinates lands in the drawing: (x, y) in px.

    For a line or an arrow that must end on a spot of the icon — the lens of a camera, the screen
    of a phone, a hand — find the spot in the icon file (its viewBox: 0–48 Health Icons, 0–24
    Material Symbols, 0–256 Phosphor), then:
        lx, ly = sk.icon_point(CAMERA, 560, 52, 78, 200, 128, flip=True)   # the same x, y, size, flip as sk.icon(…)
        f'<path class="ln-hot" d="M{lx:.0f} {ly:.0f}H{lx - 180:.0f}"/>'
    Pass the same flip= as the icon. A mark that sits ON the icon is simpler as icon(…, overlay=…).
    """
    path = _need_file(src, "icon_point()")
    m = re.search(r'viewBox="([-\d.]+)[ ,]+([-\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)"', path.read_text(encoding="utf-8"))
    if not m:
        _err(f"icon_point(): {src} has no viewBox; fetch icons with scripts/icons.mjs get")
    vx, vy, vw, _vh = (float(v) for v in m.groups())
    left, top, w, _h = _icon_geom(src, x, y, size, flip)[2]
    s = w / vw
    ix = (px - vx) * s
    return (left + w - ix if flip else left + ix, top + (py - vy) * s)


def icon(src, x: float, y: float, size: float = 64, *, cls: str = "f-mute", flip: bool = False,
         overlay: str = None) -> str:
    """SVG markup of an icon, for use inside svg() together with shapes and text.

    Get the file first with the bundled tool (open-source sets: Health Icons, Material Symbols,
    Phosphor):
        node <skill>/scripts/icons.mjs search camera          → ph:video-camera-fill, healthicons:video, …
        node <skill>/scripts/icons.mjs get <deck-dir> ph:video-camera-fill
    then  sk.icon("figures/icons/ph--video-camera-fill.svg", 560, 52, 78, flip=True).

    x, y:  centre of the icon, in slide px of the drawing
    size:  width in px (the height follows the icon's proportions)
    cls:   the colour — 'f-mute' (grey, the default), 'f-accent' (the subject), 'f-accent-2',
           'f-hot' (the one thing to look at), 'f-ink2', 'f-tint'
    flip:  mirror left–right, so that a thing faces the way it acts in the scene (a camera towards
           the person it records, a person towards whom they talk to)

    A person with a prop — a phone at the ear, glasses, a helmet — is one icon when a set has it
    (search first); otherwise compose it: the person, then the prop placed over the right spot.

    overlay: SVG markup drawn on top of the icon IN THE ICON'S OWN COORDINATES (its viewBox, e.g.
             0–48 for Health Icons, 0–24 for Material Symbols, 0–256 for Phosphor), with the diagram
             classes — for a prop on a person, a blush on a cheek. It moves, scales and flips with the
             icon. Lines keep their width (non-scaling strokes are set for you).
             sk.icon(head, 200, 90, 120, overlay='<path class="ln f-bg" d="M27 20L37 18Q43 22 43 28Q43 37 35 39L27 38Z"/>')
    Colour a drawn mark by what it depicts — a blush may be red; sweat, tears or a device are not.
    The red of emphasis is for pointing at something, not for colouring a thing that is not red.
    """
    if cls not in _FILL_CLASSES:
        _err(f"icon(): cls is one of {', '.join(_FILL_CLASSES)}")
    body, tr, _ = _icon_geom(src, x, y, size, flip)
    body = _icon_clean(body)
    if not overlay:
        return f'<g class="{cls}" transform="{tr}">{body}</g>'
    over = re.sub(r'<(\w+)([^>]*\bclass="[^"]*\bln[^"]*"[^>]*?)(\s*/?)>',
                  lambda m: f'<{m.group(1)}{m.group(2)} vector-effect="non-scaling-stroke"{m.group(3)}>'
                  if "vector-effect" not in m.group(2) else m.group(0), overlay)
    return f'<g transform="{tr}"><g class="{cls}">{body}</g>{over}</g>'


def posmap(points_, *, x: str, y: str, target=None, width: int = 620, height: int = 300) -> H:
    """A two-axis map that places a few things by judgement — for the rare slide whose point IS a
    position. Decide that the slide needs it before drawing it (references/figures.md §7).

    It works only when all of these hold:
    - the talk turns on a trade-off between two AMOUNTS the listeners weigh against each other
      ('費用の安さ', '答えられる質問の幅'), the others each give up one of them, and this work (or
      the proposal) claims both — and the audience would not see that from two bullets as fast;
    - both axes are amounts that run from less to more and that the field itself compares the
      approaches on — never kinds (who was studied, which type of effect, which family of method)
      and never yes / no: a list of kinds has no order, so a place on it means nothing;
    - the evidence for the places differs in kind from point to point (different measures,
      different studies), so the points cannot share a scale — when every point has the same
      measure on both axes, plot the values (a matplotlib scatter with ticks) instead.
    It is not the default picture for a prior-work slide; most talks have no such slide.

    points_: [(name, x, y), …], (name, x, y, side) or (name, x, y, side, value); x and y are 0–1
             (0 = low, 1 = high), placed in the order the material supports. side is where the name
             goes: 'right' (default), 'left', 'above', 'below'. value is the evidence for the place —
             usually what the approach falls short on ('R²=0.203', '掲載した約40問だけ'; '$R^2$'
             cannot be used here) — written bold on a second line under the name.
    x, y:    the amounts; an arrowhead shows the direction "more". Name what increases
             ('〜の高さ', '〜の幅'). Both names are horizontal (y above the top of its axis).
    target:  (name, x, y) — the spot this work aims at: a dashed ring in the accent colour. The ring
             is enough; nothing else marks the empty region.
    """
    # The plane is symmetric inside the drawing (equal margins left and right), so that centring
    # the drawing centres the plane. Both axis names are horizontal text: nothing is rotated.
    side, top = 20, 40
    ox, oy, right = side, height - 40, width - side

    def X(v):
        return ox + 40 + v * (right - ox - 80)

    def Y(v):
        return oy - 30 - v * (oy - top - 60)

    e = _html.escape
    s = [
        f'<path class="ln-bold" d="M{ox} {top}V{oy}H{right}"/>',
        f'<path class="ln-bold" d="M{ox - 7} {top + 10}L{ox} {top}L{ox + 7} {top + 10}"/>',
        f'<path class="ln-bold" d="M{right - 10} {oy - 7}L{right} {oy}L{right - 10} {oy + 7}"/>',
        f'<text class="t-mute t-end" x="{right}" y="{oy + 30}">{e(x)}</text>',
        f'<text class="t-mute" x="{ox - 8}" y="{top - 14}">{e(y)}</text>',
    ]
    if target:
        name, tx, ty = target
        r = builtins.max(30, _units(name) * 11.4 + 12)
        s.append(f'<circle class="ln-dash" cx="{X(tx):.0f}" cy="{Y(ty):.0f}" r="{r:.0f}"/>')
        s.append(f'<text class="t-accent t-bold t-mid" x="{X(tx):.0f}" y="{Y(ty) + 6:.0f}">{e(name)}</text>')
    for pt in points_:
        if not isinstance(pt, (list, tuple)) or not 3 <= len(pt) <= 5:
            _err("posmap(): each point is (name, x, y), (name, x, y, side) or (name, x, y, side, value)")
        name, px_, py_ = pt[:3]
        side = pt[3] if len(pt) > 3 and pt[3] else "right"
        value = pt[4] if len(pt) > 4 else None
        if not (0 <= px_ <= 1 and 0 <= py_ <= 1):
            _err(f"posmap(): {name!r} is placed at ({px_}, {py_}); places are 0–1 on each axis")
        cx, cy = X(px_), Y(py_)
        s.append(f'<circle class="f-mute" cx="{cx:.0f}" cy="{cy:.0f}" r="10"/>')
        # baselines of the name and, under it, the value: the pair is centred on the dot beside it,
        # stacked away from the dot above / below it
        if side in ("right", "left"):
            nx, anchor = (cx + 18, "") if side == "right" else (cx - 18, "t-end")
            ny, vy = (cy - 9, cy + 23) if value else (cy + 6, None)
        elif side == "above":
            nx, anchor = cx, "t-mid"
            ny, vy = (cy - 52, cy - 20) if value else (cy - 20, None)
        elif side == "below":
            nx, anchor = cx, "t-mid"
            ny, vy = cy + 34, (cy + 66 if value else None)
        else:
            _err("posmap(): side is 'right', 'left', 'above' or 'below'")
        s.append(f'<text class="{anchor}" x="{nx:.0f}" y="{ny:.0f}">{e(name)}</text>')
        if value:
            s.append(f'<text class="{_cls("t-bold", anchor)}" x="{nx:.0f}" y="{vy:.0f}">{e(str(value))}</text>')
    out = svg("\n".join(s), width, height, label=f"{x} × {y}")
    # the linter asks of every position map whether the slide needs it (lint F8, info)
    return H(out.replace('<svg class="dia"', '<svg class="dia" data-posmap="1"', 1))


def math(tex: str, *, large: bool = False) -> H:
    """One display equation (KaTeX), centred. One or two per slide."""
    return H(f'<div class="{_cls("math-block", "large" if large else "")}">$${_html.escape(tex, quote=False)}$$</div>')


# a number as it is printed in a table: 12, 1,234, 0.52, .52 (APA style), −.48*, 3.2%, 0.1〜0.3,
# (0.59) — a standard deviation in parentheses, ** — a significance mark on its own, — / – / empty
_NUM_CORE = r"[−+\-±]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)"
_NUMERIC = re.compile(rf"^[(（]?{_NUM_CORE}\s*(?:%|\*{{1,3}}|†)?(?:[〜~–\-−]{_NUM_CORE}%?)?[)）]?$|^[—–\-*]?$|^\*{{1,3}}$|^†$"
                      rf"|^{_NUM_CORE}\s*[(（]{_NUM_CORE}[)）]$")      # also a mean with its SD: 3.19 (0.59)


def table(header, body, *, highlight=None, hot=None, dim=None, numeric=None, caption=None,
          small: bool = False, full: bool = False) -> H:
    """A table of NUMBERS, with horizontal rules only. Mostly for the appendix.

    A table whose cells are words is refused: a grid of phrases is the mark of a machine-made
    slide. Say such a comparison with a figure (bars, samples) or two bullets.

    header:    ['指標', '係数', '寄与（%）']
    body:      [[cell, …], …]   the first column names the row; the rest are numbers.
               Numbers may be written as the field writes them: '.52', '−.48*', '0.31**', '3.19 (0.59)'.
               Name each column by what it holds — 平均, SD — and a point one standard deviation above
               the mean is '+1SD', never '+1平均'. Means are what a reader wants; give SDs only when
               the context needs them, in a column of their own.
    highlight: row index(es) tinted — the subject;  hot: row index(es) in red;  dim: greyed out
    numeric:   column indexes to right-align (default: detected)
    """
    ncol = len(header)
    cells = [[("" if c is None else str(c)) for c in r] for r in body]
    for r in cells:
        if len(r) != ncol:
            _err(f"table(): row {r!r} has {len(r)} cells but the header has {ncol}")
    data_cells = [c.strip() for r in cells for c in r[1:]]
    n_num = sum(1 for c in data_cells if c and _NUMERIC.match(c))
    n_filled = sum(1 for c in data_cells if c)
    if not n_filled or n_num / n_filled < 0.5:
        _err("table(): this is a table of words. A table is for numbers only — show the comparison with a figure "
             "(sk.bars, sk.vbars, sk.samples) or say it in two bullets")
    if numeric is None:
        numeric = [j for j in range(ncol) if cells and all(_NUMERIC.match(r[j].strip()) for r in cells)]
    as_set = lambda v: set() if v is None else ({v} if isinstance(v, int) else set(v))  # noqa: E731
    hl, ht, dm = as_set(highlight), as_set(hot), as_set(dim)
    n_attr = lambda j: ' class="n"' if j in numeric else ""  # noqa: E731
    thead = "".join(f"<th{n_attr(j)}>{inline(t)}</th>" for j, t in enumerate(header))
    trs = []
    for i, r in enumerate(cells):
        rc = "hot" if i in ht else ("hl" if i in hl else ("dim" if i in dm else ""))
        tds = "".join(f"<td{n_attr(j)}>{inline(c)}</td>" for j, c in enumerate(r))
        trs.append(f'    <tr{f" class={chr(34)}{rc}{chr(34)}" if rc else ""}>{tds}</tr>')
    cap = f"\n  <caption>{inline(caption)}</caption>" if caption else ""
    c = _cls("tbl", "full" if full else "", "sm" if small else "")
    return H(f'<table class="{c}">\n  <thead>\n    <tr>{thead}</tr>\n  </thead>\n  <tbody>\n'
             + "\n".join(trs) + f"\n  </tbody>{cap}\n</table>")


# --------------------------------------------------------------------------------------------
# columns
# --------------------------------------------------------------------------------------------
class _Col(H):
    pass


def col(*children) -> _Col:
    """One column of cols(); its content is centred vertically."""
    inner = _flat(children)
    return _Col('<div class="col">\n' + "\n".join(_ind(x) for x in inner) + "\n</div>")


def cols(ratio: str, *columns) -> H:
    """Columns on the 12-column grid: a figure beside a figure, or a figure beside a few words.

    ratio:   '6-6' '5-7' '7-5' '4-8' '8-4' '4-4-4'
    columns: one argument per column — a component, a list of components, or col(...)
    Use it when two figures must be read together, or when the figure is tall and narrow.
    The default layout of a slide is NOT columns: it is figure on top, words below.
    """
    if ratio not in _RATIOS:
        _err(f'cols("{ratio}"): unknown preset; use one of {", ".join(_RATIOS)}')
    if len(columns) != _RATIOS[ratio]:
        _err(f'cols("{ratio}") needs {_RATIOS[ratio]} columns, got {len(columns)}')
    built = [c if isinstance(c, _Col) else col(c) for c in columns]
    return H(f'<div class="cols c-{ratio}">\n' + "\n".join(_ind(b) for b in built) + "\n</div>")


# --------------------------------------------------------------------------------------------
# deck
# --------------------------------------------------------------------------------------------
_FIGURE_MARK = re.compile(r'class="(fig|samples-wrap|chart|flow|math-block|tbl|therefore)\b|<svg class="dia"')
_SEP = re.compile(r"\s*[-‐–—－―]\s*")


class Deck:
    """A deck. Slides are added in order with cover(), slide(), refs(), blank(), appendix()."""

    def __init__(self, title: str, *, minutes=None, ratio: str = "16:9", date=None, lang: str = "ja",
                 known_abbr=(), accent=None, theme=None, out: str = "deck.html"):
        """
        title:   the talk's title (cover and document title)
        minutes: length of the talk — used to check the number of slides and the planned time
        ratio:   "16:9" or "4:3" (ask the venue; a 学会 / 研究室 projector is often 4:3)
        date:    shown small at the bottom left of every slide, e.g. "2026/9/16"
        """
        global _RATIO
        if ratio not in _GEOM:
            _err('ratio is "16:9" or "4:3"')
        _RATIO = ratio
        self.title, self.minutes, self.ratio, self.lang = title, minutes, ratio, lang
        self.date = date
        self.known_abbr = list(known_abbr)
        self.accent = accent            # (accent, accent_tint) hex pair, or None for the theme blue
        self.out = out
        if theme is None:
            theme = "theme" if (ROOT / "theme").exists() or not (ROOT.parent / "theme").exists() else "../theme"
        self.theme = theme
        self._slides = []               # dicts: role, html, title, sec

    # ---- geometry helpers ----
    def span_px(self, n: int) -> int:
        """Width in px of an n-column span; size figures with this (e.g. deck.span_px(7))."""
        return span_px(n, self.ratio)

    @property
    def content_w(self) -> int:
        """Width in px of the content area (between the side margins)."""
        g = _GEOM[self.ratio]
        return g["w"] - 2 * g["pad_x"]

    @property
    def body_h(self) -> int:
        """Height in px under heading + message. A figure with three bullets under it: ~body_h - 150."""
        return _BODY_H

    # ---- slides ----
    def cover(self, title=None, *, event=None, sub=None, lines=(), sec=None, notes=None):  # noqa: A002
        """The cover, left-aligned: event (small) -> title (large) -> short rule -> lines (grey).

        title: defaults to the deck title; break it with \\n at a phrase boundary.
        lines: who / where / when, one string per line: ['○○専攻', '氏名', '2026年9月16日']
        """
        parts = []
        if event:
            parts.append(f'    <p class="cover-event">{inline(event)}</p>')
        parts.append(f'    <h1 class="cover-title">{inline(title or self.title)}</h1>')
        if sub:
            parts.append(f'    <p class="cover-sub">{inline(sub)}</p>')
        if isinstance(lines, str):
            lines = [lines]
        if lines:
            parts.append('    <div class="cover-rule"></div>')
            parts.append('    <div class="cover-meta">' + "".join(f"<p>{inline(x)}</p>" for x in lines) + "</div>")
        body = '  <div class="cover-main">\n' + "\n".join(parts) + "\n  </div>"
        self._add("cover", "slide cover", body, title or self.title, sec, notes)

    def slide(self, heading: str, message, *body, sec=None, notes=None, text_only: bool = False,
              appendix: bool = False, lint_off=None):
        """A content slide: heading -> message -> figure -> a few words.

        heading:   the part of the talk, optionally with the topic after " - ":
                   '研究背景'  '方法 - 実験'  '結果 - 精度'  'まとめ'.  The topics of one part name the
                   same kind of thing (結果 - 精度 / 結果 - 速度 / 結果 - 頑健性), never items of content.
        message:   ONE short claim under the heading — what this slide says, with its subject and what
                   happens to it. Noun-ending, no 「、」「。」, about 18 characters at most; the key words
                   may be bold (**…**). None when the heading says it all (目的, まとめ).
                   ○ 「予測性能と説明性の両立」  × 「既存の手法は予測性能と説明性を両立できていない」
                   ○ 「雨天では検出率が晴天より低下」  × 「雨天では逆に低下」 (what, compared with what?)
        body:      components, top to bottom. The first is normally a figure.
        sec:       seconds planned for this slide
        notes:     what you say aloud. Everything that is not on the slide goes here.
        text_only: True to declare that this slide has no figure on purpose (目的, まとめ)
        lint_off:  rule ids to silence on this slide — only with a reason in a comment
        """
        if not isinstance(heading, str) or not heading.strip():
            _err("slide(): the heading is empty")
        if isinstance(message, H) or (message is not None and not isinstance(message, str)):
            _err("slide(): the 2nd argument is the message — one short phrase — or None; components come after it:\n"
                 '    deck.slide("研究背景", "細いひび割れほど見落とし", sk.samples(...), sk.points([...]))')
        heading = _SEP.sub(" - ", heading.strip()) if re.search(r"\S\s+[-‐–—－―]\s+\S|[–—－―]", heading) else heading.strip()
        head_max = self.content_w / (_PX["head"] * 1.0) - 0.5
        if "\n" in heading or _units(heading) > head_max:
            _err(f"slide(): heading {heading!r} is too long (one line holds about {head_max:.0f} characters). "
                 "The heading only names the part of the talk; what the slide says goes to the message")
        msg_html = ""
        if message is not None:
            if re.search(r"[、，。．]", message):
                _err(f"slide(): the message {message!r} contains 「、」 or 「。」 — it has become a sentence. "
                     "Write one noun-ending phrase (「指標決定と寄与測定」), and say the rest aloud")
            msg_html = _lines(message, "slide(): message", builtins.min(24, self.content_w / _PX["msg"] - 1), 1)
        blocks = _flat(body)
        role = "appendix" if appendix else "main"
        has_fig = any(_FIGURE_MARK.search(b) for b in blocks)
        inner = f'  <header class="head">\n    <h2 class="heading">{inline(heading)}</h2>\n  </header>\n'
        if msg_html:
            inner += f'  <p class="msg">{msg_html}</p>\n'
        inner += '  <div class="body">\n' + "\n".join(_ind(b, 4) for b in blocks) + "\n  </div>"
        cls = _cls("slide", "appendix" if appendix else "")
        if not has_fig and not text_only and not appendix:
            _warn(f'slide "{heading}" has no figure. Show it — sk.samples / sk.bars / sk.vbars / sk.shares / sk.flow / '
                  "sk.fig / sk.math — or pass text_only=True if words alone are right here (目的, まとめ)")
        extra = ' data-text-only="1"' if text_only else ""
        self._add(role, cls, inner, heading, sec, notes, lint_off, extra)

    def appendix(self, heading: str, message, *body, **kw):
        """An appendix slide (after refs() and blank()). Same arguments as slide(); tables of numbers belong here."""
        self.slide(heading, message, *body, appendix=True, **kw)

    def disclosure(self, lines, *, heading: str = "利益相反の開示", sec=10, notes=None):
        """A disclosure the event requires — most often the conflict-of-interest (COI) statement that
        many 学会 ask for right after the title. Put it directly after cover().

        lines: the statement in the event's own wording, one string per line, e.g.
               ["筆頭演者：氏名", "発表に関連し開示すべきCOI関係にある企業などはありません"].
               Use the event's form when it gives one; this slide follows the event, not this skill.
        sec:   seconds it stays up (counted in the talk time, not in the slide count).
        It is a slide of words by nature: it has no message and no figure, and the checks for main
        slides do not apply to it.
        """
        if isinstance(lines, str):
            lines = [lines]
        lines = [str(x) for x in lines]
        if not lines or len(lines) > 6:
            _err("disclosure(): 1 to 6 lines, in the wording the event asks for")
        html = [_lines(x, "disclosure()", self.content_w / _PX["body"] - 1, 2) for x in lines]
        inner = (f'  <header class="head">\n    <h2 class="heading">{inline(heading)}</h2>\n  </header>\n'
                 '  <div class="body">\n    <div class="disclosure-text">\n'
                 + "\n".join(f"      <p>{x}</p>" for x in html) + "\n    </div>\n  </div>")
        self._add("disclosure", "slide disclosure", inner, heading, sec, notes)

    def refs(self, items, *, heading="参考文献", per_slide=None):
        """The reference list. items are strings in citation order; *…* marks a journal/book title.

        A Latin-script title is set in italics; a Japanese one is not (Japanese has no italics —
        write it as it is, 『…』 if the field uses them).
        List the works cited on the slides, not the paper's whole bibliography. When the list does
        not fit on one slide it continues on further slides (「参考文献(1)」「参考文献(2)」) with the
        numbers running on: the split is estimated from the length of each entry, or set it with
        per_slide=N.
        """
        items = list(items)
        if per_slide:
            n = int(per_slide)
            chunks = [items[i:i + n] for i in range(0, len(items), n)] or [[]]
        else:
            # 14pt entries, line-height 1.5, 11px apart, in the body of a slide without a message
            per_line = (_content_w() - 2.6 * 18.67) / 18.67
            budget = _BODY_H + 47 - 24
            chunks, cur, used = [], [], 0.0
            for it in items:
                lines = builtins.max(1, -(-_units(re.sub(r"\*", "", str(it))) // per_line))
                h = lines * 28.0 + 11
                if cur and used + h > budget:
                    chunks.append(cur)
                    cur, used = [], 0.0
                cur.append(it)
                used += h
            chunks.append(cur)
        starts = [sum(len(c) for c in chunks[:k]) for k in range(len(chunks))]
        for k, chunk in enumerate(chunks):
            lis = []
            for it in chunk:
                s = _html.escape(str(it), quote=False)
                s = re.sub(r"\*(.+?)\*", lambda m: m.group(1) if _JA.search(m.group(1)) else f"<i>{m.group(1)}</i>", s)
                lis.append(f"      <li>{s}</li>")
            head = heading if len(chunks) == 1 else f"{heading}({k + 1})"
            start = f' style="--start: {starts[k]}"' if k else ""
            inner = (f'  <header class="head">\n    <h2 class="heading">{inline(head)}</h2>\n  </header>\n'
                     f'  <div class="body">\n    <ol class="refs"{start}>\n' + "\n".join(lis) + "\n    </ol>\n  </div>")
            self._add("backmatter", "slide backmatter", inner, head, None, None)

    def blank(self):
        """An empty slide: the buffer between the references and the appendix."""
        self._add("blank", "slide blank", "", "", None, None)

    def _add(self, role, cls, inner, title, sec, notes, lint_off=None, extra=""):
        attrs = f' class="{cls}"'
        if self.date and role not in ("cover", "blank"):
            attrs += f' data-date="{_html.escape(str(self.date))}"'
        if sec is not None:
            attrs += f' data-sec="{sec:g}"'
        attrs += extra
        if lint_off:
            attrs += f' data-lint-off="{_html.escape(lint_off if isinstance(lint_off, str) else " ".join(lint_off))}"'
        if notes:
            lines = [ln.strip() for ln in str(notes).strip().split("\n")]
            n = "\n".join("    " + _html.escape(ln, quote=False) for ln in lines if ln)
            inner += f'\n  <aside class="notes">\n{n}\n  </aside>'
        self._slides.append({"role": role, "title": str(title), "sec": sec,
                             "html": f"<section{attrs}>\n{inner}\n</section>" if inner else f"<section{attrs}></section>"})

    # ---- output ----
    def html(self) -> str:
        t = self.theme.rstrip("/")
        body = "\n\n".join(f"<!-- {i + 1} -->\n{s['html']}" for i, s in enumerate(self._slides))
        uses_math = bool(re.search(r"\$[^$\n]+\$|\\\(|\\\[", body))
        head = [
            '<meta charset="utf-8">',
            f"<title>{_html.escape(self.title)}</title>",
            f'<link rel="stylesheet" href="{t}/slide.css">',
            f'<link rel="stylesheet" href="{t}/ratio-{_GEOM[self.ratio]["css"]}.css">',
        ]
        if uses_math:
            head += [
                f'<link rel="stylesheet" href="{t}/vendor/katex/katex.min.css">',
                f'<script defer src="{t}/vendor/katex/katex.min.js"></script>',
                f'<script defer src="{t}/vendor/katex/auto-render.min.js"></script>',
                f'<script defer src="{t}/math.js"></script>',
            ]
        if self.accent:
            a, tint = self.accent
            head.append(f"<style>:root {{ --accent: {a}; --accent-tint: {tint}; }}</style>")
        attrs = f' lang="{self.lang}"'
        if self.minutes is not None:
            attrs += f' data-minutes="{self.minutes:g}"'
        if self.known_abbr:
            attrs += f' data-known-abbr="{_html.escape(" ".join(self.known_abbr))}"'
        return ("<!doctype html>\n<!-- generated by slidekit from deck.py — edit deck.py, not this file -->\n"
                f"<html{attrs}>\n<head>\n" + "\n".join(head) + "\n</head>\n<body>\n\n" + body + "\n\n</body>\n</html>\n")

    def save(self, path=None) -> Path:
        """Write deck.html next to the script and print a one-screen summary."""
        if not self._slides:
            _err("the deck has no slides")
        out = Path(path) if path else ROOT / self.out
        out.write_text(self.html(), encoding="utf-8", newline="\n")
        mains = [s for s in self._slides if s["role"] in ("cover", "main")]
        # a disclosure (COI) is shown for a few seconds: it counts in the time, not in the slide count
        secs = [s["sec"] for s in mains] + [s["sec"] for s in self._slides if s["role"] == "disclosure"]
        line = f"slidekit: wrote {out.name} — {len(self._slides)} slides ({len(mains)} main incl. cover)"
        if self.minutes is not None:
            line += f", {self.minutes:g} min"
            if all(v is not None for v in secs):
                line += f", planned {sum(secs):g}s of {self.minutes * 60:g}s"
            else:
                _warn("set sec= on the cover and on every main slide so the timing can be checked")
        print(line)
        for w in _WARNINGS:
            print(f"slidekit: warning: {w}", file=sys.stderr)
        return out


# --------------------------------------------------------------------------------------------
# matplotlib figures at slide size, in the deck's font and colours
# --------------------------------------------------------------------------------------------
PX_PER_IN = 96.0
#: theme colours for plots — accent (dark blue) for the subject, mute (grey) for what is only there
#: for comparison, hot (red) for the one thing to look at, accent2 (light blue) for a variant of the subject
C = {
    "ink": "#1a2330", "ink2": "#4a5665", "ink3": "#7a8593", "line": "#c9d0d8", "tint": "#f1f4f7",
    "accent": "#1f3f6b", "accent2": "#7fa7d1", "accent_tint": "#e9eff7", "hot": "#c8372d", "mute": "#a9b0b8",
}
#: theme type scale in pt
PT = {"body": 20, "sub": 17, "small": 14, "tiny": 12}
_MPL_READY = False


def _font_dir():
    for d in (ROOT / "theme" / "fonts", ROOT.parent / "theme" / "fonts", HERE / "theme" / "fonts", HERE.parent / "theme" / "fonts"):
        if d.exists():
            return d
    return None


def _mpl():
    """Import matplotlib lazily and apply the deck style once."""
    global _MPL_READY
    try:
        import matplotlib
    except ImportError as e:
        raise DeckError("matplotlib is not installed (pip install matplotlib fonttools brotli)") from e
    if not _MPL_READY:
        matplotlib.use("Agg")
        from cycler import cycler
        from matplotlib import font_manager
        family = "sans-serif"
        fd = _font_dir()
        if fd:
            cache = ROOT / "figures" / ".fontcache"
            for weight in ("Regular", "Bold"):
                src = fd / f"NotoSansJP-{weight}.woff2"
                if not src.exists():
                    continue
                dst = cache / f"NotoSansJP-{weight}.ttf"
                if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
                    try:
                        from fontTools.ttLib import TTFont
                        cache.mkdir(parents=True, exist_ok=True)
                        f = TTFont(str(src))
                        f.flavor = None
                        f.save(str(dst))
                    except ImportError as e:
                        raise DeckError("fonttools and brotli are needed to read the theme fonts (pip install fonttools brotli)") from e
                font_manager.fontManager.addfont(str(dst))
                family = "Noto Sans JP"
        if family == "sans-serif":
            print("slidekit: warning: theme fonts not found; figures will use a system font", file=sys.stderr)
        import matplotlib.pyplot as plt
        plt.rcParams.update({
            "font.family": family, "font.size": PT["small"],
            "axes.titlesize": PT["small"], "axes.labelsize": PT["small"],
            "xtick.labelsize": PT["small"], "ytick.labelsize": PT["small"], "legend.fontsize": PT["small"],
            "text.color": C["ink"], "axes.labelcolor": C["ink2"], "axes.edgecolor": C["ink2"],
            "xtick.color": C["ink2"], "ytick.color": C["ink2"],
            "axes.linewidth": 1.1, "axes.spines.top": False, "axes.spines.right": False,
            "axes.axisbelow": True, "axes.grid": False, "grid.color": C["line"], "grid.linewidth": 0.75,
            "xtick.major.width": 1.1, "ytick.major.width": 1.1, "xtick.major.size": 4, "ytick.major.size": 4,
            "xtick.major.pad": 5, "ytick.major.pad": 5, "axes.labelpad": 8,
            "lines.linewidth": 2.5, "lines.markersize": 8, "lines.solid_capstyle": "round", "patch.linewidth": 0,
            "axes.prop_cycle": cycler(color=[C["accent"], C["hot"], C["accent2"], C["mute"]]),
            "legend.frameon": False, "legend.handlelength": 1.2, "legend.borderaxespad": 0,
            "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none", "savefig.edgecolor": "none",
            "figure.dpi": PX_PER_IN, "savefig.dpi": 192, "svg.fonttype": "path", "axes.unicode_minus": False,
        })
        _MPL_READY = True
    import matplotlib.pyplot as plt
    return plt


def new_fig(width_px: float, height_px: float, nrows: int = 1, ncols: int = 1, **kw):
    """A matplotlib figure that is exactly width_px × height_px on the slide. Returns (fig, ax).

    Text sizes given in pt are the same pt on the slide (default 14pt; label the data itself at 17pt bold).
    Size it for its place: new_fig(deck.content_w, 300) under a message with two bullets below.
    """
    plt = _mpl()
    kw.setdefault("layout", "constrained")
    figure, ax = plt.subplots(nrows, ncols, figsize=(width_px / PX_PER_IN, height_px / PX_PER_IN), **kw)
    return figure, ax


def hgrid(ax) -> None:
    """Light horizontal gridlines only (values on the y axis)."""
    ax.grid(axis="y")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)


def vgrid(ax) -> None:
    """Light vertical gridlines only (values on the x axis)."""
    ax.grid(axis="x")
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)


def ylabel_top(ax, text: str) -> None:
    """Name the y axis with horizontal text above its top end, instead of a rotated label.

    Everything on a slide is read left to right; a label turned on its side makes the audience
    tilt their heads. Use this in place of ax.set_ylabel().
    """
    ax.set_ylabel("")
    ax.annotate(text, xy=(0, 1), xycoords="axes fraction", xytext=(0, 10), textcoords="offset points",
                ha="left", va="bottom", color=C["ink2"], fontsize=PT["small"], annotation_clip=False)


def _jobs(figure) -> list:
    """Work that needs the final layout (sizes in px, positions of labels): done by save_fig()."""
    if not hasattr(figure, "_sk_jobs"):
        figure._sk_jobs = []
    return figure._sk_jobs


def ring(ax, x: float, y: float, width: float = 70, height: float = 46) -> None:
    """Draw one red ellipse around the place in a plot the slide is about.

    x, y:          the centre, in data coordinates (a point, or the middle of a gap between two points)
    width, height: the size in slide px — the same on every panel whatever its scale
    A static mark that is part of the figure — not something that appears during the talk. Use it
    when colour and a direct label do not already lead the eye there: the gap between two
    conditions, the one point that breaks the trend. At most one per panel, and only on the panels
    the slide is about. To ring the gap between two points, ring_between() sizes it for you.
    """
    _mpl()
    from matplotlib.patches import Ellipse
    from matplotlib.transforms import ScaledTranslation
    where = ax.figure.dpi_scale_trans + ScaledTranslation(x, y, ax.transData)
    ax.add_patch(Ellipse((0, 0), width / PX_PER_IN, height / PX_PER_IN, transform=where, fill=False,
                         edgecolor=C["hot"], linewidth=2.2, clip_on=False, zorder=5))


def ring_between(ax, x: float, y1: float, y2: float, *, width: float = 46, pad: float = 14) -> None:
    """Ring the gap between two points at the same x (two conditions at one level, say).

    The height is measured on the finished plot — the distance between the two points in px plus
    `pad` above and below — so the ring fits on every panel without hand-tuning.
    """
    def job():
        p1, p2 = ax.transData.transform([(x, y1), (x, y2)])
        h = abs(p2[1] - p1[1]) * PX_PER_IN / ax.figure.dpi + 2 * pad
        ring(ax, x, (y1 + y2) / 2, width, h)
    _jobs(ax.figure).append(job)


def end_labels(ax, items, *, side: str = "right", gap: float = 10) -> None:
    """Name lines at their ends — no legend — and keep the names from touching.

    items: [(text, x, y, colour), …] — x, y the end point of the line in data units; colour from C.
           A name in the accent or the red colour is bold (it is the subject); grey names are not.
    side:  'right' (the names after the last points) or 'left' (before the first points)
    Names whose ends are close are pushed apart, in the order of the lines, so the eye goes straight
    from each line to its name.
    """
    if side not in ("right", "left"):
        _err("end_labels(): side is 'right' or 'left'")

    def job():
        fig_ = ax.figure
        rows = []
        for it in items:
            text, x, y, colour = it[:4]
            ypt = ax.transData.transform((x, y))[1] * 72.0 / fig_.dpi
            rows.append([ypt, text, x, y, colour])
        rows.sort(key=lambda r: r[0])
        need = PT["sub"] * 1.3
        placed = []
        for r in rows:
            t = r[0] if not placed or r[0] - placed[-1] >= need else placed[-1] + need
            placed.append(t)
        shift = [pl - r[0] for pl, r in zip(placed, rows)]
        mean = sum(shift) / len(shift)
        for r, sh in zip(rows, shift):
            bold = r[4] in (C["accent"], C["hot"])
            ax.annotate(r[1], (r[2], r[3]), xytext=(gap if side == "right" else -gap, sh - mean),
                        textcoords="offset points", ha="left" if side == "right" else "right", va="center",
                        fontsize=PT["sub"], fontweight="bold" if bold else "normal", color=r[4],
                        annotation_clip=False)
    _jobs(ax.figure).append(job)


def bar_values(ax, bars, texts=None, *, err=None, gap: float = 6) -> None:
    """Write each bar's value above it — above the cap of its error bar when it has one, so that the
    number never sits on the whisker.

    bars:  what ax.bar(…) returned
    texts: the strings to print ('7.2'), in the order of the bars; default: the heights, as %g
    err:   the error-bar lengths given to ax.bar(yerr=…): one per bar, or one for all
    A bar drawn in the red or the dark blue of the theme gets its value bold in that colour; the
    others get theirs in grey. Leave room above the tallest whisker with ax.set_ylim — save_fig warns
    when a value runs out of the top of the plot.
    """
    _mpl()
    from matplotlib.colors import to_hex
    bars = list(bars)
    if texts is None:
        texts = [f"{b.get_height():g}" for b in bars]
    if len(texts) != len(bars):
        _err("bar_values(): one text per bar")
    if err is None:
        errs = [0.0] * len(bars)
    elif isinstance(err, (int, float)):
        errs = [float(err)] * len(bars)
    else:
        errs = [float(e) for e in err]
        if len(errs) != len(bars):
            _err("bar_values(): err= has one length per bar (the yerr given to ax.bar)")
    notes = []
    for b, t, e in zip(bars, texts, errs):
        colour = to_hex(b.get_facecolor()).lower()
        key = colour in (C["hot"], C["accent"])
        top = b.get_y() + b.get_height() + e
        notes.append(ax.annotate(str(t), (b.get_x() + b.get_width() / 2, top), xytext=(0, gap + (4 if e else 0)),
                                 textcoords="offset points", ha="center", va="bottom", fontsize=PT["sub"],
                                 fontweight="bold" if key else "normal", color=colour if key else C["ink2"],
                                 annotation_clip=False))

    def job():
        box = ax.get_window_extent()
        if any(n.get_window_extent().y1 > box.y1 + 1 for n in notes):
            _warn("bar_values(): a value runs out of the top of the plot; raise the top of the y axis (ax.set_ylim) "
                  "so that it stays inside, clear of the axis name")
    _jobs(ax.figure).append(job)


def _category_grid(figure) -> bool:
    """True when a plot puts marks on two axes that are both lists of names — groups of people
    across, kinds of effect up. Such a place means nothing: the rows could be swapped."""
    from matplotlib.collections import PathCollection

    def names(labels):
        ts = [t.get_text().strip() for t in labels if t.get_visible() and t.get_text().strip()]
        return len(ts) >= 2 and not any(re.search(r"\d", t) for t in ts)
    for ax in figure.axes:
        if getattr(ax, "_sk_schematic", False):
            continue
        if not (names(ax.get_xticklabels()) and names(ax.get_yticklabels())):
            continue
        marks = any(isinstance(c, PathCollection) and len(c.get_offsets()) for c in ax.collections)
        marks = marks or any(str(ln.get_marker()) not in ("None", "", " ") and len(ln.get_xdata()) for ln in ax.lines)
        if marks:
            return True
    return False


def schematic_axes(ax, *, x: str = None, y: str = None, keep_xticks: bool = False) -> None:
    """Axes for a schematic — a prediction, a concept — where the quantities have no values.

    No ticks and no numbers (keep_xticks=True keeps x ticks that are real conditions or levels).
    An arrowhead at the end of each axis says "more"; each name sits at its arrowhead, so it reads as
    part of the axis: name what increases (「照明の明るさ」, 「理解の程度」), not a bare noun and not a
    placeholder such as 「各指標」.
    """
    _mpl()
    ax._sk_schematic = True
    if not keep_xticks:
        ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_visible(True)
    ax.plot(1, 0, marker=">", color=C["ink2"], markersize=7, transform=ax.transAxes, clip_on=False)
    ax.plot(0, 1, marker="^", color=C["ink2"], markersize=7, transform=ax.transAxes, clip_on=False)
    if x:
        ax.set_xlabel(x, loc="right", color=C["ink2"], fontsize=PT["small"])
    if y:
        ax.set_ylabel("")
        ax.annotate(y, xy=(0, 1), xycoords="axes fraction", xytext=(10, 0), textcoords="offset points",
                    ha="left", va="center", color=C["ink2"], fontsize=PT["small"], annotation_clip=False)


def _trim_axes(figure) -> None:
    """End each visible bottom / left axis line a little past where its scale ends — past the last
    tick or the furthest data, by about 14 px — so that it neither stops dead at the last point nor
    runs on under the labels written beyond the data. Schematic axes keep their full length."""
    import math as _m
    for ax in figure.axes:
        if getattr(ax, "_sk_schematic", False):
            continue
        lim = ax.dataLim
        inv = ax.transData.inverted()
        for side, view, ticks, hi_data, k in (("bottom", ax.get_xlim(), ax.get_xticks(), lim.x1, 0),
                                             ("left", ax.get_ylim(), ax.get_yticks(), lim.y1, 1)):
            sp = ax.spines[side]
            if not sp.get_visible() or view[0] > view[1]:
                continue
            inside = [t for t in ticks if view[0] - 1e-9 <= t <= view[1] + 1e-9]
            end = builtins.max(inside + ([hi_data] if _m.isfinite(hi_data) else []), default=None)
            if end is None:
                continue
            pt = [end, view[0]] if k == 0 else [view[0], end]
            disp = ax.transData.transform(pt)
            disp[k] += 14 * figure.dpi / PX_PER_IN
            end = inv.transform(disp)[k]
            if end < view[1]:
                sp.set_bounds(view[0], end)


def _center_axes(figure) -> None:
    """Move the plot area to the middle of the image, so that centring the image on the slide centres
    the plot — not the plot plus the names written beside it. Only the wider margin is kept."""
    poss = [ax.get_position() for ax in figure.axes if ax.get_visible()]
    if not poss:
        return
    x0 = builtins.min(p.x0 for p in poss)
    x1 = builtins.max(p.x1 for p in poss)
    m = builtins.max(x0, 1 - x1)
    if abs(x0 - (1 - x1)) < 0.01 or 1 - 2 * m <= 0.2:
        return
    k = (1 - 2 * m) / (x1 - x0)
    for ax in figure.axes:
        p = ax.get_position()
        ax.set_position([m + (p.x0 - x0) * k, p.y0, p.width * k, p.height])


def save_fig(figure, name: str, *, caption=None, alt: str = "", trim: bool = True, center: bool = True) -> H:
    """Save the figure as figures/<name>.svg and return it as a slide component.

    trim:   end the axis lines a little past the last tick / the furthest data (default), so that a
            line neither stops dead nor runs on under the labels written at the ends of the data.
    center: put the plot area in the middle of the image (default), so that the plot — not the plot
            plus its outside labels — sits on the centre line of the slide, and the caption under it.
    Labels and rings placed with end_labels() / ring_between() are laid out here, on the final plot.
    """
    plt = _mpl()
    out_dir = ROOT / "figures"
    out_dir.mkdir(exist_ok=True)
    figure.canvas.draw()                                   # the layout, so that px are known
    jobs = getattr(figure, "_sk_jobs", [])
    for job in jobs:
        job()
    if jobs:
        figure.canvas.draw()                               # make room for what the jobs added
    if center:
        _center_axes(figure)
        figure.set_layout_engine("none")
        figure.canvas.draw()
    if trim:
        _trim_axes(figure)
    catgrid = _category_grid(figure)
    if catgrid:
        _warn(f"save_fig({name!r}): both axes are lists of names, with marks at their crossings. A place on such a "
              "chart means nothing — the rows could be swapped — so the grid pretends to measure. Show what really "
              "differs: an amount on its own axis with its values, a time on a time axis, two settings as pictures "
              "side by side — or say it in two bullets (references/figures.md §7)")
    # every text in the plot, so that the numbers in it reach the number check (lint)
    from matplotlib.text import Text
    texts = [t.get_text().replace("$", "") for t in figure.findobj(Text) if t.get_visible() and t.get_text().strip()]
    path = out_dir / f"{name}.svg"
    figure.savefig(path, format="svg", metadata={"Date": None})
    plt.close(figure)
    # the linter asks of every chart whether it says where to look; red in a plot (a red line,
    # a red point, ring()) is such a mark
    marked = C["hot"].lower() in path.read_text(encoding="utf-8").lower()
    html = str(fig(f"figures/{name}.svg", caption=caption, alt=alt))
    attrs = ' data-plot="1"' + (' data-marked="1"' if marked else "") + (' data-catgrid="1"' if catgrid else "")
    attrs += f' data-text="{_html.escape(" ｜ ".join(texts))}"'
    return H(html.replace('<figure class="fig"', f'<figure class="fig"{attrs}', 1))
