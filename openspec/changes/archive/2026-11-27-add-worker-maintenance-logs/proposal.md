# Proposal

## Why

La Issue [#65](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/65), detectada al revisar la #38: el Makefile raíz genera `<servicio>-up`, `-down` y `-logs` por cada carpeta con `Makefile`, pero `worker` y `maintenance` comparten `backend/`. Las reglas genéricas ya aceptan `make worker-logs` (y `-up` y `-down`), pero `make help` no los muestra, así que nadie sabe que existen.

## What Changes

- El Makefile raíz añade `worker-logs` y `maintenance-logs`, con su `## descripción`, para que aparezcan en `make help`. Siguen el log de ese servicio de Compose, igual que `backend-logs`.
- Por el mismo motivo, y a petición de la persona en la revisión, añade también `worker-up`, `worker-down`, `maintenance-up` y `maintenance-down`.
- CONTRIBUTING §10 cita los seis objetivos junto a los objetivos por servicio.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- Ninguna: es una comodidad del entorno de desarrollo; no cambia el comportamiento del producto. Se archiva con `--skip-specs`.

## Impact

- `Makefile` y `CONTRIBUTING.md`.
- No cambia Compose, el CI, el código, OpenAPI ni el contrato API. No aplica ningún requisito del PRD.
