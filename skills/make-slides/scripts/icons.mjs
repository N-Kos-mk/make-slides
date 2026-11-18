#!/usr/bin/env node
// icons.mjs — find and fetch icons / pictograms for diagrams (people, hands, a phone, a camera, …).
//
//   node icons.mjs sets                                   the icon sets that are installed, with their licences
//   node icons.mjs search <word> [<word> …] [--all] [--set <set>] [--limit N]
//                                                          names that contain any of the words (English): those
//                                                          with all of them first, then those with fewer; filled
//                                                          shapes only unless --all. Words are separate arguments:
//                                                          search video camera (not "video camera"). Give synonyms
//                                                          together: search phone smartphone mobile. A person from the
//                                                          side is "head"; a screen is "monitor" / "desktop"
//   node icons.mjs get <deck-dir> <set:name> [<set:name> …] [--as <file-name>]
//                                                          copy icons into <deck-dir>/figures/icons/ as SVG files,
//                                                          and record their licence in figures/icons/LICENSES.md
//   node icons.mjs show <deck-dir> <set:name> [<set:name> …]
//                                                          write figures/icons/_preview.png (and .html): the
//                                                          candidates side by side with their names — one image to
//                                                          look at when choosing
//
// The sets are open-source (Material Symbols: Apache-2.0; Health Icons, Phosphor: MIT). They are
// installed with the other tooling (`npm install --prefix <skill>/scripts`). Place an icon on a slide
// inside sk.svg() with sk.icon("figures/icons/<file>.svg", x, y, size, cls=…) — see references/figures.md §9.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(HERE, 'node_modules', '@iconify-json');
const SETS = ['healthicons', 'material-symbols', 'ph'];      // order = preference when names tie

const argv = process.argv.slice(2);
const flag = (name) => { const i = argv.indexOf(`--${name}`); if (i < 0) return null; const v = argv[i + 1]; argv.splice(i, 2); return v; };
const bool = (name) => { const i = argv.indexOf(`--${name}`); if (i < 0) return false; argv.splice(i, 1); return true; };

const die = (msg) => { console.error(msg); process.exit(2); };
const loaded = new Map();
function load(set) {
  if (loaded.has(set)) return loaded.get(set);
  const dir = path.join(ROOT, set);
  if (!fs.existsSync(path.join(dir, 'icons.json'))) return null;
  const icons = JSON.parse(fs.readFileSync(path.join(dir, 'icons.json'), 'utf8'));
  const info = JSON.parse(fs.readFileSync(path.join(dir, 'info.json'), 'utf8'));
  const v = { icons, info };
  loaded.set(set, v);
  return v;
}
const installed = () => SETS.filter((s) => load(s));
if (!installed().length) die(`No icon set is installed. Run: npm install --prefix "${HERE}"`);

// outline / thin / light / bold / duotone variants are listed only with --all: filled shapes read best on a slide
const VARIANT = /(-outline|-thin|-light|-bold|-duotone|-negative|-24px|2x-outline|-sharp)(-|$)/;

function resolve(set, name) {
  const s = load(set);
  if (!s) return null;
  const { icons } = s;
  let icon = icons.icons[name];
  const extra = {};
  if (!icon && icons.aliases && icons.aliases[name]) {
    const a = icons.aliases[name];
    icon = icons.icons[a.parent];
    Object.assign(extra, a);
  }
  if (!icon) return null;
  const w = icon.width || icons.width || 16;
  const h = icon.height || icons.height || 16;
  let body = icon.body;
  const hFlip = Boolean(icon.hFlip) !== Boolean(extra.hFlip);
  if (hFlip) body = `<g transform="translate(${w} 0) scale(-1 1)">${body}</g>`;
  return { set, name, w, h, left: icon.left || icons.left || 0, top: icon.top || icons.top || 0, body };
}

const cmd = argv.shift();
if (!cmd || cmd === 'help' || cmd === '--help') {
  const head = [];
  for (const l of fs.readFileSync(fileURLToPath(import.meta.url), 'utf8').split('\n').slice(1)) { if (!l.startsWith('//')) break; head.push(l.replace(/^\/\/ ?/, '')); }
  console.log(head.join('\n'));
  process.exit(0);
}

if (cmd === 'sets') {
  for (const s of installed()) {
    const { info, icons } = load(s);
    console.log(`${s.padEnd(18)} ${String(Object.keys(icons.icons).length).padStart(6)} icons  ${info.name} — ${info.license.title} (${info.author.name})`);
  }
  process.exit(0);
}

if (cmd === 'search') {
  const all = bool('all');
  const only = flag('set');
  const limit = parseInt(flag('limit') || '40', 10);
  const words = argv.map((w) => w.toLowerCase());
  if (!words.length) die('usage: node icons.mjs search <word> [<word> …] [--all] [--set <set>] [--limit N]');
  // A name matches when it contains ANY of the words; names that contain more of them come first,
  // so `search video camera` lists names with both words first, then those with one of them.
  const hits = [];
  for (const s of installed()) {
    if (only && s !== only) continue;
    const { icons } = load(s);
    const names = Object.keys(icons.icons).concat(Object.keys(icons.aliases || {}));
    for (const n of names) {
      const k = words.filter((w) => n.includes(w)).length;
      if (!k) continue;
      if (!all && VARIANT.test(n)) continue;
      // phosphor: only the filled weight unless --all
      if (s === 'ph' && !all && !/-fill$/.test(n)) continue;
      hits.push({ id: `${s}:${n}`, k, len: n.length });
    }
  }
  hits.sort((a, b) => b.k - a.k || a.len - b.len);
  const shown = hits.slice(0, limit);
  if (words.length > 1 && shown.length) {
    const full = shown.filter((h) => h.k === words.length).length;
    if (!full) console.log(`(no name contains all of: ${words.join(', ')} — names with some of them follow)`);
  }
  let prevK = shown.length ? shown[0].k : 0;
  for (const h of shown) {
    if (words.length > 1 && h.k < prevK) console.log(`— with ${h.k} of the ${words.length} words —`);
    prevK = h.k;
    console.log(h.id);
  }
  if (hits.length > limit) console.log(`… ${hits.length - limit} more (--limit N)`);
  if (!hits.length) console.log('no match — try a synonym (person / man / woman / people; hand; camera / video; phone; desk / table; monitor / desktop)');
  process.exit(0);
}

const toSvg = (ic) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${ic.left} ${ic.top} ${ic.w} ${ic.h}" width="${ic.w}" height="${ic.h}">${ic.body}</svg>\n`;
const fileName = (ic) => `${ic.set}--${ic.name}.svg`;

if (cmd === 'get' || cmd === 'show') {
  const as = flag('as');
  const deckDir = argv.shift();
  if (!deckDir || !argv.length) die(`usage: node icons.mjs ${cmd} <deck-dir> <set:name> [<set:name> …]`);
  const out = path.join(path.resolve(deckDir), 'figures', 'icons');
  fs.mkdirSync(out, { recursive: true });
  const got = [];
  for (const spec of argv) {
    const [set, name] = spec.includes(':') ? spec.split(':') : [null, spec];
    const ic = set ? resolve(set, name) : installed().map((s) => resolve(s, name)).find(Boolean);
    if (!ic) die(`not found: ${spec} (search first: node icons.mjs search <word>)`);
    got.push(ic);
  }
  if (cmd === 'show') {
    const cells = got.map((ic) => `<figure>${toSvg(ic).replace('<svg ', '<svg class="i" ')}<figcaption>${ic.set}:${ic.name}</figcaption></figure>`).join('\n');
    const html = path.join(out, '_preview.html');
    fs.writeFileSync(html, `<!doctype html><meta charset="utf-8"><style>
body{margin:0;font:14px sans-serif;display:flex;flex-wrap:wrap;gap:18px;padding:18px;color:#1a2330;width:${Math.min(got.length, 6) * 168 + 18}px}
figure{margin:0;width:150px;text-align:center}.i{width:110px;height:110px;color:#4a5665}figcaption{word-break:break-all}
</style>\n${cells}\n`);
    // and a picture of it, to look at with one image
    const png = path.join(out, '_preview.png');
    try {
      const { launch } = await import('./lib/deck.mjs');
      const { browser } = await launch();
      const page = await browser.newPage();
      await page.goto(pathToFileURL(html).href);
      await page.screenshot({ path: png, fullPage: true });
      await browser.close();
      console.log(`wrote figures/icons/_preview.png (and _preview.html) — ${got.length} candidates`);
    } catch (e) {
      console.log(`wrote figures/icons/_preview.html — ${got.length} candidates (no picture: ${String(e.message).split('\n')[0]})`);
    }
    process.exit(0);
  }
  const licences = new Map();
  for (const [k, ic] of got.entries()) {
    const fn = as && got.length === 1 ? (as.endsWith('.svg') ? as : `${as}.svg`) : fileName(ic);
    fs.writeFileSync(path.join(out, fn), toSvg(ic));
    console.log(`figures/icons/${fn}`);
    licences.set(ic.set, load(ic.set).info);
    void k;
  }
  // licence record: one entry per set used, kept across runs
  const lf = path.join(out, 'LICENSES.md');
  const old = fs.existsSync(lf) ? fs.readFileSync(lf, 'utf8') : '# Icons used in this deck\n\n';
  let text = old;
  for (const [set, info] of licences) {
    if (old.includes(`(${set})`)) continue;
    text += `- ${info.name} (${set}) — ${info.license.title}, ${info.author.name}: ${info.license.url}\n`;
  }
  fs.writeFileSync(lf, text);
  process.exit(0);
}

die(`unknown command "${cmd}" — use sets, search, get or show`);
