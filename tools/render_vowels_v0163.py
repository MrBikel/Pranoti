#!/usr/bin/env python3
"""Render v0.163 vowel specimens (and LOOK at them).

(a) before-after-v0.163.png: all 11 vowels, v0.162 grey (top) vs v0.163
    black (bottom), with TRUE baseline (red) and headline y=1157 (blue)
    guides. BASIC layout so each vowel renders alone at its font origin.
(b) v0163-vowel-demo.png: the 11 vowels large, each in a real word, a few
    sentences using all 11 vowels, and the vowel row side-by-side
    v0.162 (grey) vs v0.163 (black) so the restored tops show.
"""
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
PREP162 = BASE / 'v0162-prep'
PREP = BASE / 'v0163-prep'
V162 = str(PREP162 / 'Pranoti-Regular-v0.162-beta.ttf')
V163 = str(PREP / 'Pranoti-Regular-v0.163-beta.ttf')
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
UPM = 1536
HEADLINE = 1157

VOWELS = [('অ', 'bn_a'), ('আ', 'bn_aa'), ('ই', 'bn_i'), ('ঈ', 'bn_ii'),
          ('উ', 'bn_u'), ('ঊ', 'bn_uu'), ('ঋ', 'bn_ri'), ('এ', 'bn_e'),
          ('ঐ', 'bn_ai'), ('ও', 'bn_o'), ('ঔ', 'bn_au')]
WORDS = [('অ', 'অমর'), ('আ', 'আমি'), ('ই', 'ইলিশ'), ('ঈ', 'ঈদ'),
         ('উ', 'উঠান'), ('ঊ', 'ঊষা'), ('ঋ', 'ঋণ'), ('এ', 'একা'),
         ('ঐ', 'ঐতিহ্য'), ('ও', 'ওজন'), ('ঔ', 'ঔষধ')]


def basic(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)


def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


label_f = ImageFont.truetype(DEJA, 13)
small_f = ImageFont.truetype(DEJA, 11)

# ---------------- (a) before/after grid ----------------
SIZE = 110
CELL = 190
COLS = 4
ROWS = (len(VOWELS) + COLS - 1) // COLS
W = COLS * CELL + 20
H = 60 + ROWS * 2 * (SIZE + 46) + 40
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), 'Pranoti v0.162 (top, grey) vs v0.163 (bottom, black) — all 11 vowels',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d.text((10, 32), 'Red = baseline (y=0). Blue = headline (y=1157). BASIC layout: vowels shown alone at their font origin.',
       font=small_f, fill='#586575')
f162, f163 = basic(V162, SIZE), basic(V163, SIZE)
sc = SIZE / UPM
for idx, (ch, name) in enumerate(VOWELS):
    col, row = idx % COLS, idx // COLS
    x0 = 10 + col * CELL
    for band, fnt, colr in ((0, f162, '#8a97a3'), (1, f163, '#111820')):
        y_base = 60 + row * 2 * (SIZE + 46) + band * (SIZE + 46) + SIZE + 18
        y_head = y_base - round(HEADLINE * sc)
        d.line([(x0, y_head), (x0 + CELL - 12, y_head)], fill='#3b82f6', width=1)
        d.line([(x0, y_base), (x0 + CELL - 12, y_base)], fill='#e11d48', width=1)
        d.text((x0 + 60, y_base), ch, font=fnt, fill=colr, anchor='ls')
        if band == 1:
            d.text((x0 + 2, y_base + 18), name, font=small_f, fill='#586575')
im.save(PREP / 'specimens/before-after-v0.163.png', optimize=True)
print('saved specimens/before-after-v0.163.png', im.size)

# ---------------- (b) vowel demo ----------------
W2, H2 = 1100, 1450
im2 = Image.new('RGB', (W2, H2), 'white')
d2 = ImageDraw.Draw(im2)
lab = ImageFont.truetype(DEJA, 15)
d2.text((30, 16), 'Pranoti v0.163-beta — vowel fine-tuning demo', font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d2.text((30, 44), 'The 11 vowels, each in a word, sentences using all 11, and the vowel row v0.162 vs v0.163.',
        font=lab, fill='#586575')
y = 110
d2.text((30, y), 'অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ', font=raqm(V163, 64), fill='#111820', direction='ltr', language='bn')
y += 110
for ch, word in WORDS:
    d2.text((30, y), f'{ch} — {word}', font=raqm(V163, 34), fill='#111820', direction='ltr', language='bn')
    y += 52
y += 10
pf = raqm(V163, 30)
sentences = ['অমর অফিসে গেল। আমি আজ ইলিশ মাছ কিনেছি।',
             'ঈদের ছুটিতে উঠানে বসে ঊষার গল্প শুনলাম।',
             'ঋণ শোধ করে একা ঐতিহ্যবাহী বাড়িতে ওজন মেপে ঔষধ খেলাম।']
for s in sentences:
    for line in textwrap.wrap(s, width=42):
        d2.text((30, y), line, font=pf, fill='#111820', direction='ltr', language='bn')
        y += 44
y += 10
d2.text((30, y), 'Vowel row, v0.162 (grey) vs v0.163 (black) — the four restored tops sit higher in black:',
        font=lab, fill='#586575')
y += 40
row = 'অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ'
d2.text((30, y), row, font=raqm(V162, 44), fill='#8a97a3', direction='ltr', language='bn')
y += 64
d2.text((30, y), row, font=raqm(V163, 44), fill='#111820', direction='ltr', language='bn')
y += 80
im2 = im2.crop((0, 0, W2, y))
im2.save(PREP / 'specimens/v0163-vowel-demo.png', optimize=True)
print('saved specimens/v0163-vowel-demo.png', im2.size)
