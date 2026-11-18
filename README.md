# make-slides

資料と発表時間を渡すだけで、正式な場でそのまま使える整ったスライドをベクター PDF で作る skill です。
学会発表・中間発表・ゼミ・進捗報告・業務の説明を想定し、日本語のスライドを主な対象にしています。英語のスライドも作れます。
AIの用いるSlopな図、意味のないグラフ化やテキストだけの表などを抑え、直感的に伝えやすいスライドを生成します。

![同梱の見本の一覧](docs/gallery-1.png)

*同梱の見本の一部。題材・数値・画像はすべて架空です。*

プロンプトの例です。

```
progress/ をもとに、研究室のゼミで10分の発表スライドを作って。
聞き手は同じ研究室の学生で、手法の基礎は知っている。自分の研究として発表する。
```

## 特徴

### スライドの見た目

スライドスタイルはある程度調整していますが、以下が特徴として如実に顕れますので気に入らない箇所は個別で修正してください。

- 本編は1分に約1枚の少なめの枚数
- 区分名の大きな見出しと、読点のない短い一言
- どのスライドにも大きな図、箇条書きは3項目まで
- 話す内容はスライドに書かず発表者メモへ
- 文字だけの表・「ラベル：説明」の行・カードは使わない
- 箇条書きは左端にそろえ、1項目1行で言い切る
- 色は濃紺が主題、灰色が比較、赤は見てほしい1か所
- グラフは見る場所を赤と値で示し、名前を並べただけの軸は使わない
- 論文の図には赤い楕円と、読み方の1〜2行を添える
- 割合には分母を書き、大事でない数値は丸めて小さく
- 手法は変えた部分ごとに、実物の画像と値で見せる
- アニメーションも飾りのアイコンも使わない

### 仕組み

- 文字の大きさ・色・余白は固定のテーマで決まり、見た目はデッキごとにぶれません。
  スライドは Python の小さなライブラリ（slidekit）で書き、HTML を経て、
  インストール済みの Chrome / Edge でベクター PDF にします。
- 描画した結果をブラウザで測る linter が、文字だけのスライド、小さすぎる図、
  どこを見ればよいか分からないグラフ、短すぎて片側が空く箇条書き、はみ出しなど、
  機械的なスライドの癖を指摘します。
- スライドに載ったすべての数値を一覧にし、資料と照合してから報告します。
- 引用する文献は資料から写し、記憶では書きません。資料に見つからない文献は、
  参考文献のスライドに赤字の「出典未確認」として残し、作成時と検査で警告して、報告の最初に挙げます。
- 論文の図の余白からパネルを見つけて番号を付け、必要なパネルだけを切り出す道具（`figpanels.py`）が付いています。
  どのパネルを使うかは AI が図を見て決めます。

## 環境

| 環境 | 用途 |
|---|---|
| Node.js 18 以上 | 検査・PDF 作成のスクリプト |
| Python 3.9 以上 | スライドの元（`deck.py`）を実行 |
| Google Chrome または Microsoft Edge | PDF の書き出し（インストール済みのものを使い、ブラウザはダウンロードしません） |
| matplotlib・fonttools・brotli（任意） | グラフを描くとき |
| Pillow（任意） | 資料の画像を切り出すとき |

## インストール

Agent Skills の形式で書いた skill で、シェルを実行でき画像を読める AI エージェントで使えます。
動作確認は Claude Code で行っています。

### 1. skill を入れる

GitHub CLI 2.90 以降なら、エージェントを指定して入れます。

```
gh skill install N-Kos-mk/make-slides make-slides --agent <エージェント>
```

`<エージェント>` には `claude-code`・`codex`・`cursor`・`gemini-cli`・`github-copilot` などを指定します。
すべてのプロジェクトで使うなら `--scope user` を付けます。

手で入れるなら、clone して `skills/make-slides` をエージェントの skill フォルダにコピーします。
Claude Code の skill フォルダは `~/.claude/skills/` です。

```
git clone https://github.com/N-Kos-mk/make-slides.git
```

### 2. 依存パッケージを入れる

`<skill>` は `SKILL.md` のあるフォルダです。`doctor.mjs` が足りないものと入れ方を示します。

```
npm install --prefix <skill>/scripts
python -m pip install matplotlib fonttools brotli pillow
node <skill>/scripts/doctor.mjs
```

### Claude Code の plugin として入れる

Claude Code 2.1.275 以降では plugin としても入れられます。npm の依存は自動で入るので、`pip install` だけを実行します。

```
/plugin install make-slides --marketplace N-Kos-mk/make-slides
```

## 更新

- GitHub CLI: `gh skill update` のあと `npm install` をやり直す
- 手でコピー: `git pull` してコピーし直す。上書きなら `scripts/node_modules` は残る
- Claude Code の plugin: `claude plugin update make-slides@nkos`

作成済みのデッキは「新しい版に合わせて」と頼めば更新されます。変更点は [CHANGELOG.md](CHANGELOG.md) にあります。

## 使い方

資料と発表時間を渡して頼むだけです。直すときはページと問題を書きます。

```
main.tex と results/ をもとに、10分の中間発表のスライドを作って（4:3）
```

```
この論文を研究室のゼミで5分で紹介するスライドにして
```

```
p.6 が文字だらけと言われたので、内容は変えずに直して
```

既定は、質疑のある正式な発表、同じ分野だがこの話題を知らない聞き手、16:9 です。
違うときは、場面・聞き手・発表者の立場・比率・文献の場所を書き足します。

冒頭の例に、比率と文献の場所を書き足すと次のようになります。

```
progress/ をもとに、研究室のゼミで10分の発表スライドを作って。
聞き手は同じ研究室の学生で、手法の基礎は知っている。自分の研究として発表する。4:3。
文献の情報は progress/refs.bib にある。
```

作業は、資料を読む → 構成 → 図 → `deck.py` → 検査 → PDF → 数値の照合と報告、の順に進みます。
できるものは次のとおりです。

```
<deck-dir>/
├── deck.py         スライドの元。直すのはこのファイル
├── outline.md      構成
├── numbers.md      スライドの数値と出典
├── figures/        切り出した画像と生成した図
└── out/
    ├── <名前>.pdf   完成した PDF
    ├── notes.md     発表者メモ
    └── sheet-1.png  全スライドの一覧
```

## 中身

```
.claude-plugin/       Claude Code の plugin と marketplace の定義
package.json          plugin で入れたときの npm の依存。scripts/ の写し
package-lock.json
skills/make-slides/
├── SKILL.md          手順と規則
├── references/       構成・図・デザイン・部品・検査・報告の詳細
├── scripts/          doctor・init・lint・build・icons・figpanels
└── assets/
    ├── slidekit.py   スライドを書くライブラリ
    ├── theme/        CSS・フォント・KaTeX
    ├── template/     deck.py の雛形
    └── gallery/      全パターンの見本
evals/                skill の評価用の依頼例
```

## 制約

- 出力は PDF と PNG だけで、編集できる .pptx などは作らない
- テーマは1種類で、変えられるのはアクセントの色だけ

## ライセンス

[MIT License](LICENSE)。同梱のフォント・KaTeX・アイコンのライセンスは [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) にあります。

---

## English

make-slides is a skill in the Agent Skills format. It turns source material and a talk length into a
vector-PDF deck for formal talks, mainly in Japanese, and avoids the habits of machine-made slides:
decorative figures, charts that measure nothing, tables of words.

Requirements: Node.js 18+, Python 3.9+, an installed Chrome or Edge, and an AI agent that runs shell
commands. matplotlib, fonttools, brotli and Pillow are optional.

Install: `gh skill install N-Kos-mk/make-slides make-slides --agent <agent>`, or copy
`skills/make-slides` into the agent's skills folder. Then run `npm install --prefix <skill>/scripts`
and `node <skill>/scripts/doctor.mjs`. In Claude Code:
`/plugin install make-slides --marketplace N-Kos-mk/make-slides`.

Update: `gh skill update`, `git pull` and copy again, or `claude plugin update make-slides@nkos`.

License: MIT. Bundled fonts, KaTeX and icons: see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
