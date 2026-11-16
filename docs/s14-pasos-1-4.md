# S14 - Avance de los pasos 1 al 4

Jatniel Jair Suarez Vigo · 12/11/2026

## Paso 1. Crear las ramas de trabajo

Se creó `feature/integracion-estabilizacion-suarez` en backend y frontend, tomando como base `origin/develop`. Después se integró el avance de S13 para conservar las funciones que ya estaban terminadas.

Las dos carpetas locales están en esa rama. Las ramas se publicaron el 13/11/2026: backend PR #4 y frontend PR #5 hacia develop.

## Paso 2. Cargar volumen de prueba y medir la línea base

Archivo: `docs/sql/volumen_pruebas.sql`.

Se ejecutó en el esquema Oracle local de desarrollo, con el backend en perfil `dev`. Se agregaron 5000 productos y 20000 ventas sin detalle, vinculadas al cliente de prueba `Carga S14 Pruebas`. Estas ventas sirven para medir listados; no son ventas comerciales ni evidencia para validar reportes.

| Dato | Antes de cargar | Después |
|---|---:|---:|
| Productos | 15 | 5015 |
| Ventas | 29 | 20029 |

Se repitió el script: insertó 0 productos y 0 ventas. La carga no se duplicó. Se invalidaron únicamente las claves de caché de productos para medir la consulta a Oracle.

**Adaptación al proyecto:** el esquema utiliza `ID_CATEGORIA`. La columna `creado_por` todavía no existe, porque V4 corresponde al paso 5 de la guía. El script funciona con el esquema actual y rellena esa columna si existe. Se mantiene fuera de las migraciones.

### Mediciones HTTP

Bytes del cuerpo JSON, sin cabeceras ni compresión. Una petición por caso; los tiempos son una línea base local, no un promedio ni una prueba de mejora de velocidad.

| Consulta | Antes: HTTP / ms / bytes | Después: HTTP / ms / bytes |
|---|---|---|
| Productos, página 0, tamaño 20 | 200 / 247.842 / 4722 | 200 / 250.013 / 4722 |
| Productos, página 0, tamaño 100 | 200 / 81.242 / 23441 | 200 / 79.022 / 23441 |
| Productos, página 249, tamaño 20 | 200 / 61.117 / 4783 | 200 / 63.719 / 4783 |
| Productos, página 0, tamaño 500 | 200 / 100.171 / 117003 | **409 / 34.146 / 233** |
| Productos, orden desconocido | 409 / 35.338 / 220 | 409 / 17.140 / 219 |
| Ventas, del 01 al 12/11/2026, página 0 | 200 / 124.133 / 1608 | 200 / 276.455 / 3126 |
| Productos, última página real (250), tamaño 20 | 200 / 57.496 / 3588 | 200 / 57.101 / 3588 |

Ventas devolvía 10 filas por defecto y ahora devuelve 20; sus tiempos y bytes no comparan el mismo tamaño de página. La consulta del período encontró 662 ventas.

Con los 15 productos que ya existían, la página 249 de la guía no es la última. La última real es la 250 (base 0): contiene 15 filas y `ultima=true`.

Se encontró y corrigió una incidencia: el backend aceptaba `tamanio=500`. Productos y Ventas ahora aceptan tamaños de 1 a 100, rechazan páginas negativas con HTTP 409 y usan tamaño 20 por defecto. Productos añade el ID como desempate del orden para evitar resultados inestables entre páginas.

Hibernate generó `OFFSET ... FETCH FIRST ... ROWS ONLY` y la consulta `COUNT` del total. El SQL capturado está en `evidencias-s14/02-sql-paginacion.txt`.

## Paso 3. Paginar en la SPA: modelo, servicio y paginador

En el frontend:

- `src/app/core/models/pagina.ts`: expone `Pagina<T>` reutilizando el contrato existente y define `ConsultaPagina`.
- `src/app/features/productos/services/producto-service.ts`: envía página, tamaño, campo y dirección. Conserva la firma anterior para los formularios existentes.
- `src/app/shared/components/paginador/`: componente compartido por Productos y Ventas, con primera, anterior, siguiente, última y resumen de registros.

Incluye tamaños 10, 20 y 50, además de los tamaños existentes 5 y 100. Los botones se deshabilitan en los límites y durante la carga. El selector muestra el tamaño real de la respuesta.

Esto evita repetir la misma lógica en cada listado y permite recorrer el volumen cargado sin descargar todo a la vez.

## Paso 4. La lista de productos con la página en la URL

Archivos principales del frontend:

- `src/app/features/productos/pages/producto-list/producto-list.ts` y su plantilla.
- `src/app/features/ventas/pages/venta-list/venta-list.ts` y su plantilla.
- `src/app/core/utils/paginacion-url.ts` para interpretar y validar parámetros.

La página, el tamaño y el orden se leen de la URL mediante `input()`. `withComponentInputBinding()` ya estaba configurado. `rxResource` solicita la nueva página y cancela las solicitudes anteriores; `linkedSignal` conserva el resultado previo mientras llega el nuevo.

Ejemplos:

```text
/productos?pagina=1&tamanio=20&orden=nombre&dir=asc
/ventas?pagina=0&tamanio=20&estado=REGISTRADA&desde=2026-11-01&hasta=2026-11-12&orden=fecha&dir=desc
```

Cambiar tamaño, orden o filtro vuelve a `pagina=0`. Ventas guarda cliente, estado y fechas en la URL. F5 y el historial del navegador restauran esos valores. Una página fuera de rango se ajusta a la última disponible.

El filtro de categoría de Productos mantiene su comportamiento anterior: se aplica a la página actual, como indica la pantalla. Ahora también conserva su selección en la URL. No se agregó un buscador de texto; por ello no corresponde aplicar `debounceTime(300)`.

### Comprobación en pantalla

Se verificó en la SPA local:

- Productos: 20 filas iniciales, siguiente, anterior, primera y última página.
- F5 conservó la página 2 y las 20 filas seleccionadas.
- Cambiar a 50 filas y ordenar por precio reiniciaron la página.
- La última página mostró `5001–5015 de 5015`, con Siguiente deshabilitado.
- Ventas conservó estado y fechas después de F5; Atrás restauró página y tamaño.
- Se validó el rango invertido de fechas y el resultado vacío `0–0 de 0`.
- Limpiar eliminó los filtros. La consola del navegador no registró errores en estas pruebas.

Las capturas y los resultados están en `docs/evidencias-s14/`.

### Validación del código

- Maven: **19 pruebas, 0 fallos y 0 errores**; empaquetado correcto.
- Angular: compilación de producción correcta. Queda un aviso anterior: `venta-form.css` supera su presupuesto de 4 kB por 57 bytes.

Para revisar el avance: iniciar el backend con perfil `dev` y la SPA con `npm.cmd start`, abrir Productos e iniciar sesión con una cuenta existente. Las mediciones se pueden repetir con `python tools/s14_local.py measure --stage despues`; solicita la contraseña sin guardarla en las evidencias.

El siguiente paso de la guía es el **Paso 5: auditoría y migración V4**. Este documento solo acredita los pasos 1 al 4.
