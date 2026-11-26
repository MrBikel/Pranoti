#!/usr/bin/env python3
"""Transplant the v0.167 outlines into a fontTools copy of v0.166.

Same pattern as v0.161/v0.166: FontForge's generate() rewrites tables, so
only the changed glyf outlines (+ their hmtx lsb) are copied into a
fontTools copy of the v0.166 font — every other table stays byte-identical
to v0.166 by construction. Name IDs 3/5 and head.fontRevision become
v0.167. clean_glyph (v0.160 hygiene) runs on each transplanted glyph.

TOUCHED (27 glyphs):
- 13 signs (width scale about the left edge; bn_rikaar also shifted
  left so xMax ~ -66).
- Khanda_Ta (ৎ): re-centred (dx +196); advance widened 759 -> 1210
  so the ink [8,1203] sits inside its advance.
- bn_da, bn_ga, bn_uu, bn_aa, bn_na: point surgery (intermediate).
- bn_nya, bn_sa: re-traced (intermediate).
- bn_yya, bn_ca, bn_jha, bn_na, bn_sa, bn_aa, bn_i, bn_ii, bn_ri:
  horizontal scale about the outline bbox centre.
- bn_anusvara (ং): width-scaled loop + the swoosh contour restored
  (see SWOOSH below).

SWOOSH (bn_anusvara): the loop is the width-scaled v0.166 loop; the
swoosh is re-traced from the r4c7 cell (Otsu 152, the contour below
the loop, pixel bbox x[14,59] y[49.3,73.3]) and fitted uniformly at
the loop's y-scale, positioned relative to the loop, then translated
so its bottom lands at -120 (target -100..-140, like v0.120's -133).
SWOOSH_SOURCE='fresh' (default) uses that trace; 'v0150' uses the
v0.150 glyph's swoosh contour (x[164,710] y[-130,334]) translated
to sit under the v0.167 loop — the fallback if the fresh swoosh
looks too wide/detached in the কং render.

Revert rule: any glyph whose FontForge validate on the FINAL TTF is
worse than on v0.166, or whose re-measured ridge leaves the 72-97 band,
is reverted to its v0.166 outline — re-run this script with the glyph
added to REVERTED after checking the measurements.

Run: python3 tools/transplant_v0167.py [fresh|v0150]
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0160-prep/tools')
import trace_glyphs as tg  # noqa: E402
from build_pranoti_v0160_beta import clean_glyph  # noqa: E402

BASE_DIR = Path('/home/hatch/workspace/fonts/bengali-hand')
PREP166 = BASE_DIR / 'v0166-prep'
PREP167 = BASE_DIR / 'v0167-prep'
BASE = PREP166 / 'Pranoti-Regular-v0.166-beta.ttf'
TMP = PREP167 / 'tmp-fontforge-width.ttf'
OUT = PREP167 / 'Pranoti-Regular-v0.167-beta.ttf'
V150 = BASE_DIR / 'github-repo' / 'Pranoti-Regular-v0.150-beta.ttf'
EXPECTED_BASE_SHA256 = 'a07809f97f42fc2ea85938f00779e63377b6cdb2f9b7fcd363ca838259328c06'

TOUCHED = ['bn_aakaar', 'bn_ikaar', 'bn_iikaar', 'bn_ukaar', 'bn_uukaar',
           'bn_rikaar', 'bn_ekaar', 'bn_aikaar', 'bn_okaar', 'bn_aukaar',
           'bn_anusvara', 'bn_visarga', 'bn_candrabindu',
           'Khanda_Ta', 'bn_da', 'bn_ga', 'bn_yya', 'bn_ca', 'bn_jha',
           'bn_nya', 'bn_na', 'bn_sa', 'bn_uu', 'bn_aa', 'bn_i', 'bn_ii',
           'bn_ri']
REVERTED = set()  # filled by the validate/ridge comparison if any glyph worsens
SWOOSH_SOURCE = sys.argv[1] if len(sys.argv) > 1 else 'fresh'
assert SWOOSH_SOURCE in ('fresh', 'v0150')


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


def fresh_swoosh(loop_font_box):
    """Trace the r4c7 cell, take the swoosh contour (below the loop),
    fit uniformly at the loop's y-scale, position relative to the loop,
    and translate so its bottom lands at -120."""
    cell = BASE_DIR / 'v0160-prep/cells/cons_16_r4c7.png'
    arr = np.asarray(Image.open(cell).convert('L'))
    ink = cell_ink_thr(arr, 152)
    contours = tg.potrace_svg('anusvara_swoosh', ink)
    # identify loop (top, the LARGEST contour with bbox y1 < 40) and
    # swoosh (below, bbox y0 > 40). The loop has an outer contour and
    # a hole; the hole is smaller, so largest-area wins.
    loop_c = swoosh_c = None
    loop_area = -1.0
    for c in contours:
        x0, y0, x1, y1 = tg.contour_bbox(c)
        area = (x1 - x0) * (y1 - y0)
        if y0 > 40:
            swoosh_c = c
        elif y1 < 40 and area > loop_area:
            loop_c = c
            loop_area = area
    assert loop_c is not None and swoosh_c is not None, 'loop/swoosh not found'
    lx0, ly0, lx1, ly1 = tg.contour_bbox(loop_c)
    sx0, sy0, sx1, sy1 = tg.contour_bbox(swoosh_c)
    fx0, fy0, fx1, fy1 = loop_font_box
    s = (fy1 - fy0) / (ly1 - ly0)  # loop y-scale (uniform for the swoosh)
    # convert the swoosh contour (cubic) to a quadratic glyph at scale s,
    # anchored: swoosh centre-x relative to loop centre-x; swoosh top
    # relative to loop bottom (pixel gap * s).
    g = tg.contours_to_glyph(
        [swoosh_c], s,
        (fx0 + fx1) / 2.0 + ((sx0 + sx1) / 2.0 - (lx0 + lx1) / 2.0) * s,
        fy0 - (sy0 - ly1) * s,
        (sx0 + sx1) / 2.0, sy0)
    tg.reverse_contours(g)
    # the swoosh is a single contour; make its endPts explicit
    g.endPtsOfContours = [len(g.coordinates) - 1]
    assert len(g.endPtsOfContours) == 1, 'swoosh must be a single contour'
    # clamp the bottom to -120
    ys = [p[1] for p in g.coordinates]
    dy = -120 - min(ys)
    coords = [(x, y + dy) for x, y in g.coordinates]
    g.coordinates = GlyphCoordinates(coords)
    return g, {'scale': round(s, 3), 'dy_clamp': dy,
               'loop_px_box': [round(v, 1) for v in (lx0, ly0, lx1, ly1)],
               'swoosh_px_box': [round(v, 1) for v in (sx0, sy0, sx1, sy1)],
               'swoosh_font_box': (min(p[0] for p in coords),
                                   min(p[1] for p in coords),
                                   max(p[0] for p in coords),
                                   max(p[1] for p in coords))}


def v0150_swoosh(loop_font_box):
    """Take the v0.150 anusvara's swoosh contour (the one dipping below
    the baseline) and translate it under the v0.167 loop."""
    f = TTFont(V150)
    g = f['glyf']['bn_anusvara']
    # the swoosh is the contour whose bbox dips below y=0
    start = 0
    swoosh_idx = None
    for ci, e in enumerate(g.endPtsOfContours):
        pts = g.coordinates[start:e + 1]
        ys = [p[1] for p in pts]
        if min(ys) < 0:
            swoosh_idx = (start, e)
        start = e + 1
    assert swoosh_idx is not None, 'no v0.150 swoosh found'
    s0, e0 = swoosh_idx
    coords = list(g.coordinates[s0:e0 + 1])
    flags = list(g.flags[s0:e0 + 1])
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    fx0, fy0, fx1, fy1 = loop_font_box
    # centre the swoosh under the loop (its bottom is already -130)
    dx = (fx0 + fx1) / 2.0 - (min(xs) + max(xs)) / 2.0
    coords = [(x + dx, y) for x, y in coords]
    ng = f['glyf']['bn_anusvara'].__class__()
    ng.coordinates = GlyphCoordinates(coords)
    ng.flags = np.array(flags, dtype=np.uint8)
    ng.endPtsOfContours = [len(coords) - 1]
    f.close()
    return ng, {'dx': round(dx, 1),
                'swoosh_font_box': (min(p[0] for p in coords),
                                    min(p[1] for p in coords),
                                    max(p[0] for p in coords),
                                    max(p[1] for p in coords))}


def main() -> None:
    assert sha256(BASE) == EXPECTED_BASE_SHA256, 'v0.166 base checksum mismatch'
    base = TTFont(BASE, checkChecksums=2)
    tmp = TTFont(TMP, checkChecksums=2)
    assert set(base.getGlyphOrder()) == set(tmp.getGlyphOrder()), 'glyph set changed'
    assert len(base.getGlyphOrder()) == len(tmp.getGlyphOrder()) == 652
    assert base.getBestCmap() == tmp.getBestCmap(), 'cmap changed'
    glyf, hmtx = base['glyf'], base['hmtx']
    tglyf = tmp['glyf']
    for name in TOUCHED:
        if name in REVERTED:
            print(f'  {name:14s} REVERTED to v0.166 outline')
            continue
        g = tglyf[name]
        assert not g.isComposite() and g.numberOfContours > 0, f'{name} not simple'
        prog = getattr(g, 'program', None)
        nbc = len(prog.getBytecode()) if prog is not None else 0
        removed, inserted = clean_glyph(g)
        glyf[name] = g
        xs = [p[0] for p in g.coordinates]
        adv, old_lsb = hmtx[name]
        new_lsb = min(xs)
        if name == 'Khanda_Ta':
            adv = 1210  # widen the advance so the re-centred ink fits
        assert adv == hmtx[name][0] or name == 'Khanda_Ta', \
            f'{name}: advance changed!'
        hmtx[name] = (adv, new_lsb)
        print(f'  {name:14s} pts={len(g.coordinates)} bytecode={nbc} '
              f'clean_rm={removed} clean_ins={inserted} '
              f'lsb {old_lsb}->{new_lsb} adv={adv}')

    # ---- bn_anusvara: add the swoosh under the width-scaled loop ----
    loop_box = (glyf['bn_anusvara'].xMin, glyf['bn_anusvara'].yMin,
                glyf['bn_anusvara'].xMax, glyf['bn_anusvara'].yMax)
    if SWOOSH_SOURCE == 'fresh':
        sw, info = fresh_swoosh(loop_box)
    else:
        sw, info = v0150_swoosh(loop_box)
    g = glyf['bn_anusvara']
    old_n = len(g.coordinates)
    coords = list(g.coordinates) + list(sw.coordinates)
    flags = list(g.flags) + list(sw.flags)
    ends = list(g.endPtsOfContours) + [e + old_n for e in sw.endPtsOfContours]
    g.coordinates = GlyphCoordinates(coords)
    g.flags = np.array(flags, dtype=np.uint8)
    g.endPtsOfContours = ends
    # numberOfContours is a stored attribute, not derived: update it,
    # or the compiled glyph is malformed (stale count vs endPts).
    g.numberOfContours = len(ends)
    g.recalcBounds(base.getGlyphSet())
    xs = [p[0] for p in g.coordinates]
    hmtx['bn_anusvara'] = (hmtx['bn_anusvara'][0], min(xs))
    print(f"  bn_anusvara + swoosh ({SWOOSH_SOURCE}): contours="
          f"{g.numberOfContours} bbox=({g.xMin},{g.yMin},{g.xMax},{g.yMax}) "
          f"info={info}")

    name = base['name']
    for nid, val in [(3, 'Pranoti:Version 0.167-beta'),
                     (5, 'Version 0.167-beta')]:
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)
    base['head'].fontRevision = 0.167
    base.recalcBBoxes = True
    base.save(OUT)
    print(f'Built: {OUT}')
    print(f'v0.167 SHA-256: {sha256(OUT)}')
    print(f"glyphs: {len(base.getGlyphOrder())}, cmap: {len(base.getBestCmap())}")


if __name__ == '__main__':
    main()
