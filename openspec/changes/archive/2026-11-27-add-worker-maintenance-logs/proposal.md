# Proposal

## Why

La Issue [#65](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/65), detectada al revisar la #38: el Makefile raíz genera `<servicio>-up`, `-down` y `-logs` por cada carpeta con `Makefile`, pero `worker` y `maintenance` comparten `backend/`. La regla genérica `%-logs` ya acepta `make worker-logs`, pero `make help` no lo muestra, así que nadie sabe que existe.

## What Changes

- El Makefile raíz añade `worker-logs` y `maintenance-logs`, con su `## descripción`, para que aparezcan en `make help`. Siguen el log de ese servicio de Compose, igual que `backend-logs`.
- CONTRIBUTING §10 cita los dos objetivos junto a los objetivos por servicio.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- Ninguna: es una comodidad del entorno de desarrollo; no cambia el comportamiento del producto. Se archiva con `--skip-specs`.

## Impact

- `Makefile` y `CONTRIBUTING.md`.
- No cambia Compose, el CI, el código, OpenAPI ni el contrato API. No aplica ningún requisito del PRD.
