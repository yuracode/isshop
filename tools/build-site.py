# -*- coding: utf-8 -*-
"""練習用サイト（サイバー購買部）の HTML を生成する。

    python3 tools/build-site.py

商品データはこのファイルの DATA だけにある。テーマを差し替えるときは DATA と
style.css を直して実行しなおす。index.html と items/*.html は生成物なので、
直接編集しないこと（次に実行したとき消える）。

守るべき制約は CLAUDE.md の「練習用サイトの設計」を参照。とくに次の3点。
  - 価格は数値だけを item-price に入れる（「280円」にしない）
  - 在庫は詳細ページにだけ置く（一覧に出すとステップ6の意味がなくなる）
  - 最安値・最高値は1商品だけにして、答えを一意にする
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (カテゴリ, [(名前, アイコン, 価格, 在庫, 説明), ...])
DATA = [
    ("パン", [
        ("メロンパン", "🍈", 150, "あり",
         "サクサクのクッキー生地。購買部で一番人気で、昼には売り切れることもあります。"),
        ("焼きそばパン", "🍜", 180, "あり",
         "麺がぎっしり。これ1つでお腹がいっぱいになる、部活前の定番です。"),
        ("カツサンド", "🥪", 280, "残りわずか",
         "厚めのロースカツをはさみました。テスト前によく売れる、購買部の勝負めしです。"),
        ("あんぱん", "🥯", 140, "あり",
         "しっとりしたつぶあん。牛乳といっしょにどうぞ。"),
        ("コロッケパン", "🥔", 190, "品切れ",
         "揚げたてのコロッケにソースをひとぬり。数が少ないので早い者勝ちです。"),
        ("クリームパン", "🍮", 150, "あり",
         "たまごの風味がしっかりしたカスタード。ふんわり生地でつつみました。"),
    ]),
    ("軽食", [
        ("鮭おにぎり", "🍙", 120, "あり",
         "焼き鮭をほぐして混ぜこみました。朝ごはんを食べそこねた日に。"),
        ("ツナマヨおにぎり", "🍙", 120, "残りわずか",
         "だれが買っても外さない味。いつも最初になくなります。"),
        ("昆布おにぎり", "🍘", 110, "あり",
         "しっかり味の昆布入り。いちばん安いおにぎりです。"),
        ("玉子サンド", "🥚", 220, "あり",
         "ゆで玉子をあらめにつぶしました。パンの耳は落としてあります。"),
        ("ミックスサンド", "🥗", 240, "残りわずか",
         "ハム・たまご・野菜の3種類入り。いろいろ食べたい人向け。"),
        ("から揚げ棒", "🍗", 160, "品切れ",
         "1本ずつ紙につつんであります。あたためは購買部のレンジで。"),
    ]),
    ("飲み物", [
        ("いちごオレ", "🥛", 110, "あり",
         "紙パックのいちご牛乳。冷蔵ケースのいちばん手前にあります。"),
        ("スポーツドリンク", "💧", 130, "あり",
         "500mlペットボトル。体育のあとや夏場に。"),
        ("冷たい緑茶", "🍵", 130, "あり",
         "無糖の緑茶。お弁当にあわせる人が多い1本です。"),
        ("麦茶", "🫖", 120, "残りわずか",
         "カフェインなし。夏はいちばんに売り切れます。"),
        ("コーヒー牛乳", "☕", 120, "あり",
         "あまさ控えめの紙パック。パンとの相性がよいです。"),
        ("炭酸水", "🫧", 100, "あり",
         "味なしの炭酸。すっきりしたいときに。"),
    ]),
    ("文具", [
        ("シャープペンの芯", "✏️", 100, "あり",
         "0.5mm・HB・40本入り。切らしたときはここで。"),
        ("B5ノート", "📓", 160, "あり",
         "A罫30枚。授業でいちばん使うサイズです。"),
        ("消しゴム", "🧽", 90, "あり",
         "よく消えて、けずりカスがまとまるタイプ。"),
        ("黒ボールペン", "🖊️", 120, "残りわずか",
         "0.5mm の油性。提出物を書くならこれ。"),
        ("蛍光ペン", "🖍️", 130, "あり",
         "黄・ピンク・青の3色から選べます。裏うつりしにくいインクです。"),
        ("クリアファイル", "📁", 80, "あり",
         "A4サイズ。プリントをなくしがちな人へ。購買部でいちばん安い商品です。"),
    ]),
    ("日用品", [
        ("マスク5枚入り", "😷", 200, "あり",
         "使いすてタイプ。忘れた日のために置いてあります。"),
        ("ばんそうこう", "🩹", 150, "あり",
         "3サイズの詰めあわせ。保健室が閉まっているときに。"),
        ("ヘアゴム", "🎀", 180, "残りわずか",
         "黒の2本組。体育の前に買っていく人が多いです。"),
        ("折りたたみ傘", "☂️", 980, "あり",
         "急な雨のときの備え。購買部でいちばん高い商品です。"),
        ("使い捨てカイロ", "🔥", 90, "品切れ",
         "貼らないタイプ。冬のあいだだけの取りあつかいです。"),
        ("ティッシュ", "🧻", 110, "あり",
         "ポケットサイズが4個入り。花粉の季節によく出ます。"),
    ]),
]

# 通し番号を振る
items = []
n = 0
for category, rows in DATA:
    for name, icon, price, stock, desc in rows:
        n += 1
        items.append({
            "no": n,
            "file": "item%02d.html" % n,
            "category": category,
            "name": name,
            "icon": icon,
            "price": price,
            "stock": stock,
            "desc": desc,
        })

TOTAL = len(items)
HEADER = """    <header class="site-header">
      <h1 class="site-title">サイバー購買部</h1>
      <p class="site-lead">{lead}</p>
    </header>"""
FOOTER = """    <footer class="site-footer">
      <p>サイバー高校 購買部 / このお店は授業用の架空のものです</p>
    </footer>"""


def index_html():
    out = []
    out.append('<!DOCTYPE html>')
    out.append('<html lang="ja">')
    out.append('  <head>')
    out.append('    <meta charset="utf-8">')
    out.append('    <meta name="viewport" content="width=device-width, initial-scale=1">')
    out.append('    <meta name="description" content="授業用に作った架空の購買部サイトです。">')
    out.append('    <title>サイバー購買部 商品一覧</title>')
    out.append('    <link rel="stylesheet" href="style.css">')
    out.append('  </head>')
    out.append('  <body>')
    out.append(HEADER.format(lead="きょうの商品ラインナップ"))
    out.append('')
    out.append('    <main>')
    out.append('      <p class="item-count">ぜんぶで <span class="item-total">%d</span> 商品</p>' % TOTAL)
    for category, _ in DATA:
        rows = [it for it in items if it["category"] == category]
        out.append('')
        out.append('      <section class="category">')
        out.append('        <h3 class="category-name">%s</h3>' % category)
        out.append('        <div class="item-list">')
        for it in rows:
            out.append('          <div class="item">')
            out.append('            <p class="item-icon">%s</p>' % it["icon"])
            out.append('            <h2 class="item-name">%s</h2>' % it["name"])
            out.append('            <p class="item-category">%s</p>' % it["category"])
            out.append('            <p class="item-price-line"><span class="item-price">%d</span>円</p>' % it["price"])
            out.append('            <a class="item-link" href="items/%s">くわしく見る</a>' % it["file"])
            out.append('          </div>')
        out.append('        </div>')
        out.append('      </section>')
    out.append('    </main>')
    out.append('')
    out.append(FOOTER)
    out.append('  </body>')
    out.append('</html>')
    return "\n".join(out) + "\n"


def detail_html(it):
    out = []
    out.append('<!DOCTYPE html>')
    out.append('<html lang="ja">')
    out.append('  <head>')
    out.append('    <meta charset="utf-8">')
    out.append('    <meta name="viewport" content="width=device-width, initial-scale=1">')
    out.append('    <meta name="description" content="%s（%s）の商品ページです。">' % (it["name"], it["category"]))
    out.append('    <title>%s | サイバー購買部</title>' % it["name"])
    out.append('    <link rel="stylesheet" href="../style.css">')
    out.append('  </head>')
    out.append('  <body>')
    out.append(HEADER.format(lead="商品の詳細"))
    out.append('')
    out.append('    <main>')
    out.append('      <div class="item">')
    out.append('        <p class="item-icon">%s</p>' % it["icon"])
    out.append('        <h2 class="item-name">%s</h2>' % it["name"])
    out.append('        <p class="item-category">%s</p>' % it["category"])
    out.append('        <p class="item-price-line"><span class="item-price">%d</span>円</p>' % it["price"])
    out.append('        <p class="item-stock">%s</p>' % it["stock"])
    out.append('        <p class="item-description">%s</p>' % it["desc"])
    out.append('      </div>')
    out.append('      <p class="back-link"><a href="../index.html">商品一覧にもどる</a></p>')
    out.append('    </main>')
    out.append('')
    out.append(FOOTER)
    out.append('  </body>')
    out.append('</html>')
    return "\n".join(out) + "\n"


os.makedirs(os.path.join(ROOT, "items"), exist_ok=True)
for old in os.listdir(os.path.join(ROOT, "items")):
    if old.endswith(".html"):
        os.remove(os.path.join(ROOT, "items", old))

with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html())
for it in items:
    with open(os.path.join(ROOT, "items", it["file"]), "w", encoding="utf-8") as f:
        f.write(detail_html(it))

prices = [it["price"] for it in items]
cheapest = min(items, key=lambda x: x["price"])
priciest = max(items, key=lambda x: x["price"])
print("商品数:", TOTAL)
print("最安:", cheapest["name"], cheapest["price"], "(", cheapest["file"], ")")
print("最高:", priciest["name"], priciest["price"], "(", priciest["file"], ")")
print("最安の重複:", prices.count(cheapest["price"]), "/ 最高の重複:", prices.count(priciest["price"]))
for s in ["あり", "残りわずか", "品切れ"]:
    print("在庫", s, ":", sum(1 for it in items if it["stock"] == s))
print("先頭5件の在庫:", [it["stock"] for it in items[:5]])
