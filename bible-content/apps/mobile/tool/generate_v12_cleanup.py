import collections
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "assets" / "bibles" / "rv1909" / "books"
DIrection_ROOT = Path(__file__).resolve().parents[1] / "assets" / "bible_direction"
OUTPUT = Path(__file__).resolve().parents[3] / "editorial-changes" / "v12.json"

# Finite-verb enclitics whose current-word-order rewrite is unambiguous.
# Infinitives, gerunds, and imperatives are intentionally excluded.
MAPPINGS = {
    "volvióse": "se volvió",
    "púsose": "se puso",
    "hízolo": "lo hizo",
    "púsolo": "lo puso",
    "sentóse": "se sentó",
    "levantáronse": "se levantaron",
    "sepultáronlo": "lo sepultaron",
    "dióles": "les dio",
    "inclinóse": "se inclinó",
    "púsole": "le puso",
    "respondióle": "le respondió",
    "enojóse": "se enojó",
    "fuéronse": "se fueron",
    "hízole": "le hizo",
    "juntáronse": "se juntaron",
    "encendióse": "se encendió",
    "hiciéronle": "le hicieron",
    "tomóla": "la tomó",
    "volviéronse": "se volvieron",
    "hízose": "se hizo",
    "matólo": "lo mató",
    "pusiéronse": "se pusieron",
    "fuéle": "le fue",
    "hablóles": "les habló",
    "púsolos": "los puso",
    "quedóse": "se quedó",
    "diólo": "lo dio",
    "juntóse": "se juntó",
    "llevólo": "lo llevó",
    "salióse": "se salió",
    "secóse": "se secó",
    "diéronle": "le dieron",
    "hízolos": "los hizo",
    "respondióles": "les respondió",
    "acordóse": "se acordó",
    "dijéronles": "les dijeron",
    "entrególos": "los entregó",
    "harálos": "los hará",
    "púsome": "me puso",
    "tornóse": "se volvió",
    "hiciéronlo": "lo hicieron",
    "hiriólo": "lo hirió",
    "llevólos": "los llevó",
    "pusiéronlo": "lo pusieron",
    "trajéronlo": "lo trajeron",
    "dióle": "le dio",
    "echóse": "se echó",
    "sentáronse": "se sentaron",
    "tornáronse": "se volvieron",
    "apartóse": "se apartó",
}


def whole_word_count(text, expected):
    count = 0
    cursor = 0
    while True:
        offset = text.find(expected, cursor)
        if offset < 0:
            return count
        before = text[offset - 1] if offset else ""
        after_offset = offset + len(expected)
        after = text[after_offset] if after_offset < len(text) else ""
        if not before.isalpha() and not after.isalpha():
            count += 1
        cursor = offset + 1


def main():
    entries = []
    ambiguous = []
    for path in sorted(ROOT.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        found = collections.defaultdict(list)
        for chapter in document["chapters"]:
            for verse in chapter["verses"]:
                text = verse["text"]
                for expected, replacement in MAPPINGS.items():
                    for form, rewritten in (
                        (expected, replacement),
                        (expected[0].upper() + expected[1:], replacement[0].upper() + replacement[1:]),
                    ):
                        count = whole_word_count(text, form)
                        if count == 1:
                            found[(form, rewritten)].append(
                                {"chapter": chapter["chapter"], "verse": verse["verse"]}
                            )
                        elif count > 1:
                            ambiguous.append(
                                (document["book"], chapter["chapter"], verse["verse"], form, count)
                            )
        for (expected, replacement), references in found.items():
            entries.append(
                {
                    "book": document["book"],
                    "references": references,
                    "expected": expected,
                    "replacement": replacement,
                    "category": "clear-archaic-finite-enclitic-order",
                    "reason": (
                        "Se coloca el pronombre antes del verbo finito según el español actual, "
                        "sin cambiar la acción, sus participantes ni el contenido del versículo."
                    ),
                }
            )

    entries, existing_excluded = exclude_existing_edits(entries)

    entries.insert(
        0,
        {
            "book": "EXO",
            "chapter": 15,
            "verse": 25,
            "expected": "el cual metídolo que hubo dentro de las aguas",
            "replacement": "y lo echó en las aguas",
            "category": "context-reviewed-corrupted-verb-phrase",
            "reason": (
                "La frase fuente combina una forma dañada de ‘metiólo’ con palabras que rompen "
                "la oración. El contexto muestra que Moisés echó el árbol en el agua; se restaura "
                "esa acción sin añadir información."
            ),
        },
    )
    output = {
        "format": "shine-reading-2026-editorial-change-set",
        "schemaVersion": 1,
        "contentVersion": 12,
        "generatedAt": "2026-09-10T00:00:00.000Z",
        "issuedAt": "2026-09-10T00:00:00.000Z",
        "expiresAt": "2028-09-10T00:00:00.000Z",
        "sourceVersionId": "RV1909",
        "filterId": "RV1909-LECTURA-2026",
        "changes": entries,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "rules": len(entries),
                "expanded": sum(len(entry.get("references", [None])) for entry in entries),
                "books": len({entry["book"] for entry in entries}),
                "ambiguousExcluded": ambiguous,
                "existingExcluded": existing_excluded,
            },
            ensure_ascii=False,
        )
    )


def exclude_existing_edits(entries):
    corpora = {}
    occupied = {}
    for path in DIrection_ROOT.glob("*_reading_2026.rv1909.v1.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        for verse in document.get("verses", []):
            key = (document["book"], verse["chapter"], verse["verse"])
            occupied[key] = verse.get("edits", [])
    excluded = []
    kept_entries = []
    for entry in entries:
        book = entry["book"]
        if book not in corpora:
            corpus_path = ROOT / f"{book}.json"
            corpora[book] = json.loads(corpus_path.read_text(encoding="utf-8"))
        corpus = corpora[book]
        kept_references = []
        for reference in entry["references"]:
            chapter = next(x for x in corpus["chapters"] if x["chapter"] == reference["chapter"])
            verse = next(x for x in chapter["verses"] if x["verse"] == reference["verse"])
            start = verse["text"].find(entry["expected"])
            end = start + len(entry["expected"])
            collision = next(
                (
                    edit
                    for edit in occupied.get((book, reference["chapter"], reference["verse"]), [])
                    if edit["startOffset"] < end and start < edit["endOffset"]
                ),
                None,
            )
            if collision:
                excluded.append(
                    {
                        "book": book,
                        **reference,
                        "expected": entry["expected"],
                        "existingReplacement": collision["replacement"],
                    }
                )
            else:
                kept_references.append(reference)
        if kept_references:
            entry["references"] = kept_references
            kept_entries.append(entry)
    return kept_entries, excluded


if __name__ == "__main__":
    main()
