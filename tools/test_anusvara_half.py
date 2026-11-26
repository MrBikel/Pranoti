#!/usr/bin/env python3
"""Test: bn_anusvara at half delta (-7) instead of -15.
The -15 thin created a degenerate kink (two non-adjacent points at distance
0.00 in contour 0), tripping FontForge validate 0x4. Try -7.
Run: fontforge -lang=py tools/test_anusvara_half.py
"""
import fontforge
from pathlib import Path

PREP160 = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
PREP161 = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
BASE = str(PREP160 / 'Pranoti-Regular-v0.160-beta.ttf')

f = fontforge.open(BASE)
g = f['bn_anusvara']
print('before: validate', g.validate(), 'bbox', g.boundingBox())
g.changeWeight(-7)
g.addExtrema()
g.correctDirection()
print('after -7: validate', g.validate(), 'bbox', g.boundingBox())
f.generate(str(PREP161 / 'tmp-test-anusvara-minus7.ttf'))
f.close()
print('done')
