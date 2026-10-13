#!/usr/bin/env python3
"""Build the Sonolumina word codebook (codebook/*.json).

Algorithm "The Eye" (Matthew 6:22). Each LEMMA gets one fixed tone from how the Bible itself uses the word
(no letter values, no gematria, no numerology); see /workspace/logos-theta/SONOLUMINA_ALGORITHM.md.
Signature entry: [step, octave, c1, c2, count, first_global_verse_idx]
  step: index into the 12-step just scale, golden-ratio spread of first-appearance rank
  octave: 0/1/2 from occurrence count (>=200 / 20-199 / <20); app plays F0 * JUST[step] * 2**octave
  c1, c2: index into CONS (1, 5/4, 4/3, 3/2, 2): top-2 verse companions snapped to a consonance of the word
places.json: OpenBible.info Bible Geocoding Data (CC-BY 4.0), KJV place name -> [name, type, modern id, verses]
Sources (fetch into SRC first):
  Hebrew: Open Scriptures Hebrew Bible (OSHB, WLC + Strong's lemmas), CC-BY 4.0
          git clone https://github.com/openscriptures/morphhb
  Greek:  MorphGNT SBLGNT lemmas, CC-BY-SA 3.0 (SBLGNT text under the SBLGNT EULA;
          only lemma lookups and counts are shipped)
          git clone https://github.com/morphgnt/sblgnt
  English: the app's own KJV files (kjv/*.json), public domain.
Usage: python3 tools/build_codebook.py /path/to/src   (needs src/meta.json: [[book,[verse counts]],...])
"""
import sys, os, re, json, unicodedata, glob, math
from collections import Counter, defaultdict
SRC = sys.argv[1] if len(sys.argv) > 1 else '/workspace/cbsrc'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = json.load(open(os.path.join(SRC, 'meta.json')))
names = [b for b, _ in META]
OFF = {}; n = 0
for b, cs in META:
    OFF[b] = []
    for c in cs: OFF[b].append(n); n += c
TOTAL = n
def gi(b, c, v):  # clamp chapter/verse to KJV versification (stats only)
    c = min(c, len(OFF[b])); cs = META[names.index(b)][1] if b in names else None
    return OFF[b][c-1] + min(v, cs[c-1]) - 1 if cs else OFF[b][c-1] + v - 1
OSIS = dict(Gen='Genesis',Exod='Exodus',Lev='Leviticus',Num='Numbers',Deut='Deuteronomy',Josh='Joshua',Judg='Judges',Ruth='Ruth',
 **{'1Sam':'1Samuel','2Sam':'2Samuel','1Kgs':'1Kings','2Kgs':'2Kings','1Chr':'1Chronicles','2Chr':'2Chronicles'},Ezra='Ezra',Neh='Nehemiah',
 Esth='Esther',Job='Job',Ps='Psalms',Prov='Proverbs',Eccl='Ecclesiastes',Song='SongofSolomon',Isa='Isaiah',Jer='Jeremiah',Lam='Lamentations',
 Ezek='Ezekiel',Dan='Daniel',Hos='Hosea',Joel='Joel',Amos='Amos',Obad='Obadiah',Jonah='Jonah',Mic='Micah',Nah='Nahum',Hab='Habakkuk',
 Zeph='Zephaniah',Hag='Haggai',Zech='Zechariah',Mal='Malachi')
def canon(name):
    k = re.sub(r'\W', '', name).lower()
    for b in names:
        if re.sub(r'\W', '', b).lower() == k: return b
    raise KeyError(name)

def heb_cons(s):  # strip points, cantillation, morpheme slashes; keep the 27 letters
    return ''.join(ch for ch in s if '\u05d0' <= ch <= '\u05ea')
def grk_norm(s):
    s = ''.join(ch for ch in unicodedata.normalize('NFD', s) if not unicodedata.combining(ch)).lower()
    return re.sub(r'[^α-ω]', '', s.replace('ς', 'σ'))
def eng_stem(w):  # same rules as engStem() in index.html
    w = re.sub(r'[^a-z]', '', w.lower())
    for suf in ('eth', 'est', 'ing', 'ed', 'es', 's'):
        if len(w) - len(suf) >= 3 and w.endswith(suf): return w[:-len(suf)]
    return w

JUST = [1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2, 8/5, 5/3, 9/5, 15/8]   # 12-step just scale (iris)
CONS = [1, 5/4, 4/3, 3/2, 2]                                             # unison, major third, fourth, fifth, octave
PHI = (1 + 5 ** 0.5) / 2
def snap(ratio):
    """index into CONS of the consonant interval nearest to ratio (folded into one octave)."""
    while ratio >= 2: ratio /= 2
    while ratio < 1: ratio *= 2
    return min(range(len(CONS)), key=lambda i: (abs(math.log(ratio / CONS[i])), i))

def signatures(verses):
    """The Eye. verses: canonical-order list of (global_idx, [lemma,...]) ->
    {lemma: [step, octave, c1, c2, count, first_verse]}
      step   = floor(12 * frac(rank * PHI)), rank = order of first appearance (0-based, token order)
      octave = 0 if count>=200, 1 if 20..199, 2 if <20         freq = F0 * JUST[step] * 2**octave
      c1,c2  = CONS index of the 2 most frequent verse companions' tones, snapped to the word's tone"""
    cnt, first, rank, co = Counter(), {}, {}, defaultdict(Counter)
    for g, ls in sorted(verses, key=lambda x: x[0]):   # stable: keeps token order inside a verse
        for l in ls:
            cnt[l] += 1
            if l not in first: first[l] = g
            if l not in rank: rank[l] = len(rank)
    stop = {l for l, _ in cnt.most_common(40)}  # function words: excluded as companions
    for g, ls in verses:
        al = set(ls); u = [l for l in al if l not in stop]
        for a in al:
            for b in u:
                if a != b: co[a][b] += 1
    step = {l: int(12 * ((rank[l] * PHI) % 1)) for l in cnt}
    octv = {l: 0 if cnt[l] >= 200 else 1 if cnt[l] >= 20 else 2 for l in cnt}
    rel = {l: JUST[step[l]] * 2 ** octv[l] for l in cnt}   # tone relative to F0
    out = {}
    for l in cnt:
        comp = [b for b, _ in sorted(co[l].items(), key=lambda x: (-x[1], x[0]))[:2]]
        cs = [snap(rel[b] / rel[l]) for b in comp] + [0, 0]
        out[l] = [step[l], octv[l], cs[0], cs[1], cnt[l], first[l]]
    return out

def save(name, obj):
    p = os.path.join(ROOT, 'codebook', name)
    json.dump(obj, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(name, os.path.getsize(p) // 1024, 'KB')

# Hebrew (OSHB)
hv, forms = [], defaultdict(Counter)
for f in glob.glob(os.path.join(SRC, 'morphhb/wlc/*.xml')):
    osis = os.path.basename(f)[:-4]
    if osis not in OSIS: continue
    b = canon(OSIS[osis]); x = open(f, encoding='utf-8').read()
    for m in re.finditer(r'<verse osisID="[^.]+\.(\d+)\.(\d+)"[^>]*>(.*?)</verse>', x, re.S):
        c, v = int(m[1]), int(m[2])
        if c > len(OFF[b]): continue
        v = min(v, META[names.index(b)][1][c-1])  # Hebrew vs KJV versification: clamp (stats only)
        ls = []
        for w in re.finditer(r'<w lemma="([^"]*)"[^>]*>(.*?)</w>', m[3]):
            nums = [re.match(r'\d+', s)[0] for s in w[1].split('/') if re.match(r'\d+', s)]
            if not nums: continue
            l = 'H' + nums[-1]; ls.append(l)
            forms[heb_cons(w[2])][l] += 1
        hv.append((gi(b, c, v), ls))
json.dump(hv, open(os.path.join(SRC, 'lemmas_heb.json'), 'w'))  # per-verse lemmas, reused by build_vad.py
save('heb.json', {'lex': signatures(hv), 'forms': {k: c.most_common(1)[0][0] for k, c in forms.items() if k}})

# Greek (MorphGNT SBLGNT)
gv, forms, cur, ls = [], defaultdict(Counter), None, []
for f in sorted(glob.glob(os.path.join(SRC, 'sblgnt/*-morphgnt.txt'))):
    for line in open(f, encoding='utf-8'):
        p = line.split()
        if len(p) < 7: continue
        bk = int(p[0][:2]) - 1 + 39; c, v = int(p[0][2:4]), int(p[0][4:6])
        key = (bk, c, v)
        if key != cur:
            if cur: gv.append((gi(names[cur[0]], cur[1], cur[2]), ls))
            cur, ls = key, []
        l = 'G' + p[6]; ls.append(l); forms[grk_norm(p[4])][l] += 1
gv.append((gi(names[cur[0]], cur[1], cur[2]), ls))
json.dump(gv, open(os.path.join(SRC, 'lemmas_grk.json'), 'w'))
save('grk.json', {'lex': signatures(gv), 'forms': {k: c.most_common(1)[0][0] for k, c in forms.items() if k}})

# English (KJV stems), whole Bible
ev = []
for b, cs in META:
    d = json.load(open(os.path.join(ROOT, 'kjv', b.replace(' ', '') + '.json'), encoding='utf-8'))
    for ci, ch in enumerate(d['c']):
        for vi, t in enumerate(ch):
            ev.append((gi(b, ci+1, vi+1), [s for s in map(eng_stem, t.split()) if s]))
# BSB (public domain): stems the KJV lacks get their own entries; KJV entries stay exactly as before (R(w) unchanged).
# Ranks for new stems continue after the KJV (BSB verses indexed after the whole KJV); first = the BSB verse index.
bv = []
for b, cs in META:
    p = os.path.join(ROOT, 'bsb', b.replace(' ', '') + '.json')
    if not os.path.exists(p): continue
    d = json.load(open(p, encoding='utf-8'))
    for ci, ch in enumerate(d['c']):
        for vi, t in enumerate(ch):
            bv.append((TOTAL + gi(b, ci+1, vi+1), [s for s in map(eng_stem, t.split()) if s]))
kj = signatures(ev); both = signatures(ev + bv)
for l, sig in both.items():
    if l not in kj: kj[l] = sig[:5] + [sig[5] - TOTAL if sig[5] >= TOTAL else sig[5]]
save('eng.json', {'lex': kj})
save('meta.json', {'total': TOTAL, 'credits': 'Hebrew lemmas: Open Scriptures Hebrew Bible (OSHB, WLC), CC-BY 4.0. Greek lemmas: MorphGNT SBLGNT, CC-BY-SA 3.0. English: KJV (public domain).'})

# Places (OpenBible.info Bible Geocoding Data, ancient.jsonl, CC-BY 4.0): only places the KJV names, with their KJV verses
pl = {}
OS2 = {v: k for k, v in OSIS.items()}
GNT = ['Matt','Mark','Luke','John','Acts','Rom','1Cor','2Cor','Gal','Eph','Phil','Col','1Thess','2Thess','1Tim','2Tim','Titus','Phlm','Heb','Jas','1Pet','2Pet','1John','2John','3John','Jude','Rev']
OSB = {**{k: canon(v) for k, v in OSIS.items()}, **{o: names[39 + i] for i, o in enumerate(GNT)}}
pf = os.path.join(SRC, 'ancient.jsonl')
if os.path.exists(pf):
    for line in open(pf, encoding='utf-8'):
        d = json.loads(line); vs = []
        for v in d.get('verses', []):
            if 'kjv' not in v.get('translations', []): continue
            b, c, n = v['osis'].split('.')[:3]
            if b in OSB: vs.append(gi(OSB[b], int(c), int(n)))
        if not vs: continue
        ids = d.get('identifications') or [{}]
        modern = re.sub(r'<[^>]+>', '', (ids[0].get('description') or ''))[:60]
        typ = (d.get('types') or ['place'])[0]
        nm = d['friendly_id']; key = re.sub(r'[^a-z]', '', nm.lower().split(' ')[0])
        if key: pl.setdefault(key, []).append([nm, typ, modern, sorted(set(vs))])
    save('places.json', pl)
