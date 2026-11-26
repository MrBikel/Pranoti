#!/usr/bin/env python3
"""Render the Peace School & College invitation sentences in Pranoti v0.162.

The user sent a photo of the printed invitation (file 38) and asked for a
sample: the same sentences set in his handwriting font. RAQM shaping via
PIL, same approach as render_specimens_v0160.py. Also a real connected-text
test: the invitation exercises ~20 conjuncts (most still base-font
ligatures in v0.160), listed in the footer.
"""
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PREP = Path('/home/hatch/workspace/fonts/bengali-hand/v0162-prep')
V162 = str(PREP / 'Pranoti-Regular-v0.162-beta.ttf')
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)

BODY = ('মুহতারাম, আসসালামু আলাইকুম ওয়া রহমাতুল্লাহ। আপনি জেনে আনন্দিত হবেন যে, '
        'প্রথমবারের মতো পীস স্কুল অ্যান্ড কলেজ, বগুড়া শাখার উদ্যোগে আগামী '
        '২১ মে, ২০২৬ বৃহস্পতিবার \u2018প্রতীকী হজ্ব শিক্ষা প্রদর্শনী\u2019র '
        'আয়োজন করা হয়েছে। উক্ত অনুষ্ঠানে আপনার উপস্থিতি আমাদের জন্য অত্যন্ত '
        'উৎসাহ ব্যঞ্জক হবে এবং আমাদের শিক্ষার্থীদের অনুপ্রাণিত করবে।')
VENUE = ['স্থান : টিটু মিলনায়তন।',
         'তারিখ : ২১ মে, ২০২৬ বৃহস্পতিবার।',
         'সময় : বিকেল ৩:০০ ঘটিকা।']
SIGN = ['ধন্যবাদান্তে,',
        'ড. ফাহমিদা সুলতানা',
        'অধ্যক্ষ',
        'পীস স্কুল অ্যান্ড কলেজ, বগুড়া',
        'জান-ই-সাফা কমপ্লেক্স, জামিলনগর',
        'বগুড়া।']

W = 1100
im = Image.new('RGB', (W, 2200), 'white')
d = ImageDraw.Draw(im)
lab = ImageFont.truetype(DEJA, 15)
small = ImageFont.truetype(DEJA, 13)
d.text((30, 16), 'Pranoti v0.162-beta — invitation sentences (Peace School & College, Bogura)',
       font=ImageFont.truetype(DEJA, 18), fill='#17202a')
d.text((30, 44), 'The same sentences from the printed invitation, set in your handwriting font.',
       font=lab, fill='#586575')
y = 110
bf = raqm(V162, 34)
# greeting on its own line, as in the original
d.text((30, y), 'মুহতারাম,', font=bf, fill='#111820', direction='ltr', language='bn')
y += 56
para = BODY.split('মুহতারাম, ', 1)[1]
for line in textwrap.wrap(para, width=36):
    d.text((30, y), line, font=bf, fill='#111820', direction='ltr', language='bn')
    y += 52
y += 24
for line in VENUE:
    d.text((30, y), line, font=bf, fill='#111820', direction='ltr', language='bn')
    y += 52
y += 24
for line in SIGN:
    d.text((W - 30, y), line, font=bf, fill='#111820', direction='ltr',
           language='bn', anchor='ra')
    y += 52
y += 24
d.text((30, y), 'Conjuncts exercised in this text (set in Pranoti below):', font=small, fill='#586575')
y += 26
d.text((30, y), 'প্র ক্ষ র্শ ষ্ঠ স্থ ৎস ব্য ঞ্জ র্থ ণ্ত হ্প স্প ন্য ব্দ ল্ত ধ্য ম্প প্ল ক্স স্ফ জ্ব ড়',
       font=raqm(V162, 30), fill='#111820', direction='ltr', language='bn')
y += 48
d.text((30, y), 'Most of these ligatures are still base-font shapes in v0.162 — they are the v0.170 replacement list.',
       font=small, fill='#586575')
y += 40
im = im.crop((0, 0, W, y))
out = PREP / 'specimens/invitation-v0.162.png'
im.save(out, optimize=True)
print('saved', out, im.size)
