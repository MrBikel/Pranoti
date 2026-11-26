#!/usr/bin/env python3
"""Render v0.167 sign specimens (and LOOK at them).

(a) before-after-v0.167.png: the 13 ka+sign clusters (কা কি কী কু কূ কৃ
    কে কৈ কো কৌ কং কঃ কাঁ) + the 3 khanda-ta words (হঠাৎ সৎ উৎপাত),
    v0.166 grey (top) vs v0.167 black (bottom), RAQM, with TRUE baseline
    (red) and headline y=1157 (blue) guides. English-only labels
    (DejaVu has no Bengali glyphs — no Bengali in captions).
(b) v0167-sign-demo.png: the 13 clusters large, each sign in a real
    word, sentences using them heavily, and the cluster row side-by-side
    v0.166 (grey) vs v0.167 (black).
"""
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
PREP166 = BASE / 'v0166-prep'
PREP = BASE / 'v0167-prep'
V166 = str(PREP166 / 'Pranoti-Regular-v0.166-beta.ttf')
V167 = str(PREP / 'Pranoti-Regular-v0.167-beta.ttf')
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
UPM = 1536
HEADLINE = 1157

CLUSTERS = [('aakaar', 'কা'), ('ikaar', 'কি'), ('iikaar', 'কী'),
            ('ukaar', 'কু'), ('uukaar', 'কূ'), ('rikaar', 'কৃ'),
            ('ekaar', 'কে'), ('aikaar', 'কৈ'), ('okaar', 'কো'),
            ('aukaar', 'কৌ'), ('anusvara', 'কং'), ('visarga', 'কঃ'),
            ('candrabindu', 'কাঁ')]
WORDS = [('aakaar', 'কাল'), ('ikaar', 'দিন'), ('iikaar', 'নদী'),
         ('ukaar', 'ফুল'), ('uukaar', 'দূর'), ('rikaar', 'কৃষক'),
         ('ekaar', 'কেন'), ('aikaar', 'বৈশাখ'), ('okaar', 'কোন'),
         ('aukaar', 'মৌমাছি'), ('anusvara', 'বাংলা'), ('visarga', 'দুঃখ'),
         ('candrabindu', 'চাঁদ')]
KHANDA_WORDS = ['হঠাৎ', 'সৎ', 'উৎপাত']


def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


label_f = ImageFont.truetype(DEJA, 13)
small_f = ImageFont.truetype(DEJA, 11)

# ---------------- (a) before/after grid ----------------
SIZE = 72
CELL_W = 300
CELL_H = 150
COLS = 3
ITEMS = CLUSTERS + [('khanda-ta', w) for w in KHANDA_WORDS]
ROWS = (len(ITEMS) + COLS - 1) // COLS
W = COLS * CELL_W + 20
H = 60 + ROWS * 2 * CELL_H + 40
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), 'Pranoti v0.166 (top, grey) vs v0.167 (bottom, black) — ka+sign clusters and khanda-ta words',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d.text((10, 32), 'Red = baseline (y=0). Blue = headline (y=1157). RAQM layout: clusters shown in context.',
       font=small_f, fill='#586575')
f166, f167 = raqm(V166, SIZE), raqm(V167, SIZE)
sc = SIZE / UPM
for idx, (name, text) in enumerate(ITEMS):
    col, row = idx % COLS, idx // COLS
    x0 = 10 + col * CELL_W
    for band, fnt, colr in ((0, f166, '#8a97a3'), (1, f167, '#111820')):
        y_base = 60 + row * 2 * CELL_H + band * CELL_H + 110
        y_head = y_base - round(HEADLINE * sc)
        d.line([(x0, y_head), (x0 + CELL_W - 12, y_head)], fill='#3b82f6', width=1)
        d.line([(x0, y_base), (x0 + CELL_W - 12, y_base)], fill='#e11d48', width=1)
        d.text((x0 + 30, y_base), text, font=fnt, fill=colr, anchor='ls',
               direction='ltr', language='bn')
        if band == 1:
            d.text((x0 + 2, y_base + 18), name, font=small_f, fill='#586575')
im.save(PREP / 'specimens/before-after-v0.167.png', optimize=True)
print('saved specimens/before-after-v0.167.png', im.size)

# ---------------- (b) sign demo ----------------
W2, H2 = 1100, 1750
im2 = Image.new('RGB', (W2, H2), 'white')
d2 = ImageDraw.Draw(im2)
lab = ImageFont.truetype(DEJA, 15)
d2.text((30, 16), 'Pranoti v0.167-beta — vowel-sign and mark width-evening demo',
        font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d2.text((30, 44), 'The 13 ka+sign clusters, each sign in a word, sentences using them, and the clusters v0.166 vs v0.167.',
        font=lab, fill='#586575')
y = 110
d2.text((30, y), 'কা কি কী কু কূ কৃ কে কৈ কো কৌ কং কঃ কাঁ', font=raqm(V167, 56),
        fill='#111820', direction='ltr', language='bn')
y += 100
for name, word in WORDS:
    d2.text((30, y), f'{word}', font=raqm(V167, 34), fill='#111820',
            direction='ltr', language='bn')
    d2.text((330, y + 8), name, font=lab, fill='#586575')
    y += 52
y += 6
d2.text((30, y), 'হঠাৎ  সৎ  উৎপাত', font=raqm(V167, 34), fill='#111820',
        direction='ltr', language='bn')
d2.text((330, y + 8), 'khanda-ta (re-centred, adv 759->1210)', font=lab, fill='#586575')
y += 52
y += 10
pf = raqm(V167, 30)
sentences = ['বাংলা ভাষায় চাঁদের আলোয় নদীর কূলে বসে দুঃখ ভুলে',
             'কৃষক বৈশাখের গান শোনে। হঠাৎ বৃষ্টি নামল, তবুও সবাই',
             'মিলে উৎপাত ভুলে আনন্দ করল। দূর থেকে মৌমাছি এলো।']
for s in sentences:
    for line in textwrap.wrap(s, width=42):
        d2.text((30, y), line, font=pf, fill='#111820', direction='ltr', language='bn')
        y += 44
y += 10
d2.text((30, y), 'Cluster row, v0.166 (grey) vs v0.167 (black) — widths evened in black (ki, kai, ri narrower; o, au wider):',
        font=lab, fill='#586575')
y += 40
row = 'কা কি কী কু কূ কৃ কে কৈ কো কৌ কং কঃ কাঁ'
d2.text((30, y), row, font=raqm(V166, 44), fill='#8a97a3', direction='ltr', language='bn')
y += 64
d2.text((30, y), row, font=raqm(V167, 44), fill='#111820', direction='ltr', language='bn')
y += 80
im2 = im2.crop((0, 0, W2, y))
im2.save(PREP / 'specimens/v0167-sign-demo.png', optimize=True)
print('saved specimens/v0167-sign-demo.png', im2.size)
