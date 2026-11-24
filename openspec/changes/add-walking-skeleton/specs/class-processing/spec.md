# Spec Delta

## Purpose

Que una clase enviada a la API se procese de forma diferida, por etapas, y su resultado estructurado se pueda consultar al terminar. En este cambio el procesamiento es simulado y el resultado, sintético: los modelos reales llegan en E3 y E4, y la recepción completa del audio en E2. El contrato está en [CONTRACTS](../../../../../docs/CONTRACTS/README.md).

## ADDED Requirements

### Requirement: Envío de una clase
La API SHALL aceptar el envío de una clase con audio y metadatos válidos según el contrato, de una persona docente o de la credencial de servicio, y SHALL responder 202 con los identificadores de la clase y del trabajo sin esperar al procesamiento (RF-01, RNF-05).

#### Scenario: Envío válido
- **WHEN** una docente autenticada envía audio y metadatos válidos
- **THEN** recibe 202 con `class_id`, `job_id` y estado `queued`, y el trabajo queda pendiente de procesar.

#### Scenario: Participantes incoherentes
- **WHEN** los metadatos repiten un `participant_id` o el número de participantes no coincide con la lista
- **THEN** recibe 422 `invalid_participants` y no se crea ningún trabajo.

#### Scenario: Sin referencia de consentimiento
- **WHEN** los metadatos no incluyen `consent_reference`
- **THEN** recibe 422 `invalid_consent_reference` y no se crea ningún trabajo.

#### Scenario: Sin audio
- **WHEN** el envío no incluye el archivo de audio
- **THEN** recibe 422 y no se crea ningún trabajo.

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
