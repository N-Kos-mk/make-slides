"""{{TITLE}} — deck source.

Run:  python deck.py        (lint.mjs and build.mjs also run it for you)
This file is the deck. deck.html is generated from it; never edit deck.html by hand.
Every function used here is documented in the skill's references/layouts.md.

Every slide:  heading -> message (one short phrase) -> figure -> a few lines of words.
What you would say aloud goes to notes=, not on the slide.
Choose each figure from what THIS material can show (references/story.md §5, figures.md §2) —
not from this template and not from the gallery.
"""
import slidekit as sk

deck = sk.Deck(
    title="{{TITLE}}",
    minutes={{MINUTES}},
    ratio="{{RATIO}}",
    # date="2026/9/16",               # bottom-left of every slide — only when the date is known
)

# ---- 1 cover -------------------------------------------------------------------------------
deck.cover(
    event="会議・発表会の名称",
    lines=["所属", "氏名"],             # who / where / when; placeholders when identifiers may not appear
    sec=15,
)

# only when the event requires a conflict-of-interest statement, in the event's own wording:
# deck.disclosure(["筆頭演者：氏名", "発表に関連し開示すべきCOI関係にある企業などはありません"])

# ---- 2 -------------------------------------------------------------------------------------
deck.slide(
    "研究背景",                      # heading: the part of the talk (+ " - topic" when the part has several slides)
    "ここに一言",                    # message: a claim, noun-ending, no 「、」, about 18 characters — or None
    # the figure, chosen for what this slide says (figures.md §2), for example:
    #   real cases         sk.samples(sk.sample("figures/a.png", "97%"), sk.sample("figures/b.png", "63%", tone="hot"))
    #   one picture        sk.fig("figures/screen.png", fill=True, shot=True)
    #   a few values       sk.vbars([...], hot=[...]) / a ranking: sk.bars([...])
    #   shares of a whole  sk.shares([(whole, [values]), ...], parts=[...], title="…に占める割合（%）")
    #   a pipeline         sk.flow(sk.thing(…, img=…), sk.op(…), …)   — the boxes show one real case
    #   a plot             sk.new_fig(…) … sk.save_fig(fig, "name")     — axes are amounts, never lists of names
    #   a setting          sk.svg(sk.person(…) + sk.icon(…) + …)
    sk.vbars([("比較対象", "0.20"), ("本研究", "0.57")], highlight=["本研究"], title="図の題（単位）"),
    sk.points([                      # at most three bullets, flush left; each a full line that reaches across the slide
        "1行に事実を1つ、数値や条件や出典を添えて幅の7割以上まで書く[1]",
        "含意は改行して矢印で書き、直前の行より長くしない\n→このように短く書く",
    ]),
    sec=60,
    notes="""
    話す内容。スライドに書かなかった説明・条件・理由はすべてここに書く。
    """,
)

# ---- references, blank, appendix -----------------------------------------------------------
# deck.refs(["著者: 題名, *誌名*, 巻, ページ (年)", …])     # only the works cited on the slides
# deck.blank()
# deck.appendix("補足 - …", None, sk.table([...], [...]))   # what only a questioner needs

deck.save()
