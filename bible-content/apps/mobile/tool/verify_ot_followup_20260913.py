"""Validate the four reviewed OT corrections and preserve every other verse."""
import copy
import gzip
import hashlib
import json
from nt_context_review import ROOT, read, render

HISTORY = read(ROOT/'editorial-review/ot-followup-20260913.json')
SCOPE = {('rv1909','ZEC',14,4),('kjv','2KI',23,11),('kjv','EZK',45,2),('kjv','PSA',18,26)}
assert {(h['version'],h['book'],h['chapter'],h['verse']) for h in HISTORY} == SCOPE
assert len(HISTORY) == 4

def approved_verses(version, book, verses):
    result = copy.deepcopy(verses)
    for h in HISTORY:
        if (h['version'],h['book']) != (version,book): continue
        row = next(v for v in result if (v['chapter'],v['verse']) == (h['chapter'],h['verse']))
        assert row['edits'] == h['previousEdits'], ('stale OT approval',h['id'])
        assert row['sourceTextSha256'] == h['sourceTextSha256']
        assert hashlib.sha256(h['source'].encode()).hexdigest() == h['sourceTextSha256']
        assert h['reason'].strip() and h['evidence'] and len(h['localControls']) == 4
        assert render(h['source'], h['previousEdits']) == h['previousReading']
        assert render(h['source'], h['edits']) == h['finalReading']
        assert h['previousReading'] != h['finalReading']
        row['edits'] = h['edits']
    return result

if __name__ == '__main__':
    checked = 0
    for version,base in [('rv1909',27),('kjv',15)]:
        old = json.loads(gzip.decompress((ROOT/f'channel/reading_2026.{version}.v{base}.package.json.gz').read_bytes()))
        folder = ROOT/'apps/mobile/assets/bible_direction'
        if version=='kjv': folder /= 'kjv'
        current = json.loads(gzip.decompress((folder/f'packages/reading_2026.{version}.v1.package.json.gz').read_bytes()))
        assert current['contentVersion'] == base + 1
        assert current['sourceCorpusSha256'] == old['sourceCorpusSha256']
        assert [b['book'] for b in current['books']] == [b['book'] for b in old['books']]
        for before,after in zip(old['books'],current['books']):
            assert before['sourceContentSha256'] == after['sourceContentSha256']
            expected = approved_verses(version,before['book'],before['verses'])
            assert after['verses'] == expected, ('unapproved change',version,before['book'])
            checked += 1
    print(json.dumps(dict(ok=True,booksCompared=checked,approvedChangedVerses=4,newTestamentUnchanged=True,otherOldTestamentVersesUnchanged=True)))
