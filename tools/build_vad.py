#!/usr/bin/env python3
"""Per-verse emotion E(v) = (valence, arousal, dominance), Sonolumina build 2026101222 - multi-source blend.
Lexicon: NRC VAD Lexicon (Mohammad 2018, National Research Council Canada), research/non-commercial use with credit;
the lexicon itself is NOT shipped, only per-verse aggregates.
Sources (per verse, each scored separately, then turned into percentiles across all 31,102 verses):
  BSB   0.35  Berean Standard Bible (public domain)              -> bsb/<Book>.json (tools/build_bsb.py)
  WEB   0.25  World English Bible (public domain)                -> SRC/web/engwebp_vpl.txt
  GLOSS 0.30  original languages: OSHB Strong's numbers / MorphGNT lemmas -> English glosses (strongs_def) from the
              public-domain Strong's dictionaries (Open Scriptures JSON). APPROXIMATE: a gloss is a dictionary
              definition, not the word's sense in that verse; proper names and divine names are skipped.
  KJV   0.10  King James Version                                  -> kjv/<Book>.json
  (weights renormalise when a source has no scoreable words for a verse)
Scoring per English source: salience-weighted mean (w = 0.25+|V-.5|+|A-.5|) of lexicon words, divine names excluded.
Negation: a word with not/no/never/nor/neither/none/without/cannot in the 3 words before it has its valence
  flipped and halved around neutral (v -> .5-(v-.5)*.5) and its arousal pulled halfway to neutral ("no more death" reads as relief).
Smoothing: the BSB text available has no section headings, so passage smoothing stays at chapter level:
  E = 0.45*blend + 0.35*arc (Gaussian sigma 2 verses within chapter) + 0.20*book mean.
Output: vad/<Book>.json = one string per chapter, 6 digits VVAADD per verse.
Usage: python3 tools/build_vad.py /workspace/cbsrc   (run tools/build_codebook.py first: it writes SRC/lemmas_*.json)"""
import sys, os, json, re, math, glob, unicodedata
SRC = sys.argv[1] if len(sys.argv) > 1 else '/workspace/cbsrc'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEX = {}
for line in open(glob.glob(os.path.join(SRC, 'nrcvad/*/NRC-VAD-Lexicon.txt'))[0], encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) == 4:
        try: LEX[p[0]] = tuple(map(float, p[1:]))
        except ValueError: pass
ARCH = {'saith': 'say', 'hath': 'have', 'doth': 'do', 'spake': 'speak', 'shew': 'show', 'shewed': 'show', 'smote': 'strike', 'slew': 'kill',
        'wrought': 'work', 'begat': 'beget', 'sware': 'swear', 'brake': 'break', 'wept': 'weep', 'gat': 'get', 'clave': 'cleave'}
def norm(w): return re.sub(r'[^a-z]', '', w.lower().replace('’', "'").split("'")[0])
def look(w):
    w = ARCH.get(w, w)
    if not w: return None
    if w in LEX: return LEX[w]
    for suf in ('eth', 'est', 'ed', 'es', 's', 'ing', 'ly'):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            b = w[:-len(suf)]
            for c in (b, b + 'e', b[:-1] if len(b) > 3 and b[-1] == b[-2] else None):
                if c and c in LEX: return LEX[c]
    return None
NAMES = {'god', 'lord', 'jesus', 'christ', 'gods', 'lords', 'yahweh', 'jehovah'}
NEG = {'not', 'no', 'never', 'nor', 'neither', 'none', 'without', 'cannot', 'nothing', 'nt'}
def sal(x): return 0.25 + abs(x[0] - 0.5) + abs(x[1] - 0.5)
def score_text(t):
    toks = [norm(w) for w in re.split(r"\s+|—|-", t.replace("n't", " nt"))]; toks = [w for w in toks if w]
    m = []
    for i, w in enumerate(toks):
        if w in NAMES or w in NEG: continue
        x = look(w)
        if not x: continue
        if any(p in NEG for p in toks[max(0, i - 3):i]): x = (0.5 - (x[0] - 0.5) * 0.5, 0.5 + (x[1] - 0.5) * 0.5, x[2])
        m.append(x)
    if not m: return None
    ws = [sal(x) for x in m]
    return tuple(sum(w * x[i] for w, x in zip(ws, m)) / sum(ws) for i in range(3))
META = json.load(open(os.path.join(SRC, 'meta.json')))
OFF = {}; n = 0
for b, cs in META:
    for c, k in enumerate(cs):
        OFF[(b, c + 1)] = n; n += k
TOTAL = n
def gi(b, c, v): return OFF[(b, c)] + v - 1
def from_json(d):
    out = [None] * TOTAL
    for b, cs in META:
        j = json.load(open(os.path.join(ROOT, d, b.replace(' ', '') + '.json'), encoding='utf-8'))
        for ci, ch in enumerate(j['c']):
            for vi, t in enumerate(ch[:cs[ci]]): out[gi(b, ci + 1, vi + 1)] = score_text(t) if t else None
    return out
kjv, bsb = from_json('kjv'), from_json('bsb')
# WEB: book codes in file order map onto canonical order
web = [None] * TOTAL; codes = []; wt = {}
for l in open(os.path.join(SRC, 'web/engwebp_vpl.txt'), encoding='utf-8-sig'):
    m = re.match(r'^(\w+) (\d+):(\d+) (.*)', l.strip())
    if not m: continue
    if m[1] not in codes: codes.append(m[1])
    wt[(m[1], int(m[2]), int(m[3]))] = m[4]
assert len(codes) == 66, codes
for (cd, c, v), t in wt.items():
    b, cs = META[codes.index(cd)]
    if c <= len(cs) and v <= cs[c - 1]: web[gi(b, c, v)] = score_text(t)
# glosses
def dic(f):
    s = open(os.path.join(SRC, f), encoding='utf-8').read(); return json.loads(s[s.index('{'):s.rindex('}') + 1])
def strip(s): return ''.join(ch for ch in unicodedata.normalize('NFD', s) if not unicodedata.combining(ch)).lower()
HD, GD = dic('strongs-hebrew-dictionary.js'), dic('strongs-greek-dictionary.js')
DIV = {'H430', 'H410', 'H433', 'H3068', 'H3069', 'H136', 'H3050', 'G2316', 'G2962', 'G2424', 'G5547'}
def gloss_vec(e):
    d = (e.get('strongs_def') or '') + ' ' + (e.get('kjv_def') or '')
    if re.search(r'\b(a name|an Israelite|a place|an Edomite|a Levite|a city|a son of|patronymic|Gentilic|a town|a mountain|a region)\b', d, re.I): return None
    sd = (e.get('strongs_def') or e.get('kjv_def') or '').split(';')[0]
    return score_text(re.sub(r'\([^)]*\)', ' ', sd)[:160])
GV = {}
for k, e in HD.items(): GV[k] = None if k in DIV else gloss_vec(e)
GL = {}
for k, e in GD.items():
    if 'lemma' in e: GL[strip(e['lemma'])] = None if k in DIV else gloss_vec(e)
gloss = [None] * TOTAL
for f, key in (('lemmas_heb.json', lambda x: re.sub(r'[a-z]$', '', x)), ('lemmas_grk.json', lambda x: strip(x[1:]))):
    for i, lem in json.load(open(os.path.join(SRC, f))):
        m = [x for x in (GV.get(key(l)) if l.startswith('H') else GL.get(key(l)) for l in lem) if x]
        if m:
            ws = [sal(x) for x in m]; gloss[i] = tuple(sum(w * x[d] for w, x in zip(ws, m)) / sum(ws) for d in range(3))
SRCS = [(bsb, .35), (web, .25), (gloss, .30), (kjv, .10)]
def pctl(raw):
    idx = [i for i, x in enumerate(raw) if x]; out = [None] * TOTAL
    for d in range(3):
        o = sorted(idx, key=lambda k: raw[k][d])
        for r, k in enumerate(o): out[k] = (out[k] or []) + [r / (len(o) - 1)]
    return out
P = [(pctl(r), w) for r, w in SRCS]
blend = []
for i in range(TOTAL):
    have = [(p[i], w) for p, w in P if p[i]]
    blend.append([sum(x[d] * w for x, w in have) / sum(w for _, w in have) for d in range(3)] if have else [0.5] * 3)
cov = {nm: sum(1 for x in r if x) for nm, (r, _) in zip(('bsb', 'web', 'gloss', 'kjv'), SRCS)}
total = 0; k = 0; DUMP = {}
for b, cs in META:
    idx = [list(range(OFF[(b, c + 1)], OFF[(b, c + 1)] + n)) for c, n in enumerate(cs)]
    flat = [j for c in idx for j in c]; bm = [sum(blend[j][d] for j in flat) / len(flat) for d in range(3)]
    out = []
    for c in idx:
        s = ''
        for a, j in enumerate(c):
            e = []
            for d in range(3):
                ws = [(math.exp(-((a - q) ** 2) / 8), blend[c[q]][d]) for q in range(len(c)) if abs(a - q) <= 6]
                arc = sum(w * x for w, x in ws) / sum(w for w, _ in ws)
                e.append(min(99, int(round(99 * (0.45 * blend[j][d] + 0.35 * arc + 0.20 * bm[d])))))
            s += '%02d%02d%02d' % tuple(e)
            DUMP[j] = (e, [None if p[j] is None else round(p[j][0] * 99) for p, _ in P])
        out.append(s)
    p = os.path.join(ROOT, 'vad', b.replace(' ', '') + '.json')
    json.dump(out, open(p, 'w'), separators=(',', ':')); total += os.path.getsize(p)
print('verses', TOTAL, 'coverage', cov, 'vad bytes', total)
print('%-18s %-4s %-4s %-4s | valence pct: BSB WEB GLOSS KJV' % ('verse', 'V', 'A', 'D'))
for b, c, v in [('Genesis', 1, 1), ('Psalms', 22, 1), ('Psalms', 23, 1), ('Lamentations', 1, 1), ('John', 11, 35), ('Revelation', 21, 4), ('Psalms', 150, 1)]:
    e, s = DUMP[gi(b, c, v)]; print('%-18s %-4d %-4d %-4d | %s' % ('%s %d:%d' % (b, c, v), *e, s))
