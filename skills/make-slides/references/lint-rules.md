# Lint rules (Phase 5)

`node "<skill-dir>/scripts/lint.mjs" <deck-dir> --metrics` runs `deck.py`, opens the generated
deck in a browser, measures it, and prints findings grouped by slide.

```
  p.5  提案手法 - 全体像
    WARN  F2  the figure takes only 19% of the body; make it the main thing …
              ← div.flow "路面画像検出ひび割れ画素…"
    WARN  W1  5 bullets next to a figure; three at most …
```

- `ERROR` — the slide is broken (content cut off, markup showing, a table of words, forbidden
  styling). Always fix.
- `WARN` — the slide departs from the rules of the skill. Fix, or silence with a stated reason.
- `info` — a judgement call. Read it and decide.
- Exit code 1 when there are errors (or warnings with `--strict`).

Options: `--metrics` (per-slide numbers), `--no-info`, `--strict`, `--json`.
It also writes `out/lint.json` and `out/numbers-on-slides.md` (every number printed on a slide —
including the numbers inside plots made with `save_fig`, marked "(plot)" — for the Phase 7 check).

Before the linter runs, `deck.py` itself is executed. slidekit raises a `DeckError` for the
mistakes it can see without rendering (a message with 「、」, a table of words, nested bullets, a
bare string in the body, text too long for one line). Its message says what to write instead —
read it; do not work around it.

## How to fix findings

Fix the cause, in this order of preference:

1. **cut bullets, not bullets into stubs** — too much text is fixed by having fewer bullets; each
   one that stays is still a full line. What was cut goes to `notes=`;
2. **change the form** — show it as a figure instead of saying it; one short thing to say is a
   centred `conclusion` line, not a one-stub list;
3. **split** — two slides, or detail moved to the appendix.

The two word-count failures pull in opposite directions, and both are measured: a slide that
explains everything (D1, W1, W2) and a slide whose bullets are keywords that leave half of it
empty (L6). The target is between them: two or three complete, dense lines.

Never fix a finding by editing `slidekit.py`, `theme/` or `deck.html`, or by adding hand-written
styles through `sk.raw()`. Never fix "the figure is small" by adding text around it, and never
fix "the list is thin" with adjectives — add the number, the condition, the source.

## Silencing a rule

`deck.slide(..., lint_off="F2")` silences the rule on that slide. Put a comment beside it saying
why the slide is right as it is, and list every silenced rule in the final report. Errors should
not be silenced.

## Reading `--metrics`

```
    p.10  fig  72% | fill  85% | cx − 1% | text  55 chars | message 11 chars | 75s  結果 - 精度
```

- `fig` — share of the body **area** taken by figures. Aim for 40% or more on a figure slide;
  under 25% is a warning (F2).
- `fill` — share of the body **height** that carries content. Under 50% is a warning (L3).
- `cx` — the **centre of gravity**: how far the weight of the body sits from the centre line of
  the slide, in % of its width (− = left). Each block counts as its bounding box, weighted by
  what is drawn in it. Lists are flush left, so a small negative value is normal; aim for within
  ±5%. Beyond ±8% on a figure slide is a warning (L6): one side of the slide is empty — usually
  the right, because the bullets are stubs.
- `text` — running text in the body: bullets, conclusion, boxed statement. Labels inside charts
  and diagrams, captions and tables are not counted. Guide: under 140 (4:3) or 180 (16:9). Too
  little is also a fault: see L6 for lists that do not reach across the slide.
- `message` — length of the message in full-width characters. Aim for 18 or fewer.
- `img` — the smallest scale at which a raster image is drawn on the slide (its width on the slide
  ÷ its width in pixels). Text baked into an image shows at its height in the image × this scale:
  a 30 px label at `img ×0.45` is 13.5 px, too small (want 19 px, 14 pt). Crop tighter, or give the
  figure more room.

## The rules

### M — the message under the heading

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| M1 | error / warn | The message contains 「、」「。」 (error), is written with です・ます・である, or ends on a verb (する・できない・ている …) | One noun-ending phrase: 「〜を左右する」→「〜を左右」, 「両立できていない」→「〜の両立」, 「翻訳し、測る」→「指標決定と寄与測定」 |
| M2 | warn | The message is longer than about 20 characters | Cut to ~18; drop what the heading already says |
| M3 | info | The slide has a figure but no message | Say in one phrase what the figure shows |
| M4 | warn | The message points at something it does not contain: 逆に, 反対に, 同様に, 同じく, 前者, 後者 | A message is read alone; it is a claim with its subject and what happens to it, and a comparison names both sides: 「雨天では逆に低下」→「雨天では検出率が晴天より低下」 |

### F — figures

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| F1 | warn | A main slide has no figure | Add one (real images, bars, shares, flow, plot, equation with an example). `text_only=True` only for 目的 and まとめ |
| F2 | warn | The figure takes under 25% of the body, or an image is under 110 px tall | Fewer words; a larger plot (`new_fig` size); fewer boxes with larger pictures. Not more text. A single `shares` bar is a thin strip: pair it with another figure, or carry the second fact in a bullet |
| F3 | warn (deck) | More than a quarter of the main slides are text-only | Find the figures; see figures.md §1 |
| F4 | error / info | A table whose cells are words (error); any table on a main slide (info). Numbers in the field's notation count as numbers (`.52`, `−.48*`, `(0.59)`, `3.19 (0.59)`, `**`) | A figure or two bullets; tables of numbers go to the appendix |
| F5 | warn | A chart (bars, or a plot made with `save_fig`) says nowhere where to look: no red or dark-blue bar, no red in the plot, and no bold / red / accent words in the message | Mark the point (SKILL.md rule 3): the key words of the message in bold, the bars it is about in red (`hot=`) or this work in dark blue (`highlight=`), red for the decisive line or point of a plot with a direct label, or one `sk.ring`. One or two of these, not all |
| F6 | warn | The longest horizontal bar reaches less than 60% of its axis: `axis_max` is far above the data and the right side of the chart is empty | `axis_max` just above the largest value. A total that matters (a time limit, a maximum score) goes in the title or a bullet, or chart the share of it |
| F9 | info | The slide's only figure is a raster image (a paper's figure, a photo) and nothing beside it says what to read in it: no bullet, no conclusion line, no ring | When it is a figure of data, ring the place it is about (`sk.fig(…, ring=(l, t, r, b))`) and add a line or two that read it. A photograph that speaks for itself may stay as it is |
| F8 | info | A position map (`sk.posmap`) is on the slide. It is a judgement call every time | Keep it only if the position itself is the point — a trade-off between two amounts that the others each give up and this work holds, which two bullets would not show as quickly (figures.md §7). Otherwise show what actually differs, or say it in two bullets. Name the reason it is needed in the report |
| F7 | warn | A plot (made with `save_fig`) places marks on two axes that are both lists of names — groups across, kinds up. No place on it means anything: swap two rows and the chart is the same | Show what actually differs: an amount on its own axis at its real values, a time on a time axis, the two settings as pictures — or two bullets (figures.md §7). An axis is an amount or the ordered steps of one |

### G — flows

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| G1 | warn | A box in a flow has a label that reads like an operation (〜回帰, 〜抽出, 〜化, 〜分析 …) | A box is a thing. Put the operation on the arrow with `sk.op()` and name what it produces: `op("線形回帰"), thing("予測評定")` |
| G2 | warn | Fewer than half of the boxes of a flow show anything but a word | A flow of words is text with arrows and leaves the slide empty. Follow one real case through it — `img=` the actual image, `values=` its numbers, `value=` the result — or do not draw a flow |

### H — containment

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| H1 | warn | A part sticks out of what it belongs to: the consequence line (→) of a bullet is longer than the line it follows; the text under a picture is wider than the picture | Shorten the part (or move words up into the first line). 階層構造: a part stays inside its whole |

### W — words

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| W1 | warn / error | More than three bullets beside a figure; more than six on a slide; a nested list (error) | Keep what must be read; say the rest aloud |
| W2 | warn | A bullet or paragraph of three or more lines (only reachable through `raw()`; `points` refuses it) | One idea per bullet, two lines at most; cut to a noun phrase |
| W3 | warn | Two conclusion / boxed statements on one slide; boxed statements on more than two slides | One point per slide; the frame is for the purpose |
| W4 | warn / info | More than one small grey line (caption, note) on a slide; both a caption and per-image notes under samples (info) | Sub-labels are the mark of a generated slide. Keep one; say the rest |
| W5 | warn | A line with two or more parenthetical remarks, or three or more lines with parentheses on one slide | A gloss in brackets after the noun is English word order. Put the qualifier in front of the noun as one block (「研修を修了した経験5年以上の点検員が判定」), or say it aloud |

### D — density and wording

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| D1 | warn | Too much running text (over ~140 characters at 4:3, ~180 at 16:9; ×1.6 in the appendix) | The slide is explaining. Fewer bullets (keep each one full); move explanation to `notes=` |
| D3 | warn | Text written as sentences (。, です・ます, である) | Noun-ending phrases |
| D4 | info | An abbreviation used only once in the main deck. Roman numerals (第II期) and names with a digit (a formula such as CO2, a model number) are not counted | Spell it out, or `known_abbr=[…]` if the audience knows it or it is a name |
| D5 | warn | Two or more bullets of the form 「見出し語：説明」 | State the point itself; this label-and-explanation pattern reads as generated. (A bold label in brackets for an item referred to later — 「**[仮説1]** …」 — is not this pattern.) A term is glossed inside the line instead: 「〜を数える **MCI** で区間を評価」. On the rare slide whose job is to define a few terms, silence D5 with that reason |
| D6 | warn | A line stops on the continuative 〜ず (変わらず, 見られず) | End on 〜ない or a noun: 「処理時間は変わらず」→「処理時間は変わらない」 |

### S — structure

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| S1 | error | A slide without heading/body structure; an empty heading; text on the blank slide | Build slides with `deck.slide(heading, message, …)` |
| S2 | error / warn | The heading does not fit on one line; the cover title runs to four lines | The heading only names the part of the talk; shorten the cover title or use `sub=` |
| S5 | warn (deck) | Two slides share a heading | Add a topic: 「結果 - 精度」「結果 - 速度」; number repeats: 「指標の例(1)」 |
| S6 | warn (deck) | No `lang` on the document | `sk.Deck(…, lang="ja")` (the default) |
| S7 | error | Bare text directly inside a layout container (only possible through `raw()`) | Wrap the text in `<p>` |
| S8 | warn | The cover title breaks into very uneven lines | Put the `\n` at a phrase boundary near the middle |
| S9 | warn | Template text is still on a slide | Replace it |
| S10 | info (deck) | The topics of each part that has two or more, listed side by side | Read them as a set: they name the same kind of thing at one level, not the items of content of each slide. Results: the kind of analysis or measure (精度 / 速度 / 頑健性). Method: the stages of the procedure, all of one kind (装置 / 手順 / 測定 / 分析, or 全体像 / 検出 / 優先度の計算) — not a thing, a setting and a schedule side by side (story.md §4) |

### C — citations

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| C1 | warn / info | Names written like methods or models (CamelCase, `++`, hyphenated capitals: RoadSeg++, PaveScan-Net) appear on the main slides and nothing in the deck is cited (warn), or a name never stands on a slide that carries a citation mark (info) | Cite someone else's method, model, dataset or measure where it first appears, its reference copied from the material. This work's own names need none; names the audience knows as products can go in `known_abbr=[…]` |
| C2 | warn (deck, cannot be silenced) | A reference was entered with `sk.missing_ref`: the material does not give it | **Not yours to clear.** Do not write it from memory. Search the material once more (the name, et al., DOI, arXiv, `.bib`, README); if it is not there, ask the user, and name it first in the report |

### O — overflow

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| O1 | error | Something extends outside the slide | Cut content |
| O2 | error | Something extends outside the body area; the message does not fit on one line | Cut bullets or words; a smaller plot only if the plot was oversized. A bullet line that runs out of the slide: shorten it or break it with `\n` (lines never wrap by themselves) |
| O3 | error | Content is wider than its column / box; a flow is wider than the slide; the name or value of a part of a `shares` bar is wider than its segment | In a column: break the bullet with `\n` or shorten it. In a flow: fewer things, shorter labels, a narrower picture. In `shares`: a shorter part name, or merge small parts |
| O4 | warn | Text blocks overlap; diagram labels overlap or leave the drawing | Move or shorten labels; enlarge the drawing |
| O5 | error | Content is clipped by a container | Cut content |

### T — typography

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| T1 | error / warn | Text under 12 pt (error); under 14 pt outside sources and citation marks (warn) | Use theme components; in plots keep to `sk.PT` |
| T2 | warn | A size that is not on the type scale | Never set sizes by hand |
| T3 | warn | Over 30% of the body text is bold, or more than six emphasised runs | Bold the few keywords the slide is about (the measures, a hypothesis label), not phrases |
| T4 | warn | Italic Japanese, or underline | Remove |
| T5 | warn | A text or fill colour that is not a theme colour | Use theme classes / `sk.C` |
| T6 | warn | Four or more centred lines | Multi-line text is left-aligned |
| T7 | warn / info | The last line holds a single character (warn); lines very uneven (info; not for a bullet of a list on its own, whose second line is meant to be the shorter) | Reword, or place `\n` at a phrase boundary so the lines are similar in length |
| T8 | warn | A table cell wraps to three lines | Tables hold numbers |
| T9 | warn | A font other than the theme font | Remove the override |
| T10 | warn | A bullet of a list on its own (not in a column, not a premise of `therefore`) is broken into two lines although it would fit on one, or its first line stops before 75% of the width | Remove the `\n`, or break near the end of the line. Lines of similar length are for text set against a figure, a frame or a column; in a list on its own an early break empties the right side |

### L — layout

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| L3 | warn | Content covers under half of the body height | Enlarge the figure, or merge the slide into a neighbour. Never pad with text |
| L5 | error | The heading rule sits at a different height on some slide | Do not restyle the header. (Math in a heading, which also moves the rule, is refused by slidekit before lint runs) |
| L6 | warn / info | **Balance.** (a) A list — flush left at the margin — reaches less than 70% of the way across a 4:3 slide (65% at 16:9): stubs leave the right side empty. (b) A figure, equation or frame stands more than 4% of the width off the centre line. (c) On a figure slide, the centre of gravity of the body is more than 8% off centre. (info) One long bullet among stubs | (a) Write fuller bullets: each a line that carries a fact with its number, condition or source — not adjectives. Or change the form: one centred `conclusion` line, or the list beside the figure in `cols()`. Never centre the list. (b) Use the components; a hand-drawn diagram should be balanced within its canvas. (c) Fuller bullets, a wider figure, or two columns of similar weight |

### I — images

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| I1 | error | An image failed to load | Check the path (relative to the deck directory) |
| I2 | warn | A raster image has under 1.3 pixels per slide pixel | Use a larger original (the full-size figure linked from a paper's HTML version, the supplementary files). If none exists: crop to the part the slide needs, show it no wider than about twice its pixel width, and if the picture is essential silence I2 on that slide with the reason (figures.md §3) |
| I3 | error | An image is stretched | Set only one dimension |
| I4 | warn | An SVG figure or inline diagram is scaled | Regenerate it at the size it is shown at |

### A — forbidden styling

| Rule | Level | Meaning |
|---|---|---|
| A1 | error | Emoji or pictograph in text |
| A2 | error | Shadow, text shadow, filter |
| A3 | error | Gradient |
| A4 | warn | Rounded corners over 4 px |
| A5 | error | Animation or transition |
| A6 | warn | A box with both a border and a fill |
| A7 | warn | A thick coloured bar on the left edge of a box |
| A8 | error | Raw markup showing as text (`**`, `\textbf`, `<br>`, `$…$` that did not render) |
| A9 | warn | An inline `style=` that sets more than a size |
| A11 | warn (deck) | The deck carries its own `<style>` |
| A12 | warn | A class the theme does not define |

All of these come from hand-written HTML in `raw()`; remove the styling and use a component.

### K — deck level

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| K1 | warn / info | Too many or too few main slides for the talk length (outside 0.6–1.3 per minute); talk length not set. A disclosure slide (`deck.disclosure`) is not counted | Cut or move to the appendix; split overloaded slides |
| K2 | warn / info | `sec=` does not add up to the talk length (a disclosure's seconds count); a main slide planned for under 25 s or over 150 s | Rebalance; merge or split |
| K3 | warn | A part of the talk resumes after another part. The method and the results may alternate (提案手法 - 検出 → 結果 - 検出 → 提案手法 - 順位付け → 結果 - 順位付け) | Keep the slides of one part together |
| K4 | warn | Red text (`!!…!!`) more than once on a slide | Red marks one thing |

### R — resources

| Rule | Level | Meaning | Fix |
|---|---|---|---|
| R1 | error | A script error, a file that failed to load, a font that did not load | Check `theme/` is next to `deck.html` |
| R2 | error | `theme/` or `slidekit.py` differs from the skill's copy | `node init.mjs <deck-dir> --refresh`; never edit them |
