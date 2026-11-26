#!/usr/bin/env python3
"""Render re-trace candidates for ঞ and স, fitted to their v0.166 boxes,
so the cleanest trace can be chosen by eye.

Candidates: bn_nya photo16@178 (current), photo16@193, photo17@160;
bn_sa photo16@174 (current), photo16@189.
Fit: uniform scale to the v0.166 glyf bbox height, centre-x + top
(v0.160 letter rule). Draws the fitted quadratic outlines filled.
"""
import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0160-prep/tools')
import trace_glyphs as tg

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
CELLS = BASE / 'v0160-prep/cells'
PREP167 = BASE / 'v0167-prep'
V166 = BASE / 'v0166-prep/Pranoti-Regular-v0.166-beta.ttf'
DEJA = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


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
    return a fontTools Glyph (quadratic, reversed winding)."""
    arr = np.asarray(Image.open(cell_path).convert('L'))
    ink = cell_ink_thr(arr, thr)
    contours = tg.potrace_svg(cell_path.stem + f'_fit{thr}', ink)
    tx0, ty0, tx1, ty1 = tg.true_bbox(contours)
    gx0, gy0, gx1, gy1 = target_box
    s = (gy1 - gy0) / (ty1 - ty0)
    glyph = tg.contours_to_glyph(contours, s, (gx0 + gx1) / 2.0, gy1,
                                 (tx0 + tx1) / 2.0, ty0)
    tg.reverse_contours(glyph)
    return glyph, len(contours)


class FlatPen(BasePen):
    def __init__(self, glyphSet):
        super().__init__(glyphSet)
        self.polys = []
        self.cur = []
    def _moveTo(self, p):
        self._flush(); self.cur = [p]
    def _lineTo(self, p):
        self.cur.append(p)
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for k in range(1, 9):
            t = k / 8; mt = 1 - t
            self.cur.append((mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * p2[0] + t**3 * p3[0],
                             mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * p2[1] + t**3 * p3[1]))
    def _closePath(self):
        self._flush()
    def _endPath(self):
        self._flush()
    def _flush(self):
        if len(self.cur) > 2:
            self.polys.append(self.cur)
        self.cur = []


def draw_glyph(glyph, size=380):
    """Draw a fontTools glyph (coords in font units) fitted into a square."""
    xs = [p[0] for p in glyph.coordinates]
    ys = [p[1] for p in glyph.coordinates]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    sc = (size - 40) / max(x1 - x0, y1 - y0)
    im = Image.new('RGB', (size, size), 'white')
    d = ImageDraw.Draw(im)
    # draw via glyphPen-like flattening: use the coordinates directly
    pen = FlatPen(None)
    # rebuild polygons from the glyph's own contours
    start = 0
    for e in glyph.endPtsOfContours:
        pts = list(glyph.coordinates[start:e + 1])
        flags = list(glyph.flags[start:e + 1])
        # expand quadratics: walk points, off-curve = control
        poly = []
        n = len(pts)
        for i in range(n):
            p = pts[i]
            f = flags[i]
            if f & 1:
                poly.append((float(p[0]), float(p[1])))
            else:
                # quadratic: sample from prev on-curve to next on-curve
                prev = pts[i - 1]
                nxt = pts[(i + 1) % n]
                p0 = prev if (flags[i - 1] & 1) else (
                    (prev[0] + pts[i - 2][0]) / 2, (prev[1] + pts[i - 2][1]) / 2)
                p2 = nxt if (flags[(i + 1) % n] & 1) else (
                    (nxt[0] + p[0]) / 2, (nxt[1] + p[1]) / 2)
                for k in range(1, 9):
                    t = k / 8; mt = 1 - t
                    poly.append((mt * mt * p0[0] + 2 * mt * t * p[0] + t * t * p2[0],
                                 mt * mt * p0[1] + 2 * mt * t * p[1] + t * t * p2[1]))
        start = e + 1
        if len(poly) > 2:
            d.polygon([(20 + (x - x0) * sc, size - 20 - (y - y0) * sc) for x, y in poly],
                      fill='#111820')
    return im


def current_glyph(name):
    f = TTFont(V166)
    g = f['glyf'][name]
    box = (g.xMin, g.yMin, g.xMax, g.yMax)
    f.close()
    return box


rows = []
# bn_nya candidates
box = current_glyph('bn_nya')
print('bn_nya v0.166 glyf box:', box)
for label, cell, thr in [('nya photo16@178 (current)', CELLS / 'cons_16_r1c10.png', 178),
                         ('nya photo16@193', CELLS / 'cons_16_r1c10.png', 193),
                         ('nya photo17@160', PREP167 / 'cells-17/cons_17_r1c10.png', 160)]:
    g, n = fit_trace(cell, thr, box)
    rows.append((label, g, n))
    print(f'  {label}: contours={n} pts={len(g.coordinates)}')
# bn_sa candidates
box = current_glyph('bn_sa')
print('bn_sa v0.166 glyf box:', box)
for label, cell, thr in [('sa photo16@174 (current)', CELLS / 'cons_16_r4c1.png', 174),
                         ('sa photo16@189', CELLS / 'cons_16_r4c1.png', 189)]:
    g, n = fit_trace(cell, thr, box)
    rows.append((label, g, n))
    print(f'  {label}: contours={n} pts={len(g.coordinates)}')

W = 420
H = 60 + len(rows) * 420
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
d.text((10, 8), 'Re-trace candidates, fitted to v0.166 boxes (filled outlines)',
       font=ImageFont.truetype(DEJA, 16), fill='#17202a')
y = 50
lab_f = ImageFont.truetype(DEJA, 14)
for label, g, n in rows:
    d.text((10, y), f'{label} — {n} contours', font=lab_f, fill='#17202a')
    im.paste(draw_glyph(g), (10, y + 24))
    y += 420
im.save(PREP167 / 'specimens/retrace-candidates.png', optimize=True)
print('saved specimens/retrace-candidates.png', im.size)
