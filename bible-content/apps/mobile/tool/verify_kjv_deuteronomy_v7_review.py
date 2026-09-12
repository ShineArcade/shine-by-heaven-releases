import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    book = load(ROOT / "apps/mobile/assets/bibles/kjv/books/DEU.json")
    layer = load(ROOT / "apps/mobile/assets/bible_direction/kjv/books/deu_reading_2026.kjv.v1.json")
    registry = load(ROOT / "editorial-review/registry.kjv.json")
    config = load(ROOT / "apps/mobile/assets/bible_direction/kjv/reading_2026.package-source.json")
    source = {(c["chapter"], v["verse"]): v["text"] for c in book["chapters"] for v in c["verses"]}
    assert len(source) == 959
    assert config["contentVersion"] == 7
    assert layer["ownerReview"] == {"contentVersion": 7, "review": "KJV Deuteronomy complete-context review", "requiredFullTest": True}

    rendered = dict(source)
    spans = set()
    for patch in layer["verses"]:
        ref = (patch["chapter"], patch["verse"])
        text = source[ref]
        assert patch["sourceTextSha256"] == hashlib.sha256(text.encode()).hexdigest()
        previous = len(text) + 1
        for edit in sorted(patch["edits"], key=lambda item: item["startOffset"], reverse=True):
            start, end = edit["startOffset"], edit["endOffset"]
            assert 0 <= start < end <= len(text)
            assert end <= previous
            assert text[start:end] == edit["expected"]
            assert (*ref, start, end) not in spans
            spans.add((*ref, start, end))
            text = text[:start] + edit["replacement"] + text[end:]
            previous = start
        rendered[ref] = text

    required = {
        (1, 7): ["near it"],
        (7, 5): ["Asherah poles"],
        (10, 17): ["awe-inspiring", "accepts bribes"],
        (14, 2): ["special possession"],
        (19, 4): ["unintentionally"],
        (22, 8): ["parapet", "fall from there"],
        (23, 13): ["digging tool", "relievest thyself"],
        (28, 31): ["thy donkey", "eat of it"],
        (31, 16): ["be unfaithful"],
        (32, 18): ["gave thee birth"],
    }
    for ref, phrases in required.items():
        for phrase in phrases:
            assert phrase in rendered[ref], (ref, phrase, rendered[ref])
    all_text = "\n".join(rendered.values())
    for forbidden in ["thine donkey", "near thereunto", "street of it", "shaltmake", "rooff"]:
        assert forbidden not in all_text, forbidden

    pending = [item for item in registry["pending"] if item.get("id", "").startswith("deuteronomy-kjv-v7-")]
    assert len(pending) == 4
    print(json.dumps({"ok": True, "sourceVerses": 959, "changedVerses": len(layer["verses"]), "edits": sum(len(v["edits"]) for v in layer["verses"]), "pending": len(pending)}, indent=2))


if __name__ == "__main__":
    main()
