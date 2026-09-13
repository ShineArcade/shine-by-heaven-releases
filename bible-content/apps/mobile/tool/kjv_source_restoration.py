"""Compatible reading-layer restoration; pinned corpus bytes remain untouched."""
import copy,difflib,hashlib,re
from nt_context_review import ROOT,read,render
from plan_kjv_punctuation_restoration import tokens,plan_one

EVIDENCE={'label':'Verified canonical USFM; conversion-loss restoration',
          'url':'https://ebible.org/Scriptures/eng-kjv_usfm.zip'}
REASON='Restores punctuation or a verified lost final letter from the original KJV USFM. The installed source and its hash remain unchanged.'
LETTER_REFS={('MRK',4,24),('LUK',7,44),('JHN',13,20)}


def fingerprint(s):return ''.join(c for c in s if c.isalnum())


def anchored_edits(source,after,previous):
    """Serialize exact output with nonempty, whole-token source anchors.

    No text is invented here: applying the result must reproduce after exactly.
    Insertions/deletions borrow a neighbouring word and overlapping anchors are
    merged before serialization. This satisfies released Mobile's span rules.
    """
    assert source and after
    assert all(ord(c)<=0xffff for c in source+after),'UTF-16 offset conversion required'
    st,so=tokens(source);rt,ro=tokens(after)
    ops=difflib.SequenceMatcher(None,st,rt,autojunk=False).get_opcodes()
    intervals=[]
    for kind,a,b,c,d in ops:
        if kind=='equal':continue
        left,right=a,b
        if a==b or c==d or not ''.join(st[a:b]).strip() or not ''.join(rt[c:d]).strip():
            # Include a real word, not an empty or whitespace-only anchor.
            anchor=next((i for i in range(a-1,-1,-1) if any(ch.isalnum() for ch in st[i])),None)
            if anchor is not None:left=anchor
            else:
                anchor=next((i for i in range(b,len(st)) if any(ch.isalnum() for ch in st[i])),None)
                assert anchor is not None
                right=anchor+1
        intervals.append([left,right])
    merged=[]
    for a,b in sorted(intervals):
        if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
        else:merged.append([a,b])

    def mapped(point,side):
        candidates=[]
        for kind,a,b,c,d in ops:
            if kind=='equal' and a<=point<=b:candidates.append(c+point-a)
            elif kind!='equal':
                if point==a:candidates.append(c)
                if point==b:candidates.append(d)
        assert candidates,(point,side)
        return min(candidates) if side=='start' else max(candidates)

    edits=[]
    for a,b in merged:
        start,end=so[a],so[b]; c,d=mapped(a,'start'),mapped(b,'end')
        expected,replacement=source[start:end],after[ro[c]:ro[d]]
        assert expected and replacement and expected!=replacement
        affected=[e for e in previous if e['startOffset']<end and e['endOffset']>start]
        lexical=fingerprint(expected)!=fingerprint(replacement) and bool(affected)
        reasons=list(dict.fromkeys(e['reason'] for e in affected)) if lexical else []
        evidence=[copy.deepcopy(EVIDENCE)]
        if lexical:
            for e in affected:
                for link in e.get('evidence',[]):
                    if link not in evidence:evidence.append(copy.deepcopy(link))
        edits.append(dict(startOffset=start,endOffset=end,expected=expected,replacement=replacement,
            category='source-restoration-with-reviewed-reading' if lexical else 'source-conversion-restoration',
            reason=' '.join(reasons+[REASON]),evidence=evidence))
    assert render(source,edits)==after,'Anchor serialization changed the reviewed output'
    return edits


def restore_kjv(payload):
    spec=read(ROOT/'editorial-review/kjv-source-restoration-20260912.json')
    overrides={(x['book'],x['chapter'],x['verse']):x for x in read(ROOT/'editorial-review/kjv-punctuation-boundaries-20260912.json')}
    corpus={};history=[];used=set()
    layers={b['book']:b for b in payload['books']}
    for item in spec['verses']:
        book=item['book'];key=(book,item['chapter'],item['verse'])
        if book not in corpus:
            corpus[book]={(c['chapter'],v['verse']):v['text'] for c in read(ROOT/f'apps/mobile/assets/bibles/kjv/books/{book}.json')['chapters'] for v in c['verses']}
        source=corpus[book][key[1:]]; corrected=item['restoredSource']
        assert hashlib.sha256(source.encode()).hexdigest()==item['sourceSha256'],(key,'wrong installed source')
        assert hashlib.sha256(corrected.encode()).hexdigest()==item['restoredSourceSha256'],(key,'restoration changed')
        assert (fingerprint(source)==fingerprint(corrected))==item['sameWords']
        assert item['sameWords'] or key in LETTER_REFS,(key,'unapproved source letters')
        layer=layers[book]
        verse=next((v for v in layer['verses'] if (v['chapter'],v['verse'])==key[1:]),None)
        previous=verse['edits'] if verse else []
        before=render(source,previous)
        planned=plan_one(source,corrected,before)
        manual=overrides.get(key)
        if manual:
            assert manual['sourceSha256']==item['sourceSha256']
            assert hashlib.sha256(before.encode()).hexdigest()==manual['readingSha256'],(key,'manual punctuation decision needs re-review after lexical change')
            after=manual['after'];used.add(key)
            assert fingerprint(after)==fingerprint(before),(key,'manual lexical drift')
            mode='individually_reviewed_boundary'
        else:
            assert not planned['blocked'],(key,'punctuation alignment requires review',planned['blocked'])
            after=planned['after'];mode='unchanged_token_alignment'
        if item['sameWords']:assert fingerprint(before)==fingerprint(after),(key,'lexical drift')
        if before==after:
            history.append(dict(book=book,chapter=key[1],verse=key[2],status='already_restored',mode=mode,
                before=before,after=after,sourceSha256=item['sourceSha256'],reason=manual['reason'] if manual else REASON))
            continue
        edits=anchored_edits(source,after,previous)
        if verse is None:
            verse=dict(chapter=key[1],verse=key[2],sourceTextSha256=item['sourceSha256'],edits=[])
            layer['verses'].append(verse)
        assert verse['sourceTextSha256']==item['sourceSha256']
        history.append(dict(book=book,chapter=key[1],verse=key[2],status='restored',mode=mode,
            sourceSha256=item['sourceSha256'],before=before,after=after,previousEdits=copy.deepcopy(previous),
            resultingEdits=copy.deepcopy(edits),reason=manual['reason'] if manual else REASON,evidence=[EVIDENCE]))
        verse['edits']=edits
    assert used==set(overrides),'Unused manual boundary decisions'
    for layer in layers.values():layer['verses'].sort(key=lambda v:(v['chapter'],v['verse']))
    return history
