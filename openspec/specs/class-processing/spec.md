# class-processing Specification

## Purpose
Que una clase enviada a la API se procese de forma diferida, por etapas, y su resultado estructurado se pueda consultar al terminar. En este cambio el procesamiento es simulado y el resultado, sintético: los modelos reales llegan en E3 y E4, y la recepción completa del audio en E2. El contrato está en [CONTRACTS](../../../docs/CONTRACTS/README.md).

## Requirements

### Requirement: Envío de una clase
La API SHALL aceptar el envío de una clase con audio y metadatos válidos según el [contrato](../../../docs/CONTRACTS/coteach-ai-api.md), de una persona docente o de la credencial de servicio. Antes de responder, SHALL comprobar que el audio está en un formato admitido por su contenido y no solo por su nombre, y que su tamaño y su duración están dentro de los límites configurados, y SHALL guardarlo de forma privada junto con la clase y el trabajo. Después SHALL responder 202 con los identificadores de la clase y del trabajo sin esperar al procesamiento. Un envío rechazado no deja ni clase, ni trabajo, ni audio guardado (RF-01, RNF-05).

#### Scenario: Envío válido
- **WHEN** una docente autenticada envía un audio admitido dentro de los límites y metadatos válidos
- **THEN** recibe 202 con `class_id`, `job_id` y estado `queued`, el audio queda guardado de forma privada y el trabajo queda pendiente de procesar.

#### Scenario: Participantes incoherentes
- **WHEN** los metadatos repiten un `participant_id` o el número de participantes no coincide con la lista
- **THEN** recibe 422 `invalid_participants` y no se crea ningún trabajo.

#### Scenario: Sin referencia de consentimiento
- **WHEN** los metadatos no incluyen `consent_reference`
- **THEN** recibe 422 `invalid_consent_reference` y no se crea ningún trabajo.

#### Scenario: Sin audio
- **WHEN** el envío no incluye el archivo de audio
- **THEN** recibe 422 y no se crea ningún trabajo.

#### Scenario: Audio demasiado grande
- **WHEN** el audio supera el tamaño máximo configurado
- **THEN** recibe 413 `audio_too_large`, no se crea ningún trabajo y no queda ningún archivo guardado.

#### Scenario: Cuerpo multipart demasiado grande
- **WHEN** una persona autorizada declara o transmite en `POST /v1/classes` un cuerpo multipart mayor que el límite de audio más el margen de metadatos
- **THEN** recibe 413 `audio_too_large` antes de analizar el formulario, el servidor deja de recibir el cuerpo y no quedan temporales, clases ni trabajos.

#### Scenario: Formato no admitido
- **WHEN** el contenido del archivo no es audio en uno de los formatos admitidos, aunque su nombre o su tipo declarado lo sean
- **THEN** recibe 415 `unsupported_audio`, no se crea ningún trabajo y no queda ningún archivo guardado.

#### Scenario: Duración fuera de los límites
- **WHEN** el audio dura menos que la duración mínima o más que la máxima configuradas
- **THEN** recibe 422 `invalid_audio_duration`, no se crea ningún trabajo y no queda ningún archivo guardado.

### Requirement: Seguimiento del trabajo por etapas
El servicio SHALL procesar cada trabajo de forma diferida, recorriendo las etapas del contrato hasta `ready_for_review` o `failed`, y SHALL permitir consultar en cualquier momento su estado y su etapa (RNF-05).

#### Scenario: Trabajo en curso
- **WHEN** una persona autorizada consulta un trabajo que se está procesando
- **THEN** recibe su estado y su etapa actuales.

#### Scenario: Trabajo terminado
- **WHEN** el procesamiento termina sin errores
- **THEN** el trabajo pasa a `ready_for_review`.

#### Scenario: Fallo de una etapa
- **WHEN** una etapa del procesamiento falla
- **THEN** el trabajo pasa a `failed` con un código de error del contrato y no queda ningún resultado consultable.

#### Scenario: Reinicio del worker
- **WHEN** el worker se reinicia con un trabajo a medias
- **THEN** el trabajo vuelve a la cola y termina de procesarse, sin quedarse bloqueado (ADR-0002).

### Requirement: Resultado estructurado al terminar
Cuando el trabajo está en `ready_for_review`, la API SHALL devolver a la docente de la clase un resultado que cumple el contrato, con la transcripción y el análisis separados; antes de ese momento SHALL indicar que el resultado aún no está listo (RF-04).

#### Scenario: Resultado listo
- **WHEN** la docente consulta el resultado de un trabajo en `ready_for_review`
- **THEN** recibe 200 con `schema_version`, `result_version` 1, la transcripción y el análisis en secciones separadas.

#### Scenario: Resultado todavía no listo
- **WHEN** la docente consulta el resultado de un trabajo que no ha terminado
- **THEN** recibe 409 `result_not_ready`.

### Requirement: Recepción acotada antes del análisis multipart
La API SHALL limitar la recepción de `POST /v1/classes` antes de que el analizador multipart consuma todo el cuerpo. SHALL autenticar y autorizar primero, SHALL rechazar con 413 `audio_too_large` un `Content-Length` mayor que `UPLOAD_MAX_BYTES` más un margen fijo para la envolvente multipart y SHALL contar los fragmentos cuando la cabecera falte o sea menor que los bytes reales. El margen no SHALL alterar la validación exacta del archivo ni permitir bytes adicionales de audio (RF-01, RNF-05).

#### Scenario: Archivo en el límite exacto
- **WHEN** el archivo de audio mide exactamente `UPLOAD_MAX_BYTES` y la envolvente multipart cabe en su margen
- **THEN** se conserva para la validación normal del contenido, formato y duración.

#### Scenario: Autorización antes del límite temprano
- **WHEN** una petición sin credencial válida o sin rol para enviar clases declara un cuerpo mayor que el límite de recepción
- **THEN** responde 401 o 403 respectivamente sin consumir el cuerpo.

### Requirement: Recepción idempotente
Cuando un envío lleva `Idempotency-Key`, la API SHALL tratar como el mismo envío los que repiten la clave de quien envía con el mismo audio y los mismos metadatos, y SHALL rechazar la misma clave con otro contenido. Sin la cabecera, cada envío crea una clase nueva (RF-01).

#### Scenario: Reenvío idéntico
- **WHEN** una docente repite un envío con la misma `Idempotency-Key`, el mismo audio y los mismos metadatos
- **THEN** recibe 202 con los mismos `class_id` y `job_id` y no se crea otra clase, otro trabajo ni otra copia del audio.

#### Scenario: Misma clave con otro contenido
- **WHEN** una docente reutiliza una `Idempotency-Key` con otro audio u otros metadatos
- **THEN** recibe 409 `idempotency_conflict` y no se crea ningún trabajo.

#### Scenario: Misma clave de otra persona
- **WHEN** otra persona que envía clases usa una `Idempotency-Key` que ya usó una docente distinta
- **THEN** su envío se trata como nuevo y no recibe los identificadores de la clase de la otra docente.
