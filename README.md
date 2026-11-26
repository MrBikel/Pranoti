# Pranoti AdorshoLipi v0.150-beta

> **Experimental public beta — not production-ready.** This is an installable review build for testing, not a final font release. Installability does not mean production approval.

Pranoti v0.150-beta continues **AdorshoLipi by Partha Sarathi Pal** with the owner's strategy: progressively replace AdorshoLipi's glyphs with the owner's handwriting, glyph by glyph, until the whole font is his. This batch replaces 69 core glyphs with handwriting outlines, adds the 4 previously missing codepoints, generalises candrabindu positioning to all bases, and normalises all 56 core letters to one size. The distributed TrueType font's internal family name is **Pranoti**.

## Download and install

`Pranoti-Regular-v0.150-beta.ttf` (local build; no GitHub release published yet — do not push or publish without the owner's approval). Verify its SHA-256 before installing:

```text
679ba5155faa048c039560469bdc174451f395a7852b79e88496bbab2aa40c93
```

- **Windows:** Right-click the downloaded `.ttf` and choose **Install** (or **Install for all users** if appropriate). Close and reopen apps that use fonts. Remove any earlier Pranoti copy first to avoid cached or duplicate versions.
- **macOS:** Open the `.ttf` in Font Book and choose **Install Font**. Restart the target app if it was already open.
- **Linux:** Copy the file to `~/.local/share/fonts/`, then run `fc-cache -f` and restart the target app.

These are general installation steps, not a compatibility claim. Browsers, mobile platforms, print workflows, and other applications have not received broad beta testing.

## What changed

- **69 core glyphs are now John's handwriting** (11 vowels, 35 consonants, 10 digits, 13 vowel signs/marks), fitted to the v0.120 metrics: same baseline, advance widths and side bearings. The hasanta was deliberately kept AdorshoLipi. 7 core codepoints stay AdorshoLipi for now (see limitations). Per-glyph log: `REPLACEMENT-LOG-v0.130.md`.
- **4 new glyphs, designed from scratch in AdorshoLipi's style:** U+0980 ANJI, U+09FB GANDA MARK, U+09FC VEDIC ANUSVARA, U+09FE SANDHI MARK.
- **Candrabindu (U+0981) is now anchor-based over all bases:** the three reviewed offsets are preserved exactly — `কাঁ` Δ(−450,+125), `চাঁ` Δ(−278,+125), `ক্ষ্মাঁ` Δ(−632,+125) — and the mark is now positioned over all 55 bases and 375 ligatures (e.g. `গাঁ` now positions correctly; it did not before).
- GDEF glyph classes (base / ligature / mark) were added so shaping engines apply the mark lookups. No GSUB changes were made.
- **v0.140 polish:** the 73 handwriting glyph outlines were smoothed (cleaner, sharper edges) and near-duplicate points merged; metrics, spacing and shaping are unchanged. Per-glyph log: `POLISH-LOG-v0.140.md`.
- **v0.150 size normalisation:** all 56 core letters (11 vowels, 35 consonants, 10 digits) were mildly rescaled (uniform ×0.970–×1.062) and translated so every letter's ink top and ink centre match AdorshoLipi's for that letter — ink-top error is now exactly 0 for all 56. Advances are unchanged; ঞ's two stray hairline slivers were removed. Per-glyph log: `SIZE-LOG-v0.150.md`.

See the [changelog](CHANGELOG.md), [test summary](TEST-SUMMARY.md), [replacement log](REPLACEMENT-LOG-v0.130.md), [polish log](POLISH-LOG-v0.140.md), [size log](SIZE-LOG-v0.150.md), and [specimens](specimens/before-after-v0.150.png) (before/after) and [specimens](specimens/matched-v0.140-v0.150-review.png) (matched review).

## Clear limitations

- **Bengali coverage is now 96/96 in the reviewed coverage set** (the 4 previously missing codepoints were added). Still absent from the cmap: **U+098D, U+098E, U+0991, U+0992** (঍, ঎, ঑, ঒) and Assamese **U+09F0, U+09F1** (ৰ, ৱ).
- **Conjunct ligatures are still AdorshoLipi.** The ~64 conjuncts from the handwriting sheets have not been replaced yet; that is the next batch.
- **7 core codepoints are still AdorshoLipi:** ঌ (U+098C, absent from the handwriting source), plus the six absent from the cmap listed above.
- **The handwriting outlines are traced, not redrawn:** some glyphs are rough (ঋ, ঝ, ঙ keep rough traced shapes; ধ's top loop is slightly pinched). No kerning or GPOS pair positioning beyond candrabindu.
- **Expert type-design sign-off is pending.** Broad testing across Microsoft Office/Word, browsers, mobile platforms, printing, and other target environments is also pending.
- The owner reported testing v0.120 on **Windows 11 Home with Microsoft Word** and said everything looked okay. This is an owner-reported result only, not independent QA; specific test cases and broad compatibility were not established. v0.130, v0.140 and v0.150 have not been owner-tested yet.
- The font's `OS/2 fsType=4` Preview & Print setting and the original GPL font-embedding exception are retained. This does not certify that every application will honor those terms or render the font identically.

Please report issues with the application, operating system, font size, and a reproducible sample. Do not treat this beta as production-ready.

## Build and test materials

This repository includes the editable FontForge source snapshot, the v0.120 baseline, the handwriting source (`inputs/Pranoti-Handwriting-v4.ttf`), the new-glyphs source (`inputs/new-glyphs-v0130.ttf`, drawn with `tools/draw_new_glyphs.py`), build and verification scripts, selected shaping-test data, a checksum manifest, and beta-labelled specimens. The build uses FontTools; the verification script also requires `hb-shape` and Pillow with RAQM support.

```bash
python3 tools/build_pranoti_v0150_beta.py
python3 tools/verify_pranoti_v0150_beta.py
```

The build verifies the v0.140 input hash before resizing. The v0.150 output hash is in `CHECKSUMS-SHA256.txt`.

## License and attribution

This derivative is distributed under the original font's **GNU GPL version 2 or (at your option) any later version**, with the original font-embedding exception preserved. The unmodified GPL Version 2 text is in [`LICENSE-GPL-2.txt`](LICENSE-GPL-2.txt), and the preserved upstream notice and attribution are in [`ATTRIBUTION-LICENSE-NOTICE.txt`](ATTRIBUTION-LICENSE-NOTICE.txt). The source font is **AdorshoLipi by Partha Sarathi Pal**. The font's embedded attribution and license metadata have been retained.

## বাংলায় সংক্ষেপে

এটি **পরীক্ষামূলক public beta—production-ready নয়**। ইনস্টল করা যায়, কিন্তু উৎপাদন ব্যবহারের অনুমোদন নেই। এই সংস্করণে ৬৯টি মূল অক্ষর এখন মালিকের হাতের লেখা; আগে অনুপস্থিত ৪টি অক্ষর (U+0980, U+09FB, U+09FC, U+09FE) নতুন করে আঁকা হয়েছে, ফলে পর্যালোচিত coverage এখন **৯৬/৯৬**। চন্দ্রবিন্দু এখন সব অক্ষরের ওপরে anchor-based পদ্ধতিতে বসে; আগের তিনটি পর্যালোচিত অবস্থান (`কাঁ`, `চাঁ`, `ক্ষ্মাঁ`) হুবহু একই আছে। যুক্তাক্ষর এখনো AdorshoLipi—পরের ধাপে হাতের লেখা দিয়ে বদলানো হবে। v0.140-এ হাতের লেখার অক্ষরগুলোর ধার মসৃণ ও শার্প করা হয়েছে; আকার, ব্যবধান ও শেপিং একই আছে। v0.150-এ সব ৫৬টি মূল বর্ণ একই মাপে সাজানো হয়েছে — সবাই এক বেসলাইনে, এক মাথায় বসে। বিশেষজ্ঞের sign-off এবং Word/Office, browser, mobile, printসহ বিভিন্ন প্ল্যাটফর্মে বিস্তৃত পরীক্ষা বাকি।
