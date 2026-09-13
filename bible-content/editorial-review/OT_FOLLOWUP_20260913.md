# Repaso breve de cambios del Antiguo Testamento — 13 septiembre 2026

Base pública comprobada: RV1909 v27 y KJV v15, commit `42d612b`.
Resultado de este repaso: RV1909 v28 y KJV v16. La publicación se comprueba en
los canales firmados; este informe no certifica recepción en cada dispositivo.

## Alcance real

Se ejecutaron las guardas existentes sobre los 39 libros de ambas versiones:
5.315 versículos modificados RV y 3.431 KJV. Se validaron 7.022 y 4.056 offsets,
respectivamente, y se confirmó que el AT coincidía con la integración auditada
v26/v14. Esas pruebas pasaron **antes** de encontrar los problemas siguientes;
por ello no se presentan como prueba de fidelidad editorial absoluta.

Después se releyó una muestra dirigida de 66 pasajes con versión identificada:
33 RV y 33 KJV, de los cuales 55 tenían cambios y 11 eran controles conservados.
Se añadieron ambas lecturas de 2 Samuel 22:27 como paralelo de Salmos 18:26.
La muestra priorizó concordancia, imágenes, referentes, espacios del templo y
pasajes que ya habían suscitado objeciones. No fue una nueva lectura completa del AT.

Las referencias se consultaron en los archivos locales RVR1960, LBLA, NVI y NIV
(tres versiones españolas y una inglesa), leyendo los versículos completos.
El historial adjunto conserva los hashes de esos archivos; no redistribuye sus
textos completos. Las referencias orientan una decisión por contexto, no una
sustitución automática por mayoría.

## Cuatro correcciones, cinco ocurrencias

| Versión y referencia | Lectura anterior de la capa | Lectura corregida | Razón |
|---|---|---|---|
| RV Zacarías 14:4, dos menciones | las Olivos | los Olivos | El nombre modernizado es masculino. Se amplían los dos tramos para incluir el artículo. El paralelo 2 Samuel 15:30 ya tenía esta corrección; faltaba aquí. |
| KJV 2 Reyes 23:11 | pasturelands | court | Se describe el recinto de entrada al templo junto a la cámara del funcionario, no pastos de una ciudad levítica. |
| KJV Ezequiel 45:2 | pasturelands | open space | La franja rodea el santuario; se conserva su función espacial sin añadir uso ganadero. |
| KJV Salmos 18:26, segunda ocurrencia | show thyself perverse | show thyself shrewd | El primer calificativo describe a la persona; el segundo, la respuesta de Dios. NIV, LBLA, NVI y el paralelo 2 Samuel 22:27 distinguen esa respuesta; RVR1960 la expresa como severidad. El primer perverse y los pronombres KJV se conservan. |

El registro exacto de antes/después, offsets, razón y referencias locales está en
[`ot-followup-20260913.json`](ot-followup-20260913.json). La web añade estas cuatro
decisiones al historial previo; no reemplaza ni borra la revisión del NT.

## Decisiones que no se generalizaron

- Se mantienen los pastos de 1 Crónicas 6:55 y Levítico 25:34. Las dos excepciones
  del templo no justifican cambiar el resto de `suburbs` ni de `ejidos`.
- En Éxodo 7:14, RVR1960 y NVI locales sí usan «endurecido»; LBLA y NIV expresan
  terquedad o resistencia. La objeción antigua no demuestra por sí sola un error
  en este versículo. No se reescribe toda la familia del endurecimiento.
- Éxodo 9:23, 10:7 y 15:8 muestran diferencias reales de expresión entre las
  referencias. Las lecturas activas tienen apoyo contextual: rayos en NVI/NIV,
  ruina en LBLA/NVI y aliento en RVR1960/LBLA. Se conservan en este repaso.
  En particular, los archivos locales contradicen la afirmación anterior de que
  RVR1960 conserva necesariamente «narices» en 15:8: el archivo leído dice aliento.
- Éxodo 15:11 queda señalado para revisión específica de la fuerza de «terrible»
  y de «loores». La diversidad entre referencias no autoriza declarar que la
  solución actual sea la única fiel. No se aplica una nueva paráfrasis aquí.
- En 2 Samuel 22:27, `unsavoury` pertenece al original KJV y no fue introducido por
  la capa. Se registra para una futura aclaración contextual; no se cambia por
  propagación automática desde Salmos.
- Génesis 1:27 RV conserva el original `crió`. Se usó como control, no como prueba
  de que el vocabulario original entero ya estuviese modernizado.

## Verificación de la corrección

Las guardas incorporan las regresiones concretas: `las Olivos`, pastos indebidos
en los dos recintos y la segunda ocurrencia de Salmos. Un verificador adicional
compara los **132 libros empaquetados** con v27/v15 y admite exclusivamente estas
cuatro decisiones documentadas. Los 27 libros NT de ambas versiones, todos los
demás versículos del AT y los corpus fuente deben conservarse.

La publicación requiere reaplicación idempotente del change-set RV, construcción
determinista, registro obligatorio, ambos smoke de firma/paquete, guardas AT,
verificación contextual NT y reparación de puntuación KJV. Las reservas siguen
visibles; ni esta revisión breve ni las pruebas certifican ausencia total de errores.

### Resultado local de las pruebas antes de publicar

- Reaplicación y reconstrucción: 138 artefactos idénticos byte por byte.
- Registro obligatorio y ambos smoke completos de canal: PASS.
- Guardas AT RV/KJV y comparación de 132 libros: PASS; cuatro versículos admitidos.
- Verificación contextual de las 4.629 decisiones NT y los 2.017 versículos de
  puntuación restaurada: PASS; no se alteran en este lote.
- RV28: 12.026 ajustes activos, SHA-256 del paquete
  `da4c7fc9ed3f2af47380f0d2ee2a98bd4bac0fb19c53ef093b23fc7068f98d09`.
- KJV16: 14.585 ajustes activos, SHA-256 del paquete
  `500cd6bf520d923e41ae7ce5e4e692d4222dc9e5e2d3a84c242da7775f634436`.

El número de ajustes se conserva porque se corrigen ocurrencias existentes.
Los historiales añaden una decisión RV y tres KJV; las dos reservas añadidas
figuran en los registros públicos, con sus referencias y motivos.
