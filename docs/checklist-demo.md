# Antes de demostrar

- [ ] Docker Desktop listo; `docker ps` muestra Oracle, Redis y Nginx activos.
- [ ] Oracle en localhost:1522/FREEPDB1; perfil `dev`, `ddl-auto=validate`, migración V4 correcta. No usar una base ajena a la demostración.
- [ ] `http://localhost:8080/actuator/health` devuelve UP.
- [ ] `docker exec pharma-s13-redis-1 redis-cli ping` devuelve PONG.
- [ ] Frontend: `npm.cmd ci`, `npx.cmd playwright install chromium`, `npm.cmd run build`. Nginx sirve el build en `http://localhost:8081`.
- [ ] Para repetir E2E definir `E2E_ADMIN_PASSWORD`, `E2E_VENDEDOR_PASSWORD` y `E2E_ALMACEN_PASSWORD` solo en la sesión local; ejecutar `npx.cmd playwright test --repeat-each=3`. No publicar esos valores.
- [ ] Preparar cuentas admin/vendedor/almacen con sus permisos; comprobar las claves antes, sin guardarlas en Git.
- [ ] Preparar un cliente sintético y producto con stock 20 mediante los formularios. Después de cada ensayo restablecer solo ese producto con una actualización autorizada; no vaciar la base ni borrar ventas de otros.
- [ ] Productos de carga disponibles: `docs/sql/volumen_pruebas.sql` es idempotente. No ejecutarlo contra producción.
- [ ] Cerrar sesiones y dejar pestañas listas: SPA, auditoría, health, informe Playwright, colección Postman y log con requestId.
- [ ] Comprobar [índice](README.md), PDF y reproducción del video. Descargar una copia local por si no hay Internet.
- [ ] Completar los dos ensayos orales y revisar las diez respuestas de defensa.

Plan B: mostrar comprobante, stock, BD, log y HTML ya guardados en `evidencias/s14-estabilizacion/`. Explicar cuándo se capturaron; no presentarlos como una ejecución en vivo. El video técnico no sustituye la defensa del estudiante.

Para Postman, importar `postman/PharmaBackend.postman_collection.json` desde esta carpeta docs. Crear un entorno local con `adminPassword` y `vendedorPassword` como secretos; no exportarlo. `baseUrl` apunta a localhost:8080/api/v1. La colección crea sus propios datos.
