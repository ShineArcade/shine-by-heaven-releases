"""Read-only chapter viewer for the exact published base and its reading layer.

This prepares review material; it does not label any verse editorially approved.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = {"rv1909": 26, "kjv": 14}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render(source, edits):
    end = 0
    for e in sorted(edits, key=lambda e: e["startOffset"]):
        assert e["startOffset"] >= end
        assert source[e["startOffset"]:e["endOffset"]] == e["expected"]
        end = e["endOffset"]
    for e in sorted(edits, key=lambda e: e["startOffset"], reverse=True):
        source = source[:e["startOffset"]] + e["replacement"] + source[e["endOffset"]:]
    return source


def rows(version, book):
    pack = json.loads(gzip.decompress((ROOT / f"channel/reading_2026.{version}.v{BASE[version]}.package.json.gz").read_bytes()))
    layer = next(b for b in pack["books"] if b["book"] == book)
    patches = {(v["chapter"], v["verse"]): v for v in layer["verses"]}
    source = read(ROOT / f"apps/mobile/assets/bibles/{version}/books/{book}.json")
    for c in source["chapters"]:
        for v in c["verses"]:
            p = patches.get((c["chapter"], v["verse"]), {"edits": []})
            if p["edits"]:
                assert hashlib.sha256(v["text"].encode()).hexdigest() == p["sourceTextSha256"]
            yield {"chapter": c["chapter"], "verse": v["verse"], "source": v["text"], "rendered": render(v["text"], p["edits"]), "edits": p["edits"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("version", choices=BASE)
    p.add_argument("book")
    p.add_argument("first", type=int)
    p.add_argument("last", type=int)
    p.add_argument("--changed-only", action="store_true")
    p.add_argument("--edits", action="store_true")
    p.add_argument("--working", action="store_true", help="Read the unpublished composed layer, including verified KJV source restoration")
    a = p.parse_args()
    working={}
    if a.working:
        from apply_nt_context_repairs import build
        payloads,_=build()
        b=next(b for b in payloads[a.version]['books'] if b['book']==a.book)
        working={(v['chapter'],v['verse']):v['edits'] for v in b['verses']}
        print('UNPUBLISHED WORKING READING; DELTA below describes the published lexical baseline.')
    for v in rows(a.version, a.book):
        if not a.first <= v["chapter"] <= a.last or (a.changed_only and not v["edits"]):
            continue
        text=render(v['source'],working.get((v['chapter'],v['verse']),[])) if a.working else v['rendered']
        print(f'{a.book} {v["chapter"]}:{v["verse"]} {text}')
        if a.edits and v["edits"]:
            print("  DELTA " + " | ".join(f'{e["expected"]} => {e["replacement"]}' for e in v["edits"]))
