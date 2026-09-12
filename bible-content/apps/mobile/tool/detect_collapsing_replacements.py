# -*- coding: utf-8 -*-
"""FASE 3: busca reemplazos que COLAPSAN el texto: dejan mucho menos de lo que sustituyen.

Esta clase aparecio al leer Numeros 31:3, donde dos reglas dejaron el versiculo en
"Moises hablo al pueblo, diciendo: e de vosotros para la guerra, e contra Madian".
Los detectores de duplicacion no la ven porque no duplica nada: borra.
"""
import json, os, re, sys, io, glob
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
os.chdir(Path(__file__).resolve().parents[4])

CAPAS = [('RV', 'bible-content/apps/mobile/assets/bibles/rv1909/books',
          'bible-content/apps/mobile/assets/bible_direction/*_reading_2026.rv1909.v1.json', None),
         ('KJV', 'bible-content/apps/mobile/assets/bibles/kjv/books',
          'bible-content/apps/mobile/assets/bible_direction/kjv/books/*_reading_2026.kjv.v1.json', True)]
OT = set(('GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC '
          'SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL').split())
MARK = re.compile(r'\\\+(?:w|add|nd)\*?\s*', re.I)
def nk(t):
    s = MARK.sub('', t); s = re.sub(r'\s+([,.;:!?])', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()
VACIAS = set('a e i o u y á é í ó ú de del la el los las un una y o que en con por para a'.split())
for nombre, cdir, pat, norm in CAPAS:
    corp, E = {}, defaultdict(list)
    for p in glob.glob(os.path.join(cdir, '*.json')):
        bk = json.load(open(p, encoding='utf-8'))
        if bk['book'] not in OT: continue
        for ch in bk['chapters']:
            for v in ch['verses']:
                t = v['text']
                corp[(bk['book'], ch['chapter'], v['verse'])] = nk(t) if norm else t
    for p in glob.glob(pat):
        d = json.load(open(p, encoding='utf-8'))
        if d.get('book') not in OT: continue
        for v in d['verses']:
            E[(d['book'], v['chapter'], v['verse'])] = sorted(v['edits'], key=lambda x: x['startOffset'])
    def proj(k):
        t = corp[k]
        for e in sorted(E.get(k, []), key=lambda x: -x['startOffset']):
            t = t[:e['startOffset']] + e['replacement'] + t[e['endOffset']:]
        return t
    graves, leves = [], []
    for k in sorted(E):
        for e in E[k]:
            pe, pr = e['expected'].split(), e['replacement'].split()
            if not pe: continue
            # colapso: el reemplazo pierde mas de la mitad de las palabras y lo que queda no aporta
            perdidas = len(pe) - len(pr)
            solo_vacias = all(w.strip('.,;:¿?¡!').lower() in VACIAS for w in pr) if pr else True
            if len(pe) >= 2 and (not pr or (solo_vacias and perdidas >= 1)):
                graves.append((k, e))
            elif len(pe) >= 4 and len(pr) * 2 < len(pe):
                leves.append((k, e))
    print('\n########## %s: colapsos graves=%d  acortamientos fuertes=%d' % (nombre, len(graves), len(leves)))
    for k, e in graves:
        print('\n  GRAVE %s %d:%d  %r -> %r' % (k + (e['expected'][:60], e['replacement'][:40])))
        print('        RV/KJV: %s' % corp[k][:175])
        print('        CAPA  : %s' % proj(k)[:175])
    for k, e in leves[:14]:
        print('  corto %-4s %3d:%-3d %r -> %r' % (k + (e['expected'][:58], e['replacement'][:44])))
    if len(leves) > 14: print('  ... +%d' % (len(leves) - 14))
