#!/usr/bin/env python3
"""Vowel fine-tuning for Pranoti v0.163-beta (FontForge step).

Run:  fontforge -script tools/build_vowels_v0163.py
Reads the v0.162 TTF, applies the per-glyph transforms below, and saves a
TEMPORARY TTF. The temp file is NOT the deliverable: only the changed glyf
outlines are transplanted into a fontTools copy of v0.162 (see
transplant_v0163.py), so every other table stays byte-identical to v0.162.

Measurement (tools/measure_vowels_v0163.py, rasterised true ink at 1536px;
targets = the v0.150 fitted ink boxes from v0160-prep/traced_glyphs.json):
- Stroke weights of all 11 vowels are IN the +/-15% band around 84.5
  (84.5-92.2), so NO changeWeight is applied anywhere.
- Ink centres are already on target (cx_err -1.5..+1.5) and bottoms are
  within ~4 of target, so NO horizontal shift is applied. (Side-bearing
  evening was examined and rejected: the vowel-row gaps are dominated by
  ink-width-vs-advance mismatch, up to -331 units; equalising them would
  need shifts of 120-330 units, far beyond the +/-40 anchor-safe cap, and
  merely centring ink in the advance barely changes the gap spread
  406 -> 393 while moving candrabindu anchors up to 40 units. See
  VOWEL-LOG-v0.163.md.)
- The four vowels thinned in v0.161 sit low: bn_i -21, bn_e -20,
  bn_ai -20, bn_au -12 (ink top vs target). Each gets a UNIFORM scale
  about its raster ink centre restoring the v0.150 target HEIGHT, plus a
  small dy translate putting the ink top exactly on target. Uniform
  scale (x and y together, v0.150 method) keeps stroke weight almost
  unchanged (+1.0-3.6%, still in band) and keeps the ink centre where
  it is. Widths grow by the same 1-3.6% (his handwriting is genuinely
  wider; no width rescaling - outside the v0.150 [0.97, 1.08] clamp).
- No shape surgery: 0 self-intersections and no degenerate contours on
  any vowel; bn_ri's roughness is his pen's character, left as is.

Two FontForge behaviours (from the v0.161/v0.162 builds):
- `glyph.foreground` returns a COPY: contour transforms only stick if
  the layer is assigned back (`g.foreground = layer`).
- In this build `psMat.compose(a, b)` applies a FIRST, then b (verified
  in the v0.162 build): scale_about translates (-c) first.
- In-session `glyph.validate()` returns transient 524288 values; the
  revert rule compares validate on the FINAL transplanted TTF.
"""
import json
import fontforge
import psMat
from pathlib import Path

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
PREP162 = BASE / 'v0162-prep'
PREP163 = BASE / 'v0163-prep'
TTF = str(PREP162 / 'Pranoti-Regular-v0.162-beta.ttf')
TMP = str(PREP163 / 'tmp-fontforge-vowels.ttf')
LOG = PREP163 / 'tools' / 'vowel-transforms.json'

FIX = ['bn_i', 'bn_e', 'bn_ai', 'bn_au']  # the four v0.161-thinned vowels


def translate(dx, dy):
    return psMat.translate(dx, dy)


def scale_about(sx, sy, cx, cy):
    """Scale about point (cx, cy). psMat.compose(a, b) applies a FIRST."""
    return psMat.compose(psMat.translate(-cx, -cy),
                         psMat.compose(psMat.scale(sx, sy),
                                       psMat.translate(cx, cy)))


def signed_area(contour):
    pts = [(p.x, p.y) for p in contour]
    if len(pts) < 3:
        return 0.0
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1]
                     - pts[(i + 1) % len(pts)][0] * pts[i][1]
                     for i in range(len(pts)))


def snap(g):
    bb = g.boundingBox()
    areas = [round(signed_area(c), 1) for c in g.foreground]
    return {'bbox': [round(v, 1) for v in bb], 'width': g.width,
            'validate': g.validate(), 'n_contours': len(g.foreground),
            'signed_areas': areas}


def main():
    meas = {r['glyph']: r for r in json.load(
        open(PREP163 / 'checks' / 'vowel-measure-v0.162.json', encoding='utf-8'))}
    traced = json.load(open(BASE / 'v0160-prep' / 'traced_glyphs.json', encoding='utf-8'))
    font = fontforge.open(TTF)
    print(f'opened {TTF}: {len(font)} glyphs, em={font.em}')
    log = []
    for name in FIX:
        m = meas[name]
        tgt = traced[name]['target']  # [x0, y0, x1, y1] v0.150 fitted ink box
        ink_h = m['ink_y1'] - m['ink_y0']
        tgt_h = tgt[3] - tgt[1]
        s = tgt_h / ink_h
        cx, cy = m['ink_cx'], m['ink_cy']
        new_top = cy + (m['ink_y1'] - cy) * s
        dy = tgt[3] - new_top
        g = font[name]
        before = snap(g)
        layer = g.foreground
        for c in layer:
            c.transform(scale_about(s, s, cx, cy))
        g.foreground = layer
        layer = g.foreground
        for c in layer:
            c.transform(translate(0, dy))
        g.foreground = layer
        g.addExtrema()
        g.correctDirection()
        after = snap(g)
        if [a > 0 for a in before['signed_areas']] != [a > 0 for a in after['signed_areas']]:
            print(f'  !! {name}: contour winding CHANGED by transforms!')
        log.append({'glyph': name, 'char': m['char'], 'scale': round(s, 5),
                    'pivot': [cx, cy], 'dy': round(dy, 1),
                    'ink_top_before': m['ink_y1'], 'ink_top_target': tgt[3],
                    'before': before, 'after': after})
        print(f"  {name:6s} U+{ord(m['char']):04X} scale x{s:.5f} about ({cx},{cy}) dy {dy:+.1f} "
              f"top {m['ink_y1']}->{tgt[3]} bbox {before['bbox']} -> {after['bbox']} "
              f"validate {before['validate']}->{after['validate']} (in-session; see header)")
    font.generate(TMP)
    print(f'generated temp TTF: {TMP}')
    json.dump(log, open(LOG, 'w'), indent=1)
    print(f'wrote {LOG}')
    font.close()


main()
