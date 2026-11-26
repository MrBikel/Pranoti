#!/usr/bin/env python3
"""Pass 2 of the v0.161 weight-evening: FontForge changeWeight on 4 glyphs.

Pass-1 re-measurement left exactly the four predicted glyphs beyond +15%:
bn_ai 104.5, bn_i 102.5, bn_e 99.8, bn_yya 99.8. Per WEIGHT-PLAN-v0.161.md
§4, each takes another capped -16. (bn_anusvara stays REVERTED — its -15
thin created a degenerate kink; see transplant.py.)
Run: fontforge -lang=py tools/changeweight_pass2.py
Base is the pass-1 v0.161 TTF; output is a temporary TTF for transplant.
"""
import json
import fontforge
from pathlib import Path

PREP161 = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
BASE = str(PREP161 / 'Pranoti-Regular-v0.161-beta.ttf')
TMP = str(PREP161 / 'tmp-fontforge-pass2.ttf')
LOG = PREP161 / 'tools' / 'changeweight-pass2.json'

ADJUST = {'bn_ai': -16, 'bn_i': -16, 'bn_e': -16, 'bn_yya': -16}


def snap(g):
    bb = g.boundingBox()
    return {'bbox': [bb[0], bb[1], bb[2], bb[3]], 'width': g.width,
            'validate': g.validate(), 'points': len(g.layers[1]) if len(g.layers) > 1 else 0}


def main():
    font = fontforge.open(BASE)
    print(f'opened {BASE}: {len(font)} glyphs, em={font.em}')
    log = []
    for name, delta in ADJUST.items():
        g = font[name]
        before = snap(g)
        g.changeWeight(delta)
        g.addExtrema()
        g.correctDirection()  # thinning flips contours; restore orientation
        after = snap(g)
        log.append({'glyph': name, 'delta': delta, 'before': before, 'after': after})
        print(f"  {name:14s} d={delta:+3d} bbox {before['bbox']} -> {after['bbox']} "
              f"width {before['width']}->{after['width']} validate {before['validate']}->{after['validate']}")
    font.generate(TMP)
    print(f'generated temp TTF: {TMP}')
    json.dump(log, open(LOG, 'w'), indent=1)
    print(f'wrote {LOG}')
    font.close()


main()
