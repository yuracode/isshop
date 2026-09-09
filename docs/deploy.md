# 公開手順

練習用サイトを GitHub Pages で公開する手順。

- リポジトリ：https://github.com/yuracode/isshop
- 公開URL：**https://yuracode.github.io/isshop/**

---

## 1. リポジトリ構成

GitHub Pages のブランチ公開で選べるフォルダは `/(root)` と `/docs` の2つだけで、
`/site` のような任意のフォルダは指定できない。
そのため、**サイトのファイルをリポジトリ直下に置く**構成にしている。

```
isshop/
├── index.html          商品一覧（トップページ）… 公開される
├── items/
│   ├── item01.html     商品詳細（全30件）     … 公開される
│   └── item30.html
├── style.css                                  … 公開される
├── samples/
│   ├── wikipedia-melonpan.html  ステップ7で読む保存版 … 公開される
│   └── README.md       出典・ライセンス・取り直し手順
├── .nojekyll           Jekyll による変換を止める
├── notebooks/
│   ├── student.ipynb   受講生用（穴埋め）
│   └── instructor.ipynb 講師用（解答入り）
├── tools/
│   ├── build-site.py       商品データ → index.html / items/*.html
│   ├── slides-to-pptx.mjs  slides.md → 編集できる slides.pptx
│   ├── check-materials.py  教材の整合性を31項目チェック
│   ├── slides-to-pdf.sh    pptx → 配布用 PDF（PowerPoint 経由）
│   └── render-slides.sh    pptx を描画して、消えた文字を検出
├── .claude/skills/         作業手順（Claude Code 用）
├── docs/
│   ├── slides.md       投影用スライド（原稿）
│   ├── slides.pptx     ↑から生成した PowerPoint（そのまま使える）
│   ├── slides.pdf      ↑から生成した配布用 PDF
│   ├── handout.md      受講生用プリント（A4両面2枚）
│   ├── lesson-plan.md  進行台本
│   └── deploy.md       このファイル
└── CLAUDE.md
```

`notebooks/` `docs/` `CLAUDE.md` も同じリポジトリにあるため、
`https://yuracode.github.io/isshop/docs/lesson-plan.md` のようなURLでアクセスできてしまう。
授業の運用上は問題ないが、**`instructor.ipynb` に解答が入っている点は認識しておくこと**
（公開リポジトリなので、そもそも GitHub 上で誰でも閲覧できる）。

`.nojekyll` は、GitHub Pages が既定で走らせる Jekyll の変換を無効にするための空ファイル。
`docs/*.md` が勝手に HTML に変換されるのを防ぎ、置いたファイルがそのまま配信される。

---

## 2. 公開の手順

### 2-1. リポジトリに push する

```bash
cd /path/to/isshop
git init
git add .
git commit -m "教材一式を追加"
git branch -M main
git remote add origin https://github.com/yuracode/isshop.git
git push -u origin main
```

### 2-2. GitHub Pages を有効にする

1. https://github.com/yuracode/isshop を開く
2. **Settings** → 左メニューの **Pages**
3. **Source** で `Deploy from a branch` を選ぶ
4. **Branch** を `main`、フォルダを **`/ (root)`** に設定して **Save**

> フォルダは必ず `/ (root)`。`/docs` を選ぶと `docs/` の中身が公開され、サイトが表示されない。

### 2-3. 公開を待つ

反映まで**1〜2分**かかる（初回は5分程度かかることもある）。
Settings → Pages の上部に緑のチェックと公開URLが表示されれば完了。

---

## 3. 公開後の確認

以下をすべてブラウザで確認する。**授業前日までに必ず実施すること。**

- [ ] https://yuracode.github.io/isshop/ が開き、5つのカテゴリに30商品が並んでいる
- [ ] CSS が効いている（オレンジのヘッダーとカード表示になっている）
- [ ] カテゴリの見出し（パン／軽食／飲み物／文具／日用品）が出ている
- [ ] 「くわしく見る」を押すと詳細ページに飛び、在庫が表示される
- [ ] 詳細ページの「商品一覧にもどる」で戻れる
- [ ] スマートフォンで開いてもレイアウトが崩れない
- [ ] **学校のネットワークから開ける**（フィルタリングで塞がれていないか）
- [ ] ステップ7をやる回は https://yuracode.github.io/isshop/samples/wikipedia-melonpan.html が開ける
      （装飾が当たらず素っ気ない見た目になるのが正常。`<link>` を外してあるため）

さらに、`notebooks/instructor.ipynb` を Colab で開き、**上から順に全セル実行して通ること**を確認する。
ステップ6まで含めて1分程度で終わる（ステップ6は先頭5商品だけを巡回する）。

> **`instructor.ipynb` の 7-5 だけは外部（Wikipedia の API）にアクセスする。**
> 授業では講師機で1回だけ実行するセル。`student.ipynb` には入れていないので、
> **生徒側からの外部アクセスは1件もない。**

---

## 4. URL が変わったときにやること

ノートブック内で URL を書いているのは**「準備」セルの `BASE_URL` の1箇所だけ**。
ここを書き換えれば全ステップが追随する。

```python
BASE_URL = "https://yuracode.github.io/isshop/"
```

ただし、**ステップ0の説明（Markdown セル）にブラウザで開くためのリンクも1つ**書いてある。
コードから参照されてはいないが、生徒がそこをクリックするので、あわせて直すこと。

書き換える対象は次の3ファイル。

| ファイル | 箇所 |
|---|---|
| `notebooks/instructor.ipynb` | 準備セルの `BASE_URL` / ステップ0のリンク |
| `notebooks/student.ipynb` | 準備セルの `BASE_URL` / ステップ0のリンク |
| `docs/lesson-plan.md` | 冒頭の「対象サイト」 / 事前準備チェック |

```bash
grep -rn "yuracode.github.io" notebooks/ docs/
```
で全箇所を洗い出せる。

> **末尾のスラッシュを必ず残す。**
> ステップ6で `BASE_URL + "items/item01.html"` のように連結しているため、
> `.../shop`（スラッシュなし）にすると詳細ページが取得できなくなる。

---

## 5. スライドとプリントを変換する

`docs/slides.md` は **Marp** 形式、`docs/handout.md` はふつうの Markdown。
どちらもリポジトリに置いてあるのは**元原稿**で、配布物は各自で変換する。

### 5-1. スライド → PowerPoint

**`docs/slides.pptx` はリポジトリに置いてある。**
そのままダウンロードして使えるので、ふだんは変換の必要はない。

`docs/slides.md` を直したら、次のコマンドで作りなおす。

```bash
npm install                    # 最初の1回だけ（pptxgenjs が入る）
node tools/slides-to-pptx.mjs  # docs/slides.md → docs/slides.pptx
```

生成は決定的で、内容が同じなら何度実行しても同じファイルになる。
差分が出たら、それは本当に中身が変わったということ。

このスクリプトは**テキストボックスとして組み直す**ので、
**PowerPoint 側で文字を直せる**。授業に合わせて文言を変えたいときはこちら。

内容がスライドの下からはみ出しそうな場合、実行時に警告が出る。
出たら、そのスライドの行数を減らすか2枚に分ける。

### 5-1b. スライド → PDF

**`docs/slides.pdf` はリポジトリに置いてある。** 投影機に PowerPoint が無いとき、
生徒に配るとき、印刷するときはこれを使う。63ページ・16:9（960×540pt）。

`docs/slides.pptx` を作りなおしたら、次のコマンドで PDF も作りなおす。

```bash
bash tools/slides-to-pdf.sh    # docs/slides.pptx → docs/slides.pdf
```

Windows の PowerPoint に変換させている（WSL から `powershell.exe` を呼ぶ）。
**pptx が正、PDF はその写し**、という関係にしてある。Marp から直接 PDF を作ると、
`slides-to-pptx.mjs` が入れているタグの色分け（開きタグと閉じタグを同じ色にする）が
出ないため、投影するものと配るものが食い違う。

#### Marp を使う場合（Markdown の見た目のまま出したいとき）

`docs/slides.md` は Marp 形式でもある。

1. VS Code に **Marp for VS Code** をインストール
2. `docs/slides.md` を開き、右上のプレビューで確認
3. コマンドパレット → `Marp: Export Slide Deck...` → `.pdf`

```bash
npx @marp-team/marp-cli@latest docs/slides.md --pdf
```

> **Marp の `--pptx` は各スライドを画像として貼りこむ。**
> 見た目は Markdown どおりになるが、**PowerPoint で文字を編集できない**。
> 編集したいなら上のスクリプトを使うこと。

> **WSL から実行すると失敗する。**
> Marp は内部で Chrome を動かす。Chrome が Windows 側にしか無い WSL2 では起動できず
> `ERR_UNHANDLED_REJECTION` で落ちる。WSL 内の Chrome も
> `libnss3` `libnspr4` `libasound2` が無いと動かない
> （`sudo apt install libnss3 libasound2t64` で入る）。
> **Windows 側の PowerShell から実行するか、VS Code 拡張を使うのが早い。**
> `--html` 出力だけは Chrome 不要なので、内容の確認には使える。

```bash
# 内容の確認だけならこれでよい（ブラウザで開く）
npx @marp-team/marp-cli@latest docs/slides.md --html -o /tmp/slides.html
```

**変換後、投影機で必ず1度表示を確認する。** 見るのは次の3点。

- 絵文字（🍈 など）が豆腐（□）になっていないか
- コード部分が折り返されて読めなくなっていないか
- 教室のいちばん後ろの席から本文が読めるか

#### 変換結果を目で確認する

```bash
sudo apt-get install -y libreoffice-impress poppler-utils fonts-noto-cjk   # 最初の1回
bash tools/render-slides.sh
```

PDF と 1枚ずつの PNG を作り、**枠からはみ出して消えた文字**が無いかを
`docs/slides.md` と全文突き合わせて確認する。
過去に「pptx の中には文字があるのに描画されると消える」事故が起きているので、
**スライドを直したら必ず通すこと。**

> Linux には Meiryo / MS Gothic が無いので、この方法での見た目は本番と完全には一致しない。
> **絵文字は豆腐（□）になる**が、Windows の PowerPoint では正しく出る。
> 位置関係とはみ出しの確認に使うもの、と割り切ること。

### 5-2. プリント → PDF

`docs/handout.md` は **A4両面2枚（4ページ）**。
`<div style="page-break-after: always;">` でページの切れ目を指定してあるので、
ブラウザ印刷でも表が途中で分断されない。

**1枚に減らしたい場合**は、4章（タグ表）・6章（サイトの地図）・7章（命令表）・8章（エラー対処）
だけを印刷する。この4つが早見表の本体で、残りはスライドと重複している。

いちばん手軽なのは、GitHub 上で `docs/handout.md` を開いてブラウザから印刷する方法
（`Ctrl + P` → 「PDFに保存」）。VS Code の Markdown PDF 拡張でもよい。

印刷時の設定。

- 用紙 **A4**、**両面**、余白は「狭い」
- **背景のグラフィック**を有効にする（表の見出しの色が出る）
- 4ページに収まらない場合は、縮小率を 90% にする

チェックボックス（`- [ ]`）は、変換方法によって四角が出ないことがある。
出ない場合は手書き用の枠として `□` に置き換えてよい。

## 6. 教材を直したときの確認

**何を直しても、最後にこれを通す。**

```bash
python3 tools/check-materials.py
```

商品数・class 名の突合・最安値の一意性・BASE_URL の重複・受講生用ノートブックからの
外部アクセス・スライドと台本の整合など、31項目を数秒で確認する。外部ツールは要らない。

NG が出た項目には**直す場所も表示される**。

`index.html` や `items/*.html` は `tools/build-site.py` の生成物なので、
**手で直さないこと。** 商品やテーマを変えるときは、そのファイルの `DATA` を直して

```bash
python3 tools/build-site.py
```

で作りなおす。手で直すと `check-materials.py` の「HTML が build-site.py の出力と一致」で落ちる。

## 7. テーマを差し替えるときは

購買部以外のテーマにする場合、書き換えるのは以下だけでよい。

| ファイル | 何を直すか |
|---|---|
| `tools/build-site.py` の `DATA` | 商品そのもの（名前・アイコン・価格・在庫・説明） |
| `style.css` | 見た目を変える場合 |
| `docs/slides.md` | 「商品1つ分の中身」「名札の一覧」スライド |
| `docs/handout.md` | 6章（同じ図と表を載せている） |

直したら再生成と確認。

```bash
python3 tools/build-site.py
node tools/slides-to-pptx.mjs
python3 tools/check-materials.py
```

> `index.html` と `items/*.html` は**生成物**なので手で直さない。次の生成で消える。

`samples/` はテーマに依存しないので、そのままでよい。

**ノートブックは触らなくてよい。** 商品名を決め打ちで書いていないため、
class 名（`item` / `item-name` / `item-price` / `item-category` / `item-stock` / `item-link`）さえ揃っていれば
そのまま動く。

差し替え時に守ること（`check-materials.py` が自動で確認する）。

- 商品数は30のままにする（`print(len(items))` で `30` を確認する進行になっている）
- **最安値と最高値は1商品だけ**にする。同額があるとステップ3の答えがぶれる
- **先頭5商品に3種の在庫を散らす**（ステップ6は `items[:5]` しか見にいかない）
- 価格は数値だけを入れる（「280円」にしない）
- 在庫は「あり / 残りわずか / 品切れ」の3種を、**詳細ページ側**に置く
- `<title>` と `<h1>` は別の文字列にする
