# S14 - Publicación preparada

Rama en ambos repositorios: `feature/integracion-estabilizacion-suarez`. Destino de ambos PR: `develop`.

La publicación no se ejecutó: la revisión automática bloqueó la lectura y uso de la credencial de GitHub guardada. Es necesaria autorización explícita para usar esa credencial, publicar las dos ramas y crear ambos PR. No se fusionarán los PR.

## Backend

Título: **S14: auditoría, paginación y estabilización del backend**

Descripción preparada:

La API limita la paginación a 100 filas y agrega una búsqueda de productos activos con stock. Flyway aplica V4 con columnas de autoría, bitácora e índices. Los eventos de negocio se registran después del commit; el login fallido conserva su propio evento. La consulta de auditoría está restringida a USUARIOS_ADMINISTRAR.

Validación: 23 pruebas Maven aprobadas; matriz de integración 8/8; rollback real sin evento falso; siete pruebas Playwright aprobadas tres veces con el frontend. Evidencias, incidencias y PDF incluidos. Baseline 2 corresponde al esquema legado que ya contenía V2; V4 quedó registrada con success=1.

## Frontend

Título: **S14: paginación en URL, auditoría y pruebas E2E**

Descripción preparada:

Productos y Ventas comparten un paginador y conservan página, tamaño, orden y filtros en la URL. Nueva venta busca productos en el servidor y excluye inactivos o agotados. Se agregó la consulta protegida de auditoría y se conserva la autoría en DTO/modelos.

Validación: compilación de producción correcta; 21/21 ejecuciones Playwright, un trabajador y cero reintentos; npm sin vulnerabilidades tras los parches compatibles de Angular 22. Se mantiene el aviso CSS anterior de 57 bytes en venta-form.css.

## Comandos para publicar tras la autorización

```powershell
cd C:\Users\jatni\Downloads\pharmaSoft-main
git push -u origin feature/integracion-estabilizacion-suarez
cd C:\Users\jatni\Downloads\pharma-frontend
git push -u origin feature/integracion-estabilizacion-suarez
```

Después crear en cada repositorio un PR con base `develop` y compare `feature/integracion-estabilizacion-suarez`, usando las descripciones anteriores.

Backend: https://github.com/JanislyIsa/pharmaSoft
Frontend: https://github.com/JanislyIsa/pharma-frontend
