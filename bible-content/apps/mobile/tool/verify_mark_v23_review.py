import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/rv1909/books/MRK.json"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/mark_reading_2026.rv1909.v1.json"
PACKAGE = ROOT / "apps/mobile/assets/bible_direction/packages/reading_2026.rv1909.v1.package.json.gz"
MANIFEST = ROOT / "apps/mobile/assets/bible_direction/packages/reading_2026.rv1909.v1.manifest.json"
REGISTRY = ROOT / "editorial-review/registry.json"
CHANGE_SET = ROOT / "editorial-changes/v23.json"


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
    source_doc = read(CORPUS)
    source = {(c["chapter"], v["verse"]): v["text"] for c in source_doc["chapters"] for v in c["verses"]}
    direction = read(DIRECTION)
    patches = {(v["chapter"], v["verse"]): v for v in direction["verses"]}
    rendered = {}
    for ref, text in source.items():
        patch = patches.get(ref, {"edits": []})
        if patch["edits"]:
            assert patch["sourceTextSha256"] == hashlib.sha256(text.encode()).hexdigest(), ref
        rendered[ref] = render(text, patch["edits"])
    assert len(rendered) == 678

    changes = read(CHANGE_SET)
    assert changes["contentVersion"] == 23 and len(changes["changes"]) == 297
    for item in changes["changes"]:
        ref = (item["chapter"], item["verse"])
        assert item["expected"] in source[ref], (ref, item["expected"])
        assert item["replacement"] in rendered[ref], (ref, item["replacement"], rendered[ref])

    expected = {
        (1, 26): "lo convulsionó",
        (6, 2): "milagros realizados por sus manos",
        (8, 31): "fuera muerto y resucitara",
        (12, 37): "¿cómo, pues, es su hijo?",
        (12, 44): "todo lo que tenía para vivir",
        (14, 27): "serán dispersadas las ovejas",
        (16, 18): "Tomarán serpientes en sus manos",
    }
    for ref, phrase in expected.items():
        assert phrase in rendered[ref], (ref, phrase, rendered[ref])

    forbidden = (
        "haciendo pedazos", "milagros que por sus manos son hechas", "y ser muerto",
        "¿de dónde, pues, es su hijo?", "todo lo que tenía, todo lo que tenía",
        "serán derramadas las ovejas", "Quitarán serpientes",
    )
    for ref, text in rendered.items():
        for phrase in forbidden:
            assert phrase not in text, (ref, phrase, text)

    raw = PACKAGE.read_bytes()
    manifest = read(MANIFEST)
    # Mark keeps its v23 owner review when a later book advances the
    # package-wide content version.
    assert manifest["contentVersion"] >= 23
    assert manifest["contentSha256"] == hashlib.sha256(raw).hexdigest()
    payload = json.loads(gzip.decompress(raw))
    assert payload["contentVersion"] == manifest["contentVersion"] and len(payload["books"]) == 66
    assert next(book for book in payload["books"] if book["book"] == "MRK") == direction

    registry = read(REGISTRY)
    assert registry["activeChangeSet"].startswith("editorial-changes/v")
    pending = [x for x in registry["pending"] if x["id"].startswith("mark-v23-")]
    assert len(pending) == 14
    assert all(x["reason"] and x["references"] and x["evidence"] for x in pending)
    print(json.dumps({
        "markReviewVersion": 23,
        "packageContentVersion": manifest["contentVersion"],
        "verifiedMarkVerses": len(rendered),
        "verifiedChanges": len(changes["changes"]),
        "markChangedVerses": len(direction["verses"]),
        "markEdits": sum(len(v["edits"]) for v in direction["verses"]),
        "pendingFamilies": len(pending),
        "contentSha256": manifest["contentSha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
