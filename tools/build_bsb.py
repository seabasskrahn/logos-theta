#!/usr/bin/env python3
"""Berean Standard Bible (public domain since April 2023, bereanbible.com/bsb.txt) -> bsb/<Book>.json {"b":book,"c":[[verse,...],...]}
laid out on the app's KJV versification (meta.json); verses the BSB omits (textual notes) are left as ''."""
import sys, os, re, json
SRC = sys.argv[1] if len(sys.argv) > 1 else '/workspace/cbsrc'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = json.load(open(os.path.join(SRC, 'meta.json')))
ALIAS = {'Psalm': 'Psalms'}
data = {}
for l in open(os.path.join(SRC, 'bsb.txt'), encoding='utf-8'):
    m = re.match(r'^(.+?) (\d+):(\d+)\t(.*)$', l.rstrip('\n'))
    if m: data[(ALIAS.get(m[1], m[1]), int(m[2]), int(m[3]))] = m[4].strip()
miss = 0
for b, cs in META:
    out = [[data.get((b, c + 1, v + 1), '') for v in range(n)] for c, n in enumerate(cs)]
    miss += sum(1 for ch in out for t in ch if not t)
    json.dump({'b': b, 'c': out}, open(os.path.join(ROOT, 'bsb', b.replace(' ', '') + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('BSB verses', len(data), 'empty slots on KJV versification', miss)
