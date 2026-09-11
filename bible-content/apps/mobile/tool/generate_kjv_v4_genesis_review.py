import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"

# Each phrase was reviewed in its complete Genesis verse. These are narrow
# comprehension edits; names, doctrine, numbers, and the immutable KJV corpus
# remain untouched.
CHANGES = [
    (1, 20, "creature that hath life", "creature that has life"),
    (1, 21, "living creature that moveth", "living creature that moves"),
    (1, 25, "every thing that creepeth upon the earth", "everything that crawls upon the earth"),
    (1, 28, "replenish the earth", "fill the earth"),
    (1, 28, "living thing that moveth", "living thing that moves"),
    (1, 29, "for meat", "for food"),
    (1, 30, "wherein there is life", "in which there is life"),
    (1, 30, "for meat", "for food"),
    (2, 10, "from thence it was parted, and became into four heads", "from there it divided into four branches"),
    (3, 1, "more subtil", "more crafty"),
    (3, 13, "beguiled me", "deceived me"),
    (3, 17, "hearkened unto the voice of thy wife", "listened to the voice of your wife"),
    (4, 4, "firstlings of his flock", "firstborn of his flock"),
    (4, 5, "he had not respect", "he had no regard"),
    (4, 5, "very wroth, and his countenance fell", "very angry, and his face fell"),
    (4, 7, "sin lieth at the door", "sin lies at the door"),
    (4, 10, "blood crieth unto me", "blood cries out to me"),
    (4, 12, "a fugitive and a vagabond", "a fugitive and a wanderer"),
    (4, 14, "every one that findeth me shall slay me", "everyone who finds me shall kill me"),
    (4, 15, "whosoever slayeth Cain", "whoever kills Cain"),
    (4, 23, "hearken unto my speech", "listen to my speech"),
    (6, 4, "mighty men which were of old, men of renown", "mighty men of ancient times, men of renown"),
    (6, 6, "it repented the LORD", "the LORD regretted"),
    (8, 1, "the waters asswaged", "the waters subsided"),
    (8, 21, "a sweet savour", "a pleasing aroma"),
    (9, 20, "an husbandman", "a farmer"),
    (12, 5, "the souls that they had gotten", "the people they had acquired"),
    (15, 1, "thy exceeding great reward", "your very great reward"),
    (15, 4, "come forth out of thine own bowels", "come from your own body"),
    (15, 6, "counted it to him for righteousness", "credited it to him as righteousness"),
    (16, 2, "restrained me from bearing", "kept me from having children"),
    (16, 7, "a fountain of water", "a spring of water"),
    (16, 8, "whence camest thou? and whither wilt thou go?", "where did you come from, and where are you going?"),
    (18, 5, "comfort ye your hearts", "refresh yourselves"),
    (18, 24, "Peradventure", "Perhaps"),
    (18, 28, "Peradventure", "Perhaps"),
    (18, 29, "Peradventure", "Perhaps"),
    (18, 30, "Peradventure", "Perhaps"),
    (18, 31, "Peradventure", "Perhaps"),
    (18, 32, "Peradventure", "Perhaps"),
    (19, 11, "wearied themselves to find the door", "exhausted themselves trying to find the door"),
    (20, 6, "suffered I thee", "allowed you"),
    (21, 14, "a bottle of water", "a skin of water"),
    (21, 17, "What aileth thee", "What troubles you"),
    (22, 1, "God did tempt Abraham", "God tested Abraham"),
    (23, 4, "buryingplace", "burial place"),
    (23, 6, "sepulchres", "tombs"),
    (24, 5, "Peradventure", "Perhaps"),
    (24, 39, "Peradventure", "Perhaps"),
    (24, 53, "raiment", "clothing"),
    (25, 8, "gave up the ghost", "died"),
    (25, 23, "from thy bowels", "from your womb"),
    (25, 27, "a plain man", "a quiet man"),
    (25, 29, "sod pottage", "cooked stew"),
    (25, 30, "that same red pottage", "that red stew"),
    (25, 34, "pottage of lentiles", "lentil stew"),
    (26, 14, "great store of servants", "many servants"),
    (28, 11, "lighted upon a certain place", "came to a certain place"),
    (31, 19, "stolen the images", "stolen the household gods"),
    (31, 34, "the camel’s furniture", "the camel’s saddle"),
    (34, 3, "his soul clave unto Dinah", "his soul clung to Dinah"),
    (34, 7, "wrought folly in Israel", "committed a disgraceful act in Israel"),
    (35, 18, "as her soul was in departing, (for she died)", "as her life was leaving her (for she died)"),
    (36, 6, "all his substance", "all his possessions"),
    (38, 21, "the harlot", "the prostitute"),
    (39, 6, "he knew not ought he had", "he concerned himself with nothing he had"),
    (40, 17, "bakemeats", "baked goods"),
    (41, 2, "seven well favoured kine and fatfleshed", "seven healthy and well-fed cows"),
    (41, 3, "seven other kine", "seven other cows"),
    (41, 4, "the ill favoured and leanfleshed kine", "the ugly and thin cows"),
    (41, 5, "seven ears of corn", "seven heads of grain"),
    (41, 6, "blasted with the east wind", "scorched by the east wind"),
    (41, 14, "brought him hastily out of the dungeon", "quickly brought him out of prison"),
    (41, 35, "lay up corn", "store grain"),
    (41, 49, "corn as the sand of the sea", "grain as plentiful as the sand of the sea"),
    (42, 1, "corn in Egypt", "grain in Egypt"),
    (42, 7, "made himself strange unto them", "acted like a stranger toward them"),
    (42, 9, "the nakedness of the land", "the undefended parts of the land"),
    (42, 27, "he espied his money", "he saw his money"),
    (43, 30, "his bowels did yearn upon his brother", "he was deeply moved for his brother"),
    (44, 34, "lest peradventure I see the evil", "lest I see the harm"),
    (45, 6, "neither be earing nor harvest", "be neither plowing nor harvest"),
    (45, 17, "lade your beasts", "load your animals"),
    (45, 18, "the fat of the land", "the best of the land"),
    (45, 22, "changes of raiment", "changes of clothing"),
    (45, 24, "See that ye fall not out by the way", "Do not quarrel along the way"),
    (46, 15, "all the souls of his sons and his daughters were thirty and three", "all his sons and daughters numbered thirty-three people"),
    (46, 34, "Thy servants’ trade hath been about cattle", "Your servants have worked with livestock"),
    (47, 4, "the famine is sore", "the famine is severe"),
    (47, 6, "men of activity", "capable men"),
    (47, 18, "there is not ought left", "there is nothing left"),
    (48, 6, "thy issue", "your offspring"),
    (49, 9, "a lion’s whelp", "a young lion"),
    (49, 14, "a strong ass", "a strong donkey"),
    (49, 26, "my progenitors", "my ancestors"),
    (49, 33, "yielded up the ghost", "died"),
    (50, 15, "will certainly requite us", "will certainly repay us"),
    (50, 25, "from hence", "from here"),
]

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

base = read(CORPUS / "books/GEN.json")
direction_path = DIRECTION / "books/gen_reading_2026.kjv.v1.json"
direction = read(direction_path)
texts = {(c["chapter"], v["verse"]): v["text"] for c in base["chapters"] for v in c["verses"]}

added = []
for chapter, verse, expected, replacement in CHANGES:
    text = texts[(chapter, verse)]
    start = text.find(expected)
    if start < 0:
        raise RuntimeError(f"Missing exact phrase GEN.{chapter}.{verse}: {expected!r}")
    end = start + len(expected)
    patch = next((v for v in direction["verses"] if v["chapter"] == chapter and v["verse"] == verse), None)
    if patch is None:
        patch = {"chapter": chapter, "verse": verse, "sourceTextSha256": sha(text.encode()), "edits": []}
        direction["verses"].append(patch)
    if patch["sourceTextSha256"] != sha(text.encode()):
        raise RuntimeError(f"Source hash mismatch GEN.{chapter}.{verse}")
    if any(start < e["endOffset"] and end > e["startOffset"] for e in patch["edits"]):
        exact = next((e for e in patch["edits"] if e["startOffset"] == start and e["endOffset"] == end and e["replacement"] == replacement), None)
        if exact:
            continue
        raise RuntimeError(f"Overlapping edit GEN.{chapter}.{verse}: {expected!r}")
    patch["edits"].append({
        "startOffset": start, "endOffset": end, "expected": expected, "replacement": replacement,
        "category": "genesis-complete-context-review",
        "reason": "The complete Genesis verse was reviewed to remove an archaic or misleading construction while preserving its people, action, and theological sense.",
        "evidence": [{"label": "Complete-verse KJV contextual review", "url": f"https://www.biblegateway.com/passage/?search=Genesis+{chapter}%3A{verse}&version=KJV"}],
    })
    patch["edits"].sort(key=lambda e: e["startOffset"])
    added.append((chapter, verse, expected, replacement))

direction["verses"].sort(key=lambda v: (v["chapter"], v["verse"]))
direction["editorialStatus"] = "approved-genesis-complete-context-v4"
direction["ownerReview"] = {"contentVersion": 4, "review": "KJV Genesis complete-context review", "requiredFullTest": True}
write(direction_path, direction)

source_path = DIRECTION / "reading_2026.package-source.json"
source = read(source_path)
source["contentVersion"] = 4
source["generatedAt"] = "2026-09-11T00:00:00.000Z"
source["editorialPolicy"]["version"] = 4
write(source_path, source)

order = {read(p)["book"]: read(p)["order"] for p in (CORPUS / "books").glob("*.json")}
books = [read(p) for p in (DIRECTION / "books").glob("*.json")]
books.sort(key=lambda b: order[b["book"]])
payload = {
    "books": books, "contentVersion": 4, "editorialPolicy": source["editorialPolicy"],
    "filterId": source["filterId"], "format": "shine-reading-filter-package",
    "normalizationId": source["normalizationId"], "schemaVersion": 1,
    "sourceCorpusSha256": source["sourceCorpusSha256"], "sourceVersionId": "KJV",
}
raw = canonical(payload).encode()
compressed = gzip.compress(raw, compresslevel=9, mtime=0)
packages = DIRECTION / "packages"
(packages / "reading_2026.kjv.v1.package.json.gz").write_bytes(compressed)
coverage = {
    "expectedBookCount": 66, "includedBookCount": 66,
    "changedVerseCount": sum(len(b["verses"]) for b in books),
    "editCount": sum(sum(len(v["edits"]) for v in b["verses"]) for b in books),
}
manifest = {
    "format": "shine-reading-filter-manifest", "filterId": source["filterId"], "schemaVersion": 1,
    "contentVersion": 4, "sourceVersionId": "KJV", "sourceCorpusSha256": source["sourceCorpusSha256"],
    "normalizationId": source["normalizationId"], "contentSha256": sha(compressed), "sizeBytes": len(compressed),
    "expandedSizeBytes": len(raw), "mimeType": "application/vnd.shine.reading-filter+gzip",
    "generatedAt": "2026-09-11", "editorialPolicy": source["editorialPolicy"], "coverage": coverage,
    "books": [{
        "id": b["book"], "order": order[b["book"]],
        "sourceFile": next(p.name for p in (DIRECTION / "books").glob("*.json") if read(p)["book"] == b["book"]),
        "sourceContentSha256": b["sourceContentSha256"], "payloadSha256": sha(canonical(b).encode()),
        "changedVerseCount": len(b["verses"]), "editCount": sum(len(v["edits"]) for v in b["verses"]),
    } for b in books],
}
write(packages / "reading_2026.kjv.v1.manifest.json", manifest)

registry = read(REGISTRY)
registry["updatedAt"] = "2026-09-11T00:00:00.000Z"
registry["activeContentVersion"] = 4
known = {(x["reference"], x["expected"], x["replacement"]) for x in registry["applied"]}
for chapter, verse, expected, replacement in CHANGES:
    item = {
        "reference": f"GEN.{chapter}.{verse}", "expected": expected, "replacement": replacement,
        "category": "genesis-complete-context-review",
        "reason": "Complete-verse Genesis review for clear, faithful contemporary reading.",
        "evidenceUrl": f"https://www.biblegateway.com/passage/?search=Genesis+{chapter}%3A{verse}&version=KJV",
    }
    key = (item["reference"], expected, replacement)
    if key not in known:
        registry["applied"].append(item)
        known.add(key)
write(REGISTRY, registry)

print(json.dumps({"added": len(added), "genesisVerses": len(direction["verses"]), "genesisEdits": sum(len(v["edits"]) for v in direction["verses"]), **coverage, "contentSha256": manifest["contentSha256"]}, indent=2))
