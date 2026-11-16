# Matriz de integración S14

| ID | Origen → destino | Verificación real | Resultado |
|---|---|---|---|
| I-01 | Clientes → Venta | Un cliente sintético recién registrado aparece y se selecciona en Nueva venta. | Cumple |
| I-02 | Catálogo → Venta | Producto activo con stock a precio 12.50; variantes inactiva y con stock 0 excluidas. | Cumple |
| I-03 | Venta → Catálogo | Se venden 2 unidades; al navegar a Productos sin F5 el stock pasa de 20 a 18, con la caché previamente calentada. | Cumple |
| I-04 | Venta → Reportes | El producto aparece en más vendidos con 2 unidades y monto 25.00. | Cumple |
| I-05 | Venta → Auditoría | Evento con vendedor, ID de venta y X-Request-Id de la respuesta original. | Cumple |
| I-06 | Catálogo → Auditoría | Cambiar de 12.50 a 13 registra ambos valores; modificadoPor=admin. | Cumple |
| I-07 | Seguridad → todos | El reloj controlado de la SPA avanza hasta la expiración recibida, redirige a login y retorna a la ruta de venta al autenticarse. | Cumple |
| I-08 | Paginación → filtros | En Ventas, página 5, cambiar fechas vuelve a página 1; F5 conserva los filtros. | Cumple |

8/8 filas. I-07 simula el paso del tiempo en la SPA; no espera una hora real ni afirma haber alterado el reloj del servidor. La prueba de rollback intenta una venta con una primera línea válida y una segunda inexistente: HTTP 404, stock conservado y ningún nuevo evento de venta confirmada.

Evidencias: `evidencias-s14/08-integracion.json`, `09-playwright-resumen.json` y `10-estabilidad.json`.
