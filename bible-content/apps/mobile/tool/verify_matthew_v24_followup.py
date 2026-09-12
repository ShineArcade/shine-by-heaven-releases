import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/rv1909/books/MAT.json"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/matthew_reading_2026.rv1909.v1.json"
PACKAGE = ROOT / "apps/mobile/assets/bible_direction/packages/reading_2026.rv1909.v1.package.json.gz"
MANIFEST = ROOT / "apps/mobile/assets/bible_direction/packages/reading_2026.rv1909.v1.manifest.json"
REGISTRY = ROOT / "editorial-review/registry.json"
CHANGE_SET = ROOT / "editorial-changes/v24.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render(source, edits):
    result = source
    prior_end = -1
    for edit in sorted(edits, key=lambda item: item["startOffset"]):
        assert edit["startOffset"] >= prior_end, edit
        assert source[edit["startOffset"]:edit["endOffset"]] == edit["expected"], edit
        prior_end = edit["endOffset"]
    for edit in sorted(edits, key=lambda item: item["startOffset"], reverse=True):
        result = result[:edit["startOffset"]] + edit["replacement"] + result[edit["endOffset"]:]
    return result


def main():
    spec = importlib.util.spec_from_file_location(
        "generator", Path(__file__).with_name("generate_v24_matthew_followup.py")
    )
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)

    source_doc = read(CORPUS)
    source = {
        (chapter["chapter"], verse["verse"]): verse["text"]
        for chapter in source_doc["chapters"]
        for verse in chapter["verses"]
    }
    direction = read(DIRECTION)
    assert direction["ownerReview"]["contentVersion"] == 22
    assert direction["followupReview"]["contentVersion"] == 24
    patches = {(item["chapter"], item["verse"]): item for item in direction["verses"]}
    rendered = {}
    for ref, text in source.items():
        patch = patches.get(ref, {"edits": []})
        if patch["edits"]:
            assert patch["sourceTextSha256"] == hashlib.sha256(text.encode()).hexdigest(), ref
        rendered[ref] = render(text, patch["edits"])
    assert len(rendered) == 1071

    change_set = read(CHANGE_SET)
    assert change_set["contentVersion"] == 24
    assert len(change_set["changes"]) == 16
    for item in change_set["changes"]:
        ref = (item["chapter"], item["verse"])
        assert item["expected"] in source[ref], (ref, item["expected"])
        assert item["replacement"] in rendered[ref], (ref, item["replacement"], rendered[ref])

    forbidden = (
        "había aparecido de la estrella",
        "el última moneda",
        "las saludos",
        "os insulten y os persiguieren",
        "la polilla y el óxido corrompe,",
        "ni polilla ni óxido corrompe,",
        "debajo de un recipiente, pero sobre",
        "no es muerta, pero duerme",
        "no te lo reveló carne ni sangre, pero mi Padre",
    )
    for ref, text in rendered.items():
        for phrase in forbidden:
            assert phrase not in text, (ref, phrase, text)

    raw = PACKAGE.read_bytes()
    manifest = read(MANIFEST)
    assert manifest["contentVersion"] == 24
    assert manifest["contentSha256"] == hashlib.sha256(raw).hexdigest()
    payload = json.loads(gzip.decompress(raw))
    assert payload["contentVersion"] == 24 and len(payload["books"]) == 66
    assert next(book for book in payload["books"] if book["book"] == "MAT") == direction

    registry = read(REGISTRY)
    assert registry["activeChangeSet"] == "editorial-changes/v24.json"
    print(json.dumps({
        "contentVersion": 24,
        "verifiedMatthewVerses": len(rendered),
        "followupCorrections": len(change_set["changes"]),
        "matthewChangedVerses": len(direction["verses"]),
        "matthewEdits": sum(len(item["edits"]) for item in direction["verses"]),
        "contentSha256": manifest["contentSha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
