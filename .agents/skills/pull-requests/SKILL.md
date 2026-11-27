---
name: pull-requests
description: Cómo publicar el PR de una historia a dev con Closes, esperar al CI, aplicar las correcciones de la revisión y, en la sección de integración, hacer sync y archive. Úsala en los pasos de publicar, revisar y archivar de WORKFLOW §6.
---

# Pull requests de una historia

Convenciones en [CONTRIBUTING §7](../../../CONTRIBUTING.md#7-pull-requests); el flujo, en [WORKFLOW §6](../../../WORKFLOW.md#6-fase-3--ejecución-de-una-historia).

## Publicar

1. `openspec validate --all`, `make test` y `make lint`. En la sección de integración, además, la prueba E2E en local: `make up`, `make e2e-install` (una vez por equipo) y `make e2e` ([CONTRIBUTING §8](../../../CONTRIBUTING.md#prueba-de-extremo-a-extremo)); el resultado va en la «Validación» del PR.
2. Actualiza la documentación afectada según la tabla «Qué actualizar cuando algo cambia» de WORKFLOW §2.
3. Commits con la skill `commits`, incluido el de las casillas marcadas en `tasks.md`.
4. Push de la rama y PR a `dev` con la plantilla de PR, en español. El cuerpo lleva `Closes #N`, el cambio y la sección de `tasks.md` (o `no-spec`) y los hallazgos del reviewer.
5. Espera al CI. Si falla, corrígelo dentro del alcance, publica y vuelve a esperar. Nunca entregues un PR en rojo.
6. Avisa con el enlace al PR, el resultado del reviewer y de los checks, el estado del CI y la versión prevista que comenta el CI.

## Durante la revisión

- Publica en el mismo PR las correcciones que pida la persona, sin volver a pedir permiso, y espera al CI.
- Si cambian el comportamiento, repite `verify` sobre la sección. Tras cada corrección, vuelve a pasar el reviewer.

Con la Parada 3, la persona mergea con **Rebase and merge**. Solo la sección de integración tiene antes un último paso.

## Archivar, en la sección de integración (tras la Parada 3)

1. Comprueba con `openspec list` que el cambio tiene todas sus tareas hechas. Las demás secciones ya están en `dev`, porque la de integración depende de todas.
2. `verify` sobre el cambio completo; si queda alguna discrepancia, corrígela o informa.
3. `sync` (commit `docs(specs): sync <cambio>`) y `archive` en un último commit que solo contiene el archivo del cambio (`chore(openspec): archive <cambio>`).
4. Si es la última funcionalidad de la épica en el ROADMAP, añade `Closes #E` al cuerpo del PR.
5. Publica y espera al CI. Si falla, las correcciones entran en este mismo PR.
6. Avisa a la persona de que ya puede mergear.

Una historia suelta archiva igual, porque su única sección es también la de integración. Con `no-spec` no hay `sync` ni `archive`.

**Si otro cambio toca la misma spec y se archiva antes**, actualiza tu rama sin forzar el push: `gh pr update-branch --rebase` y después `git pull --rebase`. Repite `sync` y resuelve el conflicto en `openspec/specs/` antes del archive.
