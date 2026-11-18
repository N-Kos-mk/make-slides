# Designing the talk (Phase 2)

A deck looks good when each slide has one thing to show and a few words to name it. That is
decided here, before any slide exists. Layout cannot repair a slide that was designed as a
paragraph.

## Contents

1. Audience first
2. The one sentence
3. Slide budget from the talk length
4. The parts of the talk, and the headings
5. Designing one slide: figure first
6. Writing the message
7. Words on the slide, and what goes to the notes
8. The slides that are easy to get wrong
9. Conditions, limits, and anticipated questions
10. Appendix
11. Speaker notes and timing
12. The outline file
13. Checklist before leaving Phase 2

---

## 1. Audience first

Answer three questions and write the answers at the top of `outline.md`.

- **Who is in the room?** e.g. 同じ専攻の大学院生と教員 / 学会の同分野の研究者 / 他部署の管理職
- **What do they already know?** This sets the line of common knowledge.
- **What should they be able to say or decide afterwards?**

The line of common knowledge decides what gets explained — and the explaining is done **aloud**,
not on the slide. Draw the line deliberately:

- A term everyone in the room uses daily needs no gloss. Explaining it wastes time.
- A term from your sub-field needs a gloss the first time: one spoken sentence, written in the
  notes. It goes on the slide only when the audience must keep it in view to follow the figure.
- The line depends on the people, not on how technical the term sounds. For a general graduate
  audience in informatics, 「線形回帰」 needs no explanation but 「Shapley値」 does. For a Japanese
  audience the rules of 麻雀 need no explanation and the rules of poker do.

Make a short list in the outline: terms that get a gloss (and on which slide), terms that do not.

Abbreviations: prefer the full word. Use an abbreviation only when the thing appears at least
twice in the main slides, and introduce it at first use. Standard symbols are welcome where they
are shorter than the words and the audience reads them without effort: 「$R^2=0.203$」 rather than
「決定係数は0.203」, 「$r=0.77$」 rather than 「予測相関は0.77」.

## 2. The one sentence

Write the one sentence the audience should be able to repeat tomorrow.

> 例: 「安価な路面画像だけで、幅1mm未満のひび割れまで9割を自動で検出できる」

Every main slide must help deliver that sentence. Material that does not is cut or moved to the
appendix, however much work went into it.

## 3. Slide budget from the talk length

Count main slides including the cover; references, the blank slide and the appendix are extra.

| Talk length | Main slides (incl. cover) | Typical |
|---|---|---|
| 3 min | 3–4 | 4 |
| 5 min | 5–7 | 6 |
| 7 min | 7–9 | 8 |
| 10 min | 9–12 | 11 |
| 12 min | 11–14 | 13 |
| 15 min | 13–18 | 15 |
| 20 min | 17–24 | 20 |
| 30 min | 24–34 | 28 |
| 45 min | 34–46 | 40 |
| 60 min | 42–56 | 48 |

Rules of thumb behind the table:

- About one main slide per minute. Slides in this skill carry one figure and a few words, so they
  are taken in quickly; a slide that needs two minutes is carrying two points and should be two
  slides.
- More than about 1.3 per minute means slides are flipped, not seen. Fewer than 0.6 per minute
  means slides are overloaded.
- Cover: 10–20 seconds. A content slide: 35–75 seconds. A slide with a dense figure: 60–90.
- A slide that would be on screen for less than 25 seconds does not deserve to exist; merge it.
- Leave a few percent of the time unassigned. Talks run long, never short.

Pass `minutes=` to `sk.Deck` and `sec=` to the cover and every main slide; the linter checks that
the seconds add up and that the count fits.

## 4. The parts of the talk, and the headings

Derive the parts from the argument. These are common shapes, not templates to fill.

**Research talk (学会発表・中間発表・ゼミ), 10–15 minutes**

| Part (= heading) | Slides | Share of time | What it must establish |
|---|---|---|---|
| 研究背景 | 1 | 10% | why the question matters to this audience |
| 先行研究 | 1 | 10% | what is known and what is missing |
| 目的 | 1 | 5% | what this work sets out to do, in one line |
| 提案手法 / 方法 | 3–4 | 35% | an overview, then the key steps on concrete examples |
| 結果 | 2–3 | 30% | one point per slide, each with its figure |
| まとめ | 1 | 8% | the points again, and what comes next |

Background and prior work together stay under a quarter of the time. The method gets several
slides because it is *shown*, step by step, not described in one block. If cutting is needed, cut
a method step — it can go to the appendix.

**Experimental study (心理学・人間工学・教育などの実験), 10–15 minutes**: 研究背景 → 先行研究 → 目的
→ 仮説 → 方法 - 実験 → 方法 - 測定と分析 → 結果 - 〈測定・分析の種類〉 … → まとめ. The method is
shown as what happened (the setting drawn with its people, the stimulus or the item as the
participant saw it), and the results are read against the hypotheses (§8).

**Progress report (進捗報告)**: 前回からの結論 → 根拠 → 課題 → 次の予定.

**Paper reading (輪講)**: 論文の主張 → 位置づけ → 手法 → 結果 → 批評.

**Business briefing**: 結論と依頼 → 理由 → 選択肢 → 次の行動.

**The heading** of a slide is the name of its part, set large. When a part has several slides,
add the topic after a hyphen so the audience always knows where they are:

```
研究背景
先行研究
目的
提案手法 - 全体像
提案手法 - 検出
提案手法 - 優先度の計算
結果 - 精度
結果 - 速度
結果 - 頑健性
まとめ
```

**The topics of one part are siblings, at one level.** Each names the kind of question its slide
answers — the kind of analysis or measure — not the items of content on it:

```
× 結果 - 検出率と誤検出        ○ 結果 - 精度
  結果 - 処理時間                結果 - 速度
  結果 - 夜間と雨天の画像          結果 - 頑健性
```

The left mixes two measures, one measure and two subsets of data; the third topic is so specific
that the part no longer reads as one. If one topic is 「精度」, its siblings are 「速度」「頑健性」,
not 「夜間の画像」. Write the topics of each part side by side in the outline and read them as a
set before writing a slide (the linter lists them, S10). Keep them bare — 「実験」, not
「被験者実験」 — and when nothing general fits a slide, it may belong under a neighbouring topic.

The same holds for the method. Its topics are the stages a listener follows, all of one kind:
the parts of the procedure (「装置 / 手順 / 測定 / 分析」) or the steps of the computation
(「全体像 / 検出 / 優先度の計算」). Mixing the kinds — 「方法 - カメラ」 (a thing), 「方法 - 撮影の
条件」 (a setting), 「方法 - 1週間の走行」 (a schedule) — reads as a list of whatever each slide
happened to hold. Name a slide by the stage it shows: the camera and its mounting are 「装置」, the
conditions and the schedule of the drives are 「手順」.

- The heading is a label, never a sentence: it fits in about 17 full-width characters at 4:3
  (23 at 16:9), and usually in far fewer.
- Slides of one part sit together. Every heading in the deck is different (number the topic when
  two slides share one: 「指標の例(1)」「指標の例(2)」).
- The large heading replaces divider slides and the agenda.

What does not get a slide:

- **Agenda / 目次** for talks under about 20 minutes.
- **Section dividers.** A slide with only a section name is a slide with nothing to show.
- **"Thank you" / 「ご清聴ありがとうございました」.** The summary stays up during questions.
- **A slide that exists only to perform an action** (reveal, transition, "here is a question").

What does get a slide although it shows nothing: **a disclosure the event requires**. Many 学会
ask for a conflict-of-interest (COI) statement right after the title, in a wording or a form of
their own. Add it with `deck.disclosure([...])` directly after the cover, in the event's wording,
for about 10 seconds; it counts in the time, not in the slide budget, and the checks for main
slides do not apply to it. Do not add one when the event does not ask for it; when it is unclear
whether it does, leave it out and say so in the report.

## 5. Designing one slide: figure first

For each slide decide, in this order:

1. **The message** — what does this slide say? One short phrase (section 6).
2. **The figure** — what can the audience *look at* that makes the message true before their
   eyes? Name it concretely, together with **what in it they should look at**: "a wide and a fine
   crack from the data, side by side, each with its detection rate — the fine one in red";
   "detection rate by crack width, the narrowest group in red"; "the pipeline as a flow with the
   road image as its first box".
3. **The words** — what must be readable on the slide besides the figure? Usually two or three
   facts, each written as one full line, or one closing line. Often nothing.
4. **The notes** — everything else you would say.

Finding the figure is the real work of this phase. Go through what you collected in Phase 1:

| The slide is about | Look for | Typical figure |
|---|---|---|
| a phenomenon, a problem, "what X looks like" | photos, screenshots, samples in the material | two real examples side by side, each with its value |
| what prior work did and did not do | the prior papers' figures and numbers | the key figure of a prior paper; real examples of what earlier methods miss; their numbers as bars beside this work's; what differs from this work on its real axis (a time, an amount). Not a grid of names; a position map only when the position itself is the point (figures.md §7) |
| how the method works overall | the things that flow through it | a flow: boxes = things, arrows = operations |
| how an experiment was run | the setting, the apparatus, the stimulus, the questionnaire | the setting drawn with its people as people (`sk.person`); the stimulus or the item as shown |
| what a hypothesis predicts | — | a schematic of the predicted pattern: axes named by their quantities, no ticks, no numbers, one outcome per panel |
| one step of the method, a definition | one real input and its computed value | the real example with the value under it, plus the formula |
| a model | its equation and one worked case | equation + the terms of one real example as bars |
| a comparison of a few values | the numbers | vertical bars with the values on them |
| a ranking, a breakdown | the numbers | horizontal bars, sorted, the subject coloured |
| a trend, a relation, a distribution | the data | a plot with the lines labelled directly |
| what the study aims at | — | (text-only) premises → arrow → the purpose in a frame |
| the conclusions | — | (text-only) large bullets |

If you cannot name a figure for a slide, one of these is true: the slide is the purpose or the
summary; the slide is saying something abstract that should be said with a concrete example
instead; or the slide should not exist and its content should be spoken on a neighbouring slide.

The table is a list of possibilities, not a mapping from parts of the talk to figures. Two talks
whose prior-work slides are both position maps, or whose methods are both four-box flows, were
filled from the table rather than from their material (SKILL.md rule 21).

Use the material's own images generously. A dataset of screenshots, a photo of the apparatus, a
sample of the raw data, a page of the questionnaire — these make a talk concrete in a way no
generated diagram does, and leaving them unused is a common and serious omission.

## 6. Writing the message

The message sits under the heading: one phrase, read at a glance, saying what the slide says.

- **Noun-ending (体言止め).** Not a sentence.
- **No 「、」 and no 「。」.** A phrase with a comma in it is two phrases; keep one.
- **18 full-width characters or fewer as the aim.** Over 20 is a warning (M2); the library
  refuses more than 24.
- It **says something** — it is not a second heading. 「精度の評価結果」 says nothing;
  「幅1mm未満も9割を検出」 does.
- It is **a claim with its subject and what happens to it**, and a comparison names both sides.
  「雨天では逆に低下」 leaves out what drops and compared with what: 「雨天では検出率が晴天より低下」.
  Words that point outside the message — 逆に、同様に、前者、後者 — have nothing to point at in a
  phrase read alone (lint M4).
- **Its key words may be bold**, once, when the figure below proves them:
  「**幅1mm未満**のひび割れも9割を検出」. This is one of the ways a chart says where to look
  (SKILL.md rule 3).

| A sentence (reads as generated) | The phrase |
|---|---|
| 見た目の第一印象がサイト全体の評価を左右する | 第一印象がサイト全体の評価を左右 |
| 既存の手法は予測性能と説明性を両立できていない | 予測性能と説明性の両立 |
| デザイン原則を指標に翻訳し、評価への寄与を測る | 指標決定と寄与測定 |
| 約1万2千枚の路面画像と、120区間の点検記録を使用 | （データは箇条書き1行で足りる。このスライドは不要） |
| 安価な画像だけで、車載レーザー計測と同程度の発見率 | 車載レーザー計測と同程度の発見率 |
| ひび割れの面積と補修の緊急度は一致しない | ひび割れの面積と緊急度は不一致 |
| 発見率の低下は、ほとんどが雨天の画像で起きている | 発見率の低下は主に雨天の画像 |
| 画像の暗く細い線の連なりからひび割れを検出する | 暗く細い線の連なりでひび割れを検出 |
| （比べる相手がない）雨天では逆に低下 | 雨天では検出率が晴天より低下 |

(The first three rows are corrections made in review.)

How to get from the sentence to the phrase:

1. Write the sentence you would say aloud when the slide appears.
2. Drop what the heading already says (「既存の手法は」 under 先行研究; 「本研究では」 anywhere).
3. Turn the verb into its noun: 左右する → 左右、測る → 測定、一致しない → 不一致、占める → drop it.
4. If there is a 「、」, the sentence has two parts. Keep the one the slide is about, or join two
   nouns with 「と」: 「指標に翻訳し、寄与を測る」 → 「指標決定と寄与測定」.
5. A negative state can be named by the thing at stake: 「両立できていない」 → 「〜の両立」 (the
   figure shows that nobody has achieved it).

When the heading says it all, the slide has no message: 目的 and まとめ normally pass `None`.

Test: read only the headings and messages, in order. They should give the outline of the talk.

## 7. Words on the slide, and what goes to the notes

**On the slide**

- Next to a figure: at most three bullets. One line each where possible; never more than two.
- **Each bullet is one full line** — a fact stated completely, with its number, its condition or
  its source — that reaches well across the slide (at 4:3 about 21–28 characters; at least 70%
  of the width). Bullets are flush left, so stubs leave the right half of the slide empty.

  | A stub (too thin) | A full line | A sentence (too much) |
  |---|---|---|
  | 50ミリ秒で形成 | サイトの視覚的な印象は提示から約50ミリ秒で形成[1] | 見た目の第一印象は、提示からわずか50ミリ秒程度という短い時間で形成されることが知られている。 |
  | 見落としが多い | 幅1mm未満のひび割れは熟練者でも3割以上を見落とし[2] | 幅が1mmに満たない細いひび割れについては、熟練した点検員であっても3割以上を見落とすことが報告されている。 |
  | 根拠が不明 | 深層学習は発見率95%と高いが判断の根拠は不明[4] | 深層学習による手法は高い発見率を報告しているが、何を根拠にひび割れと判断したのかを示すことができない。 |

  Length comes from content, never from padding (「非常に」「〜することができる」). If a point
  has no more content than a keyword, it is not a bullet: merge it into another, say it aloud,
  or — when it is the one thing to say — make it a centred `sk.conclusion` line.
- Noun-ending phrases, no です・ます, no 「。」, one idea per bullet, parallel grammar.
- One level: no sub-bullets, no grey second line, no parenthetical gloss on every item.
- **Parentheses at most once in a line, and not on every line** (lint W5). A gloss in brackets
  after a noun is English word order — 「点検員が判定（経験5年以上・研修修了）」 reads like "inspectors,
  who…". Japanese says the important thing as one block in front of the noun:
  「研修を修了した経験5年以上の点検員が判定」. A 「、」 that separates a long qualifier from its noun
  is fine (「共通の基準で訓練した、経験5年以上の点検員」); one that joins two clauses is not.
- End a line on a noun or a finished form — not on the continuative 〜ず, which leaves it hanging:
  「処理時間は変わらず」→「処理時間は変わらない」 (lint D6).
- Items that later slides refer to by name — hypotheses, research questions — start with a bold
  label: 「**[仮説1]** 照明が暗いほど検出率が低下」. The label is the one bold thing that may open a
  bullet.
- One quantity in one unit: 「300秒」 or 「5分」, not both.
- Do not tell the audience what was left out — 「エラーバーは省略」「詳細は割愛」「一部抜粋」. Nobody
  misses what is not there; the notes can say it.
- A sample is one noun block with its breakdown in front: 「等速条件20名と2倍速条件20名の大学生計40名で
  実験」, not 「大学生40名を…に20名ずつ割り当て」.
- Keep the 「、」 a long line needs. The message has none (§6), but a bullet or the purpose that opens
  with a long phrase reads in one go only with a pause after it: 「見落としを恐れて、点検員は同じ区間を
  2回確認」; between a subject and a predicate far away: 「判断の根拠を示せる手法で、細いひび割れまで
  自動検出」. One or two per line, where you would pause when reading aloud.
- Do not cut a verb to its stem to save a character: 「雨で光り見落とし」→「雨で光って見落とし」.
- In an experiment the people tested are 被験者 (not 参加者, even when the paper
  writes 実験参加者). In a clinical or field study — patients, residents or users who receive a
  care or a service — keep the field's word as the material writes it (対象者, 患者,
  利用者).
- A consequence gets its own line starting with an arrow, and is no longer than the line it
  follows: `"デザイン原則のどれが印象に影響を与えるか\n→大規模なデータでは未検証"`.
- You place every line break. A bullet that fits on one line stays on one line. One that does
  not is trimmed first; if it must be two lines, break it at the phrase boundary nearest the end
  of the line, so that the first line is long. Lines of similar length are for text set against a
  figure, a frame or a column — not for a list on its own, where an early break empties the right
  side (SKILL.md rule 6, lint T10).
- Bullets of one list are of similar length: one stub among full lines makes a ragged block.
- Under a flow, add what the flow cannot show — the idea behind a step, the size of the data —
  rather than naming its boxes again.
- Numbers as digits with units, rounded to what matters (約1万2千枚, not 12,436枚).
- One name for one thing. If it is 「指標」 on slide 5 it is not 「特徴量」 on slide 8.
- No filler and no sales language: 「非常に」「さまざまな」「重要である」「革新的」「包括的」
  「〜を実現」「〜が鍵」. Say the specific thing.
- No 「見出し語：説明」 constructions (「線形回帰の理由：〜」「深層学習との違い：〜」). State the
  point itself, or say it aloud.

**In the notes** (`notes=`), not on the slide

- how a method works in detail; why this method and not another;
- definitions of terms; the gloss for anything below the audience's line of knowledge;
- conditions and caveats that a listener does not need in view (keep on the slide only the one
  without which the figure would mislead);
- counts and names nobody will ask about (how many features a baseline used, who published a
  dataset, exact sample sizes when the order of magnitude is what matters);
- what each number means and how good it is;
- the sentence that leads to the next slide.

A useful check on every bullet: *would the audience miss it if it were only spoken?* If not, it is
spoken.

Compressing:

| In the paper | On the slide |
|---|---|
| 本研究では、120区間・12,436枚の路面画像を対象とし、ひび割れの幅ごとに発見率を評価した。 | 120区間・約1万2千枚の路面画像で幅ごとの発見率を評価 |
| 提案手法は従来手法と比較して精度が高いことが確認された。 | (two bars; no words) |
| この結果から、幅1mm未満のひび割れでも91%を検出しており、目視点検の63%を大きく上回ると考えられる。 | 幅1mm未満の発見率は目視点検の63%に対して91% |
| 輝度の勾配だけを用いる従来法では、発見率は62%にとどまる。 | 輝度の勾配だけでは発見率 62% どまり |
| 深層学習を用いないのは、判断の根拠を示せるためである。 | (notes only) |

Compress the grammar, keep the content: the slide version drops the subject, the copula and the
hedges (「〜と考えられる」「〜ことが確認された」), not the numbers and the nouns.

## 8. The slides that are easy to get wrong

**研究背景.** Not a list of facts with citations. One real picture of the phenomenon (examples
from the material), then two or three bullets that end in the gap.

**先行研究.** Not a comparison table, not a grid of names, and not automatically a position map.
Choose the figure from what the prior work offers: the key figure of a prior paper (cited); real
examples of what earlier methods miss; the numbers they report as bars beside this work's. Then
two bullets, one for each prior approach, each saying what it falls short on with its number — its
strength only as the contrast in front (「深層学習は発見率95%と高いが判断の根拠は不明」) — and the
gap as a consequence line. Bullets that only say what the prior work achieved leave the audience
asking what is wrong with it. Name each prior approach by what
distinguishes it from this work (rule 15 of SKILL.md).

Where this work stands is usually said by those two bullets. When it must be seen, show **what
actually differs** — the one amount or time that the purpose turns on, on a real axis with each
study at its value (how many days after watching each study tested; the narrowest crack each
method finds), or the two settings side by side as pictures. Never lay names of kinds (who was
studied, which effect) along two axes with dots at the crossings: no place on it means anything
(figures.md §7, lint F7). A position map placed by judgement (`sk.posmap`) is for the rare talk
whose point is a trade-off between two amounts that the others each give up and this work alone
holds; decide each time that the slide needs it (figures.md §7 lists when it works and when it
does not), and then write the evidence for each place under its name and ring this work. Most
talks have none.

**目的.** The purpose in one line, in a frame, under an arrow from two bullets that state what is
missing (`sk.therefore`). Nothing about the method. If you find yourself writing why the method
was chosen, stop: that is said aloud on the first method slide.

**仮説.** (when the results are read against hypotheses) One bullet per hypothesis, each opening
with a bold label so that the result slides can point back to it:
「**[仮説1]** 照明が暗いほど検出率が低下」「**[仮説2]** 雨天では低下がさらに大きい」. A schematic of
the predicted pattern may stand above them: labelled as a prediction, no numbers, axes named by
their quantities with no 低/高 ticks (SKILL.md rule 22), one outcome per axis — three outcomes
drawn on one axis look like one. When the hypotheses predict the same shape for several outcomes,
draw the shape once and name the outcomes once (「視聴時間・正答数・自己評価のいずれもこの形を
予測」 in the caption); three identical panels in a row look clumsy.

**提案手法 / 方法.** Several slides. For a computational method: first an overview as a flow in
which the boxes are things and the arrows are operations, then each key step on a concrete
example from the data — the real input, the value computed from it, the formula. For an
experiment: the setting drawn (who sat where, who faced whom, what was recorded; people as people,
`sk.person`), then what was measured, shown on the real item or a real case. The dataset or the
sample is a bullet, not a slide.

**結果.** One point per slide, and **the figure shows where the point is**: the bars or the line it
is about in red, the decisive gap labelled or ringed, the key words of the message in bold
(SKILL.md rule 3). A bullet that bears on a hypothesis is two lines: what the chart shows, then
the hypothesis in words with its label —

```
× 予習なしの被験者では2倍速で得点が低下
  →仮説1を支持                               (what was hypothesis 1?)
○ 2倍速の線は予習なしでだけ大きく下がる
  →予習なしでは2倍速で得点が低下：**仮説1**の支持
```

and the measures the chart is about may be bold in the bullets (「**得点**」「**自己評価**」). Write
支持, not 立証. The bullets carry at most the two facts that the chart cannot show (another
dataset, a robustness check). When the claim is about quantities (time in each condition), chart
those quantities; a chart of coefficients makes the audience decode signs.

**まとめ.** Large bullets only: the conclusions (two or three), then what comes next in the accent
colour. No new information, no figure: the summary stays up during questions, and a fact seen for
the first time there cannot be checked against a figure and draws the questions away from the
results. A fact important enough for the summary — the minutes a check of the detections takes
per kilometre, the yearly cost of the service — is important enough for a main slide: put it
there first, as a bullet on the result slide it belongs with (or in the notes, if it is not), and
let the summary repeat it.

## 9. Conditions, limits, and anticipated questions

- The one condition without which a figure would mislead goes on the slide, small — a caption or
  `sk.note()` (「評価条件が異なるため優劣は論じない」「架空のデータ」). One per slide at most; the
  rest are spoken.
- Where two numbers are easy to confuse (the same metric on different data), keep them apart on
  the slide — different charts, different slides — and spell out the difference in the notes.
- List the questions a critical listener will ask. For each: it is answered by a main slide, or an
  appendix slide is prepared. Record the list in the outline.

## 10. Appendix

The appendix holds what only a questioner needs: full tables of numbers, definitions, alternative
analyses, derivations, data details.

- Order: main slides → 参考文献 → one blank slide → appendix. The blank slide keeps the appendix
  from appearing by accident after the last click.
- Appendix slides are added with `deck.appendix(...)`; give them headings that start with 「補足 - 」.
  They have the same anatomy as main slides. Tables of numbers belong here.
- Appendix slides are not counted in the slide budget and take no `sec=`.
- Do not skimp on it. A 10-minute research talk usually has three to six appendix slides: the
  original figures you redrew, the full tables of the numbers you showed in part, the analyses and
  measures left out of the main part, the details of the procedure, and one slide for each
  anticipated question that the main slides do not answer (§9).
- An appendix slide answers one question, and some answers are words: the criteria for including
  people in a study, the reasons a measure was left out. Such a slide may be text only
  (`text_only=True`), under the same rules as any list — up to five full-line bullets, one level,
  no 「見出し語：説明」 rows. Look for its figure first all the same: how many were excluded at each
  step is a flow of counts; a definition has its formula and one example.

## 11. Speaker notes and timing

Each main slide takes `notes="""…"""`. The build collects them into `out/notes.md`. Because the
slides carry so little text, the notes are where the content of the talk lives — write them with
the same care as the slides.

For each slide write:

1. the opening line — the message, as a spoken sentence;
2. where to look on the figure (「左が幅3mm以上、右が幅1mm未満のひび割れ」) — this replaces
   pointing devices and marks added during the talk; what must be seen without the speaker is
   marked in the figure itself (SKILL.md rule 3);
3. what each number means and how good it is, with the comparison;
4. the conditions, definitions and reasons that were kept off the slide;
5. the line that leads into the next slide.

Pace for a formal talk in Japanese is about 300 characters per minute, so a 60-second slide
carries about 300 characters of speech. If the notes for a slide are much longer than its seconds
allow, split the slide.

The presenter must be able to explain every word, figure and number on a slide immediately.
Anything they could not explain does not go on the slide.

## 12. The outline file

Write `<deck-dir>/outline.md` in the user's language, in this shape:

```markdown
# 発表設計

- 発表: 2026年度 ○○発表会（10分、質疑あり）
- 聞き手: 同じ分野の研究者と大学院生。画像処理の基礎は既知、舗装点検の実務は未知
- 持ち帰ってほしい一文: 〜〜
- 比率: 16:9
- 口頭で説明する用語: ひび割れ率（p.5）、適合率と再現率（p.8）
- 説明しない用語: 畳み込み、相関
- 区分ごとの話題: 提案手法 = 全体像 / 検出 / 優先度の計算、結果 = 精度 / 速度 / 頑健性

## 構成（本編 11枚 / 600秒）

| No | 見出し | 一言 | 図 | スライド上の文字 | 秒 |
|---|---|---|---|---|---|
| 1 | （表紙） | — | — | — | 15 |
| 2 | 研究背景 | 細いひび割れほど見落とし | 幅の広いひび割れと細いひび割れの画像を並べて目視での発見率を添える。細い方の値を赤 | 箇条書き3行（点検は1kmあたり約3時間[1]／幅1mm未満は3割以上を見落とし[2]／細いうちの補修で費用は約5分の1） | 55 |
| 3 | 先行研究 | 精度と費用の両立 | 先行手法の報告値を本研究と並べた棒（発見率）。本研究を濃紺 | 箇条書き2行（車載レーザーは1台約1億円[3]／スマートフォン画像は細いひび割れが未評価[4]） | 55 |
| 4 | 目的 | — | （文字のみ）前提→矢印→目的 | 前提3行（幅いっぱいに届く長さで）＋目的1行 | 35 |
| 5 | 提案手法 - 全体像 | 検出と区間ごとの順位付け | フロー: 1区間を通す。箱の中身は実際の路面画像→検出したひび割れ画素→区間の指標の値→補修の順位 | 箇条書き3行（市販のカメラで撮影／暗く細い線の連なりを検出／区間ごとに集計） | 60 |
| … | | | | | |

## 本編のあと

| No | 種別 | 見出し |
|---|---|---|
| 12 | 参考文献 | 参考文献 |
| 13 | 空白 | — |
| 14 | 補足 | 補足 - 区間ごとの指標（数値の表） |

## 図の素材

| 図 | 出どころ | 準備 |
|---|---|---|
| p.2 のひび割れ2枚 | データセットの画像、発見率は論文の表2 | prepare.py で幅の最大・最小の例を選んで縮小 |
| p.8 の棒グラフ | 結果の CSV | deck.py で sk.bars（幅1mm未満を赤） |

## 想定質問

| 質問 | 対応 |
|---|---|
| 夜間でも使えるか | p.10 に記載、詳細は補足 p.16 |
```

## 13. Checklist before leaving Phase 2

- [ ] The one sentence is written and every main slide serves it.
- [ ] The slide count is inside the budget; the seconds add up to the talk length.
- [ ] Every heading is a part name (plus topic); no two are the same.
- [ ] The topics of each part, read side by side, are at one level: the kind of analysis or
      measure, not items of content.
- [ ] Every message is a noun-ending phrase with no 「、」, about 18 characters or fewer, and says
      something: a claim with its subject, both sides of any comparison, no 逆に/同様に.
      Headings and messages read in order give the outline of the talk.
- [ ] **Every slide except 目的 and まとめ names a concrete figure** — and what in it the audience
      should look at — and the material's own images are used wherever they exist.
- [ ] No figure was chosen because the gallery has one for that part of the talk, and none was
      added to fill space: each figure is there because the point needs that figure.
- [ ] No slide plans a table of words, a "label: explanation" list, or a row of statistics.
- [ ] The words planned for each slide are two or three *full lines* (facts with their numbers),
      not keywords; where there is only one short thing to say, it is planned as a conclusion line.
- [ ] Every planned diagram has something to show in it (a real case to follow through a flow);
      none is words in boxes.
- [ ] The method has an overview slide and at least one slide with a concrete example.
- [ ] The purpose slide states only the purpose.
- [ ] No slide lays names of kinds along two axes; where this work stands is shown by what
      actually differs, and a position map appears only where the position is the point.
- [ ] Every percentage is planned with its whole and its part named in the audience's words.
- [ ] Every fact in the summary has appeared on a main slide.
- [ ] What is not on the slides is planned for the notes.
- [ ] No agenda, divider or thank-you slide.
- [ ] Terms to gloss aloud are listed; abbreviations are justified.
- [ ] Anticipated questions are listed with where they are answered; the appendix holds what
      was left out (redrawn figures' originals, full tables, omitted analyses).
