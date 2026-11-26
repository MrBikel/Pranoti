# Pranoti — test summaries

> **Status: experimental public beta, not production-ready.** These results cover bounded checks only and are not expert type-design sign-off or broad compatibility testing.

## v0.160-beta

- FontTools table comparison vs v0.120 recorded changes limited to GPOS, glyf, hmtx, cmap, head, name, maxp and loca. GSUB, GDEF, OS/2 and attribution/license name records were preserved. Glyph count is 652. Advances are unchanged; side bearings follow the new outlines (hmtx lsb = new outline xMin, v0.150 precedent); the derived `hhea.minRightSideBearing` moved -654 -> -1155 (the wider re-traced marks) and matches the value derived from the font's own glyf/hmtx data.
- HarfBuzz checks passed for **22 representative shaping samples**, including the exact offsets for `কাঁ` (−450,+125), `চাঁ` (−278,+125), and `ক্ষ্মাঁ` (−632,+125) at UPM 1536. Sample results are in `checks/harfbuzz-22-samples-v0.160.tsv`.
- **1,369/1,369** Bengali consonant-pair regression checks matched the v0.120 baseline; the recorded grid has no `.notdef` results. Data is in `checks/consonant-pair-grid-v0.160.tsv`.
- Ink boxes: rasterised true ink top vs the v0.150 target, worst error 5 units over all 83 re-traced glyphs. Data is in `checks/ink-boxes-v0.160.tsv`.
- The 4 new glyphs (U+0980, U+09FB, U+09FC, U+09FE) still render (no `.notdef`) and shape correctly. Candrabindu anchors are unchanged.
- OpenType Sanitizer **8.2.1** reported "File sanitized successfully." FontForge **20230101** validation flagged 85 glyphs — all 83 re-traced glyphs with bit 5 only (no FontForge anchor points, expected for traced outlines, same kind as v0.150), plus the 2 pre-existing (bn_anji, bn_vedic_anusvara). Near-duplicate-point flags (bit 2) fell from 28 glyphs in v0.150 to 1 (bn_vedic_anusvara, untouched); wrong-direction flags (bit 3): 0. This is not independent design validation.
- Five FreeType/Pillow RAQM specimens were produced for visual review: a before/after grid of all 83 re-traced glyphs with baseline/headline guides (`specimens/before-after-v0.160.png`), a writing demo (`specimens/v0160-writing-demo.png`), a 200 px close-up of the most-changed glyphs (`specimens/closeup-v0.160.png`), a matched v0.150/v0.160 review at 12/16/24/32 px (`specimens/matched-v0.150-v0.160-review.png`), and the chosen vowel cells (`specimens/chosen-vowels-v0.160.png`). All were inspected: all 83 glyphs sit on one baseline and headline with even rhythm, no collisions, nothing floats or sinks. A specimen is illustrative, not proof of rendering across applications or devices.
- v0.160 has not been owner-tested yet.

## v0.150-beta

- FontTools table comparison vs v0.140 recorded changes limited to GPOS, glyf, hmtx, cmap, head, name, maxp and loca. GSUB, GDEF, OS/2 and attribution/license name records were preserved. Glyph count is 652. Advances are unchanged; side bearings were re-centred as part of the size normalisation.
- HarfBuzz checks passed for **22 representative shaping samples**, including the exact offsets for `কাঁ` (−450,+125), `চাঁ` (−278,+125), and `ক্ষ্মাঁ` (−632,+125) at UPM 1536. Sample results are in `checks/harfbuzz-22-samples-v0.150.tsv`.
- **1,369/1,369** Bengali consonant-pair regression checks matched the v0.120 baseline; the recorded grid has no `.notdef` results. Data is in `checks/consonant-pair-grid-v0.150.tsv`.
- The 4 new glyphs (U+0980, U+09FB, U+09FC, U+09FE) still render (no `.notdef`) and shape correctly. Candrabindu anchors are unchanged.
- OpenType Sanitizer **8.2.1** reported “File sanitized successfully.” FontForge **20230101** read the font and reported 652 glyphs; its validation returned 36, identical to v0.140 (no new flags). This is not independent design validation.
- Three FreeType/Pillow RAQM specimens were produced for visual review: a before/after grid of all 56 core letters with baseline/headline guides (`specimens/before-after-v0.150.png`), a writing demo (`specimens/v0150-writing-demo.png`), a 200 px + 64 px close-up of the most-changed glyphs (`specimens/closeup-v0.150.png`), and a matched v0.140/v0.150 review at 12/16/24/32 px (`specimens/matched-v0.140-v0.150-review.png`). All were inspected: all 56 letters sit on one baseline and headline with even rhythm, no collisions, nothing floats or sinks. A specimen is illustrative, not proof of rendering across applications or devices.
- v0.150 has not been owner-tested yet.

## v0.140-beta

- FontTools table comparison vs v0.120 recorded changes limited to GPOS, GDEF (new glyph classes only, from v0.130), glyf, hmtx, cmap, head, name, maxp and loca. GSUB, OS/2 and attribution/license name records were preserved. Glyph count is 652. hmtx is unchanged vs v0.130 (verified by the build assertion); only the derived `hhea.minRightSideBearing` moved -660 -> -654 (bn_ikaar's leftmost point moved ~6 units during smoothing — metadata only).
- HarfBuzz checks passed for **22 representative shaping samples**, including the exact offsets for `কাঁ` (−450,+125), `চাঁ` (−278,+125), and `ক্ষ্মাঁ` (−632,+125) at UPM 1536. Sample results are in `checks/harfbuzz-22-samples-v0.140.tsv`.
- **1,369/1,369** Bengali consonant-pair regression checks matched the v0.120 baseline; the recorded grid has no `.notdef` results. Data is in `checks/consonant-pair-grid-v0.140.tsv`.
- The 4 new glyphs (U+0980, U+09FB, U+09FC, U+09FE) still render (no `.notdef`) and shape correctly. Candrabindu was checked on all 55 bases and 375 ligatures: the mark sits above the base with its outline overlapping the base span in every case.
- OpenType Sanitizer **8.2.1** reported “File sanitized successfully.” FontForge **20230101** read the font and reported 652 glyphs; its validation returned 36: bit 32 (glyphs in the mark lookups have no FontForge anchor points — expected, as in v0.130) and bit 4 on 28 glyphs (down from 33 in v0.130; traced handwriting outlines with points ~1 font unit apart — cosmetic only). This is not independent design validation.
- Two FreeType/Pillow RAQM specimens were produced for visual review: a matched v0.130/v0.140 review at 12/16/24/32 px (`specimens/matched-v0.130-v0.140-review.png`) and a before/after grid with a paragraph and a 64 px close-up of the roughest glyphs (`specimens/before-after-v0.140.png`). Both were inspected: all 69 replaced glyphs sit on the baseline with no collisions; the polish is visible as cleaner edges at 64 px (mean raster change 3.8% of ink at 150 px, mostly sub-pixel edge shifts); at 12/16 px the rendering is unchanged in legibility. A specimen is illustrative, not proof of rendering across applications or devices.
- v0.140 has not been owner-tested yet.

## v0.130-beta

## Automated and recorded checks

- FontTools table comparison recorded changes limited to GPOS, GDEF (new glyph classes only), glyf, hmtx, cmap, head, name, maxp and loca. GSUB, OS/2 and attribution/license name records were preserved. Glyph count is 652 (648 + 4 new).
- HarfBuzz checks passed for **22 representative shaping samples**, including the exact offsets for `কাঁ` (−450,+125), `চাঁ` (−278,+125), and `ক্ষ্মাঁ` (−632,+125) at UPM 1536. Sample results are in `checks/harfbuzz-22-samples-v0.130.tsv`.
- **1,369/1,369** Bengali consonant-pair regression checks matched the v0.120 baseline; the recorded grid has no `.notdef` results. Data is in `checks/consonant-pair-grid-v0.130.tsv`.
- The 4 new glyphs (U+0980, U+09FB, U+09FC, U+09FE) all render (no `.notdef`) and shape correctly. Candrabindu was checked on all 55 bases and 375 ligatures: the mark sits above the base with its outline overlapping the base span in every case.
- OpenType Sanitizer **8.2.1** reported “File sanitized successfully.” FontForge **20230101** read the font and reported 652 glyphs; its validation returned 36: bit 32 (glyphs in the mark lookups have no FontForge anchor points — expected, because the anchor-based GPOS was built with FontTools, which does not create FontForge glyph anchor points; HarfBuzz and OTS do not need them) and bit 4 on 33 glyphs (traced handwriting outlines with points ~1 font unit apart, plus the vedic anusvara's dot touching the bowl's top edge — cosmetic only; FreeType, HarfBuzz and OTS all accept the outlines, and the build already removes all exact duplicate points shape-preservingly). This is not independent design validation.
- Two FreeType/Pillow RAQM specimens were produced for visual review: a matched v0.120/v0.130 review (`specimens/matched-v0.120-v0.130-review.png`) and a before/after grid with a paragraph (`specimens/before-after-v0.130.png`). The before/after was inspected: all 69 replaced glyphs sit on the baseline with no collisions; `অভিযাত্রী` shows the ী/া fix holding; `গাঁ`'s candrabindu now positions correctly; the 4 new glyphs render. A specimen is illustrative, not proof of rendering across applications or devices.

## Owner-reported application test

The owner reported testing v0.120 on **Windows 11 Home with Microsoft Word** and said, “everything okay.” This is reported with provenance, not independently verified. v0.130 has not been owner-tested yet.

## Known limitations and remaining work

- Bengali coverage is **96/96** in the reviewed coverage set. Still absent from the cmap: U+098D, U+098E, U+0991, U+0992 and Assamese U+09F0, U+09F1.
- **Conjunct ligatures are still from the base font** (~64 conjuncts from the handwriting sheets not yet replaced). That is the next replacement batch.
- 7 core codepoints are still from the base font: ঌ (U+098C) plus the six absent from the cmap above. The hasanta was deliberately kept from the base font.
- Handwriting outlines are traced: ঋ, ঝ, ঙ keep rough shapes; ধ's top loop is slightly pinched. No kerning; no GPOS pair positioning beyond candrabindu.
- Candrabindu anchors are calibrated for the common aakaar case, so on a bare vowel the mark sits a little right of centre (still over the letter).
- Expert type-design sign-off remains outstanding.
- Broad target-platform testing remains outstanding, including Microsoft Word/Office, other desktop applications, browsers, mobile platforms, and print workflows.
- Production readiness is **not claimed**.
