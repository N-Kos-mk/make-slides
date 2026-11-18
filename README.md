# make-slides

資料と発表時間を渡すだけで、正式な場でそのまま使える整ったスライド（ベクター PDF）を作る
[Claude Code](https://code.claude.com/docs) の skill です。学会発表・中間発表・ゼミ・進捗報告・業務の説明を想定し、
日本語のスライドを主な対象にしています（英語のスライドも作れます）。

![同梱の見本（gallery）の一覧](docs/gallery-1.png)

*同梱の見本（gallery）の一部。題材・数値・画像はすべて架空です。*

## 特徴

- **図が主役で、文字は最小限**: どのスライドも「見出し（区分名）→ 一言 → 図 → 少しの文字」の形で作り、
  話す内容は発表者メモに分けます。資料の中の画像やデータを、そのまま図として使います。
- **見た目が毎回同じ**: スライドは Python の小さなライブラリ（slidekit）で書き、HTML を経て、
  インストール済みの Chrome / Edge でベクター PDF にします。文字の大きさ・色・余白は固定のテーマで決まり、
  デッキごとにぶれません。
- **機械的なスライドの癖を検査**: 描画した結果をブラウザで測る linter が、文字だけのスライド、小さすぎる図、
  どこを見ればよいか分からないグラフ、短すぎて片側が空く箇条書き、はみ出しなどを指摘します。
- **数値の照合**: スライドに載ったすべての数値を一覧にし、資料と照合してから報告します。
- **参考文献は資料から**: 引用する文献は資料から写し、記憶では書きません。資料に見つからない文献は、参考文献の
  スライドに赤字の「出典未確認」として残し、作成時と検査で警告して、報告の最初に挙げます。
- **論文の図の切り出し**: 図の余白からパネルを見つけて番号を付け、必要なパネルだけを切り出す道具
  （`figpanels.py`）が付いています。どのパネルを使うかは Claude が図を見て決めます。

## 必要なもの

| もの | 用途 |
|---|---|
| Claude Code | skill を実行する環境 |
| Node.js 18 以上 | 検査・PDF 作成のスクリプト |
| Python 3.9 以上 | スライドの元（`deck.py`）を実行 |
| Google Chrome または Microsoft Edge | PDF の書き出し（インストール済みのものを使い、ブラウザはダウンロードしません） |
| matplotlib・fonttools・brotli（任意） | グラフを描くとき |
| Pillow（任意） | 資料の画像を切り出すとき |

## インストール

1. このリポジトリを clone します。

   ```
   git clone https://github.com/N-Kos-mk/make-slides.git
   ```

2. `skills/make-slides` フォルダを、skill の置き場所にコピーします。

   | 使う範囲 | コピー先 |
   |---|---|
   | すべてのプロジェクト | `~/.claude/skills/make-slides`（Windows では `%USERPROFILE%\.claude\skills\make-slides`） |
   | 1つのプロジェクトだけ | そのプロジェクトの `.claude/skills/make-slides` |

3. 依存パッケージを入れ、環境を確かめます（初回だけ）。

   ```
   npm install --prefix ~/.claude/skills/make-slides/scripts
   python -m pip install matplotlib fonttools brotli pillow
   node ~/.claude/skills/make-slides/scripts/doctor.mjs
   ```

   `npm install` で入るのは、ブラウザを操作する playwright-core と、図に使うアイコン集です。
   `doctor.mjs` は足りないものと、それを入れるコマンドを表示します。

**インストールせずに試す**: clone したフォルダを plugin として読み込めます。この場合の skill 名は
`/make-slides:make-slides` です。

```
claude --plugin-dir ./make-slides
```

## 更新

clone したフォルダで最新版を取得し、`skills/make-slides` をコピーし直します。`npm install` で入れたパッケージは
`scripts/node_modules` にあるので、コピー先のフォルダを丸ごと消さずに上書きすれば入れ直す必要はありません。

```
git pull
```

変更点は [CHANGELOG.md](CHANGELOG.md) にあります。作成済みのデッキに新しい版のライブラリとテーマを反映するには、
デッキのフォルダに対して `node ~/.claude/skills/make-slides/scripts/init.mjs <deck-dir> --refresh` を実行します。

## 使い方

Claude Code で、資料と発表時間を渡して頼むだけです。

```
main.tex と results/ をもとに、10分の中間発表のスライドを作って（4:3）
```

```
この論文を研究室のゼミで5分で紹介するスライドにして
```

```
p.6 が文字だらけと言われたので、内容は変えずに直して
```

Claude は、資料を読む → 構成を立てる → 図を用意する → `deck.py` を書く → 検査が通るまで直す →
PDF を作って目で確かめる → 数値を照合して報告する、の順に進めます。

デッキのフォルダには次のものができます。

```
<deck-dir>/
├── deck.py         スライドの元（修正はこのファイルに対して行います）
├── outline.md      構成（聞き手、1枚ごとの見出し・一言・図・秒数）
├── numbers.md      数値台帳（スライドに載せる数値と出典）
├── figures/        資料から切り出した画像と、生成した図
└── out/
    ├── <名前>.pdf   完成した PDF
    ├── notes.md     発表者メモ
    └── sheet-1.png  全スライドの一覧画像
```

## 中身

```
skills/make-slides/
├── SKILL.md          手順と規則（Claude が最初に読む）
├── references/       話の組み立て・図・デザイン・部品・検査規則・確認と報告
├── scripts/          doctor / init / lint / build / icons（Node.js）、figpanels（Python、図の切り出し）
└── assets/
    ├── slidekit.py   スライドを書くためのライブラリ
    ├── theme/        CSS・フォント・KaTeX
    ├── template/     deck.py の雛形
    └── gallery/      すべての型の見本（deck.py と PDF）
evals/                skill を評価するための依頼の例
```

## 制約

- 出力は PDF と PNG です。編集できる .pptx・Keynote・Google スライドは作りません。
- テーマは1種類（白地・濃紺・強調の赤）です。変えられるのはアクセントの色だけです。
- アニメーションは使いません。
- 規則と例は日本語のスライドを中心に作っています。

## ライセンス

[MIT License](LICENSE)。同梱のフォント・KaTeX・アイコンは、それぞれのライセンスに従います
（[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)）。

---

## English

make-slides is a Claude Code skill that turns source material and a talk length into a
presentation-ready deck, delivered as a vector PDF. It is written for Japanese talks — conference
and thesis presentations, seminars, progress reports, business briefings — and works for English
decks too.

Each slide follows one shape: the part of the talk as a large heading, one short claim, a figure
that does the work, and a few lines of text; everything the speaker says goes to the notes. The
deck is a short Python script against a bundled library; the library writes HTML under a fixed
theme, a browser-based linter measures the rendered slides, and an installed Chrome or Edge prints
the PDF.

**Requirements**: Claude Code, Node.js 18+, Python 3.9+, Google Chrome or Microsoft Edge;
matplotlib, fonttools, brotli and Pillow for plots and images.

**Install**: clone this repository, copy `skills/make-slides` to `~/.claude/skills/make-slides`
(or to a project's `.claude/skills/`), then run
`npm install --prefix ~/.claude/skills/make-slides/scripts` and
`node ~/.claude/skills/make-slides/scripts/doctor.mjs`. To try it without installing:
`claude --plugin-dir ./make-slides`. To update: `git pull` in the clone, copy `skills/make-slides`
over the installed folder again, and see [CHANGELOG.md](CHANGELOG.md).

**License**: MIT. Bundled fonts, KaTeX and icons keep their own licences
([THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
