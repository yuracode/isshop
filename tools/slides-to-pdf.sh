#!/usr/bin/env bash
# docs/slides.pptx を PDF にする（Windows の PowerPoint に変換させる）。
#
#     bash tools/slides-to-pdf.sh [出力.pdf]
#
# Marp の --pdf は WSL からだと Chrome が無くて落ちるうえ、pptx 側で入れた
# タグの色分けが出ない。授業で投影するのは pptx なので、配布用 PDF も
# 「pptx を PowerPoint に変換させたもの」を正とする。
#
# 必要なもの: Windows 側に PowerPoint（WSL から powershell.exe が叩けること）
set -euo pipefail
cd "$(dirname "$0")/.."

OUT="${1:-docs/slides.pdf}"
PPTX="docs/slides.pptx"

[ -f "$PPTX" ] || { echo "$PPTX がありません。先に  node tools/slides-to-pptx.mjs  を実行してください。"; exit 1; }
command -v powershell.exe >/dev/null || { echo "powershell.exe が見つかりません。WSL から Windows の PowerPoint を呼ぶ想定のスクリプトです。"; exit 127; }

# PowerPoint は WSL のパスに書けないので、Windows 側の一時フォルダを経由する
WINTMP=$(powershell.exe -NoProfile -Command '[Console]::Out.Write($env:TEMP)' | tr -d '\r')
WORKWIN="$WINTMP\\isshop-pdf"
WORKWSL="/mnt/c${WINTMP#C:}"; WORKWSL="${WORKWSL//\\//}/isshop-pdf"

mkdir -p "$WORKWSL"
cp "$PPTX" "$WORKWSL/slides.pptx"
rm -f "$WORKWSL/slides.pdf"

powershell.exe -NoProfile -Command "
  \$app = New-Object -ComObject PowerPoint.Application
  \$p = \$app.Presentations.Open('$WORKWIN\\slides.pptx', \$true, \$false, \$false)
  \$p.SaveAs('$WORKWIN\\slides.pdf', 32)   # 32 = ppSaveAsPDF
  \$p.Close(); \$app.Quit()
" >/dev/null

[ -f "$WORKWSL/slides.pdf" ] || { echo "PDF が作られませんでした。PowerPoint が入っているか確認してください。"; exit 1; }
cp "$WORKWSL/slides.pdf" "$OUT"

python3 - "$OUT" <<'PY'
import re, sys
d = open(sys.argv[1], "rb").read()
pages = max(int(x) for x in re.findall(rb"/Count\s+(\d+)", d))
box = sorted({m.decode() for m in re.findall(rb"/MediaBox\s*\[[^\]]*\]", d)})
print(f"{sys.argv[1]}  {pages} ページ / {len(d)//1024} KB / {' '.join(box)}")
print("※ 960x540pt = 13.33x7.5in（16:9）であること")
PY
