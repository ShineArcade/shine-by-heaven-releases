# Fase 7 — Integración y distribución

> Informe histórico de la rama v23/v12. La integración final se hizo sobre la
> línea pública posterior y quedó preparada como RV v26/KJV v14; consulte
> `INTEGRACION_AUDITORIA_AT_v26_v14.md` para el estado vigente.

Rama: `ot/final-review-20260912`, sobre la base canónica `a57cf85`.

## Estado listo para publicar

| | Lectura 2026 (RV1909) | Reading 2026 (KJV) |
|---|---|---|
| Versión publicada hoy en el canal | v22 | v11 |
| Versión preparada en esta rama | **v23** | **v12** |
| `contentSha256` del paquete | `2e4d1355504e9f69d31aea225b6da5672876228b88b000d360f6bb88ee95eec8` | `6babfa6e5d7e88f1846d9199df80a32b039b0b2ccca1224ff2cd767335192ec0` |
| Corpus fuente | intacto, verificado archivo por archivo | intacto |
| Nuevo Testamento | idéntico a `a57cf85` | idéntico a `a57cf85` |

Manifiestos, paquetes y hashes están regenerados y son **reproducibles byte a byte**: la
batería reconstruye ambos paquetes y comprueba que salen idénticos.

## La actualización sigue siendo incremental

La capa no reescribe la Biblia: el corpus RV1909 y el KJV son inmutables y lo que viaja es
el **delta**. `editorial-changes/v23.json` contiene 869 reglas nuevas o revisadas y 189
retiradas —no las 9 418 ediciones acumuladas—, y el canal declara `versionAuthority:
contentVersion` con `higherVersion: accept-after-verification`, de modo que un cliente en
v22 recibe únicamente lo que cambia. Eso no se ha tocado.

## El fallo que habría detenido la publicación

El primer paso del workflow es `apply_editorial_change_set.mjs`. Al ejecutarlo:

```
Error: Editorial change validation failed: 1SA 28:7 expected text
```

El contrato exige que **cada reemplazo identifique una sola ocurrencia exacta**, y el
aplicador rechaza un cambio cuyo `expected` aparece dos veces en el mismo versículo. Nueve
ediciones de v23 lo incumplían: 1 Samuel 28:7, 2 Crónicas 10:16, Deuteronomio 22:26,
Jeremías 40:5, Números 7:1 y Rut 4:1 —todas ellas versículos donde la misma frase aparece
dos veces—. **Tal como estaba, la publicación se habría parado en su primer paso.**

Se resolvió ensanchando cada edición palabra a palabra hasta que el tramo es único y
trasladando el prefijo y el sufijo al reemplazo, de modo que el texto proyectado **no
cambia**: comprobado, 0 versículos difieren. La comprobación está ahora en la batería como
puerta permanente.

## Puertas del contrato de distribución

| Puerta | Estado |
|---|---|
| 1. La nueva versión supera a la publicada | **pasa** · RV v23 > v22, KJV v12 > v11 |
| 2. Cada reemplazo identifica una ocurrencia exacta, con motivo y evidencia | **pasa** · 0 ambiguos de 869 |
| 3. Reaplicar el change-set es idempotente | **pasa** · y no altera la capa |
| 4. El paquete trae los 66 libros y reproduce los hashes del corpus | **pasa** |
| 5. Smoke test de firma efímera sobre fuente, paquete, motivo y evidencia | **pasa** · las dos Biblias |
| 6. GitHub Actions firma y verifica los bytes de producción | **BLOQUEADA** |

## El único paso bloqueado

La puerta 6 exige firmar el canal con la clave Ed25519 de producción, que vive como secreto
de GitHub Actions (`SHINE_BIBLE_CONTENT_SIGNING_PRIVATE_KEY_PEM`) y **no está disponible
aquí**. El disparador es un *push* a `main` que toque `bible-content/**`, y ese push es
exactamente lo que esta tarea tiene prohibido hacer: publicar releases, desplegar la web o
cambiar los canales activos.

**Paso bloqueado, con nombre y apellidos:**

> Hacer *merge* de `ot/final-review-20260912` a `main` y empujarlo, para que el workflow
> `.github/workflows/bible-content.yml` firme `channel/channel-stable.json` y
> `channel/kjv-channel-stable.json` con la clave protegida, verifique los bytes publicados,
> cree la release inmutable `bible-content-v23` y dispare la regeneración del sitio.

Eso lo tiene que lanzar quien custodia la clave. No se ha sustituido por ningún otro
método: no se ha firmado con una clave alternativa, no se ha tocado ningún canal activo, no
se ha subido ninguna release y no se ha llamado al hook de despliegue.

Lo que sí queda hecho: **todo lo demás**. Al hacer ese merge, el workflow encuentra el
change-set aplicado, el registro validado, los paquetes reproducibles y las seis puertas
—salvo la suya propia— ya verdes.

## Consumo desde los tres clientes

Móvil, escritorio y web consumen el mismo `channel-stable.json` firmado; ninguno necesita
copias de los archivos fuente. Lo que esta rama cambia es el contenido que ese canal
apuntará tras la firma. El comportamiento de recepción —rechazo de bajada de versión,
conflicto ante igual versión con distinto hash, conservación de la última revisión válida
ante fallo— no se ha tocado.

## Cómo reproducir la verificación

```
python bible-content/apps/mobile/tool/run_ot_final_2026_battery.py
```

54 comprobaciones. Al cierre de esta fase: 43 pasan, **0 fallan por esta auditoría**, 11
ya fallaban en `a57cf85` —medido ejecutándolas en un worktree sobre ese commit, no supuesto—.
