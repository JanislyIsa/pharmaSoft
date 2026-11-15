# Verificación del flujo principal

El asistente ejecutó estos recorridos por la interfaz de Nginx (:8081), fuera del runner E2E. Cada uno comenzó con un producto distinto recién creado con stock 20, un cliente sintético y sesión cerrada. No se vació la base existente. No se presentan como ensayos orales del estudiante.

| Fecha y hora Lima | Duración | Venta / producto | Resultado | Desvío |
|---|---:|---|---|---|
| 15/11/2026 17:58 | 121 s | 22430 / 22434 | Comprobante; stock 20→19 | Pausa para recopilar evidencia, incluida en el tiempo |
| 15/11/2026 17:59 | 74 s | 22435 / 22435 | Comprobante; stock 20→19 | Pausa para contrastar pruebas, incluida en el tiempo |
| 15/11/2026 18:00 | 41 s | 22439 / 22436 | Comprobante; stock 20→19 | Se amplió la página a 100 por altas concurrentes de la suite |

Secuencia: login vendedor → cliente preparado → producto → cantidad 1 → revisar y confirmar → comprobante → Productos sin F5 → stock descontado → cerrar sesión.

[Registro de tiempos](evidencias/s14-estabilizacion/recorridos-manuales.json). Evidencias: [comprobante 1](evidencias/s14-estabilizacion/manual-1-comprobante.png), [stock 1](evidencias/s14-estabilizacion/manual-1-stock.png), [comprobante 2](evidencias/s14-estabilizacion/manual-2-comprobante.png), [stock 2](evidencias/s14-estabilizacion/manual-2-stock.png), [comprobante 3](evidencias/s14-estabilizacion/manual-3-comprobante.png), [stock 3](evidencias/s14-estabilizacion/manual-3-stock.png).

La primera venta se enlaza con creado_por, bitácora y requestId en [auditoría](auditoria.md). El filtro de Productos por categoría es local a la página y la pantalla lo aclara; para estos recorridos se usó orden por ID y paginación real.
