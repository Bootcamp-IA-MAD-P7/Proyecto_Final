---
name: feature-planning
description: Cómo planificar una funcionalidad de una épica con un único cambio de OpenSpec (propuesta, specs, diseño y tasks.md por historias) y crear después sus historias en GitHub. Úsala en la fase 2, antes de empezar cualquier historia de la funcionalidad.
---

# Planificar una funcionalidad

El flujo y sus paradas están en [WORKFLOW §5](../../../WORKFLOW.md#5-fase-2--planificación-de-una-funcionalidad); el modelo épica → funcionalidad → historia, en [CONTRIBUTING §2](../../../CONTRIBUTING.md#2-modelo-de-trabajo). Esta skill es el procedimiento. Primero la spec y después las historias: no crees Issues de historia antes de que la persona apruebe el plan.

## 1. Preparar

1. Elige la épica: la siguiente del hito en curso del ROADMAP, o la que diga la persona. Comprueba que sus dependencias están terminadas.
2. Si la épica no tiene Issue, créala con la skill `issues`.
3. Si es la primera funcionalidad de la épica, decide el reparto:
   - **una sola funcionalidad** si la épica es pequeña: hasta unas cinco historias de una o dos capacidades relacionadas;
   - **varias** si no: cada una con valor propio, que se pueda probar sola, en orden. La primera suele ser el camino mínimo de extremo a extremo.
4. `git switch dev && git pull`, y crea la rama `docs/<épica>-<cambio>`, por ejemplo `docs/7-add-briefing-generation`. El nombre del cambio va en inglés y en kebab-case, y empieza por un verbo (`add-`, `change-`, `remove-`).

## 2. Explorar (opcional)

Si los requisitos o el enfoque no están claros, usa `explore`. Si hay mucho que leer, encárgaselo al subagente de exploración de tu herramienta, para no cargar tu contexto:

- **Qué lee**, en este orden: la épica y su entrada en el ROADMAP; los requisitos del PRD que cubre; las specs afectadas y los cambios en curso sobre las mismas capacidades; ARCHITECTURE, los ADR y los contratos de los componentes afectados; el código y los tests implicados.
- **Qué devuelve**, en no más de 400 palabras y con rutas en lugar de contenido copiado: qué pide la funcionalidad y qué requisitos y specs toca; los archivos y componentes que cambiarán; las restricciones de la arquitectura, los ADR y los contratos; una división en historias por capas, y las dudas que cambian el resultado.

⏸ **Parada 1:** presenta las conclusiones y, si la épica es nueva, el reparto en funcionalidades.

## 3. Proponer

Usa `propose` para crear el cambio. Las reglas de cada artefacto están en `openspec/config.yaml`; en resumen:

- `proposal.md`: la épica (`#E`), los requisitos (`RF`, `RNF`, `RD`) que cubre, el alcance y lo que queda fuera.
- Delta de specs: una spec por capacidad afectada, con comportamiento observable y escenarios. Sin requisitos inventados.
- `design.md`: componentes, contratos y decisiones. Marca las que piden un ADR (skill `adr`) o un contrato nuevo (skill `contracts`).
- `tasks.md`: una sección por historia, siguiendo el trabajo por capas:

  ```markdown
  ## 1. Contrato de generación (contrato)

  **Criterios de aceptación:**
  - …

  **Depende de:** —

  - [ ] 1.1 …
  - [ ] 1.2 …

  ## 2. Endpoint de generación (backend)

  **Depende de:** 1
  …

  ## 3. Generación de extremo a extremo (integración)

  **Depende de:** 1, 2
  …
  ```

  El contrato va primero, una sección por capa después y la integración al final. Cada sección deja su capa funcionando y cabe en un PR. La de integración conecta las capas, comprueba el resultado de extremo a extremo y depende de todas las demás: su PR es el que archiva el cambio.

Ejecuta `openspec validate <cambio>`. ⏸ **Parada 2:** presenta el plan: qué cubre, las historias con su capa y sus dependencias, y las decisiones abiertas. Espera la aprobación; si la persona pide cambios, ajusta los artefactos y vuelve a presentarlos.

## 4. Crear las historias

Con el plan aprobado, sigue la skill `issues`:

1. Una Issue de historia por sección, en orden (primero las que bloquean a otras). Título: el de la sección. Cuerpo desde la plantilla de historia: el objetivo y el enlace a su sección de `tasks.md`. No copies los criterios ni las tareas: viven en la sección.
2. Sub-issue de la épica y bloqueos según el «Depende de» de cada sección.
3. Añade el número a cada encabezado de `tasks.md`: `## 2. Endpoint de generación (backend) · #12`.
4. Marca `ready` las que no tienen bloqueos: cumplirán la definición de Ready en cuanto se mergee el PR del plan.

## 5. Publicar el plan

1. En `docs/ROADMAP.md`, añade el cambio a las «Funcionalidades» de su épica y, si faltaba, el enlace a la Issue de la épica.
2. En la Issue de la épica, añade el cambio a su lista de «Funcionalidades».
3. Commits con la skill `commits`: `docs(openspec): propose <cambio>` y `docs(roadmap): link <cambio>`, con `Refs #E`.
4. Push y PR a `dev` con `Refs #E`, explicando el plan y enlazando las historias creadas. Espera al CI.
5. Avisa: el plan está listo para mergear y, una vez en `dev`, la primera historia se puede empezar (skill `story`), en una sesión nueva si es posible.
