---
name: story
description: Cómo ejecutar una historia de una funcionalidad ya planificada, desde comprobar que está lista hasta dejarla revisada por el subagente reviewer y lista para publicar. Úsala en la fase 3, al empezar o retomar una historia.
---

# Ejecutar una historia

El flujo y sus paradas están en [WORKFLOW §6](../../../WORKFLOW.md#6-fase-3--ejecución-de-una-historia); la definición de Ready y Done, en [CONTRIBUTING §2](../../../CONTRIBUTING.md#definición-de-ready). Esta skill cubre hasta la revisión del subagente; la publicación y el cierre siguen en la skill `pull-requests`.

## 1. Preparar

1. **Retomar:** si la rama ya existe, deduce en qué paso está por los commits, las casillas de su sección en `tasks.md` y el estado del PR, y sigue desde ahí.
2. **Ready:** la Issue cuelga de su épica, su sección de `tasks.md` está en `dev` (o es una historia suelta) y no tiene bloqueos abiertos. Si no, dilo y no empieces.
3. **Contexto**, en el orden de [AGENTS §1](../../../AGENTS.md#1-qué-leer-para-cada-tarea), leyendo solo lo que la historia necesita: la Issue; su sección de `tasks.md` y las partes de `design.md` y de las specs que esa sección cita (no el cambio entero); los requisitos, ARCHITECTURE, ADR y contratos que afecten, por secciones; el código y los tests que va a tocar. Los artefactos generados (como `backend/openapi.json`) no se leen enteros: se leen sus fuentes (por ejemplo, `backend/app/contract/`). Si hay mucho que leer, encárgaselo al subagente de exploración de tu herramienta y pídele un resumen con rutas.
4. **Rama:** `git switch dev && git pull` y `git switch -c <tipo>/<issue>-<descripcion>` según la etiqueta de la Issue ([CONTRIBUTING §4](../../../CONTRIBUTING.md#4-tipos-de-trabajo)). Para trabajar en paralelo, el subagente `implementer` usa su propio worktree.

**Historia suelta** (sin funcionalidad): antes de implementar, crea su propio cambio con `propose` y ⏸ espera la aprobación del plan, como en la skill `feature-planning`. Con `no-spec`, la Issue hace de plan.

## 2. Implementar

1. `apply` solo sobre la sección de la historia. No toques las secciones de otras historias.
2. TDD cuando haya una unidad de comportamiento con sentido propio; tests de lo que cubren los criterios de aceptación.
3. Marca cada casilla de la sección al terminar su tarea.
4. Haz commits por bloques lógicos sobre la marcha (skill `commits`).
5. Si el plan no se sostiene: para, explica por qué y propone un `update` del cambio, indicando a qué otras historias afecta. ⏸ Sigue solo cuando la persona lo apruebe.
6. Lo que encuentres fuera del alcance no lo arregles: anótalo para proponerlo como Issue.

## 3. Revisar con el subagente

1. Ejecuta `make test` y `make lint` y corrige lo que falle.
2. Lanza el subagente `reviewer` con: el número de la Issue, el cambio y la sección, la rama, y si es la sección de integración.
3. Corrige los hallazgos dentro del alcance y vuelve a lanzar el reviewer, esta vez solo sobre los commits de corrección y con la lista de hallazgos que resuelven, hasta que no quede ninguno. Los de fuera del alcance, a la lista de Issues propuestas.

Sigue sin pausa con la skill `pull-requests` para publicar.
