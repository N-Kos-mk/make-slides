#!/usr/bin/env node
// doctor.mjs — check that everything the skill needs is installed, and say how to fix what is not.
//
//   node doctor.mjs
//
// Exit code 0 = ready to build decks. 1 = something required is missing.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { SKILL_DIR, launch, packageDir } from './lib/deck.mjs';

const scripts = path.join(SKILL_DIR, 'scripts');
let required = 0;
const line = (ok, label, detail, fix) => {
  console.log(`  ${ok ? 'ok     ' : 'MISSING'} ${label}${detail ? ` — ${detail}` : ''}`);
  if (!ok && fix) console.log(`          fix: ${fix}`);
};

console.log('make-slides doctor');

// node
const major = Number(process.versions.node.split('.')[0]);
line(major >= 18, 'Node.js >= 18', `found ${process.versions.node}`, 'install a current Node.js LTS');
if (major < 18) required++;

// playwright-core
const pw = packageDir('playwright-core') !== null;
line(pw, 'playwright-core', '', `npm install --prefix "${scripts}"`);
if (!pw) required++;

// open-source icon sets for diagrams (scripts/icons.mjs, sk.icon)
const iconSets = ['healthicons', 'material-symbols', 'ph'].filter((s) => {
  const dir = packageDir(`@iconify-json/${s}`);
  return dir !== null && fs.existsSync(path.join(dir, 'icons.json'));
});
line(iconSets.length === 3, 'icon sets', iconSets.length ? iconSets.join(', ') : 'none', `npm install --prefix "${scripts}"`);

// browser
if (pw) {
  try {
    const { browser, label } = await launch();
    const v = browser.version();
    await browser.close();
    line(true, 'browser', `${label} ${v}`);
  } catch (e) {
    line(false, 'browser', String(e.message).split('\n')[0], 'install Google Chrome or Microsoft Edge, or set SLIDES_BROWSER to a Chromium executable');
    required++;
  }
}

// theme files
const themeOk = ['slide.css', 'ratio-4x3.css', 'ratio-16x9.css', 'fonts/NotoSansJP-Light.woff2', 'fonts/NotoSansJP-Regular.woff2', 'fonts/NotoSansJP-Bold.woff2']
  .every((f) => fs.existsSync(path.join(SKILL_DIR, 'assets', 'theme', f)));
line(themeOk, 'theme (css + fonts)', '', 'the skill directory is incomplete; restore assets/theme/');
if (!themeOk) required++;

// python side: deck.py is Python (required); matplotlib and Pillow are for plots and image preparation
const py = (() => {
  for (const exe of ['python', 'python3', 'py']) {
    try {
      const out = execFileSync(exe, ['-c', 'import sys;print(sys.version.split()[0])'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
      return { exe, version: out };
    } catch { /* try next */ }
  }
  return null;
})();
if (!py) {
  line(false, 'python (deck.py is a Python script)', '', 'install Python 3.9+');
  required++;
} else {
  line(true, `python ${py.version}`, '', '');
  const has = (m) => { try { execFileSync(py.exe, ['-c', `import ${m}`], { stdio: 'ignore' }); return true; } catch { return false; } };
  const plot = ['matplotlib', 'fontTools', 'brotli'].filter((m) => !has(m));
  line(!plot.length, 'matplotlib, fonttools, brotli (optional: plotted figures)',
    plot.length ? `missing ${plot.join(', ')}` : '', `${py.exe} -m pip install matplotlib fonttools brotli`);
  line(has('PIL'), 'Pillow (optional: cutting and resizing images from the material)', '', `${py.exe} -m pip install pillow`);
}

console.log(required ? `\n  ${required} required item(s) missing.` : '\n  ready.');
process.exit(required ? 1 : 0);
