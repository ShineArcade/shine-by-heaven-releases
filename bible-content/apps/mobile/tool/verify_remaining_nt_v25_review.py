import gzip
import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/rv1909/books"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction"
PACKAGE = DIRECTION / "packages/reading_2026.rv1909.v1.package.json.gz"
MANIFEST = DIRECTION / "packages/reading_2026.rv1909.v1.manifest.json"
SOURCE_CONFIG = DIRECTION / "reading_2026.package-source.json"
CHANGE_SET = ROOT / "editorial-changes/v25.json"
REGISTRY = ROOT / "editorial-review/registry.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render(source, edits):
    prior_end = -1
    for edit in sorted(edits, key=lambda item: item["startOffset"]):
        assert edit["startOffset"] >= prior_end, edit
        assert source[edit["startOffset"]:edit["endOffset"]] == edit["expected"], edit
        prior_end = edit["endOffset"]
    result = source
    for edit in sorted(edits, key=lambda item: item["startOffset"], reverse=True):
        result = result[:edit["startOffset"]] + edit["replacement"] + result[edit["endOffset"]:]
    return result


def whole(text, term):
    return re.search(rf"(?<![A-Za-z\u00c1\u00c9\u00cd\u00d3\u00da\u00dc\u00d1\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1]){re.escape(term)}(?![A-Za-z\u00c1\u00c9\u00cd\u00d3\u00da\u00dc\u00d1\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1])", text, re.IGNORECASE)


def main():
    spec = importlib.util.spec_from_file_location(
        "generator", Path(__file__).with_name("generate_v25_remaining_new_testament_review.py")
    )
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)

    sources = {}
    for path in CORPUS.glob("*.json"):
        doc = read(path)
        if doc["book"] not in generator.BOOK_NAMES:
            continue
        for chapter in doc["chapters"]:
            for verse in chapter["verses"]:
                sources[(doc["book"], chapter["chapter"], verse["verse"])] = verse["text"]
    assert len(sources) == 6208

    direction_docs = {}
    rendered = {}
    for path in DIRECTION.glob("*_reading_2026.rv1909.v1.json"):
        doc = read(path)
        if doc.get("book") not in generator.BOOK_NAMES:
            continue
        direction_docs[doc["book"]] = doc
        patches = {(item["chapter"], item["verse"]): item for item in doc.get("verses", [])}
        for (book, chapter, verse), source in sources.items():
            if book != doc["book"]:
                continue
            patch = patches.get((chapter, verse), {"edits": []})
            if patch["edits"]:
                assert patch["sourceTextSha256"] == hashlib.sha256(source.encode()).hexdigest()
            rendered[(book, chapter, verse)] = render(source, patch["edits"])
    assert len(direction_docs) == 25
    assert len(rendered) == 6208

    changes = read(CHANGE_SET)
    assert changes["contentVersion"] == 25
    assert len(changes["changes"]) == 337
    assert all(item.get("reason") and item.get("evidence") for item in changes["changes"])
    changed_books = {item["book"] for item in changes["changes"]}
    assert len(changed_books) == 23
    assert "MAT" not in changed_books and "MRK" not in changed_books
    for item in changes["changes"]:
        ref = (item["book"], item["chapter"], item["verse"])
        assert item["expected"] in sources[ref], (ref, item["expected"])
        assert item["replacement"] in rendered[ref], (ref, item["replacement"], rendered[ref])

    required = {
        ("1CO", 1, 25): "la debilidad de Dios",
        ("1CO", 9, 22): "a los d\u00e9biles, d\u00e9bil",
        ("2CO", 12, 9): "mi poder se perfecciona en la debilidad",
        ("ACT", 10, 1): "unidad militar llamada la Italiana",
        ("GAL", 2, 9): "la mano derecha en se\u00f1al de compa\u00f1erismo",
        ("LUK", 24, 17): "De qu\u00e9 convers\u00e1is",
        ("HEB", 13, 10): "no tienen derecho a comer",
        ("ROM", 5, 20): "la gracia abund\u00f3 mucho m\u00e1s",
        ("JAS", 5, 5): "para el d\u00eda de la matanza",
    }
    for ref, phrase in required.items():
        assert phrase in rendered[ref], (ref, phrase, rendered[ref])

    retired = (
        "flaco", "flaca", "flacos", "flaqueza", "flaquezas", "pl\u00e1ticas",
        "facultad", "cebado", "disoluciones", "sobrepuj\u00f3", "vituperado",
    )
    for ref, text in rendered.items():
        for term in retired:
            assert not whole(text, term), (ref, term, text)

    forbidden = (
        "la conocimiento", "toda conocimiento", "la amor", "el multitud",
        "los pasiones", "vuestra almas", "un ofrenda", "el persona",
        "la cautivos", "la campos", "\ufffd",
    )
    for ref, text in rendered.items():
        lowered = text.casefold()
        for phrase in forbidden:
            assert phrase.casefold() not in lowered, (ref, phrase, text)

    raw = PACKAGE.read_bytes()
    manifest = read(MANIFEST)
    source_config = read(SOURCE_CONFIG)
    assert manifest["contentVersion"] == 25
    assert source_config["contentVersion"] == 25
    assert manifest["contentSha256"] == hashlib.sha256(raw).hexdigest()
    assert manifest["sourceCorpusSha256"] == "af7a0acc03b228719b549539dcd0dcaca3c40af51a4b3d6c96f51ec8510ec739"
    assert manifest["coverage"] == {
        "expectedBookCount": 66,
        "includedBookCount": 66,
        "changedVerseCount": 7722,
        "editCount": 10011,
    }
    payload = json.loads(gzip.decompress(raw))
    assert payload["contentVersion"] == 25 and len(payload["books"]) == 66
    for book in changed_books:
        assert next(item for item in payload["books"] if item["book"] == book) == direction_docs[book]

    registry = read(REGISTRY)
    assert registry["activeChangeSet"] == "editorial-changes/v25.json"
    pending = [item for item in registry["pending"] if item["id"].startswith("nt-v25-")]
    assert len(pending) == 8
    assert all(item.get("reason") and item.get("references") and item.get("proposedOptions") for item in pending)
    assert all(ref["book"] in generator.BOOK_NAMES for item in pending for ref in item["references"])

    print(json.dumps({
        "contentVersion": 25,
        "verifiedSourceVerses": len(rendered),
        "reviewedRules": len(generator.RULES),
        "verifiedChanges": len(changes["changes"]),
        "changedBooks": len(changed_books),
        "pendingFamilies": len(pending),
        "contentSha256": manifest["contentSha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
