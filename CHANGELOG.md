# Changelog

## v0.120-beta — Experimental public beta

- Preserves the reviewed installable TTF byte-for-byte (SHA-256: `9b6c853a268513f0eece232ad85970307315c3ad579e2c4a2c2ca7f6bf34c748`).
- Adds three C-position candrabindu GPOS adjustments at UPM 1536: `কাঁ` Δ(−450,+125), `চাঁ` Δ(−278,+125), and `ক্ষ্মাঁ` Δ(−632,+125).
- No GSUB changes; regression checks recorded no differences in the 1,369 tested Bengali consonant pairs.
- **Experimental only; not production-ready.** Coverage gaps, narrow shaping scope, pending expert sign-off, and broad platform-test gaps are listed in the [README](README.md) and [test summary](TEST-SUMMARY.md).
