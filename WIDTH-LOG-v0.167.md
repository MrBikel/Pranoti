# WIDTH-LOG-v0.167.md — Pranoti v0.167-beta

**Base:** v0.166-beta (`Pranoti-Regular-v0.166-beta.ttf`, SHA-256
`a07809f97f42fc2ea85938f00779e63377b6cdb2f9b7fcd363ca838259328c06`, verified before work).
**Built:** 2026-11-26. **Final TTF:** `Pranoti-Regular-v0.167-beta.ttf`,
SHA-256 `c18502d7cb692e3723546ad561e2b66cd1c50d27a352ea88171229c6196ce101`,
652 glyphs, cmap 204, head.fontRevision = 0.167.
**Status:** built and verified by Muse; **NOT pushed** (v0.165 and v0.166 are also
still unpushed — each needs John's separate approval).

## Why this version

John reviewed the v0.166 specimens and said the sizes don't look right. Measured:
heights were on target but widths varied widely vs the AdorshoLipi reference
(ি +504, ৈ +442, ৃ +211, ূ +171, ু +100, ী +69 over target; ো −806, ৌ −674 under).
He chose option 1 (bring widths toward target) WITH the condition that the
handwriting must stay more or less intact — a **gentle, capped width pass**, not a
redraw and not a full normalization. While the build was running he flagged
further letters one by one; the scope closed at 27 glyphs (the আ/ই/ঈ/ঋ batch was
the last — anything else he flags later goes into v0.168).

## Scope (27 glyphs touched, nothing else)

- **Width pass (13 signs/marks):** া ি ী ু ূ ৃ ে ৈ ো ৌ ং ঃ ঁ
  (bn_aakaar, bn_ikaar, bn_iikaar, bn_ukaar, bn_uukaar, bn_rikaar, bn_ekaar,
  bn_aikaar, bn_okaar, bn_aukaar, bn_anusvara, bn_visarga, bn_candrabindu).
- **Flagged glyphs:** bn_anusvara (swoosh), bn_rikaar (shift), Khanda_Ta (re-centre),
  bn_da, bn_yya, bn_ga, bn_ca, bn_jha, bn_nya, bn_na, bn_sa, bn_uu, bn_aa,
  bn_i, bn_ii, bn_ri.
- **NOT touched:** ৎ's shape (only its placement/advance), hasanta, ৢ, other vowels,
  other consonants, digits, punctuation, conjuncts, GSUB/GPOS/GDEF, cmap, glyph
  order. No changeWeight anywhere in this pass. Advances unchanged except
  Khanda_Ta (759 → 1210).

## 1. Width pass — the 13 signs/marks

Method: horizontal scale only, closing **half** of each sign's width error,
scale factor capped ×0.85–×1.20 per glyph. Heights, tops, bottoms and stroke
weights unchanged; ridge must stay in the ±15% band around the 84.5 median
(71.8–97.2).

**Pivot deviation (deliberate, documented in `tools/build_width_v0167.py`):**
the brief said "about the ink centre", but all 13 signs already have their
LEFT edge on target (left_err −4..+13) and carry their ENTIRE width error on
the RIGHT edge (right_err +28..+516 over, −811/−674 under for ো/ৌ). Centre
scaling would move the already-correct left edges 17–122 units in the WRONG
direction and shift marks relative to their bases. So the scale is about the
ink LEFT edge + centre-y (the v0.130/v0.166 sign rule). The left edge stays
fixed; only the right edge moves toward target.

**GPOS check:** only bn_candrabindu has a GPOS mark anchor (−386,1293); the
other 12 signs are positioned by advance/bearings, not GPOS. The candrabindu
anchor is NOT touched: its ×1.024 scale about the left edge moves the outline
at the anchor by only +6 units, and HarfBuzz dx/dy offsets depend on the anchor
alone, so the 3 reviewed candrabindu offsets stay exact (verified 22/22).

| glyph | sign | scale | width before → after | target | err before → after | ridge before → after |
|---|---|---|---|---|---|---|
| bn_aakaar | া | ×0.9810 | 656 → 643 | 631 | +25 → +12 | 84.5 → 84.5 |
| bn_ikaar | ি | ×0.85 (cap) | 1625 → 1381 | 1121 | +504 → +260 | 84.5 → 76.8 |
| bn_iikaar | ী | ×0.9739 | 1322 → 1288 | 1253 | +69 → +35 | 84.5 → 81.6 |
| bn_ukaar | ু | ×0.9382 | 809 → 760 | 709 | +100 → +51 | 84.5 → 86.9 |
| bn_uukaar | ূ | ×0.95 (override) | 854 → 811 | 683 | +171 → +128 | 76.0 → 75.6 |
| bn_rikaar | ৃ | ×0.8586 + shift −110 | 746 → 640 | 535 | +211 → +105 | 84.5 → 86.9 |
| bn_ekaar | ে | ×0.9795 | 708 → 694 | 679 | +29 → +15 | 84.5 → 85.9 |
| bn_aikaar | ৈ | ×0.85 (cap) | 1216 → 1034 | 774 | +442 → +260 | 84.5 → 92.2 |
| bn_okaar | ো | ×1.20 (cap) | 879 → 1055 | 1685 | −806 → −630 | 84.5 → 84.5 |
| bn_aukaar | ৌ | ×1.20 (cap) | 1188 → 1425 | 1862 | −674 → −437 | 84.5 → 84.5 |
| bn_anusvara | ং | ×0.85 (cap) | loop 560 → 475 | 364 | +196 → +111 | 91.0 → 92.5 |
| bn_visarga | ঃ | ×0.9593 | 504 → 483 | 463 | +41 → +20 | 84.5 → 79.1 |
| bn_candrabindu | ঁ | ×1.0243 | 493 → 504 | 517 | −24 → −13 | 84.5 → 92.2 |

Widths halved toward target as planned (the ×0.85/×1.20 caps bind on ি, ৈ, ো, ৌ,
ং). All ridges in the 71.8–97.2 band. Tops within ±4 of target. No
self-intersections (all 0). Cluster boxes recorded in `checks/sign-measure-v0.167.tsv`
(কৃ [−107,−521,1265,1157] — the ৃ tucks under the ক).

**Reductions / overrides:**
- **bn_uukaar ×0.95 (not the planned ×0.8999):** the planned scale pushed its
  ridge to 70.8, below the 71.8 floor — so it closes only 25% of its width
  error instead of half. Still the widest over-target sign (+128).
- **ো/ৌ ×1.20 hard cap:** their targets (~1685/~1862) are ~2× their narrow
  single-stroke forms (879/1188). They are widened modestly and keep their
  single-stroke character; they are still well under target (−630/−437).
  Stretching them anywhere near double would destroy the handwriting.
- **Ridge honesty:** ি's ridge fell to 76.8 (−7.7) and ু's to 86.9 — outside the
  ±5 per-glyph check but inside the ±15% band, so kept per the band rule.

## 2. The three flagged glyphs (steer 1)

### bn_anusvara (ং) — "ঠিক নেই"
v0.166 was a loop only (bounds 84,618,644,1101) — no tail, while v0.120 dips to
−133 and his handwriting cell r4c7 shows loop + swoosh (dropped in v0.160 as
"one contour to add back"). **Fix: swoosh restored.**
Two versions were built and compared (`specimens/swoosh-compare.png`, words
কং/বাংলা/কাঁদ/সংসার at 110px):
- **Fresh re-trace REJECTED:** fitted at the loop's y-scale it is 876 wide
  (x 182–1058, bottom −120) and sweeps far right under/into the following
  letter (in বাংলা its tip reaches under the ল).
- **v0.150 swoosh CHOSEN:** the v0.150 glyph's swoosh contour (x[164,710]
  y[−130,334]) translated dx −115 to sit under the v0.167 loop (x 49–595,
  bottom −130, top 334) — compact, matches the base font's proportions, ends
  before the next letter. It is the same handwriting, already at the right
  proportions.
Final: bbox (49,−130,595,1101), 3 contours, ridge 92.5 (in band; the added
swoosh did not push it out). In বাংলা/কাঁদ/সংসার the tail now dips below the
baseline like the base font's, and the loop + swoosh read as one letter.
(Two transplant bugs found and fixed: the fresh-swoosh loop identification
picked the loop's HOLE instead of its outer contour; and `numberOfContours` is
a stored attribute, not derived — after appending the swoosh contour it stayed
stale at 2 and produced a malformed glyph. Both fixed in `tools/transplant_v0167.py`.)

### bn_rikaar (ৃ) — "সঠিক জায়গায় বসে নাই"
v0.166 bounds (−596,−522,152,171) vs v0.120 (−598,−528,−66,177) — it reached
218 units further right and hung detached in কৃ. **Fix: shift left** (dx −110,
the width-pass scale applied first). Final bbox (−706,−521,−67,170): xMax −67
(target −66, within 1; clean_glyph removed a point). Advance (30) and anchors
unchanged. Re-rendered কৃ, গৃ, মৃ, রৃ, হৃ — the mark now tucks under the base
consonant the way the base font's does (কৃ cluster box [−107,−521,1265,1157]).

### Khanda_Ta (ৎ) — "সকল জায়গায় সঠিকভাবে দেখা যাচ্ছে না"
**Diagnosis (pixel analysis, definitive):** at 1536 units, per-glyph ink masks
show v0.166's ৎ shares REAL ink pixels with the previous glyph in ALL 7 test
words — হঠাৎ vs া 6,193 px; সৎ vs স 56,065 px; উৎপাত/উৎসাহ/উৎস vs উ 8,938 px
each; মৎস্য vs ম 35,020 px; বিৎ vs ব 43,560 px — while v0.120's ৎ touches
NOTHING in all 7. The +248 right overhang never touches the next glyph's ink
(it passes through empty bbox space). So the fix is about the LEFT overhang
(−188). **Fix: translate dx +196 and widen the advance 759 → 1210.**
Ink [−188,27,1007,1169] → [8,27,1203,1169], centred in its advance; shape
unchanged. The +8 changeWeight "Invalid 2nd order spline in SplineRefigure2"
warning from v0.166 was already checked benign (0 crossings, validate 0).
**Pixel re-check on the final v0.167 TTF: 0 shared ink pixels in 6 of 7 words**
(হঠাৎ, সৎ, উৎপাত, উৎসাহ, মৎস্য, উৎস). **Residual: বিৎ still shows 3,700 px**
(ৎ vs ব) — the preceding ব's ink overhangs its advance by 167 units
(bn_ba ink to x 1104 on advance 937) and its right stroke grazes the ৎ's loop.
That is the ব's width/advance issue, not the ৎ's placement — the ৎ is now
correctly inside its advance. It belongs to the v0.168 spacing/advance pass
(widen the ব's advance or narrow its ink), not to distorting the ৎ further.

## 3. The other flagged letters (steers 2–10)

All measured first; every flag was a real defect. Width ratios vs v0.120 are
now 1.05–1.24 (was 1.17–1.51).

| glyph | letter | fix | width before → after (base) | ratio | ridge before → after | other |
|---|---|---|---|---|---|---|
| bn_da | দ | re-trace at 140/164/180 all identical (solid ink, not a threshold artefact) → manual repair: tail tip up-left ~40–50, diagonal lower-right points left 30 | 1096 → 1096 (1046) | 1.048 | 76.8 → 76.8 | height 1158 → 1106; reads balanced now |
| bn_yya | য় | horizontal scale ×0.90 about ink centre (see reduction below) | 1478 → 1330 (1032) | 1.289 | 84.5 → 76.8 | top 1157, tail −279 kept exact |
| bn_ga | গ | stem excursion DELETED (see below), tail flick shortened +35 in x | 1219 → 1219 (987) | 1.235 | 92.2 → 92.2 | top 1383 → 1226; stem flush with bar |
| bn_ca | চ | horizontal scale ×0.88 about ink centre | 1091 → 960 (880) | 1.091 | 83.1 → 78.3 | top 1157, bottom 111 kept |
| bn_jha | ঝ | horizontal scale ×0.85 about ink centre | 1739 → 1479 (1190) | 1.243 | 92.2 → 76.8 | top 1343, bottom 19 kept |
| bn_nya | ঞ | re-trace at Otsu **193** (photo 16 r1c10); bottom-left diagonal KEPT (v0.120 has the same sweep — it is his stroke, not the neighbour's ink) | 1745 → 1742 (1485) | 1.173 | 75.6 → 79.1 | strokes fuller, no scratched look |
| bn_na | ন | manual join: stub tip (599,446) → (520,500); removeOverlap merged stub+loop (4 → 3 contours); then scale ×0.90 | 1264 → 1138 (970) | 1.173 | 92.2 → 84.5 | loop joined, one connected shape |
| bn_sa | স | re-trace at Otsu **189** (photo 16 r4c1); hook already rounds in the new trace (smooth U-turn, no manual rounding needed); then scale ×0.88 | 1468 → 1306 (1130) | 1.156 | 84.5 → 84.5 | middle strokes solid, hook rounded |
| bn_uu | ঊ | fork removed: weaker tail stroke (points i81–i101, ~30 units) deleted, old i102 reflagged on-curve, off-curve (520,380) inserted after i80 | 1196 → 1196 (1291) | 0.926 | 92.2 → 92.2 | single tail; hooks left as-is (acceptable) |
| bn_aa | আ | hook capped 1336 → 1157 (pts i1–i8); stem straightened (left edge x → 1525, right edge x → 1445); then scale ×0.90 | 1987 → 1789 (1696) | 1.055 | 84.5 → 76.8 | top 1336 → 1157; bar top left wavy (v0.169 matra pass) |
| bn_i | ই | horizontal scale ×0.88 about ink centre | 1355 → 1193 (1090) | 1.094 | 85.9 → 84.5 | top 1616 kept |
| bn_ii | ঈ | very gentle scale ×0.95 only (already on target); hook left as-is | 1125 → 1069 (1106) | 0.967 | 84.5 → 84.5 | still thinner/more open than base's bold ঈ — his character, not forced |
| bn_ri | ঋ | horizontal scale ×0.85 about ink centre | 1638 → 1392 (1234) | 1.128 | 84.5 → 76.8 | parts pulled together, no longer loose |

**Re-trace threshold correction (important):** the briefs said "LOWER Otsu", which
is backwards. Measured, lower thresholds make strokes THINNER and more
fragmented (ঞ area 1206@150 vs 1391@178; ন 677@130 vs 958@172; স 1031@140 vs
1311@174). The faded light-grey strokes are only recovered by RAISING the
threshold. Chosen: ঞ photo 16 r1c10 at Otsu 193 (2 contours, area 1477, fuller
middle strokes, left-loop hole intact); স photo 16 r4c1 at Otsu 189 (2 contours,
area 1390, fuller zigzag). ন: NO threshold (130–202) connects the loop — the
diagonal is genuinely missing (pen lifted, paper blank); the join is manual.
দ: re-trace at 140/164/180 all give the identical 1-contour trace — the
diagonal/tail is solid ink, not a threshold artefact; manual repair only.
Photo 17's ঞ cell (extracted via grid_detect, `cells-17/cons_17_r1c10.png`)
traces nearly identically to photo 16's — no advantage; photo 16 @193 used.

**গ stem, row-above ink RULED OUT:** the crop above the গ cell in photo 16
(`specimens/ga-cell-context.png`) is blank paper — row 1 is the top row,
nothing above it. The tall stem is his own stroke, genuinely overshooting.
**গ fix, two attempts:** first the stem-top points were flattened to y=1210 —
that created a collinear fold (the contour retraced x 795–816 along y=1210)
and FontForge validate flagged bn_ga bit 4 (self-intersecting), a worsening
under the revert rule. So the stem-top excursion was DELETED instead (points
i0–i8 and i187–i193 removed; contour now runs i186 (721,1139) → i9 (818,1207),
the bar's top edge interpolated across the stem). Final bbox top 1226 (the bar
top), validate clean, and the render shows the stem flush with the bar.

**য় reduction:** the brief's ×0.85 was applied first, but re-measuring with
explicit `chr(0x09DF)` showed its ridge had fallen to 69.1 — BELOW the 71.8
band floor. (The earlier 84.5 reading was the decomposed য+nukta form, not
U+09DF — see the measurement trap below.) Scale reduced to ×0.90: width
1478 → 1330 (ratio 1.289), ridge 76.8, in band.
**ঝ watch:** its ridge also dropped 92.2 → 76.8 (−15.4) at ×0.85 — in band,
and the render shows its strokes still solid, not fragile. Kept; judge again
in the v0.168 specimen review.

**Measurement trap (matters for v0.170):** ড়/ঢ়/য় typed as decomposed
base+nukta in a script render as base+nukta and give WRONG ink boxes/ridges —
future scripts must use explicit codepoints `chr(0x09DC/0x09DD/0x09DF)`. This
trap bit the first touched-measure: its literal 'য়' was the decomposed form
(1181 wide instead of the true 1478). Fixed in `tools/measure_touched_v0167.py`
and re-measured.

**Rendering note:** a standalone combining mark (ং, ৃ) rendered through
HarfBuzz shows a dashed/dotted circle beside the mark — that is HarfBuzz's
dotted-circle placeholder for a lone mark, NOT a font defect; judge such
glyphs only by outline and in clusters. (The fixed-letters specimen renders
standalone marks with BASIC layout to avoid the placeholder.)

## 4. Verification (final TTF, SHA c18502d7…)

- **HarfBuzz: 22/22** representative samples — all exact context, substitution,
  cluster and advance checks passed. The 3 reviewed candrabindu offsets
  preserved exactly at UPM 1536: কাঁ −450,+125; চাঁ −278,+125; ক্ষ্মাঁ −632,+125.
- **Consonant-pair grid: 1,369/1,369 identical** to v0.120; **.notdef = 0**.
- **Sign contexts: 13 clusters identical**, 3 khanda-ta words same glyphs,
  advance 1210 confirmed.
- **Ink-box check:** worst |top_err − expected| = 7.5 units over 83 glyphs
  (tolerance 8). V0167_FIX entries: bn_ga −169, bn_aa −184 (the deliberate
  top moves: গ stem 1383→1226, আ hook 1336→1157).
- **OTS: clean** (`ots-sanitize` — "File sanitized successfully!").
- **FontForge validate: 62 → 47 flagged glyphs** (v0.166 → v0.167). No TOUCHED
  glyph worsened — the revert rule needed no revert. 15 glyphs LOST their
  bit-32 (missing extrema, cosmetic) flag because the build's `addExtrema`
  added extrema points. The only bit-4 (self-intersecting) glyph is
  bn_vedic_anusvara (36 = 32+4), pre-existing in v0.166 and NOT a touched
  glyph. The গ's bit-4 from the first flatten attempt was fixed by the
  deletion (see §3). Remaining flags are all bit 32 (missing extrema,
  cosmetic) on glyphs already flagged in v0.166.
- **ৎ pixel check:** 0 shared ink pixels in 6/7 words; বিৎ residual 3,700 px
  (ব's overhang — see §2).
- **Table comparison:** only GPOS, glyf, hmtx, cmap, head, name, maxp, loca
  differ; GSUB, GDEF, OS/2, attribution and license name records preserved.
- hhea minRightSideBearing = −926 (derived from glyf/hmtx; was −654 in
  v0.120/v0.150) — from the wide ink glyphs and the ৎ's right overhang; a
  derived metric, not a failure. It will move again in the v0.168 spacing pass.

## 5. Specimens (all in `v0167-prep/specimens/`)

- `before-after-v0.167.png` — (a) ক + each sign/mark, v0.166 grey vs v0.167
  black, with baseline/headline guides; the 3 khanda-ta words.
- `v0167-sign-demo.png` — (b) the 13 clusters large, each sign in a real word,
  sentences using them heavily, cluster row v0.166 vs v0.167.
- `invitation-v0.167.png` — (c) the Peace School & College invitation sentences
  re-rendered in v0.167 (same text as v0.166).
- `fixed-letters-v0.167.png` — (d) ং/ৃ/ৎ before/after in real words
  (বাংলা, কাঁদ, কৃষক, হঠাৎ, সৎ, উৎপাত).
- `touched-letters-v0.167.png` — (e) the 13 repaired/resized letters large
  (v0.166 grey vs v0.167 black) plus their words (দিন/দাদা/বাংলাদেশ,
  মায়া/ছায়া, গরু/গান/বাংলা, চাঁদ/চোখ/চা, ঝড়/ঝাপসা, মিঞা/কিঞ্চিৎ,
  নদী/নাম/কান, সকাল/মাস/বসা, ঊষা/ঊন, আম/আসা/বাংলা, ইদ/ইতি, ঈদ/ঈশ্বর,
  ঋণ/ঋতু).
- Also: `swoosh-compare.png` (fresh vs v0.150 swoosh), `intermediate-surgery.png`,
  `khanda-ta-test.png`, `khanda-ta-invitation-test.png`, `nya-base-vs-current.png`,
  `ga-cell-context.png`, `retrace-candidates.png`, `threshold-test/`.

**What I see in the specimens (honest):** the clusters look more even in size
now — কি/কৈ/কৃ visibly narrower, কো/কৌ visibly wider, and no sign looks
stretched or squashed or loses its character; the marks still sit right. The
ং's swoosh dips below the baseline in বাংলা/কাঁদ/সংসার like the base font's.
The ৃ tucks under the ক in কৃষক. The ৎ reads cleanly in হঠাৎ/সৎ/উৎপাত. The
গ's stem no longer pokes above the matra and the bar top is clean. The ন's
loop is joined. The ঊ's tail is single. The আ's stem looks straight. The ঞ/স
strokes look solid, the স's hook is a smooth curve. The য় no longer dwarfs
its neighbours in মায়া/ছায়া. The ঝ is narrower but its strokes still look
solid (ridge 76.8 — watch it in v0.168). The invitation reads naturally in
connected text. The matra still does not form a continuous line across words
(each letter's headline is still its own hand-drawn stroke) and the word
spacing is still uneven — both are the v0.168/v0.169 passes, deliberately NOT
done here.

## 6. Deliberately left alone (and why)

- **Spacing / advances:** NOT done in v0.167 (John's word-spacing complaint is
  a dedicated v0.168 pass — even advances across all letters). Only Khanda_Ta's
  advance changed (759 → 1210), because its placement fix required it.
- **Matra straightening:** NOT done (v0.168/v0.169 word-polish pass), except
  the আ hook cap and গ stem trim, which are the flagged-letter fixes.
- **ো/ৌ targets:** not stretched anywhere near double (×1.20 cap) — their
  narrow single-stroke forms are his handwriting's character.
- **ৎ's traced shape:** unchanged — only its placement (dx +196) and advance.
- **ঈ's shape:** not forced to the base font's bold compact form — it is
  already on target for size; its thinner, more open look is his character.
- **দ's structure:** not redrawn from the base font — his diagonal still sweeps
  down-right; only the tail was shortened and the diagonal nudged toward balance.
- **Digits and the global size pass:** queued for v0.168 (see below).
- **The fresh swoosh:** rejected (too wide, invades the next letter) in favour
  of the v0.150 swoosh contour.

## 7. Leftover list (v0.168 / v0.169, per the plan)

- **v0.168 — global size evening + spacing + digits:** even widths across ALL
  83 handwriting glyphs (same gentle capped approach); even advances (fixes
  the বিৎ residual and the uneven ink-to-ink gaps); the queued digit fixes —
  ০ round + ×1.05, ১ scale ×0.82–0.85 + thicken +15–20, ২/৩ reshape, ৪
  straighten axis, ৫ close the slit + re-trace, ৭/৮ thicken legs/arms, ৯ scale
  ×0.88–0.90. Watch the ঝ's ridge (76.8) in the v0.168 specimens.
- **v0.169 — matra + word polish:** straighten every handwriting glyph's
  headline to a horizontal bar at y=1157 with even thickness so adjacent
  headlines meet, combined with the spacing evening.
- **v0.170 — conjunct replacement** (~250–300 cells, matched by shape against
  the GSUB ligature list, uncertain names shown to John). Still needed from
  John: the names of the 4 glyphs in photo 5. Remember the ড়/ঢ়/য়
  decomposed-codepoint trap (`chr(0x09DC/0x09DD/0x09DF)`).
- **v0.180 — symbols (optional, later):** Roman numerals, math, brackets,
  * # @ % &, ৳ (U+09F3).

## Build files

- `tools/build_intermediate_v0167.py` (+ `tools/intermediate-log.json`) —
  re-traces (ঞ@193, স@189, fitted to the v0.166 glyf boxes) + point surgery
  (গ/দ/ঊ/আ/ন). Intermediate SHA `df5e36a37efcfa09ddbda7eb1a4ced3c538f01a6d3aa04f737a5eb4dda3d0975`
  (rebuilt after the গ deletion fix; the first intermediate was
  `7193824c19e863a98876b364063916ee09489f7ab9d8149f40366bf982322bdf`).
- `tools/build_width_v0167.py` (+ `tools/width-transforms.json`) — FontForge:
  ন removeOverlap, 13 sign scales (left-edge pivot), ৃ shift, ৎ translate,
  9 centre scales.
- `tools/transplant_v0167.py` — copies the temp's outlines into a fresh v0.166
  copy, adds the ং swoosh (v0.150 contour), sets Khanda_Ta advance 1210,
  head.fontRevision = 0.167. (The fresh-swoosh version is saved at
  `/tmp/v0167-fresh.ttf`, SHA 54b53cc0… — NOT the delivered font.)
- `tools/measure_signs_v0167.py`, `tools/measure_touched_v0167.py` —
  measurements (`checks/sign-measure-v0.167.tsv/.json`,
  `checks/touched-measure-v0.167.tsv/.json`).
- `tools/verify_pranoti_v0167_beta.py` — the verification suite
  (`checks/summary-v0.167.txt`, `specimens/matched-v0.166-v0.167-review.png`).
- `tools/render_signs_v0167.py`, `tools/render_invitation_v0167.py`,
  `tools/render_fixed_touched_v0167.py`, `tools/test_khanda_ta.py`,
  `tools/retrace_consonants.py`, `tools/render_retrace_candidates.py`,
  `tools/investigate_traces.py`, `tools/fontforge_validate.py`.
- `cells-17/cons_17_r1c10.png` — the photo-17 ঞ cell (extracted, not used).
