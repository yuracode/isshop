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
│   ├── wikipedia-melonpan.html  ステップ5で読む保存版 … 公開される
│   └── README.md       出典・ライセンス・取り直し手順
├── .nojekyll           Jekyll による変換を止める
├── notebooks/
│   ├── student.ipynb   受講生用（穴埋め）
│   └── instructor.ipynb 講師用（解答入り）
├── docs/
│   ├── slides.md       投影用スライド（Marp形式）
│   ├── handout.md      受講生用プリント（A4両面1枚）
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
- [ ] ステップ5をやる回は https://yuracode.github.io/isshop/samples/wikipedia-melonpan.html が開ける
      （装飾が当たらず素っ気ない見た目になるのが正常。`<link>` を外してあるため）

さらに、`notebooks/instructor.ipynb` を Colab で開き、**上から順に全セル実行して通ること**を確認する。
ステップ4まで含めて1分程度で終わる（ステップ4は先頭5商品だけを巡回する）。

> **`instructor.ipynb` の 5-5 だけは外部（Wikipedia の API）にアクセスする。**
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
> ステップ4で `BASE_URL + "items/item01.html"` のように連結しているため、
> `.../shop`（スラッシュなし）にすると詳細ページが取得できなくなる。

---

## 5. スライドとプリントを変換する

`docs/slides.md` は **Marp** 形式、`docs/handout.md` はふつうの Markdown。
どちらもリポジトリに置いてあるのは**元原稿**で、配布物は各自で変換する。

### 5-1. スライド → PowerPoint / PDF

**いちばん簡単なのは VS Code の拡張機能。**

1. VS Code に **Marp for VS Code** をインストール
2. `docs/slides.md` を開く
3. 右上のプレビューボタンで表示を確認
4. コマンドパレット → `Marp: Export Slide Deck...` → `.pptx` または `.pdf` を選ぶ

コマンドラインでもできる（Node.js が必要）。

```bash
npx @marp-team/marp-cli@latest docs/slides.md --pptx
npx @marp-team/marp-cli@latest docs/slides.md --pdf
```

> **WSL から実行すると失敗することがある。**
> Marp の PowerPoint / PDF 出力は内部で Chrome を動かす。Chrome が Windows 側にしか
> 無い環境（WSL2）では、WSL から起動できず `ERR_UNHANDLED_REJECTION` で落ちる。
> その場合は **Windows 側の PowerShell から実行する**か、VS Code 拡張を使う。
> `--html` 出力だけは Chrome 不要なので、内容の確認には使える。

```bash
# 内容の確認だけならこれでよい（ブラウザで開く）
npx @marp-team/marp-cli@latest docs/slides.md --html -o /tmp/slides.html
```

**変換後、投影機で必ず1度表示を確認する。** 見るのは次の3点。

- 絵文字（🍈 など）が豆腐（□）になっていないか
- コード部分が折り返されて読めなくなっていないか
- 教室のいちばん後ろの席から本文が読めるか

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

## 6. テーマを差し替えるときは

購買部以外のテーマにする場合、書き換えるのは以下だけでよい。

- `index.html`
- `items/item01.html` 〜 `item30.html`
- `style.css`（見た目を変える場合）
- `docs/slides.md` の「商品1つ分の中身」「名札の一覧」スライド
- `docs/handout.md` の6章（同じ図と表を載せている）

`samples/` はテーマに依存しないので、そのままでよい。

**ノートブックは触らなくてよい。** 商品名を決め打ちで書いていないため、
class 名（`item` / `item-name` / `item-price` / `item-category` / `item-stock` / `item-link`）さえ揃っていれば
そのまま動く。

差し替え時に守ること。

- 商品数は30のままにする（`print(len(items))` で `30` を確認する進行になっている）
- 一覧側の商品カードにも `<p class="item-category">` を入れる（ステップ3の「やってみよう」で使う）
- 価格は `<span class="item-price">280</span>` のように**数値だけ**を入れる（「280円」にしない）
- 在庫は「あり / 残りわずか / 品切れ」の3種を、**詳細ページ側**に置く
  （一覧に在庫があるとステップ4の意味がなくなる）
- `<title>` と `<h1>` は別の文字列にする（ステップ1の「やってみよう」で違いを見せている）
