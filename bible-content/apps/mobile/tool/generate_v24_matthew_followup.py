import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK = ROOT / "apps/mobile/assets/bibles/rv1909/books/MAT.json"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/matthew_reading_2026.rv1909.v1.json"
CHANGE_SET = ROOT / "editorial-changes/v24.json"
REGISTRY = ROOT / "editorial-review/registry.json"
PACKAGE_SOURCE = ROOT / "apps/mobile/assets/bible_direction/reading_2026.package-source.json"
VERSION = 24


def change(chapter, verse, expected, replacement, category, reason, remove_expected):
    return {
        "book": "MAT",
        "chapter": chapter,
        "verse": verse,
        "expected": expected,
        "replacement": replacement,
        "category": category,
        "reason": reason,
        "removeExpected": remove_expected,
        "evidence": [{
            "label": "Control contextual RVR1960, NVI, LBLA y RVC",
            "url": f"https://www.biblegateway.com/passage/?search=Mateo+{chapter}%3A{verse}&version=RVR1960%3BNVI%3BLBLA%3BRVC",
        }],
    }


# Revisión breve posterior a Marcos. Cada entrada corrige una frase que quedó
# gramaticalmente rota en la salida renderizada de Mateo; no reabre las
# decisiones doctrinales ni las familias que siguen reservadas.
CHANGES = [
    change(2, 7, "entendió de ellos diligentemente el tiempo del aparecimiento de la estrella", "averiguó cuidadosamente cuándo había aparecido la estrella", "grammar-inquiry-clause", "La frase completa elimina el complemento huérfano de la estrella y conserva que Herodes averiguó el momento de su aparición.", ["entendió de ellos diligentemente el tiempo del aparecimiento"]),
    change(5, 11, "os vituperaren y os persiguieren, y dijeren", "os insulten, os persigan y digan", "grammar-parallel-verbs", "Los tres verbos coordinados conservan la misma persona y el mismo tiempo verbal después de modernizar vituperaren.", ["os vituperaren"]),
    change(5, 15, "mas", "sino", "contextual-adversative-connector", "Después de una negación, la lámpara se coloca no debajo del recipiente, sino sobre el candelero.", ["mas"]),
    change(5, 26, "el último cuadrante", "la última moneda", "grammar-coin-agreement", "El artículo, el adjetivo y el sustantivo deben concordar al explicar el cuadrante como la última moneda adeudada.", ["último cuadrante"]),
    change(5, 33, "mas", "sino que", "contextual-adversative-connector", "La instrucción contrapone no jurar falsamente con cumplir los juramentos al Señor; sino que expresa esa corrección.", ["mas"]),
    change(6, 13, "mas", "sino", "contextual-adversative-connector", "La petición contrapone no entrar en tentación con ser librados del mal.", ["mas"]),
    change(6, 19, "la polilla y el orín corrompe", "la polilla y el óxido corrompen", "grammar-compound-subject", "Polilla y óxido forman un sujeto compuesto y requieren el verbo plural.", ["orín"]),
    change(6, 20, "ni polilla ni orín corrompe", "ni polilla ni óxido corrompen", "grammar-compound-subject", "Los dos agentes coordinados conservan el plural verbal en la imagen paralela del tesoro celestial.", ["orín"]),
    change(7, 21, "mas", "sino", "contextual-adversative-connector", "La frase distingue a quien solo dice Señor de quien hace la voluntad del Padre.", ["mas"]),
    change(9, 17, "mas", "sino que", "contextual-adversative-connector", "El vino nuevo no se pone en odres viejos, sino que se pone en odres nuevos.", ["mas"]),
    change(9, 24, "mas", "sino que", "contextual-adversative-connector", "Jesús afirma que la niña no está muerta, sino que duerme.", ["mas"]),
    change(15, 11, "mas", "sino", "contextual-adversative-connector", "La enseñanza contrapone lo que entra por la boca con lo que sale de ella.", ["mas"]),
    change(16, 17, "mas", "sino", "contextual-adversative-connector", "La revelación no procede de carne ni sangre, sino del Padre celestial.", ["mas"]),
    change(21, 21, "mas", "sino que", "contextual-adversative-connector", "No solo podrían repetir la señal de la higuera, sino que también podrían hablar al monte; sino que mantiene esa ampliación.", ["mas"]),
    change(22, 30, "mas", "sino que", "contextual-adversative-connector", "En la resurrección no se casan, sino que son como los ángeles de Dios.", ["mas"]),
    change(23, 7, "las salutaciones", "los saludos", "grammar-greeting-agreement", "El artículo debe concordar con saludos después de modernizar salutaciones.", ["salutaciones"]),
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, compact=False):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=None if compact else 2,
                   separators=(",", ":") if compact else None) + "\n",
        encoding="utf-8",
    )


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    source_doc = read(BOOK)
    source = {
        (chapter["chapter"], verse["verse"]): verse["text"]
        for chapter in source_doc["chapters"]
        for verse in chapter["verses"]
    }
    direction = read(DIRECTION)
    patches = {(item["chapter"], item["verse"]): item for item in direction["verses"]}
    applied = []

    for item in CHANGES:
        ref = (item["chapter"], item["verse"])
        text = source[ref]
        if text.count(item["expected"]) != 1:
            raise RuntimeError(f"expected exactly once at MAT.{ref[0]}.{ref[1]}: {item['expected']!r}")
        patch = patches[ref]
        removals = set(item["removeExpected"])
        removed = [edit for edit in patch["edits"] if edit["expected"] in removals]
        if {edit["expected"] for edit in removed} != removals:
            raise RuntimeError(f"prior edit missing at MAT.{ref[0]}.{ref[1]}: {removals}")
        patch["edits"] = [edit for edit in patch["edits"] if edit["expected"] not in removals]

        start = text.index(item["expected"])
        end = start + len(item["expected"])
        overlaps = [
            edit for edit in patch["edits"]
            if edit["startOffset"] < end and start < edit["endOffset"]
        ]
        if overlaps:
            raise RuntimeError(f"overlap at MAT.{ref[0]}.{ref[1]}: {overlaps}")
        patch["edits"].append({
            "startOffset": start,
            "endOffset": end,
            "expected": item["expected"],
            "replacement": item["replacement"],
            "category": item["category"],
            "reason": item["reason"],
            "evidence": item["evidence"],
        })
        applied.append(item)

    for patch in direction["verses"]:
        text = source[(patch["chapter"], patch["verse"])]
        patch["sourceTextSha256"] = sha(text)
        patch["edits"].sort(key=lambda edit: edit["startOffset"])
        prior_end = -1
        for edit in patch["edits"]:
            if edit["startOffset"] < prior_end:
                raise RuntimeError(f"overlap at MAT.{patch['chapter']}.{patch['verse']}")
            if text[edit["startOffset"]:edit["endOffset"]] != edit["expected"]:
                raise RuntimeError(f"offset mismatch at MAT.{patch['chapter']}.{patch['verse']}: {edit}")
            prior_end = edit["endOffset"]

    direction["followupReview"] = {
        "contentVersion": VERSION,
        "changeSet": "editorial-changes/v24.json",
        "review": "Repaso breve de concordancia y conectores después de Marcos",
        "requiredFullTest": True,
    }
    write(DIRECTION, direction, compact=True)

    payload = {
        "format": "shine-reading-2026-editorial-change-set",
        "schemaVersion": 1,
        "contentVersion": VERSION,
        "generatedAt": "2026-09-12T22:20:00.000Z",
        "issuedAt": "2026-09-12T22:20:00.000Z",
        "expiresAt": "2028-09-12T22:20:00.000Z",
        "sourceVersionId": "RV1909",
        "filterId": "RV1909-LECTURA-2026",
        "changes": [{key: value for key, value in item.items() if key != "removeExpected"} for item in applied],
    }
    write(CHANGE_SET, payload)

    package_source = read(PACKAGE_SOURCE)
    package_source["contentVersion"] = VERSION
    package_source["generatedAt"] = "2026-09-12T22:20:00.000Z"
    package_source["editorialPolicy"]["version"] = VERSION
    write(PACKAGE_SOURCE, package_source)

    registry = read(REGISTRY)
    registry["updatedAt"] = "2026-09-12T22:20:00.000Z"
    registry["activeChangeSet"] = "editorial-changes/v24.json"
    write(REGISTRY, registry)

    print(json.dumps({
        "contentVersion": VERSION,
        "correctedMatthewVerses": len(applied),
        "matthewChangedVerses": len(direction["verses"]),
        "matthewEdits": sum(len(item["edits"]) for item in direction["verses"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
