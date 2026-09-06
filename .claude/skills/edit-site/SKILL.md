---
name: edit-site
description: 練習用サイト（サイバー購買部）の商品やテーマを変えるとき。商品の追加・削除・価格変更・テーマ差し替え・カテゴリ変更に使う。index.html や items/*.html を直接編集してはいけない理由と、変更が波及する先を示す。
---

# 練習用サイトを変える

## 大原則：HTML を手で直さない

`index.html` と `items/item01〜30.html` は **`tools/build-site.py` の生成物**。
手で直しても次の生成で消える。**必ず `DATA` を直して再生成する。**

```bash
python3 tools/build-site.py
```

## 商品を変える

`tools/build-site.py` の `DATA` はカテゴリごとのリスト。1商品は
`(名前, アイコン, 価格, 在庫, 説明)` の5つ組。

守ること。破ると授業が止まる。

- **最安値と最高値は1商品だけ**にする。同額があるとステップ3の答えがぶれる
- 在庫は `あり` / `残りわずか` / `品切れ` の3種のみ
- **先頭5商品に3種の在庫を散らす**。ステップ4は `items[:5]` しか見にいかない
- 価格は数値。`item-price` には数字だけが入る（「280円」にしない）
- 商品名は重複させない

## テーマごと差し替える

`DATA` と `style.css` を直す。**ノートブックは触らない**（商品名を決め打ちしていない）。
class 名（`item` / `item-name` / `item-price` / `item-category` / `item-link` / `item-stock`）
だけ揃っていればそのまま動く。

## 商品数を変える

30 から変えると、次のすべてに波及する。**片方だけ直すと必ずずれる。**

| 直す場所 | 何が書いてあるか |
|---|---|
| `tools/build-site.py` の `DATA` | 商品そのもの |
| `tools/check-materials.py` の `EXPECTED_ITEMS` | 期待値 |
| `notebooks/instructor.ipynb` `student.ipynb` | 「30個あるので」「`30` が出れば成功」 |
| `docs/slides.md` | ステップ0・2の説明、「名札の一覧」 |
| `docs/handout.md` | 1章・6章 |
| `docs/lesson-plan.md` | 導入の口上、ステップ0・2の台本 |
| `docs/deploy.md` | 構成図、公開後の確認 |
| `CLAUDE.md` | 「練習用サイトの設計」 |

`docs/slides.md` を直したら **pptx も作りなおす**（`edit-slides` スキル）。

## 終わったら

```bash
python3 tools/check-materials.py
```
