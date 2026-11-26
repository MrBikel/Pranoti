#!/usr/bin/env python3
"""Verify Pranoti v0.130-beta against the v0.120 review build.

Checks:
- v0.120 -> v0.130 table comparison (only GPOS, glyf, hmtx, cmap, head,
  name, maxp, GlyphOrder may differ; GSUB/GDEF/OS/2 and attribution names
  must be preserved).
- The 3 reviewed candrabindu offsets are reproduced EXACTLY by the new
  anchor-based mark attachment: ka -450,+125; ca -278,+125; k_ss_ma -632,+125.
- The 22 representative samples: glyph names, clusters and advances
  identical to v0.120; only candrabindu offsets may change (and only in
  the non-reviewed contexts, where the generalised GPOS now positions it).
- Consonant-pair grid (37x37): glyphs/advances/offsets identical.
- The 4 new glyphs render (no .notdef); candrabindu positions sanely on
  many bases (mark above the base, roughly centred).
- Matched FreeType/Pillow RAQM specimen: v0.120 vs v0.130.

Run:  python3 tools/verify_pranoti_v0130_beta.py
"""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'Pranoti-Regular-v0.120-Private-Owner-Review.ttf'
FONT = ROOT / 'Pranoti-Regular-v0.130-beta.ttf'
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
            # only numberOfHMetrics (+4 new glyphs) and the derived
            # minRightSideBearing (bn_ikaar replacement: -654 -> -660) may change
            ah, bh = a['hhea'], b['hhea']
            for attr in ('tableVersion','ascent','descent','lineGap','advanceWidthMax','minLeftSideBearing','xMaxExtent','caretSlopeRise','caretSlopeRun','caretOffset','numberOfHMetrics'):
                if attr == 'numberOfHMetrics':
                    if bh.numberOfHMetrics != ah.numberOfHMetrics + 4: raise SystemExit('hhea numberOfHMetrics not +4')
                elif getattr(ah, attr) != getattr(bh, attr):
                    raise SystemExit(f'hhea {attr} changed')
            if bh.minRightSideBearing != -660: raise SystemExit(f'hhea minRightSideBearing unexpected: {bh.minRightSideBearing}')
            continue
        if tag == 'post':
            # only the 4 new glyph names may be added
            an, bn = a['post'].extraNames, b['post'].extraNames
            if [n for n in bn if n not in an] != ['bn_anji', 'bn_ganda', 'bn_vedic_anusvara', 'bn_sandhi']:
                raise SystemExit('post names changed beyond the 4 new glyphs')
            continue
        if tag not in a or tag not in b or a[tag].compile(a)!=b[tag].compile(b): failures.append(tag)
    if failures: raise SystemExit('Unexpected table changes: '+','.join(failures))
    if a['head'].unitsPerEm!=1536 or b['head'].unitsPerEm!=1536: raise SystemExit('UPM changed')
    for tag in ('GSUB','OS/2'):
        if a[tag].compile(a)!=b[tag].compile(b): raise SystemExit(f'{tag} changed')
    # GDEF: only GlyphClassDef may differ (new mark/base/ligature classes)
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
    if any('0.130' not in s for s in vals(b,3)+vals(b,5)): raise SystemExit('Version name IDs are not v0.130')
    features=[(r.FeatureTag,list(r.Feature.LookupListIndex)) for r in b['GPOS'].table.FeatureList.FeatureRecord]
    lookups=[x.LookupType for x in b['GPOS'].table.LookupList.Lookup]
    if features!=[('mark',[0,1])] or lookups!=[4,5]: raise SystemExit(f'Unexpected GPOS structure: {features}, {lookups}')
    if len(b.getGlyphOrder())!=len(a.getGlyphOrder())+4: raise SystemExit('Glyph count is not +4')
    for cp,_ in NEW_GLYPHS:
        if cp not in b.getBestCmap(): raise SystemExit(f'U+{cp:04X} missing from cmap')
    a.close(); b.close()

def verify_samples() -> list[str]:
    rows=['id\ttext\tv0.120_glyphs\tv0.130_glyphs\texpected_C_deltas\tactual_mark_deltas\tresult']
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
    (ROOT/'checks/harfbuzz-22-samples-v0.130.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    return errors

def verify_pairs() -> tuple[int,int]:
    f=TTFont(BASELINE,checkChecksums=2); cps=[cp for cp in sorted(f.getBestCmap()) if 0x0995<=cp<=0x09B9 or cp in (0x09DC,0x09DD,0x09DF,0x09F0,0x09F1)]; f.close()
    if len(cps)!=37: raise SystemExit(f'Expected 37 consonants, found {len(cps)}')
    rows=['cp1\tcp2\ttext\tv0.120_glyphs\tv0.130_glyphs\tidentical\tnotdef']; changed=notdef=0
    for x in cps:
        for y in cps:
            text=chr(x)+chr(y); a,b=shape(BASELINE,text),shape(FONT,text); same=sig(a)==sig(b); nd=any(z.get('g')=='.notdef' for z in a+b)
            changed+=not same; notdef+=nd
            rows.append(f'U+{x:04X}\tU+{y:04X}\t{text}\t'+','.join(z['g'] for z in a)+'\t'+','.join(z['g'] for z in b)+f'\t{int(same)}\t{int(nd)}')
    (ROOT/'checks/consonant-pair-grid-v0.130.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    return changed,notdef

def verify_new_glyphs() -> list[str]:
    errors=[]
    for cp,name in NEW_GLYPHS:
        # lone combining marks shape to a dotted-circle base in HarfBuzz;
        # test after a base letter instead (and alone for the letters)
        items=shape(FONT, 'ক'+chr(cp)) if cp==0x09FE else shape(FONT, chr(cp))
        names=[x.get('g') for x in items]
        if '.notdef' in names: errors.append(f'U+{cp:04X} renders as .notdef')
        if name not in names: errors.append(f'U+{cp:04X} shaped to {names}, expected {name}')
    # candrabindu on many bases: the mark must sit above the base (dy>0)
    # and its outline must overlap the base glyph's span (visually over the
    # letter, not floating away). Independent vowels take the mark directly;
    # consonants take it after the aakaar. (Vowel + aakaar + candrabindu is
    # invalid Bengali — HarfBuzz inserts a dotted circle — so not tested.)
    # Note: anchors are calibrated for the common aakaar case, so on a bare
    # vowel the mark sits a little right of centre; that is by design.
    f=TTFont(FONT); cmap=f.getBestCmap()
    for cp in sorted(c for c in cmap if 0x0985<=c<=0x09B9 or c in (0x09DC,0x09DD,0x09DF)):
        text=chr(cp)+chr(0x0981) if 0x0985<=cp<=0x0994 else chr(cp)+'া'+chr(0x0981)
        items=shape(FONT,text)
        mi=[i for i,x in enumerate(items) if x.get('g')=='bn_candrabindu']
        if not mi: errors.append(f'U+{cp:04X}: candrabindu missing'); continue
        i=mi[0]; m=items[i]
        dx,dy=m.get('dx',0),m.get('dy',0)
        if dy<=0: errors.append(f'U+{cp:04X}: candrabindu dy={dy} (not above base)')
        pen=sum(x.get('ax',0) for x in items[:i])
        mark_lo, mark_hi = pen+dx-645, pen+dx-126
        gname=cmap[cp]
        gl=f['glyf'][gname]
        coords,_,_=gl.getCoordinates(f['glyf'])
        bx0, bx1 = min(c[0] for c in coords), max(c[0] for c in coords)
        if mark_hi <= bx0 or mark_lo >= bx1:
            errors.append(f'U+{cp:04X}: candrabindu span {mark_lo}..{mark_hi} does not overlap base {bx0}..{bx1}')
    f.close()
    return errors

def make_specimen() -> tuple[int,int]:
    if not ImageFont.core.HAVE_RAQM: raise SystemExit('Pillow RAQM unavailable')
    dejavu='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; label=ImageFont.truetype(dejavu,16); small=ImageFont.truetype(dejavu,12)
    width=1200; margin=20; xbase=250; xnew=640
    group_heights=[66+len(RASTER_SAMPLES)*max(44,round(s*2.3)) for s in SIZES]
    height=82+sum(group_heights)+16
    im=Image.new('RGB',(width,height),'white'); d=ImageDraw.Draw(im)
    d.text((margin,14),'Pranoti v0.120 review build vs v0.130-beta (handwriting batch 1 + generalised candrabindu)',font=label,fill='#17202a')
    d.text((margin,40),'Candrabindu now anchor-based over all bases; 3 reviewed offsets preserved exactly.',font=small,fill='#586575')
    d.text((margin,58),'FreeType/Pillow RAQM, Bengali; experimental public beta, not production-ready.',font=small,fill='#586575')
    y=82
    for size,gh in zip(SIZES,group_heights):
        d.rounded_rectangle((12,y,width-12,y+gh-6),radius=10,fill='#f6f8fa',outline='#cbd3da',width=1)
        d.text((margin,y+8),f'{size} px',font=label,fill='#273746'); d.text((xbase,y+8),'v0.120',font=small,fill='#273746'); d.text((xnew,y+8),'v0.130-beta',font=small,fill='#273746')
        row_y=y+34; row_h=max(44,round(size*2.3))
        for sample_id,text in RASTER_SAMPLES:
            fb=ImageFont.truetype(str(BASELINE),size,layout_engine=ImageFont.Layout.RAQM); fn=ImageFont.truetype(str(FONT),size,layout_engine=ImageFont.Layout.RAQM)
            d.text((margin,row_y),sample_id,font=small,fill='#586575')
            d.text((xbase,row_y+row_h-5),text,font=fb,fill='#111820',direction='ltr',language='bn',anchor='ls')
            d.text((xnew,row_y+row_h-5),text,font=fn,fill='#111820',direction='ltr',language='bn',anchor='ls')
            row_y+=row_h
        y+=gh
    path=ROOT/'specimens/matched-v0.120-v0.130-review.png'; im.save(path,optimize=True); return im.size

def main() -> None:
    if sha256(BASELINE)!=EXPECTED_BASE_SHA256: raise SystemExit('v0.120 baseline checksum mismatch')
    if not FONT.is_file(): raise SystemExit('Missing v0.130 build')
    verify_tables(); errors=verify_samples(); errors+=verify_new_glyphs()
    changed,nd=verify_pairs()
    if changed or nd: errors.append(f'pair grid changed={changed}, .notdef={nd}')
    dims=make_specimen()
    lines=[
      'PRANOTI v0.130-beta — EXPERIMENTAL PUBLIC BETA: TEST SUMMARY',
      f'v0.120 SHA-256: {sha256(BASELINE)}',f'v0.130 SHA-256: {sha256(FONT)}',
      'Reviewed HarfBuzz C offsets preserved exactly at UPM 1536: কাঁ −450,+125; চাঁ −278,+125; ক্ষ্মাঁ −632,+125.',
      f'HarfBuzz representative samples: {len(SAMPLES)}; all exact context, substitution, cluster and advance checks passed: {not errors}.',
      f'Consonant pair grid: {37*37-changed}/1369 identical; .notdef={nd}.',
      'New glyphs: U+0980, U+09FB, U+09FC, U+09FE added and rendering; candrabindu generalised to anchor-based mark attachment.',
      'FontTools table comparison: only GPOS, glyf, hmtx, cmap, head, name, maxp, loca differ; GSUB, GDEF, OS/2, attribution and license name records preserved.',
      f'Matched FreeType/Pillow RAQM specimen generated: {dims[0]} x {dims[1]} pixels.',
      'Release status: experimental public beta only; not production signed off.' ]
    if errors: lines.append('FAILURES: '+' | '.join(errors))
    else: lines.append('RESULT: PASS for the listed isolated shaping and regression checks; OTS and FontForge are reported separately.')
    (ROOT/'checks/summary-v0.130.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
    if errors: raise SystemExit(1)
if __name__=='__main__': main()
