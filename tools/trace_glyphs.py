#!/usr/bin/env python3
"""v0.160 tracing: pick the best vowel instance, threshold + potrace each
chosen cell, fit the outline to the v0.150 target ink box, and save the
fitted quadratic outlines as JSON for the build script.

- Threshold: Otsu within the cell crop; keep only components that touch
  the thr=100 ink mask (paper texture / crease shadows are grey and never
  reach 100, so they are excluded even if Otsu admits them).
- Trace: potrace -s (defaults: turdsize 2, alphamax 1.0), SVG parsed
  directly (all <path> elements; M/m, C/c, L/l, Z/z with implicit command
  repetition), cubic -> quadratic via fontTools Cu2QuPen (error 1.0 px).
- Fit (uniform scale, no distortion): s = target_height / trace_height,
  where both heights are TRUE INK bboxes (the trace's is measured by
  sampling the potrace cubic curves — the raw control-point bbox
  overshoots the ink top by up to ~3 px and would push the fitted ink
  down by up to ~56 units; v0.150 SIZE-LOG lesson).
  translate so the scaled ink top == target top and:
    * letters & punctuation: scaled ink centre-x == target centre-x
      (v0.150 rule);
    * signs/marks (kind 'sign'): scaled ink LEFT edge == target left edge
      (v0.130 rule — preserves the mark's ink position relative to its
      fixed GPOS anchor; centre alignment would shift it by half the
      width change).
  Advances are NOT changed here (build script keeps the v0.150 hmtx).
- bn_anusvara: the cell contains a stray pen flick (swoosh) below the loop,
  in the inter-row gap; the v0.150 glyph carries the same stray. The swoosh
  contour is dropped and the loop is fitted to the v0.150 loop-only box
  (83, 618, 447, 1098).
- Vowel choice: score 28 instances/vowel (7 cols x 4 photos) on ink
  area, aspect, stroke width vs the row median, plus an edge-touch
  penalty; lowest score wins. The chosen 11 are rendered to a contact
  sheet for eyeballing before the build.
"""
import json, math, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen

ROOT = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
CELLS = ROOT / 'cells'
PBM = ROOT / 'pbm'
SVG = ROOT / 'svg'
for d in (PBM, SVG):
    d.mkdir(parents=True, exist_ok=True)

VOWEL_GLYPHS = ['bn_a', 'bn_aa', 'bn_i', 'bn_ii', 'bn_u', 'bn_uu', 'bn_ri',
                'bn_e', 'bn_ai', 'bn_o', 'bn_au']
VOWEL_ROWS = ['অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'এ', 'ঐ', 'ও', 'ঔ']


def otsu(arr):
    hist, _ = np.histogram(arr, bins=256, range=(0, 256))
    hist = hist.astype(float)
    total = hist.sum()
    w0 = np.cumsum(hist)
    w1 = total - w0
    centres = np.arange(256)
    m0 = np.cumsum(hist * centres)
    mt = m0[-1]
    with np.errstate(invalid='ignore', divide='ignore'):
        m1 = (mt - m0) / np.maximum(w1, 1)
        m0n = m0 / np.maximum(w0, 1)
        between = w0 * w1 * (m0n - m1) ** 2
    between[w0 == 0] = 0
    between[w1 == 0] = 0
    return int(np.argmax(between))


def cell_ink(crop_arr):
    """Return (ink mask, otsu threshold, mask100) for a cell crop."""
    thr = otsu(crop_arr)
    mask = crop_arr < thr
    mask100 = crop_arr < 100
    lab, n = ndimage.label(mask)
    keep = np.zeros_like(mask)
    if n:
        objs = ndimage.find_objects(lab)
        for i, sl in enumerate(objs, 1):
            comp = (lab[sl] == i)
            if comp.sum() < 4:
                continue
            if not mask100[sl][comp].any():
                continue  # grey smudge / crease, never reaches true ink
            keep[sl] |= comp
    return keep, thr, mask100


def cell_metrics(crop_arr):
    ink, thr, mask100 = cell_ink(crop_arr)
    if not ink.any():
        return None
    ys, xs = np.where(ink)
    y0, y1, x0, x1 = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
    h, w = y1 - y0 + 1, x1 - x0 + 1
    area = int(ink.sum())
    dist = ndimage.distance_transform_edt(ink)
    stroke = float(4 * np.median(dist[ink])) if area else 0.0
    edge = int(ink[:2, :].sum() + ink[-2:, :].sum() +
               ink[:, :2].sum() + ink[:, -2:].sum())
    return dict(area=area, w=w, h=h, aspect=w / h, stroke=stroke,
                edge_touch=edge, thr=thr, bbox=[x0, y0, x1, y1])


def potrace_svg(name, ink):
    """Write PBM, run potrace, return parsed contours in pixel coords
    (x right, y DOWN from the top of the PBM)."""
    pbm_path = PBM / f'{name}.pbm'
    Image.fromarray(np.where(ink, 0, 255).astype(np.uint8), 'L').convert('1').save(pbm_path)
    svg_path = SVG / f'{name}.svg'
    r = subprocess.run(['potrace', '-s', '-o', str(svg_path), str(pbm_path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'potrace failed for {name}: {r.stderr}')
    return parse_potrace_svg(svg_path, ink.shape)


def parse_potrace_svg(path, shape):
    """Parse potrace's SVG path (M/m, C/c, L/l, Z/z with implicit command
    repetition). Path coords are 10x pixels, y measured UP from the
    bottom of the PBM. Returns contours in pixel coords (x right,
    y DOWN from the top)."""
    txt = Path(path).read_text()
    paths = re.findall(r'<path d="([^"]+)"', txt)
    if not paths:
        raise RuntimeError(f'no path in {path}')
    H = shape[0]
    contours = []
    for d in paths:
        contours += _parse_path_d(d, H)
    return contours


def _parse_path_d(d, H):
    tokens = re.findall(r'[MmCcLlZz]|-?\d+\.?\d*', d)
    contours = []
    cur = None
    x = y = 0.0  # current point, pixel coords (y down)
    sx = sy = 0.0  # current subpath start
    cmd = None
    i = 0

    def num():
        nonlocal i
        v = float(tokens[i])
        i += 1
        return v

    while i < len(tokens):
        t = tokens[i]
        if t in 'MmCcLlZz':
            cmd = t
            i += 1
            if t in 'Zz':
                cur.append(('Z',))
                x, y = sx, sy  # after close, current point is subpath start
                cmd = None
            continue
        if cmd is None:
            raise RuntimeError('number without command in path data')
        if cmd == 'M':
            x = num() / 10.0
            y = H - num() / 10.0
            sx, sy = x, y
            cur = [('M', x, y)]
            contours.append(cur)
            cmd = 'L'
        elif cmd == 'm':
            x = x + num() / 10.0
            y = y - num() / 10.0
            sx, sy = x, y
            cur = [('M', x, y)]
            contours.append(cur)
            cmd = 'l'
        elif cmd == 'C':
            x1, y1 = num() / 10.0, H - num() / 10.0
            x2, y2 = num() / 10.0, H - num() / 10.0
            x, y = num() / 10.0, H - num() / 10.0
            cur.append(('C', x1, y1, x2, y2, x, y))
        elif cmd == 'c':
            x1 = x + num() / 10.0
            y1 = y - num() / 10.0
            x2 = x + num() / 10.0
            y2 = y - num() / 10.0
            x = x + num() / 10.0
            y = y - num() / 10.0
            cur.append(('C', x1, y1, x2, y2, x, y))
        elif cmd == 'L':
            x = num() / 10.0
            y = H - num() / 10.0
            cur.append(('L', x, y))
        elif cmd == 'l':
            x = x + num() / 10.0
            y = y - num() / 10.0
            cur.append(('L', x, y))
        else:
            raise RuntimeError(f'unexpected command {cmd!r} in path data')
    return contours


def cubic_point(p0, p1, p2, p3, t):
    mt = 1 - t
    return (mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0],
            mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1])


def true_bbox(contours, n=24):
    """True ink bbox of parsed cubic contours: sample the curves.
    (The bbox of the raw points INCLUDES off-curve control points, which
    overshoot the real ink by up to ~3 px — the v0.150 SIZE-LOG lesson.
    Fitting to the control-point bbox pushes the true ink top down by
    up to ~56 units; the fit must use this true bbox.)"""
    xs, ys = [], []
    for c in contours:
        start = cur = None
        for seg in c:
            if seg[0] == 'M':
                cur = (seg[1], seg[2])
                start = cur
                xs.append(cur[0]); ys.append(cur[1])
            elif seg[0] == 'L':
                cur = (seg[1], seg[2])
                xs.append(cur[0]); ys.append(cur[1])
            elif seg[0] == 'C':
                p0 = cur
                p1 = (seg[1], seg[2]); p2 = (seg[3], seg[4]); p3 = (seg[5], seg[6])
                for k in range(1, n + 1):
                    x, y = cubic_point(p0, p1, p2, p3, k / n)
                    xs.append(x); ys.append(y)
                cur = p3
            elif seg[0] == 'Z':
                cur = start
    return min(xs), min(ys), max(xs), max(ys)


def contour_bbox(c):
    """(x0, y0, x1, y1) of a parsed contour incl. control points."""
    xs, ys = [], []
    for p in c:
        if p[0] in ('M', 'L'):
            xs.append(p[1]); ys.append(p[2])
        elif p[0] == 'C':
            xs += [p[1], p[3], p[5]]; ys += [p[2], p[4], p[6]]
    return min(xs), min(ys), max(xs), max(ys)


def contours_to_glyph(contours, scale, tx_cx, ty_top, trace_cx, trace_y0):
    """Map pixel coords -> font units, cubic->quadratic, return TTGlyph."""
    pen = TTGlyphPen(None)
    qpen = Cu2QuPen(pen, 1.0)
    for contour in contours:
        for j, seg in enumerate(contour):
            if seg[0] == 'M':
                _, px, py = seg
                qpen.moveTo((tx_cx + (px - trace_cx) * scale,
                             ty_top - (py - trace_y0) * scale))
            elif seg[0] == 'L':
                _, px, py = seg
                qpen.lineTo((tx_cx + (px - trace_cx) * scale,
                             ty_top - (py - trace_y0) * scale))
            elif seg[0] == 'C':
                _, x1, y1, x2, y2, px, py = seg
                qpen.curveTo(
                    (tx_cx + (x1 - trace_cx) * scale, ty_top - (y1 - trace_y0) * scale),
                    (tx_cx + (x2 - trace_cx) * scale, ty_top - (y2 - trace_y0) * scale),
                    (tx_cx + (px - trace_cx) * scale, ty_top - (py - trace_y0) * scale))
            elif seg[0] == 'Z':
                qpen.closePath()
    g = pen.glyph()
    g.coordinates = __import__('fontTools.ttLib.tables._g_l_y_f', fromlist=['GlyphCoordinates']).GlyphCoordinates(
        [(round(px), round(py)) for px, py in g.coordinates])
    return g


def reverse_contours(g):
    """Reverse the winding of every contour (point+flag order).

    Potrace emits contours clockwise in image coords (y down); the
    y-flip into font coords (y up) reverses the winding, leaving outer
    contours counter-clockwise — FontForge validate bit 3 (value 8,
    wrong direction) on every traced glyph. TrueType wants outer contours
    clockwise (negative signed area in y-up) and holes counter-clockwise.
    Reversing each contour's point order fixes all of them at once (the
    y-flip reversed them uniformly). Safe for quadratic outlines: a
    quadratic segment is symmetric, and implied on-curve midpoints
    between two off-curve points are unchanged by reversal."""
    coords = list(g.coordinates)
    flags = list(g.flags)
    ends = list(g.endPtsOfContours)
    new_c, new_f, new_e = [], [], []
    start = 0
    for e in ends:
        pts = coords[start:e + 1]
        fl = flags[start:e + 1]
        start = e + 1
        new_c.extend(pts[::-1])
        new_f.extend(fl[::-1])
        new_e.append(len(new_c) - 1)
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    from array import array as _array
    g.coordinates = GlyphCoordinates(new_c)
    g.flags = _array('B', new_f)
    g.endPtsOfContours = new_e


def main():
    manifest = json.load(open(ROOT / 'cells.json'))
    targets = json.load(open(ROOT / 'targets.json'))

    # bn_anusvara target override: the v0.150 target bbox [82,-130,709,1098]
    # includes a stray pen flick (a swoosh below the loop — see the
    # anusvara cell: it sits in the inter-row gap, detached from the loop,
    # and the v0.150 glyph carries the same stray, contour 0, x164-710 /
    # y-130-334). The loop alone is contour 2 of v0.150: x83-447, y618-1098
    # (hole = contour 1). Fit the loop to the loop-only box.
    targets['bn_anusvara']['ink_after'] = [83, 618, 447, 1098]
    targets['bn_anusvara']['note'] = 'loop-only target; stray swoosh excluded'

    # ---- vowel best-of-7 x 4 photos -------------------------------------
    by_glyph = {}
    for m in manifest:
        if m['tag'].startswith('vow_'):
            by_glyph.setdefault(m['glyph'], []).append(m)
    selection = {}
    print('=== vowel selection (28 candidates each) ===')
    for g in VOWEL_GLYPHS:
        cands = []
        for m in by_glyph[g]:
            arr = np.array(Image.open(m['file']).convert('L'))
            met = cell_metrics(arr)
            if met is None:
                print(f'  !! {g} {m["tag"]} r{m["row"]}c{m["col"]}: no ink')
                continue
            cands.append((m, met))
        areas = np.median([c[1]['area'] for c in cands])
        aspects = np.median([c[1]['aspect'] for c in cands])
        strokes = np.median([c[1]['stroke'] for c in cands])
        scored = []
        for m, met in cands:
            score = (abs(met['area'] - areas) / areas
                     + abs(met['aspect'] - aspects) / aspects
                     + abs(met['stroke'] - strokes) / strokes
                     + (5.0 if met['edge_touch'] > 0 else 0.0))
            scored.append((score, m, met))
        scored.sort(key=lambda t: t[0])
        best_score, best_m, best_met = scored[0]
        second = scored[1]
        selection[g] = dict(photo=best_m['photo'], row=best_m['row'],
                            col=best_m['col'], file=best_m['file'],
                            score=round(best_score, 3),
                            metrics={k: (round(v, 2) if isinstance(v, float) else v)
                                     for k, v in best_met.items()},
                            runner_up=dict(photo=second[1]['photo'],
                                           row=second[1]['row'],
                                           col=second[1]['col'],
                                           score=round(second[0], 3)))
        print(f"  {targets[g]['ch']} {g}: {best_m['tag']} r{best_m['row']}c{best_m['col']} "
              f"score={best_score:.3f} area={best_met['area']} aspect={best_met['aspect']:.2f} "
              f"stroke={best_met['stroke']:.1f} thr={best_met['thr']} "
              f"(runner-up {second[1]['tag']} r{second[1]['row']}c{second[1]['col']} {second[0]:.3f})")
    json.dump(selection, open(ROOT / 'vowel_selection.json', 'w'),
              ensure_ascii=False, indent=1)

    # ---- build the trace list: 69 + punctuation --------------------------
    trace_list = []  # (glyph_name, cell manifest entry)
    for g in VOWEL_GLYPHS:
        sel = selection[g]
        m = next(m for m in by_glyph[g]
                 if m['photo'] == sel['photo'] and m['row'] == sel['row']
                 and m['col'] == sel['col'])
        trace_list.append((g, m))
    seen = set(g for g, _ in trace_list)
    for m in manifest:
        if m['tag'] == 'cons_16' and m['glyph']:
            if m['row'] == 6:
                continue  # duplicate ো/ৌ row — backups only
            if m['glyph'] in seen:
                continue  # keep the first instance (e.g. colon c5, not c7)
            seen.add(m['glyph'])
            trace_list.append((m['glyph'], m))
    print(f'trace list: {len(trace_list)} glyphs')

    # ---- trace + fit -------------------------------------------------------
    out = {}
    for gname, m in trace_list:
        tgt = targets[gname]
        arr = np.array(Image.open(m['file']).convert('L'))
        ink, thr, _ = cell_ink(arr)
        contours = potrace_svg(gname, ink)
        dropped = 0
        if gname == 'bn_anusvara':
            # drop the stray swoosh: any contour starting below the ink
            # bbox vertical midpoint (the loop is in the top half).
            ys_i, _ = np.where(ink)
            mid_y = (ys_i.min() + ys_i.max()) / 2.0
            kept = [c for c in contours if contour_bbox(c)[1] <= mid_y]
            dropped = len(contours) - len(kept)
            contours = kept
        # trace TRUE ink bbox (sampled curves, not control points — see
        # true_bbox; the control-point bbox overshoots the ink top by up
        # to ~3 px and would push the fitted ink down by up to ~56 units)
        tx0, ty0, tx1, ty1 = true_bbox(contours)
        gx0, gy0, gx1, gy1 = tgt['ink_after']
        s = (gy1 - gy0) / (ty1 - ty0)
        if tgt['kind'] == 'sign':
            # marks: v0.130 rule — align LEFT edge + top to the target box.
            # (Centre alignment would shift the mark's ink relative to its
            # fixed GPOS anchor by half the width change.)
            ref_x, trace_ref_x = gx0, tx0
        else:
            # letters & punctuation: centre-x + top (v0.150 rule).
            ref_x, trace_ref_x = (gx0 + gx1) / 2.0, (tx0 + tx1) / 2.0
        glyph = contours_to_glyph(contours, s, ref_x, gy1, trace_ref_x, ty0)
        reverse_contours(glyph)  # potrace winding is reversed by the y-flip
        # fitted ink bbox from the integer-rounded outline
        xs2 = [c[0] for c in glyph.coordinates]
        ys2 = [c[1] for c in glyph.coordinates]
        # NOTE: outline bbox includes off-curve control points; the true
        # ink box is measured again at build verification time.
        from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
        out[gname] = dict(
            char=tgt['ch'], kind=tgt['kind'], adv=tgt['adv'],
            source=dict(photo=m['photo'], row=m['row'], col=m['col'],
                        file=m['file']),
            otsu=int(thr), scale=round(s, 4),
            trace_bbox_px=[round(v, 1) for v in (tx0, ty0, tx1, ty1)],
            target=tgt['ink_after'],
            fitted_outline_bbox=[min(xs2), min(ys2), max(xs2), max(ys2)],
            width_ratio=round(((max(xs2) - min(xs2)) / (gx1 - gx0)), 3),
            contours=len(glyph.endPtsOfContours),
            dropped_contours=dropped,
            points=len(glyph.coordinates),
            coords=[[int(x), int(y)] for x, y in glyph.coordinates],
            flags=[int(f) for f in glyph.flags],
            ends=[int(e) for e in glyph.endPtsOfContours])
        flag = ''
        wr = out[gname]['width_ratio']
        if not (0.85 <= wr <= 1.15):
            flag = '  <-- WIDTH OFF'
        print(f"  {tgt['ch']} {gname:16s} {m['tag']} r{m['row']}c{m['col']} "
              f"thr={thr} s={s:.2f} pts={len(glyph.coordinates)} "
              f"contours={len(glyph.endPtsOfContours)} w_ratio={wr:.2f}{flag}")
    json.dump(out, open(ROOT / 'traced_glyphs.json', 'w'), ensure_ascii=False)
    print('wrote traced_glyphs.json:', len(out), 'glyphs')


if __name__ == '__main__':
    main()
