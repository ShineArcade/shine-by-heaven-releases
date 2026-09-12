import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"
BOOK = "MRK"
VERSION = 12


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, compact=False):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2,
                               separators=(",", ":") if compact else None) + "\n", encoding="utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def c(chapter, verse, expected, replacement, category, reason):
    return chapter, verse, expected, replacement, category, reason


# Every rule is bound to a reviewed Mark reference. No book-wide search and
# replace is performed; pronouns, doctrine, metaphors and textual variants are
# intentionally excluded for focused review.
CHANGES = [
    c(1,4,"remission of sins","forgiveness of sins","historical-forgiveness-term","Remission means forgiveness in John's baptismal proclamation."),
    c(1,6,"a girdle of a skin about his loins","a leather belt around his waist","archaic-clothing-phrase","The phrase describes John's leather belt around his waist."),
    c(1,7,"the latchet of whose shoes","the straps of whose sandals","historical-footwear-phrase","Latchet and shoes describe the straps of sandals in this scene."),
    c(1,7,"stoop down and unloose","stoop down and untie","archaic-untie-verb","Unloose means untie the sandal straps."),
    c(1,8,"Holy Ghost","Holy Spirit","historical-spirit-term","Holy Ghost is modernized to Holy Spirit without changing the referent."),
    c(1,10,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(1,18,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(1,18,"forsook their nets","left their nets","archaic-departure-verb","Forsook means they left their nets to follow Jesus."),
    c(1,19,"in the ship","in the boat","historical-vessel-term","Ship denotes the fishing boat on the Sea of Galilee."),
    c(1,20,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(1,20,"in the ship","in the boat","historical-vessel-term","Ship denotes Zebedee's fishing boat."),
    c(1,21,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(1,25,"Hold thy peace and come out of him","Be silent, and come out of him","archaic-silence-command","The command orders the unclean spirit to be silent and leave the man."),
    c(1,26,"had torn him","had convulsed him","false-friend-convulsion-verb","Torn describes a convulsion; the man's body was not torn apart."),
    c(1,32,"at even","in the evening","archaic-time-phrase","At even means in the evening."),
    c(1,32,"possessed with devils","demon-possessed","historical-demon-phrase","Devils refers to demons in this healing account."),
    c(1,34,"divers diseases","various diseases","false-friend-variety-term","Divers means various, not people who dive."),
    c(1,34,"cast out many devils","cast out many demons","historical-demon-term","Devils refers to demons."),
    c(1,34,"suffered not the devils to speak","did not allow the demons to speak","archaic-permission-clause","Suffered not means did not allow; devils refers to demons."),
    c(1,39,"cast out devils","cast out demons","historical-demon-term","Devils refers to demons."),
    c(1,43,"straitly charged him","sternly warned him","archaic-warning-phrase","Straitly charged means sternly warned."),
    c(1,43,"forthwith sent him away","sent him away at once","archaic-speed-phrase","Forthwith means at once."),
    c(1,30,"they tell him of her","they told him about her","grammar-narrative-tense","The narrative continues in the past tense when they told Jesus about Simon's mother-in-law."),

    c(2,1,"it was noised that he was in the house","it became known that he was in the house","false-friend-report-phrase","Noised means the news became known, not that a sound was made."),
    c(2,2,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(2,2,"insomuch that","so that","archaic-result-connector","Insomuch that introduces the result of the crowd gathering."),
    c(2,3,"bringing one sick of the palsy, which was borne of four","bringing a paralyzed man carried by four people","obsolete-medical-phrase","Palsy denotes paralysis and borne means carried; the whole phrase preserves the four carriers without duplicating the action."),
    c(2,4,"come nigh unto him for the press","come near him because of the crowd","archaic-crowd-phrase","Press denotes the crowd blocking access to Jesus."),
    c(2,4,"the bed wherein the sick of the palsy lay","the mat on which the paralyzed man lay","obsolete-medical-phrase","The object lowered through the roof was the paralyzed man's mat."),
    c(2,5,"the sick of the palsy","the paralyzed man","obsolete-medical-term","Palsy denotes paralysis."),
    c(2,8,"that they so reasoned within themselves","that they were reasoning within themselves","archaic-reasoning-phrase","The scribes were deliberating inwardly; the complete phrase preserves natural word order."),
    c(2,9,"the sick of the palsy","the paralyzed man","obsolete-medical-term","Palsy denotes paralysis."),
    c(2,10,"the sick of the palsy","the paralyzed man","obsolete-medical-term","Palsy denotes paralysis."),
    c(2,12,"We never saw it on this fashion","We have never seen anything like this","archaic-manner-phrase","On this fashion means in this manner; the complete sentence avoids retaining a false object pronoun."),
    c(2,14,"receipt of custom","tax collection booth","historical-tax-phrase","The phrase identifies Levi's tax collection post."),
    c(2,15,"sat at meat","was dining","false-friend-meal-phrase","Sat at meat means was dining, not sitting only with meat."),
    c(2,15,"publicans","tax collectors","historical-tax-term","Publicans were tax collectors."),
    c(2,16,"publicans","tax collectors","historical-tax-term","Publicans were tax collectors."),
    c(2,19,"children of the bridechamber","wedding guests","historical-wedding-phrase","The phrase denotes the bridegroom's wedding companions."),
    c(2,21,"No man also seweth a piece of new cloth on an old garment else the new piece that filled it up taketh away from the old and the rent is made worse","No one sews a piece of new cloth on an old garment; otherwise the new patch pulls away from the old, and the tear becomes worse","archaic-garment-parable","The complete sentence keeps the patch image clear and prevents obsolete wording from obscuring the result."),
    c(2,22,"old bottles","old wineskins","historical-wineskin-term","Bottles denotes leather wineskins."),
    c(2,22,"the bottles","the wineskins","historical-wineskin-term","Bottles denotes leather wineskins."),
    c(2,22,"new bottles","new wineskins","historical-wineskin-term","Bottles denotes leather wineskins."),
    c(2,23,"corn fields","grainfields","historical-grain-term","Corn means grain in this British English context."),
    c(2,23,"ears of corn","heads of grain","historical-grain-term","The disciples plucked heads of grain, not modern maize."),

    c(3,4,"held their peace","remained silent","archaic-silence-phrase","Held their peace means remained silent."),
    c(3,6,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(3,9,"a small ship","a small boat","historical-vessel-term","Ship denotes a small boat kept ready for Jesus."),
    c(3,9,"should wait on him","should be kept ready for him","false-friend-readiness-phrase","Wait on means that the boat was to remain ready for Jesus, not that it served him as an attendant."),
    c(3,9,"lest they should throng him","so they would not crush him","archaic-crowding-phrase","Throng describes the crowd pressing hard against Jesus."),
    c(3,10,"insomuch that they pressed upon him for to touch him, as many as had plagues","so that all who had afflictions pressed toward him to touch him","false-friend-affliction-clause","Plagues denotes personal afflictions; the complete clause identifies those pressing toward Jesus to touch him."),
    c(3,12,"straitly charged them","sternly warned them","archaic-warning-phrase","Straitly charged means sternly warned."),
    c(3,15,"cast out devils","cast out demons","historical-demon-term","Devils refers to demons."),
    c(3,22,"by the prince of the devils casteth he out devils","by the prince of the demons he casts out demons","archaic-demon-clause","The complete clause states the accusation that Jesus expelled demons by their prince."),
    c(3,27,"spoil his goods","plunder his possessions","false-friend-plunder-phrase","Spoil means plunder and goods means possessions."),
    c(3,27,"spoil his house","plunder his house","false-friend-plunder-phrase","Spoil means plunder the bound strong man's house."),

    c(4,4,"fowls of the air","birds of the air","archaic-bird-term","Fowls means birds."),
    c(4,17,"they are offended","they fall away","false-friend-fall-away-verb","Offended describes abandoning the word under affliction or persecution."),
    c(4,21,"under a bushel","under a basket","historical-container-term","Bushel denotes the measuring container placed over a lamp."),
    c(4,21,"on a candlestick","on a lampstand","historical-lampstand-term","Candlestick denotes a stand for an oil lamp."),
    c(4,21,"Is a candle brought","Is a lamp brought","historical-lamp-term","Candle denotes the oil lamp placed on a lampstand in this setting."),
    c(4,28,"For the earth bringeth forth fruit of herself","For the earth produces crops by itself","archaic-growth-clause","The earth produces the crop by itself in the parable."),
    c(4,28,"first the blade then the ear after that the full corn in the ear","first the stalk, then the head, after that the full grain in the head","historical-growth-phrase","The sequence describes the growth of grain from stalk to mature head."),
    c(4,32,"all herbs","all garden plants","historical-garden-term","Herbs denotes cultivated garden plants in the comparison."),
    c(4,32,"fowls of the air","birds of the air","archaic-bird-term","Fowls means birds."),
    c(4,36,"in the ship","in the boat","historical-vessel-term","Ship denotes the boat used to cross the lake."),
    c(4,36,"other little ships","other small boats","historical-vessel-term","Ships denotes the other small boats accompanying them."),
    c(4,37,"great storm of wind","great windstorm","archaic-storm-phrase","The phrase describes a violent windstorm."),
    c(4,37,"the ship","the boat","historical-vessel-term","Ship denotes the boat on the lake."),
    c(4,38,"hinder part of the ship","stern of the boat","historical-vessel-location","The hinder part is the stern of the boat."),
    c(4,39,"Peace be still And the wind ceased","Be silent, be still. And the wind ceased","archaic-silence-command","The two commands order the sea to be silent and still; the period preserves the boundary before the narrative resumes."),

    c(5,2,"out of the ship","out of the boat","historical-vessel-term","Ship denotes the boat arriving at shore."),
    c(5,4,"fetters and chains","shackles and chains","historical-restraint-term","Fetters are restraining shackles."),
    c(5,4,"plucked asunder","torn apart","archaic-break-phrase","Plucked asunder means torn apart."),
    c(5,4,"fetters broken in pieces","shackles broken in pieces","historical-restraint-term","Fetters are restraining shackles."),
    c(5,10,"besought him much","begged him earnestly","archaic-pleading-phrase","Besought means begged earnestly."),
    c(5,11,"herd of swine","herd of pigs","historical-animal-term","Swine means pigs."),
    c(5,12,"all the devils besought him","all the demons begged him","archaic-demon-clause","Devils refers to demons and besought means begged."),
    c(5,12,"into the swine","into the pigs","historical-animal-term","Swine means pigs."),
    c(5,13,"forthwith","at once","archaic-speed-adverb","Forthwith means at once."),
    c(5,13,"gave them leave","allowed them","archaic-permission-phrase","Gave them leave means allowed the spirits to enter the pigs."),
    c(5,13,"entered into the swine","entered the pigs","historical-animal-term","Swine means pigs."),
    c(5,13,"were choked in the sea","drowned in the sea","archaic-drowning-phrase","Choked in the sea means the herd drowned after running down the steep bank."),
    c(5,14,"fed the swine","tended the pigs","historical-animal-phrase","The people were tending the herd of pigs."),
    c(5,15,"possessed with the devil","demon-possessed","historical-demon-phrase","Devil refers to the demon that had possessed the man."),
    c(5,16,"how it befell to him that was possessed with the devil","what had happened to the man who had been demon-possessed","archaic-event-clause","The complete clause identifies what happened to the man and avoids leaving an obsolete relative construction around the modernized term."),
    c(5,16,"concerning the swine","concerning the pigs","historical-animal-term","Swine means pigs."),
    c(5,17,"began to pray him to depart out of their coasts","began to beg him to leave their region","archaic-request-phrase","Pray means beg and coasts means their surrounding region; the full clause avoids the unidiomatic phrase leave out of."),
    c(5,18,"into the ship","into the boat","historical-vessel-term","Ship denotes the boat."),
    c(5,18,"possessed with the devil","demon-possessed","historical-demon-phrase","Devil refers to the demon that had possessed the man."),
    c(5,18,"prayed him that he might be with him","begged to go with him","archaic-request-phrase","Prayed means begged; the man asked to accompany Jesus."),
    c(5,21,"by ship","by boat","historical-vessel-term","Ship denotes the boat used to cross the lake."),
    c(5,21,"much people gathered unto him","a large crowd gathered around him","archaic-crowd-phrase","Much people means a large crowd gathered around Jesus."),
    c(5,21,"nigh unto the sea","near the sea","archaic-near-term","Nigh means near."),
    c(5,23,"besought him greatly","begged him earnestly","archaic-pleading-phrase","Besought means begged earnestly."),
    c(5,23,"lieth at the point of death","is at the point of death","archaic-near-death-phrase","Lieth is an obsolete form; the daughter is near death."),
    c(5,25,"an issue of blood twelve years","chronic bleeding for twelve years","historical-medical-phrase","Issue of blood denotes persistent bleeding over twelve years."),
    c(5,29,"the fountain of her blood was dried up","her bleeding stopped","historical-medical-phrase","The phrase states that the woman's bleeding stopped."),
    c(5,29,"that plague","that affliction","false-friend-affliction-term","Plague denotes the woman's affliction, not an epidemic."),
    c(5,30,"virtue had gone out of him","power had gone out of him","false-friend-power-term","Virtue means healing power, not moral goodness."),
    c(5,30,"the press","the crowd","false-friend-crowd-term","Press denotes the crowd surrounding Jesus."),
    c(5,30,"turned him about","turned around","archaic-turn-phrase","Turned him about means Jesus turned around in the crowd."),
    c(5,34,"whole of thy plague","healed of that affliction","archaic-healing-phrase","Whole means healed and plague denotes the affliction; the wording avoids mixing pronoun systems."),
    c(5,39,"make ye this ado","make this commotion","archaic-commotion-term","Ado means commotion."),
    c(5,39,"the damsel","the girl","archaic-girl-term","Damsel means girl."),
    c(5,40,"laughed him to scorn","laughed at him","archaic-ridicule-phrase","The mourners ridiculed Jesus by laughing at him."),
    c(5,40,"the damsel","the girl","archaic-girl-term","Damsel means girl."),
    c(5,41,"the damsel","the girl","archaic-girl-term","Damsel means girl."),
    c(5,41,"Damsel, I say unto thee, arise","Girl, I say unto thee, arise","archaic-girl-phrase","Damsel means girl; the direct command and KJV pronoun system are retained."),
    c(5,42,"straightway the damsel arose","immediately the girl arose","archaic-speed-and-girl-phrase","Straightway means immediately and damsel means girl."),
    c(5,42,"astonished with a great astonishment","completely astonished","archaic-amazement-phrase","The expression communicates the great degree of their astonishment without repeating the same word."),
    c(5,43,"charged them straitly","sternly ordered them","archaic-command-phrase","Charged them straitly means sternly ordered them."),

    c(6,2,"mighty works are wrought by his hands","miracles are performed by his hands","archaic-miracle-phrase","Mighty works denotes miracles and wrought means performed."),
    c(6,2,"From whence hath this man these things","From where did this man get these things","archaic-origin-question","Whence asks where Jesus received these things; the complete question uses current English syntax."),
    c(6,5,"no mighty work","no miracle","archaic-miracle-term","Mighty work means miracle."),
    c(6,5,"a few sick folk","a few sick people","archaic-people-term","Folk means people."),
    c(6,8,"no scrip","no travel bag","historical-travel-bag","Scrip is a travel bag for provisions."),
    c(6,13,"cast out many devils","cast out many demons","historical-demon-term","Devils refers to demons."),
    c(6,14,"mighty works do shew forth themselves in him","miraculous powers are at work in him","archaic-miracle-phrase","The phrase attributes miraculous powers to the risen John in Herod's explanation."),
    c(6,19,"had a quarrel against him","held a grudge against him","false-friend-grudge-phrase","Quarrel means a continuing grievance or grudge here."),
    c(6,22,"the damsel","the girl","archaic-girl-term","Damsel means girl."),
    c(6,22,"daughter of the said Herodias","daughter of Herodias","archaic-said-reference","Said is an obsolete legal-style reference to the previously named Herodias."),
    c(6,25,"came in straightway with haste unto the king","came immediately to the king","archaic-speed-phrase","The girl returned immediately to the king; the urgency remains explicit in her demand for the head right now."),
    c(6,25,"by and by in a charger","right now on a platter","false-friend-platter-phrase","By and by means immediately and charger means platter."),
    c(6,28,"in a charger","on a platter","historical-platter-term","Charger means platter."),
    c(6,28,"the damsel","the girl","archaic-girl-term","Damsel means girl."),
    c(6,31,"had no leisure so much as to eat","did not even have time to eat","false-friend-opportunity-phrase","No leisure means they lacked time to eat."),
    c(6,32,"by ship","by boat","historical-vessel-term","Ship denotes the boat."),
    c(6,33,"ran afoot thither","ran there on foot","archaic-movement-phrase","Afoot thither means there on foot."),
    c(6,33,"outwent them","arrived ahead of them","archaic-arrival-verb","Outwent means the people reached the place before the boat."),
    c(6,37,"two hundred pennyworth of bread","two hundred denarii worth of bread","historical-coin-phrase","Pennyworth refers to denarii, not modern pennies."),
    c(6,39,"by companies","in groups","archaic-group-term","Companies means organized groups."),
    c(6,40,"in ranks","in groups","archaic-group-term","Ranks means organized groups seated together."),
    c(6,45,"straightway he constrained his disciples to get","immediately he made his disciples get","archaic-urgency-phrase","Constrained means Jesus made them embark without delay; the complete phrase remains grammatical."),
    c(6,45,"into the ship","into the boat","historical-vessel-term","Ship denotes the boat."),
    c(6,47,"when even was come","when evening came","archaic-time-phrase","Even means evening."),
    c(6,47,"the ship","the boat","historical-vessel-term","Ship denotes the boat on the lake."),
    c(6,48,"toiling in rowing","struggling to row","archaic-rowing-phrase","The wind made rowing difficult."),
    c(6,48,"about the fourth watch of the night","before dawn","historical-night-watch","The fourth watch corresponds to the final hours before dawn."),
    c(6,51,"into the ship","into the boat","historical-vessel-term","Ship denotes the boat."),
    c(6,51,"sore amazed in themselves beyond measure, and wondered","utterly amazed and wondered","archaic-intensity-phrase","The phrase expresses overwhelming amazement without stacking two modern intensifiers."),
    c(6,54,"out of the ship","out of the boat","historical-vessel-term","Ship denotes the boat."),
    c(6,54,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(6,54,"they knew him","they recognized him","false-friend-recognition-verb","Knew means the people recognized Jesus when he left the boat."),
    c(6,56,"besought him","begged him","archaic-pleading-verb","Besought means begged."),
    c(6,56,"were made whole","were healed","archaic-healing-phrase","Made whole means healed."),

    c(7,11,"by whatsoever thou mightest be profited by me","whatever help thou mightest have received from me","archaic-support-phrase","The saying declares parental support dedicated as Corban while retaining the KJV pronoun system."),
    c(7,12,"ye suffer him no more","ye no longer allow him","archaic-permission-phrase","Suffer means allow; the KJV pronoun system remains intact."),
    c(7,12,"do ought for his father","do anything for his father","archaic-anything-term","Ought means anything here."),
    c(7,19,"Because it entereth not into his heart but into the belly and goeth out into the draught purging all meats","Because it does not enter his heart but his stomach, and then passes out of the body, making all foods clean","historical-bodily-phrase","Draught is an old bodily-elimination term and meats means foods generally; the complete clause keeps its verbs consistent."),
    c(7,26,"besought him","begged him","archaic-pleading-verb","Besought means begged."),
    c(7,26,"cast forth the devil out of her daughter","cast the demon out of her daughter","historical-demon-phrase","Devil refers to the demon in her daughter; the full phrase avoids duplicating out."),
    c(7,27,"it is not meet","it is not right","false-friend-right-term","Meet means right or appropriate."),
    c(7,29,"the devil is gone out","the demon has gone out","historical-demon-term","Devil refers to the demon in her daughter."),
    c(7,30,"found the devil gone out","found that the demon had gone out","historical-demon-clause","The woman discovered that the demon had left her daughter."),
    c(7,30,"her daughter laid upon the bed","her daughter lying upon the bed","grammar-participle-phrase","Lying is the correct participle for the daughter's position on the bed."),
    c(7,31,"departing from the coasts","departing from the region","false-friend-region","Coasts means the region around Tyre and Sidon."),
    c(7,31,"through the midst of the coasts of Decapolis","through the region of Decapolis","false-friend-region","Coasts means the region of Decapolis."),
    c(7,32,"one that was deaf, and had an impediment in his speech","a deaf man with a speech impediment","historical-disability-phrase","The phrase identifies a man who could not hear and had difficulty speaking."),
    c(7,35,"the string of his tongue was loosed, and he spake plain","his speech impediment disappeared, and he spoke clearly","historical-speech-phrase","The healing removes the speech impediment and restores clear speech."),
    c(7,37,"he maketh both the deaf to hear, and the dumb to speak","he enables deaf people to hear and people unable to speak to speak","historical-disability-phrase","The current wording describes the restored abilities without obsolete labels."),

    c(8,3,"divers of them","some of them","false-friend-quantity-term","Divers means some in this crowd."),
    c(8,4,"From whence can a man satisfy these men with bread here in the wilderness","Where can anyone get enough bread to feed all these people here in the wilderness","archaic-feeding-question","The complete question asks where enough food could be obtained for the crowd in the wilderness."),
    c(8,8,"they took up of the broken meat that was left seven baskets","they collected seven baskets of leftover pieces","false-friend-food-phrase","Meat means food generally; the complete phrase states that seven baskets of pieces remained."),
    c(8,10,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(8,10,"into a ship","into a boat","historical-vessel-term","Ship denotes the boat."),
    c(8,11,"tempting him","testing him","false-friend-test-verb","The demand for a sign was intended to test Jesus."),
    c(8,13,"into the ship","into the boat","historical-vessel-term","Ship denotes the boat."),
    c(8,14,"in the ship","in the boat","historical-vessel-term","Ship denotes the boat."),
    c(8,15,"the leaven of the Pharisees","the yeast of the Pharisees","historical-yeast-term","Leaven means yeast in Jesus' warning image."),
    c(8,15,"the leaven of Herod","the yeast of Herod","historical-yeast-term","Leaven means yeast in Jesus' warning image."),
    c(8,16,"reasoned among themselves","discussed among themselves","archaic-discussion-verb","Reasoned means they discussed the lack of bread."),
    c(8,22,"they bring a blind man unto him, and besought him to touch him","they bring a blind man to him and beg him to touch him","archaic-pleading-clause","Besought means begged; the complete phrase keeps the narrative tense consistent."),
    c(8,23,"if he saw ought","whether he saw anything","archaic-anything-phrase","Ought means anything in Jesus' question."),
    c(8,31,"be rejected of the elders, and of the chief priests, and scribes","be rejected by the elders, chief priests, and scribes","archaic-agent-phrase","Modern English uses by for all the leaders who reject him."),

    c(9,3,"his raiment became shining, exceeding white as snow; so as no fuller on earth can white them","his clothes became shining, exceedingly white as snow, whiter than any launderer on earth could make them","historical-launderer-phrase","The whole phrase modernizes raiment, fuller and white as a verb while preserving the extraordinary whiteness."),
    c(9,5,"three tabernacles","three shelters","historical-shelter-term","Tabernacles means temporary shelters in this scene."),
    c(9,6,"sore afraid","very afraid","archaic-intensity-phrase","Sore intensifies their fear."),
    c(9,12,"be set at nought","be treated with contempt","archaic-contempt-phrase","Set at nought means treated as worthless or with contempt."),
    c(9,13,"whatsoever they listed","whatever they wanted","archaic-desire-phrase","Listed means wanted in this context."),
    c(9,15,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(9,17,"my son, which hath a dumb spirit","my son, who has a spirit that prevents him from speaking","historical-disability-phrase","Dumb describes the effect of the spirit on speech, not the son's intelligence."),
    c(9,18,"wheresoever he taketh him, he teareth him","wherever it seizes him, it convulses him","false-friend-convulsion-phrase","The spirit seizes and convulses the son; teareth does not mean his body is torn apart."),
    c(9,18,"he foameth, and gnasheth with his teeth, and pineth away","he foams at the mouth, grinds his teeth, and becomes rigid","historical-seizure-phrase","The phrase describes symptoms of the convulsion in current language."),
    c(9,19,"how long shall I suffer you bring him unto me","how long must I endure you? Bring him unto me","archaic-endure-clause","Suffer means endure in Jesus' lament; the punctuation separates the command to bring the boy."),
    c(9,20,"straightway the spirit tare him","immediately the spirit convulsed him","false-friend-convulsion-phrase","Tare describes a convulsion, not bodily tearing."),
    c(9,20,"he fell on the ground, and wallowed foaming","he fell on the ground and rolled around, foaming at the mouth","archaic-convulsion-phrase","Wallowed here describes the boy rolling on the ground during the convulsion."),
    c(9,24,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(9,25,"dumb and deaf spirit","spirit that prevents speech and hearing","historical-disability-phrase","The command identifies the spirit by its effects without obsolete labels."),
    c(9,26,"rent him sore","convulsed him violently","false-friend-convulsion-phrase","Rent him sore describes a violent convulsion, not a torn body."),
    c(9,38,"casting out devils","casting out demons","historical-demon-term","Devils refers to demons."),
    c(9,38,"we forbad him","we forbade him","historical-verb-form","Forbad is an obsolete form of forbade."),
    c(9,42,"whosoever shall offend one of these little ones that believe in me it is better for him that a millstone were hanged about his neck and he were cast into the sea","whoever causes one of these little ones who believe in me to stumble, it would be better for him if a millstone were hung around his neck and he were thrown into the sea","false-friend-stumble-clause","Offend means cause spiritual stumbling; the complete sentence keeps the believing little ones together and preserves the warning's comparison."),
    c(9,43,"hand offend thee","hand causes thee to sin","false-friend-stumble-phrase","Offend means cause to sin; the KJV pronoun system remains intact."),
    c(9,43,"enter into life maimed","enter life with one hand","historical-disability-phrase","Maimed describes the loss of the hand in the comparison."),
    c(9,45,"foot offend thee","foot causes thee to sin","false-friend-stumble-phrase","Offend means cause to sin; the KJV pronoun system remains intact."),
    c(9,45,"enter halt into life","enter life unable to walk","historical-disability-phrase","Halt is an obsolete term for impaired walking."),
    c(9,47,"eye offend thee","eye causes thee to sin","false-friend-stumble-phrase","Offend means cause to sin; the KJV pronoun system remains intact."),
    c(9,50,"lost his saltness","lost its flavor","false-friend-salt-phrase","Saltness means flavor in the salt image."),
    c(9,50,"wherewith will ye season it","how will ye restore its flavor","archaic-season-phrase","The question asks how the salt's flavor could be restored while retaining the KJV pronoun system."),

    c(10,1,"coasts of Judæa","region of Judæa","false-friend-region","Coasts means the region, not a seacoast."),
    c(10,1,"as he was wont","as was his custom","archaic-custom-phrase","Was wont means it was his customary practice."),
    c(10,2,"put away his wife","divorce his wife","archaic-divorce-phrase","Put away means divorce in this legal-marital context."),
    c(10,2,"tempting him","testing him","false-friend-test-verb","The Pharisees' question was intended to test Jesus."),
    c(10,4,"Moses suffered to write a bill of divorcement, and to put her away","Moses allowed a man to write a certificate of divorce and divorce her","archaic-divorce-clause","The sentence describes permission to issue a divorce certificate and divorce the wife."),
    c(10,8,"they twain","the two","archaic-number-term","Twain means two."),
    c(10,8,"no more twain","no longer two","archaic-number-term","Twain means two."),
    c(10,9,"put asunder","separate","archaic-separation-verb","Put asunder means separate."),
    c(10,14,"Suffer the little children","Allow the little children","archaic-permission-verb","Suffer means allow."),
    c(10,19,"Defraud not","Do not cheat","archaic-defraud-command","Defraud means cheat or deprive another unfairly."),
    c(10,21,"whatsoever thou hast","whatever thou hast","archaic-whatever-phrase","Whatsoever means whatever; the KJV pronoun system remains intact."),
    c(10,23,"How hardly shall they that have riches enter","How difficult it is for those who have riches to enter","false-friend-difficulty-phrase","Hardly means with difficulty, not scarcely; the full clause remains grammatical."),
    c(10,35,"we would that thou shouldest do for us whatsoever we shall desire","we want thee to do for us whatever we ask","archaic-request-clause","The complete request uses current syntax while retaining the KJV second-person pronoun system."),
    c(10,43,"your minister","your servant","historical-service-term","Minister means servant in the contrast with worldly authority."),
    c(10,44,"the chiefest","first","archaic-rank-term","Chiefest means first in rank."),
    c(10,45,"to be ministered unto but to minister","to be served but to serve","historical-service-phrase","Ministered means served in both halves of the contrast."),
    c(10,46,"highway side","roadside","archaic-roadside-term","Highway side means the roadside."),
    c(10,48,"many charged him that he should hold his peace","many ordered him to be silent","archaic-silence-clause","Charged means ordered and hold his peace means be silent."),
    c(10,48,"he cried the more a great deal","he cried out all the more","archaic-intensity-clause","The phrase means Bartimæus kept crying out even more loudly despite the warning."),
    c(10,49,"Be of good comfort","Take courage","archaic-encouragement-phrase","The bystanders encourage Bartimæus because Jesus is calling him."),

    c(11,3,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(11,3,"send him hither","send him here","archaic-direction-adverb","Hither means here."),
    c(11,13,"he came, if haply he might find any thing thereon","he came to see whether he might find anything on it","archaic-possibility-phrase","Haply means perhaps; the complete phrase states the purpose without leaving an unnecessary comma."),
    c(11,15,"moneychangers","money changers","historical-spacing","The current spelling separates the two words."),
    c(11,15,"began to cast out them that sold and bought","began to cast out those who sold and bought","archaic-word-order","The modern word order keeps those who sold and bought as the object of cast out."),
    c(11,16,"would not suffer","would not allow","archaic-permission-verb","Suffer means allow."),
    c(11,16,"any vessel through the temple","anything through the temple","false-friend-carried-object","Vessel denotes any carried object or merchandise in this context."),
    c(11,17,"den of thieves","den of robbers","historical-robber-term","The phrase refers to violent robbers using a den, not only secret theft."),
    c(11,25,"if ye have ought against any","if ye have anything against anyone","archaic-anything-phrase","Ought means anything; the KJV pronoun system remains intact."),
    c(11,31,"reasoned with themselves","discussed among themselves","archaic-discussion-verb","They discussed how to answer Jesus."),

    c(12,1,"set an hedge","put a hedge","historical-article-grammar","Modern English uses a before hedge."),
    c(12,1,"winefat","winepress","historical-winepress-term","Winefat denotes the lower receptacle of a winepress; winepress communicates the whole installation."),
    c(12,1,"digged a place","dug a place","archaic-dig-verb","Digged is an obsolete past-tense form of dug."),
    c(12,1,"let it out to husbandmen","leased it to tenant farmers","historical-tenant-phrase","Husbandmen are the tenant farmers to whom the vineyard was leased."),
    c(12,2,"the husbandmen","the tenant farmers","historical-tenant-term","Husbandmen are tenant farmers."),
    c(12,7,"those husbandmen","those tenant farmers","historical-tenant-term","Husbandmen are tenant farmers."),
    c(12,9,"the husbandmen","the tenant farmers","historical-tenant-term","Husbandmen are tenant farmers."),
    c(12,16,"image and superscription","image and inscription","historical-inscription-term","Superscription means the written inscription on the coin."),
    c(12,27,"do greatly err","are greatly mistaken","archaic-error-phrase","Err means be mistaken."),
    c(12,36,"Holy Ghost","Holy Spirit","historical-spirit-term","Holy Ghost is modernized to Holy Spirit without changing the referent."),
    c(12,39,"uppermost rooms at feasts","places of honor at feasts","false-friend-honor-phrase","Uppermost rooms means the places of highest honor, not upstairs rooms."),
    c(12,42,"two mites, which make a farthing","two small coins, worth only a fraction of a day's wage","historical-coin-phrase","The phrase explains the very small value without equating the coins with modern currency."),
    c(12,44,"all that she had even all her living","everything she had, all she had to live on","false-friend-livelihood-phrase","Living means her entire livelihood; the complete phrase avoids duplicating all she had."),

    c(13,8,"divers places","various places","false-friend-variety-term","Divers means various."),
    c(13,8,"beginnings of sorrows","beginning of birth pains","historical-birth-pains","The phrase uses the image of the beginning of labor pains."),
    c(13,11,"take no thought beforehand","do not worry beforehand","false-friend-worry-phrase","Take no thought means do not worry, not avoid thinking altogether."),
    c(13,11,"Holy Ghost","Holy Spirit","historical-spirit-term","Holy Ghost is modernized to Holy Spirit without changing the referent."),
    c(13,17,"them that are with child","those who are pregnant","archaic-pregnancy-phrase","With child means pregnant."),
    c(13,17,"them that give suck","those who are nursing infants","archaic-nursing-phrase","Give suck means nurse an infant."),
    c(13,22,"to seduce if it were possible even the elect","to deceive, if it were possible, even the elect","false-friend-deception-phrase","Seduce means deceive in this warning about false signs, not its common modern sexual sense."),
    c(13,34,"taking a far journey","going on a long journey","archaic-journey-phrase","The man leaves home for a long journey."),
    c(13,34,"the porter","the doorkeeper","historical-doorkeeper-term","Porter means the doorkeeper assigned to watch."),
    c(13,35,"at even","in the evening","archaic-time-phrase","Even means evening."),
    c(13,35,"at the cockcrowing","when the rooster crows","historical-night-watch","Cockcrowing identifies the night watch associated with the rooster's crow."),

    c(14,1,"take him by craft","arrest him by deception","false-friend-deception-phrase","Craft means deception in the plot to arrest Jesus."),
    c(14,3,"sat at meat","was dining","false-friend-meal-phrase","Sat at meat means was dining."),
    c(14,3,"an alabaster box of ointment of spikenard very precious","an alabaster jar of very costly pure nard perfume","historical-perfume-phrase","The phrase describes a costly perfume of pure nard in an alabaster jar."),
    c(14,3,"she brake the box","she broke the jar","historical-container-phrase","The woman broke the alabaster jar before pouring the perfume."),
    c(14,14,"goodman of the house","owner of the house","archaic-householder-term","Goodman means the owner or head of the household."),
    c(14,14,"guestchamber","guest room","archaic-room-term","Guestchamber means guest room."),
    c(14,33,"sore amazed, and to be very heavy","deeply distressed and troubled","archaic-distress-phrase","The phrase conveys Jesus' intense distress and anguish."),
    c(14,34,"exceeding sorrowful unto death","overwhelmed with sorrow to the point of death","archaic-sorrow-phrase","The phrase retains the extreme depth of Jesus' sorrow."),
    c(14,34,"tarry ye here","remain here","archaic-stay-phrase","Tarry means remain."),
    c(14,43,"with swords and staves","with swords and clubs","historical-weapon-term","Staves means clubs in the arresting crowd."),
    c(14,44,"given them a token","given them a signal","false-friend-signal-term","Token means the prearranged identifying signal."),
    c(14,45,"he goeth straightway to him","he went immediately to him","archaic-speed-clause","Straightway means immediately; the full phrase keeps the narrative action in the past tense."),
    c(14,47,"smote a servant","struck a servant","archaic-strike-verb","Smote means struck."),
    c(14,48,"against a thief","against a bandit","historical-robber-term","The term describes a bandit confronted by an armed group."),
    c(14,48,"with staves","with clubs","historical-weapon-term","Staves means clubs."),
    c(14,54,"into the palace of the high priest","into the courtyard of the high priest","false-friend-courtyard-term","Palace refers here to the high priest's courtyard where Peter warmed himself."),
    c(14,56,"bare false witness","gave false testimony","archaic-testimony-phrase","Bare witness means gave testimony."),
    c(14,56,"their witness agreed not together","their testimony did not agree","archaic-agreement-phrase","The witnesses' statements did not agree with one another."),
    c(14,57,"bare false witness","gave false testimony","archaic-testimony-phrase","Bare witness means gave testimony."),
    c(14,61,"held his peace","remained silent","archaic-silence-phrase","Held his peace means remained silent."),
    c(14,63,"rent his clothes","tore his clothes","archaic-tear-verb","Rent means tore."),
    c(14,66,"beneath in the palace","below in the courtyard","false-friend-courtyard-term","Palace refers to the courtyard where Peter remained below."),
    c(14,70,"thy speech agreeth thereto","thy accent confirms it","archaic-accent-phrase","Peter's accent identifies him as Galilæan while retaining the KJV pronoun system."),

    c(15,1,"straightway in the morning","early in the morning","archaic-time-phrase","Straightway indicates the early, immediate morning action."),
    c(15,16,"they call together the whole band","they called together the whole company of soldiers","historical-military-clause","Band means the company of soldiers, and the complete phrase retains the past narrative tense."),
    c(15,17,"platted a crown of thorns","braided a crown of thorns","archaic-braid-verb","Platted means braided."),
    c(15,17,"put it about his head","put it on his head","archaic-placement-phrase","About his head means the crown was placed on his head."),
    c(15,19,"bowing their knees worshipped him","knelt before him in mockery","context-reviewed-mockery-phrase","The soldiers' gesture is mocking homage, not sincere worship."),
    c(15,19,"smote him on the head","struck him on the head","archaic-strike-verb","Smote means struck."),
    c(15,19,"did spit upon him","spat on him","archaic-spit-phrase","The current verb form preserves the soldiers' act of spitting on Jesus."),
    c(15,21,"one Simon a Cyrenian","a man named Simon from Cyrene","historical-origin-phrase","Cyrenian means a person from Cyrene."),
    c(15,26,"superscription of his accusation","inscription stating the charge against him","historical-inscription-phrase","Superscription means the written charge displayed above Jesus."),
    c(15,27,"two thieves","two bandits","historical-robber-term","The term denotes bandits or violent criminals, not only covert thieves."),
    c(15,29,"railed on him","insulted him","archaic-abuse-verb","Railed on means insulted."),
    c(15,29,"wagging their heads","shaking their heads","archaic-gesture-verb","Wagging means shaking in this mocking gesture."),
    c(15,32,"reviled him","insulted him","archaic-abuse-verb","Reviled means insulted."),
    c(15,37,"gave up the ghost","died","archaic-death-phrase","Gave up the ghost means died in this narrative statement."),
    c(15,38,"veil of the temple was rent in twain","curtain of the temple was torn in two","archaic-temple-phrase","Veil means curtain, rent means torn, and twain means two."),
    c(15,39,"saw that he so cried out, and gave up the ghost","saw how he cried out and died","archaic-death-clause","The centurion observed the manner of Jesus' cry and death; the complete clause avoids a broken mixture of old and current syntax."),
    c(15,43,"an honourable counsellor","a respected member of the council","historical-council-role","Joseph was a respected council member."),
    c(15,43,"which also waited for the kingdom of God","who also waited for the kingdom of God","grammar-person-relative-pronoun","Who is the current relative pronoun for Joseph as a person."),
    c(15,43,"came, and went in boldly unto Pilate, and craved","came and went boldly to Pilate to ask for","archaic-request-clause","The complete clause removes the broken came-and-went construction while preserving Joseph's bold request."),
    c(15,46,"a sepulchre which was hewn out of a rock","a tomb cut out of rock","archaic-tomb-phrase","Sepulchre means tomb and hewn means cut."),
    c(15,46,"door of the sepulchre","entrance of the tomb","archaic-tomb-phrase","The stone closed the entrance of the tomb."),

    c(16,1,"sweet spices","aromatic spices","false-friend-aromatic-term","Sweet spices means fragrant burial spices."),
    c(16,2,"unto the sepulchre","to the tomb","archaic-tomb-term","Sepulchre means tomb."),
    c(16,3,"door of the sepulchre","entrance of the tomb","archaic-tomb-phrase","The stone blocked the tomb's entrance."),
    c(16,5,"entering into the sepulchre","entering the tomb","archaic-tomb-term","Sepulchre means tomb."),
    c(16,5,"were affrighted","were alarmed","archaic-fear-verb","Affrighted means alarmed or frightened."),
    c(16,6,"Be not affrighted","Do not be alarmed","archaic-fear-command","Affrighted means alarmed."),
    c(16,8,"from the sepulchre","from the tomb","archaic-tomb-term","Sepulchre means tomb."),
    c(16,9,"cast seven devils","expelled seven demons","historical-demon-phrase","Devils refers to demons; expelled avoids duplicating out in the surrounding phrase."),
    c(16,13,"told it unto the residue: neither believed they them","told the others, but they did not believe them either","archaic-report-clause","Residue means the remaining disciples; the full clause keeps the report and their disbelief clear."),
    c(16,14,"sat at meat","were dining","false-friend-meal-phrase","Sat at meat means were dining."),
    c(16,14,"upbraided them with their unbelief","rebuked them for their unbelief","archaic-rebuke-phrase","Upbraided means rebuked; for expresses the reason for the rebuke."),
    c(16,14,"because they believed not them which had seen him after he was risen","because they did not believe those who had seen him after he was risen","archaic-belief-clause","The complete clause states clearly that they did not believe the eyewitnesses."),
    c(16,16,"shall be damned","shall be condemned","archaic-condemnation-term","Damned means condemned in this judgment statement."),
    c(16,17,"these signs shall follow them that believe In my name shall they cast out devils they shall speak with new tongues","these signs shall accompany those who believe: In my name they shall cast out demons; they shall speak with new tongues","false-friend-accompany-clause","Follow means the signs accompany believers; the complete sentence also preserves the two listed signs with clear punctuation."),
]


PENDING = {
    "mark-kjv-v12-pronouns": ("thee/thou/thy/ye verb system", "Isolated pronoun changes would create mixed grammar; Mark requires a complete person-and-number policy."),
    "mark-kjv-v12-eternal-damnation": ("eternal damnation", "Mark 3:29 has textual and theological wording differences that a vocabulary pass must not decide."),
    "mark-kjv-v12-isaiah-citation": ("lest at any time they should be converted", "The Isaiah citation in Mark 4:12 has interpretive questions of purpose and result."),
    "mark-kjv-v12-ritual-washings": ("washing of hands, cups and vessels", "The historical washing practices and a textual variant need an explanatory note rather than a quick substitute."),
    "mark-kjv-v12-evil-list": ("evil things from within", "Several Greek terms in Mark 7:21-22 carry distinct moral meanings and require individual review."),
    "mark-kjv-v12-if-thou-canst": ("If thou canst believe", "The received reading and other textual traditions punctuate or formulate Mark 9:23 differently."),
    "mark-kjv-v12-prayer-fasting": ("prayer and fasting", "Fasting belongs to a traditional textual variant and remains untouched."),
    "mark-kjv-v12-hell-fire-salt": ("hell, worm, fire and salt", "The repeated traditional verses and linked images require textual and exegetical review together."),
    "mark-kjv-v12-cup-baptism": ("cup and baptism of suffering", "These metaphors should not be flattened into paraphrase."),
    "mark-kjv-v12-abomination": ("abomination of desolation", "The prophetic phrase depends on Daniel and textual variants and remains unchanged."),
    "mark-kjv-v12-testament": ("new testament / covenant", "Changing testament to covenant requires a Bible-wide terminology decision."),
    "mark-kjv-v12-long-ending": ("long ending of Mark", "Mark 16:9-20 remains fully included. Lexical clarifications do not decide authenticity or add or remove clauses."),
}

PENDING_REFS = {
    "mark-kjv-v12-eternal-damnation": [(3,29)],
    "mark-kjv-v12-isaiah-citation": [(4,12)],
    "mark-kjv-v12-ritual-washings": [(7,3),(7,4),(7,8)],
    "mark-kjv-v12-evil-list": [(7,21),(7,22)],
    "mark-kjv-v12-if-thou-canst": [(9,23)],
    "mark-kjv-v12-prayer-fasting": [(9,29)],
    "mark-kjv-v12-hell-fire-salt": [(9,43),(9,44),(9,45),(9,46),(9,47),(9,48),(9,49)],
    "mark-kjv-v12-cup-baptism": [(10,38),(10,39)],
    "mark-kjv-v12-abomination": [(13,14)],
    "mark-kjv-v12-testament": [(14,24)],
    "mark-kjv-v12-long-ending": [(16,v) for v in range(9,21)],
}


def main():
    source_doc = read(CORPUS / "books/MRK.json")
    source = {(x["chapter"], v["verse"]): v["text"] for x in source_doc["chapters"] for v in x["verses"]}
    direction_path = DIRECTION / "books/mrk_reading_2026.kjv.v1.json"
    direction = read(direction_path)
    patches = {(v["chapter"], v["verse"]): v for v in direction.get("verses", [])}
    # Consolidate the earlier spelling-only repair into the complete reviewed
    # miracle phrase so the rendered sentence cannot retain archaic scaffolding.
    for ref, obsolete in [((6, 14), "shew"), ((7, 35), "spake")]:
        if ref in patches:
            patches[ref]["edits"] = [e for e in patches[ref]["edits"] if e["expected"] != obsolete]
    applied = []
    for chapter, verse, expected, replacement, category, reason in CHANGES:
        text = source[(chapter, verse)]
        if expected not in text:
            raise RuntimeError(f"missing at MRK.{chapter}.{verse}: {expected!r}")
        patch = patches.get((chapter, verse))
        if patch is None:
            patch = {"chapter": chapter, "verse": verse, "sourceTextSha256": sha(text.encode()), "edits": []}
            direction["verses"].append(patch)
            patches[(chapter, verse)] = patch
        cursor = 0
        while True:
            start = text.find(expected, cursor)
            if start < 0:
                break
            end = start + len(expected)
            cursor = end
            exact = next((e for e in patch["edits"] if e["startOffset"] == start and e["endOffset"] == end), None)
            if exact:
                if exact["replacement"] == replacement:
                    continue
                raise RuntimeError(f"replacement collision at MRK.{chapter}.{verse}: {exact}")
            overlaps = [e for e in patch["edits"] if e["startOffset"] < end and start < e["endOffset"]]
            if overlaps:
                raise RuntimeError(f"overlap at MRK.{chapter}.{verse} for {expected!r}: {overlaps}")
            edit = {"startOffset": start, "endOffset": end, "expected": expected, "replacement": replacement,
                    "category": category, "reason": reason,
                    "evidence": [{"label": "Complete-verse KJV, NKJV, NIV, ESV and NRSVUE control",
                                  "url": f"https://www.biblegateway.com/passage/?search=Mark+{chapter}%3A{verse}&version=KJV%3BNKJV%3BNIV%3BESV%3BNRSVUE"}]}
            patch["edits"].append(edit)
            applied.append((chapter, verse, expected, replacement, category, reason))

    for patch in direction["verses"]:
        text = source[(patch["chapter"], patch["verse"])]
        patch["sourceTextSha256"] = sha(text.encode())
        patch["edits"].sort(key=lambda e: e["startOffset"])
        prior_end = -1
        for edit in patch["edits"]:
            if edit["startOffset"] < prior_end or text[edit["startOffset"]:edit["endOffset"]] != edit["expected"]:
                raise RuntimeError(f"invalid edit at MRK.{patch['chapter']}.{patch['verse']}: {edit}")
            prior_end = edit["endOffset"]
    direction["verses"].sort(key=lambda v: (v["chapter"], v["verse"]))
    direction["editorialStatus"] = "approved-mark-complete-context-review-v12"
    direction["ownerReview"] = {"contentVersion": VERSION, "review": "KJV Mark complete contextual review", "requiredFullTest": True}
    write(direction_path, direction, compact=True)

    source_path = DIRECTION / "reading_2026.package-source.json"
    package_source = read(source_path)
    package_source["contentVersion"] = VERSION
    package_source["generatedAt"] = "2026-09-12T20:30:00.000Z"
    package_source["editorialPolicy"]["version"] = VERSION
    write(source_path, package_source)

    books = {read(p)["book"]: read(p) for p in (CORPUS / "books").glob("*.json")}
    order = {book: doc["order"] for book, doc in books.items()}
    direction_paths = {read(p)["book"]: p for p in (DIRECTION / "books").glob("*.json")}
    direction_books = [read(p) for p in direction_paths.values()]
    direction_books.sort(key=lambda x: order[x["book"]])
    payload = {"books": direction_books, "contentVersion": VERSION, "editorialPolicy": package_source["editorialPolicy"],
               "filterId": package_source["filterId"], "format": "shine-reading-filter-package",
               "normalizationId": package_source["normalizationId"], "schemaVersion": 1,
               "sourceCorpusSha256": package_source["sourceCorpusSha256"], "sourceVersionId": package_source["sourceVersionId"]}
    raw = canonical(payload).encode()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    packages = DIRECTION / "packages"
    package_path = packages / "reading_2026.kjv.v1.package.json.gz"
    package_path.write_bytes(compressed)
    coverage = {"expectedBookCount": 66, "includedBookCount": len(direction_books),
                "changedVerseCount": sum(len(b["verses"]) for b in direction_books),
                "editCount": sum(len(v["edits"]) for b in direction_books for v in b["verses"])}
    manifest = {"format": "shine-reading-filter-manifest", "filterId": package_source["filterId"], "schemaVersion": 1,
                "contentVersion": VERSION, "sourceVersionId": package_source["sourceVersionId"],
                "sourceCorpusSha256": package_source["sourceCorpusSha256"], "normalizationId": package_source["normalizationId"],
                "contentSha256": sha(compressed), "sizeBytes": len(compressed), "expandedSizeBytes": len(raw),
                "mimeType": "application/vnd.shine.reading-filter+gzip", "generatedAt": "2026-09-12",
                "editorialPolicy": package_source["editorialPolicy"], "coverage": coverage,
                "books": [{"id": b["book"], "order": order[b["book"]], "sourceFile": direction_paths[b["book"]].name,
                           "sourceContentSha256": b["sourceContentSha256"], "payloadSha256": sha(canonical(b).encode()),
                           "changedVerseCount": len(b["verses"]), "editCount": sum(len(v["edits"]) for v in b["verses"])}
                          for b in direction_books]}
    write(packages / "reading_2026.kjv.v1.manifest.json", manifest)

    registry = read(REGISTRY)
    registry["updatedAt"] = "2026-09-12T20:30:00.000Z"
    registry["activeContentVersion"] = VERSION
    registry["applied"] = [x for x in registry["applied"] if not (
        (x.get("reference") == "MRK.6.14" and x.get("expected") == "shew")
        or (x.get("reference") == "MRK.7.35" and x.get("expected") == "spake")
    )]
    known = {(x["reference"], x["expected"], x["replacement"]) for x in registry["applied"]}
    for chapter, verse, expected, replacement, category, reason in applied:
        key = (f"MRK.{chapter}.{verse}", expected, replacement)
        if key not in known:
            registry["applied"].append({"reference": key[0], "expected": expected, "replacement": replacement,
                                        "category": category, "reason": reason,
                                        "evidenceUrl": f"https://www.biblegateway.com/passage/?search=Mark+{chapter}%3A{verse}&version=KJV%3BNKJV%3BNIV%3BESV%3BNRSVUE"})
            known.add(key)
    registry["pending"] = [x for x in registry.get("pending", []) if not x.get("id", "").startswith("mark-kjv-v12-")]
    pronoun_refs = []
    pronouns = {"thee", "thou", "thy", "thine", "ye", "hath", "doth", "shalt", "wilt"}
    for chapter in source_doc["chapters"]:
        for verse in chapter["verses"]:
            words = {word.strip(".,:;!?()[]\"'¶").lower() for word in verse["text"].split()}
            if words.intersection(pronouns):
                pronoun_refs.append((chapter["chapter"], verse["verse"]))
    for pending_id, (term, reason) in PENDING.items():
        refs = pronoun_refs if pending_id.endswith("pronouns") else PENDING_REFS[pending_id]
        registry["pending"].append({"id": pending_id, "status": "pending-review", "scope": "new-testament", "term": term,
                                    "proposedOptions": ["Retain with an explanatory note", "Modernize after focused clause review"],
                                    "reason": reason, "references": [{"book": BOOK, "chapter": c, "verse": v} for c, v in refs],
                                    "evidence": [{"label": "Mark multi-version contextual control",
                                                  "url": "https://www.biblegateway.com/passage/?search=Mark&version=KJV%3BNKJV%3BNIV%3BESV%3BNRSVUE"}]})
    write(REGISTRY, registry)
    print(json.dumps({"addedEdits": len(applied), "markChangedVerses": len(direction["verses"]),
                      "markEdits": sum(len(v["edits"]) for v in direction["verses"]),
                      "pendingFamilies": len(PENDING), "package": coverage, "contentSha256": manifest["contentSha256"]}, indent=2))


if __name__ == "__main__":
    main()
