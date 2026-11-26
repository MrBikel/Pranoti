#!/usr/bin/env python3
"""Inventory + measure ALL punctuation glyphs in Pranoti v0.161-beta.

For each punctuation glyph: source (John's handwriting from v0.160 vs base
font), advance, side bearings, rasterised TRUE ink bbox (1536 px em, PIL
BASIC — the v0.160 lesson: glyf header bboxes include off-curve overshoot),
connected-component analysis (dot diameters for the dot family), and ridge
stroke width (EDT medial axis at 400 px em, same estimator as
v0160-prep/weight/measure_stroke_v0160.py) for stroke-like glyphs.

Reference: letter stroke median 84.5 units, headline y=1157, baseline 0,
UPM 1536.
"""
import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from fontTools.ttLib import TTFont

PREP = Path('/home/hatch/workspace/fonts/bengali-hand/v0162-prep')
BASE = Path('/home/hatch/workspace/fonts/bengali-hand/v0162-prep')
TTF = str(BASE / 'Pranoti-Regular-v0.162-beta.ttf')

# glyph name -> source
HAND = ['danda', 'period', 'comma', 'semicolon', 'colon', 'hyphen',
        'emdash', 'slash', 'quoteleft', 'quoteright', 'quotedblleft',
        'quotedblright', 'question', 'exclam']
BASE_GLYPHS = ['quotedbl', 'quotesingle', 'parenleft', 'parenright',
               'asterisk', 'plus', 'less', 'equal', 'greater', 'at',
               'numbersign', 'dollar', 'percent', 'ampersand',
               'bracketleft', 'bracketright', 'backslash', 'asciicircum',
               'underscore', 'grave', 'braceleft', 'braceright', 'bar',
               'asciitilde', 'divide', 'doubledanda', 'endash']
PUNCT = [(g, 'handwriting') for g in HAND] + [(g, 'base') for g in BASE_GLYPHS]

font = TTFont(TTF)
cmap = font.getBestCmap()
inv = {v: k for k, v in cmap.items()}
hmtx = font['hmtx']
glyf = font['glyf']
UPM = 1536


def raster_bbox_and_components(glyph, size=1536):
    """Render one glyph alone; return true ink bbox in font coords
    [x0, bottom, x1, top] and a list of components [(x0, bottom, x1, top,
    pixels)] sorted by area descending. Font coords: baseline y=0, up +."""
    f = ImageFont.truetype(TTF, size, layout_engine=ImageFont.Layout.BASIC)
    ch = chr(inv[glyph])
    img = Image.new('L', (3200, 3200), 0)
    d = ImageDraw.Draw(img)
    ox, base = 1200, 1900  # baseline at image row 1900
    d.text((ox, base), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(img) > 0
    if not a.any():
        return None, []
    bb = img.getbbox()  # (left, upper, right, lower) in image coords
    box = [bb[0] - ox, base - bb[3], bb[2] - ox, base - bb[1]]
    lab, n = ndimage.label(a)
    comps = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(xs) == 0:
            continue
        comps.append([int(xs.min()) - ox, base - int(ys.max()),
                      int(xs.max()) + 1 - ox, base - int(ys.min()),
                      int(len(xs))])
    comps.sort(key=lambda c: -c[4])
    return box, comps


def ridge_stroke(glyph, size=400):
    """EDT ridge median stroke width in font units (400 px em)."""
    f = ImageFont.truetype(TTF, size, layout_engine=ImageFont.Layout.BASIC)
    ch = chr(inv[glyph])
    img = Image.new('L', (900, 1100), 0)
    d = ImageDraw.Draw(img)
    d.text((100, 550), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(img) > 0
    if not a.any():
        return None, None
    scale = UPM / size
    dist = ndimage.distance_transform_edt(a)
    ridge = (dist > 0) & (dist == ndimage.maximum_filter(dist, size=3))
    vals = 2.0 * dist[ridge] * scale
    return round(float(np.median(vals)), 1), round(
        float(np.percentile(vals, 75) - np.percentile(vals, 25)), 1)


rows = []
for glyph, source in PUNCT:
    adv, lsb = hmtx[glyph]
    g = glyf[glyph]
    gb = [g.xMin, g.yMin, g.xMax, g.yMax] if g.numberOfContours else None
    box, comps = raster_bbox_and_components(glyph)
    med, iqr = ridge_stroke(glyph)
    if box is None:
        rows.append(dict(glyph=glyph, char=chr(inv[glyph]), source=source,
                         advance=adv, lsb=lsb, ink=None, comps=[],
                         ridge_med=med, ridge_iqr=iqr))
        continue
    w, h = box[2] - box[0], box[3] - box[1]
    rows.append(dict(glyph=glyph, char=chr(inv[glyph]), source=source,
                     advance=adv, lsb=lsb, rsb=adv - lsb - w,
                     ink=dict(x0=box[0], bottom=box[1], x1=box[2], top=box[3],
                              width=w, height=h, glyf_bbox=gb),
                     comps=[dict(x0=c[0], bottom=c[1], x1=c[2], top=c[3],
                                 width=c[2] - c[0], height=c[3] - c[1],
                                 pixels=c[4]) for c in comps],
                     ridge_med=med, ridge_iqr=iqr))

out = PREP / 'checks'
out.mkdir(parents=True, exist_ok=True)
with open(out / 'punct-inventory-v0.162.tsv', 'w', encoding='utf-8') as f:
    f.write('glyph\tchar\tsource\tadvance\tlsb\trsb\tink_x0\tink_bottom\tink_x1\tink_top\tink_w\tink_h\tridgemed\tridgeiqr\tn_comp\tcomp_summary\n')
    for r in rows:
        ink = r['ink']
        comps = '; '.join(
            f"{c['width']}x{c['height']}@{c['x0']},{c['bottom']}" for c in r['comps'])
        f.write(f"{r['glyph']}\t{r['char']}\t{r['source']}\t{r['advance']}\t{r['lsb']}\t"
                f"{r.get('rsb','')}\t"
                f"{ink['x0'] if ink else ''}\t{ink['bottom'] if ink else ''}\t"
                f"{ink['x1'] if ink else ''}\t{ink['top'] if ink else ''}\t"
                f"{ink['width'] if ink else ''}\t{ink['height'] if ink else ''}\t"
                f"{r['ridge_med']}\t{r['ridge_iqr']}\t{len(r['comps'])}\t{comps}\n")

json.dump(rows, open(out / 'punct-inventory-v0.162.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# ---- family analysis, printed for the log ----
def show(name):
    r = next(x for x in rows if x['glyph'] == name)
    ink = r['ink']
    print(f"  {name:14s} {r['char']} [{r['source'][:4]}] adv={r['advance']:5d} "
          f"lsb={r['lsb']:5d} rsb={r.get('rsb',''):>5} "
          f"ink {ink['width']}x{ink['height']} top={ink['top']} bot={ink['bottom']} "
          f"ridge={r['ridge_med']} iqr={r['ridge_iqr']} comps={len(r['comps'])}")

print('=== DOT FAMILY (period / colon dots / semicolon dot / comma head / ? dot / ! dot) ===')
for n in ('period', 'colon', 'semicolon', 'comma', 'question', 'exclam'):
    show(n)
print('=== ? and ! ===')
for n in ('question', 'exclam'):
    show(n)
print('=== DANDA ===')
for n in ('danda', 'doubledanda'):
    show(n)
print('=== QUOTES (curly handwriting vs straight base) ===')
for n in ('quoteleft', 'quoteright', 'quotedblleft', 'quotedblright',
          'quotesingle', 'quotedbl'):
    show(n)
print('=== DASHES + SLASH ===')
for n in ('hyphen', 'endash', 'emdash', 'slash'):
    show(n)
print('=== PARENS / BRACKETS / BRACES ===')
for n in ('parenleft', 'parenright', 'bracketleft', 'bracketright',
          'braceleft', 'braceright'):
    show(n)
print('=== OTHER BASE SYMBOLS ===')
for n in ('asterisk', 'plus', 'less', 'equal', 'greater', 'at', 'numbersign',
          'dollar', 'percent', 'ampersand', 'backslash', 'asciicircum',
          'underscore', 'grave', 'bar', 'asciitilde', 'divide'):
    show(n)
