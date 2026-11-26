#!/usr/bin/env python3
"""Build Pranoti v0.150-beta from v0.140-beta.

v0.150: size normalisation + beautiful arrangement (ink-based, v2).

KEY CORRECTION vs the first v0.150 attempt (discarded, never shipped):
  fontTools' glyph bbox INCLUDES off-curve control points. In these traced
  outlines the control points overshoot the real ink by up to ~90 units
  (e.g. bn_ta control y=126, true ink bottom y=175; bn_ttha control y=81,
  true ink bottom y=133). So ALL measurements here use TRUE INK bboxes
  (rasterised at 1536 px, ink-measure.json) -- never the outline bbox.

What v0.150 actually does (per glyph, 56 letters: 11 vowels + 35 consonants
+ 10 digits):
  1. Mild uniform scale s about the ink-bbox centre. s is the average of
     the ink-area scale and the ink-box scale vs AdorshoLipi, clamped to
     [0.97, 1.08] and further capped so the resulting ink height stays
     within +/-40 units of AdorshoLipi's height for the same letter.
     (Heights already match AdorshoLipi within ~+/-30, so no letter is
     stretched; the scale only evens out visual weight/width.)
  2. Translate so the scaled ink bbox's TOP matches AdorshoLipi's ink top
     for the same letter (common headline ~1157 for plain letters, taller
     for ascenders) and its horizontal CENTRE matches AdorshoLipi's ink
     centre for the same letter. Horizontal shift capped at +/-40 units
     so the GPOS candrabindu anchors (unchanged) stay visually aligned.
  3. Re-centre side bearings: hmtx lsb = new outline xMin. Advances
     UNCHANGED (verification requires them identical to v0.120).

  The 13 vowel signs/marks and the 4 new glyphs (U+0980, U+09FB, U+09FC,
  U+09FE) are NOT resized or moved. GSUB/GPOS/GDEF/cmap are untouched.
  Only glyf outlines (+ hmtx lsb), head, name, maxp, loca, hhea move.

  bn_nya: delete two degenerate separate contours (c4, c5) -- long thin
  slivers (bbox ~1000x520, area 1840 and 902, average width < 2 units)
  that render as stray diagonal hairlines across the glyph. They are
  tracing artefacts, not strokes; the rest of the glyph is untouched.
  (The earlier "spike collapse" idea was WRONG and is NOT used: the
  supposed spike tips are off-curve control points, not ink -- collapsing
  them moved real loop bottoms up by up to 96 units. The remaining
  in-contour hairline folds are sub-pixel at text sizes and are left
  for a later batch; see SIZE-LOG-v0.150.md.)

Input : ../github-repo/Pranoti-Regular-v0.140-beta.ttf (read-only)
Output: Pranoti-Regular-v0.150-beta.ttf, size-transforms.json
"""
import json, math
from fontTools.ttLib import TTFont

BASE = '/home/hatch/workspace/fonts/bengali-hand/github-repo/Pranoti-Regular-v0.140-beta.ttf'
OUT  = '/home/hatch/workspace/fonts/bengali-hand/v0150-prep/Pranoti-Regular-v0.150-beta.ttf'
MEAS = '/home/hatch/workspace/fonts/bengali-hand/v0150-prep/ink-measure.json'

LETTERS = ['bn_a','bn_aa','bn_i','bn_ii','bn_u','bn_uu','bn_ri','bn_e','bn_ai','bn_o','bn_au',
 'bn_ka','bn_kha','bn_ga','bn_gha','bn_nga','bn_ca','bn_cha','bn_ja','bn_jha','bn_nya',
 'bn_tta','bn_ttha','bn_dda','bn_ddha','bn_nna','bn_ta','bn_tha','bn_da','bn_dha','bn_na',
 'bn_pa','bn_pha','bn_ba','bn_bha','bn_ma','bn_ya','bn_ra','bn_la','bn_sha','bn_ssa','bn_sa','bn_ha',
 'bn_rra','bn_rha','bn_yya',
 'bn_zero','bn_one','bn_two','bn_three','bn_four','bn_five','bn_six','bn_seven','bn_eight','bn_nine']

meas = json.load(open(MEAS))
font = TTFont(BASE)
glyf = font['glyf']
hmtx = font['hmtx']

def transform(g, s, cx, cy, dx, dy):
    """new = centre + (p - centre)*s + (dx, dy)."""
    coords = list(g.coordinates)
    new = []
    for (x, y) in coords:
        new.append((round(cx + (x - cx) * s + dx), round(cy + (y - cy) * s + dy)))
    # slice-assign to keep fontTools' Coordinates object (has calcIntBounds)
    g.coordinates[:] = new

def delete_contours(g, idxs):
    coords = list(g.coordinates); ends = list(g.endPtsOfContours); flags = list(g.flags)
    keep_c, keep_e, keep_f = [], [], []
    s = 0; new_end = -1
    for ci, e in enumerate(ends):
        seg_c = coords[s:e+1]; seg_f = flags[s:e+1]; s = e+1
        if ci in idxs:
            continue
        keep_c += seg_c; keep_f += seg_f
        new_end += len(seg_c); keep_e.append(new_end)
    from array import array
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    g.coordinates = GlyphCoordinates(keep_c); g.endPtsOfContours = keep_e; g.flags = array('B', keep_f)
    g.numberOfContours = len(keep_e)

log = []
for name in LETTERS:
    m = meas[name]
    x0, y0, x1, y1 = m['v140']['bbox']
    ax0, ay0, ax1, ay1 = m['ado']['bbox']
    h140 = y1 - y0; href = ay1 - ay0
    s = m['s_final']
    # cap: resulting ink height within +/-40 of AdorshoLipi's height
    s = max((href - 40) / h140, min((href + 40) / h140, s))
    s = round(max(0.97, min(1.08, s)), 4)
    cx = (x0 + x1) / 2.0; cy = (y0 + y1) / 2.0
    # scaled ink bbox
    sx0 = cx + (x0 - cx) * s; sx1 = cx + (x1 - cx) * s
    sy1 = cy + (y1 - cy) * s
    # translate: top -> AdorshoLipi top, centre-x -> AdorshoLipi centre-x
    dx = (ax0 + ax1) / 2.0 - (sx0 + sx1) / 2.0
    dx = max(-40, min(40, dx))
    dy = ay1 - sy1
    g = glyf[name]
    if g.isComposite():
        raise SystemExit(f'{name} is composite, abort')
    if name == 'bn_nya':
        delete_contours(g, {4, 5})
        print('bn_nya: deleted degenerate contours c4, c5 (hairline slivers)')
    transform(g, s, cx, cy, dx, dy)
    adv, lsb = hmtx[name]
    xs = [p[0] for p in g.coordinates]
    hmtx[name] = (adv, min(xs))
    # resulting ink bbox (analytic)
    nx0 = round(sx0 + dx); nx1 = round(sx1 + dx)
    ny1 = round(ay1); ny0 = round(cy + (y0 - cy) * s + dy)
    log.append({'glyph': name, 'ch': m['ch'], 'scale': s, 'dx': round(dx, 1), 'dy': round(dy, 1),
                'ink_before': [x0, y0, x1, y1], 'ink_after': [nx0, ny0, nx1, ny1],
                'ado_ink': [ax0, ay0, ax1, ay1], 'adv': adv})
    print(f"  {m['ch']} {name}: s={s} dx={dx:+.0f} dy={dy:+.0f} ink y[{y0},{y1}] -> y[{ny0},{ny1}] (ado [{ay0},{ay1}]) x[{x0},{x1}] -> x[{nx0},{nx1}] (ado [{ax0},{ax1}])")

# name table: v0.150-beta (both Mac and Windows records, like v0.140 did)
name = font['name']
for nid, val in [(1, 'Pranoti'), (3, 'Pranoti:Version 0.150-beta'),
                 (4, 'Pranoti Regular'), (5, 'Version 0.150-beta'),
                 (6, 'Pranoti-Regular'), (16, 'Pranoti')]:
    name.setName(val, nid, 3, 1, 0x409)
    name.setName(val, nid, 1, 0, 0)
font['head'].fontRevision = 0.150
font.recalcBBoxes = True
font.save(OUT)

import hashlib
sha = hashlib.sha256(open(OUT, 'rb').read()).hexdigest()
print('Built:', OUT)
print('v0.150 SHA-256:', sha)
json.dump(log, open('/home/hatch/workspace/fonts/bengali-hand/v0150-prep/size-transforms.json', 'w'),
          ensure_ascii=False, indent=1)
print('wrote size-transforms.json')
