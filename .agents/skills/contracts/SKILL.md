---
name: contracts
description: Cómo registrar, cambiar y versionar un contrato entre componentes (API, eventos, esquemas o formatos de archivo) en docs/CONTRACTS. Úsala en la historia de contrato o cuando cambie una interfaz de la que depende otro componente.
---

# Contratos

Reglas y formato en [`docs/CONTRACTS/README.md`](../../../docs/CONTRACTS/README.md); el papel del contrato en el trabajo por capas, en [WORKFLOW §5](../../../WORKFLOW.md#trabajo-por-capas). Esta skill es el procedimiento.

## Registrar un contrato nuevo

1. **Comprueba que hace falta:** otro componente o un sistema externo depende de la interfaz. Si solo cambia dentro de un mismo cambio de OpenSpec, basta con su `design.md`.
2. **Artefacto ejecutable primero**, si el stack lo permite (OpenAPI, JSON Schema…): ese archivo es la fuente de verdad y vive junto al servicio productor.
3. **Crea** `docs/CONTRACTS/<contract-name>.md` (en inglés y kebab-case) a partir de `_template.md`. Si hay artefacto ejecutable, enlázalo y explica solo lo que el artefacto no cuenta; no copies sus campos.
4. **Estado y versión:** `Propuesto`, versión `0.1.0`, productor y consumidores.
5. **Índice:** añade la fila en `docs/CONTRACTS/README.md`.
6. **Enlaces:** desde ARCHITECTURE §5 (el flujo que lo usa) y desde las specs que lo citan. Las specs describen comportamiento y enlazan el contrato.
7. **Mocks:** si la capa consumidora va a avanzar en paralelo, deja preparado un ejemplo de respuesta o un mock a partir del contrato.

## Cambiar un contrato

1. **Clasifica el cambio:**
   - compatible (campo opcional nuevo, nuevo código de error documentado…): sube MINOR;
   - incompatible (campo eliminado o renombrado, cambio de tipo o de significado): sube MAJOR y exige un ADR (skill `adr`) o una nota de migración en «Compatibilidad».
2. Actualiza el artefacto ejecutable, el `.md`, la versión y el índice en el mismo commit.
3. Avisa en el PR de qué consumidores se ven afectados. Si el cambio es incompatible, el commit lleva `!` y `BREAKING CHANGE:` (skill `commits`).
