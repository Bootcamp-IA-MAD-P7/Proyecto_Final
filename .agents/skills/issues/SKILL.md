---
name: issues
description: Cómo crear en GitHub las etiquetas, épicas, historias y bugs, con jerarquía y bloqueos nativos. Úsala al planificar una funcionalidad (las historias salen de su tasks.md aprobado) o al crear cualquier Issue.
---

# Issues

Modelo de trabajo y definición de Ready en [CONTRIBUTING §2 y §6](../../../CONTRIBUTING.md#2-modelo-de-trabajo); etiquetas en [`docs/ISSUE_LABELS.md`](../../../docs/ISSUE_LABELS.md). Necesitas GitHub CLI 2.94 o superior (`gh --version`): las anteriores no tienen `--parent` ni `--blocked-by`.

1. **Etiquetas:** si falta alguna de `docs/ISSUE_LABELS.md`, ejecuta `make labels`, que las crea o actualiza todas.
2. **Orden:** crea antes las Issues de las que dependen otras, para poder enlazar los bloqueos.
3. **Cuerpo:** desde su plantilla de `.github/ISSUE_TEMPLATE/` (épica, historia o bug), en español y sin copiar lo que ya tiene dueño: la épica enlaza su entrada del ROADMAP, y la historia de una funcionalidad, su sección de `tasks.md` ya aprobada, de la que toma el título. Nunca crees historias de una funcionalidad antes de que la persona apruebe su plan.
4. **Etiquetas de cada Issue:** exactamente una de nivel (`epic` o `story`) y al menos una de tipo. Aplícalas de forma explícita con `--label`; `gh` no las toma de la plantilla.
5. **Jerarquía y bloqueos:** con las relaciones nativas, nunca en el texto: `gh issue create --parent <épica> --blocked-by <N,M>`.
6. **Ready:** marca `ready` las historias que cumplen la definición de Ready.
7. **`no-spec`:** nunca la pongas tú; es decisión de la persona.
8. Al crear las historias de una funcionalidad, añade su número al encabezado de su sección en `tasks.md` (`· #N`).
9. Al crear una épica, enlázala en `docs/ROADMAP.md` (`· Issue: #N`). Ese cambio se publica en el PR del plan de la funcionalidad (skill `feature-planning`) o, si va solo, en un PR `docs/` a `dev`.

Si falta autenticación o permiso de escritura (`gh auth status`), di qué hay que configurar; no des el trabajo por hecho.
