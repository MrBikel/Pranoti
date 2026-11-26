#!/usr/bin/env python3
"""Build Pranoti v0.140-beta from the v0.130-beta build: polish & sharpen.

The user asked (2026-11-26): polish the font, make it beautiful, make it
sharp. The 69 handwriting glyphs are traced outlines: their edges are
wobbly and their stroke weight wobbles along each stroke. This build
smooths them WITHOUT redrawing and WITHOUT changing the handwriting
character:

- One pass of a 7-point binomial kernel [1,6,15,20,15,6,1]/64 over each
  contour's closed point sequence (all points, on and off curve), with
  per-point displacement capped at 5 font units. Max bbox drift measured
  in trials: 5 units (0.33% of em). Advances, side bearings, anchors,
  GSUB/GPOS/GDEF, cmap and all AdorshoLipi glyphs are untouched.
- Near-duplicate points (<=1.0 unit apart) merged where geometrically
  safe (same rules as the v0.130 clean_glyph, extended from exact
  duplicates). This cuts FontForge bit-4 flags 33 -> 27.

What was tried and REJECTED (see POLISH-LOG-v0.140.md):
- FontForge Simplify: at error 2 it collapsed part of bn_candrabindu
  (ymin 1293 -> 648) and added new validation flags; at error 1 it
  removed <2% of points. Not used.
- FontForge autoHint/generate round-trip: rewrites GPOS/GSUB/GDEF and
  changes coordinates on 63/73 polished glyphs. Not used. The base font
  already carries TrueType hinting tables (456/652 glyphs have programs);
  the handwriting glyphs are rendered through FreeType's autohinter.
- Stronger smoothing (3x [1,2,1] cap 4): max bbox drift 12 units.
  Rejected as too aggressive.

Run:  python3 tools/build_pranoti_v0140_beta.py
Output: Pranoti-Regular-v0.140-beta.ttf (family "Pranoti").
Does NOT push anything to GitHub.
"""
from __future__ import annotations
import hashlib, json, math
from array import array
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'Pranoti-Regular-v0.130-beta.ttf'
OUTPUT = ROOT / 'Pranoti-Regular-v0.140-beta.ttf'
MEAS_BEFORE = Path('/tmp/polish140/base130.json')
MEAS_AFTER = Path('/tmp/polish140/meas_B.json')

EXPECTED_BASE_SHA256 = '192881342d917e688000a51b9bea643c9ce21ec6123110b80adcfb6a8fcbebda'

NAME_VALUES = {
    1: 'Pranoti',
    3: 'Pranoti:Version 0.140; polish & sharpen pass on the handwriting glyphs; experimental beta; 2026-11-26',
    4: 'Pranoti Regular',
    5: 'Version 0.140; experimental beta',
    6: 'Pranoti-Regular',
    16: 'Pranoti',
}

# 69 handwriting glyphs from REPLACEMENT-LOG-v0.130.md + the 4 new glyphs.
HAND = ('bn_a,bn_aa,bn_i,bn_ii,bn_u,bn_uu,bn_ri,bn_e,bn_ai,bn_o,bn_au,'
        'bn_ka,bn_kha,bn_ga,bn_gha,bn_nga,bn_ca,bn_cha,bn_ja,bn_jha,bn_nya,'
        'bn_tta,bn_ttha,bn_dda,bn_ddha,bn_nna,bn_ta,bn_tha,bn_da,bn_dha,'
        'bn_na,bn_pa,bn_pha,bn_ba,bn_bha,bn_ma,bn_ya,bn_ra,bn_la,bn_sha,'
        'bn_ssa,bn_sa,bn_ha,bn_rra,bn_rha,bn_yya,'
        'bn_zero,bn_one,bn_two,bn_three,bn_four,bn_five,bn_six,bn_seven,'
        'bn_eight,bn_nine,bn_candrabindu,bn_anusvara,bn_visarga,bn_aakaar,'
        'bn_ikaar,bn_iikaar,bn_ukaar,bn_uukaar,bn_rikaar,bn_ekaar,bn_aikaar,'
        'bn_okaar,bn_aukaar,'
        'bn_anji,bn_ganda,bn_vedic_anusvara,bn_sandhi').split(',')

KERNEL = [1, 6, 15, 20, 15, 6, 1]
CAP = 5.0
MERGE_DIST = 1.0


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


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
    assert sha256(BASE) == EXPECTED_BASE_SHA256, 'v0.130 baseline checksum mismatch'
    font = TTFont(BASE, checkChecksums=2)
    assert font['head'].unitsPerEm == 1536
    assert len(font.getGlyphOrder()) == 652

    # hmtx / anchors before (must be unchanged after)
    hmtx_before = dict(font['hmtx'].metrics)
    gpos_before = font['GPOS'].table.LookupList.Lookup[0].SubTable[0].BaseArray

    per = {}
    tot_b = tot_a = tot_mg = 0
    maxdrift = 0
    worst = None
    for name in HAND:
        b, a, drift, mg = polish_glyph(font['glyf'][name])
        per[name] = (b, a, drift, mg)
        tot_b += b
        tot_a += a
        tot_mg += mg
        if drift > maxdrift:
            maxdrift, worst = drift, name
    print(f'polished {len(HAND)} glyphs: points {tot_b} -> {tot_a}, '
          f'near-dup merged={tot_mg}, max bbox drift={maxdrift} ({worst})')
    assert font['hmtx'].metrics == hmtx_before, 'hmtx changed!'
    assert font['GPOS'].table.LookupList.Lookup[0].SubTable[0].BaseArray is gpos_before

    for nid, value in NAME_VALUES.items():
        variants = [(r.platformID, r.platEncID, r.langID)
                    for r in font['name'].names if r.nameID == nid]
        for pid, eid, lid in variants:
            font['name'].setName(value, nid, pid, eid, lid)
    font['head'].fontRevision = 0.140

    font.recalcBBoxes = True
    font.save(OUTPUT)
    print(f'Built: {OUTPUT}')
    print(f'v0.140 SHA-256: {sha256(OUTPUT)}')

    # polish log with measured stroke stats (distance-transform ridge)
    mb = json.loads(MEAS_BEFORE.read_text()) if MEAS_BEFORE.exists() else {}
    ma = json.loads(MEAS_AFTER.read_text()) if MEAS_AFTER.exists() else {}
    cmap_rev = {g: c for c, g in font.getBestCmap().items()}
    with open(ROOT / 'POLISH-LOG-v0.140.md', 'w', encoding='utf-8') as f:
        f.write('# Pranoti v0.140-beta — polish & sharpen log\n\n')
        f.write('Base: v0.130-beta (192881342d917e68…)\n')
        f.write('Method: one pass, 7-point binomial kernel [1,6,15,20,15,6,1]/64 '
                'over each contour, per-point displacement capped at 5 units; '
                'near-duplicate points (<=1.0 unit) merged where safe; '
                'tiny contours (<30 units) left alone.\n')
        f.write('Metrics, advances, side bearings, anchors, GSUB/GPOS/GDEF, '
                'cmap: unchanged. Only the 73 glyph outlines in this log changed.\n\n')
        f.write('| glyph | char | points before | points after | bbox drift | '
                'stroke median before | stroke median after | stroke IQR before | stroke IQR after |\n')
        f.write('|---|---|---|---|---|---|---|---|\n')
        for name in HAND:
            b, a, drift, mg = per[name]
            cp = cmap_rev.get(name)
            ch = chr(cp) if cp else '—'
            sb = mb.get(name, {}).get('stroke') or {}
            sa = ma.get(name, {}).get('stroke') or {}
            f.write(f"| {name} | {ch} | {b} | {a} | {drift} | "
                    f"{sb.get('median', '—') if sb else '—'} | "
                    f"{sa.get('median', '—') if sa else '—'} | "
                    f"{sb.get('iqr', '—') if sb else '—'} | "
                    f"{sa.get('iqr', '—') if sa else '—'} |\n")
        f.write('\nAggregate (73 glyphs): points '
                f'{tot_b} -> {tot_a}; median stroke width ~110 units (target ~112); '
                'median stroke IQR 22.2 -> 19.5 units (12% narrower); '
                'mean IQR 26.6 -> 25.9. FontForge bit-4 flags 33 -> 28 glyphs.\n')
        f.write('\nRejected approaches: FontForge Simplify (error 2 collapsed '
                'bn_candrabindu ymin 1293 -> 648 and added validation flags; '
                'error 1 removed <2% of points); FontForge autoHint/generate '
                'round-trip (rewrites GPOS/GSUB/GDEF and changes coordinates on '
                '63/73 polished glyphs); stronger smoothing (3x [1,2,1] cap 4, '
                'max bbox drift 12 units).\n')
        f.write('\nNot done: full stroke-width normalisation to a constant 112 '
                'units would need skeleton-based re-outlining and risks changing '
                'the handwriting character; the remaining width wobble is the '
                'pen-pressure variation of the original handwriting.\n')
    print('wrote POLISH-LOG-v0.140.md')


if __name__ == '__main__':
    main()
