/**
 * docs/slides.md（Marp形式）から、編集できる PowerPoint を作る。
 *
 *   npm install pptxgenjs
 *   node tools/slides-to-pptx.mjs [入力.md] [出力.pptx]
 *
 * Marp 公式の --pptx は各スライドを画像として埋めこむため、PowerPoint 側で
 * 文字を直せない。授業では文言を調整したくなるので、テキストボックスとして
 * 組み直している。見た目の忠実さが要るとき（PDF配布など）は Marp を使う。
 */
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let PptxGenJS;
try {
  PptxGenJS = require("pptxgenjs");
} catch {
  console.error("pptxgenjs が見つかりません。`npm install pptxgenjs` を実行してください。");
  process.exit(1);
}

const SRC = process.argv[2] ?? "docs/slides.md";
const OUT = process.argv[3] ?? "docs/slides.pptx";

/**
 * 練習用サイトの配色を、プロジェクター向けにコントラストを上げて調整したもの。
 * 教室のスクリーンは色が飛んで薄く見えるので、地は白に寄せ、文字は黒に寄せる。
 * かっこ内は地（bg / titleBg / sectionBg）に対するコントラスト比。
 */
const C = {
  bg: "FFFCF6",        // ほぼ白。もとの FDF8EF は投影すると文字が沈む
  text: "1A1512",      // ほぼ黒 (16.5:1)
  accent: "8A4A00",    // 見出しの茶オレンジ (7.4:1)
  rule: "E07B00",      // 見出しの下線。装飾なので鮮やかさを残す
  strong: "9E1B12",    // 強調の赤 (7.9:1)
  codeBg: "FFFFFF", codeBorder: "C7B48E",
  inlineBg: "F6E0B0", inlineFg: "6B3A00",   // 本文中の `コード` (9.5:1)
  thBg: "F2D9A6",      // 表の見出し行
  quote: "3F3830",     // 引用 (10.6:1)
  titleBg: "C06600",   // タイトルの地。もとの F0932B に白文字は 2.3:1 で読めない
  sectionBg: "241F19", sectionFg: "FFB459", // 中扉の見出し (8.7:1)
  white: "FFFFFF",
};
const FONT = "Meiryo";        // Windows・Mac どちらにもある無難な和文フォント
const FONT_CODE = "MS Gothic"; // 等幅かつ日本語が出る

const PAGE_W = 13.3, PAGE_H = 7.5, MX = 0.7;   // LAYOUT_WIDE の実寸
const BODY_W = PAGE_W - MX * 2;

// ------------------------------------------------- 折り返しの見積もり
/** 文字列の幅を em で返す。全角は1em、半角は約0.52em */
function emWidth(str) {
  let w = 0;
  for (const ch of str) {
    const c = ch.codePointAt(0);
    const wide =
      (c >= 0x1100 && c <= 0x115f) || (c >= 0x2e80 && c <= 0xa4cf) ||
      (c >= 0xac00 && c <= 0xd7a3) || (c >= 0xf900 && c <= 0xfaff) ||
      (c >= 0xfe30 && c <= 0xfe6f) || (c >= 0xff00 && c <= 0xff60) ||
      (c >= 0xffe0 && c <= 0xffe6) || (c >= 0x1f300 && c <= 0x1faff);
    w += wide ? 1 : 0.52;
  }
  return w;
}

/** 幅 widthIn インチ・fontPt の箱に text を入れたときの行数 */
function lineCount(text, widthIn, fontPt) {
  const cap = (widthIn * 72) / fontPt;           // 1行に入る em 数
  if (cap <= 0) return 1;
  return text.split("\n").reduce(
    (n, line) => n + Math.max(1, Math.ceil(emWidth(line) / cap)), 0);
}

/** fontPt の1行の高さ（インチ）。行間ぶんの余裕を含む */
const lineH = (fontPt) => (fontPt / 72) * 1.34;

/** 本文ブロックの高さ */
function textH(text, widthIn, fontPt, pad = 0.12) {
  return lineCount(text, widthIn, fontPt) * lineH(fontPt) + pad;
}

// ---------------------------------------------------------------- パース

function parse(md) {
  let s = md.replace(/\r\n/g, "\n");
  s = s.replace(/^---\n[\s\S]*?\n---\n/, "");   // front matter
  s = s.replace(/<style>[\s\S]*?<\/style>\n?/g, "");
  return s
    .split(/\n---\n/)
    .map((raw) => {
      const cls = raw.match(/<!--\s*_class:\s*([\w-]+)\s*-->/)?.[1] ?? "";
      const body = raw.replace(/<!--[\s\S]*?-->/g, "").trim();
      return { cls, blocks: blocks(body) };
    })
    .filter((s) => s.blocks.length);
}

function blocks(body) {
  const out = [];
  const lines = body.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (!l.trim()) continue;

    if (l.startsWith("```")) {                                  // コード
      const lang = l.slice(3).trim();
      const buf = [];
      while (++i < lines.length && !lines[i].startsWith("```")) buf.push(lines[i]);
      out.push({ t: "code", lang, lines: buf });
      continue;
    }
    const h = l.match(/^(#{1,3})\s+(.*)$/);
    if (h) { out.push({ t: "h", level: h[1].length, text: h[2] }); continue; }

    if (l.startsWith("|")) {                                    // 表
      const rows = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        const cells = lines[i].split("|").slice(1, -1).map((c) => c.trim());
        if (!cells.every((c) => /^:?-{2,}:?$/.test(c))) rows.push(cells);
        i++;
      }
      i--;
      out.push({ t: "table", rows });
      continue;
    }
    if (l.startsWith(">")) {                                    // 引用
      const buf = [];
      while (i < lines.length && lines[i].startsWith(">")) buf.push(lines[i].replace(/^>\s?/, "")), i++;
      i--;
      out.push({ t: "quote", lines: buf });
      continue;
    }
    if (/^[-*]\s+/.test(l)) {                                   // 箇条書き
      const items = [];
      while (i < lines.length && (/^[-*]\s+/.test(lines[i]) || /^\s{2,}\S/.test(lines[i]))) {
        if (/^[-*]\s+/.test(lines[i])) items.push(lines[i].replace(/^[-*]\s+/, ""));
        else items[items.length - 1] += " " + lines[i].trim();
        i++;
      }
      i--;
      out.push({ t: "list", items });
      continue;
    }
    const buf = [l];                                            // 段落
    while (i + 1 < lines.length && lines[i + 1].trim() &&
           !/^([-*>|#]|```)/.test(lines[i + 1])) buf.push(lines[++i]);
    out.push({ t: "p", lines: buf });
  }
  return out;
}

/** **強調** と `コード` をテキストランに分ける */
function runs(text, base) {
  const parts = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) parts.push({ text: text.slice(last, m.index), options: { ...base } });
    const tok = m[0];
    if (tok.startsWith("**")) {
      parts.push({ text: tok.slice(2, -2), options: { ...base, bold: true, color: base.strongColor ?? C.strong } });
    } else {
      parts.push({ text: tok.slice(1, -1), options: { ...base, fontFace: FONT_CODE, color: base.codeColor ?? C.inlineFg } });
    }
    last = m.index + tok.length;
  }
  if (last < text.length) parts.push({ text: text.slice(last), options: { ...base } });
  return parts.length ? parts : [{ text, options: { ...base } }];
}

const plain = (t) => t.replace(/\*\*/g, "").replace(/`/g, "");

/**
 * HTML のコードブロックを、開きタグと閉じタグが同じ色になるように塗り分ける。
 * HTML 未習の生徒には「どれとどれが1組か」が最初の壁なので、色で対応づける。
 * 色は組ごとに変える（入れ子の深さではなく出てきた順）。同じ深さの <h2> と <p> が
 * 同じ色になると、どれとどれが1組か分からなくなるため。
 * 複数行にまたがる組は、開きから閉じまでを左の縦線でもつなぐ（spans）。
 */
const PAIR = ["B23A00", "0B5A9E", "116B36", "6B2FA0"];   // いずれも白地に 5:1 以上

function htmlPairs(lines, fontPt) {
  const stack = [], spans = [], runs = [];
  let opened = 0;   // 何組目か。色はこの順に振る
  const rows = lines.map((line, li) => {
    const parts = [];
    const re = /<\/?[a-zA-Z][\w-]*(?:\s[^>]*?)?\/?>/g;
    let last = 0, m;
    while ((m = re.exec(line))) {
      if (m.index > last) parts.push({ text: line.slice(last, m.index), color: C.text });
      const tok = m[0];
      let color;
      if (tok.startsWith("</")) {                      // 閉じタグ：開きと同じ色にする
        const open = stack.pop();
        color = open?.color ?? C.text;
        if (open && open.line !== li) spans.push({ from: open.line, to: li, depth: open.depth, color });
      } else {
        color = PAIR[opened++ % PAIR.length];
        if (!tok.endsWith("/>")) stack.push({ line: li, depth: stack.length, color });
      }
      parts.push({ text: tok, color, bold: true });
      last = m.index + tok.length;
    }
    if (last < line.length) parts.push({ text: line.slice(last), color: C.text });
    return parts.length ? parts : [{ text: line || " ", color: C.text }];
  });

  rows.forEach((parts, i) => parts.forEach((p, j) => runs.push({
    text: p.text,
    options: {
      fontFace: FONT_CODE, fontSize: fontPt, color: p.color, bold: !!p.bold,
      breakLine: j === parts.length - 1 && i < rows.length - 1,
    },
  })));
  return { runs, spans };
}

// ---------------------------------------------------------------- 描画

const warnings = [];

function build(slides) {
  const pptx = new PptxGenJS();
  pptx.layout = "LAYOUT_WIDE";   // 13.3 x 7.5in。LAYOUT_16x9 は 10 x 5.625in なので使わない
  pptx.title = "Webページから情報を取り出してみよう";

  slides.forEach((s, i) => {
    const slide = pptx.addSlide();
    if (s.cls === "title")        renderCentered(slide, s, C.titleBg, C.white, C.white, 46);
    else if (s.cls === "section") renderCentered(slide, s, C.sectionBg, C.sectionFg, C.white, 42);
    else {
      const bottom = renderNormal(slide, s, s.cls === "big");
      if (bottom > PAGE_H - 0.3) {
        const head = s.blocks.find((b) => b.t === "h" && b.level === 1);
        warnings.push(`  スライド${i + 1}「${plain(head?.text ?? "")}」 下端 ${bottom.toFixed(2)}in（上限 ${(PAGE_H - 0.3).toFixed(2)}in）`);
      }
    }
  });
  return pptx;
}

function renderCentered(slide, s, bg, headFg, bodyFg, headSize) {
  slide.background = { color: bg };
  const head = s.blocks.find((b) => b.t === "h" && b.level === 1);
  const sub  = s.blocks.find((b) => b.t === "h" && b.level === 2);
  const rest = s.blocks.filter((b) => b.t !== "h");
  // 中身の高さを先に出して、スライドの真ん中に置く
  const total = (head ? 1.35 : 0) + (sub ? 0.9 : 0) +
    rest.filter((b) => b.t === "p").length * 0.7;
  let y = Math.max(0.6, (PAGE_H - total) / 2);
  if (head) {
    slide.addText(plain(head.text), {
      x: MX, y, w: BODY_W, h: 1.2, fontSize: headSize, bold: true,
      color: headFg, fontFace: FONT, align: "center",
    });
    y += 1.35;
  }
  if (sub) {
    slide.addText(plain(sub.text), {
      x: MX, y, w: BODY_W, h: 0.8, fontSize: 28, bold: true, color: bodyFg, fontFace: FONT, align: "center",
    });
    y += 0.9;
  }
  for (const b of rest) {
    if (b.t !== "p") continue;
    slide.addText(runs(b.lines.join(" "), { fontSize: 24, bold: true, color: bodyFg, fontFace: FONT, strongColor: bodyFg, codeColor: bodyFg }), {
      x: MX, y, w: BODY_W, h: 0.6, align: "center",
    });
    y += 0.7;
  }
}

function renderNormal(slide, s, big) {
  slide.background = { color: C.bg };
  const fs = big ? 28 : 24;
  let y = 0.4;

  const head = s.blocks.find((b) => b.t === "h" && b.level === 1);
  if (head) {
    const hPt = big ? 40 : 36;
    const hh = Math.max(0.85, textH(plain(head.text), BODY_W, hPt, 0.1));
    slide.addText(runs(head.text, { fontSize: hPt, bold: true, color: C.accent, fontFace: FONT, strongColor: C.accent, codeColor: C.accent }), {
      x: MX, y, w: BODY_W, h: hh, valign: "middle", fit: "shrink",
    });
    slide.addShape("rect", { x: MX, y: y + hh + 0.02, w: BODY_W, h: 0.08, fill: { color: C.rule } });
    y += hh + 0.35;
  }

  // 1回目：高さを測って描画手順だけ作る
  const ops = [];
  for (const b of s.blocks) {
    if (b.t === "h" && b.level === 1) continue;
    const op = layout(slide, b, fs, big);
    if (op) ops.push(op);
  }
  const total = ops.reduce((a, o) => a + o.h, 0);

  // 2回目：残りの高さの中央に寄せて描く（寄せすぎないよう上限あり）
  const bottom = PAGE_H - 0.45;
  const offset = Math.min(1.2, Math.max(0, (bottom - y - total) / 2));
  let cy = y + offset;
  for (const op of ops) { op.draw(cy); cy += op.h; }
  return cy;
}

/** ブロック1つぶんの高さと描画手順を返す */
function layout(slide, b, fs, big) {
  if (b.t === "h") {
    const h = textH(plain(b.text), BODY_W, 28, 0.1);
    return { h: h + 0.12, draw: (y) =>
      slide.addText(runs(b.text, { fontSize: 28, bold: true, color: C.accent, fontFace: FONT }),
        { x: MX, y, w: BODY_W, h }) };
  }

  if (b.t === "p") {
    const txt = b.lines.join("\n");
    const h = textH(txt, BODY_W, fs);
    return { h: h + 0.16, draw: (y) =>
      slide.addText(runs(txt, { fontSize: fs, color: C.text, fontFace: FONT }),
        { x: MX, y, w: BODY_W, h, valign: "top", fit: "shrink" }) };
  }

  if (b.t === "list") {
    const w = BODY_W - 0.35;
    const hs = b.items.map((it) => textH(it, w - 0.2, fs, 0.06));
    return {
      h: hs.reduce((a, v) => a + v + 0.04, 0) + 0.12,
      draw: (y) => {
        let cy = y;
        b.items.forEach((it, i) => {
          slide.addText(runs(it, { fontSize: fs, color: C.text, fontFace: FONT }), {
            x: MX + 0.35, y: cy, w, h: hs[i], bullet: { characterCode: "25CF" }, valign: "top", fit: "shrink",
          });
          cy += hs[i] + 0.04;
        });
      },
    };
  }

  if (b.t === "quote") {
    const txt = b.lines.join("\n");
    const h = textH(txt, BODY_W - 0.35, fs - 1, 0.22);
    return { h: h + 0.18, draw: (y) => {
      slide.addShape("rect", { x: MX, y, w: 0.1, h, fill: { color: C.rule } });
      slide.addText(runs(txt, { fontSize: fs - 1, color: C.quote, fontFace: FONT, strongColor: C.quote }),
        { x: MX + 0.3, y, w: BODY_W - 0.3, h, valign: "middle", fit: "shrink" });
    } };
  }

  if (b.t === "code") {
    // 一番長い行が収まるところまで文字を小さくする（折り返させない）。
    // 行数が多いブロックは縦にもあふれるので、そのぶん上限を下げる。
    const inner = BODY_W - 0.36;
    const widest = Math.max(...b.lines.map(emWidth), 1);
    const cap = b.lines.length >= 9 ? 17 : b.lines.length >= 6 ? 19 : 20;
    const codePt = Math.min(cap, Math.floor(((inner * 72) / widest) * 10) / 10);
    const pitch = lineH(codePt);
    const h = b.lines.length * pitch + 0.3;
    const html = b.lang === "html" ? htmlPairs(b.lines, codePt) : null;
    return { h: h + 0.2, draw: (y) => {
      slide.addShape("roundRect", {
        x: MX, y, w: BODY_W, h, fill: { color: C.codeBg },
        line: { color: C.codeBorder, width: 1 }, rectRadius: 0.06,
      });
      // 複数行にまたがるペアは、開きから閉じまでを縦線でつなぐ
      for (const sp of html?.spans ?? []) {
        slide.addShape("roundRect", {
          x: MX + 0.09 + sp.depth * 0.08, y: y + 0.15 + sp.from * pitch + 0.02,
          w: 0.04, h: (sp.to - sp.from + 1) * pitch - 0.04,
          fill: { color: sp.color }, line: { color: sp.color, width: 0 }, rectRadius: 0.02,
        });
      }
      slide.addText(html ? html.runs : b.lines.join("\n"), {
        x: MX + 0.18, y: y + 0.15, w: inner, h: h - 0.3,
        fontSize: codePt, fontFace: FONT_CODE, color: C.text, valign: "top", lineSpacingMultiple: 1.06,
      });
    } };
  }

  if (b.t === "table") {
    const [head, ...body] = b.rows;
    const ncol = head.length;
    // 列幅は、各列のいちばん長い中身の比率で配分する
    const weight = head.map((_, i) => Math.max(...b.rows.map((r) => emWidth(plain(r[i] ?? ""))), 1));
    const totalW = weight.reduce((a, v) => a + v, 0);
    const raw = weight.map((v) => Math.max(1.0, (BODY_W * v) / totalW));
    const scale = BODY_W / raw.reduce((a, v) => a + v, 0);
    const cols = raw.map((v) => v * scale);

    const tPt = big ? 22 : ncol >= 4 ? 18 : 20;
    const pad = 0.16;
    const rowHs = b.rows.map((r) =>
      Math.max(0.42, Math.max(...r.map((c, i) => lineCount(plain(c), cols[i] - pad, tPt) * lineH(tPt))) + 0.16));

    const rows = [
      head.map((c) => ({ text: plain(c), options: { bold: true, fill: { color: C.thBg }, color: C.text } })),
      ...body.map((r) => r.map((c) => ({ text: plain(c), options: { color: C.text } }))),
    ];
    return { h: rowHs.reduce((a, v) => a + v, 0) + 0.2, draw: (y) =>
      slide.addTable(rows, {
        x: MX, y, w: BODY_W, colW: cols, rowH: rowHs, fontSize: tPt, fontFace: FONT,
        border: { type: "solid", color: C.codeBorder, pt: 1 },
        fill: { color: C.white }, valign: "middle", margin: 0.05,
      }) };
  }

  return null;
}

/**
 * 生成日時を固定して、中身が同じなら常に同じバイト列になるようにする。
 * これをしないと、作りなおすたび docProps/core.xml の日時だけが変わり、
 * 730KB のバイナリ差分が毎回コミットに乗ってしまう。
 */
async function freeze(buf) {
  const JSZip = require("jszip");
  const FIXED = "2020-01-01T00:00:00Z";
  const zip = await JSZip.loadAsync(buf);
  const core = "docProps/core.xml";
  if (zip.file(core)) {
    const xml = (await zip.file(core).async("string"))
      .replace(/(<dcterms:created[^>]*>)[^<]*(<\/dcterms:created>)/, `$1${FIXED}$2`)
      .replace(/(<dcterms:modified[^>]*>)[^<]*(<\/dcterms:modified>)/, `$1${FIXED}$2`);
    zip.file(core, xml);
  }
  zip.forEach((_, f) => { f.date = new Date(FIXED); });
  return zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE", compressionOptions: { level: 9 } });
}

// ---------------------------------------------------------------- 実行

const slides = parse(readFileSync(SRC, "utf8"));
const pptx = build(slides);
let buf = await pptx.write({ outputType: "nodebuffer" });
buf = await freeze(buf);
writeFileSync(OUT, buf);
console.log(`${SRC} → ${OUT}  (${slides.length} スライド, ${(buf.length / 1024).toFixed(0)} KB)`);
if (warnings.length) {
  console.warn(`\n内容がスライドからはみ出している可能性があります（${warnings.length}枚）:`);
  console.warn(warnings.join("\n"));
  console.warn("\n該当スライドの行数を減らすか、2枚に分けてください。");
} else {
  console.log("はみ出しの疑いがあるスライドはありません。");
}
