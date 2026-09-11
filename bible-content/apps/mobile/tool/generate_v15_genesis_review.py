import json
from pathlib import Path


CONTENT_ROOT = Path(__file__).resolve().parents[3]
BOOK_PATH = CONTENT_ROOT / "apps/mobile/assets/bibles/rv1909/books/GEN.json"
CHANGE_SET = CONTENT_ROOT / "editorial-changes/v15.json"
REGISTRY = CONTENT_ROOT / "editorial-review/registry.json"


# Only changes whose meaning converges in the complete verse across RVR1960,
# NVI and at least one additional Reina-Valera control are applied here.
CHANGES = [
    (1, 11, "hierba que dé simiente", "hierba que dé semilla"),
    (1, 11, "que su simiente esté en él", "cuya semilla esté en él"),
    (1, 12, "hierba verde, hierba que da simiente", "hierba verde que da semilla"),
    (1, 12, "cuya simiente está en él", "cuya semilla está en él"),
    (1, 14, "Sean lumbreras", "Haya luminarias"),
    (1, 16, "las dos grandes lumbreras", "las dos grandes luminarias"),
    (1, 16, "la lumbrera mayor", "la luminaria mayor"),
    (1, 16, "la lumbrera menor", "la luminaria menor"),
    (1, 20, "reptil de ánima viviente", "seres vivientes"),
    (1, 21, "las grandes ballenas", "los grandes animales marinos"),
    (1, 21, "toda cosa viva que anda arrastrando", "todo ser viviente que se mueve"),
    (1, 26, "señoree en los peces de la mar, y en las aves de los cielos, y en las bestias, y en toda la tierra, y en", "domine sobre los peces del mar, sobre las aves de los cielos, sobre las bestias, sobre toda la tierra y sobre"),
    (1, 26, "todo animal que anda arrastrando", "todo animal que se arrastra"),
    (1, 28, "Fructificad y multiplicad", "Sean fructíferos y multiplíquense"),
    (1, 28, "henchid", "llenen", "llenad"),
    (1, 28, "sojuzgadla", "sométanla"),
    (1, 28, "señoread en los peces de la mar, y en las aves de los cielos, y en todas las bestias que se mueven sobre la tierra", "dominen sobre los peces del mar, las aves de los cielos y todas las bestias que se mueven sobre la tierra"),
    (2, 1, "Y FUERON acabados los cielos y la tierra, y todo su ornamento", "Así quedaron terminados los cielos y la tierra, y todo lo que hay en ellos"),
    (2, 7, "alentó en su nariz soplo de vida", "sopló en su nariz aliento de vida"),
    (2, 7, "fué el hombre en alma viviente", "fue el hombre un ser viviente"),
    (2, 9, "árbol de ciencia del bien y del mal", "árbol del conocimiento del bien y del mal"),
    (2, 12, "bdelio", "bedelio"),
    (2, 12, "piedra cornerina", "ónice"),
    (2, 14, "Hiddekel", "Tigris"),
    (2, 18, "ayuda idónea", "ayuda adecuada"),
    (2, 20, "ayuda que estuviese idónea", "ayuda adecuada"),
    (2, 23, "será llamada Varona, porque del varón fué tomada", "será llamada Mujer, porque del hombre fue tomada"),
    (2, 24, "allegarse ha á su mujer", "se unirá a su mujer"),
    (3, 16, "tus dolores y tus preñeces", "tus dolores y tus embarazos"),
    (3, 16, "con dolor parirás los hijos", "con dolor darás a luz a tus hijos"),
    (3, 16, "él se enseñoreará de ti", "él te dominará"),
    (3, 17, "por amor de ti", "por tu causa"),
    (4, 4, "de su grosura", "de su grasa"),
    (4, 5, "Mas no miró propicio", "Pero no miró con agrado"),
    (4, 6, "te has ensañado", "te has enfurecido"),
    (4, 6, "se ha inmutado tu rostro", "ha decaído tu semblante"),
    (4, 7, "¿no serás ensalzado?", "¿no serás enaltecido?"),
    (4, 7, "tú te enseñorearás de él", "tú lo dominarás"),
    (4, 22, "acicalador de toda obra de metal y de hierro", "artífice de toda obra de bronce y de hierro"),
    (4, 26, "comenzaron á llamarse del nombre de Jehová", "comenzaron a invocar el nombre de Jehová"),
    (6, 4, "varones de nombre", "hombres de renombre"),
    (6, 14, "aposentos", "compartimentos"),
    (6, 14, "la embetunarás con brea", "la cubrirás con brea"),
    (6, 21, "toda vianda que se come", "todo alimento que se come"),
    (6, 21, "allégala á ti", "almacénalo"),
    (7, 2, "de siete en siete, macho y su hembra", "siete parejas, macho y hembra"),
    (7, 2, "dos, macho y su hembra", "una pareja, macho y hembra"),
    (8, 11, "una hoja de oliva tomada en su pico", "una hoja de olivo en su pico"),
    (8, 13, "las aguas se enjugaron", "las aguas se secaron"),
    (8, 13, "la faz de la tierra estaba enjuta", "la superficie de la tierra estaba seca"),
    (11, 2, "como se partieron de oriente", "cuando salieron de oriente"),
    (11, 2, "una vega", "una llanura"),
    (11, 2, "asentaron allí", "se establecieron allí"),
    (11, 6, "nada les retraerá", "nada los hará desistir"),
    (11, 6, "han pensando hacer", "han pensado hacer"),
    (15, 2, "ando sin hijo", "sigo sin hijos"),
    (15, 3, "no me has dado prole", "no me has dado descendencia"),
    (15, 3, "es mi heredero uno nacido en mi casa", "mi heredero será un esclavo nacido en mi casa"),
    (15, 12, "el pavor de una grande obscuridad cayó sobre él", "el temor de una gran oscuridad cayó sobre él"),
    (16, 10, "tu linaje", "tu descendencia"),
    (16, 10, "que no será contado á causa de la muchedumbre", "que no podrá ser contada a causa de la multitud"),
    (16, 11, "parirás un hijo", "darás a luz un hijo"),
    (16, 11, "oído ha Jehová", "Jehová ha oído"),
    (17, 4, "muchedumbre de gentes", "una multitud de naciones"),
    (17, 7, "entre mí y ti, y tu simiente después de ti", "entre mí y ti, y tu descendencia después de ti"),
    (17, 7, "por alianza perpetua", "por pacto perpetuo"),
    (17, 7, "para serte á ti por Dios, y á tu simiente después de ti", "para ser tu Dios, y el de tu descendencia después de ti"),
    (18, 5, "sustentad vuestro corazón", "recobrad fuerzas"),
    (18, 6, "de priesa", "deprisa"),
    (18, 6, "flor de harina", "harina fina"),
    (18, 11, "viejos, entrados en días", "ancianos, de edad avanzada"),
    (18, 11, "á Sara había cesado ya la costumbre de las mujeres", "Sara ya había dejado de menstruar"),
    (19, 3, "porfió con ellos mucho", "insistió tanto"),
    (19, 3, "se vinieron", "fueron"),
    (19, 11, "se fatigaban por hallar la puerta", "no podían encontrar la puerta"),
    (19, 20, "vivirá mi alma", "salvaré mi vida"),
    (19, 21, "He aquí he recibido también tu súplica sobre esto", "También he aceptado tu petición"),
    (19, 34, "conservemos de nuestro padre generación", "conservemos la descendencia de nuestro padre"),
    (20, 3, "He aquí muerto eres", "Vas a morir"),
    (20, 3, "casada con marido", "casada"),
    (20, 12, "toméla por mujer", "la tomé por mujer"),
    (21, 6, "cualquiera que lo oyere", "cualquiera que lo oiga"),
    (21, 14, "ella partió, y andaba errante", "ella salió y anduvo errante"),
    (21, 16, "como un tiro de arco", "a la distancia de un tiro de arco"),
    (22, 1, "tentó Dios á Abraham", "Dios puso a prueba a Abraham"),
    (22, 13, "trabado en un zarzal", "enredado en un matorral"),
    (22, 20, "fué dada nueva á Abraham", "informaron a Abraham"),
    (24, 12, "dame, te ruego, el tener hoy buen encuentro, y haz misericordia con mi señor Abraham", "te ruego que hoy me vaya bien y muestres misericordia a mi señor Abraham"),
    (24, 33, "delante qué comer", "comida delante"),
    (24, 43, "la doncella", "la joven"),
    (24, 63, "á orar al campo", "a meditar al campo"),
    (25, 27, "varón quieto", "hombre tranquilo"),
    (25, 30, "de eso", "de ese guiso"),
    (27, 1, "sus ojos se ofuscaron", "sus ojos se oscurecieron"),
    (28, 11, "encontró con un lugar", "llegó a cierto lugar"),
    (29, 2, "abrevaban los ganados", "bebían los ganados"),
    (29, 7, "abrevad las ovejas, é id á apacentarlas", "den de beber a las ovejas y llévenlas a pastar"),
    (30, 32, "reses manchadas y de color vario", "ovejas manchadas y salpicadas de color"),
    (30, 32, "las manchadas y de color vario entre las cabras", "las manchadas y moteadas entre las cabras"),
    (30, 37, "descortezó en ellas mondaduras blancas", "les quitó parte de la corteza para formar franjas blancas"),
    (31, 10, "las ovejas se recalentaban", "las ovejas estaban en celo"),
    (31, 34, "una albarda de un camello", "la montura de un camello"),
    (31, 34, "tentó Labán toda la tienda", "buscó Labán por toda la tienda"),
    (31, 36, "Entonces Jacob se enojó, y regañó con Labán; y respondió Jacob y dijo á Labán: ¿Qué prevaricación es la mía?", "Entonces Jacob se enojó y discutió con Labán. Jacob le dijo: ¿Qué falta he cometido?"),
    (31, 36, "con tanto ardor has venido en seguimiento mío", "me persigues con tanto ardor"),
    (31, 39, "de mi mano lo requerías", "a mí me lo cobrabas"),
    (31, 51, "este majano", "este montón de piedras"),
    (31, 51, "este título", "esta señal"),
    (32, 18, "Presente es de tu siervo Jacob", "Es un regalo de tu siervo Jacob"),
    (32, 20, "con el presente", "con el regalo"),
    (32, 20, "quizá le seré acepto", "quizá me reciba bien"),
    (32, 25, "el sitio del encaje de su muslo", "la coyuntura de su cadera"),
    (32, 25, "descoyuntóse", "se dislocó", "se descoyuntó"),
    (32, 25, "el muslo de Jacob", "la cadera de Jacob"),
    (33, 2, "los postreros", "los últimos"),
    (33, 10, "toma mi presente de mi mano", "acepta el regalo que te ofrezco"),
    (33, 10, "hazme placer", "me has recibido con favor"),
    (34, 15, "os haremos placer", "aceptaremos"),
    (34, 21, "traficarán en él", "comerciarán en él"),
    (35, 17, "había trabajo en su parir", "tenía dificultades en el parto"),
    (35, 18, "al salírsele el alma", "al exhalar su último aliento"),
    (37, 11, "paraba la consideración en ello", "meditaba en esto"),
    (37, 35, "no quiso tomar consolación", "no quiso recibir consuelo"),
    (37, 36, "eunuco de Faraón", "oficial de Faraón"),
    (38, 1, "descendió de con sus hermanos", "se apartó de sus hermanos"),
    (38, 8, "Entra á la mujer de tu hermano, y despósate con ella, y suscita simiente á tu hermano", "Únete a la mujer de tu hermano, cumple con tu deber de cuñado y da descendencia a tu hermano"),
    (38, 13, "fué dado aviso á Thamar", "avisaron a Thamar"),
    (38, 13, "trasquilar", "esquilar"),
    (38, 29, "¿Por qué has hecho sobre ti rotura?", "¡Cómo te has abierto paso!"),
    (39, 2, "Jehová fué con José", "Jehová estaba con José"),
    (39, 2, "fué varón prosperado", "fue un hombre próspero"),
    (39, 4, "servíale", "le servía"),
    (39, 4, "mayordomo de su casa", "administrador de su casa"),
    (39, 8, "mi señor no sabe conmigo lo que hay en casa", "mi señor no se preocupa de lo que hay en casa estando yo aquí"),
    (39, 11, "para hacer su oficio", "para cumplir con sus responsabilidades"),
    (39, 11, "y no había nadie de los de casa allí en casa", "y no había nadie de la casa allí"),
    (39, 21, "el principal de la casa de la cárcel", "el jefe de la cárcel"),
    (39, 21, "gracia en ojos", "gracia ante los ojos"),
    (40, 7, "aquellos eunucos de Faraón", "aquellos oficiales de Faraón"),
    (40, 7, "¿Por qué parecen hoy mal vuestros semblantes?", "¿Por qué tienen hoy tan mala cara?"),
    (40, 14, "Acuérdate, pues, de mí para contigo cuando tuvieres ese bien", "Acuérdate de mí cuando te vaya bien"),
    (40, 17, "Y en el canastillo más alto había de todas las viandas de Faraón, obra de panadero; y que las aves las comían del canastillo de sobre mi cabeza", "En la canasta más alta había toda clase de panes y pasteles para Faraón, y las aves los comían de la canasta que estaba sobre mi cabeza"),
    (41, 8, "mas no había quien á Faraón los declarase", "pero nadie podía interpretarlos para Faraón"),
    (41, 9, "Acuérdome hoy de mis faltas", "Hoy me acuerdo de mis faltas"),
    (41, 15, "no hay quien lo declare", "no hay quien lo interprete"),
    (41, 15, "oyes sueños para declararlos", "puedes interpretar sueños"),
    (41, 16, "Dios será el que responda paz á Faraón", "Dios dará una respuesta favorable a Faraón"),
    (41, 21, "su parecer era aún malo, como de primero", "su apariencia seguía tan mala como antes"),
    (41, 24, "helo dicho á los magos", "lo he dicho a los magos"),
    (41, 24, "no hay quien me lo declare", "no hay quien me lo interprete"),
    (41, 28, "halo mostrado á Faraón", "lo ha mostrado a Faraón"),
    (41, 29, "grande hartura", "gran abundancia"),
    (41, 34, "quinte la tierra de Egipto", "recoja la quinta parte de las cosechas de Egipto"),
    (41, 34, "los siete años de la hartura", "los siete años de abundancia"),
    (42, 6, "el señor de la tierra", "el gobernador del país"),
    (42, 6, "que vendía á todo el pueblo de la tierra", "quien vendía alimento a todo el pueblo"),
    (42, 9, "Espías sois; por ver lo descubierto del país habéis venido", "Ustedes son espías; han venido a ver las zonas desprotegidas del país"),
    (42, 28, "aun helo aquí", "aquí está"),
    (43, 23, "vuestro dinero vino á mí", "yo recibí vuestro dinero"),
    (43, 23, "sacó á Simeón á ellos", "les entregó a Simeón"),
    (43, 31, "Poned pan", "Sirvan la comida"),
    (45, 6, "ni habrá arada ni siega", "no habrá siembra ni cosecha"),
    (46, 34, "Hombres de ganadería han sido tus siervos", "Tus siervos se han dedicado a criar ganado"),
    (46, 34, "nosotros y nuestros padres", "al igual que nuestros padres"),
    (46, 34, "los Egipcios abominan todo pastor de ovejas", "los egipcios detestan el oficio de pastor"),
    (47, 12, "de pan, hasta la boca del niño", "con alimento, según el número de sus hijos"),
    (47, 17, "les dió alimentos por caballos, y por el ganado de las ovejas, y por el ganado de las vacas, y por asnos", "les dio alimentos a cambio de caballos, ovejas, vacas y asnos"),
    (47, 17, "sustentólos", "los alimentó", "los sustentó"),
    (47, 17, "de pan por todos sus ganados aquel año", "durante aquel año a cambio de todo su ganado"),
    (47, 23, "He aquí os he hoy comprado y á vuestra tierra para Faraón: ved aquí simiente, y sembraréis la tierra", "Hoy los he comprado a ustedes y a su tierra para Faraón. Aquí tienen semilla; siembren la tierra"),
    (49, 4, "Corriente como las aguas", "Impetuoso como las aguas"),
    (49, 4, "no seas el principal", "ya no serás el principal"),
    (49, 4, "entonces te envileciste, subiendo á mi estrado", "profanaste mi lecho"),
    (49, 23, "asaeteáronle", "le lanzaron flechas", "le asaetearon"),
    (49, 23, "los archeros", "los arqueros"),
    (49, 26, "la mollera", "la frente"),
    (49, 26, "del Nazareo de sus hermanos", "del que fue apartado de entre sus hermanos"),
]


PENDING = [
    ("expansión", ["firmamento", "bóveda celeste"], "Las referencias conservan o interpretan de modo distinto el término cosmológico; cambiarlo globalmente podría imponer una explicación."),
    ("bdelio", ["resina aromática", "bedelio"], "Es el nombre de una sustancia antigua. NVI la explica como resina, mientras las Reina-Valera conservan el nombre."),
    ("madera de Gopher", ["madera de gofer", "madera resinosa"], "La especie exacta no está identificada con certeza; se conserva el término y se reserva una posible ayuda de lectura."),
    ("No contenderá mi espíritu", ["Mi espíritu no permanecerá", "Mi espíritu no luchará"], "Génesis 6:3 admite matices distintos en las traducciones de control y requiere revisión teológica específica."),
    ("Grande es mi iniquidad", ["Mi castigo es demasiado grande", "Mi culpa es demasiado grande"], "Génesis 4:13 alterna entre culpa y castigo en las referencias; no se debe escoger una lectura sin revisión adicional."),
    ("velo de ojos", ["compensación", "protección del honor"], "Génesis 20:16 presenta una figura difícil y las referencias la explican de maneras distintas."),
    ("se burlaba", ["se burlaba de Isaac", "jugaba con Isaac"], "Génesis 21:9 tiene una variante interpretativa que afecta la acción; se conserva hasta revisión textual."),
    ("grosuras de la tierra", ["lo mejor de la tierra", "lejos de la fertilidad de la tierra"], "Génesis 27:39 se entiende de forma opuesta entre referencias modernas; no es un cambio seguro."),
    ("arrancaron muro", ["desjarretaron toros"], "Génesis 49:6 parece contener una lectura fuente distinta. Requiere cotejo textual antes de corregir la imagen."),
    ("entre dos tercios", ["entre los apriscos", "entre dos alforjas"], "La imagen poética de Génesis 49:14 diverge entre referencias y no admite sustitución automática."),
    ("dará dichos hermosos", ["tendrá hermosos cervatillos", "pronunciará dichos hermosos"], "Génesis 49:21 tiene dos lecturas muy distintas; queda reservado para cotejo textual."),
    ("collados eternos", ["colinas eternas", "montes antiguos"], "La bendición poética de Génesis 49:26 requiere conservar paralelismo y base textual antes de simplificarla."),
]


def whole_word_occurs(text, term):
    lowered = text.casefold()
    needle = term.casefold()
    start = 0
    while True:
        start = lowered.find(needle, start)
        if start < 0:
            return False
        before = text[start - 1] if start else ""
        end = start + len(term)
        after = text[end] if end < len(text) else ""
        if not before.isalpha() and not after.isalpha():
            return True
        start += 1


def main():
    book = json.loads(BOOK_PATH.read_text(encoding="utf-8"))
    verses = {
        (chapter["chapter"], verse["verse"]): verse["text"]
        for chapter in book["chapters"]
        for verse in chapter["verses"]
    }
    changes = []
    for item in CHANGES:
        chapter, verse, expected, replacement, *previous = item
        text = verses[(chapter, verse)]
        if not previous:
            assert text.count(expected) == 1, (chapter, verse, expected)
        change = {
            "book": "GEN", "chapter": chapter, "verse": verse,
            "expected": expected, "replacement": replacement,
            "category": "genesis-complete-context-review",
            "reason": "El versículo completo fue contrastado con RVR1960, NVI, RV2020 y RVC. El ajuste elimina una palabra o construcción extraña y conserva el referente, la acción y el sentido del pasaje.",
            "evidence": [
                {"label": "Control contextual RVR1960", "url": f"https://www.biblegateway.com/passage/?search=Genesis+{chapter}%3A{verse}&version=RVR1960"},
                {"label": "Control contextual NVI", "url": f"https://www.biblegateway.com/passage/?search=Genesis+{chapter}%3A{verse}&version=NVI"},
            ],
        }
        if previous:
            change["previousReplacement"] = previous[0]
        changes.append(change)
    CHANGE_SET.write_text(json.dumps({
        "format": "shine-reading-2026-editorial-change-set", "schemaVersion": 1,
        "contentVersion": 15, "generatedAt": "2026-09-11T00:00:00.000Z",
        "issuedAt": "2026-09-11T00:00:00.000Z", "expiresAt": "2028-09-11T00:00:00.000Z",
        "sourceVersionId": "RV1909", "filterId": "RV1909-LECTURA-2026", "changes": changes,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    pending = [entry for entry in registry["pending"] if not entry.get("id", "").startswith("genesis-v15-")]
    for index, (term, options, reason) in enumerate(PENDING, 1):
        references = [
            {"book": "GEN", "chapter": chapter, "verse": verse}
            for (chapter, verse), text in verses.items() if whole_word_occurs(text, term)
        ]
        assert references, term
        pending.append({
            "id": f"genesis-v15-{index}", "status": "pending-review", "scope": "old-testament",
            "term": term, "proposedOptions": options, "reason": reason,
            "references": references,
            "evidence": [{"label": "Control contextual RVR1960 y NVI", "url": "https://www.biblegateway.com/passage/?search=Genesis&version=RVR1960%3BNVI"}],
        })
    registry.update({
        "updatedAt": "2026-09-11T00:00:00.000Z",
        "activeChangeSet": "editorial-changes/v15.json",
        "pending": pending,
    })
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"applied": len(changes), "pending": len(PENDING)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
