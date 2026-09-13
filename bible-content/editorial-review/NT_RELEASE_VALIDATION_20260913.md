# Cierre de la revisión contextual NT

Revisión solicitada: los 27 libros, RV1909 y KJV, sobre RV v26/KJV v14.
Resultado preparado: RV v27 / KJV v15. La publicación efectiva debe comprobarse
en los canales firmados; este informe no acredita instalación en un teléfono.

- Lectura secuencial de ambas versiones, incluidos versículos antes sin cambios.
- Cierre por contexto y relectura de los compuestos; vuelta dirigida a Mateo y Marcos.
- 4.629 decisiones en 4.121 combinaciones versión/versículo, con razones y lectura final.
- 57 entradas nuevas de interpretación reservada; los términos y referencias
  previamente registrados permanecen o pasan a historial cuando ya fueron reemplazados.
- Corpus originales y 39 libros del Antiguo Testamento preservados. Las pruebas
  comparan la proyección completa contra la aprobada, no solo conteos de palabras.

## Integridad y pruebas actuales

`verify_nt_context_repairs.py --package-ready`, `verify_kjv_source_restoration.py`,
`validate_editorial_review_registry.mjs`, `verify_kjv_reading_2026.mjs`, ambos
smoke de canal y las guardas finales RV/KJV del AT pasan en la preparación.
El selector de ocurrencia verifica spans repetidos y rechaza posiciones obsoletas.
La reaplicación y reconstrucción se comprueban aparte como bytes idénticos.

Las siete comprobaciones históricas v22/v24/v25, KJV v10/v12/v13 y Marcos v23
también se ejecutaron; no son verdes sobre este contenido posterior. Sus primeras
expectativas incompatibles son: `confusión` frente a `desorden` en1CO14:33;
`forgiveness` frente a `passing over` enROM3:25; correas/straps frente a correa/strap
enMRK1:7; metadato fijo `ownerReview=22`; y fruit frente a fruits enMAT3:8.
No se han alterado esas pruebas ni se han reintroducido los errores para satisfacerlas.
Las decisiones nuevas explican cada modificación y la verificación actual comprueba
todos los versículos afectados, integridad, límites de palabras, ámbito y regresiones.
Una prueba técnica que pasa no certifica infalibilidad lingüística o teológica.

## Reparación de puntuación KJV

La fuente USFM verificada permite reparar 2.017 versículos en la capa; dos ya estaban
reparados. Veinte límites ambiguos tienen decisiones individuales y tres versículos
recuperan una letra final documentada. No se reescribe el corpus instalado.
Con Reading 2026 desactivado todavía se ve el defecto del corpus anterior; una futura
migración del corpus requiere su propio contrato de compatibilidad. No confundir
esta reparación compatible con una actualización del archivo base.

## Paquetes preparados

- RV v27: 12.026 ajustes activos, 9.128 versículos; SHA-256
  `0af535e37cb05b056ea57d633e9b49cb86ae2f120186c31a73391df36e0f02c4`.
- KJV v15: 14.585 ajustes activos, 7.927 versículos; SHA-256
  `130a1ac72f901caf7f3ad1331fa65a86e3a9ecc7a72329d800b93b695a4fc629`.

Son conteos del paquete completo, incluido AT y puntuación; no son conteos de
errores nuevos ni de palabras distintas. El diario inicial, el cierre, el manifiesto
y el historial completo permiten auditar conservar/ajustar/restaurar por contexto.
