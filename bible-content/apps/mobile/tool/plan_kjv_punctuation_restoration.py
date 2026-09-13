"""Plan verified source restoration over a reading layer; never approve ambiguity.

This is alignment/integrity work, NOT a lexical search-and-replace or an
assertion that unreviewed books have received an editorial reading.
"""
import difflib
import hashlib
import json
import re
from pathlib import Path
from nt_context_review import ROOT, read, render

TOKEN = re.compile(r"\w+(?:[’']\w+)*|\s+|[^\w\s]", re.UNICODE)


def tokens(text):
    ms=list(TOKEN.finditer(text))
    assert ''.join(m.group() for m in ms)==text
    return [m.group() for m in ms], [m.start() for m in ms]+[len(text)]


def equivalent_spans(source, reading):
    st,so=tokens(source);rt,ro=tokens(reading)
    return [(so[a],so[b],ro[c],ro[d]) for kind,a,b,c,d in
            difflib.SequenceMatcher(None,st,rt,autojunk=False).get_opcodes()
            if kind=='equal']


def map_point(point, spans, source_length, reading_length):
    if point==0:return 0
    if point==source_length:return reading_length
    candidates={rs+point-ss for ss,se,rs,re_ in spans if ss<=point<=se}
    return next(iter(candidates)) if len(candidates)==1 else None


def plan_one(source, restored_source, reading):
    equal=equivalent_spans(source,reading)
    operations=[];blocked=[]
    for kind,a,b,c,d in difflib.SequenceMatcher(None,source,restored_source,autojunk=False).get_opcodes():
        if kind=='equal':continue
        expected,replacement=source[a:b],restored_source[c:d]
        ra,rb=map_point(a,equal,len(source),len(reading)),map_point(b,equal,len(source),len(reading))
        # An unchanged word can sit INSIDE a rewritten phrase: "offend thee"
        # -> "causes thee to sin". A token matcher alone would put the comma
        # after "thee", before "to sin". Added words across a whitespace-only
        # boundary make that punctuation boundary editorially ambiguous.
        if a==b:
            for left,right in zip(equal,equal[1:]):
                ss,se,rs,re_=left; ns,ne,nr,nre=right
                if se==ns and ss<=a<=se and not source[a:se].strip() and any(ch.isalnum() for ch in reading[re_:nr]):
                    ra=rb=None
        op=dict(sourceStart=a,sourceEnd=b,expected=expected,replacement=replacement,
                readingStart=ra,readingEnd=rb)
        # A lexical revision may already supply this exact sign (e.g.
        # Verily verily -> Truly, truly). Retain it once, never duplicate it.
        if ra is not None and ra==rb and replacement and all(c in ',.;:!?()' for c in replacement):
            if reading[ra:ra+len(replacement)]==replacement or reading[max(0,ra-len(replacement)):ra]==replacement:
                op['alreadyPresent']=True
                operations.append(op)
                continue
        # The terminal boundary is structural even when the last word was
        # modernized. Never append a second terminal sign already supplied by
        # a reviewed lexical clause; a different sign requires manual review.
        if a==b==len(source) and reading and reading[-1] in '.;:!?\"”':
            if reading.endswith(replacement):
                op['alreadyPresent']=True
                operations.append(op)
                continue
            ra=rb=None
        if ra is None or rb is None or ra>rb or reading[ra:rb]!=expected:
            op['blockedReason']='Source restoration intersects or borders a changed lexical span ambiguously'
            blocked.append(op)
        else:operations.append(op)
    # A verse is all-or-nothing in this plan. No partially punctuated result
    # is mistaken for a complete restoration.
    if blocked:return dict(status='manual_alignment_required',operations=operations,blocked=blocked)
    after=reading
    for op in sorted(operations,key=lambda o:(o['readingStart'],o['readingEnd']),reverse=True):
        if op.get('alreadyPresent'):continue
        after=after[:op['readingStart']]+op['replacement']+after[op['readingEnd']:]
    # The aligner must not create adjacent sentence separators at a lexical
    # edit boundary. These are review candidates, not silently normalized.
    for m in re.finditer(r'[,.;:!?]{2,}',after):
        if m.group() not in reading and m.group() not in restored_source:
            return dict(status='manual_alignment_required',operations=operations,
                        blocked=[dict(blockedReason='Restoration would introduce adjacent punctuation',sequence=m.group())])
    return dict(status='aligned_candidate',operations=operations,blocked=[],after=after)


def main():
    from apply_nt_context_repairs import build
    payloads,_=build(restore_source=False)
    kjv=payloads['kjv']
    book_layers={b['book']:{(v['chapter'],v['verse']):v for v in b['verses']} for b in kjv['books']}
    restorations=read(ROOT/'editorial-review/kjv-source-restoration-20260912.json')['verses']
    corpus_cache={}
    records=[]
    for item in restorations:
        book=item['book']; key=item['chapter'],item['verse']
        if book not in corpus_cache:
            corpus_cache[book]={(c['chapter'],v['verse']):v['text'] for c in read(ROOT/f'apps/mobile/assets/bibles/kjv/books/{book}.json')['chapters'] for v in c['verses']}
        source=corpus_cache[book][key]
        assert hashlib.sha256(source.encode()).hexdigest()==item['sourceSha256'], (book,key,'unverified installed source')
        layer=book_layers[book].get(key,{'edits':[]})
        reading=render(source,layer['edits'])
        planned=plan_one(source,item['restoredSource'],reading)
        if item['sameWords'] and planned['status']=='aligned_candidate':
            assert ''.join(c for c in reading if c.isalnum())==''.join(c for c in planned['after'] if c.isalnum()), (book,key,'letter drift')
        records.append(dict(book=book,chapter=key[0],verse=key[1],source=source,
            verifiedRestoredSource=item['restoredSource'],before=reading,sourceSha256=hashlib.sha256(source.encode()).hexdigest(),
            sameSourceWords=item['sameWords'],**planned))
    dest=ROOT.parent/'scratch/nt-review/punctuation-alignment-plan.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    from collections import Counter
    print(json.dumps({'verses':len(records),'status':dict(Counter(r['status'] for r in records)),
        'blockedByBook':dict(Counter(r['book'] for r in records if r['blocked'])),
        'output':str(dest),'applied':False,'editorialReviewCompleted':False}))


if __name__=='__main__': main()
