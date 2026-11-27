# Proposal

## Why

La Issue [#64](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/64), detectada al revisar la #38: la prueba de extremo a extremo (`make e2e`) existe desde el walking skeleton y el README explica cómo lanzarla, pero CONTRIBUTING no dice cuándo es obligatoria. Como no corre en el CI, nada garantiza que la sección de integración de un cambio la ejecute antes de su PR.

## What Changes

- CONTRIBUTING §8 (Calidad y CI) explica que la prueba E2E no corre en el CI, y que la sección de integración de cada cambio ejecuta `make e2e` contra `make up` (con `make e2e-install` una vez por equipo) antes de abrir su PR y anota el resultado en la «Validación» del PR.
- CONTRIBUTING §10 (Makefile) añade `e2e-install` y `e2e` a los objetivos generales.
- El README sigue siendo el dueño del «cómo» (modelos, audio sintético, puertos); CONTRIBUTING enlaza a él en lugar de repetirlo.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- Ninguna: solo documenta una regla del flujo de trabajo; no cambia el comportamiento del producto. Se archiva con `--skip-specs`.

## Impact

- Documentación: `CONTRIBUTING.md`.
- No cambia el Makefile, el CI, el código, OpenAPI ni el contrato API. No aplica ningún requisito del PRD (es una regla de proceso).
