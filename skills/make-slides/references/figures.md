# Figures: real images, charts, flows, plots, equations (Phase 3)

The figure is the main thing on every slide. This file is about getting good ones: where they
come from, which form fits which content, and how to make each with slidekit.

## Contents

1. Where figures come from
2. Choose the form
3. Real images — `sk.samples()` / `sk.fig()`
4. Preparing images and data — `prepare.py`
5. Bars — `sk.bars()` / `sk.vbars()` / `sk.shares()`
6. Flow — `sk.flow()`
7. Where this work stands — real axes first; `sk.posmap()` rarely
8. Plots with matplotlib — `sk.new_fig()` / `sk.save_fig()`
9. Diagrams by hand — `sk.svg()`
10. Equations — `sk.math()`
11. Tables — `sk.table()`
12. Rules for every figure
13. Checklist

---

## 1. Where figures come from

In this order of preference:

1. **The material's own pictures.** Photographs, screenshots, samples from the dataset, the
   stimulus as the participant saw it, a page of the questionnaire, the output of the system. A
   real example convinces in a way no drawing does, and the audience remembers it. If the
   material contains a dataset of images, the deck should be full of them.
2. **The data, drawn.** Result tables and CSVs become bars and plots. A value that the paper
   states in a sentence (「決定係数は0.203にとどまる」) is still data: two bars.
3. **A real case, computed.** A definition or a model is shown by running it on one actual input
   and showing the input, the intermediate values and the output. This often needs a few lines of
   code against the material (section 4) and is worth it every time.
4. **Structure, drawn with little text.** A pipeline as a flow; a setting with its people drawn as
   people. Shapes and a handful of nouns — never boxes full of sentences.

What is **not** a figure: a table of words, a list in boxes, an icon, a stock illustration, a
decorative shape, a word cloud, a big number on its own, a grid of names with dots at the
crossings (§7). If a "diagram" would still say the same
thing with its boxes removed, it is a list. (A person drawn in a diagram of the setting is not an
icon: it is the thing shown.)

When reading the material in Phase 1, list everything that can be shown. Typical finds that a
first reading misses:

| In the material | Becomes |
|---|---|
| a directory of dataset images + a CSV of scores | the highest and lowest case side by side; a low / high example for each indicator |
| result CSVs behind a table in the paper | bars, sorted, with the subject coloured |
| the code that computes a quantity | one worked example of that quantity on a real input |
| per-item values of a fitted model | the terms of one real prediction as signed bars |
| a figure in the paper, its data in the material | the same data redrawn at slide size, the point marked |
| a figure in the paper, only the picture | the picture itself (`fig`), cropped to the panels the slide needs |
| a sentence comparing two approaches | two bars of their numbers, on the one measure they share |
| a percentage of a whole (「全区間の38%」), a breakdown before / after | bars that run to 100%, the whole and every part named (`shares`) |
| a description of the setting of an experiment | the setting drawn, people as people (`sk.person`) |

### Figures from a paper

A paper's figure is material like any other, and how to use it depends on whether its data is
there too.

- **The data is in the material** (a table, a CSV, the numbers in the text): redraw the figure at
  slide size in the theme — legible type, the subject coloured, the point marked. Cite the paper.
- **Only the picture exists**: show the picture (`sk.fig(…, fill=True)`), cropped to the panels the
  slide is about so that its type is still readable at slide size (14 pt or more). Then read it for
  the audience: the point in the message (bold key words), **one ring on the place it is about**
  (`sk.fig(…, ring=(left, top, right, bottom))`, the box in the image's own pixels) and **a line or
  two that say what to see** (「雨天の画像の線だけが幅1mm未満で急に下がる」「先行手法では細いひび割れの
  山が消える」). An original figure with only the message above it is the slide the audience cannot
  read (lint F9) — keep those lines even when the figure would be larger without them. Do not read
  values off the image to redraw it: read values are estimates, and printing them would be
  inventing numbers (SKILL.md rule 20).
- **Only the picture exists and it is illegible** even when cropped: reading it off (digitising)
  is the last resort. Say so in the notes and the report, check the read values against any number
  the text states, and still print none of them.

- **Only the picture exists, but the text reports the statistics behind it**: compute the plotted
  values from the reported numbers — this is exact, unlike reading the picture. A typical case is
  a figure of estimates at −1SD / +1SD of a moderator, two conditions: with the condition means of
  the outcome and of the moderator (a table), the moderator's SD, and the simple slopes (their
  t × SE, or b), each point is

  ```
  estimate = mean_Y(condition) + slope(condition) × (moderator − mean_M(condition)),  moderator = grand mean ± SD
  ```

  Check by comparing the difference between the conditions at each level with the reported simple
  effect. Put the computation in `prepare.py` with the source of every input in a comment.

Is a cropped figure legible? Its smallest text, as it will be shown, must be 14 pt (≈ 19 px) or
larger: measure the height of a tick label in the original image in px, and multiply by the
scale at which the crop will be shown — `lint --metrics` prints it for every slide as `img ×0.45`.
A tick label 16 px tall in a crop shown at ×1.1 is 18 px — just legible. When it is too small,
crop tighter (fewer panels, a wider slot) rather than accept unreadable type; in the appendix,
where the full figure is reference, small type is tolerated.

**Cutting panels out — `scripts/figpanels.py`.** Composite figures stand on a white ground with
gutters between the panels, and those gutters can be found by machine; which panel the slide needs
cannot. So the work is split: the script finds and numbers the panels, you look and choose.

```
cd <deck-dir>
python "<skill-dir>/scripts/figpanels.py" <material>/fig3.png --preview figures/_panels_fig3.png
      → fig3.png: 2057x998 px, 3 panels … ; the preview shows each panel boxed and numbered
python "<skill-dir>/scripts/figpanels.py" <material>/fig3.png --crop 2 --out figures/fig3_b.png --max-width 1400
python "<skill-dir>/scripts/figpanels.py" <material>/fig3.png --crop 1,3 --arrange row --out figures/fig3_ac.png
python "<skill-dir>/scripts/figpanels.py" <material>/fig5.png --box "40,20,1800,300;40,780,1800,980" --arrange col --out figures/fig5_rows.png
```

- The split follows white space, not meaning: a panel letter or an axis title that stands apart is
  folded into its panel, but check the preview; when a split is wrong, crop a `--box` or several
  numbers together. Every output is trimmed to a narrow white margin (`--pad`).
- Rows picked from a figure laid out as a table (a header row and three of its rows) may be set one
  above the other with `--box "…;…" --arrange col`: it is still a crop when the header row comes
  first, the rows keep their original order, and nothing in them is changed.
- Read the material by its path and write only into the deck's `figures/`.

**Whose figure is it?** When the talk presents the authors' own work (the presenter speaks as an
author), their figures need no credit on the slide; the paper is named on the cover or in the
notes. When the figure is someone else's, cite it where it is shown — the reference mark in the
message, a bullet or the caption, with the entry on the reference slide — and when it is used under
a licence such as CC BY, the reference entry carries the licence and says it was cropped
(「文献[3]の図2より一部を切り出し、CC BY 4.0」 on the reference slide, not under the figure).

How to read a figure off, when you must: find the marks (points, bar ends) by their colour or
shape in the image with a few lines of Pillow / numpy in `prepare.py`; map pixel to value with two
tick marks of each axis; then check the values against what the text reports — a difference
between two conditions against the reported difference (or its test statistic × standard error),
a mean against the table. Record the largest discrepancy in the notes. A value that cannot be
read (two marks on top of each other) is placed from the text, if the text gives it, or left out.

## 2. Choose the form

| What the slide says | Form | Component |
|---|---|---|
| "this is what it looks like" / "these two differ" | real images side by side with their values | `samples` |
| "this is the screen / the apparatus / their figure" | one image | `fig(fill=True)` |
| a ranking; a breakdown into many parts | horizontal bars, sorted | `bars` |
| a few values compared | vertical bars with values on top | `vbars` |
| what share of a whole each part is (2–4 parts); how that changes between conditions | bars that run to 100%, the whole in the title, each part named | `shares` |
| values with a sign (effects, differences, terms of a sum) | bars from a centre line, both directions named | `bars(signed=True, ends=(…, …))` |
| two kinds of quantity | two charts side by side, each titled | `cols` + `vbars` ×2 |
| a pipeline, a procedure | flow: things in boxes, operations on arrows | `flow` |
| where this work stands among others | what actually differs: an amount on its own axis at its real values, a time on a time axis, the two settings as pictures (§7) | `bars` / `vbars`, matplotlib, `samples` |
| (rarely) a trade-off between two amounts that only this work holds together, the evidence differing in kind | a position map placed by judgement, the evidence under each name, this work in a dashed ring (§7) | `posmap` |
| who was where in an experiment; what they saw | the setting drawn, people as people | `svg` + `person` |
| what a hypothesis predicts | the predicted pattern, no numbers, no ticks | matplotlib or `svg` |
| a trend over an ordered axis | line plot, lines labelled at their ends | matplotlib |
| a relation between two quantities | scatter, only the named points labelled | matplotlib |
| a distribution | histogram with the mean marked | matplotlib |
| a definition | formula + real examples of low / high | `math` + `samples` |
| a model | equation + one worked case | `math` + `bars(signed=True)` |
| exact values for reference | table of numbers, in the appendix | `table` |

Not available, on purpose: pie and donut charts (a share is `shares`), 3-D charts, dual-axis
charts, radar charts, gauges, comparison matrices of text, stat cards, timelines of text boxes,
icon grids, and plots whose two axes are lists of names (slidekit warns, lint F7).

## 3. Real images — `sk.samples()` / `sk.fig()`

```python
sk.samples(
    sk.sample("figures/road_sound.png", "0.3%", "補修の順位 118位"),
    sk.sample("figures/road_alligator.png", "12.6%", "補修の順位 1位", tone="hot"),
)
```

- **Choose the examples from the data, not by taste.** The highest and the lowest; the case at
  each end of the quantity being explained. Extremes are honest ("these are the top and bottom of
  120 sections") and make the difference visible without explanation. Say in the notes how they were
  chosen.
- **Each image carries the value it stands for**, large, directly under it. What the value *is*
  is said once: by the message, or by `caption=`. A per-image `note` adds a second quantity only
  when the slide is about the relation between the two (indicator value and rating).
- `tone="accent"` / `tone="hot"` colours a value to tie it to a line or bar of the same colour
  elsewhere on the slide.
- 2 images for a contrast (each gets half the width). 3–6 for a series: `tight=True` narrows the
  gaps, `small=True` shrinks the values. `stack=True` puts two images one above the other, for a
  column beside a plot.
- **Order follows what the images are paired with.** Beside a plot, stack them in the order of
  the line ends they belong to (the higher line's image on top). In a series along a scale, left
  to right is low to high. The eye should go straight from a mark to its example; two such paths
  must not cross.
- The value and its note stay within the width of the image above them (containment, lint H1):
  keep the note short.
- The images share the free height of the slide. Fewer words below → larger pictures. If the
  linter says an image is under 110 px tall (F2), the slide has too many words.
- `sk.fig(path, fill=True, shot=True)` is the same for one image. `shot=True` (the default in
  `sample`) draws a hairline so that a screenshot with a white edge has a visible boundary.

Images must be sharp: at least 1.5 image pixels per slide pixel. For two images side by side at
4:3 that means 650 px wide or more; for a single full-width image, 1,300 px. Get a larger
original rather than upscaling.

When no larger original exists — the only photograph of an apparatus is a figure 500 px wide in
the paper — look again before giving up: the HTML version of a paper often links the full-size
figure, and supplementary files hold originals. If there is truly none:

1. crop to the part the slide is about, so that fewer pixels have to fill the place;
2. show it no wider than about twice its pixel width (`sk.fig(path, width=…)`): softer than a
   sharp image, still clean. Beyond that it is visibly blurred on a projector;
3. never sharpen, upscale with a filter, trace or redraw it — that would be a different picture;
4. if the picture is essential (the one view of the apparatus), keep it at that size, silence I2
   on that slide with the reason in a comment, and name it in the report. If it is not essential,
   leave it out and show the thing another way (a drawing of the setting with icons).

No effects: no shadow, tilt, rounded corners or device frame. Do not decorate a photo or a
screenshot. To point at one place in it, crop to that place, colour its value (`tone="hot"`), or
name it in the message. A ring is for charts and diagrams — your own (§8, §9), or a chart taken
from a paper (`sk.fig(…, ring=…)`, §1) — not for photographs.

## 4. Preparing images and data — `prepare.py`

When figures need the material to be processed — finding the extreme cases in a CSV, resizing
large images, computing a quantity for one example — write `<deck-dir>/prepare.py`. It reads the
material (path given as an argument, never hard-coded), and writes into `<deck-dir>/figures/`:

- the images the deck uses, resized to about 1,000–1,400 px wide (JPEG quality ~88 for
  photographs and screenshots);
- `figures/data.json` with every number the charts need.

`deck.py` then reads only `figures/`. The deck can be rebuilt without the material, and the
selection of examples is reproducible.

```python
# prepare.py (sketch)
import csv, json, sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")        # Japanese output on a Windows console
src = Path(sys.argv[1]); out = Path(__file__).parent / "figures"; out.mkdir(exist_ok=True)
rows = list(csv.DictReader(open(src / "scores.csv", encoding="utf-8")))
rows.sort(key=lambda r: float(r["score"]))
picks = {"bottom": rows[0], "top": rows[-1]}
data = {}
for name, r in picks.items():
    im = Image.open(src / "images" / r["file"]).convert("RGB")
    im.thumbnail((1200, 1200))
    im.save(out / f"case_{name}.jpg", quality=88)
    data[name] = {"img": f"figures/case_{name}.jpg", "score": round(float(r["score"]), 2)}
(out / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
```

Print what was selected, and check that it reproduces the numbers in the material (a wrong
example is worse than none). Record the computed numbers in `numbers.md` like any other.

Use only the standard library, `numpy` and `Pillow` unless the environment already has more.
Write every script as a file in the deck directory and run it by its path: piping a script that
holds Japanese text or backslashes through a shell here-document can garble it (Windows in
particular).

## 5. Bars — `sk.bars()` / `sk.vbars()` / `sk.shares()`

Drawn in HTML in the deck's own type: they take the free height of the slide and never need
sizing.

```python
sk.bars([("幅3mm以上", "98"), ("幅1〜3mm", "95"), ("幅1mm未満", "91")],
        hot=["幅1mm未満"], axis_max=100, title="ひび割れの幅ごとの発見率（%）")

sk.vbars([("輝度の勾配[3]", "62"), ("本研究", "91")],
         highlight=["本研究"], axis_max=100, title="幅1mm未満の発見率（%）")

sk.bars([("ひび割れ率", "+0.9"), ("交通量", "+0.5"), ("前回補修からの年数", "-0.2")], signed=True,
        ends=("優先度を下げる", "優先度を上げる"), title="この区間の各項（点）")
```

- **Values on the bars, no axis.** Pass values as strings to fix the digits (`"11.0"`).
- **Sort** horizontal bars, largest first, unless the order itself means something.
- **Colour is meaning**: `hot=` red for the bars the slide is about; `highlight=` dark blue for
  this work among others; `light=` light blue for a variant of this work; the rest grey. Usually
  one of `hot` / `highlight` is enough.
- `title=` says what the numbers are, with the unit. It is small; the message says what they mean.
- `axis_max=`: a round number just above the largest value. Give two charts that are compared the
  same `axis_max`. Bars start at zero, always. Never a total far past the data — scores near 30 on
  a 100-point axis leave two thirds of the chart empty (slidekit warns; lint F6). If the total
  matters, chart the share of it, or name it in the title.
- **Signed bars need their directions named.** A bar to the left means nothing until the audience
  knows what "left" is: `ends=("晴天より低い", "晴天より高い")` writes it under the two ends of the
  axis. And when the claim is about the quantities themselves — time in each condition, the rate
  in each group — chart those quantities, not the coefficients: 「長い・短い」 is seen at once in two
  bars and has to be decoded from a sign.
- `bars`: up to ~12 rows (labels shrink to 14pt from nine rows). `vbars`: 2–7 bars; a label may
  contain `\n`. Two bars standing alone (not in a column) get wider columns by themselves, so the
  chart still carries the slide; in `cols` they stay narrow.
- One chart = one kind of number. Different kinds → separate charts with their own titles (in
  `cols`), or separate slides.
- Error bars, grouped bars: matplotlib (section 8); write the values with `sk.bar_values` so that
  they sit above the whiskers. Include error bars when the comparison depends on them and the
  material gives them, and say once what they are (「エラーバーは標準偏差」, the caption);
  otherwise leave them to the appendix. Decide — this is not a question for the user.

### Shares of a whole — `sk.shares()`

```python
sk.shares(
    [("導入前", ["52", "30", "18"]), ("導入後", ["74", "12", "14"])],
    parts=["その場で解決", "折り返しで解決", "未解決"], highlight="その場で解決",
    title="問い合わせ全体に占める割合（%）",
)
```

A percentage means nothing until the audience sees **what 100% is and what the part is**. A bar
that says 「ランクⅢ・Ⅳ 38%」 beside the row name 「区分」 leaves both open: 38% of what, and what
are ランクⅢ・Ⅳ? `shares` makes the answer part of the chart:

- `title=` (required) names the whole and the unit: 「点検した市道の全区間に占める割合（%）」.
- `parts=` names every part — the rest of the whole too — in words the audience knows. A code, a
  grade or a category name that has not been explained (「ランクⅢ・Ⅳ」「区分A〜C」) is replaced by
  what it means (「補修が必要な区間」); say the code aloud if the field uses it. When the parts are
  steps of a scale the audience does not know and the material gives every step, show the scale:
  all its steps as parts, in order.
- Every segment carries its value, and its name wherever the name fits; slidekit refuses a part
  too narrow to be named anywhere. 2–4 parts; more, or small ones, go to `bars()`, sorted.
- The rows are wholes of one kind split into the same parts: before / after, condition A / B.
  **Two shares of different wholes are never rows of one chart** — 「全区間のうち補修が必要な区間」
  above 「昨年補修した区間のうち再び傷んだ区間」 reads as one comparison and is two facts. Give
  each its own figure, or chart one and say the other in a bullet.
- The part the slide is about comes first and is coloured (`hot=` red, `highlight=` dark blue), so
  its bars start together at the left and the rows compare at a glance.
- A single share is a thin strip; it rarely carries a slide alone. Pair it with what it is about
  (examples of the parts, in `cols`), or let the bullets carry the second fact.

## 6. Flow — `sk.flow()`

```python
sk.flow(
    sk.thing("路面画像", img="figures/road.png", width=170),
    sk.op("検出"),
    sk.thing("ひび割れ画素", img="figures/road_mask.png", width=170),
    sk.op("集計"),
    sk.thing("区間の指標", values=[("ひび割れ率", "4.2%"), ("最大幅", "3.1mm"), ("ほか2指標", "")]),
    sk.op("順位付け"),
    sk.thing("補修の順位", media=rank_bars(), accent=True),
)
```

Two rules. **A box is a thing; an arrow is an operation.** And **a box shows its thing.**

### A flow must be worth drawing

```
×  ┌────────┐ 検出 ┌──────────┐ 集計 ┌────────┐ 順位付け ┌────────┐
   │路面画像 │ ──→ │ひび割れ画素│ ──→ │区間の指標│ ────→ │補修の順位│     words in boxes
   └────────┘      └──────────┘      └────────┘        └────────┘

○  ┌────────┐ 検出 ┌──────────┐ 集計 ┌──────────────┐ 順位付け ┌────────┐
   │[路面]   │ ──→ │[検出結果] │ ──→ │ひび割れ率 4.2%│ ────→ │ ▇▇▇▇▇▇ │
   │         │      │          │      │最大幅  3.1mm │        │ ▇▇▇▇   │   one real case,
   │路面画像 │      │ひび割れ画素│      │区間の指標    │        │補修の順位│   walked through
   └────────┘      └──────────┘      └──────────────┘        └────────┘
```

The first says nothing that 「画像からひび割れを検出し、区間ごとに集計して順位を付ける」 does not,
and it is a thin strip that leaves the slide empty. The second shows what an input looks like,
what the detector finds in it, what "the indicators of a section" are (named numbers), and what
comes out. Take **one real case from the data** and put it in the boxes:

| The thing is | Give the box | |
|---|---|---|
| an image, a document, a screen | `img="figures/…"` | the actual one |
| a set of quantities | `values=[(name, number), …, ("ほか2指標", "")]` | three to five real numbers of this case |
| one quantity | `value="4.2%"` | the actual result |
| a breakdown, a distribution | `media=` a small chart drawn with `sk.svg` from the real data (shapes only) | the chart the audience will see in full later |

If you cannot fill the boxes — the steps are abstract, there is no case to follow — then the
content is not a flow figure: say it in bullets, or find the figure that shows it (an example
of the input and output side by side, with `samples`).

### Boxes and arrows

| × | ○ |
|---|---|
| ［デザイン原則］→［視覚統計量］→［線形回帰］→［寄与の分解］ (an example from review) | ［路面画像］─検出→［ひび割れ画素］─集計→［区間の指標］─順位付け→［補修の順位］ |

In the first, data appears to turn into "linear regression" — an object becomes an action. Ask of
every box: *can I point at it?* An image, a set of values, a model, a score, a report: yes.
「回帰」「抽出」「正規化」「評価する」: no — those go on arrows, and the box after the arrow is what
the operation produces.

- Labels are nouns of a few characters. No sub-label (a small explanatory line) under a label.
- What is in a box is real and legible: the data of the case being followed. Not an icon, not an
  anonymous squiggle for atmosphere.
- **One direction.** A flow runs left to right on one line: it is the one place on a slide where
  the eye is sent sideways. Nothing else on that slide points sideways. The bullets under it add
  what the flow cannot show (the idea behind a step, the size of the data, the measure).
- **It fills its place.** With content in the boxes a flow has height (170–220 px) and spans the
  width; together with three full bullets it covers the body. A flow that is a thin strip with
  empty margins is unbalanced (lint F2, L3).
- 2–5 things. Operation names of two to four characters keep a four-box flow inside a 4:3 slide;
  when the linter says the flow is too wide (O3), narrow the picture or drop a value.
- `accent=True` marks the one box the talk is about; it is the only bold label.
- A process with a branch or a loop: `sk.svg`, kept as simple (section 9).

## 7. Where this work stands — real axes first; `sk.posmap()` rarely

「この研究はどこに位置するのか」 is easily answered with a picture that looks like data and says
nothing. Before drawing anything, ask **what actually differs** between this work and the others —
and whether the audience needs a picture for it at all.

### A place on a chart is a value

An axis is an amount, or the ordered steps of one (school years, the grades of a scale in their
order). A list of kinds is not: who was studied (大学生 / 高校生), what was measured (直後の得点 /
1週間後の得点), which family of method. Put two such lists on two axes with a dot at a crossing, and
the place means nothing — swap two rows and the chart is the same — while the grid, the axes and
the dots promise a measurement that is not there. It is a table of words dressed as a chart.
slidekit warns when a plot has names on both axes and marks at their crossings, and lint reports
it (F7).

```
×  対象                                   ○  視聴から小テストまでの日数
   高校生                     ◎本研究         ●───────●──────────────────────────◎
   大学生   ●[3]     ●[4]                      0日      1日                         7日
            直後      翌日     1週間後          先行研究[3] 先行研究[4]              本研究
```

On the left the place of each dot is arbitrary. On the right the one thing that really differs —
how long after watching each study tested — is an axis with values, and this work's place is
read at once; that the students were of another age is said in a bullet. Ask what differs, and
show that:

| What differs | Show it as |
|---|---|
| an amount (the narrowest crack found, the size of the sample, the cost) | the values on one real axis — bars, this work coloured |
| a time (how many days after watching each study tested; how many years of inspection records each method used) | a time axis with each study at its real time |
| a kind of object or setting (motorways and city streets; students and workers) | the two settings side by side as pictures (`samples`, a drawing with icons), the difference visible |
| several of these | the one that the purpose of this work turns on; the others in two bullets |

Often the honest answer is that the position needs no picture of its own: the prior-work slide
shows the problem (real examples of what earlier methods miss, the numbers they report as bars)
and two bullets name the gap.

### A position map — only when the position is the point

`sk.posmap` places a few things by judgement on two axes. Using it is a decision to make each
time, not a habit and not the picture of a prior-work slide: lint lists every position map (F8,
info), and the report names the reason the slide needs it.

**It works when all of these hold:**

1. **The talk turns on a trade-off** between two amounts that the listeners weigh against each
   other: each of the other approaches gives up one of them, and this work (or the proposal)
   holds both. Two dots in opposite corners and a ring in the third show that at a glance — and
   the listeners do not already know it, or two bullets would do.
2. **Both axes are amounts**: they run from less to more (「費用の安さ」「答えられる質問の幅」), and
   they are what people in the field compare the approaches on.
3. **The evidence for the places differs in kind** — a yearly cost for one option, a number of
   questions for another — so that the points cannot share a scale.
4. Each place follows the order the material supports.

**It does not work — use another form — when any of these holds:**

- the others differ from this work in **kind** (who was studied, which effect was measured): there
  is no axis (above);
- they differ on **one** property: two bars of it;
- every point has the **same measures** on both axes: plot the values (a matplotlib scatter with
  ticks, the points named) — a place that is a value beats a place by judgement;
- the gap is **one missing thing** (「〜は未検証」), or there is only one other approach: a bullet
  says it;
- the map would only repeat the two bullets under it, or the axes were chosen so that a corner
  comes out empty.

When it is drawn, make every part of it carry something — a few dots on two arrows is not enough:

```python
sk.posmap(
    [("電話窓口の増員", 0.12, 0.86, "right", "年約1,200万円"),
     ("FAQページの整備", 0.88, 0.14, "left", "掲載した約40問だけ")],
    x="費用の安さ", y="答えられる質問の幅",
    target=("チャット導入", 0.86, 0.86),
    width=deck.span_px(9), height=330,
)
```

- **The evidence under each name.** The fifth element of a point is written bold on a second line
  under its name: the fact that puts it where it is — usually what it falls short on (「年約1,200万
  円」 under the costly option, 「掲載した約40問だけ」 under the narrow one). The audience reads why
  each dot sits where it does without the speaker.
- **This work in a dashed ring** (`target=`), and nothing else marks the empty region: the ring
  already says where this work aims.
- **The bullets say what is wrong with the others.** One bullet for each other approach, ending
  on what it falls short on, with its strength only as the contrast in front (「すべての質問に答え
  られるが人件費が年約1,200万円」). Bullets that only describe or praise the others leave the
  audience asking what is wrong with them, even when the figure shows it as numbers; the number at
  a point may appear again in the bullet that says what it means.
- **Names that distinguish** (SKILL.md rule 15), and axis names that say what increases
  (「〜の安さ」「〜の幅」). Two or three dots.
- `side` places each name (and the value under it): `"right"` (default), `"left"`, `"above"`,
  `"below"`. Both axis names are horizontal and the plane is centred in the drawing.

## 8. Plots with matplotlib — `sk.new_fig()` / `sk.save_fig()`

For lines, scatters, histograms and anything the HTML charts cannot draw. `slidekit` sets the
font (the deck's own), sizes, colours and spines; you supply the data and the few labels that
carry the point.

**Size first.** The figure is created at the exact size it will occupy and is never scaled, so
14 pt in the plot is 14 pt on the slide.

```python
fig, ax = sk.new_fig(deck.content_w, 340)        # full width, with two bullets below
fig, ax = sk.new_fig(deck.span_px(6), 330)       # half width, in cols("6-6", …)
```

Heights: see the capacity table in layouts.md §2 (about 400 px with two bullets under it, 360 px
with three). `lint --metrics` shows whether the slide is full.

Colours: `sk.C["accent"]` (dark blue — the subject), `sk.C["hot"]` (red — the one to look at),
`sk.C["accent2"]` (light blue — a variant of the subject), `sk.C["mute"]` (grey — comparison),
`sk.C["ink"]`, `sk.C["ink2"]` (text, axes). Sizes: `sk.PT["sub"]` (17) for labels on the data,
`sk.PT["small"]` (14, the default) for axes.

### Line plot

```python
fig, ax = sk.new_fig(deck.content_w, 340)
ax.plot(x, baseline, color=sk.C["mute"], marker="o")
ax.plot(x, ours, color=sk.C["accent"], marker="o")
# label the lines at their right ends instead of a legend; leave room with xlim
ax.annotate("提案手法", (x[-1], ours[-1]), xytext=(10, 0), textcoords="offset points",
            va="center", fontsize=sk.PT["sub"], fontweight="bold", color=sk.C["accent"])
ax.annotate("従来手法", (x[-1], baseline[-1]), xytext=(10, 0), textcoords="offset points",
            va="center", fontsize=sk.PT["sub"], color=sk.C["ink2"])
ax.set_xlim(x[0] - 0.4, x[-1] + 1.8)
ax.set_ylim(0, 80)
ax.set_yticks([0, 20, 40, 60, 80])
sk.ylabel_top(ax, "正答率（%）")
sk.hgrid(ax)
plot = sk.save_fig(fig, "trend", alt="正答率の推移")
```

### Scatter plot

```python
fig, ax = sk.new_fig(deck.span_px(10), 370)
for name, x, y, is_subject in points:
    ax.scatter(x, y, s=120 if is_subject else 80,
               color=sk.C["hot"] if is_subject else sk.C["mute"],
               edgecolors="white", linewidths=1.5, zorder=3 if is_subject else 2)
# name only the points the talk mentions
ax.annotate("区間A", (xa, ya), xytext=(10, 0), textcoords="offset points",
            va="center", fontweight="bold", color=sk.C["ink"])
ax.set_xlabel("ひび割れ率（%）")
sk.ylabel_top(ax, "補修までの年数の平均（年）")
sk.hgrid(ax)
```

### Histogram

```python
fig, ax = sk.new_fig(deck.content_w, 330)
ax.hist(values, bins=20, color=sk.C["mute"])
ax.axvline(mean, color=sk.C["accent"])
ax.annotate(f"平均 {mean:.1f}", (mean, ax.get_ylim()[1]), xytext=(8, -4),
            textcoords="offset points", va="top", fontsize=sk.PT["sub"], color=sk.C["accent"])
ax.set_xlabel("ひび割れ率（%）")
sk.ylabel_top(ax, "区間の数")
sk.hgrid(ax)
```

### Two curves whose shape is the point (ticks replaced by words)

```python
fig, ax = sk.new_fig(deck.span_px(6), 330)
for curve, colour in ((steep, sk.C["accent"]), (flat, sk.C["hot"])):
    ax.plot(curve.x, curve.y, color=colour)
    ax.annotate(curve.label, (curve.x[-1], curve.y[-1]), xytext=(8, 0), textcoords="offset points",
                va="center", color=colour, fontsize=sk.PT["sub"], fontweight="bold", annotation_clip=False)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xticks([1, 256]); ax.set_xticklabels(["大まかな明暗", "細部"])   # words, when the numbers do not matter
ax.set_yticks([]); ax.minorticks_off()
ax.set_xlabel("空間周波数"); sk.ylabel_top(ax, "振幅")
fig.get_layout_engine().set(rect=(0, 0, 0.88, 1))                      # room for the labels at the right
```

### Pointing at the point: a direct label and one ring

```python
fig, ax = sk.new_fig(deck.span_px(7), 360)
x = [0, 1]                                                          # two real conditions: two ticks
ax.plot(x, ours, color=sk.C["accent"], marker="o")
ax.plot(x, base, color=sk.C["mute"], marker="o")
for ys, name, colour in ((ours, "本研究", sk.C["accent"]), (base, "輝度の勾配", sk.C["ink2"])):
    ax.annotate(name, (x[-1], ys[-1]), xytext=(12, 0), textcoords="offset points",
                va="center", fontsize=sk.PT["sub"], color=colour)
gap = (ours[-1] + base[-1]) / 2
ax.annotate(f"差 {ours[-1] - base[-1]:.0f}ポイント", (x[-1], gap), xytext=(-18, 0), textcoords="offset points",
            ha="right", va="center", fontsize=sk.PT["sub"], fontweight="bold", color=sk.C["hot"])
sk.ring(ax, x[-1], gap, 44, 130)                                  # the one place to look (size in px)
ax.set_xticks(x); ax.set_xticklabels(["晴天", "雨天"])
ax.set_xlim(-0.3, 1.6); ax.set_ylim(40, 100)
sk.ylabel_top(ax, "幅1mm未満の発見率（%）")
sk.hgrid(ax)
plot = sk.save_fig(fig, "weather", alt="天候ごとの発見率")
```

The message says the finding (「**雨天**でも輝度の勾配より30ポイント高い発見率」); the figure shows
where it is: the gap labelled in red, one ring around it. Without the label and the ring the
audience sees two lines and has to work out which distance the speaker means.

### Bars with error bars

```python
fig, ax = sk.new_fig(deck.span_px(7), 340)
colors = [sk.C["hot"] if c == subject else sk.C["mute"] for c in cats]
bars = ax.bar(cats, means, yerr=sds, color=colors, width=0.5,
              error_kw={"ecolor": sk.C["ink2"], "elinewidth": 1.2, "capsize": 5})
sk.bar_values(ax, bars, ["7.2", "5.1"], err=sds)     # each value above the cap of its whisker
ax.set_ylim(0, 10)                                    # room above the tallest whisker
ax.set_yticks([0, 5, 10])
sk.ylabel_top(ax, "小テストの得点の平均（点）")
sk.hgrid(ax)
plot = sk.save_fig(fig, "score", caption="エラーバーは標準偏差", alt="条件ごとの得点")
```

A value written at the top of the bar sits on the whisker, which runs up through the same
place; written beside it, it drifts off its bar. `sk.bar_values` puts each value above the cap of
its error bar, bold in the bar's colour when the bar is red or dark blue, and warns when a value
would leave the plot (raise `ylim`). Say once what the error bars are (the caption).

Rules for plots:

- **Say where to look** (SKILL.md rule 3): the series the slide is about in red or dark blue, the
  decisive value labelled directly, or one `sk.ring`. Red in a plot is what the linter takes as its
  mark (F5), so keep `sk.C["hot"]` for the one thing the slide is about.
- **Name an axis by its quantity**, with its unit in parentheses — the only parentheses in an axis
  name — and with the aggregate when the values are aggregates: 「発見までの時間の平均（秒）」. Not a
  list of what is plotted, not 「予測値（検出率・誤検出）」-style glosses.
- **An axis with no values has no ticks.** When an axis only runs from less to more (a schematic,
  a prediction), its name says what increases (「照明の明るさ」) and `ax.set_xticks([])` removes the
  ticks; 「低」「高」 at the ends are ticks pretending to be values. Two ticks are right when they are
  two real conditions or values (晴天 / 雨天, −1 SD / +1 SD).
- **A place is a value.** Both axes of a plot that places marks are amounts (or the ordered steps
  of one); names of kinds on both axes make a grid in which no place means anything (§7, F7).
- **One quantity per axis.** Three outcomes drawn against one axis read as one curve. Give each
  its own panel (`sk.new_fig(w, h, ncols=3)`, one `ax` each) or its own slide — unless they take
  the same shape: then draw the shape once, name the axis by the quantity they share in plain
  words (「理解の程度」), and list the outcomes once in the caption. Identical panels side by side
  are clutter.
- **A ring is sized in px** (`sk.ring(ax, x, y, width, height)`; x, y in data units), so it looks
  the same on every panel; at most one per panel, on the panels the slide is about. To ring the
  gap between two points, `sk.ring_between(ax, x, y1, y2)` measures it on the finished plot.
- **Name lines with `sk.end_labels(ax, [(name, x, y, colour), …])`**: at the line ends, no legend,
  pushed apart when the ends are close; the subject's name bold.
- **A schematic** (a prediction, a concept) uses `sk.schematic_axes(ax, x=…, y=…)`: no ticks, an
  arrowhead at the end of each axis, the names at the arrowheads. Name what increases
  (「理解の程度」「〜の高さ」), never a placeholder (「各指標」「予測値」).
- **The plot sits on the centre line.** `sk.save_fig` moves the plot area to the middle of the
  image, so that the plot — not the plot plus the names written beside it — is centred on the
  slide, with its axis name and caption under its middle; and it lets each axis line run a little
  past the last tick (not dead at the last point, not under the labels). `center=False`,
  `trim=False` turn these off, with a reason.
- **No `$…$` in a plot.** Inside matplotlib, `$…$` is matplotlib's own math, not the slide's KaTeX:
  「p = .007」 comes out spaced wrongly. Write it as plain text (「p = .007」).
- **The axis line ends where the scale ends.** `sk.save_fig` stops the x and y axis lines at the
  last tick or the furthest data, so that a line does not run on under labels written past the
  data. Pass `trim=False` only with a reason.
- Colours only from `sk.C`. One series is the subject; the rest are grey.
- **Label the data directly** — values on bars, names at line ends. No legend box, no chart
  title (the message is the title).
- **Remove what nobody reads**: tick numbers when only the shape matters, gridlines when values
  are printed on the marks, the y axis when bars carry their values.
- **No rotated text.** Name the y axis with `sk.ylabel_top(ax, "…")` — horizontal, above the top
  of the axis — instead of `ax.set_ylabel`. Do not rotate tick labels either: shorten them, or
  turn the chart into horizontal bars.
- Do not call `ax.set_title`, `plt.legend` with a frame, `plt.style.use`, or `rcParams.update`.
- No text below `sk.PT["tiny"]` (12).
- Leave room for direct labels inside the figure (widen `xlim`, or reserve a margin as above),
  and check in the visual pass that no two labels touch. When labels collide, move one with
  `xytext` or label fewer points — do not shrink the text.
- `sk.save_fig` writes `figures/<name>.svg` and returns the component. To change the size, change
  `new_fig` and rerun; an SVG is never scaled when placed.

## 9. Diagrams by hand — `sk.svg()`

For a structure that is not a flow: containment, a branch, a small network, a setting. Drawn in
slide pixels at scale 1.

```python
sk.svg("""
    <rect class="f-tint" x="0" y="0" width="200" height="72"/>
    <text class="t-bold t-mid" x="100" y="43">入力画像</text>
    <path class="ln-bold" d="M200 36H288"/>
    <path class="ln-bold" d="M278 29L288 36L278 43"/>
    <rect class="f-accent-tint" x="288" y="0" width="200" height="72"/>
    <text class="t-bold t-accent t-mid" x="388" y="43">指標</text>
    """, 488, 72, label="画像から指標へ")
```

Pass only the inner markup, the width and the height. Use these classes — no `fill=`, `stroke=`,
`font-size=` or `style=` attributes (the library rejects them):

| Class | On | Effect |
|---|---|---|
| `ln` | line, path | 1.5 px grey line |
| `ln-bold` | line, path | 2.5 px grey line (axes, arrows) |
| `ln-hair` | line, path | 1 px hairline (guides) |
| `ln-accent` / `ln-hot` | line, path | 2.5 px accent / red line |
| `ln-dash` | circle, path | dashed accent outline (a target, something not yet there) |
| `f-tint` | shapes | pale neutral fill (an ordinary box) |
| `f-accent-tint` | shapes | pale accent fill (the box that is the subject) |
| `f-accent` / `f-accent-2` / `f-hot` / `f-mute` | marks | dark blue / light blue / red / grey |
| `f-ink2` | path | dark grey fill (arrow heads) |
| `f-bg` | shapes | white (to mask) |
| `ln-hot` on `ellipse` | shape | a red ring — the one place to look (once per figure) |
| *(none)* | text | 17 pt |
| `t-sm` / `t-body` | text | 14 pt / 20 pt |
| `t-bold`, `t-mute`, `t-accent`, `t-hot` | text | weight and colour |
| `t-mid`, `t-end` | text | anchor at centre / end (default is start) |

### People and things with a shape

Draw what has a familiar outline as that outline — recognisably. A circle labelled 「被験者」 is a
symbol the audience has to decode; a balloon or a blob standing in for a hand or a device is
worse: it reads as something else and looks forced. Use, in this order:

1. **An icon from the bundled sets** (open source: Health Icons and Phosphor under MIT, Material
   Symbols under Apache-2.0; installed by `doctor.mjs`'s `npm install`). Search in English, fetch
   into the deck, place with `sk.icon` inside `sk.svg`:

   ```
   node "<skill-dir>/scripts/icons.mjs" search hand               → ph:hand-fill, material-symbols:back-hand, …
   node "<skill-dir>/scripts/icons.mjs" show <deck-dir> ph:hand-fill material-symbols:back-hand
                                                                   (writes figures/icons/_preview.html to compare)
   node "<skill-dir>/scripts/icons.mjs" get <deck-dir> ph:hand-fill
   ```
   `sk.icon("figures/icons/ph--hand-fill.svg", x, y, size, cls="f-mute", flip=False)` — x, y is the
   centre, size the width in px. Filled shapes read best; the search lists them first. `show`
   writes one PNG of the candidates (`figures/icons/_preview.png`) to compare them at a glance.
   Search with English words as separate arguments: names that contain any of them are listed,
   those with all of them first — so give synonyms together (`search phone smartphone mobile`; a
   person seen from the side is a "head"; a screen is a "monitor" or "desktop"). The tool records
   each set's licence in `figures/icons/LICENSES.md`.
2. **A composition** when no single icon shows the thing: a person and a prop over the right
   spot (a phone at the ear, glasses on the face, a helmet on the head), at matching scale. Search
   for the combination first — sets often have it (a person with a cane, a person at a desk). A
   prop that no set has is drawn **in the icon's own coordinates** with
   `sk.icon(…, overlay='<path class="ln f-bg" d="…"/>')`, so it moves, scales and flips with the
   person; `sk.icon_box(path, x, y, size)` tells where the icon lands, for a name under it, and
   `sk.icon_point(path, x, y, size, px, py, flip=…)` where one spot of the icon (px, py in its own
   coordinates) lands in the drawing — for an arrow or a line that must end on the lens of a
   camera or the screen of a phone. Look at the icon file (its viewBox: 0–48 Health Icons, 0–24
   Material Symbols, 0–256 Phosphor) to find the spot.
3. **`sk.person(x, y, height, cls=…)`** — a plain head-and-shoulders figure from the front, for a
   diagram that only needs "a person here".
4. **Drawn by hand** with rects and paths — only what no set has, and only when it comes out
   recognisable at a glance. If it does not, choose another figure; a forced drawing is worse than
   none.

Keep the shapes plain and grey, and the one that is the subject (the subject of the experiment,
the inspector) in the accent colour. **Colour a drawn mark by what it depicts**: a blush may be
red, but sweat, tears or a device drawn red read as something else; the red of emphasis points,
it does not colour things. **Each thing faces the way it acts**: a camera points at the
person it records, a screen faces its viewer, two people talking face each other; mirror an icon
with `flip=True` rather than leave it facing away. Draw the setting from the front or the side when
who faces whom matters, from above when distances and positions matter, and write each name under
its shape.

```python
W, H = 680, 210
dia = sk.svg(
    sk.person(120, 20, 120, cls="f-accent")                                         # the subject
    + '<rect class="f-ink2" x="250" y="30" width="170" height="104"/>'              # a screen …
    + '<rect class="f-ink2" x="327" y="134" width="16" height="22"/>'               # … on its stand
    + sk.person(560, 20, 120)
    + '<text class="t-mid" x="120" y="190">被験者</text><text class="t-mid" x="335" y="190">講義動画</text>'
    + '<text class="t-mid" x="560" y="190">実験者</text>',
    W, H, label="視聴実験の配置",
)
```

Rules for diagrams:

- Few elements, few words. Shapes carry the meaning; labels are nouns. If the text in the
  diagram is more than about 30 characters in total, it is a list drawn as a diagram.
- Boxes are things, arrows are operations (section 6) — here too.
- One subject in the accent colour; the rest grey or pale.
- Names beside or inside their shapes. No legend, no leader lines, no numbered callouts.
- Align on a grid: equal widths, equal gaps, shared edges. Compute coordinates; do not eyeball
  them. Leave at least 12 px between a label and anything else.
- Text width: a full-width character at 17 pt is about 23 px, at 14 pt about 19 px. The linter
  flags labels that overlap or leave the drawing. Text is placed by its baseline: a 17 pt label
  needs its baseline at least 24 px below the top of the drawing (14 pt: 20 px), and about 7 px
  above the bottom.
- A drawing inside a column of `cols()` is made for the column: `deck.span_px(n)` wide for an
  n-of-12 column (`"6-6"` → `span_px(6)`), or it is shrunk and its text with it (lint I4, T1).

## 10. Equations — `sk.math()`

```python
sk.math(r"\text{ひび割れ率} = \frac{\text{ひび割れの画素数}}{\text{路面の画素数}}")
sk.math(r"\text{優先度} = \sum_{j=1}^{4} w_j z_j")
```

- Raw strings for TeX. Japanese inside `\text{…}` is set in the deck font.
- An equation never stands alone: pair it with a real example (patterns G and I in layouts.md).
- Write the equation in the audience's words where possible (a fraction of named quantities reads
  faster than symbols that need a legend).
- Define symbols aloud. A symbol table on the slide is a table of words.
- Inline math in text is `$…$`: `"輝度の勾配だけでは $R^2=0.41$"`.
- Derivations belong in the appendix.

## 11. Tables — `sk.table()`

A table is for numbers the audience may want to read off — in the appendix. `sk.table()` refuses
a table whose cells are words.

- First column: the row name. Other columns: numbers (one text column, such as a group name, is
  tolerated).
- `hot=` (red) or `highlight=` (tinted) marks the rows the talk is about; `dim=` greys rows.
- Same number of decimals within a column; units in the header (「発見率（%）」), not in the cells.
- Numbers may be written as the field writes them — `.52`, `−.48*`, `0.31**`. Say once what the
  marks mean (`caption=`).
- **Means and SDs.** Name each column by what it holds: 「平均」, 「SD」. A reader wants the means;
  give SDs only where the context needs them (the appendix table of a study), in a column of
  their own beside the mean. `3.19 (0.59)` in one cell is accepted but harder to read. A point
  one standard deviation above the mean is labelled 「+1SD」, never 「+1平均」.
- `caption=` explains marks and sort order. `small=True` for a long table; `full=True` to span
  the width.
- On a main slide, show the same numbers as bars instead.

## 12. Rules for every figure

- **Says where to look.** Each figure has one thing to see, and the slide marks it: the key words
  of the message in bold, the subject in red or dark blue, a direct label at the decisive place,
  or one ring (SKILL.md rule 3).
- **One thing to see.** Each figure has one subject, and colour says which.
- **Same thing, same colour** on every slide of the deck.
- **Little text inside.** Labels are nouns; values are on the marks. What the figure means is
  the message; how to read it is spoken.
- **No sub-labels**: no grey line under each box, no caption that repeats the message, no legend
  that repeats direct labels. At most one caption or note per slide.
- **Sized to dominate**: half the body or more. A figure that takes a quarter of the slide with
  text around it is an illustration, not the main thing.
- **Real over schematic.** Where a real example exists, show it instead of a drawing about it.
- **On the axis.** A figure is centred, and is itself balanced: a diagram whose content sits in
  one half of its canvas drags the slide to that side. In two columns, the sides weigh about the
  same.
- **One way for the eye.** Everything reads left to right and top to bottom: no rotated labels;
  names at the marks they name; paired things adjacent and in the same order; at most one figure
  per slide that runs sideways.
- **Parts inside wholes.** A caption no wider than its picture; a label inside its box.
- **A diagram shows something.** Boxes that hold one word each, joined by arrows, are text. A
  diagram earns its place by its content — real images, real numbers — and by filling it.
- **No ornament.** What is drawn is data or the thing itself. A picture that is only an aid to
  imagination is kept to the one thing the audience needs to imagine (イメージの補助は1つ) — but
  what is drawn is drawn recognisably: a person as a person, not as a labelled circle.
- **Chosen for this material.** Not the gallery's figure with new labels (SKILL.md rule 21).
- **Not filler.** Each figure is there because the point needs that figure. A second figure
  added to fill a column or a corner — a scale drawn out, a picture of a word — is filler.
- **Recognisable.** A thing with a shape is drawn as that shape, with an icon where one exists,
  facing the way it acts. A makeshift drawing that could be read as something else is removed.
- **Axes name their quantities** (SKILL.md rule 22): unit in parentheses, no ticks on an axis
  without values, one quantity per axis, the line ending with the scale.
- **A place means a value.** No grid of names with dots at the crossings. Where this work stands is
  shown by what actually differs, on a real axis or in pictures; a position map only when the
  position is the point, with the evidence at each point (§7).
- **A share names its whole**: the title says what 100% is, every part is named in words the
  audience knows, and shares of different wholes are not rows of one chart (§5).
- **Every number on a figure is in `numbers.md`.**
- Data that is not the presenter's own carries its source: a citation mark in the message, a
  bullet or the caption, with the entry on the reference slide.

## 13. Checklist

- [ ] Every main slide except 目的 and まとめ has a figure, named in the outline.
- [ ] The material's own images are used wherever they exist; examples were chosen from the data.
- [ ] No table of words, no boxes of text, no decorative graphics.
- [ ] Each chart holds one kind of number; values are on the marks; one thing is coloured.
- [ ] Every chart says where to look (bold key words in the message, red / dark blue, a direct
      label, or one ring); lint F5 is clean.
- [ ] Axes are named by their quantities; no 低/高 ticks; one outcome per axis; no axis far past
      the data (F6); no plot with names of kinds on both axes (F7).
- [ ] A position map, if any, is there because the position is the point of its slide (§7: a
      trade-off the others each give up and this work holds) — with the evidence under each name
      and bullets that say what each other approach falls short on — not because prior work
      "needs" one. Its reason is in the report.
- [ ] Every percentage shows its whole and its part in words the audience knows; shares of
      different wholes are separate charts.
- [ ] A paper's figure is redrawn only from data in the material; otherwise the picture is shown.
- [ ] People and things are drawn recognisably (icons from the bundled sets), facing the way they
      act; no forced drawing, no figure added to fill space; no caption about what was left out.
- [ ] In every flow, boxes are things and arrows are operations; the boxes show one real case
      (image, named numbers, result), not bare words; no sub-labels in boxes.
- [ ] No rotated text; lines are named at their ends; examples are in the order of what they are
      paired with.
- [ ] `cx` in `lint --metrics` is within a few percent of zero on every slide.
- [ ] Plotted figures were created at the size they are shown at.
- [ ] Text in figures is 14 pt or larger (12 pt minimum for sources).
- [ ] `fig` in `lint --metrics` is 40% or more on figure slides.
