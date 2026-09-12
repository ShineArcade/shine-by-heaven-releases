import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"
BOOK = "NUM"
VERSION = 6


# These classes were reviewed across every occurrence in Numbers. They are
# uniform objects, units, or lexical false friends in this book. The generator
# still emits one traceable record for every verse occurrence.
UNIFORM = [
    ("meat offering", "grain offering", "false-friend-offering", "Meat in this sacrificial formula means a grain offering, not animal flesh."),
    ("sweet savour", "pleasing aroma", "archaic-offering-phrase", "Sweet savour describes an aroma acceptable to the LORD."),
    ("candlestick", "lampstand", "false-friend-object", "The sanctuary object is an oil lampstand, not a wax-candle holder."),
    ("shewbread", "bread of the Presence", "archaic-liturgical-term", "Shewbread is the bread displayed before the LORD."),
    ("staves", "poles", "archaic-object", "Staves are the carrying poles for sanctuary objects."),
    ("vail", "veil", "archaic-spelling", "Vail is the historical spelling of veil."),
    ("basons", "basins", "archaic-spelling", "Basons is the historical spelling of basins."),
    ("snuffdishes", "wick trays", "obsolete-object", "Snuffdishes held burned wick trimmings from the lamps."),
    ("brasen", "bronze", "archaic-material", "Brasen means made of bronze in this sanctuary context."),
    ("polls", "individuals", "archaic-census-term", "Polls means individual persons counted in the census."),
    ("the matrix", "the womb", "obsolete-anatomy", "Matrix is the historical anatomical term for womb."),
    ("fourscore", "eighty", "archaic-number", "Fourscore equals eighty."),
    ("peradventure", "perhaps", "archaic-adverb", "Peradventure means perhaps."),
    ("raiment", "clothing", "archaic-noun", "Raiment means clothing."),
    ("asses", "donkeys", "archaic-animal-name", "Asses is the historical plural of donkey."),
]


# Each phrase below was read in its complete verse. Whole phrases are used
# where changing a lone word could alter grammar, participants, or imagery.
CHANGES = [
    (1, 2, "by their polls", "individual by individual", "archaic-census-term", "The census counts each male individually."),
    (1, 51, "the tabernacle setteth forward", "the tabernacle sets out", "archaic-travel-phrase", "Setteth forward means begins its journey."),
    (1, 51, "the stranger that cometh nigh", "the unauthorized person who comes near", "archaic-legal-phrase", "Stranger here is an unauthorized outsider approaching the sacred work."),
    (3, 10, "the stranger that cometh nigh", "the unauthorized person who comes near", "archaic-legal-phrase", "Stranger here is an unauthorized outsider approaching the priestly office."),
    (3, 13, "the day that I smote", "the day that I struck", "archaic-verb", "Smote is the historical past tense of strike."),
    (3, 13, "I hallowed unto me", "I consecrated to myself", "archaic-religious-verb", "Hallowed here means set apart as holy for the LORD."),
    (3, 31, "the hanging", "the curtain", "archaic-sanctuary-object", "The hanging is the sanctuary curtain assigned to the Kohathites."),
    (3, 47, "five shekels apiece by the poll", "five shekels for each person", "archaic-census-phrase", "By the poll means for each counted person."),
    (4, 7, "covers to cover withal", "covers for covering them", "archaic-adverb", "Withal means with them in this equipment list."),
    (4, 16, "to the office of Eleazar the son of Aaron the priest pertaineth", "Eleazar son of Aaron the priest shall be responsible for", "archaic-grammar", "The clause assigns responsibility to Eleazar."),
    (4, 48, "eight thousand and five hundred and fourscore", "eight thousand five hundred eighty", "archaic-number", "Fourscore equals eighty in the census total."),
    (6, 10, "two turtles", "two turtledoves", "archaic-animal-name", "Turtles here means turtledoves, not reptiles."),
    (6, 19, "the sodden shoulder", "the boiled shoulder", "obsolete-cooking-verb", "Sodden means boiled."),
    (9, 7, "wherefore are we kept back", "why are we prevented", "archaic-question", "Wherefore asks why, and kept back means prevented."),
    (9, 13, "forbeareth to keep the passover", "fails to keep the Passover", "archaic-verb", "Forbeareth here means refrains from or fails to observe it."),
    (9, 16, "So it was alway", "So it was always", "archaic-adverb", "Alway is the historical form of always."),
    (9, 17, "where the cloud abode", "where the cloud remained", "archaic-verb", "Abode means remained."),
    (9, 18, "as long as the cloud abode", "as long as the cloud remained", "archaic-verb", "Abode means remained."),
    (9, 20, "they abode in their tents", "they remained in their tents", "archaic-verb", "Abode means remained."),
    (9, 21, "from even unto the morning", "from evening until morning", "archaic-time-phrase", "Even means evening in this time span."),
    (9, 21, "the cloud abode", "the cloud remained", "archaic-verb", "Abode means remained."),
    (9, 22, "the children of Israel abode in their tents", "the children of Israel remained in their tents", "archaic-verb", "Abode means remained."),
    (11, 11, "Wherefore hast thou afflicted thy servant? and wherefore have I not found favour in thy sight, that thou layest", "Why have you afflicted your servant? And why have I not found favor in your sight, that you lay", "archaic-question", "Both linked questions are modernized together so the singular address remains consistent."),
    (11, 12, "as a nursing father beareth the sucking child", "as a nursing father carries an infant", "archaic-family-phrase", "Beareth means carries and sucking child means infant."),
    (11, 13, "Whence should I have flesh", "Where could I get meat", "archaic-question", "Whence asks where the meat could come from."),
    (11, 18, "against to morrow", "for tomorrow", "archaic-time-phrase", "Against to morrow means in preparation for tomorrow."),
    (11, 23, "Is the LORD’s hand waxed short? thou shalt see now whether my word shall come to pass unto thee or not.", "Has the LORD’s hand become too short? You shall now see whether my word comes to pass for you or not.", "opaque-idiom", "The whole reply is modernized consistently while retaining the verse's hand image."),
    (11, 30, "Moses gat him into the camp", "Moses returned to the camp", "archaic-movement-phrase", "Gat him into means went or returned to the camp."),
    (11, 33, "ere it was chewed", "before it was chewed", "archaic-conjunction", "Ere means before."),
    (11, 33, "the LORD smote the people", "the LORD struck the people", "archaic-verb", "Smote is the historical past tense of strike."),
    (11, 35, "and abode at Hazeroth", "and remained at Hazeroth", "archaic-verb", "Abode means remained."),
    (12, 8, "even apparently, and not in dark speeches", "clearly, and not in riddles", "opaque-revelation-phrase", "Apparently means clearly here, while dark speeches are riddles."),
    (12, 8, "the similitude of the LORD", "the form of the LORD", "archaic-noun", "Similitude means visible form or likeness in this verse."),
    (13, 20, "the firstripe grapes", "the early-ripening grapes", "obsolete-agriculture", "Firstripe means first ripe or early-ripening."),
    (13, 23, "they bare it between two", "two of them carried it", "archaic-verb", "Bare here means carried, not gave birth."),
    (14, 3, "And wherefore hath the LORD brought us", "And why has the LORD brought us", "archaic-question", "Wherefore asks why; the whole opening keeps the grammar consistent."),
    (14, 10, "the congregation bade stone them", "the congregation ordered that they be stoned", "archaic-verb", "Bade means ordered."),
    (14, 11, "how long will it be ere they believe me", "how long will it be before they believe me", "archaic-conjunction", "Ere means before."),
    (14, 18, "The LORD is longsuffering", "The LORD is patient", "archaic-divine-attribute", "Longsuffering means patient and slow to anger."),
    (14, 25, "To morrow turn you, and get you into the wilderness", "Tomorrow turn back and go into the wilderness", "archaic-time-and-grammar", "The complete travel command is modernized without changing its destination."),
    (14, 30, "save Caleb", "except Caleb", "archaic-exception", "Save means except."),
    (14, 40, "gat them up into the top", "went up to the top", "archaic-movement-phrase", "Gat them up means went up."),
    (14, 41, "Wherefore now do ye transgress", "Why are you now disobeying", "archaic-question", "Wherefore asks why and transgress here means disobey the command."),
    (14, 45, "smote them, and discomfited them", "struck them and defeated them", "obsolete-battle-verbs", "Smote means struck and discomfited means defeated."),
    (15, 24, "if ought be committed by ignorance", "if anything is done unintentionally", "archaic-legal-phrase", "Ought means anything and by ignorance describes an unintentional act."),
    (15, 30, "the soul that doeth ought presumptuously", "the person who does anything defiantly", "archaic-legal-phrase", "Soul means person, ought means anything, and presumptuously describes defiant intent."),
    (15, 38, "a ribband of blue", "a blue cord", "obsolete-clothing-term", "Ribband is a historical form of ribbon; the object is a cord on the fringe."),
    (15, 39, "go a whoring", "pursue unfaithfulness", "archaic-metaphor", "The phrase describes covenant unfaithfulness rather than ordinary travel."),
    (16, 5, "Even to morrow", "By tomorrow", "archaic-time-phrase", "To morrow is the historical spelling of tomorrow."),
    (16, 9, "Seemeth it but a small thing unto you, that the God of Israel hath separated you", "Is it a small thing to you that the God of Israel has separated you", "archaic-question", "The complete opening question is modernized together to avoid mixed grammar."),
    (16, 15, "Moses was very wroth", "Moses was very angry", "archaic-adjective", "Wroth means angry."),
    (16, 27, "they gat up from the tabernacle", "they moved away from the tabernacle", "archaic-movement-phrase", "Gat up here means withdrew from the surrounding area."),
    (16, 31, "the ground clave asunder", "the ground split apart", "obsolete-verb", "Clave asunder means split apart."),
    (16, 39, "the brasen censers", "the bronze censers", "archaic-material", "Brasen means made of bronze."),
    (16, 41, "on the morrow", "the next day", "archaic-time", "Morrow means the next day."),
    (16, 48, "the plague was stayed", "the plague was stopped", "archaic-verb", "Stayed means stopped in this plague account."),
    (16, 50, "the plague was stayed", "the plague was stopped", "archaic-verb", "Stayed means stopped in this plague account."),
    (17, 8, "on the morrow", "the next day", "archaic-time", "Morrow means the next day."),
    (17, 10, "quite take away their murmurings", "completely put an end to their complaints", "archaic-idiom", "Quite means completely; murmurings are complaints."),
    (19, 7, "until the even", "until evening", "archaic-time", "Even means evening."),
    (19, 8, "until the even", "until evening", "archaic-time", "Even means evening."),
    (19, 10, "until the even", "until evening", "archaic-time", "Even means evening."),
    (19, 21, "until even", "until evening", "archaic-time", "Even means evening."),
    (19, 22, "until even", "until evening", "archaic-time", "Even means evening."),
    (20, 1, "the people abode in Kadesh", "the people remained in Kadesh", "archaic-verb", "Abode means remained."),
    (20, 3, "the people chode with Moses", "the people quarreled with Moses", "obsolete-verb", "Chode is an old past tense meaning quarreled."),
    (20, 11, "he smote the rock twice", "he struck the rock twice", "archaic-verb", "Smote is the historical past tense of strike."),
    (20, 14, "all the travail that hath befallen us", "all the hardship that has come upon us", "false-friend", "Travail here means hardship, not childbirth."),
    (21, 5, "our soul loatheth this light bread", "we detest this miserable food", "archaic-idiom", "Soul represents the people themselves; light here means contemptible, not low-calorie."),
    (21, 23, "would not suffer Israel to pass", "would not allow Israel to pass", "false-friend", "Suffer here means allow."),
    (21, 24, "Israel smote him", "Israel struck him", "archaic-verb", "Smote is the historical past tense of strike."),
    (21, 35, "they smote him", "they struck him", "archaic-verb", "Smote is the historical past tense of strike."),
    (22, 6, "peradventure I shall prevail", "perhaps I shall prevail", "archaic-adverb", "Peradventure means perhaps."),
    (22, 7, "the rewards of divination", "the fees for divination", "false-friend-payment", "Rewards here are the payment carried to hire Balaam's divination."),
    (22, 8, "the princes of Moab abode with Balaam", "the leaders of Moab stayed with Balaam", "archaic-verb-and-title", "Abode means stayed; princes here are leaders or officials."),
    (22, 11, "peradventure I shall be able", "perhaps I shall be able", "archaic-adverb", "Peradventure means perhaps."),
    (22, 13, "refuseth to give me leave", "refuses to permit me", "archaic-permission-phrase", "Give me leave means permit me."),
    (22, 19, "tarry ye also here", "you also stay here", "archaic-verb", "Tarry means stay or wait."),
    (22, 21, "his ass", "his donkey", "archaic-animal-name", "Ass is the historical English name for a donkey."),
    (22, 22, "his ass", "his donkey", "archaic-animal-name", "Ass is the historical English name for a donkey."),
    (22, 23, "the ass", "the donkey", "archaic-animal-name", "Ass is the historical English name for a donkey."),
    (22, 25, "the ass", "the donkey", "archaic-animal-name", "Ass is the historical English name for a donkey."),
    (22, 27, "the ass", "the donkey", "archaic-animal-name", "Ass is the historical English name for a donkey."),
    (22, 28, "the mouth of the ass", "the donkey’s mouth", "archaic-animal-name", "Ass is the historical English name for a donkey."),
    (22, 29, "unto the ass", "to the donkey", "archaic-animal-name", "Ass is the historical English name for a donkey."),
    (22, 30, "the ass said", "the donkey said", "archaic-animal-name", "Ass is the historical English name for a donkey."),
    (22, 30, "Am not I thine ass, upon which thou hast ridden ever since I was thine unto this day? was I ever wont to do so unto thee?", "Am I not your donkey, which you have ridden ever since I became yours to this day? Have I ever been accustomed to doing this to you?", "archaic-animal-and-grammar", "The donkey's complete question is modernized together to keep the singular address coherent."),
    (22, 30, "Nay", "No", "archaic-response", "Nay is the historical negative response no."),
    (22, 32, "Wherefore hast thou smitten thine ass these three times?", "Why have you struck your donkey these three times?", "archaic-animal-and-grammar", "The complete question is modernized together to keep the singular address coherent."),
    (22, 32, "behold, I went out to withstand thee, because thy way is perverse before me", "behold, I came out to oppose you, because your way is perverse before me", "archaic-grammar", "The remainder of the reply is modernized consistently without changing its moral judgment."),
    (22, 33, "the ass saw me", "the donkey saw me", "archaic-animal-name", "Ass is the historical English name for a donkey."),
    (22, 41, "on the morrow", "the next day", "archaic-time", "Morrow means the next day."),
    (23, 3, "peradventure the LORD", "perhaps the LORD", "archaic-adverb", "Peradventure means perhaps."),
    (23, 18, "hearken unto me", "listen to me", "archaic-verb", "Hearken means listen."),
    (23, 22, "the strength of an unicorn", "the strength of a wild ox", "obsolete-animal-name", "Unicorn in this KJV passage represents a powerful wild bovine, not the modern mythical animal."),
    (23, 23, "What hath God wrought!", "What God has done!", "archaic-exclamation", "Wrought means done; the exclamation retains its praise."),
    (23, 27, "peradventure it will please God", "perhaps it will please God", "archaic-adverb", "Peradventure means perhaps."),
    (24, 5, "How goodly are thy tents, O Jacob, and thy tabernacles, O Israel!", "How beautiful are your tents, O Jacob, and your dwellings, O Israel!", "archaic-adjective-and-grammar", "The full parallel line is modernized together; tabernacles here means dwellings."),
    (24, 8, "the strength of an unicorn", "the strength of a wild ox", "obsolete-animal-name", "Unicorn here represents a powerful wild bovine."),
    (24, 14, "I will advertise thee what this people shall do to thy people", "I will tell you what this people shall do to your people", "false-friend", "Advertise here means tell or inform; both pronouns are modernized together."),
    (24, 17, "but not nigh", "but not near", "archaic-adverb", "Nigh means near."),
    (25, 1, "Israel abode in Shittim", "Israel remained in Shittim", "archaic-verb", "Abode means remained; Shittim is a place name and remains unchanged."),
    (25, 1, "commit whoredom", "commit sexual immorality", "archaic-sexual-term", "Whoredom is an archaic term for sexual immorality in this narrative."),
    (25, 8, "the plague was stayed", "the plague was stopped", "archaic-verb", "Stayed means stopped."),
    (25, 18, "they vex you with their wiles", "they harass you through their schemes", "archaic-phrase", "Vex means harass and wiles are deceptive schemes."),
    (26, 59, "whom her mother bare", "whom her mother bore", "archaic-verb", "Bare is the historical past tense of bear in childbirth."),
    (26, 59, "she bare unto Amram", "she bore to Amram", "archaic-verb", "Bare is the historical past tense of bear in childbirth."),
    (26, 65, "save Caleb", "except Caleb", "archaic-exception", "Save means except."),
    (27, 4, "the name of our father be done away", "our father’s name disappear", "archaic-idiom", "Done away means removed or made to disappear."),
    (27, 7, "speak right", "are right", "archaic-idiom", "Speak right means that their claim is correct."),
    (27, 19, "give him a charge", "commission him", "archaic-leadership-phrase", "Giving Joshua a charge means formally commissioning him."),
    (28, 4, "at even", "in the evening", "archaic-time", "Even means evening."),
    (28, 8, "at even", "in the evening", "archaic-time", "Even means evening."),
    (31, 10, "their goodly castles", "their fortified encampments", "false-friend-settlement", "Castles here are fortified camps or settlements, not medieval stone castles."),
    (31, 14, "Moses was wroth", "Moses was angry", "archaic-adjective", "Wroth means angry."),
    (31, 28, "the beeves", "the cattle", "obsolete-animal-name", "Beeves is an obsolete plural referring to cattle."),
    (31, 30, "the beeves", "the cattle", "obsolete-animal-name", "Beeves is an obsolete plural referring to cattle."),
    (31, 34, "threescore and one thousand asses", "sixty-one thousand donkeys", "archaic-number-and-animal", "Threescore and one is sixty-one; asses means donkeys."),
    (31, 39, "the asses were thirty thousand", "the donkeys were thirty thousand", "archaic-animal-name", "Asses means donkeys."),
    (31, 39, "threescore and one", "sixty-one", "archaic-number", "Threescore and one is sixty-one."),
    (31, 45, "thirty thousand asses", "thirty thousand donkeys", "archaic-animal-name", "Asses means donkeys."),
    (31, 49, "there lacketh not one man of us", "not one of our men is missing", "archaic-grammar", "The clause reports that every soldier returned."),
    (32, 5, "Wherefore, said they, if we have found grace in thy sight, let this land be given unto thy servants for a possession, and bring us not over Jordan", "Therefore they said, if we have found favor in your sight, let this land be given to your servants as a possession, and do not take us across Jordan", "archaic-request-formula", "The complete request is modernized together so its singular address and action remain coherent."),
    (32, 12, "Save Caleb", "Except Caleb", "archaic-exception", "Save means except."),
    (32, 14, "in your fathers’ stead", "in your fathers’ place", "archaic-noun", "Stead means place."),
    (32, 17, "the fenced cities", "the fortified cities", "false-friend", "Fenced means fortified or walled, not merely enclosed by a fence."),
    (33, 3, "on the morrow after the passover", "the day after the Passover", "archaic-time", "Morrow means the next day."),
    (33, 3, "with an high hand", "boldly", "archaic-idiom", "With a high hand means openly and boldly."),
    (33, 9, "threescore and ten palm trees", "seventy palm trees", "archaic-number", "Threescore and ten equals seventy."),
    (33, 52, "their molten images", "their cast-metal idols", "archaic-idolatry-term", "Molten images are idols cast from metal."),
    (33, 52, "quite pluck down", "completely tear down", "archaic-phrase", "Quite means completely and pluck down means tear down."),
    (34, 2, "the coasts thereof", "its borders", "false-friend-geography", "Coasts here means the land's boundaries, not seashores."),
    (34, 5, "the border shall fetch a compass", "the border shall turn", "opaque-boundary-phrase", "Fetch a compass means turn or curve around."),
    (34, 11, "the coast shall go down", "the border shall go down", "false-friend-geography", "Coast here means border."),
    (35, 2, "suburbs for the cities", "pasturelands around the cities", "false-friend-land-term", "Suburbs here are open pasturelands assigned around Levitical cities."),
    (35, 4, "the suburbs of the cities", "the pasturelands around the cities", "false-friend-land-term", "Suburbs here are pasturelands outside the city wall."),
    (35, 5, "the suburbs of the cities", "the pasturelands around the cities", "false-friend-land-term", "Suburbs here are pasturelands measured around the cities."),
    (35, 6, "forty and two cities", "forty-two cities", "archaic-number", "Forty and two is forty-two."),
    (35, 7, "forty and eight cities", "forty-eight cities", "archaic-number", "Forty and eight is forty-eight."),
    (35, 11, "killeth any person at unawares", "kills any person unintentionally", "archaic-legal-phrase", "At unawares means unintentionally in the refuge-city law."),
    (35, 15, "killeth any person unawares", "kills any person unintentionally", "archaic-legal-phrase", "Unawares means unintentionally."),
    (35, 19, "The revenger of blood", "The avenger of blood", "archaic-legal-title", "Revenger is the older form of avenger in this legal office."),
    (35, 21, "the revenger of blood", "the avenger of blood", "archaic-legal-title", "Revenger is the older form of avenger."),
    (35, 25, "the revenger of blood", "the avenger of blood", "archaic-legal-title", "Revenger is the older form of avenger."),
    (35, 30, "by the mouth of witnesses", "by the testimony of witnesses", "archaic-legal-phrase", "By the mouth of witnesses means on their testimony."),
    (35, 31, "take no satisfaction for the life", "accept no ransom for the life", "false-friend-legal-term", "Satisfaction here means a ransom or payment to avoid the sentence."),
    (35, 32, "take no satisfaction for him", "accept no ransom for him", "false-friend-legal-term", "Satisfaction here means ransom."),
    (35, 29, "statute of judgment", "legal statute", "archaic-legal-phrase", "The phrase denotes a binding legal statute."),
    (36, 4, "when the jubile", "when the Jubilee", "archaic-spelling", "Jubile is the historical spelling of Jubilee."),
    (36, 5, "hath said well", "is right", "archaic-idiom", "Hath said well means their statement is correct."),
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


base = read(CORPUS / "books/NUM.json")
texts = {(c["chapter"], v["verse"]): v["text"] for c in base["chapters"] for v in c["verses"]}
direction_path = DIRECTION / "books/num_reading_2026.kjv.v1.json"
direction = read(direction_path)

expanded = list(CHANGES)
for expected, replacement, category, reason in UNIFORM:
    for (chapter, verse), text in texts.items():
        if expected in text:
            expanded.append((chapter, verse, expected, replacement, category, reason))

added = []
for chapter, verse, expected, replacement, category, reason in expanded:
    text = texts[(chapter, verse)]
    matches = []
    cursor = 0
    while True:
        start = text.find(expected, cursor)
        if start < 0:
            break
        matches.append(start)
        cursor = start + len(expected)
    if not matches:
        raise RuntimeError(f"Missing NUM.{chapter}.{verse}: {expected!r}")
    for start in matches:
        end = start + len(expected)
        patch = next((x for x in direction["verses"] if x["chapter"] == chapter and x["verse"] == verse), None)
        if patch is None:
            patch = {"chapter": chapter, "verse": verse, "sourceTextSha256": sha(text.encode()), "edits": []}
            direction["verses"].append(patch)
        if patch["sourceTextSha256"] != sha(text.encode()):
            raise RuntimeError(f"Source hash mismatch NUM.{chapter}.{verse}")
        overlap = next((e for e in patch["edits"] if start < e["endOffset"] and end > e["startOffset"]), None)
        if overlap:
            if overlap["startOffset"] == start and overlap["endOffset"] == end and overlap["expected"] == expected and overlap["replacement"] == replacement:
                continue
            # Explicit whole-phrase reviews are added before the uniform lexical
            # rules.  When a short lexical token is contained in that reviewed
            # phrase, keep the contextual edit and do not stack a second edit.
            if expected in overlap["expected"]:
                continue
            if overlap["expected"] in expected:
                patch["edits"].remove(overlap)
                overlap = None
            if overlap is None:
                pass
            else:
                raise RuntimeError(f"Overlapping edit NUM.{chapter}.{verse}: {expected!r} with {overlap['expected']!r}")
        edit = {
            "startOffset": start,
            "endOffset": end,
            "expected": expected,
            "replacement": replacement,
            "category": category,
            "reason": reason,
            "evidence": [{
                "label": "Complete-verse KJV contextual review",
                "url": f"https://www.biblegateway.com/passage/?search=Numbers+{chapter}%3A{verse}&version=KJV",
            }],
        }
        patch["edits"].append(edit)
        patch["edits"].sort(key=lambda x: x["startOffset"])
        added.append((chapter, verse, expected, replacement, category, reason))

direction["verses"].sort(key=lambda x: (x["chapter"], x["verse"]))
direction["editorialStatus"] = "approved-numbers-complete-context-v6"
direction["ownerReview"] = {"contentVersion": VERSION, "review": "KJV Numbers complete-context review", "requiredFullTest": True}
write(direction_path, direction)

source_path = DIRECTION / "reading_2026.package-source.json"
source = read(source_path)
source["contentVersion"] = VERSION
source["generatedAt"] = "2026-09-12T00:00:00.000Z"
source["editorialPolicy"]["version"] = VERSION
write(source_path, source)

order = {read(p)["book"]: read(p)["order"] for p in (CORPUS / "books").glob("*.json")}
files = list((DIRECTION / "books").glob("*.json"))
books = [read(p) for p in files]
books.sort(key=lambda b: order[b["book"]])
payload = {
    "books": books,
    "contentVersion": VERSION,
    "editorialPolicy": source["editorialPolicy"],
    "filterId": source["filterId"],
    "format": "shine-reading-filter-package",
    "normalizationId": source["normalizationId"],
    "schemaVersion": 1,
    "sourceCorpusSha256": source["sourceCorpusSha256"],
    "sourceVersionId": "KJV",
}
raw = canonical(payload).encode()
compressed = gzip.compress(raw, compresslevel=9, mtime=0)
packages = DIRECTION / "packages"
(packages / "reading_2026.kjv.v1.package.json.gz").write_bytes(compressed)
coverage = {
    "expectedBookCount": 66,
    "includedBookCount": 66,
    "changedVerseCount": sum(len(b["verses"]) for b in books),
    "editCount": sum(sum(len(v["edits"]) for v in b["verses"]) for b in books),
}
manifest = {
    "format": "shine-reading-filter-manifest",
    "filterId": source["filterId"],
    "schemaVersion": 1,
    "contentVersion": VERSION,
    "sourceVersionId": "KJV",
    "sourceCorpusSha256": source["sourceCorpusSha256"],
    "normalizationId": source["normalizationId"],
    "contentSha256": sha(compressed),
    "sizeBytes": len(compressed),
    "expandedSizeBytes": len(raw),
    "mimeType": "application/vnd.shine.reading-filter+gzip",
    "generatedAt": "2026-09-12",
    "editorialPolicy": source["editorialPolicy"],
    "coverage": coverage,
    "books": [{
        "id": b["book"],
        "order": order[b["book"]],
        "sourceFile": next(p.name for p in files if read(p)["book"] == b["book"]),
        "sourceContentSha256": b["sourceContentSha256"],
        "payloadSha256": sha(canonical(b).encode()),
        "changedVerseCount": len(b["verses"]),
        "editCount": sum(len(v["edits"]) for v in b["verses"]),
    } for b in books],
}
write(packages / "reading_2026.kjv.v1.manifest.json", manifest)

registry = read(REGISTRY)
registry["updatedAt"] = "2026-09-12T00:00:00.000Z"
registry["activeContentVersion"] = VERSION
known = {(x["reference"], x["expected"], x["replacement"]) for x in registry["applied"]}
for chapter, verse, expected, replacement, category, reason in added:
    item = {
        "reference": f"NUM.{chapter}.{verse}",
        "expected": expected,
        "replacement": replacement,
        "category": category,
        "reason": reason,
        "evidenceUrl": f"https://www.biblegateway.com/passage/?search=Numbers+{chapter}%3A{verse}&version=KJV",
    }
    if (item["reference"], expected, replacement) not in known:
        registry["applied"].append(item)
write(REGISTRY, registry)

print(json.dumps({
    "added": len(added),
    "numbersChangedVerses": len(direction["verses"]),
    "numbersEdits": sum(len(v["edits"]) for v in direction["verses"]),
    **coverage,
    "contentSha256": manifest["contentSha256"],
}, indent=2))
