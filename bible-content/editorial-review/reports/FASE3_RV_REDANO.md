# Fase 3 — RV1909 Lectura 2026: familia «redaño»

Base: `a57cf85` (v22) → versión de esta rama **v23**.

## Hallazgo

RV1909 usa una sola palabra, «redaño», para **dos términos hebreos distintos**:

| Hebreo | Sentido | Apariciones tratadas así en RV1909 |
|---|---|---|
| *yoteret* (יֹתֶרֶת) | el lóbulo o apéndice del hígado | Ex 29:13, 29:22; Lv 3:4, 3:10, 3:15, 4:9, 7:4, 8:16, 8:25, 9:10, 9:19 |
| *peder* (פֶּדֶר) | el sebo | Lv 1:8, 1:12 |

La capa v22 sólo había tocado las dos apariciones de Éxodo y las había convertido en «grasa»,
colapsando *yoteret* con *chelev* (el sebo) **dentro del mismo versículo**: Ex 29:13 enumera
«el sebo… y el redaño del hígado», dos elementos distintos del sacrificio, que quedaban
como uno solo.

## Decisión y votos

«el lóbulo del hígado» donde traduce *yoteret*; texto conservado donde traduce *peder*.

- NVI: «el lóbulo del hígado» (Ex 29:13, Lv 3:4).
- LBLA: «el lóbulo del hígado».
- RVR1960: «la grosura que está sobre el hígado» — lo funde con la grosura.
- RVC: lo funde con la grosura.

**Son 2 de 4, no un consenso de cuatro.** El argumento decisivo no es el recuento sino que
*yoteret* y *chelev* aparecen juntos en el mismo versículo: ninguna de las cuatro versiones
los iguala entre sí. Las dos apariciones de *peder* quedan registradas como pendientes en
`registry.json` (`leviticus-v17-1`) y el texto no se toca.

## Aplicado

11 ediciones, en 11 versículos. Los 13 versículos con «redaño» se releyeron proyectados
uno por uno; los dos de *peder* se verificaron sin tocar.

## Corrección de una pasada anterior

La primera pasada de esta familia produjo «el lóbulo del el hígado» (Ex 29:13) y «el lóbulo
del hígado del hígado» (Lv 8:16, 8:25, 9:19) porque el `expected` no abarcaba el sintagma
completo. Se corrigió con spans exactos y se releyó el resultado.
