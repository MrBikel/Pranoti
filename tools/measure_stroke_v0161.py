#!/usr/bin/env python3
"""Measure per-glyph stroke width in Pranoti v0.160-beta.

Method (distance-transform ridge, validated against POLISH-LOG-v0.140):
  Render each glyph alone with PIL BASIC layout at 400 px em
  (3.84 font units/px). Binary ink mask (coverage > 0). Euclidean
  distance transform over the ink (scipy.ndimage.distance_transform_edt).
  Ridge = ink pixels that are local maxima of the EDT (equal to the
  3x3 maximum filter) — the medial axis. Stroke width at a ridge pixel
  is 2 * EDT * scale; the glyph's stroke width is the MEDIAN of that
  over the ridge, IQR measures how much the width wobbles within the
  glyph. 400 px was chosen because 800 px resolves sub-pixel outline
  hairlines (e.g. bn_dha's pinched loop neck) that the eye never sees
  at text size and that drag the median down; 400 px matches the
  v0.140 log's letter values within ~0-15 units (bn_a 99.8 vs 99.84,
  bn_la 107.5 vs 107.52, bn_nna 103.7 vs 104.46, bn_one 107.1 vs 110.76).
  Also reported: trimmed median (bottom 20% of ridge values dropped)
  as a check against hairline artifacts.

Caveat: for filled blobs (anusvara loop, visarga dots, candrabindu,
danda/period dots, quote marks) the ridge value measures the blob
radius, not a stroke — those rows are flagged and excluded from the
letter ranking. Combining marks are measured alone at their origin
(BASIC layout), which is what the v0.140 log did.
"""
import json, re
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

PREP160 = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
PREP = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
TTF = str(PREP / 'Pranoti-Regular-v0.161-beta.ttf')
OUT = PREP / 'weight'
SIZE = 400
SCALE = 1536 / SIZE  # font units per pixel

traced = json.load(open(PREP160 / 'traced_glyphs.json', encoding='utf-8'))

# v0.140-after medians, parsed from POLISH-LOG-v0.140.md, for the cross-check
v140 = {}
for line in open('/home/hatch/workspace/fonts/bengali-hand/github-repo/POLISH-LOG-v0.140.md', encoding='utf-8'):
    m = re.match(r'\| (bn_\w+|danda|slash) \| .+? \| \d+ \| \d+ \| \d+ \| [\d.]+ \| ([\d.]+) \|', line)
    if m:
        v140[m.group(1)] = float(m.group(2))

BLOB = {'bn_anusvara', 'bn_visarga', 'bn_candrabindu', 'danda', 'period',
        'comma', 'quoteleft', 'quoteright', 'quotedblleft', 'quotedblright'}

font = ImageFont.truetype(TTF, SIZE, layout_engine=ImageFont.Layout.BASIC)
rows = []
for name, d in traced.items():
    ch = d['char']
    im = Image.new('L', (900, 1100), 0)
    dr = ImageDraw.Draw(im)
    dr.text((100, 550), ch, font=font, fill=255, anchor='ls')
    a = np.asarray(im) > 0
    if not a.any():
        rows.append(dict(name=name, char=ch, kind=d['kind'], median=None,
                         trimmed=None, iqr=None, area=0, v140=v140.get(name)))
        continue
    dist = ndimage.distance_transform_edt(a)
    ridge = (dist > 0) & (dist == ndimage.maximum_filter(dist, size=3))
    vals = 2.0 * dist[ridge] * SCALE
    med = float(np.median(vals))
    lo = np.percentile(vals, 20)
    trimmed = float(np.median(vals[vals >= lo]))
    rows.append(dict(name=name, char=ch, kind=d['kind'],
                     median=round(med, 1),
                     trimmed=round(trimmed, 1),
                     iqr=round(float(np.percentile(vals, 75) - np.percentile(vals, 25)), 1),
                     area=int(a.sum()), v140=v140.get(name)))

letters = [r for r in rows if r['kind'] == 'letter' and r['median'] is not None]
letter_med = float(np.median([r['median'] for r in letters]))
for r in rows:
    if r['median'] is not None:
        r['dev'] = round(r['median'] - letter_med, 1)
        r['dev_pct'] = round(100 * (r['median'] - letter_med) / letter_med, 1)
        r['dev140'] = round(r['median'] - r['v140'], 1) if r['v140'] else None

with open(OUT / 'stroke-widths-v0.161.tsv', 'w', encoding='utf-8') as f:
    f.write('glyph\tchar\tkind\tmedian_stroke_units\ttrimmed_median_units\tiqr_units\tdev_from_letter_median_units\tdev_pct\tv0140_after_median\tchange_vs_v0140\n')
    for r in sorted(rows, key=lambda r: (r['median'] is None, -(r['median'] or 0))):
        f.write(f"{r['name']}\t{r['char']}\t{r['kind']}\t{r['median']}\t{r['trimmed']}\t{r['iqr']}\t"
                f"{r.get('dev','')}\t{r.get('dev_pct','')}\t{r['v140'] or ''}\t{r.get('dev140','')}\n")

summary = dict(n=len(rows), n_measured=sum(1 for r in rows if r['median'] is not None),
               overall_median=round(float(np.median([r['median'] for r in rows if r['median'] is not None])), 1),
               letter_median=round(letter_med, 1),
               letter_min=min(r['median'] for r in letters), letter_max=max(r['median'] for r in letters),
               letter_iqr_of_medians=round(float(np.percentile([r['median'] for r in letters], 75) - np.percentile([r['median'] for r in letters], 25)), 1))
json.dump(dict(summary=summary, rows=rows), open(OUT / 'stroke-widths-v0.161.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(summary, indent=1))
print('\nThickest 12 letters:')
for r in sorted(letters, key=lambda r: -r['median'])[:12]:
    print(f"  {r['name']:14s} {r['char']} med={r['median']:6.1f} trim={r['trimmed']:6.1f} iqr={r['iqr']:5.1f} {r['dev_pct']:+6.1f}%  v140={r['v140']} d={r.get('dev140')}")
print('Thinnest 12 letters:')
for r in sorted(letters, key=lambda r: r['median'])[:12]:
    print(f"  {r['name']:14s} {r['char']} med={r['median']:6.1f} trim={r['trimmed']:6.1f} iqr={r['iqr']:5.1f} {r['dev_pct']:+6.1f}%  v140={r['v140']} d={r.get('dev140')}")
print('\nSigns + punctuation:')
for r in rows:
    if r['kind'] != 'letter':
        print(f"  {r['name']:14s} {r['char']} med={r['median']} trim={r['trimmed']} iqr={r['iqr']} {r.get('dev_pct',''):+}%  v140={r['v140']} d={r.get('dev140')}" if r['median'] else f"  {r['name']} NO INK")
print('\nLargest within-glyph wobble (IQR) among letters:')
for r in sorted(letters, key=lambda r: -r['iqr'])[:8]:
    print(f"  {r['name']:14s} {r['char']} iqr={r['iqr']:5.1f} med={r['median']:6.1f}")
