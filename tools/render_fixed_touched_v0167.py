#!/usr/bin/env python3
"""Render v0.167 fixed-letters and touched-letters specimens (and LOOK at them).

(d) fixed-letters-v0.167.png: the three flagged glyphs — bn_anusvara (swoosh
    restored), bn_rikaar (shifted left), Khanda_Ta (re-centred) — v0.166 grey
    vs v0.167 black, large, in real words (বাংলা, কাঁদ, কৃষক, হঠাৎ, সৎ, উৎপাত),
    with baseline (red) and headline y=1157 (blue) guides. Standalone marks
    are rendered with BASIC layout (RAQM adds a dotted-circle placeholder to
    a lone combining mark — not a font defect).
(e) touched-letters-v0.167.png: the 13 point-repair / scale glyphs —
    দ য় গ চ ঝ ঞ ন স ঊ আ ই ঈ ঋ — each large (v0.166 grey vs v0.167 black)
    plus its words in v0.167. bn_yya is chr(0x09DF) explicitly: the literal
    'য়' in a Python source file can be the decomposed য+nukta sequence,
    which shapes as base+nukta and gives wrong ink boxes.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
V166 = str(BASE / 'v0166-prep/Pranoti-Regular-v0.166-beta.ttf')
V167 = str(BASE / 'v0167-prep/Pranoti-Regular-v0.167-beta.ttf')
PREP = BASE / 'v0167-prep'
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
UPM = 1536
HEADLINE = 1157

YAA = chr(0x09DF)


def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


def basic(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)


lab = ImageFont.truetype(DEJA, 15)
small = ImageFont.truetype(DEJA, 12)

# ---------------- (d) fixed letters ----------------
W, H = 1100, 1180
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((30, 16), 'Pranoti v0.167-beta — the three flagged glyphs, fixed',
       font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d.text((30, 44), 'v0.166 grey (top) vs v0.167 black (bottom). Red = baseline, blue = headline (y=1157).',
       font=lab, fill='#586575')
y = 100
FIXED = [
    ('anusvara (swoosh restored)', 'ং', ['বাংলা', 'কাঁদ', 'সংসার']),
    ('rikaar (shifted left, xMax -66)', 'ৃ', ['কৃষক', 'গৃহ', 'মৃদু', 'হৃদয়']),
    ('khanda-ta (re-centred, adv 759->1210)', 'ৎ', ['হঠাৎ', 'সৎ', 'উৎপাত']),
]
for label, ch, words in FIXED:
    d.text((30, y), label, font=lab, fill='#17202a')
    y += 34
    # standalone glyph (BASIC layout: no dotted-circle placeholder)
    for band, fnt, colr in ((0, basic(V166, 84), '#8a97a3'), (1, basic(V167, 84), '#111820')):
        y_base = y + 92
        sc = 84 / UPM
        d.line([(30, y_base - round(HEADLINE * sc)), (240, y_base - round(HEADLINE * sc))],
               fill='#3b82f6', width=1)
        d.line([(30, y_base), (240, y_base)], fill='#e11d48', width=1)
        d.text((40, y_base), ch, font=fnt, fill=colr, anchor='ls')
        y += 108
    # words in v0.167 (RAQM), on one line
    d.text((30, y), '  '.join(words), font=raqm(V167, 44), fill='#111820',
           direction='ltr', language='bn')
    y += 76
    y += 14
im = im.crop((0, 0, W, y))
im.save(PREP / 'specimens/fixed-letters-v0.167.png', optimize=True)
print('saved specimens/fixed-letters-v0.167.png', im.size)

# ---------------- (e) touched letters ----------------
TOUCHED = [
    ('bn_da', 'দ', ['দিন', 'দাদা', 'বাংলাদেশ']),
    ('bn_yya', YAA, ['মায়া', 'ছায়া']),
    ('bn_ga', 'গ', ['গরু', 'গান', 'বাংলা']),
    ('bn_ca', 'চ', ['চাঁদ', 'চোখ', 'চা']),
    ('bn_jha', 'ঝ', ['ঝড়', 'ঝাপসা']),
    ('bn_nya', 'ঞ', ['মিঞা', 'কিঞ্চিৎ']),
    ('bn_na', 'ন', ['নদী', 'নাম', 'কান']),
    ('bn_sa', 'স', ['সকাল', 'মাস', 'বসা']),
    ('bn_uu', 'ঊ', ['ঊষা', 'ঊন']),
    ('bn_aa', 'আ', ['আম', 'আসা', 'বাংলা']),
    ('bn_i', 'ই', ['ইদ', 'ইতি']),
    ('bn_ii', 'ঈ', ['ঈদ', 'ঈশ্বর']),
    ('bn_ri', 'ঋ', ['ঋণ', 'ঋতু']),
]
W2, H2 = 1100, 2600
im2 = Image.new('RGB', (W2, H2), 'white')
d2 = ImageDraw.Draw(im2)
d2.text((30, 16), 'Pranoti v0.167-beta — the 13 repaired / resized letters',
        font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d2.text((30, 44), 'Each letter large: v0.166 grey (left) vs v0.167 black (right); its words in v0.167 below.',
        font=lab, fill='#586575')
y = 100
for name, ch, words in TOUCHED:
    d2.text((30, y), name, font=lab, fill='#17202a')
    # large glyph, before (grey) left, after (black) right, BASIC layout
    for band, fnt, colr, x in ((0, basic(V166, 96), '#8a97a3', 40),
                                (1, basic(V167, 96), '#111820', 300)):
        y_base = y + 108
        sc = 96 / UPM
        d2.line([(x, y_base - round(HEADLINE * sc)), (x + 220, y_base - round(HEADLINE * sc))],
                fill='#3b82f6', width=1)
        d2.line([(x, y_base), (x + 220, y_base)], fill='#e11d48', width=1)
        d2.text((x + 10, y_base), ch, font=fnt, fill=colr, anchor='ls')
    # words in v0.167 (RAQM) on the right
    d2.text((560, y + 40), '  '.join(words), font=raqm(V167, 40), fill='#111820',
            direction='ltr', language='bn')
    y += 150
im2 = im2.crop((0, 0, W2, y))
im2.save(PREP / 'specimens/touched-letters-v0.167.png', optimize=True)
print('saved specimens/touched-letters-v0.167.png', im2.size)
