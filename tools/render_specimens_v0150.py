#!/usr/bin/env python3
"""Render v0.150 visual specimens (and LOOK at them).

(a) before-after-v0.150.png: all 56 core letters, v0.140 row over v0.150
    row, with TRUE baseline (red) and headline y=1157 (blue) guides.
(b) v0150-writing-demo.png: headline + paragraph + alphabet + digits.
(c) closeup-v0.150.png: the most-resized glyphs at large size + 64 px row.
"""
from PIL import Image, ImageDraw, ImageFont

V140 = '/home/hatch/workspace/fonts/bengali-hand/github-repo/Pranoti-Regular-v0.140-beta.ttf'
V150 = '/home/hatch/workspace/fonts/bengali-hand/v0150-prep/Pranoti-Regular-v0.150-beta.ttf'
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
UPM = 1536
HEADLINE = 1157

LETTERS = [('অ','bn_a'),('আ','bn_aa'),('ই','bn_i'),('ঈ','bn_ii'),('উ','bn_u'),('ঊ','bn_uu'),
 ('ঋ','bn_ri'),('এ','bn_e'),('ঐ','bn_ai'),('ও','bn_o'),('ঔ','bn_au'),
 ('ক','bn_ka'),('খ','bn_kha'),('গ','bn_ga'),('ঘ','bn_gha'),('ঙ','bn_nga'),
 ('চ','bn_ca'),('ছ','bn_cha'),('জ','bn_ja'),('ঝ','bn_jha'),('ঞ','bn_nya'),
 ('ট','bn_tta'),('ঠ','bn_ttha'),('ড','bn_dda'),('ঢ','bn_ddha'),('ণ','bn_nna'),
 ('ত','bn_ta'),('থ','bn_tha'),('দ','bn_da'),('ধ','bn_dha'),('ন','bn_na'),
 ('প','bn_pa'),('ফ','bn_pha'),('ব','bn_ba'),('ভ','bn_bha'),('ম','bn_ma'),
 ('য','bn_ya'),('র','bn_ra'),('ল','bn_la'),('শ','bn_sha'),('ষ','bn_ssa'),
 ('স','bn_sa'),('হ','bn_ha'),('ড়','bn_rra'),('ঢ়','bn_rha'),('য়','bn_yya'),
 ('০','bn_zero'),('১','bn_one'),('২','bn_two'),('৩','bn_three'),('৪','bn_four'),
 ('৫','bn_five'),('৬','bn_six'),('৭','bn_seven'),('৮','bn_eight'),('৯','bn_nine')]

def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)

# ---------------- (a) before/after grid ----------------
SIZE = 110
CELL = 190
COLS = 7
ROWS = (len(LETTERS) + COLS - 1) // COLS
label_f = ImageFont.truetype(DEJA, 13)
small_f = ImageFont.truetype(DEJA, 11)
W = COLS * CELL + 20
H = 60 + ROWS * 2 * (SIZE + 46)
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), 'Pranoti v0.140 (top, grey) vs v0.150 (bottom, black) — all 56 core letters',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d.text((10, 32), 'Red = baseline (y=0). Blue = headline (y=1157). Anchored on the true baseline.',
       font=small_f, fill='#586575')
f140, f150 = raqm(V140, SIZE), raqm(V150, SIZE)
sc = SIZE / UPM
for idx, (ch, name) in enumerate(LETTERS):
    col, row = idx % COLS, idx // COLS
    x0 = 10 + col * CELL
    for band, fnt, colr in ((0, f140, '#8a97a3'), (1, f150, '#111820')):
        y_base = 60 + row * 2 * (SIZE + 46) + band * (SIZE + 46) + SIZE + 18
        y_head = y_base - round(HEADLINE * sc)
        d.line([(x0, y_head), (x0 + CELL - 12, y_head)], fill='#3b82f6', width=1)
        d.line([(x0, y_base), (x0 + CELL - 12, y_base)], fill='#e11d48', width=1)
        d.text((x0 + 8, y_base + 2), ch, font=fnt, fill=colr, anchor='ls', direction='ltr', language='bn')
        if band == 1:
            d.text((x0 + 2, y_base + 18), name, font=small_f, fill='#586575')
im.save('specimens/before-after-v0.150.png', optimize=True)
print('saved specimens/before-after-v0.150.png', im.size)

# ---------------- (b) writing demo ----------------
W2, H2 = 1100, 1250
im2 = Image.new('RGB', (W2, H2), 'white')
d2 = ImageDraw.Draw(im2)
lab = ImageFont.truetype(DEJA, 15)
d2.text((30, 16), 'Pranoti v0.150-beta — writing demo', font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d2.text((30, 44), 'Headline, paragraph, alphabet and digits. Check: even rhythm, no collisions, nothing floats or sinks.',
        font=lab, fill='#586575')
y = 110
d2.text((30, y), 'অভিযাত্রী', font=raqm(V150, 84), fill='#111820', direction='ltr', language='bn')
y += 130
import textwrap
para = ('অভিযাত্রী সাহিত্য পত্রিকার নতুন সংখ্যায় চাঁদের আলোয় লেখা কবিতা, '
        'ক্ষমা ও জ্ঞানের গল্প, আর সংখ্যা ১২৩৪৫৬৭৮৯০ ছাপা হয়েছে। '
        'বাংলা ভাষার সৌন্দর্য প্রতিটি বর্ণে ফুটে ওঠে যখন সব বর্ণ একই '
        'আকারে সাজানো থাকে।')
pf = raqm(V150, 30)
for line in textwrap.wrap(para, width=42):
    d2.text((30, y), line, font=pf, fill='#111820', direction='ltr', language='bn')
    y += 44
d2.text((30, y), 'অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ', font=raqm(V150, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), 'ক খ গ ঘ ঙ চ ছ জ ঝ ঞ ট ঠ ড ঢ ণ ত থ দ ধ ন প ফ ব ভ ম য র ল শ ষ স হ ড় ঢ় য়',
        font=raqm(V150, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), '০ ১ ২ ৩ ৪ ৫ ৬ ৭ ৮ ৯', font=raqm(V150, 40), fill='#111820', direction='ltr', language='bn')
y += 90
d2.text((30, y), 'চাঁদ  ক্ষমা  জ্ঞান  সংখ্যা  অভিযাত্রী  কাঁটা  চাঁপা',
        font=raqm(V150, 40), fill='#111820', direction='ltr', language='bn')
y += 70
d2.text((30, y), 'কাঁ  চাঁ  ক্ষ্মাঁ  গাঁ  পাঁ', font=raqm(V150, 40), fill='#111820', direction='ltr', language='bn')
im2.save('specimens/v0150-writing-demo.png', optimize=True)
print('saved specimens/v0150-writing-demo.png', im2.size)

# ---------------- (c) close-ups of the most-changed glyphs ----------------
MOST = [('ত','bn_ta','s 1.062, lightest'),('ভ','bn_bha','s 1.037'),('ক','bn_ka','s 1.037'),
        ('ও','bn_o','s 1.036'),('ঙ','bn_nga','s 1.033'),('০','bn_zero','s 1.033'),
        ('গ','bn_ga','s 0.971, heaviest'),('ধ','bn_dha','s 0.970'),('ল','bn_la','s 0.970'),
        ('ঞ','bn_nya','2 hairline contours deleted'),('ঠ','bn_ttha','loop bottom'),
        ('ঔ','bn_au','s 1.028')]
SIZE3 = 200
CELL3 = 300
W3 = 4 * CELL3 + 20
H3 = 60 + 3 * (SIZE3 + 70)
im3 = Image.new('RGB', (W3, H3), 'white')
d3 = ImageDraw.Draw(im3)
d3.text((10, 8), 'Pranoti v0.150 — close-ups of the most-changed glyphs (v0.140 grey left, v0.150 black right)',
        font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d3.text((10, 32), 'Red = baseline, blue = headline y=1157. 200 px, plus a 64 px row at the bottom of each cell.',
        font=small_f, fill='#586575')
f140b, f150b = raqm(V140, SIZE3), raqm(V150, SIZE3)
f140s, f150s = raqm(V140, 64), raqm(V150, 64)
sc3 = SIZE3 / UPM
for idx, (ch, name, note) in enumerate(MOST):
    col, row = idx % 4, idx // 4
    x0 = 10 + col * CELL3
    y_base = 60 + row * (SIZE3 + 70) + SIZE3 + 10
    y_head = y_base - round(HEADLINE * sc3)
    d3.line([(x0, y_head), (x0 + CELL3 - 12, y_head)], fill='#3b82f6', width=1)
    d3.line([(x0, y_base), (x0 + CELL3 - 12, y_base)], fill='#e11d48', width=1)
    d3.text((x0 + 6, y_base), ch, font=f140b, fill='#b9c2cb', anchor='ls', direction='ltr', language='bn')
    d3.text((x0 + 6, y_base), ch, font=f150b, fill='#111820', anchor='ls', direction='ltr', language='bn')
    d3.text((x0 + 2, y_base + 16), f'{ch} {name} — {note}', font=small_f, fill='#586575')
    d3.text((x0 + 6, y_base + 44), ch, font=f140s, fill='#b9c2cb', anchor='ls', direction='ltr', language='bn')
    d3.text((x0 + 90, y_base + 44), ch, font=f150s, fill='#111820', anchor='ls', direction='ltr', language='bn')
im3.save('specimens/closeup-v0.150.png', optimize=True)
print('saved specimens/closeup-v0.150.png', im3.size)
