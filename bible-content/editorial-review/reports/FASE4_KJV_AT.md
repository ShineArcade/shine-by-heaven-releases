# Fase 4 — KJV Reading 2026, Antiguo Testamento

Base: `a57cf85` (KJV v11) → **KJV v12**. Nuevo Testamento sin tocar.

## Cómo se buscó

Siete detectores sobre el **100 %** del texto proyectado del Antiguo Testamento
(`tools_audit/fase4_kjv_detect.py`): 4 032 ediciones, 3 412 versículos, offsets
válidos 4 032/4 032, cero superposiciones. Los detectores marcan estados imposibles,
no juicios editoriales: **cada candidato se leyó después en el versículo completo**,
original y proyección lado a lado, antes de decidir.

| Detector | Marcados | Defectos reales | Falsos positivos |
|---|---|---|---|
| K1 you/your junto a thee/thou/ye | 24 | 24 | 0 |
| K2 reemplazo idéntico repetido | 0 | — | — |
| K3 palabra duplicada o espaciado roto | 1 | 1 | 0 |
| K4 repetición de 4+ palabras | 6 | 1 | 5 |
| K5 artículo a/an incorrecto | 22 | 22 | 0 |
| K6 concordancia rota con thou/ye | 1 | 1 | 0 |
| K7 dos términos para el mismo referente | 3 | 3 | 0 |
| K8 his/its sobre el mismo objeto | 13 | 9 | 4 |

Los 5 falsos positivos de K4 (DEU 26:14, ECC 2:19, ISA 51:1, JER 20:14, NUM 34:11)
se dejaron como están: en los cuatro primeros el texto base ya repite la estructura;
en NUM 34:11 las dos palabras que la capa unificó son el mismo *gevul* hebreo, de modo
que el cambio **restituye** la uniformidad del original en vez de romperla. Los 4 de K8
(DEU 3:11, DEU 33:16, JOS 6:26, JOS 21:12) mezclan `his` e `its` porque se refieren a
**dos sujetos distintos** dentro del versículo, no a uno solo.

## Qué se corrigió

### Pronombres — 24 ediciones (K1)

La regla del proyecto es no modernizar el sistema pronominal de la KJV. Veinticuatro
reemplazos introducían `you`/`your` en versículos que conservaban `thee`, `thou`, `thy`
o `ye`. En cada uno se **conservó la modernización léxica** y se restituyó la forma que
concuerda con el pronombre del texto base:

| Referencia | Antes | Después |
|---|---|---|
| GEN 3:17 | listened to the voice of **your** wife | listened to the voice of **thy** wife |
| GEN 15:1 | **your** very great reward | **thy** very great reward |
| GEN 15:4 | come from **your own body** | come forth out of **thine own body** |
| GEN 25:23 | from **your womb** | from **thy body** |
| GEN 44:15 | **do you not know** that | **know ye not** that |
| GEN 46:34 | **Your** servants have worked with livestock | **Thy** servants have worked with livestock |
| GEN 48:6 | **your** offspring | **thy** offspring |
| EXO 2:14 | **do you intend** to kill me, as **you killed** | **dost thou intend** to kill me, as **thou killedst** |
| EXO 3:18 | listen to **your** voice · we ask **you** | listen to **thy** voice · we ask **thee** |
| EXO 7:16 | until now **you have refused to listen** | until now **thou wouldest not listen** |
| EXO 10:4 | locusts into **your** territory | locusts into **thy** territory |
| EXO 13:7 | throughout **your** territory | throughout all **thy** territory |
| EXO 15:7 | the greatness of **your** majesty | the greatness of **thy** majesty |
| EXO 16:23 | boil what **you** will boil | boil that **ye** will boil |
| EXO 17:2 | why do **you** test the LORD? | why do **ye** test the LORD? |
| EXO 22:26 | **your** neighbour's cloak as **collateral** | **thy** neighbour's cloak **as a pledge** |
| EXO 28:40 | **you shall make caps** for them | **caps shalt thou make** for them |
| EXO 33:18 | I plead with **you** | I plead with **thee** |

En GEN 46:34 el `Thy` se dirige a Faraón y el `ye` a los hermanos: son **dos
interlocutores distintos** en el texto base, no una incoherencia. Cambiar sólo uno de
los dos era lo que modernizaba a medias.

En EXO 22:26 se cambió además «collateral», término financiero moderno, por «as a
pledge», que conserva el sentido de *chavol*.

### Artículo — 25 ocurrencias en 22 versículos (K5)

Las reglas `ass → donkey`, `harlot → prostitute` y `husbandman → farmer` no tocaban el
artículo, y la proyección leía **«an donkey», «an prostitute», «an farmer»**. Cada
edición se amplió para incluir el artículo. Afecta a 1SA 16:20 y 25:42, 2SA 19:26,
2KI 4:24 y 6:25, DEU 22:10, JDG 11:1, 15:15, 15:16 (×2), 16:1, 19:28, JOS 2:1,
ISA 1:21 y 23:15, JER 22:19, EZK 16:31, JOL 3:3, AMO 7:17, MIC 1:7 (×2), PRO 7:10,
ZEC 9:9 (×2) y ZEC 13:5.

Los «an house», «an hundred» y «an harlot» **propios del texto base** no se tocan: son
la ortografía histórica de la KJV.

### Gramática y sentido — 7 correcciones puntuales

| Referencia | Problema | Solución |
|---|---|---|
| DEU 29:23 | `the whole land thereof → that whole land` chocaba con el «And that» anterior y producía **«And that that whole land»** | `→ the whole land` |
| EXO 18:18 | **«Thou will surely wear yourselves out»**: número y concordancia rotos; el versículo acaba en «thyself alone» | `wilt surely wear thyself out` |
| GEN 20:6 | «suffered I thee → allowed you» dejaba la oración **sin sujeto**: «therefore allowed you not to touch her» | edición ampliada: `I did not allow thee to touch her` |
| EXO 37:17 | la versión plana producía «he made the lampstand… he made the lampstand» | se restituye la inversión del original: `of hammered work made he the lampstand` |
| EXO 27:4 | el mismo versículo leía «network of **brass**» y «four **bronze** rings» | se convierte también el primero |
| EXO 4:6, 4:7 | «bosom → cloak» en 2 de las 36 apariciones, dejando «his bosom» sin tocar **en el mismo versículo** | se restituye el texto base; término reservado |
| EXO 13:16 | «frontlets between thine eyes → a reminder on your forehead» cambia el **objeto ritual** (*totafot*) y su lugar, y deja DEU 6:8 y 11:18 sin tocar | se restituye el texto base; término reservado |

### Familias de término incompletas — 52 ocurrencias en 48 versículos

Dos familias estaban convertidas a medias, lo que dejaba **dos nombres para el mismo
objeto** dentro del mismo libro y, en EXO 27:4, dentro del mismo versículo:

| Familia | Hebreo | Estado en v11 | Estado en v12 |
|---|---|---|---|
| `brass` / `brasen` → `bronze` | *nechoshet* | 107 de 148 | 148 de 148 |
| `candlestick` → `lampstand` | *menorah* | 30 de 41 | 41 de 41 |

Ambas corresponden a **una sola palabra hebrea en todo el Antiguo Testamento**, de modo
que la conversión es de clase y no depende del pasaje. Aun así los 48 versículos se
imprimieron y leyeron antes y después de aplicarla. La conversión de NUM 21:9 («serpent
of brass» → «of bronze») además pone el versículo de acuerdo con 2KI 18:4, que ya leía
«bronze» y habla del mismo objeto.

### Posesivo de objeto inanimado — 10 ediciones (K8)

La KJV usa `his` como posesivo de objetos inanimados en todo el corpus. La v11
introdujo `its` en 64 reemplazos; en nueve versículos de Éxodo eso dejaba **un mismo
objeto con las dos formas**: «his pans… **its** basins… his firepans» (EXO 27:3),
«The bronze altar, **its** bronze grate… all **his** vessels» (EXO 39:39). Se restituyó
`his`, conservando la modernización léxica (*basons→basins*, *fleshhooks→meat forks*,
*taches→clasps*, *staves→carrying poles*, *laver→basin*, *pins→tent pegs*).

Convertir todo el corpus de `his` a `its` es una decisión que afecta al Antiguo
Testamento entero y queda **registrada como pendiente**, no resuelta por cuenta propia.

## Reservas registradas en `registry.kjv.json`

| id | Término | Por qué se reserva | Referencias |
|---|---|---|---|
| `ot-final-2026-kjv-bosom` | bosom | *cheq* cubre el pecho y el pliegue del vestido | 32 |
| `ot-final-2026-kjv-frontlets` | frontlets | objeto ritual *totafot* en fórmula fija | 3 |
| `ot-final-2026-kjv-knop` | knop | **dos** palabras hebreas: *kaftor* (Éxodo) y *peqaim* (1 Reyes) | 12 |
| `ot-final-2026-kjv-glory-over-me` | Glory over me | modismo *hitpaer alay*; la lectura de v11 añadía interpretación | 1 |
| `ot-final-2026-kjv-inanimate-his` | his (objeto inanimado) | decisión de alcance total, no versículo a versículo | 8 |

## Resultado

| | v11 | v12 |
|---|---|---|
| Ediciones en el AT | 3 983 | 4 032 |
| Ediciones en toda la Biblia | 4 666 | 4 715 |
| Reseñas en `applied` | 3 354 | 3 406 |
| Términos pendientes | 71 | 76 |
| `contentSha256` | — | `91269585e45ff9a6f7d129fa43c68bde02eeb5feca0bdc37e21e1e84c07e5bcf` |

Libros con cambio de contenido: GEN, EXO, LEV, NUM, DEU, JOS, JDG, 1SA, 2SA, 2KI,
PRO, ISA, JER, EZK, JOL, AMO, MIC, ZEC. Los 21 libros restantes del Antiguo Testamento
quedaron **byte a byte idénticos** a `a57cf85`.

## Pruebas dirigidas

`apps/mobile/tool/verify_kjv_ot_final_2026_guards.py` — siete guardas (KG1–KG7) que
fallan si cualquiera de estos defectos vuelve. Se comprobó que **detectan de verdad**:
reintroduciendo a propósito el defecto, KG1/KG3, KG2, KG4, KG5 y KG6 fallan; con el
texto correcto, ninguna falla.

## Lo que esto **no** significa

Los detectores cubrieron el 100 % del texto proyectado y toda la lectura individual
recayó sobre lo que marcaron más los pasajes de riesgo. **Ningún libro del Antiguo
Testamento tiene todavía evidencia de lectura secuencial completa**, ni en KJV ni en
RV1909. La matriz `OT_2026_FINAL_COVERAGE.md` lo registra así y no debe leerse de otro
modo.

## Vuelta sobre KJV con los detectores que la Fase 3 obligó a inventar

La Fase 3 de RV hizo falta inventar dos detectores que no existían al hacer la primera
pasada de KJV. Se aplicaron después al Antiguo Testamento entero de KJV:

- **Colapso del texto** (un reemplazo que deja mucho menos de lo que sustituye): **0 casos
  graves** en KJV. El único del proyecto era Números 31:3 en RV.
- **Mismo `expected`, decisión divergente**: 5 términos. Tres son divergencia por sentido y
  se conservan (`prevent me` = salir al encuentro o recibir; `of cunning work` cambia de
  preposición según el pasaje; `abode`).
- **Familia convertida a medias**: 13 familias con 31 apariciones sueltas fuera, casi todas
  en Génesis, Levítico, Números y Deuteronomio, que se revisaron bajo versiones anteriores
  con juegos de reglas distintos. Se cerraron 24 apariciones en 12 familias:

  | Familia | Convertidas antes | Quedaban | Ahora |
  |---|---|---|---|
  | `harlot` → prostitute | 32 | 6 | 38 |
  | `raiment` → clothing | 30 | 6 | 36 |
  | `suburbs` → pasturelands (*migrash*) | 112 | 3 | 115 |
  | `chapiters` → capitals | 14 | 2 | 16 |
  | `usury` → interest | 20 | 2 | 22 |
  | `beforetime`, `emerods`, `nether`, `rereward`, `taches` | 9+7+14+5+9 | 1 c/u | — |

  Dos de esas apariciones eran **choques dentro del mismo versículo**: Génesis 38:21 leía
  «Where is the **prostitute**… There was no **harlot** in this place» por la misma palabra
  hebrea, y Génesis 45:22 leía «changes of **clothing**… five changes of **raiment**».

  `prevented` en Números 9:7 **no** se convierte: allí ya significa «ser detenido», que es
  el sentido moderno, y no el de 2 Samuel 22 («salir al encuentro»). Queda registrado como
  `ot-final-2026-kjv-prevent`.

Tras esta vuelta: **4 056 ediciones** en el AT, 3 431 versículos tocados, offsets
4 056/4 056, cero superposiciones; `contentSha256`
`6babfa6e5d7e88f1846d9199df80a32b039b0b2ccca1224ff2cd767335192ec0`, 3 429 reseñas
aplicadas y 77 términos pendientes. KG5 vigila ahora las once familias cerradas.
