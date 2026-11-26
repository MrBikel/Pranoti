#!/usr/bin/env python3
"""Render v0.160 visual specimens (and LOOK at them).

(a) before-after-v0.160.png: all 83 changed glyphs, v0.150 row over
    v0.160 row, with TRUE baseline (red) and headline y=1157 (blue) guides.
    BASIC layout (no shaping) so the 13 combining marks render alone, at
    their font origin — the comparison is of the outlines themselves.
(b) v0160-writing-demo.png: headline + paragraph + alphabet + digits +
    punctuation, v0.160 (RAQM); plus a side-by-side paragraph v0.150/v0.160.
(c) closeup-v0.160.png: the most-changed / most-notable glyphs at 200 px.
(d) chosen-vowels-v0.160.png: the 11 vowel cells actually traced, with
    their source photo/row/col labels.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PREP = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
V150 = '/home/hatch/workspace/fonts/bengali-hand/github-repo/Pranoti-Regular-v0.150-beta.ttf'
V160 = str(PREP / 'Pranoti-Regular-v0.160-beta.ttf')
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
UPM = 1536
HEADLINE = 1157

traced = json.load(open(PREP / 'traced_glyphs.json', encoding='utf-8'))
GLYPHS = [(d['char'], name) for name, d in traced.items()]

def basic(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)

def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)

# ---------------- (a) before/after grid ----------------
SIZE = 110
CELL = 190
COLS = 7
ROWS = (len(GLYPHS) + COLS - 1) // COLS
label_f = ImageFont.truetype(DEJA, 13)
small_f = ImageFont.truetype(DEJA, 11)
W = COLS * CELL + 20
H = 60 + ROWS * 2 * (SIZE + 46)
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), 'Pranoti v0.150 (top, grey) vs v0.160 (bottom, black) — all 83 re-traced glyphs',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d.text((10, 32), 'Red = baseline (y=0). Blue = headline (y=1157). BASIC layout: marks shown alone at their font origin.',
       font=small_f, fill='#586575')
f150, f160 = basic(V150, SIZE), basic(V160, SIZE)
sc = SIZE / UPM
for idx, (ch, name) in enumerate(GLYPHS):
    col, row = idx % COLS, idx // COLS
    x0 = 10 + col * CELL
    for band, fnt, colr in ((0, f150, '#8a97a3'), (1, f160, '#111820')):
        y_base = 60 + row * 2 * (SIZE + 46) + band * (SIZE + 46) + SIZE + 18
        y_head = y_base - round(HEADLINE * sc)
        d.line([(x0, y_head), (x0 + CELL - 12, y_head)], fill='#3b82f6', width=1)
        d.line([(x0, y_base), (x0 + CELL - 12, y_base)], fill='#e11d48', width=1)
        d.text((x0 + 60, y_base), ch, font=fnt, fill=colr, anchor='ls')
        if band == 1:
            d.text((x0 + 2, y_base + 18), name, font=small_f, fill='#586575')
im.save(PREP / 'specimens/before-after-v0.160.png', optimize=True)
print('saved specimens/before-after-v0.160.png', im.size)

# ---------------- (b) writing demo ----------------
W2, H2 = 1100, 1500
im2 = Image.new('RGB', (W2, H2), 'white')
d2 = ImageDraw.Draw(im2)
lab = ImageFont.truetype(DEJA, 15)
d2.text((30, 16), 'Pranoti v0.160-beta — writing demo', font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d2.text((30, 44), 'Headline, paragraph, alphabet, digits and punctuation. Check: even rhythm, no collisions, nothing floats or sinks.',
        font=lab, fill='#586575')
y = 110
d2.text((30, y), 'অভিযাত্রী', font=raqm(V160, 84), fill='#111820', direction='ltr', language='bn')
y += 130
import textwrap
para = ('অভিযাত্রী সাহিত্য পত্রিকার নতুন সংখ্যায় চাঁদের আলোয় লেখা কবিতা, '
        'ক্ষমা ও জ্ঞানের গল্প, আর সংখ্যা ১২৩৪৫৬৭৮৯০ ছাপা হয়েছে। '
        'বাংলা ভাষার সৌন্দর্য প্রতিটি বর্ণে ফুটে ওঠে যখন সব বর্ণ একই '
        'আকারে সাজানো থাকে।')
pf = raqm(V160, 30)
for line in textwrap.wrap(para, width=42):
    d2.text((30, y), line, font=pf, fill='#111820', direction='ltr', language='bn')
    y += 44
y += 10
d2.text((30, y), 'অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ', font=raqm(V160, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), 'ক খ গ ঘ ঙ চ ছ জ ঝ ঞ ট ঠ ড ঢ ণ ত থ দ ধ ন প ফ ব ভ ম য র ল শ ষ স হ ড় ঢ় য়',
        font=raqm(V160, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), '০ ১ ২ ৩ ৪ ৫ ৬ ৭ ৮ ৯', font=raqm(V160, 40), fill='#111820', direction='ltr', language='bn')
y += 90
d2.text((30, y), 'চাঁদ  ক্ষমা  জ্ঞান  সংখ্যা  অভিযাত্রী  কাঁটা  চাঁপা',
        font=raqm(V160, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), 'কাঁ  চাঁ  ক্ষ্মাঁ  গাঁ  পাঁ', font=raqm(V160, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), '। , ; : ? ! / — “ ” ‘ ’', font=raqm(V160, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), 'কি কু কৃ কে কৈ কো কৌ কং কঃ কাঁ', font=raqm(V160, 40), fill='#111820', direction='ltr', language='bn')
y += 90
d2.text((30, y), 'Side-by-side paragraph (v0.150 top, v0.160 bottom):', font=lab, fill='#586575')
y += 40
side = ('বাংলা আমার মাতৃভাষা; চাঁদের আলোয় কবিতা লেখা হয়। '
        'ক্ষমা, জ্ঞান আর সংখ্যা — সবই এই বর্ণমালায়।')
pf150, pf160 = raqm(V150, 30), raqm(V160, 30)
for line in textwrap.wrap(side, width=42):
    d2.text((30, y), line, font=pf150, fill='#8a97a3', direction='ltr', language='bn')
    y += 44
for line in textwrap.wrap(side, width=42):
    d2.text((30, y), line, font=pf160, fill='#111820', direction='ltr', language='bn')
    y += 44
im2.save(PREP / 'specimens/v0160-writing-demo.png', optimize=True)
print('saved specimens/v0160-writing-demo.png', im2.size)

# ---------------- (c) close-ups ----------------
MOST = [('ঋ', 'bn_ri', 'widest vowel, w 1.35'),
        ('ৈ', 'bn_aikaar', 'widest mark, w 1.58'),
        ('ং', 'bn_anusvara', 'stray swoosh removed — loop only'),
        ('ো', 'bn_okaar', 'narrow single-stroke form, w 0.52'),
        ('য়', 'bn_yya', 'w 1.45'),
        ('খ', 'bn_kha', 'w 1.42'),
        ('১', 'bn_one', 'w 1.49'),
        ('/', 'slash', 'w 1.75'),
        ('ঃ', 'bn_visarga', 'two ring dots'),
        ('ঙ', 'bn_nga', 'w 1.32'),
        ('ঔ', 'bn_au', 'w 1.08'),
        ('ঞ', 'bn_nya', 'w 1.19')]
SIZE3 = 200
CELL3 = 300
W3 = 4 * CELL3 + 20
H3 = 60 + 3 * (SIZE3 + 70)
im3 = Image.new('RGB', (W3, H3), 'white')
d3 = ImageDraw.Draw(im3)
d3.text((10, 8), 'Pranoti v0.160 — close-ups (v0.150 grey left, v0.160 black right)',
        font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d3.text((10, 32), 'Red = baseline, blue = headline y=1157. 200 px. BASIC layout for marks.',
        font=small_f, fill='#586575')
f150b, f160b = basic(V150, SIZE3), basic(V160, SIZE3)
sc3 = SIZE3 / UPM
for idx, (ch, name, note) in enumerate(MOST):
    col, row = idx % 4, idx // 4
    x0 = 10 + col * CELL3
    y_base = 60 + row * (SIZE3 + 70) + SIZE3 + 10
    y_head = y_base - round(HEADLINE * sc3)
    d3.line([(x0, y_head), (x0 + CELL3 - 12, y_head)], fill='#3b82f6', width=1)
    d3.line([(x0, y_base), (x0 + CELL3 - 12, y_base)], fill='#e11d48', width=1)
    d3.text((x0 + 30, y_base), ch, font=f150b, fill='#8a97a3', anchor='ls')
    d3.text((x0 + 160, y_base), ch, font=f160b, fill='#111820', anchor='ls')
    d3.text((x0 + 2, y_base + 18), f'{name} — {note}', font=small_f, fill='#586575')
im3.save(PREP / 'specimens/closeup-v0.160.png', optimize=True)
print('saved specimens/closeup-v0.160.png', im3.size)

# ---------------- (d) chosen vowel cells ----------------
sel = json.load(open(PREP / 'vowel_selection.json', encoding='utf-8'))
CELL4 = 200
W4 = 4 * CELL4 + 20
H4 = 60 + 3 * (CELL4 + 30)
im4 = Image.new('L', (W4, H4), 255)
d4 = ImageDraw.Draw(im4)
d4.text((10, 8), 'Pranoti v0.160 — the 11 vowel cells actually traced (best-of-7 x 4 photos)',
        font=ImageFont.truetype(DEJA, 16), fill=0)
d4.text((10, 32), 'Chosen by ink area / aspect / stroke width vs the row median; all 28 instances per vowel were near-identical.',
        font=small_f, fill=80)
for idx, (gname, s) in enumerate(sel.items()):
    col, row = idx % 4, idx // 4
    x0 = 10 + col * CELL4
    y0 = 60 + row * (CELL4 + 30)
    cell = Image.open(s['file']).convert('L')
    cell.thumbnail((CELL4 - 10, CELL4 - 30))
    im4.paste(cell, (x0, y0 + 24))
    d4.text((x0 + 2, y0 + 2), f"{traced[gname]['char']} {gname} — {s['photo'][:10]} r{s['row']}c{s['col']}", font=small_f, fill=0)
im4.save(PREP / 'specimens/chosen-vowels-v0.160.png', optimize=True)
print('saved specimens/chosen-vowels-v0.160.png', im4.size)
