# Pranoti v0.160-beta — re-trace log

Clean-photo re-trace of the 69 handwriting glyphs + handwritten punctuation (83 glyphs total), replacing the blurry-photo traces that v0.130–v0.150 carried. Built 2026-11-26.

**TTF:** `Pranoti-Regular-v0.160-beta.ttf` — SHA-256 `2a50aafe90584e1868fd6dd85c8e03f61cbab46b7ae3333efc9d8e25789ba614`, 652 glyphs, cmap 204, UPM 1536, family "Pranoti".
**Base:** v0.150-beta (`679ba515…40c93`), verified by checksum before the build. Only the 83 glyphs below changed; GSUB/GPOS/GDEF, cmap, glyph order, advances, anchors, the 4 new glyphs (U+0980, U+09FB, U+09FC, U+09FE) and all ~375 conjunct ligatures are untouched.

## Source photos

- Vowels (11 × best-of-7 from 4 full-sheet photos): `1000036047_1`, `1000038364_2`, `1000036048_3`, `1000036049_4`. Close-ups `1000036051_6`, `1000036052_7` used for stroke detail (not as trace sources). For each vowel the cleanest, most characteristic of the 28 instances was chosen by ink area / aspect / stroke width vs the row median + an edge-touch penalty; the 28 instances per vowel were near-identical (scores 0.004–0.018), so the choice is among near-equals. Chosen cells are in `specimens/chosen-vowels-v0.160.png` and `vowel_selection.json`.
- Consonants / signs / digits / punctuation: photo 16 (`1000033792_16`) only. Photo 17 is backup only (a dark strip on its left edge is read as an extra column). Photos 8/9 are the same sheet upside down and were not used.
- Photo 5 (the 4-glyph conjunct sheet) was NOT used — names unconfirmed. Conjuncts are the later v0.170 phase and were not touched.

## Method (tools/)

- `tools/grid_detect.py` + `tools/extract_cells.py`: 399 cells, no warnings; contact sheets visually verified (every cell maps to the right glyph).
- `tools/measure_targets.py` → `targets.json`: the v0.150 per-glyph TRUE INK boxes (rasterised at 1536 px; the 56 letters from `size-transforms.json` `ink_after`, the 13 signs + 14 punctuation measured from the v0.150 TTF).
- `tools/trace_glyphs.py`: Otsu threshold within each cell, keep only components touching the thr=100 ink mask (paper texture/crease shadows never reach 100); potrace `-s` to SVG; SVG parsed directly (all `<path>` elements; M/m, C/c, L/l, Z/z with implicit repetition); cubic → quadratic via fontTools Cu2QuPen (error 1.0 px).
- **Fit (uniform scale, no distortion):** s = target height / trace TRUE-INK height; translate so the scaled ink top = target top, and letters/punctuation centre-x = target centre-x (v0.150 rule), while signs/marks align their LEFT edge = target left edge (v0.130 rule — preserves the mark's ink position relative to its fixed GPOS anchor; centre alignment would have shifted it by half the width change). Advances unchanged; hmtx lsb = new outline xMin (v0.150 precedent).
- `tools/build_pranoti_v0160_beta.py`: clean_glyph (verbatim from v0.130) + polish_glyph (verbatim from v0.140: one pass 7-point binomial kernel, move cap 5, near-dup merge ≤1.0) applied to the new glyphs only; name table v0.160-beta; `head.fontRevision = 0.160`.
- `tools/verify_pranoti_v0160_beta.py` → `checks/`; `tools/render_specimens_v0160.py` → `specimens/`; `tools/fontforge_validate.py` → `checks/fontforge-validate-v0.160.txt`.

## Findings — read this before judging the font

1. **His clean handwriting is genuinely ~25% wider than the v0.150 font** (median width ratio ≈ 1.25, range 0.91–1.60 for letters). This is NOT a photo artefact: the aspect ratio of each vowel agrees across all 4 independent photos to within 1–2% (e.g. অ mean 1.21, per-photo means 1.195–1.216). The old blurry-photo traces were narrower (blur + the old pipeline eroded them). The new glyphs keep their v0.150 advances, so text is denser — the letters fill more of each advance and the headline bar reads more solid. Negative side bearings are normal for this font (v0.150 letters already had them, e.g. bn_i −75, bn_ha −83); the wider traces push them further (worst bn_jha −267, bn_ha −309), but nothing collides: the matra is meant to join across letters. If the owner finds the text too dense, the fix is wider advances, not narrower glyphs.
2. **Ink-top fit is exact.** After the first build measured ink-top errors of −11 to −56 units, the cause was found: the fit had used the control-point bbox, whose off-curve points overshoot the real ink top by up to ~3 px (the v0.150 SIZE-LOG lesson). The fit now samples the potrace cubic curves for the TRUE ink bbox. Final rasterised ink-top error: worst |5| units over all 83 glyphs (all 0 to −5).
3. **Contour winding was reversed and fixed.** The y-flip from image coords to font coords reversed every contour's winding (FontForge validate bit 3, wrong direction, on all 83). The trace step now reverses each contour's point order; FontForge bit 3 is gone from all 83. (The rendered shapes were never wrong — outer and holes reversed together — but the font is now conventionally correct.)
4. **bn_anusvara (ং): stray swoosh removed.** The cell contains a detached pen flick below the loop, sitting in the inter-row gap; the v0.150 glyph carried the same stray (contour 0). The swoosh contour is dropped; the loop alone is fitted to the v0.150 loop-only box (83, 618, 447, 1098). The new ং is a clean wide oval loop. If the owner says the swoosh belongs to his ং, it is one contour to add back.
5. **bn_okaar (ো) and bn_aukaar (ৌ) are narrow single-stroke forms** (w 0.52 / 0.64): he writes ো/ৌ as one wavy stroke, not the font's wide two-part ে+া. Kept as written. In context (কো, কৌ) they read correctly — see the writing demo — but they look very different from the old ones, so the owner should judge them there.
6. **bn_candrabindu (ঁ) is the closest match** (w 0.98); the marks' left edges are preserved by the left-align rule, so their GPOS anchor registration is unchanged (lsb of bn_ikaar −51 → −46, bn_iikaar −786 → −784).
7. **Honest assessment, per glyph:** every one of the 83 new traces is visibly cleaner and bolder than the v0.150 trace of the same letter — none is worse. The most dramatic improvements are the consonants whose old traces were wispy or broken (খ, ছ, ঝ, হ, য়, ১, ৩, ণ, ধ, থ). The ones that changed character rather than just cleaning up are ো/ৌ (narrower), ং (swoosh gone), । (thinner), / (longer diagonal) — flagged in the table below.

## Verification (checks/)

- **HarfBuzz 22/22 samples** identical to v0.120 (glyph names, clusters, advances); the 3 reviewed candrabindu offsets exact: কাঁ −450,+125; চাঁ −278,+125; ক্ষ্মাঁ −632,+125. (`checks/harfbuzz-22-samples-v0.160.tsv`)
- **Consonant-pair grid 1,369/1,369** identical to v0.120; 0 `.notdef`. (`checks/consonant-pair-grid-v0.160.tsv`)
- **Ink boxes:** rasterised true ink top vs v0.150 target, worst |5| units over 83 glyphs. (`checks/ink-boxes-v0.160.tsv`)
- **Tables vs v0.120:** only GPOS, glyf, hmtx, cmap, head, name, maxp, loca differ; GSUB, GDEF, OS/2, attribution and license name records preserved. hhea: advances/ascent/descent/lineGap/caret/numberOfHMetrics unchanged; minLeftSideBearing −1128 and xMaxExtent 2300 unchanged; minRightSideBearing moved −654 → −1155 (the wider re-traced marks) and matches the value derived from the font's own glyf/hmtx data.
- **OTS:** "File sanitized successfully!" — clean. (`checks/ots-v0.160.txt`)
- **FontForge 20230101 validate:** 85 glyphs flagged — all 83 re-traced glyphs with bit 5 only (value 32, no FontForge anchor points, expected for traced glyphs, same as v0.150), plus bn_anji (32, pre-existing) and bn_vedic_anusvara (36, pre-existing). Near-duplicate-point flags (bit 2, value 4) fell from 28 glyphs in v0.150 to 1 in v0.160 (bn_vedic_anusvara, untouched) — the new traces are cleaner. Wrong-direction flags (bit 3, value 8): 0. (`checks/fontforge-validate-v0.160.txt`)
- **Polish:** drift ≤ 5 units on every glyph (capped), 0 near-duplicate points merged, clean_glyph removed 0–3 duplicate points per glyph. (`build-log-v0.160.json`)
- **Visual check (looked at, not just generated):** `specimens/before-after-v0.160.png` (all 83, v0.150 grey over v0.160 black, baseline/headline guides — every top sits on its headline), `specimens/v0160-writing-demo.png` (headline, paragraph, alphabet, digits, punctuation, conjunct words, candrabindu words, side-by-side paragraph), `specimens/closeup-v0.160.png` (12 most-changed glyphs at 200 px), `specimens/matched-v0.150-v0.160-review.png` (22 samples at 12/16/24/32 px), `specimens/chosen-vowels-v0.160.png` (the 11 traced vowel cells).

## Per-glyph table

`src` = source photo (first 10 chars of the file name) + row/col in the sheet. `s` = uniform fit scale. `w` = fitted ink width / v0.150 target width (1.00 = same width). `top` = rasterised ink-top error vs target in font units (0 = exact; all 0 to −5). `pts` = points after polish. `lsb` = hmtx left side bearing before → after (advance unchanged). `drop` = contours dropped (only bn_anusvara: the stray swoosh).

| glyph | char | src | s | w | top | pts | lsb | drop | notes |
|---|---|---|---|---|---|---|---|---|---|
| bn_a | অ | 1000036047_1 r1c3 | 23.80 | 1.05 | -3 | 155 | -37→-69 | 0 |  |
| bn_aa | আ | 1000036047_1 r2c2 | 24.47 | 1.21 | -5 | 175 | -25→-199 | 0 |  |
| bn_i | ই | 1000036048_3 r3c5 | 27.45 | 1.22 | -4 | 141 | -61→-180 | 0 |  |
| bn_ii | ঈ | 1000036048_3 r4c1 | 21.81 | 0.99 | -4 | 168 | -48→-36 | 0 |  |
| bn_u | উ | 1000036049_4_24mu.jpg r5c2 | 21.14 | 0.94 | -4 | 160 | -35→-12 | 0 |  |
| bn_uu | ঊ | 1000036048_3 r6c5 | 22.73 | 0.96 | -4 | 172 | -60→-41 | 0 |  |
| bn_ri | ঋ | 1000036047_1 r7c2 | 23.56 | 1.35 | -3 | 185 | 46→-165 | 0 |  |
| bn_e | এ | 1000036047_1 r8c3 | 25.69 | 1.27 | -4 | 77 | 79→-52 | 0 |  |
| bn_ai | ঐ | 1000036047_1 r9c3 | 26.09 | 1.27 | -3 | 159 | 60→-94 | 0 |  |
| bn_o | ও | 1000036049_4_24mu.jpg r10c5 | 22.18 | 1.15 | -2 | 101 | 39→-30 | 0 |  |
| bn_au | ঔ | 1000036047_1 r11c1 | 24.12 | 1.10 | -4 | 126 | 75→24 | 0 |  |
| bn_ka | ক | 1000033792_16 r1c1 | 17.61 | 1.16 | 0 | 154 | -14→-107 | 0 |  |
| bn_kha | খ | 1000033792_16 r1c2 | 16.89 | 1.44 | -4 | 159 | 27→-174 | 0 | w 1.44 — visibly cleaner and bolder than the wispy v0.150 trace. |
| bn_ga | গ | 1000033792_16 r1c3 | 19.32 | 1.28 | -4 | 149 | 55→-77 | 0 |  |
| bn_gha | ঘ | 1000033792_16 r1c4 | 16.52 | 1.12 | -5 | 122 | -13→-67 | 0 |  |
| bn_nga | ঙ | 1000033792_16 r1c5 | 17.18 | 1.37 | -4 | 168 | 12→-145 | 0 |  |
| bn_ca | চ | 1000033792_16 r1c6 | 17.51 | 1.27 | 0 | 117 | -6→-121 | 0 |  |
| bn_cha | ছ | 1000033792_16 r1c7 | 18.03 | 1.44 | -4 | 156 | 2→-186 | 0 |  |
| bn_ja | জ | 1000033792_16 r1c8 | 17.12 | 1.08 | -3 | 189 | -15→-56 | 0 |  |
| bn_jha | ঝ | 1000033792_16 r1c9 | 19.87 | 1.51 | -4 | 186 | -3→-294 | 0 | Widest consonant (w 1.51). |
| bn_nya | ঞ | 1000033792_16 r1c10 | 19.43 | 1.23 | -3 | 256 | 40→-70 | 0 |  |
| bn_tta | ট | 1000033792_16 r2c1 | 15.30 | 1.04 | -5 | 207 | -84→-87 | 0 |  |
| bn_ttha | ঠ | 1000033792_16 r2c2 | 15.19 | 1.18 | -3 | 200 | -7→-79 | 0 |  |
| bn_dda | ড | 1000033792_16 r2c3 | 16.47 | 1.03 | -1 | 190 | 7→-7 | 0 |  |
| bn_ddha | ঢ | 1000033792_16 r2c4 | 15.27 | 1.01 | -2 | 105 | -13→-11 | 0 |  |
| bn_nna | ণ | 1000033792_16 r2c5 | 16.98 | 1.35 | -2 | 136 | 63→-83 | 0 |  |
| bn_ta | ত | 1000033792_16 r2c6 | 16.96 | 1.09 | -1 | 136 | -31→-80 | 0 |  |
| bn_tha | থ | 1000033792_16 r2c7 | 17.10 | 1.41 | -4 | 116 | 24→-174 | 0 |  |
| bn_da | দ | 1000033792_16 r2c8 | 16.33 | 1.10 | -1 | 105 | -17→-76 | 0 |  |
| bn_dha | ধ | 1000033792_16 r2c9 | 16.38 | 1.42 | -3 | 164 | 106→-64 | 0 |  |
| bn_na | ন | 1000033792_16 r2c10 | 20.28 | 1.34 | -1 | 142 | -7→-170 | 0 |  |
| bn_pa | প | 1000033792_16 r3c1 | 14.99 | 1.27 | -3 | 180 | 83→-52 | 0 |  |
| bn_pha | ফ | 1000033792_16 r3c2 | 16.95 | 1.07 | -1 | 198 | -28→-72 | 0 |  |
| bn_ba | ব | 1000033792_16 r3c3 | 19.29 | 1.38 | -2 | 141 | -18→-192 | 0 |  |
| bn_bha | ভ | 1000033792_16 r3c4 | 15.59 | 1.03 | -1 | 183 | -10→-25 | 0 |  |
| bn_ma | ম | 1000033792_16 r3c5 | 16.39 | 1.11 | 0 | 155 | -30→-84 | 0 |  |
| bn_ya | য | 1000033792_16 r3c6 | 17.16 | 1.19 | 0 | 118 | -22→-114 | 0 |  |
| bn_ra | র | 1000033792_16 r3c7 | 16.30 | 1.12 | 0 | 128 | -14→-68 | 0 |  |
| bn_la | ল | 1000033792_16 r3c8 | 16.34 | 1.14 | -2 | 145 | -15→-86 | 0 |  |
| bn_sha | শ | 1000033792_16 r3c9 | 16.35 | 1.04 | -4 | 175 | -101→-111 | 0 |  |
| bn_ssa | ষ | 1000033792_16 r3c10 | 19.12 | 1.32 | -2 | 139 | -21→-182 | 0 |  |
| bn_sa | স | 1000033792_16 r4c1 | 17.29 | 1.37 | -1 | 191 | -2→-197 | 0 |  |
| bn_ha | হ | 1000033792_16 r4c2 | 19.09 | 1.43 | 0 | 125 | -27→-235 | 0 | w 1.43 — visibly cleaner and bolder than the wispy v0.150 trace. |
| bn_rra | ড় | 1000033792_16 r4c3 | 17.01 | 1.07 | -3 | 197 | -13→-48 | 0 |  |
| bn_rha | ঢ় | 1000033792_16 r4c4 | 16.08 | 1.07 | -1 | 120 | -21→-47 | 0 |  |
| bn_yya | য় | 1000033792_16 r4c5 | 20.49 | 1.47 | -3 | 160 | -27→-249 | 0 | w 1.47; the dot below the baseline is part of the letter (also in v0.150). |
| bn_anusvara | ং | 1000033792_16 r4c7 | 19.90 | 1.59 | -1 | 53 | 82→72 | 1 | LOOP ONLY — stray pen flick (swoosh) below the loop removed; the v0.150 glyph carried the same stray. Fitted to the v0.150 loop-only box (83,618,447,1098). |
| bn_visarga | ঃ | 1000033792_16 r4c8 | 17.00 | 1.13 | -4 | 90 | 146→149 | 0 |  |
| bn_candrabindu | ঁ | 1000033792_16 r4c9 | 17.48 | 0.98 | -3 | 44 | -645→-640 | 0 | Crescent + dot, w 0.98 — the closest match to v0.150 of all 83. |
| bn_aakaar | া | 1000033792_16 r5c1 | 17.02 | 1.05 | -4 | 69 | -177→-173 | 0 |  |
| bn_ikaar | ি | 1000033792_16 r5c2 | 16.61 | 1.45 | -1 | 147 | -51→-46 | 0 | Left-edge aligned (mark rule); lsb almost unchanged (-51 → -46). |
| bn_iikaar | ী | 1000033792_16 r5c3 | 16.63 | 1.06 | -2 | 176 | -786→-784 | 0 | Left-edge aligned; lsb -786 → -784 (the extreme-left mark in the font). |
| bn_ukaar | ু | 1000033792_16 r5c4 | 15.61 | 1.16 | -2 | 85 | -620→-616 | 0 |  |
| bn_uukaar | ূ | 1000033792_16 r5c5 | 12.48 | 1.25 | -5 | 95 | -508→-508 | 0 |  |
| bn_rikaar | ৃ | 1000033792_16 r5c6 | 18.86 | 1.41 | -3 | 60 | -598→-596 | 0 |  |
| bn_ekaar | ে | 1000033792_16 r5c7 | 18.99 | 1.06 | -4 | 59 | -35→-39 | 0 |  |
| bn_aikaar | ৈ | 1000033792_16 r5c8 | 27.62 | 1.60 | -2 | 114 | -126→-126 | 0 | Widest mark (w 1.60): the two parts sit far apart in his handwriting. |
| bn_okaar | ো | 1000033792_16 r5c9 | 16.16 | 0.52 | -4 | 135 | -38→-42 | 0 | NARROW single-stroke form (w 0.52): his handwritten ো is one wavy stroke, not the font's wide two-part ে+া. Kept as written; judge in the specimen. |
| bn_aukaar | ৌ | 1000033792_16 r5c10 | 19.89 | 0.64 | -4 | 132 | -129→-126 | 0 | NARROW single-stroke form (w 0.64), same as bn_okaar with an extra top tick. |
| danda | । | 1000033792_16 r7c1 | 22.04 | 0.65 | -4 | 24 | 326→349 | 0 | Thin vertical stroke (w 0.65) — his danda is much narrower than the font's thick one. Kept as written. |
| period | . | 1000033792_16 r7c2 | 19.27 | 1.20 | -4 | 14 | 128→107 | 0 |  |
| comma | , | 1000033792_16 r7c3 | 19.74 | 1.23 | 0 | 42 | 118→84 | 0 |  |
| semicolon | ; | 1000033792_16 r7c4 | 22.50 | 1.62 | -3 | 67 | 115→23 | 0 | Dot + comma, horizontally offset in his handwriting (w 1.62). |
| colon | : | 1000033792_16 r7c5 | 20.43 | 1.58 | -4 | 36 | 155→86 | 0 | Two dots, horizontally offset (w 1.58). |
| hyphen | - | 1000033792_16 r7c8 | 23.50 | 1.62 | -1 | 35 | 74→-93 | 0 | Long horizontal stroke (w 1.62). |
| emdash | — | 1000033792_16 r7c9 | 18.84 | 1.32 | 0 | 41 | 91→-49 | 0 |  |
| slash | / | 1000033792_16 r8c1 | 27.98 | 1.76 | -3 | 49 | -39→-294 | 0 | Long diagonal (w 1.76) — his slash is much longer/steeper than the font's. |
| quoteleft | ‘ | 1000033792_16 r8c2 | 21.82 | 1.31 | -4 | 37 | 102→62 | 0 |  |
| quoteright | ’ | 1000033792_16 r8c3 | 22.16 | 1.22 | -3 | 29 | 110→79 | 0 |  |
| quotedblleft | “ | 1000033792_16 r8c4 | 22.07 | 1.48 | -3 | 69 | 126→-25 | 0 |  |
| quotedblright | ” | 1000033792_16 r8c5 | 20.46 | 1.37 | -4 | 67 | 110→-6 | 0 |  |
| question | ? | 1000033792_16 r8c6 | 14.82 | 0.86 | -2 | 78 | 180→221 | 0 |  |
| exclam | ! | 1000033792_16 r8c7 | 19.43 | 1.22 | -1 | 63 | 226→202 | 0 |  |
| bn_one | ১ | 1000033792_16 r9c1 | 18.81 | 1.52 | -4 | 113 | 147→-11 | 0 | Bold loop + tail; w 1.52. |
| bn_two | ২ | 1000033792_16 r9c2 | 19.57 | 1.18 | -3 | 112 | 93→16 | 0 |  |
| bn_three | ৩ | 1000033792_16 r9c3 | 19.32 | 1.53 | -3 | 109 | -1→-256 | 0 | Bold; w 1.53. |
| bn_four | ৪ | 1000033792_16 r9c4 | 17.13 | 1.07 | -1 | 148 | 44→49 | 0 |  |
| bn_five | ৫ | 1000033792_16 r9c5 | 17.49 | 1.06 | -3 | 161 | 89→71 | 0 |  |
| bn_six | ৬ | 1000033792_16 r9c6 | 18.07 | 1.23 | -4 | 137 | 15→-89 | 0 |  |
| bn_seven | ৭ | 1000033792_16 r9c7 | 18.04 | 1.31 | -2 | 125 | 182→103 | 0 |  |
| bn_eight | ৮ | 1000033792_16 r9c8 | 16.91 | 1.17 | -3 | 127 | 34→-45 | 0 |  |
| bn_nine | ৯ | 1000033792_16 r9c9 | 19.19 | 1.23 | -4 | 127 | 33→-38 | 0 |  |
| bn_zero | ০ | 1000033792_16 r9c10 | 14.75 | 0.97 | -3 | 88 | 122→132 | 0 |  |

## Skipped / left as AdorshoLipi

- **bn_hasanta (্):** kept AdorshoLipi, as in v0.130 (the v4 short bar does not scale).
- **ৢ (U+09E2, bn_likaar):** not one of the 69 — it was never in the handwriting set; stays AdorshoLipi.
- **Punctuation not replaced:** ellipsis … (U+2026) — no glyph in the font's cmap, so no cmap entry was invented; ":-" and "---" — ambiguous combos on the sheet, not single glyphs; straight quotes U+0027/U+0022 — the sheet marks are curly-style; doubledanda U+0965 — stays AdorshoLipi.
- **Latin digits 1–0:** out of scope; stay AdorshoLipi.
- **ৎ (khanda-ta, row 4 col 6):** not one of the 69; untouched.
- **Conjuncts (~300 cells across the sheets):** the v0.170 phase; not touched. Photo 5 (4 glyphs × 7) not used — names unconfirmed.
- **Still missing from all sheets:** ঌ, ঍/঎/঑/঒, ৰ/ৱ — nothing to trace for them.

## Files

- `Pranoti-Regular-v0.160-beta.ttf` — the build.
- `RE-TRACE-LOG-v0.160.md` — this file.
- `traced_glyphs.json`, `vowel_selection.json`, `targets.json`, `cells.json`, `build-log-v0.160.json` — trace/build data.
- `tools/grid_detect.py`, `tools/extract_cells.py`, `tools/measure_targets.py`, `tools/trace_glyphs.py`, `tools/build_pranoti_v0160_beta.py`, `tools/verify_pranoti_v0160_beta.py`, `tools/render_specimens_v0160.py`, `tools/fontforge_validate.py`.
- `checks/` — harfbuzz-22-samples-v0.160.tsv, consonant-pair-grid-v0.160.tsv, ink-boxes-v0.160.tsv, ots-v0.160.txt, fontforge-validate-v0.160.txt, summary-v0.160.txt.
- `specimens/` — before-after-v0.160.png, v0160-writing-demo.png, closeup-v0.160.png, matched-v0.150-v0.160-review.png, chosen-vowels-v0.160.png.
- Intermediate: `cells/` (399 cell crops), `pbm/` + `svg/` (per-glyph potrace inputs/outputs), `contact_vowels.png`, `contact_consonants.png`.

**Status:** built and verified in `v0160-prep/` only. `github-repo/` untouched. No push — integration and any push happen only after the owner approves the specimens.