#!/usr/bin/env python3
"""Pass 1 of the v0.161 weight-evening: FontForge changeWeight on 18 glyphs.

Run:  fontforge -lang=py tools/changeweight_pass1.py
Reads the v0.160 TTF, applies the WEIGHT-PLAN-v0.161.md §4 pass-1 table,
runs addExtrema() on each touched glyph, and saves a TEMPORARY TTF.
The temp file is NOT the deliverable: only its 18 changed glyf outlines
are transplanted into a fontTools copy of v0.160 (see transplant.py),
so every other table stays byte-identical to v0.160.
"""
import json
import fontforge
from pathlib import Path

PREP160 = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
PREP161 = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
BASE = str(PREP160 / 'Pranoti-Regular-v0.160-beta.ttf')
TMP = str(PREP161 / 'tmp-fontforge-pass1.ttf')
LOG = PREP161 / 'tools' / 'changeweight-pass1.json'

# WEIGHT-PLAN-v0.161.md §4, pass 1 (delta = change in stem width, units)
ADJUST = {
    # thin down
    'bn_ai': -16, 'bn_i': -16, 'bn_e': -16, 'bn_yya': -16,
    'bn_one': -16, 'bn_six': -16, 'bn_au': -16,
    'bn_kha': -15, 'bn_ga': -15, 'bn_ya': -15,
    'bn_aikaar': -16, 'bn_ikaar': -15, 'bn_anusvara': -15,
    # thicken up
    'bn_tta': 14, 'bn_cha': 15, 'bn_pa': 15,
    'bn_okaar': 16, 'bn_uukaar': 16,
}


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
        # changeWeight FLIPS every contour on thinning (inset); verified:
        # bn_ai -8 and -16 both reversed the signed area. Half-delta does
        # NOT help. correctDirection() restores the original orientation
        # (verified on bn_ai: area sign matches the v0.160 original).
        # Harmless no-op on the thickened glyphs (already correct).
        g.correctDirection()
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
