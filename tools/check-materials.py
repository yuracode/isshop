#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""教材一式の整合性をまとめて確認する。

    python3 tools/check-materials.py

CLAUDE.md の「完成の判定」を機械で確認できるところだけ自動化したもの。
教材を直したら必ず通すこと。落ちた項目は、直す場所も一緒に表示する。

見た目（投影の可読性、印刷の収まり）はここでは見られない。
スライドの描画確認は tools/render-slides.sh を使う。
"""
import ast, glob, html, io, json, os, re, sys, unicodedata, zipfile
from collections import Counter
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

EXPECTED_ITEMS = 30
STOCKS = ("あり", "残りわずか", "品切れ")

ok, ng = [], []
def check(cond, title, detail=""):
    (ok if cond else ng).append((title, detail))
    return cond

def read(p):
    return io.open(p, encoding="utf-8").read()


# --------------------------------------------------------- HTML の簡易パーサ
class Grab(HTMLParser):
    """div.item ごとに、子要素の class → テキスト を集める"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.items, self.cur = [], [], None
        self.styles = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "style" in a:
            self.styles += 1
        cls = a.get("class", "").split()
        self.stack.append([tag, cls, "", a])
        if tag == "div" and "item" in cls:
            self.cur = {"_href": None}
    def handle_data(self, data):
        if self.stack:
            self.stack[-1][2] += data
    def handle_endtag(self, tag):
        while self.stack:
            t, cls, txt, a = self.stack.pop()
            if self.cur is not None:
                for c in cls:
                    if c == "item":
                        continue
                    if c == "item-link":
                        self.cur["_href"] = a.get("href")
                    self.cur.setdefault(c, txt.strip())
            if t == tag:
                break
        if tag == "div" and self.cur is not None and not any("item" in s[1] for s in self.stack):
            self.items.append(self.cur)
            self.cur = None

def parse(path):
    g = Grab()
    g.feed(read(path))
    return g

def tag_text(src, pat):
    m = re.search(pat, src, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else None


# ============================================================ 1. 練習用サイト
print("■ 練習用サイト")
idx = parse("index.html")
items = idx.items
details = sorted(glob.glob("items/*.html"))

check(len(items) == EXPECTED_ITEMS, f"一覧の商品数が {EXPECTED_ITEMS}", f"実際 {len(items)} 件 / tools/build-site.py の DATA")
check(len(details) == EXPECTED_ITEMS, f"詳細ページが {EXPECTED_ITEMS} 件", f"実際 {len(details)} 件")

names = [i.get("item-name") for i in items]
prices = [int(i["item-price"]) for i in items]
check(len(set(names)) == len(names), "商品名に重複が無い")
check(prices.count(min(prices)) == 1, "最安値が1商品に定まる",
      f"{min(prices)}円が {prices.count(min(prices))} 件。ステップ3の答えがぶれる")
check(prices.count(max(prices)) == 1, "最高値が1商品に定まる",
      f"{max(prices)}円が {prices.count(max(prices))} 件。ステップ3のやってみようがぶれる")
check(all("item-stock" not in i for i in items), "一覧に在庫が出ていない",
      "一覧に item-stock があるとステップ6の意味がなくなる")
check(idx.styles == 0, "HTML に style 属性が無い", "装飾は style.css に出す")

hrefs = [i["_href"] for i in items]
check(sorted(hrefs) == details, "一覧のリンクと詳細ページが1対1",
      f"孤立: {sorted(set(details) - set(hrefs))} / 欠落: {sorted(set(hrefs) - set(details))}")

bad_detail, bad_title = [], []
for h, n in zip(hrefs, names):
    d = parse(h)
    if not d.items:
        bad_detail.append(f"{h}: div.item が無い"); continue
    di = d.items[0]
    if di.get("item-name") != n:
        bad_detail.append(f"{h}: 商品名が一覧と違う")
    if di.get("item-stock") not in STOCKS:
        bad_detail.append(f"{h}: 在庫が {STOCKS} 以外 ({di.get('item-stock')})")
    src = read(h)
    if tag_text(src, r"<title>(.*?)</title>") == tag_text(src, r"<h1[^>]*>(.*?)</h1>"):
        bad_title.append(h)
isrc = read("index.html")
if tag_text(isrc, r"<title>(.*?)</title>") == tag_text(isrc, r"<h1[^>]*>(.*?)</h1>"):
    bad_title.append("index.html")
check(not bad_detail, "詳細ページの中身が一覧と一致", "; ".join(bad_detail[:3]))
check(not bad_title, "title と h1 が別の文字列",
      f"{bad_title[:3]} / ステップ1のやってみようで差を見せている")

# 生成スクリプトとのずれ（手で HTML を直していないか）
import subprocess, tempfile, shutil
snap = {p: read(p) for p in ["index.html"] + details}
r = subprocess.run([sys.executable, "tools/build-site.py"], capture_output=True, text=True)
drift = [p for p, v in snap.items() if not os.path.exists(p) or read(p) != v]
for p, v in snap.items():
    io.open(p, "w", encoding="utf-8").write(v)      # 生成前の状態に戻す
check(r.returncode == 0 and not drift, "HTML が tools/build-site.py の出力と一致",
      f"ずれ: {drift[:3]} / HTML を手で直した可能性。DATA を直して再生成する")


# ============================================================ 2. ノートブック
print("■ ノートブック")
nbs = {p: json.load(io.open(p, encoding="utf-8")) for p in
       ["notebooks/student.ipynb", "notebooks/instructor.ipynb"]}

def cells(nb, kind=None):
    return [("".join(c["source"]), c) for c in nb["cells"] if kind is None or c["cell_type"] == kind]

base_urls = {}
for p, nb in nbs.items():
    found = re.findall(r'BASE_URL\s*=\s*"([^"]+)"', "\n".join(s for s, _ in cells(nb)))
    check(len(found) == 1, f"{os.path.basename(p)}: BASE_URL の定義が1箇所",
          f"{len(found)} 箇所。URL は準備セルにだけ書く")
    base_urls[p] = found[0] if found else None
    check(not found or found[0].endswith("/"), f"{os.path.basename(p)}: BASE_URL が / で終わる",
          "ステップ6の連結が壊れる")
check(len(set(base_urls.values())) == 1, "2つのノートブックで BASE_URL が同じ", str(base_urls))

host = re.match(r"https?://[^/]+", base_urls["notebooks/student.ipynb"] or "").group(0) if base_urls["notebooks/student.ipynb"] else ""
ext = [u for u in re.findall(r'https?://[^\s"\\)]+', json.dumps(nbs["notebooks/student.ipynb"], ensure_ascii=False))
       if not u.startswith(host)]
check(not ext, "student.ipynb から外部サイトへのアクセスが無い", f"{ext[:3]}")

over = [(i, s.count("____")) for i, (s, c) in enumerate(cells(nbs["notebooks/student.ipynb"], "code")) if s.count("____") > 2]
check(not over, "student の空欄が1セル2箇所まで", f"超過セル: {over}")
check(sum(s.count("____") for s, _ in cells(nbs["notebooks/instructor.ipynb"])) == 0,
      "instructor に空欄が残っていない")

SUBST = [('class_="____"', 'class_="x"'), ('id="____"', 'id="x"'), ("soup.____.", "soup.title."),
         ("requests.get(____)", "requests.get(1)"), ("link.____(", "link.get("),
         ("price ____ cheapest_price", "price < cheapest_price"), ('find_all("____")', 'find_all("h2")'),
         ("price ____ 120", "price <= 120"), ("prices.____()", "prices.sort()")]
syn = []
for p, nb in nbs.items():
    for i, (s, c) in enumerate(cells(nb, "code")):
        t = s
        for a, b in SUBST:
            t = t.replace(a, b)
        try:
            ast.parse(t)
        except SyntaxError as e:
            syn.append(f"{os.path.basename(p)} コードセル{i}: {e.msg}")
check(not syn, "全コードセルが Python として妥当", "; ".join(syn[:3]))


# ============================================================ 3. 教材間の突合
print("■ 教材間の突合")
docs = {p: read(p) for p in ["docs/slides.md", "docs/handout.md", "docs/lesson-plan.md", "docs/deploy.md"]}
site_src = read("index.html") + "".join(read(p) for p in details)
nb_src = json.dumps(nbs, ensure_ascii=False)

used = set()
for name, src in list(docs.items()) + [("notebooks", nb_src)]:
    used |= set(re.findall(r'class="([a-z][a-z-]*)"', src)) | set(re.findall(r'class_="([a-z][a-z-]*)"', src))
ghost = sorted(c for c in used if f'class="{c}"' not in site_src)
check(not ghost, "教材が書いている class がサイトに実在する", f"存在しない: {ghost}")

core = ["item", "item-name", "item-price", "item-category", "item-link", "item-stock"]
missing = {p: [c for c in core if c not in src] for p, src in
           [("docs/slides.md", docs["docs/slides.md"]), ("docs/handout.md", docs["docs/handout.md"])]}
check(all(not v for v in missing.values()), "スライドとプリントに主要な class が揃っている", str(missing))

wrong = [p for p, src in docs.items() if re.search(r"(?<!\d)8\s*(つ|個|件|商品)", src)]
wrong += [p for p, nb in nbs.items() if re.search(r"(?<!\d)8\s*(つ|個|件|商品)", json.dumps(nb, ensure_ascii=False))]
check(not wrong, f"商品数の記述が {EXPECTED_ITEMS} に揃っている", f"古い記述が残っている: {wrong}")


# ============================================================ 4. スライドと台本
print("■ スライドと台本")
md = re.sub(r"<style>[\s\S]*?</style>\n?", "", re.sub(r"^---\n[\s\S]*?\n---\n", "", docs["docs/slides.md"]))
slides = [s for s in md.split("\n---\n") if s.strip()]
print(f"    スライド {len(slides)} 枚")

if os.path.exists("docs/slides.pptx"):
    z = zipfile.ZipFile("docs/slides.pptx")
    n = len([x for x in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", x)])
    check(n == len(slides), "slides.pptx の枚数が slides.md と一致",
          f"pptx {n} 枚 / md {len(slides)} 枚。node tools/slides-to-pptx.mjs で作りなおす")
    check(not [x for x in z.namelist() if re.match(r"ppt/media/.+", x)],
          "pptx が画像でなくテキストで出来ている", "Marp の --pptx を使うと編集できなくなる")
else:
    check(False, "docs/slides.pptx がある", "node tools/slides-to-pptx.mjs")

refs = [int(m) for m in re.findall(r"スライド(\d+)", docs["docs/lesson-plan.md"])]
bad_ref = sorted({r for r in refs if not 1 <= r <= len(slides)})
check(not bad_ref, "台本が参照するスライド番号が実在する", f"範囲外: {bad_ref}")

# タイムテーブルはコマごとに別の表になっている。表ごとに、頭からの積み上げを見る
PERIOD = 50          # 1コマの持ち時間（分）
groups, cur = [], []
for line in docs["docs/lesson-plan.md"].splitlines():
    m = re.match(r"^\|\s*(\d\d):(\d\d)\s*\|\s*(\d+)\s*\|", line)
    if m:
        cur.append(m.groups())
    elif cur:
        groups.append(cur); cur = []
if cur:
    groups.append(cur)

bad_time = []
for g in groups:
    if g[0][:2] != ("00", "00"):
        bad_time.append(f"表の先頭が {g[0][0]}:{g[0][1]}（00:00 から始める）")
    for (h1, m1, d), nxt in zip(g, g[1:]):
        if int(h1) * 60 + int(m1) + int(d) != int(nxt[0]) * 60 + int(nxt[1]):
            bad_time.append(f"{h1}:{m1}+{d}分 → {nxt[0]}:{nxt[1]} が合わない")
    end = int(g[-1][0]) * 60 + int(g[-1][1]) + int(g[-1][2])
    if end > PERIOD:
        bad_time.append(f"1コマが {end}分（{PERIOD}分に収まっていない）")
check(groups and not bad_time, f"タイムテーブルの時刻が積み上がっている（{len(groups)}コマ）", "; ".join(bad_time))


# ============================================================ 5. スナップショット
print("■ スナップショット（ステップ7）")
snapf = "samples/wikipedia-melonpan.html"
if os.path.exists(snapf):
    s = read(snapf)
    check(tag_text(s, r'<h1[^>]*id="firstHeading"[^>]*>(.*?)</h1>') is not None,
          "h1#firstHeading がある", "5-2 が動かなくなる")
    h2 = [html.unescape(re.sub(r"<[^>]+>", "", m)).strip() for m in re.findall(r"<h2[^>]*>(.*?)</h2>", s, re.S)]
    check(h2 and h2[0] == "目次", "find_all('h2') の1つ目が「目次」",
          f"実際: {h2[:1]}。5-3 の「いらないものが混ざる」が成立しない")
    p1 = re.search(r"<p(?:\s[^>]*)?>(.*?)</p>", s, re.S)
    check(p1 and "<sup" in p1.group(1), "最初の <p> に脚注 <sup> がある", "5-4 の掃除の題材が無くなる")
    outer = sum(s.count(x) for x in ['src="//', 'src="http', "<script src", '<link rel'])
    check(outer == 0, "スナップショットに外部リソース参照が無い", f"{outer} 件。授業中に外部へ出てしまう")
else:
    check(False, "samples のスナップショットがある", "samples/README.md の手順で取得する")


# ============================================================ 結果
print()
for t, d in ok:
    print(f"  ✓ {t}")
for t, d in ng:
    print(f"  ✗ {t}" + (f"\n      → {d}" if d else ""))
print(f"\n{len(ok)} 件 OK / {len(ng)} 件 NG")
sys.exit(1 if ng else 0)
