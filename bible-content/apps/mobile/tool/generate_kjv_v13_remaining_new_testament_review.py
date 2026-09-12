import gzip
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"
VERSION = 13
STAMP = "2026-09-13T01:30:00.000Z"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, compact=False):
    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=None if compact else 2,
            separators=(",", ":") if compact else None,
        ) + "\n",
        encoding="utf-8",
    )


def sha(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def recase(found, replacement):
    if found.isupper():
        return replacement.upper()
    if found[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def r(book, chapter, verse, expected, replacement, category, reason, word=False):
    return {
        "book": book,
        "chapter": chapter,
        "verse": verse,
        "expected": expected,
        "replacement": replacement,
        "category": category,
        "reason": reason,
        "word": word,
    }


# These families were reviewed across every remaining-New-Testament occurrence.
# Exact counts are a guardrail: a changed corpus or an unreviewed new occurrence
# makes this generator fail instead of being silently modernized.
STABLE_FAMILIES = [
    ("aforetime", "formerly", 2, "archaic-time-term", "Aforetime means formerly in both reviewed contexts."),
    ("albeit", "although", 1, "archaic-concession-term", "Albeit introduces a concession and means although."),
    ("arrayed", "dressed", 6, "archaic-clothing-term", "Arrayed describes being dressed or clothed in the stated garment."),
    ("bishoprick", "office", 1, "historical-office-term", "Bishoprick denotes the office that another person would take."),
    ("charity", "love", 28, "false-friend-love-term", "Charity denotes self-giving love, not only charitable donations."),
    ("covetousness", "greed", 8, "archaic-greed-term", "Covetousness denotes greed in every reviewed context."),
    ("ensamples", "examples", 3, "archaic-example-term", "Ensamples means examples to observe or avoid."),
    ("fain", "gladly", 1, "archaic-desire-term", "Fain means the hungry son would gladly have eaten."),
    ("guile", "deceit", 7, "archaic-deceit-term", "Guile means deceit in every reviewed context."),
    ("haply", "perhaps", 4, "archaic-possibility-term", "Haply means perhaps in every reviewed context."),
    ("hither", "here", 19, "archaic-direction-term", "Hither means toward or to this place; here preserves that direction in the reviewed clauses."),
    ("nigh", "near", 36, "archaic-nearness-term", "Nigh means near in every reviewed context."),
    ("peradventure", "perhaps", 2, "archaic-possibility-term", "Peradventure means perhaps."),
    ("publican", "tax collector", 4, "historical-tax-term", "A publican was a tax collector in the Roman system."),
    ("publicans", "tax collectors", 7, "historical-tax-term", "Publicans were tax collectors in the Roman system."),
    ("quickened", "made alive", 5, "archaic-life-term", "Quickened means made alive in these resurrection and spiritual-life contexts."),
    ("raiment", "clothing", 13, "archaic-clothing-term", "Raiment means clothing in every reviewed context."),
    ("remission", "forgiveness", 8, "historical-forgiveness-term", "Remission denotes forgiveness of sins in every reviewed context."),
    ("salutation", "greeting", 6, "archaic-greeting-term", "Salutation means greeting."),
    ("salute", "greet", 29, "archaic-greeting-verb", "Salute means greet in these personal greetings and visits."),
    ("scrip", "travel bag", 4, "historical-travel-bag", "Scrip is a travel bag for provisions."),
    ("shewing", "showing", 9, "spelling-modernization", "Shewing is the older spelling of showing."),
    ("straightway", "immediately", 11, "archaic-speed-adverb", "Straightway means immediately."),
    ("swine", "pigs", 4, "historical-animal-term", "Swine means pigs."),
    ("temperance", "self-control", 4, "false-friend-self-control", "Temperance denotes self-control, not only abstinence from alcohol."),
    ("thither", "there", 13, "archaic-direction-term", "Thither means toward or to that place; there preserves that direction in the reviewed clauses."),
    ("twain", "two", 1, "archaic-number-term", "Twain means two."),
    ("unfeigned", "sincere", 4, "archaic-sincerity-term", "Unfeigned means sincere or genuine."),
    ("verily", "truly", 79, "archaic-affirmation-term", "Verily marks a solemn affirmation and means truly."),
    ("whithersoever", "wherever", 4, "archaic-direction-term", "Whithersoever means wherever."),
]


PHRASE_FAMILIES = [
    ("Holy Ghost", "Holy Spirit", 80, "historical-spirit-term", "Holy Ghost is modernized to Holy Spirit without changing the referent."),
    ("candlesticks", "lampstands", 6, "historical-lampstand-term", "Candlesticks are stands for oil lamps."),
    ("candlestick", "lampstand", 4, "historical-lampstand-term", "Candlestick is a stand for an oil lamp."),
    ("devils", "demons", 26, "historical-demon-term", "Devils refers to demons in these reviewed passages."),
]


CONTEXT_RULES = [
    # Follow-up grammar after stable-family modernization.
    r("ACT", 14, 19, "there came there certain Jews", "certain Jews came there", "grammar-direction-clause", "The directional modernization is reordered to avoid the duplicate there."),
    r("ACT", 27, 8, "near whereunto was the city of Lasea", "near which was the city of Lasea", "grammar-relative-location", "The relative location remains clear after nigh is modernized."),
    r("EPH", 2, 5, "hath made alive us together", "hath made us alive together", "grammar-object-position", "The object is placed naturally inside the verb phrase."),
    r("1CO", 6, 13, "Foods for the belly, and the belly for foods", "Food is for the belly, and the belly for food", "grammar-food-clause", "The generic food statement uses natural singular wording."),
    r("REV", 3, 5, "clothed in white clothing", "clothed in white garments", "grammar-clothing-phrase", "Garments avoids a tautology after raiment is modernized."),
    r("REV", 3, 18, "white clothing that thou mayest be clothed", "white garments that thou mayest be clothed", "grammar-clothing-phrase", "Garments avoids repeating clothing and clothed in the same phrase."),
    r("REV", 4, 4, "clothed in white clothing", "clothed in white garments", "grammar-clothing-phrase", "Garments avoids a tautology after raiment is modernized."),
    r("LUK", 19, 2, "chief among the tax collectors", "chief tax collector", "historical-tax-title", "The phrase identifies Zacchaeus as a chief tax collector."),
    r("1CO", 13, 4, "Love suffereth long", "Love is patient", "archaic-patience-clause", "Suffereth long means love is patient."),
    r("LUK", 15, 1, "near unto", "near", "grammar-modern-preposition", "Near no longer needs the archaic preposition unto."),
    r("LUK", 22, 47, "near unto", "near", "grammar-modern-preposition", "Near no longer needs the archaic preposition unto."),

    # Respect can mean favoritism, attention, regard or concern.
    r("1PE", 1, 17, "without respect of persons", "without favoritism", "false-friend-partiality-phrase", "The Father judges without favoritism."),
    r("COL", 3, 25, "no respect of persons", "no favoritism", "false-friend-partiality-phrase", "Divine judgment shows no favoritism."),
    r("EPH", 6, 9, "there respect of persons with him", "there favoritism with him", "false-friend-partiality-phrase", "The Master in heaven shows no favoritism."),
    r("JAS", 2, 1, "with respect of persons", "with favoritism", "false-friend-partiality-phrase", "Faith in Christ must not be practiced with favoritism."),
    r("JAS", 2, 9, "have respect to persons", "show favoritism", "false-friend-partiality-phrase", "The action condemned is showing favoritism."),
    r("ROM", 2, 11, "no respect of persons with God", "no favoritism with God", "false-friend-partiality-phrase", "God's judgment shows no favoritism."),
    r("JAS", 2, 3, "have respect to him", "give special attention to him", "false-friend-preference-phrase", "The assembly gives special attention to the richly dressed man."),
    r("COL", 2, 16, "in respect of an holyday", "regarding a holy day", "false-friend-regard-phrase", "Respect of means regarding in the list of observances."),
    r("HEB", 11, 26, "had respect unto the recompence of the reward", "looked to the recompense of the reward", "archaic-regard-phrase", "Had respect unto means Moses looked ahead to the reward."),
    r("PHP", 4, 11, "in respect of want", "because of need", "false-friend-need-phrase", "Paul says he is not speaking because he is in need."),

    # Admonition is warning or instruction according to the local clause.
    r("1CO", 10, 11, "for our admonition", "for our warning", "archaic-warning-term", "Israel's examples were written as a warning."),
    r("EPH", 6, 4, "nurture and admonition of the Lord", "discipline and instruction of the Lord", "archaic-instruction-phrase", "The clause concerns raising children with the Lord's discipline and instruction."),
    r("TIT", 3, 10, "after the first and second admonition", "after the first and second warning", "archaic-warning-term", "The divisive person is rejected after two warnings."),
    r("COL", 2, 16, "judge you in food, or in drink, or regarding a holy day, or of the new moon, or of the sabbath days", "judge you regarding food, drink, a holy day, the new moon, or sabbath days", "grammar-observance-list", "The five observances remain parallel after food and respect are modernized."),
    r("HEB", 11, 26, "looked to the recompense of the reward", "looked to the reward", "grammar-reward-phrase", "The shorter phrase removes an obsolete tautology while preserving the reward."),
    r("1CO", 10, 11, "happened unto them for examples", "happened to them as examples", "grammar-example-clause", "The prepositions are modernized after ensamples becomes examples."),
    r("JAS", 2, 3, "gay clothing", "fine clothing", "false-friend-clothing-term", "Gay describes splendid or fine clothing in this context."),
    r("TIT", 3, 10, "A man that is an heretick", "A divisive person", "false-friend-divisive-person", "The instruction concerns a person who persists in causing division."),
    r("1PE", 1, 17, "time of your sojourning here", "time of your stay here as foreigners", "archaic-sojourning-phrase", "Sojourning describes the believers' temporary stay as foreigners."),
    r("1CO", 10, 25, "Whatsoever is sold in the shambles", "Whatever is sold in the meat market", "historical-market-phrase", "Shambles denotes a meat market, not a state of disorder."),
    r("JAS", 3, 4, "wherever the governor listeth", "wherever the pilot wishes", "archaic-navigation-phrase", "The governor is the pilot of the ship, and listeth means wishes."),
    r("JHN", 3, 8, "where it listeth", "where it wishes", "archaic-desire-term", "Listeth means the wind blows where it wishes."),
    r("LUK", 13, 24, "the strait gate", "the narrow gate", "false-friend-narrow-term", "Strait means narrow in the gate image."),
    r("PHP", 1, 23, "in a strait betwixt two", "torn between the two", "archaic-dilemma-phrase", "Paul describes being pressed between two desires."),
    r("1CO", 1, 28, "bring to nought things that are", "bring to nothing the things that are", "archaic-nullify-phrase", "Bring to nought means reduce or bring to nothing."),
    r("1CO", 2, 6, "come to nought", "come to nothing", "archaic-failure-phrase", "The rulers of this age come to nothing."),
    # Death idiom: Jesus' voluntary yielding is kept distinct from ordinary death.
    r("ACT", 5, 5, "gave up the ghost", "died", "archaic-death-idiom", "The idiom states that Ananias died."),
    r("ACT", 5, 10, "yielded up the ghost", "died", "archaic-death-idiom", "The idiom states that Sapphira died."),
    r("ACT", 12, 23, "gave up the ghost", "died", "archaic-death-idiom", "The idiom states that Herod died."),
    r("JHN", 19, 30, "gave up the ghost", "gave up his spirit", "archaic-death-idiom", "The wording preserves John's statement that Jesus yielded his spirit."),
    r("LUK", 23, 46, "gave up the ghost", "gave up his spirit", "archaic-death-idiom", "The wording preserves Luke's statement that Jesus yielded his spirit."),

    # Tomb terminology; Romans 3:13 uses the image of an open grave.
    r("ROM", 3, 13, "sepulchre", "grave", "archaic-grave-term", "The quotation compares the throat to an open grave."),

    # Clear false friends and obsolete clauses.
    r("ACT", 9, 26, "assayed to join himself", "tried to join", "archaic-attempt-phrase", "Assayed means Saul tried to join the disciples."),
    r("ACT", 16, 7, "assayed to go", "tried to go", "archaic-attempt-phrase", "Assayed means they tried to enter Bithynia."),
    r("LUK", 5, 4, "a draught", "a catch", "historical-fishing-term", "Draught denotes a catch of fish."),
    r("LUK", 5, 9, "the draught of the fishes", "the catch of fish", "historical-fishing-term", "Draught denotes the catch of fish."),
    r("ACT", 10, 29, "without gainsaying", "without objection", "archaic-objection-term", "Peter came without objection when summoned."),
    r("JUD", 1, 11, "the gainsaying of Core", "the rebellion of Korah", "historical-rebellion-phrase", "Gainsaying denotes Korah's rebellion."),
    r("ROM", 10, 21, "a disobedient and gainsaying people", "a disobedient and contrary people", "archaic-opposition-term", "Gainsaying describes people who continually oppose God."),
    r("ACT", 18, 14, "wrong or wicked lewdness", "wrongdoing or a serious crime", "false-friend-crime-phrase", "Lewdness here denotes serious criminal conduct, not only sexual conduct."),
    r("LUK", 11, 46, "lade men with burdens grievous to be borne", "burden people with loads hard to carry", "archaic-burden-clause", "The lawyers impose burdens that are hard for people to carry."),
    r("2TI", 3, 6, "silly women laden with sins", "gullible women burdened with sins", "false-friend-captive-clause", "Silly means vulnerable or gullible here, and laden means burdened."),
    r("JAS", 1, 21, "superfluity of naughtiness", "overflow of wickedness", "false-friend-wickedness-phrase", "The phrase denotes an abundance of wickedness."),
    r("1CO", 5, 11, "a railer", "a verbally abusive person", "archaic-abuse-term", "Railer means a person who verbally abuses others."),
    r("JHN", 6, 7, "Two hundred pennyworth of bread", "Two hundred denarii worth of bread", "historical-coin-phrase", "Pennyworth refers to denarii, not modern pennies."),
    r("LUK", 12, 6, "two farthings", "two small copper coins", "historical-coin-phrase", "Farthings denotes two low-value Roman copper coins."),
    r("ROM", 13, 13, "chambering and wantonness", "sexual immorality and sensuality", "archaic-moral-phrase", "The paired terms describe sexual immorality and shameless sensuality."),

    # Context-dependent 'careful'.
    r("LUK", 10, 41, "art careful and troubled", "art anxious and troubled", "false-friend-anxiety-term", "Careful means anxious in Jesus' reply to Martha."),
    r("PHP", 4, 6, "Be careful for nothing", "Be anxious for nothing", "false-friend-anxiety-term", "Careful means anxious in the contrast with prayer."),
    r("PHP", 4, 10, "ye were also careful", "ye were also concerned", "false-friend-concern-term", "The Philippians remained concerned for Paul."),
    r("TIT", 3, 8, "be careful to maintain good works", "be diligent to maintain good works", "false-friend-diligence-term", "Careful means diligent in maintaining good works."),

    # Bowels is literal only in Acts 1:18, which remains unchanged.
    r("1JN", 3, 17, "shutteth up his bowels of compassion", "closes his heart of compassion", "archaic-compassion-phrase", "Bowels denotes the inner seat of compassion."),
    r("2CO", 6, 12, "straitened in your own bowels", "restricted in your own affections", "archaic-affection-phrase", "Bowels denotes inward affections in this appeal."),
    r("COL", 3, 12, "bowels of mercies", "heartfelt compassion", "archaic-compassion-phrase", "Bowels of mercies means heartfelt compassion."),
    r("PHM", 1, 7, "the bowels of the saints", "the hearts of the saints", "archaic-affection-term", "Bowels denotes the saints' hearts or inward affections."),
    r("PHM", 1, 12, "mine own bowels", "mine own heart", "archaic-affection-term", "Paul calls Onesimus his own heart."),
    r("PHM", 1, 20, "refresh my bowels", "refresh my heart", "archaic-affection-term", "Bowels denotes Paul's heart or inward affections."),
    r("PHP", 1, 8, "in the bowels of Jesus Christ", "with the affection of Jesus Christ", "archaic-affection-phrase", "Bowels denotes Christlike affection."),
    r("PHP", 2, 1, "any bowels and mercies", "any affection and compassion", "archaic-compassion-phrase", "The pair denotes affection and compassion."),

    # Different senses of divers.
    r("ACT", 19, 9, "when divers were hardened", "when some were hardened", "false-friend-people-term", "Divers here means some people, not various kinds."),

    # Farming terms.
    r("2TI", 2, 6, "The husbandman that laboureth", "The farmer who laboureth", "historical-farmer-term", "Husbandman means farmer."),
    r("JAS", 5, 7, "the husbandman waiteth", "the farmer waiteth", "historical-farmer-term", "Husbandman means farmer."),
    r("JHN", 15, 1, "my Father is the husbandman", "my Father is the gardener", "historical-vineyard-term", "In the vine image, husbandman denotes the one who tends the vineyard."),
    r("LUK", 20, 9, "let it forth to husbandmen", "leased it to tenant farmers", "historical-tenant-term", "The husbandmen are tenant farmers entrusted with the vineyard."),
    r("LUK", 20, 10, "the husbandmen", "the tenant farmers", "historical-tenant-term", "The husbandmen are the vineyard's tenant farmers."),
    r("LUK", 20, 14, "the husbandmen", "the tenant farmers", "historical-tenant-term", "The husbandmen are the vineyard's tenant farmers."),
    r("LUK", 20, 16, "these husbandmen", "these tenant farmers", "historical-tenant-term", "The husbandmen are the vineyard's tenant farmers."),

    # Infirmity distinguished as illness or weakness by context.
    r("GAL", 4, 13, "infirmity of the flesh", "physical illness", "archaic-illness-term", "Paul refers to a physical illness."),
    r("HEB", 5, 2, "compassed with infirmity", "surrounded by weakness", "archaic-weakness-term", "The high priest shares human weakness."),
    r("HEB", 7, 28, "men high priests which have infirmity", "men as high priests who have weakness", "archaic-weakness-clause", "The law appoints human high priests who have weakness."),
    r("JHN", 5, 5, "had an infirmity", "had an illness", "archaic-illness-term", "The man had a disabling illness for thirty-eight years."),
    r("LUK", 13, 11, "a spirit of infirmity", "a disabling spirit", "archaic-disability-phrase", "The spirit had disabled the woman for eighteen years."),
    r("LUK", 13, 12, "loosed from thine infirmity", "freed from thine affliction", "archaic-affliction-phrase", "Jesus declares the woman freed from her affliction."),
    r("ROM", 6, 19, "infirmity of your flesh", "weakness of your flesh", "archaic-weakness-term", "Paul accommodates the weakness of his hearers' human nature."),
    r("1TI", 5, 23, "often infirmities", "frequent ailments", "archaic-ailment-term", "The plural refers to Timothy's recurring ailments."),
    r("2CO", 11, 30, "mine infirmities", "my weaknesses", "archaic-weakness-term", "Paul boasts in his weaknesses."),
    r("2CO", 12, 5, "mine infirmities", "my weaknesses", "archaic-weakness-term", "Paul boasts only in his weaknesses."),
    r("2CO", 12, 9, "my infirmities", "my weaknesses", "archaic-weakness-term", "Paul boasts in weaknesses so Christ's power may rest on him."),
    r("2CO", 12, 10, "infirmities", "weaknesses", "archaic-weakness-term", "The list begins with Paul's weaknesses for Christ's sake.", True),
    r("HEB", 4, 15, "our infirmities", "our weaknesses", "archaic-weakness-term", "The high priest sympathizes with human weaknesses."),
    r("LUK", 5, 15, "their infirmities", "their illnesses", "archaic-illness-term", "The crowds came to be healed of illnesses."),
    r("LUK", 7, 21, "their infirmities and plagues", "their illnesses and afflictions", "archaic-illness-phrase", "The clause distinguishes illnesses and other afflictions."),
    r("LUK", 8, 2, "evil spirits and infirmities", "evil spirits and illnesses", "archaic-illness-term", "The women had been healed of spirits and illnesses."),
    r("ROM", 8, 26, "our infirmities", "our weaknesses", "archaic-weakness-term", "The Spirit helps believers in their weaknesses."),
    r("ROM", 15, 1, "the infirmities of the weak", "the weaknesses of the weak", "archaic-weakness-term", "The strong are to bear the weaknesses of the weak."),

    # Meat means food or a meal in KJV usage.
    r("1CO", 3, 2, "not with meat", "not with solid food", "false-friend-food-term", "The contrast is milk versus solid food."),
    r("HEB", 5, 12, "strong meat", "solid food", "false-friend-food-term", "The contrast is milk versus solid food."),
    r("HEB", 5, 14, "strong meat", "solid food", "false-friend-food-term", "Solid food belongs to the mature in the metaphor."),
    r("1CO", 8, 10, "sit at meat", "dining", "false-friend-meal-phrase", "Sit at meat means dining."),
    r("LUK", 7, 36, "sat down to meat", "sat down to dine", "false-friend-meal-phrase", "Sat down to meat means sat down to dine."),
    r("LUK", 7, 37, "sat at meat", "was dining", "false-friend-meal-phrase", "Sat at meat means was dining."),
    r("LUK", 7, 49, "sat at meat", "were dining", "false-friend-meal-phrase", "Sat at meat means were dining."),
    r("LUK", 11, 37, "sat down to meat", "sat down to dine", "false-friend-meal-phrase", "Sat down to meat means sat down to dine."),
    r("LUK", 12, 37, "sit down to meat", "sit down to dine", "false-friend-meal-phrase", "Sit down to meat means sit down to dine."),
    r("LUK", 14, 10, "sit at meat", "dine", "false-friend-meal-phrase", "Sit at meat means dine."),
    r("LUK", 14, 15, "sat at meat", "were dining", "false-friend-meal-phrase", "Sat at meat means were dining."),
    r("LUK", 17, 7, "sit down to meat", "sit down to eat", "false-friend-meal-phrase", "Sit down to meat means sit down to eat."),
    r("LUK", 22, 27, "sitteth at meat", "dineth", "false-friend-meal-phrase", "Sitteth at meat means dineth; the KJV verb system is retained."),
    r("LUK", 24, 30, "sat at meat", "was dining", "false-friend-meal-phrase", "Sat at meat means was dining."),

    # Adjectival meet; verbal meet remains unchanged.
    r("1CO", 15, 9, "not meet to be called", "not worthy to be called", "false-friend-worthy-term", "Meet means worthy in this self-description."),
    r("1CO", 16, 4, "if it be meet", "if it is fitting", "false-friend-fitting-term", "Meet means fitting or appropriate."),
    r("2PE", 1, 13, "I think it meet", "I think it right", "false-friend-right-term", "Meet means right or appropriate."),
    r("2TH", 1, 3, "as it is meet", "as is fitting", "false-friend-fitting-term", "Meet means fitting or appropriate."),
    r("2TI", 2, 21, "meet for the master\u2019s use", "useful to the master", "false-friend-useful-term", "Meet means useful or suitable for the master."),
    r("ACT", 26, 20, "works meet for repentance", "works consistent with repentance", "false-friend-suitable-term", "The works are consistent with genuine repentance."),
    r("COL", 1, 12, "made us meet to be partakers", "made us fit to share", "false-friend-fit-term", "Meet means fit or qualified to share in the inheritance."),
    r("HEB", 6, 7, "herbs meet for them", "crops useful to those", "false-friend-useful-term", "Meet means useful to those who cultivate the land."),
    r("LUK", 15, 32, "It was meet", "It was right", "false-friend-right-term", "Meet means right or fitting to celebrate."),
    r("PHP", 1, 7, "it is meet for me", "it is right for me", "false-friend-right-term", "Meet means right or appropriate."),
    r("ROM", 1, 27, "recompence of their error which was meet", "penalty of their error which was due", "archaic-penalty-phrase", "Meet means due, and recompence denotes the resulting penalty."),

    # Places and grain.
    r("ACT", 13, 50, "out of their coasts", "out of their region", "false-friend-region-term", "Coasts denotes the surrounding territory."),
    r("ACT", 19, 1, "the upper coasts", "the inland regions", "false-friend-region-term", "The route passed through inland regions before Ephesus."),
    r("ACT", 26, 20, "all the coasts", "all the region", "false-friend-region-term", "Coasts denotes the region of Judaea."),
    r("1CO", 9, 9, "the corn", "the grain", "historical-grain-term", "Corn means grain in this British English context."),
    r("1TI", 5, 18, "the corn", "the grain", "historical-grain-term", "Corn means grain in this British English context."),
    r("ACT", 7, 12, "corn in Egypt", "grain in Egypt", "historical-grain-term", "Corn means grain in this British English context."),
    r("JHN", 12, 24, "a corn of wheat", "a kernel of wheat", "historical-grain-term", "Corn denotes one kernel of wheat."),
    r("LUK", 6, 1, "corn fields", "grainfields", "historical-grain-term", "Corn fields means grainfields."),
    r("LUK", 6, 1, "ears of corn", "heads of grain", "historical-grain-term", "Ears of corn means heads of grain."),

    # Palsy and damsel are handled as complete local phrases for grammar.
    r("ACT", 9, 33, "was sick of the palsy", "was paralyzed", "obsolete-medical-phrase", "Palsy denotes paralysis."),
    r("LUK", 5, 18, "a man which was taken with a palsy", "a man who was paralyzed", "obsolete-medical-phrase", "Palsy denotes paralysis."),
    r("LUK", 5, 24, "the sick of the palsy", "the paralyzed man", "obsolete-medical-phrase", "Palsy denotes paralysis."),
    r("ACT", 12, 13, "a damsel came to hearken, named Rhoda", "a servant girl named Rhoda came to answer", "archaic-servant-clause", "Damsel denotes the servant girl who answered the door."),
    r("ACT", 16, 16, "a certain damsel possessed", "a certain young woman possessed", "archaic-young-woman-term", "Damsel denotes a young woman in this account."),
    r("JHN", 18, 17, "the damsel that kept the door", "the servant girl who kept the door", "archaic-servant-term", "Damsel denotes the servant girl guarding the door."),

    # Alms is expressed with natural grammar in each setting.
    r("ACT", 3, 2, "to ask alms", "to ask for charitable gifts", "historical-almsgiving-phrase", "Alms are charitable gifts for the poor."),
    r("ACT", 3, 3, "asked an alms", "asked for a charitable gift", "historical-almsgiving-phrase", "Alms are charitable gifts for the poor."),
    r("ACT", 3, 10, "sat for alms", "sat asking for charitable gifts", "historical-almsgiving-phrase", "Alms are charitable gifts for the poor."),
    r("ACT", 10, 2, "gave much alms", "gave many charitable gifts", "historical-almsgiving-phrase", "Alms are charitable gifts for the poor."),
    r("ACT", 10, 4, "thine alms", "thy charitable gifts", "historical-almsgiving-term", "Alms are charitable gifts for the poor."),
    r("ACT", 10, 31, "thine alms", "thy charitable gifts", "historical-almsgiving-term", "Alms are charitable gifts for the poor."),
    r("ACT", 24, 17, "bring alms", "bring charitable gifts", "historical-almsgiving-term", "Alms are charitable gifts for the poor."),
    r("LUK", 11, 41, "give alms", "give to the poor", "historical-almsgiving-phrase", "Giving alms means giving to the poor."),
    r("LUK", 12, 33, "give alms", "give to the poor", "historical-almsgiving-phrase", "Giving alms means giving to the poor."),

    # Concupiscence and sedition are resolved by clause, not by global replacement.
    r("1TH", 4, 5, "lust of concupiscence", "lustful passion", "archaic-desire-phrase", "The phrase denotes uncontrolled sexual passion."),
    r("COL", 3, 5, "evil concupiscence", "evil desire", "archaic-desire-term", "The list names evil desire."),
    r("ROM", 7, 8, "all manner of concupiscence", "all kinds of covetous desire", "archaic-coveting-phrase", "The commandment against coveting governs this context."),
    r("ACT", 24, 5, "a mover of sedition", "one who stirs up rebellion", "historical-rebellion-term", "The accusers claim Paul stirs up rebellion."),
    r("LUK", 23, 19, "a certain sedition made in the city", "a certain insurrection in the city", "historical-insurrection-term", "Sedition denotes the city insurrection."),
    r("LUK", 23, 25, "for sedition and murder", "for insurrection and murder", "historical-insurrection-term", "Sedition denotes the insurrection associated with Barabbas."),
    r("GAL", 5, 20, "seditions", "divisions", "contextual-division-term", "The plural denotes divisive factions among the works of the flesh.", True),

    # Nought has several distinct senses.
    r("2TH", 3, 8, "for nought", "free of charge", "false-friend-cost-phrase", "For nought means without payment."),
    r("ACT", 4, 11, "set at nought of you builders", "rejected by you builders", "archaic-rejection-phrase", "Set at nought means rejected."),
    r("ACT", 5, 36, "brought to nought", "came to nothing", "archaic-failure-phrase", "The movement failed and came to nothing."),
    r("ACT", 5, 38, "come to nought", "come to nothing", "archaic-failure-phrase", "A merely human work will come to nothing."),
    r("ACT", 19, 27, "set at nought", "discredited", "archaic-discredit-term", "The concern is that the temple will be discredited."),
    r("LUK", 23, 11, "set him at nought", "treated him with contempt", "archaic-contempt-phrase", "Herod and his soldiers treated Jesus with contempt."),
    r("REV", 18, 17, "come to nought", "come to nothing", "archaic-destruction-phrase", "The riches are destroyed in one hour."),
    r("ROM", 14, 10, "set at nought thy brother", "despise thy brother", "archaic-contempt-phrase", "Set at nought means despise; the KJV pronoun system is retained."),

    # Ministry terminology.
    r("2CO", 3, 7, "ministration", "ministry", "archaic-ministry-term", "Ministration denotes a ministry or service.", True),
    r("2CO", 3, 8, "ministration", "ministry", "archaic-ministry-term", "Ministration denotes a ministry or service.", True),
    r("2CO", 3, 9, "ministration", "ministry", "archaic-ministry-term", "Ministration denotes a ministry or service.", True),
    r("2CO", 9, 13, "ministration", "ministry", "archaic-ministry-term", "Ministration denotes this ministry of giving.", True),
    r("ACT", 6, 1, "daily ministration", "daily distribution", "historical-distribution-term", "The widows were neglected in the daily distribution of food."),
    r("LUK", 1, 23, "days of his ministration", "days of his service", "historical-priestly-service", "Ministration denotes Zechariah's priestly service."),

    # Peculiar is a false friend in these possession formulas.
    r("1PE", 2, 9, "a peculiar people", "a people for God's own possession", "false-friend-possession-phrase", "Peculiar denotes a people belonging especially to God."),
    r("TIT", 2, 14, "a peculiar people", "a people for his own possession", "false-friend-possession-phrase", "Peculiar denotes a people belonging especially to Christ."),
]


# Stable families that have one semantic exception or need a phrase-level pass.
WORD_EXCLUSIONS = {
    "sepulchre": {"ROM.3.13"},
}


PENDING_FAMILIES = {
    "nt-kjv-v13-pronoun-verb-system": (
        ["thee", "thou", "thy", "thine", "ye", "hath", "doth", "shalt", "wilt"],
        "Changing isolated pronouns or verbs creates mixed KJV grammar; this requires a Bible-wide person-and-number policy.",
    ),
    "nt-kjv-v13-unto-register": (["unto"], "Unto has directional, recipient and idiomatic uses and remains until its clauses are reviewed individually."),
    "nt-kjv-v13-where-connectors": (["wherefore", "wherein", "whereby", "wherewithal"], "These connectors vary among why, therefore, in which, by which and with what."),
    "nt-kjv-v13-suffer-family": (["suffer", "suffered", "suffereth", "sufferings"], "Suffer can mean allow, endure or experience suffering; a global change would alter meaning."),
    "nt-kjv-v13-request-prayer-family": (["pray", "prayed", "besought", "entreat", "entreated"], "These verbs alternate between prayer to God and ordinary requests or pleading."),
    "nt-kjv-v13-devil-singular": (["devil"], "Singular devil can refer to Satan or to one demon and must be distinguished verse by verse."),
    "nt-kjv-v13-abide-family": (["abide", "abideth", "abode"], "Abide language carries ordinary and theological senses, especially in John."),
    "nt-kjv-v13-doctrinal-covenant": (["testament", "atonement", "propitiation", "ordinances"], "Covenant and atonement terminology requires a coordinated doctrinal policy."),
    "nt-kjv-v13-sexual-purity-family": (["fornication", "uncleanness", "lasciviousness"], "These terms overlap in some lists but remain distinct in Greek; they need clause-level review."),
    "nt-kjv-v13-authority-family": (["principalities", "powers"], "Spiritual and civil authority uses must be distinguished before modernization."),
    "nt-kjv-v13-dispensation": (["dispensation"], "Dispensation alternates between stewardship, commission and plan."),
    "nt-kjv-v13-circumcision-family": (["uncircumcision"], "Literal, social and theological uses require coordinated review."),
    "nt-kjv-v13-long-suffering": (["longsuffering"], "Longsuffering may be patience, endurance or forbearance and sometimes appears beside patience."),
    "nt-kjv-v13-ought-family": (["ought"], "Ought can express duty, expectation or debt and remains pending clause review."),
    "nt-kjv-v13-wrought-family": (["wrought"], "Wrought can mean worked, produced, accomplished or performed."),
    "nt-kjv-v13-recompence-reproach": (["recompence", "reproach"], "Reward, penalty, disgrace and suffering senses must remain distinct."),
    "nt-kjv-v13-abroad-family": (["abroad"], "Abroad varies among publicly, widely, away and scattered; automatic replacement would be unsafe."),
    "nt-kjv-v13-bid-bade-family": (["bid", "bade"], "Bid and bade vary among command, invite, greet and say farewell."),
    "nt-kjv-v13-tarry-family": (["tarry"], "Tarry can mean stay, wait or delay and needs clause review."),
    "nt-kjv-v13-travail-family": (["travail"], "Travail can mean labor, hardship or childbirth pain."),
    "nt-kjv-v13-want-family": (["want"], "Want can mean lack, need or be in poverty."),
    "nt-kjv-v13-anathema-maranatha": (["anathema"], "The paired Aramaic and Greek formula needs an explanatory note, not a quick lexical substitute."),
}


def corpus_and_paths():
    books = {read(p)["book"]: read(p) for p in (CORPUS / "books").glob("*.json")}
    order = {book: doc["order"] for book, doc in books.items()}
    paths = {read(p)["book"]: p for p in (DIRECTION / "books").glob("*.json")}
    remaining = {book for book, number in order.items() if number >= 42}
    source = {
        (book, chapter["chapter"], verse["verse"]): verse["text"]
        for book, doc in books.items() if book in remaining
        for chapter in doc["chapters"] for verse in chapter["verses"]
    }
    return books, order, paths, remaining, source


def render(source, edits):
    result = source
    for edit in sorted(edits, key=lambda item: item["startOffset"], reverse=True):
        if source[edit["startOffset"]:edit["endOffset"]] != edit["expected"]:
            raise RuntimeError(f"invalid existing edit: {edit}")
        result = result[:edit["startOffset"]] + edit["replacement"] + result[edit["endOffset"]:]
    return result


def make_family_rules(source):
    rules = []
    for expected, replacement, expected_count, category, reason in STABLE_FAMILIES:
        pattern = re.compile(rf"(?<![A-Za-z]){re.escape(expected)}(?![A-Za-z])", re.I)
        hits = []
        for (book, chapter, verse), text in source.items():
            for _ in pattern.finditer(text):
                hits.append((book, chapter, verse))
        if len(hits) != expected_count:
            raise RuntimeError(f"unchecked {expected!r} occurrence count: {len(hits)} != {expected_count}")
        for book, chapter, verse in sorted(set(hits)):
            rules.append(r(book, chapter, verse, expected, replacement, category, reason, True))

    for expected, replacement, expected_count, category, reason in PHRASE_FAMILIES:
        pattern = re.compile(rf"(?<![A-Za-z]){re.escape(expected)}(?![A-Za-z])", re.I)
        hits = []
        for (book, chapter, verse), text in source.items():
            hits.extend((book, chapter, verse) for _ in pattern.finditer(text))
        if len(hits) != expected_count:
            raise RuntimeError(f"unchecked {expected!r} phrase count: {len(hits)} != {expected_count}")
        for book, chapter, verse in sorted(set(hits)):
            rules.append(r(book, chapter, verse, expected, replacement, category, reason, False))

    # Sepulchre is stable except for the grave image in Romans 3:13.
    pattern = re.compile(r"(?<![A-Za-z])sepulchre(?![A-Za-z])", re.I)
    hits = []
    for (book, chapter, verse), text in source.items():
        ref = f"{book}.{chapter}.{verse}"
        if ref in WORD_EXCLUSIONS["sepulchre"]:
            continue
        hits.extend((book, chapter, verse) for _ in pattern.finditer(text))
    if len(hits) != 22:
        raise RuntimeError(f"unchecked sepulchre count: {len(hits)} != 22")
    for book, chapter, verse in sorted(set(hits)):
        rules.append(r(book, chapter, verse, "sepulchre", "tomb", "archaic-tomb-term", "Sepulchre means tomb in this burial setting.", True))

    # Divers means various in ten reviewed verses; Acts 19:9 is handled above.
    pattern = re.compile(r"(?<![A-Za-z])divers(?![A-Za-z])", re.I)
    hits = []
    for (book, chapter, verse), text in source.items():
        if (book, chapter, verse) == ("ACT", 19, 9):
            continue
        hits.extend((book, chapter, verse) for _ in pattern.finditer(text))
    if len(hits) != 10:
        raise RuntimeError(f"unchecked divers count: {len(hits)} != 10")
    for book, chapter, verse in sorted(set(hits)):
        rules.append(r(book, chapter, verse, "divers", "various", "false-friend-variety-term", "Divers means various in this reviewed context.", True))

    # Food terms, excluding the meal and solid-food phrases handled explicitly.
    phrase_refs = {(x["book"], x["chapter"], x["verse"]) for x in CONTEXT_RULES if "meat" in x["expected"]}
    for word, replacement, expected_count in (("meat", "food", 43), ("meats", "foods", 6)):
        pattern = re.compile(rf"(?<![A-Za-z]){word}(?![A-Za-z])", re.I)
        seen = 0
        for ref, text in source.items():
            matches = list(pattern.finditer(text))
            seen += len(matches)
            if not matches or ref in phrase_refs:
                continue
            rules.append(r(*ref, word, replacement, "false-friend-food-term", f"{word.capitalize()} means food in this reviewed context.", True))
        if seen != expected_count:
            raise RuntimeError(f"unchecked {word} count: {seen} != {expected_count}")

    # The repeated Johannine affirmation needs punctuation after both words
    # are modernized. Likewise, nigh unto becomes near before the obsolete
    # preposition is removed. Counts keep both passes bounded to reviewed text.
    double_verily = []
    nigh_unto = []
    for ref, text in source.items():
        if re.search(r"(?<![A-Za-z])Verily verily(?![A-Za-z])", text, re.I):
            double_verily.append(ref)
        if re.search(r"(?<![A-Za-z])nigh unto(?![A-Za-z])", text, re.I):
            nigh_unto.append(ref)
    if len(double_verily) != 25 or len(nigh_unto) != 13:
        raise RuntimeError(f"unchecked post-pass counts: verily={len(double_verily)}, nigh_unto={len(nigh_unto)}")
    for ref in double_verily:
        rules.append(r(*ref, "Truly truly", "Truly, truly", "grammar-repeated-affirmation", "A comma separates the repeated solemn affirmation."))
    for ref in nigh_unto:
        rules.append(r(*ref, "near unto", "near", "grammar-modern-preposition", "Near no longer needs the archaic preposition unto."))
    return rules


def replace_rule(text, entry):
    if entry["word"]:
        pattern = re.compile(rf"(?<![A-Za-z]){re.escape(entry['expected'])}(?![A-Za-z])", re.I)
        matches = list(pattern.finditer(text))
        if not matches:
            replacement_pattern = re.compile(rf"(?<![A-Za-z]){re.escape(entry['replacement'])}(?![A-Za-z])", re.I)
            if replacement_pattern.search(text):
                return text, 0
            raise RuntimeError(f"missing word {entry['expected']!r}")
        return pattern.sub(lambda match: recase(match.group(0), entry["replacement"]), text), len(matches)
    count = text.lower().count(entry["expected"].lower())
    if not count:
        if entry["replacement"].lower() in text.lower():
            return text, 0
        raise RuntimeError(f"missing phrase {entry['expected']!r}")
    pattern = re.compile(re.escape(entry["expected"]), re.I)
    return pattern.sub(lambda match: recase(match.group(0), entry["replacement"]), text), count


def main():
    books, order, paths, remaining, source = corpus_and_paths()
    directions = {book: read(paths[book]) for book in remaining}
    rules = make_family_rules(source) + CONTEXT_RULES
    grouped = defaultdict(list)
    for entry in rules:
        grouped[(entry["book"], entry["chapter"], entry["verse"])].append(entry)

    applied = []
    changed_books = set()
    verified_occurrences = 0
    for ref, entries in sorted(grouped.items(), key=lambda item: (order[item[0][0]], item[0][1], item[0][2])):
        book, chapter, verse = ref
        direction = directions[book]
        patch = next((item for item in direction.get("verses", []) if item["chapter"] == chapter and item["verse"] == verse), None)
        original = source[ref]
        current = render(original, [] if patch is None else patch["edits"])
        before = current
        local_applied = []
        for entry_index, entry in enumerate(entries):
            try:
                current, count = replace_rule(current, entry)
            except RuntimeError as error:
                superseded = any(
                    entry["replacement"].casefold() in later["expected"].casefold()
                    and later["replacement"].casefold() in current.casefold()
                    for later in entries[entry_index + 1:]
                )
                if superseded:
                    count = 0
                else:
                    raise RuntimeError(f"{book}.{chapter}.{verse}: {error}") from error
            if count:
                verified_occurrences += count
                local_applied.append(entry)
        if current == before:
            continue
        evidence_url = (
            "https://www.biblegateway.com/passage/?search="
            f"{book}+{chapter}%3A{verse}&version=KJV%3BNKJV%3BNIV%3BESV%3BNRSVUE"
        )
        edit = {
            "startOffset": 0,
            "endOffset": len(original),
            "expected": original,
            "replacement": current,
            "category": "remaining-new-testament-context-review",
            "reason": "The complete verse preserves earlier approved edits and the newly reviewed contextual clarifications.",
            "evidence": [{"label": "Complete-verse KJV, NKJV, NIV, ESV and NRSVUE control", "url": evidence_url}],
        }
        new_patch = {"chapter": chapter, "verse": verse, "sourceTextSha256": sha(original), "edits": [edit]}
        if patch is None:
            direction.setdefault("verses", []).append(new_patch)
        else:
            patch.clear()
            patch.update(new_patch)
        for entry in local_applied:
            applied.append({**entry, "reference": f"{book}.{chapter}.{verse}", "evidenceUrl": evidence_url})
        changed_books.add(book)

    for book in changed_books:
        direction = directions[book]
        direction["verses"].sort(key=lambda item: (item["chapter"], item["verse"]))
        direction["editorialStatus"] = "approved-remaining-new-testament-context-review-v13"
        direction["ownerReview"] = {
            "contentVersion": VERSION,
            "review": "KJV remaining New Testament complete-context review",
            "requiredFullTest": True,
        }
        write(paths[book], direction, compact=True)

    source_path = DIRECTION / "reading_2026.package-source.json"
    package_source = read(source_path)
    package_source["contentVersion"] = VERSION
    package_source["generatedAt"] = STAMP
    package_source["editorialPolicy"]["version"] = VERSION
    package_source["editorialPolicy"]["description"] = (
        "Only exact, occurrence-reviewed wording that materially improves comprehension is projected. "
        "The packaged KJV remains immutable, and ambiguous or doctrinal families remain pending."
    )
    write(source_path, package_source)

    direction_books = [read(path) for path in paths.values()]
    direction_books.sort(key=lambda item: order[item["book"]])
    payload = {
        "books": direction_books,
        "contentVersion": VERSION,
        "editorialPolicy": package_source["editorialPolicy"],
        "filterId": package_source["filterId"],
        "format": "shine-reading-filter-package",
        "normalizationId": package_source["normalizationId"],
        "schemaVersion": 1,
        "sourceCorpusSha256": package_source["sourceCorpusSha256"],
        "sourceVersionId": package_source["sourceVersionId"],
    }
    raw = canonical(payload).encode()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    packages = DIRECTION / "packages"
    package_path = packages / "reading_2026.kjv.v1.package.json.gz"
    package_path.write_bytes(compressed)
    coverage = {
        "expectedBookCount": 66,
        "includedBookCount": len(direction_books),
        "changedVerseCount": sum(len(book["verses"]) for book in direction_books),
        "editCount": sum(len(verse["edits"]) for book in direction_books for verse in book["verses"]),
    }
    manifest = {
        "format": "shine-reading-filter-manifest",
        "filterId": package_source["filterId"],
        "schemaVersion": 1,
        "contentVersion": VERSION,
        "sourceVersionId": package_source["sourceVersionId"],
        "sourceCorpusSha256": package_source["sourceCorpusSha256"],
        "normalizationId": package_source["normalizationId"],
        "contentSha256": sha(compressed),
        "sizeBytes": len(compressed),
        "expandedSizeBytes": len(raw),
        "mimeType": "application/vnd.shine.reading-filter+gzip",
        "generatedAt": "2026-09-13",
        "editorialPolicy": package_source["editorialPolicy"],
        "coverage": coverage,
        "books": [
            {
                "id": book["book"],
                "order": order[book["book"]],
                "sourceFile": paths[book["book"]].name,
                "sourceContentSha256": book["sourceContentSha256"],
                "payloadSha256": sha(canonical(book)),
                "changedVerseCount": len(book["verses"]),
                "editCount": sum(len(verse["edits"]) for verse in book["verses"]),
            }
            for book in direction_books
        ],
    }
    write(packages / "reading_2026.kjv.v1.manifest.json", manifest)

    registry = read(REGISTRY)
    registry["updatedAt"] = STAMP
    registry["activeContentVersion"] = VERSION
    known = {(item["reference"], item["expected"], item["replacement"]) for item in registry["applied"]}
    for entry in applied:
        key = (entry["reference"], entry["expected"], entry["replacement"])
        if key in known:
            continue
        registry["applied"].append({
            "reference": entry["reference"],
            "expected": entry["expected"],
            "replacement": entry["replacement"],
            "category": entry["category"],
            "reason": entry["reason"],
            "evidenceUrl": entry["evidenceUrl"],
        })
        known.add(key)

    registry["pending"] = [
        item for item in registry.get("pending", [])
        if not item.get("id", "").startswith("nt-kjv-v13-")
    ]
    all_source = list(source.items())
    for pending_id, (terms, reason) in PENDING_FAMILIES.items():
        refs = {}
        patterns = [re.compile(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", re.I) for term in terms]
        for (book, chapter, verse), text in all_source:
            if any(pattern.search(text) for pattern in patterns):
                refs[(book, chapter, verse)] = {"book": book, "chapter": chapter, "verse": verse}
        registry["pending"].append({
            "id": pending_id,
            "status": "pending-review",
            "scope": "remaining-new-testament",
            "term": " / ".join(terms),
            "proposedOptions": ["Retain with an explanatory note", "Modernize after focused clause review"],
            "reason": reason,
            "references": [refs[key] for key in sorted(refs, key=lambda ref: (order[ref[0]], ref[1], ref[2]))],
            "evidence": [{
                "label": "KJV remaining New Testament multi-version contextual control",
                "url": "https://www.biblegateway.com/passage/?search=Luke-Rev&version=KJV%3BNKJV%3BNIV%3BESV%3BNRSVUE",
            }],
        })
    write(REGISTRY, registry)

    print(json.dumps({
        "contentVersion": VERSION,
        "reviewedSourceVerses": len(source),
        "reviewedRules": len(rules),
        "verifiedOccurrences": verified_occurrences,
        "changedBooks": len(changed_books),
        "newRegistryRecords": len(applied),
        "pendingFamilies": len(PENDING_FAMILIES),
        "coverage": coverage,
        "contentSha256": manifest["contentSha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
