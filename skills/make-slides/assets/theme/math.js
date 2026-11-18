// Renders TeX in the deck with the vendored KaTeX. Load order (all with `defer`):
//   theme/vendor/katex/katex.min.js -> theme/vendor/katex/auto-render.min.js -> theme/math.js
// Inline: $…$ or \(…\)    Display: $$…$$ or \[…\]
// build.mjs / lint.mjs wait for window.deckReady before measuring anything.
window.deckReady = (async () => {
  if (typeof renderMathInElement === 'function') {
    renderMathInElement(document.body, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '\\[', right: '\\]', display: true },
        { left: '\\(', right: '\\)', display: false },
        { left: '$', right: '$', display: false },
      ],
      ignoredClasses: ['notes'],
      throwOnError: false,
    });
  }
  await document.fonts.ready;
})();
