# Herramientas de la auditoría del Antiguo Testamento 2026-09-12

> Registro histórico de la rama de auditoría v23/v12. Sus cambios revisados se
> integraron sobre la línea pública posterior como RV v26 y KJV v14.

Todo lo que hizo falta para producir RV v23 y KJV v12 se puede volver a ejecutar desde la
raíz del repositorio. En orden de uso:

| Herramienta | Para qué |
|---|---|
| `detect_rv_projection_defects.py` | Diez detectores sobre el 100 % del AT proyectado en RV1909. |
| `detect_kjv_projection_defects.py` | Siete detectores equivalentes sobre KJV. |
| `detect_collapsing_replacements.py` | Busca reemplazos que **borran** texto en las dos Biblias. Es el que encontró Números 31:3. |
| `diff_rv_projection_against.py <ref>` | Compara el texto proyectado con el de otro commit, versículo a versículo. Detecta modernizaciones absorbidas sin querer por una edición más ancha. |
| `make_change_spans_unique.py` | Ensancha las ediciones cuyo `expected` no es único en su versículo. Sin esto, la publicación falla en su primer paso. |
| `repair_verse_source_hashes.py` | Repone `sourceTextSha256` en los versículos añadidos. |
| `build_ot_final_2026_change_set.py` | Regenera `editorial-changes/v23.json` diferenciando la capa contra `a57cf85`. |
| `build_kjv_v12_package.py` | Publica KJV v12 sincronizando el registro con la diferencia real contra `a57cf85`. |
| `build_public_change_list.py` | Genera el registro público de cambios que consume la web. |
| `verify_ot_final_2026_guards.py` | Guardas RV G1–G10: fallan si vuelve un defecto ya corregido. |
| `verify_kjv_ot_final_2026_guards.py` | Guardas KJV KG1–KG7. |
| `run_ot_final_2026_battery.py` | **La batería completa**: 54 comprobaciones de una sola vez. |

Para verificar el estado entero basta con la última:

```
python bible-content/apps/mobile/tool/run_ot_final_2026_battery.py
```
