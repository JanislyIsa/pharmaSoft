# Contrato de auditoría S14

`GET /api/v1/auditoria` exige `Authorization: Bearer <JWT>` y permiso `USUARIOS_ADMINISTRAR`.
Filtros opcionales: usuario (exacto, sin distinguir mayúsculas), accion (exacta), desde y hasta (ISO yyyy-MM-dd, hasta inclusive).
Paginación base 0: pagina=0, tamanio=20 por defecto; tamaño entre 1 y 100. Orden estable fecha DESC, id DESC.

Respuesta 200: PaginaResponseDTO, con contenido de {id,fecha,usuario,accion,entidad,entidadId,detalle,requestId}.
401: falta sesión válida. 403: falta permiso. 409: página/tamaño o rango de fechas inválidos. 400: formato de fecha inválido.
Acciones: LOGIN_EXITOSO, LOGIN_FALLIDO, VENTA_REGISTRADA, PRECIO_MODIFICADO, PRODUCTO_ELIMINADO.
La baja es lógica. Una venta revertida no publica un evento confirmado. La bitácora no incluye contraseñas ni tokens.

`GET /api/v1/productos/buscar?texto=...` exige CATALOGO_LEER. Devuelve hasta 20 productos activos con stock positivo cuyo nombre contiene el texto (máximo 150 caracteres), ordenados por nombre e ID. Respuesta PaginaResponseDTO.
