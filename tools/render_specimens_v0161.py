#!/usr/bin/env python3
"""Render v0.161 visual specimens (and LOOK at them).

(a) before-after-v0.161.png: the 17 adjusted glyphs, v0.160 row over
    v0.161 row, with TRUE baseline (red) and headline y=1157 (blue) guides.
    BASIC layout (no shaping) so the marks render alone at their font origin.
(b) v0161-writing-demo.png: headline + paragraph + alphabet + digits +
    punctuation, v0.161 (RAQM); plus a side-by-side paragraph v0.160/v0.161.
(c) closeup-v0.161.png: the most-changed glyphs at 200 px (pass-2 four first).
(d) stroke-widths-before-after-v0.161.png: v0.160 vs v0.161 median stroke
    width for the 17 adjusted glyphs, with the 84.5 target line.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

PREP = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
PREP160 = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
V160 = str(PREP160 / 'Pranoti-Regular-v0.160-beta.ttf')
V161 = str(PREP / 'Pranoti-Regular-v0.161-beta.ttf')
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
UPM = 1536
HEADLINE = 1157

traced = json.load(open(PREP160 / 'traced_glyphs.json', encoding='utf-8'))
ADJUSTED = ['bn_ai', 'bn_i', 'bn_e', 'bn_yya', 'bn_one', 'bn_six', 'bn_au',
            'bn_kha', 'bn_ga', 'bn_ya', 'bn_aikaar', 'bn_ikaar',
            'bn_tta', 'bn_cha', 'bn_pa', 'bn_okaar', 'bn_uukaar']
GLYPHS = [(traced[n]['char'], n) for n in ADJUSTED]


def basic(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)


def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


label_f = ImageFont.truetype(DEJA, 13)
small_f = ImageFont.truetype(DEJA, 11)

# ---------------- (a) before/after grid ----------------
SIZE = 110
CELL = 190
COLS = 6
ROWS = (len(GLYPHS) + COLS - 1) // COLS
W = COLS * CELL + 20
H = 60 + ROWS * 2 * (SIZE + 46) + 70  # +70: the last row's deep descenders (bn_uukaar to -498) need room
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), 'Pranoti v0.160 (top, grey) vs v0.161 (bottom, black) — all 17 weight-adjusted glyphs',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d.text((10, 32), 'Red = baseline (y=0). Blue = headline (y=1157). BASIC layout: marks shown alone at their font origin.',
       font=small_f, fill='#586575')
f160, f161 = basic(V160, SIZE), basic(V161, SIZE)
sc = SIZE / UPM
for idx, (ch, name) in enumerate(GLYPHS):
    col, row = idx % COLS, idx // COLS
    x0 = 10 + col * CELL
    for band, fnt, colr in ((0, f160, '#8a97a3'), (1, f161, '#111820')):
        y_base = 60 + row * 2 * (SIZE + 46) + band * (SIZE + 46) + SIZE + 18
        y_head = y_base - round(HEADLINE * sc)
        d.line([(x0, y_head), (x0 + CELL - 12, y_head)], fill='#3b82f6', width=1)
        d.line([(x0, y_base), (x0 + CELL - 12, y_base)], fill='#e11d48', width=1)
        d.text((x0 + 60, y_base), ch, font=fnt, fill=colr, anchor='ls')
        if band == 1:
            d.text((x0 + 2, y_base + 18), name, font=small_f, fill='#586575')
im.save(PREP / 'specimens/before-after-v0.161.png', optimize=True)
print('saved specimens/before-after-v0.161.png', im.size)

# ---------------- (b) writing demo ----------------
W2, H2 = 1100, 1500
im2 = Image.new('RGB', (W2, H2), 'white')
d2 = ImageDraw.Draw(im2)
lab = ImageFont.truetype(DEJA, 15)
d2.text((30, 16), 'Pranoti v0.161-beta — writing demo', font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d2.text((30, 44), 'Headline, paragraph, alphabet, digits and punctuation. Check: even rhythm, no collisions, nothing floats or sinks.',
        font=lab, fill='#586575')
y = 110
d2.text((30, y), 'অভিযাত্রী', font=raqm(V161, 84), fill='#111820', direction='ltr', language='bn')
y += 130
import textwrap
para = ('অভিযাত্রী সাহিত্য পত্রিকার নতুন সংখ্যায় চাঁদের আলোয় লেখা কবিতা, '
        'ক্ষমা ও জ্ঞানের গল্প, আর সংখ্যা ১২৩৪৫৬৭৮৯০ ছাপা হয়েছে। '
        'বাংলা ভাষার সৌন্দর্য প্রতিটি বর্ণে ফুটে ওঠে যখন সব বর্ণ একই '
        'আকারে সাজানো থাকে।')
pf = raqm(V161, 30)
for line in textwrap.wrap(para, width=42):
    d2.text((30, y), line, font=pf, fill='#111820', direction='ltr', language='bn')
    y += 44
y += 10
d2.text((30, y), 'অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ', font=raqm(V161, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), 'ক খ গ ঘ ঙ চ ছ জ ঝ ঞ ট ঠ ড ঢ ণ ত থ দ ধ ন প ফ ব ভ ম য র ল শ ষ স হ ড় ঢ় য়',
        font=raqm(V161, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), '০ ১ ২ ৩ ৪ ৫ ৬ ৭ ৮ ৯', font=raqm(V161, 40), fill='#111820', direction='ltr', language='bn')
y += 90
d2.text((30, y), 'চাঁদ  ক্ষমা  জ্ঞান  সংখ্যা  অভিযাত্রী  কাঁটা  চাঁপা',
        font=raqm(V161, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), 'কাঁ  চাঁ  ক্ষ্মাঁ  গাঁ  পাঁ', font=raqm(V161, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), '। , ; : ? ! / — “ ” ‘ ’', font=raqm(V161, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), 'কি কু কৃ কে কৈ কো কৌ কং কঃ কাঁ', font=raqm(V161, 40), fill='#111820', direction='ltr', language='bn')
y += 90
d2.text((30, y), 'Side-by-side paragraph (v0.160 top, v0.161 bottom):', font=lab, fill='#586575')
y += 40
side = ('বাংলা আমার মাতৃভাষা; চাঁদের আলোয় কবিতা লেখা হয়। '
        'ক্ষমা, জ্ঞান আর সংখ্যা — সবই এই বর্ণমালায়।')
pf160, pf161 = raqm(V160, 30), raqm(V161, 30)
for line in textwrap.wrap(side, width=42):
    d2.text((30, y), line, font=pf160, fill='#8a97a3', direction='ltr', language='bn')
    y += 44
for line in textwrap.wrap(side, width=42):
    d2.text((30, y), line, font=pf161, fill='#111820', direction='ltr', language='bn')
    y += 44
im2.save(PREP / 'specimens/v0161-writing-demo.png', optimize=True)
print('saved specimens/v0161-writing-demo.png', im2.size)

# ---------------- (c) close-ups ----------------
MOST = [('ঐ', 'bn_ai', 'thinned -32 total (pass 1+2)'),
        ('ই', 'bn_i', 'thinned -32 total (pass 1+2)'),
        ('এ', 'bn_e', 'thinned -32 total (pass 1+2)'),
        ('য়', 'bn_yya', 'thinned -32 total (pass 1+2)'),
        ('ছ', 'bn_cha', 'thickened +15'),
        ('প', 'bn_pa', 'thickened +15'),
        ('ো', 'bn_okaar', 'thickened +16'),
        ('ূ', 'bn_uukaar', 'thickened +16')]
SIZE3 = 200
CELL3 = 300
W3 = 4 * CELL3 + 20
H3 = 60 + 2 * 2 * (SIZE3 + 46) + 70  # 2 glyph rows x 2 bands (grey top, black bottom)
im3 = Image.new('RGB', (W3, H3), 'white')
d3 = ImageDraw.Draw(im3)
d3.text((10, 8), 'Pranoti v0.161 — close-ups (v0.160 grey top, v0.161 black bottom)',
        font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d3.text((10, 32), 'Red = baseline, blue = headline y=1157. 200 px. BASIC layout for marks. Check counters stay open.',
        font=small_f, fill='#586575')
f160b, f161b = basic(V160, SIZE3), basic(V161, SIZE3)
sc3 = SIZE3 / UPM
for idx, (ch, name, note) in enumerate(MOST):
    col, row = idx % 4, idx // 4
    x0 = 10 + col * CELL3
    for band, fnt, colr in ((0, f160b, '#8a97a3'), (1, f161b, '#111820')):
        y_base = 60 + row * 2 * (SIZE3 + 46) + band * (SIZE3 + 46) + SIZE3 + 18
        y_head = y_base - round(HEADLINE * sc3)
        d3.line([(x0, y_head), (x0 + CELL3 - 12, y_head)], fill='#3b82f6', width=1)
        d3.line([(x0, y_base), (x0 + CELL3 - 12, y_base)], fill='#e11d48', width=1)
        d3.text((x0 + 60, y_base), ch, font=fnt, fill=colr, anchor='ls')
        if band == 1:
            d3.text((x0 + 2, y_base + 18), f'{name} — {note}', font=small_f, fill='#586575')
im3.save(PREP / 'specimens/closeup-v0.161.png', optimize=True)
print('saved specimens/closeup-v0.161.png', im3.size)

# ---------------- (d) stroke-width before/after chart ----------------
fm.fontManager.addfont(V161)
PRANOTI = fm.FontProperties(family='Pranoti')
old = json.load(open(PREP160 / 'weight/stroke-widths-v0.160.json', encoding='utf-8'))
new = json.load(open(PREP / 'weight/stroke-widths-v0.161.json', encoding='utf-8'))
oldm = {r['name']: r['median'] for r in old['rows']}
newm = {r['name']: r['median'] for r in new['rows']}
names = ADJUSTED
chars = [traced[n]['char'] for n in names]
x = range(len(names))
fig, ax = plt.subplots(figsize=(11, 6))
w = 0.38
ax.bar([i - w / 2 for i in x], [oldm[n] for n in names], width=w, color='#8a97a3', label='v0.160')
ax.bar([i + w / 2 for i in x], [newm[n] for n in names], width=w, color='#111820', label='v0.161')
ax.set_xticks(list(x))
ax.set_xticklabels(chars, fontproperties=PRANOTI, fontsize=13)
ax.axhline(84.5, color='#111820', lw=1.2, label='target 84.5')
ax.axhspan(84.5 * 0.85, 84.5 * 1.15, color='#2ecc71', alpha=0.12, label='±15% band')
ax.set_ylabel('Median stroke width (font units, UPM 1536)')
ax.set_title('Pranoti v0.161-beta — stroke width before/after (17 adjusted glyphs)')
ax.legend(loc='upper right', fontsize=10)
ax.set_ylim(50, 130)
for i, n in enumerate(names):
    ax.text(i - w / 2, oldm[n] + 2, f'{oldm[n]:.0f}', ha='center', fontsize=8, color='#555555')
    ax.text(i + w / 2, newm[n] + 2, f'{newm[n]:.0f}', ha='center', fontsize=8, color='#111820')
plt.tight_layout()
out = PREP / 'specimens/stroke-widths-before-after-v0.161.png'
plt.savefig(out, dpi=110)
print('saved', out)
