---
name: add-snapshot
description: 外部サイトを教材に使いたくなったとき。受講生を外部へアクセスさせずに「本物のページ」を扱うための、スナップショットの取りかたと samples/ への置きかた。Wikipedia など外部サイトを題材にする話が出たら使う。
---

# 外部サイトを教材に使う

## 絶対制約

**受講生が実行するコードから外部サイトへアクセスさせない。**
20人が一斉に叩くと、学校の共有グローバルIPからは1つのボットの並列アクセスに見える。

代わりに、**事前に1回だけ取得したスナップショットを `samples/` に置き、
GitHub Pages 経由で全員がそれを読む。** 体験は「本物の HTML をむしる」ままで、
負荷はゼロ、構造が固定されるので当日壊れない。

外部への実アクセスは `instructor.ipynb` の**講師実演セル1つ**に閉じ、
「生徒には実行させない」とセル内に明記する。

## 取得の手順

**1回だけ取得する。ループで回さない。**

```bash
UA='CyberKoubaibu-LessonSnapshot/1.0 (https://github.com/yuracode/isshop) curl'
curl -sS -A "$UA" -o /tmp/raw.html "https://ja.wikipedia.org/wiki/メロンパン"
```

- **連絡先入りの User-Agent を必ず付ける。** Wikimedia は `python-requests` や `curl` の
  既定値を名指しで避けるよう求めており、付けないと **403 が返る**（実測で確認済み）
- 取得先の robots.txt と利用規約を先に読む

## 加工

1. `<script>` `<style>` `<link>` を削除し、`<img>` の `src` / `srcset` を外す
   （授業中に外部へリクエストが飛ばないようにするため。構造は取得時のまま残す）
2. ファイル冒頭に HTML コメントで **出典・URL・版（oldid）・取得日・ライセンス・改変点**を書く
3. `samples/README.md` の表に1行足す

Wikipedia 本文は **CC BY-SA 4.0**。出典表示が要る。

## ノートブック側

- `student.ipynb` は `BASE_URL + "samples/..."` で読む。**外部URLを書かない**
- 記事を差し替えたら、ステップ5が前提にしている次の3点を確認する
  - `<h1 id="firstHeading">` に記事名が入っている
  - `find_all("h2")` の**1つ目が「目次」**（「いらないものが混ざる」の実演に使う）
  - 文書内で最初の `<p>` が書き出しで、`<sup>` の脚注 `[1]` を含む

`python3 tools/check-materials.py` がこの3点と外部参照ゼロを自動で確認する。

## 授業での言いかた

禁止事項の列挙にしない。**「なぜそうするのか」**が分かる形にする。

> 「本物を20人で一斉に叩くんじゃなくて、先生が前もって1回だけ取ってきて置いてあります。」

Wikipedia は「絶対だめ」ではなく **「行儀よくならいい」** が正確なところ
（robots.txt に "Friendly, low-speed bots are welcome viewing article pages" とある）。
20人程度のアクセスが Wikipedia の負荷になるわけではない、という事実もごまかさない。
