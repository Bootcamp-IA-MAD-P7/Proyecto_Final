# API de CoTeach AI

- **Estado:** Propuesto
- **Versión:** 0.1.0
- **Productor → consumidores:** backend (componente api) → frontend y CoTeach
- **Artefacto ejecutable:** [`backend/openapi.json`](../../backend/openapi.json)

## Propósito

Estabiliza el intercambio entre el servicio y quien lo usa: comprobar que está vivo y disponible, enviar una clase con su audio y sus metadatos, seguir su trabajo de procesamiento, consultar el resultado (transcripción y repaso pedagógico por separado), corregirlo y aprobarlo. Permite que la API, el procesamiento y la web avancen en paralelo desde el walking skeleton ([add-walking-skeleton](../../openspec/changes/add-walking-skeleton/design.md)).

## Fuente de verdad

- Las rutas, los objetos, los estados y los códigos de error están en `backend/openapi.json`. Este documento no copia sus campos.
- `openapi.json` se exporta de los modelos Pydantic de `backend/app/contract/` y de las rutas de `backend/app/api/` con `make -C backend openapi`. Un test de `backend` falla si el archivo versionado no coincide con la API declarada, así que cualquier cambio del contrato aparece en el diff del PR.
- Los ejemplos sintéticos están en [`backend/tests/fixtures/contract/`](../../backend/tests/fixtures/contract/): `valid/` cumple el contrato y `invalid/` debe rechazarse, con el código de error esperado cuando es de metadatos. Los tests los validan contra los modelos y sirven de base a los mocks de la web.

## Lo que el artefacto no cuenta

### Autenticación y acceso

- `GET /health` y `GET /ready` no llevan credencial ni datos de clases; `/ready` nombra las dependencias caídas sin credenciales ni cadenas de conexión ([spec service-operation](../../openspec/changes/add-walking-skeleton/specs/service-operation/spec.md)).
- Toda petición a `/v1` lleva `Authorization: Bearer <token>`, firmado por el emisor configurado. El rol y el sujeto salen del token, nunca del cuerpo: los objetos de petición rechazan campos desconocidos ([spec api-access](../../openspec/changes/add-walking-skeleton/specs/api-access/spec.md), [ADR-0004](../ADR/0004-access-and-retention.md)).
- El servidor resuelve el acceso a cada clase: la crea una docente o la credencial de servicio de CoTeach, y la consultan las personas cuyo `participant_id` coincide con el sujeto del token. Una clase o un trabajo ajenos, inexistentes o con un identificador mal formado responden 404 `resource_not_available`, para no revelar que existen; 403 `forbidden` es solo para una operación no permitida sobre una clase que sí se ve.
- El alumnado solo ve la versión publicada de un resultado; ante un borrador recibe 404.
- Mientras CoTeach no defina su emisor, la demo usa un emisor de pruebas aislado que no forma parte del contrato (PRD §14).

### Errores

- Todo error usa el sobre `ErrorResponse`: `error.code`, `error.message` seguro, `error.retryable` y `request_id`, que también va en la cabecera `X-Request-ID`. Nunca lleva trazas, tokens, audio, transcripciones ni datos de la petición.
- Un fallo inesperado responde 500 `internal_error`, sin detalles.
- Solo los errores transitorios (`service_unavailable`) llevan `retryable=true`. Los 409 de corrección y aprobación piden releer el resultado y resolver, no repetir a ciegas.
- En un 422 de `POST /v1/classes`, `invalid_consent_reference` prevalece sobre `invalid_participants`, y ambos sobre `invalid_request`.
- Un trabajo fallido o en espera de reintento se consulta con 200 y lleva su propio `error` con un código de `JobErrorCode`.

### Comportamiento

- `POST /v1/classes` responde 202 sin esperar al procesamiento. Recibir `consent_reference` y validar su forma no prueba que exista el consentimiento; cómo se verifica sigue pendiente (PRD §14).
- Estados del trabajo: `queued` → `normalizing` → `transcribing` → `diarizing` → `analyzing` → `ready_for_review`, con `failed` como salida. `retry_wait`, `published` y `expired` están declarados, pero no se producen hasta E2 y E5.
- En `PATCH .../review`, cada sección enviada reemplaza la sección completa y las ausentes se conservan; la respuesta es la nueva versión del resultado. No se editan la identidad de la clase, los permisos, la publicación ni el plazo.
- Fechas en UTC con zona horaria (ISO 8601). El plazo de revisión no se fija en el contrato: lo calcula el servicio (PRD DEC-05, pendiente de Lay).

### Estado en el walking skeleton

En v0.1 todas las rutas responden ([tasks.md](../../openspec/changes/add-walking-skeleton/tasks.md), sección 2): recepción, consulta del trabajo y del resultado leen y escriben en PostgreSQL; corrección y aprobación devuelven los ejemplos sin guardar nada hasta E5. La recepción todavía no guarda el audio, que llega en E2. La idempotencia y los límites de tamaño y formato del audio (409, 413 y 415) se declaran ya y llegan en E2.

## Compatibilidad

- Compatible, sube MINOR: una ruta, un campo opcional, un valor de enumeración o un código de error nuevos. Los consumidores deben ignorar los valores de enumeración que no conocen o tratarlos como genéricos.
- Incompatible, sube MAJOR con un ADR o una nota de migración aquí: eliminar o renombrar un campo, cambiar su tipo o su significado, o hacer obligatorio uno opcional (por ejemplo, `Idempotency-Key`).
- `schema_version` de cada resultado indica la versión del contrato con que se produjo.
- Cada épica que amplíe el contrato sube MINOR y la web regenera sus tipos desde `backend/openapi.json` (skill `contracts`).
