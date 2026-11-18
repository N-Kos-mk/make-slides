# Visual rules and the reasons for them (Phase 4)

The theme fixes the look; this file explains it, so that the choices that remain yours — what to
show, how many words, where a line breaks — are made in the same spirit.

## Contents

1. The look in one paragraph
2. The design policy
3. What machine-made slides look like, and what to do instead
4. Canvas and anatomy
5. Type
6. Colour
7. Layout: the path of the eye and the centre of gravity
8. Line breaks
9. Emphasis
10. Boxes, lines and other furniture
11. Numbers
12. Consistency across the deck
13. Questions to ask of every slide

---

## 1. The look in one paragraph

White background, near-black text, one dark blue. A large light-weight heading in that blue with
a thick rule under it; one short phrase below; then a figure that takes most of the slide — real
images with their values, a chart with one thing coloured — and under it two or three bullets,
flush left on the edge of the heading, each a full line that reaches well across the slide; or a
single bold centred line. The figure is centred and the lines of text are long enough that the
weight of the slide rests in the middle. The date bottom-left, the page number bottom-right,
small and grey. Nothing else. No cards, no bands,
no tables of words, no icons. The effect aimed at is the deck of a researcher who drew every
figure for a reason and left the explaining to the talk.

## 2. The design policy

The rules of this skill are built on one person's standard for slides, written down as the table
below. It is kept in its original Japanese so that the intent is not lost in translation.

| 方針 | 内容 |
|---|---|
| 聞き手がどんな人たちか考える | 常識のラインをどこに置くか。言葉を噛み砕く。略語はできるだけ使わず、2回以上出る場合にのみ用いる。その語の説明が要るかどうかを聞き手で決める |
| 枚数を極限まで削る | 区分だけのスライド、アクションのためだけのスライドを作らない |
| 不要な要素を置かない | その図・文字・画像が絶対に必要だから置く。「その図がないと成立しないスライド」を目指す。イメージの補助も1つに絞る |
| 文章の削減 | 体言止めなどを活用し、文章をなるべく使わない |
| 視覚的な動きを抑える | アニメーション、後から赤丸で囲うなどのアクションをしない |
| 視線誘導 | 整列を意識。縦積み・横書きなら横矢印などは抑える。重心位置を意識 |
| 階層構造の明確化 | 自分を包含するコンテンツからはみ出さない |
| 整列 | 左端を基本揃える。中央揃えは大事な理由があるとき、または独立したテキストボックス要素のみ |
| 強調 | 太字はキーワード、趣旨、サブタイトル以上のみ。他の本文では一切使わない |
| 後からわかる | 発表を聞いていなくてもスライドを見れば内容が8割わかる。反論の余地を潰す |
| 理解度 | スライドの語句、図、表はすべて即座に説明できるようにしておく。数値はどれくらい有効なのかがわかる比較とともに。スライドには数値、説明は口頭。ただし重要なら付記する |

The rules were then sharpened by reviews of decks made with earlier versions of this skill — first
a deck that followed the letter of this table but explained everything in tidy text, then decks
that other models made from other papers with this skill alone, so that what went wrong was the
skill's, not the model's. What those reviews taught, in the order they came:

1. **The slide does not explain everything.** Sentences, sub-labels and tables of words were the
   first faults. 「後からわかる」 is satisfied by the message and the figure — a reader gets the
   point of each slide — not by writing the argument out.
2. **Fuller bullets, not centred stubs.** Cutting the words had turned the bullets into stubs;
   stubs at the left margin under centred things left the right half of the slide empty.
   Centring the list as a block is not the fix — a list is flush left. Writing fuller bullets is:
   few lines, each carrying a whole fact across the slide. 「視線誘導」「重心」「階層構造」「整列」
   are not satisfied by tidy components; they are properties of the whole slide (section 7).
3. **A diagram shows something.** A flow whose boxes hold one word each is text with arrows.
4. **A figure says what it shows**: correct charts with nothing marked leave the audience to find
   the point (SKILL.md rule 3; lint F5). **The topics of one part are at one level** — the kind of
   analysis, not the items on the slide (rule 2; S10). **The gallery is not a template** (rule 21).
   **A message is a claim** with its subject and its predicate, and **Japanese says the important
   thing as a block in front of the noun**, not in brackets after it (rules 2 and 5; M4, W5, D6).
   **What has a shape is drawn as that shape** (figures.md §9).
5. **Axes say what they measure** (rule 22): no 「低」「高」 ticks on an axis that has no values, one
   outcome per axis, the axis line ending with its scale, no axis set to a total far beyond the
   values on it, and an axis named by what increases (「〜の高さ」).
6. **No figure to fill space**; **one drawing for one shape** (the same panel three times is
   clutter — draw it once and say what it stands for); **draw things recognisably** — icons from
   the bundled sets, composed when needed, never a makeshift shape that reads as something else —
   and **facing the way they act**; **say nothing about what was left out**; **balanced line
   breaks only for text set against something else** — a bullet on its own runs its first line
   long; in an experiment the people tested are 被験者.
7. **Keep the 「、」 a long line needs**, and do not cut a verb to its stem. **Red points; it does
   not colour things** (a blush may be red, sweat may not). A result bullet that bears on a
   hypothesis gives the fact read off the chart, then the hypothesis in words with its label. The
   appendix holds what a questioner will ask for.
8. **A place on a chart is a value**: no grid of names with dots at the crossings (rule 22; F7),
   and a position map only when the position itself is the point (figures.md §7). **A share names
   its whole** (rule 10). On a prior-work slide, the bullets say what the others fall short on.

The purpose slide also has to fill its slide (the premises are set large when they fit).

How each line of the policy is carried by this skill:

| 方針 | Where it lives |
|---|---|
| 聞き手・言葉を噛み砕く | story.md §1; lint D4 (single-use abbreviations); explanations go to `notes=` |
| 枚数を極限まで削る | story.md §3–4: no divider, agenda or thank-you slide; lint K1 |
| 不要な要素を置かない | every slide has a figure it cannot do without (F1, F2); a diagram shows real content or is not drawn (G2); no decoration exists in the theme; at most one small grey line (W4) |
| 文章の削減 | the message is a phrase (M1, M2); bullets are noun-ending lines, few in number (D1, D3, W1, W2) |
| 視覚的な動きを抑える | static output: nothing appears, moves or is circled during the talk. A mark drawn into a figure — one ring around the place that matters — is part of the figure, not an action |
| 視線誘導（整列・横矢印・重心） | section 7: figures centred, lists flush left and full enough to balance the slide (L6), one direction per slide, paired things in the same order, no rotated text |
| 階層構造の明確化 | section 7 "containment" (H1; O3) |
| 整列 | text is flush left on the edge of the heading (左端を揃える); only independent objects are centred — a figure, an equation, the conclusion line, the frame. A list is never centred, except as a sub-element inside a column |
| 強調 | section 9: bold for the conclusion, the framed statement, key values, one or two keywords, and the key words of a message ("サブタイトル以上"); every chart marks its point (F5) |
| 後からわかる・反論の余地を潰す | message + figure carry the point; the one condition a critic would raise is on the slide, small (`sk.note`) |
| 理解度 | story.md §11: the notes hold what each number means; the slide holds the number |

When a situation is not covered by a rule in this skill, decide it by this section.

## 3. What machine-made slides look like, and what to do instead

These are the marks by which an audience recognises a generated deck. The left column is what a
language model produces when it is not paying attention; every item was observed in real output
and criticised in review.

| The mark | Why it fails | Instead |
|---|---|---|
| **The title is a full sentence** with a comma (「〜を指標に翻訳し、評価への寄与を測る」) | It is read as prose, not seen; every slide looks like a paragraph with a heading | Heading = the part of the talk, large. Message = one noun-ending phrase (「指標決定と寄与測定」) |
| **A small label above the title** (BACKGROUND / 背景 in tiny letters) | The audience cannot tell where in the talk they are | The part name *is* the heading, at 34pt |
| **A table of phrases**: options across, aspects down, a phrase in every cell, often with a row like 「残る課題 ｜ — 」 | It looks rigorous and carries almost nothing; it is the signature of generated slides | A figure that shows the difference (bars of the one measure, two images), or two bullets |
| **A grid of names with dots at the crossings** — groups of people across, kinds of effect up, this work ringed in one cell | The same table of words, dressed as a chart: swap two rows and nothing changes, yet the grid promises a measurement | What actually differs, on a real axis (a time, an amount) or as two pictures; or two bullets (figures.md §7, F7) |
| **A position map on every prior-work slide**, dots placed by feel on two arrows with nothing else in it | A template; and a place that nobody can check is not evidence | Only when the position is the point (figures.md §7); then the evidence under each name and this work in a dashed ring |
| **Prior-work bullets that only say what the others achieved** (「深層学習は発見率95%を達成」) | The audience cannot tell what is wrong with prior work, even when the figure shows it | Each bullet ends on what that work falls short on, its strength only as the contrast in front (「発見率95%と高いが判断の根拠は不明」) |
| **A share whose whole is not named** — 「ランクⅢ・Ⅳ 38%」 on a bar labelled 「区分」, the rest of the bar grey and blank, a share of another whole stacked under it | 38% of what? The audience cannot read it, and the two bars read as one comparison | The whole in the title, every part named in plain words (`sk.shares`); different wholes in different charts |
| **Rows of "bold label + explanation"** (「線形回帰の理由：…」「深層学習との違い：…」) with hairlines between | A table in disguise; the slide is explaining itself | State the point, or say it aloud |
| **A grey sub-line under everything**: under each bullet, each box, each number | Sub-labels double the text and halve the hierarchy | One level. What the sub-line said is spoken |
| **A big number filling half the slide** when the value itself does not matter (「50ミリ秒」) | Size claims importance that is not there | The fact in a bullet: 「印象の形成は提示から約50ミリ秒」 |
| **Three statistics in a row** of different kinds (区間数・画像数・指標数) | Neighbours read as the same kind of thing | One bullet: 「120区間・約1万2千枚の路面画像」; the rest is not needed |
| **Exact digits nobody needs** (12,436枚), provenance details (who published the data, how many features a baseline had) | Noise | Round (約1万2千枚); drop the details into the notes |
| **A full-width tinted band** with left-aligned text at the bottom of every slide | Unequal space left and right inside the band; a ritual, not a conclusion | One bold centred line with no box, on the slides that need one |
| **A flow of four boxes** where some are data and some are actions, each with a sub-label, and a paragraph under each | Data appears to turn into an operation; the diagram is a list | Boxes are things, arrows are operations, no sub-labels; show the real input in the first box |
| **The purpose slide explains the method** | The audience still does not know what the aim is | The purpose, one line, framed |
| **The method on one slide** that turns out to describe only the dataset | The method cannot be seen | Several slides, each a step on a real example |
| **Text only**, slide after slide, though the material is full of images | Words do not reach an audience | A figure on every slide; the material's own pictures first |
| **A category name that also fits this work** (prior work called 「特徴量の回帰」 when this work is one too) | The comparison distinguishes nothing | Name things by what makes them different |
| **Bullets cut down to stubs** (「影響は未検証」「50ミリ秒で形成」) at the left margin, while the figure, the arrow or the frame is centred | The right half of the slide is empty and its weight is off centre | Fewer bullets, each a full line that carries a fact across the slide. Or one centred conclusion line; or the list beside the figure in a column |
| **A bullet list centred as a block** to balance the slide | It looks amateurish. A list belongs on the left edge | Flush left, and long enough to balance. Only a list inside a column — a sub-element — is centred in its column |
| **A flow whose boxes hold one word each** | Text with arrows: it says nothing a sentence would not, and leaves the slide empty | Follow one real case through the flow: the actual image, the actual numbers, the actual result in the boxes. Otherwise do not draw a flow |
| **Bullets under a flow that only name its boxes again** | The eye maps a vertical list onto a horizontal chain and learns nothing | The words add what the flow cannot show: the idea behind a step, the size of the data, the measure |
| **Tiny unlabelled charts or icons** dropped into boxes for atmosphere | Decoration | What is in a box is real data of the case being followed, legible, or nothing |
| **Rotated axis labels**; a legend far from the lines; examples in the opposite order to the lines they belong to | The audience tilts their heads and traces crossing paths | Horizontal labels; values at the line ends; paired things side by side in the same order |
| **A consequence line longer than the line it hangs from**; a caption wider than its picture | The part sticks out of the whole; the hierarchy blurs | A part stays inside what it belongs to |
| **A chart with nothing marked**: every bar grey, every line equally coloured, a message that names the topic but not the finding | The audience studies the chart to find what the speaker means | Mark it: the key words of the message in bold, the bars it is about in red, a direct label at the decisive place, or one ring (F5) |
| **Heading topics at different levels** (「結果 - 検出率と誤検出」「結果 - 処理時間」「結果 - 夜間と雨天の画像」) | The outline of the talk is lost; one topic is far more specific than its siblings | Name each topic by the kind of question it answers, at one level: 精度 / 速度 / 頑健性 |
| **The gallery's figures with new labels** — a position map on the prior-work slide, a four-box flow for every method | It looks like a template because it is one | Choose each figure from what this material shows (SKILL.md rule 21) |
| **A message with no subject or no second term** (「雨天では逆に低下」) | What changed, compared with what? | 「雨天では検出率が晴天より低下」 |
| **Parentheses on every line**; a gloss in brackets after the noun (「点検員が判定（経験5年以上・研修修了）」) | Reads as translated from English; each line has two voices | The qualifier in front of the noun, as one block: 「研修を修了した経験5年以上の点検員が判定」 |
| **A line that stops on 〜ず** (「処理時間は変わらず」) | It hangs, as if a clause were missing | 「処理時間は変わらない」, or a noun ending |
| **Schematic axes with 低 / 高 ticks**; three outcomes on one axis; an axis line running on under the labels; an axis set to a total far past the data | Ticks pretend to be values; three curves read as one; the axis sticks out; the chart is half empty | Name the quantity and drop the ticks; one outcome per panel; the line ends with the scale; the axis ends just past the data (rule 22, F6) |
| **People drawn as labelled circles** in a diagram of the setting | A symbol to decode | People as people (`sk.person`), things with a shape as that shape (`sk.icon`) |
| **A makeshift drawing** — a balloon or a blob standing for a hand, a phone, a device | It reads as something else; it looks forced | An icon from the bundled sets, or icons composed; otherwise another figure |
| **Things facing the wrong way** — a camera turned away from the person it records | The scene stops making sense | Each thing faces the way it acts (`flip=True`) |
| **A figure added to fill space** — a rating scale drawn out beside a chart, a picture of a word | Filler, and it shows | Enlarge the figure that matters, or give the words the width |
| **The same panel three times** for outcomes predicted to behave alike | Clumsy; the eye compares three identical things | The shape once, and the outcomes it stands for named once |
| **A caption about what is missing** (「エラーバーは省略」) | Noise; nobody misses what is not there | Leave it out; the notes can say it |
| **Bullets broken early into two equal lines** | The right side of the slide is empty | A bullet that fits stays on one line; a long one breaks near the end of the line |
| **Every 「、」 removed** from long bullets and the purpose | A long line cannot be read in one go | A 「、」 after a long opening phrase, between a subject and a far predicate (the message keeps none) |
| **A verb cut to its stem** (「光り見落とし」「濡れ滑る」) | Reads clipped, like a headline in translation | 「光って見落とし」「濡れて滑る」 |
| **Red on something that is not red** (sweat, a device) | The colour of emphasis turns into the colour of the thing | Colour marks by what they depict; red points |
| **An axis named by a placeholder** (「各指標の予測値」) or a bare noun (「不安」) | Nobody knows what goes up | The quantity in plain words, 「〜の高さ」; an arrowhead on an axis without values |
| **「→仮説1を支持」** | The audience has to remember what hypothesis 1 was | The fact read off the chart → the hypothesis in words：**仮説1**の支持 |
| **A thin appendix** | The questions the talk invites have nowhere to go | Originals of redrawn figures, full tables, omitted analyses, one slide per likely question |
| Lines that run to the edge and drop one word | Careless | Break at the phrase boundary; similar line lengths |
| Gradients, rounded cards, drop shadows, icons, emoji, a coloured bar down the left edge of a box | Decoration | None of it exists in the theme |
| Bold on half the text; three accent colours | Nothing stands out | Bold for one or two keywords; blue, grey, and red once |
| Section-divider slides, an agenda, 「ご清聴ありがとうございました」 | Slides with nothing to show | The large heading does this job |

## 4. Canvas and anatomy

The canvas is PowerPoint's: 4:3 = 960 × 720 px (10 × 7.5 in), 16:9 = 1280 × 720 px. 1 pt is
1 pt in PowerPoint.

```
30 ─┬─ heading (34pt, light, accent)            margins: 56 px left/right at 4:3, 72 px at 16:9
97 ─┴━ rule (3 px, accent)
113 ── message (22pt)
168 ─┬
     │  body: 506 px — figure first, words below
674 ─┴
692 ── footer: date (left) · page number (right), 12pt grey
```

The heading and its rule sit at the same height on every slide, with or without a message. The
footer never changes. This fixed frame is what lets the body vary — an image pair here, a chart
there — and still read as one deck.

## 5. Type

One family: Noto Sans JP, in three weights — Light for the heading and the cover title, Regular
for text, Bold for emphasis.

| Token | pt | Used for |
|---|---|---|
| head | 34 | slide heading (Light) |
| cover | 30 | cover title (Light) |
| large | 24 | summary bullets; the value under a sample image |
| msg | 22 | the message; the conclusion line; a boxed statement; display math |
| body | 20 | bullets |
| sub | 17 | chart labels and values, table cells, labels in diagrams |
| small | 14 | captions, chart titles, axis text, notes |
| tiny | 12 | sources, citation marks, footer |

- These are the only sizes. There is no way to set another, and no reason: when text does not
  fit, there is too much text.
- The heading is large and light: size gives it rank, the light weight keeps it from shouting.
- 14 pt is the smallest size for anything the audience must read; 12 pt is for sources, citation
  marks and the footer.
- No italics for Japanese (the font has none), no underline, no letter-spacing tricks, no
  all-caps labels.

## 6. Colour

| Colour | Token | Meaning |
|---|---|---|
| dark blue `#1f3f6b` | accent | the heading, the rule, the frame; **the subject** in a chart (this work) |
| light blue `#7fa7d1` | accent-2 | a variant of the subject (a second bar of the same kind) |
| blue text `#2a62a8` | accent-text | a second voice in text (future work in the summary) |
| grey `#a9b0b8` | mute | everything shown only for comparison |
| red `#c8372d` | hot | **the one thing to look at**: the bars the slide is about, one phrase |
| near-black `#1a2330`, greys | ink | text, axes |
| pale fills | tint, accent-tint | boxes in a flow |

- A chart has one coloured thing. Everything else is grey. If two things are coloured, the
  audience does not know where to look.
- Red is rare: the bars the message is about (`hot=`), or one phrase in a bullet (`!!…!!`) that
  doubles as the legend for those bars. Not both on every slide.
- The same thing keeps its colour through the deck (this work is always dark blue).
- Colour is never decoration: no coloured backgrounds, no coloured section bands, no alternating
  hues for variety.
- A deck may replace the accent pair (`Deck(accent=(…))`) — a university colour, say — and
  nothing else.

## 7. Layout: the path of the eye and the centre of gravity

A slide is looked at before it is read. Two things decide whether that look is comfortable:
**where the eye is led** (視線誘導) and **where the weight sits** (重心). Neither is a property of
a component; both are properties of the whole slide, and a slide made of correct components can
still get them wrong.

### What is centred, and what is flush left

- **Text is flush left** on the edge of the heading (左端を基本揃える): the message, every list.
- **Independent objects are centred** (中央揃えは独立したテキストボックス要素のみ): a figure, an
  equation, the conclusion line, the frame, the arrow between premises and frame.
- **A list is not centred as a block.** Centring a bullet list to fill a hole looks amateurish.
  The exceptions are lists that belong to a centred composition: a list inside a column of
  `cols()`, beside a figure, is centred within its column; and the premises of the purpose slide
  (`therefore`) are centred as a block over the centred arrow and frame. The rule of
  thumb: text that runs to the right edge is fine flush left; where it stops short beside
  centred things, a little centring is better than an empty right side.

### A list carries its width

Text on the left and objects in the middle balance only if the text reaches across the slide.
This is the point at which writing becomes layout:

```
×  目的                                      ○  目的
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━             ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   • 見落としが多い                              • 幅1mm未満のひび割れは目視点検でも3割以上を見落とし
   • 費用が高い                                  • 車載レーザー計測は1台約1億円で市町村には導入困難
                                                • スマートフォン画像の手法は細いひび割れの精度が未検証
               ▼                                               ▼
      ┌──────────────────┐                         ┌──────────────────────────────────┐
      │  自動で検出       │                         │ 安価な画像で細いひび割れまで自動検出 │
      └──────────────────┘                         └──────────────────────────────────┘
   stubs at the left, arrow and frame           full lines span the slide; the centred
   in the middle: the right half is             arrow and frame sit under their middle
   empty and the slide tips over
```

- **A bullet is one full line**: a fact with its number, its condition, its source, the object of
  its verb. Not a keyword. The longest line of a list reaches at least 70% of the way across a
  4:3 slide (65% at 16:9) — about 21 characters or more at 4:3 — and the other lines are of
  similar length.
- **Fuller is not wordier.** Fill a line with information. 「非常に」「さまざまな」「〜することが
  できる」 add length and nothing else; a number, a citation, a named condition add both.
- **Few lines, not thin lines.** Three full bullets beat five stubs. Two short bullets can often
  be one full one (「120区間・約1万2千枚の路面画像で幅ごとの発見率を評価」).
- **When there is too little to say for a full line**, a list is the wrong form. Use one centred
  conclusion line (`sk.conclusion`), which is an independent object; or put the list beside the
  figure in a column; or let the figure stand alone.
- This is still not prose: noun-ending, no 「、」-joined clauses, no です・ます, three bullets at
  most beside a figure. The earlier failure (a slide that explains everything) and this one
  (stubs) are the two sides; the target is between them — a handful of complete, dense lines.

The linter measures it (L6): how far a list reaches across the slide; whether a figure is off
the centre line; and the centre of gravity of the whole body (`cx` in `--metrics`).

### Centre of gravity

- **Horizontally** the weight rests near the centre line: centred figures, and lists long enough
  not to pull it left. In two columns, the two sides should weigh about the same: a large plot
  beside two small images is left-heavy; give the lighter side more.
- **Vertically** the blocks are spread evenly between the message and the footer; nothing hugs
  the top with the bottom third empty. If a slide looks empty, it was given too little to show:
  enlarge the figure, or merge the slide into a neighbour.
- **Inside a block** the shape should be stable: lines of similar length (section 8), never one
  long line over a stub.
- **A diagram fills its place.** A flow or a map that is a thin strip in a tall slide, with
  margins above and below, is unbalanced however tidy it is. Give its boxes real content so that
  it has height, or choose a figure that suits the space.
- **The figure is the heavy thing.** Half of the body area or more. If the words need more room
  than the figure, the slide is a document.

### One direction

The eye should not have to change direction more than once, and never to go back.

- The stack is read **top to bottom**: heading → message → figure → words. Text that comments on
  a figure goes under it, not above (the message is the one line read first).
- In a stack of horizontal text, **sideways arrows are held back** (縦積み横書きなら横矢印は抑える).
  A flow is the one figure that runs left to right; when a slide has one, nothing else on that
  slide points sideways. The words under it add what the flow cannot show — the idea behind a
  step, the size of the data, the measure — rather than naming its boxes a second time.
- The arrow of a consequence in a bullet (「→大規模データで未検証」) starts a new line and points
  to that line's own text; it does not send the eye across the slide.
- **No rotated text.** Axis names are horizontal: the y axis is named above its top end
  (`sk.ylabel_top`; `sk.posmap` does it by itself). Nobody should tilt their head.

### Paired things: adjacent, same order, same colour

When two parts of a slide refer to each other, the eye travels between them. Keep the trip short
and never let two trips cross.

- A value sits directly under the image it was read from.
- Lines in a plot are named **at their ends**, not in a legend elsewhere.
- Examples beside a plot are stacked **in the same order as the line ends they belong to** (the
  upper line's example on top) and their values take the lines' colours.
- A red phrase in a bullet names what is red in the chart above it.
- Bars and their labels are in one row; a table's highlighted row is the one the message is about.

### Containment (階層構造)

A part stays inside the extent of what it belongs to (自分を包含するコンテンツからはみ出さない):

- a value and its note are no wider than the image above them; a caption is no wider than its
  figure; a chart's title sits over the chart;
- the consequence line of a bullet (→) is no longer than the line it follows;
- a label fits inside its box, a column's content inside its column;
- an axis line ends where its scale ends, not under the labels written past the data;
- everything is inside the extent of the heading rule.

When a part sticks out, the hierarchy stops being visible. Shorten the part (lint H1, O3).

### Columns

Columns are for two figures that are read together: two charts, a plot with the cases behind it,
an image beside the bars computed from it. Each column's content is centred in its column. Do not
use columns to put a paragraph beside a figure — the default is one stack.

## 8. Line breaks

Japanese text has no spaces, so a careless break lands in the middle of a phrase or strands one
word. **No text on a slide is wrapped automatically: you place every break**, with `\n`. Two
rules:

1. **Break where the meaning turns.**
2. **The length of the lines depends on what the text stands against.** Text set against
   something else — a caption under its picture, the framed statement, the centred conclusion, the
   cover title, a label, a list inside a column — gets lines of similar length, even if the first
   stops short of the edge: a narrower, balanced block sits on its figure or frame. A list on its
   own is different: a bullet that fits on one line stays on one line, and one that does not
   breaks near the end of the line, so the first line is long. An early, balanced break there
   only empties the right side of the slide (lint T10).

```
× 雨天の画像では細いひび割れの発見率が低     ○ 雨天の画像では
  下                                           細いひび割れの発見率が低下
```

- A bullet is written to fill one line (section 7), and stays on one line. One that runs over is
  trimmed to fit; only if it cannot be is it broken — near the end of the line. The library
  refuses a line that is too long and tells you so.
- The message is one line. The conclusion and the framed statement are broken only by your `\n`.
- A consequence gets its own line with an arrow — a designed break:
  `"細いひび割れをどこまで画像で拾えるか\n→実際の路面では未検証"`.
- Never leave a single character, a particle, a unit or a citation mark alone on a line.
- Prefer rewording to a third line. A bullet of three lines is a paragraph.

## 9. Emphasis

- **Bold** by design, and only for the gist and for key words (太字はキーワード・趣旨・サブタイトル
  以上のみ): the conclusion line, the framed statement, values under images, the highlighted bars,
  the one box of a flow that the talk is about. Ordinary labels in a diagram are regular weight. In
  bullets, `**…**` on a few keywords per slide — on a result slide the measures the chart is about
  and the hypothesis label — never a whole bullet, never every bullet. In
  the message, the words that carry the finding, once (「**幅1mm未満**のひび割れも9割を検出」). A
  label in front of an item that is referred to later (**[仮説1]**) is bold.
- **Pointing inside a figure**: the bars or the line it is about in red, the decisive value
  labelled directly (bold, red), and — only when these do not lead the eye there — one ring. It is
  drawn into the figure, static; nothing is circled during the talk.
- **Red** (`!!…!!`): one phrase per slide at most.
- **Size**: only through the components (large bullets on the summary, the value under an image).
- Position is emphasis too: what matters most is the figure, in the middle.
- No underline, no italics, no highlighter backgrounds, no ALL CAPS, no exclamation marks.

## 10. Boxes, lines and other furniture

- **The rule under the heading** is the only line on a slide besides chart axes.
- **A frame** (`boxed`) holds one statement, hugs its text with equal padding on both sides, and
  is centred. Once per deck: the purpose.
- **No band, card or panel.** A tinted full-width strip with text at its left end has unequal
  margins and reads as a template. The conclusion of a slide is bold centred text with no
  container.
- **Flow boxes** are pale fills without borders; they mark things, not emphasis.
- **Arrows** mean one thing per figure: an operation in a flow, a consequence in the purpose
  slide (the thick down arrow), "therefore" in a bullet (→). Do not use arrows as bullets or
  decoration.
- **Screenshots** get a hairline (`shot=True`) so a white edge is visible. No shadows, no device
  frames.
- Square corners, flat fills, no shadows, no gradients — the linter rejects the rest.

## 11. Numbers

- A number appears at the size its importance earns. The value under a sample image is large
  because the image is the evidence and the value is what it shows. A fact in passing
  (50ミリ秒, 約1万2千枚) is ordinary text in a bullet.
- Round to what the audience needs: 約1万2千, 91%, 0.77. Keep the digits that are compared.
- One quantity in one unit (「300秒」, not 「5分間（300秒）」). Name the aggregate where it is one
  (「時間の平均（秒）」).
- Use symbols when they are shorter and familiar: `$R^2=0.203$`, `$r=0.773$`.
- A number comes with its comparison — as a second bar or a second image, which is why results
  are charts and not statistics.
- Do not line up numbers of different kinds (a count, a rating, a correlation). One chart or one
  row of images holds one kind.
- A percentage shows its whole: what 100% is (the title) and what the part is (its name), in words
  the audience knows. Shares of different wholes are not rows of one chart.
- A place on a chart is a value: an axis is an amount or the ordered steps of one, never a list of
  kinds.
- Units in chart titles (「幅ごとの発見率（%）」) and after values under images (「12.6%」).
- Every number is in `numbers.md` (Phase 3) and is verified (Phase 7).

## 12. Consistency across the deck

- Same anatomy on every content slide; the frame never moves.
- Same thing, same name, same colour.
- Same kind of content, same pattern (two "example of an indicator" slides look alike).
- The appendix uses the same anatomy; only tables of numbers are added.
- Variety comes from the figures, not from layouts.

## 13. Questions to ask of every slide

1. If I cover the words, does the figure still make the point? (If not, the figure is weak.)
2. If I cover the figure, do the words still make the point? (If so, the figure is decoration —
   or the words are too many.)
3. Can the message be read in one glance? Does it say something?
4. Is there anything on the slide I would not point at or mention while talking? Remove it.
5. Is there a sentence here that I am going to say anyway? Move it to the notes.
6. Is there a small grey line that only repeats or glosses something? Remove it.
7. Would a table of numbers, a list of labels with explanations, or a row of statistics have
   crept in under another name?
8. Does anything look generated — a tidy symmetry of three boxes, a label on everything, a
   closing band? Would a person drawing this by hand have bothered?
9. Squint at the thumbnail. Does the weight sit near the centre line, or is one half empty? Do
   the bullets reach across the slide, or do stubs at the left leave the right side blank?
10. Trace the path of the eye with a finger: does it go down once, without turning back, without
    two paths crossing, without a label read sideways?
11. Does any part stick out of what it belongs to — a caption wider than its picture, a
    consequence longer than its premise?
12. Does every diagram show something — real images, real numbers — or is it words in boxes?
    Does it fill its place, or is it a thin strip with empty margins around it?
13. What does each chart say — and where on the slide is that said or marked? Could someone who
    sees only the slide point at the place in two seconds?
14. Read the headings of one part together: are the topics at one level?
15. Is any figure on this slide because the gallery has one for this part of the talk — or
    because there was space to fill?
16. Read the message alone: does it have a subject, and does every comparison name both sides?
17. Does every drawn thing look like what it is, and face the way it acts?
18. Does every place on a chart mean a value? If a dot could move to another row without changing
    the meaning, the chart is a table of words.
19. Can every percentage be read alone — 100% of what, and which part?
