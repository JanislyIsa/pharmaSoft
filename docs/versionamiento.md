# Versión de demostración

Historial real, sin modificar fechas:

| Repositorio | 12/11/2026 | 13/11/2026 | 15/11/2026 |
|---|---|---|---|
| Backend | a3c5103 chore(s14): integra base S13 | 9ec8c49 feat(auditoria): V4 y eventos | 953f7cf feat(auditoria): alta y anulación |
| Frontend | 1414d3a chore(s14): integra base S13 | 1920d4e feat(spa): paginación y auditoría | 59844af test(s14): catorce casos |

Son tres días distintos por repositorio, con mensajes de Conventional Commits; el historial incluye además fix, test y docs. Los commits del 15/11 que agregan evidencia no cambian el comportamiento probado.

La etiqueta anotada `v1.0-demo` identifica la entrega completa de cada repositorio. No se reemplazó ninguna etiqueta preexistente. Los enlaces del PDF apuntan a esa versión. Las ramas y PR de integración se mantienen para revisión; no se fusionaron automáticamente.

Validación funcional: backend `953f7cf`; frontend `5809bc4` (incluye la corrección de accesibilidad posterior a los catorce casos). Resultado: 42/42, más 14/14 en vivo durante el video. Documentación y video se agregaron en commits posteriores.
