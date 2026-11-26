#!/usr/bin/env python3
"""Transplant the 18 changeWeight'd glyphs into a fontTools copy of v0.160.

Why transplant instead of shipping FontForge's generated TTF: FontForge's
generate() rewrites tables (and its save() writes SFD, not TTF). By copying
only the 18 changed glyf outlines (+ their hmtx lsb) into a fontTools copy
of the v0.160 font, every other table stays byte-identical to v0.160 by
construction. Name IDs 3/5 and head.fontRevision become v0.161.

Also runs clean_glyph (from build_pranoti_v0160_beta.py, the proven v0.160
hygiene step) on each transplanted glyph: changeWeight+addExtrema created
exact duplicate consecutive points (min distance 0.00) on the touched
glyphs, which the v0.160 build had already cleaned out of the base.

Run: python3 tools/transplant.py
"""
import hashlib
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

sys.path.insert(0, '/home/hatch/workspace/fonts/bengali-hand/v0160-prep/tools')
from build_pranoti_v0160_beta import clean_glyph  # noqa: E402

PREP160 = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
PREP161 = Path('/home/hatch/workspace/fonts/bengali-hand/v0161-prep')
BASE = PREP160 / 'Pranoti-Regular-v0.160-beta.ttf'
TMP = PREP161 / 'tmp-fontforge-pass1.ttf'
OUT = PREP161 / 'Pranoti-Regular-v0.161-beta.ttf'
EXPECTED_BASE_SHA256 = '2a50aafe90584e1868fd6dd85c8e03f61cbab46b7ae3333efc9d8e25789ba614'

TOUCHED = ['bn_ai', 'bn_i', 'bn_e', 'bn_yya', 'bn_one', 'bn_six', 'bn_au',
           'bn_kha', 'bn_ga', 'bn_ya', 'bn_aikaar', 'bn_ikaar', 'bn_anusvara',
           'bn_tta', 'bn_cha', 'bn_pa', 'bn_okaar', 'bn_uukaar']

# REVERT (per WEIGHT-PLAN §6 revert rule): bn_anusvara's -15 thin created a
# degenerate kink (two non-adjacent contour points at distance 0.00),
# tripping FontForge validate 0x4 (32 -> 36). A half-delta retry (-7) shrank
# the kink to 1.00 but the 0x4 flag persisted, so the glyph is reverted to
# its v0.160 outline (stroke 100.0, +18% — slightly thick, left for a later
# manual pass). It is NOT transplanted; its v0.160 glyph and hmtx are kept.
REVERTED = {'bn_anusvara'}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    assert sha256(BASE) == EXPECTED_BASE_SHA256, 'v0.160 base checksum mismatch'
    base = TTFont(BASE, checkChecksums=2)
    tmp = TTFont(TMP, checkChecksums=2)
    assert set(base.getGlyphOrder()) == set(tmp.getGlyphOrder()), 'glyph set changed'
    assert len(base.getGlyphOrder()) == len(tmp.getGlyphOrder()) == 652
    # NOTE: FontForge reorders glyphs on generate (e.g. it moves 'dollar'
    # before 'percent'); order is irrelevant here — everything is looked
    # up by name, and the cmap (codepoint -> name) must be identical.
    assert base.getBestCmap() == tmp.getBestCmap(), 'cmap changed'
    glyf, hmtx = base['glyf'], base['hmtx']
    tglyf = tmp['glyf']
    for name in TOUCHED:
        if name in REVERTED:
            print(f'  {name:14s} REVERTED to v0.160 outline (see REVERTED note)')
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
    # name table: v0.161-beta (both Mac and Windows records, like v0.160)
    name = base['name']
    for nid, val in [(3, 'Pranoti:Version 0.161-beta'),
                     (5, 'Version 0.161-beta')]:
        name.setName(val, nid, 3, 1, 0x409)
        name.setName(val, nid, 1, 0, 0)
    base['head'].fontRevision = 0.161
    base.recalcBBoxes = True
    base.save(OUT)
    print(f'Built: {OUT}')
    print(f'v0.161 SHA-256: {sha256(OUT)}')
    print(f"glyphs: {len(base.getGlyphOrder())}, cmap: {len(base.getBestCmap())}")


if __name__ == '__main__':
    main()
