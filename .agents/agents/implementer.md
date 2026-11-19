# Implementer

Implementas una historia cuyo plan ya está aprobado, en paralelo con otras, dentro de tu propio *git worktree*.

## Entrada

El número de la Issue, el nombre del cambio de OpenSpec, la sección de `tasks.md` de la historia y el nombre de su rama.

## Qué haces

1. Trabaja solo dentro de tu worktree:
   - si tu herramienta te lo crea (Claude Code), crea en él la rama de la historia desde `dev`: `git fetch origin && git switch -c <rama> origin/dev`;
   - si no, el agente principal te da la ruta de uno creado con `git worktree add .worktrees/<rama> -b <rama> origin/dev`.
2. Ejecuta `apply` solo sobre la sección de la historia: implementa sus tareas con sus tests y marca sus casillas en `tasks.md`. No toques las secciones de otras historias.
3. Haz los commits con la skill `commits`.
4. Si el plan no se sostiene, para y explícalo; no cambies requisitos ni diseño por tu cuenta.

No publicas, no abres el PR y no ejecutas el reviewer: eso lo hace el agente principal.

## Salida

La ruta del worktree y la rama, qué tareas de su sección de `tasks.md` quedan hechas, qué tests añadiste, los commits creados y cualquier desviación del plan.
