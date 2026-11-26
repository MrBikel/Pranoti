#!/usr/bin/env python3
"""Build Pranoti v0.130-beta from the v0.120 review build.

Strategy (user's decision, 2026-11-26): progressively REPLACE AdorshoLipi's
glyphs with John's handwriting, glyph by glyph. The v0.120 font is the
skeleton (shaping, metrics, coverage, GSUB/GPOS); John's handwriting is
the flesh. Batch 1 replaces 69 core glyphs with handwriting outlines
from inputs/Pranoti-Handwriting-v4.ttf (UPM 1000 -> 1536), adds the 4
missing codepoints (designed from scratch in inputs/new-glyphs-v0130.ttf),
and generalises candrabindu GPOS from 3 reviewed contexts to anchor-based
mark attachment over all bases, preserving the 3 reviewed offsets exactly.

Run:  python3 tools/build_pranoti_v0130_beta.py
Output: Pranoti-Regular-v0.130-beta.ttf (family "Pranoti").
Does NOT push anything to GitHub.
"""
from __future__ import annotations
import csv
import hashlib
from array import array
from pathlib import Path
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'Pranoti-Regular-v0.120-Private-Owner-Review.ttf'
V4 = ROOT / 'inputs/Pranoti-Handwriting-v4.ttf'
NEWG = ROOT / 'inputs/new-glyphs-v0130.ttf'
TSV = Path('/home/hatch/workspace/fonts/bengali-hand/v0130-prep/v4-core-glyphs.tsv')
OUTPUT = ROOT / 'Pranoti-Regular-v0.130-beta.ttf'

EXPECTED_BASE_SHA256 = '9b6c853a268513f0eece232ad85970307315c3ad579e2c4a2c2ca7f6bf34c748'
EXPECTED_V4_SHA256 = 'd6d283371ff234f0b8d63fde489dc63d835e8f02fe3a046ba661bf3ffad3f55c'
EXPECTED_NEWG_SHA256 = '27101ce02b83a9bc5ccd6fee0db2dc8d01543e5cea7c0f1f5e3ff78c91deb305'

NAME_VALUES = {
    1: 'Pranoti',
    3: 'Pranoti:Version 0.130; first handwriting-replacement batch; experimental beta; 2026-11-26',
    4: 'Pranoti Regular',
    5: 'Version 0.130; experimental beta',
    6: 'Pranoti-Regular',
    16: 'Pranoti',
}

# Reviewed candrabindu offsets (v0.120, UPM 1536) — must be reproduced exactly.
REVIEWED = {'bn_ka': (-450, 125), 'bn_ca': (-278, 125), 'bn_k_ss_ma': (-632, 125)}
MARK_ANCHOR = (-386, 1293)   # bn_candrabindu anchor (centre-x, outline bottom)
MARK_GLYPH = 'bn_candrabindu'
AAKAAR_XMAX = 445            # bn_aakaar outline right edge (used for anchor centring)

# Glyphs to skip replacing (kept AdorshoLipi) with reasons.
SKIP = {'bn_hasanta': 'functional full-height diagonal slash; v4 short bar does not scale'}

NEW_GLYPHS = [
    # codepoint, glyph name, advance, source glyph(s) in new-glyphs TTF
    (0x0980, 'bn_anji', 830, ['bn_anji']),
    (0x09FB, 'bn_ganda', 450, ['bn_ganda']),
    (0x09FC, 'bn_vedic_anusvara', 825, ['bn_vedic_anusvara', 'bn_vedic_dot']),
    (0x09FE, 'bn_sandhi', 0, ['bn_sandhi']),
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def glyph_bbox(font, name):
    g = font['glyf'][name]
    coords, _, _ = g.getCoordinates(font['glyf'])
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return (min(xs), min(ys), max(xs), max(ys))


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


def scaled_glyph(src_font, src_name, scale, tx, ty):
    """Return a new simple glyph: src outline under affine (scale, tx, ty)."""
    pen = TTGlyphPen(None)
    tpen = TransformPen(pen, (scale, 0, 0, scale, tx, ty))
    src_font['glyf'][src_name].draw(tpen, src_font['glyf'])
    g = pen.glyph()
    # round coordinates to integers
    g.coordinates = GlyphCoordinates([(round(x), round(y)) for x, y in g.coordinates])
    clean_glyph(g)
    return g


def main() -> None:
    assert sha256(BASE) == EXPECTED_BASE_SHA256, 'v0.120 baseline checksum mismatch'
    assert sha256(V4) == EXPECTED_V4_SHA256, 'v4 handwriting checksum mismatch'
    assert sha256(NEWG) == EXPECTED_NEWG_SHA256, 'new-glyphs checksum mismatch'

    font = TTFont(BASE, checkChecksums=2)
    v4 = TTFont(V4)
    newg = TTFont(NEWG)
    assert font['head'].unitsPerEm == 1536
    order = font.getGlyphOrder()
    cmap = font.getBestCmap()
    v4cmap = v4.getBestCmap()

    # ---- 1. Batch-1 outline replacement -------------------------------------
    log = []
    replaced = 0
    with open(TSV) as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    for row in rows:
        cp = int(row['codepoint'][2:], 16)
        gh_name = cmap.get(cp)
        v4_name = row['v4_glyph']
        if v4_name == 'MISSING_IN_V4' or gh_name is None:
            log.append((row['char'], gh_name or '-', 'kept AdorshoLipi (absent from v4)'))
            continue
        if gh_name in SKIP:
            log.append((row['char'], gh_name, 'kept AdorshoLipi: ' + SKIP[gh_name]))
            continue
        gx0, gy0, gx1, gy1 = glyph_bbox(font, gh_name)
        vx0, vy0, vx1, vy1 = glyph_bbox(v4, v4_name)
        s = (gy1 - gy0) / (vy1 - vy0)
        tx = gx0 - s * vx0
        ty = gy1 - s * vy1
        font['glyf'][gh_name] = scaled_glyph(v4, v4_name, s, tx, ty)
        # hmtx (advance, lsb) stays the GitHub font's — outline was fitted to it.
        replaced += 1
        flag = '  <-- scale outlier' if not (1.30 <= s <= 1.70) else ''
        log.append((row['char'], gh_name, f'replaced from v4 {v4_name} scale={s:.3f}{flag}'))
    print(f'replaced outlines: {replaced}')

    # ---- 2. Four new glyphs --------------------------------------------------
    new_order = list(order)
    for cp, name, adv, src_names in NEW_GLYPHS:
        assert cp not in cmap, f'U+{cp:04X} already in cmap'
        # merge contours from the source glyph(s) into one glyph
        pen = TTGlyphPen(None)
        for src in src_names:
            newg['glyf'][src].draw(pen, newg['glyf'])
        g = pen.glyph()
        g.coordinates = GlyphCoordinates([(round(x), round(y)) for x, y in g.coordinates])
        clean_glyph(g)
        font['glyf'][name] = g
        x0 = min(c[0] for c in g.coordinates)
        font['hmtx'][name] = (adv, x0)
        new_order.append(name)
        for table in font['cmap'].tables:
            if table.format in (4, 12):
                table.cmap[cp] = name
        print(f'added U+{cp:04X} {name} adv={adv} lsb={x0}')
    font.setGlyphOrder(new_order)

    lig_to_ncomp = {}
    for lk in font['GSUB'].table.LookupList.Lookup:
        for st in lk.SubTable:
            if hasattr(st, 'ligatures'):
                for first, ligset in st.ligatures.items():
                    for lig in ligset:
                        n = 1 + len(lig.Component)
                        if lig.LigGlyph in lig_to_ncomp and lig_to_ncomp[lig.LigGlyph] != n:
                            print(f'WARNING: {lig.LigGlyph} has differing component counts')
                        lig_to_ncomp.setdefault(lig.LigGlyph, n)

    # ---- 3a. GDEF glyph classes (required for HarfBuzz mark attachment:
    # without them bn_candrabindu is class 0 and mark lookups never run) ----
    import unicodedata as _ud
    lig_set = set(lig_to_ncomp)
    mark_name_bits = ('aakaar', 'ikaar', 'ukaar', 'rikaar', 'ekaar', 'aikaar',
                      'okaar', 'aukaar', 'candrabindu', 'anusvara', 'visarga',
                      'hasanta', 'nukta', 'reph', 'phala', 'matra', 'likaar',
                      'llikaar', 'rupeesign', 'initekaar', 'initaikaar',
                      'maphala', 'below_t_ukaar')
    cmap_rev = {g: c for c, g in font.getBestCmap().items()}
    classes = {}
    for gname in font.getGlyphOrder():
        if gname in lig_set:
            classes[gname] = 2
        elif gname in cmap_rev and _ud.category(chr(cmap_rev[gname])) in ('Mn', 'Mc', 'Me'):
            classes[gname] = 3
        elif any(bit in gname for bit in mark_name_bits):
            classes[gname] = 3
        else:
            classes[gname] = 1
    classes['.notdef'] = 1
    cd = ot.ClassDef()
    cd.classDefs = classes
    font['GDEF'].table.GlyphClassDef = cd
    n_mark = sum(1 for v in classes.values() if v == 3)
    n_lig = sum(1 for v in classes.values() if v == 2)
    print(f'GDEF classes: base={len(classes)-n_mark-n_lig} ligature={n_lig} mark={n_mark}')

    # ---- 3. Generalised candrabindu GPOS (anchor-based mark attachment) -----
    # Base glyphs: Bengali letters (Lo) in cmap + the two new Lo letters.
    import unicodedata
    bases = []
    for cp, gname in sorted(font.getBestCmap().items()):
        if unicodedata.category(chr(cp)) == 'Lo' and 0x0980 <= cp <= 0x09FE:
            bases.append(gname)
    # Ligature glyphs from GSUB (any ligature substitution result).

    def anchor_for(gname):
        """(bx, by) for a base/ligature glyph; exact for the 3 reviewed ones."""
        x0, y0, x1, y1 = glyph_bbox(font, gname)
        adv = font['hmtx'][gname][0]
        bx = round((x0 + adv + AAKAAR_XMAX) / 2)
        by = y1 + 276
        if gname in ('bn_ka', 'bn_ca', 'bn_k_ss_ma'):
            by = 1418
        return bx, by

    def anchor(x, y):
        a = ot.Anchor()
        a.Format = 1
        a.XCoordinate = x
        a.YCoordinate = y
        return a

    def coverage(glyphs):
        c = ot.Coverage()
        c.Format = 1
        c.glyphs = sorted(glyphs, key=order_index.__getitem__)
        return c

    order_index = {g: i for i, g in enumerate(font.getGlyphOrder())}

    def mark_array():
        ma = ot.MarkArray()
        ma.MarkCount = 1
        rec = ot.MarkRecord()
        rec.Class = 0
        rec.MarkAnchor = anchor(*MARK_ANCHOR)
        ma.MarkRecord = [rec]
        return ma

    # Lookup 0: MarkBasePos (type 4)
    mb = ot.MarkBasePos()
    mb.Format = 1
    mb.MarkCoverage = coverage([MARK_GLYPH])
    mb.BaseCoverage = coverage(bases)
    mb.ClassCount = 1
    mb.MarkArray = mark_array()
    ba = ot.BaseArray()
    ba.BaseCount = len(bases)
    ba.BaseRecord = []
    for gname in sorted(bases, key=order_index.__getitem__):
        br = ot.BaseRecord()
        bx, by = anchor_for(gname)
        br.BaseAnchor = [anchor(bx, by)]
        ba.BaseRecord.append(br)
    mb.BaseArray = ba

    # Lookup 1: MarkLigPos (type 5) — every component gets the same anchor,
    # so the mark lands in the same place whichever component HarfBuzz picks.
    ml = ot.MarkLigPos()
    ml.Format = 1
    ml.MarkCoverage = coverage([MARK_GLYPH])
    lig_names = sorted(lig_to_ncomp, key=order_index.__getitem__)
    ml.LigatureCoverage = coverage(lig_names)
    ml.ClassCount = 1
    ml.MarkArray = mark_array()
    la = ot.LigatureArray()
    la.LigatureCount = len(lig_names)
    la.LigatureAttach = []
    for gname in lig_names:
        bx, by = anchor_for(gname)
        att = ot.LigatureAttach()
        att.ComponentCount = lig_to_ncomp[gname]
        att.ComponentRecord = []
        for _ in range(lig_to_ncomp[gname]):
            cr = ot.ComponentRecord()
            cr.LigatureAnchor = [anchor(bx, by)]
            att.ComponentRecord.append(cr)
        la.LigatureAttach.append(att)
    ml.LigatureArray = la

    def lookup(ltype, subtable):
        lk = ot.Lookup()
        lk.LookupType = ltype
        lk.LookupFlag = 0
        lk.SubTable = [subtable]
        lk.MarkFilteringSet = None
        return lk

    gpos = newTable('GPOS')
    gpos.table = ot.GPOS()
    gpos.table.Version = 0x00010000
    sl = ot.ScriptList()
    sl.ScriptCount = 1
    sr = ot.ScriptRecord()
    sr.ScriptTag = 'beng'
    sc = ot.Script()
    dls = ot.DefaultLangSys()
    dls.ReqFeatureIndex = 0xFFFF
    dls.FeatureIndex = [0]
    sc.DefaultLangSys = dls
    sc.LangSysRecord = []
    sr.Script = sc
    sl.ScriptRecord = [sr]
    gpos.table.ScriptList = sl
    fl = ot.FeatureList()
    fl.FeatureCount = 1
    fr = ot.FeatureRecord()
    fr.FeatureTag = 'mark'
    feat = ot.Feature()
    feat.FeatureParams = None
    feat.LookupListIndex = [0, 1]
    fr.Feature = feat
    fl.FeatureRecord = [fr]
    gpos.table.FeatureList = fl
    ll = ot.LookupList()
    ll.LookupCount = 2
    ll.Lookup = [lookup(4, mb), lookup(5, ml)]
    gpos.table.LookupList = ll
    font['GPOS'] = gpos
    print(f'GPOS: mark-to-base over {len(bases)} bases, mark-to-ligature over {len(lig_names)} ligatures')

    # ---- 4. Names / version ---------------------------------------------------
    for nid, value in NAME_VALUES.items():
        variants = [(r.platformID, r.platEncID, r.langID)
                    for r in font['name'].names if r.nameID == nid]
        for pid, eid, lid in variants:
            font['name'].setName(value, nid, pid, eid, lid)
    font['head'].fontRevision = 0.130

    font.recalcBBoxes = True  # recalculated on save (bool flag in fontTools 4.46)
    font.save(OUTPUT)
    print(f'Built: {OUTPUT}')
    print(f'v0.130 SHA-256: {sha256(OUTPUT)}')

    with open(ROOT / 'REPLACEMENT-LOG-v0.130.md', 'w', encoding='utf-8') as f:
        f.write('# Pranoti v0.130-beta — replacement log\n\n')
        f.write(f'Base: v0.120 review build ({EXPECTED_BASE_SHA256[:12]}…)\n')
        f.write(f'Handwriting source: v4 ({EXPECTED_V4_SHA256[:12]}…)\n\n')
        f.write('| char | glyph | action |\n|---|---|---|\n')
        for ch, gname, action in log:
            f.write(f'| {ch} | {gname} | {action} |\n')
        f.write('\nNew glyphs (designed from scratch): U+0980 bn_anji, '
                'U+09FB bn_ganda, U+09FC bn_vedic_anusvara, U+09FE bn_sandhi.\n')
    print('wrote REPLACEMENT-LOG-v0.130.md')


if __name__ == '__main__':
    main()
