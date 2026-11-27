# Tasks

## 1. Recordar make e2e en la plantilla de PR y en la skill (docs) · #90

**Criterios de aceptación:**

- La «Validación» de la plantilla de PR incluye una casilla de la prueba E2E (`make e2e`), solo para la sección de integración.
- La skill `pull-requests` incluye el paso de ejecutar `make e2e` en la sección de integración antes de publicar.

**Requisitos:** ninguno del PRD; es una regla del flujo de trabajo.

**Depende de:** —

- [ ] 1.1 Añadir la casilla E2E a la «Validación» de la plantilla de PR.
- [ ] 1.2 Añadir a la skill `pull-requests` el paso de `make e2e` en la sección de integración, con enlace a CONTRIBUTING §8; verificar que el enlace resuelve.
- [ ] 1.3 Ejecutar `openspec validate remind-e2e-in-pr --strict` y `git diff --check`.
