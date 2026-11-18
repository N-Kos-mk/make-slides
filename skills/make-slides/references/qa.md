# Looking, verifying, reporting (Phases 6–8)

Lint tells you the deck is not broken. It cannot tell you the deck is good. This file covers the
three things that remain: looking at the rendered slides, verifying the content, and reporting.

## Contents

1. The visual check
2. What to look for on the contact sheet
3. What to look for on a single slide
4. Fixing what you see
5. Verifying numbers
6. Verifying words, citations and structure
7. Speaker notes
8. The report

---

## 1. The visual check

```
node "<skill-dir>/scripts/build.mjs" <deck-dir>
```

Output in `<deck-dir>/out/`:

| File | What it is |
|---|---|
| `<deck-name>.pdf` | the deliverable (named after the deck directory: a deck in `deck/` gives `deck.pdf`) |
| `sheet-1.png`, `sheet-2.png`, … | contact sheets: every slide side by side, numbered |
| `png/01.png`, … | one image per slide at slide resolution |
| `notes.md` | speaker notes collected from `notes=` |

Procedure — it is designed to cost few images:

1. Read each contact sheet (one image shows 9 slides at 4:3, 12 at 16:9). Judge the deck as a
   whole and note slide numbers that need a closer look (section 2).
2. Open `png/NN.png` only for those slides, and for every slide that contains a plot or a
   diagram — label collisions inside figures are invisible to the linter (section 3). When the
   user limits how many images may be viewed, keep to the limit: open the plots most likely to
   collide first, and list in the report the slides that were not opened.
3. Fix, rebuild, and look at the contact sheets again. Stop when a pass turns up nothing.

Viewing images may need the user's permission under their standing rules. Ask once, at the start
of the task, for "the contact sheets and the individual slides that need it". If permission is
refused, do not view anything: say so in the report, list the checks that were not done, and
point the user to `out/sheet-*.png`.

Do not take screenshots by other means, and do not open the PDF as images page by page — the
contact sheets exist so that the whole deck costs one or two images.

## 2. What to look for on the contact sheet

Look at the sheet as a stranger would look at the deck pinned to a wall.

**The first question: is it a deck of pictures or a deck of text?**

- On the sheet, each slide should read as *heading, one line, a picture, a few lines*. Count the
  slides where text covers more area than the figure. Apart from 目的 and まとめ there should be
  none.
- Is there a slide that is a grid of text — a table of phrases, rows of labels with
  explanations, boxes with titles and descriptions, or a chart whose axes are lists of names with
  dots at the crossings? That slide is rebuilt around a figure that shows what actually differs.
- Is there a position map? Then ask whether the slide needs it at all — is the position itself the
  point, a trade-off the others each give up and this work holds (figures.md §7)? — and if it
  stays, whether the evidence for each place is under its name, and whether the bullets say what
  each other approach falls short on.
- On the prior-work slide, do the bullets say what is wrong with the prior work, or only what it
  achieved?
- Does any slide carry small grey lines under several elements? Remove them.

**Rhythm and consistency**

- Do all slides look like one deck? The heading and its rule sit at the same height on every
  slide.
- Is there one slide that looks unlike the rest — much denser, much emptier?
- Are more than three consecutive slides visually identical? Then some content has probably not
  been given its right form.

**Balance of each slide** (the thumbnail is enough to judge this)

- Does the figure dominate — about half the body or more?
- Is there a large empty band in the middle or at the bottom?
- Do the images look like what the message says (a clear contrast, the right examples)?

**Centre of gravity and the path of the eye** (squint; the thumbnail is enough)

- Does the weight of each slide rest near its centre line, or is one half empty? (`cx` in
  `lint --metrics` says the same in numbers.)
- **Do the bullets reach across the slide?** They are flush left; a list of stubs leaves the
  right side blank under a centred figure or above a centred frame. Each bullet should
  be a full line. A list must never be centred to hide this.
- Are the bullets of a list of similar length, or one long line among stubs?
- **Does every diagram show something and fill its place?** A flow of one-word boxes, or a thin
  strip of a figure with empty margins above and below, is neither.
- Follow the order in which the eye will go. Does it go down once? Is there a place where it must
  turn back, read a label sideways, or cross its own path to pair two things?
- Does any part stick out of what it belongs to — a caption wider than its picture, a
  consequence longer than its premise?

**Colour, and where to look**

- Squint. On each chart, one thing should be coloured. If several are, or none is, the slide has
  no subject.
- **Cover the bullets and ask of each chart: where is the point?** Someone who sees only the slide
  should be able to put a finger on it within two seconds — the red bar, the labelled gap, the
  ring, the bold words of the message that the chart proves. If they would have to study the
  chart, mark the point (SKILL.md rule 3).
- Is the same thing the same colour from slide to slide?
- Red should be rare: the bars a slide is about, one phrase.

**Headings and messages**

- Read the headings and messages in order from the sheet. Do they give the outline of the talk?
  Is every message a short phrase, clearly shorter than the heading rule?
- Read the topics of each part together (lint S10 lists them). Are they at one level — the kind
  of analysis or measure — or is one of them the name of an item on its slide?
- Read each message alone. Does it say what it is about and what happens to it, and does every
  comparison name both sides?

**Is it a template?**

- Lay the sheet beside the gallery's sheet. If the figures are the gallery's figures with new
  labels — a position map where the gallery has one, the same four-box flow — choose each figure
  again from the material (SKILL.md rule 21).

## 3. What to look for on a single slide

Open the full-size image for slides with plots or diagrams, and for anything suspicious.

- **Label collisions in plots**: two annotations touching or overlapping; a label crossing a
  line or a point; a label cut off at the edge of the axes.
- **Legibility in plots**: tick labels readable, axis labels present with units, the subject
  series obviously the subject.
- **Axes** (SKILL.md rule 22): every axis named by its quantity, with its unit in parentheses and
  nothing else in them; no 「低」「高」 ticks on an axis without values; one quantity per axis; the
  axis line ends with the scale, not under the labels past the data; the axis does not run far
  past the largest value. Every axis that places marks is an amount: could a dot move to another
  row without changing the meaning? Then the chart is a table of words (F7).
- **Shares**: cover the speaker and read each percentage — is it clear what 100% is and what the
  part is, in words the audience knows? Are two shares of different wholes stacked as if they
  were one comparison?
- **Error bars**: no value sits on a whisker (`sk.bar_values`).
- **Figures taken from a paper**: is each one read for the audience — the place ringed, a line or
  two that say what to see — or does it stand under the message alone (F9)? Is its type readable
  at the scale it is drawn (`img ×` in `--metrics` × the height of its smallest text in the image
  ≥ 19 px)? When not, crop tighter.
- **Shapes in diagrams**: people drawn as people, things with a shape as that shape — not
  labelled circles.
- **Diagrams and flows**: text inside its box with margin; equal gaps between equal things;
  nothing a few pixels off. In a flow, every box is a thing and every arrow an operation.
- **Real images**: sharp, not cropped through something that matters, the value under each
  readable; the pair shows the contrast the message claims.
- **Line breaks**: a bullet that breaks in an awkward place or into very uneven lines; a single
  character alone on a last line; a citation mark alone at the start of a line.
- **Tables** (appendix): numbers aligned on the right; the marked rows are the ones the talk is
  about.
- **The cover**: the title broken at a natural phrase boundary; the lines under the rule complete
  and free of placeholders that should have been filled.
- **Leftovers**: template text, markup characters showing, empty captions.

## 4. Fixing what you see

| What you see | What to change in deck.py |
|---|---|
| The slide is mostly text | find the figure (figures.md §1); cut the bullets to three full lines; move the rest to `notes=` |
| The figure looks small or lost | fewer bullets under it; regenerate a plot larger (`new_fig`); real content in the boxes of a flow |
| The slide looks empty | a larger figure; or merge the slide into its neighbour — never pad with filler |
| The right side is blank beside short bullets | rewrite each bullet as a full line (the fact with its number, condition, source); or one `conclusion` line; or the list in a column. Do not centre the list |
| A flow of one-word boxes | put one real case in the boxes (`img=`, `values=`, `value=`), or replace the flow |
| Images are small strips | too many bullets under `samples`; cut them |
| A grid of text, labelled rows, a band at the bottom | rebuild: a figure (bars, samples, the material's own figure) plus two bullets or one `conclusion` |
| A chart whose point you have to search for | bold the key words of the message; `hot=` the bars it is about; label the decisive value; one `sk.ring` |
| The topics of one part at different levels | rename them by the kind of analysis or measure (精度 / 速度 / 頑健性) |
| The deck looks like the gallery | choose each figure from what the material shows; drop the pattern that was taken because it was there |
| Parentheses on every line; lines ending in 〜ず | the qualifier in front of the noun as one block; 〜ない or a noun ending |
| A schematic with 低 / 高 ticks, or three outcomes on one axis | name the quantity, `set_yticks([])`; one panel per outcome |
| People as labelled circles | `sk.person` |
| A hand, a phone, a device drawn from rectangles or balloons; a thing facing the wrong way | an icon from the bundled sets (`scripts/icons.mjs`), composed if needed; `flip=True` |
| A second figure that only fills space; the same panel repeated | remove it / draw the shape once and name what it stands for |
| A caption about what was left out | remove it |
| Bullets broken early into two short lines | one line if it fits; otherwise break near the end (T10) |
| A long bullet or the purpose without a single 「、」; a verb cut to its stem | a 「、」 after a long opening phrase; 「〜て」 |
| Red on a thing that is not red (sweat, a device) | the thing's own colour; red only to point |
| An axis named 「各指標」「予測値」 or a bare noun; a schematic axis without an arrowhead | the quantity in plain words, 「〜の高さ」; `sk.schematic_axes` |
| 「→仮説1を支持」 alone | the fact read off the chart → the hypothesis in words：**仮説1**の支持 |
| Only one or two appendix slides | add the originals of redrawn figures, full tables, omitted analyses, answers to likely questions |
| Small grey lines everywhere | keep one caption at most; say the rest |
| Plot labels collide | adjust `xytext` of one annotation; label fewer points; widen `xlim` to make room |
| A slide looks unlike the others | use the same pattern as its sibling slides |
| Nothing is coloured / everything is coloured | decide the subject; `hot=` or `highlight=` only that |
| The flow is wider than the slide | fewer things; operation names of 2–4 characters; narrower `img` width |
| Awkward line break in a bullet | place `\n` at the phrase boundary so the lines are similar in length, or reword |
| A figure sits to one side; two columns of very different weight | let the components centre it (no hand-placed HTML); in `cols`, give the lighter side more or change the ratio |
| The eye has to cross to pair two things | reorder: examples in the order of the lines / bars they belong to; names at the marks |
| A rotated axis name | `sk.ylabel_top(ax, …)` |
| The bullets under a flow only name its boxes again | replace them with what the flow cannot show (the idea behind a step, the data, the measure) |
| A consequence (→) longer than its first line; a caption wider than its picture | shorten the part |

Then run lint and build again. Do not "fix" by silencing lint rules.

## 5. Verifying numbers

A wrong number on a slide is the most damaging error a deck can contain: one is enough for the
audience to stop trusting the rest. Verify mechanically.

`numbers.md` (the ledger started in Phase 3), in the user's language:

```markdown
# 数値台帳

| p. | スライド上の表記 | 意味 | 出典（ファイル・場所） | 出典の値 | 照合 |
|---|---|---|---|---|---|
| 5 | 120区間 | 評価に使った区間の数 | paper.tex 3節 | 120 | 一致 |
| 8 | 91% | 幅1mm未満の発見率 | paper.tex 4節 / results/width.csv 2行目 | 0.9127 | 一致（丸め） |
| 8 | 63% | 同じ区間での目視点検の発見率 | paper.tex 4節 | 63.0% | 一致 |
```

Procedure:

1. Run lint. It writes `out/numbers-on-slides.md`: every number that is actually printed on a
   slide, with the text around it.
2. For each entry there, find its row in the ledger. A number on a slide with no ledger row is
   unverified: trace it to the source and add the row, or remove it from the slide.
3. For each ledger row, open the source and compare. Check the value, the rounding, the unit,
   and that the label on the slide says what the source says (the same metric, the same
   condition, the same dataset).
4. Check derived numbers by recomputing them: sums, differences, percentages, "約半分",
   "27ポイント". Record the computation in the ledger.
5. Check pairs that are easy to confuse — the same metric under different conditions — and make
   sure each is labelled with its condition on the slide.
6. Numbers produced by code in `deck.py` (read from a CSV, formatted) are checked the same way:
   look at what was printed, not at what the code intended.

Where sources disagree, follow the source the user named as authoritative; if none was named,
report the disagreement instead of choosing.

If the user said that exact verification is out of scope for this run, still produce the ledger
and mark the rows as 未照合, so the work that remains is visible.

When one source disagrees with itself — a total in a figure that does not match the text because
the two count from different points, a value rounded differently in a table and in the abstract —
do not pick one silently and do not print a number that mixes the two. Use one of them
consistently (the one the slide's comparison is built on), leave out the aggregate that would
contradict the other, say in the notes which one you used and why, and list it under 未了・要確認
in the report.

## 6. Verifying words, citations and structure

- **Terms**: list the technical terms on the slides. One name per thing; fix any slide that uses
  a different word for it. Follow a terminology list if the material provides one.
- **Abbreviations**: every abbreviation is used at least twice and introduced at first use, or is
  spelled out (lint D4 lists the single-use ones).
- **Claims**: each message is supported by the material, at the strength the material supports.
  Where the material hedges, the slide hedges. Nothing the material withdrew or the user excluded
  appears, including in the appendix.
- **Names**: the name given to each prior approach distinguishes it from this work; no category
  name also describes this work.
- **Citations**: every method, model, dataset or measure from someone else's work carries a citation
  mark where it first appears (lint C1), and for every entry on the reference slide you can point
  at the place in the material it was copied from. One you cannot is a `missing_ref`, not a
  recollection.
- **Terms**: each term the talk is built on is glossed, in a few words inside the line, on the
  slide where it first appears.
- **Examples**: the real examples shown were chosen from the data by a stated rule (highest /
  lowest, the extremes of a quantity), and the values printed under them match the data.
- **Comparisons**: no ranking between results measured under different conditions; where they
  appear together, a note says the conditions differ.
- **Citations**: every `[n]` on a slide has entry n on the reference slide; every entry is cited
  at least once; numbering follows order of first appearance (or the source's own numbering, if
  the user wants them to match).
- **Personal information**: names, student numbers and similar identifiers appear only where the
  user wants them. When unsure, placeholders — and say so.
- **Structure**: main slides → 参考文献 → blank → appendix. The last main slide is the summary.
  No divider, agenda or thank-you slide.
- **Timing**: `sec=` on the cover and every main slide, adding up to the talk length.

## 7. Speaker notes

The slides leave most of the talk unsaid on purpose, so the notes are part of the deliverable.
Each main slide's `notes=` holds, in the presenter's spoken language:

1. the opening line (the message as a spoken sentence);
2. where to look on the figure, and how the examples were chosen;
3. what each number means and how good it is, with its comparison;
4. everything that was kept off the slide: definitions, conditions, reasons, details;
5. numbers or terms that are easy to confuse, stated explicitly;
6. the line leading to the next slide.

About 300 characters per minute of `sec=`. The notes are collected in `out/notes.md`. Check that
nothing the audience needs was dropped altogether: every cut from a slide should be findable in
its notes.

## 8. The report

Report in the user's language. Lead with where the result is; keep it factual. Template
(Japanese):

```markdown
（資料で出典を確認できなかった文献があるときは、ほかのすべてより先にこの節を書く）
## 要確認: 資料で出典を確認できなかった文献
- RoadSeg++（p.4・p.6 で使用）: 資料のどこにも文献情報がない。原論文の情報をください

発表スライドを作成しました。

- PDF: <deck-dir>/out/<deck-name>.pdf（本編 N 枚＋参考文献・空白・補足 M 枚）
- 正本: <deck-dir>/deck.py（修正はこのファイルに対して行います）
- 発表者メモ: <deck-dir>/out/notes.md

## 前提として置いたもの
- 聞き手: …
- 比率: 16:9（指定がなかったため）
- …

## 構成と時間配分（合計 600 秒）
| No | 見出し | 一言 | 図 | 秒 |
|---|---|---|---|---|
| 1 | 表紙 | — | — | 15 |
| 2 | 研究背景 | … | 幅の広いひび割れと細いひび割れ（データセットの画像） | 55 |

## 図の出どころ
- 資料の画像を使ったもの: p.2, p.6, …（選び方: …）
- データから生成したもの: p.9, p.10, …
- 位置づけ図: なし / p.3（必要な理由: …。figures.md §7 の条件のどれを満たすか）

## 数値の照合
| p. | 表記 | 出典 | 照合 |
|---|---|---|---|
| 8 | 91% | paper.tex 4節 | 一致 |

（未照合の数値: なし / あり → 一覧）

## 検査結果
- lint: エラー 0、警告 0（情報 2 件: …）
- 抑制したルール: なし / p.7 の F2（理由: …）
- 目視確認: 一覧画像 2 枚と p.6・p.7 を確認 / 未実施（理由）

## 読んだファイル
- …

## 未了・要確認
- …
```

Rules for the report:

- State what was not done or not verified as plainly as what was. "未照合" is a finding, not an
  embarrassment.
- Do not describe the deck as beautiful, polished or professional. Say what it contains and what
  was checked.
- If the user's rules restrict what may be printed (names, identifiers), follow them in the
  report as well as on the slides.
- Mention any deviation from the skill's rules that the user asked for.
