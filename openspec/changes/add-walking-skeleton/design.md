# Design

## Context

Ver [proposal.md](proposal.md). La definición está aprobada: [PRD](../../../docs/PRD.md), [ARCHITECTURE](../../../docs/ARCHITECTURE.md) y ADR-0001 a ADR-0005 aceptados. No hay servicios ni specs todavía. Este cambio crea los servicios de ARCHITECTURE §3 con el mínimo comportamiento que los conecta y fija el contrato v0.1 contra el que trabajarán E2 a E5.

## Goals / Non-Goals

**Goals:**

- Todo levantado en local, con y sin Docker, con un camino mínimo real: la web envía una clase, la API crea el trabajo en PostgreSQL, el worker lo procesa con un pipeline simulado y la web muestra el resultado.
- Un contrato v0.1 ejecutable que permita trabajar en paralelo: la API lo sirve, el procesamiento produce resultados que lo cumplen y la web se genera desde él y lo simula con mocks.
- `make ci` con lint, tests e imágenes de producción de cada servicio.

**Non-Goals:** guardar o validar el audio, modelos reales, corrección y publicación persistentes, despliegue ([ADR-0005](../../../docs/ADR/0005-local-only-environment.md)). RF-06 y RF-07 quedan fuera del MVP.

## Decisions

### Servicios, carpetas y Compose

| Componente (ARCHITECTURE §3) | Carpeta y objetivos de make | Servicio de Compose | Entrada |
|---|---|---|---|
| api | `backend/` (`backend-*`) | `backend` | servidor FastAPI |
| worker | `backend/` | `worker` (imagen de `backend`, otro comando) | `python -m app.worker` |
| maintenance | `backend/` | `maintenance` (imagen de `backend`, otro comando) | `python -m app.maintenance` |
| frontend | `frontend/` (`frontend-*`) | `frontend` | servidor de Vite (dev) o estáticos (prod) |
| — | — | `db` (`postgres:17`) | — |

El `Makefile` de la raíz genera los objetivos de cada carpeta con `Makefile` y `make ci` ejecuta `make lint test` en el servicio de Compose con el nombre de la carpeta. Por eso la API se llama `backend` en Compose, y `worker` y `maintenance` reutilizan su imagen ([ADR-0001](../../../docs/ADR/0001-modular-backend.md)). Cada carpeta necesita su `Dockerfile` y su servicio de Compose desde la primera historia que la crea, o `make ci` falla.

### Contrato primero

- **Fuente de verdad:** los modelos Pydantic de `backend/app/contract/` y las rutas FastAPI que los declaran. `backend/openapi.json` es el artefacto exportado y versionado; un test de `backend` falla si no coincide con la API declarada.
- **Ficha:** `docs/CONTRACTS/coteach-ai-api.md`, Propuesto 0.1.0, productor `backend`, consumidores `frontend` y CoTeach. Enlaza el artefacto y explica lo que este no cuenta (autenticación, visibilidad, compatibilidad); no copia campos (skill `contracts`).
- **Ejemplos:** [examples.md](examples.md) pasa a fixtures JSON de `backend/tests/`, válidos e inválidos, validados contra los modelos. Los mocks de la web parten de los mismos ejemplos.
- **Web:** genera sus tipos de `backend/openapi.json` con openapi-typescript y usa un cliente tipado (openapi-fetch). El archivo generado se versiona en `frontend/` y su `lint` comprueba que no se ha desviado; para que la imagen `dev` lo vea, Compose monta `backend/openapi.json` en el servicio `frontend` en solo lectura.
- **Versionado:** cada épica que amplíe el contrato sube MINOR; un cambio incompatible sube MAJOR con ADR o nota de migración ([CONTRACTS](../../../docs/CONTRACTS/README.md)).

Alternativa descartada: escribir el OpenAPI a mano. Con FastAPI duplicaría los modelos y acabaría divergiendo.

### Contrato v0.1

Rutas y errores del MVP completo, aunque en E1 solo algunas tengan comportamiento real:

| Operación | Entrada | Salida y errores específicos | Comportamiento en E1 |
|---|---|---|---|
| POST /v1/classes | multipart: audio y metadata JSON; Idempotency-Key | 202: class_id, job_id, state; 409 clave distinta, 413 tamaño, 415 formato, 422 metadatos | Real: valida token y metadatos y crea clase y trabajo. El audio no se guarda (E2); idempotencia y límites, en E2 |
| GET /v1/jobs/{job_id} | token | 200: job_id, class_id, state, stage, attempt, error | Real, desde PostgreSQL |
| GET /v1/classes/{class_id}/result | token | 200 resultado visible; 409 result_not_ready; 404 si no es visible | Real: devuelve el resultado guardado por el worker |
| PATCH /v1/classes/{class_id}/review | expected_result_version, changes | 200 nueva versión; 409 obsoleta; 422 referencia inválida | Stub: valida token y forma y devuelve el ejemplo, sin guardar (E5) |
| POST /v1/classes/{class_id}/approve | expected_result_version | 200 publicación; 409 obsoleta | Stub, igual que la anterior (E5) |
| GET /health, GET /ready | — | 200; /ready 503 si falta una dependencia | Real |

Comunes: 401 credencial inválida; 403 operación prohibida en una clase visible; 404 recurso inexistente o ajeno, para no revelar su existencia; 503 indisponibilidad transitoria. Sobre de error: error.code, error.message seguro, error.retryable y request_id, sin trazas, tokens ni audio.

| Objeto | Campos e invariantes |
|---|---|
| Metadata | external_class_id; participant_count positivo; participants con participant_id único, role teacher/student y display_name opcional; consent_reference obligatorio. Número y lista coherentes |
| Job | job_id, class_id, state, stage nullable, attempt entero no negativo, error nullable; sin rutas locales |
| Transcript | speakers: speaker_id de sesión y participant_id nullable; segments: segment_id, start_ms y end_ms enteros no negativos con fin mayor que inicio, speaker_id existente, text |
| Analysis | general_summary; items con item_id, category y content; categorías vocabulary, grammar, errors_corrections, reinforced_successes, key_concepts, resolved_questions |
| Result | schema_version, class_id, result_version, transcript, analysis, review, publication |
| Review | status pending/in_review/approved, review_due_at; el plazo no se fija en el esquema |
| Publication | status unpublished/published, result_version, published_at y mode (teacher_approved/automatic), nullable mientras no se publique |
| Changes | transcript y analysis corregidos y asociaciones speaker_id → participant_id; no edita identidad de clase, permisos, publicación ni plazo |

Estados del trabajo: queued → normalizing → transcribing → diarizing → analyzing → ready_for_review, con failed como salida. retry_wait, published y expired se declaran en el contrato, pero no se producen hasta E2 y E5. Recibir consent_reference y validar su forma no prueba que exista consentimiento; cómo se verifica sigue pendiente (PRD §14).

### Interfaces internas

Para que API y procesamiento avancen en paralelo, la sección 1 declara dos interfaces en `backend/app/`:

- **`JobStore`:** crear clase y trabajo, consultar, reclamar el siguiente trabajo, cambiar de etapa, completar con resultado, fallar y devolver a la cola los trabajos en curso. La sección 1 trae una implementación en memoria para tests; la sección 2, la de PostgreSQL.
- **`InferencePipeline`:** de audio y metadatos a transcripción y análisis del contrato, por etapas. La sección 3 trae `FakePipeline`; E3 y E4 lo sustituyen por modelos reales sin tocar el worker.

No van a `docs/CONTRACTS/` porque no cruzan componentes desplegados por separado: viven en el mismo paquete.

### Cola y procesos de fondo

Según [ADR-0002](../../../docs/ADR/0002-durable-jobs.md): tabla de trabajos en PostgreSQL, reclamación con transacción corta y `FOR UPDATE SKIP LOCKED`, un único worker y, al arrancar, los trabajos que quedaron en curso vuelven a la cola. `FakePipeline` espera `FAKE_STAGE_SECONDS` por etapa y devuelve el resultado sintético de los ejemplos, validado contra el contrato. `maintenance` ejecuta un ciclo cada `MAINTENANCE_INTERVAL_SECONDS` que de momento solo registra actividad; la publicación al vencer llega en E5 y la purga del audio en E2.

### Autenticación y acceso en el skeleton

Según [ADR-0004](../../../docs/ADR/0004-access-and-retention.md), con un emisor de pruebas aislado mientras CoTeach no defina su emisor (PRD §14):

- La API valida tokens firmados (firma, caducidad y audiencia) con un secreto de `AUTH_SECRET`. El rol sale del token, nunca del cuerpo de la petición.
- **Pertenencia a la clase resuelta en el servidor:** quien envía la clase con rol teacher, o la credencial de servicio de CoTeach, la crea; pueden consultarla las personas cuyo `participant_id` coincide con el sujeto del token. El resto recibe 404. El alumnado no ve resultados sin publicar, así que en E1 recibe 404 en el resultado.
- **Emisor de pruebas:** `POST /dev/token` firma tokens de vida corta para los usuarios sintéticos configurados (demo-teacher, demo-student y una credencial de servicio). Solo existe con `AUTH_DEV_ISSUER=true`, que está activado en desarrollo y desactivado por defecto en producción; para una demo local con `make up-prod` se activa de forma explícita en `.env`.
- La web muestra una pantalla de entrada con los usuarios sintéticos, guarda el token solo en memoria y no decide permisos. CORS limitado a `FRONTEND_ORIGIN`.

### Web

Vite, React y TypeScript (ADR-0001), con React Router y TanStack Query para el estado del servidor. Mocks con MSW a partir de los ejemplos del contrato, activables con `VITE_API_MOCKS=true`, para trabajar sin backend. Vitest y Testing Library para componentes y cliente; ESLint y `tsc` en `lint`. Imagen `dev` con el servidor de Vite en el puerto 5173 e imagen `prod` con los estáticos construidos servidos por nginx en el 8080.

### Calidad

- `backend`: pytest y Ruff; los tests de integración usan el servicio `db` de Compose, que `make ci` levanta como dependencia.
- `frontend`: ESLint, tipos y Vitest.
- E2E: Playwright en `frontend/e2e/`, con `make e2e` contra `make up`. Por ahora se ejecuta en local y no en el CI, para no meter navegadores en la imagen del CI.

### Requisitos del contrato que se especifican en épicas posteriores

El cambio anterior especificaba en `mvp-service-contracts` comportamiento que este skeleton no implementa. Esos requisitos no se pierden: se especificarán, con sus escenarios, en la funcionalidad que los construya, y el contrato v0.1 ya declara sus formas y errores.

| Requisito anterior | Épica que lo especifica |
|---|---|
| Recepción idempotente, límites de tamaño y formato, audio guardado y purgado | E2 |
| Resultado estructurado coherente: intervalos, hablantes sin asignar, categorías vacías, resultados malformados | E3 y E4 |
| Revisión versionada, aprobación, publicación automática y carreras | E5 |
| Compatibilidad explícita del contrato | Reglas de [CONTRACTS](../../../docs/CONTRACTS/README.md) y skill `contracts` |

## Risks / Trade-offs

- **Confundir el skeleton con el MVP:** el resultado es sintético y review/approve son stubs. La web y la API lo indican en su respuesta y en la documentación, y las specs solo recogen lo que E1 hace de verdad.
- **El contrato cambiará en E2 a E5:** asumido; se versiona por MINOR y los tipos de la web se regeneran.
- **Secciones 2 y 3 tocan `backend/` a la vez:** trabajan en paquetes distintos (`app/api`, `app/db` frente a `app/worker`, `app/inference`) y comparten solo las interfaces de la sección 1.
- **E2E solo en local:** un fallo de integración puede llegar a `dev` sin que lo vea el CI. La sección 5 lo ejecuta antes de su PR.

## Migration Plan

No hay clientes ni datos. La migración inicial de Alembic crea las tablas de clases, participantes, trabajos y resultados.

## Open Questions

- Identidad real de CoTeach (PRD §14): el emisor de pruebas es temporal y no fija cómo llegará la identidad en producción.
- Límites de carga (ARCHITECTURE §11): no afectan a E1, porque no guarda audio.
