#!/usr/bin/env python3
"""Geometric self-intersection + near-duplicate check for TTF glyph outlines.

FontForge validate bit 0x4 means "glyph intersects itself", but the same
bit is also tripped by degenerate/near-duplicate points (a zero-length
segment looks like a self-intersection to the test). This script separates
the two: it flattens each quadratic contour to a polyline (implied
on-curve midpoints made explicit, correct cyclic walk) and checks for
proper crossings between non-adjacent segments of the SAME contour, and
reports the minimum distance between consecutive raw outline points.

Usage: python3 check_self_intersection.py <ttf> <glyph> [<glyph> ...]
"""
import math
import sys
from fontTools.ttLib import TTFont


def expand_contour(pts, fl):
    """Expanded cyclic point list: (x, y, on) starting at an on-curve point,
    implied midpoints between consecutive off-curve points made explicit."""
    n = len(pts)
    si = next((i for i in range(n) if fl[i] & 1), None)
    if si is None:
        out = [((pts[-1][0] + pts[0][0]) / 2, (pts[-1][1] + pts[0][1]) / 2, True)]
        seq = [(pts[i], bool(fl[i] & 1)) for i in range(n)]
    else:
        out = [(pts[si][0], pts[si][1], True)]
        seq = [(pts[(si + k) % n], bool(fl[(si + k) % n] & 1)) for k in range(1, n)]
    for (p, on) in seq:
        if not on and not out[-1][2]:
            q = out[-1]
            out.append(((q[0] + p[0]) / 2, (q[1] + p[1]) / 2, True))
        out.append((p[0], p[1], on))
    if not out[-1][2]:
        q, s = out[-1], out[0]
        out.append(((q[0] + s[0]) / 2, (q[1] + s[1]) / 2, True))
    return out


def flatten_glyph(font, name, steps=16):
    """List of contours, each a polyline [(x, y), ...] (closed, no dup end)."""
    glyf = font['glyf']
    g = glyf[name]
    if g.isComposite() or g.numberOfContours <= 0:
        return []
    coords, ends, flags = g.getCoordinates(glyf)
    contours = []
    start = 0
    for e in ends:
        pts = list(coords[start:e + 1])
        fl = list(flags[start:e + 1])
        start = e + 1
        out = expand_contour(pts, fl)
        m = len(out)
        poly = [(out[0][0], out[0][1])]
        i = 0
        while i < m:
            p0 = out[i]
            p1 = out[(i + 1) % m]
            if p1[2]:
                poly.append((p1[0], p1[1]))
                i += 1
            else:
                p2 = out[(i + 2) % m]
                for k in range(1, steps + 1):
                    t = k / steps
                    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
                    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
                    poly.append((x, y))
                i += 2
        if poly[-1] == poly[0]:
            poly.pop()
        contours.append(poly)
    return contours


def seg_intersect(a, b, c, d):
    """Proper intersection of segments ab and cd (excluding shared endpoints)."""
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return ((o1 > 0) != (o2 > 0)) and ((o3 > 0) != (o4 > 0))


def check(font, name):
    contours = flatten_glyph(font, name)
    glyf = font['glyf']
    g = glyf[name]
    coords, ends, flags = g.getCoordinates(glyf)
    min_d, min_pair = None, None
    start = 0
    for e in ends:
        pts = list(coords[start:e + 1])
        start = e + 1
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            d = math.hypot(q[0] - p[0], q[1] - p[1])
            if min_d is None or d < min_d:
                min_d, min_pair = d, (p, q)
    crossings = []
    for ci, poly in enumerate(contours):
        segs = [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]
        for i in range(len(segs)):
            for j in range(i + 2, len(segs)):
                if i == 0 and j == len(segs) - 1:
                    continue  # adjacent (closed contour wrap)
                if seg_intersect(segs[i][0], segs[i][1], segs[j][0], segs[j][1]):
                    crossings.append((ci, i, j))
    return min_d, min_pair, crossings


def main():
    path = sys.argv[1]
    names = sys.argv[2:]
    font = TTFont(path)
    for name in names:
        min_d, min_pair, crossings = check(font, name)
        status = 'CROSSINGS=%d' % len(crossings) if crossings else 'no crossings'
        print(f'{name:14s} min_consec_dist={min_d:.2f} at {min_pair}  {status}')
        for c in crossings[:5]:
            print(f'    crossing: contour {c[0]} segments {c[1]} & {c[2]}')


if __name__ == '__main__':
    main()
