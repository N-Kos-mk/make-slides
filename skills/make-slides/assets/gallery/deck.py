"""Pattern gallery — every slide pattern of the make-slides theme, as working code.

Each slide demonstrates one pattern from references/layouts.md (A–O). The slides are taken from
three invented talks so that no single study looks like "the" template:

    a business briefing   問い合わせ窓口のチャット導入        (E, J, C, O)
    an experiment         講義動画の倍速視聴と理解度          (N, M)
    a research talk       路面画像からのひび割れ検出          (A, C, F, D, G, I, B, H, K, L)

Copy the CALL you need into your own deck.py and replace the content. Never reuse the content,
and never take the choice of figure from here: a prior-work slide is not automatically anything.

Rendered result: out/gallery.pdf (build with  node ../../scripts/build.mjs . ).
The stand-in images in figures/ are drawn by make_figures.py; a real deck uses the material's
own images instead. All topics, numbers and images are invented.

This file lives inside the skill, so it imports the skill's own slidekit.py from the parent
directory. A real deck has its own copy next to deck.py and needs only `import slidekit as sk`.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import slidekit as sk  # noqa: E402

deck = sk.Deck(title="スライドの型の見本", minutes=12, ratio="16:9", date="2026/11/18")


RANKS = [1.45, 1.12, 0.86, 0.61, 0.40]          # priority of the five worst sections (invented)


def rank_bars(w=120, h=100):
    """The ranking as a tiny chart for a flow box — the same data as a later slide, shapes only."""
    step, top = h / len(RANKS), RANKS[0]
    rects = [f'<rect class="{"f-hot" if i == 0 else "f-mute"}" x="0" y="{i * step:.1f}" '
             f'width="{v / top * w:.1f}" height="{step * 0.64:.1f}"/>' for i, v in enumerate(RANKS)]
    return sk.svg("\n".join(rects), w, h, label="区間ごとの優先度")


# ===== cover =================================================================================
deck.cover(
    "スライドの型の見本",
    event="make-slides 同梱資料（題材・数値・画像はすべて架空）",
    sub="型ごとに別の架空の発表から例を取っている",
    lines=["所属名", "氏名", "2026年11月18日"],
    sec=15,
)

# =============================================================================================
# A business briefing: 問い合わせ窓口のチャット導入
# =============================================================================================

# ===== E — position map ======================================================================
# Rarely the right figure, and only after asking whether the slide needs it. Here the whole
# decision IS a position: the two options on the table each give up one of two amounts the
# listeners weigh (cost, and how many questions get answered), and the proposal holds both. The
# evidence for each place is of a different kind (a yearly cost, a number of questions), so the
# points cannot share a scale: a map placed by judgement, the evidence under each name, the
# proposal in a dashed ring. A prior-work slide is NOT automatically a position map; most talks
# have none.
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
    notes="""
    型E。めったに使わない。この発表では「どちらを取っても何かを諦める」という選択そのものが論点なので、位置で見せる。
    使う前に、2行の箇条書きで同じ速さで伝わらないかを考える。伝わるなら図にしない。
    軸は聞き手が実際に比べる2つの量（費用、答えられる質問の幅）で、どちらも多い・少ないがある。種類の名前を軸にしない。
    各点の名前の下に、その選択肢が弱い側の根拠（年約1,200万円、約40問だけ）を書く。位置の理由がその場で読める。提案は破線の円だけで示す。
    箇条書きは、ほかの選択肢それぞれの何が足りないかを言う。長所は「〜だが」の前置きにとどめる。図と同じ数値が出てもよい。
    """,
)

# ===== J — single image ======================================================================
deck.slide(
    "提案 - 画面",
    "よくある質問に**自動で回答**",
    sk.fig("figures/chat_screen.png", fill=True, shot=True),
    sk.conclusion("回答できない質問はその場で担当者に引き継ぎ"),
    sec=40,
    notes="""
    型J。画面や写真1枚。fill=True で残りの高さいっぱいに広がる。白い縁のある画像は shot=True。
    書くことが短い1つだけのときは箇条書きにしない（左に短い1行を置くと右が空く）。中央の1行（conclusion）にする。
    """,
)

# ===== C — vertical bars; two kinds of value side by side ===================================
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
    notes="""
    型C。1つのグラフには1種類の数値だけ。種類が違えばグラフを分けて、それぞれに題を付ける。
    値は棒の上に書く。導入後（主題）は濃紺、比較対象は灰色。濃紺が「どこを見るか」の印になる。
    """,
)

# ===== O — shares of a whole (bars that run to 100%) =========================================
# A share is read only when the audience sees what 100% is and what each part is: the title names
# the whole, every segment names its part in plain words, with its value. The rows are wholes of
# one kind (before and after), split into the same parts; the part the slide is about comes first.
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
    notes="""
    型O。割合は「何を100%とした、何の割合か」が見えないと読めない。題で全体（問い合わせ全体）を、帯の各部分で部分（その場で解決・折り返しで解決・未解決）を名前で示す。
    聞き手の知らない区分名や記号（「区分A〜C」など）は、意味の分かる言葉にする。記号は話す。
    行はどれも同じ部分に分けた同じ種類の全体（導入前と導入後）。全体の違う割合（問い合わせの内訳と、担当者の内訳など）は同じ図の行にしない。
    スライドが扱う部分（その場で解決）を左端に置くと、行どうしで長さを比べられる。部分は2〜4個。名前は入る帯にだけ書かれる（導入後の折り返しは値だけ）。細かい内訳は bars で並べる。
    """,
)

# =============================================================================================
# An experiment: 講義動画の倍速視聴と理解度
# =============================================================================================

# ===== N — hypotheses with a schematic of the prediction =====================================
fig, ax = sk.new_fig(deck.span_px(6), 280)
x = [0, 1]                                                      # two real conditions: two ticks
prepared, unprepared = [0.80, 0.73], [0.78, 0.46]
ax.plot(x, prepared, color=sk.C["accent"], marker="o")
ax.plot(x, unprepared, color=sk.C["hot"], marker="o")
ax.set_xticks(x)
ax.set_xticklabels(["等速", "2倍速"])
ax.set_xlim(-0.25, 1.25)
ax.set_ylim(0.3, 0.95)
# a prediction has no values: no ticks on the vertical axis, an arrowhead at each end, and the
# axis named by what increases — not a bare noun, not a placeholder such as 「各指標」
sk.schematic_axes(ax, y="理解の程度", keep_xticks=True)
sk.end_labels(ax, [("予習あり", 1, prepared[1], sk.C["accent"]), ("予習なし", 1, unprepared[1], sk.C["hot"])])
hypo = sk.save_fig(fig, "hypothesis",
                   caption="予測（得点と自己評価のいずれもこの形）", alt="予測されるパターン")

deck.slide(
    "仮説",
    "倍速の影響は**予習の有無**で差",
    hypo,
    sk.points([
        "**[仮説1]** 2倍速で視聴した被験者は等速の被験者より小テストの得点が低い",
        "**[仮説2]** 予習した被験者では2倍速による小テストの得点の低下が小さい",
    ]),
    sec=45,
    notes="""
    型N。結果を仮説と照らして読む発表では、仮説を独立したスライドにする。各仮説の先頭に太字の札を付け、
    結果のスライドから仮説の中身と札で指せるようにする（「…：**仮説1**の支持」）。
    予測の模式図は数値を持たない。値のない軸には目盛りを付けず、軸の先に矢印を付け、軸名は「何が増えるか」（理解の程度）で書く（sk.schematic_axes）。
    2つの条件（等速と2倍速）は実在する条件なので目盛りを付ける。同じ形を予測する量が複数あれば、図は1枚にして、どの量かを図注で1回だけ言う。
    線の名前は線の端に置く（sk.end_labels が重ならないように離す）。
    """,
)

# ===== M — the setting of an experiment, drawn ===============================================
# People as people (sk.person); things with a shape from the bundled icon sets (sk.icon, fetched
# with scripts/icons.mjs get). Every thing faces the way it acts: the camera records the subject,
# so it is mirrored (flip=True) to point left at them.
W, H = 820, 250
setting = sk.svg(
    sk.person(120, 22, 130, cls="f-accent")                                         # the subject, facing the screen
    + sk.icon("figures/icons/material-symbols--desktop-windows.svg", 360, 98, 190, cls="f-ink2")
    + sk.icon("figures/icons/ph--video-camera-fill.svg", 560, 52, 78, cls="f-mute", flip=True)
    + '<path class="ln-hair" d="M640 10V200"/>'                                     # a partition
    + sk.person(730, 22, 130)
    + '<text class="t-mid" x="120" y="232">被験者</text>'
    + '<text class="t-mid" x="360" y="232">講義動画</text>'
    + '<text class="t-mid" x="560" y="112">録画</text>'
    + '<text class="t-mid" x="730" y="232">実験者</text>',
    W, H, label="視聴実験の配置",
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
    notes="""
    型M。実験の場面は絵で見せる。人は円ではなく人の形（sk.person）。画面やカメラはアイコン集から取る（scripts/icons.mjs で探して取得し、sk.icon で置く）。
    物の向きは働きに合わせる。カメラは被験者を撮るので被験者の方を向ける（flip=True で左右反転）。
    主題（被験者）は濃紺、ほかは灰色。誰がどこにいて何を見たかが一目で分かればよい。細部は描かない。
    実験では「被験者」と呼ぶ。人数の内訳は名詞の前にまとめる（「等速条件20名と2倍速条件20名の大学生計40名」）。
    """,
)

# =============================================================================================
# A research talk: 路面画像からのひび割れ検出
# =============================================================================================

# ===== A — real images side by side ==========================================================
# The strongest pattern: show the thing itself. Two cases chosen from the data (the widest and the
# finest crack), each with the value it stands for; the one the slide is about in red.
deck.slide(
    "研究背景",
    "細いひび割れほど見落とし",
    sk.samples(
        sk.sample("figures/crack_wide.png", "97%"),
        sk.sample("figures/crack_fine.png", "63%", tone="hot"),
        caption="目視点検での発見率（幅3mm以上と幅1mm未満）[1]",
    ),
    sk.points([
        "市道の舗装点検は点検員の目視が中心で1kmあたり約3時間[2]",
        "幅1mm未満のひび割れは熟練した点検員でも3割以上を見落とし[1]",
        "広がる前に補修すれば費用は広がった後の約5分の1[3]\n→早い段階での発見が課題",
    ]),
    sec=55,
    notes="""
    型A。左が幅3mm以上、右が幅1mm未満のひび割れ。例はデータの両端から選び、選び方は口頭で言う。
    このスライドが言いたい側（細いひび割れ）の値だけを赤にする（tone="hot"）。
    箇条書きは左端に置く（中央に寄せない）。そのぶん1行に事実を1つ、幅の6〜9割まで届く長さで書く。
    """,
)

# ===== C (one chart) — the numbers prior work reports ========================================
deck.slide(
    "先行研究",
    "深層学習は高精度だが判断の根拠が不明",
    sk.vbars([("目視点検[1]", "63"), ("輝度の勾配[4]", "62"), ("深層学習[5]", "95")],
             hot=["深層学習[5]"], axis_max=100, title="幅1mm未満のひび割れの発見率（%）"),
    sk.points([
        "深層学習は学習に数万枚の注釈付き画像が必要で自治体には負担[5]",
        "輝度の勾配だけの手法は根拠が明確だが細いひび割れを見落とし[4]",
    ]),
    sec=50,
    notes="""
    先行研究の図は、資料が持つものから選ぶ（先行論文の代表的な図、先行手法が見落とす実例、報告された数値など）。
    ここでは報告された数値を棒で並べた。位置づけ図は決まった形ではない。
    """,
)

# ===== F — premises -> arrow -> framed statement (the purpose) ==============================
deck.slide(
    "目的",
    None,
    sk.therefore(
        ["幅1mm未満のひび割れは熟練した点検員の目視でも3割以上を見落とし",
         "深層学習は発見率95%と高いが何を根拠に判断したのかを示せない",
         "根拠の明確な輝度の勾配だけの手法では細いひび割れの発見率が62%"],
        "判断の根拠を示せる手法で、細いひび割れまで自動検出",
    ),
    text_only=True,
    sec=35,
    notes="""
    型F。目的は1行。手法は書かない。この型は1つのデッキで1回だけ使う。
    前提は幅いっぱいに届く長さで書く。短い前提を左に寄せて矢印と枠を中央に置くと、右が空いて釣り合わない。
    """,
)

# ===== D — flow: boxes are things, arrows are operations ====================================
deck.slide(
    "提案手法 - 全体像",
    "画像1枚から区間の補修順位を算出",
    sk.flow(
        sk.thing("路面画像", img="figures/road_alligator.png", width=200),
        sk.op("検出"),
        sk.thing("ひび割れ画素", img="figures/road_mask.png", width=200),
        sk.op("集計"),
        sk.thing("区間の指標", values=[("ひび割れ率", "12.6%"), ("最大幅", "3.1mm"), ("ほか2指標", "")]),
        sk.op("順位付け"),
        sk.thing("補修の順位", media=rank_bars(), accent=True),
    ),
    sk.points([
        "市販のカメラを車両の後部に付けて走行しながら路面を撮影",
        "暗く細い線の連なりを画素ごとに検出して100mの区間ごとに集計",
        "ひび割れ率と幅と交通量から区間ごとに補修の優先度を計算",
    ]),
    sec=60,
    notes="""
    型D。箱は「もの」（画像、検出結果、指標、順位）。操作（検出、集計、順位付け）は矢印に書く。
    箱には実物を入れる。1つの区間が流れを通る様子を、実際の画像・検出結果・計算した値・出てきた結果で見せる。
    言葉だけの箱を矢印でつないだ図は、文章で言えることしか言わず、スライドも空く。中身がないならフロー図にしない。
    """,
)

# ===== G — real examples + formula (one step of the method) =================================
deck.slide(
    "提案手法 - ひび割れ率",
    "ひび割れの面積の割合で傷みを測定",
    sk.samples(
        sk.sample("figures/road_sound.png", "0.3%"),
        sk.sample("figures/road_alligator.png", "12.6%", tone="hot"),
    ),
    sk.math(r"\text{ひび割れ率} = \frac{\text{ひび割れの画素数}}{\text{路面の画素数}}"),
    sec=50,
    notes="""
    型G。定義は実例で見せる。値の低い例と高い例を並べ、値を添え、式で結ぶ。
    仕組みの説明は口頭で行う。箇条書きは要らない。
    """,
)

# ===== I — equation + worked example =========================================================
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
    notes="""
    型I。式だけでは抽象的なので、実物1件を式に通した結果を並べる。
    符号のある値は bars(signed=True)。左右の向きの意味は ends= で軸の両端に書く。
    このスライドが言いたい項（ひび割れ率）だけを赤にする。結論は太字・中央の1行（箱なし）。
    """,
)

# ===== B — horizontal bars ===================================================================
deck.slide(
    "結果 - 精度",
    "**幅1mm未満**でも9割前後を検出",
    sk.bars([("幅3mm以上", "98"), ("幅2〜3mm", "96"), ("幅1〜2mm", "95"), ("幅0.5〜1mm", "92"), ("幅0.5mm未満", "88")],
            hot=["幅0.5〜1mm", "幅0.5mm未満"], axis_max=100, title="ひび割れの幅ごとの発見率（%）"),
    sk.points([
        "同じ120区間の目視点検では幅1mm未満のひび割れの発見率は63%",
        "誤検出は1kmあたり平均2.4件で画像での確認は約5分の作業",
    ]),
    sec=50,
    notes="""
    型B。値を棒に添える。このスライドの主題の棒だけ赤（hot=）にし、一言の要の語を太字にする。
    軸の最大値は値のすぐ上の切りのよい数（ここでは100%）。値から遠く離れた合計を軸にしない。
    """,
)

# ===== H — plot + the cases behind it, the point ringed ======================================
widths = [0, 1, 2]
dry = [91, 95, 98]
wet = [74, 90, 97]
fig, ax = sk.new_fig(deck.span_px(7), 360)
ax.plot(widths, dry, color=sk.C["accent"], marker="o")
ax.plot(widths, wet, color=sk.C["hot"], marker="o")
# names at the line ends; end_labels pushes apart the two that end close together (98 / 97)
sk.end_labels(ax, [("晴天", widths[-1], dry[-1], sk.C["accent"]), ("雨天", widths[-1], wet[-1], sk.C["hot"])])
# the label goes where no line runs: under the lower line, beside the ring
ax.annotate(f"差 {dry[0] - wet[0]}ポイント", (widths[0] + 0.14, wet[0] - 7), ha="left", va="center",
            fontsize=sk.PT["sub"], fontweight="bold", color=sk.C["hot"])
sk.ring_between(ax, widths[0], dry[0], wet[0])                    # the one place to look, sized to the gap
ax.set_xticks(widths)
ax.set_xticklabels(["1mm未満", "1〜3mm", "3mm以上"])
ax.set_xlim(-0.35, 2.55)
ax.set_ylim(60, 102)
ax.set_yticks([60, 70, 80, 90, 100])
ax.set_xlabel("ひび割れの幅")
sk.ylabel_top(ax, "発見率（%）")
sk.hgrid(ax)
plot = sk.save_fig(fig, "weather", alt="天候とひび割れの幅ごとの発見率")

deck.slide(
    "結果 - 頑健性",
    "**雨天**は晴天より細いひび割れを見落とし",
    sk.cols(
        "7-5",
        plot,
        # same order as the lines: the dry line is the upper one, so its image is on top
        sk.samples(
            sk.sample("figures/crack_fine.png", "91%", tone="accent"),
            sk.sample("figures/crack_wet.png", "74%", tone="hot"),
            stack=True,
        ),
    ),
    sec=55,
    notes="""
    型H。グラフと、その背後にある実例を並べる。線の名前は線の端に直接書き、同じ色・同じ上下の順で実例を置く（凡例を使わない）。
    見るべき場所（幅1mm未満での差）は、差の値を赤で直接書き、楕円を1つ描いて示す（sk.ring）。発表中に後から囲むのではなく、図の一部として描く。
    縦軸の名前は横書きで軸の上に置く（sk.ylabel_top）。軸の線は目盛りの端で止まる（save_fig が自動で揃える）。
    """,
)

# ===== K — summary ===========================================================================
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
    notes="""
    型K。結論は黒、今後は青。どちらも左端に置き、1行が幅の6〜9割に届く長さで書く。
    1行に収まる項目は改行しない（似た長さに割る改行は、図や枠と並べる文字のためのもの。単独の箇条書きでは右が空く）。
    含意の行（→）は別。新しい情報を出さない。質疑の間このスライドを出しておく。
    """,
)

# ===== references, blank, appendix ===========================================================
deck.refs([
    "架空一郎, 架空二郎, 舗装の目視点検における見落としの実態, *例示土木学会論文集*, 12(3), 45–56 (2024)",
    "A. Author, Inspection Time of Municipal Roads, *Journal of Examples*, 8(1), 1–12 (2023)",
    "B. Author, Cost of Early Pavement Repair, *Proc. Example Conf.*, 101–110 (2021)",
    "C. Author, Crack Detection from Intensity Gradients, *Trans. Examples*, 5(2), 20–31 (2019)",
    "D. Author et al., Deep Crack Segmentation, *Example Vision Letters*, 3, 1–9 (2025)",
])

deck.blank()

# ===== L — table of numbers (appendix) =======================================================
# Tables hold numbers and live in the appendix. A table of words raises an error. Numbers may be
# written as the field writes them: .52, −.48*, (0.59).
deck.appendix(
    "補足 - 上位5区間の指標",
    None,
    sk.table(
        ["区間", "ひび割れ率（%）", "最大幅（mm）", "交通量（千台/日）", "優先度", "目視との相関"],
        [
            ["区間 17", "12.6", "3.1", "8.4", "1.45", ".62**"],
            ["区間 42", "9.8", "2.6", "9.1", "1.12", ".55**"],
            ["区間 08", "8.1", "2.9", "4.2", "0.86", ".41*"],
            ["区間 63", "6.5", "1.8", "6.6", "0.61", ".38*"],
            ["区間 91", "4.9", "1.2", "5.3", "0.40", ".17"],
        ],
        hot=0,
        caption="** は1%水準、* は5%水準で有意。値はすべて架空",
    ),
)

deck.save()
