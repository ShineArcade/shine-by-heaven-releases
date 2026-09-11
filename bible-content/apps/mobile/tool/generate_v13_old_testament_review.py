import json
from pathlib import Path


CONTENT_ROOT = Path(__file__).resolve().parents[3]
BOOK_ROOT = CONTENT_ROOT / "apps" / "mobile" / "assets" / "bibles" / "rv1909" / "books"
CHANGE_SET = CONTENT_ROOT / "editorial-changes" / "v13.json"
REGISTRY = CONTENT_ROOT / "editorial-review" / "registry.json"

GLOBAL_CHANGES = {
    "menesteroso": "necesitado",
    "menesterosos": "necesitados",
    "Menesteroso": "Necesitado",
    "Menesterosos": "Necesitados",
    "ignominia": "deshonra",
    "Ignominia": "Deshonra",
}

EXACT_CHANGES = [
    ("GEN", 17, 20, "ponerlo he", "lo pondré"),
    ("GEN", 18, 21, "saberlo he", "lo sabré"),
    ("EZK", 11, 19, "darles he", "les daré"),
    ("EZK", 17, 20, "hacerlo he venir", "lo haré venir"),
    ("EZK", 17, 22, "plantarlo he yo", "yo lo plantaré"),
    ("HOS", 7, 12, "hacerlos he caer", "los haré caer"),
    ("JER", 16, 21, "enseñarles he", "les enseñaré"),
    ("JER", 51, 40, "Hacerlos he traer", "Los haré traer"),
    ("NEH", 1, 9, "traerlos he", "los traeré"),
    ("NUM", 16, 21, "consumirlos he", "los consumiré"),
    ("PRO", 13, 10, "avisados", "prudentes"),
    ("PRO", 14, 15, "avisado", "prudente"),
    ("PRO", 22, 3, "avisado", "prudente"),
    ("PRO", 27, 12, "avisado", "prudente"),
]

PENDING_TERMS = [
    ("simple", ["inexperto", "ingenuo"], "En Proverbios suele describir falta de experiencia, pero en otros contextos puede describir falta de juicio."),
    ("simples", ["inexpertos", "ingenuos"], "La forma plural comparte la ambigüedad contextual de ‘simple’."),
    ("prevaricación", ["rebelión", "infidelidad", "pecado"], "Puede señalar rebelión contra Dios, incumplimiento de un pacto o una falta concreta."),
    ("prevaricadores", ["rebeldes", "infieles"], "La identidad del grupo y el tipo de falta deben conservarse en cada pasaje."),
    ("oprobio", ["deshonra", "vergüenza", "rechazo"], "El matiz alterna entre vergüenza pública, deshonra y rechazo."),
    ("escarnio", ["burla", "humillación"], "Puede describir la acción de burlarse o el estado de humillación pública."),
    ("escarnecedor", ["burlón", "insolente"], "En Proverbios designa una conducta persistente, no siempre una burla aislada."),
    ("ciencia", ["conocimiento"], "Generalmente significa conocimiento, pero algunos contextos distinguen conocimiento, habilidad y sabiduría."),
    ("cerviz", ["cuello", "obstinación"], "Algunas apariciones son anatómicas y otras pertenecen al modismo de endurecer la cerviz."),
    ("anatema", ["cosa destinada a destrucción", "cosa consagrada"], "El término cambia entre objeto consagrado, prohibido o destinado a destrucción."),
    ("avisado", ["prudente", "advertido"], "Puede significar prudente o advertido; las cuatro referencias inequívocas de Proverbios se aplican en v13."),
    ("avisados", ["prudentes", "advertidos"], "El plural también requiere distinguir prudencia de haber recibido una advertencia."),
]


def whole_word_offsets(text, expected):
    offsets = []
    cursor = 0
    while True:
        offset = text.find(expected, cursor)
        if offset < 0:
            return offsets
        before = text[offset - 1] if offset else ""
        after_index = offset + len(expected)
        after = text[after_index] if after_index < len(text) else ""
        if not before.isalpha() and not after.isalpha():
            offsets.append(offset)
        cursor = offset + 1


def load_books():
    books = {}
    for path in BOOK_ROOT.glob("*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["order"] <= 39:
            books[document["book"]] = document
    return books


def verse_text(books, book, chapter, verse):
    chapter_entry = next(item for item in books[book]["chapters"] if item["chapter"] == chapter)
    return next(item["text"] for item in chapter_entry["verses"] if item["verse"] == verse)


def main():
    books = load_books()
    changes = []
    grouped = {}
    for book, document in books.items():
        for chapter in document["chapters"]:
            for verse in chapter["verses"]:
                for expected, replacement in GLOBAL_CHANGES.items():
                    offsets = whole_word_offsets(verse["text"], expected)
                    if len(offsets) == 1:
                        grouped.setdefault((book, expected, replacement), []).append(
                            {"chapter": chapter["chapter"], "verse": verse["verse"]}
                        )
    for (book, expected, replacement), references in grouped.items():
        changes.append({
            "book": book,
            "references": references,
            "expected": expected,
            "replacement": replacement,
            "category": "context-reviewed-clear-old-testament-lexicon",
            "reason": "RVR1960 conserva el término histórico y NVI confirma por contexto el sentido actual. La sustitución aclara la lectura sin cambiar la persona, acción ni relación del pasaje.",
        })
    for book, chapter, verse, expected, replacement in EXACT_CHANGES:
        assert verse_text(books, book, chapter, verse).count(expected) == 1, (book, chapter, verse, expected)
        changes.append({
            "book": book,
            "chapter": chapter,
            "verse": verse,
            "expected": expected,
            "replacement": replacement,
            "category": "context-reviewed-old-testament-syntax",
            "reason": "Se reorganiza la construcción futura antigua según el español actual. RVR1960 y NVI confirman la misma acción y el mismo objeto; no se copia su redacción completa.",
        })
    change_set = {
        "format": "shine-reading-2026-editorial-change-set",
        "schemaVersion": 1,
        "contentVersion": 13,
        "generatedAt": "2026-09-10T00:00:00.000Z",
        "issuedAt": "2026-09-10T00:00:00.000Z",
        "expiresAt": "2028-09-10T00:00:00.000Z",
        "sourceVersionId": "RV1909",
        "filterId": "RV1909-LECTURA-2026",
        "changes": changes,
    }
    CHANGE_SET.write_text(json.dumps(change_set, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pending = []
    for term, options, reason in PENDING_TERMS:
        references = []
        for book, document in books.items():
            for chapter in document["chapters"]:
                for verse in chapter["verses"]:
                    if whole_word_offsets(verse["text"].lower(), term):
                        references.append({"book": book, "chapter": chapter["chapter"], "verse": verse["verse"]})
        pending.append({
            "id": f"ot-{term}",
            "status": "pending-review",
            "scope": "old-testament",
            "term": term,
            "proposedOptions": options,
            "reason": reason,
            "references": references,
            "evidence": [
                {"label": "Control contextual RVR1960 y NVI", "url": f"https://www.biblegateway.com/quicksearch/?quicksearch={term}&version=RVR1960%3BNVI"}
            ],
        })
    registry = {
        "format": "shine-reading-2026-editorial-review-registry",
        "schemaVersion": 1,
        "updatedAt": "2026-09-10T00:00:00.000Z",
        "sourceVersionId": "RV1909",
        "activeChangeSet": "editorial-changes/v13.json",
        "requiredFullTest": True,
        "fullTestCommand": "node bible-content/apps/mobile/tool/smoke_bible_content_flow.mjs",
        "pending": pending,
    }
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"appliedRules": len(changes), "appliedReferences": sum(len(x.get("references", [None])) for x in changes), "pendingTerms": len(pending), "pendingReferences": sum(len(x["references"]) for x in pending)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
