import json
from pathlib import Path


CONTENT_ROOT = Path(__file__).resolve().parents[3]
BOOK_ROOT = CONTENT_ROOT / "apps" / "mobile" / "assets" / "bibles" / "rv1909" / "books"
DIRECTION_ROOT = CONTENT_ROOT / "apps" / "mobile" / "assets" / "bible_direction"
CHANGE_SET = CONTENT_ROOT / "editorial-changes" / "v14.json"
REGISTRY = CONTENT_ROOT / "editorial-review" / "registry.json"
NT_CODES = {
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH",
    "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS",
    "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
}

GLOBAL_CHANGES = {
    "empero": "pero", "Empero": "Pero",
    "postrer": "último", "Postrer": "Último",
    "postreros": "últimos", "Postreros": "Últimos",
    "contumaces": "rebeldes", "Contumaces": "Rebeldes",
    "detractores": "difamadores", "Detractores": "Difamadores",
    "ayo": "tutor", "Ayo": "Tutor",
}

EXACT_CHANGES = [
    ("2TI", 3, 3, "aborrecedores de lo bueno", "enemigos de lo bueno", "clear-character-lexicon"),
    ("2TI", 3, 16, "redargüir", "reprender", "context-reviewed-teaching-verb"),
    ("2TI", 4, 2, "redarguye", "corrige", "context-reviewed-teaching-verb"),
    ("JHN", 8, 46, "me redarguye de pecado", "demuestra que he pecado", "context-reviewed-proof-phrase"),
    ("JAS", 1, 15, "pare el pecado", "da a luz el pecado", "context-reviewed-birth-metaphor"),
    ("JAS", 1, 21, "palabra ingerida", "palabra implantada", "context-reviewed-implanted-word"),
    ("ROM", 1, 27, "cosas nefandas", "actos vergonzosos", "clear-archaic-moral-phrase"),
    ("ROM", 1, 29, "Estando atestados", "Estando llenos", "clear-archaic-fullness-phrase"),
    ("EPH", 5, 18, "disolución", "desenfreno", "context-reviewed-dissipation-lexicon"),
    ("GAL", 5, 19, "disolución", "libertinaje", "context-reviewed-dissipation-lexicon"),
    ("TIT", 1, 6, "disolución", "libertinaje", "context-reviewed-dissipation-lexicon"),
    ("JUD", 1, 4, "disolución", "libertinaje", "context-reviewed-dissipation-lexicon"),
    ("1PE", 4, 4, "desenfrenamiento de disolución", "desenfreno", "context-reviewed-dissipation-phrase"),
    ("2PE", 2, 18, "disoluciones", "conductas desenfrenadas", "context-reviewed-dissipation-lexicon"),
    ("2TI", 1, 7, "templanza", "dominio propio", "context-reviewed-self-control-lexicon"),
    ("GAL", 5, 23, "templanza", "dominio propio", "context-reviewed-self-control-lexicon"),
    ("ACT", 26, 25, "templanza", "cordura", "context-reviewed-soundness-lexicon"),
    ("ROM", 12, 3, "templanza", "sensatez", "context-reviewed-sober-judgment-lexicon"),
    ("1PE", 1, 13, "con templanza", "con sobriedad", "context-reviewed-sobriety-lexicon"),
    ("2PE", 1, 6, "Y en la ciencia templanza, y en la templanza paciencia", "Y al conocimiento dominio propio, y al dominio propio paciencia", "context-reviewed-self-control-phrase"),
    ("HEB", 5, 12, "primeros rudimentos", "principios básicos", "clear-foundational-lexicon"),
    ("COL", 2, 20, "rudimentos del mundo", "principios del mundo", "context-reviewed-world-principles"),
    ("GAL", 4, 3, "rudimentos del mundo", "principios del mundo", "context-reviewed-world-principles"),
    ("GAL", 4, 9, "rudimentos", "principios", "context-reviewed-world-principles"),
]

PENDING_TERMS = [
    ("concupiscencia", ["mal deseo", "deseo desordenado"], "Alterna entre deseo pecaminoso, deseo de la carne y deseo en sentido colectivo."),
    ("concupiscencias", ["malos deseos", "deseos desordenados"], "La forma plural necesita conservar el objeto y la fuerza moral de cada pasaje."),
    ("iniquidad", ["maldad", "injusticia", "pecado"], "Puede describir maldad, injusticia o oposición a la ley de Dios."),
    ("inicuo", ["malvado", "sin ley"], "En algunos pasajes es un adjetivo general y en otros un título escatológico."),
    ("inicuos", ["malvados", "transgresores"], "La identidad del grupo depende del contexto narrativo o profético."),
    ("propiciación", ["sacrificio que obtiene perdón", "sacrificio de reconciliación"], "Es un término doctrinal; una palabra demasiado general perdería la relación entre sacrificio, perdón y reconciliación."),
    ("potestades", ["autoridades", "poderes"], "Puede señalar autoridades humanas, poderes espirituales o capacidad delegada."),
    ("principados", ["gobernantes", "poderes espirituales"], "El referente cambia entre jerarquías y poderes espirituales."),
    ("disensión", ["división", "desacuerdo", "confusión"], "El sentido cambia entre conflicto personal, división colectiva y desorden."),
    ("disensiones", ["divisiones", "desacuerdos"], "Cada lista o episodio determina si se enfatiza división o conflicto."),
    ("longanimidad", ["paciencia prolongada", "tolerancia"], "No siempre equivale a la palabra paciencia que aparece junto a ella."),
    ("fornicación", ["inmoralidad sexual"], "La sustitución debe conservar cuándo el texto habla de una conducta concreta y cuándo usa una imagen profética."),
    ("inmundicia", ["impureza"], "Puede ser moral, corporal o metafórica; requiere verificación por referencia."),
    ("dispensación", ["administración", "plan"], "Puede describir una responsabilidad encargada o el desarrollo del plan de Dios."),
    ("incircuncisión", ["los no circuncidados", "condición de no estar circuncidado"], "Es un término técnico y a veces nombra a un grupo; no admite una sustitución global."),
    ("solícito", ["diligente", "preocupado", "prudente"], "Sus sentidos cambian entre diligencia, cuidado por otros y sobriedad."),
    ("solícitos", ["diligentes", "preocupados"], "El plural también cambia entre procurar algo y preocuparse por algo."),
]


def whole_word_offsets(text, expected):
    offsets, cursor = [], 0
    while True:
        offset = text.find(expected, cursor)
        if offset < 0:
            return offsets
        before = text[offset - 1] if offset else ""
        end = offset + len(expected)
        after = text[end] if end < len(text) else ""
        if not before.isalpha() and not after.isalpha():
            offsets.append(offset)
        cursor = offset + 1


def load_books():
    books = {}
    for path in BOOK_ROOT.glob("*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["book"] in NT_CODES:
            books[document["book"]] = document
    return books


def load_existing_edits():
    edits = {}
    for path in DIRECTION_ROOT.glob("*.json"):
        if path.name == "reading_2026.package-source.json":
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        for verse in document["verses"]:
            edits[(document["book"], verse["chapter"], verse["verse"])] = verse["edits"]
    return edits


def overlaps_existing(existing, book, chapter, verse, start, end):
    return any(
        start < edit["endOffset"] and end > edit["startOffset"]
        for edit in existing.get((book, chapter, verse), [])
    )


def verse_text(books, book, chapter, verse):
    chapter_entry = next(item for item in books[book]["chapters"] if item["chapter"] == chapter)
    return next(item["text"] for item in chapter_entry["verses"] if item["verse"] == verse)


def main():
    books = load_books()
    existing = load_existing_edits()
    changes, grouped = [], {}
    for book, document in books.items():
        for chapter in document["chapters"]:
            for verse in chapter["verses"]:
                for expected, replacement in GLOBAL_CHANGES.items():
                    offsets = whole_word_offsets(verse["text"], expected)
                    if len(offsets) == 1 and not overlaps_existing(
                        existing, book, chapter["chapter"], verse["verse"], offsets[0], offsets[0] + len(expected)
                    ):
                        grouped.setdefault((book, expected, replacement), []).append(
                            {"chapter": chapter["chapter"], "verse": verse["verse"]}
                        )
    for (book, expected, replacement), references in grouped.items():
        changes.append({
            "book": book, "references": references, "expected": expected, "replacement": replacement,
            "category": "context-reviewed-clear-new-testament-lexicon",
            "reason": "RVR1960 y NVI confirman el sentido actual en estas referencias. El ajuste reemplaza una forma arcaica sin alterar sujeto, acción ni enseñanza.",
        })
    for book, chapter, verse, expected, replacement, category in EXACT_CHANGES:
        source_text = verse_text(books, book, chapter, verse)
        assert source_text.count(expected) == 1, (book, chapter, verse, expected)
        start = source_text.index(expected)
        if overlaps_existing(existing, book, chapter, verse, start, start + len(expected)):
            continue
        changes.append({
            "book": book, "chapter": chapter, "verse": verse, "expected": expected, "replacement": replacement,
            "category": category,
            "reason": "El contexto completo fue contrastado con RVR1960 y NVI. Se conserva el significado de la frase y se elimina una construcción que interrumpe la lectura actual.",
        })
    change_set = {
        "format": "shine-reading-2026-editorial-change-set", "schemaVersion": 1,
        "contentVersion": 14, "generatedAt": "2026-09-10T00:00:00.000Z",
        "issuedAt": "2026-09-10T00:00:00.000Z", "expiresAt": "2028-09-10T00:00:00.000Z",
        "sourceVersionId": "RV1909", "filterId": "RV1909-LECTURA-2026", "changes": changes,
    }
    CHANGE_SET.write_text(json.dumps(change_set, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    pending = [entry for entry in registry["pending"] if entry["scope"] != "new-testament"]
    for term, options, reason in PENDING_TERMS:
        references = []
        for book, document in books.items():
            for chapter in document["chapters"]:
                for verse in chapter["verses"]:
                    if whole_word_offsets(verse["text"].lower(), term):
                        references.append({"book": book, "chapter": chapter["chapter"], "verse": verse["verse"]})
        pending.append({
            "id": f"nt-{term}", "status": "pending-review", "scope": "new-testament", "term": term,
            "proposedOptions": options, "reason": reason, "references": references,
            "evidence": [{"label": "Control contextual RVR1960 y NVI", "url": f"https://www.biblegateway.com/quicksearch/?quicksearch={term}&version=RVR1960%3BNVI"}],
        })
    registry.update({"updatedAt": "2026-09-10T00:00:00.000Z", "activeChangeSet": "editorial-changes/v14.json", "pending": pending})
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"appliedRules": len(changes), "appliedReferences": sum(len(x.get("references", [None])) for x in changes), "pendingTerms": len(pending), "pendingReferences": sum(len(x["references"]) for x in pending)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
