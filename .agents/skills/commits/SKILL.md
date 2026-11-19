---
name: commits
description: Cómo agrupar, redactar y comprobar los commits de este repositorio (Conventional Commits en inglés). Úsala antes de hacer cualquier commit.
---

# Commits

Las convenciones son las de [CONTRIBUTING §4 y §5](../../../CONTRIBUTING.md#5-commits); esta skill es el procedimiento.

1. **Agrupa por bloques lógicos.** Cada commit se entiende y se revisa por sí solo. No mezcles componentes (frontend y backend) ni código y documentación en el mismo commit.
2. **Elige el tipo:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci` o `build`. El tipo principal sale de la etiqueta de la Issue (CONTRIBUTING §4); `test`, `docs`, `perf`, `ci` y `build` pueden acompañarlo.
3. **Redacta el asunto** en inglés: `type(scope): description`, en imperativo, en minúscula y sin punto final. `scope` es opcional: el componente de ARCHITECTURE §3, el módulo o la capacidad.
4. **Cambio incompatible:** `!` tras el tipo y pie `BREAKING CHANGE: …`.
5. **Pie `Refs #N`** si el commit pertenece a una historia.
6. **Comprueba** que el hook `commit-msg` está activo (`git config core.hooksPath` devuelve `.githooks`); si no, ejecuta `make setup`. El CI repite la comprobación en el PR.

El tipo decide la versión (CONTRIBUTING §9): `feat` sube MINOR, `fix` y `perf` suben PATCH, `!` sube MAJOR y el resto no la cambia. Un tipo mal elegido produce una versión equivocada.

```text
feat(api): add generation endpoint
fix(editor): prevent empty submission
docs(specs): sync add-generation-endpoint
chore(openspec): archive add-generation-endpoint
```
