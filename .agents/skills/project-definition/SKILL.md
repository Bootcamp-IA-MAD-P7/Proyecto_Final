---
name: project-definition
description: Cómo redactar los documentos base del proyecto (PRD, ARCHITECTURE con sus ADR y ROADMAP), hacer el commit inicial y proteger las ramas. Úsala en la fase 1 (definición) o cuando cambie el producto.
---

# Definición del proyecto

El flujo y sus paradas están en [WORKFLOW §4](../../../WORKFLOW.md#4-fase-1--definición); qué contiene cada documento, en el [mapa de documentación](../../../WORKFLOW.md#2-mapa-de-documentación). Esta skill es el procedimiento.

## Primera definición

1. **Comprueba el punto de partida:** estás en `dev`, actualizada, y `setup/README.md` está hecho hasta su paso 7. Si no, dilo y para.
2. **Redacta los documentos en orden**, cada uno a partir del anterior ya aprobado:
   1. `docs/PRD.md`: resumen, problema, usuarios, objetivos `OBJ-n` con su comprobación, principios y alcance; glosario, flujos y requisitos `RF-nn`, `RNF-nn` y `RD-nn`, cada uno con el `OBJ` que sirve y criterios de aceptación observables; riesgos y decisiones `DEC-nn`.
   2. `docs/ARCHITECTURE.md`: stack, componentes, estructura, datos, operación, calidad y despliegue, marcando cada elemento como Actual, Objetivo o Candidata. Cada decisión técnica significativa lleva su ADR (skill `adr`).
   3. `docs/ROADMAP.md`: hitos y épicas con su resultado, requisitos y dependencias. La primera épica es el *walking skeleton* ([WORKFLOW §5](../../../WORKFLOW.md#trabajo-por-capas)).
3. **Para cada documento:**
   - haz solo las preguntas imprescindibles, todas juntas;
   - escribe un borrador corto; no rellenes con suposiciones: lo no confirmado va a «Preguntas abiertas»;
   - usa IDs estables y no los reutilices;
   - no copies datos de otro documento: enlaza a su dueño;
   - ⏸ presenta el borrador y espera la aprobación antes de pasar al siguiente.
4. **Commit inicial**, al aprobar el ROADMAP:
   1. Borra la carpeta `setup/`.
   2. Rellena en el `README.md` lo que la definición ya permite (nombre y descripción).
   3. Commit en `dev`: `docs: add project definition`, con la skill `commits`, y push a `dev`. Tu herramienta pedirá confirmación: es el único push directo.
5. **Protección de ramas:** ⏸ propón activarla y, con la aprobación de la persona, ejecuta `make github-protect` ([CONTRIBUTING §3](../../../CONTRIBUTING.md#protección-de-ramas)). Necesita permisos de administración en el repositorio; si falla, di qué falta.
6. **Avisa** de que el siguiente paso es planificar la primera funcionalidad del walking skeleton (skill `feature-planning`).

## Cambios posteriores

Cuando cambia el producto (requisito nuevo, otro alcance, un hito nuevo):

1. Rama `docs/<descripcion>` desde `dev` (o `docs/<issue>-<descripcion>` si hay Issue).
2. Actualiza solo los documentos afectados, en el mismo orden. Un requisito retirado se marca «Retirado»; una decisión reemplazada se marca y se añade la nueva.
3. ⏸ Presenta el cambio y espera la aprobación.
4. Commits con la skill `commits` y PR a `dev` con la plantilla de PR.
