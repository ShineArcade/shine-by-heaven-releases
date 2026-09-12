# -*- coding: utf-8 -*-
"""Build the deterministic KJV Reading 2026 package from reviewed book deltas."""

import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
BOOKS = DIRECTION / "books"
PACKAGES = DIRECTION / "packages"
SOURCE = DIRECTION / "reading_2026.package-source.json"
PACKAGE = PACKAGES / "reading_2026.kjv.v1.package.json.gz"
MANIFEST = PACKAGES / "reading_2026.kjv.v1.manifest.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(value):
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


source = read(SOURCE)
previous_manifest = read(MANIFEST)
order = {entry["id"]: entry["order"] for entry in previous_manifest["books"]}
paths = {}
books = []

for path in BOOKS.glob("*_reading_2026.kjv.v1.json"):
    book = read(path)
    paths[book["book"]] = path
    books.append(book)

books.sort(key=lambda book: order[book["book"]])
if len(books) != source["expectedBookCount"]:
    raise SystemExit(f"Expected {source['expectedBookCount']} books, found {len(books)}")

payload = {
    "books": books,
    "contentVersion": source["contentVersion"],
    "editorialPolicy": source["editorialPolicy"],
    "filterId": source["filterId"],
    "format": "shine-reading-filter-package",
    "normalizationId": source["normalizationId"],
    "schemaVersion": source["schemaVersion"],
    "sourceCorpusSha256": source["sourceCorpusSha256"],
    "sourceVersionId": source["sourceVersionId"],
}
expanded = canonical(payload).encode("utf-8")
compressed = bytearray(gzip.compress(expanded, compresslevel=9, mtime=0))
# Keep identical bytes on Windows and Linux.
compressed[9] = 3
compressed = bytes(compressed)

coverage = {
    "expectedBookCount": source["expectedBookCount"],
    "includedBookCount": len(books),
    "changedVerseCount": sum(len(book["verses"]) for book in books),
    "editCount": sum(len(verse["edits"]) for book in books for verse in book["verses"]),
}
manifest = {
    "format": "shine-reading-filter-manifest",
    "filterId": source["filterId"],
    "schemaVersion": source["schemaVersion"],
    "contentVersion": source["contentVersion"],
    "sourceVersionId": source["sourceVersionId"],
    "sourceCorpusSha256": source["sourceCorpusSha256"],
    "normalizationId": source["normalizationId"],
    "contentSha256": sha256(compressed),
    "sizeBytes": len(compressed),
    "expandedSizeBytes": len(expanded),
    "mimeType": "application/vnd.shine.reading-filter+gzip",
    "generatedAt": source["generatedAt"],
    "editorialPolicy": source["editorialPolicy"],
    "coverage": coverage,
    "books": [
        {
            "id": book["book"],
            "order": order[book["book"]],
            "sourceFile": paths[book["book"]].name,
            "sourceContentSha256": book["sourceContentSha256"],
            "payloadSha256": sha256(canonical(book)),
            "changedVerseCount": len(book["verses"]),
            "editCount": sum(len(verse["edits"]) for verse in book["verses"]),
        }
        for book in books
    ],
}

PACKAGES.mkdir(parents=True, exist_ok=True)
PACKAGE.write_bytes(compressed)
MANIFEST.write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(json.dumps({
    "ok": True,
    "contentVersion": source["contentVersion"],
    "contentSha256": manifest["contentSha256"],
    "books": len(books),
    **coverage,
}, indent=2))
