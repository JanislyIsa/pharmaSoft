# Unidad I - backend

Capturas originales recuperadas sin editar de los documentos del estudiante: informe técnico de agosto de 2026, evidencias S04 (06/09/2026) y S05 (10/09/2026). Son evidencia histórica, no capturas nuevas del 15/11.

- [Agosto-02.png](Agosto-02.png): Tabla CATEGORIAS en Oracle, informe de agosto de 2026.
- [Agosto-03.jpg](Agosto-03.jpg): Swagger con endpoints de Categoría y Health, informe de agosto.
- [Agosto-05.jpg](Agosto-05.jpg): Respuesta de creación de categoría, informe de agosto.
- [S04-07.png](S04-07.png): Figura 4. Respuesta 400 Bad Request: "La venta debe contener al menos un detalle".
- [S04-14.png](S04-14.png): Figura 11. Respuesta 409 Conflict: "Stock insuficiente para Azitromicina 250mg. Disponible: 38, solicitado: 9999".
- [S04-17.png](S04-17.png): Figura 14. Respuesta 201 Created: venta id 21, total 84, subtotales 54 y 30 respectivamente.
- [S04-20.png](S04-20.png): Figura 17. Stock antes: Producto 21 = 57 (ya se había descontado 3 unidades en la Prueba 5), Producto 22 = 38.
- [S04-22.png](S04-22.png): Figura 19. Respuesta 409 Conflict: "Stock insuficiente para Azitromicina 250mg. Disponible: 38, solicitado: 1000".
- [S04-23.png](S04-23.png): Figura 20. Stock después: Producto 21 sigue en 57 y Producto 22 sigue en 38. No hubo cambios.
- [S05-01.png](S05-01.png): Figura 1. Lista de endpoints del venta-controller, incluyendo /buscar y /{id}/anular.
- [S05-14.png](S05-14.png): Figura 8. Reporte ventas-por-categoria antes de anular: Antibioticos 5 u. / S/88.50, Vitaminas 4 u. / S/65.00.
- [S05-18.png](S05-18.png): Figura 11. Reporte ventas-por-categoria después de anular la venta 43.
- [S05-23.png](S05-23.png): Figura 15. Log del reporte productos-mas-vendidos ejecutado después de anular (filas=3, duracionMs=6).

[Procedencia y hashes de originales](procedencia.json). Los Word originales se conservan en Descargas; no se publican porque incluyen configuración local. [Validación actual del 15/11](validacion-actual-api.png) se mantiene separada de la evidencia histórica.
