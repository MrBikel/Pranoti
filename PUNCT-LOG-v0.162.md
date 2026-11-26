# Punctuation fine-tuning — Pranoti v0.162-beta

Status: built and verified. No TTF modified in place; nothing pushed.
Base: `Pranoti-Regular-v0.161-beta.ttf` (SHA-256 `9a46dd66…bdb5e77`, verified
before touching it). Output: `Pranoti-Regular-v0.162-beta.ttf`,
SHA-256 `8a4812d097a95cf1c44dfa890875d2aadc100220c20d9034461d22b5d1309f14`,
397,456 bytes, 652 glyphs, cmap 204, `head.fontRevision = 0.162`.
Method: FontForge contour transforms / changeWeight on the 10 touched
glyphs only, then transplant of those 10 outlines into a fontTools copy of
v0.161 (same pattern as v0.161's `transplant.py`), so every other table
stays byte-identical to v0.161 by construction.

## 1. Inventory — 41 punctuation glyphs

14 are John's handwriting (re-traced in v0.160); 27 are the base font's.
No cmap entries were invented: ellipsis … (U+2026) and straight-quote
combos stay absent, as in v0.160. Measurements are rasterised TRUE ink
boxes at 1536 px em (the v0.160 lesson: glyf header bboxes include
off-curve overshoot). Reference: letter stroke median 84.5 units,
headline y=1157, baseline 0, UPM 1536.

| glyph | char | source | adv | ink W×H (v0.161) | top | bottom |
|---|---|---|---|---|---|---|
| danda | । | handwriting | 681 | 86×1076 | 1030 | −46 |
| period | . | handwriting | 540 | 301×250 | 214 | −36 |
| comma | , | handwriting | 540 | 369×519 | 218 | −301 |
| semicolon | ; | handwriting | 597 | 497×1254 | 949 | −305 |
| colon | : | handwriting | 597 | 394×981 | 945 | −36 |
| hyphen | - | handwriting | 710 | 840×155 | 539 | 384 |
| emdash | — | handwriting | 1148 | 1191×130 | 654 | 524 |
| slash | / | handwriting | 597 | 1172×1638 | 1408 | −230 |
| quoteleft | ‘ | handwriting | 507 | 377×499 | 1357 | 858 |
| quoteright | ’ | handwriting | 507 | 366×504 | 1311 | 807 |
| quotedblleft | “ | handwriting | 891 | 958×503 | 1361 | 858 |
| quotedblright | ” | handwriting | 911 | 892×503 | 1310 | 807 |
| question | ? | handwriting | 792 | 467×1123 | 1084 | −39 |
| exclam | ! | handwriting | 696 | 285×1351 | 1074 | −277 |
| quotedbl | " | base | 739 | 487×440 | 1203 | 763 |
| quotesingle | ' | base | 341 | 173×440 | 1203 | 763 |
| parenleft | ( | base | 667 | 548×1775 | 1349 | −426 |
| parenright | ) | base | 667 | 532×1769 | 1346 | −423 |
| bracketleft | [ | base | 485 | 244×1296 | 1210 | −86 |
| bracketright | ] | base | 531 | 240×1300 | 1212 | −88 |
| braceleft | { | base | 1011 | 489×1757 | 1408 | −349 |
| braceright | } | base | 1011 | 489×1757 | 1408 | −349 |
| doubledanda | ॥ | base | 943 | 436×1085 | 1034 | −51 |
| endash | – | base | 849 | 663×131 | 654 | 523 |
| asterisk | * | base | 1052 | 780×874 | 1408 | 534 |
| plus | + | base | 1183 | 1049×1057 | 1060 | 3 |
| less | < | base | 1183 | 1053×1088 | 1078 | −10 |
| equal | = | base | 1183 | 1049×551 | 810 | 259 |
| greater | > | base | 1183 | 1059×1091 | 1080 | −11 |
| at | @ | base | 1576 | 1521×1544 | 1245 | −299 |
| numbersign | # | base | 989 | 907×1352 | 1314 | −38 |
| dollar | $ | base | 790 | 729×1130 | 1030 | −100 |
| percent | % | base | 1308 | 1200×1114 | 1059 | −55 |
| ampersand | & | base | 1169 | 1023×1202 | 1157 | −45 |
| backslash | \ | base | 597 | 659×1640 | 1408 | −232 |
| asciicircum | ^ | base | 800 | 639×733 | 907 | 174 |
| underscore | _ | base | 1210 | 1204×131 | 115 | −16 |
| grave | ` | base | 470 | 268×260 | 880 | 620 |
| bar | \| | base | 346 | 131×2039 | 1599 | −440 |
| asciitilde | ~ | base | 900 | 722×312 | 631 | 319 |
| divide | ÷ | base | 1103 | 949×888 | 940 | 52 |

Full per-glyph data (advances, side bearings, component boxes, ridge
stroke): `checks/punct-inventory-v0.161.tsv` / `.json` (before) and
`checks/punct-inventory-v0.162.tsv` / `.json` (after).

## 2. What was inconsistent (v0.161, with numbers)

Measured against the v0.120 base font as a design reference — this caught
three apparent "bugs" that are actually the base font's design (see §4).

- **Dot family, four different sizes:** period 301×249 (the reference);
  colon dots 300×245 (upper) vs 260×250 (lower), and offset 114 units
  apart in x (centres 236 vs 350); semicolon dot 375×296 (oversized);
  question dot 123×189 (a speck); exclam dot 161×182 (a speck).
- **Danda short of the headline:** top 1030 vs headline 1157 (−127).
  Doubledanda the same (top 1034). Doubledanda bars 131 wide vs the
  danda's 86 — the two do not read as a pair.
- **Hyphen longer than the en dash:** hyphen 840 > endash 663 < emdash
  1191. (The base font is ordered correctly: 532 < 663 < 913.)
- **Slash heavy:** ridge 104.5 vs the 84.5 letter median (+24%).
  Backslash heavier still: 145.7.
- **Em dash thin for its family:** ridge 107.5 vs hyphen 145.9 and
  endash 138.2.
- **? and ! tops already match** (1084 vs 1074) — no change needed there.

## 3. Per-glyph changes (v0.161 → v0.162)

All advances unchanged. No letter glyph, GSUB/GPOS/GDEF, cmap, or glyph
order touched.

| glyph | change | before → after |
|---|---|---|
| danda | vertical stretch ×1.118 about the bottom | 86×1076, top 1030 → 86×1203, top **1157**; stroke stays 84.5 |
| doubledanda | each bar scaled 131→86 wide about its own centre + vertical stretch to headline | bars 131×1085 → **86×1207**, top 1034 → **1157**; ridge 138.2 → 92.2 |
| colon | upper dot translated to centre-x 298; lower dot scaled x-only 260→300 and centred at 298 | dots 300/260 wide, centres 236/350 → **both ~300 wide, centres 298/296**; ink width 394 → 301 |
| semicolon | dot (outer contour + inner slot, transformed together) scaled 375→300, centred x 270, top 945 | dot 375×296 → **300×236 @ 709–945**; tail untouched |
| question | dot scaled to 280×245, bottom set to the period's bottom | dot 123×189 → **278×243, y −34–209**; curve untouched |
| exclam | dot scaled to 280×245, centred under the bar; y kept | dot 161×182 → **275×239, y −304–−65**, centre-x 334 vs bar 331; bar untouched |
| hyphen | horizontal scale 840→532 about its centre; y-band kept | 840×155 → **532×154**, y 384–538; ridge 145.9 → 122.9 |
| slash | changeWeight(−20) | ridge 104.5 → **85.9** (≈ the 84.5 median) |
| backslash | changeWeight(−55) | ridge 145.7 → **92.5** |
| emdash | changeWeight(+25) | ridge 107.5 → **130.6** (dash family now 123–138) |

Reverts: **none.** No touched glyph's FontForge validate worsened
(§5); no distortion was found in the specimens.

## 4. Deliberately left alone — and why

- **Quote families (curly + straight).** The left/right height offset
  (left quotes top ~1359, right ~1310) is the base font's design, not an
  error: v0.120 shows the identical offset (left 1361/856, right
  1314/805). Straight quotes sit lower than curly quotes in the base
  font too (top 1203 vs ~1335). Sizes match within each pair. Left as
  designed.
- **Exclamation dot below the baseline.** Also the base font's design:
  v0.120's ! dot is at y −279–−52. Only its size was fixed (161→280);
  its position was kept.
- **Hyphen's low y-band (centre ~461 vs en/em ~589).** The base font
  puts the hyphen there too (384–540 vs 524–654). Only its length was
  fixed.
- **? curve / ! bar.** Tops already match (1084 vs 1074). Untouched.
- **Parens / brackets / braces.** Each pair is internally consistent
  (heights within 6 units, tops within 3). Their cross-family heights
  (parens 1775, braces 1757, brackets ~1298) are the base font's design.
- **Comma, period, endash, and all other base symbols** (+ < = > @ # $
  % & \ ^ _ ` | ~ ÷ *): measured, internally consistent, untouched.
  The 31 untouched punctuation glyphs are byte-identical in ink box and
  advance between v0.161 and v0.162 (verified programmatically).

## 5. Verification — all PASS

- **HarfBuzz 22/22**, 3 candrabindu offsets exact; **consonant-pair grid
  1,369/1,369** identical to v0.120; 0 `.notdef`.
- **OTS clean** ("File sanitized successfully!").
- **FontForge validate:** 73 → 65 flagged glyphs; every touched glyph
  improved (32 → 0) or stayed 0; **nothing worsened, no reverts**. The
  one remaining bit-2 flag is pre-existing `bn_vedic_anusvara`.
- **Self-intersections:** 0 crossings on all 10 touched glyphs
  (`tools/check_self_intersection.py`); min consecutive point distance
  ≥ 1.00 (no degenerate segments).
- **Ink boxes (83 re-traced glyphs):** worst |top_err − expected| = 7.0
  (tolerance 8). The three expected top moves are the tuning itself:
  danda +127, emdash +12, slash −10 (documented in the verify script).
- **Tables vs v0.120:** only GPOS, glyf, hmtx, cmap, head, name, maxp,
  loca differ; GSUB, GDEF, OS/2, attribution/license names preserved.
  `hhea.minRightSideBearing` −1147, derived from the font's own
  glyf/hmtx (moved from −1137: the hyphen's new side bearings).
- **Specimens inspected:** before/after grid of all 41 punctuation
  glyphs; punctuation-in-sentences demo; invitation re-render; matched
  v0.161/v0.162 review at 12/16/24/32 px. Even rhythm, no collisions,
  nothing floats or sinks, no distortion. The danda now reads as a
  full-height sentence-ender; the ? and ! dots are visible; the colon
  dots stand vertically aligned; the hyphen is shorter than the en dash.

## 6. Method notes (traps found, for the next build)

- **`glyph.foreground` returns a COPY of the layer.** Contour transforms
  only stick if the layer is assigned back (`g.foreground = layer`).
  The first run silently did nothing (bboxes unchanged) — caught by the
  before/after bbox log, not by an error.
- **`psMat.compose(a, b)` applies a FIRST, then b, in this FontForge
  build** (verified numerically: the naive scale-about order collapsed
  doubledanda's bars to x 79–261). `scale_about` must be
  `compose(translate(-c), compose(scale, translate(c)))`. The wrong
  order still preserves widths but shifts pivots — the hyphen, question
  and exclam dots flew off-centre in the first run and were caught by
  the bbox log.
- **In-session `glyph.validate()` after addExtrema() returns 524288 /
  524320** (also in the v0.161 changeweight logs); after generate +
  reopen the same glyph validates 0. The value is transient — the
  revert rule must compare validate on the FINAL transplanted TTF, not
  the in-session log.
- **The semicolon dot is TWO contours** (outer dot + an inner slot,
  102×39). Both must be transformed together about the same centre or
  the slot is left behind. Found by asserting the contour count (3,
  not the assumed 2).
- **Measure the v0.120 base font before "fixing" anything.** Three
  apparent bugs (! dot below baseline, quote left/right offset,
  hyphen's low band) are AdorshoLipi's deliberate design, reproduced
  exactly in John's handwriting fits. Only sizes/alignments that
  break the family were changed.

## Files

Work is entirely in `~/workspace/fonts/bengali-hand/v0162-prep/` (TTF,
`PUNCT-LOG-v0.162.md`, `checks/` × 11, `specimens/` × 5, `tools/` × 11
incl. `measure_punct_v0162.py`, `build_punct_v0162.py`,
`transplant_v0162.py`, `verify_pranoti_v0162_beta.py`,
`render_punct_specimens.py`, `render_punct_before_after.py`,
`render_invitation_v0162.py`, `check_self_intersection.py`,
`fontforge_validate.py`, `punct-transforms.json`). No verification
failed; nothing was claimed that wasn't measured.
