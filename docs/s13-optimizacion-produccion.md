# S13 - Optimización y producción

## Paso 6 - Preparación de Redis

- Captura recibida: Redis 7 Alpine creado como pharma-redis; redis-cli ping responde PONG.
- Se añadieron los starters de Cache, Redis y Actuator, gestionados por Spring Boot.
- Conexión configurable mediante REDIS_HOST y REDIS_PORT; valores locales localhost:6379.
- Tiempo de conexión y comandos: 500 ms. TTL: 10 minutos. Estadísticas habilitadas.
- Cachés declaradas: categorias y productos.
- CacheConfig activa @EnableCaching y registra advertencias sin propagar los fallos de lectura, escritura o invalidación de caché.
- CategoriaResponseDTO, ProductoResponseDTO y PaginaResponseDTO implementan Serializable.
- Actuator queda preparado con health, info y metrics; sus reglas específicas de seguridad corresponden al paso 8 y aún están pendientes.
- Verificación: Maven compile con Java 21 terminó con BUILD SUCCESS. No se ejecutaron pruebas de integración ni se verificó todavía la conexión desde el backend reiniciado.

## Paso 7 - Caché en los servicios

- Categorías: listado con clave todas; detalle con clave id-{id}; crear y eliminar invalidan categorías, actualizar invalida categorías y productos.
- Productos: listado completo con clave todas, detalle con clave id-{id}, listado paginado con clave que incluye página, tamaño y orden completo de Pageable. Crear, actualizar y dar de baja invalidan productos.
- Registrar y anular ventas invalidan productos.
- El listado de categorías registra Inicio/Fin y duracionMs solo cuando el proxy ejecuta el método. Un acierto de caché evita tanto ese log como el SELECT de categorías.
- Se usan referencias de parámetros #p0 para evitar depender del nombre del parámetro conservado por el compilador.

### Prueba manual pendiente tras reiniciar el backend con estos cambios

1. Iniciar sesión y autorizar Swagger. Limpiar Network y la consola del backend.
2. Ejecutar GET /api/v1/categorias dos veces consecutivas.
3. Ambas peticiones deben responder HTTP 200. La primera debe ejecutar el SELECT de categorías; la segunda no. Las consultas de autenticación pueden continuar apareciendo y no se cuentan como SELECT de categorías.
4. Ejecutar en PowerShell:

```powershell
docker exec pharma-redis redis-cli EXISTS "categorias::todas"
docker exec pharma-redis redis-cli TTL "categorias::todas"
```

EXISTS debe devolver 1; TTL debe devolver un número positivo de segundos, próximo a 600 si se consulta inmediatamente después de la primera carga.

Evidencia recibida tras reiniciar el proceso actualizado: EXISTS categorias::todas devuelve 1 y TTL devuelve 572 segundos. Queda confirmada la escritura de esa clave en Redis con expiración. La captura por sí sola no comprueba un acierto posterior ni la invalidación por escrituras.

Capturas posteriores: GET de categorías con HTTP 200 y consola compartida tras limpiar y repetir la consulta. En el área visible de la consola solo aparecen consultas de roles y empleados, sin SELECT de categorías ni Inicio listar categorias; es consistente con un acierto de caché. La captura no muestra el historial completo de la consola. Falta registrar la duración de esta petición e invalidación tras una escritura.

5. Capturar la consola con un único SELECT de categorías, ambas solicitudes HTTP 200, el tiempo del segundo GET y los resultados de Redis.
6. Comprobar después la invalidación al crear categoría, actualizar producto y registrar venta, según la guía. Estas verificaciones aún están pendientes.

Capturas de invalidación recibidas: el usuario indica haber creado una categoría; EXISTS categorias::todas devuelve 0 antes de listar y 1 después del GET. Confirma la eliminación y repoblación de la clave en ese flujo. Queda pendiente la evidencia de la categoría nueva en la respuesta, la actualización de productos y el stock tras venta.

## Paso 8 - Identificador de petición y monitoreo

- RequestIdFilter se ejecuta antes de Spring Security, genera un identificador de 8 caracteres, lo guarda en MDC y devuelve X-Request-Id. Registra método, ruta sin query, estado y duración; omite el log de acceso de Actuator y restaura el contexto al terminar.
- Desarrollo usa org.hibernate.SQL DEBUG con show-sql false para incluir el identificador en las líneas SQL.
- Producción guarda logs/pharma-backend.log con rotación de 10 MB e historial 14; SQL y parámetros JDBC desactivados. logs/ queda ignorado en Git.
- /actuator/health y sus subrutas son públicos. Las demás rutas de Actuator requieren USUARIOS_ADMINISTRAR.
- Se expone X-Request-Id en CORS junto a Location.
- Verificación automática: RequestIdFilterTest, 2 pruebas aprobadas, sin errores. Comprueban coincidencia entre cabecera y MDC, limpieza del contexto y restauración incluso ante una excepción. Maven finalizó BUILD SUCCESS.
- Pendiente tras reiniciar: verificar health público UP, coincidencia de ID entre respuesta y consola, métricas con admin y 403 con vendedor; verificar logs del perfil prod durante el paso 10.

Evidencias recibidas del paso 8:

- /actuator/health abierto en una pestaña devuelve status UP y grupos liveness/readiness.
- GET /api/v1/categorias responde HTTP 200 con X-Request-Id: 3a60b0b5.
- La consola muestra [3a60b0b5] en org.hibernate.SQL y en RequestIdFilter: GET /api/v1/categorias -> 200 (687 ms). Se confirma la correlación de la respuesta con las líneas de log de esa petición.
- Los 687 ms son duración del servidor de esa petición concreta; no se usan como reemplazo del tiempo de la segunda consulta de la comparación antes/después.
- Pendientes: métricas autorizadas con admin, 403 con vendedor y comprobación de los archivos de log en producción.

Capturas de métricas recibidas: /actuator/metrics/http.server.requests devuelve HTTP 200 con token admin y mediciones COUNT, TOTAL_TIME y MAX; la misma ruta devuelve HTTP 403 con token vendedor. Quedan verificados ambos permisos en ejecución. Los archivos de log en prod siguen pendientes del paso 10.

## Cierre de ejecución - 5 de noviembre, 11:20

Se restauró Oracle tras el reinicio y se levantaron Redis y Nginx con Compose. nginx -t confirmó la configuración. El backend se empaquetó y arrancó en perfil prod con salud UP y clave JWT nueva en .local, excluida de Git.

tools/s13_verify.py ejecutó 19 comprobaciones contra servicios reales; todas aprobaron. Incluyen aciertos Redis, invalidación de categoría y nombre cruzado de producto, venta de una unidad de un producto nuevo S13 (stock 5 a 4), caída/restauración de Redis, health DOWN/UP, métricas admin/vendedor, correlación de logs, ausencia de secretos, cabeceras de caché, gzip, fallback de /productos y proxy API. Las pruebas con escrituras y detención de Redis fueron autorizadas explícitamente por el usuario.

Resultados completos: ../pharma-frontend/docs/evidencias-s13/verificacion-api.json. Informe: ../pharma-frontend/output/pdf/Suarez_LP2_S13_Practica.pdf. Quedan pendientes la captura transitoria de carga, ausencia de descarga JS para vendedor y medición de bytes del navegador tras F5; el informe lo indica.
