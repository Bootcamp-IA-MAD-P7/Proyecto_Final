# ADR-0005: Local-only environment until a server is available

- **Estado:** Aceptado
- **Fecha:** 2026-11-24
- **Decisores:** Glezino, por el equipo del proyecto
- **Relacionado:** RNF-01, RNF-03; [ARCHITECTURE §9](../ARCHITECTURE.md#9-despliegue) y [§11](../ARCHITECTURE.md#11-preguntas-abiertas); [WORKFLOW §5](../../WORKFLOW.md#trabajo-por-capas); E1 del [ROADMAP](../ROADMAP.md).

## Contexto

WORKFLOW §5 pide que el walking skeleton quede desplegado desde su primera historia: `dev` en un entorno de pruebas y `main` en producción. Hoy no hay ningún servidor para pruebas ni para producción, y no hay fecha para tenerlo. Las presentaciones del 11 y el 15 de diciembre no necesitan un despliegue público.

## Decisión

Mientras no haya servidor, no se despliega: todo se levanta en local con Docker Compose.

- Se mantienen los tres archivos de Compose. `compose.production.yaml` se usa en local con `make up-prod` para comprobar la configuración de producción.
- El CI sigue ejecutando `make ci` en cada PR: lint y tests de cada servicio en su imagen `dev` y construcción de las imágenes de producción.
- Las demostraciones se hacen desde el equipo de una persona del proyecto, con `make up` o `make up-prod`.

Cuando haya servidor, un ADR nuevo que reemplace a este fijará dónde y cómo se despliegan pruebas y producción, y ARCHITECTURE §9 recuperará los dos entornos.

## Alternativas consideradas

- **Alquilar un servidor o una nube pública ahora:** no hay presupuesto aprobado y los datos saldrían de infraestructura propia (RNF-01, RNF-03).
- **Desplegar en el servidor temporal de Odoo de CoTeach:** no está acordado y no tiene GPU.
- **Mantener el despliegue dentro del walking skeleton:** bloquearía E1 por una dependencia externa sin fecha.

## Consecuencias

- E1 se cierra con todo levantado en local, con y sin Docker, sin esperar a un servidor.
- Se pierde la detección temprana de fallos de entorno que da un despliegue real; `make up-prod` y la construcción de producción del CI la cubren en parte.
- Las demos dependen del equipo de una persona, con Docker y, si se usa, GPU: hay que ensayarlas en ese equipo.
- Añadir el despliegue más tarde es una funcionalidad propia y requiere un ADR que reemplace a este.
