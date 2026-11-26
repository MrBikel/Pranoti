#!/usr/bin/env python3
"""Re-trace faded consonant cells for v0.167 at LOWER Otsu thresholds.

Targets: bn_nya (ঞ, r1c10 — faded, thin wispy strokes), bn_na (ন, r2c10 —
connecting diagonal faded, loop detached), bn_sa (স, r4c1 — middle
strokes faded thin, hook a sharp V).

For each cell and each threshold: threshold + potrace (v0.160 method),
print contour count, per-contour pixel bboxes, ink area and a stroke
estimate. The v0.160 cell_ink filter (keep only components touching the
thr=100 mask) is kept, so grey smudges/creases are excluded.
Also tries photo 17's r1c10 cell for ঞ (extracted with the same grid
detector; photo 17's left edge carries a dark strip — handled below).
"""
import sys
import numpy as np
from pathlib import Path
from PIL import Image

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0160-prep/tools')
import trace_glyphs as tg
from grid_detect import detect

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
CELLS = BASE / 'v0160-prep/cells'
PHOTOS = Path('/home/hatch/workspace/user/files')
PREP167 = BASE / 'v0167-prep'


def cell_ink_thr(arr, thr):
    mask = arr < thr
    mask100 = arr < 100
    lab, n = tg.ndimage.label(mask)
    keep = np.zeros_like(mask)
    if n:
        objs = tg.ndimage.find_objects(lab)
        for i, sl in enumerate(objs, 1):
            comp = (lab[sl] == i)
            if comp.sum() < 4:
                continue
            if not mask100[sl][comp].any():
                continue
            keep[sl] |= comp
    return keep


def trace_cell(cell_path, thr):
    arr = np.asarray(Image.open(cell_path).convert('L'))
    ink = cell_ink_thr(arr, thr)
    contours = tg.potrace_svg(cell_path.stem + f'_t{thr}', ink)
    bboxes = [tuple(round(v, 1) for v in tg.contour_bbox(c)) for c in contours]
    dist = tg.ndimage.distance_transform_edt(ink)
    stroke = float(4 * np.median(dist[ink])) if ink.any() else 0.0
    return dict(thr=thr, n=len(contours), bboxes=bboxes,
                area=int(ink.sum()), stroke_px=round(stroke, 2))


print('=== bn_nya (ঞ) photo 16 r1c10, Otsu was 178 ===')
for t in (150, 160, 170, 178):
    print(t, trace_cell(CELLS / 'cons_16_r1c10.png', t))

print('=== bn_na (ন) photo 16 r2c10 ===')
import json as _json
_traced = _json.load(open(BASE / 'v0160-prep/traced_glyphs.json'))
print('v0.160 otsu for bn_na:', _traced['bn_na']['otsu'])
for t in (130, 140, 150, 160):
    print(t, trace_cell(CELLS / 'cons_16_r2c10.png', t))

print('=== bn_sa (স) photo 16 r4c1, Otsu was 174 ===')
print('v0.160 otsu for bn_sa:', _traced['bn_sa']['otsu'])
for t in (140, 150, 160, 174):
    print(t, trace_cell(CELLS / 'cons_16_r4c1.png', t))

print('=== bn_nya (ঞ) photo 17 r1c10 ===')
try:
    shape, bands, cells, grid = detect(str(PHOTOS / '1000038366_17_xf5r.jpg'))
    print(f'photo17: shape={shape} bands={len(bands)} cells={len(cells)}')
    by_band = {}
    for (bi, ci, x0, y0, x1, y1) in cells:
        by_band.setdefault(bi, []).append((ci, x0, y0, x1, y1))
    for bi in sorted(by_band):
        print(f'  band {bi}: {len(by_band[bi])} cells, x-ranges:',
              [(c[1], c[3]) for c in sorted(by_band[bi])][:12])
    # row 1 (band 0) should be ক খ গ ঘ ঙ চ ছ জ ঝ ঞ (10 cells); take the
    # rightmost cell as r1c10 (the dark strip adds a cell at the LEFT).
    band0 = sorted(by_band[0])
    print('  band0 cells (ci,x0,x1):', [(c[0], c[1], c[3]) for c in band0])
    ci, x0, y0, x1, y1 = band0[-1]
    im = Image.open(PHOTOS / '1000038366_17_xf5r.jpg').convert('L')
    W, H = im.size
    pad = 8
    crop = im.crop((max(0, x0 - pad), max(0, y0 - pad),
                    min(W, x1 + 1 + pad), min(H, y1 + 1 + pad)))
    out = PREP167 / 'cells-17' / 'cons_17_r1c10.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    crop.save(out)
    print('  saved', out, crop.size)
    for t in (150, 160, 170):
        print('  photo17 thr', t, trace_cell(out, t))
except Exception as e:
    print('  photo 17 extraction FAILED:', type(e).__name__, e)
