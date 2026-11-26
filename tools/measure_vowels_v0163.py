#!/usr/bin/env python3
"""Measure all 11 independent vowels in Pranoti v0.162-beta (base for v0.163).

- True ink bbox: PIL BASIC layout, 1536 px em (1 unit/px), same method as
  the v0.150 ink-measure. Targets: AdorshoLipi ink bboxes from
  v0150-prep/ink-measure.json ("ado" bbox: [x0, y0, x1, y1]).
- Stroke width: distance-transform ridge at 400 px em, same method as
  v0.161 (measure_stroke_v0161.py). Letter median target 84.5 units.
- hmtx advance / lsb / rsb from fontTools.
- Lean: ink centroid-x of the top quarter vs the bottom quarter of the
  ink height (a slant check for tall vowels).
- Shape notes: contour count, point count, degenerate (zero-area) contours.
"""
import json
import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from fontTools.ttLib import TTFont

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
TTF = sys.argv[1] if len(sys.argv) > 1 else str(BASE / 'v0162-prep/Pranoti-Regular-v0.162-beta.ttf')
TAG = sys.argv[2] if len(sys.argv) > 2 else 'v0.162'
PREP = BASE / 'v0163-prep'
OUT = PREP / 'checks'
SIZE_RIDGE = 400
SCALE = 1536 / SIZE_RIDGE

VOWELS = [('bn_a', 'অ'), ('bn_aa', 'আ'), ('bn_i', 'ই'), ('bn_ii', 'ঈ'),
          ('bn_u', 'উ'), ('bn_uu', 'ঊ'), ('bn_ri', 'ঋ'), ('bn_e', 'এ'),
          ('bn_ai', 'ঐ'), ('bn_o', 'ও'), ('bn_au', 'ঔ')]

ado = json.load(open(BASE / 'v0150-prep/ink-measure.json', encoding='utf-8'))
ft = TTFont(TTF)
hmtx = ft['hmtx']
glyf = ft['glyf']


def ink_bbox_1536(ch):
    """True ink bbox in font units: [x0, y0, x1, y1], plus ink area (px)."""
    f = ImageFont.truetype(TTF, 1536, layout_engine=ImageFont.Layout.BASIC)
    im = Image.new('L', (2600, 3000), 0)
    dr = ImageDraw.Draw(im)
    ox, oy = 300, 2200  # origin x, baseline y
    dr.text((ox, oy), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(im) > 0
    bb = Image.fromarray((a * 255).astype(np.uint8)).getbbox()
    if bb is None:
        return None, 0, None
    x0, y0, x1, y1 = bb
    # PIL y grows down; baseline at oy; font y = oy - py; x1/y1 exclusive
    return [x0 - ox, oy - (y1 - 1), x1 - 1 - ox, oy - y0], int(a.sum()), a


def ridge_stroke(ch):
    f = ImageFont.truetype(TTF, SIZE_RIDGE, layout_engine=ImageFont.Layout.BASIC)
    im = Image.new('L', (900, 1100), 0)
    dr = ImageDraw.Draw(im)
    dr.text((100, 550), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(im) > 0
    if not a.any():
        return None, None, None
    dist = ndimage.distance_transform_edt(a)
    ridge = (dist > 0) & (dist == ndimage.maximum_filter(dist, size=3))
    vals = 2.0 * dist[ridge] * SCALE
    return (round(float(np.median(vals)), 1),
            round(float(np.percentile(vals, 75) - np.percentile(vals, 25)), 1),
            round(float(np.median(vals[vals >= np.percentile(vals, 20)])), 1))


rows = []
for name, ch in VOWELS:
    bb, area, mask = ink_bbox_1536(ch)
    med, iqr, trimmed = ridge_stroke(ch)
    adv, lsb = hmtx[name]
    g = glyf[name]
    n_cont = g.numberOfContours if not g.isComposite() else -1
    n_pts = len(g.coordinates)
    t = ado[name]['ado']
    tx0, ty0, tx1, ty1 = t['bbox']
    tarea = t['area']
    # lean: centroid-x of top vs bottom quarter of ink height
    lean = None
    if mask is not None:
        ys, xs = np.nonzero(mask)
        # convert mask coords to font coords: x = px-300, y = 2200-py
        fy = 2200 - ys
        fx = xs - 300
        h = bb[3] - bb[1]
        top = fx[fy >= bb[3] - h / 4]
        bot = fx[fy <= bb[1] + h / 4]
        if len(top) and len(bot):
            lean = round(float(np.mean(top) - np.mean(bot)), 1)
    rows.append(dict(
        glyph=name, char=ch, adv=adv, lsb=lsb, rsb=adv - (bb[2] + 1) if bb else None,
        ink_x0=bb[0], ink_y0=bb[1], ink_x1=bb[2], ink_y1=bb[3],
        ink_w=bb[2] - bb[0] + 1, ink_h=bb[3] - bb[1] + 1,
        ink_cx=round((bb[0] + bb[2]) / 2, 1), ink_cy=round((bb[1] + bb[3]) / 2, 1),
        ink_area=area,
        ado_top=ty1, ado_bottom=ty0, ado_cx=round((tx0 + tx1) / 2, 1),
        ado_w=tx1 - tx0, ado_h=ty1 - ty0, ado_area=tarea,
        top_err=bb[3] - ty1, bottom_err=bb[1] - ty0,
        cx_err=round((bb[0] + bb[2]) / 2 - (tx0 + tx1) / 2, 1),
        w_err=(bb[2] - bb[0] + 1) - (tx1 - tx0),
        h_err=(bb[3] - bb[1] + 1) - (ty1 - ty0),
        area_ratio=round(area / tarea, 3),
        ridge_med=med, ridge_iqr=iqr, ridge_trimmed=trimmed,
        dev_pct=round(100 * (med - 84.5) / 84.5, 1) if med else None,
        lean=lean, n_contours=n_cont, n_points=n_pts))

hdr = ['glyph', 'char', 'adv', 'lsb', 'rsb', 'ink_x0', 'ink_y0', 'ink_x1', 'ink_y1',
       'ink_w', 'ink_h', 'ink_cx', 'ink_cy', 'ink_area', 'ado_top', 'ado_bottom',
       'ado_cx', 'ado_w', 'ado_h', 'ado_area', 'top_err', 'bottom_err', 'cx_err',
       'w_err', 'h_err', 'area_ratio', 'ridge_med', 'ridge_iqr', 'ridge_trimmed',
       'dev_pct', 'lean', 'n_contours', 'n_points']
with open(OUT / f'vowel-measure-{TAG}.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(hdr) + '\n')
    for r in rows:
        f.write('\t'.join(str(r[h]) for h in hdr) + '\n')
json.dump(rows, open(OUT / f'vowel-measure-{TAG}.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print(f"{'glyph':8s} {'ch':3s} {'top_err':>7s} {'bot_err':>7s} {'cx_err':>6s} {'w_err':>5s} "
      f"{'h_err':>5s} {'area':>5s} {'ridge':>6s} {'dev%':>6s} {'lean':>5s} {'adv':>4s} {'lsb':>4s} {'rsb':>4s} {'nc':>2s}")
for r in rows:
    print(f"{r['glyph']:8s} {r['char']:3s} {r['top_err']:7d} {r['bottom_err']:7d} {r['cx_err']:6.1f} "
          f"{r['w_err']:5d} {r['h_err']:5d} {r['area_ratio']:5.3f} {r['ridge_med']:6.1f} "
          f"{r['dev_pct']:6.1f} {r['lean']:5.1f} {r['adv']:4d} {r['lsb']:4d} {r['rsb']:4d} {r['n_contours']:2d}")
