// Shared helpers: locate a deck, launch a browser, open the deck and wait until it is fully rendered.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

export const SKILL_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

/**
 * The installed copy of an npm package, found as Node finds it: <dir>/node_modules/<name> in scripts/ or in a
 * folder above it. The skill copied by hand has its packages in scripts/node_modules (npm install --prefix);
 * installed as a Claude Code plugin, they are in the plugin's root, where Claude Code installs them. null if absent.
 */
export function packageDir(name) {
  for (let d = path.join(SKILL_DIR, 'scripts'); ; d = path.dirname(d)) {
    const p = path.join(d, 'node_modules', name);
    if (fs.existsSync(p)) return p;
    if (path.dirname(d) === d) return null;
  }
}

/**
 * Accepts a deck directory, deck.py or deck.html. When the directory has a deck.py, it is run
 * first so that deck.html is always current (deck.py is the source; deck.html is generated).
 */
export function resolveDeck(arg, { regenerate = true } = {}) {
  let p = path.resolve(arg || '.');
  const isDir = fs.existsSync(p) && fs.statSync(p).isDirectory();
  const dir = isDir ? p : path.dirname(p);
  if (regenerate && fs.existsSync(path.join(dir, 'deck.py'))) runDeckPy(dir);
  if (isDir || p.endsWith('.py')) p = path.join(dir, 'deck.html');
  if (!fs.existsSync(p)) {
    throw new Error(`deck not found: ${p}\n  Pass the deck directory (containing deck.py). Create one with init.mjs.`);
  }
  return { dir, html: p, name: path.basename(dir) };
}

/** Run <dir>/deck.py with the first Python that works; print what it prints. */
export function runDeckPy(dir) {
  const env = { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' };
  const tried = [];
  for (const exe of [process.env.SLIDES_PYTHON, 'python', 'python3', 'py'].filter(Boolean)) {
    const r = spawnSync(exe, ['deck.py'], { cwd: dir, encoding: 'utf8', env });
    if (r.error) { tried.push(exe); continue; }
    const out = `${r.stdout || ''}`.trim();
    const err = `${r.stderr || ''}`.trim();
    if (r.status !== 0) {
      throw new Error(`deck.py failed (exit ${r.status}). Fix the Python error below, then run again.\n${err || out}`);
    }
    if (out) console.log(out.split('\n').map((l) => `  ${l}`).join('\n'));
    if (err) console.log(err.split('\n').map((l) => `  ${l}`).join('\n'));
    return;
  }
  throw new Error(`Python not found (tried: ${tried.join(', ')}). Install Python 3.9+ or set SLIDES_PYTHON to its path.`);
}

/** Minimal argv parser: --flag, --key value, --key=value, positionals in _. */
export function parseArgs(argv, booleans = []) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) { out._.push(a); continue; }
    const eq = a.indexOf('=');
    if (eq > 0) { out[a.slice(2, eq)] = a.slice(eq + 1); continue; }
    const key = a.slice(2);
    if (booleans.includes(key) || i + 1 >= argv.length || argv[i + 1].startsWith('--')) out[key] = true;
    else out[key] = argv[++i];
  }
  return out;
}

async function loadPlaywright() {
  try {
    return (await import('playwright-core')).chromium;
  } catch {
    throw new Error(
      `playwright-core is not installed.\n  Run once:  npm install --prefix "${path.join(SKILL_DIR, 'scripts')}"`
    );
  }
}

/**
 * Launch a Chromium-family browser. Order: $SLIDES_BROWSER (executable path) -> installed Chrome ->
 * installed Edge -> Playwright's own Chromium (only present after `npx playwright install chromium`).
 */
export async function launch() {
  const chromium = await loadPlaywright();
  const tried = [];
  const attempts = [];
  if (process.env.SLIDES_BROWSER) attempts.push({ label: 'SLIDES_BROWSER', opts: { executablePath: process.env.SLIDES_BROWSER } });
  attempts.push({ label: 'chrome', opts: { channel: 'chrome' } });
  attempts.push({ label: 'msedge', opts: { channel: 'msedge' } });
  attempts.push({ label: 'bundled chromium', opts: {} });
  for (const a of attempts) {
    try {
      const browser = await chromium.launch({ ...a.opts, headless: true });
      return { browser, label: a.label };
    } catch (e) {
      tried.push(`  - ${a.label}: ${String(e.message).split('\n')[0]}`);
    }
  }
  throw new Error(
    `No usable browser found.\n${tried.join('\n')}\n` +
    `  Install Google Chrome or Microsoft Edge, set SLIDES_BROWSER to a Chromium executable, or run:\n` +
    `    npx --prefix "${path.join(SKILL_DIR, 'scripts')}" playwright-core install chromium`
  );
}

/** Open the deck and wait for fonts, images and math to finish. Returns { page, problems }. */
export async function openDeck(browser, htmlPath, { scale = 1 } = {}) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: scale });
  const page = await context.newPage();
  const problems = [];
  page.on('pageerror', (e) => problems.push(`script error: ${String(e).split('\n')[0]}`));
  page.on('requestfailed', (r) => problems.push(`failed to load: ${decodeURIComponent(r.url())}`));
  page.on('console', (m) => { if (m.type() === 'error') problems.push(`console: ${m.text()}`); });
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'load' });
  await page.evaluate(async () => {
    if (window.deckReady) await window.deckReady;
    await document.fonts.ready;
    await Promise.all([...document.images].map((img) => (img.complete ? null : new Promise((r) => { img.onload = img.onerror = r; }))));
  });
  const fontOk = await page.evaluate(() => {
    const fam = getComputedStyle(document.querySelector('.slide') || document.body).fontFamily.split(',')[0].trim();
    return { family: fam, loaded: [300, 400, 700].map((w) => document.fonts.check(`${w} 20px ${fam}`)) };
  });
  if (fontOk.loaded.includes(false)) problems.push(`font not loaded: ${fontOk.family} (is theme/fonts/ present next to deck.html?)`);
  return { context, page, problems };
}

/** Basic facts about the deck. */
export async function deckInfo(page) {
  return page.evaluate(() => {
    const slides = [...document.querySelectorAll('.slide')];
    if (!slides.length) return { n: 0 };
    const r = slides[0].getBoundingClientRect();
    const role = (s) => (s.classList.contains('cover') ? 'cover'
      : s.classList.contains('blank') ? 'blank'
      : s.classList.contains('backmatter') ? 'backmatter'
      : s.classList.contains('appendix') ? 'appendix'
      : s.classList.contains('disclosure') ? 'disclosure' : 'main');
    return {
      n: slides.length,
      w: Math.round(r.width),
      h: Math.round(r.height),
      title: document.title,
      minutes: parseFloat(document.documentElement.dataset.minutes || '') || null,
      slides: slides.map((s, i) => ({
        n: i + 1,
        role: role(s),
        title: (s.querySelector('.heading, .cover-title')?.textContent || '').replace(/\s+/g, ' ').trim(),
        message: (s.querySelector(':scope > .msg')?.textContent || '').replace(/\s+/g, ' ').trim(),
        sec: parseFloat(s.dataset.sec || '') || null,
        notes: (s.querySelector('.notes')?.textContent || '').split('\n').map((l) => l.trim()).filter(Boolean).join('\n'),
      })),
    };
  });
}

export function pad2(n) { return String(n).padStart(2, '0'); }
