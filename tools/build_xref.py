#!/usr/bin/env python3
"""Rebuild xref/<Book>.json from OpenBible.info cross references (CC-BY).
Source: https://a.openbible.info/data/cross-references.zip  (cross_references.txt)
Output per book: {"c.v": [[bookIdx, c, v, votes, motif, themeMask], ...]}  top 5 by votes, votes > 0.
 bookIdx = 0-based canonical index (Genesis=0 .. Revelation=65), matching META in index.html.
 motif   = last 3 digits of the target verse's letter-value sum (Hebrew gematria / Greek isopsephy where the
           original text is bundled, else English a=1..z=26), zero-padded; index.html maps each digit to a tone.
 themeMask = bit i set when the target KJV verse matches THEMES[i] in index.html.
Range refs (A-B) use their first verse. Real cross references only; no keyword matching.
Usage: python3 tools/build_xref.py path/to/cross_references.txt"""
import json, re, sys, os, unicodedata
OSIS="Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev".split()
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html=open(os.path.join(ROOT,'index.html'),encoding='utf8').read()
META=re.findall(r'\["([^"]+)","([^"]+\.json)",\[',html.split('const META=')[1])[:66]
assert len(META)==66
HEB="אבגדהוזחטיכלמנסעפצקרשתךםןףץ";HV=[1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,200,300,400,20,40,50,80,90]
GRK="αβγδεϛζηθικλμνξοπϙρστυφχψω";GV=[1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800]
def val(ch):
    if ch in HEB: return HV[HEB.index(ch)]
    c=unicodedata.normalize('NFD',ch.lower())[:1]
    if c=='ς': c='σ'
    if c in GRK: return GV[GRK.index(c)]
    return ord(c)-96 if 'a'<=c<='z' else 0
THEMES=[r'forgiv|pardon|remission|remit',r'peace',r'spirit|ghost',r'light',r'love',r'creat|heaven and the earth|firmament',
 r'covenant|oath|sware',r'commandment|statute|law\b',r'judg|wrath|destroy|curse',r'bless',r'praise|worship|sing|altar']
books=[json.load(open(os.path.join(ROOT,'kjv',f),encoding='utf8')) for _,f in META]
def parse(r):
    b,c,v=r.split('-')[0].split('.');return OSIS.index(b),int(c),int(v)
out=[{} for _ in META]
for line in open(sys.argv[1] if len(sys.argv)>1 else '/workspace/data/cross_references.txt',encoding='utf8'):
    p=line.rstrip('\n').split('\t')
    if len(p)<3 or not p[2].lstrip('-').isdigit(): continue
    votes=int(p[2])
    if votes<=0: continue
    try: (fb,fc,fv),(tb,tc,tv)=parse(p[0]),parse(p[1])
    except (ValueError,IndexError): continue
    out[fb].setdefault(f'{fc}.{fv}',[]).append((votes,tb,tc,tv))
for i,(name,f) in enumerate(META):
    o={}
    for k,lst in out[i].items():
        rows=[]
        for votes,tb,tc,tv in sorted(lst,reverse=True)[:5]:
            bk=books[tb]
            try: eng=bk['c'][tc-1][tv-1]
            except IndexError: continue
            orig=(bk.get('h') or [[]]*999)[tc-1][tv-1] if bk.get('h') else eng
            s=sum(val(ch) for ch in orig)
            mask=sum(1<<j for j,rx in enumerate(THEMES) if re.search(rx,eng,re.I))
            rows.append([tb,tc,tv,votes,str(s%1000).zfill(3),mask])
        if rows: o[k]=rows
    json.dump(o,open(os.path.join(ROOT,'xref',f),'w',encoding='utf8'),separators=(',',':'),ensure_ascii=False)
print('ok')
