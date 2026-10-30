#!/usr/bin/env python3
"""Build the byte-preserved Pranoti v0.120 experimental public-beta TTF from immutable v0.119."""
from __future__ import annotations
import hashlib
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'inputs/Pranoti-Regular-v0.119.ttf'
FEATURES = ROOT / 'source/candrabindu-C-contextual-mark.fea'
OUTPUT = ROOT / 'Pranoti-Regular-v0.120-Private-Owner-Review.ttf'
EXPECTED_BASELINE_SHA256 = '66a969bc0277bc0aff93d49a9e89fc5701c53f8db515df28ad973b6e36d667ee'
EXPECTED_SFD_SHA256 = 'c25f8529621b92a161841245b64546c6f5d5bf1ae07956e848f83f1f93bf63d1'

NAME_VALUES = {
    1: 'Pranoti v0.120 Review',
    3: 'Pranoti:Version 0.120; one original Bengali abbreviation glyph; private owner-review build; 2026-10-30',
    4: 'Pranoti v0.120 Review Regular',
    5: 'Version 0.120; private owner-review build; experimental',
    6: 'Pranoti-v0-120-Review-Regular',
    16: 'Pranoti v0.120 Review',
}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    source_sfd = ROOT / 'source/Pranoti-Regular-v0.119.sfd'
    if sha256(BASELINE) != EXPECTED_BASELINE_SHA256:
        raise SystemExit('Immutable v0.119 TTF checksum mismatch')
    if sha256(source_sfd) != EXPECTED_SFD_SHA256:
        raise SystemExit('Immutable v0.119 SFD checksum mismatch')
    if not FEATURES.is_file():
        raise SystemExit(f'Missing approved feature source: {FEATURES}')

    font = TTFont(BASELINE, checkChecksums=2, recalcBBoxes=False, recalcTimestamp=False)
    if font['head'].unitsPerEm != 1536:
        raise SystemExit('Unexpected units per em')
    if font['GPOS'].table.FeatureList.FeatureRecord or font['GPOS'].table.LookupList.Lookup:
        raise SystemExit('Expected empty baseline GPOS feature and lookup lists')
    # Crucial: compile GPOS only. Do not regenerate GSUB or any outline tables.
    addOpenTypeFeaturesFromString(font, FEATURES.read_text(encoding='utf-8'), tables=['GPOS'])

    # Keep all platform/language variants aligned so Office and other apps identify
    # this as a separate, clearly labeled review family from the v0.119 baseline.
    for name_id, value in NAME_VALUES.items():
        variants = [(r.platformID, r.platEncID, r.langID)
                    for r in font['name'].names if r.nameID == name_id]
        if not variants:
            raise SystemExit(f'Required name ID {name_id} is missing')
        for platform_id, encoding_id, language_id in variants:
            font['name'].setName(value, name_id, platform_id, encoding_id, language_id)

    font.recalcTimestamp = False
    font.save(OUTPUT, reorderTables=True)
    font.close()
    print(f'Built: {OUTPUT}')
    print(f'v0.119 input SHA-256: {sha256(BASELINE)}')
    print(f'v0.119 SFD SHA-256: {sha256(source_sfd)}')
    print(f'v0.120 review TTF SHA-256: {sha256(OUTPUT)}')

if __name__ == '__main__':
    main()
