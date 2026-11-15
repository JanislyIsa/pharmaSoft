# Auditoría

La bitácora permite saber quién hizo un cambio importante, cuándo y mediante qué solicitud. Solo la consulta quien tiene `USUARIOS_ADMINISTRAR`: el backend lo exige y la SPA usa `permisoGuard` y oculta la opción del menú.

`/auditoria` tiene fecha, usuario, acción, entidad, ID, detalle y requestId. Los filtros usuario/acción/desde/hasta y la página están en la URL; el paginador es el mismo de Productos y Ventas. Hasta incluye todo el día. Tamaño permitido: 1 a 100.

| Acción | Cuándo | Detalle guardado |
|---|---|---|
| LOGIN_EXITOSO | Autenticación correcta | Sin contraseña ni token |
| LOGIN_FALLIDO | Credenciales rechazadas | Sin contraseña ni causa que revele secretos |
| VENTA_REGISTRADA | Venta confirmada | Total y número de líneas |
| PRECIO_MODIFICADO | Cambia el precio | Precio anterior y nuevo |
| PRODUCTO_ELIMINADO | Baja lógica | Nombre del producto; ID en entidad_id |
| CLIENTE_REGISTRADO | Alta confirmada, nuevo en autónoma | Estado; sin DNI, correo ni dirección |
| VENTA_ANULADA | Cambio a ANULADA, nuevo en autónoma | Estado y total; sin datos del cliente |

Las columnas `creado_por` y `modificado_por` indican el autor del registro y de su última modificación. La bitácora conserva acontecimientos. El log sirve para diagnóstico técnico y duración; `requestId` conecta respuesta, evento y log.

Los servicios publican eventos dentro de `@Transactional`. `AuditoriaListener` escucha con `AFTER_COMMIT`: si hay rollback, no registra un éxito inexistente. La escritura usa otra transacción `REQUIRES_NEW`. El login fallido se registra directamente en una transacción propia porque el rechazo de autenticación no confirma una transacción de negocio. Si la escritura de bitácora falla después de confirmar, se registra el error técnico; no se deshace ni se informa como fallida una venta ya confirmada. Limitación: no hay outbox ni reintento durable para esa caída.

Nunca se guardan contraseñas, JWT, cabeceras Authorization, hashes de contraseña, datos de pago ni cuerpos completos de las solicitudes. Los detalles nuevos tampoco copian datos personales del cliente.

## Venta trazada

Se usa la primera venta del recorrido manual del 15/11/2026. Véanse [fila de ventas y bitácora](evidencias/s14-estabilizacion/trazabilidad-bd.png), [log correlacionado](evidencias/s14-estabilizacion/trazabilidad-log.png), [comprobante](evidencias/s14-estabilizacion/manual-1-comprobante.png) y [datos originales de la consulta](evidencias/s14-estabilizacion/trazabilidad.json). Las imágenes de BD y log son una representación legible de salidas reales, no una captura de SQL Developer.

Código: `src/main/java/pe/edu/pe/PharmaBackend/auditoria/`, `service/impl/AuditoriaServiceImpl.java`, `service/impl/ClienteServiceImpl.java`, `service/impl/VentaServiceImpl.java`, `config/SecurityConfig.java`. En frontend: `src/app/features/auditoria/auditoria.ts` y `app.routes.ts`.

Contrato de anulación conservado: cambia el estado y registra el evento; no equivale a una devolución de inventario. No se modificó esa regla para esta actividad.
