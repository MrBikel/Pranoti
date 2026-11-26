#!/usr/bin/env python3
"""Render punctuation specimens for one TTF (before/after comparison).

(a) punct-grid: every punctuation glyph at 110 px, BASIC layout, with
    baseline (red) and headline y=1157 (blue) guides.
(b) punct-sentences: every mark used inside a real Bengali sentence
    (RAQM), so the marks can be judged in context.
Usage: python3 render_punct_specimens.py <ttf> <outprefix>
"""
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TTF, PREFIX = sys.argv[1], sys.argv[2]
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


def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


# ---------------- (a) grid ----------------
SIZE = 110
CELL = 190
COLS = 7
ROWS = (len(PUNCT) + COLS - 1) // COLS
label_f = ImageFont.truetype(DEJA, 13)
small_f = ImageFont.truetype(DEJA, 11)
W = COLS * CELL + 20
H = 60 + ROWS * (SIZE + 46)
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), f'Punctuation — {Path(TTF).stem}',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d.text((10, 32), 'Red = baseline (y=0). Blue = headline (y=1157). BASIC layout: marks shown alone at their font origin.',
       font=small_f, fill='#586575')
fnt = basic(TTF, SIZE)
sc = SIZE / UPM
for idx, (name, ch) in enumerate(PUNCT):
    col, row = idx % COLS, idx // COLS
    x0 = 10 + col * CELL
    y_base = 60 + row * (SIZE + 46) + SIZE + 18
    y_head = y_base - round(HEADLINE * sc)
    d.line([(x0, y_head), (x0 + CELL - 12, y_head)], fill='#3b82f6', width=1)
    d.line([(x0, y_base), (x0 + CELL - 12, y_base)], fill='#e11d48', width=1)
    d.text((x0 + 60, y_base), ch, font=fnt, fill='#111820', anchor='ls')
    d.text((x0 + 2, y_base + 18), name, font=small_f, fill='#586575')
im.save(f'{PREFIX}-grid.png', optimize=True)
print('saved', f'{PREFIX}-grid.png', im.size)

# ---------------- (b) sentences demo ----------------
SENTENCES = [
    'আমি কি যাব? হ্যাঁ, যাব। না, যাব না!',
    'বলল, “এসো!” — সে এলো; তারপর চলে গেল।',
    'দাম: ২১ মে, ২০২৬ — বিকেল ৩:০০ ঘটিকা।',
    '‘প্রতীকী হজ্ব শিক্ষা প্রদর্শনী’ (টিটু মিলনায়তন)।',
    'ক, খ; গ: ঘ? ঙ! চ—ছ/জ ॥ ঝঞ?',
    'দাম ১০০ টাকা + ৫০ = ১৫০; ৫০% ছাড়!',
    '[প্রথম] (দ্বিতীয়) {তৃতীয়} — সবই ঠিক আছে।',
    '“কাঁদো না,” সে বলল। ‘আমি আসছি!’',
]
W2, H2 = 1100, 900
im2 = Image.new('RGB', (W2, H2), 'white')
d2 = ImageDraw.Draw(im2)
d2.text((30, 16), f'Punctuation in sentences — {Path(TTF).stem}',
        font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d2.text((30, 44), 'Every mark used inside a real Bengali sentence. Check: sizes even, nothing floats or sinks, no crowding.',
        font=ImageFont.truetype(DEJA, 15), fill='#586575')
y = 110
pf = raqm(TTF, 34)
for s in SENTENCES:
    for line in textwrap.wrap(s, width=36):
        d2.text((30, y), line, font=pf, fill='#111820', direction='ltr', language='bn')
        y += 52
    y += 18
im2 = im2.crop((0, 0, W2, y + 20))
im2.save(f'{PREFIX}-sentences.png', optimize=True)
print('saved', f'{PREFIX}-sentences.png', im2.size)
