import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION_ROOT = ROOT / "apps/mobile/assets/bible_direction/kjv"
BOOK_ROOT = DIRECTION_ROOT / "books"
PACKAGE_ROOT = DIRECTION_ROOT / "packages"
PACKAGE_PATH = PACKAGE_ROOT / "reading_2026.kjv.v1.package.json.gz"
MANIFEST_PATH = PACKAGE_ROOT / "reading_2026.kjv.v1.manifest.json"
PACKAGE_SOURCE_PATH = DIRECTION_ROOT / "reading_2026.package-source.json"
REGISTRY_PATH = ROOT / "editorial-review/registry.kjv.json"
VERSION = 11


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, compact=False):
    separators = (",", ":") if compact else None
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=None if compact else 2, separators=separators) + "\n",
        encoding="utf-8",
    )


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(value):
    return hashlib.sha256(value).hexdigest()


def source_book_payload(book):
    return {
        "book": book["book"],
        "name": book["name"],
        "order": book["order"],
        "chapters": [
            {
                "chapter": chapter["chapter"],
                "verses": [
                    {"verse": verse["verse"], "text": verse["text"]}
                    for verse in chapter["verses"]
                ],
            }
            for chapter in book["chapters"]
        ],
    }


def locate_edits(text, edits, reference):
    claimed = set()
    repaired = []
    for edit in sorted(edits, key=lambda item: item["startOffset"]):
        expected = edit["expected"]
        candidates = []
        cursor = 0
        while True:
            found = text.find(expected, cursor)
            if found < 0:
                break
            span = (found, found + len(expected))
            if span not in claimed:
                candidates.append(span)
            cursor = found + 1
        if not candidates:
            raise RuntimeError(f"{reference}: expected text not found: {expected!r}")
        start, end = min(candidates, key=lambda span: abs(span[0] - edit["startOffset"]))
        claimed.add((start, end))
        repaired.append({**edit, "startOffset": start, "endOffset": end})
    repaired.sort(key=lambda item: item["startOffset"])
    for left, right in zip(repaired, repaired[1:]):
        if right["startOffset"] < left["endOffset"]:
            raise RuntimeError(f"{reference}: repaired edits overlap")
    return repaired


def main():
    package = json.loads(gzip.decompress(PACKAGE_PATH.read_bytes()).decode("utf-8"))
    source_books = {
        path.stem: read(path)
        for path in sorted((SOURCE_ROOT / "books").glob("*.json"))
    }
    direction_paths = {
        read(path)["book"]: path
        for path in sorted(BOOK_ROOT.glob("*_reading_2026.kjv.v1.json"))
    }
    if len(source_books) != 66 or len(direction_paths) != 66 or len(package["books"]) != 66:
        raise RuntimeError("KJV source and direction must contain exactly 66 books")

    repaired_hashes = 0
    repaired_offsets = 0
    direction_books = []
    for direction in package["books"]:
        code = direction["book"]
        source = source_books[code]
        direction_changed = False
        source_hash = sha(
            json.dumps(
                source_book_payload(source),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        if direction["sourceContentSha256"] != source_hash:
            repaired_hashes += 1
            direction_changed = True
        direction["sourceContentSha256"] = source_hash
        verse_index = {
            (chapter["chapter"], verse["verse"]): verse["text"]
            for chapter in source["chapters"]
            for verse in chapter["verses"]
        }
        for verse in direction["verses"]:
            reference = f"{code}.{verse['chapter']}.{verse['verse']}"
            text = verse_index[(verse["chapter"], verse["verse"])]
            actual_hash = sha(text.encode("utf-8"))
            if verse["sourceTextSha256"] != actual_hash:
                repaired_hashes += 1
                direction_changed = True
            verse["sourceTextSha256"] = actual_hash
            repaired = locate_edits(text, verse["edits"], reference)
            offset_changes = sum(
                before["startOffset"] != after["startOffset"]
                or before["endOffset"] != after["endOffset"]
                for before, after in zip(sorted(verse["edits"], key=lambda item: item["startOffset"]), repaired)
            )
            repaired_offsets += offset_changes
            direction_changed = direction_changed or offset_changes > 0
            verse["edits"] = repaired
        if direction_changed:
            preserve_compact = direction_paths[code].read_text(encoding="utf-8").count("\n") <= 2
            write(direction_paths[code], direction, compact=preserve_compact)
        direction_books.append(direction)

    package["contentVersion"] = VERSION
    package["editorialPolicy"] = {
        **package["editorialPolicy"],
        "version": VERSION,
    }
    raw = (canonical(package) + "\n").encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    PACKAGE_PATH.write_bytes(compressed)

    manifest = read(MANIFEST_PATH)
    manifest["contentVersion"] = VERSION
    manifest["contentSha256"] = sha(compressed)
    manifest["sizeBytes"] = len(compressed)
    manifest["expandedSizeBytes"] = len(raw)
    manifest["generatedAt"] = "2026-09-12"
    manifest["editorialPolicy"] = {
        **manifest["editorialPolicy"],
        "version": VERSION,
    }
    by_code = {book["book"]: book for book in direction_books}
    for entry in manifest["books"]:
        direction = by_code[entry["id"]]
        entry["sourceContentSha256"] = direction["sourceContentSha256"]
        entry["payloadSha256"] = sha(canonical(direction).encode("utf-8"))
        entry["changedVerseCount"] = len(direction["verses"])
        entry["editCount"] = sum(len(verse["edits"]) for verse in direction["verses"])
    write(MANIFEST_PATH, manifest)

    package_source = read(PACKAGE_SOURCE_PATH)
    package_source["contentVersion"] = VERSION
    package_source["generatedAt"] = "2026-09-12T13:00:00.000Z"
    package_source["editorialPolicy"] = {
        **package_source["editorialPolicy"],
        "version": VERSION,
    }
    write(PACKAGE_SOURCE_PATH, package_source)

    registry = read(REGISTRY_PATH)
    registry["activeContentVersion"] = VERSION
    registry["updatedAt"] = "2026-09-12T13:00:00.000Z"
    write(REGISTRY_PATH, registry)

    print(json.dumps({
        "ok": True,
        "contentVersion": VERSION,
        "repairedHashes": repaired_hashes,
        "repairedOffsets": repaired_offsets,
        "contentSha256": manifest["contentSha256"],
        "editCount": manifest["coverage"]["editCount"],
    }, indent=2))


if __name__ == "__main__":
    main()
