#!/usr/bin/env python3
"""Render v0.164 consonant specimens (and LOOK at them).

(a) before-after-v0.164.png: all 35 consonants, v0.163 grey (top) vs
    v0.164 black (bottom), with TRUE baseline (red) and headline y=1157
    (blue) guides. BASIC layout so each consonant renders alone at its
    font origin.
(b) v0164-consonant-demo.png: the 35 consonants large, each in a real
    word, sentences using them, and the consonant row side-by-side
    v0.163 (grey) vs v0.164 (black) so the restored tops show.
"""
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
PREP163 = BASE / 'v0163-prep'
PREP = BASE / 'v0164-prep'
V163 = str(PREP163 / 'Pranoti-Regular-v0.163-beta.ttf')
V164 = str(PREP / 'Pranoti-Regular-v0.164-beta.ttf')
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
UPM = 1536
HEADLINE = 1157

CONSONANTS = [('ক', 'bn_ka'), ('খ', 'bn_kha'), ('গ', 'bn_ga'), ('ঘ', 'bn_gha'),
              ('ঙ', 'bn_nga'), ('চ', 'bn_ca'), ('ছ', 'bn_cha'), ('জ', 'bn_ja'),
              ('ঝ', 'bn_jha'), ('ঞ', 'bn_nya'), ('ট', 'bn_tta'), ('ঠ', 'bn_ttha'),
              ('ড', 'bn_dda'), ('ঢ', 'bn_ddha'), ('ণ', 'bn_nna'), ('ত', 'bn_ta'),
              ('থ', 'bn_tha'), ('দ', 'bn_da'), ('ধ', 'bn_dha'), ('ন', 'bn_na'),
              ('প', 'bn_pa'), ('ফ', 'bn_pha'), ('ব', 'bn_ba'), ('ভ', 'bn_bha'),
              ('ম', 'bn_ma'), ('য', 'bn_ya'), ('র', 'bn_ra'), ('ল', 'bn_la'),
              ('শ', 'bn_sha'), ('ষ', 'bn_ssa'), ('স', 'bn_sa'), ('হ', 'bn_ha'),
              (chr(0x09DC), 'bn_rra'), (chr(0x09DD), 'bn_rha'), (chr(0x09DF), 'bn_yya')]
WORDS = [('ক', 'কলম'), ('খ', 'খাতা'), ('গ', 'গাছ'), ('ঘ', 'ঘোড়া'),
         ('ঙ', 'ব্যাঙ'), ('চ', 'চাঁদ'), ('ছ', 'ছাতা'), ('জ', 'জল'),
         ('ঝ', 'ঝড়'), ('ঞ', 'মিঞা'), ('ট', 'টেবিল'), ('ঠ', 'ঠাকুর'),
         ('ড', 'ডাক'), ('ঢ', 'ঢোল'), ('ণ', 'বীণা'), ('ত', 'তাল'),
         ('থ', 'থালা'), ('দ', 'দরজা'), ('ধ', 'ধান'), ('ন', 'নদী'),
         ('প', 'পাখি'), ('ফ', 'ফুল'), ('ব', 'বই'), ('ভ', 'ভাত'),
         ('ম', 'মাছ'), ('য', 'যত্ন'), ('র', 'রাত'), ('ল', 'লতা'),
         ('শ', 'শাপলা'), ('ষ', 'ষড়যন্ত্র'), ('স', 'সূর্য'), ('হ', 'হাত'),
         (chr(0x09DC), 'গাড়ি'), (chr(0x09DD), 'আষাঢ়'), (chr(0x09DF), 'ময়না')]


def basic(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)


def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


label_f = ImageFont.truetype(DEJA, 13)
small_f = ImageFont.truetype(DEJA, 11)

# ---------------- (a) before/after grid ----------------
SIZE = 110
CELL = 230
COLS = 4
ROWS = (len(CONSONANTS) + COLS - 1) // COLS
W = COLS * CELL + 20
H = 60 + ROWS * 2 * (SIZE + 46) + 40
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), 'Pranoti v0.163 (top, grey) vs v0.164 (bottom, black) — all 35 consonants',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d.text((10, 32), 'Red = baseline (y=0). Blue = headline (y=1157). BASIC layout: consonants shown alone at their font origin.',
       font=small_f, fill='#586575')
f163, f164 = basic(V163, SIZE), basic(V164, SIZE)
sc = SIZE / UPM
for idx, (ch, name) in enumerate(CONSONANTS):
    col, row = idx % COLS, idx // COLS
    x0 = 10 + col * CELL
    for band, fnt, colr in ((0, f163, '#8a97a3'), (1, f164, '#111820')):
        y_base = 60 + row * 2 * (SIZE + 46) + band * (SIZE + 46) + SIZE + 18
        y_head = y_base - round(HEADLINE * sc)
        d.line([(x0, y_head), (x0 + CELL - 12, y_head)], fill='#3b82f6', width=1)
        d.line([(x0, y_base), (x0 + CELL - 12, y_base)], fill='#e11d48', width=1)
        d.text((x0 + 40, y_base), ch, font=fnt, fill=colr, anchor='ls')
        if band == 1:
            d.text((x0 + 2, y_base + 18), name, font=small_f, fill='#586575')
im.save(PREP / 'specimens/before-after-v0.164.png', optimize=True)
print('saved specimens/before-after-v0.164.png', im.size)

# ---------------- (b) vowel demo ----------------
W2, H2 = 1100, 2600
im2 = Image.new('RGB', (W2, H2), 'white')
d2 = ImageDraw.Draw(im2)
lab = ImageFont.truetype(DEJA, 15)
d2.text((30, 16), 'Pranoti v0.164-beta — consonant fine-tuning demo', font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d2.text((30, 44), 'The 35 consonants, each in a word, sentences using them, and the consonant row v0.163 vs v0.164.',
        font=lab, fill='#586575')
y = 110
row_all = 'ক খ গ ঘ ঙ চ ছ জ ঝ ঞ ট ঠ ড ঢ ণ ত থ দ ধ ন প ফ ব ভ ম য র ল শ ষ স হ ' + chr(0x09DC) + ' ' + chr(0x09DD) + ' ' + chr(0x09DF)
row_parts = row_all.split(' ')
d2.text((30, y), ' '.join(row_parts[:18]), font=raqm(V164, 56), fill='#111820', direction='ltr', language='bn')
y += 80
d2.text((30, y), ' '.join(row_parts[18:]), font=raqm(V164, 56), fill='#111820', direction='ltr', language='bn')
y += 110
for ch, word in WORDS:
    d2.text((30, y), f'{ch} — {word}', font=raqm(V164, 30), fill='#111820', direction='ltr', language='bn')
    y += 46
y += 10
pf = raqm(V164, 30)
sentences = ['খোকা খাতা নিয়ে ঘরে বসে গান শুনছে। চাঁদ উঠেছে, ঝড় থেমেছে।',
             'গাড়ি ছুটছে, নদীর পাড়ে মাছ ধরছে জেলেরা। ধান ক্ষেতে সূর্য উঠেছে।',
             'আষাঢ় মাসে ময়না পাখি ডাকছে, শাপলা ফুটেছে পুকুরে।']
for s in sentences:
    for line in textwrap.wrap(s, width=42):
        d2.text((30, y), line, font=pf, fill='#111820', direction='ltr', language='bn')
        y += 44
y += 10
d2.text((30, y), 'Consonant row, v0.163 (grey) vs v0.164 (black) — the three restored tops (kha, ga, yya) sit higher in black:',
        font=lab, fill='#586575')
y += 40
row = 'ক খ গ ঘ ঙ চ ছ জ ঝ ঞ ট ঠ ড ঢ ণ ত থ দ ধ ন প ফ ব ভ ম য র ল শ ষ স হ ' + chr(0x09DC) + ' ' + chr(0x09DD) + ' ' + chr(0x09DF)
rp = row.split(' ')
d2.text((30, y), ' '.join(rp[:18]), font=raqm(V163, 44), fill='#8a97a3', direction='ltr', language='bn')
y += 64
d2.text((30, y), ' '.join(rp[18:]), font=raqm(V163, 44), fill='#8a97a3', direction='ltr', language='bn')
y += 64
d2.text((30, y), ' '.join(rp[:18]), font=raqm(V164, 44), fill='#111820', direction='ltr', language='bn')
y += 64
d2.text((30, y), ' '.join(rp[18:]), font=raqm(V164, 44), fill='#111820', direction='ltr', language='bn')
y += 80
im2 = im2.crop((0, 0, W2, y))
im2.save(PREP / 'specimens/v0164-consonant-demo.png', optimize=True)
print('saved specimens/v0164-consonant-demo.png', im2.size)
