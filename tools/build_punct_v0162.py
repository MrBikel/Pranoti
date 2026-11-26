#!/usr/bin/env python3
"""Punctuation fine-tuning for Pranoti v0.162-beta (FontForge step).

Run:  fontforge -script tools/build_punct_v0162.py
Reads the v0.161 TTF, applies the per-glyph transforms below, and saves a
TEMPORARY TTF. The temp file is NOT the deliverable: only the changed glyf
outlines are transplanted into a fontTools copy of v0.161 (see
transplant_v0162.py), so every other table stays byte-identical to v0.161.

TWO FontForge behaviours found by testing (2026-11-26, see debug notes):
- `glyph.foreground` returns a COPY of the layer: contour transforms only
  stick if the layer is assigned back (`g.foreground = layer`).
- `glyph.validate()` in-session after addExtrema() returns 524288/524320
  (also in the v0.161 changeweight logs); after generate + reopen the same
  glyph validates 0. So the in-session value is TRANSIENT — the revert
  rule compares validate on the FINAL transplanted TTF, not the log here.

Transforms (targets from checks/punct-inventory-v0.161.json, i.e. the
rasterised TRUE ink boxes; factors are raster-based, pivots are the
FontForge bboxes of the same glyph):
- danda: vertical stretch to the headline (top 1030 -> 1157), bottom kept;
  horizontal stroke stays 84.5.
- doubledanda: each bar thinned 131 -> 86 wide (horizontal scale about the
  bar's own centre) + vertical stretch to the headline, bottom kept.
- colon: upper dot translated so its centre-x = advance centre (298);
  lower dot scaled x-only 260 -> 300 wide and centred at 298.
- semicolon dot: TWO contours (outer dot + inner slot — both transformed
  together about the outer dot's centre): uniform scale 375 -> 300 wide,
  then translated to centre-x 270 and top 945 (colon upper dot's top).
- question dot: scaled to 280x245 about its centre, bottom set to the
  period's bottom (-35). (Was 123x189: a speck.)
- exclam dot: scaled to 280x245 about its centre, centred under the bar;
  y kept BELOW the baseline (the base font's design: its ! dot is at
  -279..-52 too).
- hyphen: horizontal scale 840 -> 532 wide (the base font's hyphen width)
  about its centre; y-band kept (matches the base design).
- slash: changeWeight(-20) -> ~84.5 (the letter median).
- backslash: changeWeight(-55) -> ~91 (near the slash).
- emdash: changeWeight(+25) -> ~132 (matches hyphen 146 / endash 138).

Deliberately UNTOUCHED (see PUNCT-LOG-v0.162.md): the quote families
(left/right height offset is the base font's design), ? curve / ! bar
(tops already match), parens/brackets/braces (pairs internally
consistent; heights are the base design), comma, period, endash, and all
other base symbols.
"""
import json
import fontforge
import psMat
from pathlib import Path

PREP161 = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
PREP162 = Path('/home/hatch/workspace/fonts/bengali-hand/v0162-prep')
BASE = str(PREP161 / 'Pranoti-Regular-v0.161-beta.ttf')
TMP = str(PREP162 / 'tmp-fontforge-punct.ttf')
LOG = PREP162 / 'tools' / 'punct-transforms.json'

HEADLINE = 1157
COLON_CX = 298          # colon advance centre (597 / 2)
DOT_W = 300             # dot-family width (period is 301)
QDOT_W, QDOT_H = 280, 245
SEMICOLON_CX, SEMICOLON_TOP = 270, 945
HYPHEN_W = 532          # base font's hyphen width
PERIOD_BOTTOM = -35


def translate(dx, dy):
    return psMat.translate(dx, dy)


def scale_about(sx, sy, cx, cy):
    """Scale about point (cx, cy). NOTE: in this FontForge build
    psMat.compose(a, b) applies a FIRST, then b (verified numerically:
    the naive order collapsed doubledanda's bars to x 79..261). So the
    translate(-c) must be the FIRST argument."""
    return psMat.compose(psMat.translate(-cx, -cy),
                         psMat.compose(psMat.scale(sx, sy),
                                       psMat.translate(cx, cy)))


def signed_area(contour):
    pts = [(p.x, p.y) for p in contour]
    if len(pts) < 3:
        return 0.0
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1]
                     - pts[(i + 1) % len(pts)][0] * pts[i][1]
                     for i in range(len(pts)))


def snap(g):
    bb = g.boundingBox()
    areas = [round(signed_area(c), 1) for c in g.foreground]
    return {'bbox': [round(v, 1) for v in bb], 'width': g.width,
            'validate': g.validate(), 'n_contours': len(g.foreground),
            'signed_areas': areas}


def main():
    font = fontforge.open(BASE)
    print(f'opened {BASE}: {len(font)} glyphs, em={font.em}')
    log = []

    def transform_contours(g, fn):
        """Apply fn(contour, bbox) to every contour of g (layer copy must
        be assigned back or nothing sticks)."""
        layer = g.foreground
        for c in layer:
            fn(c, c.boundingBox())
        g.foreground = layer

    def touch(name):
        g = font[name]
        return g, snap(g)

    def done(name, g, before, note):
        g.addExtrema()
        g.correctDirection()
        after = snap(g)
        if [a > 0 for a in before['signed_areas']] != [a > 0 for a in after['signed_areas']]:
            print(f'  !! {name}: contour winding CHANGED by transforms!')
        log.append({'glyph': name, 'note': note, 'before': before, 'after': after})
        print(f"  {name:14s} {note} bbox {before['bbox']} -> {after['bbox']} "
              f"validate {before['validate']}->{after['validate']} (in-session; see header)")

    # ---- danda: vertical stretch to headline, bottom kept ----
    g, before = touch('danda')
    assert len(g.foreground) == 1, 'danda: expected 1 contour'
    x0, y0, x1, y1 = g.boundingBox()
    # raster-based factor 1203/1076 about the FF bottom
    f = 1203.0 / 1076.0
    transform_contours(g, lambda c, bb: c.transform(
        (1, 0, 0, f, 0, y0 * (1 - f))))
    done('danda', g, before, f'vert-stretch x{f:.4f} to headline')

    # ---- doubledanda: thin each bar 131->86, stretch to headline ----
    g, before = touch('doubledanda')
    assert len(g.foreground) == 2, 'doubledanda: expected 2 contours'
    def dd(c, bb):
        x0, y0, x1, y1 = bb
        cx = (x0 + x1) / 2
        f = (HEADLINE - y0) / (y1 - y0)
        sx = 86.0 / (x1 - x0)
        m = psMat.compose((1, 0, 0, f, 0, y0 * (1 - f)),
                          scale_about(sx, 1, cx, 0))
        c.transform(m)
    transform_contours(g, dd)
    done('doubledanda', g, before, 'bars 131->86 wide + vert-stretch to headline')

    # ---- colon: align both dots on advance centre; lower dot -> 300 wide ----
    g, before = touch('colon')
    assert len(g.foreground) == 2, 'colon: expected 2 contours'
    layer = g.foreground
    cs = sorted(layer, key=lambda c: (c.boundingBox()[1] + c.boundingBox()[3]) / 2)
    lower, upper = cs[0], cs[1]
    ux0, _, ux1, _ = upper.boundingBox()
    upper.transform(translate(COLON_CX - (ux0 + ux1) / 2, 0))
    lx0, _, lx1, _ = lower.boundingBox()
    lc = (lx0 + lx1) / 2
    lower.transform(scale_about(DOT_W / 260.0, 1, lc, 0))
    lx0, _, lx1, _ = lower.boundingBox()
    lower.transform(translate(COLON_CX - (lx0 + lx1) / 2, 0))
    g.foreground = layer
    done('colon', g, before, 'dots centred at 298; lower dot 260->300 wide')

    # ---- semicolon dot: outer dot + inner slot, scaled together ----
    g, before = touch('semicolon')
    layer = g.foreground
    dot_group = [c for c in layer
                 if (c.boundingBox()[1] + c.boundingBox()[3]) / 2 > 400]
    assert len(dot_group) == 2, f'semicolon: expected 2 dot contours, got {len(dot_group)}'
    outer = max(dot_group, key=lambda c: c.boundingBox()[2] - c.boundingBox()[0])
    ox0, oy0, ox1, oy1 = outer.boundingBox()
    ocx, ocy = (ox0 + ox1) / 2, (oy0 + oy1) / 2
    s = DOT_W / 375.0
    for c in dot_group:
        c.transform(scale_about(s, s, ocx, ocy))
    g.foreground = layer
    # re-read outer bbox, then translate to centre-x 270, top 945
    layer = g.foreground
    outer = max([c for c in layer
                 if (c.boundingBox()[1] + c.boundingBox()[3]) / 2 > 400],
                key=lambda c: c.boundingBox()[2] - c.boundingBox()[0])
    ox0, oy0, ox1, oy1 = outer.boundingBox()
    dx = SEMICOLON_CX - (ox0 + ox1) / 2
    dy = SEMICOLON_TOP - oy1
    for c in layer:
        if (c.boundingBox()[1] + c.boundingBox()[3]) / 2 > 400:
            c.transform(translate(dx, dy))
    g.foreground = layer
    done('semicolon', g, before, 'dot 375->300 wide, centred 270, top 945')

    # ---- question dot: scale to 280x245, bottom on the period's bottom ----
    g, before = touch('question')
    assert len(g.foreground) == 2, 'question: expected 2 contours'
    layer = g.foreground
    dot = min(layer, key=lambda c: (c.boundingBox()[1] + c.boundingBox()[3]) / 2)
    x0, y0, x1, y1 = dot.boundingBox()
    dot.transform(scale_about(QDOT_W / (x1 - x0), QDOT_H / (y1 - y0),
                              (x0 + x1) / 2, (y0 + y1) / 2))
    g.foreground = layer
    layer = g.foreground
    dot = min(layer, key=lambda c: (c.boundingBox()[1] + c.boundingBox()[3]) / 2)
    x0, y0, x1, y1 = dot.boundingBox()
    dot.transform(translate(0, PERIOD_BOTTOM - y0))
    g.foreground = layer
    done('question', g, before, 'dot 123x189 -> 280x245, bottom -35')

    # ---- exclam dot: scale to 280x245, centre under the bar, y kept ----
    g, before = touch('exclam')
    assert len(g.foreground) == 2, 'exclam: expected 2 contours'
    layer = g.foreground
    cs = sorted(layer, key=lambda c: (c.boundingBox()[1] + c.boundingBox()[3]) / 2)
    dot, bar = cs[0], cs[1]
    bx0, _, bx1, _ = bar.boundingBox()
    bar_cx = (bx0 + bx1) / 2
    x0, y0, x1, y1 = dot.boundingBox()
    dot.transform(scale_about(QDOT_W / (x1 - x0), QDOT_H / (y1 - y0),
                              (x0 + x1) / 2, (y0 + y1) / 2))
    g.foreground = layer
    layer = g.foreground
    cs = sorted(layer, key=lambda c: (c.boundingBox()[1] + c.boundingBox()[3]) / 2)
    dot = cs[0]
    x0, y0, x1, y1 = dot.boundingBox()
    dot.transform(translate(bar_cx - (x0 + x1) / 2, 0))
    g.foreground = layer
    done('exclam', g, before, 'dot 161x182 -> 280x245, centred under bar, y kept (below baseline)')

    # ---- hyphen: scale to 532 wide about its centre, y kept ----
    g, before = touch('hyphen')
    assert len(g.foreground) == 1, 'hyphen: expected 1 contour'
    x0, y0, x1, y1 = g.boundingBox()
    cx = (x0 + x1) / 2
    transform_contours(g, lambda c, bb: c.transform(
        scale_about(HYPHEN_W / 840.0, 1, cx, 0)))
    done('hyphen', g, before, 'width 840->532 about centre, y kept')

    # ---- slash / backslash / emdash: changeWeight ----
    for name, delta in (('slash', -20), ('backslash', -55), ('emdash', 25)):
        g, before = touch(name)
        g.changeWeight(delta)
        done(name, g, before, f'changeWeight({delta:+d})')

    font.generate(TMP)
    print(f'generated temp TTF: {TMP}')
    json.dump(log, open(LOG, 'w'), indent=1)
    print(f'wrote {LOG}')
    font.close()


main()
