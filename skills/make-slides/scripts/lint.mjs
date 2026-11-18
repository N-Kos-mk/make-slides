#!/usr/bin/env node
// lint.mjs — measure the rendered deck in a real browser and report layout / style problems.
//
//   node lint.mjs <deck-dir | deck.html> [--strict] [--json] [--no-info] [--metrics]
//
// Exit code: 0 = no errors, 1 = errors (or warnings with --strict), 2 = could not run.
// Every finding has a rule id. A rule can be silenced for one slide with
//   deck.slide(…, lint_off="F2")   — only with a reason written in a comment next to it.
// See references/lint-rules.md for what each rule means and how to fix it.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { resolveDeck, parseArgs, launch, openDeck, deckInfo, SKILL_DIR } from './lib/deck.mjs';

const args = parseArgs(process.argv.slice(2), ['strict', 'json', 'no-info', 'metrics', 'help']);
if (args.help) {
  console.log('usage: node lint.mjs <deck-dir | deck.html> [--strict] [--json] [--no-info] [--metrics]');
  process.exit(0);
}

/* ------------------------------------------------------------------------------------------
   Everything inside lintInPage runs in the browser. It must be self-contained.
   ------------------------------------------------------------------------------------------ */
function lintInPage(cfg) {
  const PX_PER_PT = 96 / 72;
  const findings = [];
  let suppressed = 0;
  const rootCS = getComputedStyle(document.documentElement);
  const tokenPt = (n) => parseFloat(rootCS.getPropertyValue(n));
  const SCALE = [...new Set(['--fs-head', '--fs-cover', '--fs-large', '--fs-msg', '--fs-body', '--fs-sub', '--fs-small', '--fs-tiny']
    .map(tokenPt).filter(Number.isFinite))].sort((a, b) => a - b);
  const FS_TINY = tokenPt('--fs-tiny') || 12;
  const FS_SMALL = tokenPt('--fs-small') || 14;

  // palette: computed rgb() string -> token name
  const probe = document.createElement('span');
  document.body.appendChild(probe);
  const norm = (c) => { probe.style.color = ''; probe.style.color = c; return getComputedStyle(probe).color; };
  const PALETTE = {};
  for (const n of ['--ink', '--ink-2', '--ink-3', '--line', '--tint', '--bg', '--accent', '--accent-tint', '--accent-2', '--accent-text', '--hot', '--hot-tint', '--c-mute']) {
    const v = rootCS.getPropertyValue(n).trim();
    if (v) PALETTE[norm(v)] = n;
  }
  PALETTE[norm('#ffffff')] = PALETTE[norm('#ffffff')] || 'white';
  probe.remove();
  const isTransparent = (c) => !c || c === 'transparent' || /rgba\(.*,\s*0\)$/.test(c);

  const visible = (el) => {
    if (el.closest('.notes, script, style, template')) return false;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 || r.height > 0;
  };
  const describe = (el) => {
    let s = el.tagName.toLowerCase();
    const cls = [...el.classList].join('.');
    if (cls) s += '.' + cls;
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (t) s += ` "${t.slice(0, 22)}${t.length > 22 ? '…' : ''}"`;
    return s;
  };
  const isOff = (el, rule) => {
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const v = n.getAttribute('data-lint-off');
      if (v && v.split(/[\s,]+/).includes(rule)) return true;
    }
    return false;
  };
  const add = (sev, slideNo, rule, msg, el) => {
    if (el && isOff(el, rule)) { suppressed++; return; }
    findings.push({ sev, slide: slideNo, rule, msg, where: el ? describe(el) : '' });
  };
  const px = (v) => `${Math.round(v)}px`;
  const units = (t) => [...t].reduce((n, ch) => n + (ch.charCodeAt(0) > 0x2e7f ? 1 : ch === ' ' ? 0.3 : 0.56), 0);

  const textNodes = (root) => {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const res = [];
    let n;
    while ((n = w.nextNode())) {
      if (!n.nodeValue.trim()) continue;
      const p = n.parentElement;
      if (!p || !visible(p)) continue;
      res.push(n);
    }
    return res;
  };
  const isInline = (el) => /^inline/.test(getComputedStyle(el).display) || getComputedStyle(el).display === 'contents';
  const blockOf = (el) => { let b = el; while (b && isInline(b) && b.parentElement) b = b.parentElement; return b; };
  const effPt = (el) => {
    let v = parseFloat(getComputedStyle(el).fontSize);
    if (el instanceof SVGElement && el.getScreenCTM) { const m = el.getScreenCTM(); if (m) v *= Math.hypot(m.a, m.b); }
    return v / PX_PER_PT;
  };
  // line boxes of the element's own inline content (stops before the first block-level child)
  const lineBoxes = (el) => {
    const r = document.createRange();
    r.selectNodeContents(el);
    for (const c of el.children) {
      if (!isInline(c) && visible(c)) { r.setEndBefore(c); break; }
    }
    const rects = [...r.getClientRects()].filter((q) => q.width > 0.5 && q.height > 0.5);
    rects.sort((a, b) => a.top - b.top || a.left - b.left);
    const lines = [];
    for (const q of rects) {
      const last = lines[lines.length - 1];
      if (last && q.top < last.bottom - Math.min(q.height, last.bottom - last.top) * 0.5) {
        last.left = Math.min(last.left, q.left); last.right = Math.max(last.right, q.right);
        last.top = Math.min(last.top, q.top); last.bottom = Math.max(last.bottom, q.bottom);
      } else lines.push({ left: q.left, right: q.right, top: q.top, bottom: q.bottom });
    }
    return lines;
  };
  const ownText = (el) => [...el.childNodes].filter((n) => n.nodeType === 3 || (n.nodeType === 1 && isInline(n) && !n.matches('.ref')))
    .map((n) => n.textContent).join('').replace(/\s+/g, ' ').trim();
  const JA = /[぀-ヿ㐀-鿿]/;
  const FIGURE = '.fig, .samples-wrap, .chart, .flow, .math-block, svg.dia';
  // a number as a table prints it: 12, 1,234, 0.52, .52 (APA), −.48*, 3.2%, 0.1〜0.3, (0.59), **, —
  const NUMERIC = /^[(（]?[−+\-±]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)\s*(?:%|\*{1,3}|†)?(?:[〜~–\-−][−+\-±]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)%?)?[)）]?$|^[—–\-*]?$|^\*{1,3}$|^†$|^[−+\-±]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)\s*[(（][−+\-±]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)[)）]$/;
  const OPLIKE = /(する|化|計算|算出|抽出|分析|解析|学習|回帰|推定|分解|選択|処理|変換|収集|検証|比較|集計|分類|検出|生成|最適化|フィルタ|クラスタリング)$/;

  const slides = [...document.querySelectorAll('.slide')];
  const roleOf = (s) => (s.classList.contains('cover') ? 'cover' : s.classList.contains('blank') ? 'blank'
    : s.classList.contains('backmatter') ? 'backmatter' : s.classList.contains('appendix') ? 'appendix'
    : s.classList.contains('disclosure') ? 'disclosure' : 'main');
  const wide = slides.length ? slides[0].getBoundingClientRect().width > 1100 : false;

  const metrics = {};
  const numbers = [];
  const headBottoms = [];
  const headings = new Map();
  const abbr = new Map();   // token -> [{slide, el}]
  const sections = [];
  const topics = new Map();   // part -> [topic, …] in slide order
  let mainCount = 0, textOnlyCount = 0, boxedSlides = 0;

  slides.forEach((slide, idx) => {
    const no = idx + 1;
    const role = roleOf(slide);
    const sr = slide.getBoundingClientRect();
    const slideBg = getComputedStyle(slide).backgroundColor;
    if (role === 'blank') {
      if (textNodes(slide).length) add('warn', no, 'S1', 'blank slide contains text; remove it or drop the "blank" class', slide);
      return;
    }
    const head = slide.querySelector(':scope > .head');
    const heading = slide.querySelector(':scope > .head > .heading');
    const msg = slide.querySelector(':scope > .msg');
    const body = slide.querySelector(':scope > .body');
    const relaxed = role === 'appendix' || role === 'backmatter';
    const textOnly = slide.hasAttribute('data-text-only');
    const figs = body ? [...body.querySelectorAll(FIGURE)].filter((el) => visible(el) && !el.parentElement.closest(FIGURE)) : [];

    /* ---------- S: structure ---------- */
    if (role !== 'cover') {
      if (!head || !heading || !body) {
        add('error', no, 'S1', 'slide has no heading/body structure; build slides with deck.slide(heading, message, *components), not raw HTML', slide);
      }
      if (heading) {
        const ht = heading.textContent.replace(/\s+/g, ' ').trim();
        if (!ht) add('error', no, 'S1', 'empty heading', heading);
        if (heading.scrollWidth > heading.clientWidth + 1) add('error', no, 'S2', 'the heading does not fit on one line; it only names the part of the talk (研究背景 / 結果 - 精度)', heading);
        headBottoms.push({ no, y: Math.round((head.getBoundingClientRect().bottom - sr.top) * 2) / 2, el: head });
        if (ht) { if (!headings.has(ht)) headings.set(ht, []); headings.get(ht).push(no); }
        if (role === 'main') {
          const [part, ...rest] = ht.split(' - ');
          sections.push(part.trim());
          if (rest.length) { if (!topics.has(part.trim())) topics.set(part.trim(), []); topics.get(part.trim()).push(rest.join(' - ').trim()); }
        }
      }
    }
    if (role === 'main') {
      mainCount++;
      if (textOnly) textOnlyCount++;
      /* ---------- M: the message under the heading ---------- */
      if (msg) {
        const mt = msg.textContent.replace(/\s+/g, ' ').trim();
        const clone = msg.cloneNode(true);
        clone.querySelectorAll('.ref, .katex').forEach((x) => x.remove());
        const plain = clone.textContent.replace(/\s+/g, ' ').trim();
        if (/[、，。．]/.test(plain)) add('error', no, 'M1', 'the message contains 「、」 or 「。」; it has become a sentence — one noun-ending phrase only', msg);
        else if (/(です|ます|でした|ました|である|であった|だ)$/.test(plain)) add('warn', no, 'M1', 'the message is a sentence (です・ます・である); end it on a noun: 「〜を左右する」→「〜を左右」', msg);
        else if (/(する|した|できる|できない|している|していない|ている|ていない|される|された|なる|なった)$/.test(plain)) add('warn', no, 'M1', `the message ends on a verb ("${plain.slice(-5)}"); try a noun ending: 「両立できていない」→「両立」, 「翻訳し測る」→「指標決定と寄与測定」`, msg);
        const deictic = plain.match(/逆に|逆の|反対に|同様に|同じく|前者|後者/);
        if (deictic) add('warn', no, 'M4', `the message says 「${deictic[0]}」 but not what it is compared with; a message is a claim with its subject and what happens to it — 「雨天では逆に低下」→「雨天では検出率が晴天より低下」`, msg);
        if (units(plain) > 20) add('warn', no, 'M2', `the message is about ${Math.round(units(plain))} characters; aim for 18 or fewer — it is a phrase to read at a glance, the rest is said aloud`, msg);
        if (msg.scrollWidth > msg.clientWidth + 1) add('error', no, 'O2', 'the message does not fit on one line', msg);
        void mt;
      } else if (figs.length && !textOnly) {
        add('info', no, 'M3', 'the slide has a figure but no message; say in one short phrase what the figure shows', heading || slide);
      }
      /* ---------- F: figures ---------- */
      // F5: a chart (bars, or a plot made with save_fig) must say where to look — inside the chart
      // (red or dark-blue bars, red in a plot, a ring) or outside it, emphasised (bold / red / accent
      // words in the message or the bullets, or the bold conclusion line)
      const charts = body ? [...body.querySelectorAll('.chart, figure[data-plot]')].filter(visible) : [];
      if (charts.length) {
        const textMarked = (msg && msg.querySelector('strong, b, .key, .alert'))
          || [...body.querySelectorAll('.points strong, .points .key, .points .alert, .conclusion')].some(visible);
        const chartMarked = charts.some((c) => c.matches('[data-marked]') || c.querySelector('.bar.hot, .bar.hl, .vbar.hot, .vbar.hl, .share-seg.hot, .share-seg.hl'));
        if (!textMarked && !chartMarked) add('warn', no, 'F5', 'the chart does not say where to look. Mark the point of the slide — the key words of the message in bold (**…**), the bars it is about in red (hot=) or dark blue (highlight=), red for the decisive line or point of a plot, or one ring (sk.ring) around the place that matters', charts[0]);
      }
      if (!figs.length && !textOnly && body) {
        add('warn', no, 'F1', 'no figure on this slide — words alone do not reach the audience. Show it (samples of real images, bars, vbars, shares, flow, a plot, an equation) or declare text_only=True (目的, まとめ)', body);
      }
    }

    // F7: a plot whose two axes are both lists of names, with marks at the crossings (slidekit marks it)
    for (const pf of body ? body.querySelectorAll('figure[data-catgrid]') : []) {
      add('warn', no, 'F7', 'both axes of this plot are lists of names (groups, kinds, methods) with marks at their crossings; a place on it means nothing — the rows could be swapped — so the grid only pretends to measure. Show what really differs: an amount on its own axis with its values, a time on a time axis, two settings as pictures side by side — or say it in two bullets', pf);
    }

    // F8: every position map is a judgement call — the slide must need it
    for (const pm of body ? body.querySelectorAll('svg[data-posmap]') : []) {
      add('info', no, 'F8', 'a position map: keep it only if the position itself is the point of this slide — a trade-off between two amounts that the others each give up and this work holds together, which two bullets would not show as quickly. Otherwise show what actually differs (a real axis, pictures) or say it in two bullets. Name the reason it is needed in the report (figures.md §7)', pm);
    }

    // S7: text placed directly in a flex/grid container next to elements is split into separate boxes
    for (const el of slide.querySelectorAll('*')) {
      if (el.closest('.katex, svg, .notes') || !visible(el)) continue;
      if (!/flex|grid/.test(getComputedStyle(el).display)) continue;
      const bare = [...el.childNodes].some((n) => n.nodeType === 3 && n.nodeValue.trim());
      if (bare && [...el.children].some((c) => visible(c) && !isInline(c))) add('error', no, 'S7', 'text sits directly inside a layout container next to other elements, so each piece becomes its own box; wrap the text in <p>', el);
    }
    if (role === 'cover') {
      const ct = slide.querySelector('.cover-title');
      if (!ct) add('error', no, 'S1', 'cover needs <h1 class="cover-title">', slide);
      else {
        const ls = lineBoxes(ct);
        if (ls.length >= 4) add('warn', no, 'S2', `cover title runs to ${ls.length} lines; shorten it or move the subtitle into sub=`, ct);
        const ws = ls.map((l) => l.right - l.left);
        if (ls.length >= 2 && Math.min(...ws) < 0.4 * Math.max(...ws)) add('warn', no, 'S8', 'cover title breaks into very uneven lines; put the \\n at a phrase boundary near the middle', ct);
      }
    }
    for (const cell of slide.querySelectorAll('.tbl th, .tbl td')) {
      if (visible(cell) && lineBoxes(cell).length >= 3) add('warn', no, 'T8', 'table cell wraps to 3+ lines; a table holds numbers, not sentences', cell);
    }
    for (const tbl of slide.querySelectorAll('.tbl, table')) {
      const cells = [...tbl.querySelectorAll('tbody td:not(:first-child)')].map((c) => c.textContent.trim()).filter(Boolean);
      const nNum = cells.filter((c) => NUMERIC.test(c)).length;
      if (cells.length && nNum / cells.length < 0.5) add('error', no, 'F4', 'a table of words. Tables are for numbers only; show the comparison with a figure or say it in two bullets', tbl);
      else if (role === 'main') add('info', no, 'F4', 'a table on a main slide: would bars()/vbars() show the same numbers at a glance? Tables belong in the appendix', tbl);
    }
    for (const lab of slide.querySelectorAll('.thing-label')) {
      const t = lab.textContent.replace(/\s+/g, '');
      if (OPLIKE.test(t)) add('warn', no, 'G1', `flow box "${t}" reads like an operation. A box is a thing (data, a result); write the operation on the arrow with sk.op() and name the thing it produces`, lab);
    }
    for (const flow of slide.querySelectorAll('.flow')) {
      const things = [...flow.querySelectorAll(':scope > .thing')];
      const shown = things.filter((t) => t.querySelector('.thing-media, .thing-value, .thing-values')).length;
      if (things.length && shown * 2 < things.length) add('warn', no, 'G2', `only ${shown} of the ${things.length} boxes in the flow show anything but a word. A flow of words is a list with arrows; it says nothing a sentence would not and leaves the slide empty — follow one real case through it (the actual image, the actual numbers, the actual result), or do not draw a flow`, flow);
    }

    // F6: horizontal bars that stop far short of their axis leave the right side of the chart empty
    for (const bl of slide.querySelectorAll('.bars')) {
      const fs = [...bl.querySelectorAll('.bar-track i, .bar-track')].map((el) => parseFloat(el.style.getPropertyValue('--f'))).filter(Number.isFinite);
      if (fs.length && Math.max(...fs) < 0.6) add('warn', no, 'F6', `the longest bar reaches only ${Math.round(Math.max(...fs) * 100)}% of the axis; the right side of the chart is empty. Set axis_max just above the largest value — a total that matters (a time limit, a maximum) goes in the title or a bullet, or chart the share of it`, bl);
    }

    // T10: a bullet of a list on its own (not in a column, not the premises of therefore) that is
    // broken early. Balanced breaks are for text laid out against something else; a list on its
    // own runs its first line to the width, and is broken only when it does not fit.
    for (const li of slide.querySelectorAll('.body .points > li')) {
      if (!visible(li) || li.closest('.cols, .therefore')) continue;
      const ls = lineBoxes(li);
      if (ls.length < 2) continue;
      const ul = li.parentElement.getBoundingClientRect();
      const avail = (slide.querySelector(':scope > .body') || li).getBoundingClientRect().right - ls[0].left;
      const total = ls.reduce((s, l) => s + (l.right - l.left), 0);
      const first = ls[0].right - ls[0].left;
      void ul;
      if (total < avail * 0.97) add('warn', no, 'T10', 'this bullet would fit on one line but is broken into two; a list on its own is not balanced by breaking lines — that leaves the right side empty. Remove the \\n (balanced breaks are for text set against a figure, a frame or a column)', li);
      else if (first < avail * 0.75) add('warn', no, 'T10', `the first line of this bullet stops at ${Math.round(100 * first / avail)}% of the width; break near the end of the line so the first line is long, or shorten the bullet to one line`, li);
    }

    /* ---------- H: containment — a part stays inside what it belongs to ---------- */
    for (const li of slide.querySelectorAll('.points > li')) {
      const then = li.querySelector(':scope > .then');
      if (!then || !visible(li)) continue;
      const first = lineBoxes(li)[0];
      const tl = lineBoxes(then);
      if (!first || !tl.length) continue;
      const fw = first.right - first.left;
      const tw = Math.max(...tl.map((l) => l.right - l.left));
      if (tw > fw + 0.6 * parseFloat(getComputedStyle(li).fontSize)) add('warn', no, 'H1', 'the consequence line (→) sticks out beyond the line it follows; a part stays inside what it belongs to — shorten the consequence, or move words up into the first line', li);
    }
    for (const fg of slide.querySelectorAll('.sample, .fig')) {
      const pic = fg.querySelector(':scope > img, :scope > svg');
      const cap = fg.querySelector(':scope > figcaption');
      if (!pic || !cap || !visible(cap)) continue;
      const pw = pic.getBoundingClientRect().width;
      const spans = [...cap.children].length ? [...cap.children] : [cap];
      const cw = Math.max(...spans.flatMap((s) => lineBoxes(s).map((l) => l.right - l.left)), 0);
      if (cw > pw + 2) add('warn', no, 'H1', `the text under the picture is ${px(cw - pw)} wider than the picture; a caption stays inside the width of what it describes — shorten it`, cap);
    }

    /* ---------- O: overflow ---------- */
    const all = [...slide.querySelectorAll('*')].filter((el) => !el.closest('.katex') && visible(el));
    const reported = [];
    const underReported = (el) => reported.some((a) => a.contains(el));
    for (const el of all) {
      if (underReported(el)) continue;
      const r = el.getBoundingClientRect();
      const o = Math.max(sr.left - r.left, r.right - sr.right, sr.top - r.top, r.bottom - sr.bottom);
      if (o > 0.5) { add('error', no, 'O1', `extends ${px(o)} outside the slide; it will be cut off`, el); reported.push(el); }
    }
    if (body) {
      const br = body.getBoundingClientRect();
      for (const el of body.querySelectorAll('*')) {
        if (!visible(el) || el.closest('.katex') || el.querySelector(':scope > .katex') || underReported(el)) continue;
        if (el instanceof SVGElement && el.tagName !== 'svg') continue;
        const r = el.getBoundingClientRect();
        const o = Math.max(br.left - r.left, r.right - br.right, r.bottom - br.bottom, br.top - r.top);
        if (o > 1) {
          const side = (r.bottom - br.bottom === o) ? 'below' : (r.right - br.right === o) ? 'right of' : (br.left - r.left === o) ? 'left of' : 'above';
          add('error', no, 'O2', `extends ${px(o)} ${side} the body area; cut words or bullets (say them aloud) — never shrink text`, el);
          reported.push(el);
        }
      }
      for (const box of body.querySelectorAll('.col, .thing, .sample, .vbar, .share-seg')) {
        const cr = box.getBoundingClientRect();
        for (const el of box.querySelectorAll('*')) {
          if (!visible(el) || el.closest('.katex') || underReported(el)) continue;
          if (el instanceof SVGElement && el.tagName !== 'svg') continue;
          const r = el.getBoundingClientRect();
          const o = Math.max(cr.left - r.left, r.right - cr.right);
          if (o > 1) { add('error', no, 'O3', `is ${px(o)} wider than its ${box.classList[0]} and collides with the neighbour`, el); reported.push(el); }
        }
      }
      const flow = body.querySelector('.flow');
      if (flow && flow.scrollWidth > flow.clientWidth + 1) add('error', no, 'O3', 'the flow is wider than the slide; use fewer things, shorter labels or smaller pictures', flow);
    }
    for (const el of all) {
      const cs = getComputedStyle(el);
      if (el === slide || !/hidden|clip/.test(cs.overflowX + cs.overflowY)) continue;
      if (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1) add('error', no, 'O5', 'content is clipped by overflow:hidden', el);
    }
    // images squeezed to nothing by too many words
    for (const img of slide.querySelectorAll('.samples img, .fig.fill img')) {
      const r = img.getBoundingClientRect();
      if (visible(img) && r.height < 110) add('warn', no, 'F2', `the image is only ${px(r.height)} tall — the words leave it no room. Cut bullets (three at most, one line each) so the picture is the main thing`, img);
    }

    /* ---------- text blocks ---------- */
    const tnodes = textNodes(slide).filter((n) => !n.parentElement.closest('.katex'));
    const blocks = [...new Set(tnodes.map((n) => blockOf(n.parentElement)))];
    const blockInfo = blocks.map((el) => {
      const lines = lineBoxes(el);
      const u = lines.length ? {
        left: Math.min(...lines.map((l) => l.left)), right: Math.max(...lines.map((l) => l.right)),
        top: lines[0].top, bottom: lines[lines.length - 1].bottom,
      } : null;
      if (!u) return { el, lines, u };
      const fs = parseFloat(getComputedStyle(el).fontSize);
      // Noto Sans JP: glyphs occupy roughly 0.28em..1.28em of the 1.45em content area
      const ink = { left: u.left, right: u.right, top: u.top + 0.26 * fs, bottom: Math.max(u.top + 0.3 * fs, u.bottom - 0.15 * fs) };
      return { el, lines, u, ink };
    }).filter((b) => b.u);

    // O4: overlapping text blocks
    let overlapN = 0;
    for (let i = 0; i < blockInfo.length && overlapN < 3; i++) {
      for (let j = i + 1; j < blockInfo.length && overlapN < 3; j++) {
        const a = blockInfo[i], b = blockInfo[j];
        if (a.el.closest('svg') || b.el.closest('svg') || a.el.contains(b.el) || b.el.contains(a.el)) continue;
        const w = Math.min(a.ink.right, b.ink.right) - Math.max(a.ink.left, b.ink.left);
        const h = Math.min(a.ink.bottom, b.ink.bottom) - Math.max(a.ink.top, b.ink.top);
        if (w > 2 && h > 2) { add('warn', no, 'O4', `text overlaps ${describe(b.el)}`, a.el); overlapN++; }
      }
    }
    // text inside SVG diagrams must not run over its neighbours or out of the drawing
    for (const svg of slide.querySelectorAll('svg.dia')) {
      const vr = svg.getBoundingClientRect();
      const ts = [...svg.querySelectorAll('text')].map((t) => ({ t, r: t.getBoundingClientRect() }));
      for (const { t, r } of ts) {
        if (r.left < vr.left - 1 || r.right > vr.right + 1 || r.top < vr.top - 1 || r.bottom > vr.bottom + 1) add('warn', no, 'O4', 'diagram text runs outside the drawing; enlarge the drawing or shorten the label', t);
      }
      let n = 0;
      for (let i = 0; i < ts.length && n < 2; i++) for (let j = i + 1; j < ts.length && n < 2; j++) {
        const a = ts[i].r, b = ts[j].r;
        if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 6) { add('warn', no, 'O4', `diagram labels overlap: "${ts[i].t.textContent}" and "${ts[j].t.textContent}"`, ts[i].t); n++; }
      }
    }

    /* ---------- T: typography ---------- */
    const offScale = new Map();
    let proseChars = 0, boldChars = 0;
    for (const n of tnodes) {
      const p = n.parentElement;
      const cs = getComputedStyle(p);
      const pt = effPt(p);
      const txt = n.nodeValue.replace(/\s+/g, '');
      const key = Math.round(pt * 10) / 10;
      const tinyOk = p.closest('.source, .ref, caption, .refs');
      if (pt < FS_TINY - 0.3) add('error', no, 'T1', `text is ${key}pt; the floor is ${FS_TINY}pt (and ${FS_SMALL}pt for anything the audience must read)`, p);
      else if (pt < FS_SMALL - 0.3 && !tinyOk) add('warn', no, 'T1', `${key}pt is reserved for sources and citation marks; use ${FS_SMALL}pt or larger`, p);
      if (!SCALE.some((s) => Math.abs(s - pt) < 0.35)) { if (!offScale.has(key)) offScale.set(key, p); }
      if (cs.fontStyle === 'italic' && JA.test(n.nodeValue)) add('warn', no, 'T4', 'italic Japanese text (the font has no italic; it is a fake slant)', p);
      if (/underline/.test(cs.textDecorationLine)) add('warn', no, 'T4', 'underlined text; emphasise with bold only', p);
      const colour = (p instanceof SVGElement) ? cs.fill : cs.color;
      if (!PALETTE[colour]) add('warn', no, 'T5', `text colour ${colour} is not a theme colour`, p);
      const fam = cs.fontFamily.split(',')[0].replace(/["']/g, '').trim();
      if (fam !== 'Noto Sans JP' && !p.closest('.refs')) add('warn', no, 'T9', `font-family "${fam}" overrides the theme font`, p);
      // running text in the body: what the audience has to read (figure labels excluded)
      if (body && body.contains(p) && !p.closest('.tbl, .chart, svg, .legend, .source, .refs, figcaption, .samples-caption, .flow, .note')) {
        proseChars += txt.length;
        if (parseInt(cs.fontWeight, 10) >= 600 && !p.closest('.conclusion, .boxed')) boldChars += txt.length;
      }
    }
    for (const [k, el] of offScale) add('warn', no, 'T2', `${k}pt is not on the type scale (${SCALE.join(', ')}pt); use a theme component, never a custom size`, el);
    if (proseChars > 40 && boldChars / proseChars > 0.3) add('warn', no, 'T3', `${Math.round(100 * boldChars / proseChars)}% of the body text is bold; bold is for keywords only`, body);
    const runs = body ? [...body.querySelectorAll('strong, b, em, .key, .alert')].filter((e) => visible(e) && !e.closest('.conclusion, .boxed, .tbl, .chart')) : [];
    if (runs.length > 6) add('warn', no, 'T3', `${runs.length} emphasised runs on one slide; keep the one or two words the audience must not miss`, body);
    const alerts = [...slide.querySelectorAll('.alert')].filter(visible);
    if (alerts.length > 1) add('warn', no, 'K4', `${alerts.length} uses of red text (!!…!!); red marks the single thing to look at`, alerts[1]);

    for (const b of blockInfo) {
      const el = b.el;
      if (el.closest('.refs, svg')) continue;
      const cs = getComputedStyle(el);
      const n = b.lines.length;
      if (n >= 4 && cs.textAlign === 'center') add('warn', no, 'T6', `${n} centred lines; multi-line text is left-aligned`, el);
      const prose = el.matches('li, p, figcaption') && !el.closest('.tbl');
      if (prose && n >= 3 && !relaxed && !el.matches('.boxed')) add('warn', no, 'W2', `a text block of ${n} lines; one idea per bullet, two lines at most — cut it to a noun phrase and say the rest aloud`, el);
      if (n >= 2) {
        const ws = b.lines.map((l) => l.right - l.left);
        const fs = parseFloat(cs.fontSize);
        const last = ws[n - 1];
        const longest = Math.max(...ws);
        // a bullet of a list on its own runs its first line long, so a short last line is right there
        const ownList = el.matches('li') && el.closest('.points') && !el.closest('.cols, .therefore');
        if (last < fs * 1.6) add('warn', no, 'T7', 'the last line holds a single character; reword, or set the break yourself with \\n at a phrase boundary', el);
        else if (last < 0.3 * longest && !el.querySelector('.then') && !ownList) add('info', no, 'T7', 'the lines are very uneven (short last line); break with \\n where the meaning turns so that the lines have similar lengths', el);
      }
    }

    /* ---------- W / D: words ---------- */
    if (body && role !== 'cover') {
      const limit = (wide ? 180 : 140) * (relaxed ? 1.6 : 1);
      if (proseChars > limit) add('warn', no, 'D1', `${proseChars} characters of running text (guide: ${Math.round(limit)}). The slide is trying to explain everything; keep what must be read and move the rest to notes=`, body);
      const lists = [...body.querySelectorAll('.points')];
      const nBullets = lists.reduce((n, ul) => n + ul.querySelectorAll(':scope > li').length, 0);
      if (figs.length && !body.querySelector('.therefore') && nBullets > 3 && !relaxed) add('warn', no, 'W1', `${nBullets} bullets next to a figure; three at most — the figure is the main thing`, lists[0]);
      if (nBullets > 6) add('warn', no, 'W1', `${nBullets} bullets on one slide; split the slide or say some aloud`, lists[0]);
      const closers = [...body.querySelectorAll('.conclusion, .boxed')].filter(visible);
      if (closers.length > 1) add('warn', no, 'W3', `${closers.length} conclusion / boxed statements on one slide; a slide comes to one point`, closers[1]);
      if (closers.length) boxedSlides += body.querySelector('.boxed') ? 1 : 0;
      const small = [...body.querySelectorAll('.note, .fig > figcaption, .samples-caption')].filter(visible);
      if (small.length > 1) add('warn', no, 'W4', `${small.length} small grey lines (captions / notes) on one slide; sub-labels make a slide look machine-made — keep one at most and say the rest aloud`, small[1]);
      const sampleNotes = [...body.querySelectorAll('.sample-note')].filter(visible);
      if (sampleNotes.length && small.length) add('info', no, 'W4', 'both a caption and per-image notes under the samples; one of them is usually enough', small[0]);
      const deep = body.querySelector('ul ul, ol ol, ul ol, ol ul');
      if (deep) add('error', no, 'W1', 'nested list; bullets have one level', deep);
      if (role === 'main') {
        const hits = [];
        for (const b of blockInfo) {
          if (!body.contains(b.el) || b.el.closest('.refs, .source, svg, .tbl caption')) continue;
          const t = ownText(b.el);
          const stops = (t.match(/。/g) || []).length;
          if (/。$/.test(t) || stops >= 1 || /(です|ます|でした|ました|ません|でしょう)(?![ぁ-ん])/.test(t) || /(である|であった)(?![ぁ-ん])/.test(t)) hits.push(b.el);
        }
        if (hits.length) add('warn', no, 'D3', `${hits.length} text block(s) written as sentences (。, です・ます, である); use noun-ending phrases, one idea per line`, hits[0]);
        const labelled = [...body.querySelectorAll('.points > li')].filter((li) => /^[^：:]{2,12}[：:]\s*\S/.test(ownText(li)));
        // W5: parentheses — glosses tucked into every line, or the English order "X（which is Y）"
        const lines = [...body.querySelectorAll('.points > li, .conclusion, .boxed')].filter(visible).map((el) => {
          const c = el.cloneNode(true); c.querySelectorAll('.ref, .katex').forEach((x) => x.remove());
          return { el, text: c.textContent };
        });
        const paren = (t) => (t.match(/[（(][^（）()]*[）)]/g) || []).length;
        const crowded = lines.find((l) => paren(l.text) >= 2);
        const withParen = lines.filter((l) => paren(l.text) >= 1);
        if (crowded) add('warn', no, 'W5', 'a line with two or more parenthetical remarks; put the qualifier in front of its noun as one block (「研修を修了した経験5年以上の点検員が判定」), or say it aloud', crowded.el);
        else if (withParen.length >= 3) add('warn', no, 'W5', `${withParen.length} lines with parentheses on one slide; a gloss in brackets on every line reads as translated — write the qualifier into the phrase, or say it aloud`, withParen[0].el);
        // D6: a line that stops on the continuative 〜ず (変わらず, 見られず) instead of ending
        const lineTexts = (el) => {      // the lines as written: math kept as a token, citation marks dropped
          const c = el.cloneNode(true);
          c.querySelectorAll('.ref').forEach((x) => x.remove());
          c.querySelectorAll('.katex').forEach((x) => x.replaceWith(document.createTextNode('$')));
          c.querySelectorAll('br').forEach((x) => x.replaceWith(document.createTextNode('\n')));
          c.querySelectorAll('.then').forEach((x) => x.prepend(document.createTextNode('\n')));
          return c.textContent.split('\n').map((t) => t.replace(/\s+/g, ' ').trim());
        };
        for (const l of lines) {
          const endsZu = lineTexts(l.el).find((t) => /[^ま必]ず$/.test(t));
          if (endsZu) { add('warn', no, 'D6', `「${endsZu.slice(-6)}」 stops on 〜ず, which leaves the line hanging; end it on 〜ない or a noun (「処理時間は変わらず」→「処理時間は変わらない」)`, l.el); break; }
        }
        if (labelled.length >= 2) add('warn', no, 'D5', `${labelled.length} bullets of the form 「見出し語：説明」 (e.g. 「〇〇の理由：…」); this label-and-explanation pattern reads as machine-made — state the point itself`, labelled[0]);
      }
    }
    if (role === 'main' || role === 'cover') {
      const known = new Set(['AI', 'IT', 'PC', 'ID', 'URL', 'OK', 'NG', 'UI', 'OS', 'CPU', 'GPU', 'PDF', 'HTML', 'CSS', 'API', 'SNS', 'QA', 'FAQ', 'USB', 'TV', 'DVD', 'GPS', 'ICT', 'LAN', 'VS', 'JPEG', 'PNG'
      ].concat((document.documentElement.dataset.knownAbbr || '').split(/[\s,]+/).filter(Boolean)));
      for (const n of tnodes) {
        if (n.parentElement.closest('.refs, .source, .ref, svg')) continue;
        for (const m of n.nodeValue.matchAll(/(?<![A-Za-z0-9])[A-Z][A-Z0-9]{1,5}(?![A-Za-z0-9])/g)) {
          if (known.has(m[0])) continue;
          if (!abbr.has(m[0])) abbr.set(m[0], []);
          abbr.get(m[0]).push({ no, el: n.parentElement });
        }
      }
    }

    /* ---------- A: forbidden styling ---------- */
    const slideText = tnodes.map((n) => n.nodeValue).join('\n');
    const leftover = slideText.match(/ここに一言|見出し語を書く|YYYY\/M\/D|YYYY年M月D日|会議・発表会の名称|^発表タイトル$/m);
    if (leftover) add('warn', no, 'S9', `template text is still on the slide: "${leftover[0]}"`, slide);
    else if (/YYYY/.test(slide.dataset.date || '')) add('warn', no, 'S9', 'the footer date is still the template text; set sk.Deck(…, date="2026/9/16")', slide);
    const emoji = slideText.match(/\p{Emoji_Presentation}|️/u);
    if (emoji) add('error', no, 'A1', `emoji / pictograph "${emoji[0]}" in text; remove it`, slide);
    const raw = slideText.match(/\*\*[^*\s][^*\n]*\*\*|\\(?:textbf|tb|emph|item|begin|end|cite|ref|frac)\b|<\/?(?:br|b|strong|span|div|p|li|ul|em|sub|sup)\b[^>]*>|&(?:nbsp|amp|lt|gt|quot);|\$[^$\n]{1,80}\$|^#{1,4}\s|`[^`\n]+`/m);
    if (raw) add('error', no, 'A8', `raw markup is showing as text: ${JSON.stringify(raw[0].slice(0, 30))}`, slide);
    const families = new Set();
    for (const el of all) {
      if (el instanceof SVGElement) continue;
      const cs = getComputedStyle(el);
      if (cs.boxShadow !== 'none' && el !== slide) add('error', no, 'A2', 'box-shadow; flat only', el);
      if (cs.textShadow !== 'none') add('error', no, 'A2', 'text-shadow; flat only', el);
      if ((cs.filter && cs.filter !== 'none') || (cs.backdropFilter && cs.backdropFilter !== 'none')) add('error', no, 'A2', 'filter / backdrop-filter effect', el);
      if (/gradient/.test(cs.backgroundImage)) add('error', no, 'A3', 'gradient background; use a flat theme colour', el);
      if (cs.animationName !== 'none' || parseFloat(cs.transitionDuration) > 0) add('error', no, 'A5', 'animation / transition; slides are static', el);
      const rad = Math.max(...[cs.borderTopLeftRadius, cs.borderTopRightRadius, cs.borderBottomLeftRadius, cs.borderBottomRightRadius].map((v) => parseFloat(v) || 0));
      if (rad > 4) add('warn', no, 'A4', `rounded corners (${rad}${/%/.test(cs.borderTopLeftRadius) ? '%' : 'px'}); the theme is square-cornered`, el);
      const bw = ['Top', 'Right', 'Bottom', 'Left'].map((s) => (cs[`border${s}Style`] !== 'none' ? parseFloat(cs[`border${s}Width`]) || 0 : 0));
      const filled = !isTransparent(cs.backgroundColor) && cs.backgroundColor !== slideBg;
      if (filled && bw.every((w) => w > 0)) add('warn', no, 'A6', 'box has both a border and a fill; use one or the other', el);
      if (bw[3] >= 3 && bw[0] < 1 && bw[1] < 1 && bw[2] < 1) add('warn', no, 'A7', 'thick accent bar on the left edge of a box (a stock AI-slide ornament); remove it', el);
      if (filled) { const tok = PALETTE[cs.backgroundColor]; if (!tok) add('warn', no, 'T5', `fill colour ${cs.backgroundColor} is not a theme colour`, el); else if (/hot/.test(tok)) families.add(el.closest('.bar, .vbar') || el); }
      const st = el.getAttribute('style');
      if (st && !el.closest('.katex')) {
        const bad = st.split(';').map((d) => d.split(':')[0].trim()).filter(Boolean)
          .filter((p) => !p.startsWith('--') && !/^(width|height|max-width|max-height|min-width|min-height|aspect-ratio)$/.test(p));
        if (bad.length) add('warn', no, 'A9', `inline style sets ${bad.join(', ')}; the look comes from the theme only — use slidekit components instead of styling by hand`, el);
      }
    }

    /* ---------- L: layout ---------- */
    if (body && role !== 'cover' && role !== 'backmatter' && role !== 'disclosure') {
      const br = body.getBoundingClientRect();
      // vertical coverage: how much of the body height carries content
      const iv = [];
      const push = (r) => { const t = Math.max(r.top, br.top), b = Math.min(r.bottom, br.bottom); if (b - t > 1) iv.push([t, b]); };
      for (const b of blockInfo) if (body.contains(b.el)) push(b.u);
      for (const el of body.querySelectorAll('img, svg, table, .bar-track i, .vbar-plot i, .shares, .thing, .boxed')) if (visible(el)) push(el.getBoundingClientRect());
      let covered = 0, maxGap = 0;
      if (iv.length) {
        iv.sort((a, b) => a[0] - b[0]);
        let [s, e] = iv[0];
        for (const [t, b] of iv) { if (t > e) { covered += e - s; maxGap = Math.max(maxGap, t - e); s = t; e = b; } else e = Math.max(e, b); }
        covered += e - s;
      }
      const fill = covered / br.height;
      // share of the body area taken by figures
      let figArea = 0;
      for (const f of figs) {
        const parts = f.matches('.math-block') ? [f] : [...f.querySelectorAll('img, svg, .bars, .vbars, .shares')].filter(visible);
        const boxes = f.matches('.flow') ? [f] : (parts.length ? parts : [f]);
        for (const p of boxes) { const r = p.getBoundingClientRect(); figArea += r.width * r.height; }
      }
      const figShare = figArea / (br.width * br.height);

      // balance — where the weight of the slide sits.
      // Figures, equations, the conclusion line and the frame are centred. A list is flush left at
      // the margin (it is never centred as a block), so it has to carry its width: a list of stubs
      // leaves the right half of the slide empty. A list inside a column is a sub-element and is
      // centred in its column.
      const inkOf = (root) => {
        const rs = [];
        for (const b of blockInfo) {
          if (!root.contains(b.el) || b.el.closest('.chart, svg, .flow, .tbl')) continue;
          for (const l of b.lines) rs.push(l);
        }
        const sel = 'img, svg.dia, .bars, .vbars, .shares, .flow, .tbl, .boxed, .arrow-down, .math-block .katex-html';
        for (const el of [root, ...root.querySelectorAll(sel)]) {
          if ((el === root && !el.matches(sel)) || !visible(el)) continue;
          rs.push(el.getBoundingClientRect());
        }
        return rs;
      };
      // a block counts as its bounding box, weighted by what is drawn in it
      let mass = 0, moment = 0;
      const measure = (blk) => {
        const rs = inkOf(blk);
        if (!rs.length) return null;
        const L = Math.min(...rs.map((r) => r.left)), R = Math.max(...rs.map((r) => r.right));
        const a = rs.reduce((s, r) => s + (r.right - r.left) * (r.bottom - r.top), 0);
        mass += a; moment += a * ((L + R) / 2);
        return { L, R, rs };
      };
      // a figure / equation / frame that is not on the centre line
      const offAxis = (blk, frame) => {
        const m = measure(blk);
        if (!m) return;
        const off = ((m.L + m.R) / 2 - (frame.left + frame.right) / 2) / frame.width;
        if (Math.abs(off) > 0.04 && m.R - m.L < 0.92 * frame.width) {
          add('warn', no, 'L6', `this block sits ${Math.round(Math.abs(off) * 100)}% of the width to the ${off < 0 ? 'left' : 'right'} of the centre line; figures, equations and frames are centred — a block pushed to one side leaves the other side empty`, blk);
        }
      };
      // a flush-left list that does not carry its width
      const sparse = (blk, frame) => {
        const m = measure(blk);
        if (!m) return;
        const reach = (m.R - frame.left) / frame.width;
        // the first lines of the bullets only: a consequence line (→) is meant to be short
        const own = [...blk.querySelectorAll('li')].flatMap((li) => lineBoxes(li));
        const lineReach = (own.length ? own : m.rs).map((r) => (r.right - frame.left) / frame.width);
        const mean = lineReach.reduce((s, v) => s + v, 0) / lineReach.length;
        const need = wide ? 0.65 : 0.7;
        if (reach < need) {
          add('warn', no, 'L6', `the list reaches only ${Math.round(reach * 100)}% of the way across the slide; a list is flush left, so short bullets leave the right side empty and the slide tips to the left. Write fuller bullets — each a line that carries a fact with its number, condition or source (aim for ${Math.round(need * 100)}–95% of the width; do not pad with adjectives) — or use another form: one centred conclusion line, or the list beside the figure in cols()`, blk);
        } else if (mean < 0.5 && lineReach.length >= 3) {
          add('info', no, 'L6', `one long bullet among stubs (the lines reach ${Math.round(mean * 100)}% of the width on average); bullets of similar length make a calmer block`, blk);
        }
      };
      const isList = (el) => el.matches('.points, .summary');
      const walk = (blk, frame, sub) => {
        if (!visible(blk)) return;
        if (blk.matches('.cols')) { for (const c of blk.children) for (const inner of c.children) walk(inner, c.getBoundingClientRect(), true); }
        else if (blk.matches('.therefore')) { for (const inner of blk.children) walk(inner, frame, true); }   // its list is centred as a block
        else if (isList(blk) && !sub) sparse(blk, frame);
        else offAxis(blk, frame);
      };
      for (const blk of body.children) walk(blk, br, false);
      const cx = mass ? (moment / mass - (br.left + br.right) / 2) / br.width : 0;
      if (figs.length && Math.abs(cx) > 0.08) add('warn', no, 'L6', `the weight of the slide sits ${Math.round(Math.abs(cx) * 100)}% of the width to the ${cx < 0 ? 'left' : 'right'} of centre; one side is empty — fuller bullets, a wider figure, or two columns of similar weight`, body);
      metrics[no] = Object.assign(metrics[no] || {}, { fill: Math.round(100 * fill), fig: Math.round(100 * figShare), gap: Math.round(maxGap), cx: Math.round(100 * cx) });
      if (role === 'main' && !textOnly) {
        if (figs.length && figShare < 0.25) add('warn', no, 'F2', `the figure takes only ${Math.round(100 * figShare)}% of the body; make it the main thing (larger picture, fewer words) — aim for half the body or more`, figs[0]);
        if (fill < 0.5) add('warn', no, 'L3', `content covers only ${Math.round(100 * fill)}% of the body height; the slide looks empty — enlarge the figure or merge this slide into a neighbour (never pad with filler text)`, body);
      }
    }

    /* ---------- I: images ---------- */
    for (const img of slide.querySelectorAll('img')) {
      if (!visible(img)) continue;
      const r = img.getBoundingClientRect();
      if (!img.naturalWidth) { add('error', no, 'I1', `image failed to load: ${img.getAttribute('src')}`, img); continue; }
      const isSvg = /\.svg(\?|#|$)/i.test(img.currentSrc || img.src);
      const fit = getComputedStyle(img).objectFit;
      const natural = img.naturalWidth / img.naturalHeight;
      if (fit === 'fill' && Math.abs(r.width / r.height - natural) / natural > 0.02) add('error', no, 'I3', 'image is stretched (aspect ratio changed); set only width OR height', img);
      const scale = r.width / img.naturalWidth;
      if (isSvg) {
        if (Math.abs(scale - 1) > 0.03) add('warn', no, 'I4', `SVG figure is shown at ${scale.toFixed(2)}x; text inside it is scaled too — regenerate the figure at its display size`, img);
      } else if (img.naturalWidth / r.width < 1.3) {
        add('warn', no, 'I2', `raster image has ${(img.naturalWidth / r.width).toFixed(1)} pixels per slide pixel; it will look soft when projected (want >= 1.5). Get a larger original (the full-size version of a paper's figure, the source file); if none exists, crop to the part the slide needs and show it no wider than about twice its pixel width, then silence I2 on this slide with the reason (figures.md §3)`, img);
      }
    }
    for (const svg of slide.querySelectorAll('svg.dia')) {
      const vb = svg.viewBox && svg.viewBox.baseVal;
      if (!vb || !vb.width) { add('warn', no, 'I4', 'inline diagram has no viewBox', svg); continue; }
      const scale = svg.getBoundingClientRect().width / vb.width;
      if (Math.abs(scale - 1) > 0.03) add('warn', no, 'I4', `inline diagram is drawn at ${scale.toFixed(2)}x (it is wider than its place); set width/height to the size it is shown at`, svg);
    }

    metrics[no] = Object.assign(metrics[no] || {}, { chars: proseChars, msgChars: msg ? Math.round(units(msg.textContent.replace(/\s+/g, ''))) : 0 });
    // every number printed on the slide, with the text block it sits in (for the number check)
    if (role !== 'backmatter') {
      const seenBlocks = new Set();
      for (const b of blockInfo) {
        if (b.el.closest('.refs, .ref, .katex') || seenBlocks.has(b.el)) continue;
        seenBlocks.add(b.el);
        const clone = b.el.cloneNode(true);
        clone.querySelectorAll('.ref, .notes, .katex-html, annotation').forEach((x) => x.remove());
        const text = clone.textContent.replace(/\s+/g, ' ').trim();
        const toks = text.match(/[−+±-]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)%?/g);
        if (toks) numbers.push({ slide: no, tokens: toks, context: text.slice(0, 70) });
      }
      // the texts inside plots made with save_fig (tick labels, values, p values), kept by slidekit
      for (const pf of slide.querySelectorAll('figure[data-plot]')) {
        const text = (pf.dataset.text || '').replace(/\s+/g, ' ').trim();
        const toks = text.match(/[−+±-]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)%?/g);
        if (toks) numbers.push({ slide: no, tokens: toks, context: `(plot) ${text.slice(0, 64)}` });
      }
    }
  });

  /* ---------- deck-level ---------- */
  const deck = (sev, rule, msg) => findings.push({ sev, slide: 0, rule, msg, where: '' });
  if (headBottoms.length) {
    const freq = new Map();
    for (const h of headBottoms) freq.set(h.y, (freq.get(h.y) || 0) + 1);
    const mode = [...freq.entries()].sort((a, b) => b[1] - a[1])[0][0];
    for (const h of headBottoms) if (Math.abs(h.y - mode) > 0.5) add('error', h.no, 'L5', `heading rule sits at y=${h.y}px but at ${mode}px on other slides; do not restyle .head`, h.el);
  }
  for (const [t, nos] of headings) if (nos.length > 1) deck('warn', 'S5', `slides ${nos.join(', ')} share the heading "${t.slice(0, 30)}"; tell them apart with a topic: 「${t} - …」 or 「${t}(1)」「${t}(2)」`);
  for (const [tok, uses] of abbr) {
    if (uses.length === 1) add('info', uses[0].no, 'D4', `abbreviation "${tok}" appears once in the main deck; spell it out (abbreviate only what is used 2+ times), or pass known_abbr=[…] to sk.Deck`, uses[0].el);
  }
  const lang = document.documentElement.getAttribute('lang');
  if (!lang) deck('warn', 'S6', '<html> has no lang attribute; create the deck with sk.Deck(…, lang="ja") so lines break at phrase boundaries');
  const minutes = parseFloat(document.documentElement.dataset.minutes || '');
  const mains = slides.filter((s) => ['main', 'cover'].includes(roleOf(s)));
  if (Number.isFinite(minutes)) {
    const n = mains.length;
    const hi = Math.ceil(minutes * 1.3), lo = Math.floor(minutes * 0.6);
    if (n > hi) deck('warn', 'K1', `${n} main slides for a ${minutes}-minute talk (more than ${hi}); cut or move slides to the appendix`);
    if (n < lo) deck('warn', 'K1', `${n} main slides for a ${minutes}-minute talk (fewer than ${lo}); slides are probably overloaded — one figure and one point per slide`);
    // a disclosure (COI) is on screen for a few seconds: it counts in the time, not in the count
    const secs = mains.concat(slides.filter((s) => roleOf(s) === 'disclosure')).map((s) => parseFloat(s.dataset.sec || ''));
    if (secs.every(Number.isFinite)) {
      const sum = secs.reduce((a, b) => a + b, 0);
      if (Math.abs(sum - minutes * 60) > minutes * 60 * 0.07) deck('warn', 'K2', `sec= adds up to ${sum}s but the talk is ${minutes * 60}s`);
    } else if (secs.some(Number.isFinite)) deck('info', 'K2', 'some main slides have sec= and some do not; set it on all of them');
  } else deck('info', 'K1', 'the talk length is not set (sk.Deck(…, minutes=…)); slide-count check skipped');
  // the parts of the talk must be contiguous
  const seen = new Set();
  let prev = null;
  for (const k of sections) { if (k !== prev && seen.has(k)) { deck('warn', 'K3', `the part "${k}" resumes after another part; keep the slides of one part together`); break; } seen.add(k); prev = k; }
  for (const [part, ts] of topics) {
    if (new Set(ts).size < 2) continue;
    const kind = /方法|手法|実験|手順|設計/.test(part)
      ? 'the stages of the procedure that a listener follows, all of one kind (装置 / 手順 / 測定 / 分析, or 全体像 / 検出 / 優先度の計算)'
      : 'the kind of analysis or measure (精度 / 速度 / 頑健性)';
    deck('info', 'S10', `topics of 「${part}」: ${[...new Set(ts)].join(' / ')} — check that they name the same kind of thing at one level — ${kind} — not items of content (story.md §4)`);
  }
  if (mainCount >= 4 && textOnlyCount > Math.max(2, Math.round(mainCount * 0.25))) deck('warn', 'F3', `${textOnlyCount} of ${mainCount} main slides are text-only; words alone do not reach the audience — keep text-only for 目的 and まとめ`);
  if (boxedSlides > 2) deck('warn', 'W3', `${boxedSlides} slides carry a boxed statement; the frame is for the one statement of the talk (the purpose)`);
  slides.forEach((s, i) => {
    const sec = parseFloat(s.dataset.sec || '');
    if (roleOf(s) !== 'main' || !Number.isFinite(sec)) return;
    if (sec < 25) add('warn', i + 1, 'K2', `only ${sec}s planned for this slide; a slide shown for under 25s should be merged into a neighbour`, s);
    if (sec > 150) add('info', i + 1, 'K2', `${sec}s planned for one slide; check it is not carrying two points`, s);
  });

  // A11: the deck may not carry its own CSS (only an accent override on :root)
  for (const st of document.querySelectorAll('style')) {
    const css = st.textContent.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\s+/g, '');
    if (css && !/^(:root\{(--accent|--accent-tint):[^;{}]+(;(--accent|--accent-tint):[^;{}]+)*;?\})+$/.test(css)) {
      deck('warn', 'A11', 'the deck carries its own <style> rules; the look comes only from the theme (Deck(accent=(…)) may change the accent colour, nothing else)');
    }
  }
  // A12: classes that the theme does not define have no effect
  if (cfg && cfg.knownClasses && cfg.knownClasses.length) {
    const known = new Set(cfg.knownClasses);
    const unknown = new Map();
    slides.forEach((s, i) => {
      for (const el of [s, ...s.querySelectorAll('[class]')]) {
        if (el.closest('.katex')) continue;
        for (const c of el.classList) if (!known.has(c) && !unknown.has(c)) unknown.set(c, { no: i + 1, el });
      }
    });
    for (const [c, u] of unknown) add('warn', u.no, 'A12', `class "${c}" is not defined by the theme, so it does nothing; build the slide with slidekit components (references/layouts.md)`, u.el);
  }

  return { findings, suppressed, scale: SCALE, metrics, numbers };
}

/* ------------------------------------------------------------------------------------------ */
const main = async () => {
  const deck = resolveDeck(args._[0]);
  const { browser } = await launch();
  try {
    const { page, problems } = await openDeck(browser, deck.html);
    const info = await deckInfo(page);
    if (!info.n) throw new Error('no <section class="slide"> found in the deck');
    // classes defined by the linked stylesheets (read from disk: file:// sheets are opaque to page scripts)
    const hrefs = await page.evaluate(() => [...document.querySelectorAll('link[rel="stylesheet"]')].map((l) => l.href));
    const knownClasses = new Set(['slide', 'appendix', 'backmatter']);
    const themeIssues = [];
    for (const href of hrefs) {
      let file;
      try { file = fileURLToPath(href); } catch { continue; }
      if (!fs.existsSync(file)) continue;
      const css = fs.readFileSync(file, 'utf8');
      for (const m of css.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/\.(-?[_a-zA-Z][\w-]*)/g)) knownClasses.add(m[1]);
      const ref = path.join(SKILL_DIR, 'assets', 'theme', path.basename(file));
      if (/^(slide|ratio-[\w]+)\.css$/.test(path.basename(file)) && fs.existsSync(ref)) {
        const norm = (s) => s.replace(/\r\n/g, '\n');
        if (norm(css) !== norm(fs.readFileSync(ref, 'utf8'))) {
          themeIssues.push(`${path.basename(file)} differs from the skill's theme (edited or outdated); never edit the theme — run init.mjs <deck> --refresh`);
        }
      }
    }
    if (!hrefs.some((h) => /slide\.css/.test(h))) themeIssues.push('deck does not link theme/slide.css');
    const libCopy = path.join(deck.dir, 'slidekit.py');
    const libRef = path.join(SKILL_DIR, 'assets', 'slidekit.py');
    if (fs.existsSync(libCopy) && fs.existsSync(libRef)) {
      const norm = (s) => s.replace(/\r\n/g, '\n');
      if (norm(fs.readFileSync(libCopy, 'utf8')) !== norm(fs.readFileSync(libRef, 'utf8'))) {
        themeIssues.push("slidekit.py differs from the skill's library (edited or outdated); never edit it — run init.mjs <deck> --refresh");
      }
    }

    const res = await page.evaluate(lintInPage, { knownClasses: [...knownClasses] });
    for (const p of [...new Set(problems)]) res.findings.push({ sev: 'error', slide: 0, rule: 'R1', msg: p, where: '' });
    for (const t of themeIssues) res.findings.push({ sev: 'error', slide: 0, rule: 'R2', msg: t, where: '' });

    const order = { error: 0, warn: 1, info: 2 };
    let list = res.findings.sort((a, b) => a.slide - b.slide || order[a.sev] - order[b.sev] || a.rule.localeCompare(b.rule));
    if (args['no-info']) list = list.filter((f) => f.sev !== 'info');
    const count = (s) => res.findings.filter((f) => f.sev === s).length;
    const summary = { errors: count('error'), warnings: count('warn'), info: count('info'), suppressed: res.suppressed };

    fs.mkdirSync(path.join(deck.dir, 'out'), { recursive: true });
    fs.writeFileSync(path.join(deck.dir, 'out', 'lint.json'), JSON.stringify({ deck: info, summary, metrics: res.metrics, findings: res.findings }, null, 2));

    const numLines = ['# Numbers on the slides', '',
      'Every number that is printed on a slide, taken from the rendered deck. Check each against its source.', '',
      '| p. | numbers | where |', '|---|---|---|'];
    for (const n of res.numbers) numLines.push(`| ${n.slide} | ${n.tokens.join(', ')} | ${n.context.replace(/\|/g, '/')} |`);
    fs.writeFileSync(path.join(deck.dir, 'out', 'numbers-on-slides.md'), `${numLines.join('\n')}\n`);

    if (args.json) {
      console.log(JSON.stringify({ summary, findings: list }, null, 2));
    } else {
      const rel = path.relative(process.cwd(), deck.html) || deck.html;
      const nMain = info.slides.filter((s) => s.role === 'main' || s.role === 'cover').length;
      console.log(`make-slides lint — ${rel}`);
      console.log(`  ${info.n} slides (${nMain} main incl. cover), ${info.w}x${info.h}px${info.minutes ? `, ${info.minutes} min` : ''}`);
      const tag = { error: 'ERROR', warn: 'WARN ', info: 'info ' };
      let last = -1;
      for (const f of list) {
        if (f.slide !== last) { console.log(f.slide ? `\n  p.${f.slide}  ${info.slides[f.slide - 1].title.slice(0, 40)}` : '\n  deck'); last = f.slide; }
        console.log(`    ${tag[f.sev]} ${f.rule.padEnd(3)} ${f.msg}${f.where ? `\n              ← ${f.where}` : ''}`);
      }
      if (args.metrics) {
        console.log('\n  metrics   (fig = share of the body area taken by figures; fill = share of the body height that carries content;\n             cx = how far the weight of the slide sits from the centre line, in % of the width, − = left; text = running text)');
        for (const sl of info.slides) {
          const m = res.metrics[sl.n];
          if (!m || sl.role === 'cover') continue;
          const pc = (v) => (v == null ? '  -' : String(v).padStart(3));
          const cx = m.cx == null ? '  -' : `${m.cx > 0 ? '+' : m.cx < 0 ? '−' : ' '}${String(Math.abs(m.cx)).padStart(2)}`;
          console.log(`    p.${String(sl.n).padEnd(3)} fig ${pc(m.fig)}% | fill ${pc(m.fill)}% | cx ${cx}% | text ${String(m.chars).padStart(3)} chars | message ${String(m.msgChars).padStart(2)} chars${sl.sec ? ` | ${sl.sec}s` : ''}  ${sl.title.slice(0, 22)}`);
        }
      }
      console.log(`\n  summary: ${summary.errors} error(s), ${summary.warnings} warning(s), ${summary.info} info${summary.suppressed ? `, ${summary.suppressed} suppressed` : ''}`);
      if (!summary.errors && !summary.warnings) console.log('  clean.');
    }
    process.exitCode = summary.errors || (args.strict && summary.warnings) ? 1 : 0;
  } finally {
    await browser.close();
  }
};

main().catch((e) => { console.error(`lint failed: ${e.message}`); process.exit(2); });
