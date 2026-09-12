import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK_PATH = ROOT / "apps/mobile/assets/bibles/rv1909/books/NUM.json"
LAYER_PATH = ROOT / "apps/mobile/assets/bible_direction/numbers_reading_2026.rv1909.v1.json"
CHANGE_SET_PATH = ROOT / "editorial-changes/v18.json"
REGISTRY_PATH = ROOT / "editorial-review/registry.json"
SOURCE_CONFIG_PATH = ROOT / "apps/mobile/assets/bible_direction/reading_2026.package-source.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    book = load(BOOK_PATH)
    layer = load(LAYER_PATH)
    change_set = load(CHANGE_SET_PATH)
    registry = load(REGISTRY_PATH)
    source_config = load(SOURCE_CONFIG_PATH)
    source = {
        (chapter["chapter"], verse["verse"]): verse["text"]
        for chapter in book["chapters"]
        for verse in chapter["verses"]
    }
    assert len(source) == 1288
    assert change_set["contentVersion"] == 18
    assert len(change_set["changes"]) == 833
    assert len(change_set["pendingReview"]) == 61
    assert source_config["contentVersion"] == 18
    assert layer["ownerReview"] == {
        "contentVersion": 18,
        "changeSet": "editorial-changes/v18.json",
        "appliedEditCount": 833,
    }

    new_keys = set()
    for change in change_set["changes"]:
        ref = (change["chapter"], change["verse"])
        assert change["book"] == "NUM"
        assert ref in source
        assert source[ref].count(change["expected"]) == 1, (ref, change["expected"])
        assert change["expected"] != change["replacement"]
        assert change["reason"].strip()
        assert len(change["evidence"]) >= 2
        key = (*ref, change["expected"])
        assert key not in new_keys, key
        new_keys.add(key)

    rendered = dict(source)
    all_spans = set()
    for verse in layer["verses"]:
        ref = (verse["chapter"], verse["verse"])
        text = source[ref]
        source_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert verse["sourceTextSha256"] == source_hash
        prior_start = len(text) + 1
        for edit in sorted(verse["edits"], key=lambda value: value["startOffset"], reverse=True):
            start, end = edit["startOffset"], edit["endOffset"]
            assert 0 <= start < end <= len(text)
            assert end <= prior_start, (ref, start, end, prior_start)
            assert text[start:end] == edit["expected"], (ref, edit["expected"], text[start:end])
            assert (*ref, start, end) not in all_spans
            all_spans.add((*ref, start, end))
            text = text[:start] + edit["replacement"] + text[end:]
            prior_start = start
        rendered[ref] = text

    required = {
        (1, 2): ["Haced el censo", "individualmente"],
        (10, 10): ["servirán de memorial"],
        (14, 25): ["en dirección al mar Rojo"],
        (16, 6): ["tomad incensarios"],
        (25, 17): ["Tratad como enemigos"],
        (33, 3): ["De Rameses partieron"],
        (35, 30): ["un solo testigo no bastará"],
        (36, 6): ["con quien ellas prefieran"],
    }
    forbidden = [
        "Hagan el censo",
        "den el toque de avance",
        "tomen incensarios",
        "Traten como enemigos",
    ]
    for ref, phrases in required.items():
        for phrase in phrases:
            assert phrase in rendered[ref], (ref, phrase, rendered[ref])
    numbers_text = "\n".join(rendered.values())
    for phrase in forbidden:
        assert phrase not in numbers_text, phrase
    assert "camino del mar Rojo" not in rendered[(14, 25)]

    pending = [
        item for item in registry["pending"]
        if item.get("id", "").startswith("numbers-v18-")
    ]
    assert len(pending) == 61
    assert registry["activeChangeSet"] == "editorial-changes/v18.json"
    print(json.dumps({
        "ok": True,
        "sourceVerses": len(source),
        "newEdits": len(change_set["changes"]),
        "totalNumbersEdits": sum(len(value["edits"]) for value in layer["verses"]),
        "pendingReview": len(pending),
        "renderedSpotChecks": sum(len(value) for value in required.values()),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
