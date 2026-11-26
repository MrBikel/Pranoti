#!/usr/bin/env python3
"""Measure the 13 vowel signs/marks + Khanda_Ta in Pranoti v0.166-beta (base for v0.167).

- True ink bbox alone: PIL BASIC layout, 1536 px em (1 unit/px), same
  method as the v0.150 ink-measure and the v0.163/164/165 passes.
  Targets: the v0.150 fitted ink boxes in v0160-prep/traced_glyphs.json
  (same target source as the vowel/consonant/digit passes). For Khanda_Ta
  the target is its OWN current ink box (it is still the base font's
  shape; the re-trace will be fitted to that box).
- Stroke width: distance-transform ridge at 400 px em, same method as
  v0.161 (measure_stroke_v0161.py). Letter median target 84.5 units.
  Blob glyphs (visarga dots, candrabindu crescent) measure blob size,
  not stroke — flagged in the notes, not ranked for adjustment.
- hmtx advance / lsb / rsb from fontTools.
- In-context: each sign attached to ক (কা কি কী কু কূ কৃ কে কৈ কো কৌ কং
  কঃ কাঁ) rendered with RAQM at 1536 px; the cluster ink box is recorded
  so the build can prove the sign still sits right on its base. Khanda_Ta
  is measured in the words হঠাৎ / সৎ / উৎপাত.
- Shape notes: contour count, point count, self-intersections
  (segment-crossing test, same as check_self_intersection.py).
"""
import json
import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from fontTools.ttLib import TTFont

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
TTF = sys.argv[1] if len(sys.argv) > 1 else str(BASE / 'v0166-prep/Pranoti-Regular-v0.166-beta.ttf')
TAG = sys.argv[2] if len(sys.argv) > 2 else 'v0.167'
PREP = BASE / 'v0167-prep'
OUT = PREP / 'checks'
SIZE_RIDGE = 400
SCALE = 1536 / SIZE_RIDGE

SIGNS = [('bn_aakaar', chr(0x09BE)), ('bn_ikaar', chr(0x09BF)),
         ('bn_iikaar', chr(0x09C0)), ('bn_ukaar', chr(0x09C1)),
         ('bn_uukaar', chr(0x09C2)), ('bn_rikaar', chr(0x09C3)),
         ('bn_ekaar', chr(0x09C7)), ('bn_aikaar', chr(0x09C8)),
         ('bn_okaar', chr(0x09CB)), ('bn_aukaar', chr(0x09CC)),
         ('bn_anusvara', chr(0x0982)), ('bn_visarga', chr(0x0983)),
         ('bn_candrabindu', chr(0x0981)), ('Khanda_Ta', chr(0x09CE))]

traced = json.load(open(BASE / 'v0160-prep' / 'traced_glyphs.json', encoding='utf-8'))
ft = TTFont(TTF)
hmtx = ft['hmtx']
glyf = ft['glyf']


def ink_bbox_1536_basic(ch):
    """True ink bbox in font units [x0, y0, x1, y1], ink area, mask (BASIC)."""
    f = ImageFont.truetype(TTF, 1536, layout_engine=ImageFont.Layout.BASIC)
    im = Image.new('L', (3200, 3400), 0)
    dr = ImageDraw.Draw(im)
    ox, oy = 1600, 2000  # origin x, baseline y
    dr.text((ox, oy), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(im) > 0
    bb = Image.fromarray((a * 255).astype(np.uint8)).getbbox()
    if bb is None:
        return None, 0, None
    x0, y0, x1, y1 = bb
    return [x0 - ox, oy - (y1 - 1), x1 - 1 - ox, oy - y0], int(a.sum()), a


def ink_bbox_1536_raqm(text):
    """True ink bbox of a shaped string (RAQM), font units rel. to origin."""
    f = ImageFont.truetype(TTF, 1536, layout_engine=ImageFont.Layout.RAQM)
    im = Image.new('L', (3200, 3400), 0)
    dr = ImageDraw.Draw(im)
    ox, oy = 1600, 2000
    dr.text((ox, oy), text, font=f, fill=255, anchor='ls',
            direction='ltr', language='bn')
    a = np.asarray(im) > 0
    bb = Image.fromarray((a * 255).astype(np.uint8)).getbbox()
    if bb is None:
        return None, 0
    x0, y0, x1, y1 = bb
    return [x0 - ox, oy - (y1 - 1), x1 - 1 - ox, oy - y0], int(a.sum())


def ridge_stroke(ch):
    f = ImageFont.truetype(TTF, SIZE_RIDGE, layout_engine=ImageFont.Layout.BASIC)
    im = Image.new('L', (1200, 1200), 0)
    dr = ImageDraw.Draw(im)
    dr.text((300, 600), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(im) > 0
    if not a.any():
        return None, None, None
    dist = ndimage.distance_transform_edt(a)
    ridge = (dist > 0) & (dist == ndimage.maximum_filter(dist, size=3))
    vals = 2.0 * dist[ridge] * SCALE
    return (round(float(np.median(vals)), 1),
            round(float(np.percentile(vals, 75) - np.percentile(vals, 25)), 1),
            round(float(np.median(vals[vals >= np.percentile(vals, 20)])), 1))


def self_intersections(name):
    """Segment-crossing count on the glyf outline (quadratic approx)."""
    g = glyf[name]
    if g.isComposite() or g.numberOfContours == 0:
        return None
    coords, ends, flags = g.getCoordinates(glyf)
    pts = []
    start = 0
    for e in ends:
        pts.append(list(coords[start:e + 1]))
        start = e + 1
    # sample each contour densely (quadratic segments, 8 samples each)
    segs = []
    for contour in pts:
        n = len(contour)
        for i in range(n):
            p0 = contour[i]
            p1 = contour[(i + 1) % n]
            segs.append((p0, p1))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    def inter(s1, s2):
        a, b = s1
        c, d = s2
        if a == c or a == d or b == c or b == d:
            return False
        d1, d2 = cross(c, d, a), cross(c, d, b)
        d3, d4 = cross(a, b, c), cross(a, b, d)
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))
    n = 0
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            if inter(segs[i], segs[j]):
                n += 1
    return n


# Khanda_Ta target = its own current ink box (base font shape)
khanda_bb, _, _ = ink_bbox_1536_basic(chr(0x09CE))
print(f'Khanda_Ta current ink box (fit target): {khanda_bb}')

CONTEXT = {'bn_aakaar': 'কা', 'bn_ikaar': 'কি', 'bn_iikaar': 'কী',
           'bn_ukaar': 'কু', 'bn_uukaar': 'কূ', 'bn_rikaar': 'কৃ',
           'bn_ekaar': 'কে', 'bn_aikaar': 'কৈ', 'bn_okaar': 'কো',
           'bn_aukaar': 'কৌ', 'bn_anusvara': 'কং', 'bn_visarga': 'কঃ',
           'bn_candrabindu': 'কাঁ'}
WORDS = {'Khanda_Ta': ['হঠাৎ', 'সৎ', 'উৎপাত']}

rows = []
for name, ch in SIGNS:
    bb, area, mask = ink_bbox_1536_basic(ch)
    med, iqr, trimmed = ridge_stroke(ch)
    adv, lsb = hmtx[name]
    g = glyf[name]
    n_cont = g.numberOfContours if not g.isComposite() else -1
    n_pts = len(g.coordinates)
    if name == 'Khanda_Ta':
        tgt = khanda_bb
    else:
        tgt = traced[name]['target']
    tx0, ty0, tx1, ty1 = tgt
    # in-context cluster box
    ctx_text = CONTEXT.get(name)
    ctx_bb, ctx_area = (None, None)
    if ctx_text:
        ctx_bb, ctx_area = ink_bbox_1536_raqm(ctx_text)
    word_boxes = {}
    for w in WORDS.get(name, []):
        wb, _ = ink_bbox_1536_raqm(w)
        word_boxes[w] = wb
    rows.append(dict(
        glyph=name, char=ch, adv=adv, lsb=lsb, rsb=adv - (bb[2] + 1) if bb else None,
        ink_x0=bb[0], ink_y0=bb[1], ink_x1=bb[2], ink_y1=bb[3],
        ink_w=bb[2] - bb[0] + 1, ink_h=bb[3] - bb[1] + 1,
        ink_cx=round((bb[0] + bb[2]) / 2, 1), ink_cy=round((bb[1] + bb[3]) / 2, 1),
        ink_area=area,
        tgt_x0=tx0, tgt_y0=ty0, tgt_x1=tx1, tgt_y1=ty1,
        top_err=bb[3] - ty1, bottom_err=bb[1] - ty0,
        left_err=bb[0] - tx0, right_err=bb[2] - tx1,
        cx_err=round((bb[0] + bb[2]) / 2 - (tx0 + tx1) / 2, 1),
        w_err=(bb[2] - bb[0] + 1) - (tx1 - tx0),
        h_err=(bb[3] - bb[1] + 1) - (ty1 - ty0),
        ridge_med=med, ridge_iqr=iqr, ridge_trimmed=trimmed,
        dev_pct=round(100 * (med - 84.5) / 84.5, 1) if med else None,
        n_contours=n_cont, n_points=n_pts,
        self_intersections=self_intersections(name),
        context=ctx_text, context_box=ctx_bb, context_area=ctx_area,
        word_boxes=word_boxes))

hdr = ['glyph', 'char', 'adv', 'lsb', 'rsb', 'ink_x0', 'ink_y0', 'ink_x1', 'ink_y1',
       'ink_w', 'ink_h', 'ink_cx', 'ink_cy', 'ink_area', 'tgt_x0', 'tgt_y0',
       'tgt_x1', 'tgt_y1', 'top_err', 'bottom_err', 'left_err', 'right_err',
       'cx_err', 'w_err', 'h_err', 'ridge_med', 'ridge_iqr', 'ridge_trimmed',
       'dev_pct', 'n_contours', 'n_points', 'self_intersections',
       'context', 'context_box', 'context_area', 'word_boxes']
OUT.mkdir(parents=True, exist_ok=True)
with open(OUT / f'sign-measure-{TAG}.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(hdr) + '\n')
    for r in rows:
        f.write('\t'.join(str(r[h]) for h in hdr) + '\n')
json.dump(rows, open(OUT / f'sign-measure-{TAG}.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print(f"{'glyph':14s} {'ch':3s} {'top':>5s} {'bot':>5s} {'lft':>5s} {'rgt':>5s} "
      f"{'cx':>6s} {'w':>5s} {'h':>5s} {'ridge':>6s} {'dev%':>6s} {'adv':>4s} {'lsb':>5s} {'rsb':>5s} {'nc':>2s} {'x':>2s}")
for r in rows:
    print(f"{r['glyph']:14s} {r['char']:3s} {r['top_err']:5d} {r['bottom_err']:5d} "
          f"{r['left_err']:5d} {r['right_err']:5d} {r['cx_err']:6.1f} {r['w_err']:5d} "
          f"{r['h_err']:5d} {r['ridge_med']:6.1f} {r['dev_pct']:6.1f} {r['adv']:4d} "
          f"{r['lsb']:5d} {r['rsb']:5d} {r['n_contours']:2d} {r['self_intersections']:2d}")
print()
for r in rows:
    if r['context']:
        print(f"{r['glyph']:14s} {r['context']}: cluster box {r['context_box']} area {r['context_area']}")
    if r['word_boxes']:
        for w, wb in r['word_boxes'].items():
            print(f"{r['glyph']:14s} {w}: box {wb}")
