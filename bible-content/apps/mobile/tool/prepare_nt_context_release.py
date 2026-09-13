"""Package the reviewed NT projection; contains no lexical discovery or replacements.

Run after apply_nt_context_repairs --write and both contextual verifiers pass.
The immutable baseline channels and corpora are never written here.
"""
import json,sys,hashlib,re
from collections import Counter
from nt_context_review import ROOT,read,render
from apply_nt_context_repairs import build

STAMP='2026-09-13T07:15:00.000Z'
VERSIONS={'rv1909':27,'kjv':15}
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

payloads,history=build()
assert read(ROOT/'editorial-review/nt-context-repair-history-20260912.json')==history
nt={h['book'] for h in history};assert len(nt)==27
directions={}
for version,payload in payloads.items():
 folder=ROOT/'apps/mobile/assets/bible_direction'
 if version=='kjv':folder/= 'kjv/books'
 files={read(p).get('book'):p for p in folder.glob('*.json') if '_reading_2026.' in p.name}
 for book in payload['books']:
  actual=read(files[book['book']]);approved=[v for v in book['verses'] if v['edits']]
  assert actual['verses']==approved,(version,book['book'],'unapproved direction change')
  assert actual['sourceContentSha256']==book['sourceContentSha256']
  directions[version,book['book']]=actual

rv_changes=[]
for book in payloads['rv1909']['books']:
 if book['book'] not in nt:continue
 for verse in book['verses']:
  for e in verse['edits']:
   rv_changes.append(dict(book=book['book'],chapter=verse['chapter'],verse=verse['verse'],**e))
change_set=dict(format='shine-reading-2026-editorial-change-set',schemaVersion=1,contentVersion=27,
 generatedAt=STAMP,issuedAt=STAMP,expiresAt='2028-09-13T07:15:00.000Z',sourceVersionId='RV1909',filterId='RV1909-LECTURA-2026',
 note='Relectura contextual NT sobre v26: conservar, aclarar y restaurar por ocurrencia. AT y corpus fuente preservados. Historial y reservas en editorial-review/nt-context-repair-history-20260912.json y NT_RESERVATION_CLOSURE_20260912.md.',changes=rv_changes)
write(ROOT/'editorial-changes/v27.json',change_set)

docroot='https://github.com/ShineArcade/shine-by-heaven-releases/blob/main/bible-content/editorial-review/'
docs=[dict(label='Revisión por libro / Book review',url=docroot+'NT_CONTEXT_DISPOSITIONS_20260912.md'),dict(label='Decisiones y reservas / Decisions and reservations',url=docroot+'NT_RESERVATION_CLOSURE_20260912.md'),dict(label='Historial completo / Full review history',url=docroot+'nt-context-repair-history-20260912.json')]
for version in VERSIONS:
 filename='registry.json' if version=='rv1909' else 'registry.kjv.json'
 p=ROOT/'editorial-review'/filename;reg=read(p)
 reg['updatedAt']=STAMP
 if version=='rv1909':reg['activeChangeSet']='editorial-changes/v27.json'
 else:reg['activeContentVersion']=15
 reg['reviewDocuments']=docs
 reg['reviewRound']=dict(id='nt-context-20260912',contentVersion=VERSIONS[version],baselineContentVersion=26 if version=='rv1909' else 14,bookCount=27,method='Sequential full verse reading, contextual reference checks, complete composite rereading and targeted closure; no automatic lexical expansion.',sourceCorpusChanged=False)
 reg['reviewHistory']=[dict(id=h['id'],book=h['book'],chapter=h['chapter'],verse=h['verse'],expected=h['previousReading'],replacement=h['replacement'],original=h['expected'],reason=h['reason'],evidence=h['evidence'],localControls=h.get('localControls',[]),restoredOriginal=h['expected']==h['replacement'],finalReading=h['finalReading']) for h in history if h['version']==version]
 # Historical exact-term pending lists sometimes still name already-replaced
 # occurrences. Move only an absent exact term; never infer a semantic approval
 # or touch an OT reference or a multi-family description.
 remaining=[];resolved=reg.get('resolvedReviewReferences',[])
 for item in reg['pending']:
  if re.fullmatch(r'[\w -]+',item['term'],re.UNICODE):
   keep=[]
   for ref in item['references']:
    if ref['book'] not in nt:keep.append(ref);continue
    corpus=read(ROOT/f'apps/mobile/assets/bibles/{version}/books/{ref["book"]}.json')
    source=next(v['text'] for c in corpus['chapters'] if c['chapter']==ref['chapter'] for v in c['verses'] if v['verse']==ref['verse'])
    verse=next((v for v in directions[version,ref['book']]['verses'] if (v['chapter'],v['verse'])==(ref['chapter'],ref['verse'])),{'edits':[]})
    final=render(source,verse['edits']);pat=r'(?<!\w)'+re.escape(item['term'])+r'(?!\w)'
    if re.search(pat,source,re.I) and not re.search(pat,final,re.I):
     resolved.append(dict(registryId=item['id'],term=item['term'],reference=ref,status='occurrence-already-replaced',contentVersion=VERSIONS[version],reason='Esta ocurrencia del término ya no aparece en la lectura activa. El cambio y su razón se conservan en el registro aplicado; esto no aprueba por extensión otras ocurrencias.',edits=verse['edits']))
    else:keep.append(ref)
   if keep:item={**item,'references':keep}
   else:continue
  remaining.append(item)
 reg['pending']=remaining
 reg['resolvedReviewReferences']=resolved
 # Each remaining new interpretation is explicitly held, not silently applied.
 reserves=read(ROOT/'editorial-review/nt-context-reservations-20260912.json')
 for item in reserves:
  if version not in item['versions']:continue
  entry={k:v for k,v in item.items() if k!='versions'}
  entry['id']=f'nt-context-{version}-'+item['id']
  entry.update(status='pending-review',scope='new-testament',evidence=[docs[1]])
  reg['pending']=[x for x in reg['pending'] if x['id']!=entry['id']]+[entry]
 if version=='kjv':
  reg['applied']=[dict(reference=f"{b['book']}.{v['chapter']}.{v['verse']}",**{k:e[k] for k in ('expected','replacement','category','reason')},evidence=e.get('evidence',[])) for b in payloads[version]['books'] for v in b['verses'] for e in v['edits']]
 write(p,reg)

source=ROOT/'apps/mobile/assets/bible_direction/kjv/reading_2026.package-source.json'
d=read(source);d.update(contentVersion=15,generatedAt=STAMP);d['editorialPolicy']['version']=15;write(source,d)
coverage=read(ROOT/'editorial-review/nt-context-coverage-20260912.json')
assert coverage['initialSequentialReadComplete'] and not coverage['unreadBooks']
for b in coverage['books']:
 b.update(stage='contextual_review_and_reservation_disposition_complete',finalEditorialClosure=True,closureRecord='NT_RESERVATION_CLOSURE_20260912.md')
coverage.update(complete=True,completionMeaning='Requested additional contextual round complete. Retained interpretive reservations remain documented; no claim of error-free translation or external audit approval.',decisionCount=len(history),versionVerseCount=len({(h['version'],h['book'],h['chapter'],h['verse']) for h in history}))
write(ROOT/'editorial-review/nt-context-coverage-20260912.json',coverage)
print(json.dumps(dict(prepared=True,rvVersion=27,kjvVersion=15,rvRules=len(rv_changes),decisions=len(history),published=False)))
