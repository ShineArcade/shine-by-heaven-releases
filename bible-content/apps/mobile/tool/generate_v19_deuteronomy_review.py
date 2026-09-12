import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK_PATH = ROOT / "apps/mobile/assets/bibles/rv1909/books/DEU.json"
LAYER_PATH = ROOT / "apps/mobile/assets/bible_direction/deuteronomy_reading_2026.rv1909.v1.json"
CHANGE_SET = ROOT / "editorial-changes/v19.json"
REGISTRY = ROOT / "editorial-review/registry.json"
VERSION = 19


# Every entry was reviewed in its complete verse against the local RVR1960 and
# NVI controls.  The controls establish context; the replacement remains an
# independently worded, minimal modernization of RV1909.
CHANGES = [
    (2, 3, "Harto habéis rodeado este monte; volveos al aquilón", "Bastante habéis rodeado este monte; volveos al norte", "archaic-direction", "Aquilón significa norte; harto significa bastante en esta frase de itinerario."),
    (2, 5, "ni aun la holladura de la planta de un pie", "ni siquiera la huella de la planta de un pie", "archaic-land-phrase", "Holladura designa aquí la mínima superficie que puede pisar un pie."),
    (4, 4, "os allegasteis á Jehová", "permanecisteis unidos a Jehová", "archaic-covenant-verb", "Allegarse expresa permanecer unido y fiel a Jehová, no solo acercarse físicamente."),
    (4, 21, "sobre vuestros negocios", "por causa de vosotros", "false-friend", "Negocios se refiere aquí a lo sucedido por causa del pueblo, no a actividades comerciales."),
    (8, 2, "Y acordarte has de", "Y te acordarás de", "archaic-verb-order", "Se moderniza el orden del verbo y el pronombre sin cambiar el mandato de recordar."),
    (11, 25, "sobre la haz de toda la tierra que hollareis", "sobre toda la tierra que pisareis", "archaic-land-phrase", "Haz significa superficie y hollar significa pisar en este recorrido territorial."),
    (12, 30, "no tropieces en pos de ellas", "no caigas en la trampa de seguirlas", "opaque-warning", "La advertencia prohíbe caer en la trampa de imitar a las naciones destruidas."),
    (13, 2, "Y acaeciere la señal ó prodigio", "Y ocurriere la señal o prodigio", "archaic-verb", "Acaecer significa ocurrir; se conserva el modo condicional del pasaje."),
    (13, 2, "Vamos en pos de dioses ajenos, que no conociste, y sirvámosles", "Vamos tras otros dioses que no conociste y sirvámoslos", "archaic-idolatry-phrase", "En pos significa tras; la frase completa mantiene la invitación a servir a otros dioses."),
    (13, 4, "En pos de Jehová vuestro Dios andaréis", "Seguiréis a Jehová vuestro Dios", "archaic-covenant-phrase", "Andar en pos de Jehová significa seguirlo con fidelidad."),
    (13, 13, "Hombres, hijos de impiedad", "Hombres impíos", "archaic-idiom", "Hijos de impiedad es una construcción antigua para describir hombres impíos."),
    (17, 8, "entre sangre y sangre, entre causa y causa, y entre llaga y llaga", "entre una clase de homicidio y otra, una causa legal y otra, o una clase de herida y otra", "opaque-legal-list", "La enumeración distingue tipos difíciles de homicidio, causas legales y lesiones."),
    (18, 22, "no fuere la tal cosa, ni viniere", "no se cumpliere ni aconteciere", "archaic-prophecy-phrase", "La prueba es que lo anunciado no se cumpla ni suceda."),
    (18, 22, "con soberbia la habló", "la habló con presunción", "false-friend", "Soberbia describe aquí la presunción de atribuir a Jehová una palabra no recibida."),
    (19, 3, "Arreglarte has el camino", "Prepararás los caminos", "archaic-verb-order", "La instrucción manda preparar rutas de acceso a las ciudades de refugio."),
    (19, 3, "el término de tu tierra", "el territorio de tu tierra", "archaic-boundary-term", "Término designa el territorio delimitado, no una palabra o plazo."),
    (19, 3, "para que todo homicida se huya allí", "para que todo homicida huya allí", "archaic-grammar", "Se elimina el pronombre antiguo innecesario sin alterar quién busca refugio."),
    (19, 5, "saltó el hierro del cabo", "se desprendió el hierro del mango", "archaic-tool-phrase", "El hierro es la cabeza del hacha que se desprende del mango."),
    (19, 5, "y encontró á su prójimo", "y golpeó a su prójimo", "false-friend", "Encontrar significa alcanzar o golpear en este accidente, no descubrir a la persona."),
    (19, 15, "En el dicho de dos testigos, ó en el dicho de tres testigos consistirá el negocio", "Por el testimonio de dos o tres testigos se establecerá el asunto", "archaic-legal-phrase", "Dicho significa testimonio y negocio significa asunto judicial."),
    (20, 8, "Y tornarán los oficiales á hablar", "Y volverán los oficiales a hablar", "archaic-verb", "Tornar significa volver a hablar en esta secuencia."),
    (21, 12, "ella raerá su cabeza", "ella rapará su cabeza", "archaic-verb", "Raer la cabeza significa raparla."),
    (22, 3, "no podrás retraerte de ello", "no podrás negarle tu ayuda", "opaque-duty-phrase", "La frase prohíbe desentenderse del objeto perdido del hermano."),
    (22, 12, "Hacerte has flecos en los cuatro cabos", "Te harás flecos en las cuatro puntas", "archaic-clothing-phrase", "Se modernizan el orden verbal y cabo como punta del manto."),
    (23, 14, "se vuelva de en pos de ti", "se aparte de ti", "archaic-direction-phrase", "La frase significa que Jehová se aparte del campamento."),
    (24, 3, "el postrer hombre", "el último hombre", "archaic-ordinal", "Postrer significa último en la secuencia de esposos."),
    (24, 4, "después que fué amancillada", "después que quedó contaminada", "archaic-ritual-term", "Amancillada expresa contaminación dentro de esta ley matrimonial."),
    (26, 17, "A Jehová has ensalzado hoy para que te sea por Dios", "Hoy has declarado solemnemente que Jehová es tu Dios", "false-friend-covenant-phrase", "Ensalzar expresa aquí una declaración solemne del pacto, no elevar en rango."),
    (26, 18, "Y Jehová te ha ensalzado hoy para que le seas su peculiar pueblo", "Y Jehová ha declarado hoy que eres su pueblo especial", "false-friend-covenant-phrase", "La respuesta del pacto declara que Israel es el pueblo especial de Jehová."),
    (28, 1, "si oyeres diligente la voz", "si escuchares atentamente la voz", "archaic-listening-phrase", "Oír diligente significa escuchar con atención y obediencia."),
    (28, 9, "Confirmarte ha Jehová", "Te confirmará Jehová", "archaic-verb-order", "Se moderniza el orden del verbo y el pronombre."),
    (29, 26, "inclináronse á ellos", "se inclinaron ante ellos", "archaic-verb-order", "Se moderniza el orden pronominal y la preposición de adoración."),
    (30, 12, "nos lo representará", "nos lo hará oír", "false-friend", "Representar no transmite el sentido del pasaje: la palabra debe hacerse oír para obedecerla."),
    (30, 20, "te allegues á él", "permanezcas unido a él", "archaic-covenant-verb", "Allegarse expresa adhesión perseverante a Jehová."),
    (31, 10, "Y mandóles Moisés", "Y Moisés les mandó", "archaic-enclitic-order", "Se coloca el pronombre antes del verbo según el español actual."),
    (31, 10, "Al cabo del séptimo año", "Al final de cada siete años", "archaic-time-phrase", "La frase señala el cierre de cada ciclo de siete años."),
    (31, 20, "volveránse á dioses ajenos", "se volverán a otros dioses", "archaic-verb-order", "Se moderniza el orden pronominal y ajenos significa otros en este contraste de lealtad."),
    (31, 29, "os aparteréis", "os apartaréis", "source-spelling-correction", "Se corrige la forma verbal defectuosa aparteréis."),
    (31, 29, "en los postreros días", "en los últimos días", "archaic-time-term", "Postreros significa últimos en esta referencia temporal."),
    (32, 23, "Yo allegaré males sobre ellos", "Yo amontonaré males sobre ellos", "false-friend", "Allegar significa acumular o amontonar calamidades en este canto."),
    (32, 41, "mi mano arrebatare el juicio", "mi mano tomare el juicio", "opaque-judgment-phrase", "La mano toma el juicio para ejecutarlo; no lo roba ni lo quita."),
    (32, 41, "yo volveré la venganza á mis enemigos", "yo tomaré venganza de mis enemigos", "archaic-judgment-phrase", "Volver la venganza significa ejecutarla contra los enemigos."),
    (32, 46, "Poned vuestro corazón á todas las palabras", "Guardad en vuestro corazón todas las palabras", "archaic-attention-idiom", "Poner el corazón significa guardar con atención para obedecer y enseñar."),
    (33, 21, "se ha provisto de la parte primera", "escogió para sí la mejor parte", "opaque-inheritance-phrase", "La bendición describe la elección de la mejor porción territorial."),
    (33, 21, "la justicia de Jehová ejecutará, y sus juicios con Israel", "con Israel ejecutó la justicia y los juicios de Jehová", "archaic-grammar", "Se restablece el orden de la cláusula: Gad ejecutó con Israel los justos juicios de Jehová."),
]


ENCLITICS = {
    "díjome": "me dijo", "díjoles": "les dijo", "díjole": "le dijo",
    "escribiólas": "las escribió", "sacóte": "te sacó", "dióme": "me dio",
    "hanse hecho": "se han hecho", "hablóme": "me habló", "dióla": "la dio",
    "aparecióse": "se apareció", "mostróle": "le mostró",
}


PENDING = [
    (23, 18, "precio de perro", "La expresión cultual es discutida y no debe convertirse en una identificación sexual concreta sin una revisión textual especializada."),
    (29, 19, "añadir la embriaguez á la sed", "El modismo hebreo tiene interpretaciones divergentes; se conserva hasta documentar una explicación fiel."),
    (31, 16, "fornicará tras los dioses ajenos", "La metáfora de infidelidad al pacto es deliberada; debe decidirse si se conserva con nota o se aclara sin borrar la imagen."),
    (33, 17, "cuernos de unicornio", "La identificación zoológica sigue debatida; el cambio vigente a búfalo debe revisarse frente a la opción más amplia bóvido salvaje."),
]


def verse_map(document):
    return {(c["chapter"], v["verse"]): v["text"] for c in document["chapters"] for v in c["verses"]}


def offsets(text, expected):
    if expected.isalpha():
        pattern = rf"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ]){re.escape(expected)}(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])"
    else:
        pattern = re.escape(expected)
    return [m.start() for m in re.finditer(pattern, text)]


def main():
    source = verse_map(json.loads(BOOK_PATH.read_text(encoding="utf-8")))
    layer = json.loads(LAYER_PATH.read_text(encoding="utf-8"))
    occupied = {(v["chapter"], v["verse"]): v.get("edits", []) for v in layer["verses"]}
    entries = []

    def add(chapter, verse, expected, replacement, category, reason):
        text = source[(chapter, verse)]
        found = offsets(text, expected)
        assert len(found) == 1, (chapter, verse, expected, text)
        start, end = found[0], found[0] + len(expected)
        assert not any(e["startOffset"] < end and start < e["endOffset"] for e in occupied.get((chapter, verse), [])), (chapter, verse, expected, "overlap")
        entries.append({
            "book": "DEU", "chapter": chapter, "verse": verse,
            "expected": expected, "replacement": replacement,
            "category": category, "reason": reason,
            "evidence": [
                {"label": "Control contextual RVR1960", "url": f"https://www.biblegateway.com/passage/?search=Deuteronomy+{chapter}%3A{verse}&version=RVR1960"},
                {"label": "Control contextual NVI", "url": f"https://www.biblegateway.com/passage/?search=Deuteronomy+{chapter}%3A{verse}&version=NVI"},
            ],
        })

    for item in CHANGES:
        add(*item)
    for expected, replacement in ENCLITICS.items():
        for (chapter, verse), text in source.items():
            if expected not in text:
                continue
            matches = offsets(text, expected)
            if not matches:
                continue
            start, end = matches[0], matches[0] + len(expected)
            if any(e["startOffset"] < end and start < e["endOffset"] for e in occupied.get((chapter, verse), [])):
                continue
            add(chapter, verse, expected, replacement, "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito según el español actual, sin cambiar la acción ni sus participantes.")

    spans = {}
    for entry in entries:
        ref = (entry["chapter"], entry["verse"])
        start = source[ref].index(entry["expected"])
        span = (start, start + len(entry["expected"]), entry["expected"])
        for prior in spans.setdefault(ref, []):
            assert span[0] >= prior[1] or prior[0] >= span[1], (ref, prior, span)
        spans[ref].append(span)

    payload = {
        "format": "shine-reading-2026-editorial-change-set", "schemaVersion": 1,
        "contentVersion": VERSION, "generatedAt": "2026-09-12T00:00:00.000Z",
        "issuedAt": "2026-09-12T00:00:00.000Z", "expiresAt": "2028-09-12T00:00:00.000Z",
        "sourceVersionId": "RV1909", "filterId": "RV1909-LECTURA-2026",
        "changes": sorted(entries, key=lambda e: (e["chapter"], e["verse"], source[(e["chapter"], e["verse"])].index(e["expected"]))),
        "pendingReview": [{"book": "DEU", "chapter": c, "verse": v, "term": t, "reason": r} for c, v, t, r in PENDING],
    }
    CHANGE_SET.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    pending = [p for p in registry.get("pending", []) if not p.get("id", "").startswith("deuteronomy-v19-")]
    for index, (chapter, verse, term, reason) in enumerate(PENDING, 1):
        pending.append({
            "id": f"deuteronomy-v19-{index}", "status": "pending-review", "scope": "old-testament",
            "term": term, "proposedOptions": ["Mantener con nota explicativa", "Actualizar tras revisión textual"],
            "reason": reason, "references": [{"book": "DEU", "chapter": chapter, "verse": verse}],
            "evidence": [{"label": "Control contextual RVR1960 y NVI", "url": f"https://www.biblegateway.com/passage/?search=Deuteronomy+{chapter}%3A{verse}&version=RVR1960%3BNVI"}],
        })
    registry.update({"updatedAt": "2026-09-12T00:00:00.000Z", "activeChangeSet": "editorial-changes/v19.json", "pending": pending})
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changes": len(entries), "changedVerses": len(spans), "pending": len(PENDING)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
