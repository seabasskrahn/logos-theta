#!/usr/bin/env python3
"""Build the Sonolumina word codebook (codebook/*.json).

Each LEMMA gets one fixed tone signature derived only from how the Bible itself
uses the word (no letter values, no gematria):
  register  <- concordance size (occurrences): common = low band, rare = high band
  root      <- first mention (canonical position of first occurrence, as a percentile
               among that language's lemmas) picks one of 4 steps within the band
  partials  <- roots of the 2 lemmas it most often shares a verse with (content words)
Signature entry: [root_idx, partial1_idx, partial2_idx, count, first_global_verse_idx]
indices point into the app's HSET (harmonic set on the 100 Hz root, 10 notes).

Sources (fetch into SRC first):
  Hebrew: Open Scriptures Hebrew Bible (OSHB, WLC + Strong's lemmas), CC-BY 4.0
          git clone https://github.com/openscriptures/morphhb
  Greek:  MorphGNT SBLGNT lemmas, CC-BY-SA 3.0 (SBLGNT text under the SBLGNT EULA;
          only lemma lookups and counts are shipped)
          git clone https://github.com/morphgnt/sblgnt
  English: the app's own KJV files (kjv/*.json), public domain.
Usage: python3 tools/build_codebook.py /path/to/src   (needs src/meta.json: [[book,[verse counts]],...])
"""
import sys, os, re, json, unicodedata, glob
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

def signatures(verses):
    """verses: list of (global_idx, [lemma,...]) -> {lemma: [root,p1,p2,count,first]}"""
    cnt, first, co = Counter(), {}, defaultdict(Counter)
    for g, ls in verses:
        for l in ls:
            cnt[l] += 1
            if l not in first or g < first[l]: first[l] = g
    stop = {l for l, _ in cnt.most_common(40)}  # function words: excluded as partners
    for g, ls in verses:
        u = [l for l in set(ls) if l not in stop]
        for a in u:
            for b in u:
                if a != b: co[a][b] += 1
    # first-mention percentile among this language's lemmas (earliest quarter -> step 0 ... latest -> 3)
    order = sorted(cnt, key=lambda l: (first[l], l)); pct = {l: i / len(order) for i, l in enumerate(order)}
    def root(l):
        c = cnt[l]; band = 0 if c >= 200 else 1 if c >= 20 else 2
        return band * 3 + min(3, int(pct[l] * 4))
    out = {}
    for l in cnt:
        r = root(l)
        ps = [root(b) for b, _ in sorted(co[l].items(), key=lambda x: (-x[1], x[0]))[:2]]
        ps = (ps + [r, r])[:2]
        out[l] = [r, ps[0], ps[1], cnt[l], first[l]]
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
save('grk.json', {'lex': signatures(gv), 'forms': {k: c.most_common(1)[0][0] for k, c in forms.items() if k}})

# English (KJV stems), whole Bible
ev = []
for b, cs in META:
    d = json.load(open(os.path.join(ROOT, 'kjv', b.replace(' ', '') + '.json'), encoding='utf-8'))
    for ci, ch in enumerate(d['c']):
        for vi, t in enumerate(ch):
            ev.append((gi(b, ci+1, vi+1), [s for s in map(eng_stem, t.split()) if s]))
save('eng.json', {'lex': signatures(ev)})
save('meta.json', {'total': TOTAL, 'credits': 'Hebrew lemmas: Open Scriptures Hebrew Bible (OSHB, WLC), CC-BY 4.0. Greek lemmas: MorphGNT SBLGNT, CC-BY-SA 3.0. English: KJV (public domain).'})
