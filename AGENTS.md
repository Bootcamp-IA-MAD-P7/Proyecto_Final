# AGENTS

Instrucciones para cualquier agente de IA (OpenCode, Codex, Claude Code…). Este archivo es un índice: lee solo lo que pide la tarea en curso y amplía cuando aparezca una dependencia. Las convenciones son las de [`CONTRIBUTING.md`](CONTRIBUTING.md) y el flujo, el de [`WORKFLOW.md`](WORKFLOW.md).

## 1. Qué leer para cada tarea

| Tarea | Skill | Lee además |
|---|---|---|
| Definir el proyecto o cambiar el producto (fase 1) | `project-definition` | [WORKFLOW §4](WORKFLOW.md#4-fase-1--definición) y el documento de `docs/` que toque |
| Planificar una funcionalidad (fase 2) | `feature-planning` | [WORKFLOW §5](WORKFLOW.md#5-fase-2--planificación-de-una-funcionalidad) |
| Crear etiquetas, épicas, historias o bugs | `issues` | [`docs/ISSUE_LABELS.md`](docs/ISSUE_LABELS.md) |
| Ejecutar una historia (fase 3) | `story` | [WORKFLOW §6](WORKFLOW.md#6-fase-3--ejecución-de-una-historia) y el contexto de la historia (abajo) |
| Hacer commits | `commits` | — |
| Publicar el PR, esperar al CI y cerrar | `pull-requests` | — |
| Preparar una versión (fase 4) | `release` | [WORKFLOW §7](WORKFLOW.md#7-fase-4--release) |
| Registrar una decisión técnica | `adr` | [`docs/ADR/README.md`](docs/ADR/README.md) |
| Crear o cambiar una interfaz entre componentes | `contracts` | [`docs/CONTRACTS/README.md`](docs/CONTRACTS/README.md) |
| Añadir un servicio (walking skeleton o nuevo) | `add-service` | [CONTRIBUTING §10](CONTRIBUTING.md#10-entorno-de-ejecución-makefile-docker-y-variables) |
| Arrancar, probar o levantar servicios | — | `make help` |
| Saber qué documento manda sobre un dato | — | [El mapa de documentación](WORKFLOW.md#2-mapa-de-documentación) |
| Dudas de alcance o prioridad | — | [`docs/PRD.md`](docs/PRD.md) |

Las skills están en [`.agents/skills/`](.agents/skills/), junto a las de OpenSpec (§4). Son los procedimientos paso a paso; las reglas siguen estando aquí y en CONTRIBUTING. Cómo las carga cada herramienta: [README](README.md#herramientas-de-ia).

**Contexto de una historia**, en este orden: la Issue, su épica y sus bloqueos; su sección de `tasks.md` y el resto del cambio de su funcionalidad en `openspec/changes/` (propuesta, delta de specs y diseño); los requisitos que cita en `docs/PRD.md`; las specs afectadas en `openspec/specs/`; `docs/ARCHITECTURE.md` y los ADR y contratos de los componentes afectados; el código y los tests implicados. Al retomar una historia, deduce en qué paso está por la rama, `tasks.md` y el estado del PR antes de actuar.

## 2. Principios

- Entre las paradas ⏸ de WORKFLOW, encadena los pasos sin esperar órdenes e informa al llegar a la siguiente. Detente antes solo ante una ambigüedad que cambie el resultado.
- No inventes decisiones de producto: pregunta o regístralas como pregunta abierta.
- Nunca afirmes que una comprobación pasó si no la has ejecutado.
- Tras cada push, espera al CI y corrige los fallos dentro del alcance antes de informar; no entregues un PR en rojo.
- Ante un dato duplicado o contradictorio, prevalece su dueño según el mapa de documentación; señala la duplicación.
- Lo que encuentres fuera del alcance no lo arregles: propónlo como Issue en la siguiente parada.
- Cambios enfocados: sin refactors ajenos a la historia. Usa TDD cuando haya una unidad de comportamiento con sentido propio; no escribas tests solo para subir la cobertura.
- Usa los objetivos del `Makefile` en lugar de inventar comandos. Si falta uno que necesitas, añádelo con su `## descripción`.

## 3. Autonomía y límites

**Sin pedir permiso puedes:**

- leer, explorar, crear ramas y hacer commits locales;
- ejecutar los checks, `verify`, `sync`, `openspec validate` y los subagentes;
- actualizar la documentación y ajustar tareas dentro del alcance aprobado (infórmalo en la siguiente parada);
- publicar correcciones en un PR en revisión, incluidas las de un CI en rojo;
- crear las etiquetas y las Issues de un plan aprobado.

**Nunca:**

- Mergear un PR, hacer push directo a `main` o `dev` (salvo el commit de la definición inicial, [WORKFLOW §4](WORKFLOW.md#4-fase-1--definición)) ni reescribir historia ya publicada: nada de `push --force`.
- Cerrar Issues a mano ni crear tags o releases: se cierran con `Closes` y los crea el CI al mergear. Si el workflow falla, informa.
- Cambiar el PRD o el ROADMAP fuera de un plan aprobado.
- Decidir por tu cuenta que una historia no necesita OpenSpec, ni poner la etiqueta `no-spec`.
- Desactivar la validación de `archive`.
- Versionar secretos o credenciales.

Los permisos del repositorio (`opencode.jsonc`, `.codex/rules/` y `.claude/settings.json`) bloquean los comandos de estos límites o piden confirmación. No intentes rodearlos.

## 4. OpenSpec

- **Configuración:** `openspec/config.yaml`. Instalación y perfil: [README](README.md#herramientas).
- **Etapas:** cada etapa es una skill de OpenSpec en `.agents/skills/`: `openspec-explore`, `openspec-propose`, `openspec-apply-change`, `openspec-update-change`, `openspec-verify-change`, `openspec-sync-specs` y `openspec-archive-change`. Se invocan con `/` en OpenCode y Claude Code, y con `$` en Codex. En la documentación se nombran por su etapa: `explore` y `propose` se usan al planificar una funcionalidad; `apply`, `update`, `verify`, `sync` y `archive`, al ejecutar sus historias.
- **Un cambio por funcionalidad, no por historia.** El cambio cubre un bloque de varias historias, en kebab-case y en inglés (`add-briefing-generation`). Primero la spec y después las historias: las Issues se crean desde las secciones de `tasks.md` del plan aprobado. Si una funcionalidad no cabe en un cambio razonable, propón repartirla.
- **`tasks.md` por historias:** una sección por historia (`## N. <título> (<capa>) · #<issue>`), con sus criterios de aceptación, sus dependencias y sus tareas. La última es la de integración y depende de todas las demás. Al implementar una historia, trabaja solo en su sección; `tasks.md` es la fuente de verdad del avance.
- **`verify`, `sync` y `archive`:** en cada historia, `verify` se limita a su sección. El PR de la sección de integración, tras su revisión, hace `verify` del cambio completo, `sync` y `archive`, una sola vez.
- **Siempre en las historias, salvo `no-spec`.** Una historia se hace sin OpenSpec solo si la persona le ha puesto la etiqueta `no-spec`; tu estimación del tamaño no lo autoriza. Una historia suelta (un bug o una mejora fuera de una épica en curso) lleva su propio cambio pequeño. Definición y release no usan OpenSpec.
- **Trabajo sin Issue:** propón crear una historia o un bug. Si la persona prefiere hacerlo directamente, trabaja sin OpenSpec, en una rama propia y con PR.
- **Sin cambio de comportamiento** (refactor, test, chore o docs que no lleven `no-spec`): sin delta de specs y archive con `--skip-specs`. No inventes requisitos para superar la validación.

## 5. Subagentes

Las instrucciones están en [`.agents/agents/`](.agents/agents/); `.opencode/agents/`, `.codex/agents/` y `.claude/agents/` solo las adaptan a cada herramienta. Para explorar, usa el subagente de exploración que traiga tu herramienta.

| Subagente | Cuándo | Qué hace |
|---|---|---|
| `reviewer` | Siempre, al terminar `apply` de una historia y tras cada corrección pedida en el PR | Con contexto limpio y solo lectura: ejecuta `verify` (de la sección o, en la de integración, del cambio completo) y revisa el código frente a la spec, el diseño y CONTRIBUTING. Devuelve hallazgos; no corrige |
| `implementer` | Opcional, con historias desbloqueadas en paralelo | Ejecuta `apply` de la sección de una historia en su propio *git worktree* |

El agente principal es el responsable de cada paso: decide qué hallazgos del reviewer están dentro del alcance, los corrige y vuelve a pasar el reviewer.

## 6. Comandos

`make help` lista todos los comandos con su descripción. Los habituales, que define el *walking skeleton*:

- `make setup`: prepara el clon (hooks de git, archivos `.env` e instalación).
- `make up` / `make down`: levanta o para todo con Docker.
- `make test` y `make lint`: los checks de cada servicio, en local.
- `make ci`: lo mismo que el job `Servicios` del CI, en Docker.
