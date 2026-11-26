# Pranoti v0.164-beta — Consonant fine-tuning log

Base: `../v0163-prep/Pranoti-Regular-v0.163-beta.ttf`
(SHA-256 verified: `129355004867c4b292ac47fde1e1a9bea11fab891bafc2d9e05da7bd8e2c35e9`).
Deliverable: `Pranoti-Regular-v0.164-beta.ttf`
SHA-256 `9bc1e3f4c2be27ef2f3d032c8bd4ecbf9e337d596d73c0c90bded87f677f2a4d`,
652 glyphs, cmap 204, UPM 1536, `head.fontRevision = 0.164`.

Scope: ONLY the 35 handwriting consonants
ক খ গ ঘ ঙ চ ছ জ ঝ ঞ ট ঠ ড ঢ ণ ত থ দ ধ ন প ফ ব ভ ম য র ল শ ষ স হ ড় ঢ় য়
(`bn_ka bn_kha bn_ga bn_gha bn_nga bn_ca bn_cha bn_ja bn_jha bn_nya bn_tta
bn_ttha bn_dda bn_ddha bn_nna bn_ta bn_tha bn_da bn_dha bn_na bn_pa bn_pha
bn_ba bn_bha bn_ma bn_ya bn_ra bn_la bn_sha bn_ssa bn_sa bn_ha bn_rra
bn_rha bn_yya`).
Nothing else touched: ৎ (base font, left as-is), bn_hasanta, bn_anusvara
(ং — separate manual pass, still +18% with a kink risk; NOT attempted
here), vowels, vowel signs, digits, punctuation, conjuncts, GSUB/GPOS/
GDEF, cmap, glyph order — all unchanged (verified by the table comparison
in `tools/verify_pranoti_v0164_beta.py`).

## 1. Measurement on the v0.163 base

Method (script `tools/measure_consonants_v0164.py`, outputs
`checks/consonant-measure-v0.163.tsv/.json`): same as the vowel pass —
true ink bbox rasterised alone at 1536 px (Pillow BASIC), compared with
the v0.150 fitted ink boxes (`v0160-prep/traced_glyphs.json`) and with
AdorshoLipi's ink boxes (`v0150-prep/ink-measure.json`); stroke weight by
distance-transform ridge median (letter median 84.5, ±15% band 72–97);
advances / side bearings from `hmtx`; shape check by self-intersection
scan (`v0161-prep/tools/check_self_intersection.py`).

**Measurement trap found and fixed (important for future passes):**
the first run rendered ড়/ঢ়/য় as base + nukta (the source chars were
stored decomposed, U+09A1/U+09A2/U+09AF + U+09BC), so BASIC layout drew
the base letter plus a standalone nukta — wrong ink boxes (bn_yya top
−7 instead of −20; bn_rra/bn_rha bottoms −330 instead of −216/−153)
and wrong ridge for bn_rha (76.8 instead of 92.2). The script now uses
explicit codepoints `chr(0x09DC/0x09DD/0x09DF)` and all values below are
from the corrected re-measurement, cross-checked against the v0.163
verify ink boxes and the fontTools glyf bboxes (which agree within 1
unit). Any future measurement/render script that types ড়/ঢ়/য় must use
explicit codepoints, never pasted characters.

| glyph | char | ink top vs v0.150 target | ink bottom vs v0.150 target | ridge stroke | dev% | v0.161 changeWeight delta |
|---|---|---|---|---|---|---|
| bn_ka | ক | 0 | +5 | 85.9 | +1.7 | 0 |
| bn_kha | খ | **−12** | +12 | 84.5 | 0.0 | −15 |
| bn_ga | গ | **−12** | +13 | 92.2 | +9.1 | −15 |
| bn_gha | ঘ | −5 | +5 | 76.8 | −9.1 | 0 |
| bn_nga | ঙ | −4 | +4 | 81.6 | −3.4 | 0 |
| bn_ca | চ | 0 | +5 | 83.1 | −1.7 | 0 |
| bn_cha | ছ | +4 | −2 | 84.5 | 0.0 | +15 |
| bn_ja | জ | −3 | +6 | 76.8 | −9.1 | 0 |
| bn_jha | ঝ | −4 | +5 | 92.2 | +9.1 | 0 |
| bn_nya | ঞ | −3 | +5 | 75.6 | −10.5 | 0 |
| bn_tta | ট | +2 | −3 | 84.5 | 0.0 | +14 |
| bn_ttha | ঠ | −3 | +2 | 76.8 | −9.1 | 0 |
| bn_dda | ড | −1 | +4 | 76.8 | −9.1 | 0 |
| bn_ddha | ঢ | −2 | +4 | 76.8 | −9.1 | 0 |
| bn_nna | ণ | −2 | +4 | 78.3 | −7.3 | 0 |
| bn_ta | ত | −1 | +4 | 76.8 | −9.1 | 0 |
| bn_tha | থ | −4 | +5 | 85.9 | +1.7 | 0 |
| bn_da | দ | −1 | +5 | 76.8 | −9.1 | 0 |
| bn_dha | ধ | −3 | +5 | 84.5 | 0.0 | 0 |
| bn_na | ন | −1 | +6 | 92.2 | +9.1 | 0 |
| bn_pa | প | +4 | −2 | 84.5 | 0.0 | +15 |
| bn_pha | ফ | −1 | +5 | 92.2 | +9.1 | 0 |
| bn_ba | ব | −2 | +5 | 92.2 | +9.1 | 0 |
| bn_bha | ভ | −1 | +3 | 82.7 | −2.1 | 0 |
| bn_ma | ম | 0 | +4 | 84.5 | 0.0 | 0 |
| bn_ya | য | −7 | +12 | 84.5 | 0.0 | −15 |
| bn_ra | র | 0 | +6 | 84.5 | 0.0 | 0 |
| bn_la | ল | −2 | +4 | 76.8 | −9.1 | 0 |
| bn_sha | শ | −4 | +6 | 84.5 | 0.0 | 0 |
| bn_ssa | ষ | −2 | +6 | 76.8 | −9.1 | 0 |
| bn_sa | স | −1 | +5 | 84.5 | 0.0 | 0 |
| bn_ha | হ | 0 | +5 | 81.6 | −3.4 | 0 |
| bn_rra | ড় | −3 | +4 | 76.8 | −9.1 | 0 |
| bn_rha | ঢ় | −1 | +3 | 92.2 | +9.1 | 0 |
| bn_yya | য় | **−20** | +22 | 84.5 | 0.0 | −32 |

What was off, per consonant:
- **bn_kha, bn_ga, bn_yya — tops sitting low** (−12/−12/−20). All three
  were thinned in v0.161; changeWeight pulls the outline in on every
  side, so the tops dropped and the bottoms rose (+12/+13/+22). The
  measured drops match the changeWeight model (delta/2 = −7.5/−7.5/−16)
  to within 4.5 units — the rest is the v0.160 re-trace residual.
- **bn_ya −7: left alone.** It matches its changeWeight model exactly
  (residual +0.5) and −7 is inside the 5–8 unit tolerance the vowel
  pass used. Same for every other consonant (tops −5..+4, residuals
  within ±5).
- **Stroke weights: nothing off.** All 35 consonants inside the ±15%
  band (75.6–92.2). **No weight changes needed or made.** Thinnest is
  bn_nya 75.6 (−10.5%); thickest bn_ga/bn_jha/bn_na/bn_pha/bn_ba 92.2
  (+9.1%).
- **Bottoms:** 32/35 sit +2..+6 above the v0.150 target bottom — a
  systematic v0.160 re-trace offset, pre-existing, within tolerance.
  Only the three thinned glyphs are further out, and the fix restores
  them too (see §2).
- **Widths:** ink is wider than the v0.150 target for 28/35 (up to
  +544 on bn_jha, +419 on bn_kha after the fix) — his handwriting is
  genuinely ~25% wider (v0.160 finding). Ink is wider than the advance
  for many consonants, so the consonant-row ink-to-ink gaps range
  **−407 to +7** — very uneven. See §3: not fixed here.
- **Shape notes:** 0 self-intersections on all 35 consonants.
  bn_nga's hook and bn_dha's loop were inspected large
  (`specimens/closeup-suspects-v0.163.png`): the hook is present and
  the loop's counter is open — both fine, no surgery. bn_nya shows no
  stray slivers (deleted in v0.150). bn_jha is rough and wide, bn_nya
  very wide — his pen's character. bn_ga and bn_cha each carry one
  duplicate consecutive point (min_consec_dist 0.00); bn_ga's survives
  the transplant (clean_glyph removed 0 points on it — see §4).

## 2. Changes (3 glyphs only)

Uniform scale about the raster ink centre (restoring the v0.150 target
height) + a small dy translate putting the ink top exactly on target —
the vowel-pass method. Scale factors 1.018–1.030, inside the v0.150
clamp [0.97, 1.08]. No changeWeight, no horizontal shift, no shape
surgery.

| glyph | char | scale | pivot (ink centre) | dy | ink top before → after | ink bottom before → after | ridge before → after | advance |
|---|---|---|---|---|---|---|---|---|
| bn_kha | খ | ×1.0184 | (528.0, 679.0) | 0.0 | 1331 → **1343** (target) | 26 → **14** (target 15) | 84.5 → 84.5 | 1023 |
| bn_ga | গ | ×1.0191 | (529.0, 717.0) | −0.5 | 1371 → **1383** (target) | 62 → **49** (target 50) | 92.2 → 92.2 | 1021 |
| bn_yya | য় | ×1.0302 | (483.5, 440.5) | −1.0 | 1137 → **1157** (target) | −257 → **−279** (target −278) | 84.5 → 84.5 | 989 |

Re-measured on v0.164 (`checks/consonant-measure-v0.164.tsv/.json`):
all three tops AND bottoms now exactly 0 vs the v0.150 target; all 35
ridge weights still in band (75.6–92.2); the 32 untouched consonants are
byte-identical in measurement to v0.163. Advances unchanged; only the
hmtx lsb moved (new outline xMin: bn_kha −164→−177, bn_ga −69→−80,
bn_yya −233→−255).

Build method: FontForge (`tools/build_consonants_v0164.py`) applies the
transforms and `addExtrema()` + `correctDirection()`, then only the
three changed glyf outlines (+ their hmtx lsb) are transplanted into a
fontTools copy of v0.163 (`tools/transplant_v0164.py`) — every other
table stays byte-identical to v0.163 by construction. Name IDs 3/5 and
`head.fontRevision` set to 0.164. No changeWeight was used, so the
v0.161 winding-flip lesson did not apply; contour winding was checked
unchanged in-session. `clean_glyph` removed 2 points on bn_kha, 0 on
bn_ga and bn_yya, inserted 0.

## 3. Deliberately left alone, and why

- **Side bearings / row spacing:** the consonant-row gaps run −407..+7
  (ink-to-ink). Equalising them would need horizontal shifts of
  100–400 units — far beyond the ±40 anchor-safe cap (candrabindu
  anchors sit on these glyphs). The uneven gaps come from
  ink-width-vs-advance mismatch (his handwriting is genuinely wider),
  not from mis-centring. Fixing it properly means wider advances — a
  decision for John, not for this pass. Same conclusion as the vowel
  pass (§3 of VOWEL-LOG-v0.163.md).
- **bn_ya's top (−7):** within the 5–8 unit tolerance and exactly what
  its v0.161 changeWeight predicts. Left alone.
- **Weights:** no changeWeight anywhere — all 35 consonants already in
  band.
- **Widths:** no width rescaling — outside the v0.150 clamp and against
  the v0.160 finding that his handwriting is genuinely wider.
- **Tops of the other 32 consonants (−5..+4):** within tolerance.
  Left alone.
- **bn_nga's hook, bn_dha's loop, bn_jha/bn_nya roughness:** inspected
  large, all fine as character. Not redrawn.
- **bn_ga/bn_cha duplicate points:** one zero-length segment each.
  FontForge validate is 0 on both, 0 crossings, renders fine. Cosmetic;
  left in place (bn_ga's survived clean_glyph — recorded here so it is
  not mistaken for a new defect later).
- **bn_anusvara (ং):** out of scope by design — still +18% heavy with
  a kink risk under changeWeight; needs a manual outline pass later.

## 4. Verification

`tools/verify_pranoti_v0164_beta.py` — **PASS**:
- HarfBuzz 22/22 representative samples identical to v0.120; the 3
  reviewed candrabindu offsets exact (কাঁ −450,+125; চাঁ −278,+125;
  ক্ষ্মাঁ −632,+125).
- Consonant-pair grid **1,369/1,369 identical** to v0.120, 0 .notdef.
- New glyphs U+0980, U+09FB, U+09FC, U+09FE still render; candrabindu
  anchors unchanged.
- Table comparison: only GPOS, glyf, hmtx, cmap, head, name, maxp, loca
  differ; GSUB, GDEF, OS/2, attribution and license name records
  preserved. hhea minRightSideBearing −1147 (derived from glyf/hmtx;
  self-consistent, unchanged from v0.163).
- Ink boxes (83 re-traced glyphs vs v0.150 targets): worst
  |top_err − expected| = **7.0** (tolerance 8; the worst is the
  pre-existing semicolon −7). The three fixed consonants: top_err 0,
  expected +4/+4.5 (the verify model carries the changeWeight offset),
  diff −4/−4.5 — PASS.
- OTS: `File sanitized successfully!` (`checks/ots-v0.164.txt`).
- FontForge validate: **64 → 62 flagged glyphs** (bn_kha 32 → 0 and
  bn_ga 32 → 0 after addExtrema; bn_yya was 0 and stays 0).
  **Nothing worsened** — no reverts needed. All remaining flags are
  bit 32 (missing extrema, cosmetic) except bn_vedic_anusvara 36
  (32 + 4, pre-existing) and one bit-2 flag (pre-existing).
- Full summary: `checks/summary-v0.164.txt`.

## 5. Specimens (looked at)

- `specimens/before-after-v0.164.png` — all 35 consonants, v0.163 grey
  vs v0.164 black, baseline/headline guides. The three fixed consonants
  now touch the blue headline in black; the other 32 are identical. No
  distortion, counters open, nothing floats or sinks. (bn_nya and
  bn_jha run slightly past their cell edges in both bands — they are
  genuinely that wide; unchanged.)
- `specimens/v0164-consonant-demo.png` — the 35 consonants large (two
  lines), each in a real word (কলম, খাতা, গাছ, ঘোড়া, ব্যাঙ, চাঁদ,
  ছাতা, জল, ঝড়, মিঞা, টেবিল, ঠাকুর, ডাক, ঢোল, বীণা, তাল, থালা,
  দরজা, ধান, নদী, পাখি, ফুল, বই, ভাত, মাছ, যত্ন, রাত, লতা, শাপলা,
  ষড়যন্ত্র, সূর্য, হাত, গাড়ি, আষাঢ়, ময়না), three sentences using
  them, and the consonant row side-by-side v0.163/v0.164. Even rhythm,
  all words legible. (First render had the top row clipped at the right
  edge and tofu boxes in the caption — DejaVu has no Bengali glyphs —
  both fixed by re-rendering with two-line rows and an English-only
  caption.)
- `specimens/invitation-v0.164.png` — the Peace School & College
  invitation sentences re-rendered; everything renders, no missing
  glyphs.
- `specimens/matched-v0.163-v0.164-review.png` — matched RAQM specimen
  from the verify script (12/16/24/32 px).
- `specimens/closeup-suspects-v0.163.png` — pre-change close look at
  ঙ ধ ঞ ঝ ঠ ট খ গ য় at 200 px, used for the shape decisions in §1.

Honest limit: at reading size the change is subtle — it is clearest at
display size, where the three restored tops now align with the other
consonants. The remaining unevenness in the consonant row is the
ink-width mismatch (§3), not position or weight.
