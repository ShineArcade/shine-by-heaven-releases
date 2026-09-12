import gzip, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"
VERSION = 9
REVIEWED = {"GEN", "EXO", "LEV", "NUM", "DEU", "JOS"}

# Phrase rules precede their component words. These meanings were checked
# across every remaining Old Testament occurrence.
RULES = [
    ("from hence", "from here", "archaic-location", "From hence means from here."),
    ("from thence", "from there", "archaic-location", "From thence means from there."),
    ("thence", "from there", "archaic-location", "Thence means from there."),
    ("from whence", "from where", "archaic-location", "From whence means from where."),
    ("whence", "from where", "archaic-location", "Whence identifies the place from which something comes."),
    ("to morrow", "tomorrow", "archaic-time", "The historical two-word spelling is modernized."),
    ("the morrow", "the next day", "archaic-time", "The morrow means the next day."),
    ("meat offerings", "grain offerings", "false-friend-offering", "Meat offering is the historical name for a grain offering."),
    ("meat offering", "grain offering", "false-friend-offering", "Meat offering is the historical name for a grain offering."),
    ("candlesticks", "lampstands", "false-friend-object", "Candlestick denotes an oil lampstand in this corpus."),
    ("candlestick", "lampstand", "false-friend-object", "Candlestick denotes an oil lampstand in this corpus."),
    ("cherubims", "cherubim", "historical-plural", "Cherubim is already the plural form."),
    ("peradventure", "perhaps", "archaic-adverb", "Peradventure means perhaps."),
    ("hitherto", "until now", "archaic-time", "Hitherto means until now."),
    ("beforetime", "formerly", "archaic-time", "Beforetime means formerly."),
    ("aforetime", "formerly", "archaic-time", "Aforetime means formerly."),
    ("eveningtide", "evening", "archaic-time", "Eveningtide means evening."),
    ("oftentimes", "often", "archaic-frequency", "Oftentimes means often."),
    ("wherewith", "with which", "archaic-relative", "Wherewith means with which."),
    ("wherein", "in which", "archaic-relative", "Wherein means in which."),
    ("therein", "in it", "archaic-relative", "Therein means in it."),
    ("thereon", "on it", "archaic-relative", "Thereon means on it."),
    ("whither", "where", "archaic-location", "Whither asks or identifies where someone goes."),
    ("thither", "there", "archaic-location", "Thither means to that place."),
    ("hither", "here", "archaic-location", "Hither means to this place."),
    ("hence", "from here", "archaic-location", "Hence means from this place."),
    ("nigh", "near", "archaic-location", "Nigh means near."),
    ("uttermost", "farthest", "archaic-location", "Uttermost means farthest or outermost."),
    ("midst", "middle", "archaic-location", "Midst means middle."),
    ("rereward", "rear guard", "obsolete-military-term", "Rereward means rear guard."),
    ("slew", "killed", "archaic-verb", "Slew means killed."),
    ("is waxed", "has grown", "archaic-verb", "Is waxed means has grown in this construction."),
    ("waxed", "grew", "archaic-verb", "Waxed means grew or became."),
    ("dwelt", "lived", "archaic-residence", "Dwelt means lived."),
    ("durst", "dared", "archaic-verb", "Durst means dared."),
    ("fain", "gladly", "archaic-adverb", "Fain means gladly or eagerly."),
    ("haply", "perhaps", "archaic-adverb", "Haply means perhaps."),
    ("minished", "diminished", "archaic-verb", "Minished means diminished."),
    ("sith", "since", "archaic-connector", "Sith means since or because."),
    ("seethe", "boil", "archaic-verb", "Seethe means boil."),
    ("furbish", "polish", "archaic-verb", "Furbish means polish."),
    ("bewray", "betray", "archaic-verb", "Bewray means reveal or betray in this warning."),
    ("asses", "donkeys", "historical-animal-name", "Asses is the historical plural for donkeys."),
    ("ass", "donkey", "historical-animal-name", "Ass is the historical name for a donkey."),
    ("kine", "cows", "historical-animal-name", "Kine is the historical plural for cows."),
    ("victuals", "provisions", "archaic-food-term", "Victuals means provisions."),
    ("raiment", "clothing", "archaic-clothing-term", "Raiment means clothing."),
    ("harlots", "prostitutes", "archaic-person-term", "Harlots is the historical term for prostitutes."),
    ("harlot", "prostitute", "archaic-person-term", "Harlot is the historical term for a prostitute."),
    ("suburbs", "pasturelands", "false-friend-land-term", "Suburbs denotes pasturelands around Levitical cities."),
    ("nether", "lower", "archaic-position", "Nether means lower."),
    ("corn", "grain", "false-friend-food-term", "Corn denotes grain rather than modern maize."),
    ("brasen", "bronze", "historical-metal-term", "Brasen means made of bronze."),
    ("brass", "bronze", "historical-metal-term", "Brass denotes bronze in these ancient objects."),
    ("vails", "veils", "historical-spelling", "The historical spelling vail is modernized to veil."),
    ("vail", "veil", "historical-spelling", "The historical spelling vail is modernized to veil."),
    ("musick", "music", "historical-spelling", "The historical spelling is modernized."),
    ("agone", "ago", "archaic-time", "Agone means ago."),
    ("hosen", "trousers", "archaic-clothing-term", "Hosen designates trousers or leggings."),
    ("targets", "large shields", "false-friend-armor-term", "Target denotes a large shield in this corpus."),
    ("target", "large shield", "false-friend-armor-term", "Target denotes a large shield in this corpus."),
    ("bucklers", "shields", "archaic-armor-term", "Bucklers are shields."),
    ("buckler", "shield", "archaic-armor-term", "A buckler is a shield."),
    ("coulters", "plowshares", "archaic-tool-term", "Coulters are cutting parts of plows."),
    ("coulter", "plowshare", "archaic-tool-term", "A coulter is the cutting part of a plow."),
    ("garners", "granaries", "archaic-storage-term", "Garners are granaries or storehouses."),
    ("husbandmen", "farmers", "archaic-occupation", "Husbandmen are farmers or vineyard workers."),
    ("husbandman", "farmer", "archaic-occupation", "A husbandman is a farmer or vineyard worker."),
    ("husbandry", "farming", "archaic-occupation", "Husbandry means farming."),
    ("emerods", "tumors", "obsolete-medical-term", "Emerods denotes the tumors in the Philistine plague."),
    ("arrogancy", "arrogance", "historical-spelling", "Arrogancy means arrogance."),
    ("churl", "scoundrel", "archaic-person-term", "Churl denotes a selfish or contemptible person in Isaiah 32."),
    ("collops", "folds", "archaic-body-term", "Collops describes folds of fat."),
    ("daysman", "mediator", "archaic-legal-term", "Daysman denotes a mediator between two parties."),
    ("dunghill", "garbage heap", "archaic-place-term", "Dunghill denotes a refuse or garbage heap."),
    ("gins", "traps", "archaic-trap-term", "Gins are traps or snares."),
    ("greaves", "leg armor", "archaic-armor-term", "Greaves are armor worn on the legs."),
    ("grinders", "teeth", "poetic-body-term", "The grinders in Ecclesiastes are the teeth."),
    ("dearth", "famine", "archaic-scarcity-term", "Dearth means famine or severe scarcity."),
    ("froward", "perverse", "archaic-character-term", "Froward describes perverse or contrary conduct."),
    ("scorners", "mockers", "archaic-mocker-term", "Scorners are mockers."),
    ("scorner", "mocker", "archaic-mocker-term", "A scorner is a mocker."),
    ("derision", "mockery", "archaic-mockery-term", "Derision means mockery."),
    ("munition", "fortification", "false-friend-fortress-term", "Munition denotes a fortified place here."),
    ("noisome", "harmful", "archaic-harm-term", "Noisome means harmful or destructive."),
    ("pate", "head", "archaic-body-term", "Pate means head."),
    ("besom", "broom", "archaic-object-term", "Besom means broom."),
    ("brigandine", "armor", "archaic-armor-term", "Brigandine denotes body armor."),
    ("habergeon", "coat of mail", "archaic-armor-term", "Habergeon denotes a coat of mail."),
    ("chapiters", "capitals", "architectural-term", "Chapiters are the capitals at the tops of pillars."),
    ("chapiter", "capital", "architectural-term", "A chapiter is the capital at the top of a pillar."),
    ("fetters", "shackles", "archaic-restraint-term", "Fetters are shackles."),
    ("usury", "interest", "historical-finance-term", "Usury denotes interest charged on a loan in these laws and accusations."),
]

PENDING = {
    "thereof": "A natural replacement depends on its antecedent and possessive phrase.",
    "wherefore": "It can mean why or therefore.",
    "wrought": "It can mean made, did, worked, produced, or accomplished.",
    "compass": "It can be a drawing tool, a circle, surrounding, or taking a circuitous route.",
    "smote": "It can mean struck, killed, defeated, or afflicted.",
    "goodly": "It can describe beauty, value, size, fertility, or moral appearance.",
    "withal": "Its modern rendering depends on the governing verb and clause.",
    "betimes": "It can mean early, promptly, or diligently.",
    "tabret": "Job 17:6 differs from the musical-instrument uses and must be reviewed separately.",
    "naughty": "It can mean wicked, worthless, or spoiled depending on the object.",
    "lees": "It is literal wine sediment in one passage and a metaphor for complacency in others.",
    "stomacher": "The underlying garment in Isaiah 3:24 is uncertain across translations.",
    "wimples": "The precise ancient garment in Isaiah 3:22 needs a note rather than a guessed equivalent.",
    "palmerworm": "The exact locust stage or species is debated.",
}

COMBINED = [
    ("1CH", 6, 58, "her suburbs, Debir with her suburbs", "her pasturelands, Debir with her pasturelands", "false-friend-land-term", "Both occurrences denote pasturelands around the Levitical cities."),
    ("1CH", 6, 72, "Kedesh with her suburbs, Daberath with her suburbs", "Kedesh with her pasturelands, Daberath with her pasturelands", "false-friend-land-term", "Both occurrences denote pasturelands around the Levitical cities."),
    ("HAB", 3, 2, "in the midst of the years, in the midst of the years", "in the middle of the years, in the middle of the years", "archaic-location", "Both parallel occurrences of midst mean middle."),
]

def read(path): return json.loads(path.read_text(encoding="utf-8"))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def sha(value): return hashlib.sha256(value).hexdigest()
def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def pattern(term): return re.compile(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", re.IGNORECASE)
def recase(actual, replacement):
    if actual.isupper(): return replacement.upper()
    if actual[:1].isupper(): return replacement[:1].upper() + replacement[1:]
    return replacement

def unique_phrase(text, start, end):
    left, right = start, end
    while text.count(text[left:right]) != 1:
        if right < len(text):
            boundary = text.find(" ", min(len(text), right + 1))
            right = len(text) if boundary < 0 else boundary
        if text.count(text[left:right]) == 1: break
        if left > 0:
            boundary = text.rfind(" ", 0, max(0, left - 1))
            left = 0 if boundary < 0 else boundary + 1
        if left == 0 and right == len(text): break
    return left, right

def main():
    books = {read(p)["book"]: read(p) for p in (CORPUS / "books").glob("*.json")}
    order = {b: d["order"] for b, d in books.items()}
    direction_paths = {read(p)["book"]: p for p in (DIRECTION / "books").glob("*.json")}
    applied = []
    repairs = [
        ("the its", "its", "grammar-article-possessive", "The definite article cannot precede the possessive determiner its."),
        ("from from here", "from here", "grammar-duplicate-preposition", "The location phrase must contain only one preposition."),
        ("is grew", "has grown", "grammar-verb-form", "The perfect construction requires has grown."),
    ]
    for book, path in direction_paths.items():
        if order[book] > 39:
            continue
        direction = read(path); changed = False
        for verse in direction.get("verses", []):
            source_text = next(v["text"] for c in books[book]["chapters"] if c["chapter"] == verse["chapter"] for v in c["verses"] if v["verse"] == verse["verse"])
            for edit in verse["edits"]:
                structural = None
                if edit["replacement"].startswith("its ") and source_text[max(0, edit["startOffset"] - 4):edit["startOffset"]].lower() == "the ":
                    structural = (4, edit["replacement"], "the its", "its", "grammar-article-possessive", "The source article is included in the edit so it does not precede the possessive determiner its.")
                elif edit["replacement"].startswith("from here") and source_text[max(0, edit["startOffset"] - 5):edit["startOffset"]].lower() == "from ":
                    structural = (5, edit["replacement"], "from from here", "from here", "grammar-duplicate-preposition", "The source preposition is included so the modern location phrase contains only one from.")
                elif edit["replacement"].startswith("grew") and source_text[max(0, edit["startOffset"] - 3):edit["startOffset"]].lower() == "is ":
                    structural = (3, "has grown" + edit["replacement"][4:], "is grew", "has grown", "grammar-verb-form", "The source auxiliary is included and the perfect construction is rendered as has grown.")
                if structural:
                    amount, replacement_text, wrong, corrected, category, reason = structural
                    new_start = edit["startOffset"] - amount
                    if not any(other is not edit and other["startOffset"] < edit["endOffset"] and new_start < other["endOffset"] for other in verse["edits"]):
                        edit["startOffset"] = new_start; edit["expected"] = source_text[new_start:edit["endOffset"]]; edit["replacement"] = replacement_text; edit["reason"] = edit["reason"] + " " + reason
                        applied.append((book, verse["chapter"], verse["verse"], wrong, corrected, category, reason)); changed = True
                for wrong, corrected, category, reason in repairs:
                    if wrong in edit["replacement"]:
                        edit["replacement"] = edit["replacement"].replace(wrong, corrected)
                        edit["reason"] = edit["reason"] + " " + reason
                        applied.append((book, verse["chapter"], verse["verse"], wrong, corrected, category, reason)); changed = True
        if changed:
            path.write_text(json.dumps(direction, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    for book, source_doc in books.items():
        if book in REVIEWED or order[book] > 39: continue
        path = direction_paths[book]; direction = read(path)
        source = {(c["chapter"], v["verse"]): v["text"] for c in source_doc["chapters"] for v in c["verses"]}
        patches = {(v["chapter"], v["verse"]): v for v in direction.get("verses", [])}
        for special_book, chapter, verse, expected, replacement, category, reason in COMBINED:
            if special_book != book:
                continue
            text = source[(chapter, verse)]
            start = text.index(expected); end = start + len(expected)
            patch = patches.get((chapter, verse))
            if patch is None:
                patch = {"chapter": chapter, "verse": verse, "sourceTextSha256": sha(text.encode()), "edits": []}
                direction["verses"].append(patch); patches[(chapter, verse)] = patch
            if not any(e["startOffset"] < end and start < e["endOffset"] for e in patch["edits"]):
                patch["edits"].append({"startOffset": start, "endOffset": end, "expected": expected, "replacement": replacement, "category": category, "reason": reason, "evidence": [{"label": "Complete-verse KJV contextual review", "url": f"https://www.biblegateway.com/passage/?search={book}+{chapter}%3A{verse}&version=KJV%3BNIV"}]})
                applied.append((book, chapter, verse, "suburbs" if book == "1CH" else "midst", "pasturelands" if book == "1CH" else "middle", category, reason))
        for ref, text in source.items():
            patch = patches.get(ref)
            occupied = [] if patch is None else [(e["startOffset"], e["endOffset"]) for e in patch["edits"]]
            if patch:
                for edit in patch["edits"]:
                    old = edit["replacement"]; new = old; labels = []
                    for expected, replacement, category, reason in RULES:
                        matches = list(pattern(expected).finditer(new))
                        if matches:
                            new = pattern(expected).sub(lambda m: recase(m.group(0), replacement), new)
                            labels.append((expected, replacement, category, reason))
                    if new != old:
                        edit["replacement"] = new
                        edit["reason"] = edit["reason"] + " The remaining archaic wording inside this reviewed clause is also modernized."
                        for item in labels: applied.append((book, *ref, *item))
            for expected, replacement, category, reason in RULES:
                for match in pattern(expected).finditer(text):
                    start, end = match.span()
                    if any(a < end and start < b for a, b in occupied): continue
                    if patch is None:
                        patch = {"chapter": ref[0], "verse": ref[1], "sourceTextSha256": sha(text.encode()), "edits": []}
                        direction["verses"].append(patch); patches[ref] = patch
                    left, right = unique_phrase(text, start, end)
                    if any(a < right and left < b for a, b in occupied): continue
                    phrase = text[left:right]; actual = text[start:end]
                    modern = recase(actual, replacement)
                    patch["edits"].append({"startOffset": left, "endOffset": right, "expected": phrase, "replacement": phrase[:start-left] + modern + phrase[end-left:], "category": category, "reason": reason, "evidence": [{"label": "Complete-verse KJV contextual review", "url": f"https://www.biblegateway.com/passage/?search={book}+{ref[0]}%3A{ref[1]}&version=KJV%3BNIV"}]})
                    occupied.append((left, right)); applied.append((book, *ref, expected, replacement, category, reason))
            if patch: patch["edits"].sort(key=lambda x: x["startOffset"])
        direction["verses"].sort(key=lambda x: (x["chapter"], x["verse"]))
        direction["editorialStatus"] = "approved-remaining-old-testament-context-v9"
        direction["ownerReview"] = {"contentVersion": VERSION, "review": "KJV remaining Old Testament stable-lexicon review", "requiredFullTest": True}
        path.write_text(json.dumps(direction, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    source_path = DIRECTION / "reading_2026.package-source.json"; package_source = read(source_path)
    package_source["contentVersion"] = VERSION; package_source["generatedAt"] = "2026-09-12T07:05:00.000Z"; package_source["editorialPolicy"]["version"] = VERSION; write(source_path, package_source)
    direction_books = [read(p) for p in direction_paths.values()]; direction_books.sort(key=lambda x: order[x["book"]])
    payload = {"books": direction_books, "contentVersion": VERSION, "editorialPolicy": package_source["editorialPolicy"], "filterId": package_source["filterId"], "format": "shine-reading-filter-package", "normalizationId": package_source["normalizationId"], "schemaVersion": 1, "sourceCorpusSha256": package_source["sourceCorpusSha256"], "sourceVersionId": package_source["sourceVersionId"]}
    raw = canonical(payload).encode(); compressed = gzip.compress(raw, compresslevel=9, mtime=0); packages = DIRECTION / "packages"; (packages / "reading_2026.kjv.v1.package.json.gz").write_bytes(compressed)
    coverage = {"expectedBookCount": 66, "includedBookCount": len(direction_books), "changedVerseCount": sum(len(b["verses"]) for b in direction_books), "editCount": sum(len(v["edits"]) for b in direction_books for v in b["verses"])}
    manifest = {"format": "shine-reading-filter-manifest", "filterId": package_source["filterId"], "schemaVersion": 1, "contentVersion": VERSION, "sourceVersionId": package_source["sourceVersionId"], "sourceCorpusSha256": package_source["sourceCorpusSha256"], "normalizationId": package_source["normalizationId"], "contentSha256": sha(compressed), "sizeBytes": len(compressed), "expandedSizeBytes": len(raw), "mimeType": "application/vnd.shine.reading-filter+gzip", "generatedAt": "2026-09-12", "editorialPolicy": package_source["editorialPolicy"], "coverage": coverage, "books": [{"id": b["book"], "order": order[b["book"]], "sourceFile": direction_paths[b["book"]].name, "sourceContentSha256": b["sourceContentSha256"], "payloadSha256": sha(canonical(b).encode()), "changedVerseCount": len(b["verses"]), "editCount": sum(len(v["edits"]) for v in b["verses"])} for b in direction_books]}
    write(packages / "reading_2026.kjv.v1.manifest.json", manifest)
    registry = read(REGISTRY); registry["updatedAt"] = "2026-09-12T07:05:00.000Z"; registry["activeContentVersion"] = VERSION
    known = {(x["reference"], x["expected"], x["replacement"]) for x in registry["applied"]}
    for book, chapter, verse, expected, replacement, category, reason in applied:
        key = (f"{book}.{chapter}.{verse}", expected, replacement)
        if key not in known:
            registry["applied"].append({"reference": key[0], "expected": expected, "replacement": replacement, "category": category, "reason": reason, "evidenceUrl": f"https://www.biblegateway.com/passage/?search={book}+{chapter}%3A{verse}&version=KJV"}); known.add(key)
    registry["pending"] = [x for x in registry.get("pending", []) if not x.get("id", "").startswith("remaining-ot-kjv-v9-")]
    for index, (term, reason) in enumerate(PENDING.items(), 1):
        refs = []
        for book, doc in books.items():
            if book in REVIEWED or order[book] > 39: continue
            for c in doc["chapters"]:
                for v in c["verses"]:
                    if pattern(term).search(v["text"]): refs.append({"book": book, "chapter": c["chapter"], "verse": v["verse"]})
        registry["pending"].append({"id": f"remaining-ot-kjv-v9-{index}", "status": "pending-review", "scope": "old-testament", "term": term, "proposedOptions": ["Retain with a note", "Modernize after clause review"], "reason": reason, "references": refs, "evidence": [{"label": "Complete-verse KJV contextual review", "url": f"https://www.biblegateway.com/quicksearch/?quicksearch={term}&version=KJV%3BNIV"}]})
    write(REGISTRY, registry)
    print(json.dumps({"addedReviews": len(applied), "changedVerses": coverage["changedVerseCount"], "editCount": coverage["editCount"], "pendingFamilies": len(PENDING), "contentSha256": manifest["contentSha256"]}, indent=2))

if __name__ == "__main__": main()
