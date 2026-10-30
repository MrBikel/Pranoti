# v0.120-beta test summary

> **Status: experimental public beta, not production-ready.** These results cover bounded checks only and are not expert type-design sign-off or broad compatibility testing.

## Automated and recorded checks

- FontTools table comparison recorded changes limited to GPOS, name strings, and dependent `head` checksum/timestamp data. GSUB, outlines, metrics, cmap, GDEF, and attribution/license name records were preserved.
- HarfBuzz checks passed for **22 representative shaping samples**, including the exact offsets for `কাঁ` (−450,+125), `চাঁ` (−278,+125), and `ক্ষ্মাঁ` (−632,+125) at UPM 1536. Sample results are in `checks/harfbuzz-22-samples-v0.120.tsv`.
- **1,369/1,369** Bengali consonant-pair regression checks matched the v0.119 baseline; the recorded grid has no `.notdef` results. Data is in `checks/consonant-pair-grid-v0.120.tsv`.
- OpenType Sanitizer **8.2.1** reported “File sanitized successfully.” FontForge **20230101** read the font and reported 648 glyphs; its log recorded `FONT_VALIDATE=0`, so this is not represented as an independent design validation.
- A matched FreeType/Pillow RAQM specimen was produced for visual review. A specimen is illustrative, not proof of rendering across applications or devices.

## Owner-reported application test

The owner reported testing on **Windows 11 Home with Microsoft Word** and said, “everything okay.” This is reported with provenance, not independently verified. No detailed test-case list, Office build, independent reproduction, or evidence of Preview & Print embedding enforcement was supplied. It does not establish general Windows/Word compatibility.

## Known limitations and remaining work

- Bengali coverage is **92/96** in the reviewed coverage set; **U+0980, U+09FB, U+09FC, and U+09FE** are missing.
- New GPOS positioning is restricted to exactly **three** contexts: `কাঁ`, `চাঁ`, and `ক্ষ্মাঁ`. Other candrabindu contexts are unchanged and not covered by the new rules.
- Expert type-design sign-off remains outstanding.
- Broad target-platform testing remains outstanding, including Microsoft Word/Office, other desktop applications, browsers, mobile platforms, and print workflows.
- Production readiness is **not claimed**.
