import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RV_CORPUS = ROOT / "apps/mobile/assets/bibles/rv1909/books"
RV_DIRECTION = ROOT / "apps/mobile/assets/bible_direction"
KJV_CORPUS = ROOT / "apps/mobile/assets/bibles/kjv/books"
KJV_DIRECTION = ROOT / "apps/mobile/assets/bible_direction/kjv/books"

BOOKS = (
    "LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM "
    "HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"
).split()

RV_TERMS = (
    "acepción advenimiento afrenta amonestación anatema benignidad concilio "
    "concupiscencia concupiscencias dispensación disensión disensiones estrado "
    "holgar huelgo holgó libación longanimidad maledicencia neófito ósculo "
    "potestad potestades salutación salutaciones sedición solícito solícitos "
    "escarnecido escarnecer escarnecieron escarneciéndole denuedo denuestos "
    "vituperio vituperios baldón oprobio contienda contiendas contumelia "
    "inicuo inicuos iniquidad propiciación principados fornicación inmundicia "
    "incircuncisión liviandad lascivia avaricia avariento detracción dádiva "
    "dádivas postrimerías prevaricación prevaricadores réprobo réprobos "
    "redargüir redarguye redargüido redargüidos apercibido apercibidos "
    "apercibir aparejado aparejados aparejar remisión remisiones expiación "
    "expiaciones circuncisión circuncidados ayuntamiento prosélito prosélitos "
    "paráclito publicanos tributo tributos denario denarios dracma dracmas "
    "cuadrante cuadrantes almud candelero candeleros odre odres salutaciones "
    "viandas vianda vituallas coyunda yugo yugos pábulo simiente simientes "
    "redimir redención primicias arras mediador testamento pacto pactos "
    "caridad caridades ciencia ciencias conversación conversaciones "
    "comunicación comunicaciones misterio misterios revelación revelaciones "
    "potentados preeminencia prevaricó refractarios irremisiblemente "
    "ignominia vituperado vituperados injurias injuriadores concupiscible "
    "solicitud solicitad solicitando sobrepujar sobrepujó sobrepujante "
    "sobreexcelente entrañas entrañable entrañablemente estrechar apremiar "
    "constreñir constreñido compelió compeler ordenanza ordenanzas rudimentos "
    "rudimento empero postrer postreros ayo contumaces detractores nefandas "
    "atestados disolución disoluciones templanza mansedumbre presbítero "
    "presbíteros obispo obispos diácono diáconos gentil gentiles gentío "
    "flaco flaca flacos flaqueza flaquezas compañía compañías plática pláticas "
    "notorio potencia facultad príncipe príncipes porfía concurso concurrencia "
    "menester plugo cebado reconvenidos hollare"
).split()

KJV_TERMS = (
    "abideth abode abroad aforetime albeit alms arrayed assayed atonement bade "
    "bid bishoprick bowels careful charity chambering concupiscence conversation "
    "covetousness divers draught ensample ensamples fain gainsaying haply "
    "husbandman husbandmen infirmity infirmities lade laden lasciviousness "
    "lewdness listeth meat meats meet ministration ordinances peculiar "
    "peradventure prevent prevented quick quickened railer recompence remission "
    "reproach respect shambles shew shewed shewing strait straightway tarry "
    "temperance testament travail unfeigned verily want wist wot wrought "
    "wherefore wherein whereby wherewithal whithersoever thither hither nigh "
    "publican publicans scrip raiment damsel palsy sepulchre twain ghost "
    "suffer suffered suffereth sufferedst sufferings unto pray prayed besought "
    "entreat entreated devils devil swine ship ships coasts corn leaven charger "
    "pennyworth farthing farthings candlestick candlesticks fornication uncleanness "
    "longsuffering propitiation principalities powers dispensation uncircumcision "
    "sedition seditions salute salutation salutations admonition anathema "
    "benignity council councils footstool malice guile superfluity nought ought"
).split()

WORD_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.UNICODE)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_verses(corpus_root):
    result = {}
    for path in corpus_root.glob("*.json"):
        doc = load(path)
        if doc["book"] not in BOOKS:
            continue
        for chapter in doc["chapters"]:
            for verse in chapter["verses"]:
                result[(doc["book"], chapter["chapter"], verse["verse"])] = verse["text"]
    return result


def directions(direction_root, kjv=False):
    result = {}
    paths = direction_root.glob("*.json")
    for path in paths:
        if path.name.endswith("package-source.json"):
            continue
        doc = load(path)
        if doc.get("book") not in BOOKS:
            continue
        for verse in doc.get("verses", []):
            result[(doc["book"], verse["chapter"], verse["verse"])] = verse["edits"]
    return result


def render(text, edits):
    for edit in sorted(edits, key=lambda x: x["startOffset"], reverse=True):
        assert text[edit["startOffset"]:edit["endOffset"]] == edit["expected"]
        text = text[:edit["startOffset"]] + edit["replacement"] + text[edit["endOffset"]:]
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", choices=("rv", "kjv"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    corpus_root = RV_CORPUS if args.language == "rv" else KJV_CORPUS
    direction_root = RV_DIRECTION if args.language == "rv" else KJV_DIRECTION
    terms = RV_TERMS if args.language == "rv" else KJV_TERMS
    verses = source_verses(corpus_root)
    edits = directions(direction_root, args.language == "kjv")
    rendered = {ref: render(text, edits.get(ref, [])) for ref, text in verses.items()}

    findings = defaultdict(list)
    counts = Counter()
    for ref, text in rendered.items():
        tokens = [token.casefold() for token in WORD_RE.findall(text)]
        counts.update(tokens)
        token_set = set(tokens)
        for term in terms:
            if term.casefold() in token_set:
                findings[term].append({"reference": f"{ref[0]}.{ref[1]}.{ref[2]}", "text": text})

    payload = {
        "language": args.language,
        "books": BOOKS,
        "verseCount": len(rendered),
        "terms": [
            {"term": term, "count": counts[term.casefold()], "verses": findings[term]}
            for term in terms if findings[term]
        ],
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"language": args.language, "verseCount": len(rendered), "candidateTerms": len(payload["terms"]), "candidateOccurrences": sum(x["count"] for x in payload["terms"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
