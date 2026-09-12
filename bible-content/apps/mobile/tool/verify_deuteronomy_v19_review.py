import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    book = load(ROOT / "apps/mobile/assets/bibles/rv1909/books/DEU.json")
    layer = load(ROOT / "apps/mobile/assets/bible_direction/deuteronomy_reading_2026.rv1909.v1.json")
    changes = load(ROOT / "editorial-changes/v19.json")
    registry = load(ROOT / "editorial-review/registry.json")
    config = load(ROOT / "apps/mobile/assets/bible_direction/reading_2026.package-source.json")
    source = {(c["chapter"], v["verse"]): v["text"] for c in book["chapters"] for v in c["verses"]}

    assert len(source) == 959
    assert changes["contentVersion"] == config["contentVersion"] == 19
    assert len(changes["changes"]) == 66
    assert len(changes["pendingReview"]) == 4
    assert layer["ownerReview"] == {"contentVersion": 19, "changeSet": "editorial-changes/v19.json", "appliedEditCount": 66}

    rendered = dict(source)
    spans = set()
    for patch in layer["verses"]:
        ref = (patch["chapter"], patch["verse"])
        text = source[ref]
        assert patch["sourceTextSha256"] == hashlib.sha256(text.encode()).hexdigest()
        prior = len(text) + 1
        for edit in sorted(patch["edits"], key=lambda value: value["startOffset"], reverse=True):
            start, end = edit["startOffset"], edit["endOffset"]
            assert 0 <= start < end <= len(text)
            assert end <= prior
            assert text[start:end] == edit["expected"]
            assert (*ref, start, end) not in spans
            spans.add((*ref, start, end))
            text = text[:start] + edit["replacement"] + text[end:]
            prior = start
        rendered[ref] = text

    required = {
        (2, 3): ["Bastante habéis rodeado", "norte"],
        (4, 21): ["por causa de vosotros"],
        (8, 2): ["te acordarás"],
        (17, 8): ["una clase de homicidio"],
        (19, 5): ["hierro del mango", "golpeó a su prójimo"],
        (26, 17): ["declarado solemnemente"],
        (30, 12): ["hará oír"],
        (31, 29): ["os apartaréis", "últimos días"],
        (33, 21): ["mejor parte", "ejecutó la justicia"],
    }
    for ref, phrases in required.items():
        for phrase in phrases:
            assert phrase in rendered[ref], (ref, phrase, rendered[ref])

    pending = [item for item in registry["pending"] if item.get("id", "").startswith("deuteronomy-v19-")]
    assert len(pending) == 4
    print(json.dumps({
        "ok": True,
        "sourceVerses": len(source),
        "newChanges": len(changes["changes"]),
        "totalChangedVerses": len(layer["verses"]),
        "totalEdits": sum(len(v["edits"]) for v in layer["verses"]),
        "pending": len(pending),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
