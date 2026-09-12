import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK_PATH = ROOT / "apps/mobile/assets/bibles/rv1909/books/JOS.json"
LAYER_PATH = ROOT / "apps/mobile/assets/bible_direction/joshua_reading_2026.rv1909.v1.json"
CHANGE_SET = ROOT / "editorial-changes/v20.json"
REGISTRY = ROOT / "editorial-review/registry.json"
VERSION = 20


# These clauses were read in their complete verse against the local RVR1960 and
# NVI controls. The replacements are minimal and independently worded.
EXPLICIT = [
    (1, 2, "Mi siervo Moisés es muerto", "Mi siervo Moisés ha muerto", "archaic-verb-phrase", "La forma actual expresa la misma muerte ya ocurrida sin el giro arcaico es muerto."),
    (1, 7, "ni á diestra ni á siniestra", "ni a derecha ni a izquierda", "archaic-direction-phrase", "Diestra y siniestra designan aquí derecha e izquierda."),
    (2, 1, "entráronse", "entraron", "archaic-enclitic-order", "El pronombre enclítico no aporta un participante distinto en esta acción."),
    (2, 18, "cordón de grana", "cordón rojo", "archaic-color-term", "Grana designa el color rojo del cordón que sirve como señal."),
    (3, 9, "Llegaos acá", "Acercaos", "archaic-imperative", "Llegarse significa acercarse en esta invitación a escuchar."),
    (4, 6, "¿Qué os significan estas piedras?", "¿Qué significan estas piedras?", "archaic-question-phrase", "Se elimina el dativo arcaico que oscurece una pregunta sobre el significado de las piedras."),
    (4, 7, "serán por memoria", "servirán como recuerdo", "archaic-memorial-phrase", "Por memoria significa que las piedras servirán como recuerdo permanente."),
    (5, 9, "oprobio", "deshonra", "archaic-lexicon", "Oprobio significa deshonra en la declaración sobre Egipto."),
    (5, 10, "asentaron el campo", "acamparon", "archaic-camp-phrase", "Asentar el campo significa instalar el campamento."),
    (6, 1, "EMPERO", "PERO", "archaic-connector", "Empero es un conector arcaico equivalente a pero."),
    (7, 14, "Os allegaréis", "Os presentaréis", "archaic-assembly-verb", "Allegarse por tribus significa presentarse para la identificación ordenada."),
    (7, 14, "la tribu que Jehová tomare, se allegará por sus familias", "la tribu que Jehová tomare, se presentará por sus familias", "archaic-assembly-verb", "Allegarse por familias significa presentarse ante la asamblea."),
    (7, 14, "la familia que Jehová tomare, se allegará por sus casas", "la familia que Jehová tomare, se presentará por sus casas", "archaic-assembly-verb", "Allegarse por casas significa presentarse ante la asamblea."),
    (7, 14, "allegaráse", "se presentará", "archaic-enclitic-order", "Se modernizan el verbo de comparecencia y el orden del pronombre."),
    (7, 16, "hizo allegar á Israel", "hizo presentarse a Israel", "archaic-assembly-verb", "La acción consiste en presentar a Israel por tribus para identificar al responsable."),
    (8, 13, "vínose Josué aquella noche al medio del valle", "Josué fue aquella noche al medio del valle", "archaic-enclitic-order", "Se moderniza el orden verbal sin alterar el desplazamiento de Josué."),
    (8, 14, "levantóse prestamente de mañana", "se levantó temprano", "archaic-time-phrase", "La frase indica que el rey se levantó temprano para combatir."),
    (8, 19, "prestamente", "rápidamente", "archaic-adverb", "Prestamente significa rápidamente en la salida de la emboscada."),
    (9, 13, "los henchimos nuevos", "los llenamos cuando eran nuevos", "archaic-container-phrase", "Henchir significa llenar; se conserva que los recipientes eran nuevos al llenarlos."),
    (9, 15, "concertó con ellos", "pactó con ellos", "archaic-covenant-verb", "Concertar aquí significa celebrar un pacto de paz."),
    (11, 4, "con gran muchedumbre de caballos y carros", "con muchísimos caballos y carros", "archaic-quantity-phrase", "Muchedumbre expresa la gran cantidad de caballos y carros."),
    (14, 9, "la tierra que holló tu pie", "la tierra que pisó tu pie", "archaic-land-verb", "Hollar significa pisar en la promesa territorial."),
    (15, 9, "sale á la ciudades", "sale a las ciudades", "source-grammar-correction", "Se corrigen la preposición y la concordancia plural de la frase."),
    (17, 13, "hicieron tributario al Cananeo", "sometieron al cananeo a trabajos forzados", "archaic-labor-phrase", "Tributario describe aquí el sometimiento del pueblo cananeo a trabajos forzados."),
    (18, 1, "asentaron allí el tabernáculo", "instalaron allí el tabernáculo", "archaic-installation-verb", "Asentar el tabernáculo significa instalarlo en Silo."),
    (18, 9, "tornaron á Josué", "volvieron a Josué", "archaic-return-verb", "Tornar significa volver en este itinerario."),
    (18, 20, "término al lado", "límite al lado", "archaic-geographic-term", "Término designa el límite territorial oriental de Benjamín."),
    (21, 41, "todas la villas", "todas las ciudades", "source-grammar-and-archaic-term", "Se corrige la concordancia todas las y se moderniza villas como ciudades."),
    (21, 34, "Cartha con sus ejidos", "Cartha con sus campos de pastoreo", "archaic-pasture-term", "Ejidos designa los campos de pastoreo que rodeaban las ciudades levíticas."),
    (21, 34, "Jocneam con sus ejidos", "Jocneam con sus campos de pastoreo", "archaic-pasture-term", "Ejidos designa los campos de pastoreo que rodeaban las ciudades levíticas."),
    (22, 16, "prevaricáis contra el Dios de Israel", "cometéis infidelidad contra el Dios de Israel", "archaic-covenant-term", "Prevaricar describe una infidelidad al pacto, no una falta administrativa moderna."),
    (22, 20, "prevaricación en el anatema", "infidelidad respecto a lo consagrado", "archaic-covenant-term", "La frase distingue la infidelidad de Acán respecto a lo que estaba consagrado a Jehová."),
    (22, 22, "por prevaricación contra Jehová", "por infidelidad contra Jehová", "archaic-covenant-term", "Prevaricación significa aquí infidelidad al pacto."),
    (22, 23, "tornarnos de en pos de Jehová", "apartarnos de Jehová", "archaic-covenant-phrase", "La construcción significa abandonar el seguimiento de Jehová."),
    (22, 33, "el negocio plugo á los hijos de Israel", "el asunto agradó a los hijos de Israel", "archaic-approval-phrase", "Negocio significa asunto y plugo significa agradó."),
    (23, 8, "á Jehová vuestro Dios os allegaréis", "permaneceréis unidos a Jehová vuestro Dios", "archaic-covenant-verb", "Allegarse expresa permanecer unido y fiel a Jehová."),
    (23, 12, "concertareis con ellas matrimonios", "contrajereis matrimonio con ellas", "archaic-marriage-phrase", "Concertar matrimonios significa contraer matrimonio con las naciones restantes."),
    (23, 14, "reconoced", "sabed", "false-friend", "Reconocer significa aquí saber con certeza, no identificar visualmente."),
    (23, 16, "traspasareis el pacto", "quebrantareis el pacto", "archaic-covenant-verb", "Traspasar el pacto significa quebrantarlo."),
    (24, 2, "es á saber", "es decir", "archaic-explanatory-phrase", "Es a saber introduce una explicación y hoy se expresa como es decir."),
    (24, 3, "trájelo", "lo traje", "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito según el español actual."),
    (24, 3, "díle á Isaac", "le di a Isaac", "archaic-enclitic-order", "Se moderniza el orden del pronombre sin cambiar el don de Isaac."),
    (24, 5, "al modo que lo hice", "conforme a lo que hice", "archaic-comparison-phrase", "Al modo que significa conforme a en este resumen de las obras en Egipto."),
    (24, 9, "levantóse", "se levantó", "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito según el español actual."),
    (24, 15, "escogeos hoy", "escoged hoy", "archaic-imperative", "Se moderniza el imperativo dirigido al pueblo."),
    (24, 21, "No, antes á Jehová serviremos", "No; serviremos a Jehová", "archaic-contrast-phrase", "Antes funciona como contraste, no como referencia temporal."),
]


# In Joshua each of these families has one stable sense. They were checked in
# the complete book, not inferred from their spelling alone.
FAMILIES = {
    "término": ("límite", "archaic-geographic-term", "Término designa un límite territorial en todas sus apariciones restantes en Josué."),
    "términos": ("límites", "archaic-geographic-term", "Términos designa límites territoriales en todas sus apariciones restantes en Josué."),
    "heredad": ("herencia", "archaic-inheritance-term", "Heredad designa la herencia territorial asignada a una tribu o familia."),
    "heredades": ("herencias", "archaic-inheritance-term", "Heredades designa las herencias territoriales de las tribus."),
    "morador": ("habitante", "archaic-inhabitant-term", "Morador significa habitante en la narración y los registros territoriales de Josué."),
    "moradores": ("habitantes", "archaic-inhabitant-term", "Moradores significa habitantes en la narración y los registros territoriales de Josué."),
    "villa": ("ciudad", "archaic-settlement-term", "Villa designa una ciudad o población en las listas territoriales de Josué."),
    "villas": ("ciudades", "archaic-settlement-term", "Villas designa ciudades o poblaciones en las listas territoriales de Josué."),
    "ejido": ("campo de pastoreo", "archaic-pasture-term", "Ejido designa el campo de pastoreo que rodeaba una ciudad levítica."),
    "ejidos": ("campos de pastoreo", "archaic-pasture-term", "Ejidos designa los campos de pastoreo que rodeaban las ciudades levíticas."),
    "ramera": ("prostituta", "archaic-person-term", "Ramera es el término antiguo empleado para describir la ocupación de Rahab."),
}


PENDING = [
    (6, 17, "anatema", "La expresión combina consagración a Jehová y destrucción; una sola palabra moderna puede perder una de esas dos ideas."),
    (7, 1, "anatema", "El relato de Acán usa el término en varios sentidos gramaticales; debe aclararse como unidad y no mediante reemplazo automático."),
    (10, 12, "Sol, detente en Gabaón", "El lenguaje poético y cosmológico debe conservarse; cualquier nota explicativa requiere revisión separada."),
    (15, 2, "lengua del mar", "La imagen geográfica sigue siendo comprensible en contexto y no se cambia sin una cartografía de apoyo."),
]


def verse_map(document):
    return {(c["chapter"], v["verse"]): v["text"] for c in document["chapters"] for v in c["verses"]}


def all_offsets(text, expected):
    pattern = rf"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ]){re.escape(expected)}(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])"
    return [m.start() for m in re.finditer(pattern, text)]


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


def main():
    source = verse_map(json.loads(BOOK_PATH.read_text(encoding="utf-8")))
    layer = json.loads(LAYER_PATH.read_text(encoding="utf-8"))
    occupied = {(v["chapter"], v["verse"]): v.get("edits", []) for v in layer["verses"]}
    entries = []
    spans = {}

    def overlaps(ref, start, end):
        return any(e["startOffset"] < end and start < e["endOffset"] for e in occupied.get(ref, [])) or any(a < end and start < b for a, b in spans.get(ref, []))

    def record(chapter, verse, expected, replacement, category, reason):
        ref = (chapter, verse)
        matches = all_offsets(source[ref], expected) if expected.isalpha() else [m.start() for m in re.finditer(re.escape(expected), source[ref])]
        assert len(matches) == 1, (ref, expected, matches, source[ref])
        start, end = matches[0], matches[0] + len(expected)
        if overlaps(ref, start, end):
            return False
        entries.append({
            "book": "JOS", "chapter": chapter, "verse": verse,
            "expected": expected, "replacement": replacement,
            "category": category, "reason": reason,
            "evidence": [
                {"label": "Control contextual RVR1960", "url": f"https://www.biblegateway.com/passage/?search=Joshua+{chapter}%3A{verse}&version=RVR1960"},
                {"label": "Control contextual NVI", "url": f"https://www.biblegateway.com/passage/?search=Joshua+{chapter}%3A{verse}&version=NVI"},
            ],
        })
        spans.setdefault(ref, []).append((start, end))
        return True

    for item in EXPLICIT:
        record(*item)

    for ref, text in source.items():
        for expected, (replacement, category, reason) in FAMILIES.items():
            for start in all_offsets(text, expected):
                end = start + len(expected)
                if overlaps(ref, start, end):
                    continue
                left, right = unique_phrase(text, start, end)
                phrase = text[left:right]
                replacement_phrase = phrase[:start-left] + replacement + phrase[end-left:]
                record(ref[0], ref[1], phrase, replacement_phrase, category, reason)

    entries.sort(key=lambda e: (e["chapter"], e["verse"], source[(e["chapter"], e["verse"])].index(e["expected"])))
    payload = {
        "format": "shine-reading-2026-editorial-change-set", "schemaVersion": 1,
        "contentVersion": VERSION, "generatedAt": "2026-09-12T05:00:00.000Z",
        "issuedAt": "2026-09-12T05:00:00.000Z", "expiresAt": "2028-09-12T05:00:00.000Z",
        "sourceVersionId": "RV1909", "filterId": "RV1909-LECTURA-2026",
        "changes": entries,
        "pendingReview": [{"book": "JOS", "chapter": c, "verse": v, "term": term, "reason": reason} for c, v, term, reason in PENDING],
    }
    CHANGE_SET.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    pending = [p for p in registry.get("pending", []) if not p.get("id", "").startswith("joshua-v20-")]
    for index, (chapter, verse, term, reason) in enumerate(PENDING, 1):
        pending.append({
            "id": f"joshua-v20-{index}", "status": "pending-review", "scope": "old-testament",
            "term": term, "proposedOptions": ["Mantener con explicación", "Actualizar tras revisión textual"],
            "reason": reason, "references": [{"book": "JOS", "chapter": chapter, "verse": verse}],
            "evidence": [{"label": "Control contextual RVR1960 y NVI", "url": f"https://www.biblegateway.com/passage/?search=Joshua+{chapter}%3A{verse}&version=RVR1960%3BNVI"}],
        })
    registry.update({"updatedAt": "2026-09-12T05:00:00.000Z", "activeChangeSet": "editorial-changes/v20.json", "pending": pending})
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changes": len(entries), "changedVerses": len(spans), "pending": len(PENDING)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
