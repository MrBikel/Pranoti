#!/usr/bin/env python3
"""Before/after specimen for Pranoti v0.130-beta.

Rows: each core glyph in v0.130-beta vs v0.140-beta (polished John's
handwriting), plus the 4 new glyphs and a paragraph of real Bengali text.
Rendered with FreeType/Pillow RAQM so shaping is real.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/home/hatch/workspace/fonts/bengali-hand/github-repo')
OLD = ROOT / 'Pranoti-Regular-v0.130-beta.ttf'
NEW = ROOT / 'Pranoti-Regular-v0.140-beta.ttf'
OUT = ROOT / 'specimens' / 'before-after-v0.140.png'

W = 1200
BG = (255, 255, 255)
INK = (20, 20, 20)
MUT = (100, 110, 125)
LINE = (200, 208, 220)
CELL = 44          # px per glyph cell (square-ish)
GRID_FS = 34       # glyph font size in the grid
LABEL_FS = 13

VOWELS = list('অআইঈউঊঋএঐওঔ')
CONSONANTS = list('কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়')
DIGITS = list('০১২৩৪৫৬৭৮৯')
# vowel signs shown attached to ka
SIGNS = ['া', 'ি', 'ী', 'ু', 'ূ', 'ৃ', 'ে', 'ৈ', 'ো', 'ৌ', 'ং', 'ঃ', 'ঁ', '্']
NEW_GLYPHS = [(0x0980, 'U+0980 ANJI'), (0x09FB, 'U+09FB GANDA'),
              (0x09FC, 'U+09FC VEDIC ANUSVARA'), (0x09FE, 'U+09FE SANDHI MARK')]

PARA = ('অভিযাত্রী একটি বাংলা সাহিত্য পত্রিকা। চাঁদের আলোয় কাঁটার বনে হাঁটতে '
        'হাঁটতে কবি লিখলেন — বাংলা ভাষা আমার প্রাণের ভাষা। ক্ষমা, জ্ঞান, '
        'স্তব্ধ রাত্রি, ত্রিশ বছর, ন্তু—এই সব শব্দে যুক্তাক্ষর জ্বলজ্বল করে। '
        'সংখ্যায় ১২৩৪৫৬৭৮৯০, দাম ৫০০ টাকা। প্রণতি ফন্টে এখন জন-এর হাতের '
        'লেখা, এক অক্ষর এক অক্ষর করে।')


def text_size(draw, s, font):
    b = draw.textbbox((0, 0), s, font=font)
    return b[2] - b[0], b[3] - b[1]


def main():
    old = ImageFont.truetype(str(OLD), GRID_FS, layout_engine=ImageFont.Layout.RAQM)
    new = ImageFont.truetype(str(NEW), GRID_FS, layout_engine=ImageFont.Layout.RAQM)
    lab = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', LABEL_FS)
    lab_b = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', LABEL_FS + 2)
    title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    para_f = ImageFont.truetype(str(NEW), 22, layout_engine=ImageFont.Layout.RAQM)
    para_f2 = ImageFont.truetype(str(NEW), 30, layout_engine=ImageFont.Layout.RAQM)

    # measure height by stacking sections
    def section_h(n_rows, row_h):
        return n_rows * row_h + 30

    rows = []
    # each entry: (label, [chars], kind) kind: 'char' | 'sign' | 'new'
    rows.append(('Vowels (11)', VOWELS, 'char'))
    rows.append(('Consonants (37)', CONSONANTS, 'char'))
    rows.append(('Digits (10)', DIGITS, 'char'))
    rows.append(('Vowel signs on KA (14)', SIGNS, 'sign'))
    rows.append(('New glyphs (4)', [chr(c) for c, _ in NEW_GLYPHS], 'new'))

    row_h = CELL + 8
    total = 90  # title block
    for label, chars, kind in rows:
        per = 6 if kind == 'sign' else 12
        n = (len(chars) + per - 1) // per
        total += 28 + n * (row_h + 4) + 14
    total += 28 + 4 * 34 + 24  # paragraph block
    total += 28 + 2 * 44 + 20  # headline block
    total += 28 + 96 + 96 + 20  # close-up block (two rows)

    img = Image.new('RGB', (W, total), BG)
    d = ImageDraw.Draw(img)
    y = 24
    d.text((24, y), 'Pranoti v0.140-beta — before / after (polish & sharpen)', font=title, fill=INK)
    y += 30
    d.text((24, y), 'Left: v0.130-beta   Right: v0.140-beta (same handwriting, smoothed outlines). '
           'Experimental public beta, not production-ready.', font=lab, fill=MUT)
    y += 30

    for label, chars, kind in rows:
        d.text((24, y), label, font=lab_b, fill=INK)
        y += 26
        # column headers
        d.text((24, y), 'v0.130-beta', font=lab, fill=MUT)
        d.text((W // 2 + 12, y), 'v0.140-beta', font=lab, fill=MUT)
        y += 18
        per = 6 if kind == 'sign' else 12
        cell_w = (W // 2 - 36) // per
        for start in range(0, len(chars), per):
            chunk = chars[start:start + per]
            for i, ch in enumerate(chunk):
                x0 = 24 + i * cell_w
                x1 = W // 2 + 12 + i * cell_w
                for x, fnt in ((x0, old), (x1, new)):
                    s = ch if kind == 'char' else ('ক' + ch if kind == 'sign' else ch)
                    if kind == 'new' and fnt is old:
                        s = ch  # present in v0.130 too; show polished vs unpolished
                    tw, th = text_size(d, s, fnt)
                    d.text((x + (cell_w - tw) / 2, y + (CELL - th) / 2 - 4), s, font=fnt, fill=INK)
                    d.rectangle([x, y, x + cell_w - 4, y + CELL], outline=LINE)
            y += row_h + 4
        y += 10

    # paragraph
    d.text((24, y), 'Paragraph (v0.140-beta, 22 px)', font=lab_b, fill=INK)
    y += 26
    # simple word-wrap
    words = PARA.split(' ')
    lines = []
    cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        tw, _ = text_size(d, t, para_f)
        if tw > W - 48 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    for ln in lines:
        d.text((24, y), ln, font=para_f, fill=INK)
        y += 34
    y += 12
    d.text((24, y), 'Headline (v0.140-beta, 30 px)', font=lab_b, fill=INK)
    y += 26
    for ln in ('অভিযাত্রী — প্রণতি', 'চাঁদ কাঁটা ক্ষমা জ্ঞান ১২৩৪৫'):
        d.text((24, y), ln, font=para_f2, fill=INK)
        y += 44
    # close-up: known-rough glyphs at 64 px, v0.130 only
    d.text((24, y), 'Close-up (64 px) — roughest handwriting glyphs + key words', font=lab_b, fill=INK)
    y += 26
    close_o = ImageFont.truetype(str(OLD), 64, layout_engine=ImageFont.Layout.RAQM)
    close_f = ImageFont.truetype(str(NEW), 64, layout_engine=ImageFont.Layout.RAQM)
    d.text((24, y), 'v0.130-beta', font=lab, fill=MUT)
    d.text((24, y + 22), 'ঋ ঝ ঙ ধ ণ  অভিযাত্রী  ক্ষ্ম  চাঁদ  গাঁ', font=close_o, fill=INK)
    y += 96
    d.text((24, y), 'v0.140-beta', font=lab, fill=MUT)
    d.text((24, y + 22), 'ঋ ঝ ঙ ধ ণ  অভিযাত্রী  ক্ষ্ম  চাঁদ  গাঁ', font=close_f, fill=INK)
    y += 96
    img.save(OUT)
    print('wrote', OUT, img.size)


if __name__ == '__main__':
    main()
