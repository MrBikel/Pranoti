#!/usr/bin/env python3
"""Test Khanda_Ta (ৎ) in many contexts, v0.166 vs v0.120, at 3 sizes.
Find where it breaks or collides before fixing its placement."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
V166 = str(BASE / 'v0166-prep/Pranoti-Regular-v0.166-beta.ttf')
V120 = str(BASE / 'github-repo/Pranoti-Regular-v0.120-Private-Owner-Review.ttf')
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
PREP = BASE / 'v0167-prep'

WORDS = ['হঠাৎ', 'সৎ', 'উৎপাত', 'উৎসাহ', 'মৎস্য', 'উৎস', 'বিৎ']
SIZES = [24, 40, 72]

def raqm(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)

lab = ImageFont.truetype(DEJA, 14)
small = ImageFont.truetype(DEJA, 11)
W = 1100
H = 60 + len(WORDS) * (len(SIZES) * 2 * 96 + 30)
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), 'Khanda_Ta test — v0.120 (grey, left) vs v0.166 (black, right), 3 sizes',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
d.text((10, 32), 'Where does ৎ collide, clip or detach? Check the tail vs the following/preceding glyph.',
       font=small, fill='#586575')
y = 60
for w in WORDS:
    d.text((10, y), w, font=lab, fill='#17202a')
    y += 26
    for size in SIZES:
        for band, (path, colr) in enumerate(((V120, '#8a97a3'), (V166, '#111820'))):
            yy = y + band * 96
            d.text((10, yy + 70), f'{size}px', font=small, fill='#586575')
            d.text((80, yy + 88), w, font=raqm(path, size), fill=colr,
                   anchor='ls', direction='ltr', language='bn')
            # baseline guide
            d.line([(80, yy + 88), (620, yy + 88)], fill='#e11d48', width=1)
        y += 2 * 96
    y += 8
im = im.crop((0, 0, W, y))
im.save(PREP / 'specimens/khanda-ta-test.png', optimize=True)
print('saved', PREP / 'specimens/khanda-ta-test.png', im.size)

# invitation line with উৎসাহ, both fonts, 2 sizes
im2 = Image.new('RGB', (W, 420), 'white')
d2 = ImageDraw.Draw(im2)
d2.text((10, 8), 'Invitation line (উৎসাহ ব্যঞ্জক) — v0.120 grey vs v0.166 black',
        font=ImageFont.truetype(DEJA, 16), fill='#17202a')
line = 'উক্ত অনুষ্ঠানে আপনার উপস্থিতি আমাদের জন্য অত্যন্ত উৎসাহ ব্যঞ্জক হবে।'
y = 70
for size in (34, 56):
    for band, (path, colr) in enumerate(((V120, '#8a97a3'), (V166, '#111820'))):
        yy = y + band * 90
        d2.text((10, yy + 60), f'{size}px', font=small, fill='#586575')
        d2.text((80, yy + 78), line, font=raqm(path, size), fill=colr,
                anchor='ls', direction='ltr', language='bn')
    y += 2 * 90
im2 = im2.crop((0, 0, W, y))
im2.save(PREP / 'specimens/khanda-ta-invitation-test.png', optimize=True)
print('saved', PREP / 'specimens/khanda-ta-invitation-test.png', im2.size)
