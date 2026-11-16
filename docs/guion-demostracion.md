# Guion de demostración - 10 minutos

| Tiempo | Bloque | Qué hacer y explicar |
|---|---|---|
| 0:00–1:00 | Contexto | Mostrar [arquitectura](arquitectura.png). La botica necesita controlar ventas y stock. Vendedor vende, almacén gestiona catálogo y admin consulta auditoría. Angular llama a Spring; Oracle conserva datos y Redis acelera lecturas. |
| 1:00–4:30 | Flujo principal | Entrar como vendedor. Buscar el cliente preparado y el producto con stock 20. Vender una unidad, revisar total, confirmar y mostrar comprobante. Ir a Productos sin F5 y comprobar stock 19. El precio definitivo lo calcula el servidor. |
| 4:30–6:00 | Seguridad | Mostrar menú del vendedor sin Auditoría. Abrir `/auditoria`: acceso denegado. Mostrar E2E-14 para 401 y aviso de sesión expirada y caso Postman 12 para 403. Explicar que ocultar un enlace no reemplaza la autorización del backend. |
| 6:00–7:30 | Volumen y rendimiento | Abrir Productos, mostrar más de 5 000 registros, solo 20 filas y página en URL. Cambiar página y recargar. Mostrar clave/TTL Redis y health UP; métricas solo admin. |
| 7:30–8:30 | Auditoría | Entrar como admin, filtrar VENTA_REGISTRADA y vendedor. Comparar ID de venta, creado_por, evento y requestId del log. Explicar AFTER_COMMIT. |
| 8:30–10:00 | Calidad | Lanzar la suite preparada o mostrar el informe HTML si tarda más de lo previsto. Mostrar 14 casos, 3 repeticiones sin reintentos, colección Postman e incidencias cerradas. Cerrar con la comprobación de stock y trazabilidad. |

No leer contraseñas en voz alta ni mostrarlas en pantalla. Prepararlas localmente antes. Para los pasos de seguridad no alterar una sesión de venta con datos reales.

## Qué puedes decir

**Contexto:** «PharmaSoft ayuda a la botica a registrar ventas y mantener el stock. El vendedor atiende, almacén gestiona productos y el administrador revisa permisos y auditoría. Esta lámina muestra Angular, Spring Boot, Oracle y Redis».

**Flujo principal:** «Entro como vendedor, selecciono el cliente y busco un producto disponible. Reviso cantidad y total antes de confirmar. El servidor calcula el precio definitivo. Aquí está el comprobante; ahora voy a Productos y compruebo que el stock bajó una unidad sin recargar toda la aplicación».

**Seguridad:** «El vendedor no tiene la opción Auditoría. Escribir la URL tampoco le permite entrar. Además, la API comprueba el permiso y responde 403. Si la sesión deja de ser válida responde 401 y la aplicación vuelve al login con un aviso».

**Volumen:** «Hay más de cinco mil productos, pero recibo solo veinte por página. La página queda en la URL y no se pierde con F5. Redis guarda lecturas por un tiempo; al vender se invalida el catálogo porque cambió el stock. Actuator permite revisar la salud del servicio».

**Auditoría:** «Esta es la venta que acabo de registrar. El autor está en creado_por y hay un evento en la bitácora. Su requestId coincide con el log. El evento se escribe después del commit para no registrar un éxito si la transacción falla».

**Calidad:** «La suite tiene catorce pruebas y pasó tres repeticiones: cuarenta y dos ejecuciones sin reintentos. Postman también comprueba errores y permisos. Aquí están las incidencias, sus causas, los cambios y las pruebas que evitan repetirlas».

Estas frases son una base para practicar: adáptalas y explica lo que estés mostrando, sin memorizar afirmaciones que no puedas defender.

## Cómo hacer los dos ensayos

1. Abre `checklist-demo.md` y comprueba servicios y claves. Usa solo el cliente/producto de demostración; deja stock 20 antes de cada ensayo con una actualización como admin, sin borrar ventas anteriores.
2. Abre cuatro pestañas: SPA `http://localhost:8081`, auditoría para admin, informe Playwright y este guion. Ten lista la evidencia del log y la colección de Postman.
3. En una PowerShell del frontend, prepara las claves de pruebas localmente y el comando `npx.cmd playwright test --reporter=list,html`. El bloque de calidad dura 1:30; si no termina, muestra el reporte anterior indicando su fecha.
4. Inicia un cronómetro en 0:00 y sigue los seis bloques. Habla y haz los clics; no pauses el cronómetro cuando te equivoques. Cambia al siguiente bloque a la hora indicada.
5. Anota la fecha, duración real y un ajuste concreto: por ejemplo «tardé buscando el producto; lo dejaré preparado». Repite desde una sesión cerrada y stock preparado. Completa las dos filas de la tabla inferior.
6. Para tu video personal, graba la pantalla con la herramienta habitual de Windows, sin mostrar contraseñas. Comprueba que dure como máximo diez minutos y que se lean comprobante, stock y auditoría. Conserva el video técnico suministrado como respaldo.

## Ensayos personales

Los recorridos por interfaz del asistente están documentados en [verificación del flujo](verificacion-flujo.md); no son ensayos orales del estudiante. Practica este guion completo dos veces y registra tiempos reales:

| Ensayo del estudiante | Fecha | Duración | Ajuste necesario |
|---|---|---|---|
| 1 | Pendiente de realizar | — | Reservar 1:30 para calidad |
| 2 | Pendiente de realizar | — | Explicar sin leer el documento |

El [video de respaldo](evidencias/s14-estabilizacion/demo-respaldo.mp4) es un recorrido técnico automatizado y rotulado; no representa una sustentación personal. Consulta su duración y bloques en [registro](evidencias/s14-estabilizacion/video.json).
