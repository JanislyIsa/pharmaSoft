# Incidencias S14

| ID | Módulo | Descripción y pasos | Severidad | Causa | Corrección (commit) | Estado |
|---|---|---|---|---|---|---|
| INC-01 | API Productos/Ventas | Pedir tamanio=500 devolvía datos en vez de 409. | Alta | Faltaba validar el límite 100. | Rangos 1 a 100 y rechazo de páginas negativas; backend `9ec8c49`. | Cerrada |
| INC-02 | SPA listados | Recargar perdía la página; cambiar filtros podía conservar una página inexistente. | Media | Estado fuera de la URL. | Inputs de URL y reinicio a página 0; frontend `1920d4e`. | Cerrada |
| INC-03 | Paginador | Mostraba 5 aunque cargaba 20 filas. | Media | Valor aplicado antes de crear las opciones. | Selección explícita de la opción real; frontend `b09009a`. | Cerrada |
| INC-04 | Nueva venta | Buscar un producto posterior a los primeros 100 no lo encontraba. | Alta | Filtrado de un bloque local incompleto. | Búsqueda remota por nombre o categoría de activos con stock, debounce y cancelación; backend `9ec8c49` y `e3c970c`, frontend `1920d4e`. | Cerrada |
| INC-05 | Migraciones | Arrancar no aplicaba V4 mediante Flyway. El primer intento posterior falló por el orden de declaraciones PL/SQL. | Alta | Faltaba starter-flyway de Boot 4; Hibernate update ocultaba la falta. | Starter, baseline 2 para el esquema legado, V4 conservadora, reparación del intento fallido y ddl-auto validate; backend `9ec8c49`. | Cerrada |
| INC-06 | Prueba de auditoría | Primera suite: 6/7 por formato decimal. Verificación posterior: 18/21 por posición del dato de prueba fuera de página 1. | Baja | Assert exigía formato en lugar de equivalencia decimal. En una verificación posterior, el prefijo numérico del producto quedó fuera de la primera página con el orden de la conexión JDBC. | Se comprueban ambos importes y el ID, aceptando ceros finales opcionales; el test recorre el paginador real para localizar el producto, sin suponer que esté en la primera página; frontend `18bbabe` y `6160fe5` (localización con paginador real). | Cerrada |

La suite final pasó 7/7 tres veces, sin reintentos. Los JSON de `evidencias-s14/` registran las corridas y la matriz 8/8. No hay incidencias funcionales críticas ni altas abiertas. Las variantes inactiva y agotada se excluyen del buscador; una venta con segunda línea inválida hace rollback del stock y no deja un evento confirmado.

Docker también requirió recuperar dos sockets temporales y reiniciar únicamente docker-desktop. Se conservaron los volúmenes y los respaldos de los directorios temporales.

## Ampliación autónoma - 15 de noviembre de 2026

La tabla anterior conserva causas, correcciones y commits reales. Se completa con fecha, resultado esperado/obtenido y regresión. BE significa backend y FE frontend.

| ID / fecha | Reproducción | Esperado / obtenido antes del arreglo | Regresión |
|---|---|---|---|
| INC-01 / 13-11-2026 | GET productos o ventas con tamanio=500 | Rechazar >100 / devolvía 200 | PaginacionTest y `evidencias-s14/02-mediciones-despues.json` |
| INC-02 / 13-11-2026 | Página 3, F5 y después cambiar fechas | Conservar página al recargar y volver a 0 al filtrar / perdía estado o quedaba página inválida | `e2e/paginacion.spec.ts` y E2E-11 |
| INC-03 / 13-11-2026 | Abrir lista tamaño 20 tras carga asíncrona | Selector 20 / selector 5 con 20 filas | `e2e/paginacion.spec.ts`, cambio a 50 y cuenta real de filas |
| INC-04 / 13-11-2026 | Buscar un producto posterior a los primeros cien | Encontrarlo por nombre/categoría / no aparecía | `e2e/flujo-venta.spec.ts`, nuevo producto y exclusión de agotado/inactivo |
| INC-05 / 13-11-2026 | Arrancar y consultar flyway_schema_history | V4 aplicada / no se ejecutaba; primer intento posterior falló en PL/SQL | Arranque validate y `evidencias-s14/05-migracion.json`, SUCCESS=1. No automatizar repair sobre bases ajenas |
| INC-06 / 13-11-2026 | Precio con ceros finales y producto fuera de página 1 | Equivalencia decimal y localizar su fila / 6 de 7 y después 18 de 21 | Flujo integrado recorre paginador; histórico 21/21 y actual 42/42 |

## INC-07 - Chromium ausente

- Fecha: 15/11/2026. Módulo: entorno de pruebas. Severidad: media. Estado: cerrada.
- Reproducir: ejecutar Playwright sin el navegador descargado en el perfil de Windows.
- Esperado: abrir Chromium. Obtenido: 42 errores de arranque, `Executable doesn't exist`; ningún flujo llegó a ejecutarse.
- Causa raíz: caché de navegadores ausente tras recuperar el equipo. No era un fallo intermitente del sistema.
- Corrección: `npx.cmd playwright install chromium`. No corresponde un commit de binarios; la instrucción queda en `checklist-demo.md`, commit documental de autónoma identificable en el tag v1.0-demo.
- Regresión: las siguientes corridas abren el navegador. Diagnóstico sanitizado en `evidencias/s14-estabilizacion/diagnosticos.json`.

## INC-08 - Etiqueta del filtro Acción

- Fecha: 15/11/2026. Módulo: auditoría/accesibilidad. Severidad: media. Estado: cerrada.
- Reproducir: seleccionar Acción con su etiqueta exacta en E2E-12.
- Esperado: seleccionar VENTA_ANULADA y conservar filtro tras F5. Obtenido: timeout en las tres repeticiones; 39/42 aprobadas.
- Causa raíz: el label envolvía las opciones; su nombre accesible incluía sus textos y no era exactamente «Acción». La traza muestra `locator.selectOption` esperando `internal:label="Acción"s`.
- Corrección: `aria-label="Acción"` en el select. Commit FE `5809bc4`.
- Regresión: E2E-12; nueva corrida completa 42/42 sin retries. La traza original queda local porque contiene tráfico autenticado; se publica solo el diagnóstico sin secretos.

## Resumen actualizado

| Severidad | Total | Abiertas |
|---|---:|---:|
| Crítica | 0 | 0 |
| Alta | 3 | 0 |
| Media | 4 | 0 |
| Baja | 1 | 0 |

Por módulo: API/paginación 1; SPA/listados 1; SPA/paginador 1; integración/catálogo 1; migraciones 1; E2E 1; entorno 1; auditoría/accesibilidad 1. Ocho incidencias cerradas y ninguna crítica ni alta abierta. Las tareas personales de ensayo/entrega y los límites descritos en defensa técnica no se presentan como funcionalidades completadas.
