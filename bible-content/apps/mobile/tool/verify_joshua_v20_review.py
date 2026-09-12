import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    book = load(ROOT / "apps/mobile/assets/bibles/rv1909/books/JOS.json")
    layer = load(ROOT / "apps/mobile/assets/bible_direction/joshua_reading_2026.rv1909.v1.json")
    changes = load(ROOT / "editorial-changes/v20.json")
    registry = load(ROOT / "editorial-review/registry.json")
    config = load(ROOT / "apps/mobile/assets/bible_direction/reading_2026.package-source.json")
    source = {(c["chapter"], v["verse"]): v["text"] for c in book["chapters"] for v in c["verses"]}

    assert len(source) == 658
    assert changes["contentVersion"] == config["contentVersion"] == 20
    assert len(changes["changes"]) == 281
    assert len(changes["pendingReview"]) == 4
    assert layer["ownerReview"] == {"contentVersion": 20, "changeSet": "editorial-changes/v20.json", "appliedEditCount": 281}

    rendered = dict(source)
    indexed = {}
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
            indexed[(ref, edit["expected"], edit["replacement"])] = indexed.get((ref, edit["expected"], edit["replacement"]), 0) + 1
            text = text[:start] + edit["replacement"] + text[end:]
            prior = start
        rendered[ref] = text

    for change in changes["changes"]:
        ref = (change["chapter"], change["verse"])
        assert indexed.get((ref, change["expected"], change["replacement"])) == 1, change

    required = {
        (1, 2): "Moisés ha muerto",
        (2, 18): "cordón rojo",
        (4, 7): "servirán como recuerdo",
        (7, 14): "Os presentaréis",
        (9, 13): "los llenamos cuando eran nuevos",
        (17, 13): "trabajos forzados",
        (21, 41): "todas las ciudades",
        (22, 33): "el asunto agradó",
        (23, 8): "permaneceréis unidos",
        (24, 15): "escoged hoy",
    }
    for ref, phrase in required.items():
        assert phrase in rendered[ref], (ref, phrase, rendered[ref])

    stable_families = ["término", "términos", "heredad", "heredades", "morador", "moradores", "villa", "villas", "ejido", "ejidos", "ramera"]
    for term in stable_families:
        pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE)
        assert not any(pattern.search(text) for text in rendered.values()), term

    joined = "\n".join(rendered.values())
    for broken in [r"\bla ciudades\b", r"\blas ciudad\b", r"\bcampo de pastoreos\b", r"\bcampos de pastoreos\b", r"\bse se\b"]:
        assert re.search(broken, joined, re.IGNORECASE) is None, broken

    pending = [item for item in registry["pending"] if item.get("id", "").startswith("joshua-v20-")]
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
