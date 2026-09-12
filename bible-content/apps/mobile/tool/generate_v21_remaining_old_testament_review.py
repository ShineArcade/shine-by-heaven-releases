import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK_ROOT = ROOT / "apps/mobile/assets/bibles/rv1909/books"
DIRECTION_ROOT = ROOT / "apps/mobile/assets/bible_direction"
CHANGE_SET = ROOT / "editorial-changes/v21.json"
REGISTRY = ROOT / "editorial-review/registry.json"
VERSION = 21
REVIEWED = {"GEN", "EXO", "LEV", "NUM", "DEU", "JOS"}


# Every family below was read across all of its remaining Old Testament
# occurrences. Each has one stable modern equivalent; ambiguous families are
# deliberately listed under PENDING instead.
FAMILIES = {
    "aqueste": ("este", "archaic-demonstrative", "Aqueste es una forma antigua de este."),
    "empero": ("pero", "archaic-connector", "Empero es un conector antiguo equivalente a pero."),
    "morador": ("habitante", "archaic-inhabitant-term", "Morador designa a quien habita el lugar."),
    "moradores": ("habitantes", "archaic-inhabitant-term", "Moradores designa a quienes habitan el lugar."),
    "aquilón": ("norte", "archaic-direction-term", "Aquilón designa el norte o el viento del norte."),
    "saeta": ("flecha", "archaic-projectile-term", "Saeta designa una flecha, tanto literal como figuradamente."),
    "saetas": ("flechas", "archaic-projectile-term", "Saetas designa flechas, tanto literales como figuradas."),
    "aljaba": ("carcaj", "archaic-container-term", "Aljaba designa el estuche donde se llevan las flechas."),
    "aljabas": ("carcajes", "archaic-container-term", "Aljabas designa los estuches donde se llevan las flechas."),
    "villa": ("ciudad", "archaic-settlement-term", "Villa designa aquí una ciudad o población."),
    "villas": ("ciudades", "archaic-settlement-term", "Villas designa aquí ciudades o poblaciones."),
    "ejido": ("terreno común", "archaic-land-term", "Ejido designa el terreno abierto o común asociado con una ciudad."),
    "ejidos": ("terrenos comunes", "archaic-land-term", "Ejidos designa terrenos abiertos o comunes asociados con ciudades."),
    "ramera": ("prostituta", "archaic-person-term", "Ramera es el término antiguo para prostituta; se conserva el uso literal o figurado del pasaje."),
    "rameras": ("prostitutas", "archaic-person-term", "Rameras es el término antiguo para prostitutas; se conserva el uso literal o figurado del pasaje."),
    "mancebo": ("joven", "archaic-person-term", "Mancebo designa a un hombre joven."),
    "mancebos": ("jóvenes", "archaic-person-term", "Mancebos designa a hombres jóvenes."),
    "oprobio": ("deshonra", "archaic-disgrace-term", "Oprobio expresa deshonra o vergüenza pública."),
    "oprobios": ("deshonras", "archaic-disgrace-term", "Oprobios expresa deshonras o vergüenzas públicas."),
    "escarnio": ("burla", "archaic-mockery-term", "Escarnio expresa burla o humillación pública."),
    "escarnios": ("burlas", "archaic-mockery-term", "Escarnios expresa burlas o humillaciones públicas."),
    "escarnecedor": ("burlador", "archaic-mocker-term", "Escarnecedor designa a quien se burla de otros o de la corrección."),
    "escarnecedores": ("burladores", "archaic-mocker-term", "Escarnecedores designa a quienes se burlan de otros o de la corrección."),
}


EXACT = [
    ("2CH", 35, 15, "no era menester que se apartasen", "no era necesario que se apartasen", "archaic-need-phrase", "La frase significa que no era necesario abandonar su puesto."),
    ("EZR", 7, 20, "te fuere menester dar", "necesites dar", "archaic-need-phrase", "La construcción futura significa lo que resulte necesario dar."),
    ("JOB", 30, 2, "para qué yo habría menester", "para qué necesitaría", "archaic-need-phrase", "Haber menester significa necesitar."),
    ("PRO", 30, 8, "pan que he menester", "pan que necesito", "archaic-need-phrase", "Haber menester significa necesitar."),
    ("JER", 49, 9, "tomarán lo que hubieren menester", "tomarán lo que necesiten", "archaic-need-phrase", "Haber menester significa necesitar."),
    ("JER", 6, 14, "con liviandad", "superficialmente", "archaic-manner-term", "La herida se trata de manera superficial, sin resolverla."),
    ("JER", 8, 11, "con liviandad", "superficialmente", "archaic-manner-term", "La herida se trata de manera superficial, sin resolverla."),
]

OVERRIDES = [
    ("2KI", 13, 17, "Saeta de salud de Jehová, y saeta de salud contra Siria", "Flecha de salvación de Jehová, y flecha de salvación contra Siria", "context-reviewed-salvation-lexicon", "Salud expresa aquí salvación y saeta designa la flecha que simboliza la victoria sobre Siria.", "Saeta de salvación de Jehová, y saeta de salvación contra Siria"),
    ("2KI", 16, 9, "trasportó los moradores á Kir", "llevó cautivos á los habitantes á Kir", "archaic-exile-lexicon", "Transportar describe la deportación forzada, y moradores designa a los habitantes.", "llevó cautivos á los moradores á Kir"),
    ("2KI", 19, 26, "sus moradores, cortos de manos", "sus habitantes, sin fuerzas", "archaic-power-idiom", "Cortos de manos significa sin fuerzas, y moradores designa a los habitantes.", "sus moradores, sin fuerzas"),
]


PENDING = {
    "postrero": ("Puede significar último, final, extremo de la tierra o días futuros; necesita redacción por frase.", ["último", "final", "confín"]),
    "cerviz": ("Alterna entre el cuello físico, dar la espalda y el modismo endurecer la cerviz.", ["cuello", "obstinación", "dar la espalda"]),
    "prevaricación": ("Alterna entre pecado, rebelión, infidelidad al pacto y una transgresión concreta.", ["transgresión", "rebelión", "infidelidad"]),
    "prevaricador": ("El sustantivo depende de si el pasaje acusa rebelión, engaño o infidelidad.", ["rebelde", "infiel", "traidor"]),
    "hollar": ("Puede significar pisar, pisotear, profanar o recorrer; la imagen del versículo decide.", ["pisar", "pisotear", "profanar"]),
    "tiesto": ("Puede ser un fragmento de cerámica, barro cocido o una imagen poética.", ["fragmento de barro", "cerámica", "barro cocido"]),
    "muladar": ("A veces es un basurero y otras forma parte del nombre propio Puerta del Muladar.", ["basurero", "montón de basura", "conservar nombre propio"]),
    "áspid": ("El término hebreo no identifica con certeza una especie moderna única.", ["serpiente venenosa", "cobra", "conservar con nota"]),
    "coyunda": ("En Job 39 describe el aparejo que ata al animal al surco; debe conservar la imagen exacta.", ["yugo", "correa del yugo"]),
    "truhanes": ("Salmo 35:16 contiene una frase hebrea difícil; no se debe aislar una sola palabra.", ["burladores impíos", "burladores en un banquete"]),
    "liviandad": ("Jeremías 3:9 usa la palabra en un sentido distinto de la superficialidad de 6:14 y 8:11.", ["ligereza", "tomar a la ligera"]),
    "mozo": ("Puede designar a un joven, un sirviente o un ayudante militar.", ["joven", "sirviente", "ayudante"]),
    "tornar": ("Puede significar volver, devolver, restaurar o convertirse en otra condición.", ["volver", "devolver", "restaurar"]),
    "allegar": ("Puede significar acercarse, reunirse, presentar, juntar o permanecer unido.", ["acercar", "reunir", "presentar"]),
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def whole_offsets(text, expected):
    pattern = rf"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ]){re.escape(expected)}(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])"
    return [match.start() for match in re.finditer(pattern, text, re.IGNORECASE)]


def unique_phrase(text, start, end):
    left, right = start, end
    while text.count(text[left:right]) != 1:
        if left > 0:
            boundary = text.rfind(" ", 0, max(0, left - 1))
            left = 0 if boundary < 0 else boundary + 1
        if text.count(text[left:right]) == 1:
            break
        if right < len(text):
            boundary = text.find(" ", min(len(text), right + 1))
            right = len(text) if boundary < 0 else boundary
        if left == 0 and right == len(text):
            break
    return left, right


def replacement_case(source, replacement):
    if source.isupper():
        return replacement.upper()
    if source[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def direction_by_book():
    result = {}
    for path in DIRECTION_ROOT.glob("*_reading_2026.rv1909.v1.json"):
        document = read(path)
        result[document["book"]] = document
    return result


def main():
    books = {read(path)["book"]: read(path) for path in BOOK_ROOT.glob("*.json") if read(path)["order"] <= 39}
    directions = direction_by_book()
    entries = []
    spans = {}

    def text(book, chapter, verse):
        return next(v["text"] for c in books[book]["chapters"] if c["chapter"] == chapter for v in c["verses"] if v["verse"] == verse)

    occupied = {
        book: {(v["chapter"], v["verse"]): v.get("edits", []) for v in directions[book].get("verses", [])}
        for book in directions
    }

    def overlaps(book, ref, start, end):
        return any(e["startOffset"] < end and start < e["endOffset"] for e in occupied[book].get(ref, [])) or any(a < end and start < b for a, b in spans.get((book, ref), []))

    def record(book, chapter, verse, expected, replacement, category, reason, previous_replacement=None):
        source = text(book, chapter, verse)
        matches = [m.start() for m in re.finditer(re.escape(expected), source)]
        assert len(matches) == 1, (book, chapter, verse, expected, matches)
        start, end = matches[0], matches[0] + len(expected)
        if previous_replacement is None and overlaps(book, (chapter, verse), start, end):
            return False
        entry = {
            "book": book, "chapter": chapter, "verse": verse,
            "expected": expected, "replacement": replacement,
            "category": category, "reason": reason,
            "evidence": [
                {"label": "Control contextual RVR1960", "url": f"https://www.biblegateway.com/passage/?search={book}+{chapter}%3A{verse}&version=RVR1960"},
                {"label": "Control contextual NVI", "url": f"https://www.biblegateway.com/passage/?search={book}+{chapter}%3A{verse}&version=NVI"},
            ],
        }
        if previous_replacement is not None:
            entry["previousReplacement"] = previous_replacement
        entries.append(entry)
        spans.setdefault((book, (chapter, verse)), []).append((start, end))
        return True

    for item in EXACT:
        record(*item)
    for item in OVERRIDES:
        record(*item)

    for book, document in books.items():
        if book in REVIEWED:
            continue
        for chapter in document["chapters"]:
            for verse in chapter["verses"]:
                source = verse["text"]
                for expected, (replacement, category, reason) in FAMILIES.items():
                    for start in whole_offsets(source, expected):
                        end = start + len(expected)
                        if overlaps(book, (chapter["chapter"], verse["verse"]), start, end):
                            continue
                        left, right = unique_phrase(source, start, end)
                        phrase = source[left:right]
                        actual = source[start:end]
                        modern = replacement_case(actual, replacement)
                        replacement_phrase = phrase[:start-left] + modern + phrase[end-left:]
                        record(book, chapter["chapter"], verse["verse"], phrase, replacement_phrase, category, reason)

    order = {book: document["order"] for book, document in books.items()}
    entries.sort(key=lambda item: (order[item["book"]], item["chapter"], item["verse"], text(item["book"], item["chapter"], item["verse"]).index(item["expected"])))
    payload = {
        "format": "shine-reading-2026-editorial-change-set", "schemaVersion": 1,
        "contentVersion": VERSION, "generatedAt": "2026-09-12T08:00:00.000Z",
        "issuedAt": "2026-09-12T08:00:00.000Z", "expiresAt": "2028-09-12T08:00:00.000Z",
        "sourceVersionId": "RV1909", "filterId": "RV1909-LECTURA-2026", "changes": entries,
    }
    CHANGE_SET.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry = read(REGISTRY)
    registry["pending"] = [item for item in registry.get("pending", []) if not item.get("id", "").startswith("ot-completion-v21-")]
    for index, (term, (reason, options)) in enumerate(PENDING.items(), 1):
        references = []
        for book, document in books.items():
            if book in REVIEWED:
                continue
            for chapter in document["chapters"]:
                for verse in chapter["verses"]:
                    if whole_offsets(verse["text"], term):
                        references.append({"book": book, "chapter": chapter["chapter"], "verse": verse["verse"]})
        registry["pending"].append({
            "id": f"ot-completion-v21-{index}", "status": "pending-review", "scope": "old-testament",
            "term": term, "proposedOptions": options, "reason": reason, "references": references,
            "evidence": [{"label": "Revisión contextual por versículo", "url": f"https://www.biblegateway.com/quicksearch/?quicksearch={term}&version=RVR1960%3BNVI"}],
        })
    registry.update({"updatedAt": "2026-09-12T08:00:00.000Z", "activeChangeSet": "editorial-changes/v21.json"})
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changes": len(entries), "changedVerses": len(spans), "books": len({e['book'] for e in entries}), "pendingFamilies": len(PENDING)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
