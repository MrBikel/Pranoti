#!/usr/bin/env python3
"""Test: does a HALF-delta thin (-8) on bn_ai still flip contour direction?
Also tests the repair: changeWeight(-16) + correctDirection().
Run: fontforge -lang=py tools/test_half_delta.py
Generates two tiny TTFs for fontTools signed-area comparison.
"""
import fontforge
from pathlib import Path

PREP160 = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
PREP161 = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
BASE = str(PREP160 / 'Pranoti-Regular-v0.160-beta.ttf')

f = fontforge.open(BASE)
g = f['bn_ai']
print('before: validate', g.validate(), 'bbox', g.boundingBox())
g.changeWeight(-8)
g.addExtrema()
print('after -8: validate', g.validate(), 'bbox', g.boundingBox())
f.generate(str(PREP161 / 'tmp-test-ai-minus8.ttf'))
f.close()

f = fontforge.open(BASE)
g = f['bn_ai']
g.changeWeight(-16)
g.addExtrema()
g.correctDirection()
print('after -16 + correctDirection: validate', g.validate(), 'bbox', g.boundingBox())
f.generate(str(PREP161 / 'tmp-test-ai-minus16-cd.ttf'))
f.close()
print('done')
