"""Apply individually approved source spans over the immutable public baseline.

Never expands a lexical rule to additional verses. Every removed overlapping
edit and both full rendered verses are retained for independent review.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
from nt_context_review import ROOT, BASE, read, render

FILE = ROOT / 'editorial-review/nt-context-repairs-20260912.json'


def build(*, restore_source=True, source_history=None):
    decisions = read(FILE)
    out = {}
    history = []
    for version, number in BASE.items():
        p = ROOT / f'channel/reading_2026.{version}.v{number}.package.json.gz'
        out[version] = json.loads(gzip.decompress(p.read_bytes()))
    for d in decisions['repairs']:
        version, book = d['version'], d['book']
        layer = next(b for b in out[version]['books'] if b['book'] == book)
        corpus = read(ROOT / f'apps/mobile/assets/bibles/{version}/books/{book}.json')
        source = next(v['text'] for c in corpus['chapters'] if c['chapter'] == d['chapter'] for v in c['verses'] if v['verse'] == d['verse'])
        matches = [i for i in range(len(source)) if source.startswith(d['expected'], i)]
        assert len(matches) == 1, (d['id'], 'ambiguous or absent source span', matches)
        start, end = matches[0], matches[0] + len(d['expected'])
        verse = next((v for v in layer['verses'] if (v['chapter'], v['verse']) == (d['chapter'], d['verse'])), None)
        if verse is None:
            verse = {'chapter': d['chapter'], 'verse': d['verse'], 'sourceTextSha256': hashlib.sha256(source.encode()).hexdigest(), 'edits': []}
            layer['verses'].append(verse)
        before = render(source, verse['edits'])
        removed = [e for e in verse['edits'] if e['startOffset'] < end and e['endOffset'] > start]
        assert all(start <= e['startOffset'] and e['endOffset'] <= end for e in removed), (d['id'], 'partial edit overlap')
        local = [{**e, 'startOffset': e['startOffset'] - start, 'endOffset': e['endOffset'] - start} for e in removed]
        assert render(d['expected'], local) == d['previousReading'], (d['id'], 'previous reading differs')
        verse['edits'] = [e for e in verse['edits'] if e not in removed]
        if d['expected'] != d['replacement']:
            verse['edits'].append({'startOffset': start, 'endOffset': end, **{k: d[k] for k in ('expected', 'replacement', 'category', 'reason', 'evidence')}})
        verse['edits'].sort(key=lambda e: e['startOffset'])
        layer['verses'].sort(key=lambda v: (v['chapter'], v['verse']))
        after = render(source, verse['edits'])
        assert before != after, (d['id'], 'no change')
        history.append({**d, 'source': source, 'before': before, 'after': after, 'supersededEdits': copy.deepcopy(removed)})
    if restore_source:
        from kjv_source_restoration import restore_kjv
        restoration_history=restore_kjv(out['kjv'])
        if source_history is not None:source_history.extend(restoration_history)
    for entry in history:
        layer = next(b for b in out[entry['version']]['books'] if b['book'] == entry['book'])
        verse = next(v for v in layer['verses'] if (v['chapter'], v['verse']) == (entry['chapter'], entry['verse']))
        entry['finalReading'] = render(entry['source'], verse['edits'])
    return out, history


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--write', action='store_true')
    a = p.parse_args()
    source_history=[]
    payloads, history = build(source_history=source_history)
    changed = {(d['version'], d['book']) for d in history}
    changed.update(('kjv',d['book']) for d in source_history if d['status']=='restored')
    if a.write:
        direction = ROOT / 'apps/mobile/assets/bible_direction'
        for version, book in changed:
            folder = direction if version == 'rv1909' else direction / 'kjv/books'
            candidates = [f for f in folder.glob('*.json') if read(f).get('book') == book]
            assert len(candidates) == 1, (version, book, candidates)
            layer = next(b for b in payloads[version]['books'] if b['book'] == book)
            layer['verses'] = [v for v in layer['verses'] if v['edits']]
            candidates[0].write_text(json.dumps(layer, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf8')
        (ROOT / 'editorial-review/nt-context-repair-history-20260912.json').write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        (ROOT / 'editorial-review/kjv-source-restoration-history-20260912.json').write_text(json.dumps(source_history, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'written': a.write, 'repairs': len(history), 'verses': len({(d['version'], d['book'], d['chapter'], d['verse']) for d in history}), 'sourceRestoredVerses':sum(d['status']=='restored' for d in source_history), 'books': sorted(changed)}, ensure_ascii=False))
