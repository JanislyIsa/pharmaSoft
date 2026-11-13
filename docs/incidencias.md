# Incidencias S14

| ID | Módulo | Descripción y pasos | Severidad | Causa | Corrección (commit) | Estado |
|---|---|---|---|---|---|---|
| INC-01 | API Productos/Ventas | Pedir tamanio=500 devolvía datos en vez de 409. | Alta | Faltaba validar el límite 100. | Rangos 1 a 100 y rechazo de páginas negativas; backend `9ec8c49`. | Cerrada |
| INC-02 | SPA listados | Recargar perdía la página; cambiar filtros podía conservar una página inexistente. | Media | Estado fuera de la URL. | Inputs de URL y reinicio a página 0; frontend `1920d4e`. | Cerrada |
| INC-03 | Paginador | Mostraba 5 aunque cargaba 20 filas. | Media | Valor aplicado antes de crear las opciones. | Selección explícita de la opción real; frontend `b09009a`. | Cerrada |
| INC-04 | Nueva venta | Buscar un producto posterior a los primeros 100 no lo encontraba. | Alta | Filtrado de un bloque local incompleto. | Búsqueda remota por nombre o categoría de activos con stock, debounce y cancelación; backend `9ec8c49`, frontend `1920d4e`. | Cerrada |
| INC-05 | Migraciones | Arrancar no aplicaba V4 mediante Flyway. El primer intento posterior falló por el orden de declaraciones PL/SQL. | Alta | Faltaba starter-flyway de Boot 4; Hibernate update ocultaba la falta. | Starter, baseline 2 para el esquema legado, V4 conservadora, reparación del intento fallido y ddl-auto validate; backend `9ec8c49`. | Cerrada |
| INC-06 | Prueba de auditoría | Primera suite: 6/7. Se esperaba 12.50, pero el evento guardó 12.5. | Baja | Assert exigía formato en lugar de equivalencia decimal. | Se comprueban ambos importes y el ID, aceptando ceros finales opcionales; frontend `18bbabe`. | Cerrada |

La suite final pasó 7/7 tres veces, sin reintentos. Los JSON de `evidencias-s14/` registran las corridas y la matriz 8/8. No hay incidencias funcionales críticas ni altas abiertas. Las variantes inactiva y agotada se excluyen del buscador; una venta con segunda línea inválida hace rollback del stock y no deja un evento confirmado.

Docker también requirió recuperar dos sockets temporales y reiniciar únicamente docker-desktop. Se conservaron los volúmenes y los respaldos de los directorios temporales.
