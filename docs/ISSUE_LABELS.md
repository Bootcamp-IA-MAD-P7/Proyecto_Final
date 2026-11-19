# Etiquetas de Issues

> Fuente de verdad de las etiquetas del repositorio: `make labels` las crea o actualiza en GitHub a partir de estas tablas, con el «Uso» como descripción (GitHub admite hasta 100 caracteres). Cómo se usan: [CONTRIBUTING §2](../CONTRIBUTING.md#2-modelo-de-trabajo) y [§6](../CONTRIBUTING.md#6-issues).

## Tipo: al menos una

| Etiqueta | Uso | Color |
|---|---|---|
| `feature` | Capacidad nueva para el usuario o el sistema | `1D76DB` |
| `enhancement` | Mejora incremental de una capacidad existente | `5319E7` |
| `fix` | Corrección de un defecto | `D73A4A` |
| `refactor` | Reestructuración sin cambio de comportamiento | `FBCA04` |
| `docs` | Solo documentación | `0075CA` |
| `test` | Solo tests | `BFD4F2` |
| `chore` | Herramientas, dependencias o mantenimiento | `C5DEF5` |

## Nivel: exactamente una

| Etiqueta | Uso | Color |
|---|---|---|
| `epic` | Capacidad de producto del ROADMAP; agrupa una o varias funcionalidades y sus historias | `3E4B9E` |
| `story` | Sección de `tasks.md` de una funcionalidad; una rama y un PR | `0E8A16` |

## Prioridad: opcional

| Etiqueta | Uso | Color |
|---|---|---|
| `priority: high` | Urgente o de alto impacto | `B60205` |
| `priority: medium` | Importante, pero no urgente | `FBCA04` |
| `priority: low` | Puede esperar | `C2E0C6` |

La prioridad no expresa bloqueos.

## Proceso: opcional

| Etiqueta | Uso | Color |
|---|---|---|
| `no-spec` | Sin OpenSpec. Solo la pone la persona, para `chore`, `docs` o bugs triviales ([AGENTS §4](../AGENTS.md#4-openspec)) | `D4C5F9` |

## Estado: opcional

| Etiqueta | Uso | Color |
|---|---|---|
| `needs: triage` | Falta confirmar el alcance y el encaje | `EDEDED` |
| `needs: clarification` | Falta información para continuar | `D876E3` |
| `ready` | Cumple la [definición de Ready](../CONTRIBUTING.md#definición-de-ready) | `0E8A16` |

Los bloqueos no llevan etiqueta: son la relación nativa *blocked by* de GitHub.

Si el proyecto usa un tablero de GitHub Projects, su campo de estado sustituye a estas etiquetas. No mantengas ambos.

Las etiquetas por defecto de GitHub que no figuran aquí (`bug`, `documentation`, etc.) pueden eliminarse; esa decisión la toma la persona.
