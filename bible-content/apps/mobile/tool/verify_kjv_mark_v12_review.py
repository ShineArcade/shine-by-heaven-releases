import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv/books/MRK.json"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv/books/mrk_reading_2026.kjv.v1.json"
PACKAGE = ROOT / "apps/mobile/assets/bible_direction/kjv/packages/reading_2026.kjv.v1.package.json.gz"
MANIFEST = ROOT / "apps/mobile/assets/bible_direction/kjv/packages/reading_2026.kjv.v1.manifest.json"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"


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


def main():
    spec = importlib.util.spec_from_file_location(
        "generator", Path(__file__).with_name("generate_kjv_v12_mark_review.py")
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
    assert direction["ownerReview"]["contentVersion"] == 12
    patches = {(item["chapter"], item["verse"]): item for item in direction["verses"]}
    rendered = {}
    for ref, text in source.items():
        patch = patches.get(ref, {"edits": []})
        if patch["edits"]:
            assert patch["sourceTextSha256"] == hashlib.sha256(text.encode()).hexdigest(), ref
        rendered[ref] = render(text, patch["edits"])
    assert len(rendered) == 678

    for chapter, verse, expected, replacement, *_ in generator.CHANGES:
        ref = (chapter, verse)
        assert expected in source[ref], (ref, expected)
        assert replacement in rendered[ref], (ref, replacement, rendered[ref])

    required = {
        (1, 26): "had convulsed him",
        (2, 12): "never seen anything like this",
        (5, 13): "drowned in the sea",
        (7, 19): "passes out of the body",
        (9, 42): "who believe in me to stumble",
        (10, 48): "cried out all the more",
        (12, 44): "all she had to live on",
        (15, 39): "saw how he cried out and died",
        (16, 17): "signs shall accompany those who believe",
    }
    for ref, phrase in required.items():
        assert phrase in rendered[ref], (ref, phrase, rendered[ref])

    forbidden = (
        "never saw it anything",
        "cast the demon out out",
        "How difficult it is for shall they",
        "leave out of their region",
        "daughter laid upon the bed",
        "all she had even all she had",
        "that he so cried out, and died",
        "were choked in the sea",
        "one of these little ones to stumble that believe",
        "he cried the more a great deal",
        "began to cast out them",
    )
    for ref, text in rendered.items():
        for phrase in forbidden:
            assert phrase not in text, (ref, phrase, text)

    raw = PACKAGE.read_bytes()
    manifest = read(MANIFEST)
    assert manifest["contentVersion"] >= 12
    assert manifest["contentSha256"] == hashlib.sha256(raw).hexdigest()
    assert manifest["coverage"]["expectedBookCount"] == 66
    assert manifest["coverage"]["includedBookCount"] == 66
    payload = json.loads(gzip.decompress(raw))
    assert payload["contentVersion"] == manifest["contentVersion"] and len(payload["books"]) == 66
    assert next(book for book in payload["books"] if book["book"] == "MRK") == direction

    registry = read(REGISTRY)
    assert registry["activeContentVersion"] == manifest["contentVersion"]
    applied = {
        (item["reference"], item["expected"], item["replacement"])
        for item in registry["applied"]
    }
    for chapter, verse, expected, replacement, *_ in generator.CHANGES:
        assert (f"MRK.{chapter}.{verse}", expected, replacement) in applied
    pending = [item for item in registry["pending"] if item["id"].startswith("mark-kjv-v12-")]
    assert len(pending) == 12
    assert all(item["reason"] and item["references"] and item["evidence"] for item in pending)

    print(json.dumps({
        "markReviewVersion": 12,
        "packageContentVersion": manifest["contentVersion"],
        "verifiedMarkVerses": len(rendered),
        "reviewedRules": len(generator.CHANGES),
        "markChangedVerses": len(direction["verses"]),
        "markEdits": sum(len(item["edits"]) for item in direction["verses"]),
        "pendingFamilies": len(pending),
        "contentSha256": manifest["contentSha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
