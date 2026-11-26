#!/usr/bin/env python3
"""Investigation for v0.167: (a) re-trace the anusvara cell r4c7 and list
all contours (the dropped swoosh); (b) re-trace the da cell r2c8 at three
Otsu thresholds and compare outlines."""
import sys
import numpy as np
from pathlib import Path
from PIL import Image

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0160-prep/tools')
import trace_glyphs as tg

CELLS = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep/cells')


def trace_cell(cell_path, thr_override=None):
    arr = np.asarray(Image.open(cell_path).convert('L'))
    if thr_override is None:
        ink, thr, _ = tg.cell_ink(arr)
    else:
        mask = arr < thr_override
        lab, n = tg.ndimage.label(mask)
        keep = np.zeros_like(mask)
        mask100 = arr < 100
        if n:
            objs = tg.ndimage.find_objects(lab)
            for i, sl in enumerate(objs, 1):
                comp = (lab[sl] == i)
                if comp.sum() < 4:
                    continue
                if not mask100[sl][comp].any():
                    continue
                keep[sl] |= comp
        ink, thr = keep, thr_override
    contours = tg.potrace_svg(cell_path.stem + f'_t{thr}', ink)
    return ink, thr, contours


def contour_bboxes(contours):
    out = []
    for c in contours:
        x0, y0, x1, y1 = tg.contour_bbox(c)
        out.append((round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)))
    return out


print('=== anusvara cell r4c7 (Otsu 152, as v0.160) ===')
ink, thr, contours = trace_cell(CELLS / 'cons_16_r4c7.png')
print(f'thr={thr} contours={len(contours)}')
for b in contour_bboxes(contours):
    print('  pixel bbox x0,y0,x1,y1,npts =', b)
ys, xs = np.where(ink)
print(f'  full ink pixel bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]')

print('=== da cell r2c8 at three thresholds ===')
for t in (140, 164, 180):
    ink, thr, contours = trace_cell(CELLS / 'cons_16_r2c8.png', thr_override=t)
    print(f'thr={t} contours={len(contours)}')
    for b in contour_bboxes(contours):
        print('  pixel bbox x0,y0,x1,y1,npts =', b)
    ys, xs = np.where(ink)
    print(f'  full ink pixel bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}] area={int(ink.sum())}')
