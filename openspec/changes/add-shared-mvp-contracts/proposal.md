# Proposal

## Why

API, inferencia e interfaz necesitan un vocabulario común antes del desarrollo paralelo de tres personas. Esta propuesta delimita el comportamiento observable de las interfaces del MVP RF-01 a RF-05 sin implementar todavía sus productores o consumidores.

## What Changes

- Proponer contrato compartido 0.1.0: identidades, estados, resultados, errores, acceso y versionado.
- Acordar endpoints y ejemplos sintéticos para recepción, consulta, corrección y aprobación.
- Especificar invariantes verificables de intercambio; los algoritmos, persistencia y despliegue se planificarán en cambios posteriores.
- Reservar decisiones abiertas de publicación y consentimiento sin convertirlas en hechos aprobados. Las 24 horas siguen siendo provisionales.
- Excluir RF-06, RF-07, reconocimiento entre sesiones, tiempo real y ejecución de modelos.

## Capabilities

### New Capabilities

- `mvp-service-contracts`: interoperabilidad entre los consumidores y productores del servicio, incluyendo acceso y representación de trabajos/resultados.

### Modified Capabilities

Ninguna; no existen specs previas.

## Impact

Referencias: [PRD](../../../docs/PRD.md) RF-01 a RF-05, RNF-01, RNF-02, RNF-03, RNF-05 y RD-04/RD-06; [arquitectura](../../../docs/ARCHITECTURE.md); ADR-0001 a ADR-0004, todos Propuestos.

Épica e Issue: pendientes de definir, sin inventar número ni crear Issues en este encargo. El ROADMAP aún es plantilla y la aprobación de fase 1 no consta cerrada. Este borrador anticipado está autorizado para revisión, no declara historias ready.

En este turno se crean solo artefactos dentro del cambio. En la ejecución autorizada de la historia de contrato se registrarán OpenAPI/JSON Schema, ejemplos y documentación normativa en docs/CONTRACTS conforme a su índice; no se modifican ahora PRD, arquitectura ni ADR.

Las cinco specs funcionales posteriores y su orden están identificados en design.md. Este cambio no pretende entregar el MVP ejecutable ni sustituir el walking skeleton exigido por WORKFLOW.
