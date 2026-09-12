import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "apps/mobile/assets/bibles/rv1909/books"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction"
CHANGE_SET = ROOT / "editorial-changes/v25.json"
REGISTRY = ROOT / "editorial-review/registry.json"
PACKAGE_SOURCE = DIRECTION / "reading_2026.package-source.json"
VERSION = 25
STAMP = "2026-09-13T00:15:00.000Z"

BOOK_NAMES = {
    "LUK": "Lucas", "JHN": "Juan", "ACT": "Hechos", "ROM": "Romanos",
    "1CO": "1 Corintios", "2CO": "2 Corintios", "GAL": "Gálatas",
    "EPH": "Efesios", "PHP": "Filipenses", "COL": "Colosenses",
    "1TH": "1 Tesalonicenses", "2TH": "2 Tesalonicenses",
    "1TI": "1 Timoteo", "2TI": "2 Timoteo", "TIT": "Tito",
    "PHM": "Filemón", "HEB": "Hebreos", "JAS": "Santiago",
    "1PE": "1 Pedro", "2PE": "2 Pedro", "1JN": "1 Juan",
    "2JN": "2 Juan", "3JN": "3 Juan", "JUD": "Judas", "REV": "Apocalipsis",
}


def rule(book, chapter, verse, expected, replacement, category, reason, previous=None, supersede=False):
    value = {
        "book": book, "chapter": chapter, "verse": verse,
        "expected": expected, "replacement": replacement,
        "category": category, "reason": reason,
    }
    if previous is not None:
        value["previousReplacement"] = previous
    if supersede:
        value["supersedeOverlaps"] = True
    return value


def same(refs, expected, replacement, category, reason):
    return [rule(book, chapter, verse, expected, replacement, category, reason)
            for book, chapter, verse in refs]


RULES = []

# Favoritismo: se ajusta la frase completa cuando la preposición cambiaría.
RULES += [
    rule("1PE", 1, 17, "sin acepción de personas juzga", "juzga sin favoritismo", "false-friend-partiality", "La frase afirma que el Padre juzga sin favoritismo."),
    rule("ACT", 10, 34, "Dios no hace acepción de personas", "Dios no muestra favoritismo", "false-friend-partiality", "Pedro reconoce que Dios no favorece a una persona sobre otra."),
    rule("COL", 3, 25, "no hay acepción de personas", "no hay favoritismo", "false-friend-partiality", "El juicio no favorece a una persona por su posición."),
    rule("EPH", 6, 9, "no hay acepción de personas", "no hay favoritismo", "false-friend-partiality", "El Señor no favorece a amos sobre siervos."),
    rule("JAS", 2, 1, "en acepción de personas", "con favoritismo", "false-friend-partiality", "La fe en Jesucristo no debe practicarse mostrando favoritismo."),
    rule("JAS", 2, 9, "hacéis acepción de personas", "mostráis favoritismo", "false-friend-partiality", "La acción condenada es tratar a unas personas con preferencia sobre otras."),
    rule("ROM", 2, 11, "no hay acepción de personas para con Dios", "Dios no muestra favoritismo", "false-friend-partiality", "El juicio de Dios no favorece a una persona sobre otra."),
]

RULES += [
    rule("2PE", 3, 4, "su advenimiento", "su venida", "archaic-coming-term", "Advenimiento significa la venida prometida; el referente se conserva."),
    rule("2TH", 2, 9, "cuyo advenimiento", "cuya venida", "archaic-coming-term", "Advenimiento significa la venida del inicuo; el referente y la concordancia se conservan."),
]

RULES += same(
    [("1CO", 11, 4), ("1CO", 11, 5), ("1TI", 3, 7), ("ACT", 5, 41),
     ], "afrenta", "deshonra",
    "archaic-dishonor-term", "Afrenta significa deshonra en este contexto.")
RULES += [
    rule("2CO", 11, 21, "cuanto á la afrenta", "para vergüenza mía", "archaic-shame-phrase", "Pablo habla irónicamente de la vergüenza de parecer débil."),
    rule("HEB", 10, 29, "hiciere afrenta al Espíritu", "insultare al Espíritu", "archaic-insult-phrase", "Hacer afrenta al Espíritu significa insultarlo gravemente."),
    rule("HEB", 11, 26, "el vituperio de Cristo", "la deshonra por Cristo", "archaic-dishonor-term", "Vituperio significa la deshonra sufrida por causa de Cristo.", "la afrenta por Cristo"),
    rule("HEB", 13, 13, "llevando su vituperio", "llevando su deshonra", "archaic-dishonor-term", "Vituperio significa compartir la deshonra sufrida por Jesús.", "llevando su afrenta"),
    rule("LUK", 1, 25, "quitar mi afrenta", "quitar mi vergüenza", "archaic-shame-phrase", "Elisabet habla de la vergüenza social que había soportado."),
]

RULES += [
    rule("2PE", 1, 13, "incitaros con amonestación", "despertaros con este recordatorio", "contextual-reminder-phrase", "Pedro declara que seguirá recordándoles estas verdades."),
    rule("EPH", 6, 4, "disciplina y amonestación del Señor", "disciplina e instrucción del Señor", "contextual-instruction-phrase", "El contexto trata de criar e instruir a los hijos en el Señor."),
    rule("TIT", 3, 10, "después de una y otra amonestación", "después de una primera y segunda advertencia", "contextual-warning-phrase", "La instrucción exige dos advertencias antes de apartarse del que causa divisiones."),
]

RULES += same(
    [("COL", 3, 12), ("GAL", 5, 22)], "benignidad", "amabilidad",
    "archaic-kindness-term", "Amabilidad conserva la cualidad bondadosa y evita confundirla con la bondad que aparece a su lado.")
RULES += same(
    [("ROM", 2, 4)], "benignidad", "bondad",
    "archaic-kindness-term", "En las dos menciones del versículo, benignidad describe la bondad de Dios que guía al arrepentimiento.")

RULES += same(
    [("ACT", 4, 15), ("ACT", 5, 21), ("ACT", 5, 27), ("ACT", 5, 34),
     ("ACT", 5, 41), ("ACT", 6, 12), ("ACT", 6, 15), ("ACT", 22, 30),
     ("ACT", 23, 1), ("ACT", 23, 6), ("ACT", 23, 15), ("ACT", 23, 20),
     ("ACT", 23, 28), ("ACT", 24, 20), ("LUK", 22, 66)],
    "concilio", "Consejo", "historical-council-term",
    "Concilio designa al Consejo judío reunido para deliberar o juzgar; no se convierte en una institución cristiana posterior.")

# Concupiscencia: cada referencia conserva su objeto y fuerza moral.
RULES += [
    rule("1JN", 2, 16, "la concupiscencia de la carne", "los deseos de la carne", "contextual-sinful-desire", "El pasaje enumera deseos mundanos procedentes de la carne."),
    rule("1JN", 2, 16, "la concupiscencia de los ojos", "los deseos de los ojos", "contextual-sinful-desire", "El pasaje enumera deseos despertados por lo que se ve."),
    rule("1JN", 2, 17, "su concupiscencia", "sus deseos", "contextual-worldly-desire", "La frase resume los deseos del mundo que pasan."),
    rule("1TH", 4, 5, "afecto de concupiscencia", "pasiones desordenadas", "contextual-sexual-desire", "El contexto contrasta la santidad sexual con pasiones desordenadas."),
    rule("2PE", 1, 4, "corrupción que está en el mundo por concupiscencia", "corrupción que está en el mundo por los malos deseos", "contextual-sinful-desire", "La corrupción del mundo se atribuye a los malos deseos."),
    rule("2PE", 2, 10, "concupiscencia é inmundicia", "deseos impuros", "contextual-impure-desire", "La frase une el deseo de la carne con su impureza sin duplicar dos términos modernos equivalentes."),
    rule("COL", 3, 5, "mala concupiscencia", "malos deseos", "contextual-sinful-desire", "La lista ordena hacer morir los malos deseos."),
    rule("COL", 3, 5, "molicie", "pasiones desordenadas", "archaic-passion-term", "Molicie designa aquí pasiones desordenadas dentro de una lista moral, no comodidad física."),
    rule("GAL", 5, 16, "la concupiscencia de la carne", "los deseos de la carne", "contextual-sinful-desire", "La frase contrapone andar en el Espíritu con satisfacer los deseos de la carne."),
    rule("JAS", 1, 14, "su propia concupiscencia", "su propio mal deseo", "contextual-tempting-desire", "El deseo propio atrae y seduce a la persona en la tentación."),
    rule("JAS", 1, 15, "la concupiscencia", "el mal deseo", "contextual-tempting-desire", "La metáfora presenta al mal deseo concibiendo y dando a luz el pecado."),
    rule("ROM", 7, 7, "la concupiscencia", "la codicia", "contextual-coveting-term", "El mandamiento citado es No codiciarás; aquí el sustantivo es codicia."),
    rule("ROM", 7, 8, "toda concupiscencia", "toda clase de codicia", "contextual-coveting-term", "El pecado produce toda clase de codicia aprovechando el mandamiento."),
    rule("1PE", 4, 2, "las concupiscencias de los hombres", "los deseos humanos", "contextual-human-desires", "El contraste es vivir según los deseos humanos o según la voluntad de Dios."),
    rule("1PE", 4, 3, "en concupiscencias", "en malos deseos", "contextual-sinful-desire", "La lista describe conductas pasadas gobernadas por malos deseos."),
    rule("2PE", 2, 18, "ceban con las concupiscencias de la carne", "seducen con los deseos de la carne", "contextual-sinful-desire", "La seducción opera mediante los deseos de la carne y el verbo deja claro que se trata de atraer al error."),
    rule("2PE", 3, 3, "sus propias concupiscencias", "sus propios deseos", "contextual-self-directed-desires", "Los burladores viven según sus propios deseos."),
    rule("2TI", 3, 6, "diversas concupiscencias", "diversos malos deseos", "contextual-sinful-desire", "Las mujeres descritas son arrastradas por diversos malos deseos."),
    rule("2TI", 4, 3, "sus concupiscencias", "sus propios deseos", "contextual-self-directed-desires", "La gente reúne maestros según sus propios deseos."),
    rule("GAL", 5, 24, "los afectos y concupiscencias", "las pasiones y malos deseos", "contextual-sinful-desire", "La pareja expresa pasiones y malos deseos asociados con la carne y conserva la concordancia."),
    rule("JAS", 4, 1, "vuestras concupiscencias, las cuales", "vuestros malos deseos, los cuales", "contextual-conflicting-desires", "Los malos deseos combaten dentro de los miembros y producen conflictos; sustantivo y relativo mantienen la concordancia."),
    rule("ROM", 1, 24, "las concupiscencias de sus corazones", "los malos deseos de sus corazones", "contextual-sinful-desire", "El pasaje atribuye la impureza a los malos deseos del corazón."),
    rule("ROM", 1, 27, "se encendieron en sus concupiscencias los unos con los otros", "se encendieron en pasiones los unos por los otros", "contextual-sexual-desire", "La frase describe pasiones mutuas y conserva sus participantes."),
    rule("ROM", 6, 12, "sus concupiscencias", "sus malos deseos", "contextual-sinful-desire", "El mandato prohíbe obedecer los malos deseos del cuerpo mortal."),
    rule("TIT", 3, 3, "concupiscencias y deleites diversos", "diversos malos deseos y placeres", "contextual-sinful-desire", "La lista recuerda la esclavitud pasada a diversos malos deseos y placeres."),
]

RULES += [
    rule("1CO", 9, 17, "la dispensación me ha sido encargada", "se me ha encargado esta responsabilidad", "contextual-entrusted-responsibility", "Pablo afirma que recibió la responsabilidad de anunciar el evangelio."),
    rule("COL", 1, 25, "según la dispensación de Dios que me fué dada", "según el encargo que Dios me dio", "contextual-divine-commission", "Pablo describe el encargo recibido de Dios para servir a la iglesia."),
    rule("EPH", 1, 10, "en la dispensación del cumplimiento de los tiempos", "en su plan para el cumplimiento de los tiempos", "contextual-divine-plan", "La frase describe el plan de Dios para reunir todas las cosas en Cristo."),
    rule("EPH", 3, 2, "la dispensación de la gracia de Dios que me ha sido dada", "la administración de la gracia de Dios que me fue dada", "contextual-stewardship", "Pablo habla de la responsabilidad de administrar la gracia recibida para los gentiles."),
    rule("EPH", 3, 9, "cuál sea la dispensación del misterio", "cómo se realiza el plan del misterio", "contextual-divine-plan", "La frase explica cómo Dios realiza el plan del misterio antes escondido."),
]

RULES += [
    rule("1CO", 14, 33, "Dios no es Dios de disensión", "Dios no es Dios de confusión", "contextual-disorder-term", "El contraste con paz y el orden de la reunión señalan confusión o desorden."),
    rule("ACT", 15, 2, "suscitada una disensión y contienda no pequeña á Pablo y á Bernabé contra ellos", "al surgir una fuerte discusión y controversia entre ellos y Pablo y Bernabé", "contextual-dispute-phrase", "Pablo y Bernabé sostuvieron una fuerte controversia con ellos; la frase completa conserva los participantes y la subordinación."),
    rule("ACT", 23, 7, "disensión entre", "división entre", "contextual-division-term", "La declaración de Pablo divide a fariseos y saduceos."),
    rule("ACT", 23, 10, "grande disensión", "gran disputa", "contextual-dispute-term", "La disputa se vuelve tan violenta que el tribuno teme por Pablo."),
    rule("JHN", 7, 43, "disensión entre la gente", "división entre la gente", "contextual-division-term", "La multitud queda dividida acerca de Jesús."),
    rule("JHN", 9, 16, "disensión entre ellos", "división entre ellos", "contextual-division-term", "Las opiniones de los fariseos quedan divididas."),
    rule("JHN", 10, 19, "disensión entre los Judíos", "división entre los Judíos", "contextual-division-term", "Las palabras de Jesús vuelven a dividir a sus oyentes."),
    rule("LUK", 12, 51, "mas disensión", "sino división", "contextual-division-term", "Jesús anuncia división aun dentro de las familias.", "sino disensión"),
]
RULES += same(
    [("1CO", 1, 10), ("1CO", 3, 3), ("1CO", 11, 18), ("2CO", 12, 20),
     ("GAL", 5, 20), ("ROM", 16, 17)], "disensiones", "divisiones",
    "contextual-division-term", "Disensiones describe divisiones dentro de la comunidad.")

RULES += [
    rule("LUK", 15, 32, "hacer fiesta y holgar nos, porque este tu hermano muerto era, y ha revivido; habíase perdido, y es hallado", "celebrar y alegrarnos, porque este hermano tuyo estaba muerto y ha vuelto a vivir; estaba perdido y ha sido hallado", "archaic-celebration-phrase", "La familia debía celebrar y alegrarse por el regreso del hermano; la frase completa conserva los dos contrastes."),
    rule("PHP", 1, 18, "en esto me huelgo, y aun me holgaré", "en esto me alegro, y seguiré alegrándome", "archaic-rejoicing-phrase", "Pablo se alegra de que Cristo sea anunciado y afirma que seguirá haciéndolo."),
    rule("PHP", 2, 17, "derramado en libación", "derramado como ofrenda", "historical-offering-image", "Pablo conserva la imagen de ser derramado, aclarando que la libación es una ofrenda."),
]

RULES += same(
    [("2CO", 6, 6), ("ROM", 2, 4)], "longanimidad", "tolerancia",
    "archaic-forbearance-term", "Tolerancia conserva la paciencia prolongada y no duplica la palabra paciencia presente en Romanos.")
RULES += [
    rule("COL", 3, 8, "maledicencia", "calumnias", "contextual-slander-term", "La lista prohíbe palabras que dañan la reputación de otros."),
    rule("EPH", 4, 31, "maledicencia", "insultos", "contextual-insult-term", "La lista ordena quitar los gritos y los insultos junto con la malicia."),
    rule("ROM", 3, 14, "maledicencia", "maldiciones", "contextual-cursing-term", "La boca descrita está llena de maldiciones y amargura."),
    rule("1TI", 3, 6, "No un neófito", "No debe ser un recién convertido", "archaic-new-convert-term", "Neófito designa a una persona recién convertida que todavía no debe ocupar ese cargo."),
]
RULES += same(
    [("1CO", 16, 20), ("1TH", 5, 26), ("2CO", 13, 12), ("ROM", 16, 16)],
    "ósculo santo", "beso santo", "archaic-greeting-term", "Ósculo significa beso en este saludo entre creyentes.")

RULES += [
    rule("1CO", 16, 21, "La salutación", "El saludo", "archaic-greeting-term", "Pablo identifica el saludo escrito de su propia mano."),
    rule("COL", 4, 18, "La salutación", "El saludo", "archaic-greeting-term", "Pablo identifica el saludo escrito de su propia mano."),
    rule("LUK", 1, 29, "qué salutación fuese ésta", "qué clase de saludo era éste", "archaic-greeting-phrase", "María se pregunta qué clase de saludo había recibido."),
    rule("LUK", 1, 41, "la salutación de María", "el saludo de María", "archaic-greeting-term", "Elisabet oye el saludo de María."),
    rule("LUK", 1, 44, "la voz de tu salutación", "la voz de tu saludo", "archaic-greeting-term", "Elisabet oye la voz del saludo de María."),
    rule("LUK", 11, 43, "las salutaciones", "los saludos", "archaic-greeting-term", "Los fariseos aman recibir saludos públicos en las plazas."),
    rule("LUK", 20, 46, "las salutaciones", "los saludos", "archaic-greeting-term", "Los escribas aman recibir saludos públicos en las plazas."),
]

RULES += [
    rule("ACT", 19, 40, "argüidos de sedición", "acusados de causar disturbios", "historical-riot-term", "Las autoridades podían acusar a la ciudad de causar los disturbios de ese día."),
    rule("ACT", 21, 38, "levantaste una sedición", "provocaste una revuelta", "historical-uprising-term", "El tribuno pregunta por la revuelta armada atribuida al egipcio."),
    rule("LUK", 23, 19, "una sedición hecha en la ciudad, y una muerte", "una revuelta ocurrida en la ciudad y un homicidio", "historical-uprising-term", "Barrabás estaba preso por una revuelta y un homicidio."),
    rule("LUK", 23, 25, "por sedición y una muerte", "por una revuelta y un homicidio", "historical-uprising-term", "La frase identifica los delitos por los que Barrabás estaba preso."),
]

RULES += [
    rule("1TI", 3, 2, "solícito, templado, compuesto", "prudente, templado, respetable", "contextual-leadership-qualities", "La lista describe prudencia, dominio propio y conducta respetable del obispo."),
    rule("2CO", 8, 17, "estando también muy solícito", "estando también muy dispuesto", "contextual-eagerness-term", "Tito parte voluntariamente porque estaba muy dispuesto a servir."),
    rule("COL", 4, 12, "siempre solícito por vosotros en oraciones", "siempre orando con empeño por vosotros", "contextual-prayer-concern", "Epafras se esfuerza constantemente en oración por ellos."),
    rule("GAL", 2, 10, "fuí también solícito en hacer", "también me esforcé por hacer", "contextual-diligence-phrase", "Pablo afirma que se esforzó por recordar a los pobres."),
    rule("EPH", 4, 3, "Solícitos á guardar", "Esforzaos por mantener", "contextual-diligence-phrase", "El mandato exige esforzarse por mantener la unidad del Espíritu."),
    rule("LUK", 12, 11, "no estéis solícitos", "no os preocupéis", "contextual-anxiety-term", "Jesús ordena no preocuparse de antemano por la defensa."),
    rule("PHP", 4, 10, "estabais solícitos", "estabais preocupados", "contextual-pastoral-concern", "Los filipenses mantenían su preocupación por Pablo aunque les faltaba oportunidad de ayudar."),
    rule("LUK", 18, 32, "será escarnecido", "será objeto de burlas", "archaic-mockery-term", "Jesús anuncia que se burlarán de él antes de maltratarlo y escupirlo."),
    rule("LUK", 18, 32, "á las gentes", "a los gentiles", "grammar-nationality-article", "El artículo masculino plural concuerda con gentiles y se elimina la tilde arcaica de la preposición.", supersede=True),
    rule("2CO", 1, 17, "usé quizá de liviandad", "actué con ligereza", "archaic-fickleness-term", "Pablo pregunta si hizo sus planes con ligereza o falta de seriedad."),
    rule("2PE", 2, 20, "sus postrimerías les son hechas peores que los principios", "su condición final es peor que la del principio", "archaic-final-condition-phrase", "La frase compara la condición final con la inicial después de volver a la corrupción."),
    rule("2TI", 3, 8, "réprobos acerca de la fe", "descalificados en cuanto a la fe", "false-friend-disqualified-term", "El juicio afirma que estos hombres no superan la prueba en cuanto a la fe."),
    rule("JHN", 8, 9, "redargüidos de la conciencia", "acusados por su conciencia", "archaic-conscience-phrase", "La conciencia los acusa y hace que se retiren uno por uno."),
    rule("JHN", 11, 47, "juntaron concilio", "reunieron el Consejo", "historical-council-term", "Los principales sacerdotes y fariseos reunieron al Consejo para deliberar."),
]

RULES += [
    rule("HEB", 11, 16, "les había aparejado ciudad", "les había preparado una ciudad", "archaic-prepared-term", "Aparejado significa preparado; la forma actual incluye el artículo requerido."),
    rule("LUK", 2, 31, "aparejado", "preparado", "archaic-prepared-term", "Aparejado significa preparado en esta referencia."),
    rule("REV", 12, 6, "lugar aparejado de Dios", "lugar preparado por Dios", "archaic-prepared-term", "Aparejado significa preparado y la preposición identifica a Dios como quien lo preparó."),
]
RULES += [
    rule("ACT", 6, 5, "prosélito de Antioquía", "convertido al judaísmo de Antioquía", "historical-convert-term", "Prosélito identifica a una persona convertida al judaísmo."),
    rule("ACT", 13, 43, "religiosos prosélitos", "convertidos devotos al judaísmo", "historical-convert-term", "La frase identifica a gentiles devotos convertidos al judaísmo."),
]
RULES += same(
    [("LUK", 3, 12), ("LUK", 5, 30), ("LUK", 7, 29),
     ("LUK", 7, 34), ("LUK", 15, 1)],
    "publicanos", "recaudadores de impuestos", "historical-tax-role", "Publicanos eran recaudadores de impuestos en el sistema romano.")
RULES += [
    rule("LUK", 5, 29, "mucha compañía de publicanos", "muchos recaudadores de impuestos", "historical-tax-role", "La casa de Leví tenía muchos recaudadores de impuestos sentados a la mesa."),
    rule("LUK", 19, 2, "principal de los publicanos", "jefe de los recaudadores de impuestos", "historical-tax-role", "Zaqueo dirigía a otros recaudadores de impuestos."),
]

RULES += [
    rule("1CO", 6, 13, "Las viandas para el vientre, y el vientre para las viandas", "Los alimentos para el estómago, y el estómago para los alimentos", "archaic-food-phrase", "Viandas significa alimentos y la frase conserva el paralelismo."),
    rule("1CO", 6, 13, "empero y á él y á ellas deshará Dios", "pero Dios destruirá tanto al uno como a los otros", "archaic-destruction-clause", "Dios pondrá fin tanto al estómago como a los alimentos; se conservan los dos referentes.", supersede=True),
    rule("1CO", 8, 4, "las viandas que son sacrificadas á los ídolos", "los alimentos sacrificados a los ídolos", "archaic-food-phrase", "La discusión trata de alimentos ofrecidos a los ídolos."),
    rule("1TI", 4, 3, "abstenerse de las viandas que Dios crió para que con hacimiento de gracias participasen de ellas los fieles, y los que han conocido la verdad", "abstenerse de los alimentos que Dios creó para que los fieles y los que han conocido la verdad los reciban con acción de gracias", "archaic-food-term", "La prohibición descrita afecta alimentos creados por Dios; la frase completa mantiene la concordancia de los pronombres.", supersede=True),
    rule("LUK", 9, 12, "hallen viandas", "encuentren comida", "archaic-food-term", "Los discípulos buscan que la multitud encuentre comida y alojamiento."),
    rule("LUK", 9, 13, "comprar viandas", "comprar comida", "archaic-food-term", "La frase habla de comprar comida para la multitud."),
    rule("1CO", 3, 2, "y no vianda", "y no alimento sólido", "contextual-solid-food-term", "El contraste es entre leche y alimento sólido."),
    rule("1CO", 8, 8, "la vianda", "el alimento", "archaic-food-term", "La frase afirma que el alimento no acerca a nadie a Dios."),
    rule("1CO", 10, 3, "la misma vianda espiritual", "el mismo alimento espiritual", "contextual-spiritual-food", "La imagen describe el mismo alimento espiritual compartido."),
    rule("HEB", 5, 14, "la vianda firme", "el alimento sólido", "contextual-solid-food-term", "El contraste es entre leche y alimento sólido para los maduros."),
]

RULES += [
    rule("EPH", 1, 14, "Que es las arras de nuestra herencia", "Que es la garantía de nuestra herencia", "historical-pledge-term", "El Espíritu es presentado como garantía de la herencia futura; se corrige además la concordancia."),
]
RULES += [
    rule("1CO", 4, 21, "con caridad", "con amor", "false-friend-love-term", "Caridad significa aquí amor, no únicamente ayuda material."),
    rule("1CO", 13, 1, "y no tengo caridad", "y no tuviese amor", "false-friend-love-term", "Caridad significa amor y el verbo conserva la forma condicional iniciada por si hablase."),
    rule("1CO", 13, 2, "y no tengo caridad", "y no tuviese amor", "false-friend-love-term", "Caridad significa amor y el verbo conserva la forma condicional iniciada por si tuviese.", supersede=True),
    rule("1CO", 14, 1, "SEGUID la caridad", "SEGUID el amor", "false-friend-love-term", "Caridad significa aquí amor, no únicamente ayuda material."),
    rule("1CO", 16, 14, "con caridad", "con amor", "false-friend-love-term", "Caridad significa aquí amor, no únicamente ayuda material."),
    rule("1TI", 6, 11, "la caridad", "el amor", "false-friend-love-term", "Caridad significa aquí amor, no únicamente ayuda material."),
    rule("2CO", 13, 11, "de caridad", "de amor", "false-friend-love-term", "Caridad significa aquí amor, no únicamente ayuda material."),
    rule("GAL", 5, 6, "por la caridad", "por el amor", "false-friend-love-term", "Caridad significa aquí amor, no únicamente ayuda material."),
]

RULES += [
    rule("1CO", 1, 5, "toda ciencia", "todo conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento y el determinante conserva el género."),
    rule("1CO", 8, 1, "tenemos ciencia", "tenemos conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento en este contexto bíblico."),
    rule("1CO", 8, 1, "La ciencia", "El conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento y el artículo conserva el género."),
    rule("1CO", 8, 7, "esta ciencia", "este conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento y el demostrativo conserva el género."),
    rule("1CO", 8, 10, "tienes ciencia", "tienes conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento en este contexto bíblico."),
    rule("1CO", 8, 11, "tu ciencia", "tu conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento en este contexto bíblico."),
    rule("1CO", 12, 8, "palabra de ciencia", "palabra de conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento en este don del Espíritu."),
    rule("1CO", 13, 2, "toda ciencia", "todo conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento y el determinante conserva el género."),
    rule("1CO", 13, 8, "la ciencia ha de ser quitada", "el conocimiento será quitado", "false-friend-knowledge-term", "Ciencia significa conocimiento y toda la frase conserva género y voz verbal."),
    rule("1CO", 14, 6, "con ciencia", "con conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento en este contexto bíblico."),
    rule("1PE", 3, 7, "según ciencia", "con conocimiento", "false-friend-knowledge-term", "El esposo debe convivir con su esposa con conocimiento y consideración."),
    rule("1TI", 6, 20, "de la falsamente llamada ciencia", "de lo que falsamente se llama conocimiento", "false-friend-knowledge-term", "La frase denuncia un conocimiento falsamente llamado así y conserva la concordancia."),
    rule("2CO", 6, 6, "en ciencia", "en conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento en este contexto bíblico."),
    rule("2CO", 8, 7, "en ciencia", "en conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento en este contexto bíblico."),
    rule("2CO", 10, 5, "la ciencia de Dios", "el conocimiento de Dios", "false-friend-knowledge-term", "Ciencia significa conocimiento y el artículo conserva el género."),
    rule("2CO", 11, 6, "aunque soy basto en la palabra, empero no en la ciencia", "aunque no sea elocuente al hablar, no me falta conocimiento", "false-friend-speech-and-knowledge-phrase", "Basto describe falta de elocuencia y ciencia significa conocimiento; la frase conserva el contraste.", supersede=True),
    rule("2PE", 1, 5, "mostrad en vuestra fe virtud, y en la virtud ciencia", "añadid a vuestra fe virtud, y a la virtud conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento y la frase conserva la secuencia de cualidades."),
    rule("LUK", 11, 52, "la llave de la ciencia", "la llave del conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento y la contracción conserva la gramática."),
    rule("PHP", 1, 9, "en ciencia y en todo conocimiento", "en conocimiento y en todo discernimiento", "contextual-knowledge-discernment", "La oración distingue conocimiento y discernimiento para orientar el amor."),
    rule("ROM", 2, 20, "la forma de la ciencia", "la forma del conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento y la contracción conserva la gramática."),
    rule("ROM", 10, 2, "conforme á ciencia", "conforme al conocimiento", "false-friend-knowledge-term", "Ciencia significa conocimiento y la contracción conserva la gramática."),
    rule("ROM", 11, 33, "de la ciencia de Dios", "del conocimiento de Dios", "false-friend-knowledge-term", "Ciencia significa conocimiento y la contracción conserva la gramática."),
]

RULES += [
    rule("1PE", 1, 15, "toda conversación", "toda vuestra conducta", "false-friend-conduct-term", "Conversación significa la manera completa de vivir."),
    rule("1PE", 1, 17, "conversad en temor", "vivid con temor", "false-friend-conduct-term", "Conversar significa aquí conducir la vida, no hablar; la exhortación es vivir con temor reverente."),
    rule("1PE", 1, 18, "vuestra vana conversación", "vuestra vana manera de vivir", "false-friend-conduct-term", "La frase se refiere al modo de vida heredado."),
    rule("1PE", 2, 12, "vuestra conversación honesta", "vuestra conducta honorable", "false-friend-conduct-term", "La conducta honorable queda visible entre los gentiles."),
    rule("1PE", 3, 1, "la conversación de sus mujeres", "la conducta de sus mujeres", "false-friend-conduct-term", "El testimonio es la conducta de las esposas, no una charla."),
    rule("1PE", 3, 2, "vuestra casta conversación", "vuestra conducta pura", "false-friend-conduct-term", "El pasaje describe una conducta pura y respetuosa."),
    rule("1PE", 3, 16, "vuestra buena conversación", "vuestra buena conducta", "false-friend-conduct-term", "Los acusadores observan la buena conducta en Cristo."),
    rule("JAS", 3, 13, "por buena conversación sus obras", "sus obras mediante una buena conducta", "false-friend-conduct-phrase", "La sabiduría debe mostrarse mediante obras y buena conducta."),
    rule("1CO", 15, 33, "las malas conversaciones", "las malas compañías", "false-friend-company-term", "La máxima advierte que las malas compañías corrompen las buenas costumbres."),
    rule("2PE", 3, 11, "santas y pías conversaciones", "conductas santas y piadosas", "false-friend-conduct-term", "Pedro pregunta qué clase de conducta santa y piadosa deben llevar."),
]

RULES += [
    rule("2CO", 8, 4, "la comunicación del servicio", "la participación en el servicio", "false-friend-sharing-term", "Las iglesias piden participar en el servicio a los santos."),
    rule("HEB", 13, 16, "Y de hacer bien y de la comunicación no os olvidéis", "Y no olvidéis hacer el bien y compartir", "false-friend-sharing-phrase", "La exhortación manda hacer el bien y compartir con otros; la coordinación completa se conserva."),
    rule("PHM", 1, 6, "la comunicación de tu fe", "la participación de tu fe", "contextual-faith-sharing", "La frase describe la participación activa que nace de la fe de Filemón."),
]

RULES += [
    rule("1PE", 5, 7, "toda vuestra solicitud", "toda vuestra ansiedad", "contextual-anxiety-term", "La exhortación invita a echar toda ansiedad sobre Dios."),
    rule("2CO", 7, 11, "cuánta solicitud ha obrado en vosotros", "cuánto empeño ha producido en vosotros", "contextual-eagerness-term", "La tristeza según Dios produjo gran empeño por corregir el asunto."),
    rule("2CO", 7, 12, "manifiesta nuestra solicitud que tenemos por vosotros", "manifiesto nuestro interés por vosotros", "contextual-pastoral-concern", "La carta hizo visible el interés pastoral por ellos y conserva la concordancia."),
    rule("2CO", 8, 7, "toda solicitud", "todo empeño", "contextual-eagerness-term", "Pablo elogia su empeño junto con fe, palabra y conocimiento."),
    rule("2CO", 8, 16, "la misma solicitud por vosotros", "el mismo interés por vosotros", "contextual-pastoral-concern", "Dios puso en Tito el mismo interés por los corintios."),
    rule("2CO", 11, 28, "la solicitud de todas las iglesias", "la preocupación por todas las iglesias", "contextual-pastoral-concern", "Pablo describe su preocupación diaria por todas las iglesias."),
    rule("ACT", 17, 11, "con toda solicitud", "con toda disposición", "contextual-readiness-term", "Los bereanos recibieron la palabra con disposición y la comprobaron."),
    rule("COL", 2, 1, "cuán gran solicitud tengo", "cuánto me esfuerzo", "contextual-striving-term", "Pablo describe su gran esfuerzo por creyentes que no lo habían visto."),
    rule("HEB", 6, 11, "muestre la misma solicitud", "muestre el mismo empeño", "contextual-diligence-term", "La exhortación pide mantener el mismo empeño hasta el fin."),
    rule("JUD", 1, 3, "por la gran solicitud que tenía", "por el gran empeño que tenía", "contextual-eagerness-term", "Judas tenía gran empeño en escribir sobre la salvación común."),
    rule("JUD", 1, 3, "la común salud", "la salvación que compartimos", "false-friend-salvation-term", "Salud significa salvación en esta frase y el texto afirma que los creyentes la comparten."),
    rule("ROM", 12, 8, "el que preside, con solicitud", "el que dirige, con dedicación", "contextual-leadership-diligence", "Quien dirige debe hacerlo con dedicación."),
]

RULES += [
    rule("1JN", 3, 17, "Mas el que tuviere bienes de este mundo, y viere á su hermano tener necesidad, y le cerrare sus entrañas", "Pero el que tiene bienes de este mundo, ve a su hermano pasar necesidad y le cierra su corazón", "historical-compassion-image", "Cerrar las entrañas significa cerrar el corazón y negar compasión al necesitado; la condición completa mantiene una sola persona verbal.", supersede=True),
    rule("2CO", 6, 12, "No estáis estrechos en nosotros, mas estáis estrechos en", "No os limitamos nosotros, sino que estáis limitados por", "historical-affection-image", "La limitación no procede de Pablo sino del afecto restringido de los corintios.", supersede=True),
    rule("2CO", 6, 12, "vuestras propias entrañas", "vuestro propio afecto", "historical-affection-image", "Entrañas significa aquí el afecto interior de los corintios."),
    rule("2CO", 7, 15, "sus entrañas son más abundantes", "su afecto es aún mayor", "historical-affection-image", "Tito siente un afecto aún mayor al recordar su obediencia."),
    rule("COL", 3, 12, "entrañas de misericordia", "profunda compasión", "historical-compassion-image", "La frase ordena vestirse de profunda compasión."),
    rule("LUK", 1, 78, "Por las entrañas de misericordia de nuestro Dios, con que nos visitó de lo alto el Oriente", "Por la profunda misericordia de nuestro Dios, el Sol naciente nos visitó desde lo alto", "historical-compassion-image", "La frase expresa la profunda misericordia de Dios y conserva la imagen mesiánica de la luz que nace desde lo alto."),
    rule("PHM", 1, 7, "recreadas las entrañas de los santos", "reanimados los corazones de los santos", "historical-encouragement-image", "El amor de Filemón había reanimado interiormente a los santos."),
    rule("PHM", 1, 12, "recíbele como á mis entrañas", "recíbelo como a mi propio corazón", "historical-affection-image", "Pablo envía a Onésimo como alguien que representa su propio corazón."),
    rule("PHM", 1, 20, "recrea mis entrañas", "reanima mi corazón", "historical-encouragement-image", "Pablo pide que Filemón reanime su corazón en el Señor."),
    rule("PHP", 1, 8, "en las entrañas de Jesucristo", "con el profundo afecto de Jesucristo", "historical-affection-image", "Pablo expresa un afecto profundo que procede de Cristo."),
    rule("PHP", 2, 1, "si algunas entrañas y misericordias", "si algún afecto y compasión", "historical-affection-image", "La pareja describe afecto y compasión entre los creyentes y conserva la concordancia."),
    rule("1PE", 1, 22, "amaos unos á otros entrañablemente", "amaos unos a otros profundamente", "archaic-depth-adverb", "El mandato pide un amor profundo y sincero entre creyentes."),
    rule("1PE", 1, 22, "vuestra almas", "vuestras almas", "grammar-number-agreement", "El posesivo debe concordar en plural con almas."),
    rule("ACT", 18, 5, "estaba constreñido por la palabra", "se dedicaba por completo a la palabra", "archaic-impelled-term", "Pablo se dedicaba por completo a anunciar la palabra y testificar acerca de Jesús."),
    rule("COL", 1, 25, "en orden á vosotros", "para vuestro beneficio", "archaic-benefit-phrase", "El encargo de Pablo fue recibido para beneficio de la iglesia."),
    rule("EPH", 3, 9, "crió todas las cosas", "creó todas las cosas", "false-friend-create-verb", "Criar significa aquí crear; la forma actual evita confundirlo con educar o alimentar."),
    rule("2CO", 11, 6, "mas en todo somos ya del todo manifiestos á vosotros", "pero en todo os lo hemos demostrado claramente", "archaic-demonstration-phrase", "Pablo afirma que su conocimiento y conducta han quedado claros ante los corintios.", supersede=True),
    rule("2CO", 11, 21, "como si nosotros hubiésemos sido flacos", "como si nosotros hubiésemos sido débiles", "archaic-weakness-term", "Flacos significa débiles en la comparación irónica de Pablo."),
    rule("2CO", 11, 28, "Sin otras cosas además, lo que sobre mí se agolpa cada día", "Además de otras cosas, me agobia cada día", "archaic-daily-pressure-phrase", "Pablo describe la presión diaria que acompaña su preocupación por las iglesias."),
    rule("2TI", 3, 6, "se entran por las casas, y llevan cautivas las mujercillas", "se introducen en las casas y cautivan a mujeres vulnerables", "archaic-exploitation-phrase", "La frase describe a falsos maestros que se introducen en hogares y explotan a mujeres vulnerables."),
    rule("PHP", 2, 17, "me gozo y congratulo por todos vosotros", "me alegro y comparto mi alegría con todos vosotros", "archaic-shared-rejoicing", "Pablo se alegra y comparte esa alegría con todos ellos."),
    rule("PHP", 2, 20, "Porque á ninguno tengo tan unánime, y que con sincera afición esté solícito por vosotros", "Porque no tengo a nadie que comparta mi sentir y se preocupe sinceramente por vosotros", "archaic-like-minded-concern", "Pablo no tiene a nadie tan afín como Timoteo para interesarse sinceramente por ellos."),
]

RULES += [
    rule("ACT", 13, 45, "visto el gentío", "al ver la multitud", "archaic-crowd-term", "Gentío significa la multitud reunida; la frase completa evita conservar un participio con género antiguo."),
    rule("ACT", 14, 14, "se lanzaron al gentío", "se lanzaron hacia la multitud", "archaic-crowd-term", "Los apóstoles corrieron hacia la multitud para detener el sacrificio."),
]

RULES += [
    rule("TIT", 3, 10, "Rehusa hombre hereje", "Rechaza al que causa divisiones", "false-friend-divisive-person", "La instrucción se refiere a una persona que persiste en causar divisiones después de ser advertida."),
]

# Verbos y frases que en 1909 no significan lo que hoy sugiere su forma.
RULES += [
    rule("ACT", 11, 26, "conversaron todo un año allí con la iglesia", "se reunieron allí con la iglesia durante todo un año", "false-friend-conduct-verb", "Conversar significa aquí reunirse y convivir con la iglesia, no únicamente hablar."),
    rule("ACT", 23, 1, "he conversado delante de Dios", "he vivido delante de Dios", "false-friend-conduct-verb", "Conversar significa aquí vivir o conducirse ante Dios."),
    rule("2CO", 1, 12, "hemos conversado en el mundo", "nos hemos conducido en el mundo", "false-friend-conduct-verb", "Conversar significa aquí conducirse en la vida."),
    rule("PHP", 1, 27, "Solamente que converséis como es digno", "Solamente comportaos de una manera digna", "false-friend-conduct-verb", "La exhortación se refiere a la manera de vivir digna del evangelio."),
    rule("1TI", 3, 15, "cómo te conviene conversar en la casa de Dios", "cómo debes comportarte en la casa de Dios", "false-friend-conduct-verb", "Conversar significa aquí comportarse dentro de la comunidad de Dios."),
    rule("HEB", 13, 18, "deseando conversar bien en todo", "deseando conducirnos bien en todo", "false-friend-conduct-verb", "Conversar significa aquí conducirse correctamente."),
    rule("1PE", 4, 3, "cuando conversábamos", "cuando vivíamos", "false-friend-conduct-verb", "Conversar significa aquí vivir según la conducta descrita."),
    rule("2PE", 2, 18, "los que conversan en error", "los que viven en el error", "false-friend-conduct-verb", "Conversar significa aquí vivir en el error, no hablar con alguien."),

    rule("LUK", 2, 10, "os doy nuevas de gran gozo", "os anuncio buenas noticias de gran gozo", "archaic-news-phrase", "El ángel anuncia buenas noticias que producen gran gozo."),
    rule("LUK", 7, 18, "sus discípulos dieron á Juan las nuevas de todas estas cosas", "sus discípulos informaron a Juan de todas estas cosas", "archaic-report-phrase", "Los discípulos informaron a Juan de lo ocurrido."),
    rule("LUK", 24, 9, "dieron nuevas de todas estas cosas", "contaron todas estas cosas", "archaic-report-phrase", "Las mujeres contaron a los once lo ocurrido en el sepulcro."),

    rule("ACT", 6, 5, "Y plugo el parecer á toda la multitud", "La propuesta agradó a toda la multitud", "archaic-pleasing-phrase", "La propuesta presentada por los apóstoles agradó a toda la comunidad."),
    rule("GAL", 1, 15, "cuando plugo á Dios", "cuando Dios quiso", "archaic-pleasing-phrase", "La frase expresa la decisión soberana de Dios."),
    rule("REV", 17, 17, "ejecutar lo que le plugo", "ejecutar su propósito", "archaic-purpose-phrase", "Dios puso en sus corazones ejecutar su propósito."),
    rule("LUK", 23, 10, "acusándole con gran porfía", "acusándolo con gran insistencia", "archaic-insistence-term", "Los líderes acusaban a Jesús con gran insistencia."),
    rule("PHP", 1, 15, "por envidia y porfía", "por envidia y rivalidad", "archaic-rivalry-term", "Algunos predicaban a Cristo movidos por rivalidad."),
    rule("ACT", 19, 32, "la concurrencia estaba confusa", "la asamblea estaba confusa", "archaic-assembly-term", "Concurrencia designa a la asamblea reunida en el teatro."),
    rule("ACT", 19, 40, "este concurso", "esta reunión", "archaic-gathering-term", "Concurso designa la reunión pública de aquel día."),
    rule("ACT", 19, 40, "despidió la concurrencia", "despidió la asamblea", "archaic-assembly-term", "Concurrencia designa a la asamblea reunida."),
    rule("ACT", 24, 12, "haciendo concurso de multitud", "reuniendo multitudes", "archaic-gathering-phrase", "La acusación niega que Pablo estuviera reuniendo multitudes."),

    rule("LUK", 19, 31, "el Señor lo ha menester", "el Señor lo necesita", "archaic-need-phrase", "Haber menester significa necesitar."),
    rule("LUK", 24, 7, "Es menester", "Es necesario", "archaic-necessity-term", "Ser menester significa ser necesario."),
    rule("ACT", 9, 16, "cuánto le sea menester que padezca", "cuánto tendrá que padecer", "archaic-necessity-phrase", "La frase anuncia cuánto tendrá que sufrir Pablo por el nombre de Jesús."),
    rule("ACT", 19, 21, "me será menester ver también á Roma", "también debo ver Roma", "archaic-necessity-phrase", "Pablo expresa que también debe visitar Roma."),
    rule("1CO", 5, 10, "os sería menester salir del mundo", "tendríais que salir del mundo", "archaic-necessity-phrase", "Haber menester significa tener que hacer algo."),
    rule("HEB", 2, 1, "es menester", "es necesario", "archaic-necessity-term", "Ser menester significa ser necesario."),
    rule("HEB", 11, 6, "es menester", "es necesario", "archaic-necessity-term", "Ser menester significa ser necesario."),

    rule("LUK", 8, 13, "que á tiempo creen", "que creen por algún tiempo", "false-friend-temporary-phrase", "La semilla sobre la piedra representa a quienes creen durante un tiempo y luego se apartan."),
    rule("ACT", 5, 34, "doctor de la ley", "maestro de la ley", "false-friend-law-teacher", "Doctor significa maestro experto en la ley en este contexto."),
    rule("ACT", 21, 38, "hombres salteadores", "sicarios", "historical-assassin-term", "El grupo armado identificado por el tribuno era conocido como los sicarios."),
    rule("ACT", 23, 6, "la una parte era de Saduceos, y la otra de Fariseos", "una parte era de saduceos y la otra de fariseos", "archaic-group-phrase", "La frase distingue los dos grupos presentes en el Consejo."),
    rule("HEB", 10, 29, "el que hollare al Hijo de Dios", "el que pisotee al Hijo de Dios", "archaic-trample-verb", "Hollar significa pisotear; se conserva la imagen de desprecio grave."),
    rule("JAS", 1, 14, "es atraído, y cebado", "es atraído y seducido", "archaic-entice-phrase", "Cebar significa seducir o atraer mediante el deseo."),
    rule("JAS", 2, 9, "sois reconvenidos de la ley", "la ley os declara culpables", "archaic-conviction-phrase", "La ley declara culpables de transgresión a quienes muestran favoritismo."),
    rule("PHP", 4, 10, "ha reflorecido vuestro cuidado de mí", "habéis renovado vuestro interés por mí", "archaic-renewed-concern", "Los filipenses renovaron la expresión de su interés por Pablo."),
]

# Flaco and flaqueza have the older sense of weak and weakness here. Each
# reference is handled separately to preserve its exact grammatical role.
RULES += [
    rule("1CO", 1, 25, "lo flaco de Dios", "la debilidad de Dios", "false-friend-weakness", "Flaco means weakness in the rhetorical contrast between God and human beings."),
    rule("1CO", 1, 27, "lo flaco del mundo", "lo débil del mundo", "false-friend-weakness", "Flaco means weak, not thin, in the contrast with what is strong."),
    rule("1CO", 8, 10, "aquel que es flaco", "aquel que es débil", "false-friend-weakness", "The passage describes someone whose conscience is weak."),
    rule("1CO", 8, 11, "hermano flaco", "hermano débil", "false-friend-weakness", "Flaco describes the brother's weakness in this matter of conscience."),
    rule("1CO", 9, 22, "á los flacos flaco", "a los débiles, débil", "false-friend-weakness", "Paul says that he became weak with the weak; the punctuation clarifies the relationship.", supersede=True),
    rule("2CO", 12, 10, "cuando soy flaco", "cuando soy débil", "false-friend-weakness", "The explicit contrast is between weakness and power."),
    rule("2CO", 13, 3, "no es flaco", "no es débil", "false-friend-weakness", "Flaco means weak in contrast with powerful."),
    rule("ROM", 14, 1, "al flaco en la fe", "al débil en la fe", "false-friend-weakness", "The exhortation receives the believer who is weak in faith."),
    rule("1CO", 8, 7, "siendo flaca", "siendo débil", "false-friend-weakness", "The conscience is weak, not physically thin."),
    rule("1CO", 8, 12, "su flaca conciencia", "su débil conciencia", "false-friend-weakness", "The phrase describes a weak conscience."),
    rule("2CO", 10, 10, "presencia corporal flaca", "presencia física débil", "false-friend-weakness", "The accusation contrasts a weak physical presence with strong letters."),
    rule("1CO", 4, 10, "nosotros flacos", "nosotros débiles", "false-friend-weakness", "Flacos means weak in contrast with strong."),
    rule("1CO", 8, 9, "los que son flacos", "los que son débiles", "false-friend-weakness", "The referent is believers who are weak in conscience."),
    rule("1CO", 12, 22, "parecen más flacos", "parecen más débiles", "false-friend-weakness", "The body parts appear weaker, not thinner."),
    rule("2CO", 13, 4, "somos flacos con él", "somos débiles con él", "false-friend-weakness", "The verse contrasts weakness and power."),
    rule("2CO", 13, 9, "seamos nosotros flacos", "nosotros seamos débiles", "false-friend-weakness", "Flacos means weak in contrast with their being strong."),
    rule("HEB", 5, 11, "sois flacos para oir", "sois lentos para oír", "contextual-slow-to-understand", "The difficulty in explaining is attributed to slowness in hearing and understanding."),
    rule("HEB", 7, 28, "hombres flacos", "hombres débiles", "false-friend-weakness", "The law appoints human priests subject to weakness."),
    rule("ROM", 5, 6, "éramos flacos", "éramos débiles", "false-friend-weakness", "The phrase describes human helplessness when Christ died for the ungodly."),
    rule("1CO", 2, 3, "con flaqueza", "con debilidad", "archaic-weakness-term", "Flaqueza means weakness in Paul's condition when he arrived."),
    rule("1CO", 15, 43, "en flaqueza", "en debilidad", "archaic-weakness-term", "The resurrection passage contrasts weakness and power."),
    rule("2CO", 11, 30, "de mi flaqueza", "de mi debilidad", "archaic-weakness-term", "Paul boasts in what displays his weakness."),
    rule("2CO", 12, 9, "mi potencia en la flaqueza se perfecciona", "mi poder se perfecciona en la debilidad", "contextual-power-in-weakness", "The phrase preserves the contrast between Christ's power and human weakness."),
    rule("2CO", 13, 4, "por flaqueza", "en debilidad", "archaic-weakness-term", "The crucifixion is presented under the condition of human weakness."),
    rule("GAL", 4, 13, "por flaqueza de carne", "por una debilidad física", "contextual-physical-weakness", "The expression refers to the physical condition related to Paul's first preaching."),
    rule("ROM", 6, 19, "por la flaqueza de vuestra carne", "por la debilidad de vuestra naturaleza humana", "contextual-human-weakness", "Paul adapts the explanation to the weakness of the human condition."),
    rule("ROM", 8, 26, "nuestra flaqueza", "nuestra debilidad", "archaic-weakness-term", "The Spirit helps in our weakness when we pray."),
    rule("2CO", 12, 5, "mis flaquezas", "mis debilidades", "archaic-weakness-term", "Flaquezas means personal weaknesses."),
    rule("2CO", 12, 9, "mis flaquezas", "mis debilidades", "archaic-weakness-term", "Paul boasts in his weaknesses so that Christ's power may rest on him."),
    rule("2CO", 12, 10, "las flaquezas", "las debilidades", "archaic-weakness-term", "The list begins with weaknesses suffered for Christ."),
    rule("ROM", 15, 1, "las flaquezas de los flacos", "las debilidades de los débiles", "archaic-weakness-term", "The strong must bear the weaknesses of those who are weak.", supersede=True),
]

# Compania names different realities. Each replacement preserves whether the
# referent is a crowd, a community, or a military unit.
RULES += [
    rule("1PE", 5, 9, "en la compañía de vuestros hermanos", "entre vuestros hermanos", "contextual-community-term", "The same afflictions occur among the brothers and sisters in the world."),
    rule("2CO", 6, 14, "qué compañía tiene la justicia con la injusticia", "qué relación tiene la justicia con la injusticia", "contextual-partnership-term", "The question contrasts the relationship between righteousness and unrighteousness."),
    rule("ACT", 1, 15, "era la compañía junta como de ciento y veinte en número", "estaba reunido un grupo de unas ciento veinte personas", "contextual-gathered-group", "The phrase reports how many people were gathered."),
    rule("ACT", 10, 1, "centurión de la compañía que se llamaba la Italiana", "centurión de la unidad militar llamada la Italiana", "historical-military-unit", "Compania denotes the military unit to which Cornelius belonged."),
    rule("ACT", 11, 24, "mucha compañía fué agregada al Señor", "muchas personas fueron agregadas al Señor", "contextual-crowd-term", "The phrase describes many people who believed."),
    rule("ACT", 17, 5, "juntando compañía", "formando una turba", "contextual-mob-term", "The gathered men formed a mob that stirred up the city."),
    rule("ACT", 21, 31, "al tribuno de la compañía", "al comandante de la unidad militar", "historical-military-unit", "The report reaches the commander of the Roman unit."),
    rule("ACT", 27, 1, "de la compañía Augusta", "de la unidad militar Augusta", "historical-military-unit", "Compania denotes Julius's military unit."),
    rule("GAL", 2, 9, "nos dieron las diestras de compañía", "nos dieron la mano derecha en señal de compañerismo", "contextual-fellowship-gesture", "The gesture expresses fellowship and agreement in the mission."),
    rule("HEB", 12, 22, "á la compañía de muchos millares de ángeles", "a incontables ángeles reunidos", "contextual-angelic-gathering", "The phrase describes an innumerable gathering of angels."),
    rule("JHN", 11, 42, "por causa de la compañía que está alrededor", "por causa de la multitud que está alrededor", "contextual-crowd-term", "Jesus speaks for the sake of the surrounding crowd."),
    rule("JHN", 18, 3, "tomando una compañía", "tomando una tropa", "historical-arresting-party", "Judas arrives accompanied by a troop and guards."),
    rule("JHN", 18, 12, "la compañía y el tribuno", "la tropa y su comandante", "historical-arresting-party", "The troop and its commander participate in the arrest."),
    rule("LUK", 2, 44, "estaba en la compañía", "estaba en el grupo", "contextual-traveling-group", "Joseph and Mary thought Jesus was traveling within the group."),
    rule("LUK", 6, 17, "la compañía de sus discípulos", "un grupo numeroso de sus discípulos", "contextual-disciple-group", "The text distinguishes the group of disciples from the crowd that came to Jesus."),
    rule("LUK", 7, 11, "y gran compañía", "y una gran multitud", "contextual-crowd-term", "A large crowd accompanied Jesus and his disciples."),
    rule("LUK", 7, 12, "grande compañía de la ciudad", "una gran multitud de la ciudad", "contextual-crowd-term", "A large crowd from the city accompanied the widow."),
    rule("LUK", 8, 4, "una grande compañía", "una gran multitud", "contextual-crowd-term", "The parable is addressed to a large gathered crowd."),
    rule("LUK", 8, 42, "le apretaba la compañía", "la multitud lo apretaba", "contextual-crowd-term", "The crowd pressed Jesus while he was on the way."),
    rule("LUK", 8, 45, "la compañía te aprieta", "la multitud te aprieta", "contextual-crowd-term", "Peter refers to the crowd surrounding and pressing Jesus."),
    rule("LUK", 9, 13, "toda esta compañía", "toda esta multitud", "contextual-crowd-term", "The loaves and fish had to feed the gathered crowd."),
    rule("LUK", 9, 37, "gran compañía les salió al encuentro", "una gran multitud les salió al encuentro", "contextual-crowd-term", "A large crowd came to meet Jesus and the disciples."),
    rule("LUK", 9, 38, "un hombre de la compañía", "un hombre de la multitud", "contextual-crowd-term", "The man who cries out is part of the crowd."),
    rule("LUK", 11, 27, "una mujer de la compañía", "una mujer de la multitud", "contextual-crowd-term", "The woman raises her voice from the crowd."),
    rule("LUK", 12, 13, "uno de la compañía", "uno de la multitud", "contextual-crowd-term", "The man who speaks with Jesus comes from the crowd."),
    rule("LUK", 13, 14, "dijo á la compañía", "dijo a la multitud", "contextual-crowd-term", "The ruler of the synagogue addresses the crowd."),
    rule("LUK", 19, 39, "Fariseos de la compañía", "fariseos de la multitud", "contextual-crowd-term", "The Pharisees who speak were among the crowd."),
    rule("REV", 7, 9, "una gran compañía, la cual ninguno podía contar", "una gran multitud que nadie podía contar", "contextual-countless-multitude", "The vision shows an innumerable multitude from every nation."),
    rule("REV", 19, 1, "gran voz de gran compañía en el cielo", "fuerte voz de una gran multitud en el cielo", "contextual-heavenly-multitude", "John hears a powerful voice in heaven like that of a great multitude."),
    rule("REV", 19, 6, "voz de una grande compañía", "voz de una gran multitud", "contextual-heavenly-multitude", "The voice heard is compared with that of a great multitude."),
]

RULES += [
    rule("1TI", 1, 6, "vanas pláticas", "discursos inútiles", "archaic-empty-talk", "The warning describes empty speech that turns people away from the teaching."),
    rule("1TI", 6, 20, "profanas pláticas de vanas cosas", "discursos profanos y vacíos", "archaic-empty-talk", "Timothy must avoid profane and empty speech opposed to his charge."),
    rule("LUK", 24, 17, "Qué pláticas son estas que tratáis entre vosotros andando", "De qué conversáis entre vosotros mientras camináis", "archaic-conversation-phrase", "Jesus asks what they were discussing as they walked."),
    rule("1CO", 5, 4, "con la facultad de nuestro Señor Jesucristo", "con el poder de nuestro Señor Jesucristo", "contextual-divine-power", "Facultad means the Lord's power or authority here."),
    rule("ACT", 9, 14, "tiene facultad de los príncipes de los sacerdotes", "tiene autoridad de los principales sacerdotes", "contextual-delegated-authority", "Saul had received authority from the chief priests to arrest."),
    rule("HEB", 13, 10, "no tienen facultad de comer", "no tienen derecho a comer", "contextual-right-term", "Facultad means the right to eat from the altar here."),
    rule("JAS", 5, 5, "habéis cebado vuestros corazones como en el día de sacrificios", "habéis engordado vuestros corazones como para el día de la matanza", "archaic-fattened-metaphor", "The image compares a life of pleasure with animals fattened for the day of slaughter."),
]

RULES += [
    rule("JAS", 1, 17, "Toda buena d\u00e1diva", "Todo buen regalo", "archaic-gift-term", "Dadiva means a gift here; the paired perfect gift remains intact."),
    rule("ROM", 6, 23, "la d\u00e1diva de Dios", "el regalo de Dios", "archaic-gift-term", "The free gift from God is contrasted with the wages of sin."),
    rule("LUK", 11, 13, "buenas d\u00e1divas", "buenos regalos", "archaic-gift-term", "The comparison concerns parents giving good gifts to their children."),
    rule("PHP", 4, 17, "No porque busque d\u00e1divas", "No es que busque donativos", "contextual-financial-gift", "Paul is not seeking financial contributions from the Philippians."),
    rule("LUK", 13, 30, "son postreros los que eran los primeros; y son primeros los que eran los postreros", "son \u00faltimos los que eran primeros, y son primeros los que eran \u00faltimos", "archaic-last-term", "Postreros means those who are last in the reversal announced by Jesus."),
    rule("2PE", 2, 2, "seguir\u00e1n sus disoluciones", "seguir\u00e1n su conducta desenfrenada", "contextual-debauchery-term", "The warning concerns shameless and morally unrestrained conduct."),
    rule("ROM", 13, 13, "no en lechos y disoluciones", "no en inmoralidad sexual ni desenfreno", "contextual-debauchery-term", "The list rejects sexual immorality and unrestrained conduct."),
    rule("ROM", 5, 20, "cuando el pecado creci\u00f3, sobrepuj\u00f3 la gracia", "cuando el pecado aument\u00f3, la gracia abund\u00f3 mucho m\u00e1s", "archaic-abounding-phrase", "The clause states that grace abounded beyond the increase of sin."),
    rule("2CO", 6, 3, "el ministerio nuestro no sea vituperado", "nuestro ministerio no sea desacreditado", "archaic-discredited-term", "Paul avoids giving offense so that the ministry is not discredited."),
]


PENDING = [
    ("nt-v25-iniquity-family", "iniquidad / inicuo", ["maldad", "injusticia", "sin ley"], "La familia alterna entre maldad, injusticia y oposición a la ley; incluye un título escatológico en 2 Tesalonicenses."),
    ("nt-v25-propitiation", "propiciación", ["conservar con nota", "aclarar como sacrificio de reconciliación"], "Es un término doctrinal que reúne sacrificio, perdón y reconciliación; una palabra general perdería parte del sentido."),
    ("nt-v25-authority-powers", "potencia / potestad / potestades / principados", ["poder", "autoridad humana", "poder delegado", "poder espiritual"], "El referente cambia entre poder divino, autoridad humana, derecho, poder milagroso y seres espirituales."),
    ("nt-v25-sexual-immorality", "fornicación / inmundicia", ["inmoralidad sexual", "impureza", "conservar en imágenes proféticas"], "Los términos cambian entre conducta sexual concreta, impureza moral y metáfora profética."),
    ("nt-v25-covenant-testament", "pacto / testamento", ["pacto", "testamento", "conservar con nota"], "La elección debe mantenerse coherente en los dichos de la Cena, Hebreos y la relación entre pacto y testamento."),
    ("nt-v25-remission-atonement", "remisión / expiación", ["perdón", "liberación", "expiación"], "Son términos doctrinales con matices distintos; no deben colapsarse mediante una sustitución general."),
    ("nt-v25-circumcision", "circuncisión / incircuncisión", ["conservar término histórico", "explicar grupo o condición por contexto"], "A veces nombra el rito, otras una condición o un grupo de personas; el término sigue siendo comprensible."),
    ("nt-v25-spiritual-terms", "redención / primicias / mediador", ["conservar", "añadir explicación contextual"], "Son términos bíblicos comprensibles y cargados de significado; se conservan hasta decidir una política de notas."),
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, compact=False):
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":") if compact else None, indent=None if compact else 2)
    path.write_text(text + "\n", encoding="utf-8")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_maps():
    books = {}
    verses = {}
    for path in CORPUS.glob("*.json"):
        doc = read(path)
        books[doc["book"]] = doc
        for chapter in doc["chapters"]:
            for verse in chapter["verses"]:
                verses[(doc["book"], chapter["chapter"], verse["verse"])] = verse["text"]
    return books, verses


def direction_maps():
    docs, paths = {}, {}
    for path in DIRECTION.glob("*_reading_2026.rv1909.v1.json"):
        doc = read(path)
        docs[doc["book"]] = doc
        paths[doc["book"]] = path
    return docs, paths


def occurrences(text, expected):
    result = []
    cursor = 0
    while True:
        start = text.find(expected, cursor)
        if start < 0:
            return result
        end = start + len(expected)
        before = text[start - 1] if start else ""
        after = text[end] if end < len(text) else ""
        if not (expected[0].isalpha() and before.isalpha()) and not (expected[-1].isalpha() and after.isalpha()):
            result.append((start, end))
        cursor = end


def main():
    books, sources = source_maps()
    directions, paths = direction_maps()
    applied = []
    changed_books = set()

    for entry in RULES:
        ref = (entry["book"], entry["chapter"], entry["verse"])
        text = sources[ref]
        spans = occurrences(text, entry["expected"])
        if not spans:
            raise RuntimeError(f"expected text absent at {ref}: {entry['expected']!r}")
        direction = directions[entry["book"]]
        patch = next((v for v in direction["verses"] if v["chapter"] == entry["chapter"] and v["verse"] == entry["verse"]), None)
        if patch is None:
            patch = {"chapter": entry["chapter"], "verse": entry["verse"], "sourceTextSha256": sha(text), "edits": []}
            direction["verses"].append(patch)
        added_here = 0
        for start, end in spans:
            exact = next((e for e in patch["edits"] if e["startOffset"] == start and e["endOffset"] == end), None)
            if exact:
                if exact["replacement"] == entry["replacement"]:
                    continue
                if entry.get("previousReplacement") == exact["replacement"]:
                    evidence_url = (
                        "https://www.biblegateway.com/passage/?search="
                        f"{BOOK_NAMES[entry['book']]}+{entry['chapter']}%3A{entry['verse']}"
                        "&version=RVR1960%3BNVI%3BLBLA%3BRVC"
                    )
                    exact.update({
                        "replacement": entry["replacement"], "category": entry["category"],
                        "reason": entry["reason"],
                        "evidence": [{"label": "Control contextual RVR1960, NVI, LBLA y RVC", "url": evidence_url}],
                    })
                    applied.append({**entry, "evidence": exact["evidence"]})
                    added_here += 1
                    continue
                raise RuntimeError(f"edit collision at {ref}: {exact}")
            overlaps = [e for e in patch["edits"] if e["startOffset"] < end and start < e["endOffset"]]
            if overlaps:
                if entry.get("supersedeOverlaps"):
                    patch["edits"] = [e for e in patch["edits"] if e not in overlaps]
                else:
                    raise RuntimeError(f"overlap at {ref} for {entry['expected']!r}: {overlaps}")
            evidence_url = (
                "https://www.biblegateway.com/passage/?search="
                f"{BOOK_NAMES[entry['book']]}+{entry['chapter']}%3A{entry['verse']}"
                "&version=RVR1960%3BNVI%3BLBLA%3BRVC"
            )
            edit = {
                "startOffset": start, "endOffset": end,
                "expected": entry["expected"], "replacement": entry["replacement"],
                "category": entry["category"], "reason": entry["reason"],
                "evidence": [{"label": "Control contextual RVR1960, NVI, LBLA y RVC", "url": evidence_url}],
            }
            patch["edits"].append(edit)
            applied.append({**entry, "evidence": edit["evidence"]})
            added_here += 1
        if added_here:
            changed_books.add(entry["book"])

    for book in changed_books:
        direction = directions[book]
        for patch in direction["verses"]:
            text = sources[(book, patch["chapter"], patch["verse"])]
            patch["sourceTextSha256"] = sha(text)
            patch["edits"].sort(key=lambda edit: edit["startOffset"])
            last = -1
            for edit in patch["edits"]:
                if edit["startOffset"] < last or text[edit["startOffset"]:edit["endOffset"]] != edit["expected"]:
                    raise RuntimeError(f"invalid edit at {book}.{patch['chapter']}.{patch['verse']}: {edit}")
                last = edit["endOffset"]
        direction["verses"].sort(key=lambda verse: (verse["chapter"], verse["verse"]))
        category_counts = Counter(edit["category"] for verse in direction["verses"] for edit in verse["edits"])
        direction["coverage"]["changedVerses"] = len(direction["verses"])
        direction["coverage"]["editCount"] = sum(len(verse["edits"]) for verse in direction["verses"])
        direction["coverage"]["categoryCounts"] = dict(sorted(category_counts.items()))
        direction["coverage"]["editorialPolicyVersion"] = VERSION
        direction["editorialStatus"] = "approved-remaining-new-testament-context-review-v25"
        direction["ownerReview"] = {
            "contentVersion": VERSION,
            "changeSet": "editorial-changes/v25.json",
            "review": "Nuevo Testamento restante revisado por contexto; familias doctrinales reservadas",
            "requiredFullTest": True,
        }
        write(paths[book], direction, compact=True)

    change_set = {
        "format": "shine-reading-2026-editorial-change-set", "schemaVersion": 1,
        "contentVersion": VERSION, "generatedAt": STAMP, "issuedAt": STAMP,
        "expiresAt": "2028-09-13T00:15:00.000Z", "sourceVersionId": "RV1909",
        "filterId": "RV1909-LECTURA-2026", "changes": applied,
    }
    write(CHANGE_SET, change_set)

    package_source = read(PACKAGE_SOURCE)
    package_source["contentVersion"] = VERSION
    package_source["generatedAt"] = STAMP
    package_source["editorialPolicy"]["version"] = VERSION
    package_source["editorialPolicy"]["description"] = (
        "Only exact, full-context comprehension improvements are applied. "
        "Understandable wording and doctrinal or textual ambiguities remain unchanged."
    )
    write(PACKAGE_SOURCE, package_source)

    registry = read(REGISTRY)
    resolved_ids = {
        "nt-concupiscencia", "nt-concupiscencias", "nt-disensión", "nt-disensiones",
        "nt-longanimidad", "nt-dispensación", "nt-solícito", "nt-solícitos",
    }
    registry["pending"] = [p for p in registry.get("pending", []) if p.get("id") not in resolved_ids and not p.get("id", "").startswith("nt-v25-")]
    all_refs = {}
    for term in ("iniquidad", "inicuo", "inicuos", "propiciación", "potencia", "potestad", "potestades", "principados", "fornicación", "inmundicia", "pacto", "testamento", "remisión", "expiación", "circuncisión", "incircuncisión", "redención", "primicias", "mediador"):
        refs = []
        for ref, text in sources.items():
            if ref[0] not in BOOK_NAMES:
                continue
            if term.casefold() in text.casefold().split() or term.casefold() in text.casefold():
                refs.append({"book": ref[0], "chapter": ref[1], "verse": ref[2]})
        all_refs[term] = refs
    pending_terms = {
        "nt-v25-iniquity-family": ["iniquidad", "inicuo", "inicuos"],
        "nt-v25-propitiation": ["propiciación"],
        "nt-v25-authority-powers": ["potencia", "potestad", "potestades", "principados"],
        "nt-v25-sexual-immorality": ["fornicación", "inmundicia"],
        "nt-v25-covenant-testament": ["pacto", "testamento"],
        "nt-v25-remission-atonement": ["remisión", "expiación"],
        "nt-v25-circumcision": ["circuncisión", "incircuncisión"],
        "nt-v25-spiritual-terms": ["redención", "primicias", "mediador"],
    }
    for pending_id, term, options, reason in PENDING:
        unique = {}
        for key in pending_terms[pending_id]:
            for ref in all_refs[key]:
                unique[(ref["book"], ref["chapter"], ref["verse"])] = ref
        registry["pending"].append({
            "id": pending_id, "status": "pending-review", "scope": "new-testament",
            "term": term, "proposedOptions": options, "reason": reason,
            "references": list(unique.values()),
            "evidence": [{"label": "Control contextual RVR1960, NVI, LBLA y RVC", "url": "https://www.biblegateway.com/"}],
        })
    registry["updatedAt"] = STAMP
    registry["activeChangeSet"] = "editorial-changes/v25.json"
    write(REGISTRY, registry)

    print(json.dumps({
        "rules": len(RULES), "addedEdits": len(applied), "changedBooks": len(changed_books),
        "pendingFamilies": len(PENDING), "perBook": dict(Counter(x["book"] for x in applied)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
