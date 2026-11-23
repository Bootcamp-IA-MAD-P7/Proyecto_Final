# Architecture Decision Records

> El porqué de las decisiones técnicas significativas. [ARCHITECTURE](../ARCHITECTURE.md) describe el resultado y enlaza aquí.

## Cuándo escribir un ADR

- Al elegir o cambiar una tecnología, un proveedor o un patrón estructural.
- Ante una decisión difícil de revertir o que afecta a varios componentes.
- Al descartar una alternativa razonable que alguien podría volver a proponer.

Para decisiones locales y reversibles basta con el `design.md` del cambio de OpenSpec.

## Formato

- Archivo `NNNN-titulo-en-kebab-case.md`, creado a partir de [`0000-template.md`](0000-template.md) y numerado de forma correlativa.
- Estados: Propuesto → Aceptado → Reemplazado por ADR-NNNN u Obsoleto.
- Un ADR aceptado no se reescribe: se reemplaza por otro.

## Índice

| ADR | Título | Estado |
|---|---|---|
| [ADR-0001](0001-modular-backend.md) | Modular backend and API-first demo | Propuesto |
| [ADR-0002](0002-durable-jobs.md) | Durable jobs in PostgreSQL | Propuesto |
| [ADR-0003](0003-private-inference.md) | Private staged inference | Propuesto |
| [ADR-0004](0004-access-and-retention.md) | Private storage and controlled publication | Propuesto |
