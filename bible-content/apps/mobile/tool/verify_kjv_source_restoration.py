"""Focused regressions for observed conversion and composition failures."""
from collections import Counter
import hashlib,json
from nt_context_review import ROOT,read,render
from apply_nt_context_repairs import build
from kjv_source_restoration import anchored_edits, fingerprint, LETTER_REFS
from plan_kjv_punctuation_restoration import plan_one

h=[]
payloads,_=build(source_history=h)
spec={(x['book'],x['chapter'],x['verse']):x for x in read(ROOT/'editorial-review/kjv-source-restoration-20260912.json')['verses']}
assert len(h)==len(spec)==2019
out={(x['book'],x['chapter'],x['verse']):x for x in h}
assert set(out)==set(spec)
letter_changed=set()
for key,r in out.items():
    s=spec[key]
    if fingerprint(r['before'])!=fingerprint(r['after']):letter_changed.add(key)
    if r['status']=='already_restored':
        assert r['before']==r['after'];continue
    if not r['previousEdits']:assert r['after']==s['restoredSource'],(key,'unmodified verse not restored exactly')
    for e in r['resultingEdits']:
        assert 0<=e['startOffset']<e['endOffset']
        assert e['expected'] and e['replacement'] and e['category'] and e['reason'] and e['evidence']
        assert len(e['expected'].encode('utf-16-le'))//2==e['endOffset']-e['startOffset']
assert letter_changed==LETTER_REFS,letter_changed
assert 'shall more be given.' in out['MRK',4,24]['after']
assert 'with tears,' in out['LUK',7,44]['after']
assert out['JHN',13,20]['after'].startswith('Truly, truly, I say unto you, He that')
assert 'causes thee to sin, pluck it out' in out['MAT',5,29]['after']
assert 'give her justice, lest' in out['LUK',18,5]['after']
assert out['MRK',4,39]['status']=='already_restored'
# Ambiguous comma inside a rewritten clause must remain blocked by the
# generic aligner; its signed-off per-verse boundary is handled separately.
assert plan_one('If it offend thee go','If it offend thee, go.','If it causes thee to sin go')['blocked']
assert plan_one('Go now','Go now.','Go immediately')['after']=='Go immediately.'
assert plan_one('Verily verily','Verily, verily.','Truly, truly')['after']=='Truly, truly.'
assert plan_one('Go now','Go now.','Go immediately?')['blocked']
# Released receivers reject zero-width edits and empty replacement strings.
for source,after in [('word','word.'),('extra word','word.'),('Hello world','Hello, world.'),('word','new phrase.')]:
    edits=anchored_edits(source,after,[])
    assert render(source,edits)==after
    assert all(e['endOffset']>e['startOffset'] and e['replacement'] for e in edits)
print(json.dumps(dict(result='PASS',sourceRecords=len(h),status=dict(Counter(r['status'] for r in h)),
    manualBoundaries=sum(r['mode']=='individually_reviewed_boundary' for r in h),lostLetterVerses=sorted(letter_changed),
    scope='Source integrity and compatible composition, not editorial review of all books',published=False)))
