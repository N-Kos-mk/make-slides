#!/usr/bin/env node
// init.mjs — create a new deck directory (or refresh the theme / library of an existing one).
//
//   node init.mjs <deck-dir> [--ratio 16:9|4:3] [--minutes 10] [--title "…"] [--refresh]
//
// Creates:
//   <deck-dir>/deck.py          the deck source (never overwritten if it exists)
//   <deck-dir>/slidekit.py      the builder library  — copy of the skill's, do not edit
//   <deck-dir>/theme/           css, fonts, KaTeX    — copy of the skill's, do not edit
//   <deck-dir>/figures/         plotted figures and images go here
//
// --refresh replaces theme/ and slidekit.py with the skill's current versions.
import fs from 'node:fs';
import path from 'node:path';
import { parseArgs, SKILL_DIR } from './lib/deck.mjs';

const args = parseArgs(process.argv.slice(2), ['refresh', 'refresh-theme', 'help']);
if (args.help || !args._[0]) {
  console.log('usage: node init.mjs <deck-dir> [--ratio 16:9|4:3] [--minutes 10] [--title "…"] [--refresh]');
  process.exit(args.help ? 0 : 2);
}

const dir = path.resolve(args._[0]);
const ratio = String(args.ratio || '16:9').replace(/\s/g, '');
if (!['4:3', '16:9'].includes(ratio)) { console.error(`unsupported ratio "${ratio}" (use 16:9 or 4:3)`); process.exit(2); }
const refresh = args.refresh || args['refresh-theme'];
const rel = (p) => path.relative(process.cwd(), p) || p;

const assets = path.join(SKILL_DIR, 'assets');
fs.mkdirSync(dir, { recursive: true });
fs.mkdirSync(path.join(dir, 'figures'), { recursive: true });
const deckPath = path.join(dir, 'deck.py');
const isNew = !fs.existsSync(deckPath);

// theme + library: fresh copies for a new deck, or on --refresh
const themeDst = path.join(dir, 'theme');
const libDst = path.join(dir, 'slidekit.py');
if (isNew || refresh || !fs.existsSync(themeDst) || !fs.existsSync(libDst)) {
  fs.rmSync(themeDst, { recursive: true, force: true });
  fs.cpSync(path.join(assets, 'theme'), themeDst, { recursive: true });
  fs.copyFileSync(path.join(assets, 'slidekit.py'), libDst);
  console.log(`theme   : ${rel(themeDst)}`);
  console.log(`library : ${rel(libDst)}`);
} else {
  console.log('theme/ and slidekit.py already exist — left untouched (pass --refresh to replace them with the skill versions)');
}

// deck.py
if (!isNew) {
  console.log('deck.py already exists — left untouched');
} else {
  const esc = (s) => String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  const py = fs.readFileSync(path.join(assets, 'template', 'deck.py'), 'utf8')
    .replaceAll('{{RATIO}}', ratio)
    .replaceAll('{{MINUTES}}', args.minutes && args.minutes !== true ? String(Number(args.minutes)) : 'None')
    .replaceAll('{{TITLE}}', esc(args.title && args.title !== true ? args.title : '発表タイトル'));
  fs.writeFileSync(deckPath, py);
  console.log(`deck    : ${rel(deckPath)}  (${ratio}${args.minutes ? `, ${args.minutes} min` : ''})`);
}

// keep build by-products and caches out of git by default
const gi = path.join(dir, '.gitignore');
if (!fs.existsSync(gi)) fs.writeFileSync(gi, 'out/png/\nout/sheet-*.png\nout/lint.json\n__pycache__/\nfigures/.fontcache/\n');

console.log('next    : write deck.py, then run lint.mjs and build.mjs on this directory');
