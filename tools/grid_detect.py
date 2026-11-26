#!/usr/bin/env python3
"""v0.160 grid detection: find row bands and column segments in a
handwriting sheet photo, extract tight cell crops, and build a labelled
contact sheet for visual verification of the cell->glyph mapping.

Method: threshold ink, horizontal projection -> row bands (split on gaps
>= min_row_gap), vertical projection inside each band -> column segments
(split on gaps >= min_col_gap). Despeckle: drop connected components
smaller than MIN_AREA px (paper specks / JPEG noise, not strokes).
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

THR = 100
MIN_AREA = 6
BORDER = 20  # ignore outer photo border (shadows / dark edges)


def load_ink(path, thr=THR):
    a = np.array(Image.open(path).convert('L'))
    ink = a < thr
    lab, n = ndimage.label(ink)
    if n:
        sizes = ndimage.sum_labels(ink, lab, range(1, n + 1))
        keep = np.zeros_like(ink)
        for i, s in enumerate(sizes, 1):
            if s >= MIN_AREA:
                keep |= (lab == i)
        ink = keep
    return ink


def runs(mask, min_gap):
    """Contiguous True runs, merging runs separated by < min_gap."""
    idx = np.where(mask)[0]
    if len(idx) == 0:
        return []
    out = []
    s = p = int(idx[0])
    for v in idx[1:]:
        v = int(v)
        if v - p > min_gap:
            out.append((s, p))
            s = v
        p = v
    out.append((s, p))
    return out


def detect(path, min_row_gap=25, min_col_gap=25, min_row_ink=200,
           min_col_ink=8):
    ink = load_ink(path)
    ink[:BORDER, :] = False
    ink[-BORDER:, :] = False
    ink[:, :BORDER] = False
    ink[:, -BORDER:] = False
    H, W = ink.shape
    rowsum = ink.sum(axis=1)
    bands = []
    for y0, y1 in runs(rowsum > 0, min_row_gap):
        if rowsum[y0:y1 + 1].sum() < min_row_ink:
            continue
        bands.append((y0, y1))
    # global column grid: segment x-centres from the widest bands
    raw = []
    for bi, (y0, y1) in enumerate(bands):
        colsum = ink[y0:y1 + 1, :].sum(axis=0)
        segs = []
        for x0, x1 in runs(colsum > 0, min_col_gap):
            sub = ink[y0:y1 + 1, x0:x1 + 1]
            if sub.sum() < min_col_ink:
                continue
            ys, xs = np.where(sub)
            segs.append((x0 + int(xs.min()), y0 + int(ys.min()),
                         x0 + int(xs.max()), y0 + int(ys.max())))
        # merge intra-glyph splits: parts of one glyph (e.g. ো = ে + া)
        # sit <55px apart; neighbouring glyphs are >=80px apart.
        merged = []
        for s in sorted(segs):
            if merged and s[0] - merged[-1][2] < 55:
                p = merged[-1]
                merged[-1] = (p[0], min(p[1], s[1]), s[2], max(p[3], s[3]))
            else:
                merged.append(s)
        for (x0, y0, x1, y1) in merged:
            raw.append((bi, x0, y0, x1, y1))
    # column grid: centres of the band with the most TOTAL ink (a full
    # consonant/letter row, not the punctuation row which has more cells
    # but far less ink and different column positions). The grid is used
    # ONLY to drop stray specks far outside the sheet columns; cells are
    # the raw segments, in left-to-right order within each band.
    per_band = {}
    for bi, x0, y0, x1, y1 in raw:
        per_band.setdefault(bi, []).append((x0, y0, x1, y1))
    ink_per_band = {bi: sum((s[2] - s[0]) * (s[3] - s[1]) for s in segs)
                    for bi, segs in per_band.items()}
    fullest = per_band[max(ink_per_band, key=ink_per_band.get)]
    centres = sorted((s[0] + s[2]) / 2 for s in fullest)
    grid = centres
    cells = []  # (band_i, col_i, x0, y0, x1, y1) tight ink boxes
    for bi, segs in sorted(per_band.items()):
        segs = sorted(segs)
        kept = []
        for (x0, y0, x1, y1) in segs:
            cx = (x0 + x1) / 2
            # drop strays: a segment whose centre is far from every grid
            # column AND far from its band-mates is a paper speck.
            if min(abs(g - cx) for g in grid) > 130 and len(segs) > 1:
                # keep it only if it sits inside the band's own span
                span0 = min(s[0] for s in segs)
                span1 = max(s[2] for s in segs)
                if cx < span0 - 20 or cx > span1 + 20:
                    continue
            kept.append((x0, y0, x1, y1))
        for ci, (x0, y0, x1, y1) in enumerate(kept):
            cells.append((bi, ci, x0, y0, x1, y1))
    return ink.shape, bands, cells, grid


def contact_sheet(path, cells, labels, out, cell_px=170):
    """Render the detected cells in a grid with labels for eyeballing."""
    im = Image.open(path).convert('L')
    a = np.array(im)
    n = len(cells)
    cols = 7
    rows = (n + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell_px, rows * (cell_px + 22)), 'white')
    d = ImageDraw.Draw(sheet)
    try:
        fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    except Exception:
        fnt = ImageFont.load_default()
    for i, (bi, si, x0, y0, x1, y1) in enumerate(cells):
        pad = 8
        crop = im.crop((max(0, x0 - pad), max(0, y0 - pad),
                        min(a.shape[1], x1 + 1 + pad), min(a.shape[0], y1 + 1 + pad)))
        w, h = crop.size
        s = min((cell_px - 6) / max(w, 1), (cell_px - 6) / max(h, 1), 1.0)
        crop = crop.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
        cx, cy = (i % cols) * cell_px, (i // cols) * (cell_px + 22)
        sheet.paste(crop, (cx + (cell_px - crop.width) // 2,
                           cy + (cell_px - crop.height) // 2))
        d.text((cx + 4, cy + cell_px + 2), labels[i], fill='black', font=fnt)
    sheet.save(out)
    return out


if __name__ == '__main__':
    path = sys.argv[1]
    shape, bands, cells, grid = detect(path)
    print(path, 'shape', shape)
    print('bands:', len(bands), 'grid centres:', [round(g) for g in grid])
    from collections import Counter
    print('cells per band:', dict(sorted(Counter(c[0] for c in cells).items())),
          'total', len(cells))
    for c in cells:
        print(c)
