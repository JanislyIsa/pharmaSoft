# Resultados de pruebas

Fecha: 15/11/2026. Entorno local: Oracle, Redis, backend dev :8080, Chromium y SPA. Sin mocks de la API ni base de datos. Los casos crean sus propios datos sintéticos; no borran información anterior.

## Playwright

Versiones probadas: backend `953f7cf`, frontend `5809bc4`. Comando: `npx.cmd playwright test --repeat-each=3`. Configuración: un worker, `retries: 0`, sin `waitForTimeout` en `e2e/`.

| Medida | Resultado |
|---|---:|
| Casos distintos | 14 |
| Repeticiones por caso | 3 |
| Ejecuciones / aprobadas | 42 / 42 |
| Fallidas / flaky / omitidas | 0 / 0 / 0 |
| Duración total | 75,61 s |

Casos: ruta protegida, credenciales erróneas, vencimiento y retorno; stock cambiado por otro usuario (409 y sin venta); venta vacía (400); cliente nuevo e inmediato; fechas desde página 3; auditoría admin y anulación; auditoría denegada a vendedor; token alterado (401); integración cliente-catálogo-venta-stock-reporte-auditoría con rollback; paginación persistente; permisos de almacén; catálogo de solo lectura para vendedor.

[Informe HTML](evidencias/s14-estabilizacion/playwright-report/index.html), [captura del resumen](evidencias/s14-estabilizacion/playwright-resultados.png) y [JSON sanitizado con los 42 resultados](evidencias/s14-estabilizacion/playwright-resumen.json). Para abrir HTML descargado: servir su carpeta o ejecutar `npx.cmd playwright show-report` después de la corrida local; GitHub no ejecuta HTML de reportes.

Antes de la verificación final hubo dos fallos diagnosticados: faltaba Chromium (42 errores de arranque) y el nombre accesible de Acción impedía E2E-12 (39 aprobadas, 3 fallidas). Se corrigieron las causas; no se habilitaron reintentos. Véanse INC-07, INC-08 y [diagnósticos](evidencias/s14-estabilizacion/diagnosticos.json). Las trazas con tráfico autenticado se conservan solo localmente; no se publican contraseñas o tokens.

## Postman y backend

CLI oficial Postman 1.90.0 contra localhost:8080: **18 solicitudes, 26 comprobaciones aprobadas, cero fallos**, 2,268 s. [Colección](postman/PharmaBackend.postman_collection.json), [resultados](evidencias/s14-estabilizacion/postman-resumen.json), [captura](evidencias/s14-estabilizacion/postman-resultados.png).

| Código | Caso verificado |
|---|---|
| 200 / 201 | Consulta paginada, cliente/producto nuevo, venta y auditoría |
| 400 | Venta sin productos |
| 401 | Productos sin token |
| 403 | Auditoría con vendedor |
| 404 | Producto inexistente |
| 409 | Venta mayor al stock; se conserva el stock |

También se verifica stock 3→2, total calculado en servidor, venta y evento con el mismo requestId y los dos eventos nuevos. Las claves se proporcionan como variables secretas del entorno; el informe publicado es sanitizado.

Maven: **23 pruebas, cero errores/fallos/omitidas, BUILD SUCCESS**, 16,625 s con empaquetado. [Resumen original](evidencias/s14-estabilizacion/backend-validacion.txt). El build de producción Angular terminó correctamente; conserva la advertencia previa de CSS de venta, 57 bytes sobre el presupuesto de aviso, sin impedir el build.

Tres recorridos por interfaz y su preparación: [verificación del flujo](verificacion-flujo.md). Esto demuestra los comportamientos cubiertos, no una prueba de carga concurrente intensiva ni la ausencia de cualquier error posible.
