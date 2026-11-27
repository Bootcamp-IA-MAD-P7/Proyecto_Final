# Tasks

## 1. Documentar cuándo se ejecuta la prueba E2E (docs) · #64

**Criterios de aceptación:**

- CONTRIBUTING cita `make e2e-install` y `make e2e` contra `make up`, y enlaza al README para el detalle.
- CONTRIBUTING dice que la prueba E2E no corre en el CI y que la sección de integración de cada cambio la ejecuta antes de abrir su PR, con el resultado en la «Validación» del PR.
- Los objetivos generales de CONTRIBUTING §10 incluyen `e2e-install` y `e2e`.

**Requisitos:** ninguno del PRD; es una regla del flujo de trabajo.

**Depende de:** —

- [x] 1.1 Añadir a CONTRIBUTING §8 la regla de la prueba E2E y a §10 sus objetivos; verificar que los enlaces al README y a WORKFLOW resuelven.
- [x] 1.2 Ejecutar `openspec validate document-e2e-run --strict` y `git diff --check`.
