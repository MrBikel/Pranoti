# Weight-evening build log — Pranoti v0.161-beta

Status: built and verified. No push — specimens go to John for approval first.
Base: `Pranoti-Regular-v0.160-beta.ttf` (SHA-256 `2a50aafe90584e1868fd6dd85c8e03f61cbab46b7ae3333efc9d8e25789ba614`).
Plan: `../v0160-prep/weight/WEIGHT-PLAN-v0.161.md` (§4 table, §5 changeWeight, §6 rules, §7 checks).
Measurement: distance-transform ridge, `weight/measure_stroke_v0160.py` lineage
(`tools/measure_stroke_v0161.py`); letter median target **84.5 units** (UPM 1536).

## 1. Result

| | v0.160 | v0.161 |
|---|---|---|
| Letter median stroke | 84.5 | 84.5 |
| Letter spread (min–max) | 69–120 | 75.6–92.5 |
| IQR of letter medians | 11.4 | 5.4 |
| Letters beyond ±15% (72–97) | 10 | 0 (except reverted bn_anusvara) |
| Thickest letter | ঐ 120.2 (+42%) | ২ 92.5 (+9.5%) |
| Thinnest letter | ছ/প 69.1 (−18%) | ঞ 75.6 (−10.5%) |

Final TTF: `Pranoti-Regular-v0.161-beta.ttf`, 397,272 bytes,
SHA-256 `9a46dd667efe2cc62b0d5d4cae590796f17cb99990e69c7c07fc7b415bdb5e77`,
652 glyphs, cmap 204, `head.fontRevision = 0.161`, name IDs 3/5 "Version 0.161-beta".

## 2. Per-glyph before/after (median stroke width, font units)

Pass 1 = §4 table (13 thins, 5 thickens, capped ±16). Pass 2 = a further −16
each for the four glyphs still beyond +15% after pass 1.

| glyph | char | v0.160 | pass 1 Δ | pass 2 Δ | v0.161 | dev from 84.5 |
|---|---|---|---|---|---|---|
| bn_ai | ঐ | 120.2 | −16 | −16 | 87.6 | +3.7% |
| bn_i | ই | 117.5 | −16 | −16 | 85.9 | +1.7% |
| bn_e | এ | 115.2 | −16 | −16 | 84.5 | +0.0% |
| bn_yya | য় | 115.2 | −16 | −16 | 84.5 | +0.0% |
| bn_one | ১ | 103.3 | −16 | — | 86.9 | +2.8% |
| bn_six | ৬ | 103.3 | −16 | — | 89.6 | +6.0% |
| bn_au | ঔ | 103.0 | −16 | — | 85.9 | +1.7% |
| bn_kha | খ | 99.8 | −15 | — | 84.5 | +0.0% |
| bn_ga | গ | 99.8 | −15 | — | 92.2 | +9.1% |
| bn_ya | য | 99.8 | −15 | — | 84.5 | +0.0% |
| bn_aikaar | ৈ | 107.5 | −16 | — | 92.2 | +9.1% |
| bn_ikaar | ি | 99.8 | −15 | — | 84.5 | +0.0% |
| bn_anusvara | ং | 100.0 | −15 | — | 100.0 | +18.3% (REVERTED, see §4) |
| bn_tta | ট | 70.8 | +14 | — | 84.5 | +0.0% |
| bn_cha | ছ | 69.1 | +15 | — | 84.5 | +0.0% |
| bn_pa | প | 69.1 | +15 | — | 84.5 | +0.0% |
| bn_okaar | ো | 66.1 | +16 | — | 82.7 | −2.1% |
| bn_uukaar | ূ | 60.0 | +16 | — | 75.6 | −10.5% |

Notes:
- changeWeight moved strokes almost exactly by the delta (e.g. ছ +15 → 69.1→84.5,
  ঐ −16−16 → 120.2→87.6). One exception: bn_ga moved only −7.6 for a −15
  delta (its strokes are mostly curved/diagonal); it still landed at 92.2,
  inside the band, so no further action.
- bn_uukaar ূ at 75.6 (−10.5%) needs no pass 2 (plan: another +16 only if
  still below −15%). Its internal wobble (IQR 48.5 in v0.160) is pen pressure
  and was left alone, as planned.
- Within-glyph wobble (IQR) was not touched anywhere.

## 3. Method — and two things the plan got wrong

### 3a. changeWeight flips contours when thinning (found, repaired)
`glyph.changeWeight(delta)` with a NEGATIVE delta reverses the winding of
EVERY contour of the glyph (verified by signed-area comparison against
v0.160: all 13 thinned glyphs flipped; all 5 thickened glyphs did not).
A half-delta retry (−8 on bn_ai) ALSO flips, so the plan's "retry at half
the delta" fallback does not help here. The repair is
`glyph.correctDirection()` after `addExtrema()`: verified on bn_ai, the
signed area matches the v0.160 original again, and after the repair NO
glyph in v0.161 has a flipped contour vs v0.160 (all 18 checked).
`correctDirection()` is a no-op on the thickened glyphs.

### 3b. The plan's FontForge validate bit labels were wrong (corrected)
The plan (§6) and the v0.130–v0.160 logs labelled validate value 32 as
"no anchor points" and value 8 as "missing extrema". FontForge's own
`validation_state` docs say: 0x2 open contour, 0x4 self-intersecting,
0x8 contour in the WRONG DIRECTION, 0x10 flipped reference,
0x20 (32) MISSING EXTREMA, 0x80000 points non-integral.
So: 32 = missing extrema (cosmetic, hinting-only — all 83 handwriting
glyphs carried it in v0.160 because potrace traces don't put points at
extrema), and 8 = wrong direction (real — the changeWeight flip above).
The live-session validate values of ~524288 were 0x80000, non-integral
coordinates in FontForge's float representation; they vanish on TTF
generate (integer rounding) and are not a defect.
Also: `font.save(path)` in FontForge writes an SFD database, NOT a TTF —
`font.generate(path)` is what produces the TTF. The first pass-1 run
saved an SFD by mistake; caught by fontTools refusing to open it
("bad sfntVersion"), fixed, re-run.

### 3c. Transplant (why, and what it preserves)
FontForge's `generate()` also reorders glyphs (it moved `dollar` before
`percent`) and rewrites tables. So only the 18 changed glyf outlines (+
their hmtx lsb = new xMin) were transplanted with fontTools into a copy
of v0.160 (`tools/transplant.py`, `tools/transplant_pass2.py`). Verified
afterwards: the ONLY tables differing v0.160 → v0.161 are glyf, head,
hhea, hmtx, loca, name. GPOS, GSUB, GDEF, cmap and glyph order are
byte-identical; all advances unchanged. `head.fontRevision = 0.161`,
name IDs 3/5 updated; hhea metrics recalculated by fontTools
(minRightSideBearing −1137 → −1147, self-consistent with glyf/hmtx).

### 3d. Duplicate points and the 0x4 flag
changeWeight+addExtrema created exact duplicate consecutive points
(min distance 0.00) on 10 touched glyphs. The v0.160 build's `clean_glyph`
dedup was run on every transplanted glyph (removes only duplicates whose
removal cannot change geometry); it removed up to 16 points (bn_ga).
A geometric self-intersection check was written for this build
(`tools/check_self_intersection.py`: flatten quadratics, test proper
crossings between non-adjacent segments of the same contour). The first
version of that script had a flattening bug (wrong start point after
consecutive off-curve points) that produced false positives on the v0.160
baseline; fixed, the baseline shows 0 crossings everywhere. On the
changeWeight output it found 1–2 tiny crossings on 7 glyphs; after
clean_glyph dedup + the direction repair, the final v0.161 shows
0 crossings on every checked glyph.

## 4. Revert — bn_anusvara (ং) only

bn_anusvara's −15 thin created a degenerate kink in contour 0 (two
non-adjacent points at distance 0.00), tripping FontForge validate 0x4
(32 → 36). A half-delta retry (−7, `tools/test_anusvara_half.py`) shrank
the kink to 1.00 but the 0x4 flag persisted. Per the §6 revert rule, the
glyph was reverted to its v0.160 outline (validate back to 32, stroke
100.0, +18.3% — the only letter still outside the ±15% band). It needs a
manual pass later; the ring itself was checked visually and is intact.
No other glyph was reverted. No glyph in v0.161 validates worse than its
v0.160 baseline (32): 12 touched glyphs actually improved to 0 (their
missing-extrema flag is gone — addExtrema added the points), 6 stayed
at 32, bn_anusvara is back at 32. Total flagged glyphs in the font fell
85 → 73. The only value-4 flag left in the font is the pre-existing
bn_vedic_anusvara = 36 (unchanged since v0.160).

## 5. Ink tops — why they moved, and why that is not a defect

changeWeight moves every outline edge inward/outward by delta/2, so ink
tops move by total_delta/2: −8 for one −16 pass, −16 for the two-pass
glyphs, +7.5 for the +15 thickens. Measured worst |top_err − expected|
= 5.0 units over all 83 glyphs (tolerance 8 in
`tools/verify_pranoti_v0161_beta.py`, which checks
|top_err − total_delta/2| ≤ 8 instead of the v0.160 re-trace tolerance
of 10 — the old tolerance assumed tops were fitted exactly, which a
weight change legitimately undoes). Worst raw top error is bn_i −21
(−16 predicted + −5 pre-existing v0.160 residual). 21 units = 1.4% of em,
~0.4 px at 32 px text — invisible at reading size. Do NOT re-run size
normalization (it would scale the corrected weights) and do NOT translate
glyphs back up (that would misalign their vertical centre).

## 6. Verification (tools/verify_pranoti_v0161_beta.py) — PASS

- HarfBuzz 22/22 representative samples: glyphs, clusters, advances
  identical to v0.120; the 3 reviewed candrabindu offsets exact
  (কাঁ −450,+125; চাঁ −278,+125; ক্ষ্মাঁ −632,+125). 0 FAIL rows.
- Consonant-pair grid: 1,369/1,369 identical to v0.120; 0 .notdef.
- 4 new glyphs (U+0980, U+09FB, U+09FC, U+09FE) still render.
- Tables: only GPOS, glyf, hmtx, cmap, head, name, maxp, loca differ vs
  v0.120 (GPOS/cmap differences are the pre-existing v0.130 changes);
  GSUB, GDEF, OS/2, attribution and license name records preserved.
- OTS: "File sanitized successfully!"
- FontForge validate: see §4. No glyph worse than its v0.160 baseline.
- Ink boxes: worst |top_err − expected| = 5.0 (tolerance 8), see §5.
- Checks in `checks/`: harfbuzz-22-samples-v0.161.tsv,
  consonant-pair-grid-v0.161.tsv, ink-boxes-v0.161.tsv, ots-v0.161.txt,
  summary-v0.161.txt.

## 7. Specimens (looked at by the builder)

- `specimens/before-after-v0.161.png` — all 17 adjusted glyphs, v0.160 grey
  over v0.161 black, baseline/headline guides. Thinned letters are visibly
  lighter with the same shapes; thickened letters bolder; no collisions.
- `specimens/closeup-v0.161.png` — ঐ ই এ য় ছ প ো ূ at 200 px. Counters
  stay OPEN on all four two-pass thins (the main risk of the −32 total);
  no filled counters, no distortion, no spikes. (One cosmetic flaw in the
  sheet itself: the bn_uukaar label is partly covered by the glyph's tail.)
- `specimens/v0161-writing-demo.png` — headline, paragraph, alphabet,
  digits, punctuation, conjuncts + side-by-side paragraph v0.160/v0.161.
  Even rhythm, no collisions, nothing floats or sinks. Honest note: at
  30 px the evening is subtle — the change is clearest at display size
  (the close-ups); at reading size it reads as a slightly more even texture.
- `specimens/invitation-v0.161.png` — the Peace School & College sentences
  re-rendered in v0.161, same text as the v0.160 specimen. Renders cleanly;
  the ~20 conjuncts are still base-font shapes (v0.170 list).
- `specimens/matched-v0.160-v0.161-review.png` — 10 samples at 12/16/24/32 px,
  v0.160 vs v0.161. Shaping identical at every size; no tofu, no missing marks.
- `specimens/stroke-widths-before-after-v0.161.png` — bar chart: all 17
  adjusted glyphs now inside the ±15% band.

## 8. What is still uneven (honest limits)

- bn_anusvara ং is still +18.3% (reverted, §4). It is the only letter
  outside the band.
- Within-glyph wobble (IQR up to ~40–54 on ১, ৭, ৌ, ো) is pen pressure,
  deliberately untouched — a uniform weight change cannot fix it.
- bn_ga responded weakly to thinning (−7.6 for −15); it landed at +9.1%,
  inside the band, so nothing further was done.
- The evening is subtle at reading size (see §7); the visible difference
  is at display size. If John still sees bold/thin letters at reading
  size, the remaining variation is the within-glyph wobble, not the
  per-glyph median — that would need per-stroke work, not another
  changeWeight pass.
