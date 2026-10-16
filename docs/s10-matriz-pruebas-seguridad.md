# Matriz de pruebas de seguridad — PharmaBackend

Usa Swagger o Postman. Para endpoints protegidos, envía `Authorization: Bearer <token>`. El login es `POST /api/v1/auth/login`.

| # | Usuario/condición | Petición | Resultado esperado |
|---|---|---|---|
| 1 | Sin token | `GET /api/health` | 200, ruta pública |
| 2 | Sin token | `GET /api/v1/productos` | 401, debe iniciar sesión |
| 3 | Clave equivocada | Login `admin` | 401, mensaje genérico |
| 4 | Usuario inactivo | Login `inactivo` | 401, mismo mensaje genérico |
| 5 | Username vacío | Login | 400, error de validación |
| 6 | Vendedor | Login correcto | 200, token y permisos de vendedor |
| 7 | Vendedor | Revisar payload JWT | `sub`, `authorities`, `iat`, `exp`; duración 3600 s |
| 8 | Vendedor | `GET /api/v1/auth/me` | 200, datos del usuario sin contraseña |
| 9 | Vendedor | `GET /api/v1/productos` | 200 |
| 10 | Vendedor | `DELETE /api/v1/productos/1` | 403 |
| 11 | Vendedor | `POST /api/v1/ventas` con una venta válida | 201 |
| 12 | Vendedor | `GET /api/v1/reportes/ventas-por-categoria` | 403 por permiso de reporte |
| 13 | Almacenero | `POST /api/v1/ventas` | 403 |
| 14 | Almacenero | `PUT /api/v1/productos/{id}` | 200 |
| 15 | Admin | `GET /api/v1/reportes/ventas-por-categoria` | 200 |
| 16 | Supervisor | Login correcto | 200; vendedor + almacenero y unión de permisos |
| 17 | Supervisor | Crear venta y actualizar producto | 201 y 200 |
| 18 | Supervisor | Consultar reportes | 403 |
| 19 | Admin | `GET /api/v1/empleados` y `/api/v1/roles` | 200; María aún no tiene usuario |
| 20 | Admin | Crear usuario de María | 201; respuesta sin password y hash BCrypt en BD |
| 21 | Admin | Repetir alta para el mismo empleado | 409 por relación 1 a 1 |
| 22 | Admin | Alta con `rolIds: [2, 99]` | 404 por rol inexistente |
| 23 | Vendedor | Enviar token alterado | 401 |
| 24 | Vendedor | Enviar token vencido | 401 |
| 25 | Usuario autenticado | `POST /api/v1/auth/change-password` con clave actual y nueva | 204; nueva clave se guarda con BCrypt |

Para cambiar la contraseña, el cuerpo es:

```json
{
  "contrasenaActual": "Vendedor2026*",
  "nuevaContrasena": "NuevaClave2026"
}
```

En Swagger, autoriza con el token sin escribir `Bearer`. Registra capturas de las respuestas al ejecutar la matriz.
