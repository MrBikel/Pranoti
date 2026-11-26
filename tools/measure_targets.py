#!/usr/bin/env python3
"""v0.160 target boxes: true ink bboxes of the v0.150 glyphs that the new
traces must be fitted to.

- 56 letters: target = size-transforms.json 'ink_after' (authoritative,
  measured the same way as the v0.150 build).
- 13 signs + 14 punctuation: no size-transform entry (they were not
  resized in v0.150); target = the v0.150 glyph's own ink box, measured
  here by rasterising the outline with PIL/FreeType at 1536px (1 unit =
  1 px), BASIC layout (no shaping, so no dotted circle on marks).
  Calibration: bn_a measures (-36, 8, 1257, 1157) vs ink_after
  (-38, 9, 1254, 1157) — within 3 units (pixel rounding).
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
V150 = '/home/hatch/workspace/fonts/bengali-hand/github-repo/Pranoti-Regular-v0.150-beta.ttf'

SIGNS = {'bn_candrabindu': 0x0981, 'bn_anusvara': 0x0982, 'bn_visarga': 0x0983,
         'bn_aakaar': 0x09BE, 'bn_ikaar': 0x09BF, 'bn_iikaar': 0x09C0,
         'bn_ukaar': 0x09C1, 'bn_uukaar': 0x09C2, 'bn_rikaar': 0x09C3,
         'bn_ekaar': 0x09C7, 'bn_aikaar': 0x09C8, 'bn_okaar': 0x09CB,
         'bn_aukaar': 0x09CC}
PUNCT = {'danda': 0x0964, 'period': 0x002E, 'comma': 0x002C,
         'semicolon': 0x003B, 'colon': 0x003A, 'hyphen': 0x002D,
         'emdash': 0x2014, 'slash': 0x002F, 'quoteleft': 0x2018,
         'quoteright': 0x2019, 'quotedblleft': 0x201C,
         'quotedblright': 0x201D, 'question': 0x003F, 'exclam': 0x0021}

# glyphs whose advance is 0 / marks with no width: their ink box is still
# measured the same way; the fit centres on the box, not the advance.


def measure_ink(path, cp):
    font = TTFont(path)
    asc = font['hhea'].ascent
    adv = font['hmtx'][font.getBestCmap()[cp]][0]
    f = ImageFont.truetype(path, 1536, layout_engine=ImageFont.Layout.BASIC)
    img = Image.new('L', (3200, 3200), 0)
    d = ImageDraw.Draw(img)
    x0, base = 1200, 1900  # wide margins: marks extend far left/up of origin
    d.text((x0, base - asc), chr(cp), font=f, fill=255)
    bb = img.getbbox()
    if bb is None:
        return None
    return [bb[0] - x0, base - bb[3], bb[2] - x0, base - bb[1]], adv


def main():
    st = json.load(open('/home/hatch/workspace/fonts/bengali-hand/v0150-prep/size-transforms.json'))
    targets = {}
    for row in st:
        targets[row['glyph']] = dict(ch=row['ch'], adv=row['adv'],
                                     ink_after=row['ink_after'],
                                     kind='letter')
    for name, cp in {**SIGNS, **PUNCT}.items():
        box, adv = measure_ink(V150, cp)
        kind = 'sign' if name in SIGNS else 'punct'
        targets[name] = dict(ch=chr(cp), cp=cp, adv=adv, ink_after=box,
                             kind=kind)
        print(f'{name:16s} {chr(cp)} adv={adv:5d} ink={box}')
    json.dump(targets, open(ROOT / 'targets.json', 'w'), ensure_ascii=False, indent=1)
    print('targets:', len(targets), '-> targets.json')


if __name__ == '__main__':
    main()
