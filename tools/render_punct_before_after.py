#!/usr/bin/env python3
"""Before/after grid for the v0.162 punctuation fine-tuning.

All 41 punctuation glyphs, v0.161 (top, grey) vs v0.162 (bottom, black),
110 px, BASIC layout, baseline (red) / headline y=1157 (blue) guides.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

V161 = '/home/hatch/workspace/fonts/bengali-hand/v0161-prep/Pranoti-Regular-v0.161-beta.ttf'
V162 = '/home/hatch/workspace/fonts/bengali-hand/v0162-prep/Pranoti-Regular-v0.162-beta.ttf'
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
UPM = 1536
HEADLINE = 1157

PUNCT = [
    ('danda', '।'), ('period', '.'), ('comma', ','), ('semicolon', ';'),
    ('colon', ':'), ('hyphen', '-'), ('endash', '–'), ('emdash', '—'),
    ('slash', '/'), ('backslash', '\\'),
    ('quoteleft', '‘'), ('quoteright', '’'),
    ('quotedblleft', '“'), ('quotedblright', '”'),
    ('quotesingle', "'"), ('quotedbl', '"'),
    ('question', '?'), ('exclam', '!'),
    ('parenleft', '('), ('parenright', ')'),
    ('bracketleft', '['), ('bracketright', ']'),
    ('braceleft', '{'), ('braceright', '}'),
    ('doubledanda', '॥'),
    ('asterisk', '*'), ('plus', '+'), ('less', '<'), ('equal', '='),
    ('greater', '>'), ('at', '@'), ('numbersign', '#'), ('dollar', '$'),
    ('percent', '%'), ('ampersand', '&'), ('asciicircum', '^'),
    ('underscore', '_'), ('grave', '`'), ('bar', '|'),
    ('asciitilde', '~'), ('divide', '÷'),
]


def basic(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)


SIZE = 110
CELL = 190
COLS = 7
ROWS = (len(PUNCT) + COLS - 1) // COLS
label_f = ImageFont.truetype(DEJA, 13)
small_f = ImageFont.truetype(DEJA, 11)
W = COLS * CELL + 20
H = 60 + ROWS * 2 * (SIZE + 46)
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), 'Pranoti v0.161 (top, grey) vs v0.162 (bottom, black) — all punctuation',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d.text((10, 32), 'Red = baseline (y=0). Blue = headline (y=1157). BASIC layout: marks shown alone at their font origin. Only 10 glyphs changed.',
       font=small_f, fill='#586575')
f161, f162 = basic(V161, SIZE), basic(V162, SIZE)
sc = SIZE / UPM
for idx, (name, ch) in enumerate(PUNCT):
    col, row = idx % COLS, idx // COLS
    x0 = 10 + col * CELL
    for band, fnt, colr in ((0, f161, '#8a97a3'), (1, f162, '#111820')):
        y_base = 60 + row * 2 * (SIZE + 46) + band * (SIZE + 46) + SIZE + 18
        y_head = y_base - round(HEADLINE * sc)
        d.line([(x0, y_head), (x0 + CELL - 12, y_head)], fill='#3b82f6', width=1)
        d.line([(x0, y_base), (x0 + CELL - 12, y_base)], fill='#e11d48', width=1)
        d.text((x0 + 60, y_base), ch, font=fnt, fill=colr, anchor='ls')
        if band == 1:
            d.text((x0 + 2, y_base + 18), name, font=small_f, fill='#586575')
out = Path('/home/hatch/workspace/fonts/bengali-hand/v0162-prep/specimens/before-after-v0.162.png')
im.save(out, optimize=True)
print('saved', out, im.size)
