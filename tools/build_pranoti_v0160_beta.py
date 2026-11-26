#!/usr/bin/env python3
"""Build Pranoti v0.160-beta from v0.150-beta.

v0.160: re-trace the 69 handwriting glyphs from the clean photos + add
handwritten punctuation (83 glyphs total), replacing the blurry-photo
traces that v0.130-v0.150 carried.

What changes (per glyph, from traced_glyphs.json — see tools/trace_glyphs.py):
  1. Outline replaced by the new clean-photo trace, fitted by uniform
     scale to the v0.150 ink-box target: ink top exact, letters/punct
     centred on the target centre-x, signs/marks left-edge aligned
     (v0.130 rule, preserves GPOS anchor registration).
  2. clean_glyph (from build_pranoti_v0130_beta.py): drop duplicate
     consecutive points that cannot change geometry; insert implied
     on-curve points for all-off-curve contours.
  3. polish_glyph (from build_pranoti_v0140_beta.py): one pass of the
     7-point binomial smoothing kernel [1,6,15,20,15,6,1]/64, per-point
     move capped at 5 units, near-duplicate points (<=1.0 unit) merged
     where safe. Applied to the new/replaced glyphs ONLY.
  4. hmtx: advance UNCHANGED; lsb = new outline xMin (v0.150 precedent).

What does NOT change: GSUB, GPOS, GDEF, cmap, glyph order, metrics of
every other glyph, the 4 new glyphs (U+0980, U+09FB, U+09FC, U+09FE),
all ~375 conjunct ligatures, bn_hasanta (kept AdorshoLipi, as in v0.130).

Input : ../github-repo/Pranoti-Regular-v0.150-beta.ttf (read-only)
        traced_glyphs.json (tools/trace_glyphs.py output)
Output: Pranoti-Regular-v0.160-beta.ttf, build-log-v0.160.json
"""
import hashlib, json, math
from array import array
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables.ttProgram import Program

ROOT = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
BASE = Path('/home/hatch/workspace/fonts/bengali-hand/github-repo/Pranoti-Regular-v0.150-beta.ttf')
EXPECTED_BASE_SHA256 = '679ba5155faa048c039560469bdc174451f395a7852b79e88496bbab2aa40c93'
TRACED = ROOT / 'traced_glyphs.json'
OUT = ROOT / 'Pranoti-Regular-v0.160-beta.ttf'

KERNEL = [1, 6, 15, 20, 15, 6, 1]
CAP = 5.0
MERGE_DIST = 1.0


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --- clean_glyph: copied verbatim from build_pranoti_v0130_beta.py -----------
def clean_glyph(g):
    """Shape-preserving outline hygiene for a simple glyph.

    The v4 handwriting outlines carry duplicate consecutive points (a
    potrace tracing artefact) and a couple of contours with no on-curve
    point at all; FontForge's validator flags both (bit 4). This removes
    only duplicates whose removal cannot change any segment's geometry
    (on/on pairs; on/off and off/on pairs whose neighbour on the far side
    is on-curve) and inserts the implied on-curve point explicitly for
    all-off-curve contours. Bbox and rendering are unchanged.
    Returns (n_removed, n_inserted)."""
    if g.isComposite() or g.numberOfContours <= 0:
        return (0, 0)
    if getattr(g, 'program', None) is not None and len(g.program.getBytecode()) > 0:
        return (0, 0)  # hinting references point indices; leave alone
    coords = list(g.coordinates)
    flags = list(g.flags)
    ends = list(g.endPtsOfContours)
    removed = inserted = 0
    contours = []
    start = 0
    for e in ends:
        contours.append((coords[start:e + 1], flags[start:e + 1]))
        start = e + 1
    out = []
    for pts, fl in contours:
        pts, fl = list(pts), list(fl)
        # repeated safe dedup passes (removals can create new adjacencies)
        changed = True
        while changed and len(pts) >= 2:
            changed = False
            n = len(pts)
            for i in range(n):
                j = (i + 1) % n
                if pts[i] != pts[j]:
                    continue
                on_i, on_j = bool(fl[i] & 1), bool(fl[j] & 1)
                drop = None
                if on_i and on_j:
                    drop = j  # zero-length line segment
                elif on_i and not on_j:
                    # drop the off-curve point only if the point after it
                    # is on-curve (else the implied midpoint would move)
                    if fl[(j + 1) % n] & 1:
                        drop = j
                elif not on_i and on_j:
                    # drop the off-curve point only if the point before it
                    # is on-curve
                    if fl[(i - 1) % n] & 1:
                        drop = i
                if drop is None:
                    continue
                del pts[drop]
                del fl[drop]
                removed += 1
                changed = True
                break
        if len(pts) < 2:
            continue  # degenerate contour: renders nothing
        if not any(f & 1 for f in fl):
            # all-off-curve: make the implied midpoint point explicit
            mx = (pts[-1][0] + pts[0][0]) // 2
            my = (pts[-1][1] + pts[0][1]) // 2
            pts.insert(0, (mx, my))
            fl.insert(0, 1)
            inserted += 1
        out.append((pts, fl))
    new_coords, new_flags, new_ends = [], [], []
    for pts, fl in out:
        new_coords.extend(pts)
        new_flags.extend(fl)
        new_ends.append(len(new_coords) - 1)
    g.coordinates = GlyphCoordinates(new_coords)
    g.flags = array('B', new_flags)
    g.endPtsOfContours = new_ends
    g.numberOfContours = len(new_ends)
    return (removed, inserted)


# --- polish: copied from build_pranoti_v0140_beta.py -------------------------
def smooth_kernel(pts, kernel, cap):
    n = len(pts)
    r = len(kernel) // 2
    wsum = float(sum(kernel))
    pts = [list(map(float, p)) for p in pts]
    new = []
    for i in range(n):
        nx = ny = 0.0
        for k, w in enumerate(kernel):
            p = pts[(i + k - r) % n]
            nx += w * p[0]
            ny += w * p[1]
        nx /= wsum
        ny /= wsum
        dx, dy = nx - pts[i][0], ny - pts[i][1]
        d = math.hypot(dx, dy)
        if d > cap:
            dx, dy = dx * cap / d, dy * cap / d
        new.append([pts[i][0] + dx, pts[i][1] + dy])
    return new


def merge_near_dup(pts, fl):
    removed = 0
    changed = True
    while changed and len(pts) >= 2:
        changed = False
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            dx = pts[i][0] - pts[j][0]
            dy = pts[i][1] - pts[j][1]
            if dx * dx + dy * dy > MERGE_DIST * MERGE_DIST:
                continue
            on_i, on_j = bool(fl[i] & 1), bool(fl[j] & 1)
            drop = None
            if on_i and on_j:
                drop = j
            elif on_i and not on_j:
                if fl[(j + 1) % n] & 1:
                    drop = j
            elif not on_i and on_j:
                if fl[(i - 1) % n] & 1:
                    drop = i
            if drop is None:
                continue
            del pts[drop]
            del fl[drop]
            removed += 1
            changed = True
            break
    return removed


def polish_glyph(g):
    if g.isComposite() or g.numberOfContours <= 0:
        return (0, 0, 0, 0)
    if getattr(g, 'program', None) is not None and len(g.program.getBytecode()) > 0:
        return (0, 0, 0, 0)
    coords = list(g.coordinates)
    flags = list(g.flags)
    ends = list(g.endPtsOfContours)
    before = len(coords)
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    bb0 = (min(xs), min(ys), max(xs), max(ys))
    out_c, out_f, out_e = [], [], []
    merged = 0
    start = 0
    for e in ends:
        pts = coords[start:e + 1]
        fl = flags[start:e + 1]
        start = e + 1
        px = [p[0] for p in pts]
        py = [p[1] for p in pts]
        if (max(px) - min(px) >= 30 or max(py) - min(py) >= 30) and len(pts) >= 4:
            pts = smooth_kernel(pts, KERNEL, CAP)
            pts = [(round(x), round(y)) for x, y in pts]
            fl = list(fl)
            merged += merge_near_dup(pts, fl)
        out_c.extend(pts)
        out_f.extend(fl)
        out_e.append(len(out_c) - 1)
    g.coordinates = GlyphCoordinates(out_c)
    g.flags = array('B', out_f)
    g.endPtsOfContours = out_e
    g.numberOfContours = len(out_e)
    xs = [c[0] for c in out_c]
    ys = [c[1] for c in out_c]
    bb1 = (min(xs), min(ys), max(xs), max(ys))
    drift = max(abs(bb1[i] - bb0[i]) for i in range(4))
    return (before, len(out_c), drift, merged)


def main() -> None:
    assert sha256(BASE) == EXPECTED_BASE_SHA256, 'v0.150 base checksum mismatch'
    traced = json.load(open(TRACED, encoding='utf-8'))
    font = TTFont(BASE, checkChecksums=2)
    assert font['head'].unitsPerEm == 1536
    assert font['name'].getDebugName(5) == 'Version 0.150-beta', 'base is not v0.150'
    glyf = font['glyf']
    hmtx = font['hmtx']
    order = font.getGlyphOrder()
    for name in traced:
        assert name in order, f'{name} not in font'

    log = []
    for name, d in traced.items():
        g = Glyph()
        g.numberOfContours = len(d['ends'])
        g.coordinates = GlyphCoordinates([(int(x), int(y)) for x, y in d['coords']])
        g.flags = array('B', [int(f) for f in d['flags']])
        g.endPtsOfContours = [int(e) for e in d['ends']]
        g.program = Program()
        g.program.fromBytecode(b'')
        removed, inserted = clean_glyph(g)
        before, after, drift, merged = polish_glyph(g)
        glyf[name] = g
        adv, old_lsb = hmtx[name]
        xs = [p[0] for p in g.coordinates]
        new_lsb = min(xs)
        hmtx[name] = (adv, new_lsb)
        log.append({'glyph': name, 'char': d['char'], 'kind': d['kind'],
                    'source': d['source'], 'otsu': d['otsu'],
                    'scale': d['scale'], 'width_ratio': d['width_ratio'],
                    'dropped_contours': d.get('dropped_contours', 0),
                    'clean_removed': removed, 'clean_inserted': inserted,
                    'pts_before_polish': before, 'pts_after_polish': after,
                    'polish_drift': drift, 'polish_merged': merged,
                    'adv': adv, 'lsb_before': old_lsb, 'lsb_after': new_lsb,
                    'fitted_outline_bbox': d['fitted_outline_bbox']})
        print(f"  {d['char']} {name:16s} pts {before}->{after} drift={drift} "
              f"merged={merged} clean_rm={removed} lsb {old_lsb}->{new_lsb}")

    # name table: v0.160-beta (both Mac and Windows records, like v0.150)
    name = font['name']
    for nid, val in [(1, 'Pranoti'), (3, 'Pranoti:Version 0.160-beta'),
                     (4, 'Pranoti Regular'), (5, 'Version 0.160-beta'),
                     (6, 'Pranoti-Regular'), (16, 'Pranoti')]:
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)
    font['head'].fontRevision = 0.160

    font.recalcBBoxes = True
    font.save(OUT)
    print(f'Built: {OUT}')
    print(f'v0.160 SHA-256: {sha256(OUT)}')
    print(f'glyphs: {len(font.getGlyphOrder())}, cmap: '
          f'{len(font.getBestCmap())}')
    json.dump(log, open(ROOT / 'build-log-v0.160.json', 'w'), ensure_ascii=False, indent=1)
    print('wrote build-log-v0.160.json:', len(log), 'glyphs')


if __name__ == '__main__':
    main()
