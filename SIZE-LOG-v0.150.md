# Pranoti v0.150-beta — Size Log (size normalisation & beautiful arrangement)

Built 2026-11-26 from `Pranoti-Regular-v0.140-beta.ttf` (SHA-256
`ad045a935a4b4243369083151e3779a327b83f1b3fedd40c819e83734f97888c`).
Output: `Pranoti-Regular-v0.150-beta.ttf`, 435,752 bytes — see SHA-256 below.
Family "Pranoti", version v0.150-beta, UPM 1536, 652 glyphs, cmap 204.

## 0. What the measurements actually showed (the real mismatch)

The user's complaint was "no letter matches another in size". Measuring
**true ink** (rasterised at 1536 px) against AdorshoLipi showed the mismatch
is NOT height — heights already matched AdorshoLipi within ~±30 units for
nearly every letter. The real mismatches were:

1. **Vertical position.** Letters sat low/high against the common headline
   and baseline. Worst cases (ink top vs AdorshoLipi's ink top): ক −22,
   ঘ −21, ঙ −12, চ −11, ড's loop bottom −27, ঢ −17, ভ −16, ট −26,
   ঠ's loop bottom +32 (too low), ঞ's tail −28 (below the baseline),
   ধ −17 below baseline, য়'s tail −28, ড় −19, ঢ় −17. Digits sat
   ~18–27 units low across the board.
2. **Visual weight (ink area).** Lightest vs AdorshoLipi: ত 0.836, ঔ 0.841,
   ঙ 0.854, ই 0.869, ঐ 0.870, ও 0.871, এ 0.913, ভ 0.925. Heaviest:
   গ 1.260, ধ 1.154, ল 1.133, ণ 1.125, ২ 1.120, স 1.108, র 1.113.
   Ink-area ratio spread before: **0.836–1.260**.
3. **Width.** Most handwriting letters are narrower than AdorshoLipi's
   in the same advance: ক 1149 vs 1223 (−74), ত 1102 vs 1199 (−97),
   ভ 1064 vs 1157 (−93), ড 1064 vs 1139 (−75), ছ 961 vs 1022 (−61),
   ঝ 1149 vs 1195, ঘ 980 vs 1026, ঙ 852 vs 884, চ 854 vs 893, ঠ 843 vs 893.
   Narrow letters sat lost inside AdorshoLipi-sized advances — that is a
   big part of why they looked "smaller" than their neighbours.

Result after v0.150: ink-top error vs AdorshoLipi is now **exactly 0 for
all 56 letters** (every top aligned); ink-area spread narrowed to
**0.888–1.188**; width error narrowed on the narrow side (−97 → −73).
The residual weight spread is the handwriting's own stroke-weight
variation — uniform scaling cannot remove it without distorting the
letters (see §5).

## 1. Method (per glyph, 56 letters: 11 vowels + 35 consonants + 10 digits)

- **Ink-based measurement.** All sizes come from rasterised ink bboxes
  (1536 px, `ink-measure.json`), NOT from the fontTools outline bbox.
  See §4 for why this matters.
- **Mild uniform scale** about the ink-bbox centre: s = average of the
  ink-area scale and the ink-box scale vs AdorshoLipi, clamped to
  [0.97, 1.08] and further capped so the resulting ink height stays
  within ±40 units of AdorshoLipi's height for the same letter. Never
  distorts stroke weight (x and y scaled together).
- **Translate** so the scaled ink top matches AdorshoLipi's ink top for
  the same letter (common headline 1157 for plain letters; taller for
  ascenders; per-digit tops for digits) and the ink centre-x matches
  AdorshoLipi's ink centre-x for the same letter. Horizontal shift
  capped at ±40 units so the (unchanged) GPOS candrabindu anchors stay
  visually aligned.
- **Side bearings re-centred:** hmtx lsb = new outline xMin. **Advances
  UNCHANGED** (verification requires them identical to v0.120).
- The 13 vowel signs/marks and the 4 new glyphs (U+0980, U+09FB, U+09FC,
  U+09FE) were NOT resized or moved.

## 2. Measurement table (ink bbox, units at UPM 1536)

`h` = ink height, `w` = ink width. "ado" = AdorshoLipi, the target.
`adv` = advance (unchanged from v0.120/v0.140).

| glyph | ch | scale | dx | dy | ink h before | ink h after | ado h | ink w before | ink w after | ado w | adv |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bn_a | অ | 0.986 | -4 | +19 | 1164 | 1148 | 1150 | 1311 | 1292 | 1296 | 1245 |
| bn_aa | আ | 0.974 | +3 | +22 | 1382 | 1346 | 1361 | 1689 | 1645 | 1667 | 1619 |
| bn_i | ই | 1.0258 | +6 | -6 | 1746 | 1791 | 1751 | 1096 | 1125 | 1103 | 989 |
| bn_ii | ঈ | 1.019 | -6 | -0 | 1604 | 1634 | 1600 | 1118 | 1140 | 1116 | 1079 |
| bn_u | উ | 1.009 | +3 | +6 | 1484 | 1497 | 1483 | 1178 | 1188 | 1176 | 1124 |
| bn_uu | ঊ | 0.991 | +4 | +9 | 1502 | 1488 | 1477 | 1281 | 1270 | 1262 | 1177 |
| bn_ri | ঋ | 0.976 | -2 | +27 | 1277 | 1246 | 1273 | 1258 | 1227 | 1245 | 1267 |
| bn_e | এ | 1.024 | +4 | -1 | 1158 | 1186 | 1158 | 925 | 947 | 927 | 1216 |
| bn_ai | ঐ | 1.0229 | -15 | -6 | 1746 | 1786 | 1746 | 1125 | 1151 | 1087 | 1267 |
| bn_o | ও | 1.036 | +3 | -4 | 982 | 1017 | 980 | 960 | 994 | 964 | 1134 |
| bn_au | ঔ | 1.0276 | -4 | -8 | 1558 | 1601 | 1561 | 1108 | 1139 | 1107 | 1298 |
| bn_ka | ক | 1.037 | +40 | +2 | 1106 | 1147 | 1136 | 1149 | 1191 | 1223 | 1197 |
| bn_kha | খ | 1.01 | +6 | +5 | 1315 | 1328 | 1322 | 972 | 982 | 992 | 1023 |
| bn_ga | গ | 0.9709 | +18 | +30 | 1373 | 1333 | 1373 | 981 | 952 | 1004 | 1021 |
| bn_gha | ঘ | 1.024 | +28 | +8 | 1127 | 1154 | 1146 | 980 | 1004 | 1026 | 993 |
| bn_nga | ঙ | 1.0327 | +13 | -6 | 1071 | 1106 | 1066 | 852 | 880 | 884 | 964 |
| bn_ca | চ | 1.012 | +24 | +5 | 1037 | 1049 | 1044 | 854 | 865 | 893 | 864 |
| bn_cha | ছ | 1.011 | +36 | +3 | 1279 | 1293 | 1298 | 961 | 972 | 1022 | 954 |
| bn_ja | জ | 0.98 | +4 | +25 | 1133 | 1110 | 1132 | 1277 | 1252 | 1282 | 1240 |
| bn_jha | ঝ | 1.009 | +29 | +23 | 1301 | 1313 | 1312 | 1149 | 1159 | 1195 | 1158 |
| bn_nya | ঞ | 0.99 | -40 | +7 | 1171 | 1159 | 1144 | 1477 | 1462 | 1456 | 1609 |
| bn_tta | ট | 0.985 | +22 | +12 | 1490 | 1468 | 1465 | 948 | 934 | 992 | 876 |
| bn_ttha | ঠ | 1.01 | +31 | +4 | 1636 | 1652 | 1680 | 843 | 851 | 893 | 857 |
| bn_dda | ড | 1.001 | +40 | -0 | 1046 | 1047 | 1019 | 1064 | 1066 | 1139 | 1099 |
| bn_ddha | ঢ | 0.994 | +17 | +14 | 998 | 992 | 992 | 880 | 874 | 908 | 878 |
| bn_nna | ণ | 0.971 | +8 | +30 | 1346 | 1307 | 1338 | 897 | 870 | 902 | 950 |
| bn_ta | ত | 1.0621 | +40 | -30 | 982 | 1043 | 1003 | 1102 | 1170 | 1199 | 1158 |
| bn_tha | থ | 1.006 | +16 | -3 | 1367 | 1375 | 1342 | 974 | 980 | 978 | 1005 |
| bn_da | দ | 1.003 | +18 | +7 | 1160 | 1163 | 1150 | 1028 | 1031 | 1053 | 1007 |
| bn_dha | ধ | 0.97 | +14 | +27 | 1199 | 1163 | 1191 | 840 | 815 | 861 | 948 |
| bn_na | ন | 0.994 | +16 | +12 | 1179 | 1172 | 1171 | 955 | 950 | 978 | 946 |
| bn_pa | প | 0.993 | +22 | +16 | 1292 | 1283 | 1289 | 1023 | 1016 | 1058 | 1124 |
| bn_pha | ফ | 1.008 | +10 | +6 | 1136 | 1145 | 1142 | 1299 | 1309 | 1311 | 1281 |
| bn_ba | ব | 0.999 | +22 | +12 | 1166 | 1165 | 1160 | 946 | 945 | 981 | 937 |
| bn_bha | ভ | 1.0374 | +40 | -6 | 989 | 1026 | 986 | 1064 | 1104 | 1157 | 1122 |
| bn_ma | ম | 1.001 | +2 | +11 | 1152 | 1153 | 1148 | 1066 | 1067 | 1063 | 1036 |
| bn_ya | য | 0.976 | -1 | +23 | 1161 | 1133 | 1152 | 1038 | 1014 | 1028 | 999 |
| bn_ra | র | 0.973 | +4 | +26 | 1146 | 1115 | 1140 | 966 | 939 | 967 | 935 |
| bn_la | ল | 0.97 | +0 | +26 | 1162 | 1127 | 1152 | 1181 | 1146 | 1176 | 1140 |
| bn_sha | শ | 0.988 | -2 | +17 | 1342 | 1326 | 1332 | 1212 | 1197 | 1207 | 1068 |
| bn_ssa | ষ | 1.016 | +18 | +4 | 1140 | 1158 | 1140 | 989 | 1004 | 1022 | 986 |
| bn_sa | স | 0.981 | +21 | +20 | 1158 | 1136 | 1152 | 1105 | 1085 | 1137 | 1101 |
| bn_ha | হ | 1.006 | +17 | +5 | 1315 | 1323 | 1314 | 992 | 998 | 1018 | 888 |
| bn_rra | ড় | 0.997 | +19 | +15 | 1381 | 1377 | 1375 | 1119 | 1115 | 1147 | 1101 |
| bn_rha | ঢ় | 0.974 | -2 | +28 | 1348 | 1313 | 1341 | 931 | 906 | 920 | 890 |
| bn_yya | য় | 0.971 | -1 | +30 | 1478 | 1435 | 1459 | 1038 | 1008 | 1028 | 989 |
| bn_zero | ০ | 1.033 | +40 | -5 | 798 | 824 | 787 | 727 | 751 | 810 | 1054 |
| bn_one | ১ | 1.014 | +4 | +2 | 1184 | 1201 | 1176 | 604 | 613 | 599 | 925 |
| bn_two | ২ | 0.975 | +16 | +23 | 1326 | 1293 | 1314 | 893 | 870 | 912 | 1009 |
| bn_three | ৩ | 1.0141 | +27 | -6 | 996 | 1010 | 970 | 956 | 970 | 982 | 1068 |
| bn_four | ৪ | 1.004 | -27 | +8 | 1115 | 1119 | 1107 | 758 | 762 | 750 | 1046 |
| bn_five | ৫ | 0.97 | +14 | +26 | 1112 | 1079 | 1101 | 897 | 870 | 928 | 1054 |
| bn_six | ৬ | 0.989 | +15 | +14 | 1114 | 1102 | 1102 | 931 | 921 | 949 | 1017 |
| bn_seven | ৭ | 0.989 | -10 | +15 | 1123 | 1111 | 1115 | 741 | 732 | 768 | 1060 |
| bn_eight | ৮ | 0.989 | +25 | +13 | 1093 | 1081 | 1080 | 944 | 934 | 980 | 1087 |
| bn_nine | ৯ | 1.0131 | -2 | -4 | 1149 | 1164 | 1124 | 847 | 858 | 864 | 1015 |

Biggest resizes: ত ×1.062 (lightest letter), ভ ×1.037, ক ×1.037,
ও ×1.036, ঙ ×1.033, ০ ×1.033; গ ×0.971, ধ ×0.970, ল ×0.970, ণ ×0.971,
য় ×0.971 (heaviest letters, scaled down). All 56 letters were resized
(×0.970–×1.062) and translated; no letter was left untouched, because
every one sat at least a few units off its AdorshoLipi target.

Horizontal shift hit the ±40 cap for: ক +40, ড +40, ত +40, ভ +40,
ছ +36, ঞ −40, ০ +40. These letters' ink centres were further from
AdorshoLipi's than 40 units; the cap protects the candrabindu anchor
alignment (see §5).

## 3. Artificial engineering — what was fixed, and what was examined

### Actually fixed
- **ঞ (bn_nya) — two degenerate contours deleted.** Contours c4 and c5
  were separate closed contours, each a long thin sliver (bbox ~1000×520,
  area 1840 and 902 sq units, average width < 2 units) that rendered as
  two stray diagonal hairlines crossing the whole glyph. They are tracing
  artefacts, not strokes (a real stroke is ~110 units wide). Deleted;
  the rest of the glyph is untouched. Verified visually: the v0.150 ঞ is
  clean, no diagonal lines, and still reads as ঞ. Glyph now has 5
  contours (was 7).

### Examined and deliberately NOT extended
- **Loop bottoms that stop short of AdorshoLipi's depth:** ঠ's loop
  bottom 28 units short, ড's 28 short, ত's 40 short after the height
  cap. These are ≤40 units (≤2.6% of em, ~0.3 px at 16 px text).
  Extending a loop bottom means moving the U-turn's control point down
  — the same surgery that damaged real shapes in the discarded first
  attempt (§4). Not worth the risk at this size; left as designed.
- **ঙ's top — a hook, not a full matra.** AdorshoLipi's ঙ has a full
  horizontal matra; John's ঙ has a short hook/curl at the top left.
  This is his pen's shape, not an unfinished stroke — it reaches the
  headline (yMax now 1110, matching AdorshoLipi) and reads clearly as ঙ.
  Drawing a matra would invent a stroke, not complete one. Left as is.
- **ধ's pinched top loop, ঋ's roughness.** Shape character, not
  shortfalls. Left (known from v0.140).

### What the alignment itself fixed
The most visible "stroke fell short" cases were letters sitting low —
their bodies not reaching the headline/baseline (ক −22, ঘ −21, চ −11,
ভ −16, ড −27, ট −26, digits −18…−27). Those are now fixed by the
translation: every letter's top sits exactly on its AdorshoLipi headline
and its body sits where the reference puts it.

## 4. Method correction — and a discarded first attempt

**Ink bbox vs outline bbox.** fontTools' glyph bbox includes off-curve
control points. In these traced outlines the control points overshoot the
real ink by up to ~90 units (bn_ta: control y=126, true ink bottom
y=175; bn_ttha: control y=81, true ink bottom y=133). All v0.150
measurements use true ink bboxes; the earlier v3/v4-era outline-bbox
numbers overstate the mismatch.

**Discarded attempt (never shipped).** The first v0.150 build used the
outline bbox and a "spike collapse" that treated off-curve control
points as spike tips. That was wrong: the supposed tips are control
points, not ink — collapsing them moved real loop bottoms up by up to
96 units (ত's loop bottom 126→222, ঠ's 81→142) and inflated ত's scale
to ×1.23. That build was thrown away. Only two of the 44 candidates
were real zero-area folds, and both were control-point artefacts, not
ink. The remaining in-contour hairline folds (thin U-turns in the traced
outlines, visible at 200 px in ক, ত, ব, ৯) are sub-pixel at text sizes
and are left for a later batch — fixing them needs control-point surgery
with the same risk. The ঞ slivers (§3) were the only safe deletion
(separate contours).

## 5. Deliberately NOT changed

- Advances (all identical to v0.120 — required by verification).
- GSUB, GPOS, GDEF, cmap, OS/2, attribution/license name records.
- The 13 vowel signs/marks and the 4 new glyphs (U+0980, U+09FB, U+09FC,
  U+09FE) — not resized or moved.
- The ~375 AdorshoLipi conjunct ligatures — not size-fitted. They were
  built for AdorshoLipi-sized bases; the core letters moved by at most
  ±40 units horizontally, so ligature alignment is unaffected in
  practice, and the pair-grid regression (§6) confirms it.
- Letter shapes beyond the uniform scale + translate in §1. No stroke
  re-outlining, no weight normalisation (full stroke-width normalisation
  to a constant ~112 units would need skeleton-based re-outlining and
  risks changing John's handwriting character — already documented as
  out of scope in v0.140).
- GPOS candrabindu anchors — unchanged, so the 3 reviewed offsets stay
  exact. Note: base glyphs moved horizontally by up to 40 units, so the
  mark sits up to 40 units further left relative to the ink than before
  on the most-shifted bases (ক, ত, ভ, ড). 40 units ≈ 0.4 px at 16 px
  text — invisible in practice, and the HarfBuzz offsets are unchanged.

## 6. Verification (all in `checks/`, specimens in `specimens/`)

- `verify_pranoti_v0150_beta.py` — **PASS**:
  - 22/22 HarfBuzz samples exact (glyphs, clusters, advances); the 3
    reviewed candrabindu offsets exact: কাঁ (−450,+125), চাঁ (−278,+125),
    ক্ষ্মাঁ (−632,+125).
  - Consonant-pair grid **1,369/1,369 identical** to v0.120, 0 `.notdef`.
  - 4 new glyphs still render; candrabindu sits above all bases/ligatures.
  - Table comparison vs v0.120: only GPOS, glyf, hmtx, cmap, head, name,
    maxp, loca differ; GSUB, GDEF, OS/2, attribution preserved. GDEF
    classes intact (candrabindu=3, bn_ka=1, bn_k_ss_ma=2). GPOS features
    [('mark',[0,1])], lookups [4,5]. hhea minRightSideBearing −654,
    unchanged and confirmed against the font's own glyf/hmtx data.
- **OTS 8.2.1:** "File sanitized successfully!" — clean.
- **FontForge 20230101 validate:** 36 — identical to v0.140 (bit 32, no
  FontForge anchor points, expected; bit 4 on 33 glyphs, traced outlines
  with near-duplicate points, cosmetic). No new flags.
- **Visual check (looked at, not just generated):**
  - `specimens/before-after-v0.150.png` — all 56 letters, v0.140 vs
    v0.150, with true baseline (red) and headline y=1157 (blue) guides.
    Every v0.150 top sits on its headline; no letter floats or sinks.
  - `specimens/v0150-writing-demo.png` — headline "অভিযাত্রী",
    paragraph, alphabet, digits, and the test words চাঁদ, ক্ষমা, জ্ঞান,
    সংখ্যা ১২৩৪৫৬৭৮৯০, কাঁটা, চাঁপা, কাঁ, চাঁ, ক্ষ্মাঁ, গাঁ, পাঁ. Even
    rhythm, no collisions, no floating/sinking. The candrabindu sits
    well over each base.
  - `specimens/closeup-v0.150.png` — 200 px + 64 px views of the
    most-changed glyphs (ত, ভ, ক, ও, ঙ, ০, গ, ধ, ল, ঞ, ঠ, ঔ).
    The ঞ hairlines are gone; the resized letters are visibly more even.
  - `specimens/matched-v0.140-v0.150-review.png` — matched RAQM specimen
    at 12/16/24/32 px (from the verify script).
- **Known remaining unevenness (honest note):** at 12/16 px the letters
  are now evenly placed, but the stroke-weight variation of the original
  handwriting is still visible up close — গ/ধ/ল/ণ are still a touch
  heavier, ত/ঔ/ঙ/ও a touch lighter (area spread 0.89–1.19 after, vs
  0.84–1.26 before). Uniform scaling closed about a third of the gap;
  the rest needs re-outlining, which is a bigger job and risks changing
  John's handwriting character.

## 7. Files in `v0150-prep/`

- `Pranoti-Regular-v0.150-beta.ttf` — SHA-256
  `679ba5155faa048c039560469bdc174451f395a7852b79e88496bbab2aa40c93`
- `SIZE-LOG-v0.150.md` — this file
- `size-transforms.json` — per-glyph scale/dx/dy and ink bboxes
- `ink-measure.json` — per-glyph ink bboxes and ink-area ratios (v0.140 vs AdorshoLipi)
- `build_pranoti_v0150_beta.py` — the build script
- `verify_pranoti_v0150_beta.py` — the verify script (adapted from v0.140)
- `render_specimens_v0150.py` — the specimen renderer
- `checks/` — `summary-v0.150.txt`, `harfbuzz-22-samples-v0.150.tsv`,
  `consonant-pair-grid-v0.150.tsv`
- `specimens/` — `before-after-v0.150.png`, `v0150-writing-demo.png`,
  `closeup-v0.150.png`, `matched-v0.140-v0.150-review.png`
- Work files: `ink-bboxes.json`, `grid-v140-*.png`, `grid-ado-*.png`,
  `zoom-compare.png`, `spike-check.png` (measurement scratch)

## 8. Status

v0.150-beta is built, verified and visually checked locally. **Nothing
was pushed to GitHub and nothing was written into `github-repo/`.**
Docs integration into the repo (CHANGELOG/README/TEST-SUMMARY/CHECKSUMS)
happens later, after the user approves. No expert type-design sign-off
and no broad platform testing is claimed.
