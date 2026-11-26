#!/usr/bin/env python3
"""Transplant the 4 vowel-tuned glyphs into a fontTools copy of v0.162.

Same pattern as v0.161/v0.162: FontForge's generate() rewrites tables, so
only the changed glyf outlines (+ their hmtx lsb) are copied into a
fontTools copy of the v0.162 font — every other table stays byte-identical
to v0.162 by construction. Name IDs 3/5 and head.fontRevision become
v0.163. clean_glyph (v0.160 hygiene) runs on each transplanted glyph.

Run: python3 tools/transplant_v0163.py
"""
import hashlib
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0160-prep/tools')
from build_pranoti_v0160_beta import clean_glyph  # noqa: E402

BASE_DIR = Path('/home/hatch/workspace/fonts/bengali-hand')
PREP162 = BASE_DIR / 'v0162-prep'
PREP163 = BASE_DIR / 'v0163-prep'
BASE = PREP162 / 'Pranoti-Regular-v0.162-beta.ttf'
TMP = PREP163 / 'tmp-fontforge-vowels.ttf'
OUT = PREP163 / 'Pranoti-Regular-v0.163-beta.ttf'
EXPECTED_BASE_SHA256 = '8a4812d097a95cf1c44dfa890875d2aadc100220c20d9034461d22b5d1309f14'

TOUCHED = ['bn_i', 'bn_e', 'bn_ai', 'bn_au']
REVERTED = set()  # filled by the validate comparison if any glyph worsens


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    assert sha256(BASE) == EXPECTED_BASE_SHA256, 'v0.162 base checksum mismatch'
    base = TTFont(BASE, checkChecksums=2)
    tmp = TTFont(TMP, checkChecksums=2)
    assert set(base.getGlyphOrder()) == set(tmp.getGlyphOrder()), 'glyph set changed'
    assert len(base.getGlyphOrder()) == len(tmp.getGlyphOrder()) == 652
    assert base.getBestCmap() == tmp.getBestCmap(), 'cmap changed'
    glyf, hmtx = base['glyf'], base['hmtx']
    tglyf = tmp['glyf']
    for name in TOUCHED:
        if name in REVERTED:
            print(f'  {name:14s} REVERTED to v0.162 outline')
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
    for nid, val in [(3, 'Pranoti:Version 0.163-beta'),
                     (5, 'Version 0.163-beta')]:
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)
    base['head'].fontRevision = 0.163
    base.recalcBBoxes = True
    base.save(OUT)
    print(f'Built: {OUT}')
    print(f'v0.163 SHA-256: {sha256(OUT)}')
    print(f"glyphs: {len(base.getGlyphOrder())}, cmap: {len(base.getBestCmap())}")


if __name__ == '__main__':
    main()
