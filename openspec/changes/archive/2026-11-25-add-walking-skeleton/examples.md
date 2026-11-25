# Ejemplos sintéticos

Ejemplos del contrato 0.1.0, sin credenciales ni datos personales reales. La sección 1 de [tasks.md](tasks.md) los convierte en fixtures JSON validados contra los modelos; desde entonces, el contrato registrado en `docs/CONTRACTS/` y `backend/openapi.json` mandan sobre este archivo. Archivo de audio simulado, no incluido. Referencia: [diseño](design.md).

Todas las peticiones a `/v1` llevan `Authorization: Bearer <token>`. En local, el token lo emite el emisor de pruebas para un usuario sintético; no se incluye ninguno aquí.

## Recepción

POST /v1/classes, multipart con audio=synthetic-class.mp3 y metadata:

```json
{"external_class_id":"demo-class-01","participant_count":2,"participants":[{"participant_id":"demo-teacher","role":"teacher","display_name":"Docente de prueba"},{"participant_id":"demo-student","role":"student","display_name":"Estudiante de prueba"}],"consent_reference":"synthetic-fixture-01"}
```

Cabecera Idempotency-Key: demo-upload-01 (aceptada; su efecto llega en E2). Respuesta 202:

```json
{"class_id":"class-demo-01","job_id":"job-demo-01","state":"queued"}
```

synthetic-fixture-01 es una referencia ficticia para pruebas, no una evidencia de consentimiento real. Recibirla y validar su estructura no verifica que exista consentimiento; el mecanismo y la responsabilidad de esa comprobación siguen pendientes de acordar.

## Consulta de trabajo

GET /v1/jobs/job-demo-01 → 200:

```json
{"job_id":"job-demo-01","class_id":"class-demo-01","state":"analyzing","stage":"analyzing","attempt":1,"error":null}
```

Error transitorio ya registrado en el trabajo, HTTP 200 al consultar:

```json
{"job_id":"job-demo-01","class_id":"class-demo-01","state":"retry_wait","stage":"transcribing","attempt":1,"error":{"code":"processing_unavailable","message":"Procesamiento temporalmente no disponible","retryable":true}}
```

## Resultado visible al docente

GET /v1/classes/class-demo-01/result → 200:

```json
{
  "schema_version":"0.1.0",
  "class_id":"class-demo-01",
  "result_version":1,
  "transcript":{
    "speakers":[{"speaker_id":"speaker-01","participant_id":null}],
    "segments":[{"segment_id":"segment-01","start_ms":0,"end_ms":2000,"speaker_id":"speaker-01","text":"Hoy practicamos saludos."}]
  },
  "analysis":{
    "general_summary":"La clase practica saludos.",
    "items":[{"item_id":"item-01","category":"vocabulary","content":"Saludos"}]
  },
  "review":{"status":"pending","review_due_at":"2026-12-11T10:00:00Z"},
  "publication":{"status":"unpublished","result_version":null,"published_at":null,"mode":null}
}
```

El vencimiento ilustra disponibilidad el 10 de diciembre a las 10:00 y un plazo de 24 horas: ambos supuestos siguen pendientes de Lay. El alumno no recibe este borrador: obtiene 404 resource_not_available.

## Corrección y aprobación

En E1 estas dos rutas devuelven estos ejemplos sin guardar nada; su comportamiento llega en E5.

PATCH /v1/classes/class-demo-01/review:

```json
{"expected_result_version":1,"changes":{"analysis":{"general_summary":"Se han practicado saludos básicos.","items":[{"item_id":"item-01","category":"vocabulary","content":"Saludos básicos"}]}}}
```

Propuesta: cada sección enviada reemplaza esa sección completa; las ausentes se conservan. Respuesta 200 con la nueva versión completa del resultado, result_version=2 y review.status=in_review.

POST /v1/classes/class-demo-01/approve:

```json
{"expected_result_version":2}
```

Respuesta 200:

```json
{"class_id":"class-demo-01","publication":{"status":"published","result_version":2,"published_at":"2026-12-10T12:00:00Z","mode":"teacher_approved"}}
```

## Errores

409 al corregir con versión obsoleta:

```json
{"error":{"code":"result_version_conflict","message":"La versión del resultado ha cambiado","retryable":false},"request_id":"request-demo-01"}
```

422 por participantes duplicados:

```json
{"error":{"code":"invalid_participants","message":"Los participantes deben tener identificadores distintos","retryable":false},"request_id":"request-demo-02"}
```

401 sin credencial válida:

```json
{"error":{"code":"unauthenticated","message":"Se requiere autenticación válida","retryable":false},"request_id":"request-demo-03"}
```

422 al omitir consent_reference o enviar una referencia inválida según el contrato; no se acepta trabajo ni se inicia el procesamiento:

```json
{"error":{"code":"invalid_consent_reference","message":"Se requiere una referencia de consentimiento válida","retryable":false},"request_id":"request-demo-04"}
```

Otros casos usan el mismo sobre: 404 resource_not_available, 403 forbidden, 409 idempotency_conflict, 409 result_not_ready, 413 audio_too_large, 415 unsupported_audio, 503 service_unavailable. Solo los errores transitorios llevan retryable=true; los 409 de corrección requieren releer y resolver, no repetir a ciegas.
