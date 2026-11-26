#!/usr/bin/env python3
"""Measure the 12 touched consonants/vowels in v0.166 vs v0.167.

Same ink-bbox (PIL BASIC, 1536 px) and ridge (distance-transform,
400 px) methods as the v0.163/v0.164 passes. Compares ink width vs
the v0.120 base glyph (width ratio), ridge vs the 84.5 median
(band 71.8-97.2), and reports contour counts + self-intersections
(segment-crossing test from v0.160 check_self_intersection.py).

Glyphs: bn_da, bn_ga, bn_yya, bn_ca, bn_jha, bn_nya, bn_na, bn_sa,
bn_uu, bn_aa, bn_i, bn_ii, bn_ri.
Run: python3 tools/measure_touched_v0167.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from fontTools.ttLib import TTFont

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0161-prep/tools')
from check_self_intersection import check as check_self_int  # noqa: E402

BASE = Path('/home/hatch/workspace/fonts/bengali-hand')
V166 = BASE / 'v0166-prep/Pranoti-Regular-v0.166-beta.ttf'
V167 = BASE / 'v0167-prep/Pranoti-Regular-v0.167-beta.ttf'
V120 = BASE / 'github-repo/Pranoti-Regular-v0.120-Private-Owner-Review.ttf'
OUT = BASE / 'v0167-prep/checks/touched-measure-v0.167.tsv'
SIZE_RIDGE = 400
SCALE = 1536 / SIZE_RIDGE

GLYPHS = [('bn_da', 'দ'), ('bn_ga', 'গ'), ('bn_yya', chr(0x09DF)),
          ('bn_ca', 'চ'),
          ('bn_jha', 'ঝ'), ('bn_nya', 'ঞ'), ('bn_na', 'ন'), ('bn_sa', 'স'),
          ('bn_uu', 'ঊ'), ('bn_aa', 'আ'), ('bn_i', 'ই'), ('bn_ii', 'ঈ'),
          ('bn_ri', 'ঋ')]


def ink_bbox_1536(ttf, ch):
    f = ImageFont.truetype(str(ttf), 1536, layout_engine=ImageFont.Layout.BASIC)
    im = Image.new('L', (2600, 3000), 0)
    dr = ImageDraw.Draw(im)
    ox, oy = 300, 2200
    dr.text((ox, oy), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(im) > 0
    bb = Image.fromarray((a * 255).astype(np.uint8)).getbbox()
    if bb is None:
        return None, 0
    x0, y0, x1, y1 = bb
    return [x0 - ox, oy - (y1 - 1), x1 - 1 - ox, oy - y0], int(a.sum())


def ridge_stroke(ttf, ch):
    f = ImageFont.truetype(str(ttf), SIZE_RIDGE, layout_engine=ImageFont.Layout.BASIC)
    im = Image.new('L', (900, 1100), 0)
    dr = ImageDraw.Draw(im)
    dr.text((100, 550), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(im) > 0
    if not a.any():
        return None, None
    dist = ndimage.distance_transform_edt(a)
    ridge = (dist > 0) & (dist == ndimage.maximum_filter(dist, size=3))
    vals = 2.0 * dist[ridge] * SCALE
    return round(float(np.median(vals)), 1), round(float(np.percentile(vals, 75) - np.percentile(vals, 25)), 1)


def measure(ttf):
    ft = TTFont(ttf)
    out = {}
    for name, ch in GLYPHS:
        bb, area = ink_bbox_1536(ttf, ch)
        med, iqr = ridge_stroke(ttf, ch)
        g = ft['glyf'][name]
        out[name] = dict(char=ch, adv=ft['hmtx'][name][0],
                         ink=bb, ink_w=bb[2] - bb[0] + 1,
                         ink_h=bb[3] - bb[1] + 1, area=area,
                         ridge_med=med, ridge_iqr=iqr,
                         n_contours=g.numberOfContours,
                         n_points=len(g.coordinates),
                         self_int=check_self_int(ft, name))
    ft.close()
    return out


def main():
    m166 = measure(V166)
    m167 = measure(V167)
    m120 = measure(V120)
    rows = ['glyph\tchar\tadv\tink_w_166\tink_w_167\tink_w_120\twidth_ratio_167\t'
            'ink_h_166\tink_h_167\ttop_166\ttop_167\tridge_166\tridge_167\t'
            'dev_pct_167\tcontours_166\tcontours_167\tself_int_166\tself_int_167']
    for name, ch in GLYPHS:
        a, b, c = m166[name], m167[name], m120[name]
        ratio = round(b['ink_w'] / c['ink_w'], 3) if c['ink_w'] else None
        dev = round(100 * (b['ridge_med'] - 84.5) / 84.5, 1) if b['ridge_med'] else None
        rows.append('\t'.join(map(str, [
            name, ch, b['adv'], a['ink_w'], b['ink_w'], c['ink_w'], ratio,
            a['ink_h'], b['ink_h'], a['ink'][3], b['ink'][3],
            a['ridge_med'], b['ridge_med'], dev,
            a['n_contours'], b['n_contours'], a['self_int'], b['self_int']])))
        print(f"{name:8s} {ch} w {a['ink_w']}->{b['ink_w']} (base {c['ink_w']}, "
              f"ratio {ratio}) h {a['ink_h']}->{b['ink_h']} top {a['ink'][3]}->{b['ink'][3]} "
              f"ridge {a['ridge_med']}->{b['ridge_med']} (dev {dev}%) "
              f"contours {a['n_contours']}->{b['n_contours']} self-int {a['self_int']}->{b['self_int']}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(rows) + '\n', encoding='utf-8')
    json.dump({'v0.166': m166, 'v0.167': m167, 'v0.120': m120},
              open(str(OUT).replace('.tsv', '.json'), 'w'), indent=1)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
