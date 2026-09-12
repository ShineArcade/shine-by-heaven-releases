# -*- coding: utf-8 -*-
"""Guardas dirigidas de la auditoria del Antiguo Testamento 2026-09-12.

Fallan si vuelve a aparecer alguno de los defectos ya corregidos:
  G1  2 Reyes 23:11 no puede volver a decir "campo(s) de pastoreo" (hebreo parvarim, recinto del templo).
  G2  Ezequiel 45:2 no puede volver a decir "campo(s) de pastoreo" (franja abierta del santuario).
  G3  Ninguna regla puede mezclar "vosotros" y "ustedes" dentro del mismo versiculo.
  G4  Ninguna regla puede reunir varios terminos hebreos distintos bajo una sola sustitucion
      dentro de la familia "ejido" (se comprueba que las excepciones documentadas se mantengan).
  G5  El texto proyectado no puede contener la conjuncion "e" acentuada ante consonante,
      cliticon doble, palabra duplicada ni doble espacio.
  G6  El corpus fuente RV1909 no puede cambiar (se comprueba archivo por archivo).
  G7  Ninguna regla puede introducir la ortografia moderna que el texto base no usa nunca:
      en todo el Antiguo Testamento RV1909 escribe á 14 734 veces y a ninguna, fué 1 159 y
      fue ninguna, dió 231 y dio ninguna, vió 120 y vio ninguna, fuí 35 y fui ninguna.
  G8  Ningun reemplazo puede colapsar el texto dejando solo palabras vacias (Numeros 31:3
      llego a leerse "Moises hablo al pueblo, diciendo: e de vosotros para la guerra").
  G9  El itinerario de Numeros 33 no puede quedar con dos verbos conjugados sin conjuncion.
  G10 Los seis versiculos que cambiaban de persona conservan la segunda del plural.

Uso: python apps/mobile/tool/verify_ot_final_2026_guards.py
"""
import json, os, re, sys, glob, hashlib, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
BD = os.path.join(ROOT, 'apps', 'mobile', 'assets', 'bible_direction')
CORP = os.path.join(ROOT, 'apps', 'mobile', 'assets', 'bibles', 'rv1909', 'books')
OT = ['GEN','EXO','LEV','NUM','DEU','JOS','JDG','RUT','1SA','2SA','1KI','2KI','1CH','2CH','EZR',
      'NEH','EST','JOB','PSA','PRO','ECC','SNG','ISA','JER','LAM','EZK','DAN','HOS','JOL','AMO',
      'OBA','JON','MIC','NAM','HAB','ZEP','HAG','ZEC','MAL']
CORPUS_SHA = 'af7a0acc03b228719b549539dcd0dcaca3c40af51a4b3d6c96f51ec8510ec739'

failures = []


def fail(guard, msg):
    failures.append('%s: %s' % (guard, msg))


def load():
    corp, proj = {}, {}
    for code in OT:
        bk = json.load(open(os.path.join(CORP, code + '.json'), encoding='utf-8'))
        for ch in bk['chapters']:
            for v in ch['verses']:
                corp[(code, ch['chapter'], v['verse'])] = v['text']
    for p in glob.glob(os.path.join(BD, '*_reading_2026.rv1909.v1.json')):
        d = json.load(open(p, encoding='utf-8'))
        if d.get('book') not in OT:
            continue
        for v in d['verses']:
            k = (d['book'], v['chapter'], v['verse'])
            t = corp[k]
            for e in sorted(v['edits'], key=lambda x: -x['startOffset']):
                t = t[:e['startOffset']] + e['replacement'] + t[e['endOffset']:]
            proj[k] = t
    return corp, proj


corp, proj = load()
render = dict(corp)
render.update(proj)

# ---- G1 / G2 -------------------------------------------------------------
PASTO = re.compile(r'campos?\s+de\s+pastoreo|pastizal', re.I)
for guard, ref, nota in [('G1', ('2KI', 23, 11), 'parvarim H6503/H6504, recinto del templo'),
                         ('G2', ('EZK', 45, 2), 'franja abierta alrededor del santuario')]:
    txt = render.get(ref, '')
    if PASTO.search(txt):
        fail(guard, '%s %d:%d volvio a traducirse como pasto (%s): %r'
             % (ref[0], ref[1], ref[2], nota, txt[:120]))

# ---- G3 mezcla de persona ------------------------------------------------
STOP = set('''verdad ciudad edad libertad mitad necesidad heredad majestad voluntad piedad bondad
santidad maldad red pared sed vid salud juventud multitud virtud potestad propiedad enfermedad
humildad vanidad eternidad soledad claridad oscuridad mocedad suavidad calidad benignidad
dificultad cantidad autoridad seguridad merced deidad impiedad iniquidad amistad crueldad
falsedad fidelidad gravedad liviandad mortandad novedad prosperidad puridad sanidad suciedad
tempestad unidad utilidad vecindad facultad'''.split())
PART = re.compile(r'(?:ad|id)[oa]s?$')
IMP = re.compile(r'\b([A-Za-zÁÉÍÓÚáéíóúñ]{2,}[aei]d)(l[oaes]{1,2}|me|nos|os)?\b')
FIN = re.compile(r'\b\w+(?:áis|éis|ís|areis|iereis|ereis|asteis|isteis|réis)\b'
                 r'|\bvosotros\b|\bvuestr[oa]s?\b|\bhabéis\b|\bsois\b', re.I)
# Solo formas que en español únicamente pueden ser 2.ª persona plural de "ustedes":
# el pronombre explícito y los imperativos con acento antepenúltimo + clítico.
UST = re.compile(r'\bustedes\b'
                 r'|\b(?:preséntense|asegúrense|quítense|llámenlo|llámenla|mójenlo|mójenla'
                 r'|tómenlo|pónganlo|háganlo|váyanse|siéntense|levántense|acérquense)\b', re.I)
# Versiculos corregidos por la auditoria: deben conservar su forma de vosotros.
VIGILADOS = {
    ('GEN', 42, 9): 'Espías sois',
    ('GEN', 1, 28): 'Fructificad y multiplicaos',
    ('GEN', 29, 7): 'dad de beber',
    ('GEN', 40, 7): 'tenéis',
    ('GEN', 43, 31): 'Servid',
    ('GEN', 47, 23): 'sembrad la tierra',
    ('EXO', 32, 13): 'vuestra descendencia',
    ('EXO', 32, 24): 'quitáoslo',
    ('EXO', 2, 20): 'llamadle',
    ('EXO', 5, 4): 'volved',
    ('EXO', 5, 11): 'halléis',
    ('EXO', 12, 16): 'preparéis',
    ('EXO', 12, 22): 'mojadlo',
    ('LEV', 22, 32): 'profanéis',
    ('LEV', 23, 32): 'guardaréis vuestro',
    ('LEV', 23, 39): 'hayáis',
    ('LEV', 25, 46): 'dominaréis',
    ('LEV', 26, 13): 'vuestro yugo',
    ('LEV', 26, 17): 'os dominarán',
    ('NUM', 4, 27): 'asignaréis',
    ('NUM', 16, 17): 'presentaos',
    ('1SA', 23, 22): 'aseguraos',
}

def vosmarks(t):
    s = set(m.group(0) for m in FIN.finditer(t))
    for m in IMP.finditer(t):
        w, b = m.group(0), m.group(1).lower()
        if b in STOP or PART.search(w.lower()):
            continue
        s.add(w)
    return s


for k, t in proj.items():
    if UST.search(t) and not UST.search(corp[k]):
        fail('G3', '%s %d:%d introduce una forma de ustedes: %r' % (k[0], k[1], k[2], t[:140]))
    if vosmarks(t) and re.search(r'\bustedes\b', t, re.I):
        fail('G3', '%s %d:%d mezcla vosotros y ustedes: %r' % (k[0], k[1], k[2], t[:140]))
for ref, esperado in VIGILADOS.items():
    txt = render.get(ref, '')
    if esperado not in txt:
        fail('G3', '%s %d:%d perdio la forma de vosotros %r: %r'
             % (ref[0], ref[1], ref[2], esperado, txt[:140]))

# ---- G4 familia ejido ----------------------------------------------------
EXCEPCIONES = {('2KI', 23, 11): 'recinto', ('EZK', 45, 2): 'espacio abierto'}
for ref, esperado in EXCEPCIONES.items():
    if esperado not in render.get(ref, ''):
        fail('G4', '%s %d:%d deberia contener %r y no lo contiene' % (ref[0], ref[1], ref[2], esperado))
for p in glob.glob(os.path.join(BD, '*_reading_2026.rv1909.v1.json')):
    d = json.load(open(p, encoding='utf-8'))
    if d.get('book') not in OT:
        continue
    for v in d['verses']:
        for e in v['edits']:
            if 'ejido' in e['expected'].lower():
                ref = (d['book'], v['chapter'], v['verse'])
                if ref in EXCEPCIONES and PASTO.search(e['replacement']):
                    fail('G4', '%s %d:%d usa una sustitucion de pasto para un termino hebreo distinto'
                         % ref)

# ---- G5 roturas ----------------------------------------------------------
ROTURAS = [('conjuncion e ante consonante',
            r'(?<![A-Za-zÁÉÍÓÚáéíóúñ])é\s+(?![iIhH])[b-df-hj-np-tv-zBCDFGJ-NP-TV-Z]'),
           ('cliticon doble', r'\b(?:le|lo|la|les|los|las|me|te|nos|os)\s+se\b'),
           ('palabra duplicada', r'\b(que|de|a|á|en|y|el|la|los|las)\s+\1\b'),
           ('doble espacio', r'  +'),
           ('articulo sin concordancia', r'\b(?:el|un)\s+(?:persona|ofrenda)\b|\b(?:la|una)\s+(?:campos|cautivos)\b')]
for nombre, pat in ROTURAS:
    rx = re.compile(pat, re.I)
    for k, t in proj.items():
        if rx.search(t) and not rx.search(corp[k]):
            fail('G5', '%s %d:%d introduce %s: %r' % (k[0], k[1], k[2], nombre, t[:130]))

# ---- G6 corpus intacto ---------------------------------------------------
canon = [{'book': c,
          'chapters': [{'chapter': ch['chapter'],
                        'verses': [{'verse': v['verse'], 'text': v['text']} for v in ch['verses']]}
                       for ch in json.load(open(os.path.join(CORP, c + '.json'), encoding='utf-8'))['chapters']]}
         for c in OT]
del canon
man = json.load(open(os.path.join(os.path.dirname(CORP), 'manifest.json'), encoding='utf-8'))
alterados = [f['path'] for f in man['files']
             if hashlib.sha256(open(os.path.join(os.path.dirname(CORP), *f['path'].split('/')),
                                    'rb').read()).hexdigest() != f['sha256']]
if alterados:
    fail('G6', 'el corpus fuente RV1909 cambio en %d archivos: %s'
         % (len(alterados), ', '.join(alterados[:5])))
if man.get('contentSha256') and man['contentSha256'] != CORPUS_SHA:
    fail('G6', 'el manifiesto del corpus RV1909 declara %s' % man['contentSha256'])

# ---- G7 ortografia: RV1909 es categorica y la capa no debe introducir la forma moderna ----
for moderna in ('a', 'A', 'fue', 'Fue', 'dio', 'Dio', 'vio', 'Vio', 'fui', 'Fui'):
    rx = re.compile(r'(?<![\wáéíóúüñÁÉÍÓÚÜÑ])' + moderna + r'(?![\wáéíóúüñÁÉÍÓÚÜÑ])')
    for k, t in proj.items():
        n_base = len(rx.findall(corp[k]))
        n_capa = len(rx.findall(t))
        if n_capa > n_base:
            fail('G7', '%s %d:%d introduce la forma moderna %r, que el texto base no usa nunca: %r'
                 % (k[0], k[1], k[2], moderna, t[:120]))

# ---- G8 colapso: un reemplazo no puede dejar solo palabras vacias ----
VACIAS = set('a e i o u y á é í ó ú de del la el los las un una que en con por para'.split())
for p in glob.glob(os.path.join(BD, '*_reading_2026.rv1909.v1.json')):
    d = json.load(open(p, encoding='utf-8'))
    if d.get('book') not in OT:
        continue
    for v in d['verses']:
        for e in v['edits']:
            pe, pr = e['expected'].split(), e['replacement'].split()
            if len(pe) >= 2 and (not pr or (len(pr) < len(pe) and
                                            all(w.strip('.,;:¿?¡!').lower() in VACIAS for w in pr))):
                fail('G8', '%s %d:%d colapsa el texto: %r -> %r'
                     % (d['book'], v['chapter'], v['verse'], e['expected'][:60], e['replacement'][:40]))

# ---- G9 itinerario de Numeros 33: dos verbos conjugados piden conjuncion ----
ASIN = re.compile(r'[Pp]artieron [^,;.]{1,60}, (?:acamparon|asentaron|volvieron|pasaron)')
for k, t in proj.items():
    if ASIN.search(t) and not ASIN.search(corp[k]):
        fail('G9', '%s %d:%d deja dos verbos conjugados sin conjuncion: %r' % (k[0], k[1], k[2], t[:120]))

# ---- G10 los seis versiculos que cambiaban de persona ----
PERSONA = [(('EXO', 1, 16), 'asistáis'), (('EXO', 1, 18), 'habéis dejado'),
           (('EXO', 5, 5), 'hacéis dejar'), (('EXO', 5, 21), 'nos habéis hecho'),
           (('EXO', 34, 13), 'cortaréis'), (('LEV', 26, 22), 'os reduzcan')]
for ref, exigido in PERSONA:
    t = render.get(ref, '')
    if exigido not in t:
        fail('G10', '%s %d:%d perdio la segunda persona del plural, falta %r: %r'
             % (ref + (exigido, t[:110])))

print(json.dumps({
    'guards': ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10'],
    'otBooksChecked': len(OT),
    'versesRendered': len(proj),
    'expectedCorpusSha256': CORPUS_SHA,
    'failures': failures,
    'ok': not failures,
}, ensure_ascii=False, indent=2))
sys.exit(1 if failures else 0)
