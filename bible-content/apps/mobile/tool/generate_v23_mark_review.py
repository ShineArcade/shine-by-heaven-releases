import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK = ROOT / "apps/mobile/assets/bibles/rv1909/books/MRK.json"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/mark_reading_2026.rv1909.v1.json"
CHANGE_SET = ROOT / "editorial-changes/v23.json"
REGISTRY = ROOT / "editorial-review/registry.json"
PACKAGE_SOURCE = ROOT / "apps/mobile/assets/bible_direction/reading_2026.package-source.json"
VERSION = 23


def item(chapter, verse, expected, replacement, category, reason, previous=None):
    value = {
        "book": "MRK", "chapter": chapter, "verse": verse,
        "expected": expected, "replacement": replacement,
        "category": category, "reason": reason,
        "evidence": [
            {"label": "Control contextual RVR1960, NVI, LBLA y RVC", "url": f"https://www.biblegateway.com/passage/?search=Marcos+{chapter}%3A{verse}&version=RVR1960%3BNVI%3BLBLA%3BRVC"},
        ],
    }
    if previous is not None:
        value["previousReplacement"] = previous
    return value


# Cada entrada se revisó dentro del versículo completo. Se excluyen variantes
# textuales, fórmulas doctrinales y metáforas cuya aclaración exige interpretación.
CHANGES = [
    item(1, 2, "envío á mi mensajero delante de tu faz, que apareje tu camino delante de ti", "envío a mi mensajero delante de ti, quien preparará tu camino", "archaic-presence-phrase", "La frase conserva el envío delante de Jesús y la preparación de su camino sin repetir una construcción antigua."),
    item(1, 6, "un cinto de cuero alrededor de sus lomos", "un cinturón de cuero alrededor de su cintura", "clear-clothing-phrase", "La frase describe un cinturón de cuero alrededor de la cintura de Juan."),
    item(1, 7, "desatar encorvado la correa de sus zapatos", "agacharme para desatar las correas de sus sandalias", "historical-footwear-phrase", "La acción es agacharse para desatar las correas de las sandalias; se conservan gesto y humildad."),
    item(1, 15, "El tiempo es cumplido", "El tiempo se ha cumplido", "grammar-fulfilled-time", "La forma actual conserva que el tiempo señalado ya llegó a su cumplimiento."),
    item(1, 19, "aderezaban las redes", "arreglaban las redes", "archaic-prepare-verb", "Aderezar las redes significa arreglarlas para volver a usarlas."),
    item(1, 22, "su doctrina", "su enseñanza", "false-friend-teaching-term", "Doctrina designa aquí la enseñanza que la multitud acaba de oír."),
    item(1, 22, "potestad", "autoridad", "archaic-authority-term", "Potestad significa la autoridad con la que Jesús enseñaba."),
    item(1, 23, "dió voces", "gritó", "archaic-cry-phrase", "Dar voces significa gritar; se conserva que el hombre interrumpió en voz alta."),
    item(1, 25, "riñó", "reprendió", "archaic-rebuke-verb", "Reñir significa reprender al espíritu con autoridad."),
    item(1, 25, "Enmudece", "Calla", "archaic-silence-command", "El mandato ordena al espíritu guardar silencio antes de salir."),
    item(1, 26, "el espíritu inmundo, haciéndole pedazos, y clamando á gran voz, salió", "el espíritu inmundo lo convulsionó y, clamando a gran voz, salió", "false-friend-convulsion-phrase", "El espíritu sacude al hombre con una convulsión; el texto no afirma que despedazó su cuerpo."),
    item(1, 27, "inquirían", "preguntaban", "archaic-inquiry-verb", "Inquirir entre sí significa preguntarse unos a otros qué había ocurrido."),
    item(1, 27, "potestad", "autoridad", "archaic-authority-term", "La multitud reconoce la autoridad con que Jesús manda a los espíritus."),
    item(1, 30, "calentura", "fiebre", "archaic-medical-term", "Calentura significa fiebre en la enfermedad de la suegra de Simón."),
    item(1, 31, "la dejó la calentura", "se le quitó la fiebre", "clear-healing-phrase", "La fiebre desaparece de la mujer después que Jesús la levanta."),
    item(1, 32, "los que tenían mal", "los enfermos", "archaic-illness-phrase", "La frase se refiere a quienes padecían enfermedades."),
    item(1, 35, "aun muy de noche", "cuando todavía estaba oscuro", "archaic-time-phrase", "La frase sitúa la salida de Jesús antes del amanecer."),
    item(1, 40, "é hincada la rodilla, le dice", "y arrodillándose, le dice", "archaic-kneeling-phrase", "Hincar la rodilla significa arrodillarse ante Jesús."),
    item(1, 44, "ofrece por tu limpieza lo que Moisés mandó", "presenta por tu purificación la ofrenda que Moisés mandó", "historical-purification-offering", "La instrucción exige presentar la ofrenda prescrita por Moisés para la purificación."),
    item(1, 45, "él salido", "cuando él salió", "archaic-participle-clause", "La forma actual aclara que, después de salir, el hombre comenzó a divulgar lo ocurrido."),
    item(1, 45, "manifiestamente", "públicamente", "archaic-public-adverb", "La frase indica que Jesús ya no podía entrar públicamente en la ciudad."),

    item(2, 1, "se oyó que estaba en casa", "se supo que estaba en casa", "clear-report-phrase", "La noticia de que Jesús estaba en casa se difundió por Capernaum."),
    item(2, 3, "unos trayendo un paralítico, que era traído por cuatro", "unos que traían a un paralítico entre cuatro personas", "clear-carrying-phrase", "Cuatro personas llevan al paralítico hasta Jesús."),
    item(2, 4, "á causa del gentío", "a causa de tanta gente", "false-friend-crowd-term", "Gentío designa la gran cantidad de personas que bloqueaba la entrada."),
    item(2, 4, "bajaron el lecho en que yacía el paralítico", "bajaron la camilla donde estaba acostado el paralítico", "historical-bed-phrase", "La camilla es el objeto que bajan por el techo con el paralítico acostado."),
    item(2, 10, "potestad", "autoridad", "archaic-authority-term", "Potestad significa autoridad para perdonar pecados."),
    item(2, 14, "al banco de los públicos tributos", "a la mesa de recaudación de impuestos", "historical-tax-phrase", "La frase identifica el puesto donde Leví cobraba impuestos."),
    item(2, 15, "publicanos", "recaudadores de impuestos", "historical-tax-term", "Publicanos eran recaudadores de impuestos en este contexto."),
    item(2, 16, "publicanos", "recaudadores de impuestos", "historical-tax-term", "Publicanos eran recaudadores de impuestos; el cambio se aplica a las dos menciones del versículo."),
    item(2, 17, "los que tienen mal", "los enfermos", "archaic-illness-phrase", "La comparación contrasta a las personas sanas con las enfermas."),
    item(2, 19, "los que están de bodas", "los invitados a la boda", "historical-wedding-phrase", "La expresión designa a quienes acompañan al novio durante la boda."),
    item(2, 21, "paño recio", "paño nuevo", "false-friend-cloth-term", "La comparación usa tela nueva sobre una prenda vieja."),
    item(2, 26, "panes de la proposición", "panes consagrados", "historical-sacred-bread", "La expresión se refiere al pan sagrado reservado para el servicio sacerdotal."),

    item(3, 1, "una mano seca", "una mano atrofiada", "historical-medical-phrase", "Seca describe una mano atrofiada o incapacitada, no falta de humedad."),
    item(3, 2, "le acechaban si en sábado le sanaría", "lo observaban atentamente para ver si lo sanaría en sábado", "archaic-surveillance-verb", "Lo vigilaban para acusarlo si sanaba en sábado."),
    item(3, 5, "condoleciéndose de la ceguedad de su corazón", "entristecido por la dureza de sus corazones", "false-friend-hardness-phrase", "El pasaje habla de dureza moral del corazón, no de ceguera física."),
    item(3, 9, "la barquilla", "una barca pequeña", "historical-vessel-term", "Barquilla significa una barca pequeña preparada para evitar que la multitud lo aplastara."),
    item(3, 9, "no le oprimiesen", "no lo aplastaran", "archaic-crowding-verb", "La barca evita que la multitud presione físicamente a Jesús."),
    item(3, 10, "caían sobre él", "se lanzaban sobre él", "clear-crowd-action", "Quienes padecían males se abalanzaban para tocarlo."),
    item(3, 10, "plagas", "dolencias", "false-friend-affliction-term", "Plagas designa aquí las dolencias que padecían quienes buscaban tocar a Jesús, no calamidades colectivas."),
    item(3, 12, "les reñía mucho que no", "les ordenaba firmemente que no", "archaic-rebuke-phrase", "Jesús ordena con firmeza que no revelen quién es."),
    item(3, 15, "potestad", "autoridad", "archaic-authority-term", "Potestad significa autoridad para sanar y expulsar demonios."),
    item(3, 17, "apellidó", "dio el sobrenombre", "archaic-naming-verb", "Jesús da a Jacobo y Juan el sobrenombre Boanerges."),
    item(3, 20, "ni aun podían comer pan", "ni siquiera podían comer", "archaic-meal-phrase", "La multitud era tan grande que Jesús y sus discípulos no podían detenerse a comer."),

    item(4, 2, "su doctrina", "su enseñanza", "false-friend-teaching-term", "Doctrina designa aquí la enseñanza comunicada por parábolas."),
    item(4, 4, "las aves del cielo, y la tragaron", "las aves del cielo y se la comieron", "archaic-eating-verb", "Las aves comen la semilla que cayó junto al camino."),
    item(4, 5, "pedregales", "terreno pedregoso", "archaic-ground-term", "Pedregales describe el terreno con poca profundidad de tierra."),
    item(4, 8, "llevó uno á treinta, y otro á sesenta, y otro á ciento", "produjo a treinta, a sesenta y a ciento por uno", "historical-yield-phrase", "La frase expresa el rendimiento multiplicado de la semilla en buena tierra."),
    item(4, 16, "la toman con gozo", "la reciben con alegría", "archaic-reception-phrase", "La imagen describe recibir la palabra con alegría."),
    item(4, 17, "antes son temporales, que en levantándose la tribulación ó la persecución por causa de la palabra, luego se escandalizan", "sino que duran poco tiempo; cuando surge la tribulación o la persecución por causa de la palabra, abandonan la fe", "context-reviewed-fall-away", "La frase completa aclara la corta duración y el abandono bajo persecución sin romper su concordancia."),
    item(4, 19, "los cuidados de este siglo", "las preocupaciones de este mundo", "archaic-worry-phrase", "La frase designa preocupaciones de la vida presente que ahogan la palabra."),
    item(4, 19, "las codicias que hay en las otras cosas", "los deseos de otras cosas", "archaic-desire-phrase", "Codicias abarca aquí deseos que entran y ahogan la palabra."),
    item(4, 21, "debajo del almud", "debajo de una canasta", "historical-container-term", "Almud designa el recipiente que cubre la lámpara; canasta conserva la imagen sin sugerir un cajón rígido.", "debajo de un cajón"),
    item(4, 21, "¿Tráese la antorcha", "¿Se trae la lámpara", "historical-lamp-term", "La imagen presenta una lámpara que se coloca para alumbrar."),
    item(4, 21, "candelero", "soporte para lámpara", "historical-lampstand-term", "El objeto eleva la lámpara para que alumbre."),
    item(4, 28, "de suyo", "por sí sola", "archaic-self-action-phrase", "La tierra produce el fruto por sí sola dentro de la parábola."),
    item(4, 29, "cuando el fruto fuere producido, luego se mete la hoz, porque la siega es llegada", "cuando el fruto está maduro, se usa la hoz, porque ha llegado la cosecha", "historical-harvest-phrase", "La frase conserva la maduración del fruto, el uso de la hoz y la llegada de la cosecha en un orden comprensible."),
    item(4, 31, "simientes", "semillas", "archaic-seed-term", "La comparación se refiere a semillas botánicas."),
    item(4, 32, "todas las legumbres", "todas las plantas del huerto", "historical-garden-term", "La comparación es con las plantas cultivadas del huerto, no solo con verduras comestibles."),
    item(4, 32, "morar bajo su sombra", "refugiarse bajo su sombra", "archaic-dwelling-phrase", "Las aves encuentran refugio bajo la sombra de las ramas de la planta."),
    item(4, 34, "declaraba todo", "explicaba todo", "archaic-explanation-verb", "En privado Jesús explicaba las parábolas a sus discípulos."),
    item(4, 36, "despachando la multitud", "despidiendo a la multitud", "archaic-dismissal-verb", "La acción es despedir a la gente antes de cruzar el lago."),
    item(4, 37, "ya se henchía", "ya se llenaba", "archaic-vessel-phrase", "Las olas llenaban de agua la barca durante la tormenta."),
    item(4, 39, "increpó al viento", "reprendió al viento", "archaic-rebuke-verb", "Jesús reprende al viento antes de ordenar al mar que calle."),
    item(4, 39, "grande bonanza", "gran calma", "archaic-calm-term", "Bonanza significa la calma que siguió al cese del viento."),
    item(4, 40, "amedrentados", "atemorizados", "archaic-fear-term", "Amedrentados significa dominados por el miedo."),

    item(5, 3, "tenía domicilio en los sepulcros", "vivía entre los sepulcros", "archaic-dwelling-phrase", "El hombre habitaba entre los sepulcros."),
    item(5, 4, "con grillos y cadenas", "con grilletes y cadenas", "historical-restraint-term", "Grillos son grilletes colocados en los pies."),
    item(5, 4, "los grillos desmenuzados", "los grilletes rotos", "historical-restraint-term", "Grillos son grilletes colocados en los pies y desmenuzados significa que habían sido rotos."),
    item(5, 17, "los términos de ellos", "su región", "false-friend-region", "Términos significa el territorio de aquella población."),
    item(5, 18, "había sido fatigado del demonio", "había estado poseído por el demonio", "false-friend-demon-phrase", "Fatigado no describe cansancio: el hombre había estado bajo posesión demoníaca."),
    item(5, 21, "gran compañía", "una gran multitud", "false-friend-crowd-term", "Compañía designa aquí una multitud reunida alrededor de Jesús."),
    item(5, 22, "príncipes de la sinagoga", "dirigentes de la sinagoga", "historical-synagogue-role", "La frase identifica a los responsables de la sinagoga."),
    item(5, 23, "está á la muerte", "está a punto de morir", "archaic-near-death-phrase", "La hija de Jairo se encuentra al borde de la muerte."),
    item(5, 23, "para que sea salva", "para que sane", "context-reviewed-healing-phrase", "En este contexto la petición inmediata de Jairo es que su hija sane y siga viviendo."),
    item(5, 25, "una mujer que estaba con flujo de sangre doce años hacía", "una mujer que padecía hemorragias desde hacía doce años", "historical-medical-term", "La mujer padecía hemorragias de manera continua desde hacía doce años."),
    item(5, 26, "nada había aprovechado", "no había mejorado", "archaic-medical-result", "A pesar de los tratamientos, su condición no había mejorado."),
    item(5, 29, "la fuente de su sangre se secó", "se detuvo la hemorragia", "historical-medical-phrase", "La hemorragia se detuvo inmediatamente."),
    item(5, 29, "aquel azote", "aquella enfermedad", "false-friend-affliction-term", "Azote designa la enfermedad que la atormentaba."),
    item(5, 30, "la virtud que había salido de él", "el poder que había salido de él", "false-friend-power-term", "Virtud significa aquí poder, no conducta moral."),
    item(5, 30, "á la compañía", "a la multitud", "false-friend-crowd-term", "Compañía designa a la multitud que rodeaba a Jesús."),
    item(5, 35, "Tu hija es muerta", "Tu hija ha muerto", "grammar-death-phrase", "La forma actual comunica la noticia de que la niña ya había muerto."),
    item(5, 35, "¿para qué fatigas más al Maestro?", "¿para qué molestas más al Maestro?", "false-friend-trouble-verb", "La pregunta sugiere que ya no vale la pena molestar al Maestro después de la muerte de la niña."),
    item(5, 38, "el alboroto", "la conmoción", "archaic-commotion-term", "La casa estaba llena de conmoción, llanto y lamentos."),
    item(5, 40, "hacían burla de él", "se burlaban de él", "archaic-mockery-phrase", "Las personas se burlaban de la afirmación de Jesús."),
    item(5, 40, "echados fuera todos", "después de hacer salir a todos", "archaic-dismissal-clause", "Jesús hace salir a la multitud antes de entrar con los padres y sus acompañantes."),
    item(5, 41, "que es, si lo interpretares", "que traducido significa", "archaic-translation-phrase", "El narrador explica el significado de Talitha cumi."),
    item(5, 42, "se espantaron de grande espanto", "quedaron sumamente asombrados", "archaic-amazement-phrase", "La repetición antigua expresa gran asombro ante la resurrección de la niña."),

    item(6, 1, "su tierra", "su pueblo", "false-friend-hometown-term", "Jesús vuelve a su lugar de origen acompañado por sus discípulos."),
    item(6, 2, "tales maravillas que por sus manos son hechas", "tales milagros realizados por sus manos", "archaic-miracle-term", "Maravillas designa los milagros realizados por sus manos; la frase completa conserva la concordancia al cambiar el sustantivo a masculino."),
    item(6, 3, "se escandalizaban en él", "lo rechazaban", "context-reviewed-rejection-phrase", "La familiaridad con Jesús les impedía aceptarlo; el contexto expresa rechazo."),
    item(6, 7, "potestad", "autoridad", "archaic-authority-term", "Potestad significa autoridad sobre los espíritus impuros."),
    item(6, 8, "báculo", "bastón", "historical-travel-staff", "Báculo significa bastón de viaje en la instrucción a los doce."),
    item(6, 8, "alforja", "bolsa de viaje", "historical-travel-bag", "Alforja es la bolsa usada para provisiones durante el viaje y se distingue de la bolsa del dinero."),
    item(6, 10, "posad", "quedaos", "archaic-stay-verb", "La orden es permanecer en la misma casa hasta salir de aquel lugar."),
    item(6, 14, "virtudes obran en él", "poderes milagrosos actúan en él", "false-friend-miraculous-power", "Virtudes designa aquí poderes milagrosos, no cualidades morales."),
    item(6, 19, "Herodías le acechaba", "Herodías le guardaba rencor", "false-friend-grudge-phrase", "El verbo expresa hostilidad persistente y deseo de matarlo, no vigilancia física."),
    item(6, 25, "prestamente", "de inmediato", "archaic-speed-adverb", "La joven regresa de inmediato con su petición."),
    item(6, 27, "uno de la guardia", "un verdugo de la guardia", "historical-executioner-role", "El guardia enviado recibe la orden específica de decapitar a Juan."),
    item(6, 31, "reposad un poco", "descansad un poco", "archaic-rest-verb", "Jesús invita a los discípulos a descansar después de la actividad continua."),
    item(6, 31, "ni aun tenían lugar de comer", "ni siquiera tenían tiempo para comer", "false-friend-opportunity-phrase", "Lugar significa aquí oportunidad o tiempo disponible para comer, no un sitio físico."),
    item(6, 33, "concurrieron allá muchos á pie", "corrieron allá muchos a pie", "archaic-movement-verb", "La gente llegó corriendo desde las ciudades y se adelantó a la barca."),
    item(6, 35, "ya fuese el día muy entrado", "ya era muy tarde", "archaic-time-phrase", "Los discípulos señalan que la hora estaba avanzada."),
    item(6, 35, "el día ya muy entrado", "ya es muy tarde", "archaic-time-phrase", "La segunda mención confirma que la hora estaba avanzada."),
    item(6, 36, "cortijos", "caseríos", "historical-rural-place", "Cortijos designa pequeños asentamientos o casas rurales de los alrededores."),
    item(6, 39, "por partidas", "por grupos", "archaic-group-term", "Jesús organiza a la multitud en grupos sobre la hierba."),
    item(6, 40, "por partidas", "en grupos", "archaic-group-term", "La multitud se sentó organizada en grupos de cien y de cincuenta."),
    item(6, 42, "se hartaron", "quedaron satisfechos", "archaic-satisfaction-verb", "Todos comieron hasta quedar satisfechos."),
    item(6, 45, "dió priesa á sus discípulos á subir en el barco, é ir delante de él", "hizo que sus discípulos subieran de inmediato al barco y fueran delante de él", "archaic-urgency-phrase", "Jesús los hizo embarcarse sin demora mientras despedía a la multitud."),
    item(6, 48, "fatigados bogando", "esforzándose por remar", "archaic-rowing-phrase", "El viento contrario hacía difícil remar."),
    item(6, 48, "cerca de la cuarta vigilia de la noche", "de madrugada", "historical-night-watch", "La cuarta vigilia corresponde a las últimas horas de la noche, antes del amanecer."),
    item(6, 50, "Alentaos", "Ánimo", "archaic-encouragement-command", "Jesús los anima al identificarse y ordenarles que no teman."),
    item(6, 52, "estaban ofuscados sus corazones", "sus corazones estaban endurecidos", "false-friend-hardness-phrase", "El versículo explica su falta de comprensión por la dureza de sus corazones."),
    item(6, 53, "tomaron puerto", "llegaron a la orilla", "archaic-landing-phrase", "La barca cruza y llega a tierra en Genesaret."),

    item(7, 2, "manos comunes", "manos impuras", "historical-ritual-term", "Comunes significa ritualmente impuras; el propio versículo aclara que no estaban lavadas."),
    item(7, 2, "es á saber", "es decir", "archaic-explanation-phrase", "La locución introduce la explicación de que las manos no estaban lavadas."),
    item(7, 2, "los condenaban", "los criticaban", "false-friend-criticism-verb", "El contexto describe la crítica de los adversarios por comer sin el lavado ritual, no una sentencia judicial."),
    item(7, 11, "Es Corbán (quiere decir, don mío á Dios )", "Es Corbán (es decir, una ofrenda dedicada a Dios)", "historical-dedicated-gift", "Corbán designa una ofrenda dedicada a Dios y explica la excusa dada a los padres."),
    item(7, 13, "que disteis", "que habéis transmitido", "false-friend-tradition-verb", "La tradición fue transmitida de generación en generación."),
    item(7, 18, "sin entendimiento", "sin comprender", "archaic-understanding-phrase", "Jesús pregunta por qué todavía no comprenden la enseñanza."),
    item(7, 19, "sale á la secreta", "sale del cuerpo", "archaic-bodily-phrase", "La frase describe la eliminación corporal de los alimentos sin conservar un eufemismo hoy opaco."),
    item(7, 19, "haciendo limpias todas las viandas", "declarando limpios todos los alimentos", "archaic-food-term", "La frase concluye que todos los alimentos quedan declarados limpios."),
    item(7, 24, "los términos de Tiro y de Sidón", "la región de Tiro y Sidón", "false-friend-region", "Términos designa la región, no límites verbales o condiciones."),
    item(7, 29, "Por esta palabra", "Por esta respuesta", "false-friend-answer-phrase", "Jesús responde a lo que la mujer acaba de decir."),
    item(7, 32, "un sordo y tartamudo", "un hombre sordo y con dificultad para hablar", "historical-speech-phrase", "La persona tenía una dificultad del habla además de no poder oír."),
    item(7, 35, "fué desatada la ligadura de su lengua, y hablaba bien", "desapareció el impedimento de su lengua, y hablaba con claridad", "clear-speech-phrase", "Después de la sanidad desapareció el impedimento del habla y el hombre pudo hablar claramente."),

    item(8, 11, "altercar", "discutir", "archaic-dispute-verb", "Los fariseos comenzaron a discutir con Jesús mientras lo ponían a prueba."),
    item(8, 11, "tentándole", "poniéndolo a prueba", "false-friend-test-verb", "La petición de una señal buscaba poner a Jesús a prueba, no describir una tentación moral."),
    item(8, 15, "les mandó", "les advirtió", "false-friend-warning-verb", "Jesús les advierte que se cuiden de la levadura de los fariseos y de Herodes."),
    item(8, 16, "altercaban los unos con los otros diciendo: Pan no tenemos", "discutían entre sí porque no tenían pan", "archaic-dispute-clause", "La frase conserva que los discípulos discutían entre sí por no haber llevado pan."),
    item(8, 17, "¿Qué altercáis", "¿Por qué discutís", "archaic-dispute-phrase", "Jesús pregunta por la discusión que sostienen acerca del pan."),
    item(8, 24, "Veo los hombres, pues veo que andan como árboles", "Veo a los hombres; parecen árboles que caminan", "clear-partial-sight-phrase", "La frase conserva la visión parcial del hombre y su comparación con árboles que caminan."),
    item(8, 25, "vió de lejos y claramente á todos", "vio todo con claridad", "clear-restored-sight-phrase", "La segunda imposición de manos restaura por completo la visión."),
    item(8, 31, "padeciese mucho, y ser reprobado de los ancianos, y de los príncipes de los sacerdotes, y de los escribas, y ser muerto, y resucitar después de tres días", "padeciese mucho, fuese rechazado por los ancianos, los principales sacerdotes y los escribas, fuera muerto y resucitara después de tres días", "archaic-rejection-clause", "La frase completa conserva el sufrimiento, el rechazo por los dirigentes, la muerte y la resurrección, y evita mezclar formas verbales incompatibles."),
    item(8, 33, "riñó á Pedro", "reprendió a Pedro", "archaic-rebuke-verb", "Jesús reprende a Pedro después de volverse hacia los discípulos."),
    item(8, 33, "no sabes las cosas que son de Dios", "no pones la mira en las cosas de Dios", "false-friend-mindset-phrase", "La reprensión se refiere a orientar la mente hacia los intereses de Dios, no a falta de información."),
    item(8, 37, "¿O qué recompensa dará el hombre por su alma?", "¿O qué dará el hombre a cambio de su alma?", "false-friend-exchange-term", "La pregunta es qué puede darse a cambio del alma, no qué premio se recibe."),

    item(9, 3, "lavador", "lavandero", "historical-launderer-term", "La blancura supera lo que cualquier lavandero podría conseguir."),
    item(9, 5, "pabellones", "refugios", "historical-shelter-term", "Pabellones designa refugios o enramadas para Jesús, Moisés y Elías."),
    item(9, 6, "Porque no sabía lo que hablaba; que estaban espantados", "No sabía qué decir, pues estaban espantados", "archaic-causal-clause", "La frase conserva que Pedro habló sin saber qué decir debido al temor de los presentes, sin repetir dos conectores causales."),
    item(9, 12, "restituirá", "restaurará", "archaic-restore-verb", "Restituir todas las cosas significa restaurarlas."),
    item(9, 18, "le despedaza", "lo convulsiona", "false-friend-convulsion-verb", "El espíritu provoca convulsiones; no despedaza el cuerpo del muchacho."),
    item(9, 18, "echa espumarajos", "echa espuma por la boca", "archaic-seizure-phrase", "La frase describe la espuma producida durante la convulsión."),
    item(9, 18, "cruje los dientes", "rechina los dientes", "archaic-seizure-phrase", "Rechinar los dientes expresa el movimiento involuntario descrito."),
    item(9, 18, "se va secando", "queda rígido", "false-friend-seizure-phrase", "La descripción culmina con rigidez corporal, no con deshidratación."),
    item(9, 19, "os tengo de sufrir", "tendré que soportaros", "archaic-endure-phrase", "Sufrir significa soportar en la lamentación de Jesús."),
    item(9, 20, "le desgarraba", "lo convulsionó", "false-friend-convulsion-verb", "El espíritu sacude al muchacho con una convulsión al ver a Jesús."),
    item(9, 20, "echando espumarajos", "echando espuma por la boca", "archaic-seizure-phrase", "La frase describe la espuma producida durante la convulsión."),
    item(9, 21, "¿Cuánto tiempo há que le aconteció esto?", "¿Desde cuándo le sucede esto?", "archaic-duration-question", "La pregunta busca desde cuándo padece el muchacho."),
    item(9, 26, "el espíritu clamando y desgarrándole mucho, salió", "el espíritu clamó, lo convulsionó violentamente y salió", "false-friend-convulsion-phrase", "El espíritu grita, causa una convulsión violenta y sale; desgarrar no describe que rompiera el cuerpo del muchacho."),
    item(9, 35, "el postrero", "el último", "archaic-rank-term", "Postrero significa último en el contraste con querer ser primero."),
    item(9, 42, "escandalizare á uno de estos pequeñitos", "haga caer a uno de estos pequeños", "context-reviewed-stumbling-phrase", "Escandalizar significa causar una caída espiritual, no provocar sorpresa."),
    item(9, 50, "la sal fuere desabrida", "la sal pierde su sabor", "archaic-salt-phrase", "Desabrida significa que la sal ha perdido su sabor."),
    item(9, 50, "la adobaréis", "la sazonarán", "archaic-season-verb", "Adobar la sal significa devolverle capacidad de sazonar."),

    item(10, 1, "los términos de Judea", "la región de Judea", "false-friend-region", "Términos designa la región geográfica de Judea."),
    item(10, 2, "para tentarle", "para ponerlo a prueba", "false-friend-test-verb", "Los fariseos plantean la pregunta para poner a prueba a Jesús."),
    item(10, 2, "repudiar á su mujer", "divorciarse de su mujer", "archaic-divorce-phrase", "Repudiar a la esposa significa divorciarse de ella."),
    item(10, 4, "carta de divorcio, y repudiar", "un certificado de divorcio y divorciarse", "historical-divorce-phrase", "La respuesta alude al documento de divorcio y a la separación legal, con el artículo necesario en español actual."),
    item(10, 11, "repudiare á su mujer, y se casare con otra", "se divorcie de su mujer y se case con otra", "archaic-divorce-phrase", "Repudiar significa divorciarse en la enseñanza de Jesús y se conserva la correlación verbal."),
    item(10, 13, "reñían á los que los presentaban", "reprendían a quienes los presentaban", "archaic-rebuke-verb", "Los discípulos reprendían a quienes acercaban a los niños."),
    item(10, 14, "Dejad los niños venir, y no se lo estorbéis", "Dejad que los niños vengan, y no se lo impidáis", "archaic-hinder-clause", "Jesús ordena permitir que los niños se acerquen y no impedírselo."),
    item(10, 17, "hincando la rodilla", "arrodillándose", "archaic-kneeling-phrase", "El hombre se arrodilla ante Jesús para hacer su pregunta."),
    item(10, 17, "poseer la vida eterna", "heredar la vida eterna", "false-friend-inherit-verb", "La pregunta usa la imagen bíblica de recibir la vida eterna como herencia."),
    item(10, 19, "No hurtes", "No robes", "archaic-steal-verb", "Hurtar significa robar en la lista de mandamientos."),
    item(10, 19, "No defraudes", "No engañes", "archaic-defraud-verb", "Defraudar significa engañar o privar injustamente a otra persona."),
    item(10, 31, "muchos primeros serán postreros, y postreros primeros", "muchos de los primeros serán últimos, y los últimos serán primeros", "archaic-order-clause", "La frase conserva la inversión entre primeros y últimos e incorpora los artículos necesarios para una lectura natural."),
    item(10, 33, "príncipes de los sacerdotes", "principales sacerdotes", "historical-priestly-role", "La frase identifica al grupo dirigente de los sacerdotes."),
    item(10, 34, "le escarnecerán", "se burlarán de él", "archaic-mockery-verb", "Escarnecer significa burlarse cruelmente de Jesús."),
    item(10, 34, "azotarán", "golpearán con látigos", "historical-scourging-phrase", "Azotar describe el castigo con látigos antes de la muerte."),
    item(10, 42, "se ven ser príncipes", "son reconocidos como gobernantes", "archaic-ruler-phrase", "La frase identifica a quienes son considerados gobernantes de las naciones."),
    item(10, 42, "se enseñorean de ellas", "las dominan", "archaic-domination-verb", "Enseñorearse significa ejercer dominio sobre otros."),
    item(10, 42, "potestad", "autoridad", "archaic-authority-term", "Potestad significa autoridad ejercida por los gobernantes."),
    item(10, 46, "una gran compañía", "una gran multitud", "false-friend-crowd-term", "Compañía designa aquí la multitud que seguía a Jesús."),
    item(10, 49, "Ten confianza", "Ten ánimo", "archaic-encouragement-phrase", "La gente anima al ciego porque Jesús lo está llamando."),
    item(10, 51, "cobre la vista", "recobre la vista", "archaic-sight-verb", "El hombre pide recuperar la capacidad de ver."),

    item(11, 1, "monte de las Olivas", "monte de los Olivos", "historical-place-name", "El nombre actual del lugar es monte de los Olivos."),
    item(11, 2, "Id al lugar que está delante de vosotros", "Id a la aldea que está frente a vosotros", "archaic-location-phrase", "Jesús los envía a la aldea que tienen delante."),
    item(11, 2, "luego entrados en él", "al entrar en ella", "grammar-village-pronoun", "El pronombre se refiere a la aldea y debe concordar en femenino; la acción ocurre al entrar en ella."),
    item(11, 15, "trastornó las mesas", "volcó las mesas", "false-friend-overturn-verb", "Trastornar significa aquí volcar físicamente las mesas."),
    item(11, 16, "llevase vaso", "transportara ningún objeto", "false-friend-carried-object", "Vaso significa aquí cualquier objeto o mercancía transportada por el templo; la frase completa conserva la prohibición."),
    item(11, 18, "su doctrina", "su enseñanza", "false-friend-teaching-term", "La multitud estaba asombrada por la enseñanza de Jesús."),
    item(11, 21, "Pedro acordándose", "Pedro, recordando", "archaic-memory-verb", "Pedro recordó la declaración de Jesús sobre la higuera."),
    item(11, 28, "facultad", "autoridad", "false-friend-authority-term", "Facultad significa la autoridad para realizar esas acciones."),
    item(11, 29, "Os preguntaré también yo una palabra", "Os haré también una pregunta", "false-friend-question-phrase", "Palabra designa aquí una pregunta que Jesús les pide contestar."),
    item(11, 29, "facultad", "autoridad", "false-friend-authority-term", "Facultad significa la autoridad para realizar esas acciones."),

    item(12, 1, "la cercó con seto", "la rodeó con una cerca", "archaic-fence-phrase", "El propietario rodeó la viña con una cerca."),
    item(12, 1, "un lagar", "una prensa para uvas", "historical-winepress-term", "Lagar es la instalación donde se exprimían las uvas."),
    item(12, 1, "labradores", "agricultores arrendatarios", "historical-tenant-term", "Los labradores cultivaban la viña arrendada y debían entregar parte del fruto."),
    item(12, 3, "le hirieron", "lo golpearon", "archaic-assault-verb", "Los arrendatarios golpearon al siervo y lo enviaron vacío."),
    item(12, 4, "volvieron á enviarle afrentado", "lo despidieron humillado", "archaic-abuse-phrase", "Afrentar significa tratar vergonzosamente al siervo; la frase actual evita sugerir que lo enviaron de nuevo a los mismos arrendatarios."),
    item(12, 6, "el postrero", "por último", "archaic-final-sequence", "El dueño envía finalmente a su hijo amado."),
    item(12, 6, "Tendrán en reverencia", "Respetarán", "archaic-respect-phrase", "El dueño espera que respeten a su hijo."),
    item(12, 7, "heredad", "herencia", "archaic-inheritance-term", "Heredad designa la herencia que los arrendatarios quieren tomar."),
    item(12, 10, "es puesta por cabeza de esquina", "se ha convertido en la piedra angular", "historical-building-term", "La cita identifica la piedra principal del edificio."),
    item(12, 13, "para que le sorprendiesen en alguna palabra", "para atraparlo en sus propias palabras", "archaic-trap-phrase", "Los enviados intentan obtener una respuesta que puedan usar contra Jesús."),
    item(12, 15, "¿Por qué me tentáis?", "¿Por qué intentáis ponerme a prueba?", "false-friend-test-verb", "Jesús reconoce que intentan ponerlo a prueba con la pregunta del tributo."),
    item(12, 19, "levante linaje á su hermano", "dé descendencia a su hermano", "historical-offspring-phrase", "La ley buscaba conservar la descendencia del hermano fallecido."),
    item(12, 24, "la potencia de Dios", "el poder de Dios", "archaic-power-term", "Potencia significa el poder de Dios para resucitar a los muertos."),
    item(12, 28, "disputar", "debatir", "archaic-discussion-verb", "El escriba había oído a Jesús debatir con los saduceos."),
    item(12, 34, "osaba preguntarle", "se atrevía a preguntarle", "archaic-dare-verb", "Después de su respuesta nadie se atrevía a hacerle otra pregunta."),
    item(12, 36, "á mi diestra", "a mi derecha", "archaic-direction-term", "Diestra significa el lado derecho en la cita del salmo."),
    item(12, 37, "¿de dónde, pues, es su hijo?", "¿cómo, pues, es su hijo?", "semantic-question-correction", "La pregunta es cómo puede el Mesías ser hijo de David si David lo llama Señor; no pregunta por un lugar de procedencia."),
    item(12, 37, "los que eran del común del pueblo", "la gente común", "archaic-ordinary-people", "La gente común escuchaba a Jesús con agrado."),
    item(12, 37, "le oían de buena gana", "lo oía con agrado", "grammar-collective-subject", "El verbo y el pronombre concuerdan con el sujeto colectivo singular la gente común."),
    item(12, 38, "su doctrina", "su enseñanza", "false-friend-teaching-term", "Doctrina designa la enseñanza pública de Jesús."),
    item(12, 38, "las salutaciones", "los saludos", "archaic-greeting-term", "Salutaciones significa saludos públicos en las plazas."),
    item(12, 39, "las primeras sillas", "los asientos principales", "historical-seat-term", "La frase se refiere a los lugares de honor en las sinagogas."),
    item(12, 39, "primeros asientos en las cenas", "lugares de honor en los banquetes", "historical-banquet-place", "Los escribas buscaban los lugares de honor en las comidas formales."),
    item(12, 40, "por pretexto hacen largas oraciones", "para aparentar hacen largas oraciones", "false-friend-pretense-phrase", "Las oraciones largas se usan como apariencia religiosa mientras explotan a las viudas."),
    item(12, 41, "arca de la ofrenda", "tesoro del templo", "historical-temple-treasury", "La escena ocurre frente al lugar donde se depositaban las ofrendas."),
    item(12, 41, "en el arca", "en el tesoro", "historical-temple-treasury", "El dinero se depositaba en el tesoro del templo."),
    item(12, 44, "ésta, de su pobreza echó todo lo que tenía, todo su alimento", "ésta, aun en su pobreza, echó todo lo que tenía para vivir", "false-friend-livelihood-phrase", "La viuda entregó todos sus recursos para vivir; la frase completa evita duplicar todo lo que tenía."),

    item(13, 3, "monte de las Olivas", "monte de los Olivos", "historical-place-name", "El nombre actual del lugar es monte de los Olivos."),
    item(13, 8, "principios de dolores serán estos", "estos serán el principio de los dolores de parto", "context-reviewed-birth-pains", "La imagen compara los primeros acontecimientos con el comienzo de los dolores de parto."),
    item(13, 9, "vosotros mirad por vosotros", "mirad por vosotros mismos", "archaic-reflexive-warning", "La advertencia pide a los discípulos estar atentos a lo que les sucederá, sin repetir vosotros."),
    item(13, 9, "concilios", "tribunales", "historical-judicial-term", "Los concilios son tribunales locales ante los que serían entregados."),
    item(13, 9, "seréis llamados", "compareceréis", "false-friend-court-appearance", "Los discípulos serían llevados ante gobernadores y reyes para dar testimonio."),
    item(13, 17, "las preñadas, y de las que criaren", "las embarazadas y de las que estén amamantando", "archaic-pregnancy-and-nursing", "La advertencia incluye a las mujeres embarazadas y a las que estén amamantando en aquellos días."),
    item(13, 19, "que crió Dios", "que Dios creó", "archaic-create-spelling", "Criar conserva aquí el sentido antiguo de crear; la forma actual evita confundirlo con educar."),
    item(13, 20, "ninguna carne se salvaría", "nadie sobreviviría", "context-reviewed-survival-phrase", "Carne representa a los seres humanos y el contexto habla de sobrevivir aquellos días."),
    item(13, 20, "por causa de los escogidos que él escogió", "por causa de los escogidos a quienes eligió", "archaic-election-clause", "La frase conserva que el Señor eligió a los escogidos y evita una repetición que dificulta la lectura."),
    item(13, 25, "las virtudes que están en los cielos serán conmovidas", "los poderes que están en los cielos serán conmovidos", "false-friend-cosmic-power", "Virtudes significa poderes celestiales, no cualidades morales."),
    item(13, 26, "mucha potestad", "gran poder", "context-reviewed-power-term", "La venida del Hijo del hombre se describe con gran poder y gloria."),
    item(13, 27, "desde el cabo de la tierra", "desde el extremo de la tierra", "archaic-extremity-phrase", "La frase expresa el límite más lejano de la tierra."),
    item(13, 27, "hasta el cabo", "hasta el extremo", "archaic-extremity-phrase", "La frase expresa el límite más lejano del cielo.", "hasta el fin"),
    item(13, 27, "juntará sus escogidos", "reunirá a sus escogidos", "archaic-gathering-phrase", "Los ángeles reunirán a los escogidos desde los extremos descritos."),
    item(13, 34, "dió facultad", "dio autoridad", "false-friend-authority-term", "El dueño delega autoridad a sus siervos durante su ausencia."),
    item(13, 34, "el hombre que partiéndose lejos", "un hombre que se fue lejos", "archaic-departure-clause", "La comparación presenta a un hombre que se marcha y deja responsabilidades a sus siervos."),

    item(14, 1, "príncipes de los sacerdotes", "principales sacerdotes", "historical-priestly-role", "La frase identifica al grupo dirigente de los sacerdotes."),
    item(14, 1, "por engaño", "con engaño", "grammar-deception-phrase", "Buscaban una manera engañosa de arrestar y matar a Jesús."),
    item(14, 1, "los días de los panes sin levadura", "la fiesta de los panes sin levadura", "historical-feast-name", "La expresión nombra la fiesta de los panes sin levadura que seguía a la Pascua."),
    item(14, 3, "un alabastro de ungüento de nardo espique de mucho precio", "un frasco de alabastro con perfume de nardo puro muy costoso", "historical-perfume-container", "La mujer trae un frasco de alabastro con perfume costoso de nardo para ungir a Jesús."),
    item(14, 3, "quebrando el alabastro", "rompiendo el frasco", "false-friend-container-material", "Alabastro nombra el material del frasco; la mujer rompe el recipiente antes de derramar el perfume."),
    item(14, 6, "¿por qué la fatigáis?", "¿por qué la molestáis?", "false-friend-trouble-verb", "Jesús pregunta por qué están molestando a la mujer que hizo una buena obra."),
    item(14, 6, "buena obra me ha hecho", "Ha hecho una buena obra conmigo", "archaic-benefit-clause", "Jesús declara que la mujer ha realizado una buena obra con él; se conserva el inicio de oración después de la pregunta."),
    item(14, 11, "se holgaron", "se alegraron", "archaic-gladness-verb", "Los principales sacerdotes se alegraron al oír la propuesta de Judas."),
    item(14, 11, "dineros", "dinero", "archaic-money-plural", "La promesa consiste en entregar dinero a Judas; el plural antiguo no añade varias monedas o pagos distintos."),
    item(14, 12, "á disponer", "a preparar", "archaic-prepare-verb", "Los discípulos preguntan dónde deben preparar la Pascua."),
    item(14, 12, "sacrificaban la pascua", "sacrificaban el cordero pascual", "historical-passover-sacrifice", "La acción concreta del primer día era sacrificar el cordero de la Pascua."),
    item(14, 15, "un gran cenáculo ya preparado", "una gran habitación superior ya preparada", "historical-upper-room", "El hombre mostraría una gran habitación en la planta superior, amueblada y lista."),
    item(14, 15, "aderezad", "preparad", "archaic-prepare-verb", "Los discípulos deben preparar allí la Pascua."),
    item(14, 16, "aderezaron", "prepararon", "archaic-prepare-verb", "Los discípulos prepararon la Pascua como Jesús indicó."),
    item(14, 23, "tomando el vaso", "tomando la copa", "historical-cup-term", "Vaso designa la copa compartida durante la cena."),
    item(14, 23, "bebieron de él todos", "todos bebieron de ella", "grammar-cup-pronoun", "El pronombre concuerda con copa después de modernizar el recipiente."),
    item(14, 26, "Y como hubieron cantado el himno, se salieron", "Y después de cantar el himno, salieron", "archaic-departure-clause", "Después de cantar el himno, Jesús y los discípulos salieron hacia el monte."),
    item(14, 26, "monte de las Olivas", "monte de los Olivos", "historical-place-name", "El nombre actual del lugar es monte de los Olivos."),
    item(14, 27, "seréis escandalizados en mí", "me abandonaréis", "context-reviewed-desertion-phrase", "La cita siguiente explica que los discípulos se dispersarán cuando hieran al pastor."),
    item(14, 27, "serán derramadas las ovejas", "serán dispersadas las ovejas", "false-friend-scattering-verb", "La cita describe la dispersión de las ovejas después de herir al pastor, no que sean derramadas como un líquido."),
    item(14, 31, "con mayor porfía", "con mayor insistencia", "archaic-insistence-term", "Pedro insistía con más vehemencia en que no negaría a Jesús."),
    item(14, 33, "comenzó á atemorizarse, y á angustiarse", "comenzó a sentir temor y profunda angustia", "archaic-distress-phrase", "La frase conserva el temor y la intensa angustia de Jesús."),
    item(14, 34, "esperad aquí", "quedaos aquí", "archaic-stay-verb", "Jesús pide a los tres discípulos permanecer y velar."),
    item(14, 36, "este vaso", "esta copa", "historical-cup-metaphor", "Vaso designa la copa como imagen del sufrimiento que Jesús enfrentará."),
    item(14, 36, "todas las cosas son á ti posibles; traspasa de mí", "todo te es posible; aparta de mí", "archaic-prayer-clause", "La petición conserva que todo es posible para el Padre y que Jesús pide que aparte de él la copa."),
    item(14, 36, "sino lo que tú", "sino lo que tú quieres", "archaic-elliptical-clause", "La forma actual hace explícito el verbo ya implícito en la entrega de Jesús a la voluntad del Padre."),
    item(14, 38, "el espíritu á la verdad es presto", "el espíritu está dispuesto", "archaic-readiness-phrase", "Presto significa dispuesto en el contraste entre espíritu y carne."),
    item(14, 38, "mas la carne enferma", "pero la carne es débil", "false-friend-weakness-term", "Enferma expresa debilidad humana, no una enfermedad concreta."),
    item(14, 43, "una compañía con espadas y palos", "una multitud con espadas y palos", "false-friend-crowd-term", "Compañía designa aquí el grupo numeroso enviado a arrestar a Jesús."),
    item(14, 43, "príncipes de los sacerdotes", "principales sacerdotes", "historical-priestly-role", "La multitud fue enviada por el grupo dirigente de los sacerdotes."),
    item(14, 44, "dado señal común", "dado una señal acordada", "false-friend-agreed-signal", "Judas había acordado previamente la señal del beso."),
    item(14, 48, "Como á ladrón", "Cómo contra un bandido", "historical-robber-term", "El término describe a un bandido violento al que se arrestaría con armas; la pregunta conserva la tilde interrogativa."),
    item(14, 55, "todo el concilio", "todo el Consejo", "historical-council-term", "La frase identifica al consejo religioso reunido para buscar testimonio."),
    item(14, 56, "sus testimonios no concertaban", "sus testimonios no coincidían", "archaic-agreement-verb", "Los falsos testimonios no concordaban entre sí."),
    item(14, 58, "que es hecho de mano", "hecho por manos humanas", "archaic-human-made-phrase", "La acusación contrasta un templo construido por manos humanas con otro no construido de ese modo."),
    item(14, 58, "otro echo sin mano", "otro no hecho por manos humanas", "spelling-and-agreement", "Echo era una errata por hecho; la frase conserva el contraste con el templo construido por manos humanas."),
    item(14, 62, "á la diestra de la potencia de Dios", "a la derecha del poder de Dios", "archaic-power-phrase", "Diestra significa derecha y potencia significa poder en la declaración de Jesús."),
    item(14, 64, "le condenaron ser culpado de muerte", "lo condenaron como merecedor de muerte", "archaic-condemnation-phrase", "El consejo lo declara merecedor de la pena de muerte."),
    item(14, 66, "atrio", "patio", "historical-courtyard-term", "Pedro estaba en el patio de la residencia del sumo sacerdote."),
    item(14, 70, "tu habla es semejante", "tu manera de hablar lo confirma", "false-friend-accent-phrase", "La manera de hablar de Pedro revelaba su origen galileo."),

    item(15, 7, "habían hecho muerte en una revuelta", "habían cometido asesinato durante una revuelta", "archaic-murder-phrase", "Barrabás estaba preso con quienes habían cometido asesinato en una revuelta."),
    item(15, 13, "dar voces", "gritar", "archaic-cry-phrase", "La multitud volvió a gritar que lo crucificaran."),
    item(15, 16, "es á saber, al Pretorio", "es decir, al Pretorio", "archaic-explanation-phrase", "Es a saber introduce la explicación del lugar."),
    item(15, 16, "convocan", "reunieron a", "grammar-narrative-tense", "La narración continúa en pasado: los soldados reunieron a toda la compañía dentro del Pretorio."),
    item(15, 19, "le adoraban hincadas las rodillas", "se arrodillaban ante él en burla", "context-reviewed-mocking-gesture", "Los soldados se arrodillan en una parodia cruel de homenaje, no como adoración sincera."),
    item(15, 20, "le hubieron escarnecido", "se hubieron burlado de él", "archaic-mockery-verb", "Escarnecer significa burlarse cruelmente de Jesús."),
    item(15, 20, "le desnudaron la púrpura", "le quitaron el manto púrpura", "historical-purple-garment", "Los soldados quitaron a Jesús el manto púrpura usado para burlarse de él."),
    item(15, 22, "que declarado quiere decir", "que traducido significa", "archaic-translation-phrase", "El evangelista explica el significado del nombre Gólgota."),
    item(15, 29, "le denostaban", "lo insultaban", "archaic-abuse-verb", "Denostar significa insultar con desprecio."),
    item(15, 31, "escarneciendo", "burlándose de él", "archaic-mockery-verb", "Los principales sacerdotes se burlaban de Jesús."),
    item(15, 32, "le denostaban", "lo insultaban", "archaic-abuse-verb", "Quienes estaban crucificados con Jesús también lo insultaban."),
    item(15, 37, "espiró", "murió", "archaic-death-verb", "Espiró expresa que Jesús murió después de dar un gran grito."),
    item(15, 43, "senador noble", "miembro respetado del Consejo", "historical-council-role", "José era un miembro respetado del consejo que esperaba el reino de Dios."),
    item(15, 43, "osadamente entró á Pilato", "se presentó con valentía ante Pilato", "archaic-boldness-phrase", "José se presentó valientemente ante Pilato para pedir el cuerpo."),
    item(15, 46, "sepulcro que estaba cavado en una peña", "sepulcro excavado en una roca", "archaic-rock-tomb", "El sepulcro había sido excavado en la roca."),
    item(15, 46, "revolvió una piedra", "hizo rodar una piedra", "false-friend-roll-verb", "José hizo rodar una piedra hasta la entrada del sepulcro."),

    item(16, 1, "drogas aromáticas", "especias aromáticas", "historical-burial-spices", "Las mujeres compraron especias aromáticas para ungir el cuerpo."),
    item(16, 3, "revolverá la piedra", "hará rodar la piedra", "false-friend-roll-verb", "La pregunta es quién hará rodar la piedra de la entrada."),
    item(16, 4, "Y como miraron, ven la piedra revuelta; que era muy grande.", "Y al mirar, vieron que la piedra había sido removida, aunque era muy grande.", "false-friend-removed-stone", "Al mirar, las mujeres vieron que la piedra ya había sido apartada; la frase completa mantiene el tiempo narrativo en pasado y la observación sobre su tamaño."),
    item(16, 5, "una larga ropa blanca", "una larga túnica blanca", "historical-garment-term", "El joven estaba vestido con una larga túnica blanca."),
    item(16, 6, "resucitado há", "ha resucitado", "grammar-resurrection-phrase", "La forma actual conserva la declaración de que Jesús resucitó."),
    item(16, 13, "lo hicieron saber", "se lo comunicaron", "archaic-report-phrase", "Los dos comunicaron a los demás lo que habían visto."),
    item(16, 14, "censuróles su incredulidad", "los reprendió por su incredulidad", "archaic-rebuke-enclitic", "Jesús reprendió a los once por su incredulidad y dureza de corazón."),
    item(16, 15, "toda criatura", "toda persona", "context-reviewed-human-audience", "El mandato envía a predicar el evangelio a todas las personas del mundo."),
    item(16, 18, "cosa mortífera", "algo mortal", "archaic-deadly-phrase", "La frase se refiere a beber algo capaz de causar la muerte."),
    item(16, 18, "Quitarán serpientes", "Tomarán serpientes en sus manos", "false-friend-take-up-verb", "Quitar significa aquí tomar o levantar serpientes; la forma actual evita entender que simplemente las apartarán."),
    item(16, 19, "á la diestra de Dios", "a la derecha de Dios", "archaic-direction-term", "Diestra significa el lado derecho en la exaltación del Señor."),
]


PENDING = [
    ("mark-v23-1", "remisión de pecados", [(1, 4)], "Es una fórmula teológica conocida; aunque perdón aclara el sentido, se reserva para mantener coherencia doctrinal con todo el Nuevo Testamento."),
    ("mark-v23-2", "Cananita / cananista", [(3, 18)], "El sobrenombre de Simón se relaciona con celo y no con procedencia cananea; requiere una política uniforme de nombres apostólicos."),
    ("mark-v23-3", "pecado eterno / juicio eterno", [(3, 29)], "Las tradiciones textuales y traducciones difieren en la formulación; no se resuelve mediante modernización léxica."),
    ("mark-v23-4", "para que no se conviertan", [(4, 12)], "La cita de Isaías tiene opciones interpretativas sobre propósito y resultado; debe permanecer intacta sin una nota enfocada."),
    ("mark-v23-5", "quería precederlos", [(6, 48)], "La acción de pasar de largo puede tener función narrativa y teofánica; una paráfrasis podría borrar ese matiz."),
    ("mark-v23-6", "lavado ritual de manos", [(7, 3), (7, 4)], "La tradición manuscrita y el sentido de la expresión de lavado exigen una nota histórica, no una sustitución rápida."),
    ("mark-v23-7", "lista de males interiores", [(7, 21), (7, 22)], "Varios términos griegos admiten matices distintos; deben revisarse individualmente antes de modernizar toda la lista."),
    ("mark-v23-8", "Si puedes creer", [(9, 23)], "La lectura recibida y otras tradiciones puntúan o formulan la respuesta de manera distinta; se conserva el texto base."),
    ("mark-v23-9", "oración y ayuno", [(9, 29)], "Ayuno pertenece a una variante textual tradicional; la revisión de claridad no debe decidir crítica textual."),
    ("mark-v23-10", "gusano, fuego y sal", [(9, 44), (9, 46), (9, 48), (9, 49)], "La imagen y los versículos tradicionales requieren tratamiento textual y exegético conjunto."),
    ("mark-v23-11", "copa y bautismo de sufrimiento", [(10, 38), (10, 39)], "Las metáforas están explicadas por el contexto pero no deben convertirse en una paráfrasis que elimine su forma bíblica."),
    ("mark-v23-12", "abominación desoladora", [(13, 14)], "Es un término profético con referencia intertextual a Daniel y variantes textuales; se conserva para una revisión enfocada."),
    ("mark-v23-13", "nuevo pacto / nuevo testamento", [(14, 24)], "Pacto y testamento implican una decisión terminológica que debe mantenerse coherente en toda la Biblia."),
    ("mark-v23-14", "final largo de Marcos", [(16, v) for v in range(9, 21)], "Marcos 16:9-20 pertenece a la tradición textual recibida. Se conserva su inclusión completa y no se decide su autenticidad; las aclaraciones léxicas internas no añaden ni eliminan cláusulas."),
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value, compact=False):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2, separators=(",", ":") if compact else None) + "\n", encoding="utf-8")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    source_doc = read(BOOK)
    source = {(c["chapter"], v["verse"]): v["text"] for c in source_doc["chapters"] for v in c["verses"]}
    direction = read(DIRECTION)
    patches = {(v["chapter"], v["verse"]): v for v in direction.get("verses", [])}
    applied = []
    replaced = []
    seen = set()
    for change in CHANGES:
        key = (change["chapter"], change["verse"], change["expected"], change["replacement"])
        if key in seen:
            raise RuntimeError(f"duplicate change {key}")
        seen.add(key)
        ref = (change["chapter"], change["verse"])
        text = source[ref]
        if change["expected"] not in text:
            raise RuntimeError(f"missing {change['expected']!r} at MRK.{ref[0]}.{ref[1]}")
        patch = patches.get(ref)
        if patch is None:
            patch = {"chapter": ref[0], "verse": ref[1], "sourceTextSha256": sha(text), "edits": []}
            direction["verses"].append(patch)
            patches[ref] = patch
        cursor = 0
        while True:
            start = text.find(change["expected"], cursor)
            if start < 0:
                break
            end = start + len(change["expected"])
            cursor = end
            exact = next((e for e in patch["edits"] if e["startOffset"] == start and e["endOffset"] == end), None)
            if exact:
                if exact["replacement"] == change["replacement"]:
                    continue
                if exact["replacement"] != change.get("previousReplacement"):
                    raise RuntimeError(f"unapproved replacement collision at MRK.{ref[0]}.{ref[1]}: {exact}")
                exact.update({k: change[k] for k in ("replacement", "category", "reason", "evidence")})
                replaced.append(change)
                continue
            overlaps = [e for e in patch["edits"] if e["startOffset"] < end and start < e["endOffset"]]
            if overlaps:
                raise RuntimeError(f"overlap at MRK.{ref[0]}.{ref[1]} for {change['expected']!r}: {overlaps}")
            patch["edits"].append({
                "startOffset": start, "endOffset": end,
                "expected": change["expected"], "replacement": change["replacement"],
                "category": change["category"], "reason": change["reason"], "evidence": change["evidence"],
            })
            applied.append(change)
    for patch in direction["verses"]:
        text = source[(patch["chapter"], patch["verse"])]
        patch["sourceTextSha256"] = sha(text)
        patch["edits"].sort(key=lambda e: e["startOffset"])
        prior_end = -1
        for edit in patch["edits"]:
            if edit["startOffset"] < prior_end or text[edit["startOffset"]:edit["endOffset"]] != edit["expected"]:
                raise RuntimeError(f"invalid edit at MRK.{patch['chapter']}.{patch['verse']}: {edit}")
            prior_end = edit["endOffset"]
    direction["verses"].sort(key=lambda v: (v["chapter"], v["verse"]))
    direction["editorialStatus"] = "approved-mark-complete-context-review-v23"
    direction["ownerReview"] = {"contentVersion": VERSION, "changeSet": "editorial-changes/v23.json", "review": "Marcos completo, versículo por versículo", "requiredFullTest": True}
    write(DIRECTION, direction, compact=True)

    payload = {
        "format": "shine-reading-2026-editorial-change-set", "schemaVersion": 1,
        "contentVersion": VERSION, "generatedAt": "2026-09-12T18:30:00.000Z",
        "issuedAt": "2026-09-12T18:30:00.000Z", "expiresAt": "2028-09-12T18:30:00.000Z",
        "sourceVersionId": "RV1909", "filterId": "RV1909-LECTURA-2026",
        "changes": [{k: v for k, v in change.items() if k != "previousReplacement"} for change in applied + replaced],
    }
    write(CHANGE_SET, payload)

    package_source = read(PACKAGE_SOURCE)
    package_source["contentVersion"] = VERSION
    package_source["generatedAt"] = "2026-09-12T18:30:00.000Z"
    package_source["editorialPolicy"]["version"] = VERSION
    write(PACKAGE_SOURCE, package_source)

    registry = read(REGISTRY)
    registry["updatedAt"] = "2026-09-12T18:30:00.000Z"
    registry["activeChangeSet"] = "editorial-changes/v23.json"
    registry["pending"] = [p for p in registry.get("pending", []) if not p.get("id", "").startswith("mark-v23-")]
    for pending_id, term, refs, reason in PENDING:
        registry["pending"].append({
            "id": pending_id, "status": "pending-review", "scope": "new-testament", "term": term,
            "proposedOptions": ["conservar con nota", "modernizar después de revisión textual y contextual"],
            "reason": reason,
            "references": [{"book": "MRK", "chapter": c, "verse": v} for c, v in refs],
            "evidence": [{"label": "Control contextual de Marcos", "url": "https://www.biblegateway.com/passage/?search=Marcos&version=RVR1960%3BNVI%3BLBLA%3BRVC"}],
        })
    write(REGISTRY, registry)
    print(json.dumps({"added": len(applied), "replacedPrior": len(replaced), "changedVerses": len(direction["verses"]), "editCount": sum(len(v["edits"]) for v in direction["verses"]), "pending": len(PENDING)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
