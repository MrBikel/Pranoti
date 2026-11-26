# Weight-evening plan — Pranoti v0.161-beta (evening pass, from v0.160)

Status: measurement + plan only. No TTF built, nothing modified.
Base: `Pranoti-Regular-v0.160-beta.ttf` (SHA-256 `2a50aafe…89ba614`).
Measurement: `weight/measure_stroke_v0160.py`, table `weight/stroke-widths-v0.160.tsv`,
chart `weight/stroke-widths-v0.160.png`.

## 1. Findings — John is right

Letter median stroke width is **84.5 units** (UPM 1536; overall median over all
83 glyphs 85.3). Letters span **69–120 units**: the thickest letter is 42%
above the median, the thinnest 18% below. That is visible at reading size.

Thickest letters (ridge median, deviation from 84.5):

| glyph | char | median | dev | v0.140-after | change vs v0.140 |
|---|---|---|---|---|---|
| bn_ai | ঐ | 120.2 | +42.2% | 115.2 | +5.0 |
| bn_i | ই | 117.5 | +39.1% | 108.6 | +8.9 |
| bn_e | এ | 115.2 | +36.3% | 84.5 | +30.7 |
| bn_yya | য় | 115.2 | +36.3% | 107.5 | +7.7 |
| bn_one | ১ | 103.3 | +22.2% | 110.8 | −7.5 |
| bn_six | ৬ | 103.3 | +22.2% | 136.7 | −33.4 |
| bn_au | ঔ | 103.0 | +21.9% | 107.5 | −4.5 |
| bn_kha | খ | 99.8 | +18.1% | 107.5 | −7.7 |
| bn_ga | গ | 99.8 | +18.1% | 115.2 | −15.4 |
| bn_ya | য | 99.8 | +18.1% | 107.5 | −7.7 |

Thinnest letters:

| glyph | char | median | dev | v0.140-after | change vs v0.140 |
|---|---|---|---|---|---|
| bn_cha | ছ | 69.1 | −18.2% | 122.9 | −53.8 |
| bn_pa | প | 69.1 | −18.2% | 107.5 | −38.4 |
| bn_tta | ট | 70.8 | −16.2% | 107.5 | −36.7 |
| bn_nya | ঞ | 75.6 | −10.5% | 107.5 | −31.9 |
| bn_gha | ঘ | 76.8 | −9.1% | 107.5 | −30.7 |
| bn_ta | ত | 76.8 | −9.1% | 99.8 | −23.0 |
| bn_la | ল | 76.8 | −9.1% | 107.5 | −30.7 |

Thinnest/widest signs: bn_uukaar ূ 60.0 (−29.0%), bn_okaar ো 66.1 (−21.8%,
within-glyph IQR 48.5 — very uneven along its own length), bn_aikaar ৈ 107.5
(+27.2%), bn_ikaar ি 99.8 (+18.1%), bn_anusvara ং 100.0 (+18.3%).

Systematic shift: v0.160 letters are ~20% thinner overall than the v0.140
traces (letter median 84.5 vs ~110). That is expected, not a defect — the old
traces came from one blurry photo, and blur inflates stroke width when
thresholded. The clean-photo re-traces show the true pen width. **Do not
"restore" the old ~112 target; the target is v0.160's own median, 84.5.**

Cross-check vs the v0.150 notes (গ/ধ/ল thick, ত/ঔ/ঙ thin): the re-trace
reshuffled the weights, so the old notes no longer describe v0.160.
গ is still thick (+18%), ধ is now exactly at the median (84.5 — fixed),
ল is now slightly thin (−9%, within tolerance), ত is still slightly thin
(−9%, within tolerance), ঔ flipped to thick (+22%), ঙ is fixed (−3%).

Within-glyph wobble (IQR of the ridge distribution) is a separate issue:
bn_one ১ 45.3, bn_seven ৭ 40.8, bn_ca চ 38.4, bn_six ৬ 38.1, bn_yya য় 32.5,
bn_aukaar ৌ 53.8, bn_okaar ো 48.5. These glyphs vary along their own strokes
— that is pen pressure, i.e. character. A uniform weight change cannot fix
it (it shifts the whole distribution); leave it alone in this pass.

## 2. Method (validated, not guessed)

Distance-transform ridge, same estimator family as POLISH-LOG-v0.140:
render each glyph alone with PIL BASIC layout at 400 px em (3.84 units/px),
binary ink mask, `scipy.ndimage.distance_transform_edt`, ridge = ink pixels
that are local maxima of the EDT (3×3 maximum filter), stroke = 2 × median
EDT on the ridge × scale. Also reported: trimmed median (bottom 20% of ridge
values dropped) and IQR.

Validation against the v0.140 log (same method on the v0.140 TTF): bn_a 99.8
vs 99.84, bn_la 107.5 vs 107.52, bn_nna 103.7 vs 104.46, bn_one 107.1 vs
110.76 — within 0–9 units. Two method notes:
- 800 px em was tried and rejected: it resolves sub-pixel outline hairlines
  (e.g. bn_dha's pinched-loop neck, ~11 units wide) that the eye never sees
  at text size and that drag the median down (bn_dha 10.9 at 800 px vs 99.8
  at 400 px). 400 px matches the v0.140 log and measures what the eye sees.
- Measurements are quantized to 7.68 units (2 px at 400 px em); differences
  under ~8 units are noise. Do not chase them.
- Blob caveat: for filled blobs/dots (period 246.5, colon 238.2, hyphen
  145.9, quotes 108–125, semicolon 120.8, anusvara/visarga/candrabindu) the
  ridge value measures the blob radius or bar height, not a stroke. They
  are coloured orange in the chart and **excluded from the ranking and from
  adjustment**. Do not "fix" the period's 246.

## 3. Target and policy

- Target: the letter median, **84.5 units**. Keep the natural ±15% band
  (72–97 units) untouched — that variation is his pen pressure, i.e. the
  handwriting character. Adjust only glyphs beyond ±15%.
- Move each outlier toward the median, capped at **±16 units of width
  change in one pass**. Glyphs that need more (ঐ, ই, এ, য়) take a second
  capped pass after re-measurement; do not force them in one go — large
  thins shrink counters and can distort joins.
- Do not touch: anything inside ±15% (including ত, ল, ঙ, ণ, ধ); any
  punctuation; within-glyph wobble (IQR).

## 4. Pass 1 — adjustment table (18 glyphs)

changeWeight(delta) changes the stem width by delta; verified below.
Expected result in parentheses (measured after: bn_cha +15 → 84.5 exactly).

Thicken down (negative delta):

| glyph | char | now | delta | expected |
|---|---|---|---|---|
| bn_ai | ঐ | 120.2 | −16 | ~104 (pass 2 candidate) |
| bn_i | ই | 117.5 | −16 | ~102 (pass 2 candidate) |
| bn_e | এ | 115.2 | −16 | ~99 (pass 2 candidate) |
| bn_yya | য় | 115.2 | −16 | ~99 (pass 2 candidate) |
| bn_one | ১ | 103.3 | −16 | ~87 |
| bn_six | ৬ | 103.3 | −16 | ~87 |
| bn_au | ঔ | 103.0 | −16 | ~87 |
| bn_kha | খ | 99.8 | −15 | ~85 |
| bn_ga | গ | 99.8 | −15 | ~85 |
| bn_ya | য | 99.8 | −15 | ~85 |
| bn_aikaar | ৈ | 107.5 | −16 | ~92 |
| bn_ikaar | ি | 99.8 | −15 | ~85 |
| bn_anusvara | ং | 100.0 | −15 | ~85 (check visually; ring, see §6) |

Thicken up (positive delta):

| glyph | char | now | delta | expected |
|---|---|---|---|---|
| bn_tta | ট | 70.8 | +14 | ~85 |
| bn_cha | ছ | 69.1 | +15 | ~84 (verified) |
| bn_pa | প | 69.1 | +15 | ~84 (verified) |
| bn_okaar | ো | 66.1 | +16 | ~82 (internal wobble stays) |
| bn_uukaar | ূ | 60.0 | +16 | ~76 (pass 2 candidate) |

Pass 2 (only after re-measuring pass 1): ঐ, ই, এ, য় another capped −16
each (expected ~86–88); ূ another +16 if still below −15% (expected ~92,
watch the hook — do not let it go fat).

## 5. How to apply — FontForge `glyph.changeWeight` (tested, not guessed)

Tested on this machine (FontForge 20230101, `fontforge -lang=py`):
`glyph.changeWeight(delta)` offsets the outline by delta/2 on every side.
- bn_cha +15: stroke 69.1 → 84.5 (+15.4, exact), bbox drift ±7.5 all sides,
  advance unchanged (954), validate unchanged (32).
- bn_pa +15: 69.1 → 84.5, advance unchanged, validate unchanged (32).
- bn_ai −28: 120.2 → 92.8 (−27.4), advance unchanged (1267), bbox shrank
  ±14.0 on x, +20.5/−14.0 on y (asymmetric — watch the bottom stroke),
  validate changed 32 → 8 after a save round-trip, and the run printed
  "Invalid 2nd order spline in SplineRefigure2" warnings.

Procedure (new `v0161-prep/` dir, following the v0.150/v0.160 pattern):
1. Copy the v0.160 TTF as the base; verify SHA-256 `2a50aafe…89ba614`.
2. FontForge script: for each row in §4, `font['<name>'].changeWeight(delta)`,
   then `glyph.addExtrema()` on each touched glyph, then save as
   `Pranoti-Regular-v0.161-beta.ttf`, `head.fontRevision = 0.161`.
3. Do not touch hmtx, GSUB/GPOS/GDEF, cmap, glyph order, or any other glyph.
4. Re-measure with `weight/measure_stroke_v0160.py` pointed at the new TTF;
   confirm the letter median is still ~84.5 and every adjusted glyph moved
   as expected; run pass 2 only for glyphs still beyond ±15%.

Fallback if changeWeight misbehaves on a glyph (validate worsens, spline
warnings, visible distortion): revert that glyph to its v0.160 outline and
either leave it for manual review or offset it with `pyclipper`
(installed 1.4.0 in the `/tmp/wvenv` venv — flatten quadratics, offset the
polygon, re-fit; lossy, so it is second choice). `pathops` is **not**
available (no matching distribution on the index — verified); do not plan
around it. FontForge Simplify and the autoHint round-trip stay rejected
(they were rejected in v0.140 for collapsing outlines / rewriting tables).

## 6. What it preserves, and what to watch

- Advances: changeWeight does not change `width` (verified on all three
  test glyphs) — spacing and the v0.150 size fit are untouched.
- Size normalization: the outline grows/shrinks by delta/2 on every side,
  so ink tops move by up to ±8 units. The v0.150 "ink-top error exactly 0"
  becomes "worst error ≤ 8 units" — 0.5% of em, ~0.17 px at 32 px text,
  invisible. Re-run the ink-box check and report the new worst error;
  do not re-run size normalization (it would scale the corrected weights).
- Anchors: changeWeight moves outline points only; GPOS anchor points are
  not moved. A ±8-unit outline shift under a fixed anchor is negligible
  for mark attachment, but the 3 candrabindu offsets are re-verified anyway
  as part of the 22 HarfBuzz samples.
- Counters: thinning shrinks counters (ঐ, ই, এ, য়). At −16 the counters
  stay open; that is why the cap exists. Check the before/after specimen
  for closed counters, especially ঐ and য়.
- bn_anusvara ং: its 100.0 measures the ring's stroke; thinning it is safe
  in principle, but check the loop visually after pass 1 — if the ring
  looks weak, revert it (it is only +18%).
- bn_okaar ো: +16 lifts its overall weight but its IQR (48.5) stays — the
  thin tail and thick head are both still there, just both thicker. That
  is the intended outcome; do not chase its internal wobble.
- bn_ai flag: after the −28 test thin, validate went 32 → 8 (bit 8, the
  "missing extrema" check) even after addExtrema. The −16 pass-1 thin is
  smaller and may not trigger it. Rule for the build: validate every
  touched glyph on the generated TTF and compare with its v0.160 value
  (baseline 32 for these glyphs); any glyph whose validate worsens gets
  reverted to v0.160 and retried at half the delta, or left for pass 2.
- "Invalid 2nd order spline in SplineRefigure2" warnings appeared during
  the thinning tests. If they appear in the build, inspect those glyphs
  in the before/after specimen before accepting the build.

## 7. Re-verification after the build (same as v0.160)

- Re-measure stroke widths; letter median ~84.5; no letter beyond ±15%
  except the four pass-2 candidates.
- `verify_pranoti_v0160_beta.py` adapted to v0.161: 22/22 HarfBuzz samples
  (3 candrabindu offsets exact), 1,369/1,369 consonant-pair grid identical
  to v0.120, 0 .notdef.
- OTS clean; FontForge validate per touched glyph (see §6 rule).
- Ink-box check vs v0.150 targets (worst error ≤ 8 units expected).
- Specimens: before/after of the 18 touched glyphs + writing demo +
  invitation re-render, for John's approval before any push. No push
  without his approval (established pattern).
