import gzip
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"
VERSION = 8


# Each family has a stable meaning throughout Joshua. Ambiguous theological
# terms and pronoun-system changes remain outside this list.
UNIFORM = [
    ("king thereof", "its king", "archaic-relative", "The phrase means its king."),
    ("foundation thereof", "its foundation", "archaic-relative", "The phrase means its foundation."),
    ("families thereof", "its families", "archaic-relative", "The phrase means its families."),
    ("spoil thereof", "its spoil", "archaic-relative", "The phrase means its spoil."),
    ("cattle thereof", "its cattle", "archaic-relative", "The phrase means its cattle."),
    ("men thereof", "its men", "archaic-relative", "The phrase means its men."),
    ("cities thereof", "its cities", "archaic-relative", "The phrase means its cities."),
    ("border thereof", "its border", "archaic-relative", "The phrase means its border."),
    ("goings out thereof", "its outgoings", "archaic-relative", "The phrase identifies where that border ends."),
    ("outgoings thereof", "its outgoings", "archaic-relative", "The phrase identifies where that border ends."),
    ("suburbs thereof", "its pasturelands", "archaic-relative", "The phrase refers to the city's pasturelands."),
    ("villages thereof", "its villages", "archaic-relative", "The phrase refers to the villages belonging to that territory."),
    ("other half thereof", "its other half", "archaic-relative", "The phrase refers to the other half of the tribe."),
    ("heard thereof", "heard of it", "archaic-relative", "The phrase means heard of it."),
    ("nigh", "near", "archaic-location", "Nigh means near."),
    ("whither", "where", "archaic-location", "Whither asks where someone went."),
    ("thither", "there", "archaic-location", "Thither means to that place."),
    ("whence", "where", "archaic-location", "Whence means from where; the source clauses already contain from."),
    ("wherein", "in which", "archaic-relative", "Wherein means in which."),
    ("wherewith", "with which", "archaic-relative", "Wherewith means with which."),
    ("thereof", "of it", "archaic-relative", "Thereof means of it."),
    ("therein", "in it", "archaic-relative", "Therein means in it."),
    ("thereon", "on it", "archaic-relative", "Thereon means on it."),
    ("hither", "here", "archaic-location", "Hither means to this place."),
    ("hence", "here", "archaic-location", "Hence means from here in this departure phrase."),
    ("hitherto", "until now", "archaic-time", "Hitherto means until now."),
    ("peradventure", "perhaps", "archaic-adverb", "Peradventure means perhaps."),
    ("bade", "commanded", "archaic-verb", "Bade means commanded in Joshua's obedience to the LORD."),
    ("slew", "killed", "archaic-battle-verb", "Slew means killed."),
    ("waxed", "grew", "archaic-verb", "Waxed means grew in the description of Joshua's age."),
    ("ass", "donkey", "archaic-animal-name", "Ass is the historical name for a donkey."),
    ("asses", "donkeys", "archaic-animal-name", "Asses is the historical plural for donkeys."),
    ("victuals", "provisions", "archaic-food-term", "Victuals means provisions for a journey."),
    ("raiment", "clothing", "archaic-clothing-term", "Raiment means clothing."),
    ("harlot", "prostitute", "archaic-person-term", "Harlot is the historical term used for Rahab's occupation."),
    ("coast", "border", "false-friend-geography", "Coast denotes a territorial border in Joshua, not only a shoreline."),
    ("coasts", "borders", "false-friend-geography", "Coasts denotes territorial borders or regions in Joshua."),
    ("goodly", "fine", "archaic-adjective", "Goodly describes a fine Babylonian garment."),
    ("reproach", "disgrace", "archaic-noun", "Reproach means disgrace in the declaration about Egypt."),
    ("rereward", "rear guard", "obsolete-military-term", "Rereward means the rear guard of the procession."),
    ("midst", "middle", "archaic-location", "Midst means middle."),
    ("dwelt", "lived", "archaic-residence-verb", "Dwelt means lived or resided."),
    ("abode", "stayed", "archaic-residence-verb", "Abode means stayed."),
    ("smote", "struck", "archaic-battle-verb", "Smote means struck; complete-clause exceptions are handled separately."),
    ("unwittingly", "unintentionally", "archaic-legal-adverb", "Unwittingly means without intent in the refuge-city law."),
    ("suburbs", "pasturelands", "false-friend-land-term", "Suburbs denotes pasturelands surrounding the Levitical cities."),
    ("nether", "lower", "archaic-geographic-term", "Nether means lower in these place descriptions."),
    ("beforetime", "formerly", "archaic-time", "Beforetime means formerly."),
    ("uttermost", "farthest", "archaic-geographic-term", "Uttermost means farthest or outermost in the boundary description."),
]


CHANGES = [
    (3, 5, "to morrow", "tomorrow", "archaic-time-phrase", "The two-word historical spelling is modernized."),
    (5, 11, "on the morrow", "the next day", "archaic-time-phrase", "On the morrow means the next day."),
    (5, 12, "on the morrow", "the next day", "archaic-time-phrase", "On the morrow means the next day."),
    (7, 13, "against to morrow", "for tomorrow", "archaic-time-phrase", "The command prepares the people for the next day's assembly."),
    (11, 6, "to morrow about this time", "tomorrow about this time", "archaic-time-phrase", "The two-word historical spelling is modernized."),
    (22, 18, "to morrow", "tomorrow", "archaic-time-phrase", "The two-word historical spelling is modernized."),
    (6, 22, "bring out thence the woman", "bring the woman out from there", "archaic-location-phrase", "Thence means from that house; the clause is reordered for current English."),
    (15, 4, "From thence", "From there", "archaic-location", "Thence means from there."),
    (15, 14, "drove thence", "drove from there", "archaic-location", "Thence means from that place."),
    (15, 15, "went up thence", "went up from there", "archaic-location", "Thence means from that place."),
    (18, 13, "from thence", "from there", "archaic-location", "Thence means from there."),
    (18, 14, "drawn thence", "drawn from there", "archaic-location", "Thence means from that point."),
    (19, 13, "from thence", "from there", "archaic-location", "Thence means from there."),
    (19, 34, "from thence", "from there", "archaic-location", "Thence means from there."),
    (9, 7, "Peradventure", "Perhaps", "archaic-adverb", "Peradventure means perhaps."),
    (5, 9, "Wherefore the name", "Therefore the name", "archaic-connector", "Wherefore introduces the resulting place name."),
    (7, 5, "wherefore the hearts", "therefore the hearts", "archaic-connector", "Wherefore introduces the result of Israel's defeat."),
    (7, 7, "wherefore hast thou", "why hast thou", "archaic-question", "Wherefore asks why in Joshua's lament."),
    (7, 10, "wherefore liest thou", "why liest thou", "archaic-question", "Wherefore asks why Joshua remains on his face."),
    (7, 26, "Wherefore the name", "Therefore the name", "archaic-connector", "Wherefore introduces the resulting place name."),
    (9, 11, "Wherefore our elders", "Therefore our elders", "archaic-connector", "Wherefore introduces the elders' response."),
    (9, 22, "Wherefore have ye beguiled us", "Why have ye deceived us", "archaic-question", "Wherefore asks why, and beguiled means deceived."),
    (10, 3, "Wherefore Adoni-zedek", "Therefore Adoni-zedek", "archaic-connector", "Wherefore introduces the king's response to the preceding news."),
    (6, 26, "Joshua adjured them", "Joshua bound them under oath", "archaic-oath-verb", "Adjured means to bind solemnly under oath."),
    (6, 3, "compass the city", "march around the city", "archaic-military-verb", "Compass means march around the city."),
    (6, 4, "compass the city", "march around the city", "archaic-military-verb", "Compass means march around the city."),
    (6, 7, "compass the city", "march around the city", "archaic-military-verb", "Compass means march around the city."),
    (15, 3, "fetched a compass to Karkaa", "turned toward Karkaa", "archaic-geographic-phrase", "Fetched a compass describes the boundary turning toward Karkaa."),
    (10, 10, "discomfited them", "threw them into confusion", "obsolete-battle-verb", "Discomfited means threw the enemy into confusion before Israel."),
    (7, 15, "wrought folly in Israel", "committed a disgraceful act in Israel", "archaic-moral-phrase", "Wrought folly describes a disgraceful act against the covenant community."),
    (14, 7, "to espy out the land", "to explore the land", "archaic-exploration-verb", "Espy out means explore in the mission from Kadesh-barnea."),
    (13, 30, "threescore cities", "sixty cities", "archaic-number", "Threescore equals sixty."),
    (14, 10, "fourscore and five years old", "eighty-five years old", "archaic-number", "Fourscore and five equals eighty-five."),
    (11, 13, "save Hazor only", "except Hazor only", "archaic-exception", "Save means except in this comparison of cities."),
    (11, 19, "save the Hivites", "except the Hivites", "archaic-exception", "Save means except in this statement about peace."),
    (14, 4, "save cities to dwell in", "except cities to live in", "archaic-exception", "Save means except, and dwell means live in this allocation."),
    (7, 12, "except ye destroy", "unless ye destroy", "archaic-condition", "Except means unless in this condition."),
    (5, 11, "old corn", "old grain", "false-friend-food-term", "Corn denotes grain rather than modern maize."),
    (5, 11, "parched corn", "parched grain", "false-friend-food-term", "Corn denotes grain rather than modern maize."),
    (5, 12, "old corn", "old grain", "false-friend-food-term", "Corn denotes grain rather than modern maize."),
    (22, 23, "meat offering", "grain offering", "false-friend-offering-term", "Meat offering is the historical name for a grain offering."),
    (22, 29, "meat offerings", "grain offerings", "false-friend-offering-term", "Meat offering is the historical name for a grain offering."),
    (22, 5, "cleave unto him", "remain faithful to him", "archaic-covenant-verb", "Cleave unto the LORD means remain faithfully attached to him."),
    (23, 8, "cleave unto the LORD", "remain faithful to the LORD", "archaic-covenant-verb", "Cleave unto the LORD means remain faithful to him."),
    (23, 12, "cleave unto the remnant of these nations", "join the remnant of these nations", "archaic-alliance-verb", "Cleave means join in the warning against alliances and intermarriage."),
    (7, 5, "smote of them about thirty and six men", "killed about thirty-six of them", "archaic-battle-phrase", "The clause reports approximately thirty-six Israelite deaths."),
    (9, 18, "smote them not", "did not attack them", "archaic-battle-verb", "Israel refrained from attacking the Gibeonites because of the oath."),
    (10, 10, "smote them to Azekah", "struck them down as far as Azekah", "archaic-battle-phrase", "The pursuit and defeat continued as far as Azekah."),
    (10, 40, "Joshua smote all the country", "Joshua conquered all the country", "archaic-battle-verb", "Smote describes Joshua's conquest of the region."),
    (10, 41, "Joshua smote them from Kadesh-barnea", "Joshua defeated them from Kadesh-barnea", "archaic-battle-verb", "Smote describes military defeat across the named region."),
    (12, 1, "which the children of Israel smote", "whom the children of Israel defeated", "archaic-battle-verb", "Smote describes the defeat of the kings."),
    (12, 7, "which Joshua and the children of Israel smote", "whom Joshua and the children of Israel defeated", "archaic-battle-verb", "Smote describes the defeat of the kings."),
    (13, 21, "whom Moses smote", "whom Moses defeated", "archaic-battle-verb", "Smote describes Moses' defeat of Sihon and the Midianite leaders."),
    (20, 5, "he smote his neighbour unwittingly", "he killed his neighbour unintentionally", "archaic-legal-phrase", "The refuge law concerns an unintentional killing."),
    (18, 5, "Judah shall abide in their coast on the south, and the house of Joseph shall abide in their coasts on the north", "Judah shall remain in their territory on the south, and the house of Joseph shall remain in their territory on the north", "false-friend-geography", "Coast means tribal territory in this allocation, and abide means remain."),
    (9, 1, "in all the coasts of the great sea", "throughout all the regions along the great sea", "false-friend-geography", "Coasts refers to the regions along the Mediterranean."),
    (10, 19, "suffer them not to enter into their cities", "do not allow them to enter their cities", "archaic-permission-verb", "Suffer means allow in this pursuit command."),
]


PENDING = [
    (6, 17, "accursed / accursed thing", "The phrase combines devotion to the LORD with destruction and should be modernized as one coherent passage."),
    (7, 1, "trespass in the accursed thing", "The covenant offense and the devoted property must be explained together rather than by isolated word replacement."),
    (10, 12, "Sun, stand thou still upon Gibeon", "The poetic and cosmological wording should remain intact unless an explanatory note is approved."),
    (15, 18, "a south land", "The request concerns dry land and water sources; the exact modern wording needs a full-clause review."),
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def offsets(text, expected):
    pattern = rf"(?<![A-Za-z]){re.escape(expected)}(?![A-Za-z])" if expected.isalpha() else re.escape(expected)
    return [m.start() for m in re.finditer(pattern, text)]


def main():
    base = read(CORPUS / "books/JOS.json")
    texts = {(c["chapter"], v["verse"]): v["text"] for c in base["chapters"] for v in c["verses"]}
    direction_path = DIRECTION / "books/jos_reading_2026.kjv.v1.json"
    direction = read(direction_path)
    expanded = list(CHANGES)
    for expected, replacement, category, reason in UNIFORM:
        for (chapter, verse), text in texts.items():
            if offsets(text, expected):
                expanded.append((chapter, verse, expected, replacement, category, reason))

    added = []
    for chapter, verse, expected, replacement, category, reason in expanded:
        text = texts[(chapter, verse)]
        matches = offsets(text, expected)
        if not matches:
            raise RuntimeError(f"Missing JOS.{chapter}.{verse}: {expected!r}")
        for start in matches:
            end = start + len(expected)
            patch = next((x for x in direction["verses"] if x["chapter"] == chapter and x["verse"] == verse), None)
            if patch is None:
                patch = {"chapter": chapter, "verse": verse, "sourceTextSha256": sha(text.encode()), "edits": []}
                direction["verses"].append(patch)
            overlap = next((e for e in patch["edits"] if start < e["endOffset"] and end > e["startOffset"]), None)
            if overlap:
                if overlap["startOffset"] == start and overlap["endOffset"] == end and overlap["replacement"] == replacement:
                    continue
                if expected in overlap["expected"]:
                    continue
                if overlap["expected"] in expected:
                    patch["edits"].remove(overlap)
                else:
                    raise RuntimeError(f"Overlap JOS.{chapter}.{verse}: {expected!r} / {overlap['expected']!r}")
            patch["edits"].append({
                "startOffset": start, "endOffset": end, "expected": expected, "replacement": replacement,
                "category": category, "reason": reason,
                "evidence": [{"label": "Complete-verse KJV contextual review", "url": f"https://www.biblegateway.com/passage/?search=Joshua+{chapter}%3A{verse}&version=KJV%3BNIV"}],
            })
            patch["edits"].sort(key=lambda x: x["startOffset"])
            added.append((chapter, verse, expected, replacement, category, reason))

    direction["verses"].sort(key=lambda x: (x["chapter"], x["verse"]))
    direction["editorialStatus"] = "approved-joshua-complete-context-v8"
    direction["ownerReview"] = {"contentVersion": VERSION, "review": "KJV Joshua complete-context review", "requiredFullTest": True}
    write(direction_path, direction)

    source_path = DIRECTION / "reading_2026.package-source.json"
    source = read(source_path)
    source["contentVersion"] = VERSION
    source["generatedAt"] = "2026-09-12T06:30:00.000Z"
    source["editorialPolicy"]["version"] = VERSION
    write(source_path, source)

    order = {read(path)["book"]: read(path)["order"] for path in (CORPUS / "books").glob("*.json")}
    books = [read(path) for path in (DIRECTION / "books").glob("*.json")]
    books.sort(key=lambda book: order[book["book"]])
    payload = {"books": books, "contentVersion": VERSION, "editorialPolicy": source["editorialPolicy"], "filterId": source["filterId"], "format": "shine-reading-filter-package", "normalizationId": source["normalizationId"], "schemaVersion": 1, "sourceCorpusSha256": source["sourceCorpusSha256"], "sourceVersionId": source["sourceVersionId"]}
    raw = canonical(payload).encode()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    packages = DIRECTION / "packages"
    (packages / "reading_2026.kjv.v1.package.json.gz").write_bytes(compressed)
    coverage = {"expectedBookCount": 66, "includedBookCount": len(books), "changedVerseCount": sum(len(book["verses"]) for book in books), "editCount": sum(len(verse["edits"]) for book in books for verse in book["verses"])}
    files = list((DIRECTION / "books").glob("*.json"))
    manifest = {
        "format": "shine-reading-filter-manifest", "filterId": source["filterId"], "schemaVersion": 1,
        "contentVersion": VERSION, "sourceVersionId": source["sourceVersionId"], "sourceCorpusSha256": source["sourceCorpusSha256"],
        "normalizationId": source["normalizationId"], "contentSha256": sha(compressed), "sizeBytes": len(compressed),
        "expandedSizeBytes": len(raw), "mimeType": "application/vnd.shine.reading-filter+gzip", "generatedAt": "2026-09-12",
        "editorialPolicy": source["editorialPolicy"], "coverage": coverage,
        "books": [{"id": book["book"], "order": order[book["book"]], "sourceFile": next(path.name for path in files if read(path)["book"] == book["book"]), "sourceContentSha256": book["sourceContentSha256"], "payloadSha256": sha(canonical(book).encode()), "changedVerseCount": len(book["verses"]), "editCount": sum(len(v["edits"]) for v in book["verses"])} for book in books],
    }
    write(packages / "reading_2026.kjv.v1.manifest.json", manifest)

    registry = read(REGISTRY)
    registry["updatedAt"] = "2026-09-12T06:30:00.000Z"
    registry["activeContentVersion"] = VERSION
    known = {(item["reference"], item["expected"], item["replacement"]) for item in registry["applied"]}
    for chapter, verse, expected, replacement, category, reason in added:
        key = (f"JOS.{chapter}.{verse}", expected, replacement)
        if key not in known:
            registry["applied"].append({"reference": key[0], "expected": expected, "replacement": replacement, "category": category, "reason": reason, "evidenceUrl": f"https://www.biblegateway.com/passage/?search=Joshua+{chapter}%3A{verse}&version=KJV"})
            known.add(key)
    registry["pending"] = [item for item in registry.get("pending", []) if not item.get("id", "").startswith("joshua-kjv-v8-")]
    for index, (chapter, verse, term, reason) in enumerate(PENDING, 1):
        registry["pending"].append({"id": f"joshua-kjv-v8-{index}", "status": "pending-review", "scope": "old-testament", "term": term, "proposedOptions": ["Retain with a note", "Modernize after textual review"], "reason": reason, "references": [{"book": "JOS", "chapter": chapter, "verse": verse}], "evidence": [{"label": "Complete-verse KJV contextual review", "url": f"https://www.biblegateway.com/passage/?search=Joshua+{chapter}%3A{verse}&version=KJV%3BNIV"}]})
    write(REGISTRY, registry)
    print(json.dumps({"added": len(added), "joshuaChangedVerses": len(direction["verses"]), "joshuaEdits": sum(len(v["edits"]) for v in direction["verses"]), "pending": len(PENDING), "contentSha256": manifest["contentSha256"]}, indent=2))


if __name__ == "__main__":
    main()
