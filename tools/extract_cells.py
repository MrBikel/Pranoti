#!/usr/bin/env python3
"""v0.160 cell extraction: run grid detection on the clean source photos,
assign each detected cell to its glyph by the known sheet layout, save
tight cell crops, and build labelled contact sheets for visual checking.

Layouts (verified by reading the photos):
  Vowel sheet (11 rows x 7): rows অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ, 7 instances each.
  Consonant sheet (10 rows):
    R0 ক খ গ ঘ ঙ চ ছ জ ঝ ঞ
    R1 ট ঠ ড ঢ ণ ত থ দ ধ ন
    R2 প ফ ব ভ ম য র ল শ ষ
    R3 স হ ড় ঢ় য় ৎ ং ঃ ঁ
    R4 া ি ী ু ূ ৃ ে ৈ ো ৌ
    R5 ো ৌ ো ৌ            (duplicates of R4's last two — backups)
    R6 । . , ; : :- : – — --- ...   (":-" and "---" ambiguous, "..." has no cmap entry)
    R7 / ‘ ’ “ ” ? !
    R8 ১ ২ ৩ ৪ ৫ ৬ ৭ ৮ ৯ ০
    R9 1 2 3 4 5 6 7 8 9 0  (Latin digits — out of scope, extracted for reference only)
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parent))
from grid_detect import detect

ROOT = Path('/home/hatch/workspace/fonts/bengali-hand/v0160-prep')
PHOTOS = Path('/home/hatch/workspace/user/files')

VOWEL_ROWS = ['অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'এ', 'ঐ', 'ও', 'ঔ']
VOWEL_GLYPHS = ['bn_a', 'bn_aa', 'bn_i', 'bn_ii', 'bn_u', 'bn_uu', 'bn_ri',
                'bn_e', 'bn_ai', 'bn_o', 'bn_au']
VOWEL_FILES = ['1000036047_1_lxem.jpg', '1000038364_2_t9wh.jpg',
               '1000036048_3_pr9o.jpg', '1000036049_4_24mu.jpg']

CONS_ROWS = [
    (['ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ'],
     ['bn_ka', 'bn_kha', 'bn_ga', 'bn_gha', 'bn_nga', 'bn_ca', 'bn_cha',
      'bn_ja', 'bn_jha', 'bn_nya']),
    (['ট', 'ঠ', 'ড', 'ঢ', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন'],
     ['bn_tta', 'bn_ttha', 'bn_dda', 'bn_ddha', 'bn_nna', 'bn_ta', 'bn_tha',
      'bn_da', 'bn_dha', 'bn_na']),
    (['প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ'],
     ['bn_pa', 'bn_pha', 'bn_ba', 'bn_bha', 'bn_ma', 'bn_ya', 'bn_ra',
      'bn_la', 'bn_sha', 'bn_ssa']),
    (['স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ'],
     ['bn_sa', 'bn_ha', 'bn_rra', 'bn_rha', 'bn_yya', None,
      'bn_anusvara', 'bn_visarga', 'bn_candrabindu']),
    (['া', 'ি', 'ী', 'ু', 'ূ', 'ৃ', 'ে', 'ৈ', 'ো', 'ৌ'],
     ['bn_aakaar', 'bn_ikaar', 'bn_iikaar', 'bn_ukaar', 'bn_uukaar',
      'bn_rikaar', 'bn_ekaar', 'bn_aikaar', 'bn_okaar', 'bn_aukaar']),
    (['ো', 'ৌ', 'ো', 'ৌ'], ['bn_okaar', 'bn_aukaar', 'bn_okaar', 'bn_aukaar']),
    (['।', '.', ',', ';', ':', ':-', ':', '–', '—', '---', '...'],
     ['danda', 'period', 'comma', 'semicolon', 'colon', None, 'colon',
      'hyphen', 'emdash', None, None]),
    (['/', '‘', '’', '“', '”', '?', '!'],
     ['slash', 'quoteleft', 'quoteright', 'quotedblleft', 'quotedblright',
      'question', 'exclam']),
    (['১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯', '০'],
     ['bn_one', 'bn_two', 'bn_three', 'bn_four', 'bn_five', 'bn_six',
      'bn_seven', 'bn_eight', 'bn_nine', 'bn_zero']),
    (['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
     [None] * 10),
]
CONS_FILES = ['1000033792_16_ve4v.jpg']  # photo 17 is backup only: its
# left edge carries a dark strip that the detector reads as an extra
# column; use it only for individual damaged cells, case by case.


def extract(photo, layout_rows, tag, outdir):
    """layout_rows: list of (chars, glyph_names). Returns manifest list."""
    path = PHOTOS / photo
    shape, bands, cells, grid = detect(str(path))
    im = Image.open(path).convert('L')
    W, H = im.size
    man = []
    assert len(bands) == len(layout_rows), \
        f'{photo}: {len(bands)} bands, expected {len(layout_rows)} rows'
    by_band = {}
    for (bi, ci, x0, y0, x1, y1) in cells:
        by_band.setdefault(bi, []).append((ci, x0, y0, x1, y1))
    for bi, (chars, glyphs) in enumerate(layout_rows):
        got = sorted(by_band.get(bi, []))
        if len(got) != len(chars):
            print(f'  !! {photo} band {bi}: {len(got)} cells, expected {len(chars)} '
                  f'({chars})')
        for ci, (cj, x0, y0, x1, y1) in enumerate(got):
            if ci >= len(chars):
                print(f'  !! {photo} band {bi}: extra cell {cj} at x{x0}-{x1}')
                continue
            pad = 8
            cx0, cy0 = max(0, x0 - pad), max(0, y0 - pad)
            cx1, cy1 = min(W, x1 + 1 + pad), min(H, y1 + 1 + pad)
            crop = im.crop((cx0, cy0, cx1, cy1))
            name = f'{tag}_r{bi + 1}c{ci + 1}.png'
            crop.save(outdir / name)
            man.append(dict(photo=photo, tag=tag, row=bi + 1, col=ci + 1,
                            char=chars[ci], glyph=glyphs[ci],
                            box=[x0, y0, x1, y1], cropbox=[cx0, cy0, cx1, cy1],
                            file=str(outdir / name)))
    return man


def sheet(cells_info, out, cols=7, cell_px=150, label=None):
    n = len(cells_info)
    rows = (n + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell_px, rows * (cell_px + 20)), 'white')
    d = ImageDraw.Draw(sheet)
    try:
        fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    except Exception:
        fnt = ImageFont.load_default()
    for i, info in enumerate(cells_info):
        crop = Image.open(info['file']).convert('L')
        w, h = crop.size
        s = min((cell_px - 4) / max(w, 1), (cell_px - 4) / max(h, 1), 1.0)
        crop = crop.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
        cx, cy = (i % cols) * cell_px, (i // cols) * (cell_px + 20)
        sheet.paste(crop, (cx + (cell_px - crop.width) // 2,
                           cy + (cell_px - crop.height) // 2))
        lab = label(info) if label else info.get('char', '')
        d.text((cx + 4, cy + cell_px + 2), lab, fill='black', font=fnt)
    sheet.save(out)
    print('wrote', out)


def main():
    outdir = ROOT / 'cells'
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for photo in VOWEL_FILES:
        tag = photo.split('_')[0][-2:] if False else photo[:10]
        tag = 'vow_' + photo.split('_')[1]  # vow_1, vow_2, ...
        layout = [( [c], [g]) for c, g in zip(VOWEL_ROWS, VOWEL_GLYPHS)]
        # expand: each row has 7 instances of the same glyph
        rows = []
        for c, g in zip(VOWEL_ROWS, VOWEL_GLYPHS):
            rows.append(([c] * 7, [g] * 7))
        print(photo, '->', tag)
        manifest += extract(photo, rows, tag, outdir)
    for photo in CONS_FILES:
        tag = 'cons_' + photo.split('_')[1]
        print(photo, '->', tag)
        manifest += extract(photo, CONS_ROWS, tag, outdir)
    json.dump(manifest, open(ROOT / 'cells.json', 'w'), ensure_ascii=False, indent=1)
    print('total cells:', len(manifest))
    # contact sheets
    vow1 = [m for m in manifest if m['tag'] == 'vow_1']
    sheet(vow1, ROOT / 'contact_vowels.png', cols=7,
          label=lambda m: f"r{m['row']}c{m['col']} {m['char']}")
    cons16 = [m for m in manifest if m['tag'] == 'cons_16']
    sheet(cons16, ROOT / 'contact_consonants.png', cols=10,
          label=lambda m: f"r{m['row']}c{m['col']} {m['char']}")
    print('done')


if __name__ == '__main__':
    main()
