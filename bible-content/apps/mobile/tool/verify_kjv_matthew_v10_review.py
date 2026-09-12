import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv/books/MAT.json"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv/books/mat_reading_2026.kjv.v1.json"
PACKAGE = ROOT / "apps/mobile/assets/bible_direction/kjv/packages/reading_2026.kjv.v1.package.json.gz"
MANIFEST = ROOT / "apps/mobile/assets/bible_direction/kjv/packages/reading_2026.kjv.v1.manifest.json"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render(source, edits):
    prior_end = -1
    for edit in sorted(edits, key=lambda e: e["startOffset"]):
        assert edit["startOffset"] >= prior_end, edit
        assert source[edit["startOffset"]:edit["endOffset"]] == edit["expected"], edit
        prior_end = edit["endOffset"]
    result = source
    for edit in sorted(edits, key=lambda e: e["startOffset"], reverse=True):
        result = result[:edit["startOffset"]] + edit["replacement"] + result[edit["endOffset"]:]
    return result


def main():
    spec = importlib.util.spec_from_file_location("generator", Path(__file__).with_name("generate_kjv_v10_matthew_review.py"))
    generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
    source_doc = read(CORPUS)
    source = {(c["chapter"], v["verse"]): v["text"] for c in source_doc["chapters"] for v in c["verses"]}
    direction = read(DIRECTION)
    assert direction["ownerReview"]["contentVersion"] == 10
    patches = {(v["chapter"], v["verse"]): v for v in direction["verses"]}
    rendered = {}
    for ref, text in source.items():
        patch = patches.get(ref, {"edits": []})
        if patch["edits"]:
            assert patch["sourceTextSha256"] == hashlib.sha256(text.encode()).hexdigest(), ref
        rendered[ref] = render(text, patch["edits"])
    assert len(rendered) == 1071

    for chapter, verse, expected, replacement, *_ in generator.CHANGES:
        assert expected in source[(chapter, verse)], (chapter, verse, expected)
        assert replacement in rendered[(chapter, verse)], (chapter, verse, replacement, rendered[(chapter, verse)])

    forbidden = ("the its", "from from here", "is grew", "old bottles", "lost his savour", "strain at a gnat", "yielded up the ghost")
    for ref, text in rendered.items():
        for phrase in forbidden:
            assert phrase not in text, (ref, phrase, text)

    raw = PACKAGE.read_bytes(); manifest = read(MANIFEST)
    # Matthew keeps its v10 owner review when a later book advances the
    # package-wide content version.
    assert manifest["contentVersion"] >= 10
    assert manifest["contentSha256"] == hashlib.sha256(raw).hexdigest()
    payload = json.loads(gzip.decompress(raw))
    assert payload["contentVersion"] == manifest["contentVersion"] and len(payload["books"]) == 66
    package_mat = next(book for book in payload["books"] if book["book"] == "MAT")
    assert package_mat == direction

    registry = read(REGISTRY)
    assert registry["activeContentVersion"] == manifest["contentVersion"]
    applied = {(x["reference"], x["expected"], x["replacement"]) for x in registry["applied"]}
    for chapter, verse, expected, replacement, *_ in generator.CHANGES:
        assert (f"MAT.{chapter}.{verse}", expected, replacement) in applied
    pending = [x for x in registry["pending"] if x["id"].startswith("matthew-kjv-v10-")]
    assert len(pending) == len(generator.PENDING)
    assert all(x["reason"] and x["references"] and x["evidence"] for x in pending)
    print(json.dumps({"matthewReviewVersion": 10, "packageContentVersion": manifest["contentVersion"], "verifiedMatthewVerses": len(rendered), "reviewedRules": len(generator.CHANGES), "matthewChangedVerses": len(direction["verses"]), "matthewEdits": sum(len(v["edits"]) for v in direction["verses"]), "pendingFamilies": len(pending), "contentSha256": manifest["contentSha256"]}, indent=2))


if __name__ == "__main__":
    main()
