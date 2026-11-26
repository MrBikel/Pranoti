#!/usr/bin/env python3
"""Draw the 4 missing Bengali glyphs for Pranoti v0.130 from scratch.

Run with FontForge (not plain python3):
    fontforge -lang=py -script tools/draw_new_glyphs.py

Shapes are original designs drawn in AdorshoLipi's style (UPM 1536,
stem ~112), using Noto Sans Bengali renderings only as visual reference
for what each character looks like. No outlines are copied from any font.
Output: inputs/new-glyphs-v0130.ttf (glyphs only; the build script
copies their outlines into the main font).
"""
import fontforge

EM = 1536
STEM = 112

f = fontforge.font()
f.em = EM
f.ascent = 1781
f.descent = 903
f.fontname = "PranotiNewGlyphs0130"
f.familyname = "PranotiNewGlyphs0130"
f.fullname = "PranotiNewGlyphs0130"


def circle(pen, cx, cy, r):
    """Closed circle centreline, 4 cubic segments."""
    k = r * 0.5522847498
    pen.moveTo(cx + r, cy)
    pen.curveTo(cx + r, cy + k, cx + k, cy + r, cx, cy + r)
    pen.curveTo(cx - k, cy + r, cx - r, cy + k, cx - r, cy)
    pen.curveTo(cx - r, cy - k, cx - k, cy - r, cx, cy - r)
    pen.curveTo(cx + k, cy - r, cx + r, cy - k, cx + r, cy)
    pen.closePath()


def anji(g):
    pen = g.glyphPen()
    circle(pen, 310, 810, 205)          # loop centreline
    # stem + bottom hook centreline
    pen.moveTo(520, 780)
    pen.lineTo(520, -20)
    pen.curveTo(520, -95, 480, -100, 420, -60)
    g.stroke("circular", STEM)
    g.simplify()
    g.correctDirection()


def ganda(g):
    pen = g.glyphPen()
    pen.moveTo(430, 640)
    pen.curveTo(250, 520, 140, 300, 180, -40)
    pen.curveTo(220, -160, 400, -200, 560, -210)
    g.stroke("circular", 100)
    g.simplify()
    g.correctDirection()


def vedic(g):
    pen = g.glyphPen()
    # bowl (U shape), two cubic segments
    pen.moveTo(140, 620)
    pen.curveTo(140, 400, 260, 300, 415, 300)
    pen.curveTo(570, 300, 690, 400, 690, 620)
    pen.closePath()
    # diagonal bar at bottom right
    pen.moveTo(310, 150)
    pen.lineTo(660, -80)
    g.stroke("circular", STEM)
    g.simplify()
    g.correctDirection()


def vedic_dot(g):
    # filled dot for the vedic anusvara: a plain filled circle contour.
    # Kept in its own glyph (never stroked); the build script merges its
    # contours into bn_vedic_anusvara.
    pen = g.glyphPen()
    circle(pen, 415, 700, 80)
    g.correctDirection()


def sandhi(g):
    pen = g.glyphPen()
    pen.moveTo(-150, 1330)
    pen.lineTo(150, 1330)
    pen.lineTo(150, 1050)
    pen.curveTo(150, 960, 100, 950, 50, 950)
    g.stroke("circular", 100)
    g.simplify()
    g.correctDirection()


SPECS = [
    (0x0980, "bn_anji", anji),
    (0x09FB, "bn_ganda", ganda),
    (0x09FC, "bn_vedic_anusvara", vedic),
    (0x09FE, "bn_sandhi", sandhi),
    (0xE000, "bn_vedic_dot", vedic_dot),
]

for cp, name, draw in SPECS:
    g = f.createChar(cp, name)
    draw(g)
    g.width = 0

f.generate("inputs/new-glyphs-v0130.ttf")
print("generated inputs/new-glyphs-v0130.ttf")
for cp, name, _ in SPECS:
    g = f[name]
    print(name, "bbox", g.boundingBox(), "width", g.width)
