# -*- coding: utf-8 -*-
"""FASE 3: barrido de detectores sobre el 100 % del Antiguo Testamento en RV1909 v23.

R9 es el detector que la Fase 4 obligo a anadir: una familia de termino convertida a
medias deja dos nombres para el mismo objeto. Marca candidatos, no veredictos.
"""
import json, os, re, sys, io, glob
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
os.chdir(Path(__file__).resolve().parents[4])

BD = 'bible-content/apps/mobile/assets/bible_direction'
CORP = 'bible-content/apps/mobile/assets/bibles/rv1909/books'
OT = ('GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG '
      'ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL').split()
corp = {}
for c in OT:
    bk = json.load(open(os.path.join(CORP, c + '.json'), encoding='utf-8'))
    for ch in bk['chapters']:
        for v in ch['verses']:
            corp[(c, ch['chapter'], v['verse'])] = v['text']
proj, edits, byverse = {}, [], defaultdict(list)
ok = bad = ov = 0
for p in glob.glob(os.path.join(BD, '*_reading_2026.rv1909.v1.json')):
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
        for e in sorted(es, key=lambda x: -x['startOffset']):
            t = t[:e['startOffset']] + e['replacement'] + t[e['endOffset']:]
        proj[k] = t
for k in corp:
    proj.setdefault(k, corp[k])
print('RV AT: ediciones=%d  versiculos tocados=%d  offsets ok=%d bad=%d  superposiciones=%d'
      % (len(edits), len(byverse), ok, bad, ov))

R = {}
R['R1 e-acentuada ante consonante'] = [
    (k, m.group(0)) for k in proj
    for m in [re.search(r'\bé\s+[^aeiouáéíóúAEIOU\W]', proj[k])] if m and not re.search(r'\bé\s+[^aeiouáéíóúAEIOU\W]', corp[k])]
PARES = [('a', 'á'), ('fue', 'fué'), ('dio', 'dió'), ('vio', 'vió'), ('fui', 'fuí')]
R['R2 ortografia categorica mezclada'] = []
for base, acc in PARES:
    rb = re.compile(r'(?<![\wáéíóúñ])' + base + r'(?![\wáéíóúñ])')
    ra = re.compile(r'(?<![\wáéíóúñ])' + acc + r'(?![\wáéíóúñ])')
    for k in proj:
        if rb.search(proj[k]) and ra.search(proj[k]):
            R['R2 ortografia categorica mezclada'].append((k, '%s/%s' % (base, acc)))
VOS = re.compile(r'\b\w+(?:áis|éis|ís|asteis|isteis|abais|íais)\b')
UST = re.compile(r'\b(?:ustedes|les\s+dijo|su\s+de\s+ustedes)\b', re.I)
R['R3 vosotros y ustedes en el mismo versiculo'] = [
    (k, 'mezcla') for k in proj if VOS.search(proj[k]) and UST.search(proj[k])]
R['R4 reemplazo identico repetido en el versiculo'] = []
for k, es in byverse.items():
    c = Counter(e['replacement'] for e in es)
    for rep, n in c.items():
        if n >= 2 and len(rep.split()) >= 3:
            R['R4 reemplazo identico repetido en el versiculo'].append((k, rep))
def r4(t):
    w = t.split(); seen = set()
    for i in range(len(w) - 3):
        g = ' '.join(w[i:i + 4]).lower()
        if g in seen: return g
        seen.add(g)
    return None
R['R5 repeticion de 4+ palabras introducida'] = [
    (k, r4(proj[k])) for k in proj if r4(proj[k]) and not r4(corp[k])]
DUP = re.compile(r'(?<![\wáéíóúñ])(el|la|los|las|de|del|y|a|en|que|un|una|su|sus)\s+\1(?![\wáéíóúñ])', re.I)
SP = re.compile(r'  +|,\s*,|\(\s*\)|\s+[.,;:]')
R['R6 palabra duplicada o espaciado roto'] = [
    (k, (DUP.search(proj[k]) or SP.search(proj[k])).group(0)) for k in proj
    if (DUP.search(proj[k]) or SP.search(proj[k])) and not (DUP.search(corp[k]) or SP.search(corp[k]))]
ART = re.compile(r'\b(el|los)\s+\w+(?:a|as)\b(?!\s*(?:de|que))|\b(la|las)\s+\w+os\b', re.I)
R['R7 posible desacuerdo articulo-sustantivo'] = [
    (k, ART.search(proj[k]).group(0)) for k in proj
    if ART.search(proj[k]) and not ART.search(corp[k])]
div = defaultdict(set)
for k, e in edits: div[e['expected'].lower()].add(e['replacement'].lower())
R['R8 mismo expected con reemplazos divergentes'] = [
    ((x, 0, 0), ' | '.join(sorted(div[x])[:4])) for x in sorted(div) if len(div[x]) > 1]
# --- R9 familias de termino a medias
fam = defaultdict(lambda: [0, 0])
for k, e in edits:
    for w in re.findall(r'[a-záéíóúñü]{4,}', e['expected'].lower()):
        fam[w][0] += 1
R['R9 familia de termino convertida a medias'] = []
for w, (tocadas, _) in sorted(fam.items()):
    if tocadas < 4: continue
    rx = re.compile(r'(?<![\wáéíóúñ])' + w + r'(?![\wáéíóúñ])', re.I)
    quedan = [k for k in proj if rx.search(proj[k])]
    if quedan and tocadas >= 4 * len(quedan) and len(quedan) <= 12:
        R['R9 familia de termino convertida a medias'].append(
            ((w, tocadas, len(quedan)), ', '.join('%s %d:%d' % q for q in sorted(quedan)[:6])))

for n in sorted(R):
    rs = R[n]
    print('\n--- %s : %d' % (n, len(rs)))
    if rs and isinstance(rs[0][0], tuple) and isinstance(rs[0][0][0], str) and n.startswith('R9'):
        for x in rs[:25]:
            print('     %-16s convertida %3d veces, quedan %2d: %s' % (x[0][0], x[0][1], x[0][2], x[1][:88]))
    elif rs and n.startswith('R8'):
        for x in rs[:20]: print('     %-28s -> %s' % (x[0][0][:28], x[1][:86]))
    else:
        bb = Counter(x[0][0] for x in rs)
        if bb: print('     por libro:', dict(sorted(bb.items(), key=lambda x: -x[1])[:10]))
        for x in rs[:12]: print('     %-4s %3d:%-3d %s' % (x[0][0], x[0][1], x[0][2], str(x[1])[:90]))
    if len(rs) > 25: print('     ... +%d' % (len(rs) - 25))
json.dump({n: [[list(x[0]) if isinstance(x[0], tuple) else x[0], x[1]] for x in R[n]] for n in R},
          open('tools_audit/rv_detect.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
