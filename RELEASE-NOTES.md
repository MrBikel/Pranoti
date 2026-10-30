# Pranoti v0.120-beta — experimental public beta

**Not production-ready.** This is an installable test build of AdorshoLipi by Partha Sarathi Pal, with the reviewed TTF preserved byte-for-byte.

## Scope

The only new GPOS positioning is in three contexts at UPM 1536: `কাঁ` Δ(−450,+125), `চাঁ` Δ(−278,+125), and `ক্ষ্মাঁ` Δ(−632,+125). No GSUB changes were made.

## Limits

Bengali coverage is 92/96; U+0980, U+09FB, U+09FC, and U+09FE are missing. GPOS changes apply only to the three contexts above. Expert sign-off and broad Microsoft Office/Word, browser, mobile, print, and other platform testing remain pending. The owner reported a Windows 11 Home + Microsoft Word test as okay; this is not independent QA.

## Asset integrity

`Pranoti-Regular-v0.120-Private-Owner-Review.ttf` SHA-256: `9b6c853a268513f0eece232ad85970307315c3ad579e2c4a2c2ca7f6bf34c748`.

See the [README](README.md), [test summary](TEST-SUMMARY.md), and [license/attribution notice](ATTRIBUTION-LICENSE-NOTICE.txt) before installation or redistribution.
