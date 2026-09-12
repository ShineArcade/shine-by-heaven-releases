# Integración de la auditoría del Antiguo Testamento — RV v26 / KJV v14

Fuente auditada: commit `62caea3` de `ot/final-review-20260912`.

Base pública de integración: commit `74b7aa1`, con RV v25 y KJV v13.

## Decisión de integración

La rama de auditoría partió de RV v22/KJV v11. No se fusionó directamente,
porque hacerlo habría reemplazado la revisión posterior del Nuevo Testamento.
Se tomó únicamente el contenido del Antiguo Testamento que la auditoría dejó
distinto y se combinó con el Nuevo Testamento público vigente.

La comparación estructural confirma:

- RV: 28 libros del Antiguo Testamento distintos de la base pública.
- KJV: 18 libros del Antiguo Testamento distintos de la base pública.
- Los 39 libros del Antiguo Testamento resultantes coinciden exactamente con
  la rama auditada en ambas Biblias.
- Los 27 libros del Nuevo Testamento resultantes coinciden exactamente con la
  versión pública RV v25/KJV v13.

## Resultado preparado

| | RV1909 Lectura 2026 | KJV Reading 2026 |
|---|---:|---:|
| Nueva versión | 26 | 14 |
| Versículos con ediciones | 7.747 | 4.763 |
| Ediciones acumuladas | 10.036 | 5.610 |
| Reglas del delta de integración | 869 | — |
| Reglas RV retiradas | 189 | — |
| Términos reservados | 192 | 111 |

El defecto de Números 31:3 que reducía dos frases a la conjunción `e` queda
retirado. El versículo vuelve a conservar sus cláusulas completas.

## Verificación ejecutada

- Aplicación repetida e idempotente del change-set RV v26.
- Construcción determinista de ambos paquetes.
- Integridad del corpus fuente RV1909 y KJV.
- 10 guardas de regresión RV sobre los 39 libros del Antiguo Testamento.
- 7 guardas de regresión KJV, 4.056 offsets válidos y cero superposiciones.
- Conservación de los 27 libros del Nuevo Testamento de RV v25 y KJV v13.
- Smoke tests de los dos canales con versiones 26 y 14.

## Límite de la evidencia

La auditoría pasó detectores sobre todo el Antiguo Testamento y leyó completos
los versículos marcados y los pasajes de riesgo. No existe evidencia de una
lectura humana secuencial de los 23.145 versículos de cada Biblia. Las reservas
siguen visibles en el registro y no se aplican automáticamente.
