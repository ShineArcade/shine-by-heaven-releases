import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/kjv"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv"
REGISTRY = ROOT / "editorial-review/registry.kjv.json"
BOOK = "MAT"
VERSION = 10


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, compact=False):
    separators = (",", ":") if compact else None
    path.write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2, separators=separators) + "\n", encoding="utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def c(chapter, verse, expected, replacement, category, reason):
    return (chapter, verse, expected, replacement, category, reason)


# Each clause below was read in its complete Matthew verse and compared with the
# local NIV control. Rules are deliberately reference-bound: the same English
# token can carry another meaning elsewhere.
CHANGES = [
    c(1,2,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,3,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,4,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,5,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,6,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,6,"of her that had been the wife of Urias","by her who had been the wife of Urias","archaic-parentage-phrase","The genealogy identifies Solomon's mother through her former marriage to Uriah; by expresses parentage clearly."),
    c(1,7,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,8,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,9,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,10,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,11,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,12,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,13,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,14,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,15,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,16,"begat","fathered","archaic-genealogy-verb","Begat means fathered in Matthew's genealogy."),
    c(1,18,"on this wise","in this way","archaic-narrative-phrase","On this wise means in this way."),
    c(1,18,"When as his mother","When his mother","archaic-conjunction-phrase","When as is an obsolete conjunction; modern English uses when."),
    c(1,18,"espoused to Joseph","pledged to marry Joseph","historical-betrothal-phrase","Espoused describes Mary's binding betrothal to Joseph before they lived together."),
    c(1,18,"found with child of the Holy Ghost","found to be pregnant through the Holy Spirit","archaic-pregnancy-phrase","The phrase describes Mary's pregnancy through the Holy Spirit; the complete span avoids the ungrammatical wording produced by separate substitutions."),
    c(1,19,"put her away","divorce her","archaic-divorce-phrase","Put her away means divorce her in this legal-marital context."),
    c(1,19,"publick","public","historical-spelling","The historical spelling is modernized without changing the meaning."),
    c(1,20,"Holy Ghost","Holy Spirit","historical-spirit-term","Holy Ghost is modernized to Holy Spirit without changing the referent."),
    c(1,21,"bring forth a son","give birth to a son","archaic-birth-phrase","Bring forth means give birth in this announcement."),
    c(1,23,"bring forth a son","give birth to a son","archaic-birth-phrase","Bring forth means give birth in this prophecy."),
    c(1,24,"bidden him","commanded him","archaic-command-verb","Bidden means commanded in the angel's instruction."),
    c(1,25,"brought forth her firstborn son","given birth to her firstborn son","archaic-birth-phrase","Brought forth means given birth in this narrative."),
    c(2,7,"enquired of them diligently","carefully learned from them","archaic-inquiry-phrase","Herod carefully determined the star's appearing time from the visitors."),
    c(2,16,"exceeding wroth","furious","archaic-anger-phrase","Exceeding wroth means furious."),
    c(2,16,"slew all the children","killed all the children","archaic-kill-verb","Slew means killed."),
    c(2,16,"coasts thereof","surrounding region","false-friend-region","Coasts means the surrounding region, not a seacoast."),
    c(3,4,"raiment","clothing","archaic-clothing-term","Raiment means clothing."),
    c(3,4,"about his loins","around his waist","archaic-body-term","Loins identifies the waist in this clothing description."),
    c(3,4,"meat was locusts","food was locusts","false-friend-food-term","Meat means food generally here."),
    c(3,8,"fruits meet for repentance","fruit consistent with repentance","archaic-repentance-phrase","Meet means appropriate or consistent with repentance."),
    c(3,15,"Suffer it to be so now","Allow it to be so now","archaic-permission-verb","Suffer means allow in Jesus' reply."),
    c(3,15,"Then he suffered him","Then he allowed him","archaic-permission-verb","Suffered means allowed in the narrative response."),
    c(3,11,"Holy Ghost","Holy Spirit","historical-spirit-term","Holy Ghost is modernized to Holy Spirit without changing the referent."),
    c(3,16,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(4,8,"sheweth him","shows him","historical-spelling","Sheweth means shows."),
    c(4,20,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(4,21,"in a ship","in a boat","historical-vessel-term","Ship denotes the fishing boat used on the Sea of Galilee."),
    c(4,24,"divers diseases","various diseases","false-friend-variety-term","Divers means various."),
    c(4,24,"possessed with devils","demon-possessed","historical-demon-phrase","Devils refers to demons in this healing list."),
    c(4,24,"lunatick","having seizures","obsolete-medical-term","Lunatick is an obsolete diagnosis; the immediate list describes a seizure condition."),
    c(4,24,"had the palsy","were paralyzed","obsolete-medical-term","Palsy denotes paralysis here."),
    c(5,13,"lost his savour","lost its flavor","false-friend-taste-term","Savour means flavor in the salt image."),
    c(5,15,"under a bushel","under a basket","historical-container-term","Bushel denotes the measuring container covering the lamp."),
    c(5,15,"on a candlestick","on a lampstand","false-friend-lamp-term","Candlestick denotes a lampstand for an oil lamp."),
    c(5,26,"uttermost farthing","last small coin","historical-coin-term","The phrase means the final coin owed, not a modern currency amount."),
    c(5,29,"eye offend thee","eye causes thee to sin","false-friend-stumble-verb","Offend means cause to stumble into sin here."),
    c(5,30,"hand offend thee","hand causes thee to sin","false-friend-stumble-verb","Offend means cause to stumble into sin here."),
    c(5,31,"put away his wife","divorce his wife","archaic-divorce-phrase","Put away means divorce in this legal-marital context."),
    c(5,31,"writing of divorcement","certificate of divorce","archaic-legal-phrase","The phrase names the written divorce certificate."),
    c(5,32,"put away his wife","divorce his wife","archaic-divorce-phrase","Put away means divorce in this legal-marital context."),
    c(5,41,"go with him twain","go with him two","archaic-number-term","Twain means two."),
    c(5,46,"publicans","tax collectors","historical-tax-term","Publicans were tax collectors."),
    c(5,47,"publicans","tax collectors","historical-tax-term","Publicans were tax collectors."),
    c(6,5,"corners of the streets","street corners","grammar-word-order","The modern order preserves the public location."),
    c(6,6,"enter into thy closet","enter thy private room","false-friend-private-room","Closet means a private room for prayer."),
    c(6,7,"vain repetitions","meaningless repetitions","archaic-prayer-phrase","Vain describes empty or meaningless repetition."),
    c(6,24,"mammon","wealth","historical-wealth-term","Mammon personifies money or wealth in the contrast with serving God."),
    c(6,25,"Take no thought for your life","Do not worry about your life","false-friend-worry-phrase","Take no thought means do not worry, not do not plan or think."),
    c(6,25,"life more than meat","life more than food","false-friend-food-term","Meat means food generally here."),
    c(6,25,"body than raiment","body than clothing","archaic-clothing-term","Raiment means clothing."),
    c(6,26,"fowls of the air","birds of the air","archaic-bird-term","Fowls means birds."),
    c(6,28,"take ye thought for raiment","worry about clothing","archaic-worry-phrase","Take thought means worry, and raiment means clothing."),
    c(6,34,"Take therefore no thought for the morrow","Therefore do not worry about tomorrow","archaic-worry-phrase","The morrow means tomorrow and take no thought means do not worry."),
    c(7,3,"mote that is in thy brother","speck that is in thy brother","false-friend-small-object","Mote means a tiny speck in the eye."),
    c(7,5,"mote out of thy brother","speck out of thy brother","false-friend-small-object","Mote means a tiny speck in the eye."),
    c(7,6,"pearls before swine","pearls before pigs","historical-animal-term","Swine means pigs."),
    c(7,13,"strait gate","narrow gate","false-friend-width-term","Strait means narrow in this gate image."),
    c(7,14,"strait is the gate","narrow is the gate","false-friend-width-term","Strait means narrow in this gate image."),
    c(7,15,"ravening wolves","ferocious wolves","archaic-violence-term","Ravening describes violently predatory wolves."),
    c(7,22,"cast out devils","cast out demons","historical-demon-term","Devils refers to demons in this exorcism."),
    c(8,6,"sick of the palsy","paralyzed","obsolete-medical-term","Palsy denotes paralysis here."),
    c(8,21,"suffer me first","allow me first","archaic-permission-verb","Suffer means allow in the disciple's request."),
    c(8,23,"entered into a ship","entered a boat","historical-vessel-term","Ship denotes the boat used on the lake."),
    c(8,24,"great tempest","great storm","archaic-storm-term","Tempest means storm."),
    c(8,24,"the ship was covered","the boat was covered","historical-vessel-term","Ship denotes the boat used on the lake."),
    c(8,28,"possessed with devils","demon-possessed","historical-demon-phrase","Devils refers to demons here."),
    c(8,31,"devils besought him","demons begged him","archaic-demon-phrase","Devils refers to demons and besought means begged."),
    c(8,31,"herd of swine","herd of pigs","historical-animal-term","Swine means pigs."),
    c(8,32,"herd of swine","herd of pigs","historical-animal-term","Swine means pigs."),
    c(8,34,"depart out of their coasts","leave their region","false-friend-region","Coasts means their region, not a seacoast."),
    c(8,16,"When the even was come","When evening came","archaic-time-phrase","Even means evening in this time marker."),
    c(8,16,"possessed with devils","demon-possessed","historical-demon-phrase","Devils refers to demons here."),
    c(8,33,"possessed of the devils","demon-possessed men","historical-demon-phrase","The phrase identifies the men formerly possessed by demons."),
    c(8,34,"besought him","begged him","archaic-request-verb","Besought means begged."),
    c(9,2,"sick of the palsy","paralyzed","obsolete-medical-term","Palsy denotes paralysis here."),
    c(9,6,"sick of the palsy","paralyzed","obsolete-medical-term","Palsy denotes paralysis here."),
    c(9,9,"receipt of custom","tax collection booth","historical-tax-phrase","The phrase names Matthew's tax collection booth."),
    c(9,10,"sat at meat","was dining","false-friend-meal-phrase","Sat at meat means was eating a meal."),
    c(9,10,"publicans","tax collectors","historical-tax-term","Publicans were tax collectors."),
    c(9,11,"publicans","tax collectors","historical-tax-term","Publicans were tax collectors."),
    c(9,16,"the rent is made worse","the tear is made worse","false-friend-tear-term","Rent means a tear in the garment."),
    c(9,17,"old bottles","old wineskins","false-friend-container-term","Bottles here were skin containers for wine."),
    c(9,17,"new bottles","new wineskins","false-friend-container-term","Bottles here were skin containers for wine."),
    c(9,20,"issue of blood","chronic bleeding","historical-medical-phrase","Issue of blood describes the woman's long-term bleeding."),
    c(9,23,"minstrels","flute players","historical-funeral-musician","The minstrels are the musicians playing pipes at the mourning scene."),
    c(9,30,"straitly charged them","sternly warned them","archaic-warning-phrase","Straitly charged means sternly warned."),
    c(9,32,"dumb man","mute man","historical-disability-term","Dumb means unable to speak in this account."),
    c(9,32,"possessed with a devil","possessed by a demon","historical-demon-phrase","Devil refers to a demon in this possession account."),
    c(9,33,"the devil was cast out","the demon was cast out","historical-demon-term","Devil refers to a demon in this possession account."),
    c(9,33,"the dumb","the mute man","historical-disability-term","Dumb means unable to speak in this account."),
    c(9,34,"casteth out devils","casts out demons","historical-demon-term","Devils refers to demons."),
    c(9,34,"prince of the devils","prince of the demons","historical-demon-term","Devils refers to demons."),
    c(9,37,"labourers","workers","archaic-worker-term","Labourers means workers in the harvest image."),
    c(9,38,"labourers","workers","archaic-worker-term","Labourers means workers in the harvest image."),
    c(10,8,"cast out devils","cast out demons","historical-demon-term","Devils refers to demons."),
    c(10,10,"scrip for your journey","bag for your journey","archaic-travel-bag","Scrip means a travel bag."),
    c(10,10,"nor yet staves","nor a staff","archaic-travel-staff","Staves is the historical plural of staff; the instruction concerns carrying a staff."),
    c(10,10,"workman is worthy of his meat","worker is worthy of his food","archaic-work-and-food-phrase","Workman means worker and meat means food generally."),
    c(10,29,"sold for a farthing","sold for a small coin","historical-coin-term","Farthing names a very small ancient coin in the comparison."),
    c(10,35,"set a man at variance against his father","set a man against his father","archaic-conflict-phrase","At variance means in conflict or opposition."),
    c(11,6,"offended in me","caused to stumble because of me","false-friend-stumble-phrase","Offended means caused to stumble or fall away because of Jesus."),
    c(11,18,"He hath a devil","He has a demon","historical-demon-phrase","The accusation claims demonic possession; devil refers to a demon here."),
    c(11,8,"soft raiment","fine clothing","archaic-clothing-phrase","Soft raiment means fine clothing."),
    c(11,17,"piped unto you","played the pipe for you","archaic-music-verb","Piped means played a pipe."),
    c(11,17,"mourned unto you","sang a dirge for you","archaic-mourning-phrase","The parallel line describes singing a funeral lament."),
    c(11,19,"winebibber","drunkard","archaic-person-term","Winebibber means drunkard."),
    c(11,19,"publicans","tax collectors","historical-tax-term","Publicans were tax collectors."),
    c(11,20,"upbraid the cities","denounce the cities","archaic-rebuke-verb","Upbraid means strongly rebuke or denounce."),
    c(11,20,"mighty works","miracles","archaic-miracle-phrase","Mighty works refers to Jesus' miracles in these towns."),
    c(11,21,"mighty works","miracles","archaic-miracle-phrase","Mighty works refers to Jesus' miracles."),
    c(11,21,"sackcloth and ashes","mourning clothes and ashes","historical-mourning-term","Sackcloth was rough clothing used as a sign of mourning and repentance."),
    c(11,23,"mighty works","miracles","archaic-miracle-phrase","Mighty works refers to Jesus' miracles."),
    c(11,28,"labour and are heavy laden","are weary and burdened","archaic-burden-phrase","The invitation addresses people who are weary and burdened."),
    c(12,10,"hand withered","disabled hand","historical-disability-phrase","Withered describes the man's disabled hand."),
    c(12,16,"charged them","warned them","archaic-warning-verb","Charged means warned or ordered here."),
    c(12,22,"possessed with a devil","possessed by a demon","historical-demon-phrase","Devil refers to a demon in this healing account."),
    c(12,22,"blind, and dumb","blind and mute","historical-disability-term","Dumb means unable to speak in this healing account."),
    c(12,22,"the blind and dumb","the blind and mute man","historical-disability-phrase","The two disabilities belong to the same man; the modern phrase preserves both healings."),
    c(12,24,"cast out devils","cast out demons","historical-demon-term","Devils refers to demons."),
    c(12,24,"prince of the devils","prince of the demons","historical-demon-term","Devils refers to demons."),
    c(12,27,"cast out devils","cast out demons","historical-demon-term","Devils refers to demons."),
    c(12,28,"cast out devils","cast out demons","historical-demon-term","Devils refers to demons."),
    c(12,31,"Holy Ghost","Holy Spirit","historical-spirit-term","Holy Ghost is modernized to Holy Spirit without changing the referent."),
    c(12,32,"Holy Ghost","Holy Spirit","historical-spirit-term","Holy Ghost is modernized to Holy Spirit without changing the referent."),
    c(12,20,"smoking flax","smoldering wick","false-friend-lamp-image","Smoking flax denotes a dimly burning lamp wick."),
    c(12,29,"spoil his goods","carry off his possessions","false-friend-plunder-phrase","Spoil means plunder or carry off possessions."),
    c(12,29,"spoil his house","plunder his house","false-friend-plunder-phrase","Spoil means plunder."),
    c(12,36,"idle word","careless word","false-friend-speech-term","Idle means careless or empty in this warning about speech."),
    c(12,40,"whale\u2019s belly","great fish's belly","historical-animal-term","Matthew's comparison refers to Jonah's great fish; whale is overly specific in current usage."),
    c(12,42,"uttermost parts","farthest parts","archaic-location-term","Uttermost means farthest."),
    c(13,2,"went into a ship","went into a boat","historical-vessel-term","Ship denotes a boat on the lake."),
    c(13,4,"fowls came","birds came","archaic-bird-term","Fowls means birds."),
    c(13,21,"by and by he is offended","he immediately falls away","archaic-stumble-phrase","By and by means immediately here, and offended means falls away under persecution."),
    c(13,25,"tares among the wheat","weeds among the wheat","historical-weed-term","Tares are weeds resembling wheat."),
    c(13,26,"the tares also","the weeds also","historical-weed-term","Tares are weeds resembling wheat."),
    c(13,27,"servants of the householder","landowner's servants","archaic-landowner-term","Householder means the owner of the field."),
    c(13,27,"hath it tares","has it weeds","historical-weed-term","Tares are weeds resembling wheat."),
    c(13,29,"gather up the tares","gather up the weeds","historical-weed-term","Tares are weeds resembling wheat."),
    c(13,30,"first the tares","first the weeds","historical-weed-term","Tares are weeds resembling wheat."),
    c(13,33,"leaven","yeast","historical-baking-term","Leaven means yeast in this baking image."),
    c(13,33,"three measures of meal","three measures of flour","false-friend-flour-term","Meal means flour in this baking image."),
    c(13,36,"tares of the field","weeds of the field","historical-weed-term","Tares are weeds resembling wheat."),
    c(13,38,"the tares are","the weeds are","historical-weed-term","Tares are weeds in Jesus' explanation of the parable."),
    c(13,40,"the tares are gathered","the weeds are gathered","historical-weed-term","Tares are weeds resembling wheat."),
    c(13,41,"all things that offend","everything that causes sin","false-friend-stumble-phrase","Offend means cause sin or stumbling in this judgment statement."),
    c(13,49,"sever the wicked","separate the wicked","archaic-separate-verb","Sever means separate here."),
    c(13,52,"man that is an householder","head of a household","archaic-householder-term","Householder means the person responsible for a household and its stored treasure."),
    c(13,54,"mighty works","miracles","archaic-miracle-phrase","Mighty works refers to Jesus' miracles."),
    c(13,58,"mighty works","miracles","archaic-miracle-phrase","Mighty works refers to Jesus' miracles."),
    c(14,9,"sat with him at meat","dined with him","archaic-meal-phrase","Sitting at meat means dining."),
    c(14,2,"mighty works","miracles","archaic-miracle-phrase","Mighty works refers to miracles in Herod's explanation."),
    c(14,15,"buy themselves victuals","buy themselves food","archaic-food-term","Victuals means food or provisions."),
    c(14,22,"straightway Jesus constrained his disciples","immediately Jesus made his disciples","archaic-command-phrase","Straightway means immediately and constrained means made or compelled in this instruction."),
    c(14,22,"get into a ship","get into a boat","historical-vessel-term","Ship denotes a boat on the lake."),
    c(14,24,"the ship","the boat","historical-vessel-term","Ship denotes a boat on the lake."),
    c(14,25,"fourth watch of the night","hours before dawn","historical-night-watch","The fourth Roman watch was the final period before dawn."),
    c(14,27,"straightway","immediately","archaic-speed-adverb","Straightway means immediately."),
    c(14,30,"wind boisterous","strong wind","archaic-wind-term","Boisterous describes the wind as strong or violent."),
    c(14,36,"besought him","begged him","archaic-request-verb","Besought means begged."),
    c(15,2,"transgress the tradition","break the tradition","archaic-break-verb","Transgress means break or violate."),
    c(15,3,"transgress the commandment","break the commandment","archaic-break-verb","Transgress means break or violate."),
    c(15,17,"cast out into the draught","eliminated from the body","false-friend-bodily-phrase","Draught refers to bodily waste disposal, not a drink or air current."),
    c(15,21,"coasts of Tyre and Sidon","region of Tyre and Sidon","false-friend-region","Coasts means region or vicinity."),
    c(15,22,"same coasts","same region","false-friend-region","Coasts means region or vicinity."),
    c(15,22,"grievously vexed with a devil","terribly tormented by a demon","archaic-demon-phrase","The daughter is suffering terribly under demonic oppression."),
    c(15,23,"besought him","begged him","archaic-request-verb","Besought means begged."),
    c(15,29,"came nigh unto","came near","archaic-location-phrase","Nigh means near."),
    c(15,30,"dumb, maimed","mute, disabled","historical-disability-terms","Dumb means unable to speak and maimed describes disability here."),
    c(15,31,"the dumb to speak","those who could not speak begin to speak","historical-disability-phrase","Dumb means unable to speak; the complete phrase is made grammatical in current English."),
    c(15,37,"broken meat","broken pieces","false-friend-leftovers-term","Meat here denotes pieces of bread or food left over."),
    c(15,39,"coasts of Magdala","region of Magdala","false-friend-region","Coasts means region or vicinity."),
    c(16,1,"tempting desired him","testing him, asked him","false-friend-test-verb","Tempting means testing Jesus with a demand for a sign."),
    c(16,13,"coasts of Caesarea Philippi","region of Caesarea Philippi","false-friend-region","Coasts means region or vicinity."),
    c(16,20,"charged he his disciples","warned his disciples","archaic-warning-verb","Charged means warned or instructed here."),
    c(16,23,"an offence unto me","a stumbling block to me","false-friend-stumble-term","Offence means a stumbling block here."),
    c(16,23,"savourest not the things","do not have in mind the things","archaic-thought-phrase","Savourest means set the mind on or have in mind, not taste."),
    c(17,2,"raiment was white","clothing was white","archaic-clothing-term","Raiment means clothing."),
    c(17,4,"three tabernacles","three shelters","historical-shelter-term","Tabernacles means temporary shelters in Peter's proposal."),
    c(17,6,"sore afraid","very afraid","archaic-intensity-adverb","Sore means very in this fear phrase."),
    c(17,9,"charged them","instructed them","archaic-command-verb","Charged means instructed or commanded here."),
    c(17,12,"whatsoever they listed","whatever they wanted","archaic-desire-verb","Listed means wished or wanted."),
    c(17,18,"rebuked the devil","rebuked the demon","historical-demon-term","Devil refers to the demon afflicting the child."),
    c(17,15,"lunatick, and sore vexed","having seizures and suffering terribly","obsolete-medical-phrase","Lunatick is obsolete; the verse itself describes recurring seizures and severe suffering."),
    c(17,17,"shall I suffer you","shall I bear with you","false-friend-endure-verb","Suffer means endure or bear with in this lament."),
    c(17,24,"received tribute money","collected the temple tax","historical-tax-term","Tribute money here is the temple tax."),
    c(18,6,"offend one of these little ones","cause one of these little ones to stumble","false-friend-stumble-verb","Offend means cause to stumble spiritually."),
    c(18,7,"because of offences","because of stumbling blocks","false-friend-stumble-term","Offences means causes of spiritual stumbling."),
    c(18,7,"offences come","stumbling blocks come","false-friend-stumble-term","Offences means causes of spiritual stumbling."),
    c(18,7,"offence cometh","stumbling block comes","false-friend-stumble-term","Offence means a cause of spiritual stumbling."),
    c(18,8,"foot offend thee","foot causes thee to sin","false-friend-stumble-verb","Offend means cause to sin here."),
    c(18,9,"eye offend thee","eye causes thee to sin","false-friend-stumble-verb","Offend means cause to sin here."),
    c(18,15,"brother shall trespass against thee","brother sins against thee","archaic-sin-verb","Trespass means sin or do wrong in this church-discipline instruction."),
    c(18,17,"as an heathen man and a publican","as a Gentile and a tax collector","historical-community-terms","Heathen and publican identify a Gentile and a tax collector in this social comparison."),
    c(18,28,"an hundred pence","a hundred silver coins","historical-coin-term","Pence refers to ancient silver denarii, not modern pennies."),
    c(18,29,"fellowservant","fellow servant","historical-compound-spacing","The historical compound is separated for modern readability."),
    c(18,29,"besought him","begged him","archaic-request-verb","Besought means begged."),
    c(18,33,"fellowservant","fellow servant","historical-compound-spacing","The historical compound is separated for modern readability."),
    c(19,1,"coasts of Judaea","region of Judea","false-friend-region","Coasts means region, and the place name uses modern English spelling."),
    c(19,3,"tempting him","testing him","false-friend-test-verb","Tempting means testing Jesus with a disputed legal question."),
    c(19,3,"put away his wife","divorce his wife","archaic-divorce-phrase","Put away means divorce."),
    c(19,5,"they twain","the two","archaic-number-term","Twain means two."),
    c(19,6,"no more twain","no longer two","archaic-number-phrase","Twain means two."),
    c(19,6,"put asunder","separate","archaic-separate-phrase","Put asunder means separate."),
    c(19,7,"put her away","divorce her","archaic-divorce-phrase","Put away means divorce."),
    c(19,8,"suffered you to put away your wives","allowed you to divorce your wives","archaic-divorce-phrase","Suffered means allowed and put away means divorce."),
    c(19,9,"put away his wife","divorce his wife","archaic-divorce-phrase","Put away means divorce."),
    c(19,9,"which is put away","who is divorced","archaic-divorce-phrase","Put away means divorced."),
    c(20,1,"man that is an householder","landowner","archaic-landowner-term","Householder means the owner of the vineyard."),
    c(20,1,"hire labourers","hire workers","archaic-worker-term","Labourers means workers."),
    c(20,2,"labourers for a penny a day","workers for a denarius a day","historical-wage-term","The wage was one denarius for the day, not a modern penny."),
    c(20,6,"standing idle","standing without work","false-friend-work-status","Idle means without work in the hiring scene."),
    c(20,8,"even was come","evening came","archaic-time-phrase","Even means evening here."),
    c(20,8,"unto his steward","to his foreman","historical-manager-term","The steward manages the vineyard labor and wages."),
    c(20,8,"Call the labourers and give them their hire","Call the workers and give them their wages","archaic-wage-phrase","Labourers means workers and hire means wages in this payment instruction."),
    c(20,11,"murmured against the goodman of the house","grumbled against the landowner","archaic-complaint-phrase","The goodman of the house is the landowner, and murmured means grumbled."),
    c(20,13,"for a penny","for a denarius","historical-wage-term","Penny denotes the agreed denarius wage."),
    c(20,19,"to mock and to scourge","to ridicule and to whip","historical-abuse-terms","Scourge means whip in the passion prediction."),
    c(20,26,"let him be your minister","let him be your servant","false-friend-service-term","Minister means servant in Jesus' teaching about greatness."),
    c(20,28,"not to be ministered unto but to minister","not to be served but to serve","false-friend-service-phrase","Minister denotes serving others in both clauses."),
    c(21,1,"drew nigh unto Jerusalem","came near Jerusalem","archaic-location-phrase","Nigh means near."),
    c(21,2,"straightway ye shall find an ass","immediately ye shall find a donkey","historical-animal-term","Straightway means immediately and ass means donkey."),
    c(21,5,"sitting upon an ass","sitting upon a donkey","historical-animal-term","Ass means donkey."),
    c(21,7,"brought the ass","brought the donkey","historical-animal-term","Ass means donkey."),
    c(21,12,"overthrew the tables of the moneychangers","overturned the tables of the money changers","archaic-overturn-phrase","Overthrew means physically overturned; money changers is spaced normally."),
    c(21,13,"den of thieves","den of robbers","historical-robber-term","The cited phrase concerns robbers using a den."),
    c(21,17,"lodged there","stayed there overnight","archaic-lodging-verb","Lodged means stayed overnight."),
    c(21,31,"publicans and the harlots","tax collectors and the prostitutes","historical-person-terms","Publicans were tax collectors and harlots were prostitutes."),
    c(21,32,"publicans and the harlots","tax collectors and the prostitutes","historical-person-terms","Publicans were tax collectors and harlots were prostitutes."),
    c(21,33,"certain householder","certain landowner","archaic-landowner-term","Householder means the landowner in the parable."),
    c(21,33,"let it out to husbandmen","rented it to tenant farmers","archaic-tenant-phrase","Husbandmen are the tenant farmers managing the vineyard."),
    c(21,34,"to the husbandmen","to the tenant farmers","archaic-tenant-term","Husbandmen are the tenant farmers."),
    c(21,35,"the husbandmen","the tenant farmers","archaic-tenant-term","Husbandmen are the tenant farmers."),
    c(21,38,"the husbandmen","the tenant farmers","archaic-tenant-term","Husbandmen are the tenant farmers."),
    c(21,40,"those husbandmen","those tenant farmers","archaic-tenant-term","Husbandmen are the tenant farmers."),
    c(21,41,"other husbandmen","other tenant farmers","archaic-tenant-term","Husbandmen are the tenant farmers."),
    c(21,41,"render him the fruits","give him the fruit","archaic-give-verb","Render means give in the tenant payment."),
    c(22,3,"bidden to the wedding","invited to the wedding","archaic-invitation-term","Bidden means invited."),
    c(22,4,"which are bidden","who are invited","archaic-invitation-term","Bidden means invited."),
    c(22,4,"fatlings","fattened cattle","historical-banquet-animal","Fatlings are animals fattened for the banquet."),
    c(22,6,"entreated them spitefully","mistreated them","archaic-abuse-phrase","Entreated spitefully means treated abusively."),
    c(22,8,"which were bidden","who were invited","archaic-invitation-term","Bidden means invited."),
    c(22,20,"superscription","inscription","archaic-coin-term","Superscription means the inscription on the coin."),
    c(22,35,"a lawyer","an expert in the law","historical-law-expert","Lawyer here means an expert in the religious law."),
    c(22,46,"neither durst any man","and no one dared","archaic-dare-verb","Durst means dared."),
    c(23,14,"devour widows\u2019 houses","take over widows' houses","archaic-exploitation-phrase","The image condemns exploitation that consumes widows' property."),
    c(23,15,"compass sea and land","travel over sea and land","false-friend-travel-verb","Compass means travel around or across here."),
    c(23,15,"one proselyte","one convert","historical-convert-term","Proselyte means a religious convert."),
    c(23,23,"omitted the weightier matters","neglected the more important matters","archaic-priority-phrase","Weightier means more important, and omitted means neglected."),
    c(23,23,"judgment mercy and faith","justice mercy and faith","false-friend-justice-term","Judgment denotes justice as a requirement of the law."),
    c(23,24,"strain at a gnat","strain out a gnat","historical-filtering-phrase","The image is filtering a gnat out of a drink; at obscures the action today."),
    c(23,27,"whited sepulchres","whitewashed tombs","archaic-tomb-phrase","Whited sepulchres means tombs whitened on the outside."),
    c(23,29,"garnish the sepulchres","decorate the tombs","archaic-decoration-phrase","Garnish means decorate, and sepulchres means tombs."),
    c(24,7,"divers places","various places","false-friend-variety-term","Divers means various."),
    c(24,8,"beginning of sorrows","beginning of birth pains","context-reviewed-birth-image","The Greek image and the discourse context identify labor pains, not generic sadness."),
    c(24,10,"many be offended","many fall away","false-friend-apostasy-phrase","Offended means fall away in this warning."),
    c(24,12,"love of many shall wax cold","love of many shall grow cold","archaic-growth-verb","Wax means grow or become."),
    c(24,19,"them that are with child","pregnant women","archaic-pregnancy-phrase","With child means pregnant."),
    c(24,19,"them that give suck","nursing mothers","archaic-nursing-phrase","Give suck means nurse an infant."),
    c(24,43,"goodman of the house","owner of the house","archaic-homeowner-term","Goodman means the male owner or head of the house."),
    c(24,43,"suffered his house to be broken up","allowed his house to be broken into","false-friend-burglary-phrase","Suffered means allowed and broken up means burglarized."),
    c(24,45,"give them meat in due season","give them food at the proper time","archaic-food-phrase","Meat means food and due season means the proper time."),
    c(24,49,"smite his fellowservants","beat his fellow servants","archaic-violence-phrase","Smite means beat here; fellowservants is separated for readability."),
    c(25,5,"bridegroom tarried","bridegroom was delayed","archaic-delay-verb","Tarried means was delayed."),
    c(25,5,"slumbered and slept","became drowsy and slept","archaic-sleep-verb","Slumbered means became drowsy."),
    c(25,7,"trimmed their lamps","prepared their lamps","historical-lamp-phrase","Trimming an oil lamp means preparing it for use."),
    c(25,27,"money to the exchangers","money with the bankers","historical-finance-term","Exchangers means bankers or money dealers in this deposit example."),
    c(25,27,"mine own with usury","my own with interest","historical-interest-term","Usury denotes interest on the deposited money here."),
    c(25,35,"I was an hungred","I was hungry","archaic-hunger-phrase","An hungred means hungry."),
    c(25,35,"gave me meat","gave me food","false-friend-food-term","Meat means food generally."),
    c(25,35,"ye took me in","ye welcomed me","archaic-hospitality-phrase","Took me in means welcomed or hosted me."),
    c(25,38,"took thee in","welcomed thee","archaic-hospitality-phrase","Took thee in means welcomed thee."),
    c(25,42,"I was an hungred","I was hungry","archaic-hunger-phrase","An hungred means hungry."),
    c(25,42,"gave me no meat","gave me no food","false-friend-food-term","Meat means food generally."),
    c(25,43,"ye took me not in","ye did not welcome me","archaic-hospitality-phrase","Took me in means welcomed me."),
    c(25,44,"did not minister unto thee","did not serve thee","false-friend-service-phrase","Minister means serve in this response."),
    c(26,7,"alabaster box","alabaster jar","historical-container-term","Box denotes a jar or flask of alabaster."),
    c(26,7,"precious ointment","expensive perfume","false-friend-perfume-term","Ointment denotes the costly aromatic perfume used for anointing."),
    c(26,7,"sat at meat","was dining","archaic-meal-phrase","Sat at meat means was eating a meal."),
    c(26,28,"remission of sins","forgiveness of sins","doctrinally-controlled-forgiveness","Remission means forgiveness; the relation to the covenant blood remains intact."),
    c(26,31,"shall be offended because of me","shall fall away because of me","false-friend-desertion-phrase","Offended means the disciples will fall away and scatter."),
    c(26,37,"very heavy","deeply troubled","false-friend-emotional-phrase","Heavy describes deep distress, not physical weight."),
    c(26,38,"exceeding sorrowful","overwhelmed with sorrow","archaic-intensity-phrase","Exceeding sorrowful means overwhelmed with sorrow."),
    c(26,38,"tarry ye here","stay here","archaic-stay-verb","Tarry means stay."),
    c(26,47,"swords and staves","swords and clubs","archaic-weapon-term","Staves means clubs or staffs carried as weapons."),
    c(26,55,"swords and staves","swords and clubs","archaic-weapon-term","Staves means clubs or staffs carried as weapons."),
    c(26,63,"I adjure thee","I charge thee under oath","archaic-oath-phrase","Adjure means solemnly command under oath."),
    c(26,65,"rent his clothes","tore his clothes","false-friend-tear-verb","Rent means tore in this mourning and accusation gesture."),
    c(26,67,"buffeted him","struck him with their fists","archaic-violence-verb","Buffeted means struck repeatedly with fists."),
    c(26,67,"smote him with the palms of their hands","slapped him","archaic-violence-phrase","The phrase describes striking Jesus with open hands."),
    c(26,73,"speech bewrayeth thee","accent gives thee away","archaic-reveal-phrase","Bewrayeth means reveals; Peter's regional speech exposes him."),
    c(27,3,"repented himself","was filled with remorse","false-friend-remorse-phrase","The phrase describes Judas's remorse after the condemnation."),
    c(27,15,"was wont to release","customarily released","archaic-custom-phrase","Was wont means customarily did something."),
    c(27,16,"notable prisoner","notorious prisoner","false-friend-prisoner-term","Notable describes Barabbas as notorious, not admirable."),
    c(27,26,"scourged Jesus","whipped Jesus","historical-punishment-term","Scourged means whipped as a Roman punishment."),
    c(27,27,"common hall","governor's headquarters","historical-government-building","The common hall is the governor's Praetorium or headquarters."),
    c(27,27,"whole band of soldiers","whole company of soldiers","historical-military-term","Band denotes the assembled company of soldiers."),
    c(27,31,"his own raiment","his own clothes","archaic-clothing-term","Raiment means clothes."),
    c(27,38,"two thieves","two robbers","historical-robber-term","The term identifies robbers crucified beside Jesus."),
    c(27,39,"reviled him","insulted him","archaic-abuse-verb","Reviled means insulted abusively."),
    c(27,39,"wagging their heads","shaking their heads","archaic-gesture-verb","Wagging means shaking in this gesture of mockery."),
    c(27,44,"The thieves","The robbers","historical-robber-term","The term identifies the robbers crucified beside Jesus."),
    c(27,50,"yielded up the ghost","gave up his spirit","archaic-death-phrase","The phrase describes Jesus giving up his spirit at death."),
    c(27,51,"veil of the temple was rent in twain","curtain of the temple was torn in two","archaic-temple-phrase","Veil means curtain, rent means torn, and twain means two."),
    c(27,60,"hewn out in the rock","cut out of the rock","archaic-cut-verb","Hewn means cut or carved out."),
    c(27,60,"door of the sepulchre","entrance of the tomb","archaic-tomb-phrase","Sepulchre means tomb and door denotes its entrance."),
    c(27,61,"the sepulchre","the tomb","archaic-tomb-term","Sepulchre means tomb."),
    c(27,64,"sepulchre be made sure","tomb be secured","archaic-tomb-phrase","The order is to secure the tomb."),
    c(27,66,"made the sepulchre sure","secured the tomb","archaic-tomb-phrase","The guards secured the tomb."),
    c(28,3,"raiment white as snow","clothing white as snow","archaic-clothing-term","Raiment means clothing."),
    c(28,1,"In the end of the sabbath, as it began to dawn toward the first day of the week","After the sabbath, as the first day of the week began to dawn","archaic-resurrection-time-phrase","The phrase places the visit after the sabbath at the dawn of the first day, without changing the event sequence."),
    c(28,1,"see the sepulchre","see the tomb","archaic-tomb-term","Sepulchre means tomb."),
    c(28,4,"keepers","guards","historical-guard-term","Keepers means the guards assigned to the tomb."),
    c(28,8,"departed quickly from the sepulchre","departed quickly from the tomb","archaic-tomb-term","Sepulchre means tomb."),
    c(28,19,"teach all nations","make disciples of all nations","context-reviewed-great-commission","The command is to make disciples among all nations; teach alone no longer carries the whole action."),
    c(28,19,"Holy Ghost","Holy Spirit","historical-spirit-term","Holy Ghost is modernized to Holy Spirit without changing the referent."),
]


PENDING = {
    "matthew-kjv-v10-pronoun-system": ("thee/thou/thy/ye verb system", "Modernizing isolated pronouns or verb endings creates mixed grammar; Matthew requires a complete person-and-number pass before any such conversion."),
    "matthew-kjv-v10-raca": ("Raca", "The transliterated insult in Matthew 5:22 has cultural and legal force that a one-word replacement may flatten."),
    "matthew-kjv-v10-fornication": ("fornication in divorce sayings", "The scope of porneia in Matthew 5:32 and 19:9 is doctrinally disputed and needs explicit owner review."),
    "matthew-kjv-v10-hell-terms": ("hell / hell fire", "Matthew uses distinct underlying terms and images; they must not be flattened through a broad replacement."),
    "matthew-kjv-v10-single-eye": ("single eye", "Matthew 6:22 is an idiom whose best plain-English rendering depends on interpretation."),
    "matthew-kjv-v10-kingdom-violence": ("kingdom suffereth violence", "Matthew 11:12 has major interpretive and grammatical alternatives; it remains unchanged pending a focused note."),
    "matthew-kjv-v10-bind-loose": ("bind and loose", "Matthew 16:19 and 18:18 carry legal and ecclesial background that a simple paraphrase could distort."),
    "matthew-kjv-v10-regeneration": ("in the regeneration", "Matthew 19:28 refers to cosmic renewal; replacing the theological term requires a note and owner review."),
    "matthew-kjv-v10-eunuchs": ("eunuchs", "Matthew 19:12 uses the term literally and figuratively within one verse; it needs explanation rather than a blind synonym."),
    "matthew-kjv-v10-carcase-eagles": ("carcase and eagles", "Matthew 24:28 may be rendered carcass with vultures or eagles; the zoological and symbolic choice remains debated."),
    "matthew-kjv-v10-cut-asunder": ("cut him asunder", "Matthew 24:51 can be read literally or as severe punishment language; it remains unchanged pending focused review."),
    "matthew-kjv-v10-tormentors": ("tormentors", "Matthew 18:34 may identify jailers who torture; a replacement should preserve both custody and punishment."),
    "matthew-kjv-v10-textual-additions": ("traditional KJV textual additions", "Verses and clauses absent from some modern critical-text editions remain untouched; editorial modernization must not silently decide textual criticism."),
    "matthew-kjv-v10-marital-know": ("knew her not", "Matthew 1:25 uses know as a marital euphemism; its temporal wording should be explained without implying a doctrinal conclusion."),
}

PENDING_REFS = {
    "matthew-kjv-v10-raca": [(5, 22)],
    "matthew-kjv-v10-fornication": [(5, 32), (19, 9)],
    "matthew-kjv-v10-hell-terms": [(5, 22), (5, 29), (5, 30), (10, 28), (11, 23), (16, 18), (18, 9), (23, 15), (23, 33)],
    "matthew-kjv-v10-single-eye": [(6, 22)],
    "matthew-kjv-v10-kingdom-violence": [(11, 12)],
    "matthew-kjv-v10-bind-loose": [(16, 19), (18, 18)],
    "matthew-kjv-v10-regeneration": [(19, 28)],
    "matthew-kjv-v10-eunuchs": [(19, 12)],
    "matthew-kjv-v10-carcase-eagles": [(24, 28)],
    "matthew-kjv-v10-cut-asunder": [(24, 51)],
    "matthew-kjv-v10-tormentors": [(18, 34)],
    "matthew-kjv-v10-textual-additions": [(5, 22), (5, 44), (17, 21), (18, 11), (20, 16), (23, 14), (27, 35), (28, 20)],
    "matthew-kjv-v10-marital-know": [(1, 25)],
}


def main():
    source_doc = read(CORPUS / "books/MAT.json")
    source = {(c["chapter"], v["verse"]): v["text"] for c in source_doc["chapters"] for v in c["verses"]}
    direction_path = DIRECTION / "books/mat_reading_2026.kjv.v1.json"
    direction = read(direction_path)
    patches = {(v["chapter"], v["verse"]): v for v in direction.get("verses", [])}
    # Earlier KJV rounds normalized a few source verses after the direction
    # layer was created. Rebind every Matthew patch to the current canonical
    # source only after proving that all declared source slices still match.
    for ref, patch in patches.items():
        text = source[ref]
        for edit in patch["edits"]:
            if text[edit["startOffset"]:edit["endOffset"]] != edit["expected"]:
                raise RuntimeError(f"stale edit at MAT.{ref[0]}.{ref[1]}: {edit}")
        patch["sourceTextSha256"] = sha(text.encode())
    # Consolidate two v10 edits that rendered "pregnant of" and replace an
    # earlier article-only repair with the final contextual wording.
    patch_1_18 = patches.get((1, 18))
    if patch_1_18:
        old = [e for e in patch_1_18["edits"] if e["expected"] in {"found with child", "Holy Ghost"}]
        if old:
            patch_1_18["edits"] = [e for e in patch_1_18["edits"] if e not in old]
    patch_13_52 = patches.get((13, 52))
    if patch_13_52:
        prior = next((e for e in patch_13_52["edits"] if e["expected"] == "man that is an householder"), None)
        if prior:
            prior["replacement"] = "head of a household"
            prior["category"] = "archaic-householder-term"
            prior["reason"] = "Householder means the person responsible for a household and its stored treasure."
    patch_15_31 = patches.get((15, 31))
    if patch_15_31:
        prior = next((e for e in patch_15_31["edits"] if e["expected"] == "the dumb to speak"), None)
        if prior:
            prior["replacement"] = "those who could not speak begin to speak"
            prior["category"] = "historical-disability-phrase"
            prior["reason"] = "Dumb means unable to speak; the complete phrase is made grammatical in current English."
    applied = []
    skipped = []
    seen = set()
    for chapter, verse, expected, replacement, category, reason in CHANGES:
        key = (chapter, verse, expected, replacement)
        if key in seen:
            raise RuntimeError(f"duplicate change: {key}")
        seen.add(key)
        text = source[(chapter, verse)]
        count = text.count(expected)
        if count == 0:
            raise RuntimeError(f"expected text missing at MAT.{chapter}.{verse}: {expected!r}")
        patch = patches.get((chapter, verse))
        if patch is None:
            patch = {"chapter": chapter, "verse": verse, "sourceTextSha256": sha(text.encode()), "edits": []}
            direction["verses"].append(patch); patches[(chapter, verse)] = patch
        cursor = 0
        added_for_rule = False
        for _ in range(count):
            start = text.index(expected, cursor); end = start + len(expected); cursor = end
            duplicate = next((e for e in patch["edits"] if e["startOffset"] == start and e["endOffset"] == end and e["replacement"] == replacement), None)
            if duplicate:
                continue
            overlaps = [e for e in patch["edits"] if e["startOffset"] < end and start < e["endOffset"]]
            if overlaps:
                skipped.append({"reference": f"MAT.{chapter}.{verse}", "expected": expected, "start": start, "overlaps": overlaps})
                continue
            patch["edits"].append({
                "startOffset": start, "endOffset": end, "expected": expected, "replacement": replacement,
                "category": category, "reason": reason,
                "evidence": [{"label": "Complete-verse KJV and NIV contextual control", "url": f"https://www.biblegateway.com/passage/?search=Matthew+{chapter}%3A{verse}&version=KJV%3BNIV"}],
            })
            added_for_rule = True
        if added_for_rule:
            applied.append((chapter, verse, expected, replacement, category, reason))
    for patch in direction["verses"]:
        patch["edits"].sort(key=lambda e: e["startOffset"])
    direction["verses"].sort(key=lambda v: (v["chapter"], v["verse"]))
    direction["editorialStatus"] = "approved-matthew-context-review-v10"
    direction["ownerReview"] = {"contentVersion": VERSION, "review": "KJV Matthew complete contextual review", "requiredFullTest": True}
    write(direction_path, direction, compact=True)

    source_path = DIRECTION / "reading_2026.package-source.json"
    package_source = read(source_path)
    package_source["contentVersion"] = VERSION
    package_source["generatedAt"] = "2026-09-12T12:15:00.000Z"
    package_source["editorialPolicy"]["version"] = VERSION
    write(source_path, package_source)

    books = {read(p)["book"]: read(p) for p in (CORPUS / "books").glob("*.json")}
    order = {book: doc["order"] for book, doc in books.items()}
    direction_paths = {read(p)["book"]: p for p in (DIRECTION / "books").glob("*.json")}
    direction_books = [read(p) for p in direction_paths.values()]
    direction_books.sort(key=lambda x: order[x["book"]])
    payload = {"books": direction_books, "contentVersion": VERSION, "editorialPolicy": package_source["editorialPolicy"], "filterId": package_source["filterId"], "format": "shine-reading-filter-package", "normalizationId": package_source["normalizationId"], "schemaVersion": 1, "sourceCorpusSha256": package_source["sourceCorpusSha256"], "sourceVersionId": package_source["sourceVersionId"]}
    raw = canonical(payload).encode()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    packages = DIRECTION / "packages"
    (packages / "reading_2026.kjv.v1.package.json.gz").write_bytes(compressed)
    coverage = {"expectedBookCount": 66, "includedBookCount": len(direction_books), "changedVerseCount": sum(len(b["verses"]) for b in direction_books), "editCount": sum(len(v["edits"]) for b in direction_books for v in b["verses"])}
    manifest = {"format": "shine-reading-filter-manifest", "filterId": package_source["filterId"], "schemaVersion": 1, "contentVersion": VERSION, "sourceVersionId": package_source["sourceVersionId"], "sourceCorpusSha256": package_source["sourceCorpusSha256"], "normalizationId": package_source["normalizationId"], "contentSha256": sha(compressed), "sizeBytes": len(compressed), "expandedSizeBytes": len(raw), "mimeType": "application/vnd.shine.reading-filter+gzip", "generatedAt": "2026-09-12", "editorialPolicy": package_source["editorialPolicy"], "coverage": coverage, "books": [{"id": b["book"], "order": order[b["book"]], "sourceFile": direction_paths[b["book"]].name, "sourceContentSha256": b["sourceContentSha256"], "payloadSha256": sha(canonical(b).encode()), "changedVerseCount": len(b["verses"]), "editCount": sum(len(v["edits"]) for v in b["verses"])} for b in direction_books]}
    write(packages / "reading_2026.kjv.v1.manifest.json", manifest)

    registry = read(REGISTRY)
    registry["updatedAt"] = "2026-09-12T12:15:00.000Z"
    registry["activeContentVersion"] = VERSION
    registry["applied"] = [x for x in registry["applied"] if not (
        (x.get("reference") == "MAT.1.18" and x.get("expected") in {"found with child", "Holy Ghost"})
        or (x.get("reference") == "MAT.13.52" and x.get("expected") == "man that is an householder")
        or (x.get("reference") == "MAT.15.31" and x.get("expected") == "the dumb to speak")
    )]
    known = {(x["reference"], x["expected"], x["replacement"]) for x in registry["applied"]}
    for chapter, verse, expected, replacement, category, reason in CHANGES:
        key = (f"MAT.{chapter}.{verse}", expected, replacement)
        if key not in known:
            registry["applied"].append({"reference": key[0], "expected": expected, "replacement": replacement, "category": category, "reason": reason, "evidenceUrl": f"https://www.biblegateway.com/passage/?search=Matthew+{chapter}%3A{verse}&version=KJV%3BNIV"})
            known.add(key)
    registry["pending"] = [x for x in registry.get("pending", []) if not x.get("id", "").startswith("matthew-kjv-v10-")]
    pronoun_refs = []
    pronouns = ("thee", "thou", "thy", "thine", "ye", "hath", "doth", "shalt")
    for chapter in source_doc["chapters"]:
        for verse in chapter["verses"]:
            words = {word.strip(".,:;!?()[]\"'\u00b6").lower() for word in verse["text"].split()}
            if words.intersection(pronouns):
                pronoun_refs.append((chapter["chapter"], verse["verse"]))
    for pending_id, (term, reason) in PENDING.items():
        refs = pronoun_refs if "pronoun" in pending_id else PENDING_REFS[pending_id]
        registry["pending"].append({"id": pending_id, "status": "pending-review", "scope": "new-testament", "term": term, "proposedOptions": ["Retain with an explanatory note", "Modernize after focused clause review"], "reason": reason, "references": [{"book": BOOK, "chapter": chapter, "verse": verse} for chapter, verse in refs], "evidence": [{"label": "Matthew KJV/NIV contextual control", "url": "https://www.biblegateway.com/passage/?search=Matthew+1-28&version=KJV%3BNIV"}]})
    write(REGISTRY, registry)
    print(json.dumps({"added": len(applied), "skippedOverlaps": len(skipped), "skips": skipped, "matthewChangedVerses": len(direction["verses"]), "matthewEdits": sum(len(v["edits"]) for v in direction["verses"]), "package": coverage, "contentSha256": manifest["contentSha256"]}, indent=2))


if __name__ == "__main__":
    main()
