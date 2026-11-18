#!/usr/bin/env node
// build.mjs — render a deck to PDF, per-slide PNGs and contact sheets.
//
//   node build.mjs <deck-dir | deck.html> [--no-png] [--no-sheet] [--cols 3] [--scale 1]
//
// Output (inside the deck directory):
//   out/<deck-name>.pdf        the deliverable (vector, fonts embedded, one page per slide)
//   out/png/NN.png             one image per slide at slide resolution
//   out/sheet-N.png            contact sheets (all slides side by side) for a cheap visual check
//   out/notes.md               speaker notes collected from <aside class="notes">, if any
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { resolveDeck, parseArgs, launch, openDeck, deckInfo, pad2 } from './lib/deck.mjs';

const args = parseArgs(process.argv.slice(2), ['no-png', 'no-sheet', 'help']);
if (args.help) {
  console.log('usage: node build.mjs <deck-dir | deck.html> [--no-png] [--no-sheet] [--cols 3] [--scale 1]');
  process.exit(0);
}

const SHEET_MAX = 1568; // long edge that an image reader takes without downscaling
const main = async () => {
  const deck = resolveDeck(args._[0]);
  const outDir = path.join(deck.dir, 'out');
  const pngDir = path.join(outDir, 'png');
  fs.mkdirSync(outDir, { recursive: true });

  const { browser, label } = await launch();
  try {
    const scale = Number(args.scale || 1);
    const { page, problems } = await openDeck(browser, deck.html, { scale });
    const info = await deckInfo(page);
    if (!info.n) throw new Error('no <section class="slide"> found in the deck');

    // ---- PNG per slide (screen media) ----
    const pngs = [];
    if (!args['no-png']) {
      fs.rmSync(pngDir, { recursive: true, force: true });
      fs.mkdirSync(pngDir, { recursive: true });
      const slides = page.locator('.slide');
      for (let i = 0; i < info.n; i++) {
        const file = path.join(pngDir, `${pad2(i + 1)}.png`);
        await slides.nth(i).screenshot({ path: file, animations: 'disabled' });
        pngs.push(file);
      }
    }

    // ---- PDF (print media) ----
    const pdfPath = path.join(outDir, `${deck.name}.pdf`);
    await page.emulateMedia({ media: 'print' });
    await page.pdf({
      path: pdfPath,
      width: `${info.w}px`,
      height: `${info.h}px`,
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
      preferCSSPageSize: false,
    });
    const pdfPages = countPdfPages(pdfPath);

    // ---- contact sheets ----
    const sheets = [];
    if (pngs.length && !args['no-sheet']) {
      for (const f of fs.readdirSync(outDir)) if (/^sheet-\d+\.png$/.test(f)) fs.rmSync(path.join(outDir, f));
      const cols = Math.max(1, Number(args.cols || 3));
      const gap = 14, labelH = 20;
      const thumbW = Math.floor((SHEET_MAX - gap * (cols + 1)) / cols);
      const thumbH = Math.round(thumbW * info.h / info.w);
      const rows = Math.max(1, Math.floor((SHEET_MAX - gap) / (thumbH + labelH + gap)));
      const per = cols * rows;
      const sheetPage = await page.context().newPage();
      for (let s = 0; s * per < pngs.length; s++) {
        const chunk = pngs.slice(s * per, (s + 1) * per);
        const cells = chunk.map((f, k) => {
          const n = s * per + k + 1;
          const meta = info.slides[n - 1];
          const tag = meta.role === 'main' ? '' : ` (${meta.role})`;
          return `<figure><figcaption>${n}${tag}</figcaption><img src="${pathToFileURL(f).href}" width="${thumbW}" height="${thumbH}"></figure>`;
        }).join('');
        const html = `<!doctype html><meta charset="utf-8"><style>
          html,body{margin:0;background:#fff}
          .g{display:grid;grid-template-columns:repeat(${cols},${thumbW}px);gap:${gap}px;padding:${gap}px;width:max-content}
          figure{margin:0} figcaption{font:600 13px/${labelH}px Arial,sans-serif;color:#222}
          img{display:block;outline:1px solid #8a8f96}</style><div class="g">${cells}</div>`;
        const tmp = path.join(outDir, `_sheet-${s + 1}.html`);
        fs.writeFileSync(tmp, html);
        await sheetPage.setViewportSize({ width: SHEET_MAX, height: 800 });
        await sheetPage.goto(pathToFileURL(tmp).href, { waitUntil: 'load' });
        const file = path.join(outDir, `sheet-${s + 1}.png`);
        await sheetPage.locator('.g').screenshot({ path: file });
        fs.rmSync(tmp);
        sheets.push(file);
      }
      await sheetPage.close();
    }

    // ---- speaker notes ----
    const withNotes = info.slides.filter((s) => s.notes);
    const notesPath = path.join(outDir, 'notes.md');
    if (withNotes.length) {
      const md = [`# ${info.title || deck.name} — speaker notes`, ''];
      for (const s of info.slides) {
        if (!s.notes) continue;
        md.push(`## ${s.n}. ${s.title || `(${s.role})`}${s.sec ? `  (${s.sec}s)` : ''}`, '', s.notes, '');
      }
      fs.writeFileSync(notesPath, md.join('\n'));
    } else if (fs.existsSync(notesPath)) fs.rmSync(notesPath);

    // ---- report ----
    const rel = (p) => path.relative(process.cwd(), p) || p;
    console.log(`make-slides build — ${rel(deck.html)}`);
    console.log(`  browser : ${label}`);
    console.log(`  slides  : ${info.n}  (${info.w}x${info.h}px)`);
    console.log(`  pdf     : ${rel(pdfPath)}  (${pdfPages ?? '?'} pages, ${(fs.statSync(pdfPath).size / 1024).toFixed(0)} KB)`);
    if (pngs.length) console.log(`  png     : ${rel(pngDir)}${path.sep}01.png … ${pad2(info.n)}.png`);
    for (const s of sheets) console.log(`  sheet   : ${rel(s)}`);
    if (withNotes.length) console.log(`  notes   : ${rel(notesPath)}`);
    let failed = false;
    if (pdfPages != null && pdfPages !== info.n) {
      failed = true;
      console.log(`  ERROR   : PDF has ${pdfPages} pages but the deck has ${info.n} slides — content is spilling onto extra pages. Run lint.mjs.`);
    }
    for (const p of [...new Set(problems)]) { failed = true; console.log(`  ERROR   : ${p}`); }
    process.exitCode = failed ? 1 : 0;
  } finally {
    await browser.close();
  }
};

function countPdfPages(file) {
  try {
    const s = fs.readFileSync(file).toString('latin1');
    const m = s.match(/\/Type\s*\/Page(?![a-zA-Z])/g);
    return m ? m.length : null;
  } catch { return null; }
}

main().catch((e) => { console.error(`build failed: ${e.message}`); process.exit(2); });
