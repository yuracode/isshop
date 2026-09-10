# Webページから情報を取り出してみよう

高校生向けプログラミング体験授業（**50分×2コマ**）の教材一式です。
プログラミングも HTML も未経験の人が、Google Colaboratory 上で
Python の `requests` と Beautiful Soup を使って **Webスクレイピング** を体験します。

## まずここから

| | リンク |
|---|---|
| 受講生用ノートブック（Colab で開く） | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yuracode/isshop/blob/main/notebooks/student.ipynb) |
| 練習用サイト「サイバー購買部」 | https://yuracode.github.io/isshop/ |

> **リンクは Ctrl＋クリック**（Mac は ⌘＋クリック）**で開くと、このページを残したまま新しいタブに出せます。**
> 練習用サイトと Colab を行き来するので、両方タブで開いておくと便利です。

Colab のリンクを開いて、上のセルから順に実行していけば授業が進みます。
インストールや環境構築は必要ありません（Colab に最初から入っているものだけを使います）。

## Webスクレイピングって何？

Webページの正体は **HTML** という文字の並びです。ブラウザはそれを読んで、
きれいな見た目に描き直して見せてくれています。

スクレイピングは、そのHTMLをプログラムで読みこんで、
**ほしい部分だけを取り出す**ことです。今回使う道具は2つだけ。

- `requests` … ページを取ってくる係
- `BeautifulSoup` … 取ってきたページをバラバラに分解して、探しやすくする係

```python
import requests
from bs4 import BeautifulSoup

res = requests.get("https://yuracode.github.io/isshop/")
res.encoding = "utf-8"
soup = BeautifulSoup(res.text, "html.parser")

for name in soup.find_all("h2"):
    print(name.text)
```

HTMLでは、中身に `<div class="item">` のような**目印（タグと class）**が付いています。
「この目印が付いているところを全部持ってきて」とお願いするのが `find_all()` です。
商品名・値段・在庫がそれぞれ別の目印で包まれているので、狙ったものだけを取り出せます。

授業では次の順で進みます。

| | ステップ | やること |
|---|---|---|
| 1コマ目 | 0 | ページをブラウザで見る |
| | 1 | ページのタイトルを取る |
| | 2 | 商品名を全部並べる |
| 2コマ目 | 3 | 値段も取って最安値を探す |
| | 4 | ほしいものだけ選ぶ（120円以下・安い順） |
| | 5 | カテゴリごとに数える（平均を出す） |
| | 6 | 詳細ページを辿って在庫を見る |
| | 7 | 本物の Wikipedia 記事を読む（発展） |

## 大事なマナー

スクレイピングは、相手のサーバーにアクセスして働かせる行為です。

- **短い時間に何回もアクセスしない。** 1回ごとに `time.sleep(1)` で待つ
- **相手のルールを確認する。** 利用規約と `robots.txt` を見る
- **取ったデータの使い道に気をつける。** 勝手に再配布しない

この教材では、受講生が実行するコードのアクセス先は
**この練習用サイトと、リポジトリに保存してある記事のコピーだけ**にしてあります。
20人が一斉に外部サイトを叩くと、相手からは1つのプログラムの連打に見えてしまうためです。

## リポジトリの中身

| 場所 | 中身 |
|---|---|
| `index.html` / `items/` / `style.css` | 練習用サイト（30商品）。`tools/build-site.py` の生成物 |
| `notebooks/student.ipynb` | 受講生用ノートブック（穴埋め式） |
| `notebooks/instructor.ipynb` | 講師用ノートブック（解答つき） |
| `samples/` | ステップ7で読む Wikipedia 記事の保存版 |
| `docs/slides.md` / `slides.pptx` / `slides.pdf` | 投影用スライド |
| `docs/handout.md` | 受講生用プリント（A4両面2枚） |
| `docs/lesson-plan.md` | 進行台本（タイムテーブル・想定質問） |
| `docs/deploy.md` | 公開と変換の手順 |
| `tools/` | 生成とチェックのスクリプト |

## 教材をメンテナンスする

```bash
python3 tools/build-site.py       # 商品データ → index.html / items/*.html
node tools/slides-to-pptx.mjs     # slides.md → slides.pptx
bash tools/slides-to-pdf.sh       # slides.pptx → slides.pdf
python3 tools/check-materials.py  # 教材の整合性をチェック
```

何かを直したら、最後に `check-materials.py` を通してください。
`index.html` と `items/*.html`、`docs/slides.pptx`、`docs/slides.pdf` は生成物なので直接編集しません。
