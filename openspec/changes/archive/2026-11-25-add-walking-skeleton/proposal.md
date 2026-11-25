# Proposal

## Why

E1 del [ROADMAP](../../../docs/ROADMAP.md), épica [#1](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/1), es el *walking skeleton*: el producto tiene que estar levantado de extremo a extremo antes de construir sus capacidades, para que API, procesamiento e interfaz avancen en paralelo contra un contrato común y se vea la aplicación real desde el principio ([WORKFLOW §5](../../../WORKFLOW.md#trabajo-por-capas)). Este cambio reorienta el anterior `add-shared-mvp-contracts`, que solo definía el contrato, para que además deje todo levantado en local.

## What Changes

- **Contrato v0.1 del servicio:** modelos Pydantic y `backend/openapi.json` exportado como fuente de verdad, con ejemplos sintéticos validados y su ficha en `docs/CONTRACTS/`.
- **`backend/`:** API FastAPI con `/health` y `/ready`, las rutas `/v1` del contrato, autenticación con un emisor de pruebas, PostgreSQL con Alembic y la cola de trabajos. Las rutas cuyo comportamiento llega en épicas posteriores devuelven los ejemplos del contrato.
- **Procesos de fondo:** `worker`, que recorre las etapas con un pipeline simulado y guarda un resultado sintético, y `maintenance`, con su ciclo periódico todavía vacío.
- **`frontend/`:** web React con TypeScript y Vite, tipos generados del contrato y mocks: entrar con un usuario sintético, subir una clase, ver el progreso, ver el resultado y aprobarlo.
- **Entorno:** Makefile de cada servicio, Dockerfiles `dev` y `prod`, los tres archivos de Compose y los `.env.example`; el CI ejecuta `make ci`.
- **Sin despliegue:** todo se levanta en local mientras no haya servidor ([ADR-0005](../../../docs/ADR/0005-local-only-environment.md)).

Fuera de alcance: guardar, validar y purgar el audio (E2); transcripción y diarización reales (E3); análisis pedagógico real (E4); corrección, aprobación y publicación persistentes (E5), y el despliegue.

## Capabilities

### New Capabilities

- `service-operation`: salud y disponibilidad de la API y actividad observable de los procesos de fondo.
- `api-access`: autenticación con token y acceso limitado a las clases de cada persona.
- `class-processing`: enviar una clase, seguir su trabajo por etapas y consultar el resultado cuando está listo.

### Modified Capabilities

Ninguna; todavía no hay specs.

## Impact

- **Requisitos:** RNF-01 (acceso autenticado y limitado por clase), RNF-03 (contrato en un formato abierto) y RNF-05 (procesamiento diferido). Prepara RF-01 y RF-04 sin implementarlos: el audio no se guarda y el resultado es sintético.
- **Documentación:** `docs/CONTRACTS/` (contrato nuevo e índice); ARCHITECTURE §3 (componentes Actual), §4 (estructura), §5 (enlace al contrato) y §7 (puertos); README si cambia la puesta en marcha.
- **ADR:** aplica ADR-0001, ADR-0002 (un único worker, sin lease), ADR-0004 (emisor de pruebas aislado) y ADR-0005 (solo local). No necesita un ADR nuevo.
- **Épica:** #1. Una historia por sección de `tasks.md`, creadas al aprobar este plan.
