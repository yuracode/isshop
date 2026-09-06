---
name: edit-slides
description: 投影用スライドや受講生用プリントを直すとき。slides.md を直してから pptx を作りなおし、描画して確認するまでの一連。スライドの追加・削除・文言変更・レイアウト調整に使う。
---

# スライドとプリントを直す

## 原稿と生成物

| ファイル | 位置づけ |
|---|---|
| `docs/slides.md` | **原稿。ここを直す**（Marp 形式） |
| `docs/slides.pptx` | 生成物。直接編集しない |
| `docs/handout.md` | プリント。これ自体が原稿 |

## 手順

```bash
node tools/slides-to-pptx.mjs   # 原稿 → pptx
bash tools/render-slides.sh     # 描画して、消えた文字が無いか確認
python3 tools/check-materials.py
```

**pptx を作りなおさずに終わらせない。** 原稿と pptx がずれると、
投影したものと台本が食い違う。`check-materials.py` が枚数のずれを検出する。

## 描画確認を省略しない

`slides-to-pptx.mjs` は高さを計算で見積もっているだけで、実際の描画は見ていない。
過去に **pptx の中には文字があるのに描画されると消える**事故が起きている
（スライドサイズの取り違え。`LAYOUT_16x9` は 10×5.625in で、13.3×7.5in ではない）。

`render-slides.sh` は原稿と描画結果を全文突き合わせるので、これを通せば同じ事故は防げる。

## Marp の `--pptx` は使わない

各スライドを**画像として貼りこむ**ため、PowerPoint で文言を直せなくなる。
`tools/slides-to-pptx.mjs` はテキストボックスとして組み直す。
**PDF が欲しいときだけ** Marp を使う（`npx @marp-team/marp-cli docs/slides.md --pdf`）。

## 書くときの制約

- 1スライド1メッセージ。本文は5行以内、表は6行以内、コードは10行以内
- 第1部で扱うタグは、**その日のコードに出てくるものだけ**。網羅しない
- スライドを増減したら `docs/lesson-plan.md` の「スライドN〜M」の参照を直す
- 所要時間を変えたらタイムテーブルの開始時刻を計算しなおす

## プリント

`docs/handout.md` は **A4両面2枚（4ページ）**。増やさない。
`<div style="page-break-after: always;">` でページの切れ目を指定してある。
**4章・6章・7章・8章の4つだけで早見表として成立する**ように保つ
（1枚に減らしたいときにそこだけ印刷できる）。
