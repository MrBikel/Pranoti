#!/usr/bin/env python3
"""Transplant the 10 punctuation-tuned glyphs into a fontTools copy of v0.161.

Same pattern as v0.161's transplant.py: FontForge's generate() rewrites
tables, so only the changed glyf outlines (+ their hmtx lsb) are copied
into a fontTools copy of the v0.161 font — every other table stays
byte-identical to v0.161 by construction. Name IDs 3/5 and
head.fontRevision become v0.162. clean_glyph (v0.160 hygiene) runs on each
transplanted glyph.

Run: python3 tools/transplant_v0162.py
"""
import hashlib
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0160-prep/tools')
from build_pranoti_v0160_beta import clean_glyph  # noqa: E402

PREP161 = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
PREP162 = Path('/home/hatch/workspace/fonts/bengali-hand/v0162-prep')
BASE = PREP161 / 'Pranoti-Regular-v0.161-beta.ttf'
TMP = PREP162 / 'tmp-fontforge-punct.ttf'
OUT = PREP162 / 'Pranoti-Regular-v0.162-beta.ttf'
EXPECTED_BASE_SHA256 = '9a46dd667efe2cc62b0d5d4cae590796f17cb99990e69c7c07fc7b415bdb5e77'

TOUCHED = ['danda', 'doubledanda', 'colon', 'semicolon', 'question',
           'exclam', 'hyphen', 'slash', 'backslash', 'emdash']
REVERTED = set()  # filled by the validate comparison if any glyph worsens


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    assert sha256(BASE) == EXPECTED_BASE_SHA256, 'v0.161 base checksum mismatch'
    base = TTFont(BASE, checkChecksums=2)
    tmp = TTFont(TMP, checkChecksums=2)
    assert set(base.getGlyphOrder()) == set(tmp.getGlyphOrder()), 'glyph set changed'
    assert len(base.getGlyphOrder()) == len(tmp.getGlyphOrder()) == 652
    assert base.getBestCmap() == tmp.getBestCmap(), 'cmap changed'
    glyf, hmtx = base['glyf'], base['hmtx']
    tglyf = tmp['glyf']
    for name in TOUCHED:
        if name in REVERTED:
            print(f'  {name:14s} REVERTED to v0.161 outline')
            continue
        g = tglyf[name]
        assert not g.isComposite() and g.numberOfContours > 0, f'{name} not simple'
        prog = getattr(g, 'program', None)
        nbc = len(prog.getBytecode()) if prog is not None else 0
        removed, inserted = clean_glyph(g)
        glyf[name] = g
        xs = [p[0] for p in g.coordinates]
        adv, old_lsb = hmtx[name]
        new_lsb = min(xs)
        hmtx[name] = (adv, new_lsb)
        print(f'  {name:14s} pts={len(g.coordinates)} bytecode={nbc} '
              f'clean_rm={removed} clean_ins={inserted} '
              f'lsb {old_lsb}->{new_lsb} adv={adv}')
    name = base['name']
    for nid, val in [(3, 'Pranoti:Version 0.162-beta'),
                     (5, 'Version 0.162-beta')]:
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)
    base['head'].fontRevision = 0.162
    base.recalcBBoxes = True
    base.save(OUT)
    print(f'Built: {OUT}')
    print(f'v0.162 SHA-256: {sha256(OUT)}')
    print(f"glyphs: {len(base.getGlyphOrder())}, cmap: {len(base.getBestCmap())}")


if __name__ == '__main__':
    main()
