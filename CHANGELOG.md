# Changelog

## v0.140-beta — Experimental public beta

- **Polish & sharpen pass on the 73 handwriting glyphs** (user's request, 2026-11-26): one pass of a 7-point binomial smoothing kernel over each outline contour (per-point move capped at 5 units, max bbox drift 5 units) plus merging of near-duplicate points. Same handwriting, cleaner and sharper edges. Measured: points 23,413 -> 23,345; median stroke width stays ~110 units (target ~112); median stroke-width variation (IQR) 22.2 -> 19.5 units (12% narrower); FontForge bit-4 flags 33 -> 28 glyphs. Full per-glyph log: `POLISH-LOG-v0.140.md`. Build: `tools/build_pranoti_v0140_beta.py`.
- **Nothing else changed:** advances, side bearings, anchors, GSUB/GPOS/GDEF, cmap and all AdorshoLipi glyphs are byte-identical to v0.130 (every table except glyf, head, name, maxp, loca and the derived hhea metric) — verification re-passed 22/22 HarfBuzz samples (3 reviewed candrabindu offsets exact) and 1,369/1,369 consonant-pair checks, OTS sanitised clean. The derived `hhea.minRightSideBearing` moved -660 -> -654 because smoothing moved bn_ikaar's leftmost point ~6 units; it is metadata only and now matches the v0.120 value.
- **Experimental only; not production-ready.** Conjunct ligatures are still AdorshoLipi, expert sign-off and broad platform testing remain outstanding; see the [README](README.md) and [test summary](TEST-SUMMARY.md).

## v0.130-beta — Experimental public beta

- **Batch 1 handwriting replacement (user's strategy: progressively replace AdorshoLipi with John's handwriting):** 69 core glyph outlines replaced with John's handwriting from `inputs/Pranoti-Handwriting-v4.ttf` (UPM 1000 → 1536, fitted to the GitHub font's baseline, advance widths and side bearings; v4 advances never imported). 11 vowels, 35 consonants, 10 digits, 13 vowel signs/marks. The hasanta (`bn_hasanta`) was deliberately kept AdorshoLipi — the v4 outline does not scale to the GitHub font's full-height diagonal slash. 7 core codepoints stay AdorshoLipi for now (ঌ U+098C absent from v4; ঍ U+098D, ঎ U+098E, ঑ U+0991, ঒ U+0992, ৰ U+09F0, ৱ U+09F1 not in the cmap at all). Full per-glyph log: `REPLACEMENT-LOG-v0.130.md`. Build: `tools/build_pranoti_v0130_beta.py`.
- **The 4 missing codepoints are added, designed from scratch in AdorshoLipi's style** (none exist in AdorshoLipi or v4): U+0980 ANJI, U+09FB GANDA MARK, U+09FC VEDIC ANUSVARA, U+09FE SANDHI MARK. Bengali coverage in the reviewed set is now **96/96**. All 4 render and shape correctly (verified with HarfBuzz).
- **Candrabindu GPOS generalised:** the three reviewed contexts are preserved exactly (`কাঁ` Δ(−450,+125), `চাঁ` Δ(−278,+125), `ক্ষ্মাঁ` Δ(−632,+125)) and anchor-based mark attachment now positions candrabindu (U+0981) over all 55 bases and 375 ligatures. GDEF glyph classes were added (base/ligature/mark) so HarfBuzz applies the mark lookups.
- **Outline hygiene:** exact duplicate points and all-off-curve contours inherited from the traced handwriting outlines were cleaned shape-preservingly in the build; the 4 new glyphs were cleaned the same way.
- No GSUB changes; regression checks recorded no differences in the 1,369 tested Bengali consonant pairs. New TTF SHA-256: `192881342d917e688000a51b9bea643c9ce21ec6123110b80adcfb6a8fcbebda`.
- **Experimental only; not production-ready.** Conjunct ligatures are still AdorshoLipi (handwriting conjuncts not yet replaced), expert sign-off and broad platform testing remain outstanding; see the [README](README.md) and [test summary](TEST-SUMMARY.md).

## v0.120-beta — Experimental public beta

- Preserves the reviewed installable TTF byte-for-byte (SHA-256: `9b6c853a268513f0eece232ad85970307315c3ad579e2c4a2c2ca7f6bf34c748`).
- Adds three C-position candrabindu GPOS adjustments at UPM 1536: `কাঁ` Δ(−450,+125), `চাঁ` Δ(−278,+125), and `ক্ষ্মাঁ` Δ(−632,+125).
- No GSUB changes; regression checks recorded no differences in the 1,369 tested Bengali consonant pairs.
- **Experimental only; not production-ready.** Coverage gaps, narrow shaping scope, pending expert sign-off, and broad platform-test gaps are listed in the [README](README.md) and [test summary](TEST-SUMMARY.md).
