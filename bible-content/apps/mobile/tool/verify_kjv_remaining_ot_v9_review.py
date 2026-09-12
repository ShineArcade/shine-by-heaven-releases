import gzip, hashlib, importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "apps/mobile/assets/bible_direction/kjv/packages/reading_2026.kjv.v1.package.json.gz"
MANIFEST = ROOT / "apps/mobile/assets/bible_direction/kjv/packages/reading_2026.kjv.v1.manifest.json"
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv/books"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"

def read(path): return json.loads(path.read_text(encoding="utf-8"))

def main():
    spec = importlib.util.spec_from_file_location("generator", Path(__file__).with_name("generate_kjv_v9_remaining_old_testament_review.py"))
    generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
    raw = PACKAGE.read_bytes(); manifest = read(MANIFEST)
    assert manifest["contentVersion"] == 9
    assert manifest["contentSha256"] == hashlib.sha256(raw).hexdigest()
    package = json.loads(gzip.decompress(raw)); assert package["contentVersion"] == 9 and len(package["books"]) == 66
    rendered = {}
    for book_patch in package["books"][:39]:
        book = book_patch["book"]; source = read(CORPUS / f"{book}.json")
        texts = {(c["chapter"], v["verse"]): v["text"] for c in source["chapters"] for v in c["verses"]}
        patches = {(v["chapter"], v["verse"]): v["edits"] for v in book_patch.get("verses", [])}
        for ref, original in texts.items():
            text = original
            for edit in sorted(patches.get(ref, []), key=lambda x: x["startOffset"], reverse=True):
                assert original[edit["startOffset"]:edit["endOffset"]] == edit["expected"]
                text = text[:edit["startOffset"]] + edit["replacement"] + text[edit["endOffset"]:]
            rendered[(book, *ref)] = text
    for (book, chapter, verse), text in rendered.items():
        if book in generator.REVIEWED: continue
        for term, *_ in generator.RULES:
            assert not generator.pattern(term).search(text), (book, chapter, verse, term, text)
    registry = read(REGISTRY)
    assert registry["activeContentVersion"] == 9
    pending = [x for x in registry["pending"] if x["id"].startswith("remaining-ot-kjv-v9-")]
    assert len(pending) == 14 and all(x["reason"] and x["references"] for x in pending)
    print(json.dumps({"contentVersion": 9, "verifiedSourceVerses": len(rendered), "retiredRules": len(generator.RULES), "pendingFamilies": len(pending), "contentSha256": manifest["contentSha256"]}, indent=2))

if __name__ == "__main__": main()
