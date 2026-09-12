import gzip
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"
VERSION = 7


# Every occurrence of these forms was read in Deuteronomy.  Only classes whose
# meaning stays stable in this book are uniform; ambiguous imagery and species
# remain outside this table.
UNIFORM = [
    ("nigh", "near", "archaic-location", "Nigh means near."),
    ("wroth", "angry", "archaic-emotion", "Wroth means angry."),
    ("abode", "remained", "archaic-verb", "Abode means remained."),
    ("whither", "where", "archaic-location", "Whither means where in a destination clause."),
    ("thither", "there", "archaic-location", "Thither means to that place."),
    ("whereunto", "to which", "archaic-relative", "Whereunto means to which."),
    ("whereby", "by which", "archaic-relative", "Whereby means by which."),
    ("wherewith", "with which", "archaic-relative", "Wherewith means with which."),
    ("thereunto", "to it", "archaic-relative", "Thereunto means to it."),
    ("therein", "in it", "archaic-relative", "Therein means in it or in that place."),
    ("thereof", "of it", "archaic-relative", "Thereof means of it."),
    ("wherein", "in which", "archaic-relative", "Wherein means in which."),
    ("therewith", "with it", "archaic-relative", "Therewith means with it."),
    ("thereon", "on it", "archaic-relative", "Thereon means on it."),
    ("thereto", "to it", "archaic-relative", "Thereto means to it."),
    ("raiment", "clothing", "archaic-noun", "Raiment means clothing."),
    ("fenced", "fortified", "false-friend", "Fenced means fortified by defensive walls."),
    ("manservant", "male servant", "archaic-household-term", "Manservant means male servant."),
    ("maidservant", "female servant", "archaic-household-term", "Maidservant means female servant."),
    ("damsel", "young woman", "archaic-person-term", "Damsel means young woman."),
    ("bondman", "slave", "archaic-status-term", "Bondman denotes a male slave in the Egypt reminder."),
    ("stranger", "foreigner", "archaic-residency-term", "Stranger denotes a foreigner living among or outside Israel."),
    ("at even", "in the evening", "archaic-time", "Even means evening."),
    ("usury", "interest", "false-friend-finance", "Usury here means interest on a loan, not only an excessive rate."),
    ("straitness", "distress", "archaic-siege-term", "Straitness means severe distress during a siege."),
    ("ass", "donkey", "archaic-animal-name", "Ass is the historical name for a donkey."),
    ("groves", "Asherah poles", "false-friend-idolatry", "Groves translates cultic Asherah objects, not ordinary groups of trees."),
    ("bedstead", "bed", "archaic-object", "Bedstead means bed."),
    ("every whit", "completely", "archaic-adverb", "Every whit means completely."),
    ("lusteth after", "desires", "archaic-verb", "Lusteth after means desires in this food permission."),
]


CHANGES = [
    (1, 7, "nigh thereunto", "near it", "archaic-location", "The phrase means near that mountain region."),
    (1, 19, "great and terrible wilderness", "great and terrifying wilderness", "false-friend", "Terrible describes a frightening wilderness."),
    (1, 28, "Whither shall we go up?", "Where shall we go up?", "archaic-question", "Whither asks where they can go."),
    (2, 4, "the coast of your brethren", "the territory of your brethren", "false-friend-geography", "Coast means territory, not shoreline."),
    (2, 18, "the coast of Moab", "the border of Moab", "false-friend-geography", "Coast means the border region."),
    (2, 33, "we smote him, and his sons, and all his people", "we defeated him, his sons, and all his people", "archaic-battle-verb", "Smote describes defeating the king and his people in battle."),
    (3, 3, "we smote him until none was left to him remaining", "we defeated him until none of his people remained", "archaic-battle-verb", "The complete clause describes total military defeat."),
    (3, 4, "threescore cities", "sixty cities", "archaic-number", "Threescore equals sixty."),
    (3, 17, "Jordan, and the coast thereof", "Jordan and its border", "false-friend-geography", "Coast denotes the territorial boundary along the Jordan."),
    (3, 25, "that goodly mountain", "that beautiful mountain", "archaic-adjective", "Goodly means beautiful or desirable here."),
    (4, 2, "neither shall ye diminish ought from it", "neither shall ye diminish anything from it", "archaic-pronoun", "Ought means anything in this prohibition."),
    (4, 42, "kill his neighbour unawares", "kill his neighbour unintentionally", "archaic-legal-adverb", "Unawares means unintentionally in the refuge-city law."),
    (4, 29, "from thence", "from there", "archaic-location", "Thence means from there."),
    (5, 14, "thine ass", "thy donkey", "archaic-animal-and-grammar", "The noun is modernized while retaining correct singular KJV possessive grammar."),
    (5, 15, "brought thee out thence", "brought thee out from there", "archaic-location", "Thence means from there."),
    (6, 10, "great and goodly cities", "great and beautiful cities", "archaic-adjective", "Goodly means beautiful or desirable here."),
    (6, 23, "brought us out from thence", "brought us out from there", "archaic-location", "Thence means from there."),
    (7, 12, "Wherefore it shall come to pass", "Therefore it shall come to pass", "archaic-connector", "Wherefore has the result sense therefore here."),
    (7, 19, "The great temptations", "The great trials", "false-friend", "Temptations means trials or tests witnessed in Egypt."),
    (7, 21, "a mighty God and terrible", "a mighty and awe-inspiring God", "false-friend-divine-description", "Terrible means inspiring reverent fear, not morally bad."),
    (8, 4, "Thy raiment waxed not old upon thee", "Thy clothing did not wear out upon thee", "archaic-verb-phrase", "Waxed not old means did not wear out."),
    (8, 9, "eat bread without scarceness", "eat bread without shortage", "archaic-noun", "Scarceness means shortage."),
    (8, 12, "goodly houses", "fine houses", "archaic-adjective", "Goodly describes fine houses."),
    (8, 15, "great and terrible wilderness", "great and terrifying wilderness", "false-friend", "Terrible describes a frightening wilderness."),
    (9, 19, "hot displeasure, wherewith the LORD was wroth", "great anger, with which the LORD was angry", "archaic-emotion-phrase", "Hot displeasure and wroth describe great anger."),
    (9, 12, "from hence", "from here", "archaic-location", "Hence means here in this departure command."),
    (9, 28, "the land whence thou broughtest us out", "the land from which thou broughtest us out", "archaic-relative", "Whence means from which place."),
    (10, 7, "From thence", "From there", "archaic-location", "Thence means from there."),
    (10, 17, "a mighty, and a terrible", "mighty and awe-inspiring", "false-friend-divine-description", "Terrible means awe-inspiring in this description of God."),
    (10, 17, "taketh reward", "accepts bribes", "false-friend-legal-term", "Reward means a bribe in the impartial-judgment clause."),
    (10, 21, "great and terrible things", "great and awesome things", "false-friend", "Terrible describes awe-inspiring acts witnessed by Israel."),
    (10, 22, "threescore and ten persons", "seventy persons", "archaic-number", "Threescore and ten equals seventy."),
    (11, 24, "shall your coast be", "shall your border be", "false-friend-geography", "Coast means territorial border."),
    (11, 10, "from whence", "from where", "archaic-relative", "Whence means from where."),
    (14, 2, "a peculiar people unto himself", "a people who are his special possession", "false-friend-covenant-term", "Peculiar means specially possessed, not strange."),
    (14, 21, "seethe a kid", "boil a young goat", "archaic-cooking-verb", "Seethe means boil; kid here is a young goat."),
    (15, 2, "lendeth ought", "lends anything", "archaic-pronoun", "Ought means anything."),
    (15, 17, "take an aul", "take an awl", "archaic-spelling", "Aul is the historical spelling of awl."),
    (16, 4, "in all thy coast", "throughout all thy territory", "false-friend-geography", "Coast means the whole territory."),
    (17, 1, "any evilfavouredness", "any serious defect", "obsolete-description", "Evilfavouredness means an unacceptable physical defect."),
    (19, 3, "divide the coasts of thy land", "divide the territory of thy land", "false-friend-geography", "Coasts means the territorial area divided for refuge cities."),
    (19, 4, "killeth his neighbour ignorantly", "kills his neighbour unintentionally", "false-friend-legal-adverb", "Ignorantly means without intent in this law."),
    (19, 7, "Wherefore I command thee", "Therefore I command thee", "archaic-connector", "Wherefore has the result sense therefore."),
    (19, 8, "enlarge thy coast", "enlarge thy territory", "false-friend-geography", "Coast means territory."),
    (19, 12, "fetch him thence", "fetch him from there", "archaic-location", "Thence means from there."),
    (22, 8, "make a battlement for thy roof", "make a parapet for thy roof", "obsolete-building-term", "A battlement here is a protective parapet around a flat roof."),
    (22, 8, "fall from thence", "fall from there", "archaic-location", "Thence means from there."),
    (22, 19, "amerce him in an hundred shekels", "fine him one hundred shekels", "obsolete-legal-verb", "Amerce means impose a monetary fine."),
    (22, 21, "hath wrought folly in Israel", "has committed a disgraceful act in Israel", "archaic-legal-phrase", "Wrought folly denotes a disgraceful act against the community."),
    (23, 13, "a paddle upon thy weapon", "a digging tool among thy equipment", "false-friend-camp-term", "Weapon denotes equipment here; the object is a digging tool."),
    (23, 13, "when thou wilt ease thyself abroad", "when thou relievest thyself outside", "archaic-euphemism", "The phrase describes using the designated place outside the camp."),
    (26, 14, "taken away ought thereof", "taken away anything from it", "archaic-pronoun", "Ought means anything."),
    (26, 14, "given ought thereof", "given anything from it", "archaic-pronoun", "Ought means anything."),
    (26, 18, "his peculiar people", "his special possession", "false-friend-covenant-term", "Peculiar means specially possessed, not strange."),
    (24, 18, "redeemed thee thence", "redeemed thee from there", "archaic-location", "Thence means from there."),
    (28, 31, "thine ass", "thy donkey", "archaic-animal-and-grammar", "The noun is modernized while retaining correct singular KJV possessive grammar."),
    (28, 52, "high and fenced walls", "high and fortified walls", "false-friend", "Fenced means fortified by defensive walls."),
    (29, 7, "we smote them", "we defeated them", "archaic-battle-verb", "Smote describes defeating the kings in battle."),
    (29, 24, "Wherefore hath the LORD done thus", "Why has the LORD done this", "archaic-question", "Wherefore asks why in this direct question."),
    (30, 14, "the word is very nigh unto thee", "the word is very near to thee", "archaic-location", "Nigh means near."),
    (30, 4, "from thence", "from there", "archaic-location", "Thence means from there."),
    (31, 16, "go a whoring after the gods of the strangers of the land", "be unfaithful by pursuing the gods of the foreigners in the land", "archaic-covenant-metaphor", "The phrase describes covenant unfaithfulness through idolatry."),
    (32, 15, "Jeshurun waxed fat", "Jeshurun grew fat", "archaic-verb", "Waxed means became or grew."),
    (32, 18, "the Rock that begat thee", "the Rock that gave thee birth", "archaic-birth-verb", "Begat describes giving birth within the parental metaphor for God."),
    (32, 20, "a very froward generation", "a very perverse generation", "archaic-adjective", "Froward means morally perverse or contrary."),
    (3, 11, "length thereof", "its length", "archaic-relative", "The phrase refers to the bed's length."),
    (3, 12, "the cities thereof", "its cities", "archaic-relative", "The phrase refers to the cities of that land."),
    (7, 25, "snared therein", "trapped by it", "archaic-relative", "The pronoun refers to the silver or gold taken from an idol."),
    (9, 21, "the dust thereof", "its dust", "archaic-relative", "The phrase refers to the calf's dust."),
    (12, 2, "all the places, wherein", "all the places where", "archaic-relative", "Wherein means where in this location clause."),
    (12, 15, "may eat thereof", "may eat it", "archaic-relative", "The pronoun refers to the permitted meat."),
    (13, 15, "the cattle thereof", "its cattle", "archaic-relative", "The phrase refers to the city's cattle."),
    (13, 16, "the street thereof", "its street", "archaic-relative", "The phrase refers to the city's street."),
    (13, 16, "the spoil thereof", "its spoil", "archaic-relative", "The phrase refers to the city's spoil."),
    (15, 23, "the blood thereof", "its blood", "archaic-relative", "The phrase refers to the animal's blood."),
    (16, 8, "do no work therein", "do no work on it", "archaic-relative", "The pronoun refers to the seventh day."),
    (17, 1, "sheep, wherein is blemish", "sheep that has a blemish", "archaic-relative", "The clause describes an animal that has a blemish."),
    (20, 11, "the people that is found therein", "the people found in it", "archaic-relative", "The phrase refers to the people in the city."),
    (20, 13, "every male thereof", "every male in it", "archaic-relative", "The phrase refers to every male in the city."),
    (20, 14, "the spoil thereof", "its spoil", "archaic-relative", "The phrase refers to the city's spoil."),
    (20, 19, "the trees thereof", "its trees", "archaic-relative", "The phrase refers to the city's trees."),
    (28, 30, "the grapes thereof", "its grapes", "archaic-relative", "The phrase refers to the vineyard's grapes."),
    (28, 31, "eat thereof", "eat of it", "archaic-relative", "The pronoun refers to the slaughtered ox."),
    (29, 11, "thy stranger", "the foreigner", "archaic-residency-term", "The phrase refers to the foreigner residing in the camp."),
    (29, 23, "the whole land thereof", "that whole land", "archaic-relative", "The phrase refers to the land under judgment."),
    (31, 12, "thy stranger", "the foreigner", "archaic-residency-term", "The phrase refers to the foreigner residing within the gates."),
    (33, 16, "fulness thereof", "its fullness", "archaic-relative", "The phrase refers to the earth's fullness."),
]


PENDING = [
    (12, 15, "roebuck / hart", "Ancient animal names may require gazelle/deer, but exact species identification should be settled consistently."),
    (23, 18, "price of a dog", "The cultic expression is disputed and should not be expanded into a specific sexual identification without textual review."),
    (32, 13, "high places of the earth", "The poetic image may mean heights or elevated land; retain it until its parallelism is reviewed."),
    (33, 29, "tread upon their high places", "The poetic military image should be retained or clarified consistently with its Hebrew parallel."),
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def whole_offsets(text, expected):
    pattern = rf"(?<![A-Za-z]){re.escape(expected)}(?![A-Za-z])" if expected.isalpha() else re.escape(expected)
    return [match.start() for match in re.finditer(pattern, text)]


base = read(CORPUS / "books/DEU.json")
texts = {(c["chapter"], v["verse"]): v["text"] for c in base["chapters"] for v in c["verses"]}
direction_path = DIRECTION / "books/deu_reading_2026.kjv.v1.json"
direction = read(direction_path)

expanded = list(CHANGES)
for expected, replacement, category, reason in UNIFORM:
    for (chapter, verse), verse_text in texts.items():
        if whole_offsets(verse_text, expected):
            expanded.append((chapter, verse, expected, replacement, category, reason))

added = []
for chapter, verse, expected, replacement, category, reason in expanded:
    text = texts[(chapter, verse)]
    matches = whole_offsets(text, expected)
    if not matches:
        raise RuntimeError(f"Missing DEU.{chapter}.{verse}: {expected!r}")
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
                raise RuntimeError(f"Overlap DEU.{chapter}.{verse}: {expected!r} / {overlap['expected']!r}")
        patch["edits"].append({
            "startOffset": start, "endOffset": end, "expected": expected, "replacement": replacement,
            "category": category, "reason": reason,
            "evidence": [{"label": "Complete-verse KJV and NIV contextual review", "url": f"https://www.biblegateway.com/passage/?search=Deuteronomy+{chapter}%3A{verse}&version=KJV%3BNIV"}],
        })
        patch["edits"].sort(key=lambda x: x["startOffset"])
        added.append((chapter, verse, expected, replacement, category, reason))

direction["verses"].sort(key=lambda x: (x["chapter"], x["verse"]))
direction["editorialStatus"] = "approved-deuteronomy-complete-context-v7"
direction["ownerReview"] = {"contentVersion": VERSION, "review": "KJV Deuteronomy complete-context review", "requiredFullTest": True}
write(direction_path, direction)

source_path = DIRECTION / "reading_2026.package-source.json"
source = read(source_path)
source["contentVersion"] = VERSION
source["generatedAt"] = "2026-09-12T00:00:00.000Z"
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
    "contentVersion": VERSION, "sourceVersionId": source["sourceVersionId"],
    "sourceCorpusSha256": source["sourceCorpusSha256"], "normalizationId": source["normalizationId"],
    "contentSha256": sha(compressed), "sizeBytes": len(compressed), "expandedSizeBytes": len(raw),
    "mimeType": "application/vnd.shine.reading-filter+gzip", "generatedAt": "2026-09-12",
    "editorialPolicy": source["editorialPolicy"], "coverage": coverage,
    "books": [{
        "id": book["book"], "order": order[book["book"]],
        "sourceFile": next(path.name for path in files if read(path)["book"] == book["book"]),
        "sourceContentSha256": book["sourceContentSha256"],
        "payloadSha256": sha(canonical(book).encode()),
        "changedVerseCount": len(book["verses"]),
        "editCount": sum(len(v["edits"]) for v in book["verses"]),
    } for book in books],
}
write(packages / "reading_2026.kjv.v1.manifest.json", manifest)

registry = read(REGISTRY)
registry["updatedAt"] = "2026-09-12T00:00:00.000Z"
registry["activeContentVersion"] = VERSION
known = {(item["reference"], item["expected"], item["replacement"]) for item in registry["applied"]}
for chapter, verse, expected, replacement, category, reason in added:
    if (f"DEU.{chapter}.{verse}", expected, replacement) not in known:
        registry["applied"].append({"reference": f"DEU.{chapter}.{verse}", "expected": expected, "replacement": replacement, "category": category, "reason": reason, "evidenceUrl": f"https://www.biblegateway.com/passage/?search=Deuteronomy+{chapter}%3A{verse}&version=KJV"})
        known.add((f"DEU.{chapter}.{verse}", expected, replacement))
registry["pending"] = [item for item in registry.get("pending", []) if not item.get("id", "").startswith("deuteronomy-kjv-v7-")]
for index, (chapter, verse, term, reason) in enumerate(PENDING, 1):
    registry["pending"].append({"id": f"deuteronomy-kjv-v7-{index}", "status": "pending-review", "scope": "old-testament", "term": term, "proposedOptions": ["Retain with a note", "Modernize after textual review"], "reason": reason, "references": [{"book": "DEU", "chapter": chapter, "verse": verse}], "evidence": [{"label": "Complete-verse KJV and NIV contextual review", "url": f"https://www.biblegateway.com/passage/?search=Deuteronomy+{chapter}%3A{verse}&version=KJV%3BNIV"}]})
write(REGISTRY, registry)

print(json.dumps({"added": len(added), "deuteronomyChangedVerses": len(direction["verses"]), "deuteronomyEdits": sum(len(v["edits"]) for v in direction["verses"]), "pending": len(PENDING), "contentSha256": manifest["contentSha256"]}, indent=2))
