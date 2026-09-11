import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "apps/mobile/assets/bibles/rv1909/books/EXO.json"
LAYER = ROOT / "apps/mobile/assets/bible_direction/exodus_reading_2026.rv1909.v1.json"
REF_ROOT = Path(r"C:\Users\pocos\Documents\Codex\backups\shine-bibles-before-private12-20260831\source\books\EXO")
OUTPUT = Path(r"C:\Users\pocos\Documents\Codex\2026-09-07\realtime-voice-chat\outputs\EXODO_RV_CANDIDATOS_EDITORIALES.md")

TERMS = [
    "aqueste", "aquesta", "aquestos", "empero", "luégo", "presto", "allende",
    "doquiera", "por ventura", "apercibe", "apercibid", "apercibió", "allegó",
    "allegaron", "allegarse", "ayuntó", "ayuntaron", "bastimentos", "vianda",
    "henchir", "henchirá", "henchirán", "corroboró", "corroborados", "raeré",
    "raído", "oprobio", "estrado", "mancebo", "mozo", "moza", "doncella",
    "arquilla", "carrizal", "calafateó", "betún", "abrevó", "abrevaban",
    "congoja", "incircunciso de labios", "agravó su corazón", "mano fuerte",
    "se puso en camino", "se tornó", "tornóse", "volvióse", "púsose", "púsolo",
    "púsole", "díjole", "díjoles", "respondióle", "hablóle", "tomóla", "hízolo",
    "jofaina", "ázimos", "leudado", "haz del desierto", "aparejarán",
    "cogerá para cada un día", "sustentó", "mantenía", "holgó", "holgar",
    "malquistar", "extrañare", "prevaricación", "estatuto", "ordenanza",
    "propiciatorio", "tabernáculo", "efod", "pectoral", "mitra", "calzoncillos",
    "estoraque", "gálbano", "almáciga", "hisopo", "óbolo", "siclo", "codo",
    "talento", "primicias", "libación", "expiación", "holocausto", "oblación",
    "olor suave", "panes de la proposición", "flor de harina", "obra de primor",
    "obra de recamador", "obra de tejedor", "engastes", "corchetes", "aldabas",
    "molduras", "capiteles", "basas", "tenazas", "despabiladeras", "aguamanil",
    "cuerno de aceite", "consagrarás sus manos", "llenarás sus manos",
]

# These terms were read in their Exodus contexts and intentionally retained.
# They name a biblical object, rite, office, unit, or architectural part; replacing
# them everywhere would remove useful precision. The reading UI can explain them
# through a glossary without rewriting the verse.
RETAINED = {
    "tabernáculo", "efod", "pectoral", "capiteles", "codo", "holocausto",
    "engastes", "molduras", "estatuto", "mitra", "expiación", "siclo",
    "talento", "obra de tejedor", "libación", "primicias", "hisopo",
    "ordenanza", "ázimos", "tenazas", "mano fuerte", "gálbano",
}

PENDING_REFS = {
    (3, 19): "mano fuerte: el sujeto de la fuerza en esta cláusula exige revisión textual",
    (30, 34): "gálbano: sustancia antigua específica; conviene una nota antes que sustituir el nombre",
}

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def verse_map(document):
    return {(c["chapter"], v["verse"]): v["text"] for c in document["chapters"] for v in c["verses"]}

def apply_layer(text, patch):
    for edit in sorted(patch.get("edits", []), key=lambda e: e["startOffset"], reverse=True):
        start, end = edit["startOffset"], edit["endOffset"]
        if text[start:end] != edit["expected"]:
            raise RuntimeError(f"desajuste de offset: {edit}")
        text = text[:start] + edit["replacement"] + text[end:]
    return text

source = verse_map(read(SOURCE))
refs = {name: verse_map(read(REF_ROOT / f"{name}.json")) for name in ("RVR1960", "NVI")}
layer = read(LAYER)
patches = {(v["chapter"], v["verse"]): v for v in layer["verses"]}

flags = []
for ref, original in source.items():
    current = apply_layer(original, patches.get(ref, {"edits": []}))
    hits = [term for term in TERMS if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", current, re.I)]
    # Enclitic verb forms are easy to miss in a dictionary and visually impede reading.
    hits += re.findall(r"\b(?:dijo|respondió|habló|puso|tomó|hizo|volvió|sentó|levantó|llegó)(?:le|les|lo|la|los|las|se)\b", current, re.I)
    if hits:
        flags.append((ref, original, current, sorted(set(hits), key=str.casefold)))

counts = Counter(chapter for (chapter, _), *_ in flags)
lines = [
    "# Éxodo RV1909 — candidatos editoriales posteriores a los cambios existentes",
    "",
    "Este archivo es una cola de lectura, no una aprobación automática. Cada caso exige leer el versículo completo y contrastar el sentido.",
    "",
    f"Candidatos: {len(flags)} versículos. Cambios existentes respetados: {sum(len(v['edits']) for v in layer['verses'])}.",
    "",
]
for (chapter, verse), original, current, hits in flags:
    lines += [
        f"## Éxodo {chapter}:{verse}",
        f"- Señales: {', '.join(hits)}",
        f"- RV1909 original: {original}",
        f"- Lectura actual: {current}",
        f"- RVR1960 (contexto): {refs['RVR1960'].get((chapter, verse), '[sin correspondencia]')}",
        f"- NVI (contexto): {refs['NVI'].get((chapter, verse), '[sin correspondencia]')}",
        (
            f"- Decisión editorial: PENDIENTE — {PENDING_REFS[(chapter, verse)]}"
            if (chapter, verse) in PENDING_REFS
            else "- Decisión editorial: CONSERVAR — término preciso; explicar en glosario si el usuario lo necesita"
            if all(hit.casefold() in RETAINED for hit in hits)
            else "- Decisión editorial: REVISAR — la señal todavía no tiene una decisión individual"
        ),
        "",
    ]
OUTPUT.write_text("\n".join(lines), encoding="utf-8")
print(json.dumps({"candidateVerses": len(flags), "byChapter": dict(sorted(counts.items())), "output": str(OUTPUT)}, ensure_ascii=False, indent=2))
