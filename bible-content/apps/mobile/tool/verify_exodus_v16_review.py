import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK_PATH = ROOT / "apps/mobile/assets/bibles/rv1909/books/EXO.json"
LAYER_PATH = ROOT / "apps/mobile/assets/bible_direction/exodus_reading_2026.rv1909.v1.json"
CHANGE_SET_PATH = ROOT / "editorial-changes/v16.json"


def verse_map(document):
    return {
        (chapter["chapter"], verse["verse"]): verse["text"]
        for chapter in document["chapters"]
        for verse in chapter["verses"]
    }


def render(text, edits):
    for edit in sorted(edits, key=lambda item: item["startOffset"], reverse=True):
        text = text[: edit["startOffset"]] + edit["replacement"] + text[edit["endOffset"] :]
    return text


def main():
    source = verse_map(json.loads(BOOK_PATH.read_text(encoding="utf-8")))
    layer = json.loads(LAYER_PATH.read_text(encoding="utf-8"))
    change_set = json.loads(CHANGE_SET_PATH.read_text(encoding="utf-8"))
    assert layer["ownerReview"]["contentVersion"] == change_set["contentVersion"] == 16

    patches = {(item["chapter"], item["verse"]): item for item in layer["verses"]}
    counts = Counter()
    reviewed = set()
    for change in change_set["changes"]:
        ref = (change["chapter"], change["verse"])
        reviewed.add(ref)
        source_text = source[ref]
        patch = patches[ref]
        assert patch["sourceTextSha256"] == hashlib.sha256(source_text.encode("utf-8")).hexdigest(), ref
        matches = [
            edit for edit in patch["edits"]
            if edit["expected"] == change["expected"]
            and edit["replacement"] == change["replacement"]
            and edit["category"] == change["category"]
            and edit["reason"] == change["reason"]
        ]
        assert len(matches) == 1, (ref, change["expected"], len(matches))
        edit = matches[0]
        assert source_text[edit["startOffset"]:edit["endOffset"]] == change["expected"], (ref, change["expected"])
        rendered = render(source_text, patch["edits"])
        assert change["replacement"] in rendered, (ref, change["replacement"])
        forbidden = ("la lóbulo", "una hojaldre", "el cortina", "del cortina")
        assert not any(fragment in rendered for fragment in forbidden), ref
        assert not re.search(r"\bque\s+que\b", rendered, re.IGNORECASE), ref
        assert "  " not in rendered and ".." not in rendered, ref
        counts[change["category"]] += 1

    pending_refs = {
        (item["chapter"], item["verse"])
        for item in change_set.get("pendingReview", [])
    }
    assert len(change_set["changes"]) == 605
    assert len(reviewed) >= 200
    assert len(pending_refs) == 10
    print(json.dumps({
        "ok": True,
        "contentVersion": 16,
        "verifiedEdits": len(change_set["changes"]),
        "reviewedVerses": len(reviewed),
        "pendingPassages": len(pending_refs),
        "categories": dict(sorted(counts.items())),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
