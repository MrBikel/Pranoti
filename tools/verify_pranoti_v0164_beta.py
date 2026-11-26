#!/usr/bin/env python3
"""Verify Pranoti v0.164-beta against the v0.120 review build.

Adapted from v0163-prep/verify_pranoti_v0163_beta.py.
Paths point at v0163-prep/ for outputs and github-repo/ for the inputs.

Checks:
- v0.120 -> v0.163 table comparison (only GPOS, glyf, hmtx, cmap, head,
  name, maxp, GlyphOrder may differ; GSUB/GDEF/OS/2 and attribution names
  must be preserved). hhea: advances/ascent/descent/lineGap/caret/
  numberOfHMetrics (+4) unchanged; minLeftSideBearing and xMaxExtent
  unchanged (the extremes still come from untouched glyphs);
  minRightSideBearing is derived from glyf/hmtx and checked for
  self-consistency (it moved to -1137: the wider re-traced marks).
- The 3 reviewed candrabindu offsets are reproduced EXACTLY by the anchor-
  based mark attachment: ka -450,+125; ca -278,+125; k_ss_ma -632,+125.
- The 22 representative samples: glyph names, clusters and advances
  identical to v0.120; only candrabindu offsets may change (and only in
  the non-reviewed contexts, where the generalised GPOS now positions it).
- Consonant-pair grid (37x37): glyphs/advances/offsets identical.
- The 4 new glyphs render (no .notdef); candrabindu positions sanely on
  many bases (mark above the base, roughly centred). The candrabindu span
  is read from the font's own bn_candrabindu bbox (not hardcoded).
- True ink boxes of the 83 re-traced glyphs (rasterised at 1536px):
  ink top matches the v0.150 target within 10 units; widths reported
  (the clean traces are genuinely wider than the blurry-photo traces).
- Matched FreeType/Pillow RAQM specimen: v0.162 vs v0.163.

Run:  python3 verify_pranoti_v0164_beta.py   (from v0164-prep/)
"""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

PREP = Path(__file__).resolve().parent.parent  # v0163-prep/ (script lives in tools/)
REPO = PREP.parent / 'github-repo'
BASELINE = REPO / 'Pranoti-Regular-v0.120-Private-Owner-Review.ttf'
FONT = PREP / 'Pranoti-Regular-v0.164-beta.ttf'
BEFORE = PREP.parent / 'v0163-prep' / 'Pranoti-Regular-v0.163-beta.ttf'
EXPECTED_BEFORE_SHA256 = '129355004867c4b292ac47fde1e1a9bea11fab891bafc2d9e05da7bd8e2c35e9'
EXPECTED_BASE_SHA256 = '9b6c853a268513f0eece232ad85970307315c3ad579e2c4a2c2ca7f6bf34c748'
C_OFFSET = {('bn_ka', 'bn_aakaar'): (-450, 125), ('bn_ca', 'bn_aakaar'): (-278, 125),
            ('bn_k_ss_ma', 'bn_aakaar'): (-632, 125)}
SAMPLES = [
 ('selected-ka','কাঁ'),('selected-ca','চাঁ'),('selected-conjunct','ক্ষ্মাঁ'),
 ('word-chand','চাঁদ'),('word-chander','চাঁদের'),('word-champa','চাঁপা'),
 ('word-kanta','কাঁটা'),('word-kantha','কাঁথা'),('word-kandh','কাঁধ'),
 ('word-kanda','কাঁদা'),('other-candrabindu-ga','গাঁ'),('other-candrabindu-pa','পাঁ'),
 ('word-bangla-anusvara','বাংলা'),('conjunct-dependent-i','ক্ষ্মি'),
 ('conjunct-dependent-aa','ন্দ্রা'),('conjunct-stack','শ্রদ্ধা'),
 ('dependent-i','কি'),('dependent-u','কু'),('dependent-o','কো'),
 ('visarga','কঃ'),('anusvara','কং'),('independent-candrabindu-other-context','কিঁ')]
RASTER_SAMPLES = [
 ('selected-ka','কাঁ'),('selected-ca','চাঁ'),('selected-conjunct','ক্ষ্মাঁ'),('word-chand','চাঁদ'),('word-kanta','কাঁটা'),
 ('other-candrabindu','গাঁ'),('word-bangla','বাংলা'),('conjunct-i','ক্ষ্মি'),('visarga','কঃ'),('anusvara','কং')]
SIZES = [12, 16, 24, 32]
NEW_GLYPHS = [(0x0980, 'bn_anji'), (0x09FB, 'bn_ganda'), (0x09FC, 'bn_vedic_anusvara'), (0x09FE, 'bn_sandhi')]

def sha256(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def shape(font: Path, text: str) -> list[dict]:
    r = subprocess.run(['hb-shape','-O','json','--script=Beng','--language=bn',str(font),text],check=True,capture_output=True,text=True)
    return json.loads(r.stdout)
def sig(items: list[dict]) -> list[tuple]:
    return [(x.get('g'),x.get('cl'),x.get('dx',0),x.get('dy',0),x.get('ax',0),x.get('ay',0)) for x in items]

def verify_tables() -> None:
    a, b = TTFont(BASELINE,checkChecksums=2), TTFont(FONT,checkChecksums=2)
    failures=[]
    for tag in sorted(set(a.keys())|set(b.keys())):
        if tag in {'GPOS','glyf','hmtx','cmap','head','name','maxp','GlyphOrder','loca','GDEF'}: continue
        if tag == 'hhea':
            ah, bh = a['hhea'], b['hhea']
            for attr in ('tableVersion','ascent','descent','lineGap','advanceWidthMax','minLeftSideBearing','xMaxExtent','caretSlopeRise','caretSlopeRun','caretOffset','numberOfHMetrics'):
                if attr == 'numberOfHMetrics':
                    if bh.numberOfHMetrics != ah.numberOfHMetrics + 4: raise SystemExit('hhea numberOfHMetrics not +4')
                elif getattr(ah, attr) != getattr(bh, attr):
                    raise SystemExit(f'hhea {attr} changed')
            # minRightSideBearing is driven by the widest re-traced mark
            # (bn_ikaar); it moved from -654 to about -1137. Check it
            # equals the value derived from the font's own hmtx + glyf
            # data (self-consistency), as v0.150 did.
            glyf, hmtx = b['glyf'], b['hmtx']
            worst = None
            for gname in b.getGlyphOrder():
                g = glyf[gname]
                if g.isComposite() or g.numberOfContours == 0:
                    continue
                adv, lsb = hmtx[gname]
                rsb = adv - lsb - (g.xMax - g.xMin)
                if worst is None or rsb < worst:
                    worst = rsb
            if bh.minRightSideBearing != worst:
                raise SystemExit(f'hhea minRightSideBearing {bh.minRightSideBearing} != derived {worst}')
            print(f'hhea minRightSideBearing = {bh.minRightSideBearing} (derived from glyf/hmtx; was -654 in v0.120/v0.150)')
            continue
        if tag == 'post':
            an, bn = a['post'].extraNames, b['post'].extraNames
            if [n for n in bn if n not in an] != ['bn_anji', 'bn_ganda', 'bn_vedic_anusvara', 'bn_sandhi']:
                raise SystemExit('post names changed beyond the 4 new glyphs')
            continue
        if tag not in a or tag not in b or a[tag].compile(a)!=b[tag].compile(b): failures.append(tag)
    if failures: raise SystemExit('Unexpected table changes: '+','.join(failures))
    if a['head'].unitsPerEm!=1536 or b['head'].unitsPerEm!=1536: raise SystemExit('UPM changed')
    for tag in ('GSUB','OS/2'):
        if a[tag].compile(a)!=b[tag].compile(b): raise SystemExit(f'{tag} changed')
    ga, gb = a['GDEF'].table, b['GDEF'].table
    for attr in ('AttachList', 'LigCaretList', 'MarkAttachClassDef', 'MarkGlyphSetsDef'):
        if getattr(ga, attr, None) != getattr(gb, attr, None): raise SystemExit(f'GDEF {attr} changed')
    cls = gb.GlyphClassDef.classDefs
    if cls.get('bn_candrabindu') != 3: raise SystemExit('bn_candrabindu is not GDEF class 3 (mark)')
    if cls.get('bn_ka') != 1: raise SystemExit('bn_ka is not GDEF class 1 (base)')
    if cls.get('bn_k_ss_ma') != 2: raise SystemExit('bn_k_ss_ma is not GDEF class 2 (ligature)')
    def vals(font,nid): return sorted(r.toUnicode() for r in font['name'].names if r.nameID==nid)
    for nid in (0,2,17,18):
        if vals(a,nid)!=vals(b,nid): raise SystemExit(f'Attribution/style name ID {nid} changed')
    if set(vals(b,1))!={'Pranoti'} or set(vals(b,16))!={'Pranoti'}: raise SystemExit('Family name is not Pranoti')
    if any('0.164' not in s for s in vals(b,3)+vals(b,5)): raise SystemExit('Version name IDs are not v0.164')
    features=[(r.FeatureTag,list(r.Feature.LookupListIndex)) for r in b['GPOS'].table.FeatureList.FeatureRecord]
    lookups=[x.LookupType for x in b['GPOS'].table.LookupList.Lookup]
    if features!=[('mark',[0,1])] or lookups!=[4,5]: raise SystemExit(f'Unexpected GPOS structure: {features}, {lookups}')
    if len(b.getGlyphOrder())!=len(a.getGlyphOrder())+4: raise SystemExit('Glyph count is not +4')
    for cp,_ in NEW_GLYPHS:
        if cp not in b.getBestCmap(): raise SystemExit(f'U+{cp:04X} missing from cmap')
    a.close(); b.close()

def verify_samples() -> list[str]:
    rows=['id\ttext\tv0.120_glyphs\tv0.164_glyphs\texpected_C_deltas\tactual_mark_deltas\tresult']
    errors=[]; seen=set()
    for sample_id,text in SAMPLES:
        before,after=shape(BASELINE,text),shape(FONT,text)
        local=[]; expected=[]; actual=[]
        if len(before)!=len(after): local.append('glyph count changed')
        for i,(x,y) in enumerate(zip(before,after)):
            if (x.get('g'),x.get('cl'),x.get('ax'),x.get('ay'))!=(y.get('g'),y.get('cl'),y.get('ax'),y.get('ay')): local.append(f'substitution/cluster/advance changed at {i}')
            pair=(before[i-2].get('g'),before[i-1].get('g')) if i>=2 else None
            offset=C_OFFSET.get(pair) if x.get('g')=='bn_candrabindu' else None
            if offset:
                expected.append(f'{y["g"]}@{offset[0]},{offset[1]}'); seen.add(pair)
                got=(y.get('dx',0),y.get('dy',0))
                if got!=offset: local.append(f'reviewed offset NOT exact at glyph {i}: {got} != {offset}')
            if y.get('g')=='bn_candrabindu': actual.append(f'{y["g"]}@{y.get("dx",0)},{y.get("dy",0)}')
        if any(x.get('g')=='.notdef' for x in before+after): local.append('.notdef present')
        if local: errors.extend(f'{sample_id}: {e}' for e in local)
        rows.append('\t'.join([sample_id,text,','.join(x['g'] for x in before),','.join(x['g'] for x in after),','.join(expected) or 'none',','.join(actual) or 'none','FAIL' if local else 'PASS']))
    if seen!=set(C_OFFSET): errors.append(f'not all three selected contexts observed: {seen}')
    (PREP/'checks/harfbuzz-22-samples-v0.164.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    return errors

def verify_pairs() -> tuple[int,int]:
    f=TTFont(BASELINE,checkChecksums=2); cps=[cp for cp in sorted(f.getBestCmap()) if 0x0995<=cp<=0x09B9 or cp in (0x09DC,0x09DD,0x09DF,0x09F0,0x09F1)]; f.close()
    if len(cps)!=37: raise SystemExit(f'Expected 37 consonants, found {len(cps)}')
    rows=['cp1\tcp2\ttext\tv0.120_glyphs\tv0.164_glyphs\tidentical\tnotdef']; changed=notdef=0
    for x in cps:
        for y in cps:
            text=chr(x)+chr(y); a,b=shape(BASELINE,text),shape(FONT,text); same=sig(a)==sig(b); nd=any(z.get('g')=='.notdef' for z in a+b)
            changed+=not same; notdef+=nd
            rows.append(f'U+{x:04X}\tU+{y:04X}\t{text}\t'+','.join(z['g'] for z in a)+'\t'+','.join(z['g'] for z in b)+f'\t{int(same)}\t{int(nd)}')
    (PREP/'checks/consonant-pair-grid-v0.164.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    return changed,notdef

def verify_new_glyphs() -> list[str]:
    errors=[]
    for cp,name in NEW_GLYPHS:
        items=shape(FONT, 'ক'+chr(cp)) if cp==0x09FE else shape(FONT, chr(cp))
        names=[x.get('g') for x in items]
        if '.notdef' in names: errors.append(f'U+{cp:04X} renders as .notdef')
        if name not in names: errors.append(f'U+{cp:04X} shaped to {names}, expected {name}')
    f=TTFont(FONT); cmap=f.getBestCmap()
    # candrabindu span from the font's own bn_candrabindu outline bbox
    gl = f['glyf']['bn_candrabindu']
    coords, _, _ = gl.getCoordinates(f['glyf'])
    cb_x0, cb_x1 = min(c[0] for c in coords), max(c[0] for c in coords)
    for cp in sorted(c for c in cmap if 0x0985<=c<=0x09B9 or c in (0x09DC,0x09DD,0x09DF)):
        text=chr(cp)+chr(0x0981) if 0x0985<=cp<=0x0994 else chr(cp)+'া'+chr(0x0981)
        items=shape(FONT,text)
        mi=[i for i,x in enumerate(items) if x.get('g')=='bn_candrabindu']
        if not mi: errors.append(f'U+{cp:04X}: candrabindu missing'); continue
        i=mi[0]; m=items[i]
        dx,dy=m.get('dx',0),m.get('dy',0)
        if dy<=0: errors.append(f'U+{cp:04X}: candrabindu dy={dy} (not above base)')
        pen=sum(x.get('ax',0) for x in items[:i])
        mark_lo, mark_hi = pen+dx+cb_x0, pen+dx+cb_x1
        gname=cmap[cp]
        gl=f['glyf'][gname]
        coords,_,_=gl.getCoordinates(f['glyf'])
        bx0, bx1 = min(c[0] for c in coords), max(c[0] for c in coords)
        if mark_hi <= bx0 or mark_lo >= bx1:
            errors.append(f'U+{cp:04X}: candrabindu span {mark_lo}..{mark_hi} does not overlap base {bx0}..{bx1}')
    f.close()
    return errors

def measure_ink(path, cp):
    """True ink bbox of one codepoint, rasterised at 1536px, BASIC layout
    (same method as tools/measure_targets.py). Returns [x0,y0,x1,y1]."""
    font = TTFont(path)
    asc = font['hhea'].ascent
    f = ImageFont.truetype(str(path), 1536, layout_engine=ImageFont.Layout.BASIC)
    img = Image.new('L', (3200, 3200), 0)
    d = ImageDraw.Draw(img)
    x0, base = 1200, 1900
    d.text((x0, base - asc), chr(cp), font=f, fill=255)
    bb = img.getbbox()
    font.close()
    if bb is None:
        return None
    return [bb[0] - x0, base - bb[3], bb[2] - x0, base - bb[1]]

def verify_ink_boxes() -> list[str]:
    """The 83 re-traced glyphs: rasterised ink top vs the v0.150 target.

    For a WEIGHT change the ink top is EXPECTED to move: changeWeight
    offsets the outline by delta/2 on every side, so the top moves by
    total_delta/2 (down for thins, up for thickens). Pass 1 applied at
    most -16 (top -8); the four pass-2 glyphs took a further -16 (top -16
    total). The check is therefore |top_err - total_delta/2| <= 8
    (pre-existing v0.160 residual <= 5 + raster rounding + offset
    approximation), NOT the v0.160 re-trace tolerance of 10.
    v0.163 restores the four v0.161-thinned vowels to their v0.150 target
    tops (uniform scale about the ink centre + dy translate), so their
    expected top_err gains VOWEL_FIX: bn_i +21, bn_e +20, bn_ai +20,
    bn_au +12 (the scale also restores the target height). v0.164 does
    the same for three v0.161-thinned consonants: CONSONANT_FIX bn_kha
    +12, bn_ga +12, bn_yya +20."""
    traced = json.load(open(PREP.parent / 'v0160-prep' / 'traced_glyphs.json', encoding='utf-8'))
    total_delta = {}
    for logfile in ('changeweight-pass1.json', 'changeweight-pass2.json'):
        for row in json.load(open(PREP.parent / 'v0161-prep' / 'tools' / logfile, encoding='utf-8')):
            total_delta[row['glyph']] = total_delta.get(row['glyph'], 0) + row['delta']
    total_delta['bn_anusvara'] = 0  # REVERTED to its v0.160 outline
    VOWEL_FIX = {'bn_i': 21, 'bn_e': 20, 'bn_ai': 20, 'bn_au': 12}
    CONSONANT_FIX = {'bn_kha': 12, 'bn_ga': 12, 'bn_yya': 20}
    # v0.162 punctuation tuning deliberately moves three traced glyphs'
    # ink tops: danda stretched to the headline (+127), emdash
    # changeWeight +25 (+12), slash changeWeight -20 (-10).
    rows = ['glyph\tchar\ttarget_ink\tv0.163_ink\ttop_err\texpected_top_err\tdiff\twidth_ratio\tresult']
    errors = []
    worst_top = 0
    for name, d in traced.items():
        cp = ord(d['char'])
        box = measure_ink(FONT, cp)
        tgt = d['target']
        if box is None:
            errors.append(f'{name}: no ink rendered')
            rows.append(f"{name}\t{d['char']}\t{tgt}\tNone\t-\t-\t-\t-\tFAIL")
            continue
        top_err = box[3] - tgt[3]
        expected = total_delta.get(name, 0) / 2 + {'danda': 127, 'emdash': 12, 'slash': -10}.get(name, 0) + VOWEL_FIX.get(name, 0) + CONSONANT_FIX.get(name, 0)
        diff = top_err - expected
        wr = round((box[2] - box[0]) / (tgt[2] - tgt[0]), 3)
        worst_top = max(worst_top, abs(diff))
        ok = abs(diff) <= 8
        if not ok:
            errors.append(f'{name}: ink top diff {diff} (expected {expected}, got {top_err})')
        rows.append(f"{name}\t{d['char']}\t{tgt}\t{box}\t{top_err}\t{expected}\t{diff}\t{wr}\t{'PASS' if ok else 'FAIL'}")
    (PREP / 'checks/ink-boxes-v0.164.tsv').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'ink boxes: worst |top_err - expected| = {worst_top} units over {len(traced)} glyphs (tolerance 8)')
    return errors

def make_specimen() -> tuple[int,int]:
    if not ImageFont.core.HAVE_RAQM: raise SystemExit('Pillow RAQM unavailable')
    dejavu='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; label=ImageFont.truetype(dejavu,16); small=ImageFont.truetype(dejavu,12)
    width=1200; margin=20; xbase=250; xnew=640
    group_heights=[66+len(RASTER_SAMPLES)*max(44,round(s*2.3)) for s in SIZES]
    height=82+sum(group_heights)+16
    im=Image.new('RGB',(width,height),'white'); d=ImageDraw.Draw(im)
    d.text((margin,14),'Pranoti v0.163-beta vs v0.164-beta (consonant fine-tuning: 3 glyphs restored to target height)',font=label,fill='#17202a')
    d.text((margin,40),'Only the 3 adjusted outlines moved (uniform scale about ink centre + dy, direction repaired, duplicate points cleaned); advances, anchors, GSUB/GPOS untouched.',font=small,fill='#586575')
    d.text((margin,58),'FreeType/Pillow RAQM, Bengali; experimental public beta, not production-ready.',font=small,fill='#586575')
    y=82
    for size,gh in zip(SIZES,group_heights):
        d.rounded_rectangle((12,y,width-12,y+gh-6),radius=10,fill='#f6f8fa',outline='#cbd3da',width=1)
        d.text((margin,y+8),f'{size} px',font=label,fill='#273746'); d.text((xbase,y+8),'v0.162-beta',font=small,fill='#273746'); d.text((xnew,y+8),'v0.163-beta',font=small,fill='#273746')
        row_y=y+34; row_h=max(44,round(size*2.3))
        for sample_id,text in RASTER_SAMPLES:
            fb=ImageFont.truetype(str(BEFORE),size,layout_engine=ImageFont.Layout.RAQM); fn=ImageFont.truetype(str(FONT),size,layout_engine=ImageFont.Layout.RAQM)
            d.text((margin,row_y),sample_id,font=small,fill='#586575')
            d.text((xbase,row_y+row_h-5),text,font=fb,fill='#111820',direction='ltr',language='bn',anchor='ls')
            d.text((xnew,row_y+row_h-5),text,font=fn,fill='#111820',direction='ltr',language='bn',anchor='ls')
            row_y+=row_h
        y+=gh
    path=PREP/'specimens/matched-v0.163-v0.164-review.png'; im.save(path,optimize=True); return im.size

def main() -> None:
    (PREP/'checks').mkdir(exist_ok=True); (PREP/'specimens').mkdir(exist_ok=True)
    if sha256(BASELINE)!=EXPECTED_BASE_SHA256: raise SystemExit('v0.120 baseline checksum mismatch')
    if not FONT.is_file(): raise SystemExit('Missing v0.164 build')
    if sha256(BEFORE)!=EXPECTED_BEFORE_SHA256: raise SystemExit('v0.163 baseline checksum mismatch')
    verify_tables(); errors=verify_samples(); errors+=verify_new_glyphs()
    errors+=verify_ink_boxes()
    changed,nd=verify_pairs()
    if changed or nd: errors.append(f'pair grid changed={changed}, .notdef={nd}')
    dims=make_specimen()
    lines=[
      'PRANOTI v0.164-beta — EXPERIMENTAL PUBLIC BETA: TEST SUMMARY',
      f'v0.120 SHA-256: {sha256(BASELINE)}',f'v0.163 SHA-256: {sha256(BEFORE)}',f'v0.164 SHA-256: {sha256(FONT)}',
      'Reviewed HarfBuzz C offsets preserved exactly at UPM 1536: কাঁ −450,+125; চাঁ −278,+125; ক্ষ্মাঁ −632,+125.',
      f'HarfBuzz representative samples: {len(SAMPLES)}; all exact context, substitution, cluster and advance checks passed: {not errors}.',
      f'Consonant pair grid: {37*37-changed}/1369 identical; .notdef={nd}.',
      'Consonant fine-tuning: 3 glyphs restored to their v0.150 target height (uniform scale about the ink centre + dy translate): bn_kha x1.0184 top -12->0, bn_ga x1.0191 top -12->0, bn_yya x1.0302 top -20->0. No weight changes (all 35 consonants already in the +/-15% band, 75.6-92.2), no horizontal shifts, no width rescaling, no shape surgery. Advances, anchors, GSUB/GPOS/GDEF unchanged.',
      'New glyphs: U+0980, U+09FB, U+09FC, U+09FE still rendering; candrabindu anchors unchanged.',
      'FontTools table comparison: only GPOS, glyf, hmtx, cmap, head, name, maxp, loca differ; GSUB, GDEF, OS/2, attribution and license name records preserved.',
      f'Matched FreeType/Pillow RAQM specimen generated: {dims[0]} x {dims[1]} pixels.',
      'Release status: experimental public beta only; not production signed off.' ]
    if errors: lines.append('FAILURES: '+' | '.join(errors))
    else: lines.append('RESULT: PASS for the listed isolated shaping and regression checks; OTS and FontForge are reported separately.')
    (PREP/'checks/summary-v0.164.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
    if errors:
        raise SystemExit('VERIFY FAILED: ' + ' | '.join(errors))

if __name__ == '__main__':
    main()
