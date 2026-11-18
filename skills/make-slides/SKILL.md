---
name: make-slides
description: Create formal, presentation-ready slide decks from source material and a talk length — the kind used for 学会発表, 中間発表, ゼミ・輪講, 進捗報告, and business briefings in Japanese (English decks work too). The deck is written as a short Python script against a bundled slide library; the library generates HTML under a fixed, restrained design system, a browser-based linter measures the rendered result, and a build script produces a vector PDF — so the deck looks hand-designed instead of AI-generated, the same way every time. Use this skill whenever the user asks to make, draft, rebuild or polish slides / a deck / a presentation / スライド / 発表資料 / プレゼン資料, hands over material together with a talk length (「10分の発表用に」「これをスライドにして」「発表資料にまとめて」), or asks to fix the look of slides — even when no file format is named. Do not use it when the user explicitly requires an editable .pptx, Keynote, Google Slides or LaTeX Beamer file.
---

# make-slides

Turn source material plus a talk length into a deck that can be shown at a formal talk without
apology.

## What this skill is for

Machine-made slides look machine-made. Avoiding gradients, emoji and rounded cards is not enough:
the first version of this skill did exactly that, and its output was still judged unusable. The
reason is worth understanding before anything else, because it is the mistake a language model
makes by default:

> **The slide tried to explain everything.**

A model that is good with words fills a slide with well-organised words: a sentence as the title,
a comparison table of phrases, rows of "label: explanation", a grey sub-label under every item, a
summary band at the bottom. Each piece is tidy. The whole is a document cut into pages, and an
audience cannot read a document while someone is talking. It is also instantly recognisable as
generated.

A slide made by a careful person looks different:

```
┌──────────────────────────────────────────────┐
│ 結果 - 精度                                    │  heading: the part of the talk, large
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │  thick rule
│ 幅1mm未満のひび割れも9割を検出                   │  message: one short claim, its key words bold
│                                              │
│   幅3mm以上  ████████████████████████  98%     │
│   幅1〜3mm   ███████████████████████  95%      │  the figure: half the slide or more,
│   幅1mm未満  ██████████████████████  91%  (red) │  the bars it is about in red
│                                              │
│ • 同じ区間の目視点検では幅1mm未満の発見率は63%     │  a few lines: at most three bullets,
│ • 誤検出は1kmあたり2.4件で確認は約5分の作業       │  flush left, each reaching well
│ 2026/9/16                                 10 │  across the slide — or one bold line
└──────────────────────────────────────────────┘
```

**Heading → message → figure → a few lines.** Everything else — the reasoning, the conditions,
the definitions, the "why" — is spoken, and is written in `notes=`, not on the slide.

Later versions of this skill had the amount of text about right and were still marked down for
how the slide was *composed*:

- **Stubs.** Told to cut words, the model cut bullets down to keywords. Bullets are flush left, so
  a list of stubs left the right half of the slide empty while the figure, the arrow and the frame
  were centred, and the slide tipped to one side. Centring the list as a block to compensate made
  it worse. The answer is in the writing, not the layout: **a bullet is one full line that carries
  a fact and reaches well across the slide.** Few bullets, not thin ones.
- **An empty diagram.** A flowchart whose boxes held only a word each. A diagram earns its place by
  what it shows — the actual image, the actual numbers, the actual result — not by having boxes
  and arrows.

What was missing has names — 視線誘導 (where the eye is led), 重心 (where the weight sits),
階層構造 (parts inside wholes). They are properties of the whole slide, and the skill measures them
(rules 7–9 below).

Decks made later by other models from other papers, with this skill alone, were marked down for
more things — the first of them probably the most important for any chart:

- **A figure that does not say what it shows.** Every chart was correct and none marked its point;
  the audience had to study it to find what the speaker meant (rule 3).
- **Topics at different levels.** 「結果 - 」 followed by two measures on one slide, one on the
  next and a sub-analysis on the third: the outline of the talk disappeared (rule 2).
- **The gallery's figures with new labels.** A position map on the prior-work slide because the
  examples had one: a template, and it shows (rule 21).
- **A message without a subject or a predicate** (「…は逆に低下」 — what, compared with what?)
  and lines full of parentheses in English word order (rules 2 and 5).
- **A chart whose axes were lists of names** — groups of people across, kinds of effect up, a dot
  at a crossing. Swap two rows and nothing changes: no place on it means anything, and the grid
  only pretends to measure (rule 22).
- **A share whose whole was never named** — a percentage of a group the audience could not
  identify (a range of grades nobody had explained), stacked above a share of a different whole
  (rule 10).

This skill exists to produce that kind of slide, the same way every time, whichever model runs it.

## How the skill keeps the look consistent

1. **You write content, not markup.** A deck is a Python script, `deck.py`, that calls the bundled
   library `slidekit`: `deck.slide("研究背景", "細いひび割れほど見落とし", sk.samples(…), sk.points([…]))`.
   The library writes the HTML. There is no argument anywhere for a font size, a colour or a
   margin, so those cannot drift.
2. **The library refuses the usual mistakes.** A message with 「、」 in it, a table of words, a
   nested bullet, a bare paragraph on a slide, a heading that is a sentence: each raises an error
   that says what to do instead. The components that produce machine-looking slides (comparison
   matrices, labelled rows, stat cards, takeaway bands) do not exist.
3. **A fixed theme** (`assets/theme/slide.css`): type scale, colours, the heading and its rule,
   the footer. When something does not fit, the content changes, not the style.
4. **A catalog of slide patterns** (`references/layouts.md`; running code in
   `assets/gallery/deck.py`, rendered in `assets/gallery/out/gallery.pdf`). You choose a pattern by
   what the slide shows and copy the *call*. The examples come from several invented talks; their
   topics, numbers and choice of figure are not a template for yours (rule 21).
5. **A linter that measures the rendered page** (`scripts/lint.mjs`). It opens the deck in a real
   browser and checks what a careful reviewer checks: a slide with no figure, a figure that is too
   small, a chart that does not say where to look, a plot whose axes are lists of names, a
   message that is a sentence or points at
   nothing, too many bullets, grey sub-labels, parentheses on every line, a list of stubs that
   leaves one side of the slide empty, a figure off the centre line, a flow whose boxes hold only
   words, a part that sticks out of what it belongs to, overflow, text size, uneven line breaks,
   decoration, slide count against talk length.

The deliverable is a **vector PDF rendered by headless Chrome** from that HTML. HTML/CSS is the
format in which layout can be stated exactly and verified by measurement; the PDF embeds its fonts
and opens anywhere. The canvas has PowerPoint's physical size (16:9 = 13.333 × 7.5 in,
4:3 = 10 × 7.5 in), so sizes in this skill are PowerPoint points.

## Files

`<skill-dir>` means the directory that contains this SKILL.md.

```
<skill-dir>/
├── SKILL.md
├── references/
│   ├── story.md        designing the talk: audience, parts, the message of each slide, what goes to notes
│   ├── figures.md      where figures come from; choosing the form; charts, real images, flows, plots
│   ├── design.md       the visual rules and their reasons; what machine-made slides look like
│   ├── layouts.md      the slidekit API: the slide patterns and every component
│   ├── lint-rules.md   every lint rule: what it means, how to fix it
│   └── qa.md           visual check, number verification, the final report
├── scripts/
│   ├── doctor.mjs      checks the environment
│   ├── init.mjs        creates a deck directory
│   ├── lint.mjs        runs deck.py, then measures the rendered deck
│   ├── build.mjs       runs deck.py, then writes the PDF, PNGs, contact sheets, speaker notes
│   └── icons.mjs       finds and fetches icons (people, hands, a phone, a camera …) from open-source sets
└── assets/
    ├── slidekit.py     the slide library (copied into each deck; never edited)
    ├── theme/          slide.css, ratio files, fonts, KaTeX (copied into each deck; never edited)
    ├── template/       starter deck.py
    └── gallery/        deck.py using every pattern (on invented topics), and its rendered PDF
```

A deck is a self-contained directory:

```
<deck-dir>/
├── deck.py             THE DECK — the only file you write (charts are made inside it too)
├── outline.md          the plan from Phase 2
├── numbers.md          the number ledger from Phase 3
├── prepare.py          optional: a script that cuts images / computes data from the material into figures/
├── slidekit.py         copy of the library
├── theme/              copy of the theme
├── figures/            images taken from the material, generated plots, data for the charts
├── deck.html           generated from deck.py — never edit by hand
└── out/                <deck-name>.pdf, png/, sheet-N.png, notes.md, lint.json, numbers-on-slides.md
```

## Workflow

Work through the phases in order. Each phase names the reference file to read **at that point**;
read it then, in full. The references are where the detail lives, and skipping them is the usual
cause of a deck that passes lint and still looks wrong.

### Phase 0 — Environment (once per machine)

```
node "<skill-dir>/scripts/doctor.mjs"
```

It reports what is missing with the exact command to fix it (normally only
`npm install --prefix "<skill-dir>/scripts"` the first time — it installs the browser driver and
the open-source icon sets). It needs Node.js, Python 3.9+, and
an installed Chrome or Edge; nothing is downloaded. matplotlib is needed for plotted figures,
Pillow for cutting images out of the material.

### Phase 1 — Understand the request and read the material

Establish these before designing anything:

| Input | If the user did not say |
|---|---|
| Source material | Required. Read all of it. Keep a list of every file you read. |
| Talk length in minutes | Required. Ask. Everything else is derived from it. |
| Audience | Assume educated people from the same broad field who do not know this specific topic (for a university talk: students of the same department). Say so in the report. |
| Occasion and formality | Assume a formal talk with a question session. |
| Aspect ratio | 16:9. Use 4:3 only when asked or when the venue is known to be 4:3. |
| Language | The language of the material and the request. |
| Structure after the main part | 参考文献 → one blank slide → 補足 (appendix), when the material has citations or the talk has a question session. |
| Disclosure (利益相反・COI) | Only when the event requires one (many 学会 do): right after the cover, with `deck.disclosure([...])` in the event's own wording. If the requirement is unknown, leave it out and say so in the report. |
| Presenter name, affiliation | Take them from the material. If it is unclear whether personal identifiers may appear, use placeholders (氏名 etc.) and say so. |
| Date, name of the event | Take them from the request or the material. If they are not given, leave them out — no placeholder date in the footer — and say so in the report. |

Ask only for what cannot be defaulted, once, with AskUserQuestion. The promise of this skill is
"material and a talk length are enough"; a questionnaire breaks it.

The user's standing instructions (CLAUDE.md, memory) outrank this skill. The ones that usually
matter here: permission before reading directories outside the working directory; permission
before viewing rendered images (Phase 6 needs it — ask at the start, together with anything
else); showing a plan before a large task.

**While reading, collect pictures.** List every image, photo, screenshot, plot, dataset sample,
data file and equation in the material: these become the figures. A deck is made of what can be
*shown*; the material almost always contains far more of it than a first reading for "content"
notices (a dataset of images, result CSVs, a figure in the paper, the code that computes a
quantity). For each figure of a paper, note whether its data is in the material too (a table, a
CSV, the numbers in the text) or only the picture — that decides how it can be used (figures.md
§1). Do not open old slides of the same talk unless the user offers them.

Nobody can be asked mid-task in some runs (a batch job, a delegated agent). Then decide every
open point by the defaults and the rules of this skill, and list the decisions in the report.

### Phase 2 — Design the talk

**Read `references/story.md` now.**

Write `<deck-dir>/outline.md`:

1. the audience in one line, and what they already know;
2. the one sentence the audience should remember tomorrow;
3. the slide budget from the talk length (table in story.md — about one main slide per minute
   including the cover);
4. one row per slide: number, **heading** (the part of the talk: 研究背景 / 方法 - 実験 / 結果 - 精度),
   **message** (one short noun-ending claim), **the figure** (what picture — which image from the
   material, which chart of which data, which diagram — and *what in it the audience should look
   at*), the words on the slide (at most three bullets, each a full line, or one conclusion line),
   seconds, and what will be *said* (this becomes `notes=`);
5. the topics of each part side by side (結果: 精度 / 速度 / 頑健性), read as a set: they name the
   same kind of thing, at one level (story.md §4).

Decide the figure of each slide **before** its words, from what *this* material can show — not
from the gallery. A slide whose row has no figure is not yet designed; only the purpose slide and
the summary are text-only. If a part of the talk cannot be shown in one picture, give it more
slides — the method of a study never fits on one.

Show the outline to the user. Whether to wait for approval follows their standing instructions and
how they phrased the request; if they said to go ahead, go ahead.

### Phase 3 — Prepare the figures

**Read `references/figures.md` now.**

```
node "<skill-dir>/scripts/init.mjs" <deck-dir> --ratio 16:9 --minutes 10 --title "発表タイトル"
```

(`--ratio 4:3` for 4:3.) This creates `deck.py` from the template and copies the library and the
theme. Then, for each row of the outline:

- **Real images from the material** (screenshots, photos, samples from a dataset, a page of a
  document): copy or cut them into `figures/`. Choose examples that make the point visible at a
  glance — the extremes, a clear contrast — and record the value that goes with each. When this
  takes computation (reading a CSV to find the highest and lowest example, resizing images), put it
  in `<deck-dir>/prepare.py` so it can be re-run.
- **A figure of a paper**: when its data is in the material, redraw it at slide size with its point
  marked; when only the picture exists, show the picture (cropped to the panels the slide needs)
  rather than reading values off it.
- **Data** becomes a chart in `deck.py`: `sk.bars()` / `sk.vbars()` for values to compare,
  `sk.shares()` for the shares of a whole (bars that run to 100%, every part named), matplotlib
  through `sk.new_fig()` / `sk.save_fig()` for trends, scatters and distributions (`sk.bar_values()`
  writes the values over bars with error bars). Every chart marks its point (rule 3).
- **Structure** becomes `sk.flow()` (a pipeline: boxes are things, arrows are operations), a
  drawing of the setting in `sk.svg()` with people as people (`sk.person()`); anything else is a
  small `sk.svg()`. A position map (`sk.posmap()`) is drawn only when the position itself is the
  point of the slide — rarely, and never as the default picture of prior work (figures.md §7).
- **Things with a shape** — a hand, a phone, a camera, a screen, a person seen from the side —
  come from the bundled icon sets, never from a makeshift drawing:
  `node "<skill-dir>/scripts/icons.mjs" search <word> [<word> …]` (English words as separate
  arguments; names with any of them are listed, those with all of them first — give synonyms
  together), `show <deck-dir> <set:name> …` (one PNG of the candidates to choose from),
  `get <deck-dir> <set:name>`, then `sk.icon(…)` inside `sk.svg()`. A person with a prop is one icon
  when a set has it; otherwise the person and the prop composed, the prop drawn in the icon's own
  coordinates with `sk.icon(…, overlay=…)`; a line that must end on a spot of an icon gets its end
  from `sk.icon_point(…)`. Draw by hand only what no set has, and only if it comes out
  recognisable — otherwise choose another figure (figures.md §9).
- **A definition** becomes `sk.math()` together with one worked example on real data.
- Start `<deck-dir>/numbers.md`: one row for every number that will appear on a slide — the value
  as printed, what it means, the source file and place, the slide. Never put a number on a slide
  that is not in this ledger. You verify it in Phase 7.

### Phase 4 — Compose the slides

**Read `references/design.md` and `references/layouts.md` now.** Keep
`assets/gallery/deck.py` open beside them: it is the same catalog as running code.

Write `deck.py`: one `deck.slide(...)` per row of the outline.

```python
import slidekit as sk

deck = sk.Deck(title="発表タイトル", minutes=10, ratio="16:9", date="2026/9/16")

deck.cover(event="○○発表会", lines=["所属", "氏名", "2026年9月16日"], sec=15)

deck.slide(
    "研究背景",                                   # heading: the part of the talk
    "細いひび割れほど見落とし",                      # message: one short claim, or None
    sk.samples(                                   # the figure
        sk.sample("figures/crack_wide.png", "97%"),
        sk.sample("figures/crack_fine.png", "63%", tone="hot"),   # red: the case the slide is about
        caption="目視点検での発見率（幅3mm以上と幅1mm未満）[2]",
    ),
    sk.points([                                   # a few lines, flush left, each reaching across the slide
        "市道の舗装点検は1kmあたり約3時間の目視作業[1]",
        "幅1mm未満のひび割れは熟練者でも3割以上を見落とし[2]",
        "細いうちに補修すれば費用は約5分の1[3]\n→早期の発見が課題",
    ]),
    sec=55,
    notes="""話す内容。スライドに書かなかったことはすべてここに書く。""",
)

deck.save()
```

Inline markup in any text: `**語**` bold, `[[語]]` accent colour, `!!語!!` red, `[1]` citation
mark, `$x_j$` math, `\n` a line break that you place. Everything else is escaped.

Hold to the rules in the next section while composing. They are short; their reasons are in
design.md.

### Phase 5 — Lint until clean

```
node "<skill-dir>/scripts/lint.mjs" <deck-dir> --metrics
```

This runs `deck.py` first, so there is no separate generate step. A Python error in `deck.py` is
shown and stops the run: fix it and run again. slidekit raises errors with instructions when a
component is misused — read the message; it says what to write instead.

**Read `references/lint-rules.md` the first time a rule appears that you do not know how to fix.**

- Fix every `ERROR`, then every `WARN`. `info` lines are judgement calls; read them.
- Fix the cause in the content. The fix for "too much" is always to cut and move the cut to
  `notes=` — never a smaller size, never hand-written HTML or CSS, never editing `slidekit.py`,
  `theme/` or `deck.html`.
- `--metrics` prints, per slide, the share of the body taken by the figure (`fig`, aim for 40% or
  more), how much of the body height carries content (`fill`), how far the weight of the slide
  sits from the centre line (`cx`, aim for within ±5%), the amount of running text (aim for
  under ~140 characters at 4:3, ~180 at 16:9) and the length of the message.
- A rule may be silenced on one slide with `lint_off="F2"` only when you can state, in a comment
  beside it, why the slide is right as it is. Use this rarely; report each use.

### Phase 6 — Build and look

```
node "<skill-dir>/scripts/build.mjs" <deck-dir>
```

**Read `references/qa.md` now** and follow its visual check.

The build writes `out/<deck-name>.pdf`, one PNG per slide, and contact sheets
(`out/sheet-1.png`, …: all slides side by side). The linter cannot judge whether a figure makes
its point, whether a plot is legible, or whether a slide reads at a glance — you have to look.

Look at the contact sheets first: one or two images show the whole deck. Open an individual
`out/png/NN.png` only for a slide that looks wrong on the sheet or that contains a plot or a
diagram. If the user's rules require permission before viewing images, you asked in Phase 1; if
they declined, say in the report that the visual check was not done and ask them to look at the
sheets.

Fix what you see, then lint and build again. Two or three rounds is normal.

### Phase 7 — Verify content

Follow the second half of `references/qa.md`:

- check every row of `numbers.md` against its source, and every entry of
  `out/numbers-on-slides.md` (written by lint: every number that is actually on a slide) against
  the ledger;
- check terms: one name for one thing through the whole deck; every abbreviation either used at
  least twice and introduced, or spelled out;
- check that each citation mark has an entry on the reference slide, and the reverse;
- check `notes=` on each main slide: it holds everything the slide leaves out — what each number
  means and how good it is, the conditions, the reasons. The slide shows; the speaker explains.

### Phase 8 — Report

Report to the user in their language with the template in `references/qa.md`: where the PDF is,
the slide list with time per slide, the assumptions you made in Phase 1, the number check table,
the files you read, lint status including any silenced rule, and what you could not verify. State
plainly anything that is unfinished. If you wrote a helper that another deck could use — a
function in `deck.py` or `prepare.py` that is not about this material — name it in the report:
it may belong in slidekit or in `scripts/`.

## The rules

These are the rules the library and the linter cannot fully enforce. Each has a reason; when a
case comes up that the rule did not foresee, follow the reason. Rules 1–12 and 21–22 are the ones
a language model breaks by default — read them twice.

**1. The slide does not explain. The speaker does.**
Put on the slide what the audience should *see* while you talk: the picture, the few words that
name what it shows, the number that matters. Put what you would *say* — reasons, conditions,
definitions, caveats, how the method works in detail — in `notes=`. A reader who was not in the
room should still get the point of each slide from its message and figure; they do not need the
argument. When a slide feels incomplete without another sentence, that sentence belongs in the
notes. Nor does the slide mention what it leaves out (「エラーバーは省略」「詳細は割愛」): nobody
reading it misses what is not there.

**2. The heading names the part of the talk; the message is one short claim.**
The heading is large and is only a label: 「研究背景」「先行研究」「目的」「提案手法 - 全体像」
「結果 - 精度」「まとめ」. When a part has several slides, the topics after the hyphen are siblings
and sit at **one level**: they name the same kind of thing — the kind of analysis or measure —
never the items of content on each slide:

```
× 結果 - 検出率と誤検出        ○ 結果 - 精度
  結果 - 処理時間                結果 - 速度
  結果 - 夜間と雨天の画像          結果 - 頑健性
```

On the left, one slide is named after two measures, the next after one, the third after two
subsets of the data: three levels, and the last is far too specific. Read the topics of each part
together before writing any slide (the linter lists them, S10). Keep them bare: 「実験」, not
「被験者実験」.

Under the heading goes the message — what this slide says — as a noun-ending phrase of about 18
characters or fewer, with no 「、」 and no 「。」 (the message only; other text keeps its 「、」,
rule 5):

| × a sentence (reads as generated) | ○ a phrase |
|---|---|
| 見た目の第一印象がサイト全体の評価を左右する | 第一印象がサイト全体の評価を左右 |
| 既存の手法は予測性能と説明性を両立できていない | 予測性能と説明性の両立 |
| デザイン原則を指標に翻訳し、評価への寄与を測る | 指標決定と寄与測定 |
| 安価な画像だけで、車載レーザー計測と同程度の発見率が得られた | 車載レーザー計測と同程度の発見率 |

(The first three rows are corrections made in review.)

Drop the subject when the heading supplies it, drop the verb ending (〜する → the noun), replace a
clause joined by 「、」 with two nouns joined by 「と」. Leave the message out (`None`) when the
heading already says everything (目的, まとめ).

Short is not the same as incomplete. The message is a **claim**: it names what it is about and
what happens to it, and a comparison names both sides. 「雨天では逆に低下」 says neither what
drops nor compared with what; 「雨天では検出率が晴天より低下」 does. Words that point outside the
message — 逆に、同様に、前者、後者 — have nothing to point at (lint M4). When a chart below proves the
message, its key words may be bold, once: 「**幅1mm未満**のひび割れも9割を検出」 (rule 3).

**3. Every slide has a figure, the figure is the main thing — and it says where to look.**
Words alone do not reach an audience. The figure takes half the body or more; the words fit in
what is left. Figures come from two places: **the material itself** (screenshots, photos, samples
of the dataset, plots from the paper — use them, generously; real examples are the most convincing
thing a slide can show) and **code** (charts of the data, diagrams with little text). Aim for
slides that would not work without their figure. Text-only slides are the purpose and the summary,
declared with `text_only=True`.

A correct chart whose point the audience has to hunt for has not made the point. Before drawing
it, write down the one thing it must show; then mark that thing, so it is seen at a glance:

- the key words of the message in bold (`**…**`) — the message states the finding, the chart
  proves it;
- the bars, the line or the points the slide is about in red (`hot=`), or this work in dark blue
  among grey (`highlight=`);
- a direct label at the decisive place (「差 12ポイント」 beside the gap, the value at the end of
  the line);
- when none of these leads the eye there, one ring around it (`sk.ring` in a plot, an
  `<ellipse class="ln-hot">` in a diagram). It is drawn into the figure; nothing appears later.

Use one or two of these, not all. The linter warns about a chart that has none (F5).

And a figure is there because the point needs it — *that* figure, not any figure. A second figure
added to fill a column or an empty corner (a rating scale drawn out, a picture of a word) is
filler, and looks it. When a slide has room, enlarge the figure that matters, or let the words
have the width.

**4. No table of words. No "label: explanation" rows. No cards.**
A grid of phrases — options across the top, aspects down the side, a phrase in every cell — is
the single most recognisable mark of a machine-made slide, and it is forbidden outright;
`sk.table()` accepts numbers only. The same goes for its relatives: rows of a bold label with an
explanation beside it (「課題：…」「線形回帰の理由：…」「深層学習との違い：…」), boxes with a title and a
description, a row of big statistics — and a chart whose axes are lists of names (rule 22). A
comparison is shown with a figure (two bars, two images, two values on one real axis) or said in
two bullets. A row that carries no information (「残る課題：—」) is
not written at all.

**5. Few lines, each a full one; no sub-labels.**
Beside a figure: at most three bullets, one line each where possible, two at most. Noun-ending
phrases (体言止め), no です・ます, one idea per bullet. One level only: no grey second line under an
item, no small sub-title inside a box, no parenthetical gloss on every term. At most one small
grey line (a caption or a note) on a slide.

"Few words" means few *bullets* — not bullets cut down to keywords. Each bullet is one line that
states a fact completely, with its number, its condition or its source (rule 7 says why):

```
× 3割を見落とし                                    (a stub)
○ 幅1mm未満のひび割れは熟練者でも3割以上を見落とし[2]
× 幅が1mmに満たない細いひび割れについては、熟練した点検員であっても3割以上を見落とすことが報告されている。  (a sentence)
```

A consequence is written on its own line with an arrow, not as a clause:

```
× 細いひび割れをどこまで画像で拾えるかは実際の路面で未検証
○ 細いひび割れをどこまで画像で拾えるか
  →実際の路面では未検証
```

**Write it the Japanese way.** Parentheses at most once in a line, and not on every line (lint
W5): a gloss in brackets after a noun is English word order (「点検員が判定（経験5年以上・研修修了）」,
"inspectors, who…"). Japanese puts what matters in front of the noun, as one block:
「研修を修了した経験5年以上の点検員が判定」. The same goes for a sample: 「等速条件20名と2倍速条件
20名の大学生計40名で実験」, not 「大学生40名を等速と2倍速の条件に無作為に20名ずつ割り当て」 (an
English "N were randomly assigned to A and B"). A 「、」 that separates a long qualifier from its noun
is fine; one that joins two clauses is not. And do not strip every 「、」 out of a long line: after
a long opening phrase (a cause, a condition) and between a subject and a predicate far from it,
a 「、」 is what lets the line be read in one go — 「見落としを恐れて、点検員は同じ区間を2回確認」,
the frame of the purpose 「判断の根拠を示せる手法で、細いひび割れまで自動検出」. Do not cut a verb
to its stem to save a character: 「雨で光り見落とし」→「雨で光って見落とし」. End a line on a noun or a finished form, not on
〜ず (「処理時間は変わらず」→「処理時間は変わらない」, lint D6). An item that later slides refer to by
name — a hypothesis, a research question — may start with a bold label: 「**[仮説1]** 照明が暗いほど
検出率が低下」.

**6. Line breaks follow the meaning; how long the lines are depends on what the text stands against.**
No text is wrapped for you, and a line that runs to the edge and leaves one word below it looks
careless. Where you break depends on the block:

- **Text set against something else** — a caption under its picture, the framed statement, the
  centred conclusion, the cover title, a label in a figure, a list inside a column: break where
  the phrase turns into lines of **similar length**, even if the first stops short of the edge.
  The block gets narrower and sits on its figure or frame:

  ```
  × こんにちは、私の名前はクロードと        ○ こんにちは、私の名前は
    申します。                              クロードと申します。
  ```
- **A list on its own** (bullets flush left, the summary): a bullet that fits on one line stays on
  one line. One that does not is broken at the phrase boundary **nearest the end of the line**, so
  the first line is long. Breaking a bullet early to make two equal lines empties the right side of
  the slide (lint T10) — the same fault as a stub.

The library refuses a line that is too long.

**7. The weight of the slide rests in the middle: figures centred, lists flush left and full.**
Figures, equations, the conclusion line and the frame are centred. A list is **flush left at the
margin**, on the same edge as the heading — and it is **never centred as a block** (a centred
bullet list looks amateurish). The exceptions are lists that are part of a centred composition: a
list inside a column of `cols()` is centred in its column, and the premises of `therefore()` are
centred as a block over the arrow and the frame — when they do not reach the right edge, hugging
the left would leave the right side empty beside a centred frame. A list whose lines run to the
right edge is the same either way.

That makes the length of the bullets a matter of layout. Stubs at the left under centred things
leave the right half of the slide empty, and the slide tips over:

```
×  • 見落としが多い                        ○  • 幅1mm未満のひび割れは目視点検でも3割以上を見落とし
   • 費用が高い                                • 車載レーザー計測は1台約1億円で市町村には導入困難
                                              • スマートフォン画像の手法は細いひび割れの精度が未検証
               ▼                                                  ▼
      ┌──────────────────┐                          ┌──────────────────────────────────┐
      │  自動で検出       │                          │ 安価な画像で細いひび割れまで自動検出 │
      └──────────────────┘                          └──────────────────────────────────┘
```

So: **the longest line of a list reaches at least 70% of the way across a 4:3 slide (65% at
16:9), and the others are not far behind.** About 21–28 characters per bullet at 4:3. Fill a line
with information — the number, the condition, the source, the object of the verb — never with
adjectives. If there is honestly too little to say for a full line, a list is the wrong form:
use one centred `sk.conclusion()` line, or put the list beside the figure in `cols()`.

The linter measures this (L6: a list that does not reach across; a figure off the centre line;
`cx` in `--metrics` = how far the weight of the slide sits from the centre line).

**8. The eye is led one way.**
The stack is read top to bottom, once. Hold back anything that sends the eye sideways or back:

- A flow is the one figure that runs left to right; nothing else on that slide points sideways.
  The words under a flow add what it cannot show — the idea behind a step, the size of the data —
  rather than naming its boxes again.
- No rotated text: an axis is named with horizontal text above its end (`sk.ylabel_top`).
- Things that refer to each other are adjacent, in the same order and the same colour: the value
  under its image; the name at the end of its line, not in a legend; the examples beside a plot
  stacked in the order of the line ends they belong to. Two paths of the eye never cross.

**9. A part stays inside what it belongs to.**
A caption is no wider than its picture; a value and its note sit within the width of the image
above them; the consequence line of a bullet (→) is no longer than the line it follows; a label
fits its box. When a part sticks out, the hierarchy stops being visible. Shorten the part.

**10. A number is only as large as it matters.**
If the audience needs "an instant", not "50 ms", the 50 is not a hero number — it is part of a
bullet. Round what nobody needs exactly (12,436 → 約1万2千) and say it in passing. Use symbols
(「$R^2=0.203$」, not 「決定係数は0.203」). Leave out what nobody will ask about (how many features
the baseline used, who published the dataset — these go to the notes or the appendix). Never line
up numbers of different kinds side by side: neighbours read as the same kind. A number still comes
with what it is compared to — as a second bar, not as a sentence. Name each number by what it
is — 平均 for a mean, SD for a spread; one standard deviation above the mean is 「+1SD」, never
「+1平均」. Means are what a reader wants; give SDs only where the context needs them (a table in
the appendix, a column of their own). One quantity, one unit:
「300秒」 or 「5分」, not 「5分（300秒）」. A chart is scaled to its data: an axis that runs far past
the largest value leaves the chart half empty (lint F6) — a total that matters goes in the title
or a bullet.

**A share names its whole.** A percentage is read only when the audience sees, on the slide, what
100% is and what the part is — in words they know without the speaker. 「ランクⅢ・Ⅳ 38%」 on a bar
labelled 「区分」 answers neither. Name the whole in the title (「点検した市道の全区間に占める割合
（%）」), the part by what it means (「補修が必要な区間」), and the rest of the whole too
(`sk.shares()` requires all three). A code or a grade the audience has not been taught is said
aloud, or follows its meaning once. Two shares of different wholes — all sections, and the
sections repaired last year — are never rows of one chart: neighbours read as the same kind.

**11. A box hugs its text, and there is one box.**
A full-width tinted band with left-aligned text has unequal space on its two sides and looks
wrong. A framed statement is as wide as its text plus equal padding, and centred
(`sk.boxed()`); the conclusion of a slide is a bold centred line with no box at all
(`sk.conclusion()`). The frame is for the one statement of the talk — the purpose. Do not close
every slide with a band.

**12. In a flow, boxes are things and arrows are operations — and the boxes show the things.**
「デザイン原則 → 視覚統計量 → 線形回帰 → 寄与の分解」 draws data turning into an operation (an
example from review).
A box is something that exists (an image, a set of indicators, a model, a result); what is done
to it is written on the arrow.

A flow is worth drawing only if its boxes have something to show. Words in boxes joined by arrows
say nothing a sentence would not, and leave the slide empty. Follow **one real case** through the
pipeline: the actual input image, the actual numbers computed from it, the actual result.

```python
sk.flow(sk.thing("路面画像", img="figures/road.png", width=170), sk.op("検出"),
        sk.thing("ひび割れ画素", img="figures/road_mask.png", width=170), sk.op("集計"),
        sk.thing("区間の指標", values=[("ひび割れ率", "4.2%"), ("最大幅", "3.1mm"), ("ほか2指標", "")]),
        sk.op("順位付け"), sk.thing("補修の順位", media=tiny_chart_of_the_real_ranking, accent=True))
```

No sub-label (a small explanatory line) inside a box. If the boxes would hold only words, do not
draw a flow: say it in bullets, or find the figure that shows it.

**13. The purpose slide states the purpose, in one line.**
What is missing (two bullets) → an arrow → the purpose in a frame (`sk.therefore()`). No method,
no "why linear regression", no "difference from deep learning" on this slide. If the novelty needs
arguing, the place is the prior-work slide, as a figure that makes the gap visible. There, each
bullet says what that work falls short on, its strength only as the contrast in front
(「深層学習は発見率95%と高いが判断の根拠は不明」): bullets that only say what the others achieved
leave the audience asking what is wrong with them, even when the figure shows it.

**14. The method takes several slides, and is shown with concrete examples.**
One overview (a flow), then the key steps one per slide, each on a real example: the actual image,
the value computed from it, the formula. A slide that only describes the dataset is not a method
slide; the dataset is one bullet (「120区間・約1万2千枚の路面画像」). For an experiment, the method
is shown as what happened: the setting drawn (who sat where, what they saw — people drawn as
people), the stimulus or the questionnaire item as the subject saw it, what was measured on one real
case. On the result slides, a bullet that bears on a hypothesis gives the fact read off the chart
and then, as its consequence, the hypothesis in words with its label: 「→2倍速では予習なしの被験者
だけ得点が低下：**仮説2**の支持」. A bare 「→仮説2を支持」 makes the audience recall what hypothesis 2
was. (Write 支持, not 立証: a test supports a hypothesis, it does not prove it.) Every thing in the drawing faces the way it acts — a camera points at the person it
records, a person faces whom they talk to (`sk.icon(…, flip=True)` mirrors an icon). When the results are read against hypotheses, the hypotheses get a slide of their
own (story.md §8).

**15. Names tell things apart.**
A label for prior work must not also describe this work (calling prior work 「特徴量の回帰」 when
this work is also a regression on features distinguishes nothing). Name each thing by what makes
it different.

**16. Colour: dark blue is the subject, grey is for comparison, red is the one thing to look at.**
In a chart, this work is dark blue (`highlight=`), everything shown only for comparison is grey,
and the bars the slide is about are red (`hot=`). Red text (`!!…!!`) at most once per slide. Red
points at something; it never colours a thing that is not red — a blush may be red, sweat may not.

**17. Bold is for the words that must not be missed.**
Bold is for the gist and for key words, nothing else. The conclusion line, the framed statement,
the value under an image and the highlighted bars are bold by design; ordinary labels in a
diagram are not. Inside bullets, `**…**` marks a few keywords per slide — on a result slide the
measures the chart is about (「**視聴時間**」「**正答数**」), and the label of a hypothesis — never a
whole bullet. In the message, the words that carry the finding may be bold, once (rule 3). A label
in front of an item that is referred to later (**[仮説1]**) is bold.

**18. Static, undecorated, and as few slides as the talk needs.**
No animation, nothing that appears or is circled during the talk. (A mark drawn into a figure —
one ring around the place that matters — is part of the figure, rule 3.) No icons, illustrations,
logos or shapes "for atmosphere"; an image is on the slide because the slide fails without it. A
person, a camera or a screen drawn in a diagram of the setting (`sk.person`, `sk.icon`) is not
decoration: it is the thing shown. Never put an icon beside a heading or a bullet. No divider slides, no
agenda for a talk under about 20 minutes, no 「ご清聴ありがとうございました」. The last main slide is
the summary; it stays up during questions. Detail only a questioner wants goes to the appendix
(tables of numbers live there).

**19. Write for the audience actually in the room.**
Decide what they already know and explain exactly the rest — aloud. Spell terms out; use an
abbreviation only for something that appears twice or more. Use these words where they differ
from the material's: in an experiment the people tested are 被験者, even when the paper
writes 実験参加者. An experiment is a study in which people do a task under conditions the
researcher sets. In a clinical or field study — patients, residents or users who receive a care
or a service — keep the field's own word (対象者, 患者, 利用者), as the material writes it.

**20. Nothing invented.**
Every number, name and claim comes from the material and is recorded in `numbers.md`. Do not add
"illustrative" facts or examples that are not in the source. If the material does not support a
claim the story needs, tell the user instead of filling the gap. A schematic of what a hypothesis
predicts may be drawn — labelled as a prediction, with no numbers on it. Values read off a
published figure are estimates, not data: do not print them (figures.md §1).

**21. A pattern is chosen for the content; nothing is copied from the examples.**
The gallery and the examples in the references show how to *call* each component. They are not
the answer to which figure a slide needs, and their topics and numbers are invented. A prior-work
slide is not automatically a position map, a method is not automatically a flow, a result is not
automatically bars. Decide each figure from what this material can show (story.md §5), and check
the deck as a whole: if its figures are the gallery's figures with new labels, it is a template,
and the audience sees it.

**22. Axes say exactly what is measured — and a place on a chart means something.**
An axis is an amount, or the ordered steps of one (school years, the grades of a scale, in their
order). A list of kinds — groups of people, types of effect, families of method — is not an axis:
it has no order, so a point on it is placed nowhere in particular, and a grid of names with dots
at the crossings is a table of words dressed as a chart (rule 4; slidekit warns, lint F7). To
show where this work stands, show what actually differs: an amount on its own axis at its real
values (the narrowest crack each method finds, as bars), a time on a time axis (how long after
watching each study tested), the two settings side by side as pictures — or two bullets.

A position map placed by judgement (`sk.posmap`) is a decision to make each time, never a habit,
and most talks have none. It works only when the talk turns on a trade-off between two amounts
the listeners weigh against each other — the other approaches each give up one, this work holds
both — that they would not see as quickly from two bullets, and when the evidence for the places
differs in kind so that they cannot share a scale (when every point has the same measures, plot
the values). When the others differ from this work in kind, on one property only, or by one
missing thing, it does not work: use the forms above. When it is drawn, every part carries
something: the evidence for each place under its name (`value`), this work in a dashed ring
(`target=`) and nothing else to mark the gap, the axes named by what increases. The linter lists
every position map (F8) and the report gives the reason the slide needs it (figures.md §7).

Name an axis by its quantity, with the unit in parentheses — the only parentheses in an axis
name — and with the aggregate when the values are aggregates (「発見までの時間の平均（秒）」). An
axis that only runs from less to more, with no values (a schematic, a prediction), has no ticks:
its name says what increases (「照明の明るさ」); 「低」「高」 under its ends are ticks pretending to be
values. An axis that has no values gets an arrowhead at its end, with its name at the arrowhead
(`sk.schematic_axes`). Name a level by what it is a level of: 「照明」 says less than 「照明の
明るさ」 — write 「〜の高さ」「〜の量」 when the axis runs from less to more. Two ticks are right when
they are two real conditions or values (晴天 / 雨天, −1SD / +1SD). One quantity per axis: three
outcomes on one axis read as one curve. But when several outcomes are predicted (or found) to take
the same shape, draw the shape **once**, name the axis by the quantity they share in plain words
(「理解の程度」 — never a placeholder such as 「各指標」 or 「予測値」, which says nothing), and list
the outcomes once in the caption; three identical panels side by side are clutter. An axis line
runs a little past its last tick and stops before the labels written past the data; the plot
area — not the plot plus its labels — sits on the centre line (`save_fig` does both). Details in
figures.md §8.

## Revising a deck

When the user gives feedback on a finished deck, change `deck.py`, then run Phase 5 and Phase 6
again and report what changed. Do not touch slides the feedback did not concern — but when the
feedback is about a habit (「文章が多い」「図が少ない」), it applies to every slide, not only the one
it was said about; fix the whole deck. If feedback asks for something the theme does not allow (a
different colour on one slide, smaller text), explain what the rule protects and offer the nearest
thing the theme can do; if the user still wants it, do it with `sk.raw()` and note the deviation.

To change the accent colour of a whole deck (for example to a university colour):

```python
deck = sk.Deck(title="…", minutes=10, accent=("#7a1f2b", "#f6eced"))   # (accent, very pale tint)
```

Choose an accent with at least 7:1 contrast against white and a tint that is nearly white.

If the skill itself is updated later, `node "<skill-dir>/scripts/init.mjs" <deck-dir> --refresh`
replaces a deck's `slidekit.py` and `theme/` with the current versions.

## Reference files

| File | Read it |
|---|---|
| `references/story.md` | at Phase 2, before writing the outline |
| `references/figures.md` | at Phase 3, before preparing any figure |
| `references/design.md` | at Phase 4, before writing the first slide |
| `references/layouts.md` | at Phase 4, and keep it open while composing |
| `references/lint-rules.md` | at Phase 5, when a rule needs explaining |
| `references/qa.md` | at Phase 6 and through Phases 7–8 |
