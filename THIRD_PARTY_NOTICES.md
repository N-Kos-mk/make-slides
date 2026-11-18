# Third-party notices

This repository bundles the following third-party works. Each stays under its own licence; the
rest of the repository is under the MIT License in [LICENSE](LICENSE).

## Bundled

| Component | Location | Licence |
|---|---|---|
| Noto Sans JP (Light, Regular, Bold; WOFF2) | `skills/make-slides/assets/theme/fonts/` | SIL Open Font License 1.1 — full text in `OFL.txt` in the same folder |
| KaTeX 0.16.47 (CSS, scripts, fonts) | `skills/make-slides/assets/theme/vendor/katex/` | MIT — `LICENSE` in the same folder |
| Phosphor Icons (`video-camera-fill`) | `skills/make-slides/assets/gallery/figures/icons/` | MIT — recorded in `LICENSES.md` in the same folder |
| Material Symbols (`desktop-windows`) | `skills/make-slides/assets/gallery/figures/icons/` | Apache License 2.0 — recorded in `LICENSES.md` in the same folder |

The other images of the gallery are drawn by `skills/make-slides/assets/gallery/make_figures.py`
(the PNG images) and `skills/make-slides/assets/gallery/deck.py` (the SVG plots), and are part of
this repository.

## Installed by the user (not bundled)

`npm install --prefix skills/make-slides/scripts` installs these packages; they are not part of
this repository:

| Package | Licence |
|---|---|
| playwright-core | Apache License 2.0 |
| @iconify-json/healthicons (Health Icons) | MIT |
| @iconify-json/material-symbols (Material Symbols) | Apache License 2.0 |
| @iconify-json/ph (Phosphor Icons) | MIT |

When an icon is fetched into a deck with `scripts/icons.mjs get`, the licence of its set is
recorded in that deck's `figures/icons/LICENSES.md`.
