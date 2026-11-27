# Proposal

## Why

La Issue [#90](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/90), propuesta por el reviewer de la #64: CONTRIBUTING §8 ya dice que la sección de integración de cada cambio ejecuta `make e2e` en local antes de abrir su PR, pero la regla solo está ahí. Quien prepara el PR sigue la plantilla y la skill `pull-requests`, que no la recuerdan.

## What Changes

- La plantilla de PR (`.github/pull_request_template.md`) añade a «Validación» una casilla de la prueba E2E (`make e2e`), solo para la sección de integración.
- La skill `pull-requests` añade al paso «Publicar» ejecutar `make up` y `make e2e` en la sección de integración, enlazando a CONTRIBUTING §8.
- CONTRIBUTING sigue siendo el dueño de la regla; la plantilla y la skill solo la recuerdan y enlazan a ella.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- Ninguna: solo recuerda una regla del flujo de trabajo; no cambia el comportamiento del producto. Se archiva con `--skip-specs`.

## Impact

- Documentación: `.github/pull_request_template.md` y `.agents/skills/pull-requests/SKILL.md`.
- No cambia el Makefile, el CI, el código, OpenAPI ni el contrato API. No aplica ningún requisito del PRD (es una regla de proceso).
