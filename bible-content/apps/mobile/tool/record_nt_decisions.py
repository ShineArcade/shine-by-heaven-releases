"""Record explicit verse-level decisions, never discover or expand substitutions.

Input is a JSON array with version, book, chapter, verse, expected, replacement,
reason and optional evidence. Exact unique source spans and complete containment
of existing edits are mandatory; an ambiguous token must be supplied in context.
"""
import argparse
import json
from pathlib import Path
from nt_context_review import ROOT, read, rows, render


def record(path):
    path = Path(path)
    target = ROOT / 'editorial-review/nt-context-repairs-20260912.json'
    manifest = read(target)
    cache = {}
    for proposed in read(path):
        d = dict(proposed)
        version, book = d['version'], d['book']
        key = (version, book)
        if key not in cache:
            cache[key] = {(r['chapter'], r['verse']): r for r in rows(*key)}
        row = cache[key][d['chapter'], d['verse']]
        expected = d['expected']
        assert expected and row['source'].count(expected) == 1, (d, 'ambiguous source span')
        start = row['source'].index(expected)
        end = start + len(expected)
        overlaps = [e for e in row['edits'] if e['startOffset'] < end and e['endOffset'] > start]
        assert all(start <= e['startOffset'] and e['endOffset'] <= end for e in overlaps), (d, 'partial overlap')
        d['previousReading'] = render(expected, [{**e, 'startOffset': e['startOffset'] - start, 'endOffset': e['endOffset'] - start} for e in overlaps])
        assert d['previousReading'] != d['replacement'], (d, 'no change')
        for existing in manifest['repairs']:
            if all(existing[k] == d[k] for k in ('version', 'book', 'chapter', 'verse')):
                other = row['source'].index(existing['expected'])
                assert end <= other or other + len(existing['expected']) <= start, (d, 'overlaps an already approved directive; revise that directive explicitly instead')
        d.setdefault('category', 'context-reviewed-repair')
        d.setdefault('evidence', [{'label': 'Versículo completo y contexto del texto base', 'url': f'https://github.com/ShineArcade/shine-by-heaven-releases/blob/8de177c/bible-content/apps/mobile/assets/bibles/{version}/books/{book}.json'}])
        d.setdefault('id', f'nt-20260912-{version}-{book}-{d["chapter"]}-{d["verse"]}-{len(manifest["repairs"])+1}')
        assert not any(e['id'] == d['id'] for e in manifest['repairs'])
        manifest['repairs'].append(d)
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print('Recorded', len(read(path)), 'individually specified decisions')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('input')
    record(p.parse_args().input)
