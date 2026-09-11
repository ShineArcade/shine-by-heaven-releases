import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK_PATH = ROOT / "apps/mobile/assets/bibles/rv1909/books/LEV.json"
LAYER_PATH = ROOT / "apps/mobile/assets/bible_direction/leviticus_reading_2026.rv1909.v1.json"
CHANGE_SET = ROOT / "editorial-changes/v17.json"
REGISTRY = ROOT / "editorial-review/registry.json"


# Decisions in this file were made after a chapter-by-chapter reading of all 859
# verses. The loops below only apply already-approved decisions to the explicitly
# reviewed Leviticus occurrences; they are not a lexical search-and-replace pass.
UNIFORM = {
    "palominos": ("pichones de paloma", "archaic-animal-name", "Palominos significa pichones de paloma en estas ofrendas."),
    "palomino": ("pichón de paloma", "archaic-animal-name", "Palomino significa pichón de paloma en esta ofrenda."),
    "flor de harina": ("harina fina", "archaic-food-term", "Flor de harina designa harina fina en estas ofrendas."),
    "epha": ("efa", "archaic-orthography", "Se usa la grafía moderna efa para la medida hebrea."),
    "en derredor": ("alrededor", "archaic-location", "En derredor significa alrededor."),
    "por yerro": ("involuntariamente", "archaic-legal-term", "Por yerro indica que la falta se cometió sin intención."),
    "sacrificio de paces": ("sacrificio de paz", "archaic-ritual-term", "Sacrificio de paz conserva la categoría ritual con una forma actual."),
    "sacrificio de las paces": ("sacrificio de paz", "archaic-ritual-term", "Sacrificio de paz conserva la categoría ritual con una forma actual."),
    "los ijares": ("los lomos", "archaic-anatomy", "Ijares designa los lomos del animal en esta instrucción anatómica."),
    "la espaldilla derecha": ("la pierna derecha", "archaic-anatomy", "Espaldilla designa aquí la pierna derecha reservada para el sacerdote."),
    "ofrenda agitada": ("ofrenda mecida", "archaic-ritual-term", "Ofrenda mecida expresa el gesto ritual que el propio contexto describe con el verbo mecer."),
    "pan leudo": ("pan con levadura", "archaic-food-term", "Leudo significa que el pan contiene levadura."),
    "Aquesta": ("Esta", "archaic-demonstrative", "Aquesta es una forma antigua de esta."),
    "pacto sempiterno": ("pacto perpetuo", "archaic-lexicon", "Sempiterno significa perpetuo en esta fórmula del pacto."),
    "casa de morada": ("casa de habitación", "archaic-lexicon", "Casa de morada significa casa de habitación."),
    "piedra pintada": ("piedra con imagen", "archaic-idolatry-term", "La frase designa una piedra con una imagen ante la cual se inclinan."),
    "óbolos": ("geras", "archaic-measure", "La unidad hebrea correspondiente al siclo se expresa como gera en las traducciones modernas."),
}


ENCLITICS = {
    "harálo": "lo hará", "haráse": "se hará", "ofrecerála": "la ofrecerá",
    "Traerála": "La traerá", "pondrálas": "las pondrá", "lavólos": "los lavó",
    "ciñólo": "lo ciñó", "vistióle": "le vistió", "ajustólo": "lo ajustó",
    "santificólas": "las santificó", "ungiólo": "lo ungió", "vistióles": "les vistió",
    "ciñólos": "los ciñó", "ajustóles": "les ajustó", "degollólo": "lo degolló",
    "santificólo": "lo santificó", "quemólo": "lo quemó", "púsolo": "lo puso",
    "hízolo": "lo hizo", "hízolas": "las hizo", "meciólo": "lo meció",
    "ofrécelos": "ofrécelos", "llegóse": "se acercó", "Presentáronle": "Le presentaron",
    "hízolos": "los hizo", "quemólos": "los quemó", "meciólos": "los meció",
    "bendíjolos": "los bendijo", "díjoles": "les dijo", "sacáronlos": "los sacaron",
    "hallóse": "se halló", "enojóse": "se enojó", "dióla": "la dio",
    "dióse": "se dio", "tendréislo": "lo tendréis", "tendréisla": "la tendréis",
    "tendréislos": "los tendréis", "darálo": "lo dará", "ofrecerálo": "lo ofrecerá",
    "mecerálo": "lo mecerá", "pondrálo": "lo pondrá", "mojarálo": "lo mojará",
    "lavaráse": "se lavará", "harálos": "los hará", "ceñiráse": "se ceñirá",
    "meterálo": "lo meterá", "cubrirála": "la cubrirá", "cortarála": "la cortará",
    "apedreáronlo": "lo apedrearon", "quedaráse": "se quedará",
}


SPECIAL = [
    (1, 2, "ganado vacuno ú ovejuno", "ganado vacuno, ovejas o cabras", "archaic-animal-class", "Vacuno y ovejuno son categorías antiguas; la frase actual conserva los animales incluidos."),
    (2, 1, "oblación de presente", "ofrenda de cereal", "archaic-ritual-term", "La expresión antigua designa la ofrenda de cereal de este capítulo."),
    (2, 3, "la sobra del presente", "lo que sobre de la ofrenda", "archaic-ritual-term", "Presente significa aquí la ofrenda de cereal, no un regalo cotidiano."),
    (2, 4, "ofrenda de presente", "ofrenda de cereal", "archaic-ritual-term", "La expresión designa la ofrenda de cereal preparada en horno."),
    (2, 5, "tu presente", "tu ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (2, 6, "es presente", "es una ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (2, 7, "tu presente", "tu ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (2, 9, "de aquel presente", "de aquella ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (2, 10, "lo restante del presente", "lo restante de la ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (2, 11, "Ningún presente", "Ninguna ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (2, 11, "ninguna cosa leuda", "nada con levadura", "archaic-food-term", "Leuda significa que contiene levadura."),
    (2, 13, "ofrenda de tu presente", "ofrenda de cereal", "archaic-ritual-term", "La expresión designa esta ofrenda de cereal."),
    (2, 13, "de tu presente la sal", "de tu ofrenda la sal", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (2, 14, "presente de primicias", "ofrenda de primicias", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (2, 15, "es presente", "es una ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (3, 11, "vianda de ofrenda encendida", "alimento de la ofrenda encendida", "archaic-ritual-term", "Vianda significa alimento en esta descripción ritual."),
    (3, 16, "es vianda de ofrenda", "es alimento de una ofrenda", "archaic-ritual-term", "Vianda significa alimento en esta descripción ritual."),
    (4, 14, "el pecado sobre que delinquieron", "el pecado que cometieron", "archaic-legal-term", "Delinquir significa cometer el pecado mencionado."),
    (4, 23, "su pecado en que ha delinquido", "el pecado que ha cometido", "archaic-legal-term", "Se expresa la falta con una construcción actual."),
    (4, 27, "y delinquiere", "y se haga culpable", "archaic-legal-term", "Delinquir significa aquí hacerse culpable de la falta."),
    (5, 2, "habrá delinquido", "será culpable", "archaic-legal-term", "Delinquir significa aquí quedar culpable por la impureza."),
    (5, 7, "si no le alcanzare para un cordero", "si no puede pagar un cordero", "archaic-affordability-idiom", "Alcanzar se refiere a los recursos disponibles para la ofrenda."),
    (5, 8, "desunirá su cabeza de su cuello", "le quebrará el cuello", "archaic-ritual-phrase", "La acción se expresa de forma directa sin añadir separación completa, que el versículo niega."),
    (5, 11, "si su posibilidad no alcanzare para", "si no puede pagar", "archaic-affordability-idiom", "La frase se refiere a no disponer de recursos suficientes."),
    (5, 13, "vianda", "cereal", "archaic-ritual-term", "Vianda designa aquí la ofrenda de cereal."),
    (5, 19, "ciertamente delinquió", "ciertamente se hizo culpable", "archaic-legal-term", "Delinquir significa aquí hacerse culpable ante Jehová."),
    (6, 2, "hiciere prevaricación contra Jehová", "fuere infiel a Jehová", "archaic-legal-term", "Prevaricación expresa infidelidad a Jehová en esta infracción contra el prójimo."),
    (6, 2, "calumniare á su prójimo", "extorsionare a su prójimo", "archaic-legal-term", "En esta lista de bienes, el verbo se refiere a obtener algo mediante opresión o extorsión, no a difamación verbal."),
    (6, 4, "puesto habrá pecado y ofendido", "cuando haya pecado y sea culpable", "broken-grammar", "Se repara la construcción quebrada conservando pecado y culpabilidad."),
    (6, 4, "ó por el daño de la calumnia", "o lo obtenido por extorsión", "archaic-legal-term", "La frase continúa la lista de bienes obtenidos ilícitamente; aquí calumnia designa opresión o extorsión, no difamación verbal."),
    (6, 10, "pañetes de lino", "ropa interior de lino", "archaic-garment-term", "Pañetes designa la ropa interior de lino del sacerdote."),
    (6, 14, "ley del presente", "ley de la ofrenda de cereal", "archaic-ritual-term", "Presente designa la ofrenda de cereal en esta sección."),
    (6, 15, "del presente", "de la ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda de cereal."),
    (6, 20, "presente perpetuo", "ofrenda perpetua", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (6, 21, "se aderezará", "se preparará", "archaic-food-term", "Aderezar significa preparar en esta instrucción de cocina."),
    (6, 21, "del presente", "de la ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (6, 23, "todo presente de sacerdote", "toda ofrenda del sacerdote", "archaic-ritual-term", "Presente significa aquí ofrenda."),
    (6, 12, "los sebos de las paces", "la grasa de los sacrificios de paz", "archaic-ritual-term", "Paces designa los sacrificios de paz y sebos su grasa."),
    (7, 9, "fuere aderezado", "fuere preparado", "archaic-food-term", "Aderezar significa preparar en horno, sartén o cazuela."),
    (7, 10, "todo presente", "toda ofrenda", "archaic-ritual-term", "Presente significa aquí ofrenda de cereal."),
    (7, 12, "Si se ofreciere en hacimiento de gracias", "Si se ofreciere como acción de gracias", "archaic-ritual-term", "Hacimiento de gracias significa acción de gracias."),
    (7, 12, "por sacrificio de hacimiento de gracias", "con el sacrificio de acción de gracias", "archaic-ritual-term", "Hacimiento de gracias significa acción de gracias."),
    (7, 13, "su ofrenda en el sacrificio de hacimientos de gracias de sus paces", "su ofrenda con el sacrificio de paz en acción de gracias", "archaic-ritual-term", "Hacimientos de gracias y paces designan aquí el sacrificio de paz presentado como agradecimiento."),
    (7, 15, "sacrificio de sus pacíficos en hacimiento de gracias", "sacrificio de paz en acción de gracias", "archaic-ritual-term", "Pacíficos designa el sacrificio de paz; se explicita la categoría ritual."),
    (7, 24, "se aparejará para cualquiera otro uso", "se podrá usar para cualquier otro fin", "archaic-phrase", "Aparejarse significa aquí poder destinarse a otro uso."),
    (7, 24, "animal mortecino", "animal muerto naturalmente", "archaic-legal-term", "Mortecino describe un animal que murió por sí mismo, no uno sacrificado."),
    (7, 9, "todo presente que se cociere", "toda ofrenda de cereal que se cociere", "archaic-ritual-term", "Presente designa la ofrenda de cereal."),
    (7, 18, "sacrificio de sus paces", "sacrificio de paz", "archaic-ritual-term", "Paces designa el sacrificio de paz."),
    (7, 29, "El que ofreciere sacrificio de sus paces á Jehová", "El que ofreciere sacrificio de paz a Jehová", "archaic-ritual-term", "Paces designa el sacrificio de paz."),
    (7, 29, "traerá su ofrenda del sacrificio de sus paces á Jehová", "traerá su ofrenda del sacrificio de paz a Jehová", "archaic-ritual-term", "Paces designa el sacrificio de paz."),
    (7, 32, "sacrificios de vuestras paces", "sacrificios de paz", "archaic-ritual-term", "Paces designa los sacrificios de paz."),
    (7, 33, "sangre de las paces", "sangre del sacrificio de paz", "archaic-ritual-term", "Paces designa el sacrificio de paz."),
    (7, 34, "sacrificios de sus paces", "sacrificios de paz", "archaic-ritual-term", "Paces designa los sacrificios de paz."),
    (7, 34, "la espaldilla elevada", "la pierna presentada", "archaic-anatomy", "Espaldilla designa la porción de la pierna presentada al sacerdote."),
    (7, 35, "él los allegó para ser sacerdotes", "él los presentó para servir como sacerdotes", "archaic-ritual-phrase", "Allegar significa presentar a Aarón y sus hijos para el sacerdocio."),
    (7, 37, "ley del holocausto, del presente", "ley del holocausto, de la ofrenda de cereal", "archaic-ritual-term", "Presente designa aquí la ofrenda de cereal."),
    (7, 38, "La cual intimó Jehová", "La cual ordenó Jehová", "archaic-lexicon", "Intimar significa ordenar formalmente en este contexto."),
    (8, 2, "canastillo de los ázimos", "canasta de los panes sin levadura", "archaic-food-term", "Ázimos son panes sin levadura."),
    (8, 13, "chapeos (tiaras)", "tiaras", "archaic-garment-term", "Chapeos es una palabra antigua; la propia edición ya identifica estas prendas como tiaras."),
    (8, 23, "la ternilla de la oreja derecha", "el lóbulo de la oreja derecha", "archaic-anatomy", "Ternilla designa el lóbulo de la oreja."),
    (8, 24, "la ternilla de sus orejas derechas", "el lóbulo de sus orejas derechas", "archaic-anatomy", "Ternilla designa el lóbulo de la oreja."),
    (8, 26, "canastillo de los ázimos", "canasta de los panes sin levadura", "archaic-food-term", "Ázimos son panes sin levadura."),
    (8, 26, "una lasaña", "una torta delgada", "archaic-food-term", "Lasaña designa aquí una torta delgada sin levadura, no el plato moderno."),
    (10, 3, "En mis allegados", "En los que se acercan a mí", "archaic-ritual-phrase", "Allegados se refiere a quienes se acercan a Jehová en el servicio sagrado."),
    (10, 13, "esto es fuero para ti, y fuero para tus hijos", "esta es la porción asignada a ti y a tus hijos", "archaic-legal-term", "Fuero designa aquí la porción asignada a los sacerdotes."),
    (10, 14, "por fuero para ti, y fuero para tus hijos", "como porción asignada a ti y a tus hijos", "archaic-legal-term", "Fuero designa aquí la porción asignada a la familia sacerdotal."),
    (10, 15, "por fuero perpetuo tuyo", "como porción perpetua tuya", "archaic-legal-term", "Fuero designa aquí la porción asignada al sacerdote."),
    (10, 16, "Moisés demandó el macho cabrío", "Moisés buscó diligentemente el macho cabrío", "archaic-lexicon", "Demandar significa aquí buscar o averiguar por el animal ofrecido."),
    (9, 4, "un presente amasado con aceite", "una ofrenda de cereal amasada con aceite", "archaic-ritual-term", "Presente designa la ofrenda de cereal."),
    (9, 17, "Ofreció asimismo el presente", "Ofreció asimismo la ofrenda de cereal", "archaic-ritual-term", "Presente designa la ofrenda de cereal."),
    (10, 14, "sacrificios de las paces", "sacrificios de paz", "archaic-ritual-term", "Paces designa los sacrificios de paz."),
    (10, 14, "la espaldilla elevada", "la pierna presentada", "archaic-anatomy", "Espaldilla designa la porción de la pierna presentada al sacerdote."),
    (10, 15, "la espaldilla que se ha de elevar", "la pierna que se ha de presentar", "archaic-anatomy", "Espaldilla designa la porción de la pierna presentada al sacerdote."),
    (11, 34, "Toda vianda", "Todo alimento", "archaic-food-term", "Vianda significa alimento."),
    (12, 6, "días de su purgación", "días de su purificación", "archaic-ritual-term", "Purgación significa purificación ritual en este contexto."),
    (12, 8, "si no alcanzare su mano lo suficiente para", "si no puede pagar", "archaic-affordability-idiom", "La frase se refiere a no disponer de recursos para un cordero."),
    (13, 2, "hinchazón, ó postilla", "hinchazón, erupción", "archaic-medical-term", "Postilla designa una erupción visible en la piel."),
    (13, 3, "la tez de la carne", "la piel", "archaic-medical-term", "Tez designa aquí la superficie de la piel."),
    (13, 4, "más hundida que la tez", "más hundida que la piel", "archaic-medical-term", "Tez designa aquí la piel."),
    (13, 6, "no ha cundido en la piel", "no se ha extendido en la piel", "archaic-medical-term", "Cundir significa extenderse."),
    (13, 6, "era postilla", "era una erupción", "archaic-medical-term", "Postilla designa una erupción de la piel."),
    (13, 7, "creciendo la postilla", "extendiéndose la erupción", "archaic-medical-term", "La frase describe la extensión de la afección cutánea."),
    (13, 8, "la postilla ha crecido", "la erupción se ha extendido", "archaic-medical-term", "La frase describe la extensión de la afección cutánea."),
    (13, 12, "cundiendo por el cutis", "extendiéndose por la piel", "archaic-medical-term", "Cundir y cutis significan extenderse por la piel."),
    (13, 18, "hubiere apostema", "hubiere una úlcera", "archaic-medical-term", "Apostema designa una úlcera o llaga en la piel."),
    (13, 19, "lugar de la apostema", "lugar de la úlcera", "archaic-medical-term", "Apostema designa la úlcera anterior."),
    (13, 19, "mancha blanca embermejecida", "mancha blanca rojiza", "archaic-medical-term", "Embermejecida significa enrojecida o rojiza."),
    (13, 23, "no haya cundido", "no se haya extendido", "archaic-medical-term", "Cundir significa extenderse."),
    (13, 23, "costra de la apostema", "cicatriz de la úlcera", "archaic-medical-term", "La frase identifica la marca dejada por la úlcera."),
    (13, 20, "se originó en la apostema", "se originó en la úlcera", "archaic-medical-term", "Apostema designa la úlcera anterior."),
    (13, 26, "más baja que la tez", "más baja que la piel", "archaic-medical-term", "Tez designa aquí la piel."),
    (13, 30, "más profunda que la tez", "más profunda que la piel", "archaic-medical-term", "Tez designa aquí la piel."),
    (13, 31, "más profunda que la tez", "más profunda que la piel", "archaic-medical-term", "Tez designa aquí la piel."),
    (13, 32, "más profunda que la tez", "más profunda que la piel", "archaic-medical-term", "Tez designa aquí la piel."),
    (13, 33, "lo trasquilarán, mas no trasquilarán", "lo afeitarán, pero no afeitarán", "archaic-medical-term", "Trasquilar significa cortar o afeitar el cabello en esta inspección."),
    (13, 34, "no hubiere cundido en la piel", "no se hubiere extendido en la piel", "archaic-medical-term", "Cundir significa extenderse."),
    (13, 34, "más profunda que la tez", "más profunda que la piel", "archaic-medical-term", "Tez designa aquí la piel."),
    (13, 36, "hubiere cundido en la piel", "se hubiere extendido en la piel", "archaic-medical-term", "Cundir significa extenderse."),
    (13, 42, "en la calva ó en la antecalva", "en la coronilla calva o en la frente calva", "archaic-anatomy", "Calva y antecalva distinguen la parte posterior y frontal de la cabeza."),
    (13, 42, "en su calva ó en su antecalva", "en su coronilla calva o en su frente calva", "archaic-anatomy", "Calva y antecalva distinguen la parte posterior y frontal de la cabeza."),
    (13, 43, "en su calva ó en su antecalva", "en su coronilla calva o en su frente calva", "archaic-anatomy", "Calva y antecalva distinguen la parte posterior y frontal de la cabeza."),
    (13, 43, "lepra de la tez de la carne", "afección de la piel", "archaic-medical-term", "La frase describe la afección visible en la piel sin cambiar el diagnóstico ritual del versículo."),
    (13, 45, "embozado pregonará", "cubriéndose la parte inferior del rostro gritará", "archaic-ritual-phrase", "La frase antigua describe cubrirse parte del rostro y anunciar en voz alta su condición."),
    (13, 51, "lepra roedora", "lepra maligna", "archaic-medical-term", "Roedora significa maligna o destructiva en esta inspección del tejido."),
    (13, 51, "hubiere cundido la plaga", "se hubiere extendido la plaga", "archaic-medical-term", "Cundir significa extenderse."),
    (13, 52, "lepra roedora", "lepra maligna", "archaic-medical-term", "Roedora significa maligna o destructiva en esta inspección del tejido."),
    (13, 58, "lavarse ha segunda vez", "se lavará por segunda vez", "archaic-grammar", "Se actualiza la construcción verbal futura."),
    (13, 55, "no haya cundido la plaga", "no se haya extendido la plaga", "archaic-medical-term", "Cundir significa extenderse."),
    (14, 4, "dos avecillas vivas", "dos aves vivas", "archaic-animal-name", "Avecillas significa aves pequeñas; aves conserva el referente sin precisar una especie."),
    (14, 7, "sobre la haz del campo", "en campo abierto", "archaic-location", "Haz del campo significa la superficie o extensión abierta del campo."),
    (14, 8, "raerá todos sus pelos", "se afeitará todo el pelo", "archaic-grooming-term", "Raer significa afeitar."),
    (14, 9, "raerá todos sus pelos", "se afeitará todo el pelo", "archaic-grooming-term", "Raer significa afeitar."),
    (14, 9, "raerá todo su pelo", "se afeitará todo su pelo", "archaic-grooming-term", "Raer significa afeitar."),
    (14, 12, "el un cordero", "uno de los corderos", "archaic-grammar", "Se actualiza la construcción partitiva sin cambiar la cantidad."),
    (14, 14, "la ternilla de la oreja derecha", "el lóbulo de la oreja derecha", "archaic-anatomy", "Ternilla designa el lóbulo de la oreja."),
    (14, 17, "la ternilla de la oreja derecha", "el lóbulo de la oreja derecha", "archaic-anatomy", "Ternilla designa el lóbulo de la oreja."),
    (14, 21, "que no alcanzare su mano á tanto", "que no pueda pagar tanto", "archaic-affordability-idiom", "La frase se refiere a no disponer de recursos suficientes."),
    (14, 22, "lo que alcanzare su mano", "lo que pueda pagar", "archaic-affordability-idiom", "La frase se refiere a los recursos disponibles para la ofrenda."),
    (14, 25, "la ternilla de la oreja derecha", "el lóbulo de la oreja derecha", "archaic-anatomy", "Ternilla designa el lóbulo de la oreja."),
    (14, 28, "la ternilla de la oreja derecha", "el lóbulo de la oreja derecha", "archaic-anatomy", "Ternilla designa el lóbulo de la oreja."),
    (14, 30, "lo que alcanzare su mano", "lo que pueda pagar", "archaic-affordability-idiom", "La frase se refiere a los recursos disponibles para la ofrenda."),
    (14, 31, "lo que alcanzare su mano", "lo que pueda pagar", "archaic-affordability-idiom", "La frase se refiere a los recursos disponibles para la ofrenda."),
    (14, 37, "cavernillas verdosas ó rojas", "manchas verdosas o rojizas", "archaic-building-term", "Cavernillas designa depresiones o manchas hundidas visibles en la pared."),
    (14, 41, "hará descostrar la casa", "hará raspar la casa", "archaic-building-term", "Descostrar significa raspar el revestimiento de la pared."),
    (14, 41, "el polvo que descostraren", "el material que rasparen", "archaic-building-term", "Se refiere al material retirado al raspar las paredes."),
    (14, 42, "encostrarán la casa", "revocarán la casa", "archaic-building-term", "Encostrar significa cubrir de nuevo las paredes con barro o revoque."),
    (14, 43, "descostrar la casa", "raspar la casa", "archaic-building-term", "Descostrar significa raspar el revestimiento."),
    (14, 43, "fué encostrada", "fue revocada", "archaic-building-term", "Encostrar significa volver a cubrir las paredes."),
    (14, 49, "dos avecillas", "dos aves", "archaic-animal-name", "Avecillas significa aves pequeñas; aves conserva el referente sin precisar una especie."),
    (14, 53, "sobre la haz del campo", "en campo abierto", "archaic-location", "Haz del campo significa la extensión abierta del campo."),
    (14, 56, "de la postilla", "de la erupción", "archaic-medical-term", "Postilla designa una erupción de la piel."),
    (14, 44, "lepra roedora", "lepra maligna", "archaic-building-term", "Roedora significa maligna o destructiva en la inspección de la casa."),
    (15, 3, "su carne destiló por causa de su flujo", "su cuerpo emita la secreción", "archaic-medical-term", "Destilar describe la emisión de la secreción corporal."),
    (15, 9, "todo aparejo sobre que cabalgare", "toda montura sobre la que cabalgue", "archaic-object-term", "Aparejo designa aquí la montura del animal."),
    (15, 18, "tuviera ayuntamiento de semen", "tuviera relaciones sexuales", "archaic-euphemism", "Ayuntamiento de semen designa las relaciones sexuales en este contexto."),
    (15, 25, "fuera del tiempo de su costumbre", "fuera del tiempo de su menstruación", "archaic-medical-term", "Costumbre designa aquí el período menstrual."),
    (15, 25, "más de su costumbre", "más allá de su menstruación", "archaic-medical-term", "Costumbre designa aquí el período menstrual."),
    (15, 26, "la cama de su costumbre", "la cama durante su menstruación", "archaic-medical-term", "Costumbre designa aquí el período menstrual."),
    (15, 26, "la inmundicia de su costumbre", "la impureza de su menstruación", "archaic-medical-term", "Costumbre designa aquí el período menstrual."),
    (15, 25, "como en los días de su costumbre", "como durante los días de su menstruación", "archaic-medical-term", "Costumbre designa aquí el período menstrual."),
    (15, 33, "la que padece su costumbre", "la mujer durante su menstruación", "archaic-medical-term", "Costumbre designa aquí el período menstrual."),
    (16, 4, "pañetes de lino", "ropa interior de lino", "archaic-garment-term", "Pañetes designa la ropa interior de lino del sacerdote."),
    (16, 6, "hará allegar Aarón el becerro", "Aarón presentará el becerro", "archaic-ritual-phrase", "Allegar significa presentar el animal ante Jehová."),
    (16, 9, "hará allegar Aarón el macho cabrío", "Aarón presentará el macho cabrío", "archaic-ritual-phrase", "Allegar significa presentar el animal ante Jehová."),
    (16, 22, "tierra inhabitada", "tierra deshabitada", "archaic-location", "Inhabitada significa deshabitada."),
    (17, 5, "sobre la haz del campo", "en campo abierto", "archaic-location", "Haz del campo significa la extensión abierta del campo."),
    (17, 15, "cosa mortecina", "un animal muerto naturalmente", "archaic-legal-term", "Mortecina describe carne de un animal que murió por sí mismo."),
    (17, 5, "sacrifiquen ellos sacrificios de paces", "ofrezcan sacrificios de paz", "archaic-ritual-term", "Paces designa los sacrificios de paz."),
    (18, 4, "Mis derechos", "Mis ordenanzas", "archaic-legal-term", "Derechos designa aquí las ordenanzas de Dios."),
    (18, 5, "mis derechos", "mis ordenanzas", "archaic-legal-term", "Derechos designa aquí las ordenanzas de Dios."),
    (18, 6, "se allegue á ninguna cercana de su carne", "se acerque a ninguna pariente cercana", "archaic-kinship-phrase", "La expresión designa una pariente cercana de la familia."),
    (18, 23, "tendrás ayuntamiento", "tendrás relaciones sexuales", "archaic-euphemism", "Ayuntamiento designa relaciones sexuales en esta prohibición."),
    (18, 23, "amancillándote", "contaminándote", "archaic-lexicon", "Amancillar significa contaminar en esta ley de pureza."),
    (18, 24, "os amancillaréis", "os contaminaréis", "archaic-lexicon", "Amancillar significa contaminar en esta ley de pureza."),
    (18, 26, "mis derechos", "mis ordenanzas", "archaic-legal-term", "Derechos designa aquí las ordenanzas de Dios."),
    (19, 9, "rincón de tu haza", "borde de tu campo", "archaic-agriculture-term", "Haza significa campo; borde expresa la parte que no debía segarse."),
    (19, 15, "honrarás la cara del grande", "favorecerás al poderoso", "archaic-legal-idiom", "Honrar la cara significa mostrar favoritismo en el juicio."),
    (19, 16, "No te pondrás contra la sangre de tu prójimo", "No atentarás contra la vida de tu prójimo", "archaic-legal-idiom", "La frase prohíbe poner en peligro la vida del prójimo."),
    (19, 17, "ingenuamente reprenderás", "reprenderás con franqueza", "archaic-lexicon", "Ingenuamente significa aquí con franqueza, no con ingenuidad."),
    (19, 17, "no consentirás sobre él pecado", "no participarás de su pecado", "archaic-legal-idiom", "La cláusula advierte que no se debe cargar o participar en el pecado del prójimo."),
    (19, 19, "ayuntar para misturas", "aparear con otra especie", "archaic-animal-phrase", "La frase prohíbe cruzar animales de especies distintas."),
    (19, 19, "tu haza no sembrarás con mistura de semillas", "no sembrarás tu campo con dos clases de semilla", "archaic-agriculture-term", "Se expresa la mezcla de semillas con palabras actuales."),
    (19, 23, "quitaréis su prepucio, lo primero de su fruto: tres años os será incircunciso", "consideraréis prohibido su primer fruto: durante tres años os será prohibido", "archaic-agriculture-idiom", "La imagen ritual indica que el fruto de los primeros tres años no debía comerse; se conserva la segunda persona plural del pasaje."),
    (19, 24, "santidad de loores", "consagrado para alabanza", "archaic-worship-term", "Loores significa alabanza."),
    (19, 26, "No seréis agoreros", "No interpretaréis augurios", "archaic-divination-term", "Agorero es quien interpreta presagios o augurios."),
    (19, 35, "medida de tierra", "medida de longitud", "archaic-measure-term", "La expresión se refiere a medir longitud, junto con peso y capacidad."),
    (19, 37, "todos mis derechos", "todas mis ordenanzas", "archaic-legal-term", "Derechos designa aquí las ordenanzas de Dios."),
    (20, 2, "diere de su simiente á Moloch", "entregue alguno de sus hijos a Moloch", "archaic-kinship-term", "Simiente designa aquí los hijos ofrecidos a Moloch."),
    (20, 3, "dió de su simiente á Moloch", "entregó uno de sus hijos a Moloch", "archaic-kinship-term", "Simiente designa aquí los hijos ofrecidos a Moloch."),
    (20, 3, "amancillando mi santo nombre", "deshonrando mi santo nombre", "archaic-worship-term", "Amancillar significa deshonrar en esta referencia al nombre santo."),
    (20, 12, "hicieron confusión", "cometieron perversión", "archaic-legal-term", "Confusión designa aquí la perversión prohibida, no falta de comprensión."),
    (20, 13, "tuviere ayuntamiento", "tuviere relaciones sexuales", "archaic-euphemism", "Ayuntamiento designa relaciones sexuales."),
    (20, 16, "para tener ayuntamiento con él", "para tener relaciones sexuales con él", "archaic-euphemism", "Ayuntamiento designa relaciones sexuales."),
    (20, 17, "cosa es execrable", "es cosa vergonzosa", "archaic-lexicon", "Execrable designa aquí un acto vergonzoso condenado por la ley."),
    (20, 22, "todos mis derechos", "todas mis ordenanzas", "archaic-legal-term", "Derechos designa aquí las ordenanzas de Dios."),
    (20, 27, "espíritu pithónico", "espíritu de adivinación", "archaic-divination-term", "Pithónico es una denominación antigua para un espíritu de adivinación."),
    (21, 7, "Mujer ramera ó infame", "Mujer prostituta o deshonrada", "archaic-legal-term", "Se actualizan dos denominaciones antiguas sin cambiar la prohibición sacerdotal."),
    (21, 9, "á su padre amancilla", "deshonra a su padre", "archaic-lexicon", "Amancillar significa deshonrar en esta relación familiar."),
    (21, 10, "hinchió su mano para vestir las vestimentas", "fue consagrado para vestir las vestiduras", "archaic-consecration-idiom", "Llenar la mano es la expresión ritual de consagración sacerdotal."),
    (21, 15, "no amancillará su simiente", "no deshonrará a su descendencia", "archaic-kinship-term", "Simiente designa descendencia y amancillar significa deshonrar."),
    (21, 17, "El varón de tu simiente", "El hombre de tu descendencia", "archaic-kinship-term", "Simiente designa la descendencia de Aarón."),
    (21, 20, "corcovado", "jorobado", "archaic-physical-term", "Corcovado significa jorobado."),
    (21, 20, "lagañoso", "enano", "archaic-physical-term", "En esta lista de defectos físicos, la tradición moderna vierte el término como enano."),
    (21, 20, "nube en el ojo", "cataratas en los ojos", "archaic-physical-term", "Nube en el ojo designa cataratas u opacidad visible."),
    (21, 20, "empeine", "llaga supurante", "archaic-physical-term", "En esta lista de impedimentos físicos, empeine designa una afección o llaga persistente de la piel."),
    (21, 20, "compañón relajado", "testículo dañado", "archaic-physical-term", "La expresión antigua designa una lesión en los testículos."),
    (21, 21, "varón de la simiente de Aarón", "hombre de la descendencia de Aarón", "archaic-kinship-term", "Simiente designa la descendencia de Aarón."),
    (22, 2, "que se abstengan de las santificaciones de los hijos de Israel, y que no profanen mi santo nombre en lo que ellos me santifican", "que traten con cuidado las cosas santas que los hijos de Israel me consagran, para que no profanen mi santo nombre", "archaic-ritual-phrase", "La frase ordena tratar las ofrendas santas con reverencia para no profanar el nombre de Jehová."),
    (22, 3, "Todo varón de toda vuestra simiente", "Todo hombre de vuestra descendencia", "archaic-kinship-term", "Simiente designa la descendencia sacerdotal."),
    (22, 4, "el que tocare cualquiera cosa inmunda de mortecino", "el que toque el cuerpo de un animal muerto naturalmente", "archaic-legal-term", "Mortecino describe un animal que murió por sí mismo; se repara la relación gramatical de la frase."),
    (22, 8, "Mortecino ni despedazado por fiera no comerá", "No comerá ningún animal muerto naturalmente ni despedazado por fieras", "archaic-legal-term", "Se expresa la prohibición con orden actual y se conserva la distinción entre ambas muertes."),
    (22, 13, "no tuviere prole", "no tuviere hijos", "archaic-kinship-term", "Prole significa hijos o descendencia."),
    (22, 14, "por yerro comiere", "comiere involuntariamente", "archaic-legal-term", "Por yerro indica que la acción fue involuntaria."),
    (22, 22, "perniquebrado", "con una pata quebrada", "archaic-physical-term", "Perniquebrado significa que tiene una pata quebrada."),
    (22, 24, "rompido", "roto", "archaic-physical-term", "Rompido es una forma antigua de roto."),
    (22, 29, "sacrificio de hacimiento de gracias", "sacrificio de acción de gracias", "archaic-ritual-term", "Hacimiento de gracias significa acción de gracias."),
    (22, 32, "no amancilléis mi santo nombre", "no profanen mi santo nombre", "archaic-worship-term", "Amancillar significa profanar en esta orden."),
    (23, 6, "solemnidad de los ázimos", "fiesta de los panes sin levadura", "archaic-festival-term", "Ázimos son panes sin levadura; solemnidad designa la fiesta."),
    (23, 6, "siete días comeréis ázimos", "siete días comeréis panes sin levadura", "archaic-food-term", "Ázimos son panes sin levadura."),
    (23, 16, "nuevo presente", "nueva ofrenda de cereal", "archaic-ritual-term", "Presente designa la ofrenda de cereal."),
    (23, 18, "con su presente", "con su ofrenda de cereal", "archaic-ritual-term", "Presente designa la ofrenda de cereal que acompaña los sacrificios."),
    (23, 22, "rincón de tu haza", "borde de tu campo", "archaic-agriculture-term", "Haza significa campo; borde expresa la parte que no debía segarse."),
    (23, 32, "holgaréis vuestro sábado", "guardarán su día de reposo", "archaic-festival-term", "Holgar significa cesar del trabajo y guardar reposo."),
    (23, 37, "holocausto y presente", "holocausto y ofrenda de cereal", "archaic-ritual-term", "Presente designa la ofrenda de cereal."),
    (23, 13, "su presente será", "su ofrenda de cereal será", "archaic-ritual-term", "Presente designa la ofrenda de cereal."),
    (23, 39, "hubiereis allegado el fruto", "hayan recogido el fruto", "archaic-harvest-term", "Allegar significa recoger o reunir la cosecha."),
    (23, 40, "gajos con fruto de árbol hermoso", "ramas con fruto de árbol hermoso", "archaic-plant-term", "Gajos designa aquí ramas del árbol."),
    (24, 3, "las aderezará Aarón", "Aarón las preparará", "archaic-ritual-term", "Aderezar significa preparar y mantener en orden las lámparas."),
    (24, 9, "por fuero perpetuo", "como porción perpetua", "archaic-legal-term", "Fuero designa la porción asignada a los sacerdotes."),
    (24, 10, "En aquella sazón", "En aquella ocasión", "archaic-time-term", "Sazón significa ocasión o momento en esta narración."),
    (24, 20, "la lesión que habrá hecho", "la lesión que haya causado", "archaic-grammar", "Se actualiza la construcción verbal sin cambiar la regla de proporcionalidad."),
    (25, 5, "Lo que de suyo se naciere", "Lo que nazca por sí solo", "archaic-agriculture-phrase", "De suyo significa por sí solo en el descanso de la tierra."),
    (25, 5, "año de holganza", "año de reposo", "archaic-festival-term", "Holganza significa reposo en el año sabático."),
    (25, 9, "trompeta de jubilación", "trompeta del jubileo", "archaic-festival-term", "Jubilación designa aquí el jubileo, no el retiro laboral moderno."),
    (25, 11, "lo que naciere de suyo", "lo que nazca por sí solo", "archaic-agriculture-phrase", "De suyo significa por sí solo."),
    (25, 18, "mis derechos", "mis ordenanzas", "archaic-legal-term", "Derechos designa aquí las ordenanzas de Dios."),
    (25, 19, "comeréis hasta hartura", "comeréis hasta saciaros", "archaic-food-term", "Hartura significa comer hasta quedar satisfechos."),
    (25, 23, "no se venderá rematadamente", "no se venderá a perpetuidad", "archaic-property-term", "Rematadamente significa de forma definitiva o perpetua."),
    (25, 23, "porque la tierra mía es; que vosotros peregrinos y extranjeros sois para conmigo", "porque la tierra es mía; vosotros sois forasteros y extranjeros para conmigo", "archaic-property-phrase", "Se actualiza el orden de la frase y peregrinos se aclara como forasteros en relación con la tierra."),
    (25, 25, "vendrá el rescatador, su cercano", "vendrá su pariente más cercano", "archaic-kinship-phrase", "El rescatador cercano es el pariente con derecho de rescate."),
    (25, 26, "no tuviere rescatador", "no tuviere pariente que la rescate", "archaic-property-term", "Rescatador designa al pariente que recupera la propiedad."),
    (25, 26, "si alcanzare su mano", "si consigue lo suficiente", "archaic-affordability-idiom", "La frase significa reunir los recursos necesarios."),
    (25, 28, "si no alcanzare su mano lo que basta", "si no consigue lo suficiente", "archaic-affordability-idiom", "La frase significa no reunir los recursos necesarios."),
    (25, 29, "ciudad cercada", "ciudad amurallada", "archaic-location-term", "Cercada designa una ciudad rodeada de murallas."),
    (25, 31, "como una haza de tierra", "como los terrenos del campo", "archaic-property-term", "Haza de tierra significa terreno del campo."),
    (25, 34, "tierra del ejido", "terrenos comunales", "archaic-property-term", "Ejido designa los terrenos comunales alrededor de las ciudades levíticas."),
    (25, 37, "tu vitualla", "tus víveres", "archaic-food-term", "Vitualla significa víveres o alimentos."),
    (25, 43, "No te enseñorearás de él", "No lo dominarás", "archaic-authority-term", "Enseñorearse significa dominar o ejercer autoridad dura."),
    (25, 46, "por juro de heredad", "como herencia", "archaic-property-term", "Juro de heredad significa posesión hereditaria."),
    (25, 46, "no os enseñorearéis cada uno sobre su hermano", "ninguno dominará a su hermano", "archaic-authority-term", "Enseñorearse significa dominar con dureza."),
    (25, 53, "Como con tomado á salario anualmente hará con él", "Será tratado como un jornalero contratado por año", "archaic-labor-phrase", "Se expresa la comparación laboral con orden actual."),
    (25, 53, "no se enseñoreará en él con aspereza", "no lo dominará con dureza", "archaic-authority-term", "Enseñorearse con aspereza significa dominar con dureza."),
    (26, 5, "la sementera", "el tiempo de sembrar", "archaic-agriculture-term", "Sementera designa la temporada de siembra."),
    (26, 5, "pan en hartura", "pan hasta saciarse", "archaic-food-term", "Hartura significa comer hasta quedar satisfechos."),
    (26, 13, "las coyundas de vuestro yugo", "las ataduras de su yugo", "archaic-bondage-term", "Coyundas son las correas o ataduras del yugo."),
    (26, 15, "mis derechos", "mis ordenanzas", "archaic-legal-term", "Derechos designa aquí las ordenanzas de Dios."),
    (26, 16, "extenuación y calentura", "debilidad y fiebre", "archaic-medical-term", "Extenuación y calentura designan debilidad y fiebre."),
    (26, 17, "se enseñorearán de vosotros", "los dominarán", "archaic-authority-term", "Enseñorearse significa dominar."),
    (26, 22, "os apoquen", "reduzcan su número", "archaic-lexicon", "Apocar significa disminuir o reducir en número."),
    (26, 25, "en vindicación del pacto", "para vengar la ruptura del pacto", "archaic-legal-phrase", "Vindicación expresa el castigo por quebrantar el pacto."),
    (26, 26, "el arrimo del pan", "el sustento del pan", "archaic-food-idiom", "Arrimo del pan designa el sustento o provisión alimentaria."),
    (26, 32, "se pasmarán de ella", "quedarán atónitos ante ella", "archaic-emotion-term", "Pasmarse significa quedar atónito."),
    (26, 40, "por su prevaricación con que prevaricaron contra mí", "por la infidelidad que cometieron contra mí", "archaic-legal-term", "Prevaricación expresa infidelidad al pacto en este contexto."),
    (26, 43, "menospreciaron mis derechos", "menospreciaron mis ordenanzas", "archaic-legal-term", "Derechos designa aquí las ordenanzas de Dios."),
    (26, 46, "decretos, derechos y leyes", "decretos, ordenanzas y leyes", "archaic-legal-term", "Derechos designa aquí las ordenanzas establecidas por Jehová."),
    (27, 8, "conforme á la facultad del votante", "según los recursos del que hizo el voto", "archaic-valuation-phrase", "Facultad designa la capacidad económica de quien hizo el voto."),
    (27, 10, "mudado ni trocado", "sustituido ni cambiado", "archaic-exchange-term", "Mudado y trocado describen sustituir un animal por otro."),
    (27, 10, "si se permutare un animal", "si se cambia un animal", "archaic-exchange-term", "Permutar significa cambiar una cosa por otra."),
    (27, 16, "conforme á su sembradura", "según la cantidad de semilla necesaria", "archaic-valuation-term", "Sembradura designa la cantidad de semilla necesaria para el terreno."),
    (27, 16, "un omer de sembradura de cebada", "un homer de semilla de cebada", "archaic-measure-term", "Homer es la medida hebrea usada para calcular la semilla del terreno; se evita confundirla con el omer menor."),
    (27, 29, "Cualquier anatema (cosa consagrada) de hombres que se consagrare, no será redimido", "Toda persona que haya sido consagrada irrevocablemente no podrá ser rescatada", "archaic-dedication-term", "Anatema describe aquí una dedicación irrevocable; la frase completa evita una discordancia y el sentido moderno de maldición."),
    (27, 29, "indefectiblemente ha de ser muerto", "deberá morir sin falta", "archaic-legal-phrase", "Indefectiblemente significa sin falta."),
]


PENDING = [
    (1, 8, "redaño", "La palabra puede designar grasa, membrana o lóbulo según la ubicación anatómica; no se sustituye de forma uniforme."),
    (1, 9, "olor suave", "Fórmula ritual recurrente; aroma agradable es claro, pero debe decidirse de forma coherente en todo el Pentateuco."),
    (3, 16, "olor de suavidad", "La misma fórmula ritual requiere una política uniforme antes de cambiarse."),
    (11, 13, "quebrantahuesos / esmerejón", "La identificación exacta de varias aves hebreas es incierta; se conserva la edición y se recomienda una nota."),
    (11, 18, "calamón / onocrótalo", "La identificación de las especies antiguas no es segura entre traducciones."),
    (11, 22, "aregol / haghab", "Los nombres antiguos de insectos no tienen equivalencia zoológica segura."),
    (13, 2, "lepra", "La palabra bíblica abarca diversas afecciones de piel y materiales; una sustitución global sería inexacta."),
    (13, 39, "empeine", "Las traducciones difieren entre erupción, eczema y manchas; se conserva hasta revisión médica y textual."),
    (13, 48, "estambre / trama", "Son términos técnicos de tejido; pueden necesitar una nota más que una sustitución."),
    (14, 5, "aguas vivas", "La imagen significa agua corriente o fresca; se conserva hasta decidir si debe aclararse sin perder la imagen."),
    (16, 2, "cubierta", "Designa la cubierta expiatoria del arca; requiere una política terminológica uniforme con propiciatorio."),
    (16, 8, "Azazel", "El referente de Azazel es discutido; se conserva el nombre y no se interpreta dentro del texto."),
    (18, 6, "descubrir su desnudez", "Es un eufemismo jurídico hebreo; una paráfrasis puede perder matices de parentesco y prohibición."),
    (18, 21, "Moloch", "Se conserva el nombre histórico; la grafía Moloc puede resolverse después de una política de nombres propios."),
    (19, 20, "ambos serán azotados", "La cláusula hebrea y las traducciones modernas difieren sobre pena e investigación; no se modifica sin estudio textual específico."),
    (20, 9, "su sangre será sobre él", "Fórmula legal antigua que requiere una política consistente en todos los pasajes penales."),
    (21, 18, "falto, ó sobrado", "La descripción física exacta es incierta; se conserva para una revisión textual especializada."),
    (22, 22, "verrugoso / roñoso", "La identificación exacta de los defectos del animal varía entre traducciones."),
    (23, 5, "entre las dos tardes", "Expresión temporal técnica; las interpretaciones divergen y no debe simplificarse sin nota."),
    (23, 10, "omer", "El texto parece usar omer para la gavilla mecida, no solo como medida; se conserva hasta revisión terminológica."),
    (25, 36, "usura / aumento", "Los términos económicos tienen alcance legal y requieren revisión conjunta del versículo."),
    (26, 41, "corazón incircunciso", "Imagen teológica deliberada; se conserva aunque necesite explicación."),
    (27, 2, "estimación", "Es un término técnico de valoración de votos; puede aclararse con interfaz o nota sin alterar el texto."),
]

UNIFORM_EXCLUSIONS = {("por yerro", 22, 14)}


def verse_map(document):
    return {(c["chapter"], v["verse"]): v["text"] for c in document["chapters"] for v in c["verses"]}


def apply_layer(text, patch):
    for edit in sorted(patch.get("edits", []), key=lambda e: e["startOffset"], reverse=True):
        text = text[:edit["startOffset"]] + edit["replacement"] + text[edit["endOffset"]:]
    return text


def offsets(text, expected):
    if expected.isalpha():
        return [m.start() for m in re.finditer(rf"(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ]){re.escape(expected)}(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])", text)]
    return [m.start() for m in re.finditer(re.escape(expected), text)]


def main():
    book = json.loads(BOOK_PATH.read_text(encoding="utf-8"))
    source = verse_map(book)
    layer = json.loads(LAYER_PATH.read_text(encoding="utf-8"))
    patches = {(v["chapter"], v["verse"]): v for v in layer["verses"]}
    current = {ref: apply_layer(text, patches.get(ref, {})) for ref, text in source.items()}
    occupied = {(v["chapter"], v["verse"]): v.get("edits", []) for v in layer["verses"]}
    entries = []

    def add(chapter, verse, expected, replacement, category, reason):
        rendered = current[(chapter, verse)]
        if expected == replacement:
            return
        rendered_offsets = offsets(rendered, expected)
        original = source[(chapter, verse)]
        original_offsets = offsets(original, expected)
        assert len(rendered_offsets) == 1, (chapter, verse, expected, rendered)
        assert len(original_offsets) == 1, (chapter, verse, expected, original)
        start = original_offsets[0]
        end = start + len(expected)
        assert not any(e["startOffset"] < end and start < e["endOffset"] for e in occupied.get((chapter, verse), [])), (chapter, verse, expected, "overlap")
        entries.append({
            "book": "LEV", "chapter": chapter, "verse": verse,
            "expected": expected, "replacement": replacement,
            "category": category, "reason": reason,
            "evidence": [
                {"label": "Control contextual RVR1960", "url": f"https://www.biblegateway.com/passage/?search=Leviticus+{chapter}%3A{verse}&version=RVR1960"},
                {"label": "Control contextual NVI", "url": f"https://www.biblegateway.com/passage/?search=Leviticus+{chapter}%3A{verse}&version=NVI"},
            ],
        })

    # Every occurrence below was admitted only after the complete verse and its
    # ritual/legal context were reviewed. Existing v1 edits are skipped.
    for expected, (replacement, category, reason) in UNIFORM.items():
        for ref, rendered in current.items():
            if (expected, *ref) in UNIFORM_EXCLUSIONS:
                continue
            if len(offsets(rendered, expected)) == 1 and len(offsets(source[ref], expected)) == 1:
                start = offsets(source[ref], expected)[0]
                end = start + len(expected)
                if not any(e["startOffset"] < end and start < e["endOffset"] for e in occupied.get(ref, [])):
                    add(*ref, expected, replacement, category, reason)

    for expected, replacement in ENCLITICS.items():
        for ref, rendered in current.items():
            if len(offsets(rendered, expected)) == 1 and len(offsets(source[ref], expected)) == 1:
                start = offsets(source[ref], expected)[0]
                end = start + len(expected)
                if not any(e["startOffset"] < end and start < e["endOffset"] for e in occupied.get(ref, [])):
                    add(*ref, expected, replacement, "archaic-enclitic-order", "Se coloca el pronombre antes del verbo finito según el español actual, sin cambiar la acción ni sus participantes.")

    # Mas/Empero were checked as adversative connectors in every remaining verse.
    connector_exclusions = {(13, 33)}
    for ref, rendered in current.items():
        if ref in connector_exclusions:
            continue
        for expected, replacement in (("Empero", "Pero"), ("empero", "pero"), ("Mas", "Pero"), ("mas", "pero")):
            if len(offsets(rendered, expected)) == 1 and len(offsets(source[ref], expected)) == 1:
                start = offsets(source[ref], expected)[0]
                end = start + len(expected)
                before = source[ref][start - 1] if start else ""
                after = source[ref][end] if end < len(source[ref]) else ""
                if not before.isalpha() and not after.isalpha() and not any(e["startOffset"] < end and start < e["endOffset"] for e in occupied.get(ref, [])):
                    add(*ref, expected, replacement, "archaic-connector", f"{expected.capitalize()} tiene valor adversativo en el versículo; pero conserva la relación entre las cláusulas.")

    for item in SPECIAL:
        add(*item)

    # Duplicate offset or accidentally overlapping rules would make the package
    # ambiguous; reject them before writing any production input.
    by_ref = {}
    for entry in entries:
        ref = (entry["chapter"], entry["verse"])
        start = offsets(source[ref], entry["expected"])[0]
        span = (start, start + len(entry["expected"]), entry["expected"])
        for prior in by_ref.setdefault(ref, []):
            assert span[0] >= prior[1] or prior[0] >= span[1], (ref, prior, span)
        by_ref[ref].append(span)

    change_set = {
        "format": "shine-reading-2026-editorial-change-set",
        "schemaVersion": 1,
        "contentVersion": 17,
        "generatedAt": "2026-09-11T00:00:00.000Z",
        "issuedAt": "2026-09-11T00:00:00.000Z",
        "expiresAt": "2028-09-11T00:00:00.000Z",
        "sourceVersionId": "RV1909",
        "filterId": "RV1909-LECTURA-2026",
        "changes": sorted(entries, key=lambda e: (e["chapter"], e["verse"], offsets(source[(e["chapter"], e["verse"])], e["expected"])[0])),
        "pendingReview": [
            {"book": "LEV", "chapter": ch, "verse": vs, "term": term, "reason": reason}
            for ch, vs, term, reason in PENDING
        ],
    }
    CHANGE_SET.write_text(json.dumps(change_set, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    pending = [p for p in registry["pending"] if not p.get("id", "").startswith("leviticus-v17-")]
    for index, (chapter, verse, term, reason) in enumerate(PENDING, 1):
        pending.append({
            "id": f"leviticus-v17-{index}", "status": "pending-review", "scope": "old-testament",
            "term": term, "proposedOptions": ["Mantener con nota explicativa", "Actualizar tras revisión textual"],
            "reason": reason, "references": [{"book": "LEV", "chapter": chapter, "verse": verse}],
            "evidence": [{"label": "Control contextual RVR1960 y NVI", "url": f"https://www.biblegateway.com/passage/?search=Leviticus+{chapter}%3A{verse}&version=RVR1960%3BNVI"}],
        })
    registry.update({"updatedAt": "2026-09-11T00:00:00.000Z", "activeChangeSet": "editorial-changes/v17.json", "pending": pending})
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changes": len(entries), "changedVerses": len(by_ref), "pending": len(PENDING), "output": str(CHANGE_SET)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
