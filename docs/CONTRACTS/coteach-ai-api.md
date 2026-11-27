# API de CoTeach AI

- **Estado:** Propuesto
- **Versión:** 0.2.0
- **Productor → consumidores:** backend (componente api) → frontend y CoTeach
- **Artefacto ejecutable:** [`backend/openapi.json`](../../backend/openapi.json)

## Propósito

Estabiliza el intercambio entre el servicio y quien lo usa: comprobar que está vivo y disponible, enviar una clase con su audio y sus metadatos, seguir su trabajo de procesamiento, consultar el resultado (transcripción y repaso pedagógico por separado), corregirlo y aprobarlo. Permite que la API, el procesamiento y la web avancen en paralelo desde el walking skeleton ([add-walking-skeleton](../../openspec/changes/archive/2026-11-25-add-walking-skeleton/design.md)).

## Fuente de verdad

- Las rutas, los objetos, los estados y los códigos de error están en `backend/openapi.json`. Este documento no copia sus campos.
- `openapi.json` se exporta de los modelos Pydantic de `backend/app/contract/` y de las rutas de `backend/app/api/` con `make -C backend openapi`. Un test de `backend` falla si el archivo versionado no coincide con la API declarada, así que cualquier cambio del contrato aparece en el diff del PR.
- Los ejemplos sintéticos están en [`backend/tests/fixtures/contract/`](../../backend/tests/fixtures/contract/): `valid/` cumple el contrato y `invalid/` debe rechazarse, con el código de error esperado cuando es de metadatos. Los tests los validan contra los modelos y sirven de base a los mocks de la web.

## Lo que el artefacto no cuenta

### Autenticación y acceso

- `GET /health` y `GET /ready` no llevan credencial ni datos de clases; `/ready` nombra las dependencias caídas sin credenciales ni cadenas de conexión ([spec service-operation](../../openspec/specs/service-operation/spec.md)).
- Toda petición a `/v1` lleva `Authorization: Bearer <token>`, firmado por el emisor configurado. El rol y el sujeto salen del token, nunca del cuerpo: los objetos de petición rechazan campos desconocidos ([spec api-access](../../openspec/specs/api-access/spec.md), [ADR-0004](../ADR/0004-access-and-retention.md)).
- El servidor resuelve el acceso a cada clase: la crea una docente o la credencial de servicio de CoTeach, y la consultan las personas cuyo `participant_id` coincide con el sujeto del token. Una clase o un trabajo ajenos, inexistentes o con un identificador mal formado responden 404 `resource_not_available`, para no revelar que existen; 403 `forbidden` es solo para una operación no permitida sobre una clase que sí se ve.
- El alumnado solo ve la versión publicada de un resultado; ante un borrador recibe 404.
- Mientras CoTeach no defina su emisor, la demo usa un emisor de pruebas aislado que no forma parte del contrato (PRD §14).

### Errores

- Todo error usa el sobre `ErrorResponse`: `error.code`, `error.message` seguro, `error.retryable` y `request_id`, que también va en la cabecera `X-Request-ID`. Nunca lleva trazas, tokens, audio, transcripciones ni datos de la petición.
- Un fallo inesperado responde 500 `internal_error`, sin detalles.
- Solo los errores transitorios (`service_unavailable`) llevan `retryable=true`. Los 409 de corrección y aprobación piden releer el resultado y resolver, no repetir a ciegas.
- En un 422 de metadatos de `POST /v1/classes`, `invalid_consent_reference` prevalece sobre `invalid_participants`, y ambos sobre `invalid_request`.
- Un envío de `POST /v1/classes` con varios problemas recibe siempre el primero de este orden: 401 y 403; 413 `audio_too_large` si el cuerpo multipart declarado o recibido excede el límite temprano; 422 de metadatos; 413 `audio_too_large` del archivo; 415 `unsupported_audio`; 422 `invalid_audio_duration`; 409 `idempotency_conflict`.
- Un trabajo fallido o en espera de reintento se consulta con 200 y lleva su propio `error` con un código de `JobErrorCode`.

### Audio de la clase

- **Formatos admitidos:** Opus (en Ogg, WebM o Matroska), MP3 y AAC (en M4A, MP4, MOV o 3GP, solo con audio). El servicio los reconoce por su contenido; el nombre del archivo y su `Content-Type` no cuentan. Un archivo que no se puede leer, sin pista de audio o con vídeo recibe 415 `unsupported_audio`.
- **Límites configurables** por despliegue, con estos valores por defecto: 150 MB de tamaño máximo (`UPLOAD_MAX_BYTES`, 413 `audio_too_large`) y una duración de 1 minuto a 2 horas (`UPLOAD_MIN_SECONDS` y `UPLOAD_MAX_SECONDS`, 422 `invalid_audio_duration`). Los consumidores no deben fijar estos valores: la API es quien decide.
- El cliente envía el audio ya comprimido. Un envío rechazado no deja ni clase, ni trabajo, ni audio guardado.
- Antes de analizar el multipart, el servicio rechaza con 413 los cuerpos por encima de `UPLOAD_MAX_BYTES` más 64 KiB para límites, cabeceras y metadatos multipart. Si no hay `Content-Length` o es inferior a los bytes reales, cuenta la transmisión y la corta al rebasar ese límite. El margen no aumenta el máximo del archivo: ese se sigue contando exactamente sobre la parte `audio`.
- El audio se guarda de forma privada y nunca se devuelve: ni su ruta ni su contenido salen en el contrato. Se conserva 14 días por defecto (`AUDIO_RETENTION_DAYS`, [ADR-0004](../ADR/0004-access-and-retention.md)).
- `Idempotency-Key` es opcional. Con la misma clave de quien envía, el mismo audio y los mismos metadatos, se responde 202 con la clase y el trabajo existentes; con otro contenido, 409 `idempotency_conflict`. La clave de otra persona no choca. Sin la cabecera, cada envío crea una clase nueva.

### Comportamiento

- `POST /v1/classes` responde 202 sin esperar al procesamiento. Recibir `consent_reference` y validar su forma no prueba que exista el consentimiento; cómo se verifica sigue pendiente (PRD §14).
- Estados del trabajo: `queued` → `normalizing` → `transcribing` → `diarizing` → `analyzing` → `ready_for_review`, con `failed` como salida. Desde v0.2, un trabajo sin terminar cuyo audio vence pasa a `expired`: no se procesa más, se consulta con ese estado y no lleva `error`. Un trabajo terminado conserva su resultado aunque se purgue el audio. Desde E3, un fallo transitorio (como un modelo que no está disponible) deja el trabajo en `retry_wait`, con la etapa que falló y `error.retryable` verdadero, y se reintenta solo desde `normalizing` tras una espera que crece con cada intento; `attempt` cuenta los intentos. El último intento fallido, o un fallo que no es transitorio, lo deja en `failed` con `error.retryable` falso. Un trabajo en `retry_wait` también caduca con su audio. `published` (E5) está declarado, pero todavía no se produce.
- En `PATCH .../review`, cada sección enviada reemplaza la sección completa y las ausentes se conservan; la respuesta es la nueva versión del resultado. No se editan la identidad de la clase, los permisos, la publicación ni el plazo.
- Fechas en UTC con zona horaria (ISO 8601). El plazo de revisión no se fija en el contrato: lo calcula el servicio (PRD DEC-05, pendiente de Lay).

### Transcripción y personas hablantes

- Las personas hablantes se declaran en el orden de su primera intervención con identificadores de sesión (`speaker-1`, `speaker-2`…). `participant_id` es nulo hasta que la docente las asigne en E5: los nombres y roles de los participantes no identifican voces (RD-04).
- Los segmentos van en orden temporal, no se solapan y llevan marcas en milisegundos desde el inicio de la grabación original; normalizar el audio no desplaza esas marcas. Solo se declaran las voces que tienen algún segmento, y nunca más que el número de participantes.
- La diarización es exclusiva: el texto dicho a la vez se atribuye a la voz dominante y no se marca como solapamiento. Alternativa descartada para el 11 de diciembre: un campo opcional en `Segment`, que subiría el contrato a 0.3.0.
- Una grabación sin voz produce una transcripción vacía, sin inventar texto ni hablantes. Hasta E4, el análisis sale vacío (resumen vacío y sin elementos), aunque la etapa de análisis se recorre.
- Estas aclaraciones no cambian campos: el contrato sigue en 0.2.0 y `backend/openapi.json` no cambia.

### Estado por versión

En v0.1 (walking skeleton) todas las rutas responden ([tasks.md](../../openspec/changes/archive/2026-11-25-add-walking-skeleton/tasks.md), sección 2): recepción, consulta del trabajo y del resultado leen y escriben en PostgreSQL; corrección y aprobación devuelven los ejemplos sin guardar nada hasta E5. La recepción todavía no guardaba el audio, y la idempotencia y los límites del audio (409, 413 y 415) solo estaban declarados.

v0.2 (cambio `add-class-reception`) documenta la recepción real: los formatos y límites del audio, el error nuevo `invalid_audio_duration`, el orden de los errores de la recepción y el estado `expired`. La API los aplica a partir de la historia de backend del mismo cambio.

## Historial

- **0.2.0** (MINOR, compatible): añade `ErrorCode.invalid_audio_duration` (422) en `POST /v1/classes` y documenta los formatos y límites del audio y el estado `expired`. Ningún campo cambia. Los consumidores regeneran sus tipos; un cliente de v0.1 que trate los códigos desconocidos como genéricos sigue funcionando. Los resultados producidos antes conservan `schema_version` 0.1.0.
- **0.1.0**: versión inicial del walking skeleton.

## Compatibilidad

- Compatible, sube MINOR: una ruta, un campo opcional, un valor de enumeración o un código de error nuevos. Los consumidores deben ignorar los valores de enumeración que no conocen o tratarlos como genéricos.
- Incompatible, sube MAJOR con un ADR o una nota de migración aquí: eliminar o renombrar un campo, cambiar su tipo o su significado, o hacer obligatorio uno opcional (por ejemplo, `Idempotency-Key`).
- `schema_version` de cada resultado indica la versión del contrato con que se produjo.
- Cada épica que amplíe el contrato sube MINOR y la web regenera sus tipos desde `backend/openapi.json` (skill `contracts`).
