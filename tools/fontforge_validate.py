#!/usr/bin/env python3
"""FontForge validate for Pranoti v0.160-beta (and a baseline for comparison).

Runs glyph.validate() on every glyph in the font and reports how many
glyphs carry each validation bit. Run:
  fontforge -script tools/fontforge_validate.py <ttf> [ttf ...]
"""
import sys
import fontforge


def main():
    for path in sys.argv[1:]:
        font = fontforge.open(path)
        total = 0
        by_bit = {}
        flagged = []
        for gname in font:
            g = font[gname]
            v = g.validate()
            if v:
                total += 1
                flagged.append((gname, v))
                b = 0
                while (1 << b) <= v:
                    if v & (1 << b):
                        by_bit[b] = by_bit.get(b, 0) + 1
                    b += 1
        print(f'{path}: {total} glyphs with validation flags out of {len(font)}')
        for b in sorted(by_bit):
            print(f'  bit {b} (value {1 << b}): {by_bit[b]} glyphs')
        print('  flagged glyphs: ' + ', '.join(f'{n}={v}' for n, v in flagged))
        font.close()


if __name__ == '__main__':
    main()
