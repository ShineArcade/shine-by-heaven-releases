"""Targeted integrity/regression guard; NEVER certifies an editorial book review."""
import gzip
import json
import re
import argparse
from collections import Counter
from nt_context_review import ROOT, BASE, read, render
from apply_nt_context_repairs import build

parser=argparse.ArgumentParser()
parser.add_argument('--package-ready',action='store_true')
args=parser.parse_args()

source_history=[]
payloads, history = build(source_history=source_history)
decisions = read(ROOT/'editorial-review/nt-context-repairs-20260912.json')['repairs']
approved = {(d['version'],d['book'],d['chapter'],d['verse']) for d in decisions}
technical={('kjv',d['book'],d['chapter'],d['verse']) for d in source_history if d['status']=='restored'}
declared=approved|technical
assert len({d['id'] for d in decisions})==len(decisions)
assert read(ROOT/'editorial-review/nt-context-repair-history-20260912.json')==history
assert read(ROOT/'editorial-review/kjv-source-restoration-history-20260912.json')==source_history
texts={}
for version, payload in payloads.items():
    base = json.loads(gzip.decompress((ROOT/f'channel/reading_2026.{version}.v{BASE[version]}.package.json.gz').read_bytes()))
    assert [b['book'] for b in payload['books']]==[b['book'] for b in base['books']]
    for original, book in zip(base['books'],payload['books']):
        old={(v['chapter'],v['verse']):v for v in original['verses']}
        new={(v['chapter'],v['verse']):v for v in book['verses']}
        sources={(c['chapter'],v['verse']):v['text'] for c in read(ROOT/f'apps/mobile/assets/bibles/{version}/books/{book["book"]}.json')['chapters'] for v in c['verses']}
        for key in old.keys()|new.keys():
            source=sources[key]
            before=render(source,old.get(key,{'edits':[]})['edits'])
            after=render(source,new.get(key,{'edits':[]})['edits'])
            ref=(version,book['book'],*key)
            assert (before!=after)==(ref in declared), ('undeclared or ineffective verse',ref)
            texts[ref]=after
        if not any(k[:2]==(version,book['book']) for k in declared):
            assert book==original, ('unapproved book changed',version,book['book'])
        else:
            folder=ROOT/'apps/mobile/assets/bible_direction'
            if version=='kjv':folder=folder/'kjv/books'
            files=[f for f in folder.glob('*.json') if read(f).get('book')==book['book']]
            assert len(files)==1
            expected={**book,'verses':[v for v in book['verses'] if v['edits']]}
            actual=read(files[0])
            if args.package_ready:
                # Release builders refresh counts and the owning change-set version;
                # they may not change a single approved edit or any source identity.
                omit={'coverage','ownerReview'}
                assert {k:v for k,v in actual.items() if k not in omit}=={k:v for k,v in expected.items() if k not in omit},('direction differs from approved projection',version,book['book'])
                if 'coverage' in actual:
                    assert actual['coverage']['changedVerses']==len(actual['verses'])
                    assert actual['coverage']['editCount']==sum(len(v['edits']) for v in actual['verses'])
            else:
                assert actual==expected,('direction file differs from approved build',version,book['book'])
    # Every source book byte must still match the authoritative Git baseline.
    # Git handles this check separately below; no source rewrite belongs here.

for d in decisions:
    assert d['reason'].strip() and d['evidence']
    source=next(r['source'] for r in history if r['id']==d['id'])
    start=source.index(d['expected']); end=start+len(d['expected'])
    assert not (start and source[start-1].isalnum() and source[start].isalnum()), ('start cuts word',d['id'])
    assert not (end<len(source) and source[end-1].isalnum() and source[end].isalnum()), ('end cuts word',d['id'])

regressions=[
 ('rv1909','REV',3,9,'haré que vengan y adoren'),
 ('rv1909','REV',7,3,'pongamos el sello a los siervos'),
 ('rv1909','REV',11,4,'Estos son los dos olivos'),
 ('rv1909','REV',11,9,'de las naciones'),
 ('rv1909','REV',19,15,'él las regirá'),
 ('kjv','REV',9,7,'the appearance of the locusts was'),
 ('kjv','REV',18,17,'such great riches have come to nothing'),
 ('kjv','REV',21,6,'give freely from the fountain'),
 ('rv1909','MAT',8,21,'permíteme ir primero y enterrar'),
 ('kjv','MAT',9,20,'a woman'),
 ('kjv','MAT',11,17,'sung'),
 ('kjv','MAT',14,22,'get into a boat and go'),
 ('rv1909','MRK',6,43,'cestas llenas'),
 ('rv1909','MRK',10,12,'se divorcia de su marido y se casa con otro'),
 ('kjv','MRK',14,64,'condemned him as deserving death'),
 ('rv1909','LUK',1,1,'intentado poner'),
 ('rv1909','LUK',1,35,'el poder del Altísimo'),
 ('kjv','LUK',2,49,'Did ye not know'),
 ('rv1909','LUK',13,19,'semilla de mostaza, que tomándola un hombre la metió'),
 ('rv1909','LUK',14,23,'por las cercas'),
 ('rv1909','LUK',15,8,'enciende la lámpara'),
 ('rv1909','LUK',16,26,'un gran abismo está establecido'),
 ('rv1909','LUK',17,31,'no descienda á tomarlos'),
 ('kjv','LUK',17,31,'his belongings in the house, let him not come down to take them away'),
 ('rv1909','LUK',21,1,'en la caja de las ofrendas'),
 ('rv1909','LUK',21,24,'por los gentiles, hasta que los tiempos de los gentiles'),
 ('kjv','LUK',23,38,'an inscription'),
 ('rv1909','JHN',4,5,'junto á la parcela'),
 ('rv1909','JHN',4,35,'los campos, porque ya están blancos'),
 ('rv1909','JHN',6,37,'no le echo fuera'),
 ('kjv','JHN',2,3,'they ran out of wine'),
 ('rv1909','ACT',13,38,'anunciado el perdón de pecados'),
 ('rv1909','ACT',14,4,'la población de la ciudad estaba dividida'),
 ('kjv','ACT',15,27,'by word of mouth'),
 ('kjv','ACT',17,3,'had to suffer and rise again'),
 ('rv1909','ACT',18,25,'conociendo solamente el bautismo de Juan'),
 ('kjv','ACT',20,34,'provided for my needs and for those who were with me'),
 ('rv1909','ACT',24,25,'del dominio propio'),
 ('rv1909','ACT',26,24,'el mucho estudio te vuelve loco'),
 ('rv1909','ACT',27,39,'una bahía que tenía playa, a la cual'),
 ('kjv','ACT',28,6,'expected him to swell up or suddenly fall down dead'),
 ('kjv','ROM',1,13,'was hindered until now'),
 ('kjv','ROM',3,25,'passing over of past sins'),
 ('rv1909','ROM',5,20,'Pero la ley entró'),
 ('rv1909','ROM',8,17,'si en verdad padecemos'),
 ('kjv','ROM',9,2,'great sorrow and continual anguish'),
 ('rv1909','ROM',11,8,'espíritu de aturdimiento'),
 ('rv1909','ROM',14,15,'conforme al amor'),
 ('kjv','ROM',16,18,'the unsuspecting'),
 ('kjv','ROM',16,19,'innocent concerning evil'),
 ('rv1909','1CO',4,6,'para que ninguno se envanezca'),
 ('rv1909','1CO',5,11,'fuere sexualmente inmoral, ó avaro'),
 ('kjv','1CO',5,11,'be sexually immoral, or covetous'),
 ('kjv','1CO',6,13,'destroy both the belly and food'),
 ('rv1909','1CO',7,19,'los mandamientos'),
 ('rv1909','1CO',9,4,'derecho a comer y a beber'),
 ('kjv','1CO',11,29,'judgment on himself'),
 ('rv1909','1CO',12,27,'cada uno de vosotros es miembro de él'),
 ('rv1909','1CO',13,5,'No se comporta indebidamente'),
 ('rv1909','1CO',15,51,'Ciertamente no todos dormiremos'),
 ('rv1909','1CO',16,4,'conveniente que yo también vaya'),
 ('rv1909','2CO',1,11,'por el don que nos fue concedido'),
 ('kjv','2CO',6,6,'sincere love'),
 ('rv1909','2CO',7,12,'del que lo padeció, sino para que'),
 ('rv1909','2CO',8,8,'de vuestro amor'),
 ('kjv','2CO',8,1,'we make known to you the grace'),
 ('rv1909','2CO',9,5,'que fuesen primero á vosotros, y preparasen'),
 ('kjv','2CO',9,10,'Now may he that supplieth seed'),
 ('rv1909','2CO',10,13,'Pero nosotros no nos gloriaremos'),
 ('rv1909','2CO',11,3,'corrompidos y apartados de la sincera devoción'),
 ('kjv','2CO',12,9,'thee: for my strength'),
 ('kjv','GAL',2,5,'we did not yield in submission, not even for an hour'),
 ('rv1909','GAL',3,4,'Si es que fue en vano'),
 ('rv1909','GAL',3,24,'la ley fue nuestro tutor'),
 ('rv1909','GAL',5,7,'os estorbó'),
 ('rv1909','GAL',6,6,'comparta de todo lo bueno con el que lo instruye'),
 ('rv1909','EPH',4,1,'digno del llamamiento'),
 ('rv1909','EPH',4,31,'Sean quitados de vosotros'),
 ('kjv','PHP',1,12,'advance the gospel'),
 ('rv1909','PHP',2,15,'generación maligna y perversa, en medio de la cual'),
 ('kjv','COL',1,12,'fit to share in the inheritance'),
 ('rv1909','COL',1,23,'Si en verdad permanecéis'),
 ('rv1909','COL',2,14,'quitándolo de en medio y clavándolo'),
 ('kjv','COL',2,23,'but are of no value'),
 ('rv1909','1TH',2,12,'instábamos solemnemente a que'),
 ('rv1909','1TH',4,9,'acerca del amor fraternal'),
 ('kjv','1TH',2,3,'did not arise from error or uncleanness, nor was it made with deceit'),
 ('kjv','2TH',2,7,'he who now restrains will continue to restrain'),
 ('kjv','2TH',3,2,'not all men have faith'),
 ('kjv','2TH',3,10,'if anyone is unwilling to work'),
 ('kjv','1TI',1,5,'sincere faith'),
 ('rv1909','1TI',6,9,'muchos deseos insensatos y dañinos'),
 ('rv1909','1TI',6,20,'los discursos profanos y vacíos'),
 ('rv1909','1TI',6,21,'Al profesar ese conocimiento'),
 ('kjv','1TI',2,4,'desires all men to be saved'),
 ('rv1909','2TI',2,21,'toda buena obra'),
 ('kjv','2TI',2,17,'like gangrene: among them are'),
 ('kjv','TIT',1,15,'mind and conscience are defiled'),
 ('kjv','TIT',1,16,'unfit for any good work'),
 ('kjv','PHM',1,23,'Epaphras, my fellowprisoner in Christ Jesus, greets thee'),
 ('rv1909','HEB',8,4,'las ofrendas'),
 ('rv1909','HEB',10,34,'os compadecisteis de mí en mis prisiones'),
 ('kjv','HEB',10,24,'stir up love and good works'),
 ('rv1909','HEB',12,2,'en el autor'),
 ('rv1909','HEB',13,9,'anduvieron en ellos'),
 ('kjv','HEB',9,17,'a will takes effect'),
 ('kjv','HEB',9,20,'blood of the covenant'),
 ('rv1909','HEB',11,28,'el rociamiento de la sangre'),
 ('rv1909','HEB',9,22,'sin derramamiento de sangre'),
 ('kjv','JAS',3,13,'his works by good conduct'),
 ('kjv','JAS',5,4,'which are kept back by you through fraud, cry out'),
 ('rv1909','1PE',5,2,'Pastoread el rebaño de Dios que está entre vosotros, teniendo cuidado de él'),
 ('kjv','2PE',2,5,'Noah, a preacher of righteousness, with seven others'),
 ('kjv','MAT',18,6,'which believe in me to stumble,'),
 ('kjv','LUK',6,38,'the same measure that ye use, it shall'),
 ('rv1909','ACT',27,13,'soplando el viento del sur'),
 ('rv1909','1CO',7,3,'preste a la mujer la debida atención conyugal'),
 ('kjv','1CO',10,32,'Give no cause for stumbling, neither to the Jews'),
 ('rv1909','1CO',14,10,'ninguna de esas voces carece de significado'),
 ('kjv','1CO',16,22,'under a curse. Maranatha.'),
 ('rv1909','EPH',5,5,'ni ningún avaro, que es servidor de ídolos'),
 ('kjv','JAS',2,4,'Have ye not shown favoritism among yourselves and become judges with evil thoughts?'),
 ('rv1909','HEB',9,5,'daban sombra a la cubierta de expiación'),
 ('kjv','ROM',1,29,'sexual immorality, wickedness, greed, maliciousness; full of envy, murder, strife'),
 ('rv1909','2CO',12,21,'inmundicia e inmoralidad sexual y desenfreno'),
 ('kjv','REV',17,4,'having a golden cup in her hand full of abominations and filthiness of her sexual immorality'),
 ('rv1909','REV',17,5,'LA MADRE DE LAS INMORALIDADES SEXUALES'),
]
for version,book,c,v,expected in regressions:
    assert expected in texts[version,book,c,v], (version,book,c,v,expected)
for key in declared:
    text=texts[key]
    assert not re.search(r'\b(?:la poder|los cercas|el lámpara|el caja|las gentiles|a inscription|an chronic|have sang|was entered a boat|yeasted|de el amor|de el llamamiento|la don|love sincere|faith sincere|las discursos|muchas deseos|a gangrene|todo buena obra|make known to you of|to advance of the gospel)\b',text,re.I), (key,text)

import subprocess
root=ROOT.parent
unchanged=subprocess.run(['git','diff','--exit-code','8de177c','--','bible-content/apps/mobile/assets/bibles','bible-content/channel/reading_2026.rv1909.v26.package.json.gz','bible-content/channel/reading_2026.kjv.v14.package.json.gz'],cwd=root,capture_output=True)
assert unchanged.returncode==0, 'Pinned corpora or immutable baseline package changed'
if args.package_ready:
    for version,payload in payloads.items():
        folder=ROOT/'apps/mobile/assets/bible_direction'
        if version=='kjv':folder/='kjv'
        package=json.loads(gzip.decompress((folder/f'packages/reading_2026.{version}.v1.package.json.gz').read_bytes()))
        assert package['contentVersion']>BASE[version]
        assert package['sourceCorpusSha256']==payload['sourceCorpusSha256']
        assert [b['book'] for b in package['books']]==[b['book'] for b in payload['books']]
        for actual,expected in zip(package['books'],payload['books']):
            assert actual['sourceContentSha256']==expected['sourceContentSha256']
            # Later OT corrections have their own exact approvals. NT decisions
            # and every other OT edit must still match this reviewed projection.
            from verify_ot_followup_20260913 import approved_verses
            approved_book=approved_verses(version,expected['book'],expected['verses'])
            assert actual['verses']==[v for v in approved_book if v['edits']],('packaged projection differs',version,actual['book'])
print(json.dumps({'result':'PASS','decisions':len(decisions),'versionVerses':len(approved),'sourceRestoredVerses':len(technical),'byBook':dict(Counter(f'{v}:{b}' for v,b,c,n in approved)), 'packagedProjectionVerified':args.package_ready,'editorialCompleteness':'NOT ASSERTED','publication':'NOT VERIFIED BY THIS TEST'},ensure_ascii=False))
