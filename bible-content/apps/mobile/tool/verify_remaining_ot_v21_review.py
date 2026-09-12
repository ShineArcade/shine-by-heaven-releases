import gzip
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK_ROOT = ROOT / "apps/mobile/assets/bibles/rv1909/books"
PACKAGE = ROOT / "apps/mobile/assets/bible_direction/packages/reading_2026.rv1909.v1.package.json.gz"
MANIFEST = ROOT / "apps/mobile/assets/bible_direction/packages/reading_2026.rv1909.v1.manifest.json"
REGISTRY = ROOT / "editorial-review/registry.json"
CHANGE_SET = ROOT / "editorial-changes/v21.json"
REVIEWED = {"GEN", "EXO", "LEV", "NUM", "DEU", "JOS"}
RETIRED = [
    "aqueste", "empero", "morador", "moradores", "aquilón", "saeta", "saetas",
    "aljaba", "aljabas", "villa", "villas", "ejido", "ejidos", "ramera", "rameras",
    "mancebo", "mancebos", "oprobio", "oprobios", "escarnio", "escarnios",
    "escarnecedor", "escarnecedores",
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def whole(text, term):
    return re.search(rf"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ]){re.escape(term)}(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])", text, re.IGNORECASE)


def main():
    raw = PACKAGE.read_bytes()
    manifest = read(MANIFEST)
    assert manifest["contentVersion"] == 21
    assert manifest["contentSha256"] == hashlib.sha256(raw).hexdigest()
    payload = json.loads(gzip.decompress(raw))
    assert payload["contentVersion"] == 21
    assert len(payload["books"]) == 66
    change_set = read(CHANGE_SET)
    assert len(change_set["changes"]) == 567

    rendered = {}
    for book_patch in payload["books"][:39]:
        book = book_patch["book"]
        source = read(BOOK_ROOT / f"{book}.json")
        source_verses = {(c["chapter"], v["verse"]): v["text"] for c in source["chapters"] for v in c["verses"]}
        patches = {(v["chapter"], v["verse"]): v["edits"] for v in book_patch.get("verses", [])}
        for ref, source_text in source_verses.items():
            text = source_text
            for edit in sorted(patches.get(ref, []), key=lambda item: item["startOffset"], reverse=True):
                assert source_text[edit["startOffset"]:edit["endOffset"]] == edit["expected"]
                text = text[:edit["startOffset"]] + edit["replacement"] + text[edit["endOffset"]:]
            rendered[(book, *ref)] = text

    for (book, chapter, verse), text in rendered.items():
        if book in REVIEWED:
            continue
        for term in RETIRED:
            assert not whole(text, term), (book, chapter, verse, term, text)

    required = {
        ("2CH", 35, 15): "no era necesario que se apartasen",
        ("EZR", 7, 20): "necesites dar",
        ("JOB", 30, 2): "para qué necesitaría",
        ("PRO", 30, 8): "pan que necesito",
        ("JER", 49, 9): "tomarán lo que necesiten",
        ("JER", 6, 14): "superficialmente",
        ("JER", 8, 11): "superficialmente",
    }
    for reference, phrase in required.items():
        assert phrase in rendered[reference], (reference, rendered[reference])

    registry = read(REGISTRY)
    assert registry["activeChangeSet"] == "editorial-changes/v21.json"
    pending = [item for item in registry["pending"] if item["id"].startswith("ot-completion-v21-")]
    assert len(pending) == 14
    assert all(item["reason"] and item["references"] for item in pending)
    print(json.dumps({
        "contentVersion": 21,
        "verifiedChanges": len(change_set["changes"]),
        "verifiedSourceVerses": len(rendered),
        "retiredFamilies": len(RETIRED),
        "pendingFamilies": len(pending),
        "contentSha256": manifest["contentSha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
