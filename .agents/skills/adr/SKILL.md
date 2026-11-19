---
name: adr
description: Cómo decidir si una decisión técnica necesita un ADR, redactarlo, numerarlo y registrarlo en el índice, o reemplazar uno existente. Úsala al elegir o cambiar tecnología, proveedor o patrón estructural.
---

# ADR

Cuándo escribir un ADR y su formato están en [`docs/ADR/README.md`](../../../docs/ADR/README.md); esta skill es el procedimiento.

1. **Decide si hace falta.** Sí, si la decisión elige o cambia una tecnología, un proveedor o un patrón estructural, es difícil de revertir, afecta a varios componentes o descarta una alternativa razonable. Si es local y reversible, basta con el `design.md` del cambio de OpenSpec: no crees el ADR.
2. **Numera:** el siguiente número libre del índice, con cuatro cifras (`0001`, `0002`…). Nunca reutilices un número.
3. **Crea el archivo** `docs/ADR/NNNN-titulo-en-kebab-case.md` a partir de `0000-template.md`. Título y nombre de archivo en inglés; el contenido, en español.
4. **Rellénalo:** contexto, decisión, alternativas consideradas con el motivo de descarte y consecuencias (también los costes). En «Relacionado», los `RF`, la Issue y los ADR afectados.
5. **Estado `Propuesto`.** ⏸ Solo la persona lo acepta; entonces pasa a `Aceptado` con la fecha.
6. **Índice:** añade la fila en la tabla de `docs/ADR/README.md`.
7. **ARCHITECTURE:** actualiza la tabla o sección afectada y enlaza el ADR en su columna «Decisión».

## Reemplazar una decisión

Un ADR aceptado no se reescribe:

1. Crea un ADR nuevo con la decisión nueva, que cite al anterior en «Contexto».
2. En el anterior, cambia solo el estado a `Reemplazado por ADR-NNNN`.
3. Actualiza los dos en el índice y en ARCHITECTURE.

Commits: `docs(adr): add NNNN <title>`, separados del código (skill `commits`).
