# Tasks

Plan de la funcionalidad `add-walking-skeleton` (E1, épica #1). Una sección por historia: el contrato primero, después una sección por capa, que pueden avanzar en paralelo, y la integración al final. El diseño está en [design.md](design.md).

## 1. Contrato v0.1 del servicio (contrato) · #34

**Criterios de aceptación:**
- `backend/openapi.json` (0.1.0) describe las rutas, objetos y errores del diseño, y un test falla si no coincide con la API declarada.
- Los ejemplos de [examples.md](examples.md) son fixtures JSON validados contra los modelos; los ejemplos inválidos fallan donde corresponde.
- `docs/CONTRACTS/coteach-ai-api.md` (Propuesto, 0.1.0) enlaza el artefacto sin copiar sus campos y figura en el índice de contratos.
- Las interfaces internas `JobStore` e `InferencePipeline` están declaradas, con una `JobStore` en memoria para tests.
- `make backend-test`, `make backend-lint` y `make ci` pasan.

**Depende de:** —

- [x] 1.1 Crear `backend/` (Python 3.11, FastAPI, Pydantic 2, pytest y Ruff) con su `Makefile` (`install`, `dev`, `test`, `lint`), un `Dockerfile` con las etapas `dev` y `prod`, `backend/.env.example` y el servicio `backend` en los tres archivos de Compose (skill `add-service`).
- [x] 1.2 Escribir los modelos Pydantic del contrato (metadatos, trabajo, transcripción, análisis, resultado, revisión, publicación, cambios y error) y declarar las rutas `/v1` con sus respuestas; de momento devuelven 501.
- [x] 1.3 Exportar `backend/openapi.json` con un objetivo del `Makefile` del servicio y añadir el test que falla si el archivo versionado no coincide con la API.
- [x] 1.4 Convertir `examples.md` en fixtures JSON de `backend/tests/`, con casos válidos e inválidos validados contra los modelos.
- [x] 1.5 Declarar `JobStore` e `InferencePipeline` y una implementación en memoria de `JobStore` con sus tests.
- [x] 1.6 Registrar el contrato en `docs/CONTRACTS/coteach-ai-api.md` y en su índice (skill `contracts`) y enlazarlo desde ARCHITECTURE §5.

## 2. API con base de datos y autenticación (backend) · #35

**Criterios de aceptación:**
- `make up` levanta `backend` y `db`; `GET /health` responde 200 y `GET /ready` responde 503 si la base de datos no está disponible (spec `service-operation`).
- Con un token válido y metadatos válidos, `POST /v1/classes` crea la clase y el trabajo en PostgreSQL y responde 202; los casos de error de la spec `class-processing` devuelven los códigos del contrato.
- La autenticación y el acceso por clase cumplen la spec `api-access`, incluido el emisor de pruebas solo con `AUTH_DEV_ISSUER=true`.
- `GET /v1/jobs/{job_id}` y `GET /v1/classes/{class_id}/result` leen de PostgreSQL; review y approve devuelven los ejemplos del contrato sin guardar nada.
- Los tests de integración contra PostgreSQL pasan en `make ci`.

**Depende de:** 1

- [x] 2.1 Añadir `GET /health` y `GET /ready` con la comprobación de la base de datos, con tests.
- [x] 2.2 Añadir `db` (PostgreSQL 17 con healthcheck y volumen) a Compose, SQLAlchemy 2 y Alembic con la migración inicial de clases, participantes, trabajos y resultados.
- [x] 2.3 Implementar `JobStore` sobre PostgreSQL: reclamar con `FOR UPDATE SKIP LOCKED` y devolver a la cola los trabajos en curso, con tests contra PostgreSQL.
- [x] 2.4 Validar tokens firmados (firma, caducidad y audiencia) y añadir el emisor de pruebas `POST /dev/token` para los usuarios sintéticos configurados, activo solo con `AUTH_DEV_ISSUER=true`.
- [x] 2.5 Implementar las rutas `/v1` según el diseño, con el acceso por clase resuelto desde los participantes y CORS limitado a `FRONTEND_ORIGIN`; tests de los escenarios de `api-access` y `class-processing`.
- [x] 2.6 Completar las variables en `backend/.env.example` y `.env.example` y regenerar `backend/openapi.json` si cambia, sin cambiar el contrato fuera de un `update` aprobado.

## 3. Worker y mantenimiento con procesamiento simulado (procesamiento) · #36

**Criterios de aceptación:**
- Con la `JobStore` en memoria, el worker lleva un trabajo `queued` por todas las etapas hasta `ready_for_review` y guarda un resultado sintético que cumple el contrato.
- Al arrancar, el worker devuelve a la cola los trabajos en curso y los termina (ADR-0002).
- Si una etapa falla, el trabajo queda en `failed` con un código de error del contrato y sin resultado.
- `maintenance` arranca y ejecuta su ciclo periódico; ambos procesos dejan logs sin audio, nombres ni tokens (spec `service-operation`).
- `make backend-test` y `make backend-lint` pasan.

**Depende de:** 1

- [x] 3.1 Implementar `FakePipeline` sobre `InferencePipeline`: devuelve el resultado sintético de los ejemplos, validado contra el contrato, y espera `FAKE_STAGE_SECONDS` por etapa.
- [x] 3.2 Implementar el bucle del worker sobre `JobStore`: reclamar, avanzar de etapa, completar o fallar, con un único worker.
- [x] 3.3 Devolver a la cola los trabajos en curso al arrancar y registrarlo en el log.
- [x] 3.4 Crear `maintenance` con su ciclo cada `MAINTENANCE_INTERVAL_SECONDS`, que de momento solo registra actividad.
- [x] 3.5 Añadir las entradas `python -m app.worker` y `python -m app.maintenance` y sus tests con la `JobStore` en memoria.

## 4. Web React contra el contrato (frontend) · #37

**Criterios de aceptación:**
- `frontend/` con Vite, React y TypeScript; `make frontend-lint` (ESLint y tipos) y `make frontend-test` (Vitest) pasan, también en `make ci`.
- Los tipos del cliente se generan de `backend/openapi.json` y `lint` falla si se han desviado.
- Con los mocks del contrato y sin backend se puede entrar con un usuario sintético, subir una clase, ver el progreso, ver la transcripción y el repaso por separado y aprobar.
- El token se guarda solo en memoria y la web no decide permisos.
- Imagen `dev` con el servidor de Vite e imagen `prod` con los estáticos, y el servicio `frontend` en los tres archivos de Compose.

**Depende de:** 1

- [x] 4.1 Crear `frontend/` (Vite, React, TypeScript, React Router y TanStack Query) con su `Makefile`, ESLint, Vitest y Testing Library (skill `add-service`).
- [x] 4.2 Generar los tipos con openapi-typescript y un cliente tipado con openapi-fetch, con la comprobación de desviación en `lint`.
- [x] 4.3 Añadir mocks con MSW a partir de los ejemplos del contrato, activables con `VITE_API_MOCKS=true`.
- [x] 4.4 Crear las pantallas: entrada con usuario sintético, subir una clase, progreso del trabajo, resultado con transcripción y repaso, y aprobar.
- [x] 4.5 Añadir el `Dockerfile` (`dev` y `prod`), el servicio `frontend` en Compose con `backend/openapi.json` montado en solo lectura y `frontend/.env.example` con la URL de la API.
- [x] 4.6 Añadir tests de componentes y del cliente con los mocks.

## 5. Skeleton de extremo a extremo en local (integración) · #38

**Criterios de aceptación:**
- `make up` levanta `backend`, `worker`, `maintenance`, `frontend` y `db`; desde la web, sin mocks, una clase enviada avanza por las etapas y muestra el resultado sintético.
- `make up-prod` levanta lo mismo con la configuración de producción en local (ADR-0005).
- Una prueba E2E automatizada recorre entrar, subir, ver el progreso y ver el resultado contra el stack real con `make e2e`.
- `make ci` pasa y `verify` del cambio no deja discrepancias con las specs.
- ARCHITECTURE §3 marca los componentes como Actual y §4 y §7 reflejan la estructura y los puertos reales.

**Depende de:** 1, 2, 3, 4

- [x] 5.1 Añadir `worker` y `maintenance` a los tres archivos de Compose con la imagen de `backend`, conectados a la `JobStore` de PostgreSQL y a `FakePipeline`.
- [x] 5.2 Conectar la web a la API real: URL, CORS y emisor de pruebas activado en desarrollo.
- [x] 5.3 Añadir la prueba E2E con Playwright en `frontend/e2e/` y el objetivo `make e2e`, y ejecutarla contra `make up`.
- [x] 5.4 Comprobar `make up-prod` en local y explicar en el README cómo levantar la demo.
- [x] 5.5 Actualizar ARCHITECTURE §3, §4 y §7.
- [ ] 5.6 Ejecutar `verify`, `sync` y `archive` del cambio (skill `pull-requests`).
