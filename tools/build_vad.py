#!/usr/bin/env python3
"""Per-verse emotion E(v) = (valence, arousal, dominance) for the KJV, for Sonolumina build 2026101221.
Lexicon: NRC VAD Lexicon (Mohammad 2018, National Research Council Canada), research/non-commercial use with credit;
the lexicon itself is NOT shipped, only per-verse aggregates. Download it into SRC/nrcvad first.
  raw(v)   = salience-weighted mean (w = 0.25+|V-.5|+|A-.5|; divine names excluded) of V,A,D of the verse's KJV words found in the lexicon (exact form, then simple archaic/stem fallbacks)
  pct      = percentile of raw across all 31,102 verses (0..1), per dimension
  arc(v)   = Gaussian (sigma = 2 verses) smoothing of pct within the chapter
  book(v)  = mean pct of the verse's book (slow canonical drift)
  E(v)     = 0.45*pct + 0.35*arc + 0.20*book, stored as 2-digit ints (00-99) per dimension
Output: vad/<Book>.json = ["VVAADD VVAADD ...per verse, one string per chapter", ...] (no spaces)
Usage: python3 tools/build_vad.py /workspace/cbsrc"""
import sys, os, json, re, math, glob
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
def look(w):
    w = re.sub(r'[^a-z]', '', w.lower())
    if not w: return None
    w = ARCH.get(w, w)
    if w in LEX: return LEX[w]
    for suf in ('eth', 'est', 'ed', 'es', 's', 'ing'):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            b = w[:-len(suf)]
            for c in (b, b + 'e', b[:-1] if len(b) > 3 and b[-1] == b[-2] else None):
                if c and c in LEX: return LEX[c]
    return None
# divine names occur everywhere with a fixed high valence; they are left out so they don't mask the verse's own feeling
NAMES = {'god', 'lord', 'jesus', 'christ', 'gods', 'lords'}
META = json.load(open(os.path.join(SRC, 'meta.json')))
books, raw = [], []
for b, cs in META:
    d = json.load(open(os.path.join(ROOT, 'kjv', b.replace(' ', '') + '.json'), encoding='utf-8'))
    chs = []
    for ch in d['c']:
        vs = []
        for t in ch:
            m = [x for w in t.split() if re.sub(r'[^a-z]', '', w.lower()) not in NAMES for x in [look(w)] if x]
            # salience weighting: emotionally strong words (far from neutral valence or arousal) count more
            ws = [0.25 + abs(x[0] - 0.5) + abs(x[1] - 0.5) for x in m]
            vs.append(tuple(sum(w * x[i] for w, x in zip(ws, m)) / sum(ws) for i in range(3)) if m else (0.5, 0.5, 0.5))
            raw.append(vs[-1])
        chs.append(vs)
    books.append((b, chs))
pct = []
for i in range(3):
    order = sorted(range(len(raw)), key=lambda k: raw[k][i]); r = [0.0] * len(raw)
    for rank, k in enumerate(order): r[k] = rank / (len(raw) - 1)
    pct.append(r)
k = 0; total = 0
for b, chs in books:
    idx = []; 
    for ch in chs:
        idx.append(list(range(k, k + len(ch)))); k += len(ch)
    flat = [j for c in idx for j in c]; bm = [sum(pct[i][j] for j in flat) / len(flat) for i in range(3)]
    out = []
    for c in idx:
        s = ''
        for a, j in enumerate(c):
            e = []
            for i in range(3):
                ws = [(math.exp(-((a - q) ** 2) / 8), pct[i][c[q]]) for q in range(len(c)) if abs(a - q) <= 6]
                arc = sum(w * x for w, x in ws) / sum(w for w, _ in ws)
                e.append(min(99, int(round(99 * (0.45 * pct[i][j] + 0.35 * arc + 0.20 * bm[i])))))
            s += '%02d%02d%02d' % tuple(e)
        out.append(s)
    p = os.path.join(ROOT, 'vad', b.replace(' ', '') + '.json')
    json.dump(out, open(p, 'w'), separators=(',', ':')); total += os.path.getsize(p)
print('verses', len(raw), 'vad bytes', total)
