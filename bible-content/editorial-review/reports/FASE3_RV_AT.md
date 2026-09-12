# Fase 3 — RV1909 Lectura 2026, Antiguo Testamento

Base: `a57cf85` (v22) → **v23**. Nuevo Testamento sin tocar.

## Cómo se buscó

Nueve detectores sobre el **100 %** del texto proyectado del Antiguo Testamento
(7 022 ediciones, 5 315 versículos, offsets válidos 7 022/7 022, cero superposiciones),
más un décimo detector de **colapso** que hubo que añadir a mitad de fase. Los detectores
marcan candidatos; **cada uno se leyó después en el versículo completo** antes de decidir.

| Detector | Marcados | Defectos reales | Falsos positivos |
|---|---|---|---|
| R1 `é` ante consonante | 0 | — | — |
| R2 ortografía mezclada dentro del versículo | 0 | — | — |
| R3 vosotros / ustedes | 33 | 1 (más 5 hallados con un detector preciso) | 32 |
| R4 reemplazo idéntico repetido | 4 | 0 | 4 |
| R5 repetición de 4+ palabras | 51 | 0 | 51 |
| R6 palabra duplicada o espaciado roto | 0 | — | — |
| R7 desacuerdo artículo–sustantivo | 17 | 7 | 10 |
| R8 mismo término, decisión divergente | 96 | 49 | 47 (divergencia por sentido, correcta) |
| R9 familia de término a medias | 29 | 23 | 6 (sentidos distintos) |
| **R10 colapso del texto** | **2** | **2** | **0** |

Los 51 de R5 son fieles: el texto base ya repite la frase («con sus ejidos» dos veces por
versículo en Josué 21 y 1 Crónicas 6). Los 32 de R3 eran un error de mi detector, que
tomaba `díjoles → les dijo` (narración en tercera persona) por un cambio de trato.

## El hallazgo más grave

**Números 31:3 estaba destruido.** Dos reglas lo dejaban así:

> Entonces Moisés habló al pueblo, diciendo: **e** de vosotros para la guerra, **e** contra
> Madián, y harán la venganza de Jehová en Madián.

Las reglas eran `Armaos algunos → e` y `é irán → e`. El versículo había perdido el verbo y
el sentido. Ningún detector de duplicación lo veía **porque no duplica: borra**. Por eso se
añadió el detector R10 y la guarda G8. Barrido el Antiguo Testamento entero con él, en
ambas Biblias, **no hay ningún otro caso**. Las dos reglas se retiran y el texto base se
conserva.

**Génesis 49:4** perdía una cláusula: `entonces te envileciste, subiendo á mi estrado →
profanaste mi lecho` suprimía la declaración moral del versículo. Se moderniza sólo
«estrado», que RVR1960 conserva y que NVI y LBLA leen como cama o lecho.

## Ortografía — 341 formas alineadas

Contado sobre el Antiguo Testamento completo de RV1909:

| | base | | base |
|---|---|---|---|
| `á` | **14 734** | `a` | **0** |
| `fué` | 1 159 | `fue` | 0 |
| `dió` | 231 | `dio` | 0 |
| `vió` | 120 | `vio` | 0 |
| `fuí` | 35 | `fui` | 0 |
| `ó` (conjunción) | 577 | `o` | 2 |
| `é` (conjunción) | 628 | `e` | 2 |

El texto base es categórico. La capa había introducido **321 formas modernas sueltas**.
No chocaban dentro de un mismo versículo — por eso el detector por versículo daba cero —
pero dejaban la lectura cambiando de ortografía de un capítulo a otro. Se alinearon con el
texto base: 198 `á`, 47 `fué`, 72 `dió`, 18 `ó`, 4 `vió`, 3 `é`, 1 `fuí`, 1 `Á`.

## Persona — 6 versículos

Seis reemplazos pasaban de *vosotros* a tercera persona dentro de un versículo que conserva
*vosotros*. La capa no moderniza el sistema de persona de RV1909.

| Referencia | Antes | Después |
|---|---|---|
| EXO 1:16 | Cuando **asistan**… y **vean** el sexo | Cuando **asistáis**… y **veáis** el sexo |
| EXO 1:18 | que **han dejado** con vida | que **habéis dejado** con vida |
| EXO 5:5 | vosotros **los hacen** dejar | vosotros **les hacéis** dejar |
| EXO 5:21 | nos **han hecho** abominables | nos **habéis hecho** abominables |
| EXO 34:13 | **cortarán** sus imágenes de Asera | **cortaréis** sus imágenes de Asera |
| LEV 26:22 | **reduzcan su número** | **os reduzcan** en número |

En LEV 26:22 el sujeto son las bestias y el complemento sois vosotros: el texto base lee
«os apoquen». El reemplazo trasladaba el daño a un tercero.

## Concordancia — 7 roturas

El reemplazo cambiaba el género o el número y dejaba el determinante del texto base:

| Referencia | Proyección rota | Corregido |
|---|---|---|
| EXO 30:4 | **los varas** | las varas |
| JOB 34:7 | bebe **el burla** como agua | bebe la burla como agua |
| LEV 8:13 | les ajustó **los tiaras** | les ajustó las tiaras |
| NUM 3:8 | todas **las utensilios** | todos los utensilios |
| NUM 4:7 | **los jarras** para las ofrendas | las jarras para las ofrendas |
| NUM 16:46 | **el ira** ha salido | la ira ha salido |
| NUM 33:44 | en **el frontera** de Moab | en la frontera de Moab |
| 2SA 15:30 | la cuesta de **las Olivos** | la cuesta de los Olivos |

## Itinerario de Números 33 — 43 etapas

RV1909 usa el participio: «Y **partidos** de Succoth, asentaron en Etham». La capa había
conjugado sólo el primer verbo y dejaba dos verbos conjugados seguidos sin conjunción:
«Y **partieron** de Succoth, acamparon en Etham». Se amplió cada edición para incluir la
conjunción, en las 43 etapas del capítulo.

## Familias de término — 23 conversiones, 6 reservas

Veintitrés ocurrencias sueltas quedaban sin convertir mientras el resto de su familia sí lo
estaba: *agitada, allegar, aparejado, apercibidos, aprestado, aquesta, botija, empero,
entrambos, fuero, henchid, inclináronse, juntóse, llamólo, paces, pañetes, racional, saetas,
sentóse, Sittim, sobrestantes, villas, partidos*.

Seis **no** se convierten porque la palabra cubre dos sentidos distintos, y quedan
registradas: `apercibido` (advertido frente a dispuesto), `asentar` (acampar, poner,
sentarse, establecerse), `ijares` (persona frente a res del sacrificio), `quicios` (goznes
frente a espigas), `redaño` (*peder* frente a *yoteret*) y `Sittim` (topónimo frente a la
madera de acacia).

## Glosario — 60 reemplazos unificados, 47 divergencias conservadas

El detector R8 encontró 96 términos resueltos de dos o más maneras. **Cuarenta y siete de
ellos son correctos**: la palabra castellana cubre dos palabras o dos sentidos hebreos —
*campo* (machaneh o chayil), *mediodía* (Neguev o sur), *salud* (ayuda o salvación),
*término* (límite o territorio), *trabajo* (iniquidad o sufrimiento), *mancebo* (joven o
criado), *hirió* (derrotó o mató)… Esa divergencia se conserva y se registra.

Los otros 40 términos decían exactamente lo mismo de dos maneras (`prestamente` tenía
cuatro lecturas distintas; `aljaba`, tres). Se unificaron 60 reemplazos. Los enclíticos
(*díjoles, púsole, tornóse, trájole*…) **no** se unifican: el pronombre depende del sujeto
y del objeto de cada versículo.

## Reservas registradas en `registry.json`

`ot-final-2026-rv-apercibido`, `-asentaron`, `-ijares`, `-quicios`, `-sittim`,
`-encliticos` (unos 690 versículos del AT conservan la forma enclítica; es una decisión de
alcance total) y `-glosario-divergente`. Más `leviticus-v17-1` (*redaño* / *peder*),
actualizada en esta fase.

## Resultado

| | v22 | v23 |
|---|---|---|
| Ediciones en el AT | 6 984 | 7 022 |
| Ediciones en toda la Biblia | — | 9 418 |
| Reglas en el change-set | 394 | 869 |
| Reglas retiradas | 128 | 189 |
| Términos pendientes | 171 | 178 |
| `contentSha256` | — | `2e4d1355504e9f69d31aea225b6da5672876228b88b000d360f6bb88ee95eec8` |

El hash es el del paquete tras la Fase 7, que ensanchó nueve tramos para que cada
cambio identificase una sola ocurrencia. Ese ensanchamiento no altera el texto
proyectado, pero sí los bytes del paquete.

## Pruebas dirigidas

`apps/mobile/tool/verify_ot_final_2026_guards.py` pasa de 5 guardas a **10**. Las nuevas:

- **G6** ahora comprueba de verdad el corpus fuente archivo por archivo. Antes se declaraba
  la referencia y se descartaba (`del canon`): **la guarda no comprobaba nada**.
- **G7** ninguna regla puede introducir la ortografía moderna que el texto base no usa.
- **G8** ningún reemplazo puede colapsar el texto dejando sólo palabras vacías.
- **G9** el itinerario de Números 33 no puede quedar sin conjunción.
- **G10** los seis versículos de persona conservan la segunda del plural.

Se comprobó que **detectan de verdad**: reintroduciendo a propósito cada defecto, G7, G8,
G9 y G10 fallan; con el texto correcto, ninguna falla.

## Lo que esto **no** significa

Los detectores cubrieron el 100 % del texto proyectado y la lectura individual recayó sobre
lo que marcaron más los pasajes de riesgo. **Ningún libro del Antiguo Testamento tiene
todavía evidencia de lectura secuencial completa.**
