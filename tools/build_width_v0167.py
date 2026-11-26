#!/usr/bin/env python3
"""Gentle WIDTH evening + flagged-letter fixes — Pranoti v0.167-beta.

Run:  fontforge -script tools/build_width_v0167.py
Reads the INTERMEDIATE TTF (v0.166 + re-traced ঞ/স + point surgery for
গ/দ/ঊ/আ/ন — see tools/build_intermediate_v0167.py), applies the
horizontal scales and placements, and saves a TEMPORARY TTF. The temp
file is NOT the deliverable: only the changed glyf outlines are
transplanted into a fontTools copy of v0.166 (transplant_v0167.py), so
every other table stays byte-identical.

A) 13 SIGNS — horizontal scale about (ink LEFT edge, centre-y), closing
   HALF of each width error, capped x0.85-x1.20 (see the v0.150 log and
   checks/sign-measure-v0.166.tsv). Pivot = left edge (all 13 signs have
   their left edge on target; centre-scaling would move it wrong).
   bn_uukaar override x0.95 (its x0.8999 scale pushed the ridge to 70.8,
   below the 71.8 band floor). bn_rikaar: after the scale, translate
   left so xMax ~ -66 (the v0.120 box), fixing its detached hang.
B) Khanda_Ta (ৎ): translate dx=+196 (re-centres the ink: [-188,1007]
   -> [8,1203] on the widened advance 1210, set in the transplant).
   Pixel analysis proved the -188 left overhang collides with the
   previous glyph's ink in ALL 7 test words (56,065 px in সৎ), while
   the base font's ৎ touches nothing. The +248 right overhang never
   touches the next glyph's ink (it passes through empty bbox space),
   so the widened advance is what keeps the tail clear.
C) CONSONANTS/VOWELS — horizontal scale about the OUTLINE bbox centre
   (ink centre), heights/tops unchanged, advances unchanged:
   bn_yya x0.85, bn_ca x0.88, bn_jha x0.85, bn_na x0.90, bn_sa x0.88,
   bn_aa x0.90, bn_i x0.88, bn_ii x0.95, bn_ri x0.85.
D) bn_na: removeOverlap() first, merging the extended diagonal stub
   with the loop (the join from the intermediate surgery).

FontForge behaviours (from the v0.161/v0.166 builds):
- `glyph.foreground` returns a COPY: transforms only stick if the
  layer is assigned back (`g.foreground = layer`).
- `psMat.compose(a, b)` applies a FIRST, then b.
- In-session `glyph.validate()` returns transient values; the revert
  rule compares validate on the FINAL transplanted TTF.
"""
import json
import fontforge
import psMat
from pathlib import Path

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
PREP166 = BASE / 'v0166-prep'
PREP167 = BASE / 'v0167-prep'
TMP_IN = str(PREP167 / 'intermediate-v0167.ttf')
TMP = str(PREP167 / 'tmp-fontforge-width.ttf')
LOG = PREP167 / 'tools' / 'width-transforms.json'

SIGNS = ['bn_aakaar', 'bn_ikaar', 'bn_iikaar', 'bn_ukaar', 'bn_uukaar',
         'bn_rikaar', 'bn_ekaar', 'bn_aikaar', 'bn_okaar', 'bn_aukaar',
         'bn_anusvara', 'bn_visarga', 'bn_candrabindu']
# uukaar override: the planned x0.8999 pushed its ridge to 70.8 (below
# the 71.8 band floor); x0.95 closes 25% of the width error instead.
OVERRIDES = {'bn_uukaar': 0.95}
# horizontal scale about the outline bbox centre (ink centre)
# bn_yya reduced 0.85 -> 0.90: at x0.85 its ridge fell to 69.1, BELOW
# the 71.8 band floor (the brief's revert rule); x0.90 keeps the ridge
# in band (~73-75) while still narrowing the glyph clearly.
CENTRE_SCALES = {'bn_yya': 0.90, 'bn_ca': 0.88, 'bn_jha': 0.85,
                 'bn_na': 0.90, 'bn_sa': 0.88, 'bn_aa': 0.90,
                 'bn_i': 0.88, 'bn_ii': 0.95, 'bn_ri': 0.85}
KHANDA_TA_DX = 196  # re-centre ink [-188,1007] -> [8,1203]
RIKAAR_XMAX_TARGET = -66  # v0.120 box


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


def plan_scale(m):
    """Close half the width error, capped to x0.85-x1.20."""
    w = m['ink_w']
    w_err = m['w_err']
    desired = w - w_err / 2.0
    s = desired / w
    capped = min(1.20, max(0.85, s))
    return s, capped, desired


def transform(g, mat):
    layer = g.foreground
    for c in layer:
        c.transform(mat)
    g.foreground = layer
    g.addExtrema()
    g.correctDirection()


def main():
    meas = {r['glyph']: r for r in json.load(
        open(PREP166 / 'checks' / 'sign-measure-v0.166.json', encoding='utf-8'))}
    font = fontforge.open(TMP_IN)
    print(f'opened {TMP_IN}: {len(font)} glyphs, em={font.em}')
    log = []

    # ---- D) bn_na: merge the joined stub + loop --------------------
    g = font['bn_na']
    before = snap(g)
    g.removeOverlap()
    after = snap(g)
    log.append({'glyph': 'bn_na', 'action': 'removeOverlap (join stub+loop)',
                'contours_before': before['n_contours'],
                'contours_after': after['n_contours'],
                'bbox_before': before['bbox'], 'bbox_after': after['bbox']})
    print(f"  bn_na removeOverlap: contours {before['n_contours']} -> "
          f"{after['n_contours']}, bbox {before['bbox']} -> {after['bbox']}")

    # ---- A) 13 signs: width scale about the left edge --------------
    for name in SIGNS:
        m = meas[name]
        raw_s, sx, desired_w = plan_scale(m)
        if name in OVERRIDES:
            sx = OVERRIDES[name]
        cx, cy = m['ink_x0'], m['ink_cy']
        tgt_w = m['ink_w'] - m['w_err']
        g = font[name]
        before = snap(g)
        transform(g, scale_about(sx, 1.0, cx, cy))
        # bn_rikaar: shift left so xMax matches the v0.120 box (-66)
        shift = 0
        if name == 'bn_rikaar':
            x1_after = g.boundingBox()[2]
            shift = RIKAAR_XMAX_TARGET - x1_after
            transform(g, translate(shift, 0))
        after = snap(g)
        if [a > 0 for a in before['signed_areas']] != [a > 0 for a in after['signed_areas']]:
            print(f'  !! {name}: contour winding CHANGED by transforms!')
        log.append({'glyph': name, 'char': m['char'],
                    'ink_w_before': m['ink_w'], 'target_w': tgt_w,
                    'w_err_before': m['w_err'],
                    'desired_w_half_error': round(desired_w, 1),
                    'scale_raw': round(raw_s, 5), 'scale_applied': round(sx, 5),
                    'capped': raw_s != sx, 'override': name in OVERRIDES,
                    'pivot': [cx, cy], 'pivot_rule': 'left-edge + centre-y',
                    'rikaar_shift_dx': shift,
                    'ridge_before': m['ridge_med'],
                    'before': before, 'after': after})
        print(f"  {name:14s} U+{ord(m['char']):04X} w {m['ink_w']} -> ~{m['ink_w'] * sx:.0f} "
              f"(target {tgt_w}, raw x{raw_s:.4f}{' CAPPED' if raw_s != sx else ''} -> x{sx:.4f}) "
              f"about ({cx},{cy}) bbox {before['bbox']} -> {after['bbox']} "
              f"validate {before['validate']}->{after['validate']} (in-session)"
              + (f' rikaar shift dx={shift}' if shift else ''))

    # ---- B) Khanda_Ta: re-centre the ink ---------------------------
    g = font['Khanda_Ta']
    before = snap(g)
    transform(g, translate(KHANDA_TA_DX, 0))
    after = snap(g)
    log.append({'glyph': 'Khanda_Ta', 'action': 'translate re-centre ink',
                'dx': KHANDA_TA_DX, 'advance_old': before['width'],
                'advance_new': 1210, 'bbox_before': before['bbox'],
                'bbox_after': after['bbox']})
    print(f"  Khanda_Ta translate dx=+{KHANDA_TA_DX}: bbox {before['bbox']} -> "
          f"{after['bbox']} (advance 759 -> 1210 in the transplant)")

    # ---- C) consonants/vowels: scale about the outline bbox centre -
    for name, sx in CENTRE_SCALES.items():
        g = font[name]
        before = snap(g)
        x0, y0, x1, y1 = before['bbox']
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        transform(g, scale_about(sx, 1.0, cx, cy))
        after = snap(g)
        if [a > 0 for a in before['signed_areas']] != [a > 0 for a in after['signed_areas']]:
            print(f'  !! {name}: contour winding CHANGED by transforms!')
        log.append({'glyph': name, 'action': 'horizontal scale about bbox centre',
                    'scale': sx, 'pivot': [round(cx, 1), round(cy, 1)],
                    'bbox_before': before['bbox'], 'bbox_after': after['bbox'],
                    'width_before': before['width']})
        print(f"  {name:10s} x{sx} about ({cx:.0f},{cy:.0f}): bbox "
              f"{before['bbox']} -> {after['bbox']} "
              f"validate {before['validate']}->{after['validate']} (in-session)")

    font.generate(TMP)
    print(f'generated temp TTF: {TMP}')
    json.dump(log, open(LOG, 'w'), indent=1)
    print(f'wrote {LOG}')
    font.close()


main()
