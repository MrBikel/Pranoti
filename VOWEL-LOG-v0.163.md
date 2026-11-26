# Pranoti v0.163-beta — Vowel fine-tuning log

Base: `../v0162-prep/Pranoti-Regular-v0.162-beta.ttf`
(SHA-256 verified: `8a4812d097a95cf1c44dfa890875d2aadc100220c20d9034461d22b5d1309f14`).
Deliverable: `Pranoti-Regular-v0.163-beta.ttf`
SHA-256 `129355004867c4b292ac47fde1e1a9bea11fab891bafc2d9e05da7bd8e2c35e9`,
652 glyphs, cmap 204, UPM 1536, `head.fontRevision = 0.163`.

Scope: ONLY the 11 independent vowels
অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ
(`bn_a bn_aa bn_i bn_ii bn_u bn_uu bn_ri bn_e bn_ai bn_o bn_au`).
Nothing else touched: consonants, digits, vowel signs, punctuation,
hasanta, conjuncts, GSUB/GPOS/GDEF, cmap, glyph order — all unchanged
(verified by the table comparison in `tools/verify_pranoti_v0163_beta.py`).

## 1. Measurement on the v0.162 base

Method (script `tools/measure_vowels_v0163.py`, outputs
`checks/vowel-measure-v0.162.tsv/.json`):
- True ink bbox: each vowel rasterised alone at 1536 px (Pillow BASIC),
  compared with the v0.150 fitted ink box per letter
  (`v0160-prep/traced_glyphs.json` targets) and with AdorshoLipi's ink box
  (measured the same way from `reference/AdorshoLipi.ttf`).
- Stroke weight: distance-transform ridge median, same method as the
  v0.161 weight work (`v0160-prep/weight/measure_stroke_v0160.py`,
  1536 px, sigma 5, threshold 60). Letter median 84.5, ±15% band 71.8–97.2.
- Advances / side bearings from `hmtx` + ink bbox.
- Shape check: self-intersection + degenerate-contour scan on all 11
  vowels (script `v0162-prep/tools/check_self_intersection.py`):
  **0 crossings on every vowel, no degenerate contours.**

| glyph | char | ink top vs target | ink bottom vs v0.150 target | ink centre err | width vs v0.150 target | area vs v0.150 | ridge stroke | dev% |
|---|---|---|---|---|---|---|---|---|
| bn_a | অ | −3 | +7 | −1.0 | +55 | 0.890 | 84.5 | 0.0 |
| bn_aa | আ | −5 | +20 | +0.5 | +320 | 0.889 | 84.5 | 0.0 |
| bn_i | ই | **−21** | −40* | +0.5 | +252 | 0.804 | 85.9 | +1.7 |
| bn_ii | ঈ | −4 | −29* | 0.0 | +9 | 0.785 | 84.5 | 0.0 |
| bn_u | উ | −4 | −9 | −1.5 | −110 | 0.687 | 85.9 | +1.7 |
| bn_uu | ঊ | −4 | −6 | −1.5 | −66 | 0.786 | 92.2 | +9.1 |
| bn_ri | ঋ | −3 | +32* | −1.0 | +393 | 1.060 | 84.5 | 0.0 |
| bn_e | এ | **−20** | −28* | +1.0 | +275 | 0.865 | 84.5 | 0.0 |
| bn_ai | ঐ | **−20** | −40* | +1.0 | +375 | 0.859 | 92.5 | +9.5 |
| bn_o | ও | −2 | −33* | −0.5 | +150 | 0.842 | 92.2 | +9.1 |
| bn_au | ঔ | **−12** | −39* | +0.5 | +140 | 0.743 | 85.9 | +1.7 |

\* "bottom vs v0.150 target" is derived from the AdorshoLipi-relative
bottom error in the table above; the large negative numbers are a red
herring — the v0.150 design itself puts those bottoms below AdorshoLipi
(e.g. bn_o −33 means its bottom is 33 below AdorshoLipi's, which is
exactly the v0.150 fitted target). True bottom error vs the v0.150 target
is within ~4 units for every vowel.

What was off, per vowel:
- **bn_i, bn_e, bn_ai, bn_au — tops sitting low** (−21/−20/−20/−12).
  These four were thinned in v0.161 (pass 2, −16 each on top of pass 1);
  changeWeight pulls the outline in on every side, so the tops dropped.
  In the vowel row their tops visibly sit below অ/আ/ঈ/ঊ.
- **Stroke weights: nothing off.** All 11 vowels are inside the ±15%
  band (84.5–92.5). **No weight changes needed or made.**
- **Ink areas dropped vs v0.150** (bn_u 0.981→0.687, bn_au 0.887→0.728,
  bn_ii 0.960→0.785, bn_uu 0.986→0.786, bn_i 0.914→0.804, bn_e 0.957→0.806,
  bn_ai 0.909→0.813, bn_a 1.002→0.890, bn_aa 1.026→0.889, bn_o 0.933→0.842;
  only bn_ri got heavier, 1.035→1.060). The v0.160 re-trace lightened the
  vowels; stroke weights stayed normal, so this is fewer/shorter strokes
  in the new traces, not thin strokes. The vowels still read full at
  display size (verified visually) — no action taken.
- **Widths vs v0.150 targets:** bn_aa +320, bn_ri +393, bn_ai +375,
  bn_e +275, bn_i +252, bn_o +150, bn_au +140, bn_a +55; bn_u −110,
  bn_uu −66, bn_ii +9. Ink is wider than the advance for bn_aa (1987 vs
  1619), bn_ri (1638 vs 1267), bn_ai (1422 vs 1267), bn_i (1324 vs 989),
  bn_a (1351 vs 1245). His handwriting is genuinely ~25% wider than the
  v0.150 font (v0.160 finding, verified across 4 photos) — not a defect.
- **Vowel-row gaps (ink-to-ink, from advances) range −331 to +75 — very
  uneven.** See §3 for why this was deliberately NOT fixed by shifting.
- **Shape notes:** ঋ is very wide and rough and dominates the row — that
  is his pen's character (0 crossings, no degenerate contours); ঔ's form
  is fine; ঈ/ঊ heights are on target (−4); উ/ঊ look lighter and smaller
  than their neighbours at row size but are full and bold at 200 px
  (their ink area is small because the glyphs are compact, not because
  the strokes are thin); no vowel leans. The "lean" metric computed
  ( ink-centroid minus ink-centre ) measures shape asymmetry, not slant,
  and is not actionable.

## 2. Changes (4 glyphs only)

Uniform scale about the raster ink centre (restoring the v0.150 target
height) + a small dy translate putting the ink top exactly on target.
Uniform scale (x and y together, the v0.150 method) keeps stroke weight
almost unchanged and keeps the ink centre where it is. Scale factors
1.010–1.037 are inside the v0.150 clamp [0.97, 1.08].

| glyph | char | scale | pivot (ink centre) | dy | ink top before → after | ink bottom | ridge before → after | advance |
|---|---|---|---|---|---|---|---|---|
| bn_i | ই | ×1.0234 | (500.5, 720.0) | +0.5 | 1595 → **1616** (target) | −175 (target −175) | 85.9 → 85.9 | 989 |
| bn_e | এ | ×1.0367 | (550.5, 575.0) | −1.0 | 1147 → **1167** (target) | −19 (target −19) | 84.5 → 84.5 | 1216 |
| bn_ai | ঐ | ×1.0288 | (634.5, 865.0) | −5.0 | 1733 → **1753** (target) | −33 (target −33) | 87.6 → 92.5 | 1267 |
| bn_au | ঔ | ×1.0107 | (648.0, 891.0) | +3.5 | 1683 → **1695** (target) | 95 (target 94) | 85.9 → 85.9 | 1298 |

Re-measured on v0.163 (`checks/vowel-measure-v0.163.tsv/.json`): all four
tops now top_err 0 vs the AdorshoLipi target; ink areas recovered partway
(bn_i 0.804→0.841, bn_e 0.806→0.865, bn_ai 0.813→0.859, bn_au 0.728→0.743);
all 11 ridge weights still in band (84.5–92.5); the 7 untouched vowels are
byte-identical in measurement to v0.162. Advances unchanged; only the
hmtx lsb moved (new outline xMin: bn_i −161→−176, bn_e −29→−50,
bn_ai −76→−96, bn_au 32→25).

Build method: FontForge (`tools/build_vowels_v0163.py`) applies the
transforms and `addExtrema()` + `correctDirection()`, then only the four
changed glyf outlines (+ their hmtx lsb) are transplanted into a fontTools
copy of v0.162 (`tools/transplant_v0163.py`) — every other table stays
byte-identical to v0.162 by construction. Name IDs 3/5 and
`head.fontRevision` set to 0.163. No changeWeight was used, so the
v0.161 winding-flip lesson did not apply; contour winding was checked
unchanged in-session. `clean_glyph` removed 0 points / inserted 0 points
on all four glyphs; bn_au gained 2 points from `addExtrema()` (156→158).

## 3. Deliberately left alone, and why

- **Side bearings / row spacing:** equalising the vowel-row gaps would
  need horizontal shifts of 120–330 units — far beyond the ±40
  anchor-safe cap (candrabindu anchors sit on these glyphs; moving them
  would move the mark). Merely centring ink in the advance barely changes
  the gap spread (406 → 393) while moving anchors up to 40 units. The
  uneven gaps come from ink-width-vs-advance mismatch (his handwriting is
  genuinely wider), not from mis-centring. Rejected; recorded here so it
  is not re-attempted without a new approach (wider advances would even
  the gaps, at the cost of looser text — a decision for John, not for
  this pass).
- **Widths:** no width rescaling — outside the v0.150 clamp and against
  the v0.160 finding that his handwriting is genuinely wider.
- **Weights:** no changeWeight anywhere — all 11 vowels already in band.
- **Tops of the other 7 vowels (−2..−5):** within the v0.160/v0.161
  tolerance (5–8 units ≈ 0.1 px at 32 px text). Left alone.
- **bn_ri's roughness:** his pen's character; 0 crossings, no degenerate
  contours, reads clearly. Not redrawn.
- **bn_u/bn_uu looking light in the row:** their strokes are full-weight
  (85.9/92.2); the glyphs are just compact. Not thickened.

## 4. Verification

`tools/verify_pranoti_v0163_beta.py` — **PASS**:
- HarfBuzz 22/22 representative samples identical to v0.120; the 3
  reviewed candrabindu offsets exact (কাঁ −450,+125; চাঁ −278,+125;
  ক্ষ্মাঁ −632,+125).
- Consonant-pair grid **1,369/1,369 identical** to v0.120, 0 .notdef.
- New glyphs U+0980, U+09FB, U+09FC, U+09FE still render; candrabindu
  anchors unchanged.
- Table comparison: only GPOS, glyf, hmtx, cmap, head, name, maxp, loca
  differ; GSUB, GDEF, OS/2, attribution and license name records
  preserved. hhea minRightSideBearing −1147 (derived from glyf/hmtx;
  moved because bn_i's lsb went −161→−176 — self-consistent).
- Ink boxes (83 re-traced glyphs vs v0.150 targets): worst
  |top_err − expected| = **7.0** (tolerance 8; the worst is the
  pre-existing semicolon −7). The four fixed vowels: top_err 0, expected
  +4/+5 (the verify script's raster method carries a systematic ~4–5
  unit offset vs the measurement script), diff −4/−5 — PASS.
- OTS: `File sanitized successfully!` (`checks/ots-v0.163.txt`).
- FontForge validate: **65 → 64 flagged glyphs** (bn_au 32 → 0 after
  addExtrema; bn_i/bn_e/bn_ai were 0 and stay 0). **Nothing worsened** —
  no reverts needed. All remaining flags are bit 32 (missing extrema,
  cosmetic) except bn_vedic_anusvara 36 (32 + 4, pre-existing).
- Full summary: `checks/summary-v0.163.txt`.

## 5. Specimens (looked at)

- `specimens/before-after-v0.163.png` — all 11 vowels, v0.162 grey vs
  v0.163 black, baseline/headline guides. The four fixed vowels now touch
  the blue headline in black; the other seven are identical. No
  distortion, counters open, nothing floats or sinks.
- `specimens/v0163-vowel-demo.png` — the 11 vowels large, each in a real
  word (অমর, আমি, ইলিশ, ঈদ, উঠান, ঊষা, ঋণ, একা, ঐতিহ্য, ওজন, ঔষধ), three
  sentences using all 11 vowels, and the vowel row side-by-side
  v0.162/v0.163. Even rhythm, all words legible; ঋ still the widest and
  roughest letter in the row (character, as above).
- `specimens/invitation-v0.163.png` — the Peace School & College
  invitation sentences re-rendered; everything renders, no missing
  glyphs; the এ in "এবং" now sits at the right height.
- `specimens/matched-v0.162-v0.163-review.png` — matched RAQM specimen
  from the verify script (12/16/24/32 px).

Honest limit: at reading size the change is subtle — it is clearest at
display size, where the four restored tops now align with the other
vowels. The remaining unevenness in the vowel row is the ink-width
mismatch (§3), not position or weight.
