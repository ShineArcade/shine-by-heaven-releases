# Revisión adicional del Nuevo Testamento — plan y estado verificable

Autoridad: `shine-by-heaven-releases`, base pública `8de177c`, RV v26 / KJV v14.
Responsable de escritura: líder de esta conversación. Rama `codex/nt-context-repair-20260912`.
Alcance: conservar lo correcto, revisar y reparar los 27 libros del NT en ambas capas.
No confundir pruebas de integridad con validación editorial. Nunca marcar un libro leído por ejecutar un detector.

## Secuencia

1. Localizar fuente USFM KJV y reproducir pérdida de puntuación; identificar alcance y migración compatible antes de alterar hashes fuente.
2. Extraer por capítulo texto base, lectura publicada y diferencias. Conservar un registro de cobertura real.
3. Contrastar hallazgos de Mateo con el texto completo y fuentes, incluidos posibles errores del auditor.
4. Leer progresivamente RV y KJV en orden de libro; registrar mantener/ajustar/revertir/añadir/reservar y evidencias. Detectores producen candidatos, nunca aprobación.
5. Releer cada versículo corregido con vecinos, concordancia, referentes, número, negación, tiempo y paralelismos. Verificar familias por sentido.
6. Construir guardas de regresión con fallos anteriores como negativos. Verificar integridad, cobertura editorial, historial y compatibilidad.
7. Preparar paquetes monotónicos y registro público. Publicación/recepción se reportan separadamente de la preparación.

## Estado al cierre de la ronda, 2026-09-13

Los 27 libros están leídos en ambas versiones y tienen cierre contextual documentado.
4.629 decisiones, 4.121 combinaciones versión/versículo; paquetes RV v27/KJV v15
preparados y verificados. La reaplicación y ambos paquetes son byte a byte reproducibles.
Las reservas interpretativas se conservan explícitamente; no se afirma perfección absoluta.
Consultar `NT_RELEASE_VALIDATION_20260913.md`, `NT_RESERVATION_CLOSURE_20260912.md`
y los canales firmados para distinguir preparación de publicación y recepción.

## Hitos anteriores conservados como historial

- Base pública verificada y worktree aislado creado.
- Mateo: lectura inicial completa de sus 1.071 versículos en cada versión, texto renderizado y deltas; correcciones locales y relectura en curso. Esto no equivale a una certificación final de todos los problemas semánticos.
- Marcos: lectura inicial completa de 678 versículos en cada versión, incluyendo texto sin ediciones. Ajustes locales releídos; falta cierre editorial y revisión de las reservas.
- Lucas: leídos sus 24 capítulos en ambas versiones, texto completo y diferencias, incluyendo versículos sin cambios anteriores. Sus reparaciones se han releído como versículos completos; quedan reservas contextuales documentadas para el cierre. Juan también tiene lectura inicial completa de 21 capítulos en ambas versiones; Hechos también está leído completo en ambas versiones; Romanos también tiene lectura inicial completa en ambas versiones; 1 Corintios también está leído completo en ambas versiones; 2 Corintios también está leído completo en ambas versiones; Gálatas también está leído completo en ambas versiones; Efesios también está leído completo en ambas versiones; Filipenses también está leído completo en ambas versiones; Colosenses también está leído completo en ambas versiones; 1 y 2 Tesalonicenses también están leídos completos en ambas versiones; 1 y 2 Timoteo también leídos completos en ambas versiones; Tito y Filemón también están leídos completos en ambas versiones; Hebreos también está leído completo en ambas versiones; Santiago y ambas cartas de Pedro también están leídos completos; Las tres cartas de Juan y Judas también están leídos completos; Apocalipsis también tiene lectura inicial completa. Los27libros están leídos en ambas versiones; falta cierre de reservas y controles finales. NT no terminado. Cobertura explícita en nt-context-coverage-20260912.json.
- Estado local: 4.350 decisiones individuales, de Mateo a Apocalipsis completos en lectura inicial. Cada entrada conserva original, lectura anterior, propuesta, ediciones sustituidas y lectura final combinada. La relectura corrigió propuestas propias antes de publicar: RV MAT 8:21, KJV MAT 14:22, RV MRK 6:43 y 10:12, KJV MRK 14:64; RV LUK 1:1, 1:35, 12:39; KJV LUK 1:8, 5:3, 8:43, 12:11. El número de decisiones no equivale a número de palabras erróneas ni a publicación.
- Fuente del importador localizada en el checkout Mobile activo, `scripts/build-mobile-bible-pack.mjs`. El parser actual recupera la puntuación del USFM oficial. Verificados tamaño y SHA de los USFM de los 66 libros canónicos contra el manifiesto instalado: `kjv-source-provenance-proof-20260912.json`. Esto no afirma identidad de archivos auxiliares ni de apócrifos del ZIP.
- Comparación del corpus KJV con reconstrucción: 2.019 versículos en 8 libros, 2.016 con las mismas letras; tres recuperan una letra final perdida (MRK 4:24, LUK 7:44, JHN 13:20). Es un defecto previo al plugin. Aún sin migración publicada; el corpus instalado continúa intacto.
- Las validaciones Mobile exigen spans no vacíos y fuente idéntica: una reparación compatible no puede limitarse a cambiar el hash del corpus ni insertar parches de longitud cero.
- Restauración compatible preparada en la capa: 2.017 versículos reciben la puntuación/letra fuente verificada; dos ya estaban restaurados. Dieciocho límites se resolvieron individualmente, incluido MRK 9:42: una coma después de «me» habría partido «causes ... to stumble». La guarda reproduce y rechaza ese fallo. Los spans serializados son no vacíos, conservan el hash fuente y reproducen exactamente la lectura aprobada. No es una revisión editorial de los ocho libros afectados. Con la capa desactivada, el corpus antiguo todavía conserva el defecto; no se afirma una reparación del corpus instalado.
- Inventario del auditor disponible en `shine-mateo-audit-20260912/audit_mateo/entrega`.
- Los JSON de dirección locales son una preparación reversible: antes de publicar deben convertirse en changesets canónicos, registro editorial y paquetes versionados; no se han firmado ni publicado. Los paquetes gzip existentes siguen siendo los de la base pública, no prueban estos cambios locales.
- `verify_nt_context_repairs.py`: comprobación dirigida de cambios declarados, spans enteros, historial y regresiones reales; corpus y canales publicados intactos. PASS con la tanda local. Esto no sustituye la batería oficial posterior al build ni certifica lectura editorial de los libros pendientes.

## Criterio

Cambios mínimos por comprensión, nunca modernización general por preferencia. Conservar imágenes, doctrina y lectura textual. Un mismo lema puede requerir distintas palabras por contexto. Consenso de traducciones y referencias deben comprobarse; no contarlos de memoria. Las propuestas del auditor se revisan, no se aplican en bloque.
