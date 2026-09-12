import gzip
import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
PACKAGE = DIRECTION / "packages/reading_2026.kjv.v1.package.json.gz"
MANIFEST = DIRECTION / "packages/reading_2026.kjv.v1.manifest.json"
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


def has_word(text, value):
    return bool(re.search(rf"(?<![A-Za-z]){re.escape(value)}(?![A-Za-z])", text, re.I))


def main():
    spec = importlib.util.spec_from_file_location(
        "generator", Path(__file__).with_name("generate_kjv_v13_remaining_new_testament_review.py")
    )
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)

    books, order, paths, remaining, source = generator.corpus_and_paths()
    rules = generator.make_family_rules(source) + generator.CONTEXT_RULES
    assert len(source) == 6208
    assert len(rules) == 663

    directions = {book: read(paths[book]) for book in books}
    rendered = {}
    for (book, chapter, verse), text in source.items():
        direction = directions[book]
        patch = next(
            (item for item in direction.get("verses", []) if item["chapter"] == chapter and item["verse"] == verse),
            None,
        )
        rendered[(book, chapter, verse)] = render(text, [] if patch is None else patch["edits"])

    for index, entry in enumerate(rules):
        ref = (entry["book"], entry["chapter"], entry["verse"])
        text = rendered[ref]
        superseded = any(
            (later["book"], later["chapter"], later["verse"]) == ref
            and entry["replacement"].casefold() in later["expected"].casefold()
            for later in rules[index + 1:]
        )
        if entry["word"]:
            assert not has_word(text, entry["expected"]), (ref, entry["expected"], text)
            if not superseded:
                assert has_word(text, entry["replacement"]), (ref, entry["replacement"], text)
        else:
            assert entry["expected"].casefold() not in text.casefold(), (ref, entry["expected"], text)
            if not superseded:
                assert entry["replacement"].casefold() in text.casefold(), (ref, entry["replacement"], text)

    stable_terms = [item[0] for item in generator.STABLE_FAMILIES]
    stable_terms += ["Holy Ghost", "devils", "candlestick", "candlesticks", "sepulchre"]
    for ref, text in rendered.items():
        for term in stable_terms:
            if term == "sepulchre" and ref == ("ROM", 3, 13):
                continue
            assert not has_word(text, term) if " " not in term else term.casefold() not in text.casefold(), (ref, term, text)

    forbidden = (
        "Truly truly",
        "near unto",
        "there came there",
        "hath made alive us",
        "clothed in white clothing",
        "chief among the tax collectors",
        "Foods for the belly",
        "made alive alive",
        "food food",
        "demons demons",
        "Spirit Spirit",
    )
    for ref, text in rendered.items():
        for phrase in forbidden:
            assert phrase.casefold() not in text.casefold(), (ref, phrase, text)
        assert not re.search(r"\b(the|of|to|and|a|an)\s+\1\b", text, re.I), (ref, "duplicate word", text)

    v13_books = [
        book for book in remaining
        if directions[book].get("ownerReview", {}).get("contentVersion") == 13
    ]
    assert len(v13_books) == 24
    assert all(directions[book]["editorialStatus"] == "approved-remaining-new-testament-context-review-v13" for book in v13_books)

    raw = PACKAGE.read_bytes()
    manifest = read(MANIFEST)
    assert manifest["contentVersion"] == 13
    assert manifest["contentSha256"] == hashlib.sha256(raw).hexdigest()
    assert manifest["sourceCorpusSha256"] == "4e2c28113d053e64dacef2792a8d3bcfb32367320f549ef2c2f03b3122902939"
    assert manifest["coverage"] == {
        "expectedBookCount": 66,
        "includedBookCount": 66,
        "changedVerseCount": 4709,
        "editCount": 5537,
    }
    payload = json.loads(gzip.decompress(raw))
    assert payload["contentVersion"] == 13 and len(payload["books"]) == 66
    assert payload["sourceCorpusSha256"] == manifest["sourceCorpusSha256"]
    for book in v13_books:
        assert next(item for item in payload["books"] if item["book"] == book) == directions[book]

    registry = read(REGISTRY)
    assert registry["activeContentVersion"] == 13
    applied = {(item["reference"], item["expected"], item["replacement"]) for item in registry["applied"]}
    for entry in rules:
        key = (f"{entry['book']}.{entry['chapter']}.{entry['verse']}", entry["expected"], entry["replacement"])
        assert key in applied, key
    pending = [item for item in registry["pending"] if item["id"].startswith("nt-kjv-v13-")]
    assert len(pending) == 22
    assert all(item["reason"] and item["references"] and item["evidence"] for item in pending)
    assert all(item["scope"] == "remaining-new-testament" for item in pending)
    assert all(ref["book"] in remaining for item in pending for ref in item["references"])

    touched = sum(
        1 for book in v13_books for verse in directions[book]["verses"]
        if len(verse["edits"]) == 1 and verse["edits"][0].get("category") == "remaining-new-testament-context-review"
    )
    print(json.dumps({
        "contentVersion": 13,
        "verifiedSourceVerses": len(source),
        "reviewedRules": len(rules),
        "touchedVerses": touched,
        "changedBooks": len(v13_books),
        "pendingFamilies": len(pending),
        "coverage": manifest["coverage"],
        "contentSha256": manifest["contentSha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
