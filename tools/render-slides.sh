#!/usr/bin/env bash
# docs/slides.pptx を実際に描画して、枠からはみ出して消えた文字が無いか確かめる。
#
#     bash tools/render-slides.sh [出力先ディレクトリ]
#
# 必要なもの（無ければ最初に教えてくれる）:
#     sudo apt-get install -y libreoffice-impress poppler-utils fonts-noto-cjk
#
# 出力:
#     <出力先>/slides.pdf     PDF
#     <出力先>/slide-NN.png   1枚ずつの画像（目で見る用）
#     <出力先>/slides.txt     描画された文字（機械で突き合わせる用）
#
# Linux には Meiryo / MS Gothic が無いので、行間や字幅は本番と完全一致しない。
# 絵文字は豆腐（□）になる。位置関係とはみ出しの確認に使うもの、と割り切ること。
set -euo pipefail
cd "$(dirname "$0")/.."

OUT="${1:-/tmp/isshop-slides}"
PPTX="docs/slides.pptx"

missing=()
command -v soffice   >/dev/null || missing+=(libreoffice-impress)
command -v pdftoppm  >/dev/null || missing+=(poppler-utils)
if [ ${#missing[@]} -gt 0 ]; then
  echo "必要なコマンドがありません。次を実行してください（別のターミナルで。sudo はパスワード入力に端末が要ります）:"
  echo "  sudo apt-get install -y ${missing[*]} fonts-noto-cjk"
  exit 127
fi
[ -f "$PPTX" ] || { echo "$PPTX がありません。先に  node tools/slides-to-pptx.mjs  を実行してください。"; exit 1; }

mkdir -p "$OUT"
rm -f "$OUT"/slides.pdf "$OUT"/slide-*.png "$OUT"/slides.txt

echo "PDF に変換しています..."
soffice --headless --norestore --convert-to pdf --outdir "$OUT" "$PPTX" >/dev/null
echo "画像にしています..."
pdftoppm -png -r 90 "$OUT/slides.pdf" "$OUT/slide"
pdftotext -layout "$OUT/slides.pdf" "$OUT/slides.txt"

echo
python3 - "$OUT/slides.txt" <<'PY'
# 元原稿の文が、描画結果にすべて含まれているかを確かめる
import io, re, sys, unicodedata

md = io.open("docs/slides.md", encoding="utf-8").read()
md = re.sub(r"^---\n[\s\S]*?\n---\n", "", md)
md = re.sub(r"<style>[\s\S]*?</style>\n?", "", md)
slides = [s for s in md.split("\n---\n") if s.strip()]
pages = io.open(sys.argv[1], encoding="utf-8").read().split("\f")

def norm(t):
    t = re.sub(r"<!--[\s\S]*?-->", "", t)
    t = re.sub(r"```\w*", "", t)
    for c in "*`|>#●•‣":
        t = t.replace(c, "")
    t = re.sub(r"^\s*[-*]\s*", "", t, flags=re.M)
    return unicodedata.normalize("NFKC", re.sub(r"[\s　:*-]+", "", t))

print(f"スライド {len(slides)} 枚 / 描画されたページ {len([p for p in pages if p.strip()])} 枚")
bad = []
for i, (m, p) in enumerate(zip(slides, pages), 1):
    src, got = norm(m), norm(p)
    for j in range(0, max(0, len(src) - 20)):
        if src[j:j + 20] not in got:
            bad.append((i, src[j:j + 20])); break

if bad:
    print(f"\n枠からはみ出して消えている疑い: {len(bad)} 枚")
    for i, chunk in bad:
        print(f"  スライド{i:2d}  最初に消えたあたり: {chunk}")
    print("\ndocs/slides.md の該当スライドを短くするか、2枚に分けてください。")
    sys.exit(1)
print("\n全スライド、原稿の文字が欠けずに描画されています。")
PY

echo
echo "画像: $OUT/slide-*.png  （目で見て、詰まりすぎ・空きすぎが無いか確認する）"
