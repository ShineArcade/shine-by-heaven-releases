import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK_PATH = ROOT / "apps/mobile/assets/bibles/rv1909/books/EXO.json"
LAYER_PATH = ROOT / "apps/mobile/assets/bible_direction/exodus_reading_2026.rv1909.v1.json"
CHANGE_SET = ROOT / "editorial-changes/v16.json"
REGISTRY = ROOT / "editorial-review/registry.json"


# This is deliberately an explicit Exodus-only list. Each entry was retained only
# after reading the complete verse beside RVR1960 and NVI. Repeated forms are
# expanded only in the verse references recorded below.
FINITE_ENCLITICS = {
    "llenóse": "se llenó",
    "Levantóse": "Se levantó",
    "levantóse": "se levantó",
    "díjole": "le dijo",
    "díjoles": "les dijo",
    "paróse": "se quedó",
    "criólo": "lo crio",
    "escondiólo": "lo escondió",
    "echáronlas": "las echaron",
    "defendiólas": "las defendió",
    "apareciósele": "se le apareció",
    "llamólo": "lo llamó",
    "echólo": "lo echó",
    "encontrólo": "lo encontró",
    "besóle": "lo besó",
    "inclináronse": "se inclinaron",
    "cumpliéronse": "se cumplieron",
    "esparcióla": "la esparció",
    "echáronlos": "los echaron",
    "asentóse": "se asentó",
    "oscurecióse": "se oscureció",
    "arrojóla": "la arrojó",
    "quitóles": "les quitó",
    "cubriólos": "los cubrió",
    "hundiéronse": "se hundieron",
    "pudrióse": "se pudrió",
    "derretíase": "se derretía",
    "pusiéronla": "la pusieron",
    "besólo": "lo besó",
    "preguntáronse": "se preguntaron",
    "alegróse": "se alegró",
    "fuése": "se fue",
    "estremecióse": "se estremeció",
    "darále": "le dará",
    "oiráse": "se oirá",
    "allegóse": "se reunió",
    "dijéronle": "le dijeron",
    "formólo": "le dio forma",
    "quebrólas": "las quebró",
    "quemólo": "lo quemó",
    "moliólo": "lo molió",
    "diéronmelo": "me lo dieron",
    "echélo": "lo eché",
    "extendiólo": "lo extendió",
    "poníase": "se ponía",
    "levantábase": "se levantaba",
    "volvíase": "se volvía",
    "encorvóse": "se postró",
    "llamólos": "los llamó",
    "quitábase": "se quitaba",
    "traíala": "la traía",
    "hízolas": "las hizo",
    "cubriólas": "las cubrió",
    "cubrióla": "la cubrió",
    "cubriólo": "lo cubrió",
    "uníanse": "se unían",
    "púsolas": "las puso",
    "bendíjolos": "los bendijo",
}


# These words keep one meaning throughout Exodus. They were checked in every
# occurrence before being admitted here; verses with repeated occurrences are
# handled below with a unique, larger phrase because the apply gate rejects an
# ambiguous match.
UNIFORM_TERMS = {
    "Sittim": ("acacia", "archaic-plant-name", "Sittim es el nombre antiguo de la madera de acacia usada en estos muebles y estructuras."),
    "cabos": ("extremos", "archaic-lexicon", "Cabos designa los extremos de la pieza u objeto."),
    "simiente": ("descendencia", "archaic-lexicon", "Simiente designa aquí la descendencia familiar."),
    "onix": ("ónice", "archaic-orthography", "Se usa la grafía actual del nombre de la piedra."),
    "quicios": ("espigas", "archaic-technical-lexicon", "Quicios designa las espigas de unión de las tablas."),
    "candilejas": ("lámparas", "archaic-technical-lexicon", "Candilejas designa las lámparas del candelabro."),
    "basas": ("bases", "archaic-technical-lexicon", "Basas son las bases que sostienen las tablas o columnas."),
    "corchetes": ("ganchos", "archaic-technical-lexicon", "Corchetes designa los ganchos que sujetan o unen las cortinas."),
    "ephod": ("efod", "archaic-orthography", "Se usa la grafía actual efod para la vestidura sacerdotal."),
    "racional": ("pectoral", "archaic-technical-lexicon", "Racional designa aquí el pectoral sacerdotal."),
}

UNIFORM_EXCLUSIONS = {
    ("pabellón", 39, 34),
    ("simiente", 16, 31),
    ("quicios", 36, 22),
    ("candilejas", 25, 37),
    ("basas", 26, 32),
    ("basas", 26, 37),
    ("corchetes", 26, 6),
    ("corchetes", 26, 11),
    ("corchetes", 36, 18),
}


CHANGES = [
    (1, 5, "todas las almas de los que salieron del muslo de Jacob", "todas las personas descendientes de Jacob", "archaic-idiom", "La imagen anatómica antigua designa a los descendientes de Jacob; ambos controles modernos confirman el referente."),
    (1, 10, "seamos sabios para con él", "actuemos con astucia contra él", "context-reviewed-phrase", "La frase expresa el plan astuto del faraón contra Israel, no sabiduría favorable hacia el pueblo."),
    (1, 11, "sobre él comisarios de tributos", "sobre ellos capataces", "context-reviewed-phrase", "Se corrige el referente plural y se expresa el cargo con una palabra actual."),
    (1, 11, "los molestasen con sus cargas", "los oprimieran con trabajos forzados", "context-reviewed-phrase", "Los controles coinciden en que las cargas eran trabajos impuestos para oprimir al pueblo."),
    (1, 14, "rigorismo", "rigor", "archaic-lexicon", "Rigorismo no expresa aquí una doctrina moral, sino la dureza con que los obligaban a trabajar."),
    (1, 16, "Cuando parteareis á las Hebreas, y mirareis los asientos", "Cuando asistan a las hebreas en sus partos y vean el sexo del bebé", "context-reviewed-phrase", "La construcción antigua describe la asistencia al parto y la identificación del sexo del recién nacido."),
    (1, 17, "reservaban la vida á los niños", "dejaron con vida a los niños", "context-reviewed-phrase", "Reservar la vida significa aquí no matar; la forma actual elimina esa ambigüedad."),
    (1, 18, "habéis reservado la vida á los niños", "han dejado con vida a los niños", "context-reviewed-phrase", "La pregunta del faraón se refiere a que las parteras no mataron a los niños."),
    (1, 19, "paren antes", "dan a luz antes", "archaic-lexicon", "Dar a luz es la expresión actual equivalente en este contexto."),
    (2, 1, "UN varón de la familia de Leví fué, y tomó por mujer una hija de Leví", "UN hombre de la familia de Leví tomó por esposa a una mujer de Leví", "context-reviewed-phrase", "Se elimina una construcción quebrada y se conservan parentesco, sujeto y matrimonio."),
    (2, 2, "parió un hijo", "dio a luz un hijo", "archaic-lexicon", "Dar a luz comunica la misma acción con uso actual."),
    (2, 2, "túvole escondido", "lo mantuvo escondido", "archaic-phrase", "La colocación antigua del pronombre y el verbo tener se expresan en español actual."),
    (2, 3, "una arquilla de juncos", "una cesta de juncos", "archaic-lexicon", "Arquilla designa la cesta en que fue colocado el niño."),
    (2, 3, "calafateóla con pez y betún", "la recubrió con asfalto y brea", "context-reviewed-phrase", "Los materiales y la acción convergen en los controles; pez no significa aquí un animal."),
    (2, 3, "en un carrizal", "entre los juncos", "archaic-lexicon", "Carrizal designa el conjunto de juncos de la orilla."),
    (2, 5, "la arquilla en el carrizal", "la cesta entre los juncos", "archaic-phrase", "Se conservan objeto y ubicación con palabras actuales."),
    (2, 8, "la doncella", "la muchacha", "archaic-lexicon", "Doncella se refiere aquí a la joven hermana de Moisés."),
    (2, 10, "la cual lo prohijó", "quien lo adoptó", "archaic-lexicon", "Prohijar significa adoptar como hijo."),
    (2, 11, "acaeció que", "sucedió que", "archaic-lexicon", "Acaecer significa suceder."),
    (2, 11, "vió sus cargas", "vio sus duras tareas", "context-reviewed-phrase", "Cargas designa aquí el trabajo opresivo de los hebreos."),
    (2, 13, "al que hacía la injuria", "al que maltrataba al otro", "context-reviewed-phrase", "La frase identifica al agresor en la pelea."),
    (2, 14, "Ciertamente esta cosa es descubierta", "Ciertamente esto ha sido descubierto", "archaic-phrase", "Se expresa en español actual que el homicidio ya se conocía."),
    (2, 16, "las pilas", "los abrevaderos", "context-reviewed-lexicon", "Las pilas contenían agua para las ovejas; abrevaderos hace explícita su función."),
    (2, 17, "abrevó sus ovejas", "dio de beber a sus ovejas", "archaic-lexicon", "Abrevar significa dar de beber al ganado."),
    (2, 19, "Un varón Egipcio nos defendió de mano de los pastores", "Un hombre egipcio nos defendió de los pastores", "archaic-phrase", "Se elimina la locución de mano de sin cambiar quién defendió a quién."),
    (2, 19, "abrevó las ovejas", "dio de beber a las ovejas", "archaic-lexicon", "Abrevar significa dar de beber al ganado."),
    (2, 20, "llamadle para que coma pan", "llámenlo para que coma", "archaic-phrase", "Comer pan significa aquí comer; se conserva la invitación con forma actual."),
    (2, 21, "acordó en morar con aquel varón", "aceptó quedarse a vivir con aquel hombre", "archaic-phrase", "Los controles confirman que Moisés aceptó permanecer en su casa."),
    (2, 22, "le parió un hijo", "dio a luz un hijo", "archaic-lexicon", "Dar a luz comunica la misma acción con uso actual."),
    (2, 22, "Peregrino soy", "Forastero soy", "context-reviewed-lexicon", "Peregrino describe aquí a quien vive fuera de su tierra, no un viaje devocional."),
    (2, 25, "reconociólos Dios", "Dios los reconoció", "archaic-enclitic-order", "Se actualiza el orden del pronombre sin cambiar la acción."),
    (3, 1, "detrás del desierto", "al otro extremo del desierto", "archaic-idiom", "La frase describe el lugar al que llevó el rebaño, no una posición detrás de un objeto."),
    (3, 1, "vino á Horeb", "llegó a Horeb", "archaic-lexicon", "Venir significa llegar en esta narración."),
    (3, 3, "esta grande visión", "esta gran visión", "archaic-grammar", "Se usa la forma apocopada actual delante del sustantivo."),
    (3, 5, "No te llegues acá", "No te acerques", "archaic-phrase", "Llegarse significa acercarse."),
    (3, 20, "Empero", "Pero", "archaic-connector", "Empero funciona como conector adversativo y ambos controles sostienen pero."),
    (4, 6, "Mete ahora tu mano en tu seno", "Mete ahora tu mano en tu pecho", "archaic-lexicon", "Seno designa aquí el pecho, como confirma el contexto de la señal."),
    (4, 6, "como la sacó", "cuando la sacó", "archaic-connector", "Como tiene aquí valor temporal; cuando evita una lectura comparativa."),
    (5, 4, "idos á vuestros cargos", "vuelvan a sus tareas", "archaic-phrase", "Cargos significa aquí las tareas impuestas, no puestos de autoridad."),
    (5, 5, "les hacéis cesar de sus cargos", "los hacen dejar sus tareas", "archaic-phrase", "Cargos vuelve a designar el trabajo obligatorio."),
    (5, 7, "como ayer y antes de ayer", "como hasta ahora", "archaic-idiom", "La locución significa como se venía haciendo anteriormente."),
    (5, 12, "se derramó por toda la tierra", "se esparció por toda la tierra", "context-reviewed-lexicon", "Derramarse describe aquí la dispersión del pueblo por Egipto."),
    (5, 19, "habiéndoseles dicho", "cuando se les dijo", "archaic-grammar", "Se conserva la relación temporal con una construcción directa."),
    (5, 21, "habéis hecho heder nuestro olor", "nos han hecho abominables", "archaic-idiom", "La imagen antigua significa que el faraón y sus siervos ahora los detestan."),
    (5, 21, "dándoles el cuchillo en las manos", "poniéndoles la espada en la mano", "context-reviewed-idiom", "La imagen expresa haber dado al adversario el medio para matarlos."),
    (6, 2, "Habló todavía Dios á Moisés, y", "Dios volvió a hablar a Moisés y", "archaic-phrase", "Todavía significa nuevamente en esta secuencia; se conserva la introducción al discurso."),
    (6, 3, "no me notifiqué á ellos", "no me di a conocer a ellos", "archaic-phrase", "Notificarse significa darse a conocer en este contexto."),
    (6, 9, "congoja de espíritu", "desánimo", "context-reviewed-lexicon", "La frase describe el abatimiento que les impedía escuchar por la dura esclavitud."),
    (6, 12, "mayormente siendo yo incircunciso de labios", "siendo yo torpe de labios", "archaic-idiom", "La expresión idiomática se refiere a la dificultad de Moisés para hablar."),
    (6, 23, "tomóse Aarón por mujer á Elisabeth", "Aarón tomó por esposa a Elisabet", "archaic-phrase", "Se actualiza el orden y la expresión matrimonial sin cambiar las personas."),
    (6, 23, "la cual le parió", "quien dio a luz", "archaic-lexicon", "Dar a luz comunica la misma acción con uso actual."),
    (6, 30, "yo soy incircunciso de labios", "yo soy torpe de labios", "archaic-idiom", "La expresión idiomática se refiere a la dificultad de Moisés para hablar."),
    (7, 14, "está agravado", "está endurecido", "context-reviewed-lexicon", "El contexto trata de la obstinación del corazón del faraón."),
    (7, 23, "Y tornando Faraón", "Y Faraón", "archaic-phrase", "Se elimina la duplicación de volver que ya aparece en el verbo principal."),
    (7, 23, "y no puso su corazón aun en esto", "sin prestar atención a lo sucedido", "archaic-idiom", "Poner el corazón significa aquí prestar atención."),
    (8, 9, "Gloríate sobre mí", "Dime cuándo", "archaic-idiom", "Moisés pide al faraón que elija el momento de la oración; no le pide que se gloríe."),
    (8, 15, "agravó su corazón", "endureció su corazón", "context-reviewed-lexicon", "El contexto describe la obstinación del faraón."),
    (8, 32, "agravó aún esta vez su corazón", "endureció su corazón también esta vez", "context-reviewed-phrase", "El contexto describe nuevamente la obstinación del faraón."),
    (9, 7, "se agravó", "se endureció", "context-reviewed-lexicon", "El contexto describe la obstinación del corazón del faraón."),
    (9, 23, "el fuego discurría por la tierra", "los rayos se descargaron sobre la tierra", "archaic-idiom", "Fuego designa los rayos de la tormenta y discurrir su descarga sobre Egipto."),
    (9, 34, "agravó su corazón", "endureció su corazón", "context-reviewed-lexicon", "El contexto describe la obstinación del faraón y sus siervos."),
    (10, 7, "¿Hasta cuándo nos ha de ser éste por lazo?", "¿Hasta cuándo será este hombre nuestra ruina?", "archaic-idiom", "Ser por lazo significa convertirse en causa de ruina para Egipto."),
    (10, 11, "demandasteis", "pidieron", "archaic-lexicon", "Demandar significa pedir en esta conversación."),
    (10, 14, "en todos los términos de Egipto, en gran manera grave", "por todo Egipto en tan gran cantidad", "archaic-phrase", "La frase describe la extensión y cantidad excepcional de la plaga."),
    (10, 16, "apriesa", "deprisa", "archaic-orthography", "Se usa la forma actual de la locución."),
    (12, 15, "comiere leudado", "coma algo con levadura", "archaic-lexicon", "Leudado significa alimento que contiene levadura."),
    (12, 16, "aderecéis", "preparen", "archaic-lexicon", "Aderezar significa preparar la comida en este contexto."),
    (12, 17, "fiesta de los ázimos", "fiesta de los panes sin levadura", "archaic-lexicon", "Ázimos son panes sin levadura."),
    (12, 19, "comiere leudado", "coma algo con levadura", "archaic-lexicon", "Leudado significa alimento que contiene levadura."),
    (12, 22, "mojadle", "mójenlo", "archaic-grammar", "Se actualiza la forma verbal y el pronombre referido al manojo."),
    (12, 22, "una jofaina", "una vasija", "archaic-lexicon", "Jofaina designa el recipiente que contenía la sangre."),
    (12, 22, "la jofaina", "la vasija", "archaic-lexicon", "Jofaina designa el recipiente que contenía la sangre."),
    (12, 33, "dándose priesa", "apresurándose", "archaic-phrase", "Darse priesa significa apresurarse."),
    (12, 35, "demandando á los Egipcios", "pidiendo a los egipcios", "archaic-lexicon", "Demandar significa pedir en este contexto."),
    (12, 36, "prestáronles", "les dieron todo lo que pidieron", "context-reviewed-lexicon", "Los controles confirman que los egipcios entregaron lo solicitado, no un préstamo posterior."),
    (12, 39, "no había leudado", "no había fermentado", "archaic-lexicon", "Leudar significa fermentar la masa."),
    (13, 3, "aqueste", "este", "archaic-lexicon", "Aqueste es una forma antigua de este."),
    (13, 3, "no comeréis leudado", "no comerán nada con levadura", "archaic-phrase", "Leudado significa alimento que contiene levadura."),
    (13, 7, "no se verá contigo leudado", "no tendrán nada con levadura", "archaic-phrase", "Se expresa la prohibición con palabras actuales."),
    (13, 8, "Hácese esto", "Esto se hace", "archaic-enclitic-order", "Se actualiza el orden del pronombre sin cambiar la acción."),
    (13, 9, "serte ha", "te será", "archaic-grammar", "Se actualiza la construcción verbal futura."),
    (13, 14, "decirle has", "le dirás", "archaic-grammar", "Se actualiza la construcción verbal futura."),
    (13, 16, "Serte ha", "Te será", "archaic-grammar", "Se actualiza la construcción verbal futura."),
    (14, 14, "estaréis quedos", "estarán tranquilos", "archaic-lexicon", "Quedos significa quietos o tranquilos en esta promesa."),
    (14, 25, "trastornólos gravemente", "les dificultó mucho avanzar", "archaic-idiom", "La frase describe la dificultad de los carros egipcios para avanzar."),
    (15, 2, "á éste engrandeceré", "lo alabaré", "context-reviewed-lexicon", "Engrandecer significa alabar a Dios en este cántico."),
    (15, 5, "descendieron á los profundos", "descendieron a las profundidades", "archaic-phrase", "Profundos funciona aquí como sustantivo antiguo por profundidades."),
    (15, 7, "has trastornado", "has derribado", "context-reviewed-lexicon", "Trastornar significa derribar a los que se levantaron contra Dios."),
    (15, 8, "soplo de tus narices", "soplo de tu aliento", "archaic-idiom", "La imagen poética se conserva como soplo y se expresa aliento en uso actual."),
    (15, 11, "terrible en loores", "admirable en gloriosas hazañas", "archaic-phrase", "Loores no resulta claro; el paralelismo celebra las obras temibles y maravillosas de Dios."),
    (15, 13, "llevástelo con tu fortaleza á la habitación de tu santuario", "lo llevaste con tu poder a tu santa morada", "archaic-phrase", "Habitación significa morada y fortaleza significa poder en este verso."),
    (15, 14, "Oiránlo", "Lo oirán", "archaic-enclitic-order", "Se actualiza el orden del pronombre sin cambiar la acción."),
    (15, 14, "apoderarse ha dolor", "se apoderará la angustia", "archaic-grammar", "Se actualiza la construcción futura y dolor se entiende aquí como angustia."),
    (15, 15, "á los robustos de Moab los ocupará temblor", "el temblor se apoderará de los poderosos de Moab", "archaic-phrase", "Robustos designa a los poderosos y ocupar expresa que el temor se apodera de ellos."),
    (16, 3, "pan en hartura", "pan hasta saciarnos", "archaic-lexicon", "Hartura significa comer hasta quedar satisfechos."),
    (16, 4, "cogerá para cada un día", "recogerá cada día su porción", "archaic-phrase", "Se expresa la recolección de la ración diaria."),
    (16, 5, "aparejarán lo que han de encerrar", "prepararán lo que han de guardar", "archaic-phrase", "Aparejar y encerrar significan preparar y guardar la porción."),
    (16, 8, "pan en hartura", "pan hasta saciarse", "archaic-lexicon", "Hartura significa comer hasta quedar satisfechos."),
    (16, 14, "sobre la haz del desierto", "sobre la superficie del desierto", "archaic-lexicon", "Haz significa superficie en este contexto."),
    (16, 18, "medíanlo", "lo medían", "archaic-enclitic-order", "Se actualiza el orden del pronombre sin cambiar la acción."),
    (16, 21, "recogíanlo", "lo recogían", "archaic-enclitic-order", "Se actualiza el orden del pronombre sin cambiar la acción."),
    (16, 29, "Estése, pues, cada uno en su estancia", "Quédese, pues, cada uno en su lugar", "archaic-phrase", "Estancia significa lugar y la orden se expresa de forma actual."),
    (17, 12, "sustentaban sus manos", "sostenían sus manos", "archaic-lexicon", "Sustentar significa sostener físicamente los brazos de Moisés."),
    (18, 16, "Cuando tienen negocios", "Cuando tienen asuntos", "archaic-lexicon", "Negocios significa asuntos o disputas en este contexto."),
    (18, 18, "el negocio es demasiado pesado", "la tarea es demasiado pesada", "archaic-lexicon", "Negocio significa la tarea de juzgar al pueblo."),
    (18, 21, "inquiere tú", "escoge tú", "archaic-lexicon", "Inquirir significa buscar y seleccionar aquí a los hombres capaces."),
    (19, 3, "denunciarás", "anunciarás", "archaic-lexicon", "Denunciar significa comunicar el mensaje, no acusar una falta."),
    (19, 13, "En habiendo sonado largamente la bocina", "Cuando suene largamente la trompeta", "archaic-phrase", "Se actualizan la construcción temporal y el nombre cotidiano del instrumento."),
    (19, 19, "iba esforzándose en extremo", "iba aumentando en intensidad", "archaic-phrase", "La frase describe el sonido que se hacía cada vez más fuerte."),
    (19, 21, "requiere al pueblo", "advierte al pueblo", "context-reviewed-lexicon", "Requerir significa advertirles que no crucen el límite."),
    (19, 23, "nos has requerido", "nos has advertido", "context-reviewed-lexicon", "Requerir significa haber dado una advertencia previa."),
    (20, 18, "consideraba las voces", "observaba los truenos", "archaic-phrase", "Voces designa el estruendo de los truenos y considerar significa percibir el espectáculo."),
    (21, 2, "saldrá horro de balde", "saldrá libre sin pagar nada", "archaic-phrase", "Horro significa libre y de balde significa sin pago."),
    (21, 6, "harále llegar", "lo llevará", "archaic-grammar", "Se actualiza el futuro con pronombre y se evita repetir hacer llegar."),
    (21, 6, "lesna", "punzón", "archaic-lexicon", "Lesna designa la herramienta puntiaguda usada para perforar la oreja."),
    (21, 10, "débito conyugal", "deber conyugal", "archaic-lexicon", "Débito significa deber u obligación conyugal."),
    (21, 13, "no armó asechanzas", "no pretendía herirlo", "archaic-idiom", "Armar asechanzas expresa que la muerte no fue premeditada."),
    (21, 21, "si durare por un día ó dos", "si sobrevive uno o dos días", "archaic-phrase", "Durar se refiere aquí a sobrevivir a la herida."),
    (21, 22, "mujer preñada", "mujer embarazada", "archaic-lexicon", "Preñada se reemplaza por la forma actual aplicada a una persona."),
    (21, 22, "juzgaren los árbitros", "determinen los jueces", "archaic-lexicon", "Árbitros designa aquí a los jueces que fijan la sanción."),
    (21, 26, "lo entortare", "lo dañare", "archaic-lexicon", "Entortar significa causar daño al ojo."),
    (21, 28, "de resultas muriere", "a causa de ello muriere", "archaic-phrase", "De resultas significa como consecuencia de la cornada."),
    (21, 29, "le fué hecho requerimiento", "había sido advertido", "archaic-phrase", "La frase significa que el dueño ya había recibido advertencia."),
    (22, 3, "el matador", "el autor de la muerte", "context-reviewed-lexicon", "Matador designa aquí a quien causó la muerte del ladrón."),
    (22, 3, "restituir cumplidamente", "restituir por completo", "archaic-phrase", "Cumplidamente significa completamente."),
    (22, 10, "se perniquebrare", "sufriere algún daño", "archaic-lexicon", "Perniquebrar significa lesionar o quebrar una pata del animal."),
    (22, 16, "engañare á alguna doncella", "sedujere a una mujer virgen", "context-reviewed-phrase", "El contexto legal trata de seducir a una mujer no comprometida, no de cualquier engaño."),
    (22, 19, "tuviere ayuntamiento con bestia", "tuviere relaciones sexuales con un animal", "archaic-idiom", "Ayuntamiento designa aquí una relación sexual."),
    (22, 25, "dinero emprestado", "dinero prestado", "archaic-lexicon", "Emprestado es una forma antigua de prestado."),
    (22, 25, "como logrero", "como prestamista", "archaic-lexicon", "Logrero designa a quien presta buscando ganancia abusiva."),
    (22, 31, "carne arrebatada de las fieras", "carne destrozada por las fieras", "archaic-phrase", "Arrebatada describe aquí carne de un animal despedazado por fieras."),
    (23, 10, "allegarás su cosecha", "recogerás su cosecha", "archaic-lexicon", "Allegar significa reunir o recoger la cosecha."),
    (23, 11, "la dejarás vacante y soltarás", "la dejarás descansar sin cultivarla", "archaic-phrase", "La instrucción es dejar reposar la tierra durante el séptimo año."),
    (23, 13, "seréis avisados", "cumplan", "archaic-phrase", "La frase es una orden de guardar lo dicho, no un anuncio futuro."),
    (23, 15, "fiesta de los ázimos", "fiesta de los panes sin levadura", "archaic-lexicon", "Ázimos son panes sin levadura."),
    (23, 15, "comparecerá vacío", "se presentará con las manos vacías", "archaic-idiom", "Vacío se refiere a presentarse sin ofrenda."),
    (24, 2, "se llegará á Jehová", "se acercará a Jehová", "archaic-lexicon", "Llegarse significa acercarse."),
    (24, 13, "Josué su ministro", "Josué su ayudante", "context-reviewed-lexicon", "Ministro designa aquí al asistente de Moisés."),
    (25, 7, "piedras de engastes", "piedras para engastar", "archaic-phrase", "Se expresa la función de las piedras con una construcción actual."),
    (25, 19, "de la calidad de la cubierta", "de una pieza con la cubierta", "archaic-idiom", "La frase indica que los querubines debían formar una sola pieza con la cubierta."),
    (25, 38, "despabiladeras", "cortapabilos", "archaic-lexicon", "La palabra designa el utensilio para cortar el pabilo de las lámparas."),
    (26, 6, "corchetes", "ganchos", "archaic-lexicon", "Corchetes designa los ganchos que unían las cortinas."),
    (26, 11, "corchetes de alambre", "ganchos de bronce", "context-reviewed-phrase", "Los controles identifican el material como bronce y la función como ganchos de unión."),
    (26, 18, "al lado del mediodía, al austro", "al lado sur", "archaic-direction", "Mediodía y austro designan aquí la misma dirección: el sur."),
    (26, 32, "basas", "bases", "archaic-lexicon", "Basas son las bases sobre las que se levantan las columnas."),
    (26, 35, "al mediodía", "al sur", "archaic-direction", "Mediodía designa aquí la dirección sur."),
    (26, 35, "al lado del aquilón", "al lado norte", "archaic-direction", "Aquilón designa aquí la dirección norte."),
    (27, 13, "por la parte de levante, al oriente", "por el lado oriental, al este", "archaic-direction", "Levante y oriente designan el lado este."),
    (28, 11, "harásles", "les harás", "archaic-enclitic-order", "Se actualiza el orden del pronombre sin cambiar la acción."),
    (28, 37, "por el frente anterior", "por la parte delantera", "archaic-phrase", "Se elimina una duplicación espacial sin cambiar la ubicación."),
    (28, 39, "obra de recamador", "trabajo de bordador", "archaic-lexicon", "Recamador designa al artesano que borda la faja."),
    (28, 40, "chapeos (tiaras)", "tiaras", "archaic-lexicon", "La propia fuente ya aclara el término antiguo; se conserva solo la palabra comprensible."),
    (28, 42, "pañetes de lino para cubrir la carne vergonzosa", "ropa interior de lino para cubrir su desnudez", "archaic-phrase", "Pañetes y carne vergonzosa se expresan con palabras actuales sin cambiar la función de la prenda."),
    (29, 2, "flor de harina", "harina refinada", "archaic-lexicon", "Flor de harina designa harina fina o refinada."),
    (29, 9, "los chapeos (tiaras)", "las tiaras", "archaic-lexicon", "La propia fuente aclara el término antiguo; se conserva tiaras y se ajusta el artículo."),
    (29, 13, "el redaño de sobre el hígado", "la grasa que cubre el hígado", "archaic-lexicon", "Redaño designa la membrana grasa situada sobre el hígado."),
    (29, 20, "la ternilla de la oreja", "el lóbulo de la oreja", "archaic-lexicon", "Ternilla designa aquí el lóbulo de la oreja; se ajusta también el artículo para conservar la concordancia."),
    (29, 23, "una hojaldre amasada con aceite", "una torta de pan amasada con aceite", "context-reviewed-corrupted-lexicon", "El segundo elemento de la lista es una torta de pan hecha con aceite; se conserva su preparación y se corrige la identificación."),
    (29, 23, "una lasaña", "una hojuela", "context-reviewed-corrupted-lexicon", "Lasaña rompe el sentido de la lista; el contexto y los controles identifican una pieza fina de pan sin levadura."),
    (29, 33, "henchir sus manos para ser santificados", "consagrarlos para el sacerdocio", "archaic-idiom", "Llenar las manos es una fórmula antigua de investidura sacerdotal."),
    (29, 38, "sin intermisión", "continuamente", "archaic-lexicon", "Sin intermisión significa sin interrupción."),
    (29, 40, "flor de harina", "harina refinada", "archaic-lexicon", "Flor de harina designa harina fina o refinada."),
    (29, 41, "olor de suavidad", "aroma grato", "archaic-idiom", "La frase describe que el aroma de la ofrenda es agradable."),
    (29, 42, "me concertaré con vosotros", "me reuniré con vosotros", "archaic-lexicon", "Concertarse significa encontrarse o reunirse en este contexto; se conserva la persona verbal del versículo."),
    (29, 43, "allí testificaré de mí á los hijos de Israel", "allí me reuniré con los hijos de Israel", "archaic-phrase", "Testificar de mí no tiene aquí el sentido moderno; ambos controles describen el encuentro de Dios con Israel."),
    (30, 3, "cubrirlo has", "lo cubrirás", "archaic-grammar", "Se actualiza la construcción verbal futura."),
    (30, 4, "varales", "varas", "archaic-lexicon", "Varales designa las varas usadas para transportar el altar."),
    (30, 6, "donde yo te testificaré de mí", "donde me reuniré contigo", "archaic-phrase", "La frase describe el encuentro de Dios con Moisés."),
    (30, 7, "aderezare las lámparas", "prepare las lámparas", "archaic-lexicon", "Aderezar significa preparar las lámparas."),
    (30, 10, "la sangre de la expiación para las reconciliaciones", "la sangre del sacrificio por el pecado", "archaic-phrase", "La frase designa la sangre de la ofrenda anual por el pecado."),
    (30, 13, "óbolos", "geras", "context-reviewed-unit-name", "Los controles de la tradición identifican la subdivisión del siclo como geras."),
    (32, 18, "eco de algazara de fuertes", "gritos de victoria", "context-reviewed-phrase", "La primera voz posible se identifica como gritos de victoria."),
    (32, 18, "eco de alaridos de flacos", "lamentos de derrota", "context-reviewed-phrase", "La segunda voz posible se identifica como lamentos de derrota."),
    (32, 18, "algazara de cantar", "canto", "archaic-phrase", "Moisés concluye que escucha canto, no el resultado de una batalla."),
    (32, 24, "apartadlo", "quítense el oro", "archaic-phrase", "Aarón pide que se quiten las joyas de oro para entregárselas."),
    (32, 33, "raeré", "borraré", "archaic-lexicon", "Raer significa borrar del libro."),
    (33, 7, "cualquiera que requería á Jehová", "cualquiera que buscaba a Jehová", "archaic-lexicon", "Requerir significa buscar o consultar a Jehová en este contexto."),
    (34, 2, "Apercíbete", "Prepárate", "archaic-lexicon", "Apercibirse significa prepararse."),
    (34, 2, "estáme allí", "preséntate allí ante mí", "archaic-phrase", "La orden pide a Moisés estar ante Dios en la cumbre."),
    (34, 6, "grande en benignidad", "grande en misericordia", "context-reviewed-lexicon", "Benignidad expresa aquí el amor misericordioso de Dios."),
    (34, 9, "poséenos", "tómanos como tu herencia", "archaic-idiom", "La petición es que Dios reciba al pueblo como su heredad."),
    (34, 10, "hago concierto", "hago un pacto", "archaic-lexicon", "Concierto designa el pacto que Dios establece."),
    (34, 13, "talaréis sus bosques", "cortarán sus imágenes de Asera", "context-reviewed-phrase", "Bosques designa aquí objetos de culto de Asera, no vegetación común."),
    (34, 18, "fiesta de los ázimos", "fiesta de los panes sin levadura", "archaic-lexicon", "Ázimos son panes sin levadura."),
    (34, 20, "no serán vistos vacíos delante de mí", "nadie se presentará ante mí con las manos vacías", "archaic-idiom", "La instrucción se refiere a no presentarse sin ofrenda."),
    (34, 21, "en el séptimo día cesarás", "en el séptimo día descansarás", "context-reviewed-phrase", "Cesar significa interrumpir el trabajo para descansar."),
    (34, 21, "cesarás aun en la arada y en la siega", "descansarás aun en tiempo de arar y cosechar", "context-reviewed-phrase", "La obligación de descansar también rige durante las labores agrícolas urgentes."),
    (34, 22, "á los principios de la siega", "con las primicias de la cosecha", "archaic-phrase", "Principios designa los primeros frutos de la cosecha."),
    (35, 21, "para toda su fábrica", "para toda su obra", "archaic-lexicon", "Fábrica significa aquí la obra o construcción del santuario."),
    (35, 32, "proyectar inventos", "proyectar diseños", "archaic-lexicon", "Inventos designa los diseños artísticos del artesano."),
    (36, 2, "á llegarse á la obra", "a incorporarse a la obra", "archaic-phrase", "Llegarse significa acercarse para participar en el trabajo."),
    (36, 5, "lo que es menester", "lo que se necesita", "archaic-phrase", "Ser menester significa ser necesario."),
    (36, 6, "fué el pueblo impedido de ofrecer", "el pueblo dejó de llevar ofrendas", "archaic-phrase", "La orden detuvo las ofrendas adicionales."),
    (36, 18, "corchetes", "ganchos", "archaic-lexicon", "Corchetes designa los ganchos que unían las cortinas."),
    (36, 22, "quicios enclavijados", "espigas paralelas", "archaic-technical-phrase", "La frase describe las dos piezas paralelas de unión de cada tabla."),
    (36, 23, "al lado del austro, al mediodía", "al lado sur", "archaic-direction", "Austro y mediodía designan la misma dirección: el sur."),
    (36, 37, "obra de recamador", "trabajo de bordador", "archaic-lexicon", "Recamador designa al artesano que bordó la cortina."),
    (37, 23, "despabiladeras", "cortapabilos", "archaic-lexicon", "La palabra designa el utensilio para cortar el pabilo de las lámparas."),
    (38, 13, "á la parte oriental, al levante", "al lado oriental, al este", "archaic-direction", "Levante y oriental designan el lado este."),
    (39, 6, "piedras oniquinas", "piedras de ónice", "archaic-lexicon", "Oniquinas significa de ónice."),
    (39, 28, "los adornos de los chapeos (tiaras)", "los adornos de las tiaras", "archaic-lexicon", "La propia fuente aclara el término antiguo; se conserva tiaras y se ajusta la frase completa."),
    (39, 28, "los pañetes de lino", "la ropa interior de lino", "archaic-lexicon", "Pañetes designa la ropa interior sacerdotal; se ajusta también el artículo."),
    (39, 30, "el rótulo", "la inscripción", "archaic-lexicon", "Rótulo designa el texto grabado en la placa."),

    # Segunda lectura completa: formas y frases que el inventario léxico inicial no detectó.
    (2, 23, "suspiraron á causa de la servidumbre", "gemían a causa de la servidumbre", "context-reviewed-phrase", "El contexto describe el sufrimiento continuo de Israel bajo la esclavitud."),
    (3, 21, "no salgáis vacíos", "no salgáis con las manos vacías", "archaic-idiom", "Vacíos significa aquí salir sin bienes; ambos controles hacen explícita la expresión."),
    (5, 11, "donde la hallareis", "donde la encuentren", "archaic-grammar", "Se actualiza la forma verbal sin cambiar la instrucción de recoger paja."),
    (10, 1, "he agravado su corazón", "he endurecido su corazón", "context-reviewed-lexicon", "El contexto describe la obstinación del faraón, igual que en los pasajes paralelos ya revisados."),
    (10, 4, "rehusas dejarlo ir", "te niegas a dejarlo ir", "archaic-phrase", "Rehusar expresa aquí la negativa persistente del faraón."),
    (10, 6, "llenarse han tus casas", "se llenarán tus casas", "archaic-grammar", "Se actualiza la construcción futura separada."),
    (11, 2, "demande á su vecino", "pida a su vecino", "archaic-lexicon", "Demandar significa pedir en este diálogo."),
    (12, 5, "tomaréislo", "lo tomaréis", "archaic-enclitic-order", "Se actualiza el orden del pronombre y se conserva la misma persona verbal del mandato."),
    (14, 22, "á su diestra y á su siniestra", "a su derecha y a su izquierda", "archaic-direction", "Diestra y siniestra designan los lados derecho e izquierdo."),
    (14, 29, "á su diestra y á su siniestra", "a su derecha y a su izquierda", "archaic-direction", "Diestra y siniestra designan los lados derecho e izquierdo."),
    (15, 15, "abatirse han todos los moradores de Canaán", "se acobardarán todos los habitantes de Canaán", "archaic-phrase", "Se actualiza el futuro separado; el paralelismo describe la pérdida de ánimo de los cananeos."),
    (15, 22, "mar Bermejo", "Mar Rojo", "archaic-place-name", "Bermejo es el nombre antiguo usado aquí para el Mar Rojo."),
    (16, 3, "decíanles los hijos de Israel", "les decían los hijos de Israel", "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito."),
    (16, 12, "os hartaréis de pan", "os saciaréis de pan", "archaic-lexicon", "Hartarse significa quedar satisfechos de alimento; saciarse conserva el sentido y la persona verbal."),
    (16, 14, "como una helada", "como escarcha", "context-reviewed-lexicon", "La comparación describe los copos finos semejantes a la escarcha sobre la tierra."),
    (18, 26, "traíanlo á Moisés", "lo traían a Moisés", "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito."),
    (19, 21, "porque caerá multitud de ellos", "para que no mueran muchos de ellos", "archaic-idiom", "Caer significa aquí perder la vida al traspasar el límite."),
    (21, 4, "ella le hubiere parido hijos ó hijas", "ella le hubiere dado hijos o hijas", "archaic-phrase", "La frase se refiere a los hijos nacidos de la mujer que el amo le dio."),
    (22, 29, "No dilatarás la primicia", "No tardarás en ofrecer la primicia", "archaic-phrase", "Dilatar significa demorar la presentación de la ofrenda."),
    (23, 5, "le dejarás entonces desamparado", "lo dejarás entonces sin ayuda", "archaic-phrase", "Desamparado significa aquí dejar al animal caído sin ayudarlo."),
    (23, 17, "parecerá todo varón tuyo", "se presentará todo varón tuyo", "archaic-lexicon", "Parecer significa comparecer o presentarse ante Dios en este contexto."),
    (23, 24, "quebrantarás enteramente sus estatuas", "quebrarás por completo sus estatuas", "archaic-phrase", "Se expresa en forma actual la orden de destruir por completo esos objetos de culto."),
    (24, 3, "Ejecutaremos todas las palabras", "Haremos todo lo", "archaic-phrase", "Ejecutar las palabras significa obedecer y hacer todo lo que Jehová dijo."),
    (24, 6, "púsola en tazones", "la puso en tazones", "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito."),
    (24, 14, "lléguese á ellos", "acuda a ellos", "archaic-phrase", "Llegarse a Aarón y Hur significa acudir a ellos con un asunto."),
    (25, 25, "Hacerle has también", "Le harás también", "archaic-grammar", "Se actualiza la construcción futura separada."),
    (25, 25, "en circunferencia", "alrededor", "archaic-lexicon", "La frase describe una cornisa que rodea la moldura."),
    (26, 13, "cargará sobre los lados", "colgará sobre los lados", "context-reviewed-lexicon", "La tela sobrante cuelga sobre ambos lados del tabernáculo."),
    (28, 1, "allega á ti á Aarón", "acerca a ti a Aarón", "archaic-phrase", "Allegar significa acercar o hacer comparecer."),
    (28, 9, "piedras oniquinas", "piedras de ónice", "archaic-lexicon", "Oniquinas significa de ónice."),
    (29, 14, "su pellejo", "su piel", "archaic-lexicon", "Pellejo designa aquí la piel del becerro."),
    (29, 20, "la ternilla de las orejas de sus hijos", "el lóbulo de la oreja de sus hijos", "archaic-lexicon", "Ternilla designa aquí el lóbulo de la oreja; se ajustan artículo y número para conservar la concordancia."),
    (29, 22, "el redaño del hígado", "la grasa del hígado", "archaic-lexicon", "Redaño designa la parte grasa asociada al hígado en la lista ritual."),
    (29, 24, "lo mecerás agitándolo", "lo mecerás como ofrenda", "archaic-phrase", "El movimiento corresponde a la presentación ritual de una ofrenda mecida."),
    (29, 27, "la espaldilla de la santificación", "la espaldilla de la ofrenda elevada", "context-reviewed-phrase", "El paralelismo distingue la ofrenda mecida de la porción elevada."),
    (29, 30, "el sacerdote de sus hijos, que en su lugar viniere al tabernáculo", "el sacerdote descendiente suyo que ocupe su lugar cuando venga al tabernáculo", "archaic-phrase", "Se aclara que se trata del descendiente que suceda a Aarón como sacerdote y entre a servir."),
    (30, 3, "su techado", "su cubierta", "archaic-lexicon", "Techado designa aquí la superficie superior del altar."),
    (30, 5, "los varales", "las varas", "archaic-lexicon", "Varales designa las varas usadas para transportar el altar."),
    (30, 12, "cuando los contares", "cuando los cuentes", "archaic-grammar", "Se actualiza la forma verbal sin alterar la instrucción del censo."),
    (30, 14, "pasare por la cuenta", "sea contado", "archaic-phrase", "La expresión designa a toda persona incluida en el censo."),
    (30, 35, "una confección aromática", "un incienso aromático", "archaic-phrase", "La mezcla descrita es el incienso sagrado, no una confección en el sentido actual."),
    (30, 36, "molerás alguna de ella pulverizándola", "molerás parte de ella hasta hacerla polvo", "archaic-phrase", "Se expresa directamente la preparación de una parte de la mezcla."),
    (30, 36, "donde yo te testificaré de mí", "donde me reuniré contigo", "archaic-phrase", "La frase describe el encuentro de Dios con Moisés."),
    (30, 37, "Como la confección que harás", "Como este incienso que harás", "archaic-phrase", "Confección designa aquí el incienso cuya fórmula no debía reproducirse."),
    (30, 38, "para olerla", "para disfrutar de su aroma", "archaic-phrase", "El propósito prohibido es fabricar la mezcla para uso aromático personal."),
    (32, 3, "trajéronlos á Aarón", "los trajeron a Aarón", "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito."),
    (32, 13, "y dícholes", "y les dijiste", "archaic-enclitic-order", "Se actualiza la forma verbal y el orden del pronombre."),
    (32, 19, "enardeciósele la ira á Moisés", "se encendió la ira de Moisés", "archaic-phrase", "La frase describe la reacción de Moisés al ver el becerro y las danzas."),
    (32, 25, "el pueblo estaba despojado, porque Aarón lo había despojado", "el pueblo estaba desenfrenado, porque Aarón lo había permitido", "context-reviewed-phrase", "El contexto trata del descontrol del pueblo que Aarón permitió, no de que estuvieran sin ropa o bienes."),
    (32, 31, "Ruégote", "Te ruego", "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito."),
    (32, 34, "en el día de mi visitación yo visitaré en ellos su pecado", "en el día del castigo, los castigaré por su pecado", "archaic-idiom", "Visitación designa aquí el momento en que Dios castigará el pecado."),
    (33, 4, "esta sensible palabra", "esta mala noticia", "archaic-phrase", "Sensible significa aquí dolorosa o mala, como muestra la reacción de luto."),
    (33, 18, "Ruégote", "Te ruego", "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito."),
    (35, 22, "sortijas", "anillos", "archaic-lexicon", "Sortijas designa anillos dentro de la lista de joyas ofrecidas."),
    (37, 14, "se metiesen las varas", "se introdujeran las varas", "archaic-lexicon", "La frase describe introducir las varas en los anillos para transportar la mesa."),
    (39, 21, "no se apartase el racional del ephod", "no se separara el pectoral del efod", "archaic-phrase", "Racional y ephod se expresan con las formas actuales usadas en el mismo contexto sacerdotal."),
    (40, 32, "se llegaban al altar", "se acercaban al altar", "archaic-phrase", "Llegarse significa acercarse."),

    (6, 20, "la cual le parió á Aarón y á Moisés", "quien dio a luz a Aarón y a Moisés", "archaic-phrase", "Dar a luz expresa la misma acción con uso actual."),
    (6, 25, "la cual le parió á Phinees", "quien dio a luz a Phinees", "archaic-phrase", "Dar a luz expresa la misma acción con uso actual."),
    (15, 8, "paráronse las corrientes", "se detuvieron las corrientes", "archaic-enclitic-order", "La forma antigua describe que las corrientes quedaron inmóviles."),
    (15, 9, "Perseguiré, prenderé", "Perseguiré, los alcanzaré", "context-reviewed-lexicon", "Prender significa aquí alcanzar o apresar al pueblo perseguido."),
    (16, 3, "las ollas de las carnes", "las ollas de carne", "archaic-phrase", "Se actualiza la expresión sin cambiar el alimento recordado por el pueblo."),
    (16, 31, "simiente de culantro", "semilla de cilantro", "archaic-lexicon", "La comparación del maná se refiere a la semilla de cilantro."),
    (16, 36, "epha", "efa", "archaic-orthography", "Se usa la transliteración actual de la unidad de medida."),
    (17, 14, "del todo tengo de raer la memoria de Amalec", "borraré por completo la memoria de Amalec", "archaic-phrase", "Raer significa borrar; se actualiza también la construcción verbal."),
    (20, 25, "si alzares tu pico sobre él", "si usas una herramienta sobre él", "archaic-idiom", "Pico designa aquí la herramienta que labraría la piedra del altar."),
    (20, 26, "porque tu desnudez no sea junto á él descubierta", "para que tu desnudez no quede expuesta junto a él", "archaic-phrase", "Se actualiza el orden de la cláusula y se conserva la razón de no usar gradas."),
    (22, 5, "hiciere pacer campo ó viña", "hiciere pastar en campo o viña", "archaic-phrase", "Pacer describe aquí al ganado que pasta en el terreno."),
    (22, 6, "fuere quemado montón, ó haza, ó campo", "se queme el grano amontonado, el cultivo en pie o el campo", "archaic-phrase", "Haza designa aquí el cultivo que todavía está en pie; se aclara la lista de daños por fuego."),
    (22, 27, "el vestido para cubrir sus carnes", "la ropa para cubrir su cuerpo", "archaic-phrase", "Carnes designa aquí el cuerpo de la persona necesitada."),
    (23, 18, "el sebo de mi víctima", "la grasa de mi víctima", "archaic-lexicon", "Sebo designa aquí la grasa reservada para la ofrenda."),
    (25, 6, "sahumerio aromático", "incienso aromático", "archaic-lexicon", "Sahumerio designa aquí el incienso aromático."),
    (25, 37, "hacerle has siete candilejas", "le harás siete lámparas", "archaic-phrase", "Se actualizan la construcción futura y el nombre de las lámparas."),
    (26, 1, "querubines de obra delicada", "querubines bordados artísticamente", "archaic-phrase", "La frase describe el trabajo artístico con que se bordaron los querubines."),
    (26, 19, "cuarenta basas de plata", "cuarenta bases de plata", "archaic-technical-lexicon", "Basas son las bases que sostienen las tablas."),
    (26, 19, "dos basas debajo de la una tabla para sus dos quicios", "dos bases debajo de una tabla para sus dos espigas", "archaic-technical-phrase", "Se actualizan los nombres de las bases y las piezas de unión."),
    (26, 19, "dos basas debajo de la otra tabla para sus dos quicios", "dos bases debajo de la otra tabla para sus dos espigas", "archaic-technical-phrase", "Se actualizan los nombres de las bases y las piezas de unión."),
    (26, 21, "cuarenta basas de plata", "cuarenta bases de plata", "archaic-technical-lexicon", "Basas son las bases que sostienen las tablas."),
    (26, 21, "dos basas debajo de la una tabla", "dos bases debajo de una tabla", "archaic-technical-phrase", "Basas son las bases que sostienen las tablas."),
    (26, 21, "dos basas debajo de la otra tabla", "dos bases debajo de la otra tabla", "archaic-technical-phrase", "Basas son las bases que sostienen las tablas."),
    (26, 25, "sus basas de plata", "sus bases de plata", "archaic-technical-lexicon", "Basas son las bases que sostienen las tablas."),
    (26, 25, "diez y seis basas", "dieciséis bases", "archaic-technical-phrase", "Se actualizan el número compuesto y el nombre de las piezas."),
    (26, 25, "dos basas debajo de la una tabla", "dos bases debajo de una tabla", "archaic-technical-phrase", "Basas son las bases que sostienen las tablas."),
    (26, 25, "dos basas debajo de la otra tabla", "dos bases debajo de la otra tabla", "archaic-technical-phrase", "Basas son las bases que sostienen las tablas."),
    (26, 37, "hacerlas has de fundición cinco basas de metal", "fundirás para ellas cinco bases de metal", "archaic-phrase", "Se actualiza la construcción futura y el nombre de las piezas de apoyo."),
    (29, 1, "sin tacha", "sin defecto", "archaic-lexicon", "Sin tacha significa que los animales no tenían defecto."),
    (29, 13, "todo el sebo que cubre los intestinos", "toda la grasa que cubre los intestinos", "archaic-lexicon", "Sebo designa aquí la grasa indicada para el sacrificio."),
    (29, 13, "el sebo que está sobre ellos", "la grasa que está sobre ellos", "archaic-lexicon", "Sebo designa aquí la grasa de los riñones."),
    (29, 22, "del carnero el sebo", "del carnero la grasa", "archaic-lexicon", "Sebo designa aquí la grasa del carnero."),
    (29, 22, "el sebo que cubre los intestinos", "la grasa que cubre los intestinos", "archaic-lexicon", "Sebo designa aquí la grasa indicada para el sacrificio."),
    (29, 22, "el sebo que está sobre ellos", "la grasa que está sobre ellos", "archaic-lexicon", "Sebo designa aquí la grasa de los riñones."),
    (29, 9, "el sacerdocio por fuero perpetuo", "el sacerdocio por derecho perpetuo", "archaic-lexicon", "Fuero significa aquí un derecho permanente."),
    (29, 40, "un epha", "un efa", "archaic-orthography", "Se usa la transliteración actual de la unidad de medida."),
    (30, 1, "de sahumerio de", "para quemar", "archaic-phrase", "La frase describe la función del altar sin repetir incienso."),
    (30, 7, "sahumerio de aroma", "incienso aromático", "archaic-phrase", "Sahumerio de aroma designa el incienso aromático."),
    (30, 8, "quemará el sahumerio", "quemará incienso", "archaic-lexicon", "Sahumerio designa aquí el incienso ofrecido en el altar."),
    (30, 9, "sahumerio extraño", "incienso extraño", "archaic-lexicon", "Sahumerio designa aquí un incienso no autorizado."),
    (32, 13, "vuestra simiente como las estrellas", "su descendencia como las estrellas", "archaic-phrase", "Simiente designa la descendencia de los patriarcas; se actualiza también la persona gramatical del discurso."),
    (32, 13, "á vuestra simiente toda esta tierra", "a su descendencia toda esta tierra", "archaic-phrase", "Simiente designa la descendencia de los patriarcas; se actualiza también la persona gramatical del discurso."),
    (35, 14, "El candelero de la luminaria", "El candelabro del alumbrado", "archaic-technical-phrase", "Se actualizan los nombres del objeto y su función."),
    (35, 14, "el aceite para la luminaria", "el aceite para el alumbrado", "archaic-technical-phrase", "La frase designa el aceite destinado a las lámparas."),
    (36, 1, "HIZO, pues", "Así, pues", "context-reviewed-corrupted-verb-phrase", "Los controles y el contexto continúan la instrucción sobre quienes harán la obra; HIZO deja la oración sin verbo principal coherente."),
    (36, 1, "para que supiesen hacer", "para saber hacer", "archaic-phrase", "Se actualiza la construcción que describe la capacidad concedida por Dios."),
    (36, 1, "todas las cosas que había mandado Jehová", "harán todo lo que Jehová ha mandado", "context-reviewed-corrupted-verb-phrase", "Se restituye el verbo principal futuro que concuerda con el mandato y con los controles."),
    (36, 24, "cuarenta basas de plata", "cuarenta bases de plata", "archaic-technical-lexicon", "Basas son las bases que sostienen las tablas."),
    (36, 24, "dos basas debajo de la una tabla para sus dos quicios", "dos bases debajo de una tabla para sus dos espigas", "archaic-technical-phrase", "Se actualizan los nombres de las bases y las piezas de unión."),
    (36, 24, "dos basas debajo de la otra tabla para sus dos quicios", "dos bases debajo de la otra tabla para sus dos espigas", "archaic-technical-phrase", "Se actualizan los nombres de las bases y las piezas de unión."),
    (36, 26, "cuarenta basas de plata", "cuarenta bases de plata", "archaic-technical-lexicon", "Basas son las bases que sostienen las tablas."),
    (36, 26, "dos basas debajo de la una tabla", "dos bases debajo de una tabla", "archaic-technical-phrase", "Basas son las bases que sostienen las tablas."),
    (36, 26, "dos basas debajo de la otra tabla", "dos bases debajo de la otra tabla", "archaic-technical-phrase", "Basas son las bases que sostienen las tablas."),
    (36, 30, "sus basas de plata dieciséis", "sus bases de plata dieciséis", "archaic-technical-lexicon", "Basas son las bases que sostienen las tablas."),
    (36, 30, "dos basas debajo de cada tabla", "dos bases debajo de cada tabla", "archaic-technical-phrase", "Basas son las bases que sostienen las tablas."),
    (36, 35, "querubines de delicada obra", "querubines bordados artísticamente", "archaic-phrase", "La frase describe el trabajo artístico con que se bordaron los querubines."),
    (37, 12, "en circunferencia", "alrededor", "archaic-lexicon", "La frase describe una cornisa que rodeaba la moldura."),
    (38, 18, "de obra de recamado", "bordada artísticamente", "archaic-phrase", "La frase describe el trabajo artístico de la cortina de entrada."),
    (38, 27, "las basas del santuario y las basas del velo", "las bases del santuario y las bases del velo", "archaic-technical-phrase", "Basas son las bases fundidas para sostener el santuario y el velo."),
    (38, 27, "en cien basas cien talentos", "en cien bases cien talentos", "archaic-technical-phrase", "Basas son las bases fundidas con la plata contabilizada."),
    (38, 31, "las basas del atrio alrededor", "las bases del atrio alrededor", "archaic-technical-phrase", "Basas son las bases que sostienen las columnas del atrio."),
    (38, 31, "las basas de la puerta del atrio", "las bases de la puerta del atrio", "archaic-technical-phrase", "Basas son las bases que sostienen la entrada del atrio."),
    (39, 3, "con delicada obra", "con trabajo artístico", "archaic-phrase", "La frase describe el tejido artístico de los hilos de oro."),
    (39, 21, "el racional de sus anillos á los anillos del ephod", "el pectoral por sus anillos a los anillos del efod", "archaic-technical-phrase", "Se actualizan los nombres de las piezas sacerdotales y la relación entre sus anillos."),
    (39, 21, "cinto del mismo ephod", "cinto del mismo efod", "archaic-orthography", "Se usa la grafía actual efod."),
    (39, 29, "obra de recamador", "trabajo de bordador", "archaic-lexicon", "Recamador designa al artesano que bordó la faja."),
    (39, 34, "velo del pabellón", "velo del frente", "archaic-technical-phrase", "La frase identifica la cortina frontal que protegía el interior."),
    (28, 23, "en el racional dos anillos de oro", "en el pectoral dos anillos de oro", "archaic-technical-phrase", "Racional designa aquí el pectoral sacerdotal."),
    (28, 23, "á las dos puntas del racional", "a los dos extremos del pectoral", "archaic-technical-phrase", "Se actualizan el nombre del pectoral y la ubicación de los anillos."),
    (28, 27, "á los dos lados del ephod", "a los dos lados del efod", "archaic-orthography", "Se usa la grafía actual efod."),
    (28, 27, "sobre el cinto del ephod", "sobre el cinto del efod", "archaic-orthography", "Se usa la grafía actual efod."),
    (28, 28, "el racional con sus anillos á los anillos del ephod", "el pectoral con sus anillos a los anillos del efod", "archaic-technical-phrase", "Se actualizan los nombres de las piezas sacerdotales."),
    (28, 28, "sobre el cinto del ephod", "sobre el cinto del efod", "archaic-orthography", "Se usa la grafía actual efod."),
    (28, 28, "el racional del ephod", "el pectoral del efod", "archaic-technical-phrase", "Se actualizan los nombres de las piezas sacerdotales."),
    (29, 5, "el manto del ephod", "el manto del efod", "archaic-orthography", "Se usa la grafía actual efod."),
    (29, 5, "y el ephod", "y el efod", "archaic-orthography", "Se usa la grafía actual efod."),
    (29, 5, "el cinto del ephod", "el cinto del efod", "archaic-orthography", "Se usa la grafía actual efod."),
    (39, 20, "las dos hombreras del ephod", "las dos hombreras del efod", "archaic-orthography", "Se usa la grafía actual efod."),
    (39, 20, "sobre el cinto del ephod", "sobre el cinto del efod", "archaic-orthography", "Se usa la grafía actual efod."),
    (27, 16, "un pabellón", "una cortina", "archaic-technical-lexicon", "Pabellón designa aquí la cortina de la entrada del atrio."),
    (35, 15, "el pabellón", "la cortina", "archaic-technical-lexicon", "Pabellón designa aquí la cortina de entrada del tabernáculo."),
    (35, 17, "el pabellón", "la cortina", "archaic-technical-lexicon", "Pabellón designa aquí la cortina de la entrada del atrio."),
    (38, 18, "el pabellón", "la cortina", "archaic-technical-lexicon", "Pabellón designa aquí la cortina de la entrada del atrio."),
    (39, 38, "el pabellón", "la cortina", "archaic-technical-lexicon", "Pabellón designa aquí la cortina de entrada del tabernáculo."),
    (39, 40, "el pabellón", "la cortina", "archaic-technical-lexicon", "Pabellón designa aquí la cortina de la entrada del atrio."),
    (40, 5, "el pabellón", "la cortina", "archaic-technical-lexicon", "Pabellón designa aquí la cortina de entrada del tabernáculo."),
    (40, 8, "el pabellón", "la cortina", "archaic-technical-lexicon", "Pabellón designa aquí la cortina de la entrada del atrio."),
    (40, 22, "del pabellón", "de la cortina", "archaic-technical-phrase", "Pabellón designa aquí la cortina que separaba el espacio."),
    (40, 24, "del pabellón", "de la cortina", "archaic-technical-phrase", "Pabellón designa aquí la cortina que separaba el espacio."),
    (4, 9, "y volverse han aquellas aguas que tomarás del río,", "y aquellas aguas que tomarás del río", "archaic-grammar", "Se elimina la construcción futura duplicada y se conserva una sola cláusula: las aguas se volverán sangre."),
    (2, 2, "y viéndolo que era hermoso", "y al ver que era hermoso", "archaic-phrase", "Se actualiza la construcción temporal sin cambiar la percepción de la madre."),
    (2, 5, "y paseándose sus doncellas por la ribera del río", "mientras sus doncellas se paseaban por la ribera del río", "archaic-phrase", "Se aclara que las doncellas caminaban por la ribera mientras la hija de Faraón se bañaba."),
    (9, 8, "y espárzala Moisés hacia el cielo", "y que Moisés la esparza hacia el cielo", "archaic-phrase", "Se actualiza el orden de la instrucción sin cambiar quién esparce la ceniza."),
    (12, 39, "por cuanto echándolos los Egipcios, no habían podido detenerse, ni aun prepararse comida", "pues los egipcios los echaron sin darles tiempo ni siquiera para prepararse comida", "archaic-phrase", "Se actualiza la construcción causal y se conserva que la salida apresurada impidió preparar alimentos."),
    (36, 22, "el uno delante del otro", "una junto a la otra", "archaic-grammar", "La concordancia se ajusta a las dos espigas descritas en la misma oración."),
    (22, 8, "la hacienda de su prójimo", "los bienes de su prójimo", "archaic-lexicon", "Hacienda designa aquí los bienes de otra persona; se ajustan artículo y número."),
    (22, 11, "la hacienda de su prójimo", "los bienes de su prójimo", "archaic-lexicon", "Hacienda designa aquí los bienes de otra persona; se ajustan artículo y número."),
    (25, 6, "Aceite para la luminaria", "Aceite para el alumbrado", "archaic-technical-phrase", "La frase designa el aceite destinado a las lámparas."),
    (27, 20, "para la luminaria", "para el alumbrado", "archaic-technical-phrase", "La frase designa el aceite destinado a las lámparas."),
    (35, 8, "aceite para la luminaria", "aceite para el alumbrado", "archaic-technical-phrase", "La frase designa el aceite destinado a las lámparas."),
    (35, 28, "para la luminaria", "para el alumbrado", "archaic-technical-phrase", "La frase designa el aceite destinado a las lámparas."),
    (39, 37, "aceite para la luminaria", "aceite para el alumbrado", "archaic-technical-phrase", "La frase designa el aceite destinado a las lámparas."),
]


PENDING = [
    (1, 21, "él les hizo casas", "Las referencias explican el hebraísmo como prosperar familias o conceder descendencia; requiere decidir cuánto explicitar."),
    (3, 19, "sino por mano fuerte", "La imagen puede referirse a la fuerza de Faraón o a la intervención poderosa de Dios; no se simplifica sin resolver el sujeto."),
    (4, 24, "Jehová le salió al encuentro, y quiso matarlo", "El referente de los pronombres en 4:24-26 es discutido y no debe resolverse mediante una paráfrasis automática."),
    (4, 25, "esposo de sangre", "La expresión depende del episodio de la circuncisión y necesita nota explicativa antes que sustitución."),
    (13, 13, "le degollarás", "RVR1960 y NVI describen quebrar el cuello; la fuente RV1909 presenta una acción distinta y requiere cotejo textual."),
    (22, 28, "No insultarás á los jueces", "NVI entiende Dios donde la tradición Reina-Valera dice jueces; se conserva hasta revisión textual."),
    (26, 1, "cárdeno", "El color se vierte como azul en los controles, pero la terminología de todo el conjunto textil debe cambiarse de forma coherente."),
    (28, 20, "ligurio", "Las identificaciones modernas de la piedra divergen; no se sustituye sin estudio mineralógico y textual."),
    (30, 34, "estoraque, uña aromática, gálbano", "Son sustancias antiguas específicas; una nota puede ayudar más que reemplazar los nombres."),
    (34, 7, "de ningún modo justificará al malvado", "La relación entre perdón y justicia debe revisarse como cláusula completa, no modernizarse por una palabra."),
]


def verse_map(document):
    return {(c["chapter"], v["verse"]): v["text"] for c in document["chapters"] for v in c["verses"]}


def apply_layer(text, patch):
    for edit in sorted(patch.get("edits", []), key=lambda e: e["startOffset"], reverse=True):
        text = text[: edit["startOffset"]] + edit["replacement"] + text[edit["endOffset"] :]
    return text


def main():
    book = json.loads(BOOK_PATH.read_text(encoding="utf-8"))
    source = verse_map(book)
    layer = json.loads(LAYER_PATH.read_text(encoding="utf-8"))
    patches = {(v["chapter"], v["verse"]): v for v in layer["verses"]}
    current = {ref: apply_layer(text, patches.get(ref, {})) for ref, text in source.items()}

    entries = []
    occupied = {(v["chapter"], v["verse"]): v.get("edits", []) for v in layer["verses"]}

    def add(chapter, verse, expected, replacement, category, reason):
        rendered = current[(chapter, verse)]
        pattern = re.compile(rf"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ]){re.escape(expected)}(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])") if expected.isalpha() else None
        rendered_matches = list(pattern.finditer(rendered)) if pattern else []
        rendered_count = len(rendered_matches) if pattern else rendered.count(expected)
        assert rendered_count == 1, (chapter, verse, expected, rendered)
        original = source[(chapter, verse)]
        original_matches = list(pattern.finditer(original)) if pattern else []
        original_count = len(original_matches) if pattern else original.count(expected)
        assert original_count == 1, (chapter, verse, expected, original)
        start = original_matches[0].start() if pattern else original.index(expected)
        end = start + len(expected)
        assert not any(e["startOffset"] < end and start < e["endOffset"] for e in occupied.get((chapter, verse), [])), (chapter, verse, expected, "overlap")
        entries.append({
            "book": "EXO", "chapter": chapter, "verse": verse,
            "expected": expected, "replacement": replacement,
            "category": category, "reason": reason,
            "evidence": [
                {"label": "Control contextual RVR1960", "url": f"https://www.biblegateway.com/passage/?search=Exodus+{chapter}%3A{verse}&version=RVR1960"},
                {"label": "Control contextual NVI", "url": f"https://www.biblegateway.com/passage/?search=Exodus+{chapter}%3A{verse}&version=NVI"},
            ],
        })

    # Every remaining mas/Mas/MAS in Exodus was read in its full verse and is adversative.
    for ref, text in current.items():
        for expected, replacement in (("MAS", "Pero"), ("Mas", "Pero"), ("mas", "pero")):
            if text.count(expected) == 1:
                before = text[text.index(expected) - 1] if text.index(expected) else ""
                after = text[text.index(expected) + len(expected)] if text.index(expected) + len(expected) < len(text) else ""
                if not before.isalpha() and not after.isalpha():
                    add(*ref, expected, replacement, "archaic-connector", "Mas tiene valor adversativo en este versículo completo; pero conserva la relación entre las cláusulas.")

    for expected, replacement in FINITE_ENCLITICS.items():
        for ref, text in current.items():
            if len(list(re.finditer(rf"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ]){re.escape(expected)}(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])", text))) == 1:
                add(*ref, expected, replacement, "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito según el español actual, sin cambiar la acción, sus participantes ni el contenido del versículo.")

    for expected, (replacement, category, reason) in UNIFORM_TERMS.items():
        for ref, rendered in current.items():
            if (expected, *ref) in UNIFORM_EXCLUSIONS:
                continue
            matches = list(re.finditer(rf"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ]){re.escape(expected)}(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])", rendered))
            if len(matches) == 1:
                add(*ref, expected, replacement, category, reason)

    for item in CHANGES:
        add(*item)

    change_set = {
        "format": "shine-reading-2026-editorial-change-set",
        "schemaVersion": 1,
        "contentVersion": 16,
        "generatedAt": "2026-09-11T00:00:00.000Z",
        "issuedAt": "2026-09-11T00:00:00.000Z",
        "expiresAt": "2028-09-11T00:00:00.000Z",
        "sourceVersionId": "RV1909",
        "filterId": "RV1909-LECTURA-2026",
        "changes": entries,
        "pendingReview": [
            {"book": "EXO", "chapter": ch, "verse": vs, "term": term, "reason": reason}
            for ch, vs, term, reason in PENDING
        ],
    }
    CHANGE_SET.write_text(json.dumps(change_set, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    pending = [entry for entry in registry["pending"] if not entry.get("id", "").startswith("exodus-v16-")]
    for index, (chapter, verse, term, reason) in enumerate(PENDING, 1):
        pending.append({
            "id": f"exodus-v16-{index}",
            "status": "pending-review",
            "scope": "old-testament",
            "term": term,
            "proposedOptions": ["Mantener con nota explicativa", "Actualizar tras revisión textual"],
            "reason": reason,
            "references": [{"book": "EXO", "chapter": chapter, "verse": verse}],
            "evidence": [{
                "label": "Control contextual RVR1960 y NVI",
                "url": f"https://www.biblegateway.com/passage/?search=Exodus+{chapter}%3A{verse}&version=RVR1960%3BNVI",
            }],
        })
    registry.update({
        "updatedAt": "2026-09-11T00:00:00.000Z",
        "activeChangeSet": "editorial-changes/v16.json",
        "pending": pending,
    })
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changes": len(entries), "pending": len(PENDING), "output": str(CHANGE_SET)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
