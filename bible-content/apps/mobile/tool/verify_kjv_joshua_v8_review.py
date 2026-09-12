import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    book = load(ROOT / "apps/mobile/assets/bibles/kjv/books/JOS.json")
    layer = load(ROOT / "apps/mobile/assets/bible_direction/kjv/books/jos_reading_2026.kjv.v1.json")
    manifest = load(ROOT / "apps/mobile/assets/bible_direction/kjv/packages/reading_2026.kjv.v1.manifest.json")
    registry = load(ROOT / "editorial-review/registry.kjv.json")
    source = {(c["chapter"], v["verse"]): v["text"] for c in book["chapters"] for v in c["verses"]}
    assert len(source) == 658
    assert manifest["contentVersion"] == registry["activeContentVersion"] == 8
    assert layer["ownerReview"] == {"contentVersion": 8, "review": "KJV Joshua complete-context review", "requiredFullTest": True}

    rendered = dict(source)
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
            text = text[:start] + edit["replacement"] + text[end:]
            prior = start
        rendered[ref] = text

    required = {
        (5, 11): ["old grain", "parched grain"],
        (6, 9): ["rear guard"],
        (7, 5): ["killed about thirty-six", "therefore the hearts"],
        (9, 22): ["Why have ye deceived us"],
        (10, 10): ["threw them into confusion", "as far as Azekah"],
        (14, 10): ["eighty-five years old"],
        (18, 5): ["territory on the south", "territory on the north"],
        (20, 5): ["killed his neighbour unintentionally"],
        (22, 23): ["grain offering"],
    }
    for ref, phrases in required.items():
        for phrase in phrases:
            assert phrase in rendered[ref], (ref, phrase, rendered[ref])

    retired = "nigh thence whence whither thither wherein wherewith thereof therein thereon hither hence hitherto peradventure bade slew waxed ass asses victuals raiment harlot coast coasts goodly reproach rereward midst dwelt abode unwittingly suburbs nether beforetime uttermost morrow corn meat smote discomfited".split()
    joined = "\n".join(rendered.values())
    for term in retired:
        assert re.search(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", joined, re.IGNORECASE) is None, term
    for broken in [r"\bfrom from\b", r"\bin in\b", r"\bof of\b", r"\bon on\b", r"\bto to\b"]:
        assert re.search(broken, joined, re.IGNORECASE) is None, broken

    pending = [item for item in registry["pending"] if item.get("id", "").startswith("joshua-kjv-v8-")]
    assert len(pending) == 4
    assert len(layer["verses"]) == 223
    assert sum(len(v["edits"]) for v in layer["verses"]) == 337
    print(json.dumps({"ok": True, "sourceVerses": len(source), "changedVerses": len(layer["verses"]), "edits": 337, "pending": 4}, indent=2))


if __name__ == "__main__":
    main()
