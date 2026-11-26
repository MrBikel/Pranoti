#!/usr/bin/env python3
"""Build the v0.167 INTERMEDIATE TTF (fontTools).

v0.166 base (SHA verified) + re-traced glyphs + point surgery.
The intermediate is then loaded by FontForge (build_width_v0167.py)
for the horizontal scales, and the touched outlines are transplanted
into a fresh v0.166 copy (transplant_v0167.py).

Re-traces (v0.160 method, fitted uniformly to the v0.166 glyf box,
centre-x + top, advance kept):
- bn_nya (ঞ): photo 16 r1c10 at Otsu 193 (NOT the brief's "lower"
  threshold — measured: lower thresholds make the strokes THINNER and
  more fragmented (area 1206@150 vs 1391@178); the faded light-grey
  strokes are only recovered by RAISING the threshold. @193: 2
  contours, area 1477, fuller middle strokes, left-loop hole intact.
  The bottom-left diagonal is KEPT: the v0.120 base ঞ has the same
  lower-left sweep (specimens/nya-base-vs-current.png), so it is his
  ঞ's stroke, not the neighbour's ink.
- bn_sa (স): photo 16 r4c1 at Otsu 189 (2 contours, area 1390 vs
  1311@174): middle zigzag fuller/solid. The hook is rounded in the
  FontForge step only if the render still shows a sharp V (see below).
- bn_na (ন): NO re-trace — no threshold (130..202) connects the loop
  (the diagonal is genuinely missing: pen lifted, paper blank); the
  join is done by point surgery below (stub extended to the loop,
  merged by removeOverlap in the FontForge step).

Point surgery (all on the v0.166 outlines, coordinates verified by
dumping the glyph point lists):
- bn_ga (গ): trim the tall right stem (top y=1383) down to the
  headline bar's top level (y=1210; the bar's own top is 1205-1226,
  so trimming to the global 1157 would bury the stem inside the bar
  with degenerate geometry — same visible result, clean outline).
  Flatten stem-top points i0-i8 and i187-i193 to y=1210.
  Shorten the lower-left tail flick: points i119-i123 moved +35 in x
  (tip x 28-42 -> 63-77) so it reads as part of the bowl.
  Row-above ink RULED OUT: the crop above the গ cell in photo 16
  (specimens/ga-cell-context.png) is blank paper — the tall stem is
  his own stroke, genuinely overshooting.
- bn_da (দ): shorten the long thin right tail: tip points i57-i62
  moved up-left ~40-50 (tip (1022,-1) -> (980,50)); nudge the
  diagonal's lower-right points (i37-i40, i80-i81) left by 30 so the
  sweep fills the empty lower-left a little. No re-trace (Otsu
  140/164/180 all give the identical 1-contour trace).
- bn_uu (ঊ): remove the weaker (thinner, ~30 units) of the two
  parallel bottom-left tail strokes — the second stroke (the pen's
  stutter). Delete contour points i81-i101, reflag i102 on-curve,
  insert off-curve (520,380) after i80 so the bowl's lower edge is a
  smooth curve from (441,314) to (660,298). The first (stronger,
  ~80-unit) tail stroke, reaching (-41,738), is kept.
- bn_aa (আ): cap the stem's top hook (points i1-i8, y up to 1336)
  at y=1157; straighten the stem's vertical run (left edge i24-i29
  x->1525, right edge i35-i37 and i170-i174 x->1445). The bar's top
  edge is left wavy (its full levelling is the v0.169 matra pass).
- bn_na (ন): extend the connecting diagonal stub to the loop so
  removeOverlap (FontForge step) can merge them: tip i41 (599,446)
  -> (520,500), controls i40 (560,447) -> (490,475), i42 (620,446)
  -> (555,460). The stub then overlaps the loop outline (c1) by
  ~30 units; the loop hole (c2) is kept as a hole.

Run: python3 tools/build_intermediate_v0167.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0160-prep/tools')
import trace_glyphs as tg  # noqa: E402

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
PREP166 = BASE / 'v0166-prep'
PREP167 = BASE / 'v0167-prep'
CELLS = BASE / 'v0160-prep/cells'
V166 = PREP166 / 'Pranoti-Regular-v0.166-beta.ttf'
OUT = PREP167 / 'intermediate-v0167.ttf'
LOG = PREP167 / 'tools' / 'intermediate-log.json'
EXPECTED_BASE_SHA256 = 'a07809f97f42fc2ea85938f00779e63377b6cdb2f9b7fcd363ca838259328c06'


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def cell_ink_thr(arr, thr):
    mask = arr < thr
    mask100 = arr < 100
    lab, n = tg.ndimage.label(mask)
    keep = np.zeros_like(mask)
    if n:
        for i, sl in enumerate(tg.ndimage.find_objects(lab), 1):
            comp = (lab[sl] == i)
            if comp.sum() < 4:
                continue
            if not mask100[sl][comp].any():
                continue
            keep[sl] |= comp
    return keep


def fit_trace(cell_path, thr, target_box):
    """Trace the cell at thr, fit uniformly to target_box (x0,y0,x1,y1),
    centre-x + top (v0.160 letter rule). Returns a fontTools Glyph."""
    arr = np.asarray(Image.open(cell_path).convert('L'))
    ink = cell_ink_thr(arr, thr)
    contours = tg.potrace_svg(cell_path.stem + f'_fit{thr}', ink)
    tx0, ty0, tx1, ty1 = tg.true_bbox(contours)
    gx0, gy0, gx1, gy1 = target_box
    s = (gy1 - gy0) / (ty1 - ty0)
    glyph = tg.contours_to_glyph(contours, s, (gx0 + gx1) / 2.0, gy1,
                                 (tx0 + tx1) / 2.0, ty0)
    tg.reverse_contours(glyph)
    return glyph, len(contours), s


def set_pt(glyph, idx, x=None, y=None):
    coords = list(glyph.coordinates)
    cx, cy = coords[idx]
    coords[idx] = (cx if x is None else x, cy if y is None else y)
    glyph.coordinates = GlyphCoordinates(coords)


def move_pt(glyph, idx, dx=0, dy=0):
    coords = list(glyph.coordinates)
    cx, cy = coords[idx]
    coords[idx] = (cx + dx, cy + dy)
    glyph.coordinates = GlyphCoordinates(coords)


def main():
    assert sha256(V166) == EXPECTED_BASE_SHA256, 'v0.166 base checksum mismatch'
    font = TTFont(V166, checkChecksums=2)
    glyf = font['glyf']
    log = {'retraces': {}, 'surgery': {}}

    # ---- re-traces -------------------------------------------------
    for name, cell, thr in [('bn_nya', CELLS / 'cons_16_r1c10.png', 193),
                            ('bn_sa', CELLS / 'cons_16_r4c1.png', 189)]:
        g = glyf[name]
        box = (g.xMin, g.yMin, g.xMax, g.yMax)
        new_g, n_cont, s = fit_trace(cell, thr, box)
        new_g.recalcBounds(font.getGlyphSet())
        new_g.program = g.program
        glyf[name] = new_g
        log['retraces'][name] = {'cell': cell.name, 'otsu': thr,
                                 'contours': n_cont, 'scale': round(s, 4),
                                 'target_box': box,
                                 'new_box': (new_g.xMin, new_g.yMin,
                                             new_g.xMax, new_g.yMax)}
        print(f'  {name}: re-traced {cell.name} Otsu {thr} -> '
              f'{n_cont} contours, scale x{s:.4f}, box {box} -> '
              f'{(new_g.xMin, new_g.yMin, new_g.xMax, new_g.yMax)}')

    # ---- bn_ga: stem trim + tail shorten ---------------------------
    # Stem trim: DELETE the whole stem-top excursion (points i187-i193
    # and i0-i8, the part of the stem above the headline bar) and let
    # the contour run from i186 (721,1139) straight to i9 (818,1207),
    # i.e. the bar's top edge interpolated across the stem. Flattening
    # those points to y=1210 instead created a collinear fold (the
    # contour retraced x 795-816 along y=1210) that FontForge validate
    # flags as bit 4 (self-intersecting) — the v0.167 revert rule.
    # Tail shorten first (original indices), then delete the excursion.
    g = glyf['bn_ga']
    before = (g.xMin, g.yMin, g.xMax, g.yMax)
    for i in (119, 120, 121, 122, 123):
        move_pt(g, i, dx=35)
    coords = list(g.coordinates)
    flags = list(g.flags)
    # keep indices 9..186 (the stem-top excursion is 0..8 and 187..193)
    new_coords = coords[9:187]
    new_flags = flags[9:187]
    g.coordinates = GlyphCoordinates(new_coords)
    g.flags = np.array(new_flags, dtype=np.uint8)
    g.endPtsOfContours = [len(new_coords) - 1]
    g.recalcBounds(glyf)
    log['surgery']['bn_ga'] = {
        'stem_top': '1383 -> 1226 (bar top): deleted the stem-top '
                    'excursion (pts i0-i8, i187-i193); contour now runs '
                    'i186 (721,1139) -> i9 (818,1207), the bar top edge',
        'tail_tip_x': '28-42 -> 63-77 (+35)', 'bbox_before': before,
        'bbox_after': (g.xMin, g.yMin, g.xMax, g.yMax),
        'points': f'{len(coords)} -> {len(new_coords)}'}
    print(f"  bn_ga: stem excursion deleted, tail tip +35x, bbox {before} -> "
          f"{(g.xMin, g.yMin, g.xMax, g.yMax)}")

    # ---- bn_da: tail shorten + diagonal nudge ----------------------
    g = glyf['bn_da']
    before = (g.xMin, g.yMin, g.xMax, g.yMax)
    tip_moves = {57: (-34, 40), 58: (-40, 44), 59: (-48, 52),
                 60: (-42, 51), 61: (-44, 60), 62: (-28, 53)}
    for i, (dx, dy) in tip_moves.items():
        move_pt(g, i, dx=dx, dy=dy)
    for i in (37, 38, 39, 40, 80, 81):
        move_pt(g, i, dx=-30)
    g.recalcBounds(glyf)
    log['surgery']['bn_da'] = {
        'tail_tip': '(1022,-1) -> (980,50); tip pts moved up-left 28-48',
        'diagonal': 'lower-right pts i37-i40,i80-i81 moved -30x',
        'bbox_before': before,
        'bbox_after': (g.xMin, g.yMin, g.xMax, g.yMax)}
    print(f"  bn_da: tail tip shortened, diagonal -30x, bbox {before} -> "
          f"{(g.xMin, g.yMin, g.xMax, g.yMax)}")

    # ---- bn_uu: remove the weaker fork stroke ----------------------
    g = glyf['bn_uu']
    before = (g.xMin, g.yMin, g.xMax, g.yMax)
    coords = list(g.coordinates)
    flags = list(g.flags)
    # delete indices 81..101 (the weaker second tail stroke)
    # insert off-curve (520,380) after index 80; reflag old i102 on-curve
    new_coords = coords[:81] + [(520, 380)] + coords[102:]
    new_flags = flags[:81] + [0] + flags[102:]
    new_flags[82] = 1  # old i102 becomes on-curve
    g.coordinates = GlyphCoordinates(new_coords)
    g.flags = np.array(new_flags, dtype=np.uint8)
    g.endPtsOfContours = [len(new_coords) - 1]
    g.recalcBounds(glyf)
    log['surgery']['bn_uu'] = {
        'fork': 'deleted pts i81-i101 (weaker 2nd tail stroke, ~30u wide); '
                'inserted off-curve (520,380) after i80; old i102 on-curve',
        'points': f'{len(coords)} -> {len(new_coords)}',
        'bbox_before': before,
        'bbox_after': (g.xMin, g.yMin, g.xMax, g.yMax)}
    print(f"  bn_uu: fork removed, pts {len(coords)}->{len(new_coords)}, "
          f"bbox {before} -> {(g.xMin, g.yMin, g.xMax, g.yMax)}")

    # ---- bn_aa: hook cap + stem straighten -------------------------
    g = glyf['bn_aa']
    before = (g.xMin, g.yMin, g.xMax, g.yMax)
    for i in range(1, 9):  # stem-top hook points above 1157
        set_pt(g, i, y=1157)
    for i in range(24, 30):  # stem left edge -> x=1525
        set_pt(g, i, x=1525)
    for i in list(range(35, 38)) + list(range(170, 175)):  # right edge -> 1445
        set_pt(g, i, x=1445)
    g.recalcBounds(glyf)
    log['surgery']['bn_aa'] = {
        'hook_top': '1336 -> 1157 (pts i1-i8 capped)',
        'stem': 'left edge x->1525 (i24-i29), right edge x->1445 '
                '(i35-i37, i170-i174)',
        'bbox_before': before,
        'bbox_after': (g.xMin, g.yMin, g.xMax, g.yMax)}
    print(f"  bn_aa: hook 1336->1157, stem straightened, bbox {before} -> "
          f"{(g.xMin, g.yMin, g.xMax, g.yMax)}")

    # ---- bn_na: extend the diagonal stub to the loop ---------------
    g = glyf['bn_na']
    before = (g.xMin, g.yMin, g.xMax, g.yMax)
    set_pt(g, 41, x=520, y=500)   # stub tip -> inside the loop edge
    set_pt(g, 40, x=490, y=475)   # control before the tip
    set_pt(g, 42, x=555, y=460)   # control after the tip
    g.recalcBounds(glyf)
    log['surgery']['bn_na'] = {
        'stub': 'tip i41 (599,446) -> (520,500); controls i40 -> (490,475), '
                'i42 -> (555,460); stub now overlaps loop (c1) ~30u; '
                'merge by removeOverlap in the FontForge step',
        'contours_before': 4, 'bbox_before': before,
        'bbox_after': (g.xMin, g.yMin, g.xMax, g.yMax)}
    print(f"  bn_na: stub extended to loop, bbox {before} -> "
          f"{(g.xMin, g.yMin, g.xMax, g.yMax)}")

    font.recalcBBoxes = True
    font.save(OUT)
    json.dump(log, open(LOG, 'w'), indent=1)
    print(f'Built: {OUT}')
    print(f'intermediate SHA-256: {sha256(OUT)}')
    font.close()


if __name__ == '__main__':
    main()
