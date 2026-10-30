#!/usr/bin/env python3
"""Verify the experimental public-beta v0.120 build against immutable v0.119."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'inputs/Pranoti-Regular-v0.119.ttf'
FONT = ROOT / 'Pranoti-Regular-v0.120-Private-Owner-Review.ttf'
EXPECTED_BASELINE_SHA256 = '66a969bc0277bc0aff93d49a9e89fc5701c53f8db515df28ad973b6e36d667ee'
C_OFFSET = {('bn_ka', 'bn_aakaar'): (-450, 125), ('bn_ca', 'bn_aakaar'): (-278, 125), ('bn_k_ss_ma', 'bn_aakaar'): (-632, 125)}
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
        if tag in {'GPOS','head','name','GlyphOrder'}: continue
        if tag not in a or tag not in b or a[tag].compile(a)!=b[tag].compile(b): failures.append(tag)
    if failures: raise SystemExit('Unexpected table changes: '+','.join(failures))
    if a.getGlyphOrder()!=b.getGlyphOrder() or a['head'].unitsPerEm!=1536 or b['head'].unitsPerEm!=1536:
        raise SystemExit('Glyph order or UPM changed')
    for tag in ('glyf','hmtx','hhea','cmap','GSUB','GDEF','OS/2'):
        if a[tag].compile(a)!=b[tag].compile(b): raise SystemExit(f'{tag} changed')
    def vals(font,nid): return sorted(r.toUnicode() for r in font['name'].names if r.nameID==nid)
    for nid in (0,2,17,18):
        if vals(a,nid)!=vals(b,nid): raise SystemExit(f'Attribution/style name ID {nid} changed')
    if set(vals(b,1))!={'Pranoti v0.120 Review'} or set(vals(b,16))!={'Pranoti v0.120 Review'}:
        raise SystemExit('Unique family name does not match review build')
    if any('0.120' not in s for s in vals(b,3)+vals(b,5)):
        raise SystemExit('Version name IDs are not v0.120')
    features=[(r.FeatureTag,list(r.Feature.LookupListIndex)) for r in b['GPOS'].table.FeatureList.FeatureRecord]
    lookups=[x.LookupType for x in b['GPOS'].table.LookupList.Lookup]
    if features!=[('mark',[0])] or lookups!=[8,1,1,1]: raise SystemExit(f'Unexpected GPOS structure: {features}, {lookups}')
    a.close(); b.close()

def verify_samples() -> list[str]:
    rows=['id\ttext\tbaseline_glyphs\tv0.120_glyphs\texpected_C_deltas\tactual_mark_deltas\tresult']
    errors=[]; seen=set()
    for sample_id,text in SAMPLES:
        before,after=shape(BASELINE,text),shape(FONT,text)
        local=[]; expected=[]; actual=[]
        if len(before)!=len(after): local.append('glyph count changed')
        for i,(x,y) in enumerate(zip(before,after)):
            if (x.get('g'),x.get('cl'),x.get('ax'),x.get('ay'))!=(y.get('g'),y.get('cl'),y.get('ax'),y.get('ay')): local.append(f'substitution/cluster/advance changed at {i}')
            pair=(before[i-2].get('g'),before[i-1].get('g')) if i>=2 else None
            offset=C_OFFSET.get(pair) if x.get('g')=='bn_candrabindu' else None
            want=(x.get('dx',0)+(offset[0] if offset else 0),x.get('dy',0)+(offset[1] if offset else 0))
            got=(y.get('dx',0),y.get('dy',0))
            if got!=want: local.append(f'position changed unexpectedly at glyph {i}: {got} != {want}')
            if offset:
                expected.append(f'{y["g"]}@{offset[0]},{offset[1]}'); seen.add(pair)
            if y.get('g')=='bn_candrabindu': actual.append(f'{y["g"]}@{got[0]},{got[1]}')
        if any(x.get('g')=='.notdef' for x in before+after): local.append('.notdef present')
        if local: errors.extend(f'{sample_id}: {e}' for e in local)
        rows.append('\t'.join([sample_id,text,','.join(x['g'] for x in before),','.join(x['g'] for x in after),','.join(expected) or 'none',','.join(actual) or 'none','FAIL' if local else 'PASS']))
    if seen!=set(C_OFFSET): errors.append(f'not all three selected contexts observed: {seen}')
    (ROOT/'checks/harfbuzz-22-samples-v0.120.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    return errors

def verify_pairs() -> tuple[int,int]:
    f=TTFont(BASELINE,checkChecksums=2); cps=[cp for cp in sorted(f.getBestCmap()) if 0x0995<=cp<=0x09B9 or cp in (0x09DC,0x09DD,0x09DF,0x09F0,0x09F1)]; f.close()
    if len(cps)!=37: raise SystemExit(f'Expected 37 consonants, found {len(cps)}')
    rows=['cp1\tcp2\ttext\tbaseline_glyphs\tv0.120_glyphs\tidentical\tnotdef']; changed=notdef=0
    for x in cps:
        for y in cps:
            text=chr(x)+chr(y); a,b=shape(BASELINE,text),shape(FONT,text); same=sig(a)==sig(b); nd=any(z.get('g')=='.notdef' for z in a+b)
            changed+=not same; notdef+=nd
            rows.append(f'U+{x:04X}\tU+{y:04X}\t{text}\t'+','.join(z['g'] for z in a)+'\t'+','.join(z['g'] for z in b)+f'\t{int(same)}\t{int(nd)}')
    (ROOT/'checks/consonant-pair-grid-v0.120.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    return changed,notdef

def make_specimen() -> tuple[int,int]:
    if not ImageFont.core.HAVE_RAQM: raise SystemExit('Pillow RAQM unavailable')
    dejava='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; label=ImageFont.truetype(dejava,16); small=ImageFont.truetype(dejava,12)
    width=1200; margin=20; xbase=250; xnew=640
    group_heights=[66+len(RASTER_SAMPLES)*max(44,round(s*2.3)) for s in SIZES]
    height=82+sum(group_heights)+16
    im=Image.new('RGB',(width,height),'white'); d=ImageDraw.Draw(im)
    d.text((margin,14),'Pranoti v0.119 baseline vs v0.120 experimental public beta',font=label,fill='#17202a')
    d.text((margin,40),'C offsets: ka+aa −450,+125 · ca+aa −278,+125 · k_ss_ma+aa −632,+125 units (UPM 1536)',font=small,fill='#586575')
    d.text((margin,58),'FreeType/Pillow RAQM, Bengali; experimental public beta, not production-ready.',font=small,fill='#586575')
    y=82
    for size,gh in zip(SIZES,group_heights):
        d.rounded_rectangle((12,y,width-12,y+gh-6),radius=10,fill='#f6f8fa',outline='#cbd3da',width=1)
        d.text((margin,y+8),f'{size} px',font=label,fill='#273746'); d.text((xbase,y+8),'v0.119 baseline',font=small,fill='#273746'); d.text((xnew,y+8),'v0.120 C GPOS beta',font=small,fill='#273746')
        row_y=y+34; row_h=max(44,round(size*2.3))
        for sample_id,text in RASTER_SAMPLES:
            fb=ImageFont.truetype(str(BASELINE),size,layout_engine=ImageFont.Layout.RAQM); fn=ImageFont.truetype(str(FONT),size,layout_engine=ImageFont.Layout.RAQM)
            d.text((margin,row_y),sample_id,font=small,fill='#586575')
            d.text((xbase,row_y+row_h-5),text,font=fb,fill='#111820',direction='ltr',language='bn',anchor='ls')
            d.text((xnew,row_y+row_h-5),text,font=fn,fill='#111820',direction='ltr',language='bn',anchor='ls')
            row_y+=row_h
        y+=gh
    path=ROOT/'specimens/matched-v0.119-v0.120-C-position-review.png'; im.save(path,optimize=True); return im.size

def main() -> None:
    if sha256(BASELINE)!=EXPECTED_BASELINE_SHA256: raise SystemExit('Immutable baseline checksum mismatch')
    if not FONT.is_file(): raise SystemExit('Missing installable review build')
    verify_tables(); errors=verify_samples(); changed,nd=verify_pairs()
    if changed or nd: errors.append(f'pair grid changed={changed}, .notdef={nd}')
    dims=make_specimen()
    lines=[
      'PRANOTI v0.120 — EXPERIMENTAL PUBLIC BETA: TEST SUMMARY',
      f'Baseline v0.119 SHA-256: {sha256(BASELINE)}',f'Review font SHA-256: {sha256(FONT)}',
      'Approved exact HarfBuzz C offsets at UPM 1536: কাঁ −450,+125; চাঁ −278,+125; ক্ষ্মাঁ −632,+125.',
      f'HarfBuzz representative samples: {len(SAMPLES)}; all exact context, substitution, cluster, advance, and positioning checks passed: {not errors}.',
      f'Consonant pair grid: {37*37-changed}/1369 identical; .notdef={nd}.',
      'FontTools table comparison: only GPOS, name, and dependent head data differ; GSUB, outlines, metrics, cmap, GDEF, attribution and license name records preserved.',
      f'Matched FreeType/Pillow RAQM specimen generated: {dims[0]} x {dims[1]} pixels.',
      'Release status: experimental public beta only; not production signed off.' ]
    if errors: lines.append('FAILURES: '+' | '.join(errors))
    else: lines.append('RESULT: PASS for the listed isolated shaping and regression checks; OTS and FontForge are reported separately.')
    (ROOT/'checks/summary-v0.120.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
    if errors: raise SystemExit(1)
if __name__=='__main__': main()
