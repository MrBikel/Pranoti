# Pranoti AdorshoLipi v0.120-beta

> **Experimental public beta — not production-ready.** This is an installable review build for testing, not a final font release. Installability does not mean production approval.

Pranoti v0.120-beta is a narrowly scoped update to **AdorshoLipi by Partha Sarathi Pal**. It adjusts the placement of the Bengali candrabindu in exactly three approved contexts. The distributed TrueType font is preserved byte-for-byte from the reviewed build; its internal family name is **Pranoti v0.120 Review**.

## Download and install

Download [`Pranoti-Regular-v0.120-Private-Owner-Review.ttf`](https://github.com/MrBikel/Pranoti/releases/download/v0.120-beta/Pranoti-Regular-v0.120-Private-Owner-Review.ttf) from the [v0.120-beta release](https://github.com/MrBikel/Pranoti/releases/tag/v0.120-beta). Verify its SHA-256 before installing:

```text
9b6c853a268513f0eece232ad85970307315c3ad579e2c4a2c2ca7f6bf34c748
```

- **Windows:** Right-click the downloaded `.ttf` and choose **Install** (or **Install for all users** if appropriate). Close and reopen apps that use fonts. Remove any earlier v0.120 Review copy first to avoid cached or duplicate versions.
- **macOS:** Open the `.ttf` in Font Book and choose **Install Font**. Restart the target app if it was already open.
- **Linux:** Copy the file to `~/.local/share/fonts/`, then run `fc-cache -f` and restart the target app.

These are general installation steps, not a compatibility claim. Browsers, mobile platforms, print workflows, and other applications have not received broad beta testing.

## What changed

The GPOS `mark` feature positions the candrabindu only in these three contexts (UPM 1536):

| Bengali context | GPOS offset (font units) |
|---|---:|
| `কাঁ` | Δ(−450, +125) |
| `চাঁ` | Δ(−278, +125) |
| `ক্ষ্মাঁ` | Δ(−632, +125) |

No GSUB changes were made. Other candrabindu contexts are not covered by these new rules. See the [changelog](CHANGELOG.md), [test summary](TEST-SUMMARY.md), and [specimen](specimens/c-position-contexts-v0.120-beta.png).

## Clear limitations

- **Bengali coverage is 92/96** in the reviewed coverage set. These codepoints are missing: **U+0980, U+09FB, U+09FC, and U+09FE**.
- **GPOS scope is limited to exactly three contexts:** `কাঁ`, `চাঁ`, and `ক্ষ্মাঁ`. No general candrabindu repositioning is claimed.
- **Expert type-design sign-off is pending.** Broad testing across Microsoft Office/Word, browsers, mobile platforms, printing, and other target environments is also pending.
- The owner reported testing on **Windows 11 Home with Microsoft Word** and said everything looked okay. This is an owner-reported result only, not independent QA; specific test cases and broad compatibility were not established.
- The font's `OS/2 fsType=4` Preview & Print setting and the original GPL font-embedding exception are retained. This does not certify that every application will honor those terms or render the font identically.

Please report issues with the application, operating system, font size, and a reproducible sample. Do not treat this beta as production-ready.

## Build and test materials

This repository includes the editable FontForge source snapshot, the approved FEA rules, the v0.119 baseline input required by the build, build and verification scripts, selected shaping-test data, a checksum manifest, and a beta-labelled specimen. The build uses FontTools; the verification script also requires `hb-shape` and Pillow with RAQM support.

```bash
python3 tools/build_pranoti_v0120_review.py
python3 tools/verify_pranoti_v0120_review.py
```

The build should reproduce the distributed font hash above. The exact binary retains its original review-specific internal naming so it remains distinguishable from v0.119; do not interpret that metadata as production sign-off.

## License and attribution

This derivative is distributed under the original font's **GNU GPL version 2 or (at your option) any later version**, with the original font-embedding exception preserved. The unmodified GPL Version 2 text is in [`LICENSE-GPL-2.txt`](LICENSE-GPL-2.txt), and the preserved upstream notice and attribution are in [`ATTRIBUTION-LICENSE-NOTICE.txt`](ATTRIBUTION-LICENSE-NOTICE.txt). The source font is **AdorshoLipi by Partha Sarathi Pal**. The font's embedded attribution and license metadata have been retained.

## বাংলায় সংক্ষেপে

এটি **পরীক্ষামূলক public beta—production-ready নয়**। ইনস্টল করা যায়, কিন্তু উৎপাদন ব্যবহারের অনুমোদন নেই। বাংলা coverage **92/96**; অনুপস্থিত **U+0980, U+09FB, U+09FC, U+09FE**। নতুন GPOS কেবল `কাঁ`, `চাঁ`, ও `ক্ষ্মাঁ`—এই তিনটি নির্দিষ্ট প্রসঙ্গে প্রযোজ্য। বিশেষজ্ঞের sign-off এবং Word/Office, browser, mobile, printসহ বিভিন্ন প্ল্যাটফর্মে বিস্তৃত পরীক্ষা বাকি। Windows 11 Home ও Microsoft Word-এ মালিকের পরীক্ষা সফল বলে জানানো হয়েছে; এটি স্বাধীন QA নয়।
