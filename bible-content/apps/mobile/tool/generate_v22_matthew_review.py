import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK = ROOT / "apps/mobile/assets/bibles/rv1909/books/MAT.json"
DIRECTION = ROOT / "apps/mobile/assets/bible_direction/matthew_reading_2026.rv1909.v1.json"
CHANGE_SET = ROOT / "editorial-changes/v22.json"
REGISTRY = ROOT / "editorial-review/registry.json"
VERSION = 22


def item(chapter, verse, expected, replacement, category, reason, previous=None):
    value = {
        "book": "MAT", "chapter": chapter, "verse": verse,
        "expected": expected, "replacement": replacement,
        "category": category, "reason": reason,
        "evidence": [
            {"label": "Control contextual RVR1960", "url": f"https://www.biblegateway.com/passage/?search=Mateo+{chapter}%3A{verse}&version=RVR1960"},
            {"label": "Control contextual NVI", "url": f"https://www.biblegateway.com/passage/?search=Mateo+{chapter}%3A{verse}&version=NVI"},
        ],
    }
    if previous is not None:
        value["previousReplacement"] = previous
    return value


# Every entry was reviewed in its complete verse. The list deliberately avoids
# broad pronoun conversion and doctrinal terms whose best rendering depends on
# interpretation rather than lexical clarity.
CHANGES = [
    item(1, 1, "generación", "genealogía", "context-reviewed-genealogy", "Aquí generación presenta la lista familiar de Jesús; genealogía expresa el referente sin cambiar la línea de descendencia."),
    item(1, 18, "se halló haber concebido", "se halló que había concebido", "grammar-comprehension", "La construcción actual aclara el mismo descubrimiento y conserva el tiempo verbal."),
    item(1, 20, "le aparece en sueños", "se le apareció en sueños", "grammar-narrative-tense", "El relato está en pasado; la forma corregida mantiene sujeto, aparición y sueño."),
    item(1, 21, "parirá un hijo", "dará a luz un hijo", "clear-birth-phrase", "Dar a luz es el equivalente actual de parir en este anuncio y evita un verbo hoy percibido como brusco."),
    item(1, 23, "que declarado, es: Con nosotros Dios", "que traducido significa: Dios con nosotros", "clear-translation-phrase", "El evangelista explica el significado del nombre Emmanuel; la frase moderna conserva exactamente esa explicación."),
    item(2, 1, "fué nacido Jesús", "nació Jesús", "grammar-birth-phrase", "La forma activa actual expresa el mismo nacimiento sin la construcción pasiva antigua."),
    item(2, 6, "guiador", "gobernante", "context-reviewed-ruler", "La cita habla del que gobernará y pastoreará a Israel; gobernante conserva esa función."),
    item(2, 7, "entendió de ellos diligentemente el tiempo del aparecimiento", "averiguó cuidadosamente cuándo había aparecido", "context-reviewed-inquiry-phrase", "Herodes obtiene de los magos el momento de aparición de la estrella; la redacción aclara la investigación sin añadir información."),
    item(2, 13, "Y partidos ellos", "Y después que ellos partieron", "grammar-departure-phrase", "La frase indica que los magos ya se habían marchado antes del sueño de José."),
    item(2, 16, "en todos sus términos", "en todos sus alrededores", "false-friend-region", "Términos designa aquí los alrededores de Belén, no palabras o condiciones."),
    item(2, 22, "amonestado por revelación", "advertido por revelación", "archaic-warning-verb", "Amonestado significa que recibió una advertencia divina en el sueño."),
    item(3, 3, "Aparejad", "Preparad", "archaic-prepare-verb", "Aparejar el camino significa prepararlo; el imperativo conserva la cita profética."),
    item(3, 4, "una cinta de cuero alrededor de sus lomos", "un cinturón de cuero alrededor de su cintura", "clear-clothing-phrase", "La descripción corresponde a un cinturón alrededor de la cintura; se conserva la vestimenta de Juan."),
    item(3, 9, "despertar hijos á Abraham", "levantar hijos a Abraham", "false-friend-raise-verb", "Despertar no significa sacar del sueño aquí; significa hacer surgir descendientes para Abraham."),
    item(3, 11, "los zapatos del cual", "cuyas sandalias", "historical-footwear", "El calzado descrito son sandalias; la forma posesiva actual elimina una construcción forzada."),
    item(3, 12, "Su aventador en su mano está, y aventará su era", "Su pala está en su mano, y limpiará el lugar de la trilla", "context-reviewed-winnowing-phrase", "La imagen es la limpieza del grano en la era con una pala para aventar; se aclaran ambos objetos sin perder la metáfora."),
    item(3, 12, "allegará", "recogerá", "archaic-gather-verb", "Allegar el trigo significa recogerlo en el granero."),
    item(3, 17, "en el cual tengo contentamiento", "en quien tengo mi agrado", "archaic-approval-phrase", "Contentamiento expresa aquí el agrado del Padre por el Hijo."),
    item(4, 3, "llegándose á él", "acercándose a él", "archaic-approach-verb", "Llegarse a alguien significa acercarse."),
    item(4, 5, "le pasa á la santa ciudad, y le pone", "lo llevó a la santa ciudad y lo puso", "grammar-narrative-tense", "La narración requiere pasado y conserva los dos movimientos atribuidos al diablo."),
    item(4, 8, "le pasa el diablo á un monte muy alto, y le muestra", "el diablo lo llevó a un monte muy alto y le mostró", "grammar-narrative-tense", "La redacción actual mantiene la secuencia narrativa en pasado."),
    item(4, 9, "si postrado me adorares", "si te postras y me adoras", "archaic-worship-phrase", "La condición se expresa en español actual sin alterar la exigencia de postrarse y adorar."),
    item(4, 12, "Juan era preso", "Juan había sido encarcelado", "clear-imprisonment-phrase", "Preso describe aquí el encarcelamiento de Juan, no una captura en curso."),
    item(4, 13, "ciudad marítima", "ciudad junto al mar", "false-friend-location", "Capernaum estaba junto al lago; la frase evita que marítima sugiera una costa oceánica."),
    item(4, 16, "luz les esclareció", "una luz les resplandeció", "archaic-light-phrase", "Esclarecer funciona aquí como resplandecer sobre quienes estaban en sombra."),
    item(4, 24, "todos los que tenían mal: los tomados de diversas enfermedades y tormentos", "todos los enfermos: los que sufrían diversas enfermedades y dolores", "context-reviewed-illness-phrase", "La frase enumera personas enfermas y afligidas; se elimina una construcción hoy opaca sin borrar sus padecimientos."),
    item(5, 6, "serán hartos", "serán satisfechos", "archaic-satisfaction-verb", "Hartos significa plenamente satisfechos en la bienaventuranza."),
    item(5, 11, "os vituperaren", "os insulten", "archaic-hostility-verb", "Vituperar significa insultar o hablar mal de alguien; se conserva el objeto plural."),
    item(5, 13, "si la sal se desvaneciere", "si la sal pierde su sabor", "context-reviewed-salt-idiom", "Desvanecerse describe aquí que la sal deja de saber a sal, no que desaparece."),
    item(5, 13, "hollada", "pisoteada", "archaic-trampling-verb", "Hollar significa pisotear en este contexto literal."),
    item(5, 17, "he venido para abrogar la ley", "he venido para abolir la ley", "archaic-law-verb", "Abrogar una ley significa abolirla."),
    item(5, 17, "he venido para abrogar, sino", "he venido para abolir, sino", "archaic-law-verb", "Abrogar una ley significa abolirla."),
    item(5, 22, "concejo", "concilio", "historical-council-term", "La referencia es al tribunal o concilio, no al gobierno municipal moderno."),
    item(5, 22, "Fatuo", "Insensato", "archaic-insult-term", "Fatuo es el insulto insensato o necio en la progresión del versículo."),
    item(5, 23, "presente", "ofrenda", "false-friend-offering", "Presente designa la ofrenda llevada al altar."),
    item(5, 24, "Deja allí tu presente", "Deja allí tu ofrenda", "false-friend-offering", "Presente designa la ofrenda dejada delante del altar."),
    item(5, 24, "ofrece tu presente", "ofrece tu ofrenda", "false-friend-offering", "Presente designa la ofrenda que se presenta después de la reconciliación."),
    item(5, 24, "vuelve primero en amistad con tu hermano", "reconcíliate primero con tu hermano", "clear-reconciliation-phrase", "Volver en amistad significa reconciliarse antes de presentar la ofrenda."),
    item(5, 25, "presto", "pronto", "archaic-speed-adverb", "Presto significa pronto mientras aún se va de camino al juez."),
    item(5, 25, "alguacil", "guardia", "historical-custody-term", "El funcionario recibe al condenado para llevarlo a prisión; guardia comunica esa función."),
    item(5, 26, "último cuadrante", "última moneda", "historical-coin-term", "Cuadrante era una moneda de muy poco valor; última moneda conserva la idea de pago completo."),
    item(5, 33, "No te perjurarás", "No jurarás falsamente", "archaic-oath-verb", "Perjurarse significa jurar en falso."),
    item(5, 33, "pagarás al Señor tus juramentos", "cumplirás al Señor tus juramentos", "false-friend-oath-verb", "Pagar un juramento significa cumplir lo prometido, no entregar dinero."),
    item(5, 39, "mejilla diestra", "mejilla derecha", "archaic-direction-term", "Diestra significa derecha en esta referencia corporal."),
    item(5, 43, "aborrecerás", "odiarás", "archaic-hostility-verb", "Aborrecer significa odiar en el contraste con amar."),
    item(5, 44, "ultrajan", "maltratan", "archaic-hostility-verb", "Ultrajar significa maltratar u ofender gravemente."),
    item(5, 47, "si abrazareis á vuestros hermanos solamente", "si saludáis solamente a vuestros hermanos", "context-reviewed-greeting-verb", "El verbo describe saludar a los hermanos, no necesariamente abrazarlos físicamente."),
    item(6, 2, "no hagas tocar trompeta", "no toques trompeta", "grammar-publicity-phrase", "La advertencia prohíbe anunciar públicamente la limosna; la forma actual conserva la imagen."),
    item(6, 2, "ser estimados de los hombres", "ser elogiados por los hombres", "false-friend-praise-verb", "Estimados significa aquí recibir elogio público, no solamente aprecio."),
    item(6, 6, "éntrate en tu cámara", "entra en tu habitación", "archaic-private-room-phrase", "Cámara designa aquí una habitación privada para orar."),
    item(6, 7, "no seáis prolijos", "no uséis repeticiones sin sentido", "context-reviewed-prayer-phrase", "Prolijos describe la repetición abundante y vacía que el versículo condena."),
    item(6, 16, "hipócritas, austeros", "hipócritas, sombríos", "false-friend-appearance-term", "Austeros describe aquí una apariencia triste o sombría, no disciplina económica."),
    item(6, 16, "demudan sus rostros", "desfiguran sus rostros", "archaic-appearance-verb", "Demudar el rostro significa alterar su apariencia para que otros noten el ayuno."),
    item(6, 19, "orín", "óxido", "archaic-corrosion-term", "Orín significa óxido en la imagen de bienes que se deterioran."),
    item(6, 19, "ladrones minan y hurtan", "ladrones entran a robar", "false-friend-burglary-phrase", "Minar una casa significa abrirse paso para entrar; hurtar significa robar."),
    item(6, 20, "orín", "óxido", "archaic-corrosion-term", "Orín significa óxido en la imagen de bienes que no se deterioran en el cielo."),
    item(6, 20, "ladrones no minan ni hurtan", "ladrones no entran a robar", "false-friend-burglary-phrase", "La frase describe ladrones que fuerzan la entrada para robar."),
    item(6, 23, "la lumbre", "la luz", "archaic-light-term", "Lumbre significa luz en el contraste con las tinieblas interiores."),
    item(6, 24, "Mammón", "las riquezas", "historical-wealth-term", "Mammón personifica el dinero o las riquezas; el contraste es servir a Dios o a las riquezas."),
    item(6, 25, "No os congojéis", "No os preocupéis", "archaic-worry-verb", "Congoja expresa la preocupación por comida, bebida y vestido."),
    item(6, 27, "congojándose", "preocupándose", "archaic-worry-verb", "La pregunta enseña que preocuparse no puede alargar la vida o estatura."),
    item(6, 28, "Reparad los lirios", "Observad los lirios", "false-friend-observe-verb", "Reparar significa aquí observar con atención, no arreglar."),
    item(6, 31, "con qué nos cubriremos", "con qué nos vestiremos", "clear-clothing-phrase", "Cubrirse significa vestirse en la lista de necesidades diarias."),
    item(6, 34, "no os congojéis", "no os preocupéis", "archaic-worry-verb", "Congoja expresa preocupación por el día siguiente."),
    item(7, 3, "no echas de ver", "no notas", "archaic-notice-phrase", "Echar de ver significa notar o advertir."),
    item(7, 5, "mirarás en echar", "podrás sacar", "archaic-removal-phrase", "Después de quitar la viga, la persona podrá sacar la mota del ojo ajeno."),
    item(7, 16, "abrojos", "cardos", "historical-plant-term", "Abrojos designa plantas espinosas; cardos conserva el contraste agrícola."),
    item(7, 23, "les protestaré", "les declararé", "false-friend-declaration-verb", "Protestar significa aquí declarar solemnemente, no presentar una queja."),
    item(7, 24, "peña", "roca", "archaic-rock-term", "Peña significa roca en la base firme de la casa."),
    item(7, 25, "combatieron aquella casa", "golpearon aquella casa", "archaic-impact-verb", "La lluvia, los ríos y los vientos golpean la casa; no libran combate contra ella."),
    item(7, 27, "hicieron ímpetu en aquella casa", "golpearon aquella casa", "archaic-impact-phrase", "Hacer ímpetu significa arremeter o golpear con fuerza."),
    item(7, 28, "su doctrina", "su enseñanza", "false-friend-teaching-term", "Doctrina designa aquí la enseñanza que la gente acaba de oír."),
    item(8, 4, "el presente", "la ofrenda", "false-friend-offering", "El presente ordenado por Moisés es una ofrenda sacerdotal; el tramo completo conserva la concordancia femenina."),
    item(8, 9, "hombre bajo de potestad", "hombre bajo autoridad", "archaic-authority-phrase", "Potestad significa autoridad en la cadena militar del centurión."),
    item(8, 9, "bajo de mí soldados", "soldados bajo mi mando", "grammar-command-phrase", "La frase aclara que los soldados obedecen al centurión."),
    item(8, 10, "he hallado fe tanta", "he hallado tanta fe", "grammar-word-order", "El orden actual conserva el énfasis de Jesús en la magnitud de la fe."),
    item(8, 20, "cavernas", "guaridas", "historical-animal-shelter", "Las zorras tienen guaridas, no cavernas en el sentido monumental actual."),
    item(8, 21, "dame licencia", "permíteme", "archaic-permission-phrase", "Dar licencia significa permitir que el discípulo vaya primero."),
    item(8, 24, "un gran movimiento", "una gran tormenta", "false-friend-storm-phrase", "El movimiento del mar es una tormenta que cubre la barca con olas."),
    item(8, 25, "llegándose sus discípulos", "acercándose sus discípulos", "archaic-approach-verb", "Llegarse a Jesús significa acercarse a él."),
    item(8, 26, "teméis", "tienen miedo", "context-reviewed-fear-phrase", "La expresión actual aclara la pregunta de Jesús y evita la anterior corrección aislada que dejó temen sin complemento.", "temen"),
    item(8, 29, "molestarnos", "atormentarnos", "false-friend-torment-verb", "Los demonios preguntan por el tormento antes del tiempo señalado, no por una molestia menor."),
    item(8, 30, "hato", "manada", "archaic-herd-term", "Hato significa una manada de animales."),
    item(8, 30, "puercos", "cerdos", "historical-animal-term", "Puercos significa cerdos."),
    item(8, 31, "hato", "manada", "archaic-herd-term", "Hato significa la manada de cerdos."),
    item(8, 31, "puercos", "cerdos", "historical-animal-term", "Puercos significa cerdos."),
    item(8, 32, "á aquel hato de puercos", "a aquella manada de cerdos", "archaic-herd-term", "Hato de puercos significa una manada de cerdos."),
    item(8, 32, "todo el hato de los puercos", "toda la manada de los cerdos", "archaic-herd-term", "La frase designa la manada completa de cerdos."),
    item(8, 33, "porqueros", "cuidadores de los cerdos", "archaic-occupation-term", "Porqueros son quienes cuidaban la manada de cerdos."),
    item(8, 34, "sus términos", "su región", "false-friend-region", "Términos designa aquí el territorio de la ciudad."),
    item(9, 6, "potestad", "autoridad", "archaic-authority-term", "Potestad significa la autoridad del Hijo del hombre para perdonar pecados."),
    item(9, 8, "potestad", "autoridad", "archaic-authority-term", "La multitud glorifica a Dios por haber dado tal autoridad."),
    item(9, 9, "banco de los públicos tributos", "mesa de recaudación de impuestos", "historical-tax-phrase", "La frase identifica el puesto donde Mateo cobraba impuestos."),
    item(9, 16, "paño recio", "paño nuevo", "false-friend-cloth-term", "La comparación usa tela nueva que encoge sobre un vestido viejo; recio ya no comunica esa propiedad."),
    item(9, 18, "un principal", "un dirigente", "historical-leader-term", "Principal designa a un dirigente local que acude a Jesús."),
    item(9, 18, "es muerta poco ha", "acaba de morir", "archaic-recent-death-phrase", "Poco ha significa hace poco; la frase mantiene la noticia de la muerte reciente."),
    item(9, 20, "flujo de sangre", "hemorragia", "historical-medical-term", "Flujo de sangre describe una hemorragia prolongada."),
    item(9, 23, "tañedores de flautas", "flautistas", "archaic-musician-term", "Tañedores de flautas son los músicos funerarios que tocaban ese instrumento."),
    item(9, 30, "encargó rigurosamente", "advirtió firmemente", "archaic-warning-phrase", "Jesús les da una advertencia firme para que nadie lo sepa."),
    item(9, 35, "achaque", "dolencia", "archaic-illness-term", "Achaque significa dolencia o enfermedad, sin el matiz moderno de excusa."),
    item(9, 36, "derramadas y esparcidas", "desamparadas y dispersas", "context-reviewed-sheep-phrase", "La gente aparece afligida y dispersa como ovejas sin pastor; desamparadas conserva su vulnerabilidad."),
    item(9, 37, "mies", "cosecha", "archaic-harvest-term", "Mies significa la cosecha en la comparación de Jesús."),
    item(9, 38, "Señor de la mies", "Señor de la cosecha", "archaic-harvest-term", "Mies significa la cosecha cuyo Señor envía obreros."),
    item(9, 38, "á su mies", "a su cosecha", "archaic-harvest-term", "Mies significa la cosecha a la que se envían obreros."),
    item(10, 2, "que es dicho Pedro", "que es llamado Pedro", "archaic-name-phrase", "La frase explica el nombre por el que se conoce a Simón."),
    item(10, 9, "No aprestéis", "No llevéis", "archaic-provision-verb", "Aprestar significa proveerse; la instrucción prohíbe llevar dinero para el camino."),
    item(10, 10, "alforja", "bolsa", "historical-travel-bag", "Alforja es la bolsa usada para provisiones durante el viaje."),
    item(10, 10, "bordón", "bastón", "archaic-staff-term", "Bordón significa bastón de viaje."),
    item(10, 17, "concilios", "tribunales", "historical-judicial-term", "Los concilios son tribunales locales ante los que serían entregados."),
    item(10, 19, "no os apuréis", "no os preocupéis", "false-friend-worry-verb", "Apurarse significa aquí preocuparse por lo que deberán decir."),
    item(10, 29, "un cuarto", "una moneda pequeña", "historical-coin-term", "Cuarto es una moneda de poco valor en la comparación de los pajarillos."),
    item(10, 34, "que he venido para meter paz", "que he venido para traer paz", "archaic-bring-verb", "Meter paz significa traerla; se conserva el contraste con la espada."),
    item(10, 34, "no he venido para meter paz", "no he venido para traer paz", "archaic-bring-verb", "Meter paz significa traerla; se conserva el contraste con la espada."),
    item(10, 35, "hacer disensión del hombre contra su padre", "poner al hombre contra su padre", "archaic-conflict-phrase", "Hacer disensión significa provocar oposición dentro de la familia."),
    item(11, 1, "mandamientos", "instrucciones", "false-friend-instruction-term", "Aquí son las instrucciones dadas a los doce, no una referencia técnica a los mandamientos de la Ley."),
    item(11, 6, "no fuere escandalizado en mí", "no tropiece por causa de mí", "context-reviewed-stumbling-phrase", "Escandalizarse significa tropezar o apartarse por causa de Jesús, no sentir simple ofensa."),
    item(11, 7, "meneada del viento", "sacudida por el viento", "archaic-motion-verb", "Menearse describe la caña sacudida por el viento."),
    item(11, 10, "delante de tu faz, que aparejará tu camino delante de ti", "delante de ti, que preparará tu camino", "archaic-preparation-phrase", "Faz y aparejar oscurecen una frase sencilla sobre el mensajero que prepara el camino."),
    item(11, 11, "el que es muy más pequeño", "el más pequeño", "grammar-comparison", "Muy más pequeño es una construcción antigua; el superlativo actual conserva la comparación."),
    item(11, 17, "Os tañimos flauta", "Tocamos la flauta para vosotros", "archaic-musical-verb", "Tañer significa tocar un instrumento."),
    item(11, 17, "os endechamos", "cantamos canciones de duelo para vosotros", "archaic-mourning-verb", "Endechar significa cantar lamentaciones o canciones de duelo."),
    item(11, 20, "reconvenir", "reprender", "archaic-rebuke-verb", "Reconvenir significa reprender a las ciudades por no arrepentirse."),
    item(11, 20, "muy muchas de sus maravillas", "muchas de sus maravillas", "grammar-redundancy", "Muy muchas es una intensificación antigua innecesaria; muchas mantiene el sentido."),
    item(11, 21, "en saco y en ceniza", "con ropa de luto y ceniza", "historical-mourning-phrase", "Saco designa la ropa áspera usada como señal de duelo y arrepentimiento."),
    item(11, 26, "agradó en tus ojos", "te agradó", "archaic-approval-phrase", "La expresión significa que así agradó al Padre."),
    item(11, 28, "estáis trabajados y cargados", "estáis cansados y cargados", "false-friend-burden-phrase", "Trabajados significa fatigados o cansados, no personas con empleo."),
    item(12, 4, "panes de la proposición", "panes consagrados", "historical-sacred-bread", "La frase designa el pan consagrado colocado ante Dios."),
    item(12, 10, "una mano seca", "una mano atrofiada", "historical-medical-phrase", "Seca describe una mano incapacitada o atrofiada, no falta de humedad."),
    item(12, 16, "encargaba eficazmente", "ordenaba estrictamente", "archaic-command-phrase", "Jesús les ordena con firmeza que no revelen su identidad."),
    item(12, 20, "pábilo", "mecha", "archaic-lamp-term", "Pábilo es la mecha que humea."),
    item(12, 29, "prendiere al valiente", "ate al hombre fuerte", "context-reviewed-strong-man-phrase", "La parábola describe atar primero al hombre fuerte antes de saquear su casa."),
    item(12, 33, "árbol corrompido, y su fruto dañado", "árbol malo y su fruto malo", "false-friend-tree-phrase", "Corrompido y dañado significan malos en el contraste entre árbol y fruto."),
    item(12, 39, "adulterina", "adúltera", "archaic-moral-term", "Adulterina significa adúltera en la acusación dirigida a la generación."),
    item(12, 40, "vientre de la ballena", "vientre del gran pez", "context-reviewed-sea-creature", "El término griego señala una gran criatura marina; gran pez conserva la referencia a Jonás sin identificar una especie."),
    item(12, 41, "he aquí más que Jonás en este lugar", "aquí hay alguien más grande que Jonás", "grammar-comparison-phrase", "La frase compara a Jesús con Jonás; se explicita el sujeto ya presente en el contexto."),
    item(12, 42, "he aquí más que Salomón en este lugar", "aquí hay alguien más grande que Salomón", "grammar-comparison-phrase", "La frase compara a Jesús con Salomón; se explicita el sujeto ya presente en el contexto."),
    item(13, 2, "se allegaron á él", "se reunieron alrededor de él", "archaic-gather-verb", "Allegarse significa reunirse o acercarse a Jesús."),
    item(13, 4, "simiente", "semilla", "archaic-seed-term", "Simiente significa semilla en la parábola del sembrador."),
    item(13, 15, "está engrosado", "se ha vuelto insensible", "context-reviewed-insensitivity-phrase", "Engrosado describe un corazón insensible o endurecido, no un aumento físico."),
    item(13, 15, "de los oídos oyen pesadamente", "oyen con dificultad", "archaic-hearing-phrase", "La expresión indica dificultad o resistencia para oír."),
    item(13, 15, "de sus ojos guiñan", "han cerrado sus ojos", "false-friend-eye-phrase", "Guiñar no describe un gesto breve; la cita señala que han cerrado los ojos para no ver."),
    item(13, 15, "no vean de los ojos, y oigan de los oídos, y del corazón entiendan", "no vean con los ojos, ni oigan con los oídos, ni entiendan con el corazón", "grammar-parallel-phrase", "La redacción restaura el paralelismo negativo de ver, oír y entender."),
    item(13, 21, "antes es temporal", "sino que dura poco", "false-friend-duration-phrase", "Temporal significa que la respuesta dura poco, no que pertenece al tiempo o al clima."),
    item(13, 21, "luego se ofende", "enseguida tropieza", "context-reviewed-stumbling-phrase", "Ofenderse significa aquí tropezar o abandonar ante la aflicción."),
    item(13, 24, "simiente", "semilla", "archaic-seed-term", "Simiente significa semilla en la parábola de la cizaña."),
    item(13, 27, "simiente", "semilla", "archaic-seed-term", "Simiente significa semilla en la pregunta de los siervos."),
    item(13, 28, "la cojamos", "la arranquemos", "false-friend-weeding-verb", "Los siervos preguntan si deben arrancar la cizaña."),
    item(13, 33, "quedó leudo", "quedó fermentado", "archaic-fermentation-term", "Leudo significa fermentado por la levadura."),
    item(13, 35, "rebosaré cosas escondidas", "declararé cosas escondidas", "false-friend-utterance-verb", "Rebosar significa aquí pronunciar o declarar lo oculto, no derramar líquido."),
    item(13, 37, "simiente", "semilla", "archaic-seed-term", "Simiente significa semilla en la explicación de la parábola."),
    item(13, 38, "simiente", "semilla", "archaic-seed-term", "Simiente significa semilla en la explicación de la parábola."),
    item(13, 41, "todos los escándalos", "todas las causas de tropiezo", "context-reviewed-stumbling-term", "Escándalos designa aquello que hace caer o pecar, no noticias públicas."),
    item(13, 52, "escriba docto", "escriba instruido", "false-friend-learned-term", "Docto significa instruido o preparado en el reino."),
    item(14, 2, "por eso virtudes obran en él", "por eso actúan en él poderes milagrosos", "false-friend-miraculous-power", "Virtudes designa poderes milagrosos, no cualidades morales."),
    item(14, 12, "dieron las nuevas", "dieron la noticia", "archaic-news-phrase", "Dar las nuevas significa comunicar la noticia de la muerte de Juan."),
    item(14, 13, "descierto", "desierto", "spelling-comprehension", "Se corrige la errata del lugar desierto."),
    item(14, 25, "cuarta vela", "cuarta vigilia", "historical-night-watch", "Vela designa la cuarta guardia nocturna, no una candela."),
    item(14, 31, "trabó de él", "lo sujetó", "archaic-grasp-phrase", "Trabar de Pedro significa sujetarlo cuando comenzaba a hundirse."),
    item(15, 2, "traspasan la tradición", "quebrantan la tradición", "false-friend-violate-verb", "Traspasar significa quebrantar la tradición, no cruzarla físicamente."),
    item(15, 3, "traspasáis el mandamiento", "quebrantáis el mandamiento", "false-friend-violate-verb", "Traspasar significa quebrantar o desobedecer el mandamiento."),
    item(15, 4, "muera de muerte", "sea condenado a muerte", "archaic-death-phrase", "La fórmula significa recibir la pena de muerte."),
    item(15, 19, "muertes", "homicidios", "context-reviewed-murder-term", "La lista habla de homicidios que proceden del corazón, no de muertes naturales."),
    item(15, 20, "manos por lavar", "manos sin lavar", "archaic-unwashed-phrase", "Por lavar significa que las manos no han sido lavadas."),
    item(15, 22, "malamente atormentada del demonio", "cruelmente atormentada por un demonio", "grammar-torment-phrase", "La frase conserva la gravedad del tormento y expresa su agente en español actual."),
    item(15, 33, "que hartemos á tan gran compañía", "para alimentar a tanta gente", "archaic-feed-phrase", "Hartar significa alimentar hasta quedar satisfechos; compañía designa aquí la multitud."),
    item(16, 2, "el cielo tiene arreboles", "el cielo está rojizo", "archaic-sky-term", "Arreboles describe el color rojizo del cielo al atardecer."),
    item(16, 3, "tiene arreboles el cielo triste", "el cielo está rojizo y sombrío", "archaic-sky-term", "La señal matutina es un cielo rojizo y sombrío que anuncia tormenta."),
    item(16, 3, "la faz del cielo", "el aspecto del cielo", "archaic-appearance-term", "Faz significa aspecto en la observación del cielo."),
    item(16, 23, "me eres escándalo", "me eres tropiezo", "context-reviewed-stumbling-term", "Escándalo significa aquí obstáculo o tropiezo para Jesús."),
    item(16, 26, "granjeare todo el mundo", "ganara todo el mundo", "archaic-gain-verb", "Granjear significa ganar o adquirir."),
    item(16, 27, "pagará á cada uno", "recompensará a cada uno", "false-friend-recompense-verb", "Pagar expresa aquí dar a cada persona conforme a sus obras."),
    item(16, 28, "no gustarán la muerte", "no morirán", "archaic-death-idiom", "Gustar la muerte es un modismo que significa morir."),
    item(17, 4, "pabellones", "refugios", "historical-shelter-term", "Pabellones designa refugios o enramadas para Jesús, Moisés y Elías."),
    item(17, 5, "tomo contentamiento", "tengo mi agrado", "archaic-approval-phrase", "Contentamiento expresa el agrado del Padre por el Hijo."),
    item(17, 11, "restituirá", "restaurará", "archaic-restore-verb", "Restituir todas las cosas significa restaurarlas."),
    item(17, 14, "hincándosele de rodillas", "arrodillándose ante él", "archaic-kneeling-phrase", "Hincarse de rodillas significa arrodillarse ante Jesús."),
    item(17, 15, "que es lunático, y padece malamente", "que sufre convulsiones y padece mucho", "context-reviewed-seizure-phrase", "El versículo describe ataques que lo arrojan al fuego y al agua; la frase actual comunica los síntomas sin atribuirlos a la luna."),
    item(17, 17, "generación infiel y torcida", "generación incrédula y perversa", "false-friend-unbelief-phrase", "Infiel significa incrédula y torcida describe su perversidad, no una forma física."),
    item(17, 18, "mozo", "muchacho", "context-reviewed-young-person", "Mozo designa al muchacho que fue sanado."),
    item(17, 21, "este linaje", "esta clase", "false-friend-kind-term", "Linaje designa esta clase de demonio, no una genealogía."),
    item(17, 27, "no los escandalicemos", "no los ofendamos", "context-reviewed-offense-verb", "Aquí escandalizar significa causar una objeción u ofensa por el tributo."),
    item(17, 27, "un estatero", "una moneda", "historical-coin-term", "Estatero era la moneda hallada en la boca del pez; moneda permite seguir la acción sin exigir conocimiento numismático."),
    item(18, 6, "una piedra de molino de asno", "una gran piedra de molino", "historical-millstone-term", "La frase describe una piedra grande movida por un asno."),
    item(18, 7, "por los escándalos", "por las causas de tropiezo", "context-reviewed-stumbling-term", "Escándalos designa aquello que induce a caer o pecar."),
    item(18, 7, "vengan escándalos", "vengan causas de tropiezo", "context-reviewed-stumbling-term", "La frase conserva la inevitabilidad de las ocasiones de caer."),
    item(18, 7, "viene el escándalo", "viene la causa de tropiezo", "context-reviewed-stumbling-term", "La advertencia recae sobre quien ocasiona la caída."),
    item(18, 15, "redargúyele", "corrígelo", "archaic-correction-verb", "Redargüir significa señalar y corregir la falta del hermano en privado."),
    item(18, 17, "étnico", "gentil", "historical-outsider-term", "Étnico designa a quien está fuera de la comunidad del pacto; gentil es el término bíblico conocido."),
    item(18, 19, "se convinieren", "se ponen de acuerdo", "archaic-agreement-verb", "Convenirse significa ponerse de acuerdo sobre lo que se pide."),
    item(18, 22, "mas", "sino", "grammar-correlation", "La respuesta contrapone no siete, sino hasta setenta veces siete.", "pero"),
    item(18, 28, "consiervos", "compañeros de servicio", "archaic-fellow-servant-term", "Consiervos son siervos que sirven al mismo señor."),
    item(18, 28, "trabando de él, le ahogaba", "agarrándolo, lo estrangulaba", "archaic-assault-phrase", "La acción consiste en agarrar al compañero por el cuello y estrangularlo."),
    item(18, 31, "consiervos", "compañeros de servicio", "archaic-fellow-servant-term", "Consiervos son siervos del mismo señor."),
    item(19, 4, "macho y hembra", "hombre y mujer", "context-reviewed-human-sex-phrase", "La cita habla de la creación humana como hombre y mujer; se evita una expresión hoy asociada principalmente con animales."),
    item(19, 13, "les riñeron", "los reprendieron", "archaic-rebuke-verb", "Los discípulos reprendieron a quienes llevaban los niños."),
    item(19, 17, "es á saber", "es decir", "archaic-explanation-phrase", "Es a saber introduce la explicación de que el único bueno es Dios."),
    item(19, 21, "da lo á los pobres", "dalo a los pobres", "grammar-clitic-spacing", "El pronombre unido al imperativo forma dalo."),
    item(19, 24, "más liviano trabajo es", "es más fácil", "false-friend-ease-phrase", "Liviano trabajo significa que algo resulta más fácil."),
    item(20, 1, "un hombre, padre de familia", "un propietario", "historical-landowner-term", "El personaje es el propietario que contrata trabajadores para su viña."),
    item(20, 1, "ajustar obreros", "contratar trabajadores", "archaic-hiring-phrase", "Ajustar obreros significa contratarlos y acordar su jornal."),
    item(20, 2, "habiéndose concertado", "habiendo acordado", "archaic-agreement-verb", "Concertarse significa llegar a un acuerdo de pago."),
    item(20, 7, "nos ha ajustado", "nos ha contratado", "archaic-hiring-verb", "Ajustar a alguien significa contratarlo para trabajar."),
    item(20, 8, "mayordomo", "encargado", "historical-manager-term", "El mayordomo es el encargado de pagar a los trabajadores."),
    item(20, 8, "jornal", "salario", "historical-wage-term", "Jornal es el salario correspondiente al día trabajado."),
    item(20, 13, "no te hago agravio", "no cometo injusticia contigo", "archaic-wrong-phrase", "Hacer agravio significa tratar injustamente."),
    item(20, 19, "le escarnezcan", "se burlen de él", "archaic-mockery-verb", "Escarnecer significa burlarse cruelmente de alguien."),
    item(20, 22, "beber el vaso", "beber la copa", "historical-cup-metaphor", "Vaso designa la copa como imagen del sufrimiento que Jesús enfrentará."),
    item(20, 23, "mi vaso beberéis", "mi copa beberéis", "historical-cup-metaphor", "Vaso designa la copa compartida como imagen del sufrimiento."),
    item(20, 23, "dar lo", "darlo", "grammar-clitic-spacing", "El pronombre debe unirse al infinitivo."),
    item(20, 25, "se enseñorean sobre ellos", "los dominan", "archaic-domination-verb", "Enseñorearse significa ejercer dominio sobre otros."),
    item(20, 25, "ejercen sobre ellos potestad", "ejercen autoridad sobre ellos", "archaic-authority-term", "Potestad significa autoridad en el gobierno de las naciones."),
    item(20, 29, "gran compañía", "una gran multitud", "false-friend-crowd-term", "Compañía designa aquí una multitud que sigue a Jesús."),
    item(21, 1, "monte de las Olivas", "monte de los Olivos", "historical-place-name", "El nombre actual del lugar es monte de los Olivos."),
    item(21, 5, "animal de yugo", "bestia de carga", "historical-pack-animal", "La expresión identifica al animal usado para llevar carga."),
    item(21, 12, "cambiadores", "cambistas", "historical-moneychanger-term", "Los cambiadores eran cambistas que intercambiaban monedas en el templo."),
    item(21, 12, "trastornó las mesas", "volcó las mesas", "false-friend-overturn-verb", "Trastornar significa aquí volcar físicamente las mesas."),
    item(21, 16, "los que maman", "los niños de pecho", "archaic-nursing-phrase", "La cita se refiere a bebés o niños que todavía maman."),
    item(21, 17, "posó allí", "pasó allí la noche", "false-friend-lodging-verb", "Posar significa hospedarse o pasar la noche en Betania."),
    item(21, 24, "os preguntaré una palabra", "os haré una pregunta", "false-friend-question-phrase", "Palabra designa aquí una pregunta que Jesús plantea a sus interlocutores."),
    item(21, 31, "rameras", "prostitutas", "archaic-person-term", "Rameras es el término antiguo para prostitutas."),
    item(21, 32, "rameras", "prostitutas", "archaic-person-term", "Rameras es el término antiguo para prostitutas."),
    item(21, 33, "cercó de vallado", "rodeó con una cerca", "archaic-fence-phrase", "Vallado es una cerca que rodea la viña."),
    item(21, 33, "un lagar", "una prensa para uvas", "historical-winepress-term", "Lagar es la instalación donde se exprimen las uvas."),
    item(21, 33, "la dió á renta", "la arrendó", "archaic-lease-phrase", "Dar a renta significa arrendar la viña a labradores."),
    item(21, 38, "heredad", "herencia", "archaic-inheritance-term", "Heredad designa la herencia que los labradores quieren tomar."),
    item(21, 42, "cabeza de esquina", "piedra angular", "historical-building-term", "Cabeza de esquina es la piedra angular principal de la cita."),
    item(21, 44, "le desmenuzará", "lo aplastará", "archaic-crushing-verb", "Desmenuzar describe el efecto de la piedra que cae sobre alguien."),
    item(22, 2, "un hombre rey, que hizo bodas á su hijo", "un rey que celebró la boda de su hijo", "archaic-wedding-phrase", "La parábola comienza con un rey que prepara la boda de su hijo."),
    item(22, 3, "los llamados á las bodas", "los invitados a la boda", "false-friend-invitation-phrase", "Los llamados son quienes ya habían sido invitados."),
    item(22, 4, "mi comida he aparejado", "he preparado mi comida", "archaic-prepare-verb", "Aparejar significa preparar el banquete."),
    item(22, 4, "todo está prevenido", "todo está listo", "false-friend-ready-term", "Prevenido significa preparado o listo en este contexto."),
    item(22, 5, "no se cuidaron", "no hicieron caso", "false-friend-disregard-phrase", "No cuidarse significa desatender la invitación, no falta de autocuidado."),
    item(22, 6, "los afrentaron", "los maltrataron", "archaic-abuse-verb", "Afrentar significa tratar de manera vergonzosa y violenta a los siervos."),
    item(22, 7, "homicidas", "asesinos", "historical-murderer-term", "Homicidas designa a quienes asesinaron a los siervos."),
    item(22, 8, "están aparejadas", "están preparadas", "archaic-prepare-verb", "Aparejadas significa preparadas para la celebración."),
    item(22, 9, "salidas de los caminos", "cruces de los caminos", "historical-road-junction", "La orden envía a los siervos a los cruces o puntos de salida de los caminos."),
    item(22, 10, "convidados", "invitados", "archaic-guest-term", "Convidados son los invitados reunidos para la boda."),
    item(22, 11, "convidados", "invitados", "archaic-guest-term", "Convidados son las personas invitadas a la boda."),
    item(22, 12, "cerró la boca", "se quedó sin palabras", "archaic-speechless-phrase", "La persona no pudo responder a la pregunta del rey."),
    item(22, 16, "eres amador de la verdad", "eres sincero", "archaic-sincerity-phrase", "La adulación presenta a Jesús como alguien sincero que enseña con verdad."),
    item(22, 16, "no te curas de nadie", "no te dejas influir por nadie", "false-friend-impartiality-phrase", "No curarse de nadie significa no dejarse influir por posición o presión humana."),
    item(22, 16, "no tienes acepción de persona de hombres", "no muestras favoritismo", "archaic-impartiality-phrase", "Hacer acepción de personas significa mostrar favoritismo."),
    item(22, 20, "¿Cúya es esta figura, y lo que está encima escrito?", "¿De quién son esta imagen y esta inscripción?", "archaic-coin-question", "La pregunta distingue la imagen y la inscripción grabadas en la moneda."),
    item(22, 34, "había cerrado la boca á los Saduceos", "había hecho callar a los Saduceos", "archaic-silencing-phrase", "Cerrar la boca significa haberlos dejado sin respuesta."),
    item(22, 35, "intérprete de la ley", "experto en la ley", "historical-law-expert", "El personaje es un experto en la ley que pone a prueba a Jesús."),
    item(22, 44, "á mi diestra", "a mi derecha", "archaic-direction-term", "Diestra significa el lado derecho en la cita del salmo."),
    item(22, 46, "osó", "se atrevió", "archaic-dare-verb", "Osar significa atreverse a hacer otra pregunta."),
    item(23, 7, "salutaciones", "saludos", "archaic-greeting-term", "Salutaciones significa saludos públicos en las plazas."),
    item(23, 12, "se ensalzare", "se exalte", "archaic-exalt-verb", "Ensalzarse significa exaltarse a sí mismo."),
    item(23, 14, "coméis las casas de las viudas", "se apoderan de las casas de las viudas", "context-reviewed-exploitation-phrase", "Comer las casas es una imagen de explotar a las viudas y apoderarse de sus bienes."),
    item(23, 15, "prosélito", "convertido", "historical-convert-term", "Prosélito designa a una persona convertida al grupo religioso."),
    item(23, 16, "deudor es", "queda obligado", "archaic-oath-obligation", "Ser deudor significa quedar obligado por el juramento."),
    item(23, 18, "deudor es", "queda obligado", "archaic-oath-obligation", "Ser deudor significa quedar obligado por el juramento."),
    item(23, 23, "el juicio y la misericordia y la fe", "la justicia, la misericordia y la fe", "false-friend-justice-term", "Juicio designa aquí la justicia como deber central de la ley."),
    item(24, 3, "monte de las Olivas", "monte de los Olivos", "historical-place-name", "El nombre actual del lugar es monte de los Olivos."),
    item(24, 19, "las preñadas", "las embarazadas", "archaic-pregnancy-term", "Preñadas significa mujeres embarazadas."),
    item(24, 22, "ninguna carne sería salva", "nadie sobreviviría", "context-reviewed-survival-phrase", "Carne representa aquí a los seres humanos y el contexto habla de sobrevivir aquellos días."),
    item(24, 26, "en las cámaras", "en lugares ocultos", "false-friend-hidden-place", "Cámaras designa habitaciones interiores u ocultas donde falsamente dirían que está Cristo."),
    item(24, 32, "su rama se enternece", "sus ramas se ponen tiernas", "archaic-budding-phrase", "La rama tierna y las hojas que brotan anuncian la cercanía del verano."),
    item(24, 41, "á un molinillo", "en un molino", "historical-milling-term", "Las mujeres trabajan moliendo en un molino, no con el aparato doméstico moderno llamado molinillo."),
    item(24, 43, "á cuál vela el ladrón había de venir", "a qué hora vendría el ladrón", "historical-night-watch", "Vela designa la hora o guardia nocturna en que llegaría el ladrón."),
    item(24, 43, "minar su casa", "entrar a robar en su casa", "false-friend-burglary-phrase", "Minar la casa significa abrirse paso para entrar a robar."),
    item(24, 49, "consiervos", "compañeros de servicio", "archaic-fellow-servant-term", "Consiervos son quienes sirven al mismo señor."),
    item(25, 7, "aderezaron sus lámparas", "prepararon sus lámparas", "archaic-prepare-verb", "Aderezar significa preparar las lámparas para recibir al esposo."),
    item(25, 10, "apercibidas", "preparadas", "false-friend-ready-term", "Apercibidas significa que estaban preparadas para la llegada del esposo."),
    item(25, 15, "conforme á su facultad", "conforme a su capacidad", "false-friend-ability-term", "Facultad significa capacidad para administrar lo recibido."),
    item(25, 16, "granjeó", "negoció", "archaic-trade-verb", "Granjear con el dinero significa negociarlo para obtener ganancia."),
    item(25, 27, "con usura", "con intereses", "false-friend-interest-term", "Usura designa aquí el interés producido por el depósito, sin el sentido moderno exclusivo de interés abusivo."),
    item(25, 35, "me recogisteis", "me hospedasteis", "archaic-hospitality-verb", "Recoger al forastero significa hospedarlo."),
    item(25, 38, "te recogimos", "te hospedamos", "archaic-hospitality-verb", "Recoger al forastero significa ofrecerle hospedaje."),
    item(25, 43, "no me recogisteis", "no me hospedasteis", "archaic-hospitality-verb", "Recoger al forastero significa hospedarlo."),
    item(25, 46, "tormento eterno", "castigo eterno", "context-reviewed-judgment-term", "El término expresa castigo en contraste con vida eterna; ambos controles españoles coinciden."),
    item(26, 7, "vaso de alabastro de ungüento de gran precio", "frasco de alabastro con perfume muy costoso", "historical-perfume-container", "La mujer trae un frasco de alabastro con perfume costoso para ungir a Jesús."),
    item(26, 17, "aderecemos", "preparemos", "archaic-prepare-verb", "Aderezar la Pascua significa prepararla."),
    item(26, 19, "aderezaron", "prepararon", "archaic-prepare-verb", "Los discípulos prepararon la Pascua como Jesús indicó."),
    item(26, 27, "tomando el vaso", "tomando la copa", "historical-cup-term", "Vaso designa la copa compartida durante la cena."),
    item(26, 28, "remisión de los pecados", "perdón de los pecados", "doctrinally-controlled-forgiveness-term", "Remisión significa perdón de los pecados; se conserva intacta la relación con la sangre del pacto."),
    item(26, 29, "cuando lo tengo de beber nuevo", "cuando lo beba de nuevo", "archaic-future-phrase", "Tener de beber significa beber en el futuro."),
    item(26, 31, "seréis escandalizados en mí", "me abandonaréis", "context-reviewed-desertion-phrase", "El contexto inmediato explica que las ovejas se dispersarán y los discípulos huirán."),
    item(26, 33, "Aunque todos sean escandalizados en ti, yo nunca seré escandalizado", "Aunque todos te abandonen, yo nunca te abandonaré", "context-reviewed-desertion-phrase", "Pedro afirma que no abandonará a Jesús aunque los demás lo hagan."),
    item(26, 36, "la aldea que se llama Gethsemaní", "el lugar llamado Getsemaní", "historical-place-description", "Getsemaní se presenta como un lugar al que llegan, no como una aldea."),
    item(26, 39, "pase de mí este vaso", "pase de mí esta copa", "historical-cup-metaphor", "La copa es la imagen del sufrimiento que Jesús pide que pase de él."),
    item(26, 42, "este vaso", "esta copa", "historical-cup-metaphor", "La copa mantiene la misma imagen del sufrimiento en la segunda oración."),
    item(26, 41, "el espíritu á la verdad está presto", "el espíritu está dispuesto", "false-friend-readiness-term", "Presto significa dispuesto en el contraste con la debilidad de la carne."),
    item(26, 43, "los ojos de ellos estaban agravados", "tenían los ojos pesados de sueño", "archaic-sleep-phrase", "Agravados describe el peso del sueño sobre los ojos de los discípulos."),
    item(26, 65, "Blasfemado ha", "Ha blasfemado", "grammar-word-order", "El orden actual conserva la acusación del sumo sacerdote."),
    item(26, 67, "mojicones", "puñetazos", "archaic-violence-term", "Mojicones significa golpes dados con el puño."),
    item(26, 74, "hacer imprecaciones", "maldecir", "archaic-curse-phrase", "Hacer imprecaciones significa pronunciar maldiciones mientras negaba conocer a Jesús."),
    item(27, 4, "¿Qué se nos da á nosotros? Viéras lo tú.", "¿Qué nos importa a nosotros? Allá tú.", "archaic-dismissal-phrase", "Los sacerdotes rechazan la responsabilidad y dejan el asunto en manos de Judas."),
    item(27, 24, "veréis lo vosotros", "allá vosotros", "archaic-responsibility-phrase", "Pilato intenta trasladar al pueblo la responsabilidad por la muerte de Jesús."),
    item(27, 27, "pretorio", "palacio del gobernador", "historical-government-building", "El pretorio es la residencia o sede del gobernador donde reunieron a los soldados."),
    item(27, 28, "manto de grana", "manto escarlata", "archaic-color-term", "Grana describe el color escarlata del manto."),
    item(27, 29, "hincando la rodilla", "arrodillándose", "archaic-kneeling-phrase", "Hincar la rodilla significa arrodillarse ante Jesús en burla."),
    item(27, 31, "le hubieron escarnecido", "se hubieron burlado de él", "archaic-mockery-verb", "Escarnecer significa burlarse cruelmente."),
    item(27, 34, "gustando", "después de probarlo", "archaic-taste-phrase", "Gustar significa probar la bebida antes de rechazarla."),
    item(27, 37, "su causa escrita", "la acusación escrita contra él", "historical-charge-term", "Causa designa el cargo o acusación colocado sobre la cruz."),
    item(27, 39, "le decían injurias", "lo insultaban", "archaic-abuse-phrase", "Decir injurias significa insultar a Jesús."),
    item(27, 41, "escarneciendo", "burlándose de él", "archaic-mockery-verb", "Escarnecer significa burlarse cruelmente de Jesús."),
    item(27, 48, "la hinchió de vinagre", "la empapó en vinagre", "false-friend-soak-verb", "La esponja fue empapada en vinagre, no inflada."),
    item(27, 50, "dió el espíritu", "entregó el espíritu", "context-reviewed-death-phrase", "La frase describe la muerte de Jesús como entrega del espíritu."),
    item(27, 51, "las piedras se hendieron", "las rocas se partieron", "archaic-splitting-verb", "Hender significa partir o abrir las rocas."),
    item(27, 60, "había labrado en la peña", "había excavado en la roca", "archaic-rock-cut-tomb", "El sepulcro había sido excavado en la roca."),
    item(27, 60, "revuelta una grande piedra", "después de hacer rodar una gran piedra", "archaic-rolling-phrase", "José hizo rodar una piedra grande hasta la entrada del sepulcro."),
    item(28, 1, "Y LA víspera de sábado, que amanece para el primer día de la semana", "Y PASADO el sábado, al amanecer del primer día de la semana", "context-reviewed-resurrection-time", "La frase sitúa la visita después del sábado, al amanecer del primer día de la semana."),
    item(28, 2, "había revuelto la piedra", "había hecho rodar la piedra", "archaic-rolling-phrase", "El ángel había movido la piedra haciéndola rodar."),
    item(28, 7, "id presto", "id pronto", "archaic-speed-adverb", "Presto significa pronto en la orden del ángel."),
    item(28, 19, "doctrinad á todos los Gentiles", "haced discípulos de todas las naciones", "context-reviewed-great-commission", "El mandato es hacer discípulos entre todas las naciones; doctrinar ya no comunica plenamente esa acción."),
    # Follow-up findings from rendering the entire revised book, including
    # corrections that were missed or made awkward by earlier review rounds.
    item(4, 24, "lunáticos", "los que sufrían convulsiones", "context-reviewed-seizure-term", "Lunáticos es un término histórico ligado a la luna; el contexto describe personas que sufrían convulsiones."),
    item(5, 15, "debajo de un almud", "debajo de un recipiente", "context-reviewed-container-phrase", "Almud es un recipiente de medida; recipiente conserva la imagen sin sustituirla por el cajón introducido en una revisión anterior.", "debajo de un cajón"),
    item(5, 31, "repudiare á su mujer", "se divorcie de su mujer", "archaic-divorce-phrase", "Repudiar a la esposa significa divorciarse de ella en esta enseñanza."),
    item(5, 32, "repudiare á su mujer", "se divorcie de su mujer", "archaic-divorce-phrase", "Repudiar a la esposa significa divorciarse de ella."),
    item(5, 32, "repudiada", "divorciada", "archaic-divorce-term", "Repudiada significa divorciada en la conclusión del versículo."),
    item(6, 26, "allegan", "recogen", "archaic-gather-verb", "Allegar significa recoger o almacenar la cosecha."),
    item(6, 28, "por qué os congojáis", "por qué os preocupáis", "archaic-worry-verb", "Congoja expresa preocupación por el vestido."),
    item(6, 31, "No os congojéis pues", "No os preocupéis pues", "archaic-worry-verb", "Congoja expresa preocupación por las necesidades diarias."),
    item(7, 6, "puercos", "cerdos", "historical-animal-term", "Puercos significa cerdos en la imagen de las perlas."),
    item(7, 25, "peña", "roca", "archaic-rock-term", "Peña significa roca en el fundamento de la casa."),
    item(16, 4, "adulterina", "adúltera", "archaic-moral-term", "Adulterina significa adúltera en la acusación dirigida a la generación."),
    item(19, 3, "repudiar á su mujer", "divorciarse de su mujer", "archaic-divorce-phrase", "Repudiar a la esposa significa divorciarse de ella."),
    item(19, 7, "repudiarla", "divorciarse de ella", "archaic-divorce-phrase", "Repudiarla significa divorciarse de ella."),
    item(19, 8, "repudiar á vuestras mujeres", "divorciaros de vuestras mujeres", "archaic-divorce-phrase", "Repudiar a las esposas significa divorciarse de ellas; se conserva la persona plural del discurso."),
    item(19, 9, "repudiare á su mujer", "se divorcie de su mujer", "archaic-divorce-phrase", "Repudiar a la esposa significa divorciarse de ella."),
    item(19, 9, "repudiada", "divorciada", "archaic-divorce-term", "Repudiada significa divorciada."),
    item(20, 23, "está aparejado de mi Padre", "está preparado por mi Padre", "archaic-prepare-phrase", "Aparejado significa preparado, y la preposición actual aclara al agente de la preparación."),
    item(5, 5, "recibirán la tierra por heredad", "heredarán la tierra", "archaic-inheritance-phrase", "Recibir por heredad significa heredar; la promesa conserva el mismo objeto."),
    item(10, 1, "les dió potestad", "les dio autoridad", "archaic-authority-phrase", "Potestad significa autoridad sobre los espíritus inmundos y las enfermedades."),
    item(23, 18, "el presente que está sobre él", "la ofrenda que está sobre él", "false-friend-offering", "Presente designa la ofrenda colocada sobre el altar; el tramo completo mantiene el género."),
    item(23, 19, "el presente, ó el altar que santifica al presente", "la ofrenda, o el altar que santifica la ofrenda", "false-friend-offering", "Las dos apariciones de presente designan la misma ofrenda; se conserva el contraste con el altar."),
    item(25, 34, "heredad el reino", "hereden el reino", "archaic-inheritance-command", "Heredad es el imperativo plural antiguo de heredar; la forma actual conserva la orden."),
    item(28, 18, "Toda potestad me es dada", "Toda autoridad me ha sido dada", "archaic-authority-phrase", "Potestad significa autoridad; la forma actual conserva que esa autoridad fue dada a Jesús."),
]


PENDING = [
    ("conocer", ["no tuvo relaciones con ella", "conservar con nota"], "Mateo 1:25 usa conocer como eufemismo marital; debe preservarse el alcance exacto de hasta que.", [(1, 25)]),
    ("Raca", ["conservar con nota", "insulto"], "Mateo 5:22 translitera un insulto arameo; sustituirlo borraría la progresión retórica si no se explica.", [(5, 22)]),
    ("fornicación", ["inmoralidad sexual", "relación sexual ilícita", "conservar"], "Mateo 5:32 y 19:9 son textos doctrinalmente sensibles; porneia requiere una decisión editorial explícita.", [(5, 32), (19, 9)]),
    ("ojo bueno", ["ojo sano", "ojo generoso", "conservar imagen"], "Mateo 6:22-23 puede expresar salud visual y también generosidad; no se debe escoger un solo matiz automáticamente.", [(6, 22), (6, 23)]),
    ("reino se hace fuerza", ["avanza con fuerza", "sufre violencia", "conservar con nota"], "Mateo 11:12 admite lecturas activas y pasivas; la modernización exige decisión exegética.", [(11, 12)]),
    ("infiernos", ["Hades", "lugar de los muertos", "conservar"], "Mateo 11:23 y 16:18 usan Hades, mientras otros pasajes usan Gehenna; no deben colapsarse.", [(11, 23), (16, 18)]),
    ("blasfemia contra el Espíritu", ["conservar íntegro"], "Mateo 12:31-32 es doctrinal; solo necesita claridad circundante, no paráfrasis automática.", [(12, 31), (12, 32)]),
    ("iniquidad", ["maldad", "desobediencia a la ley", "conservar"], "Mateo alterna maldad general y práctica contraria a la ley; cada referencia requiere análisis.", [(13, 41), (23, 28)]),
    ("atar y desatar", ["conservar con nota", "prohibir y permitir"], "Mateo 16:19 y 18:18 contienen una fórmula jurídica y eclesial cuya paráfrasis puede estrechar el sentido.", [(16, 19), (18, 18)]),
    ("regeneración", ["renovación de todas las cosas", "nuevo mundo", "conservar"], "Mateo 19:28 usa palingenesia en un contexto escatológico, no solo de conversión individual.", [(19, 28)]),
    ("cuerpo y águilas", ["cadáver y buitres", "conservar imagen"], "Mateo 24:28 contiene vocabulario e imagen discutidos; una especie moderna no debe imponerse sin decisión editorial.", [(24, 28)]),
    ("cortar por medio", ["castigar severamente", "cortar en dos", "conservar"], "Mateo 24:51 tiene una imagen de juicio fuerte; suavizarla o literalizarla cambia el efecto.", [(24, 51)]),
    ("verdugos", ["carceleros", "torturadores", "conservar"], "Mateo 18:34 usa un término que puede referirse a carceleros que aplican tormento; una sola equivalencia puede perder el matiz.", [(18, 34)]),
    ("texto tradicional añadido", ["conservar por política textual", "marcar variante"], "Mateo 17:21, 18:11 y cláusulas de 20:22-23 pertenecen a la tradición textual recibida; no se alteran en una revisión léxica.", [(17, 21), (18, 11), (20, 22), (20, 23)]),
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    book = read(BOOK)
    source = {(c["chapter"], v["verse"]): v["text"] for c in book["chapters"] for v in c["verses"]}
    direction = read(DIRECTION)
    # v1 modernized cantones without its article and produced "los esquinas".
    # Expand that reviewed span so the visible phrase has grammatical agreement.
    verse_6_5 = next(v for v in direction["verses"] if (v["chapter"], v["verse"]) == (6, 5))
    corner = next(e for e in verse_6_5["edits"] if e["expected"] in {"cantones", "los cantones"})
    if corner["expected"] == "cantones":
        assert source[(6, 5)][corner["startOffset"] - 4:corner["endOffset"]] == "los cantones"
        corner["startOffset"] -= 4
    corner.update({
        "expected": "los cantones", "replacement": "las esquinas",
        "category": "grammar-gender-agreement",
        "reason": "La corrección anterior cambió cantones por esquinas sin incluir el artículo; el tramo completo restaura la concordancia femenina.",
    })
    # v22 originally changed only the noun presente and rendered "el ofrenda".
    # Expand the existing edit to include the article before re-emitting v22.
    verse_8_4 = next(v for v in direction["verses"] if (v["chapter"], v["verse"]) == (8, 4))
    offering = next(e for e in verse_8_4["edits"] if e["expected"] in {"presente", "el presente"})
    if offering["expected"] == "presente":
        assert source[(8, 4)][offering["startOffset"] - 3:offering["endOffset"]] == "el presente"
        offering["startOffset"] -= 3
    offering.update({
        "expected": "el presente", "replacement": "la ofrenda",
        "category": "false-friend-offering",
        "reason": "El presente ordenado por Moisés es una ofrenda sacerdotal; el tramo completo conserva la concordancia femenina.",
    })
    DIRECTION.write_text(json.dumps(direction, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    occupied = {(v["chapter"], v["verse"]): v["edits"] for v in direction["verses"]}
    seen = set()
    for change in CHANGES:
        ref = (change["chapter"], change["verse"])
        text = source[ref]
        assert text.count(change["expected"]) == 1, (ref, change["expected"])
        start = text.index(change["expected"]); end = start + len(change["expected"])
        overlaps = [e for e in occupied.get(ref, []) if e["startOffset"] < end and start < e["endOffset"]]
        if overlaps:
            assert len(overlaps) == 1 and overlaps[0]["startOffset"] == start and overlaps[0]["endOffset"] == end, (ref, change["expected"], overlaps)
            if change.get("previousReplacement") is not None:
                assert overlaps[0]["replacement"] in {change["previousReplacement"], change["replacement"]}, (ref, change["expected"], overlaps[0]["replacement"])
            else:
                assert overlaps[0]["replacement"] == change["replacement"], (ref, change["expected"], overlaps[0]["replacement"])
        key = (*ref, start, end)
        assert key not in seen, key
        seen.add(key)

    payload = {
        "format": "shine-reading-2026-editorial-change-set", "schemaVersion": 1,
        "contentVersion": VERSION, "generatedAt": "2026-09-12T11:00:00.000Z",
        "issuedAt": "2026-09-12T11:00:00.000Z", "expiresAt": "2028-09-12T11:00:00.000Z",
        "sourceVersionId": "RV1909", "filterId": "RV1909-LECTURA-2026", "changes": CHANGES,
    }
    CHANGE_SET.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry = read(REGISTRY)
    registry["pending"] = [x for x in registry.get("pending", []) if not x.get("id", "").startswith("matthew-v22-")]
    for index, (term, options, reason, references) in enumerate(PENDING, 1):
        registry["pending"].append({
            "id": f"matthew-v22-{index}", "status": "pending-review", "scope": "new-testament",
            "term": term, "proposedOptions": options, "reason": reason,
            "references": [{"book": "MAT", "chapter": chapter, "verse": verse} for chapter, verse in references],
            "evidence": [{"label": "Revisión contextual de Mateo", "url": "https://www.biblegateway.com/passage/?search=Mateo&version=RVR1960%3BNVI"}],
        })
    registry.update({"updatedAt": "2026-09-12T11:00:00.000Z", "activeChangeSet": "editorial-changes/v22.json"})
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changes": len(CHANGES), "changedVerses": len({(x['chapter'], x['verse']) for x in CHANGES}), "pending": len(PENDING)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
