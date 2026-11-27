# Tasks

## 1. Logs de worker y maintenance con make (enhancement) · #65

**Criterios de aceptación:**

- `make worker-logs` y `make maintenance-logs` siguen el log de su servicio en Docker.
- Los dos aparecen en `make help`.
- `make worker-up`, `worker-down`, `maintenance-up` y `maintenance-down` levantan o paran solo ese servicio y también aparecen en `make help`.
- CONTRIBUTING §10 los cita.

**Requisitos:** ninguno del PRD; es una comodidad del entorno de desarrollo.

**Depende de:** —

- [x] 1.1 Añadir `worker-logs` y `maintenance-logs` al Makefile raíz con su `## descripción` y comprobar que salen en `make help`.
- [x] 1.2 Citar los objetivos en CONTRIBUTING §10.
- [x] 1.4 Añadir `worker-up`, `worker-down`, `maintenance-up` y `maintenance-down` con su `## descripción`.
- [x] 1.3 Ejecutar `openspec validate add-worker-maintenance-logs --strict`, `make -n worker-logs maintenance-logs` y `git diff --check`.
