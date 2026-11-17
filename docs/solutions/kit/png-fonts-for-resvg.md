---
title: PNG text needs complete, unwrapped fonts handed to resvg explicitly
module: kit/atelier_kit/output.py
category: kit
date: 2026-11-17
issue: 7
tags: [resvg, fonts, png, determinism]
---

# PNG text needs complete, unwrapped fonts handed to resvg explicitly

## Problem

`look` returns a PNG rasterised from the kit's SVG. The PNG must not depend on the machine's fonts, and the SVGs name `IBM Plex Mono`. Three things go wrong quietly, each producing a PNG with no error:

1. **resvg does not read WOFF2.** The faces in `docs/assets/fonts/` are WOFF2, so pointing resvg at them loads nothing and every `<text>` renders blank.
2. **The docs' Latin subsets are too small for drawings.** They lack `→ ← ≤ ≥ ≠` and box-drawing characters, which diagram labels use constantly.
3. **The subset Medium face cannot be matched by weight.** Its name table says family `IBM Plex Mono Medium` with no typographic family, so `font-family="IBM Plex Mono" font-weight="500"` falls back to Regular.

## Solution

- Vendor the complete Regular and Medium faces from the upstream `@ibm/plex-mono` npm package into `kit/atelier_kit/fonts/`, unwrapped from WOFF2 to TrueType by `scripts/vendor-kit-fonts.py` (pinned version and hash; reproducible bytes).
- Call resvg with `skip_system_fonts=True`, those files as `font_files`, and every generic family set to `IBM Plex Mono`.
- A test compares the PNG with and without its `<text>` elements, so fonts that fail to load fail the suite instead of shipping blank drawings.

## Still true

A character the face lacks (CJK, emoji) draws as an empty box in the PNG and there is no fallback font. A tool that needs another weight or face must add it to the vendoring script; naming an unvendored family in SVG silently falls back to Plex Mono Regular.
