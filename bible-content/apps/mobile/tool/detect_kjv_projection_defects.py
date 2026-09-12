# -*- coding: utf-8 -*-
"""FASE 4: detectores sobre el 100 % del Antiguo Testamento en KJV Reading 2026 v11."""
import json, os, re, sys, io, glob
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
os.chdir(Path(__file__).resolve().parents[4])

BC = os.path.join('bible-content')
KBD = os.path.join(BC, 'apps/mobile/assets/bible_direction/kjv/books')
KCORP = os.path.join(BC, 'apps/mobile/assets/bibles/kjv/books')
OT = ['GEN','EXO','LEV','NUM','DEU','JOS','JDG','RUT','1SA','2SA','1KI','2KI','1CH','2CH','EZR',
      'NEH','EST','JOB','PSA','PRO','ECC','SNG','ISA','JER','LAM','EZK','DAN','HOS','JOL','AMO',
      'OBA','JON','MIC','NAM','HAB','ZEP','HAG','ZEC','MAL']
MARK = re.compile(r'\\\+(?:w|add|nd)\*?\s*', re.I)
def nk(v):
    s = MARK.sub('', v)
    s = re.sub(r'\s+([,.;:!?])', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()
corp = {}
for c in OT:
    bk = json.load(open(os.path.join(KCORP, c + '.json'), encoding='utf-8'))
    for ch in bk['chapters']:
        for v in ch['verses']:
            corp[(c, ch['chapter'], v['verse'])] = nk(v['text'])
proj, edits, byverse = {}, [], defaultdict(list)
ok = bad = ov = 0
for p in glob.glob(os.path.join(KBD, '*_reading_2026.kjv.v1.json')):
    d = json.load(open(p, encoding='utf-8'))
    if d.get('book') not in OT: continue
    for v in d['verses']:
        k = (d['book'], v['chapter'], v['verse'])
        s = corp[k]; t = s
        es = sorted(v['edits'], key=lambda x: x['startOffset'])
        for i in range(len(es) - 1):
            if es[i]['endOffset'] > es[i + 1]['startOffset']: ov += 1
        for e in es:
            if s[e['startOffset']:e['endOffset']] == e['expected']: ok += 1
            else: bad += 1
            edits.append((k, e)); byverse[k].append(e)
        for e in sorted(v['edits'], key=lambda x: -x['startOffset']):
            t = t[:e['startOffset']] + e['replacement'] + t[e['endOffset']:]
        proj[k] = t
print('KJV AT: ediciones=%d  versiculos tocados=%d  offsets ok=%d bad=%d  superposiciones=%d'
      % (len(edits), len(proj), ok, bad, ov))

R = {}
PRON = re.compile(r'\b(?:thee|thou|thy|thine|ye)\b', re.I)
YOU = re.compile(r'\b(?:you|your|yours|yourself|yourselves)\b', re.I)
R['K1 you/your junto a thee/thou/ye'] = [
    (k, e) for k, e in edits
    if YOU.search(e['replacement']) and not YOU.search(e['expected']) and PRON.search(proj[k])]
R['K2 reemplazo identico repetido en el mismo versiculo'] = []
for k, es in byverse.items():
    c = Counter(e['replacement'] for e in es)
    for rep, n in c.items():
        if n >= 2 and len(rep.split()) >= 3:
            R['K2 reemplazo identico repetido en el mismo versiculo'].append((k, rep))
DUP = re.compile(r'\b(the|of|and|to|in|a|his|its|that|for|with|is|shall)\s+\1\b', re.I)
SP = re.compile(r'  +|,\s*,|\(\s*\)')
R['K3 palabra duplicada o espaciado roto'] = [
    (k, (DUP.search(proj[k]) or SP.search(proj[k])).group(0))
    for k in proj if (DUP.search(proj[k]) or SP.search(proj[k]))
    and not (DUP.search(corp[k]) or SP.search(corp[k]))]
def r4(t):
    w = t.split(); seen = set()
    for i in range(len(w) - 3):
        g = ' '.join(w[i:i + 4]).lower()
        if g in seen: return g
        seen.add(g)
    return None
R['K4 repeticion de 4+ palabras introducida'] = [
    (k, r4(proj[k])) for k in proj if r4(proj[k]) and not r4(corp[k])]
ART = re.compile(r'\ban\s+(?![aeiouAEIOU])[bcdfgjklmnpqrstvwxyz]|\ba\s+[aeiouAEIOU]\w', re.I)
R['K5 articulo a/an incorrecto'] = [
    (k, ART.search(proj[k]).group(0)) for k in proj
    if ART.search(proj[k]) and not ART.search(corp[k])]
VERB = re.compile(r'\bthou\s+(?:will|have|do|are|was|shall\s+not\s+\w+s)\b|\bye\s+(?:is|was|hath)\b', re.I)
R['K6 concordancia rota con thou/ye'] = [
    (k, VERB.search(proj[k]).group(0)) for k in proj
    if VERB.search(proj[k]) and not VERB.search(corp[k])]
DUPTERM = [('brass','bronze'),('candlestick','lampstand'),('vail','veil'),('shittim','acacia'),
           ('taches','clasps'),('laver','basin'),('knops','buds'),('bosom','cloak')]
R['K7 dos terminos para el mismo referente'] = []
for k in proj:
    for a, b in DUPTERM:
        ra = re.compile(r'\b' + a + r'\w*\b', re.I); rb = re.compile(r'\b' + b + r'\w*\b', re.I)
        if ra.search(proj[k]) and rb.search(proj[k]) and not rb.search(corp[k]):
            R['K7 dos terminos para el mismo referente'].append((k, '%s/%s' % (a, b))); break

for n in R:
    rs = R[n]
    bb = Counter(x[0][0] for x in rs)
    print('\n--- %s : %d' % (n, len(rs)))
    if bb: print('     por libro:', dict(sorted(bb.items(), key=lambda x: -x[1])[:12]))
    for x in rs[:10]:
        k = x[0]
        det = x[1] if not isinstance(x[1], dict) else x[1].get('replacement')
        print('     %-4s %3d:%-3d  %s' % (k[0], k[1], k[2], str(det)[:95]))
    if len(rs) > 10: print('     ... +%d' % (len(rs) - 10))
json.dump({n: [[list(x[0]), (x[1] if isinstance(x[1], str) else x[1].get('replacement', ''))] for x in R[n]]
           for n in R}, open(os.path.join('tools_audit', 'kjv_detect.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
