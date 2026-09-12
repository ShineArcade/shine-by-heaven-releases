# -*- coding: utf-8 -*-
"""Pruebas dirigidas de la auditoria final del Antiguo Testamento en KJV Reading 2026.

Cada guarda falla si vuelve a aparecer un defecto concreto que esta auditoria corrigio.
No sustituyen la lectura: comprueban estados que no deben volver a darse.

  KG1  Ningun reemplazo introduce you/your/yourself en un versiculo que conserva thee/thou/thy/ye.
  KG2  Ningun reemplazo anade un "an" ante consonante ni un "a" ante vocal que el texto base
       no tuviera ya (la KJV escribe "an house", "an hundred" y se respeta).
  KG3  Los 23 versiculos que mezclaban pronombres conservan su forma arcaica.
  KG4  Los pasajes revertidos conservan el termino del texto base.
  KG5  Las familias de termino estan convertidas al 100 % en el AT: brass/brasen, candlestick,
       harlot, raiment, suburbs (migrash), taches, chapiters, emerods, rereward, beforetime, usury.
  KG6  Ningun objeto del tabernaculo lleva "his" e "its" en el mismo versiculo.
  KG7  Offsets validos, cero superposiciones y corpus KJV intacto.
"""
import glob, hashlib, json, os, re, sys, io
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(__file__).resolve().parents[3]
KBD = ROOT / 'apps/mobile/assets/bible_direction/kjv/books'
KCORP = ROOT / 'apps/mobile/assets/bibles/kjv'
CORPUS_SHA = '4e2c28113d053e64dacef2792a8d3bcfb32367320f549ef2c2f03b3122902939'
CORPUS_MANIFEST_SHA = '15630f9bf48928cfe7bb05be307e25262ccfb9b95ce614d997d4e4649e3b9111'
OT = ('GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG '
      'ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL').split()
MARK = re.compile(r'\\\+(?:w|add|nd)\*?\s*', re.I)
def nk(t):
    s = MARK.sub('', t); s = re.sub(r'\s+([,.;:!?])', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()

corp = {}
for c in OT:
    bk = json.loads((KCORP / 'books' / (c + '.json')).read_text(encoding='utf-8'))
    for ch in bk['chapters']:
        for v in ch['verses']:
            corp[(c, ch['chapter'], v['verse'])] = nk(v['text'])

edits, proj, fallos = [], {}, []
offsets_ok = superpuestos = 0
for p in sorted(KBD.glob('*_reading_2026.kjv.v1.json')):
    d = json.loads(p.read_text(encoding='utf-8'))
    if d['book'] not in OT: continue
    for v in d['verses']:
        k = (d['book'], v['chapter'], v['verse'])
        s = corp[k]
        es = sorted(v['edits'], key=lambda x: x['startOffset'])
        for i in range(len(es) - 1):
            if es[i]['endOffset'] > es[i + 1]['startOffset']: superpuestos += 1
        t = s
        for e in es:
            if s[e['startOffset']:e['endOffset']] == e['expected']: offsets_ok += 1
            else: fallos.append('KG7 offset invalido en %s %d:%d' % k)
            edits.append((k, e))
        for e in sorted(es, key=lambda x: -x['startOffset']):
            t = t[:e['startOffset']] + e['replacement'] + t[e['endOffset']:]
        proj[k] = t

# --- KG1
ARC = re.compile(r'\b(?:thee|thou|thy|thine|ye)\b', re.I)
YOU = re.compile(r'\b(?:you|your|yours|yourself|yourselves)\b', re.I)
for k, e in edits:
    if YOU.search(e['replacement']) and not YOU.search(e['expected']) and ARC.search(proj[k]):
        fallos.append('KG1 %s %d:%d mezcla you/your con pronombre arcaico: %r' % (k + (e['replacement'],)))

# --- KG2
ART = re.compile(r'\ban\s+(?![aeiouAEIOU])[bcdfghjklmnpqrstvwxyz]|\ba\s+[aeiouAEIOU]\w', re.I)
for k in proj:
    nuevos = Counter(x.lower() for x in ART.findall(proj[k]))
    nuevos.subtract(Counter(x.lower() for x in ART.findall(corp[k])))
    sobran = sorted(x for x, n in nuevos.items() if n > 0)
    if sobran:
        fallos.append('KG2 %s %d:%d articulo incorrecto: %r' % (k + (sobran[0],)))

# --- KG3  los 23 versiculos que mezclaban pronombres
VIGILADOS = [('EXO', 2, 14), ('EXO', 3, 18), ('EXO', 4, 6), ('EXO', 7, 16), ('EXO', 8, 9),
             ('EXO', 10, 4), ('EXO', 13, 7), ('EXO', 13, 16), ('EXO', 15, 7), ('EXO', 16, 23),
             ('EXO', 17, 2), ('EXO', 18, 18), ('EXO', 22, 26), ('EXO', 28, 40), ('EXO', 33, 18),
             ('GEN', 3, 17), ('GEN', 15, 1), ('GEN', 15, 4), ('GEN', 20, 6), ('GEN', 25, 23),
             ('GEN', 44, 15), ('GEN', 46, 34), ('GEN', 48, 6)]
for k in VIGILADOS:
    t = proj.get(k, corp[k])
    if len(YOU.findall(t)) > len(YOU.findall(corp[k])):
        fallos.append('KG3 %s %d:%d volvio a introducir you/your' % k)
    if not ARC.search(t):
        fallos.append('KG3 %s %d:%d perdio el pronombre arcaico del texto base' % k)

# --- KG4  pasajes revertidos
DEBE = [(('EXO', 4, 6), 'bosom', True), (('EXO', 4, 6), 'cloak', False),
        (('EXO', 4, 7), 'bosom', True), (('EXO', 4, 7), 'cloak', False),
        (('EXO', 13, 16), 'frontlets', True), (('EXO', 13, 16), 'forehead', False),
        (('EXO', 18, 18), 'thyself', True), (('EXO', 18, 18), 'yourselves', False),
        (('EXO', 25, 31), 'knops', True), (('EXO', 37, 17), 'knops', True),
        (('DEU', 29, 23), 'that that', False), (('EXO', 27, 4), 'brass', False),
        (('GEN', 20, 6), 'therefore allowed you', False)]
for k, frase, debe in DEBE:
    hay = re.search(r'\b' + re.escape(frase) + r'\b', proj.get(k, corp[k]), re.I) is not None
    if hay != debe:
        fallos.append('KG4 %s %d:%d %s %r' % (k + ('deberia contener' if debe else 'no debe contener', frase)))

# --- KG5  familias completas
for term, nuevo in (('brass', 'bronze'), ('brasen', 'bronze'), ('candlestick', 'lampstand'),
                    ('harlot', 'prostitute'), ('raiment', 'clothing'), ('suburbs', 'pasturelands'),
                    ('taches', 'clasps'), ('chapiters', 'capitals'), ('emerods', 'tumors'),
                    ('rereward', 'rear guard'), ('beforetime', 'formerly'), ('usury', 'interest')):
    rx = re.compile(r'\b' + term + r'\w*\b', re.I)
    quedan = [k for k in corp if rx.search(proj.get(k, corp[k]))]
    if quedan:
        fallos.append('KG5 %s sigue sin convertir a %s en %d versiculos, p. ej. %s %d:%d'
                      % ((term, nuevo, len(quedan)) + quedan[0]))

# --- KG6  his/its sobre el mismo objeto
OBJETOS = [('EXO', 12, 9), ('EXO', 25, 31), ('EXO', 27, 3), ('EXO', 35, 11), ('EXO', 35, 13),
           ('EXO', 35, 16), ('EXO', 37, 17), ('EXO', 39, 33), ('EXO', 39, 39), ('EXO', 39, 40)]
for k in OBJETOS:
    t = proj.get(k, corp[k])
    if re.search(r'\bits\b', t) and re.search(r'\bhis\b', t):
        fallos.append('KG6 %s %d:%d vuelve a mezclar his e its sobre el mismo objeto' % k)

# --- KG7  corpus intacto
man = json.loads((KCORP / 'manifest.json').read_text(encoding='utf-8'))
alterados = []
for f in man['files']:
    ruta = KCORP.joinpath(*f['path'].split('/'))
    if hashlib.sha256(ruta.read_bytes()).hexdigest() != f['sha256']:
        alterados.append(f['path'])
if alterados:
    fallos.append('KG7 el corpus fuente KJV cambio en %d archivos: %s'
                  % (len(alterados), ', '.join(alterados[:5])))
if man['contentSha256'] != CORPUS_MANIFEST_SHA:
    fallos.append('KG7 el manifiesto del corpus KJV cambio: %s' % man['contentSha256'])
paquete = json.loads((ROOT / 'apps/mobile/assets/bible_direction/kjv/packages'
                      / 'reading_2026.kjv.v1.manifest.json').read_text(encoding='utf-8'))
if paquete['sourceCorpusSha256'] != CORPUS_SHA:
    fallos.append('KG7 el paquete declara otro corpus fuente: %s' % paquete['sourceCorpusSha256'])
if superpuestos: fallos.append('KG7 %d superposiciones de ediciones' % superpuestos)

print(json.dumps({'guards': ['KG1', 'KG2', 'KG3', 'KG4', 'KG5', 'KG6', 'KG7'],
                  'otBooksChecked': len(OT), 'versesRendered': len(proj),
                  'editsChecked': len(edits), 'offsetsOk': offsets_ok,
                  'overlaps': superpuestos, 'failures': fallos, 'ok': not fallos},
                 indent=2, ensure_ascii=False))
sys.exit(1 if fallos else 0)
