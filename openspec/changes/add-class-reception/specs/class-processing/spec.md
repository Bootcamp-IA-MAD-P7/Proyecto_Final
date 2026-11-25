# Spec Delta

## MODIFIED Requirements

### Requirement: Envío de una clase
La API SHALL aceptar el envío de una clase con audio y metadatos válidos según el [contrato](../../../../../docs/CONTRACTS/coteach-ai-api.md), de una persona docente o de la credencial de servicio. Antes de responder, SHALL comprobar que el audio está en un formato admitido por su contenido y no solo por su nombre, y que su tamaño y su duración están dentro de los límites configurados, y SHALL guardarlo de forma privada junto con la clase y el trabajo. Después SHALL responder 202 con los identificadores de la clase y del trabajo sin esperar al procesamiento. Un envío rechazado no deja ni clase, ni trabajo, ni audio guardado (RF-01, RNF-05).

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

#### Scenario: Formato no admitido
- **WHEN** el contenido del archivo no es audio en uno de los formatos admitidos, aunque su nombre o su tipo declarado lo sean
- **THEN** recibe 415 `unsupported_audio`, no se crea ningún trabajo y no queda ningún archivo guardado.

#### Scenario: Duración fuera de los límites
- **WHEN** el audio dura menos que la duración mínima o más que la máxima configuradas
- **THEN** recibe 422 `invalid_audio_duration`, no se crea ningún trabajo y no queda ningún archivo guardado.

## ADDED Requirements

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
