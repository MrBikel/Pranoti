#!/usr/bin/env python3
"""Transplant the 4 pass-2 glyphs into the pass-1 v0.161 font.

Same method as transplant.py (fontTools copy, only the changed glyf
outlines + hmtx lsb move; all other tables stay byte-identical). Overwrites
Pranoti-Regular-v0.161-beta.ttf with the pass-2 version.
Run: python3 tools/transplant_pass2.py
"""
import hashlib
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0160-prep/tools')
from build_pranoti_v0160_beta import clean_glyph  # noqa: E402

PREP161 = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
BASE = PREP161 / 'Pranoti-Regular-v0.161-beta.ttf'
TMP = PREP161 / 'tmp-fontforge-pass2.ttf'
EXPECTED_BASE_SHA256 = 'a2c90c66038c83eaa35a63008c38e4cc4b1c28c1336daf2b002cc5d2e3344d27'

TOUCHED = ['bn_ai', 'bn_i', 'bn_e', 'bn_yya']


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    assert sha256(BASE) == EXPECTED_BASE_SHA256, 'pass-1 v0.161 checksum mismatch'
    base = TTFont(BASE, checkChecksums=2)
    tmp = TTFont(TMP, checkChecksums=2)
    assert set(base.getGlyphOrder()) == set(tmp.getGlyphOrder()), 'glyph set changed'
    assert base.getBestCmap() == tmp.getBestCmap(), 'cmap changed'
    glyf, hmtx = base['glyf'], base['hmtx']
    tglyf = tmp['glyf']
    for name in TOUCHED:
        g = tglyf[name]
        assert not g.isComposite() and g.numberOfContours > 0, f'{name} not simple'
        removed, inserted = clean_glyph(g)
        glyf[name] = g
        xs = [p[0] for p in g.coordinates]
        adv, old_lsb = hmtx[name]
        new_lsb = min(xs)
        hmtx[name] = (adv, new_lsb)
        print(f'  {name:14s} pts={len(g.coordinates)} clean_rm={removed} '
              f'clean_ins={inserted} lsb {old_lsb}->{new_lsb} adv={adv}')
    base.recalcBBoxes = True
    base.save(BASE)
    print(f'Saved pass-2 v0.161: {BASE}')
    print(f'v0.161 SHA-256 (pass 2): {sha256(BASE)}')


if __name__ == '__main__':
    main()
