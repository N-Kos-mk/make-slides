# Slide patterns and components — the slidekit API (Phase 4)

Every slide is built by calling `slidekit` from `deck.py`. This file is the catalog: the anatomy
of a slide, the patterns to copy, and every component. The same patterns are running code in
`assets/gallery/deck.py` (rendered: `assets/gallery/out/gallery.pdf`).

## Contents

1. Shape of a deck.py
2. Anatomy of a slide, and how the space is shared
3. Choosing a pattern
4. The patterns
5. Deck methods
6. Component reference
7. Inline markup and line breaks
8. Composition rules
9. `raw()` — the escape hatch
10. Common mistakes, and the error messages you will meet

---

## 1. Shape of a deck.py

```python
"""発表タイトル — deck source."""
import slidekit as sk

deck = sk.Deck(title="発表タイトル", minutes=10, ratio="16:9", date="2026/9/16")

# (data loading and figure functions — ordinary Python — go here or just before the slide that uses them)

deck.cover(event="○○発表会", lines=["所属", "氏名", "2026年9月16日"], sec=15)

deck.slide("研究背景", "細いひび割れほど見落とし",
           sk.samples(…), sk.points([…]),
           sec=55, notes="""…""")
…
deck.refs([…])
deck.blank()
deck.appendix("補足 - 上位5区間の指標", None, sk.table(…))

deck.save()
```

`python deck.py` writes `deck.html`; `lint.mjs` and `build.mjs` run it for you.

## 2. Anatomy of a slide, and how the space is shared

```
deck.slide(heading, message, *body, sec=…, notes=…)
```

| Zone | 4:3 (960×720) | 16:9 (1280×720) | Holds |
|---|---|---|---|
| heading + rule | y 30–97 | same | the part of the talk, 34pt light, accent colour |
| message | y 113–152 | same | one phrase, 22pt |
| body | y 168–674 (**506 px** high, 848 px wide) | 506 px high, 1136 px wide | figure, then words |
| footer | y 692–704 | same | date (left), page number (right) |

Without a message the body starts at y 121 and is 553 px high.

**Where blocks sit.**

| Block | Horizontally |
|---|---|
| heading, message | flush left at the margin, on every slide |
| a list (`points`), the summary (`summary`) | **flush left at the margin**, on the same edge as the heading |
| a figure, an equation, a conclusion line, a frame, the arrow of `therefore` | centred |
| a list inside a column of `cols()` (a sub-element) | centred in its column |
| the premises of `therefore` (part of a centred composition) | centred as a block over the arrow and the frame; lines flush left inside the block |

A list is never centred as a block. So that text at the left and objects in the middle balance,
**a list must carry its width**: its longest line reaches at least 70% of the way across a 4:3
slide (65% at 16:9), and the other lines are of similar length. Write each bullet as one full
line — a fact with its number, condition or source. The linter warns about a list of stubs (L6).

Lines do not wrap by themselves — you place every break (section 7).

**How the height is shared.** Blocks are stacked top to bottom with the free space shared evenly
above, between and below them. Some blocks *take all the height that is left* after the words
have been placed:

| Takes the free height | Has its own size |
|---|---|
| `samples()`, `fig(…, fill=True)`, `bars()`, `vbars()`, `shares()`, `cols()` | `points()`, `summary()`, `conclusion()`, `boxed()`, `therefore()`, `math()`, `flow()`, `posmap()`, `svg()`, `table()`, a plotted figure (`save_fig`) |

So with `samples` + `points`, the images grow until the slide is full: fewer bullets, larger
pictures. With a fixed-size figure (a plot, a flow), choose its size so that figure and words
together cover most of the body; `lint --metrics` reports the result (`fig` = share of the body
area taken by the figure, `fill` = share of the body height that carries content, `cx` = how far
the weight of the slide sits from the centre line).

How long a bullet is (full-width characters per line):

| | 4:3: write | 4:3: a line holds | 16:9: write | 16:9: a line holds |
|---|---|---|---|---|
| `points` (20pt) | **21–28** | 30 | **27–38** | 41 |
| `points(size="large")` / `summary` (24pt) | **17–23** | 25 | **22–31** | 34 |

Shorter than "write" and the list is too thin to balance the slide (a warning); longer than "a
line holds" and the library refuses the line. Inside a column of `cols` a line holds about half
as much, and a list there is centred in its column, so it may be short.

Rough capacities under a message (506 px):

| Words on the slide | Height left for the figure |
|---|---|
| nothing | ~500 px |
| one conclusion line | ~430 px |
| 2 one-line bullets | ~400 px |
| 3 one-line bullets | ~360 px |
| 3 bullets, one of them two lines | ~320 px |
| a display equation | subtract ~70 px more |

## 3. Choosing a pattern

| The slide shows | Pattern |
|---|---|
| what something looks like; a contrast between real cases | A — real images side by side |
| a ranking or a breakdown | B — horizontal bars |
| a few values compared; two kinds of value | C — vertical bars (one chart, or two side by side) |
| how a method works overall | D — flow |
| (rarely) a choice between two amounts that only one option holds together | E — position map |
| the purpose | F — premises → arrow → framed statement |
| one step or definition, on a real example | G — real examples + formula |
| a relation, trend or distribution, with the cases behind it | H — plot + examples |
| a model and a worked case | I — equation + worked example |
| one image (a screen, a photo, a figure from a paper) | J — single image |
| the conclusions | K — summary |
| exact values for the question session | L — table of numbers (appendix) |
| the setting of an experiment: who, where, what they saw | M — the setting drawn |
| the hypotheses the results are read against | N — hypotheses + a schematic of the prediction |
| what share of a whole each part is; how that changes between conditions | O — shares of a whole |

The table maps *what a slide shows* to a form — not *parts of a talk* to forms. A prior-work slide
can be A (what earlier methods miss), C (the numbers they report) or J (their key figure) — and
only rarely E; a method can be D, G, I or M. Variety follows from content: when three slides in a row use the same
pattern, check that each content really has that form. When no pattern fits, the content is
usually two slides.

**The examples below come from three invented talks** — a research talk on detecting cracks in
road images, an experiment on watching lecture videos at double speed, and a business briefing on
a chat service for an inquiry desk — so that none of them reads as "the" talk. Copy the call;
never the content, and never the choice of figure (SKILL.md rule 21).

## 4. The patterns

### A — Real images side by side

The strongest pattern, and the one a model forgets. Use the material's own images.

```python
deck.slide(
    "研究背景",
    "細いひび割れほど見落とし",
    sk.samples(
        sk.sample("figures/crack_wide.png", "97%"),
        sk.sample("figures/crack_fine.png", "63%", tone="hot"),     # the case the slide is about
        caption="目視点検での発見率（幅3mm以上と幅1mm未満）[1]",
    ),
    sk.points([
        "市道の舗装点検は点検員の目視が中心で1kmあたり約3時間[2]",
        "幅1mm未満のひび割れは熟練した点検員でも3割以上を見落とし[1]",
        "広がる前に補修すれば費用は広がった後の約5分の1[3]\n→早い段階での発見が課題",
    ]),
    sec=55,
)
```

- The bullets are flush left and each is a full line: the list balances the two centred images
  above it. Stubs (「見落としが多い」「費用が安い」) would not.
- Two images for a contrast; three to six for a series (`tight=True`, `small=True`).
- Under each image: the **value** it stands for, large; the one the slide is about in red
  (`tone="hot"`). When the images are cases told apart by a condition rather than a number, the
  "value" may be that condition as a short name (「晴天」「雨天」): a few characters, bold,
  directly under its image. A per-image `note` (one short grey line) only when the comparison needs a second
  quantity; otherwise say what the value is once, in `caption=` or in the message.
- Choose examples that show the point without explanation: the extremes of the data.

### B — Horizontal bars

```python
deck.slide(
    "結果 - 精度",
    "**幅1mm未満**でも9割前後を検出",                  # the key words bold: the bars below prove them
    sk.bars([("幅3mm以上", "98"), ("幅2〜3mm", "96"), ("幅1〜2mm", "95"), ("幅0.5〜1mm", "92"), ("幅0.5mm未満", "88")],
            hot=["幅0.5〜1mm", "幅0.5mm未満"], axis_max=100, title="ひび割れの幅ごとの発見率（%）"),
    sk.points([
        "同じ120区間の目視点検では幅1mm未満のひび割れの発見率は63%",
        "誤検出は1kmあたり平均2.4件で画像での確認は約5分の作業",
    ]),
    sec=50,
)
```

- Every bar carries its value; there is no axis to read.
- `hot=` (red) marks the bars the slide is about; `highlight=` (dark blue) marks "this work"
  among others; everything else is grey. Together with the bold words of the message this is how
  the chart says where to look (lint F5).
- `axis_max=` is a round number just above the largest value — never a total far past the data
  (slidekit warns, lint F6).
- Up to about 12 bars with two bullets; with nine or more the labels drop to 14pt automatically.
  Two or three bars are better as vertical bars (C): horizontal bars are capped in height.

### C — Vertical bars; two kinds of value side by side

```python
deck.slide(
    "効果 - 試行導入",
    "待ち時間は約4分の1に短縮",
    sk.cols(
        "6-6",
        sk.vbars([("導入前", "12.4"), ("導入後", "3.1")], highlight=["導入後"], axis_max=14, title="平均の待ち時間（分）"),
        sk.vbars([("導入前", "3.2"), ("導入後", "4.1")], highlight=["導入後"], axis_max=5, title="満足度の平均（5段階）"),
    ),
    sk.points([
        "2026年10月の1か月の試行導入で約2,300件の問い合わせに対応",
        "自動で回答できなかった約3割は担当者への引き継ぎで解決",
    ]),
    sec=55,
)
```

- One chart holds one kind of number. Two kinds → two charts, each with its `title=`. Never put
  different kinds in one row of bars or one row of big numbers.
- 2–7 bars per chart. Give both charts the same `axis_max` when their scales are comparable.
- One chart alone is the same call without `cols` — for example the numbers that prior methods
  report, the one the slide is about in red:
  `sk.vbars([("目視点検[1]", "63"), ("輝度の勾配[4]", "62"), ("深層学習[5]", "95")], hot=["深層学習[5]"], …)`.
  Two bars alone widen by themselves (wider columns, wider gaps), so that the chart still carries
  the slide; with three bullets under them it is only a quarter of the body (the edge of F2), so
  two bullets suit it better.
- Error bars: a plot (figures.md §8) with `sk.bar_values` for the values.

### D — Flow

```python
deck.slide(
    "提案手法 - 全体像",
    "画像1枚から区間の補修順位を算出",
    sk.flow(
        sk.thing("路面画像", img="figures/road_alligator.png", width=200),     # the actual input
        sk.op("検出"),
        sk.thing("ひび割れ画素", img="figures/road_mask.png", width=200),      # what the step found in it
        sk.op("集計"),
        sk.thing("区間の指標", values=[("ひび割れ率", "12.6%"), ("最大幅", "3.1mm"), ("ほか2指標", "")]),
        sk.op("順位付け"),
        sk.thing("補修の順位", media=rank_bars(), accent=True),               # the real ranking, as a tiny chart
    ),
    sk.points([
        "市販のカメラを車両の後部に付けて走行しながら路面を撮影",
        "暗く細い線の連なりを画素ごとに検出して100mの区間ごとに集計",
        "ひび割れ率と幅と交通量から区間ごとに補修の優先度を計算",
    ]),
    sec=60,
)
```

- **A box is a thing** (data, an artefact, a result). **An arrow is an operation.** The label of
  a box is a noun; the name of the step goes on the arrow with `op()`. `thing("検出")` is wrong —
  the library warns — because data does not turn into "detection"; it turns into the detected
  pixels *by* detection.
- **The boxes show the things.** Follow one real case through the flow: `img=` the actual image,
  `values=` a few of the actual numbers computed from it (name–number pairs, units allowed, then
  `("ほか2指標", "")`), `value=` the actual result, `media=` a small chart of real data. A flow
  whose boxes hold one word each is text with arrows — it leaves the slide empty and says nothing
  a sentence would not; the library warns and the linter reports it (G2). If there is nothing to
  put in the boxes, do not draw a flow.
- No sub-label (a small explanatory line) inside a box.
- The words under the flow add what it cannot show — the idea behind a step, the size of the
  data, the measure — in full lines.
- 2–5 things. Four boxes with content and operation names of two to four characters fill the
  width; the linter reports a flow that is too wide (then: a narrower picture, fewer values).
- `accent=True` on the one box the talk is about (the only bold label).

A tiny chart for a box — real data, shapes only:

```python
def rank_bars(w=120, h=100):
    step, top = h / len(RANKS), RANKS[0]
    rects = [f'<rect class="{"f-hot" if i == 0 else "f-mute"}" x="0" y="{i * step:.1f}" '
             f'width="{v / top * w:.1f}" height="{step * 0.64:.1f}"/>' for i, v in enumerate(RANKS)]
    return sk.svg("\n".join(rects), w, h, label="区間ごとの優先度")
```

### E — Position map

```python
deck.slide(
    "選択肢",
    "**チャット導入**が費用と質問の幅を両立",
    sk.posmap(
        [("電話窓口の増員", 0.12, 0.86, "right", "年約1,200万円"),
         ("FAQページの整備", 0.88, 0.14, "left", "掲載した約40問だけ")],
        x="費用の安さ", y="答えられる質問の幅",
        target=("チャット導入", 0.86, 0.86),
        width=deck.span_px(9), height=330,
    ),
    sk.points([
        "電話窓口の増員はすべての質問に答えられるが人件費が年約1,200万円",
        "FAQページは約80万円で済むが答えられるのは掲載した約40問だけ",
    ]),
    sec=50,
)
```

- **Rarely the right figure, and a decision each time.** Use it only when the point of the slide
  *is* a position: a trade-off between two amounts the listeners weigh against each other (here
  cost and how many questions get answered), which each other option gives up and one option
  alone holds. When the others differ in kind, on one property, or by one missing thing, it does
  not work (figures.md §7). Most talks have no such slide; a prior-work slide is not one by
  default. Lint lists it (F8) and the report gives the reason.
- **Both axes are amounts** that run from less to more, named by what increases. Never kinds
  (who was studied, which effect, which method family).
- The places are judged (0–1), because the evidence for them differs in kind from point to point.
  When every point has the same measures on both axes, plot the values instead.
- **The evidence under each name**: the fifth element of a point is written bold on a second line
  (usually what that option falls short on). `target=` rings this work; nothing else marks the
  empty region.
- **The bullets say what each other option falls short on**, its strength only as the contrast in
  front. Bullets that only praise the others hide the gap; repeating the number at the point is
  fine. Name each point by what distinguishes it.

### F — Premises → arrow → framed statement (the purpose)

```python
deck.slide(
    "目的",
    None,
    sk.therefore(
        ["幅1mm未満のひび割れは熟練した点検員の目視でも3割以上を見落とし",
         "深層学習は発見率95%と高いが何を根拠に判断したのかを示せない",
         "根拠の明確な輝度の勾配だけの手法では細いひび割れの発見率が62%"],
        "判断の根拠を示せる手法で細いひび割れまで自動検出",
    ),
    text_only=True,
    sec=35,
)
```

- The purpose in one line (a second line with `\n` if it must). No method on this slide.
- **The premises, the arrow and the frame stand on the centre line.** The list of premises is
  centred as a block (its lines flush left inside it). If the premises reach the right edge this
  looks flush left; if they stop short, they sit over the arrow and the frame instead of leaving
  the right side of the slide empty. Write the premises as full lines all the same — what is
  known and what is missing, with its specifics — not stubs like 「見落としが多い」.
- When every premise fits on one line at 24 pt, the premises are set at 24 pt, and the purpose in
  the frame is 24 pt too: the composition fills the slide.
- Use this pattern once in a deck.

### G — Real examples + formula (one step of the method)

```python
deck.slide(
    "提案手法 - ひび割れ率",
    "ひび割れの面積の割合で傷みを測定",
    sk.samples(
        sk.sample("figures/road_sound.png", "0.3%"),
        sk.sample("figures/road_alligator.png", "12.6%", tone="hot"),
    ),
    sk.math(r"\text{ひび割れ率} = \frac{\text{ひび割れの画素数}}{\text{路面の画素数}}"),
    sec=50,
)
```

- A definition is shown on real inputs: the audience sees a low case and a high case, with the
  values, and the formula ties them together. No bullets are needed; how it works is spoken.

### H — Plot + the cases behind it

```python
deck.slide(
    "結果 - 頑健性",
    "**雨天**は晴天より細いひび割れを見落とし",
    sk.cols(
        "7-5",
        fig_weather(),                                             # sk.new_fig(deck.span_px(7), 360) … sk.ring(…) … sk.save_fig(…)
        sk.samples(                                                # same order as the lines: the upper line, the upper image
            sk.sample("figures/crack_fine.png", "91%", tone="accent"),
            sk.sample("figures/crack_wet.png", "74%", tone="hot"),
            stack=True,
        ),
    ),
    sec=55,
)
```

- The lines in the plot and the values under the images share colours (`tone="accent"` / `"hot"`),
  so no legend is needed.
- **Stack the images in the order of the lines they belong to** — the upper line gets the upper
  image. Then the eye goes straight across from a line to its example; in the opposite order the
  two paths cross.
- **Mark the point in the plot**: the gap written as a red label beside it (「差 17ポイント」) and, when
  the eye still would not go there, one `sk.ring(ax, x, y, width, height)` around it — centre in
  data units, size in px (figures.md §8). Name
  the lines directly at their ends. Name the y axis with `sk.ylabel_top(ax, "発見率（%）")` —
  horizontal text above the axis, never a rotated label.
- Keep the two columns about equally heavy (`cx` in `--metrics`).

### I — Equation + worked example

```python
deck.slide(
    "提案手法 - 優先度",
    "4つの指標の重み付き和で優先度を算出",
    sk.math(r"\text{優先度} = \sum_{j=1}^{4} w_j z_j"),
    sk.cols(
        "4-8",
        sk.fig("figures/road_alligator.png", fill=True, shot=True),
        sk.bars([("ひび割れ率", "+0.92"), ("交通量", "+0.41"), ("最大幅", "+0.27"), ("前回補修からの年数", "-0.15")],
                signed=True, hot=["ひび割れ率"], ends=("優先度を下げる", "優先度を上げる"),
                title="この区間の $w_j z_j$"),
    ),
    sk.conclusion("優先度 1.45 で120区間のうち1位"),
    sec=55,
)
```

- The equation alone is abstract; one real case computed through it makes it concrete.
- `bars(signed=True)` draws positive and negative terms from a centre line, and `ends=` writes
  what each direction means under the two ends — without it a bar to the left means nothing.
- When the claim is about quantities (the time in each condition), chart the quantities with
  B or C instead of their coefficients.

### J — Single image

```python
deck.slide(
    "提案 - 画面",
    "よくある質問に**自動で回答**",
    sk.fig("figures/chat_screen.png", fill=True, shot=True),
    sk.conclusion("回答できない質問はその場で担当者に引き継ぎ"),
    sec=40,
)
```

- One short thing to say: a centred `conclusion` line, not a one-stub list at the left.
- `fill=True` lets a photo or screenshot take all the free height. `shot=True` draws a hairline
  around an image with a white edge.
- A figure taken from a paper (someone else's) carries its citation mark in the message or a
  bullet. When only the picture of a figure is available, this is the pattern: crop it to the
  panels the slide needs (`scripts/figpanels.py`), ring the place it is about, and read it in a
  line or two:

  ```python
  sk.fig("figures/fig3_a.png", fill=True, ring=(300, 120, 700, 420)),   # the box, in the image's pixels
  sk.points(["輝度の勾配の線だけが幅1mm未満で急に下がり本研究との差が開く"]),
  ```

  A dense original with only the message above it is not read by the audience (lint F9).
- **A near-square figure beside bullets** (`cols`) pulls the weight of the slide to one side (L6),
  and a column narrows the figure until its type is unreadable. Keep the default stack — figure
  above, words below — and crop the figure to the panels that matter so that it is wide rather
  than tall.

### K — Summary

```python
deck.slide(
    "まとめ",
    None,
    sk.summary(
        [
            "判断の根拠を示せる手法で幅1mm未満の発見率91%を達成",
            "雨天では細いひび割れの発見率が17ポイント低下\n→雨天の画像の扱いが課題",
        ],
        [
            "夜間の撮影と照明の条件を加えた120区間での再評価",
            "算出した補修の順位を自治体の実際の補修計画と照合",
        ],
    ),
    text_only=True,
    sec=45,
)
```

- Conclusions in black, what comes next in blue. Five bullets in all at most.
- Both lists are flush left, and every bullet is a full line (17–23 characters or more at 4:3,
  22–31 at 16:9): 「指標の拡張」 alone among longer bullets is a stub — say what is extended.
- A consequence line (→) is no longer than the line it follows. Otherwise a bullet that fits on
  one line is not broken (lint T10).
- No new information. This slide stays up during questions: a fact that matters enough to be
  here (a cost, the time a check takes) appears first on the main slide it belongs with, as a
  bullet, and is repeated here.

### L — Table of numbers (appendix)

```python
deck.appendix(
    "補足 - 上位5区間の指標",
    None,
    sk.table(
        ["区間", "ひび割れ率（%）", "最大幅（mm）", "交通量（千台/日）", "優先度", "目視との相関"],
        rows,                                          # the first column names the row; the rest are numbers
        hot=0,
        caption="** は1%水準、* は5%水準で有意",
    ),
)
```

- `sk.table()` raises an error when fewer than half of its cells (the first column aside) are
  numbers. A table of words is not available in any form.
- Numbers may be written as the field writes them: `.62**`, `−.48*`, `(0.59)`.
- On a main slide, prefer bars: a table is read, a chart is seen.

### M — The setting of an experiment, drawn

```python
# node "<skill-dir>/scripts/icons.mjs" get <deck-dir> ph:video-camera-fill material-symbols:desktop-windows
setting = sk.svg(
    sk.person(120, 22, 130, cls="f-accent")                                         # the subject
    + sk.icon("figures/icons/material-symbols--desktop-windows.svg", 360, 98, 190, cls="f-ink2")
    + sk.icon("figures/icons/ph--video-camera-fill.svg", 560, 52, 78, flip=True)     # mirrored: it records the subject
    + '<path class="ln-hair" d="M640 10V200"/>'                                     # a partition
    + sk.person(730, 22, 130)
    + '<text class="t-mid" x="120" y="232">被験者</text>'
    + '<text class="t-mid" x="360" y="232">講義動画</text>'
    + '<text class="t-mid" x="560" y="112">録画</text>'
    + '<text class="t-mid" x="730" y="232">実験者</text>',
    820, 250, label="視聴実験の配置",
)
deck.slide(
    "方法 - 実験",
    "1人ずつ講義動画を視聴して小テスト",
    setting,
    sk.points([
        "等速条件20名と2倍速条件20名の大学生計40名で実験",
        "12分の講義動画を視聴した直後に10問の小テストと自己評価に回答",
    ]),
    sec=50,
)
```

- People are drawn as people (`sk.person`), things with a familiar outline from the bundled icon
  sets (`scripts/icons.mjs`, then `sk.icon`). A circle labelled 「被験者」 is a symbol to decode; a
  makeshift shape that reads as something else is worse.
- **Each thing faces the way it acts**: the camera records the subject, so it points at them
  (`flip=True` mirrors an icon).
- The subject in the accent colour, everyone and everything else grey. Names under the shapes.
- Draw from the front or the side when who faces whom matters, from above when distances matter.
  Few shapes, no detail: the drawing answers "who was where, and what did they see".
- In an experiment the people tested are 被験者; the sample is one noun block with its breakdown
  in front.

### N — Hypotheses + a schematic of the prediction

```python
fig, ax = sk.new_fig(deck.span_px(6), 280)
x = [0, 1]                                                      # two real conditions: two ticks
prepared, unprepared = [0.80, 0.73], [0.78, 0.46]
ax.plot(x, prepared, color=sk.C["accent"], marker="o")
ax.plot(x, unprepared, color=sk.C["hot"], marker="o")
ax.set_xticks(x); ax.set_xticklabels(["等速", "2倍速"])
ax.set_xlim(-0.25, 1.25); ax.set_ylim(0.3, 0.95)
sk.schematic_axes(ax, y="理解の程度", keep_xticks=True)        # no values: no ticks, arrowheads, named by what increases
sk.end_labels(ax, [("予習あり", 1, prepared[1], sk.C["accent"]), ("予習なし", 1, unprepared[1], sk.C["hot"])])
hypo = sk.save_fig(fig, "hypothesis", caption="予測（得点と自己評価のいずれもこの形）")

deck.slide(
    "仮説",
    "倍速の影響は**予習の有無**で差",
    hypo,
    sk.points([
        "**[仮説1]** 2倍速で視聴した被験者は等速の被験者より小テストの得点が低い",
        "**[仮説2]** 予習した被験者では2倍速による小テストの得点の低下が小さい",
    ]),
    sec=45,
)
```

- One bullet per hypothesis, each opening with a bold label, so that a result slide can say
  「仮説1は支持」 and the audience can look back.
- The schematic has no numbers: the axis without values has no ticks, an arrowhead at its end,
  and its name at the arrowhead says what increases (「理解の程度」) — not 「各指標」, not 「予測値」;
  「低」「高」 under its ends would be ticks pretending to be values. The two conditions are real, so
  they get their two ticks.
- The result slides then point back: 「→予習なしでは2倍速で得点が低下：**仮説1**の支持」 — the
  hypothesis in words, then its label (story.md §8).
- Label it as a prediction (`caption=`). It is not a result.
- When the hypotheses predict the same shape for several outcomes, draw the shape once and name
  the outcomes once (in the caption or the message) — not the same panel three times.

### O — Shares of a whole

```python
deck.slide(
    "効果 - 解決の経路",
    "**その場で解決**する問い合わせが約7割",
    sk.shares(
        [("導入前", ["52", "30", "18"]), ("導入後", ["74", "12", "14"])],
        parts=["その場で解決", "折り返しで解決", "未解決"], highlight="その場で解決",
        title="問い合わせ全体に占める割合（%）",
    ),
    sk.points([
        "試行導入の前後それぞれ1か月の問い合わせ約2,300件を経路ごとに集計",
        "折り返しの電話は1日平均約40件から約15件に減少して担当者の負担も軽減",
    ]),
    sec=45,
)
```

- **What 100% is, and what each part is, are on the slide.** `title=` names the whole (required);
  `parts=` names every part, the rest of the whole included, in words the audience knows — a code
  or a grade nobody has explained (「ランクⅢ・Ⅳ」) is replaced by what it means.
- The rows are wholes of one kind (before / after, two conditions), split into the same parts. A
  share of a different whole is a chart of its own or a bullet — never another row.
- The part the slide is about first and coloured (`highlight=` / `hot=`), so its bars start
  together at the left. Each segment carries its value; its name goes in wherever it fits, and
  slidekit refuses a part too narrow to be named in any bar. 2–4 parts; more go to `bars()`.
- One row alone is a thin strip: pair it with what its parts are, or let a bullet carry the second
  fact.

## 5. Deck methods

| Call | Use |
|---|---|
| `sk.Deck(title, minutes=, ratio="16:9"｜"4:3", date=, lang="ja", known_abbr=[…], accent=(…))` | create the deck. `date` is printed bottom-left on every slide; leave it out when the date is not known |
| `deck.cover(title=None, event=, sub=, lines=[…], sec=, notes=)` | the cover: event (small) → title → short rule → lines (who / where / when). Break the title with `\n` |
| `deck.slide(heading, message, *body, sec=, notes=, text_only=False, lint_off=)` | a main slide |
| `deck.refs([…], heading="参考文献", per_slide=None)` | the reference list; `*…*` marks a journal or book title (italic in Latin script, plain in Japanese). Only the works cited on the slides. A list too long for one slide continues on further slides (「参考文献(1)」「(2)」) with the numbers running on — split by the length of the entries, or by `per_slide=N` |
| `sk.missing_ref(name)` | an entry for `refs()` when the material does not give the reference of a work the slides name: it is shown red as 「出典未確認」, saving the deck warns, lint warns (C2), and the report names it first. Never write a reference from memory instead |
| `deck.blank()` | the empty slide between references and appendix |
| `deck.disclosure(lines, heading="利益相反の開示", sec=10)` | a disclosure the event requires (the COI statement many 学会 ask for), directly after the cover, in the event's wording. Counted in the time, not in the slide budget; no message, no figure |
| `deck.appendix(heading, message, *body, …)` | an appendix slide; same arguments as `slide`. A slide that answers a question in words (criteria, reasons) may be `text_only=True` |
| `deck.save()` | write `deck.html` and print the summary |
| `deck.content_w`, `deck.body_h`, `deck.span_px(n)` | geometry in px: content width, body height, width of n of 12 columns |

## 6. Component reference

### Figures

| Component | What it is |
|---|---|
| `samples(sample(path, value, note, tone=), …, caption=, tight=, small=, stack=)` | real images side by side, each with its value; fills the free height |
| `fig(path, fill=True, caption=, shot=, ring=)` | one raster image filling the free height (`width=` px instead of `fill` for a fixed size); an SVG is placed at its own size. `ring=(left, top, right, bottom)` in the image's pixels draws one red ellipse over a chart taken from a paper |
| `bars(data, hot=, highlight=, light=, axis_max=, title=, signed=, ends=)` | horizontal bars with values; fills the free height (up to 50 px per bar). `ends=("…", "…")` names the two directions of signed bars |
| `vbars(data, hot=, highlight=, light=, axis_max=, title=)` | vertical bars with values on top (2–7); fills the free height. Two bars alone get wider columns |
| `shares(rows, parts=, title=, hot=, highlight=, unit="%")` | bars that each run to 100%, split into named parts: `rows=[(whole, [values…]), …]`, `parts=[names…]`, `title=` what 100% is (required). Every row has the same parts; fills the free height |
| `flow(thing(…), op(…), thing(…), …)` | pipeline: `thing(label, img=｜values=｜value=｜media=, width=, accent=)`, `op(label)`. The boxes show one real case: its image, its numbers, its result |
| `posmap(points, x=, y=, target=, width=, height=)` | rarely, and only after deciding the slide needs it: a few points placed by judgement on two amounts; a point is `(name, x, y[, side[, value]])`, `value` the evidence for its place written bold under the name; `target=` rings this work. Never kinds on its axes (figures.md §7; lint F8 lists every use) |
| `math(tex, large=)` | one display equation, centred |
| `new_fig(w_px, h_px)` → `(fig, ax)`, `save_fig(fig, name, caption=, trim=True, center=True)` | a matplotlib plot at exact slide size, in the deck's font and colours; the plot area centred in the image, the axis lines run a little past the last tick; the numbers in the plot reach the number check |
| `ylabel_top(ax, text)`, `hgrid(ax)`, `vgrid(ax)` | plot helpers: the y-axis name as horizontal text above the axis (use instead of `set_ylabel`); light gridlines |
| `bar_values(ax, bars, texts=None, err=None)` | the value of each bar of `ax.bar(…)` written above it — above the cap of its error bar when `err=` is given — bold in the bar's colour when it is red or dark blue |
| `ring(ax, x, y, width, height)` | one red ellipse around the place in a plot the slide is about: centre in data units, size in px; at most one per panel |
| `ring_between(ax, x, y1, y2, width=46, pad=14)` | the ring around the gap between two points at the same x, sized on the finished plot |
| `end_labels(ax, [(name, x, y, colour), …], side="right")` | names at the line ends instead of a legend, pushed apart when they would touch |
| `schematic_axes(ax, x=, y=, keep_xticks=False)` | axes for a schematic: no ticks, arrowheads at the ends, the names at the arrowheads |
| `svg(inner, w, h, caption=)` | a hand-drawn inline SVG diagram using the theme's classes |
| `person(x, y, height, cls=)` | SVG markup of a person (head and shoulders) for use inside `svg()`; `cls="f-accent"` for the subject |
| `icon(path, x, y, size, cls=, flip=, overlay=)` | SVG markup of an icon fetched with `scripts/icons.mjs get` (a hand, a phone, a camera …) for use inside `svg()`; x, y the centre, size the width in px; `flip=True` mirrors it so that it faces the way it acts; `overlay=` shapes drawn in the icon's own coordinates (a prop on a person) |
| `icon_box(path, x, y, size)` | where that icon lands: (left, top, width, height) in px of the drawing |
| `icon_point(path, x, y, size, px, py, flip=False)` | where the spot (px, py) of the icon's own coordinates lands in the drawing: for a line or an arrow that ends on a part of the icon |
| `legend((name, colour), …)` | colour key for a chart, only when the labels do not already explain the colours |
| `table(header, body, highlight=, hot=, dim=, numeric=, caption=, small=, full=)` | a table of numbers |

### Words

| Component | What it is |
|---|---|
| `points(items, size=None｜"large", tone=None｜"accent")` | bullets, flush left: one level, five at most (three beside a figure), each a full line (two lines at most). `"…\n→…"` adds a consequence line |
| `summary(conclusions, future)` | the summary: conclusions (black) and what comes next (blue), large bullets, flush left |
| `conclusion(text)` | one bold centred line, no box; up to two lines with `\n` |
| `boxed(text)` | a framed statement that hugs its text; up to three lines with `\n` |
| `therefore(premises, result)` | full-line premises (flush left) → thick arrow → `boxed` (both centred) |
| `note(text)` | one small grey centred remark (a condition without which the figure would mislead) |
| `source(text)` | a 12pt source line |

### Layout

| Component | What it is |
|---|---|
| `cols(ratio, col1, col2[, col3])` | columns: `"6-6" "5-7" "7-5" "4-8" "8-4" "4-4-4"`. Each column is a component, a list, or `col(...)`; its content is centred vertically. A drawing or a plot in a column is made at the column's width: `deck.span_px(n)` for an n-of-12 column |

The default layout of a slide is **not** columns. It is the figure on top and the words below.
Use `cols` to put two figures side by side, or a tall narrow figure beside another.

## 7. Inline markup and line breaks

In any text argument:

| Write | Result |
|---|---|
| `**語**` | bold — one or two keywords per slide; the key words of a message; a label such as `**[仮説1]**` |
| `[[語]]` | bold in the accent colour |
| `!!語!!` | bold red — the one thing to look at; once per slide |
| `[1]`, `[2][3]` | citation marks (small, raised) |
| `$R^2=0.41$` | inline math (KaTeX) |
| `\n` | a line break where you put it |

Line breaks:

**Nothing is wrapped automatically.** You place every break.

- **Heading, message**: one line. Too long → the library raises an error; shorten.
- **Bullets of a list on its own**: written to fill one line (see the table in section 2). A
  bullet that fits stays on one line. One that runs over is trimmed to fit; if it cannot be, break
  it with `\n` at the phrase boundary nearest the end of the line, so the first line is long
  (three lines is refused). Never break a bullet early to make two equal lines: that empties the
  right side (lint T10). The library raises an error for a line that is too long.
- **Bullets inside a column**: the list is centred in its column, so lines of similar length are
  right there. The linter reports an overflow (O3) — add the `\n` there.
- **A consequence** (`"…\n→…"`) goes on its own line and is no longer than the line it follows.
- **`conclusion`, `boxed`, captions, labels**: text set against something else — break with `\n`
  at a phrase boundary so that the lines have similar lengths.
- **The cover title**: break it with `\n` at a phrase boundary near the middle.

```
In a caption, a frame, a column:
× "雨天の画像では細いひび割れの発見率が大きく低下"        (too long for its place → error or overflow)
× "雨天の画像では細いひび割れの発見率が\n大きく低下"      (a long line over a stub)
○ "雨天の画像では\n細いひび割れの発見率が大きく低下"      (two lines of similar length)

In a list on its own:
× "判断の根拠を示せる手法で\n幅1mm未満の発見率91%"         (fits on one line: the break empties the right side)
○ "判断の根拠を示せる手法で幅1mm未満の発見率91%を達成"     (one long line)
```

## 8. Composition rules

- One figure per slide (two when they are read together, in `cols`). Then at most one block of
  words: `points` **or** `conclusion`; exceptionally both, when the bullets are facts and the line
  is what they add up to.
- Order top to bottom: figure, then words. An equation that defines what the figure shows may sit
  above or below it.
- Do not stack three kinds of block under a figure. If a slide has a figure, an equation, bullets
  and a conclusion, it is two slides.
- `boxed` / `therefore`: once in the deck (the purpose). A second use needs a reason.
- `note`: at most one per slide, and not together with a figure caption.
- Colours carry meaning across the deck: the same thing has the same colour on every slide.
- **Balance.** Figures are centred; lists are flush left and must reach across the slide (lint
  L6). Never centre a list to fill a hole. In `cols`, keep the two sides about equally heavy.
- **One short thing to say** → `conclusion` (a centred line), not a one-stub list.
- **One direction.** A slide has at most one figure that runs sideways (a flow); the words under
  it add to it rather than repeat it.
- **A diagram shows something.** Boxes with one word each are not a figure (lint G2).
- **A chart says where to look.** Red (or dark blue for this work), a direct label of the decisive
  value, the key words of the message in bold, or one ring (lint F5).
- **Pairs.** What refers to each other is adjacent, in the same order, in the same colour.
- **Containment.** A caption, a note under a value, a consequence line: never wider than what
  they belong to (lint H1).

## 9. `raw()` — the escape hatch

`sk.raw("<div class=…>…</div>")` places hand-written HTML. It exists for a structure the library
lacks, not to restyle. Use only classes defined in `theme/slide.css`; never a `style=` attribute
that sets a font size, a colour or a margin (lint A9). If you reach for `raw()` to build a table
of text, a card, or a label-and-explanation list — that is the thing this skill exists to avoid.

## 10. Common mistakes, and the error messages you will meet

| What you wrote | What happens | What to do |
|---|---|---|
| a message with 「、」 or 「。」 | `DeckError: the message … contains 「、」 or 「。」` | one noun-ending phrase; say the rest aloud |
| a message over ~24 characters | `DeckError: … the line … is about N characters wide` | cut to ~18 |
| a component as the 2nd argument of `slide()` | `DeckError: the 2nd argument is the message` | pass the phrase, or `None` |
| a bare string in the body | `DeckError: a bare string cannot be placed on a slide` | `sk.points([...])`, `sk.conclusion(...)`, or notes |
| `points` with a tuple / nested list | `DeckError: bullets have one level only` | make it its own bullet, or say it aloud |
| six bullets | `DeckError: … Five is the limit` | keep what must be read |
| a bullet line that is too long | `DeckError: the line … is about N characters wide; one line holds M` | cut words, or break with `\n` into two lines of similar length |
| a bullet of three lines | `DeckError: a bullet of 3 lines is a paragraph` | two lines at most; say the rest aloud |
| a consequence (→) longer than its first line | lint H1 | shorten the consequence, or move words up |
| bullets cut down to keywords | lint L6: the list reaches only N% of the way across the slide (and a warning from `therefore` / `summary`) | full lines: the fact with its number, condition or source — or `conclusion`, or the list in a column |
| a flow of `thing("…")` with nothing in the boxes | warning + lint G2 | `img=`, `values=`, `value=`: one real case through the flow — or no flow |
| a flow wider than the slide | lint O3 | a narrower `img` width, fewer `values`, shorter operation names |
| `ax.set_ylabel(…)` in a plot | a rotated label | `sk.ylabel_top(ax, …)` |
| `table` of phrases | `DeckError: this is a table of words` | a figure, or two bullets |
| `thing("線形回帰")`, `thing("検出")` | warning: reads like an operation | `op("検出")` + the thing it produces |
| `fig("plot.svg", width=600)` | `DeckError: an SVG is never scaled` | regenerate the plot at that size |
| a slide with no figure | warning + lint F1 | add the figure, or `text_only=True` for 目的 / まとめ |
| a chart with nothing marked | lint F5 | `hot=` / `highlight=`, red in the plot, a direct label, `sk.ring`, or the key words of the message in bold |
| `axis_max` far above the largest value | warning + lint F6 | a round number just above the largest value |
| a message with 逆に / 同様に / 前者 | lint M4 | say what, compared with what |
| parentheses on every line | lint W5 | the qualifier in front of its noun |
| a bullet broken early into two short lines | lint T10 | one line if it fits; otherwise break near the end of the line |
| a ring sized by hand to the gap between two points | — | `sk.ring_between(ax, x, y1, y2)` |
| line names placed with hand-tuned offsets | — | `sk.end_labels(ax, …)` |
| an icon transform copied into deck.py to draw on top of it | — | `sk.icon(…, overlay=…)`, `sk.icon_box(…)`, `sk.icon_point(…)` |
| a scatter whose x and y ticks are names of kinds (groups × kinds of effect) | slidekit warning + lint F7 | show what actually differs on a real axis, or as pictures; or two bullets (figures.md §7) |
| a position map on the prior-work slide "because there is prior work" | lint F8 (info) | only when the position is the point (figures.md §7); otherwise the problem shown and two bullets |
| prior-work bullets that only say what the others achieved | — | each bullet ends on what that approach falls short on, its strength only as the contrast in front |
| a 100% bar drawn with matplotlib, its whole unnamed, the rest of it grey and blank | — | `sk.shares(…, title=…)`: the whole in the title, every part named |
| values written at the top of bars with error bars | they sit on the whiskers | `sk.bar_values(ax, bars, …, err=…)` |
| a two-bar `vbars` under-filled by three bullets | `fig` about 25%, the edge of lint F2 | two bullets; or the bars in `cols` beside the picture they compare |
| a hand, a phone, a camera drawn from rectangles and balloons | — | `scripts/icons.mjs search …`, `get`, `sk.icon` |
| a line ending in 〜ず | lint D6 | 〜ない, or a noun ending |
| a long heading | `DeckError: heading … is too long` | the heading is a label; move the content to the message |
| others' methods named on the slides, nothing cited | lint C1 | the citation mark where each first appears; the reference copied from the material |
| a reference written from memory because the material has none | (never) | search the material by the name, DOI, arXiv, `.bib`; if it is not there, `sk.missing_ref("…")` and tell the user |
| the base method's name on every slide, never explained | (the audience) | a few words woven in where it first appears: 「〜を数える **MCI** で区間を評価」 |
| math in a heading (`"結果 - $R^2$"`) | `DeckError: heading … contains math` | name the part in words; the symbol goes in the message or a bullet |
| a paper's figure under the message, nothing else | lint F9 (info) | `ring=` on the place it is about, and a line or two that read it |
| a figure cropped by hand with coordinates guessed in a script | — | `scripts/figpanels.py --preview`, then `--crop` / `--box` |
