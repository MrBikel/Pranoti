# Pranoti v0.164-beta

> **Experimental public beta — not production-ready.** This is an installable review build for testing, not a final font release. Installability does not mean production approval.

Pranoti v0.164-beta is a Bengali font in the owner's handwriting. The owner's strategy: progressively replace the base font's glyphs with his handwriting, glyph by glyph, until the whole font is his. This batch fine-tunes the handwriting glyphs in four passes on top of the v0.160 re-trace: stroke-weight evening (v0.161), punctuation (v0.162), vowels (v0.163) and consonants (v0.164), on top of the 69 core glyphs re-traced from clean photos, the 14 punctuation glyphs in his handwriting, the 4 previously missing codepoints, the generalised candrabindu positioning, and the size-normalised core letters. The distributed TrueType font's internal family name is **Pranoti**.

## Download and install

`Pranoti-Regular-v0.164-beta.ttf` (local build; no GitHub release published yet — do not push or publish without the owner's approval). Verify its SHA-256 before installing:

```text
9bc1e3f4c2be27ef2f3d032c8bd4ecbf9e337d596d73c0c90bded87f677f2a4d
```

- **Windows:** Right-click the downloaded `.ttf` and choose **Install** (or **Install for all users** if appropriate). Close and reopen apps that use fonts. Remove any earlier Pranoti copy first to avoid cached or duplicate versions.
- **macOS:** Open the `.ttf` in Font Book and choose **Install Font**. Restart the target app if it was already open.
- **Linux:** Copy the file to `~/.local/share/fonts/`, then run `fc-cache -f` and restart the target app.

These are general installation steps, not a compatibility claim. Browsers, mobile platforms, print workflows, and other applications have not received broad beta testing.

## What changed

- **69 core glyphs are now John's handwriting** (11 vowels, 35 consonants, 10 digits, 13 vowel signs/marks), fitted to the v0.120 metrics: same baseline, advance widths and side bearings. The hasanta was deliberately kept from the base font. 7 core codepoints stay from the base font for now (see limitations). Per-glyph log: `REPLACEMENT-LOG-v0.130.md`.
- **4 new glyphs, designed from scratch:** U+0980 ANJI, U+09FB GANDA MARK, U+09FC VEDIC ANUSVARA, U+09FE SANDHI MARK.
- **Candrabindu (U+0981) is now anchor-based over all bases:** the three reviewed offsets are preserved exactly — `কাঁ` Δ(−450,+125), `চাঁ` Δ(−278,+125), `ক্ষ্মাঁ` Δ(−632,+125) — and the mark is now positioned over all 55 bases and 375 ligatures (e.g. `গাঁ` now positions correctly; it did not before).
- GDEF glyph classes (base / ligature / mark) were added so shaping engines apply the mark lookups. No GSUB changes were made.
- **v0.140 polish:** the 73 handwriting glyph outlines were smoothed (cleaner, sharper edges) and near-duplicate points merged; metrics, spacing and shaping are unchanged. Per-glyph log: `POLISH-LOG-v0.140.md`.
- **v0.150 size normalisation:** all 56 core letters (11 vowels, 35 consonants, 10 digits) were mildly rescaled (uniform ×0.970–×1.062) and translated so every letter's ink top and ink centre match the base font's for that letter — ink-top error is now exactly 0 for all 56. Advances are unchanged; ঞ's two stray hairline slivers were removed. Per-glyph log: `SIZE-LOG-v0.150.md`.
- **v0.160 re-trace:** all 69 handwriting glyphs were re-traced from 37 clean photos (vowels best-of-7) and 14 punctuation glyphs are now in his handwriting too; the new outlines were fitted to the v0.150 ink boxes and polished, with advances and shaping unchanged. His handwriting is ~25% wider than the v0.150 outlines, so text reads denser and bolder. Per-glyph log: `RE-TRACE-LOG-v0.160.md`.
- **v0.161 weight evening:** the owner said some letters looked bold and some thin; measured letter stroke width (median 84.5 units) and evened 17 glyphs with FontForge `changeWeight` (capped ±16 units per pass) so the letter spread narrowed 69–120 → 75.6–92.5, median still 84.5. bn_anusvara (ং) was reverted — thinning it created a degenerate kink; it stays +18% heavy and needs a manual pass. Per-glyph log: `WEIGHT-LOG-v0.161.md`, plan: `WEIGHT-PLAN-v0.161.md`.
- **v0.162 punctuation fine-tuning:** 10 punctuation glyphs adjusted — danda and doubledanda now reach the headline (1157), colon dots aligned at ~300 wide, semicolon dot 375 → 300, question dot 123 → 278 and exclamation dot 161 → 275 (one dot family), hyphen 840 → 532 (now correctly shorter than en dash 663), slash and backslash thinned to letter weight, em dash thickened to 130.6. Per-glyph log: `PUNCT-LOG-v0.162.md`.
- **v0.163 vowel fine-tuning:** 4 vowels (ই, এ, ঐ, ঔ) had sunk 12–21 units below their target height during the v0.161 thinning and were restored (uniform scale ×1.011–×1.037 about the ink centre); tops are now exactly on target. No weight changes — all 11 vowels were already in the ±15% band. Per-glyph log: `VOWEL-LOG-v0.163.md`.
- **v0.164 consonant fine-tuning:** 3 consonants (খ, গ, য়) had sunk 12–20 units below their target height during the v0.161 thinning and were restored (uniform scale ×1.018–×1.030 about the ink centre); tops and bottoms are now exactly on target. No weight changes — all 35 consonants were already in the ±15% band (75.6–92.2). ঙ's hook and ধ's loop were checked clean, no surgery needed. Per-glyph log: `CONSONANT-LOG-v0.164.md`.

See the [changelog](CHANGELOG.md), [test summary](TEST-SUMMARY.md), [replacement log](REPLACEMENT-LOG-v0.130.md), [polish log](POLISH-LOG-v0.140.md), [size log](SIZE-LOG-v0.150.md), [re-trace log](RE-TRACE-LOG-v0.160.md), [weight log](WEIGHT-LOG-v0.161.md), [punctuation log](PUNCT-LOG-v0.162.md), [vowel log](VOWEL-LOG-v0.163.md), [consonant log](CONSONANT-LOG-v0.164.md), and [specimens](specimens/before-after-v0.164.png) (before/after) and [specimens](specimens/matched-v0.163-v0.164-review.png) (matched review).

## Clear limitations

- **Bengali coverage is now 96/96 in the reviewed coverage set** (the 4 previously missing codepoints were added). Still absent from the cmap: **U+098D, U+098E, U+0991, U+0992** (঍, ঎, ঑, ঒) and Assamese **U+09F0, U+09F1** (ৰ, ৱ).
- **Conjunct ligatures are still from the original base font.** The ~300 conjunct cells the owner photographed have not been replaced yet; that is the next batch.
- **7 core codepoints are still from the original base font:** ঌ (U+098C, absent from the handwriting source), plus the six absent from the cmap listed above.
- **The handwriting outlines are traced, not redrawn:** some glyphs are rough (ঋ, ঝ, ঙ keep rough traced shapes; ধ's top loop is slightly pinched). No kerning or GPOS pair positioning beyond candrabindu.
- **Expert type-design sign-off is pending.** Broad testing across Microsoft Office/Word, browsers, mobile platforms, printing, and other target environments is also pending.
- The owner reported testing v0.120 on **Windows 11 Home with Microsoft Word** and said everything looked okay. This is an owner-reported result only, not independent QA; specific test cases and broad compatibility were not established. v0.130–v0.164 have not been owner-tested yet.
- The font's `OS/2 fsType=4` Preview & Print setting and the original GPL font-embedding exception are retained. This does not certify that every application will honor those terms or render the font identically.

Please report issues with the application, operating system, font size, and a reproducible sample. Do not treat this beta as production-ready.

## Build and test materials

This repository includes the editable FontForge source snapshot, the v0.120 baseline, the handwriting source (`inputs/Pranoti-Handwriting-v4.ttf`), the new-glyphs source (`inputs/new-glyphs-v0130.ttf`, drawn with `tools/draw_new_glyphs.py`), build and verification scripts, selected shaping-test data, a checksum manifest, and beta-labelled specimens. The build uses FontTools; the verification script also requires `hb-shape` and Pillow with RAQM support.

```bash
python3 tools/build_consonants_v0164.py
python3 tools/verify_pranoti_v0164_beta.py
```

The build verifies the v0.163 input hash before fine-tuning. The v0.164 output hash is in `CHECKSUMS-SHA256.txt`.

## License and attribution

This font is distributed under the **GNU GPL version 2 or (at your option) any later version**, with the original font-embedding exception preserved. The unmodified GPL Version 2 text is in [`LICENSE-GPL-2.txt`](LICENSE-GPL-2.txt), and the copyright and license notices required by the GPL are preserved in [`ATTRIBUTION-LICENSE-NOTICE.txt`](ATTRIBUTION-LICENSE-NOTICE.txt). The font's embedded license metadata has been retained.

## বাংলায় সংক্ষেপে

এটি **পরীক্ষামূলক public beta—production-ready নয়**। ইনস্টল করা যায়, কিন্তু উৎপাদন ব্যবহারের অনুমোদন নেই। এই সংস্করণে ৬৯টি মূল অক্ষর এখন মালিকের হাতের লেখা; আগে অনুপস্থিত ৪টি অক্ষর (U+0980, U+09FB, U+09FC, U+09FE) নতুন করে আঁকা হয়েছে, ফলে পর্যালোচিত coverage এখন **৯৬/৯৬**। চন্দ্রবিন্দু এখন সব অক্ষরের ওপরে anchor-based পদ্ধতিতে বসে; আগের তিনটি পর্যালোচিত অবস্থান (`কাঁ`, `চাঁ`, `ক্ষ্মাঁ`) হুবহু একই আছে। যুক্তাক্ষর এখনো মূল ফন্টের—পরের ধাপে হাতের লেখা দিয়ে বদলানো হবে। v0.140-এ হাতের লেখার অক্ষরগুলোর ধার মসৃণ ও শার্প করা হয়েছে; আকার, ব্যবধান ও শেপিং একই আছে। v0.150-এ সব ৫৬টি মূল বর্ণ একই মাপে সাজানো হয়েছে — সবাই এক বেসলাইনে, এক মাথায় বসে। v0.160-এ পরিষ্কার ছবি থেকে ৬৯টি মূল বর্ণ নতুন করে তোলা হয়েছে, সাথে ১৪টি যতিচিহ্ন এখন মালিকের হাতের লেখা; লেখা আগের চেয়ে গাঢ় ও ঘন দেখাবে, কারণ তাঁর আসল হাতের লেখা ফন্টের চেয়ে ~২৫% চওড়া। v0.161-এ অক্ষরগুলোর ওজন সমান করা হয়েছে, v0.162-এ যতিচিহ্ন ঠিক করা হয়েছে, v0.163-এ ৪টি স্বরবর্ণ ও v0.164-এ ৩টি ব্যঞ্জনবর্ণের উচ্চতা আবার লক্ষ্যমাত্রায় ফেরানো হয়েছে। বিশেষজ্ঞের sign-off এবং Word/Office, browser, mobile, printসহ বিভিন্ন প্ল্যাটফর্মে বিস্তৃত পরীক্ষা বাকি।
